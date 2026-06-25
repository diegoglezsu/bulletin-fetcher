from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from ..constants import EURLEX_DOMAIN, LANGUAGE_CODE_MAP


def _required_value(binding: Mapping[str, Any], key: str) -> str:
    """Return a required SPARQL binding value and fail with a clear message."""
    try:
        value = binding[key]["value"]
    except KeyError as exc:
        raise KeyError(f"Missing required field '{key}' in SPARQL binding") from exc

    if not isinstance(value, str):
        raise TypeError(f"Field '{key}' value must be a string")
    return value


def _optional_value(binding: Mapping[str, Any], key: str) -> str | None:
    """Return an optional SPARQL binding value when present."""
    value_object = binding.get(key)
    if not isinstance(value_object, Mapping):
        return None

    value = value_object.get("value")
    return value if isinstance(value, str) else None


_ELI_PDF_RE = re.compile(
    rf"https://{re.escape(EURLEX_DOMAIN)}/eli/([^/]+)/(\d{{4}})/(\d+)(?:/oj)?$"
)


def _build_pdf_url(act_uri: str, language: str) -> str | None:
    """Build the EUR-Lex legal-content PDF URL from an ELI URI and language."""
    match = _ELI_PDF_RE.match(act_uri)
    if not match:
        return None
    section = match.group(1)
    year = match.group(2)
    number = match.group(3).zfill(5)
    lang_code = LANGUAGE_CODE_MAP.get(language)
    if lang_code is None:
        return None
    return (
        f"https://{EURLEX_DOMAIN}/legal-content/{lang_code.upper()}"
        f"/TXT/PDF/?uri=OJ:{section}_{year}{number}"
    )


@dataclass
class EurlexOfficialAct:
    act_uri: str
    celex_uri: str
    act_number: str | None
    title: str
    date: date
    section_code: str | None
    subsection_code: str | None
    category_code: str | None
    category_uri: str | None
    category_label: str | None
    institution_code: str | None
    institution_uri: str | None
    institution_label: str | None
    pdf_url: Optional[str] = None

    def _to_dict(self) -> dict[str, str | None]:
        """Return a serializable dict representation of the act."""
        return {
            "act_uri": self.act_uri,
            "celex_uri": self.celex_uri,
            "act_number": self.act_number,
            "title": self.title,
            "date": self.date.isoformat(),
            "section_code": self.section_code,
            "subsection_code": self.subsection_code,
            "category_code": self.category_code,
            "category_uri": self.category_uri,
            "category_label": self.category_label,
            "institution_code": self.institution_code,
            "institution_uri": self.institution_uri,
            "institution_label": self.institution_label,
            "pdf_url": self.pdf_url,
        }

    @classmethod
    def _from_binding(
        cls,
        binding: Mapping[str, Any],
        language: Optional[str] = None,
    ) -> EurlexOfficialAct:
        """Build an EurlexOfficialAct from one SPARQL binding item."""
        act_uri = _required_value(binding, "act")
        pdf_url = _build_pdf_url(act_uri, language) if language else None
        return cls(
            act_uri=act_uri,
            celex_uri=_optional_value(binding, "celexAct") or _optional_value(binding, "celex") or "",
            act_number=_optional_value(binding, "actNumber"),
            title=_required_value(binding, "title"),
            date=date.fromisoformat(_required_value(binding, "date").split("T")[0]),
            section_code=_optional_value(binding, "sectionCode"),
            subsection_code=_optional_value(binding, "subsectionCode"),
            category_code=_optional_value(binding, "categoryCode"),
            category_uri=_optional_value(binding, "categoryUri"),
            category_label=_optional_value(binding, "categoryLabel"),
            institution_code=_optional_value(binding, "institutionCode"),
            institution_uri=_optional_value(binding, "institutionUri"),
            institution_label=_optional_value(binding, "institutionLabel"),
            pdf_url=pdf_url,
        )


@dataclass
class CategoryType:
    """Represents a category type (resource type) from the authority list."""
    code: str
    label: str

    def _to_dict(self) -> dict[str, str]:
        """Return a serializable dict representation of the category type."""
        return {
            "code": self.code,
            "label": self.label,
        }
    
    @classmethod
    def _from_binding(cls, binding: Mapping[str, Any]) -> CategoryType:
        """Build a CategoryType from one SPARQL binding item."""
        return cls(
            code=_required_value(binding, "code"),
            label=_required_value(binding, "label"),
        )

@dataclass
class InstitutionType:
    """Represents an institution type from the authority list."""
    code: str
    label: str

    def _to_dict(self) -> dict[str, str]:
        """Return a serializable dict representation of the institution type."""
        return {
            "code": self.code,
            "label": self.label,
        }
    
    @classmethod
    def _from_binding(cls, binding: Mapping[str, Any]) -> InstitutionType:
        """Build an InstitutionType from one SPARQL binding item."""
        return cls(
            code=_required_value(binding, "code"),
            label=_required_value(binding, "label"),
        )
