from collections.abc import Mapping
import csv
import io
from typing import Any

from .api.models import DoueOfficialAct, CategoryType, InstitutionType

INVALID_SPARQL_RESPONSE_ERROR = "Invalid SPARQL response: {}"


def parse_acts_results(results: Mapping[str, Any]) -> list[DoueOfficialAct]:
    """Parse SPARQL results into a list of DoueOfficialAct objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError(INVALID_SPARQL_RESPONSE_ERROR.format("missing 'results.bindings'")) from exc

    if not isinstance(bindings, list):
        raise TypeError(INVALID_SPARQL_RESPONSE_ERROR.format("'bindings' must be a list"))

    acts: list[DoueOfficialAct] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError(INVALID_SPARQL_RESPONSE_ERROR.format("each Act binding must be a mapping"))
        acts.append(DoueOfficialAct._from_binding(binding))

    return acts


def acts_to_csv(acts: list[DoueOfficialAct]) -> str:
    """Serialize a list of acts to CSV format."""
    fieldnames = [
        "celex_uri",
        "act_number",
        "title",
        "date",
        "section_code",
        "subsection_code",
        "category_code",
        "category_uri",
        "category_label",
        "institution_code",
        "institution_uri",
        "institution_label",
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for act in acts:
        writer.writerow(act._to_dict())
    return buffer.getvalue()


def parse_category_types_results(results: Mapping[str, Any]) -> list[CategoryType]:
    """Parse SPARQL results into a list of CategoryType objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError(INVALID_SPARQL_RESPONSE_ERROR.format("missing 'results.bindings'")) from exc

    if not isinstance(bindings, list):
        raise TypeError(INVALID_SPARQL_RESPONSE_ERROR.format("'bindings' must be a list"))

    types: list[CategoryType] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError(INVALID_SPARQL_RESPONSE_ERROR.format("each category binding must be a mapping"))
        types.append(CategoryType._from_binding(binding))

    return types


def parse_institution_types_results(results: Mapping[str, Any]) -> list[InstitutionType]:
    """Parse SPARQL results into a list of InstitutionType objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError(INVALID_SPARQL_RESPONSE_ERROR.format("missing 'results.bindings'")) from exc

    if not isinstance(bindings, list):
        raise TypeError(INVALID_SPARQL_RESPONSE_ERROR.format("'bindings' must be a list"))

    types: list[InstitutionType] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError(INVALID_SPARQL_RESPONSE_ERROR.format("each institution binding must be a mapping"))
        types.append(InstitutionType._from_binding(binding))

    return types