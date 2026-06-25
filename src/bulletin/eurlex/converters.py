from collections.abc import Mapping
import csv
import importlib
import io
from typing import Any, Optional

from .api.models import EurlexOfficialAct, CategoryType, InstitutionType

INVALID_SPARQL_RESPONSE_ERROR = "Invalid SPARQL response: {}"
MISSING_DEPENDENCY_ERROR = "Missing dependency: {}. Install it or install bulletin-fetcher[{}]."
MISSING_RESULTS_BINDINGS_ERROR = "missing 'results.bindings' key."
BINDINGS_MUST_BE_LIST_ERROR = "'results.bindings' must be a list."


def parse_acts_results(
    results: Mapping[str, Any],
    language: Optional[str] = None,
) -> list[EurlexOfficialAct]:
    """Parse SPARQL results into a list of EurlexOfficialAct objects.

    Args:
        results: The SPARQL JSON response.
        language: ISO 639-3 language code (e.g. "SPA"). When provided,
            each act's ``pdf_url`` will be computed.
    """
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError(
            MISSING_RESULTS_BINDINGS_ERROR
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
        acts.append(EurlexOfficialAct._from_binding(binding, language=language))

    return acts


def acts_to_csv(acts: list[EurlexOfficialAct]) -> str:
    """Serialize a list of acts to CSV format."""
    fieldnames = [
        "act_uri",
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
        "pdf_url",
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
            MISSING_DEPENDENCY_ERROR.format("pandas", "pandas")
        ) from exc

    return pandas.DataFrame(acts_to_json(acts))


def acts_to_xml(acts: list[EurlexOfficialAct]) -> str:
    """Serialize a list of acts to XML format."""
    try:
        dicttoxml = importlib.import_module("dicttoxml")
    except ImportError as exc:
        raise ImportError(
            MISSING_DEPENDENCY_ERROR.format("dicttoxml", "dicttoxml")
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
            MISSING_RESULTS_BINDINGS_ERROR
        ) from exc

    if not isinstance(bindings, list):
        raise TypeError(
            INVALID_SPARQL_RESPONSE_ERROR.format(BINDINGS_MUST_BE_LIST_ERROR)
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
            MISSING_RESULTS_BINDINGS_ERROR
        ) from exc

    if not isinstance(bindings, list):
        raise TypeError(
            INVALID_SPARQL_RESPONSE_ERROR.format(BINDINGS_MUST_BE_LIST_ERROR)
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
