"""
Connector for the EUR-Lex / Cellar SPARQL endpoint.

Handles query building and HTTP communication.
"""

from datetime import date
from typing import Optional
import requests  # type: ignore

from ..constants import SPARQL_ENDPOINT, LANGUAGE_CODE_MAP, DEFAULT_LANGUAGE
from ..exceptions import EndpointError, QueryError


class DoueConnector:
    """Connector class for the EUR-Lex / Cellar SPARQL endpoint."""

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

        language_uri = (
            f"http://publications.europa.eu/resource/authority/language/{language}"
        )

        filters: list[str] = self._get_filters(date, date_end, title_contains, category_type, institution_type)

        query_template = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT
  ?act ?actNumber ?title ?date
  ?sectionCode ?subsectionCode
  ?categoryCode ?categoryUri ?categoryLabel
  ?institutionCode ?institutionUri ?institutionLabel
WHERE {{
  ?c_act cdm:official-journal-act_date_publication ?date ;
         owl:sameAs ?act .

  ?expr cdm:expression_belongs_to_work ?c_act ;
        cdm:expression_uses_language <{language_uri}> ;
        cdm:expression_title ?title .

  OPTIONAL {{ ?c_act cdm:official-journal-act_section_oj ?sectionCode . }}
  OPTIONAL {{ ?c_act cdm:official-journal-act_subsection_oj ?subsectionCode . }}

  OPTIONAL {{
    ?c_act cdm:work_has_resource-type ?categoryUri .
    OPTIONAL {{
      ?categoryUri skos:prefLabel ?categoryLabel .
      FILTER(LANG(?categoryLabel) = "{lang_code}")
    }}
  }}

  OPTIONAL {{
    ?c_act cdm:work_created_by_agent ?institutionUri .
    OPTIONAL {{
      ?institutionUri skos:prefLabel ?institutionLabel .
      FILTER(LANG(?institutionLabel) = "{lang_code}")
    }}
  }}

  BIND(
    IF(BOUND(?categoryUri), REPLACE(STR(?categoryUri), ".*/", ""), "")
    AS ?categoryCode
  )

  BIND(
    IF(BOUND(?institutionUri), REPLACE(STR(?institutionUri), ".*/", ""), "")
    AS ?institutionCode
  )

  {filters_str}

  OPTIONAL {{ ?c_act cdm:official-journal-act_number ?actNumber . }}
}}
ORDER BY ?sectionCode ?subsectionCode ?categoryLabel ?institutionLabel
"""
        return query_template.format(
            language_uri=language_uri,
            lang_code=lang_code,
            filters_str="\n  ".join(filters),
        )

    def build_category_types_query(self, language: str = DEFAULT_LANGUAGE) -> str:
        """Build a SPARQL query to fetch the list of category types.

        Args:
            language: ISO language code (default: "ENG").

        Returns:
            The SPARQL query string.
        """
        lang_code = LANGUAGE_CODE_MAP.get(language, "en")
        
        query = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX at: <http://publications.europa.eu/ontology/authority/>

SELECT DISTINCT ?code ?label
WHERE {{
  ?uri a skos:Concept ;
       skos:inScheme <http://publications.europa.eu/resource/authority/resource-type> ;
       at:authority-code ?code .
  
  OPTIONAL {{
    ?uri skos:prefLabel ?label .
    FILTER(LANG(?label) = "{lang_code}")
  }}
}}
ORDER BY ?code
"""
        return query
    
    def build_institution_types_query(self, language: str = DEFAULT_LANGUAGE) -> str:
        """Build a SPARQL query to fetch the list of institutions.

        Note: The corporate-body authority endpoint can be slow/unreliable.
        Consider using get_institution_types_cached() for a static list instead.

        Args:
            language: ISO language code (default: "ENG").

        Returns:
            The SPARQL query string.
        """
        lang_code = LANGUAGE_CODE_MAP.get(language, "en")
        
        query = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX at: <http://publications.europa.eu/ontology/authority/>

SELECT DISTINCT ?code ?label
WHERE {{
  ?uri a skos:Concept ;
       skos:inScheme <http://publications.europa.eu/resource/authority/corporate-body> ;
       at:authority-code ?code .
  
  OPTIONAL {{
    ?uri skos:prefLabel ?label .
    FILTER(LANG(?label) = "{lang_code}")
  }}
}}
ORDER BY ?code
"""
        return query

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
            return response.json() # type: ignore
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

    def _get_filters(self, date: str, date_end: Optional[str] = None, title_contains: Optional[str] = None, category_type: Optional[str] = None, institution_type: Optional[str] = None) -> list[str]:
        filters: list[str] = []
        if date_end is not None:
            filters.append(f'FILTER(?date >= "{date}"^^xsd:date)')
            filters.append(f'FILTER(?date <= "{date_end}"^^xsd:date)')
        else:
            filters.append(f'FILTER(?date = "{date}"^^xsd:date)')

        if title_contains is not None:
            escaped_title = _escape_sparql_literal(title_contains)
            filters.append(
                f'FILTER(CONTAINS(LCASE(STR(?title)), LCASE("{escaped_title}")))'
            )

        if category_type is not None:
            filters.append(f'FILTER(?categoryCode = "{category_type}")')

        if institution_type is not None:
            filters.append(f'FILTER(?institutionCode = "{institution_type}")')

        filters.append(
            'FILTER(STRSTARTS(STR(?act), "http://publications.europa.eu/resource/celex/"))'
        )
        return filters


def _validate_date(value: str) -> None:
    if not value or len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise QueryError(f"Invalid date format: '{value}'. Expected YYYY-MM-DD.")


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise QueryError(f"Invalid date format: '{value}'. Expected YYYY-MM-DD.") from exc


def _escape_sparql_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', "\\\"")
