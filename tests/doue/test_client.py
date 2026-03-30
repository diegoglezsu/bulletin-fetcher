"""
Unit tests for DoueBulletinClient.
"""

from datetime import date
from unittest.mock import patch

import pytest

from bulletin.doue.client import DoueBulletinClient
from bulletin.doue.constants import SPARQL_ENDPOINT
from bulletin.doue.models import DoueOfficialAct


@pytest.fixture
def mock_connector():
    """Fixture providing a mocked _DoueConnector."""
    with patch("bulletin.doue.client._DoueConnector") as mock:
        yield mock


@pytest.fixture
def client(mock_connector):
    """Fixture providing a DoueBulletinClient with mocked connector."""
    return DoueBulletinClient()


def test_init_with_defaults(mock_connector):
    """Test client initialization with default parameters."""
    DoueBulletinClient()
    mock_connector.assert_called_once_with(
        endpoint=SPARQL_ENDPOINT, timeout=30
    )


def test_init_with_custom_endpoint(mock_connector):
    """Test client initialization with custom endpoint."""
    custom_endpoint = "https://custom.endpoint/sparql"
    DoueBulletinClient(endpoint=custom_endpoint)
    mock_connector.assert_called_once_with(
        endpoint=custom_endpoint, timeout=30
    )


def test_init_with_custom_timeout(mock_connector):
    """Test client initialization with custom timeout."""
    DoueBulletinClient(timeout=60)
    mock_connector.assert_called_once_with(
        endpoint=SPARQL_ENDPOINT, timeout=60
    )


def test_init_with_all_custom_params(mock_connector):
    """Test client initialization with all custom parameters."""
    custom_endpoint = "https://custom.endpoint/sparql"
    custom_timeout = 45
    DoueBulletinClient(
        endpoint=custom_endpoint, timeout=custom_timeout
    )
    mock_connector.assert_called_once_with(
        endpoint=custom_endpoint, timeout=custom_timeout
    )


def test_get_acts_with_valid_date(client, mock_connector):
    """Test fetching acts with a valid ISO date."""
    test_date = "2025-03-27"
    mock_response = {
        "results": {
            "bindings": [
                {"act": {"value": "https://example.com/act1"}}
            ]
        }
    }
    mock_instance = mock_connector.return_value
    mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
    mock_instance.execute_query.return_value = mock_response

    with patch(
        "bulletin.doue.client.parse_results"
    ) as mock_parse:
        mock_parse.return_value = [
            DoueOfficialAct(
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
            test_date, language="ENG"
        )
        mock_instance.execute_query.assert_called_once_with(
            "SPARQL_QUERY"
        )
        mock_parse.assert_called_once_with(mock_response)
        assert len(result) == 1


def test_get_acts_with_custom_language(client, mock_connector):
    """Test fetching acts with a custom language code."""
    test_date = "2025-03-27"
    custom_language = "FRA"
    mock_instance = mock_connector.return_value
    mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
    mock_instance.execute_query.return_value = {"results": {"bindings": []}}

    with patch("bulletin.doue.client.parse_results") as mock_parse:
        mock_parse.return_value = []
        client.get_acts(test_date, language=custom_language)

        mock_instance.build_acts_query.assert_called_once_with(
            test_date, language=custom_language
        )


def test_get_acts_returns_parsed_results(client, mock_connector):
    """Test that get_acts returns the parsed results."""
    test_date = "2025-03-27"
    mock_response = {"results": {"bindings": []}}
    mock_instance = mock_connector.return_value
    mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
    mock_instance.execute_query.return_value = mock_response

    expected_acts = [
        DoueOfficialAct(
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
        DoueOfficialAct(
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

    with patch(
        "bulletin.doue.client.parse_results"
    ) as mock_parse:
        mock_parse.return_value = expected_acts
        result = client.get_acts(test_date)

        assert result == expected_acts
        assert len(result) == 2


def test_get_acts_empty_results(client, mock_connector):
    """Test get_acts with empty results from SPARQL."""
    test_date = "2025-03-27"
    mock_instance = mock_connector.return_value
    mock_instance.build_acts_query.return_value = "SPARQL_QUERY"
    mock_instance.execute_query.return_value = {"results": {"bindings": []}}

    with patch("bulletin.doue.client.parse_results") as mock_parse:
        mock_parse.return_value = []
        result = client.get_acts(test_date)

        assert result == []