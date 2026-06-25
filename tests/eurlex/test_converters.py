"""Unit tests for converters utilities."""

from datetime import date
import sys
from types import SimpleNamespace

import pytest

from bulletin.eurlex.converters import (
    acts_to_csv,
    acts_to_dataframe,
    acts_to_json,
    acts_to_xml,
    parse_acts_results,
    parse_category_types_results,
    parse_institution_types_results,
)
from bulletin.eurlex.api.models import EurlexOfficialAct, CategoryType, InstitutionType


class TestParseActsResults:
    """Tests for parse_acts_results converter."""

    def test_with_required_fields_only(self) -> None:
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

        acts = parse_acts_results(response)

        assert acts == [
            EurlexOfficialAct(
                act_uri="https://publications.europa.eu/resource/celex/32025R0001",
                celex_uri="",
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

    def test_with_all_supported_optional_fields(self) -> None:
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

        acts = parse_acts_results(response)

        assert acts[0].act_number == "2025/1"
        assert acts[0].section_code == "I"
        assert acts[0].institution_label == "European Commission"

    def test_raises_for_missing_required_fields(self) -> None:
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
            parse_acts_results(response)

    def test_raises_for_invalid_date(self) -> None:
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
            parse_acts_results(response)

    def test_raises_for_invalid_bindings_type(self) -> None:
        response = {"results": {"bindings": {"not": "a-list"}}}

        with pytest.raises(TypeError, match="'bindings' must be a list"):
            parse_acts_results(response)

    def test_with_language_sets_pdf_url(self) -> None:
        """Test that language param produces pdf_url on acts."""
        response = {
            "results": {
                "bindings": [
                    {
                        "act": {
                            "value": "https://eur-lex.europa.eu/eli/C/2025/6050"
                        },
                        "title": {"value": "Test Act"},
                        "date": {"value": "2025-01-01"},
                    }
                ]
            }
        }

        acts = parse_acts_results(response, language="ENG")
        assert acts[0].pdf_url == (
            "https://eur-lex.europa.eu/legal-content/EN"
            "/TXT/PDF/?uri=OJ:C_202506050"
        )

    def test_raises_for_invalid_binding_entry(self) -> None:
        """Test that parsing raises error when binding is not a mapping."""
        response = {"results": {"bindings": ["not-a-mapping"]}}

        with pytest.raises(TypeError, match="each Act binding must be a mapping"):
            parse_acts_results(response)

    def test_raises_for_missing_bindings_key(self) -> None:
        """Test that parsing raises error when results.bindings is missing."""
        response = {"results": {}}

        with pytest.raises(KeyError, match="missing 'results.bindings' key"):
            parse_acts_results(response)


class TestActsToCsv:
    """Tests for acts_to_csv converter."""

    def test_serializes_rows(self) -> None:
        acts = [
            EurlexOfficialAct(
                act_uri="https://eur-lex.europa.eu/eli/act1",
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
            '"act_uri","celex_uri","act_number","title","date","section_code",'
            '"subsection_code","category_code","category_uri","category_label",'
            '"institution_code","institution_uri","institution_label","pdf_url"'
        )
        assert rows[1].startswith(
            '"https://eur-lex.europa.eu/eli/act1","https://example.com/act1",'
            '"2025/1","Act 1","2025-03-27"'
        )


class TestActsToJson:
    """Tests for acts_to_json converter."""

    def test_serializes_rows(self) -> None:
        acts = [
            EurlexOfficialAct(
                act_uri="https://eur-lex.europa.eu/eli/act1",
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

        json_list = acts_to_json(acts)

        assert isinstance(json_list, list)
        assert len(json_list) == 1
        assert json_list[0]["act_uri"] == "https://eur-lex.europa.eu/eli/act1"
        assert json_list[0]["celex_uri"] == "https://example.com/act1"
        assert json_list[0]["act_number"] == "2025/1"
        assert json_list[0]["title"] == "Act 1"
        assert json_list[0]["date"] == "2025-03-27"
        assert json_list[0]["section_code"] is None

    def test_serializes_empty_list(self) -> None:
        assert acts_to_json([]) == []


class TestActsToDataFrame:
    """Tests for acts_to_dataframe converter."""

    def test_serializes_rows(self, monkeypatch) -> None:
        class FakeDataFrame:
            def __init__(self, rows):
                self.rows = rows

        fake_pandas = SimpleNamespace(DataFrame=FakeDataFrame)
        monkeypatch.setitem(sys.modules, "pandas", fake_pandas)
        acts = [
            EurlexOfficialAct(
                act_uri="https://eur-lex.europa.eu/eli/act1",
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

        dataframe = acts_to_dataframe(acts)

        assert isinstance(dataframe, FakeDataFrame)
        assert dataframe.rows == [
            {
                "act_uri": "https://eur-lex.europa.eu/eli/act1",
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
                "pdf_url": None,
            }
        ]

    def test_raises_clear_error_when_pandas_is_missing(self, monkeypatch) -> None:
        def raise_import_error(name):
            if name == "pandas":
                raise ImportError("pandas unavailable")
            return __import__(name)

        monkeypatch.setattr(
            "bulletin.eurlex.converters.importlib.import_module", raise_import_error
        )

        with pytest.raises(
            ImportError,
            match=r"Missing dependency: pandas\. Install it or install bulletin-fetcher\[pandas\]\.",
        ):
            acts_to_dataframe([])


class TestActsToXml:
    """Tests for acts_to_xml converter."""

    def test_serializes_rows(self, monkeypatch) -> None:
        recorded_call = {}

        def fake_dicttoxml(obj, custom_root, attr_type):
            recorded_call["obj"] = obj
            recorded_call["custom_root"] = custom_root
            recorded_call["attr_type"] = attr_type
            return b"<acts><test>success</test></acts>"

        fake_dicttoxml_module = SimpleNamespace(dicttoxml=fake_dicttoxml)
        monkeypatch.setitem(sys.modules, "dicttoxml", fake_dicttoxml_module)

        acts = [
            EurlexOfficialAct(
                act_uri="https://eur-lex.europa.eu/eli/act1",
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

        xml_result = acts_to_xml(acts)

        assert xml_result == "<acts><test>success</test></acts>"
        assert recorded_call == {
            "obj": [
                {
                    "act_uri": "https://eur-lex.europa.eu/eli/act1",
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
                    "pdf_url": None,
                }
            ],
            "custom_root": "acts",
            "attr_type": False,
        }

    def test_raises_clear_error_when_dicttoxml_is_missing(self, monkeypatch) -> None:
        def raise_import_error(name):
            if name == "dicttoxml":
                raise ImportError("dicttoxml unavailable")
            return __import__(name)

        monkeypatch.setattr(
            "bulletin.eurlex.converters.importlib.import_module", raise_import_error
        )

        with pytest.raises(
            ImportError,
            match=r"Missing dependency: dicttoxml\. Install it or install bulletin-fetcher\[dicttoxml\]\.",
        ):
            acts_to_xml([])


class TestParseCategoryTypesResults:
    """Tests for parse_category_types_results converter."""

    def test_with_valid_data(self) -> None:
        response = {
            "results": {
                "bindings": [
                    {"code": {"value": "REG"}, "label": {"value": "Regulation"}},
                    {"code": {"value": "DIR"}, "label": {"value": "Directive"}},
                ]
            }
        }
        types = parse_category_types_results(response)
        assert len(types) == 2
        assert types[0] == CategoryType(code="REG", label="Regulation")
        assert types[1] == CategoryType(code="DIR", label="Directive")

    def test_with_single_type(self) -> None:
        response = {
            "results": {
                "bindings": [
                    {"code": {"value": "RES"}, "label": {"value": "Resolution"}}
                ]
            }
        }
        types = parse_category_types_results(response)
        assert len(types) == 1
        assert types[0].code == "RES"
        assert types[0].label == "Resolution"

    def test_raises_for_missing_required_code(self) -> None:
        response = {"results": {"bindings": [{"label": {"value": "Regulation"}}]}}
        with pytest.raises(KeyError, match="Missing required field 'code'"):
            parse_category_types_results(response)

    def test_raises_for_missing_required_label(self) -> None:
        response = {"results": {"bindings": [{"code": {"value": "REG"}}]}}
        with pytest.raises(KeyError, match="Missing required field 'label'"):
            parse_category_types_results(response)

    def test_raises_for_invalid_bindings_type(self) -> None:
        response = {"results": {"bindings": {"not": "a-list"}}}
        with pytest.raises(
            TypeError,
            match=r"Invalid SPARQL response: 'results\.bindings' must be a list\.",
        ):
            parse_category_types_results(response)

    def test_raises_for_invalid_binding_entry(self) -> None:
        response = {"results": {"bindings": ["not-a-mapping"]}}
        with pytest.raises(TypeError, match="each category binding must be a mapping"):
            parse_category_types_results(response)

    def test_raises_for_missing_bindings(self) -> None:
        response = {"results": {}}
        with pytest.raises(KeyError, match=r"missing 'results\.bindings' key\."):
            parse_category_types_results(response)

class TestParseInstitutionTypesResults:
    """Tests for parse_institution_types_results converter."""

    def test_with_valid_data(self) -> None:
        response = {
            "results": {
                "bindings": [
                    {
                        "code": {"value": "COM"},
                        "label": {"value": "European Commission"},
                    },
                    {
                        "code": {"value": "PARL"},
                        "label": {"value": "European Parliament"},
                    },
                ]
            }
        }
        types = parse_institution_types_results(response)
        assert len(types) == 2
        assert types[0] == InstitutionType(code="COM", label="European Commission")
        assert types[1] == InstitutionType(code="PARL", label="European Parliament")

    def test_with_single_type(self) -> None:
        response = {
            "results": {
                "bindings": [
                    {
                        "code": {"value": "COM"},
                        "label": {"value": "European Commission"},
                    }
                ]
            }
        }
        types = parse_institution_types_results(response)
        assert len(types) == 1
        assert types[0].code == "COM"
        assert types[0].label == "European Commission"

    def test_raises_for_missing_required_code(self) -> None:
        response = {
            "results": {"bindings": [{"label": {"value": "European Commission"}}]}
        }
        with pytest.raises(KeyError, match="Missing required field 'code'"):
            parse_institution_types_results(response)

    def test_raises_for_missing_required_label(self) -> None:
        response = {"results": {"bindings": [{"code": {"value": "REG"}}]}}
        with pytest.raises(KeyError, match="Missing required field 'label'"):
            parse_institution_types_results(response)

    def test_raises_for_invalid_bindings_type(self) -> None:
        response = {"results": {"bindings": {"not": "a-list"}}}
        with pytest.raises(
            TypeError,
            match=r"Invalid SPARQL response: 'results\.bindings' must be a list\.",
        ):
            parse_institution_types_results(response)

    def test_raises_for_invalid_binding_entry(self) -> None:
        response = {"results": {"bindings": ["not-a-mapping"]}}
        with pytest.raises(
            TypeError, match="each institution binding must be a mapping"
        ):
            parse_institution_types_results(response)

    def test_raises_for_missing_bindings(self) -> None:
        response = {"results": {}}
        with pytest.raises(KeyError, match=r"missing 'results\.bindings' key\."):
            parse_institution_types_results(response)


