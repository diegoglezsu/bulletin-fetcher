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

    @classmethod
    def from_binding(cls, binding: Mapping[str, Any]) -> DoueOfficialAct:
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


def parse_results(results: Mapping[str, Any]) -> list[DoueOfficialAct]:
    """Parse SPARQL results into a list of DoueOfficialAct objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError("Invalid SPARQL response: missing 'results.bindings'") from exc

    if not isinstance(bindings, list):
        raise TypeError("Invalid SPARQL response: 'bindings' must be a list")

    acts: list[DoueOfficialAct] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError("Invalid SPARQL response: each binding must be a mapping")
        acts.append(DoueOfficialAct.from_binding(binding))

    return acts