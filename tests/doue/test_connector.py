import pytest
from unittest.mock import patch, MagicMock
import requests

from bulletin.doue.repository._connector import DoueConnector
from bulletin.doue.exceptions import QueryError, EndpointError


@pytest.fixture
def connector():
    return DoueConnector()


def test_build_acts_query_valid_date(connector):
    """Test query building with a valid date and default language."""
    query = connector.build_acts_query("2024-01-01")
    assert 'FILTER(?date = "2024-01-01"^^xsd:date)' in query
    assert (
        "expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG>"
        in query
    )
    assert 'FILTER(LANG(?categoryLabel) = "en")' in query


def test_build_acts_query_custom_language(connector):
    """Test query building with a custom language code."""
    query = connector.build_acts_query("2024-01-01", language="ENG")
    assert (
        "expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG>"
        in query
    )
    assert 'FILTER(LANG(?categoryLabel) = "en")' in query


def test_build_acts_query_invalid_date(connector):
    """Test query building with invalid date format raises QueryError."""
    with pytest.raises(QueryError, match="Invalid date format"):
        connector.build_acts_query("20240101")

    with pytest.raises(QueryError, match="Invalid date format"):
        connector.build_acts_query("01-01-2024")


def test_build_acts_query_unsupported_language(connector):
    """Test query building with unsupported language raises QueryError."""
    with pytest.raises(QueryError, match="Unsupported language: 'XYZ'"):
        connector.build_acts_query("2024-01-01", language="XYZ")


def test_build_acts_query_date_range(connector):
    query = connector.build_acts_query(date="2024-01-01", date_end="2024-01-31")
    assert 'FILTER(?date >= "2024-01-01"^^xsd:date)' in query
    assert 'FILTER(?date <= "2024-01-31"^^xsd:date)' in query


def test_build_acts_query_title_contains(connector):
    query = connector.build_acts_query(
        date="2024-01-01", title_contains="regulation"
    )
    assert 'CONTAINS(LCASE(STR(?title)), LCASE("regulation"))' in query


def test_build_acts_query_invalid_date_end_order(connector):
    with pytest.raises(QueryError, match="date_end must be on or after date"):
        connector.build_acts_query(date="2024-01-10", date_end="2024-01-01")


def test_execute_query_http_error(connector):
    """Test that execute_query raises EndpointError on HTTP error."""
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
    
    with patch("bulletin.doue.repository._connector.requests.post") as mock_post:
        # Create a proper HTTPError with a response object
        mock_response = MagicMock()
        mock_response.status_code = 400
        http_error = requests.exceptions.HTTPError("400 Client Error")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response
        
        with pytest.raises(EndpointError) as exc_info:
            connector.execute_query(query)
        
        assert exc_info.value.status_code == 400
        assert "HTTP 400" in str(exc_info.value)


def test_execute_query_connection_error(connector):
    """Test that execute_query raises EndpointError on connection failure."""
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
    
    with patch("bulletin.doue.repository._connector.requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Failed to connect"
        )
        
        with pytest.raises(EndpointError) as exc_info:
            connector.execute_query(query)
        
        assert exc_info.value.status_code is None
        assert "Failed to reach SPARQL endpoint" in str(exc_info.value)


def test_execute_query_timeout_error(connector):
    """Test that execute_query raises EndpointError on timeout."""
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
    
    with patch("bulletin.doue.repository._connector.requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout(
            "Request timed out"
        )
        
        with pytest.raises(EndpointError) as exc_info:
            connector.execute_query(query)
        
        assert exc_info.value.status_code is None
        assert "Failed to reach SPARQL endpoint" in str(exc_info.value)


def test_execute_query_success(connector):
    """Test that execute_query successfully returns parsed JSON response."""
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
    expected_response = {
        "head": {"vars": ["s", "p", "o"]},
        "results": {"bindings": []}
    }
    
    with patch("bulletin.doue.repository._connector.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        
        result = connector.execute_query(query)
        
        assert result == expected_response
        mock_post.assert_called_once()
        # Verify the call was made with correct parameters
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 30
        assert call_kwargs["headers"]["Accept"] == "application/sparql-results+json"


@pytest.mark.integration
def test_execute_query_live(connector):
    """Integration test that performs an actual request to the EUR-Lex SPARQL endpoint.

    This verifies that our query syntax is correct according to the live Cellar endpoint.
    Retrieves acts from 2024-05-15 (a known date).
    """
    # Use a date that definitely has publications
    query = connector.build_acts_query("2024-05-15", language="ENG")
    result = connector.execute_query(query)

    # Check SPARQL response structure
    assert "head" in result
    assert "results" in result
    assert "bindings" in result["results"]

    # We expect some Acts on May 15, 2024
    acts = result["results"]["bindings"]
    assert len(acts) > 0

    # Pick a random act and check its required fields
    act = acts[0]
    assert "act" in act
    assert "title" in act
    assert "date" in act


@pytest.mark.integration
def test_execute_query_bad_syntax(connector):
    """Test that executing an invalid SPARQL query raises an EndpointError (HTTP 400)."""
    bad_query = "SELECT * WHERE { esto es un error de sintaxis }"

    with pytest.raises(EndpointError) as exc_info:
        connector.execute_query(bad_query)

    assert exc_info.value.status_code == 400
    assert "HTTP 400" in str(exc_info.value)


@pytest.mark.integration
def test_execute_query_unreachable_endpoint():
    """Test that a bad endpoint URL raises an EndpointError without a status code."""
    fake_connector = DoueConnector(endpoint="https://esto-no-existe.europa.eu/sparql")

    with pytest.raises(EndpointError) as exc_info:
        fake_connector.execute_query("SELECT * WHERE { ?s ?p ?o } LIMIT 1")

    # No status code because the connection failed completely
    assert exc_info.value.status_code is None
    assert "Failed to reach SPARQL endpoint" in str(exc_info.value)


@pytest.mark.integration
def test_execute_query_timeout():
    """Test that a timeout raises an EndpointError."""
    # Build a valid query
    connector = DoueConnector(timeout=0.001)
    query = connector.build_acts_query("2024-05-15")

    # Give it an impossibly small timeout (0.001 seconds) to force a timeout exception
    with pytest.raises(EndpointError) as exc_info:
        connector.execute_query(query)

    assert exc_info.value.status_code is None
    assert "Failed to reach SPARQL endpoint" in str(exc_info.value)
