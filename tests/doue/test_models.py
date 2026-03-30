"""Unit tests for model parsing utilities."""

from datetime import date

import pytest

from bulletin.doue.api.models import DoueOfficialAct, parse_results


def test_parse_results_with_required_fields_only() -> None:
    response = {
        "results": {
            "bindings": [
                {
                    "act": {"value": "http://publications.europa.eu/resource/celex/32025R0001"},
                    "title": {"value": "Regulation (EU) 2025/1"},
                    "date": {"value": "2025-01-01"},
                }
            ]
        }
    }

    acts = parse_results(response)

    assert acts == [
        DoueOfficialAct(
            celex_uri="http://publications.europa.eu/resource/celex/32025R0001",
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
