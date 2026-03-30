import pytest

from bulletin.doue._connector import _DoueConnector
from bulletin.doue.exceptions import QueryError, EndpointError

@pytest.fixture
def connector():
    return _DoueConnector()


def test_build_acts_query_valid_date(connector):
    """Test query building with a valid date and default language."""
    query = connector.build_acts_query("2024-01-01")
    assert "FILTER(?date = \"2024-01-01\"^^xsd:date)" in query
    assert "expression_uses_language <https://publications.europa.eu/resource/authority/language/ENG>" in query
    assert "FILTER(LANG(?categoryLabel) = \"en\")" in query


def test_build_acts_query_custom_language(connector):
    """Test query building with a custom language code."""
    query = connector.build_acts_query("2024-01-01", language="ENG")
    assert "expression_uses_language <https://publications.europa.eu/resource/authority/language/ENG>" in query
    assert "FILTER(LANG(?categoryLabel) = \"en\")" in query


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
    fake_connector = _DoueConnector(endpoint="https://esto-no-existe.europa.eu/sparql")
    
    with pytest.raises(EndpointError) as exc_info:
        fake_connector.execute_query("SELECT * WHERE { ?s ?p ?o } LIMIT 1")
        
    # No status code because the connection failed completely
    assert exc_info.value.status_code is None
    assert "Failed to reach SPARQL endpoint" in str(exc_info.value)


@pytest.mark.integration
def test_execute_query_timeout():
    """Test that a timeout raises an EndpointError."""
    # Build a valid query
    connector = _DoueConnector(timeout=0.001)
    query = connector.build_acts_query("2024-05-15")
    
    # Give it an impossibly small timeout (0.001 seconds) to force a timeout exception
    with pytest.raises(EndpointError) as exc_info:
        connector.execute_query(query)
        
    assert exc_info.value.status_code is None
    assert "Failed to reach SPARQL endpoint" in str(exc_info.value)
