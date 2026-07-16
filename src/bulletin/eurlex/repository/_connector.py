"""Connector for the EUR-Lex / Cellar SPARQL endpoint and Cellar REST API.

Handles query building and HTTP communication.
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Union
from urllib.parse import quote

import requests  # type: ignore

from ..constants import (
    SPARQL_ENDPOINT,
    LANGUAGE_CODE_MAP,
    DEFAULT_LANGUAGE,
    CELLAR_DOMAIN,
    ACT_CONTENT_FORMAT_HTML,
    ACT_CONTENT_FORMAT_PDF,
    SUPPORTED_ACT_CONTENT_FORMATS,
)
from ..exceptions import EndpointError, QueryError

_CONTENT_ACCEPT_HEADERS = {
    ACT_CONTENT_FORMAT_HTML: (
        "application/xhtml+xml, text/html;q=0.9, application/xml;q=0.8, "
        "text/xml;q=0.7"
    ),
    ACT_CONTENT_FORMAT_PDF: "application/pdf",
}


class EurlexConnector:
    """Connector class for the EUR-Lex / Cellar SPARQL endpoint and REST API."""

    def __init__(self, endpoint: str = SPARQL_ENDPOINT, timeout: int = 300):
        self.endpoint = endpoint
        self.timeout = timeout

    def build_acts_query(
        self,
        date: str,
        language: str = DEFAULT_LANGUAGE,
        date_end: Optional[str] = None,
        title_contains: Optional[str] = None,
        category_type: Optional[str] = None,
        institution_type: Optional[str] = None,
    ) -> str:
        """Build a SPARQL query for Official Journal acts on a given date.

        Args:
            date: Publication date in ISO format (e.g. "2025-03-27").
            date_end: End date in ISO format (YYYY-MM-DD). If provided, fetch acts published between `date` and `date_end` inclusive.
            title_contains: Case-insensitive substring filter on title.
            category_type: Filter by category type code (e.g. "RES" for Resolution). Optional.
            institution_type: Filter by institution type code (e.g. "COM" for Commission). Optional.
            language: ISO language code (default: "ENG").

        Returns:
            The SPARQL query string.

        Raises:
            QueryError: If the date format is invalid.
        """
        # Basic validation
        _validate_date(date)

        if date_end is not None:
            _validate_date(date_end)
            if _parse_date(date_end) < _parse_date(date):
                raise QueryError("date_end must be on or after date.")

        if title_contains is not None:
            title_contains = title_contains.strip()
            if not title_contains:
                raise QueryError("title_contains filter cannot be empty.")

        if category_type is not None:
            category_type = category_type.strip()
            if not category_type:
                raise QueryError("category_type filter cannot be empty.")

        if institution_type is not None:
            institution_type = institution_type.strip()
            if not institution_type:
                raise QueryError("institution_type filter cannot be empty.")

        lang_code = LANGUAGE_CODE_MAP.get(language)
        if lang_code is None:
            raise QueryError(
                f"Unsupported language: '{language}'. "
                f"Supported: {', '.join(sorted(LANGUAGE_CODE_MAP))}"
            )

        language_uri = f"http://{CELLAR_DOMAIN}/resource/authority/language/{language}"

        date_filters: list[str] = self._get_date_filters(date, date_end)
        title_filter = self._get_title_filter(title_contains)
        category_block = self._get_resource_subquery_block(
            predicate="cdm:work_has_resource-type",
            candidate_var="categoryCandidate",
            output_var="categoryUriStr",
            code=category_type,
        )
        institution_block = self._get_resource_subquery_block(
            predicate="cdm:work_created_by_agent",
            candidate_var="institutionCandidate",
            output_var="institutionUriStr",
            code=institution_type,
        )

        query_template = """
            PREFIX cdm: <http://{cellar_domain}/ontology/cdm#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT DISTINCT
            ?act
            ?celexAct
            ?actNumber
            ?title
            ?date
            ?sectionCode
            ?subsectionCode
            ?categoryCode
            ?categoryUri
            ?categoryLabel
            ?institutionCode
            ?institutionUri
            ?institutionLabel
            WHERE {{
            ?c_act (
                cdm:official-journal-act_date_publication
                | cdm:resource_legal_published_in_official-journal/cdm:publication_general_date_publication
            ) ?date .
            {date_filters_str}

            OPTIONAL {{
                SELECT ?c_act (MIN(STR(?eliCandidate)) AS ?eliUriStr)
                WHERE {{
                    ?c_act owl:sameAs ?eliCandidate .
                    FILTER(CONTAINS(STR(?eliCandidate), "/resource/eli/"))
                }}
                GROUP BY ?c_act
            }}

            OPTIONAL {{
                SELECT ?c_act (MIN(STR(?celexCandidate)) AS ?celexUriStr)
                WHERE {{
                    ?c_act owl:sameAs ?celexCandidate .
                    FILTER(CONTAINS(STR(?celexCandidate), "/resource/celex/"))
                }}
                GROUP BY ?c_act
            }}

            OPTIONAL {{
                SELECT ?c_act (MIN(STR(?ojCandidate)) AS ?ojUriStr)
                WHERE {{
                    ?c_act owl:sameAs ?ojCandidate .
                    FILTER(CONTAINS(STR(?ojCandidate), "/resource/oj/"))
                }}
                GROUP BY ?c_act
            }}

            BIND(COALESCE(?eliUriStr, ?celexUriStr, ?ojUriStr) AS ?rawActStr)
            FILTER(BOUND(?rawActStr))
            BIND(
                IF(
                    CONTAINS(?rawActStr, "/resource/eli/"),
                    IRI(REPLACE(?rawActStr, "http://publications.europa.eu/resource/eli/", "https://eur-lex.europa.eu/eli/")),
                    IRI(?rawActStr)
                )
                AS ?act
            )
            BIND(IRI(?celexUriStr) AS ?celexAct)

            {{
                SELECT ?c_act (MIN(STR(?titleCandidate)) AS ?title)
                WHERE {{
                    ?expr cdm:expression_belongs_to_work ?c_act ;
                        cdm:expression_uses_language <{language_uri}> ;
                        cdm:expression_title ?titleCandidate .
                    {title_filter}
                }}
                GROUP BY ?c_act
            }}

            OPTIONAL {{
                SELECT ?c_act (MIN(STR(?sectionCandidate)) AS ?sectionCode)
                WHERE {{
                    ?c_act cdm:official-journal-act_section_oj ?sectionCandidate .
                }}
                GROUP BY ?c_act
            }}

            OPTIONAL {{
                SELECT ?c_act (MIN(STR(?subsectionCandidate)) AS ?subsectionCode)
                WHERE {{
                    ?c_act cdm:official-journal-act_subsection_oj ?subsectionCandidate .
                }}
                GROUP BY ?c_act
            }}

            {category_block}
            BIND(IRI(?categoryUriStr) AS ?categoryUri)
            BIND(REPLACE(?categoryUriStr, ".*/", "") AS ?categoryCode)

            OPTIONAL {{
                SELECT ?categoryUri (MIN(STR(?categoryLabelCandidate)) AS ?categoryLabel)
                WHERE {{
                    ?categoryUri skos:prefLabel ?categoryLabelCandidate .
                    FILTER(LANG(?categoryLabelCandidate) = "{lang_code}")
                }}
                GROUP BY ?categoryUri
            }}

            {institution_block}
            BIND(IRI(?institutionUriStr) AS ?institutionUri)
            BIND(REPLACE(?institutionUriStr, ".*/", "") AS ?institutionCode)

            OPTIONAL {{
                SELECT ?institutionUri (MIN(STR(?institutionLabelCandidate)) AS ?institutionLabel)
                WHERE {{
                    ?institutionUri skos:prefLabel ?institutionLabelCandidate .
                    FILTER(LANG(?institutionLabelCandidate) = "{lang_code}")
                }}
                GROUP BY ?institutionUri
            }}

            OPTIONAL {{
                SELECT ?c_act (MIN(STR(?officialJournalActNumberCandidate)) AS ?officialJournalActNumber)
                WHERE {{
                    ?c_act cdm:official-journal-act_number ?officialJournalActNumberCandidate .
                }}
                GROUP BY ?c_act
            }}

            OPTIONAL {{
                SELECT ?c_act (MIN(STR(?resourceLegalNumberCandidate)) AS ?resourceLegalNumber)
                WHERE {{
                    ?c_act cdm:resource_legal_number_natural ?resourceLegalNumberCandidate .
                }}
                GROUP BY ?c_act
            }}
            BIND(COALESCE(?officialJournalActNumber, ?resourceLegalNumber) AS ?actNumber)

            }}
            ORDER BY ?date ?act
        """

        return query_template.format(
            language_uri=language_uri,
            lang_code=lang_code,
            cellar_domain=CELLAR_DOMAIN,
            date_filters_str="\n  ".join(date_filters),
            title_filter=title_filter,
            category_block=category_block,
            institution_block=institution_block,
        )

    def _get_label_filter(self, var_name: str, search: Optional[str]) -> str:
        """Helper method for building specific query parts, such as filters and content URLs.
        Args:
        - var_name: The variable name used in the SPARQL query (e.g., "label").
        - search: Optional search string for filtering results.

        Returns:
        - A SPARQL filter string based on the search parameter.

        """
        if search is None:
            return ""
        search = search.strip()
        if not search:
            raise QueryError("search filter cannot be empty.")
        escaped = _escape_sparql_literal(search)
        return f'FILTER(BOUND(?{var_name}) && CONTAINS(LCASE(STR(?{var_name})), LCASE("{escaped}")))'

    def build_category_types_query(
        self, language: str = DEFAULT_LANGUAGE, search: Optional[str] = None
    ) -> str:
        """Build a SPARQL query to fetch the list of category types.

        Args:
            language: ISO language code (default: "ENG"). Examples: "ENG", "SPA", "FRA"...
            search: Optional case-insensitive substring filter on category type labels.

        Returns:
            The SPARQL query string.
        """
        lang_code = LANGUAGE_CODE_MAP.get(language, "en")

        filter_line = self._get_label_filter("label", search)

        query = f"""
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX at: <http://{CELLAR_DOMAIN}/ontology/authority/>

            SELECT DISTINCT ?code ?label
            WHERE {{
            ?uri a skos:Concept ;
                skos:inScheme <http://{CELLAR_DOMAIN}/resource/authority/resource-type> ;
                at:authority-code ?code .
            
            OPTIONAL {{
                ?uri skos:prefLabel ?label .
                FILTER(LANG(?label) = "{lang_code}")
            }}
            {filter_line}
            }}
            ORDER BY ?code
        """
        return query

    def build_institution_types_query(
        self, language: str = DEFAULT_LANGUAGE, search: Optional[str] = None
    ) -> str:
        """Build a SPARQL query to fetch the list of institutions.

        Note: The corporate-body authority endpoint can be slow/unreliable.
        Consider using get_institution_types_cached() for a static list instead.

        Args:
            language: ISO language code (default: "ENG").
            search: Optional case-insensitive substring filter on institution type labels.

        Returns:
            The SPARQL query string.
        """
        lang_code = LANGUAGE_CODE_MAP.get(language, "en")

        filter_line = self._get_label_filter("label", search)

        query = f"""
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX at: <http://{CELLAR_DOMAIN}/ontology/authority/>

            SELECT DISTINCT ?code ?label
            WHERE {{
            ?uri a skos:Concept ;
                skos:inScheme <http://{CELLAR_DOMAIN}/resource/authority/corporate-body> ;
                at:authority-code ?code .
            
            OPTIONAL {{
                ?uri skos:prefLabel ?label .
                FILTER(LANG(?label) = "{lang_code}")
            }}
            {filter_line}
            }}
            ORDER BY ?code
        """
        return query

    def build_act_content_url(self, act_id_or_uri: str) -> str:
        """Build a Cellar publication URL from a CELEX id or resource URI.

        Args:
            act_id_or_uri: CELEX id (e.g. "32014R0001") or full Cellar resource URI.

        Returns:
            A resource URI usable with Cellar's publication.

        Raises:
            QueryError: If act_id_or_uri is empty.
        """
        identifier = act_id_or_uri.strip()
        if not identifier:
            raise QueryError("act_id_or_uri cannot be empty.")

        if identifier.startswith(("http://", "https://")):
            return identifier

        return f"https://{CELLAR_DOMAIN}/resource/celex/{quote(identifier, safe='')}"

    def fetch_publication_content(
        self,
        resource_uri: str,
        language: str = DEFAULT_LANGUAGE,
    ) -> Union[str, bytes]:
        """Fetch publication content from EU API.

        Args:
            resource_uri: Full Cellar resource URI.
            language: ISO 639-3 language code used by Cellar (e.g. "ENG").

        Returns:
            The response body decoded as text, or raw bytes when return_bytes is True
            or content_format is "pdf".

        Raises:
            QueryError: If language, resource_uri, or content_format are invalid.
            EndpointError: If the request fails or Cellar is unreachable.
        """
        if not resource_uri.strip():
            raise QueryError("resource_uri cannot be empty.")

        language = language.strip().upper()
        if LANGUAGE_CODE_MAP.get(language) is None:
            raise QueryError(
                f"Unsupported language: '{language}'. "
                f"Supported: {', '.join(sorted(LANGUAGE_CODE_MAP))}"
            )

        headers = {
            "Accept": _CONTENT_ACCEPT_HEADERS[ACT_CONTENT_FORMAT_HTML],
            "Accept-Language": language.lower(),
        }

        try:
            response = requests.get(
                resource_uri,
                timeout=self.timeout,
                headers=headers,
                allow_redirects=True,
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            raise EndpointError(
                f"EU API returned HTTP {e.response.status_code}",
                status_code=e.response.status_code,
                endpoint=resource_uri,
            ) from e
        except requests.exceptions.RequestException as e:
            raise EndpointError(
                f"Failed to reach EU API: {e}",
                endpoint=resource_uri,
            ) from e

    def execute_query(self, query: str) -> dict:
        """Send a SPARQL query to the endpoint and return the JSON response.

        Args:
            query: The SPARQL query string.

        Returns:
            The parsed JSON response as a dict.

        Raises:
            EndpointError: If the request fails or the endpoint is unreachable.
        """
        try:
            response = requests.post(
                self.endpoint,
                data={"query": query},
                timeout=self.timeout,
                headers={"Accept": "application/sparql-results+json"},
            )
            response.raise_for_status()
            return response.json()  # type: ignore
        except requests.exceptions.HTTPError as e:
            raise EndpointError(
                f"SPARQL endpoint returned HTTP {e.response.status_code}",
                status_code=e.response.status_code,
                endpoint=self.endpoint,
            ) from e
        except requests.exceptions.RequestException as e:
            raise EndpointError(
                f"Failed to reach SPARQL endpoint: {e}",
                endpoint=self.endpoint,
            ) from e

    def _get_date_filters(self, date: str, date_end: Optional[str] = None) -> list[str]:
        filters: list[str] = []
        if date_end is not None:
            filters.append(f'FILTER(?date >= "{date}"^^xsd:date)')
            filters.append(f'FILTER(?date <= "{date_end}"^^xsd:date)')
        else:
            filters.append(f'FILTER(?date = "{date}"^^xsd:date)')
        return filters

    def _get_title_filter(self, title_contains: Optional[str] = None) -> str:
        if title_contains is not None:
            escaped_title = _escape_sparql_literal(title_contains)
            return (
                f"FILTER(CONTAINS(LCASE(STR(?titleCandidate)), "
                f'LCASE("{escaped_title}")))'
            )
        return ""

    def _get_resource_subquery_block(
        self,
        predicate: str,
        candidate_var: str,
        output_var: str,
        code: Optional[str],
    ) -> str:
        wrapper = "OPTIONAL " if code is None else ""
        filter_line = ""
        if code is not None:
            escaped_code = _escape_sparql_literal(code)
            filter_line = (
                f'\n                    FILTER(REPLACE(STR(?{candidate_var}), ".*/", "") = '
                f'"{escaped_code}")'
            )

        return (
            f"{wrapper}{{\n"
            f"                SELECT ?c_act (MIN(STR(?{candidate_var})) AS ?{output_var})\n"
            f"                WHERE {{\n"
            f"                    ?c_act {predicate} ?{candidate_var} ."
            f"{filter_line}\n"
            f"                }}\n"
            f"                GROUP BY ?c_act\n"
            f"            }}"
        )


def _validate_date(value: str) -> None:
    if not value or len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise QueryError(f"Invalid date format: '{value}'. Expected YYYY-MM-DD.")
    _parse_date(value)


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise QueryError(
            f"Invalid date format: '{value}'. Expected YYYY-MM-DD."
        ) from exc


def _escape_sparql_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
