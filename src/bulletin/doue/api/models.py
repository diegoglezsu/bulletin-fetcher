from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any


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


@dataclass
class DoueOfficialAct:
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

    def _to_dict(self) -> dict[str, str | None]:
        """Return a serializable dict representation of the act."""
        return {
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
        }

    @classmethod
    def _from_binding(cls, binding: Mapping[str, Any]) -> DoueOfficialAct:
        """Build a DoueOfficialAct from one SPARQL binding item."""
        return cls(
            celex_uri=_required_value(binding, "act"),
            act_number=_optional_value(binding, "actNumber"),
            title=_required_value(binding, "title"),
            date=date.fromisoformat(_required_value(binding, "date")),
            section_code=_optional_value(binding, "sectionCode"),
            subsection_code=_optional_value(binding, "subsectionCode"),
            category_code=_optional_value(binding, "categoryCode"),
            category_uri=_optional_value(binding, "categoryUri"),
            category_label=_optional_value(binding, "categoryLabel"),
            institution_code=_optional_value(binding, "institutionCode"),
            institution_uri=_optional_value(binding, "institutionUri"),
            institution_label=_optional_value(binding, "institutionLabel"),
        )
