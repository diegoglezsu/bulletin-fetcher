from collections.abc import Mapping
import csv
import importlib
import io
from typing import Any

from .api.models import EurlexOfficialAct, CategoryType, InstitutionType

INVALID_SPARQL_RESPONSE_ERROR = "Invalid SPARQL response: {}"


def parse_acts_results(results: Mapping[str, Any]) -> list[EurlexOfficialAct]:
    """Parse SPARQL results into a list of EurlexOfficialAct objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError(
            INVALID_SPARQL_RESPONSE_ERROR.format("missing 'results.bindings'")
        ) from exc

    if not isinstance(bindings, list):
        raise TypeError(
            INVALID_SPARQL_RESPONSE_ERROR.format("'bindings' must be a list")
        )

    acts: list[EurlexOfficialAct] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError(
                INVALID_SPARQL_RESPONSE_ERROR.format(
                    "each Act binding must be a mapping"
                )
            )
        acts.append(EurlexOfficialAct._from_binding(binding))

    return acts


def acts_to_csv(acts: list[EurlexOfficialAct]) -> str:
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


def acts_to_json(acts: list[EurlexOfficialAct]) -> list[dict]:
    """Serialize a list of acts to JSON format."""
    return [act._to_dict() for act in acts]


def acts_to_dataframe(acts: list[EurlexOfficialAct]) -> Any:
    """Serialize a list of acts to a pandas DataFrame."""
    try:
        pandas = importlib.import_module("pandas")
    except ImportError as exc:
        raise ImportError(
            "pandas is required to use output_format='df'. "
            "Install pandas or install bulletin-fetcher[pandas]."
        ) from exc

    return pandas.DataFrame(acts_to_json(acts))


def acts_to_xml(acts: list[EurlexOfficialAct]) -> str:
    """Serialize a list of acts to XML format."""
    try:
        dicttoxml = importlib.import_module("dicttoxml")
    except ImportError as exc:
        raise ImportError(
            "dicttoxml is required to use output_format='xml'. "
            "Install dicttoxml or install bulletin-fetcher[dicttoxml]."
        ) from exc

    acts_dicts = acts_to_json(acts)
    xml_bytes = dicttoxml.dicttoxml(acts_dicts, custom_root="acts", attr_type=False)
    return xml_bytes.decode("utf-8")


def parse_category_types_results(results: Mapping[str, Any]) -> list[CategoryType]:
    """Parse SPARQL results into a list of CategoryType objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError(
            INVALID_SPARQL_RESPONSE_ERROR.format("missing 'results.bindings'")
        ) from exc

    if not isinstance(bindings, list):
        raise TypeError(
            INVALID_SPARQL_RESPONSE_ERROR.format("'bindings' must be a list")
        )

    types: list[CategoryType] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError(
                INVALID_SPARQL_RESPONSE_ERROR.format(
                    "each category binding must be a mapping"
                )
            )
        types.append(CategoryType._from_binding(binding))

    return types


def parse_institution_types_results(
    results: Mapping[str, Any],
) -> list[InstitutionType]:
    """Parse SPARQL results into a list of InstitutionType objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError(
            INVALID_SPARQL_RESPONSE_ERROR.format("missing 'results.bindings'")
        ) from exc

    if not isinstance(bindings, list):
        raise TypeError(
            INVALID_SPARQL_RESPONSE_ERROR.format("'bindings' must be a list")
        )

    types: list[InstitutionType] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError(
                INVALID_SPARQL_RESPONSE_ERROR.format(
                    "each institution binding must be a mapping"
                )
            )
        types.append(InstitutionType._from_binding(binding))

    return types
