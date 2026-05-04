"""High-level client for querying EU Official Journal (EUR-Lex) acts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Union

if TYPE_CHECKING:
    import pandas as pd

from ..repository._connector import EurlexConnector
from ..constants import (
    ACTS_OUTPUT_FORMAT_CSV,
    ACTS_OUTPUT_FORMAT_XML,
    ACTS_OUTPUT_FORMAT_JSON,
    ACTS_OUTPUT_FORMAT_OBJECTS,
    ACTS_OUTPUT_FORMAT_PANDASDF,
    DEFAULT_LANGUAGE,
    SPARQL_ENDPOINT,
    SUPPORTED_ACTS_OUTPUT_FORMATS,
)
from ..converters import (
    acts_to_csv,
    acts_to_dataframe,
    acts_to_json,
    acts_to_xml,
    parse_acts_results,
    parse_category_types_results,
    parse_institution_types_results,
)
from .models import EurlexOfficialAct, CategoryType, InstitutionType

_ActsOutput = Union[
    List[EurlexOfficialAct],
    List[Dict[str, Optional[str]]],
    str,
    "pd.DataFrame",
]


def _normalize_acts_output_format(output_format: Optional[str]) -> str:
    """Normalize and validate the requested acts output format."""
    if output_format is None:
        return ACTS_OUTPUT_FORMAT_OBJECTS

    if not isinstance(output_format, str):
        raise TypeError("output_format must be a string or None")

    normalized = output_format.strip().lower()
    if normalized in SUPPORTED_ACTS_OUTPUT_FORMATS:
        return normalized

    supported = ", ".join(sorted(SUPPORTED_ACTS_OUTPUT_FORMATS))
    raise ValueError(
        f"Unsupported acts output format: {output_format!r}. "
        f"Supported formats are: {supported}."
    )


def _format_acts(acts: list[EurlexOfficialAct], output_format: str) -> _ActsOutput:
    """Return acts using the requested output format."""
    if output_format == ACTS_OUTPUT_FORMAT_JSON:
        return acts_to_json(acts)
    if output_format == ACTS_OUTPUT_FORMAT_CSV:
        return acts_to_csv(acts)
    if output_format == ACTS_OUTPUT_FORMAT_PANDASDF:
        return acts_to_dataframe(acts)
    if output_format == ACTS_OUTPUT_FORMAT_XML:
        return acts_to_xml(acts)
    return acts


class EurlexBulletinClient:
    """Client to query EU Official Journal acts."""

    def __init__(self, endpoint: str = SPARQL_ENDPOINT, timeout: int = 300):
        self._connector = EurlexConnector(endpoint=endpoint, timeout=timeout)

    def get_acts(
        self,
        date: str,
        language: str = DEFAULT_LANGUAGE,
        date_end: Optional[str] = None,
        title_contains: Optional[str] = None,
        category_type: Optional[str] = None,
        institution_type: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> _ActsOutput:
        """Fetch Official Journal acts for a given publication date.

        Args:
            date: Publication date in ISO format (e.g. "2025-03-27").
            language: ISO Language code (default: "ENG"). Supported values are defined in `LANGUAGE_CODE_MAP`. Examples: "ENG", "FRA", "DEU", "SPA"...
            date_end: End date in ISO format (e.g. "2025-03-27"). If provided, fetch acts published between `date` and `date_end` inclusive.
            title_contains: Case-insensitive substring filter on title.
            category_type: Filter by category type code (e.g. "RES" for Resolution, "ANNOUNC" for Announcement...). More types available at <http://publications.europa.eu/resource/authority/resource-type>. Optional.
            institution_type: Filter by institution type code (e.g. "CONSIL" for Council of the European Union, "COM" for Commission...). More types available at <http://publications.europa.eu/resource/authority/corporate-body>. Optional.
            output_format: Optional output format. Use None or "objects" to return a list of `EurlexOfficialAct` objects, "json" to return a JSON-compatible list of dictionaries, "csv" to return CSV text, "xml" to return XML text, or "df" to return a pandas DataFrame.
        Returns:
            Acts in the requested output format.

        """
        normalized_output_format = _normalize_acts_output_format(output_format)
        query = self._connector.build_acts_query(
            date,
            language=language,
            date_end=date_end,
            title_contains=title_contains,
            category_type=category_type,
            institution_type=institution_type,
        )
        response = self._connector.execute_query(query)
        acts = parse_acts_results(response)
        return _format_acts(acts, normalized_output_format)

    def get_category_types(
        self, language: str = DEFAULT_LANGUAGE
    ) -> list[CategoryType]:
        """Fetch the list of possible category types from the authority list. This method may last a few minutes due to the size of the authority list.

        Args:
            language: Language code (default: "ENG"). Examples: "ENG", "SPA", "FRA"...

        Returns:
            A list of CategoryType objects with 'code' and 'label' attributes.
        """
        query = self._connector.build_category_types_query(language=language)
        response = self._connector.execute_query(query)
        return parse_category_types_results(response)

    def get_institution_types(
        self, language: str = DEFAULT_LANGUAGE
    ) -> list[InstitutionType]:
        """Fetch the list of possible institution types from the authority list. This method may last a few minutes due to the size of the authority list.

        Args:
            language: Language code (default: "ENG"). Examples: "ENG", "SPA", "FRA"...

        Returns:
            A list of InstitutionType objects with 'code' and 'label' attributes.
        """
        query = self._connector.build_institution_types_query(language=language)
        response = self._connector.execute_query(query)
        return parse_institution_types_results(response)
