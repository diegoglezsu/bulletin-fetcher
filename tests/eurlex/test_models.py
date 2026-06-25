"""Unit tests for models and helper functions."""

import pytest

from bulletin.eurlex.api.models import (
    _build_pdf_url,
    _required_value,
    CategoryType,
    InstitutionType,
)


class TestRequiredValue:
    """Tests for _required_value helper."""

    def test_non_string_value_raises_type_error(self) -> None:
        binding = {"key": {"value": 123}}
        with pytest.raises(TypeError, match="Field 'key' value must be a string"):
            _required_value(binding, "key")


class TestBuildPdfUrl:
    """Tests for _build_pdf_url helper."""

    def test_matching_eli_uri_with_valid_language(self) -> None:
        url = _build_pdf_url(
            "https://eur-lex.europa.eu/eli/C/2025/6050", "ENG"
        )
        assert url == (
            "https://eur-lex.europa.eu/legal-content/EN"
            "/TXT/PDF/?uri=OJ:C_202506050"
        )

    def test_matching_eli_uri_with_oj_suffix(self) -> None:
        url = _build_pdf_url(
            "https://eur-lex.europa.eu/eli/C/2025/6050/oj", "SPA"
        )
        assert url == (
            "https://eur-lex.europa.eu/legal-content/ES"
            "/TXT/PDF/?uri=OJ:C_202506050"
        )

    def test_number_zero_padded(self) -> None:
        url = _build_pdf_url(
            "https://eur-lex.europa.eu/eli/C/2025/50", "ENG"
        )
        assert url == (
            "https://eur-lex.europa.eu/legal-content/EN"
            "/TXT/PDF/?uri=OJ:C_202500050"
        )

    def test_non_matching_uri_returns_none(self) -> None:
        url = _build_pdf_url(
            "https://publications.europa.eu/resource/celex/32025R0001", "ENG"
        )
        assert url is None

    def test_unsupported_language_returns_none(self) -> None:
        url = _build_pdf_url(
            "https://eur-lex.europa.eu/eli/C/2025/6050", "XYZ"
        )
        assert url is None

    def test_none_language_returns_none(self) -> None:
        url = _build_pdf_url(
            "https://eur-lex.europa.eu/eli/C/2025/6050", None
        )
        assert url is None


class TestCategoryTypeToDict:
    """Tests for CategoryType._to_dict."""

    def test_returns_correct_dict(self) -> None:
        ct = CategoryType(code="REG", label="Regulation")
        assert ct._to_dict() == {"code": "REG", "label": "Regulation"}


class TestInstitutionTypeToDict:
    """Tests for InstitutionType._to_dict."""

    def test_returns_correct_dict(self) -> None:
        it = InstitutionType(code="COM", label="European Commission")
        assert it._to_dict() == {"code": "COM", "label": "European Commission"}
