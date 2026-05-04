"""Unit tests for EurlexBulletinClient."""

from datetime import date
from unittest.mock import patch

import pytest

from bulletin.eurlex.api.client import EurlexBulletinClient
from bulletin.eurlex.constants import SPARQL_ENDPOINT
from bulletin.eurlex.api.models import EurlexOfficialAct


@pytest.fixture
def mock_connector():
    """Fixture providing a mocked EurlexConnector."""
    with patch("bulletin.eurlex.api.client.EurlexConnector") as mock:
        yield mock


@pytest.fixture
def client(mock_connector):
    """Fixture providing a EurlexBulletinClient with mocked connector."""
    return EurlexBulletinClient()


@pytest.fixture
def sample_act():
    """Fixture providing a representative parsed EUR-Lex act."""
    return EurlexOfficialAct(
        celex_uri="https://example.com/act1",
        act_number="2025/1",
        title="Act 1",
        date=date(2025, 3, 27),
        section_code=None,
        subsection_code=None,
        category_code=None,
        category_uri=None,
        category_label=None,
        institution_code=None,
        institution_uri=None,
        institution_label=None,
    )


class TestInit:
    """Tests for EurlexBulletinClient initialization."""

    def test_with_defaults(self, mock_connector):
        """Test client initialization with default parameters."""
        EurlexBulletinClient()
        mock_connector.assert_called_once_with(endpoint=SPARQL_ENDPOINT, timeout=300)

    def test_with_custom_endpoint(self, mock_connector):
        """Test client initialization with custom endpoint."""
        custom_endpoint = "https://custom.endpoint/sparql"
        EurlexBulletinClient(endpoint=custom_endpoint)
        mock_connector.assert_called_once_with(endpoint=custom_endpoint, timeout=300)

    def test_with_custom_timeout(self, mock_connector):
        """Test client initialization with custom timeout."""
        EurlexBulletinClient(timeout=60)
        mock_connector.assert_called_once_with(endpoint=SPARQL_ENDPOINT, timeout=60)

    def test_with_all_custom_params(self, mock_connector):
        """Test client initialization with all custom parameters."""
        custom_endpoint = "https://custom.endpoint/sparql"
        custom_timeout = 45
        EurlexBulletinClient(endpoint=custom_endpoint, timeout=custom_timeout)
        mock_connector.assert_called_once_with(
            endpoint=custom_endpoint, timeout=custom_timeout
        )


class TestGetActs:
    """Tests for get_acts method."""

    def test_with_valid_date(self, client, mock_connector):
        """Test fetching acts with a valid ISO date."""
        test_date = "2025-03-27"
        mock_response = {
            "results": {"bindings": [{"act": {"value": "https://example.com/act1"}}]}
        }
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = mock_response

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [
                EurlexOfficialAct(
                    celex_uri="https://example.com/act1",
                    act_number=None,
                    title="Act 1",
                    date=date(2025, 3, 27),
                    section_code=None,
                    subsection_code=None,
                    category_code=None,
                    category_uri=None,
                    category_label=None,
                    institution_code=None,
                    institution_uri=None,
                    institution_label=None,
                )
            ]
            result = client.get_acts(test_date)

            mock_instance.build_acts_query.assert_called_once_with(
                test_date,
                language="ENG",
                date_end=None,
                title_contains=None,
                category_type=None,
                institution_type=None,
            )
            mock_instance.execute_query.assert_called_once_with("SPARQL_QUERY")
            mock_parse.assert_called_once_with(mock_response)
            assert len(result) == 1

    def test_with_custom_language(self, client, mock_connector):
        """Test fetching acts with a custom language code."""
        test_date = "2025-03-27"
        custom_language = "FRA"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = []
            client.get_acts(test_date, language=custom_language)

            mock_instance.build_acts_query.assert_called_once_with(
                test_date,
                language=custom_language,
                date_end=None,
                title_contains=None,
                category_type=None,
                institution_type=None,
            )

    def test_returns_parsed_results(self, client, mock_connector):
        """Test that get_acts returns the parsed results."""
        test_date = "2025-03-27"
        mock_response = {"results": {"bindings": []}}
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = mock_response

        expected_acts = [
            EurlexOfficialAct(
                celex_uri="https://example.com/act1",
                act_number=None,
                title="Act 1",
                date=date(2025, 3, 27),
                section_code=None,
                subsection_code=None,
                category_code=None,
                category_uri=None,
                category_label=None,
                institution_code=None,
                institution_uri=None,
                institution_label=None,
            ),
            EurlexOfficialAct(
                celex_uri="https://example.com/act2",
                act_number=None,
                title="Act 2",
                date=date(2025, 3, 27),
                section_code=None,
                subsection_code=None,
                category_code=None,
                category_uri=None,
                category_label=None,
                institution_code=None,
                institution_uri=None,
                institution_label=None,
            ),
        ]

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = expected_acts
            result = client.get_acts(test_date)

            assert result == expected_acts
            assert len(result) == 2

    def test_empty_results(self, client, mock_connector):
        """Test get_acts with empty results from SPARQL."""
        test_date = "2025-03-27"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = []
            result = client.get_acts(test_date)

            assert result == []

    def test_with_date_end(self, client, mock_connector):
        """Test fetching acts with a date range using date_end parameter."""
        test_date = "2025-03-27"
        test_date_end = "2025-03-31"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = []
            client.get_acts(test_date, date_end=test_date_end)

            mock_instance.build_acts_query.assert_called_once_with(
                test_date,
                language="ENG",
                date_end=test_date_end,
                title_contains=None,
                category_type=None,
                institution_type=None,
            )

    def test_with_title_contains(self, client, mock_connector):
        """Test fetching acts with a title filter using title_contains parameter."""
        test_date = "2025-03-27"
        title_filter = "regulation"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = []
            client.get_acts(test_date, title_contains=title_filter)

            mock_instance.build_acts_query.assert_called_once_with(
                test_date,
                language="ENG",
                date_end=None,
                title_contains=title_filter,
                category_type=None,
                institution_type=None,
            )

    def test_with_date_end_and_title_contains(self, client, mock_connector):
        """Test fetching acts with both date_end and title_contains parameters."""
        test_date = "2025-03-27"
        test_date_end = "2025-03-31"
        title_filter = "directive"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = []
            client.get_acts(
                test_date, date_end=test_date_end, title_contains=title_filter
            )

            mock_instance.build_acts_query.assert_called_once_with(
                test_date,
                language="ENG",
                date_end=test_date_end,
                title_contains=title_filter,
                category_type=None,
                institution_type=None,
            )

    def test_with_category_type(self, client, mock_connector):
        """Test get_acts with category_type parameter."""
        test_date = "2025-03-27"
        category_type = "RES"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = []
            client.get_acts(test_date, category_type=category_type)

            mock_instance.build_acts_query.assert_called_once_with(
                test_date,
                language="ENG",
                date_end=None,
                title_contains=None,
                category_type=category_type,
                institution_type=None,
            )


class TestGetActsOutputFormat:
    """Tests for get_acts output_format support."""

    def test_none_format_returns_models(
        self, client, mock_connector, sample_act
    ) -> None:
        """Test get_acts returns model objects when no format is requested."""
        test_date = "2025-03-27"
        mock_response = {"results": {"bindings": []}}
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = mock_response

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            result = client.get_acts(test_date, output_format=None)

        assert result == [sample_act]
        mock_instance.build_acts_query.assert_called_once_with(
            test_date,
            language="ENG",
            date_end=None,
            title_contains=None,
            category_type=None,
            institution_type=None,
        )
        mock_instance.execute_query.assert_called_once_with("SPARQL_QUERY")
        mock_parse.assert_called_once_with(mock_response)

    def test_objects_format_returns_models(
        self, client, mock_connector, sample_act
    ) -> None:
        """Test get_acts can explicitly return model objects."""
        test_date = "2025-03-27"
        mock_response = {"results": {"bindings": []}}
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = mock_response

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            result = client.get_acts(test_date, output_format="objects")

        assert result == [sample_act]
        mock_instance.build_acts_query.assert_called_once_with(
            test_date,
            language="ENG",
            date_end=None,
            title_contains=None,
            category_type=None,
            institution_type=None,
        )

    def test_json_format_returns_serializable_dicts(
        self, client, mock_connector, sample_act
    ) -> None:
        """Test get_acts returns JSON-compatible dictionaries."""
        test_date = "2025-03-27"
        mock_response = {"results": {"bindings": []}}
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = mock_response

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            json_list = client.get_acts(test_date, output_format="json")

        assert json_list == [
            {
                "celex_uri": "https://example.com/act1",
                "act_number": "2025/1",
                "title": "Act 1",
                "date": "2025-03-27",
                "section_code": None,
                "subsection_code": None,
                "category_code": None,
                "category_uri": None,
                "category_label": None,
                "institution_code": None,
                "institution_uri": None,
                "institution_label": None,
            }
        ]
        mock_instance.build_acts_query.assert_called_once_with(
            test_date,
            language="ENG",
            date_end=None,
            title_contains=None,
            category_type=None,
            institution_type=None,
        )

    def test_csv_format_returns_csv_text(
        self, client, mock_connector, sample_act
    ) -> None:
        """Test get_acts returns CSV text."""
        test_date = "2025-03-27"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            csv_text = client.get_acts(test_date, output_format="csv")

        assert '"celex_uri","act_number","title","date"' in csv_text
        assert '"https://example.com/act1","2025/1","Act 1","2025-03-27"' in csv_text
        mock_instance.build_acts_query.assert_called_once_with(
            test_date,
            language="ENG",
            date_end=None,
            title_contains=None,
            category_type=None,
            institution_type=None,
        )

    def test_df_format_returns_dataframe(self, client, mock_connector, sample_act):
        """Test get_acts returns a DataFrame for df output."""
        test_date = "2025-03-27"
        dataframe = object()
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            with patch(
                "bulletin.eurlex.api.client.acts_to_dataframe",
                return_value=dataframe,
            ) as mock_to_dataframe:
                result = client.get_acts(test_date, output_format="df")

        assert result is dataframe
        mock_to_dataframe.assert_called_once_with([sample_act])
        mock_instance.build_acts_query.assert_called_once_with(
            test_date,
            language="ENG",
            date_end=None,
            title_contains=None,
            category_type=None,
            institution_type=None,
        )

    def test_xml_format_returns_xml_text(
        self, client, mock_connector, sample_act
    ) -> None:
        """Test get_acts returns xml string for xml output."""
        test_date = "2025-03-27"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            with patch(
                "bulletin.eurlex.api.client.acts_to_xml",
                return_value="<acts></acts>",
            ) as mock_to_xml:
                xml_result = client.get_acts(test_date, output_format="xml")

        assert xml_result == "<acts></acts>"
        mock_to_xml.assert_called_once_with([sample_act])
        mock_instance.build_acts_query.assert_called_once_with(
            test_date,
            language="ENG",
            date_end=None,
            title_contains=None,
            category_type=None,
            institution_type=None,
        )

    def test_empty_results_with_json_format(self, client, mock_connector) -> None:
        """Test get_acts returns an empty list for empty JSON output."""
        test_date = "2025-03-27"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = []
            json_list = client.get_acts(test_date, output_format="json")

        assert json_list == []

    def test_format_is_case_insensitive_and_trims_whitespace(
        self, client, mock_connector, sample_act
    ) -> None:
        """Test get_acts normalizes output_format values."""
        test_date = "2025-03-27"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            csv_text = client.get_acts(test_date, output_format=" CSV ")

        assert '"https://example.com/act1","2025/1","Act 1","2025-03-27"' in csv_text

    def test_format_does_not_change_supported_filters(
        self, client, mock_connector, sample_act
    ) -> None:
        """Test output_format works with all get_acts filters."""
        test_date = "2025-03-27"
        test_date_end = "2025-03-31"
        title_filter = "regulation"
        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
        mock_instance.execute_query.return_value = {"results": {"bindings": []}}

        with patch("bulletin.eurlex.api.client.parse_acts_results") as mock_parse:
            mock_parse.return_value = [sample_act]
            client.get_acts(
                test_date,
                language="FRA",
                date_end=test_date_end,
                title_contains=title_filter,
                category_type="RES",
                institution_type="COM",
                output_format="json",
            )

        mock_instance.build_acts_query.assert_called_once_with(
            test_date,
            language="FRA",
            date_end=test_date_end,
            title_contains=title_filter,
            category_type="RES",
            institution_type="COM",
        )

    def test_invalid_format_raises_before_querying(
        self, client, mock_connector
    ) -> None:
        """Test invalid output formats fail before touching the connector."""
        with pytest.raises(ValueError, match="Unsupported acts output format"):
            client.get_acts("2025-03-27", output_format="unknown")

        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.assert_not_called()
        mock_instance.execute_query.assert_not_called()

    def test_non_string_format_raises_before_querying(
        self, client, mock_connector
    ) -> None:
        """Test output_format only accepts strings or None."""
        with pytest.raises(TypeError, match="output_format must be a string or None"):
            client.get_acts("2025-03-27", output_format=123)

        mock_instance = mock_connector.return_value
        mock_instance.build_acts_query.assert_not_called()
        mock_instance.execute_query.assert_not_called()

    def test_removed_format_specific_methods(self) -> None:
        """Test legacy format-specific methods are no longer exposed."""
        assert not hasattr(EurlexBulletinClient, "get_acts_csv")
        assert not hasattr(EurlexBulletinClient, "get_acts_json")


class TestGetCategoryTypes:
    """Tests for get_category_types method."""

    def test_fetches_category_types(self, client, mock_connector):
        """Test fetching category types from the client."""
        mock_instance = mock_connector.return_value
        mock_instance.build_category_types_query.return_value = "CATEGORY_TYPES_QUERY"
        mock_instance.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"code": {"value": "REG"}, "label": {"value": "Regulation"}},
                    {"code": {"value": "DIR"}, "label": {"value": "Directive"}},
                ]
            }
        }

        result = client.get_category_types(language="ENG")

        mock_instance.build_category_types_query.assert_called_once_with(language="ENG")
        mock_instance.execute_query.assert_called_once_with("CATEGORY_TYPES_QUERY")
        assert len(result) == 2
        assert result[0].code == "REG"
        assert result[0].label == "Regulation"
        assert result[1].code == "DIR"
        assert result[1].label == "Directive"


class TestGetInstitutionTypes:
    """Tests for get_institution_types method."""

    def test_fetches_institution_types(self, client, mock_connector):
        """Test fetching institution types from the client."""
        mock_instance = mock_connector.return_value
        mock_instance.build_institution_types_query.return_value = (
            "INSTITUTION_TYPES_QUERY"
        )
        mock_instance.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"code": {"value": "COM"}, "label": {"value": "Commission"}},
                    {"code": {"value": "ECJ"}, "label": {"value": "Court of Justice"}},
                ]
            }
        }

        result = client.get_institution_types(language="ENG")

        mock_instance.build_institution_types_query.assert_called_once_with(
            language="ENG"
        )
        mock_instance.execute_query.assert_called_once_with("INSTITUTION_TYPES_QUERY")
        assert len(result) == 2
        assert result[0].code == "COM"
        assert result[0].label == "Commission"
        assert result[1].code == "ECJ"
        assert result[1].label == "Court of Justice"
