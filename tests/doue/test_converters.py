"""Unit tests for converters utilities."""

from datetime import date

import pytest

from bulletin.doue.converters import acts_to_csv, parse_results
from bulletin.doue.api.models import DoueOfficialAct


def test_parse_results_with_required_fields_only() -> None:
    response = {
        "results": {
            "bindings": [
                {
                    "act": {
                        "value": "https://publications.europa.eu/resource/celex/32025R0001"
                    },
                    "title": {"value": "Regulation (EU) 2025/1"},
                    "date": {"value": "2025-01-01"},
                }
            ]
        }
    }

    acts = parse_results(response)

    assert acts == [
        DoueOfficialAct(
            celex_uri="https://publications.europa.eu/resource/celex/32025R0001",
            act_number=None,
            title="Regulation (EU) 2025/1",
            date=date(2025, 1, 1),
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


def test_parse_results_with_all_supported_optional_fields() -> None:
    response = {
        "results": {
            "bindings": [
                {
                    "act": {"value": "https://example.com/act1"},
                    "actNumber": {"value": "2025/1"},
                    "title": {"value": "Act 1"},
                    "date": {"value": "2025-03-27"},
                    "sectionCode": {"value": "I"},
                    "subsectionCode": {"value": "A"},
                    "categoryCode": {"value": "REG"},
                    "categoryUri": {"value": "https://example.com/category"},
                    "categoryLabel": {"value": "Regulations"},
                    "institutionCode": {"value": "COM"},
                    "institutionUri": {"value": "https://example.com/institution"},
                    "institutionLabel": {"value": "European Commission"},
                }
            ]
        }
    }

    acts = parse_results(response)

    assert acts[0].act_number == "2025/1"
    assert acts[0].section_code == "I"
    assert acts[0].institution_label == "European Commission"


def test_parse_results_raises_for_missing_required_fields() -> None:
    response = {
        "results": {
            "bindings": [
                {
                    "title": {"value": "Act without celex"},
                    "date": {"value": "2025-01-01"},
                }
            ]
        }
    }

    with pytest.raises(KeyError, match="Missing required field 'act'"):
        parse_results(response)


def test_parse_results_raises_for_invalid_date() -> None:
    response = {
        "results": {
            "bindings": [
                {
                    "act": {"value": "https://example.com/act"},
                    "title": {"value": "Invalid date act"},
                    "date": {"value": "2025-99-99"},
                }
            ]
        }
    }

    with pytest.raises(ValueError):
        parse_results(response)


def test_parse_results_raises_for_invalid_bindings_type() -> None:
    response = {"results": {"bindings": {"not": "a-list"}}}

    with pytest.raises(TypeError, match="'bindings' must be a list"):
        parse_results(response)


def test_parse_results_raises_for_invalid_binding_entry() -> None:
    response = {"results": {"bindings": ["not-a-mapping"]}}

    with pytest.raises(TypeError, match="each binding must be a mapping"):
        parse_results(response)


def test_acts_to_csv_serializes_rows() -> None:
    acts = [
        DoueOfficialAct(
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
    ]

    csv_text = acts_to_csv(acts)
    rows = csv_text.splitlines()

    assert rows[0] == (
        "\"celex_uri\",\"act_number\",\"title\",\"date\",\"section_code\"," 
        "\"subsection_code\",\"category_code\",\"category_uri\",\"category_label\"," 
        "\"institution_code\",\"institution_uri\",\"institution_label\""
    )
    assert rows[1].startswith(
        "\"https://example.com/act1\",\"2025/1\",\"Act 1\",\"2025-03-27\""
    )
