import pytest
from unittest.mock import patch, MagicMock
import requests

from bulletin.eurlex.repository._connector import EurlexConnector
from bulletin.eurlex.exceptions import QueryError, EndpointError


@pytest.fixture
def connector():
    return EurlexConnector()


class TestBuildActsQuery:
    """Tests for build_acts_query method."""

    def test_valid_date(self, connector):
        query = connector.build_acts_query("2024-01-01")
        assert 'FILTER(?date = "2024-01-01"^^xsd:date)' in query
        assert (
            "expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG>"
            in query
        )
        assert 'FILTER(LANG(?categoryLabelValue) = "en")' in query

    def test_uses_eli_act_uri_and_optional_celex_uri(self, connector):
        query = connector.build_acts_query("2024-01-01")
        assert 'CONTAINS(STR(?eliUri), "/resource/eli/")' in query
        assert 'CONTAINS(STR(?celexUri), "/resource/celex/")' in query
        assert 'CONTAINS(STR(?ojUri), "/resource/oj/")' in query
        assert "BIND(COALESCE(?eliUri, ?celexUri, ?ojUri) AS ?rawAct)" in query
        assert "SAMPLE(?celexUri) AS ?celexAct" in query

    def test_does_not_require_eli_uri(self, connector):
        query = connector.build_acts_query("2024-01-01")
        assert (
            'FILTER(STRSTARTS(STR(?rawAct), "http://publications.europa.eu/resource/eli/"))'
            not in query
        )
        assert "FILTER(BOUND(?rawAct))" in query
        assert "GROUP BY ?act ?date" in query

    def test_includes_legacy_official_journal_date_path(self, connector):
        query = connector.build_acts_query("2017-01-04")
        assert "cdm:official-journal-act_date_publication" in query
        assert (
            "cdm:resource_legal_published_in_official-journal/"
            "cdm:publication_general_date_publication"
        ) in query

    def test_custom_language(self, connector):
        query = connector.build_acts_query("2024-01-01", language="ENG")
        assert (
            "expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG>"
            in query
        )
        assert 'FILTER(LANG(?categoryLabelValue) = "en")' in query

    def test_invalid_date(self, connector):
        with pytest.raises(QueryError, match="Invalid date format"):
            connector.build_acts_query("20240101")
        with pytest.raises(QueryError, match="Invalid date format"):
            connector.build_acts_query("01-01-2024")

    def test_unsupported_language(self, connector):
        with pytest.raises(QueryError, match="Unsupported language: 'XYZ'"):
            connector.build_acts_query("2024-01-01", language="XYZ")

    def test_date_range(self, connector):
        query = connector.build_acts_query(date="2024-01-01", date_end="2024-01-31")
        assert 'FILTER(?date >= "2024-01-01"^^xsd:date)' in query
        assert 'FILTER(?date <= "2024-01-31"^^xsd:date)' in query

    def test_title_contains(self, connector):
        query = connector.build_acts_query(
            date="2024-01-01", title_contains="regulation"
        )
        assert 'CONTAINS(LCASE(STR(?titleValue)), LCASE("regulation"))' in query

    def test_category_type(self, connector):
        query = connector.build_acts_query(date="2024-01-01", category_type="RES")
        assert 'FILTER(REPLACE(STR(?category), ".*/", "") = "RES")' in query

    def test_invalid_category_type(self, connector):
        with pytest.raises(QueryError, match="category_type filter cannot be empty"):
            connector.build_acts_query(date="2024-01-01", category_type="  ")

    def test_invalid_date_end_order(self, connector):
        with pytest.raises(QueryError, match="date_end must be on or after date"):
            connector.build_acts_query(date="2024-01-10", date_end="2024-01-01")


class TestBuildCategoryTypesQuery:
    """Tests for build_category_types_query method."""

    def test_default_language(self, connector):
        query = connector.build_category_types_query()
        assert "skos:Concept" in query
        assert "resource-type" in query
        assert 'FILTER(LANG(?label) = "en")' in query

    def test_spanish_language(self, connector):
        query = connector.build_category_types_query(language="SPA")
        assert 'FILTER(LANG(?label) = "es")' in query

    def test_search_filters_by_label(self, connector):
        query = connector.build_category_types_query(search="regulation")
        assert (
            "FILTER(BOUND(?label) && CONTAINS(LCASE(STR(?label)), "
            'LCASE("regulation")))'
        ) in query

    def test_search_is_trimmed(self, connector):
        query = connector.build_category_types_query(search="  directive  ")
        assert 'LCASE("directive")' in query

    def test_search_escapes_sparql_literal(self, connector):
        query = connector.build_category_types_query(search='foo "bar" \\ baz')
        assert 'LCASE("foo \\"bar\\" \\\\ baz")' in query

    def test_empty_search_raises(self, connector):
        with pytest.raises(QueryError, match="search filter cannot be empty"):
            connector.build_category_types_query(search="  ")


class TestBuildInstitutionTypesQuery:
    """Tests for build_institution_types_query method."""

    def test_default_language(self, connector):
        query = connector.build_institution_types_query()
        assert "corporate-body" in query
        assert 'FILTER(LANG(?label) = "en")' in query
        assert "DISTINCT ?code ?label" in query

    def test_spanish_language(self, connector):
        query = connector.build_institution_types_query(language="SPA")
        assert "corporate-body" in query
        assert 'FILTER(LANG(?label) = "es")' in query

    def test_search_filters_by_label(self, connector):
        query = connector.build_institution_types_query(search="commission")
        assert (
            "FILTER(BOUND(?label) && CONTAINS(LCASE(STR(?label)), "
            'LCASE("commission")))'
        ) in query

    def test_search_is_trimmed(self, connector):
        query = connector.build_institution_types_query(search="  court  ")
        assert 'LCASE("court")' in query

    def test_search_escapes_sparql_literal(self, connector):
        query = connector.build_institution_types_query(search='foo "bar" \\ baz')
        assert 'LCASE("foo \\"bar\\" \\\\ baz")' in query

    def test_empty_search_raises(self, connector):
        with pytest.raises(QueryError, match="search filter cannot be empty"):
            connector.build_institution_types_query(search="  ")


class TestBuildActContentUrl:
    """Tests for build_act_content_url method."""

    def test_celex_id(self, connector):
        url = connector.build_act_content_url("52025M12135")
        assert url == "https://publications.europa.eu/resource/celex/52025M12135"

    def test_full_resource_uri(self, connector):
        uri = "https://publications.europa.eu/resource/celex/52025M12135"
        assert connector.build_act_content_url(uri) == uri

    def test_strips_identifier(self, connector):
        url = connector.build_act_content_url("  52025M12135  ")
        assert url == "https://publications.europa.eu/resource/celex/52025M12135"

    def test_url_encodes_celex_id(self, connector):
        url = connector.build_act_content_url("OJ 2025/1")
        assert url == "https://publications.europa.eu/resource/celex/OJ%202025%2F1"

    def test_empty_identifier(self, connector):
        with pytest.raises(QueryError, match="act_id_or_uri cannot be empty"):
            connector.build_act_content_url("   ")


class TestFetchPublicationContent:
    """Tests for fetch_publication_content method."""

    def test_success_text(self, connector):
        resource_uri = "https://publications.europa.eu/resource/celex/52025M12135"
        expected_content = "<html><body>Act content</body></html>"

        with patch("bulletin.eurlex.repository._connector.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = expected_content
            mock_get.return_value = mock_response

            result = connector.fetch_publication_content(
                resource_uri,
                language="ENG",
                max_size=2048,
            )

        assert result == expected_content
        mock_get.assert_called_once_with(
            resource_uri,
            timeout=300,
            headers={
                "Accept": (
                    "application/xhtml+xml, text/html;q=0.9, "
                    "application/xml;q=0.8, text/xml;q=0.7"
                ),
                "Accept-Language": "eng",
                "Accept-Max-Cs-Size": "2048",
            },
            allow_redirects=True,
        )
        mock_response.raise_for_status.assert_called_once_with()

    def test_success_bytes(self, connector):
        resource_uri = "https://publications.europa.eu/resource/celex/52025M12135"
        expected_content = b"%PDF-1.7"

        with patch("bulletin.eurlex.repository._connector.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = expected_content
            mock_get.return_value = mock_response

            result = connector.fetch_publication_content(
                resource_uri,
                return_bytes=True,
            )

        assert result == expected_content

    def test_success_pdf_returns_bytes(self, connector):
        resource_uri = "https://publications.europa.eu/resource/celex/52025M12135"
        expected_content = b"%PDF-1.7"

        with patch("bulletin.eurlex.repository._connector.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = expected_content
            mock_get.return_value = mock_response

            result = connector.fetch_publication_content(
                resource_uri,
                max_size=4096,
                content_format="pdf",
            )

        assert result == expected_content
        mock_get.assert_called_once_with(
            resource_uri,
            timeout=300,
            headers={
                "Accept": "application/pdf",
                "Accept-Language": "eng",
                "Accept-Max-Cs-Size": "4096",
            },
            allow_redirects=True,
        )
        mock_response.raise_for_status.assert_called_once_with()

    def test_content_format_is_case_insensitive_and_trimmed(self, connector):
        resource_uri = "https://publications.europa.eu/resource/celex/52025M12135"

        with patch("bulletin.eurlex.repository._connector.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"%PDF-1.7"
            mock_get.return_value = mock_response

            result = connector.fetch_publication_content(
                resource_uri,
                content_format=" PDF ",
            )

        assert result == b"%PDF-1.7"
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["Accept"] == "application/pdf"

    def test_lowercase_language_is_normalized(self, connector):
        resource_uri = "https://publications.europa.eu/resource/celex/52025M12135"

        with patch("bulletin.eurlex.repository._connector.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = "<html></html>"
            mock_get.return_value = mock_response

            connector.fetch_publication_content(resource_uri, language="eng")

        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["Accept-Language"] == "eng"

    def test_unsupported_language(self, connector):
        with pytest.raises(QueryError, match="Unsupported language: 'XYZ'"):
            connector.fetch_publication_content(
                "https://publications.europa.eu/resource/celex/52025M12135",
                language="XYZ",
            )

    def test_empty_resource_uri(self, connector):
        with pytest.raises(QueryError, match="resource_uri cannot be empty"):
            connector.fetch_publication_content("   ")

    def test_invalid_max_size(self, connector):
        with pytest.raises(QueryError, match="max_size must be a positive integer"):
            connector.fetch_publication_content(
                "https://publications.europa.eu/resource/celex/52025M12135",
                max_size=0,
            )

    def test_invalid_content_format(self, connector):
        with pytest.raises(QueryError, match="Unsupported content_format"):
            connector.fetch_publication_content(
                "https://publications.europa.eu/resource/celex/52025M12135",
                content_format="docx",
            )

    def test_http_error(self, connector):
        resource_uri = "https://publications.europa.eu/resource/celex/52025M12135"

        with patch("bulletin.eurlex.repository._connector.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            http_error = requests.exceptions.HTTPError("404 Client Error")
            http_error.response = mock_response
            mock_response.raise_for_status.side_effect = http_error
            mock_get.return_value = mock_response

            with pytest.raises(EndpointError) as exc_info:
                connector.fetch_publication_content(resource_uri)

        assert exc_info.value.status_code == 404
        assert exc_info.value.endpoint == resource_uri
        assert "HTTP 404" in str(exc_info.value)

    def test_connection_error(self, connector):
        resource_uri = "https://publications.europa.eu/resource/celex/52025M12135"

        with patch("bulletin.eurlex.repository._connector.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Failed")

            with pytest.raises(EndpointError) as exc_info:
                connector.fetch_publication_content(resource_uri)

        assert exc_info.value.status_code is None
        assert exc_info.value.endpoint == resource_uri
        assert "Failed to reach EU API" in str(exc_info.value)


class TestExecuteQuery:
    """Tests for execute_query method."""

    def test_http_error(self, connector):
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
        with patch("bulletin.eurlex.repository._connector.requests.post") as mock_post:
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

    def test_connection_error(self, connector):
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
        with patch("bulletin.eurlex.repository._connector.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError(
                "Failed to connect"
            )
            with pytest.raises(EndpointError) as exc_info:
                connector.execute_query(query)
            assert exc_info.value.status_code is None

    def test_timeout_error(self, connector):
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
        with patch("bulletin.eurlex.repository._connector.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
            with pytest.raises(EndpointError) as exc_info:
                connector.execute_query(query)
            assert exc_info.value.status_code is None
            assert "Failed to reach SPARQL endpoint" in str(exc_info.value)

    def test_success(self, connector):
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
        expected_response = {
            "head": {"vars": ["s", "p", "o"]},
            "results": {"bindings": []},
        }
        with patch("bulletin.eurlex.repository._connector.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = expected_response
            mock_post.return_value = mock_response
            result = connector.execute_query(query)
            assert result == expected_response
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["timeout"] == 300
            assert call_kwargs["headers"]["Accept"] == "application/sparql-results+json"


@pytest.mark.integration
class TestExecuteQueryIntegration:
    """Integration tests for execute_query method with live endpoint."""

    def test_live_endpoint(self, connector):
        query = connector.build_acts_query("2024-05-15", language="ENG")
        result = connector.execute_query(query)
        assert "head" in result
        assert "results" in result
        assert "bindings" in result["results"]
        acts = result["results"]["bindings"]
        assert len(acts) > 0
        act = acts[0]
        assert "act" in act
        assert "title" in act
        assert "date" in act

    def test_bad_syntax(self, connector):
        bad_query = "SELECT * WHERE { esto es un error de sintaxis }"
        with pytest.raises(EndpointError) as exc_info:
            connector.execute_query(bad_query)
        assert exc_info.value.status_code == 400
        assert "HTTP 400" in str(exc_info.value)

    def test_unreachable_endpoint(self):
        fake_connector = EurlexConnector(
            endpoint="https://esto-no-existe.europa.eu/sparql"
        )
        with pytest.raises(EndpointError) as exc_info:
            fake_connector.execute_query("SELECT * WHERE { ?s ?p ?o } LIMIT 1")
        assert exc_info.value.status_code is None
        assert "Failed to reach SPARQL endpoint" in str(exc_info.value)

    def test_timeout(self):
        connector = EurlexConnector(timeout=0.001)
        query = connector.build_acts_query("2024-05-15")
        with pytest.raises(EndpointError) as exc_info:
            connector.execute_query(query)
        assert exc_info.value.status_code is None
        assert "Failed to reach SPARQL endpoint" in str(exc_info.value)
