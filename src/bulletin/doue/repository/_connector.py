"""
Connector for the EUR-Lex / Cellar SPARQL endpoint.

Handles query building and HTTP communication.
"""

import requests

from ..constants import SPARQL_ENDPOINT, LANGUAGE_CODE_MAP, DEFAULT_LANGUAGE
from ..exceptions import EndpointError, QueryError


class DoueConnector:
    """Connector class for the EUR-Lex / Cellar SPARQL endpoint."""

    def __init__(self, endpoint: str = SPARQL_ENDPOINT, timeout: int = 30):
        self.endpoint = endpoint
        self.timeout = timeout

    def build_acts_query(self, date: str, language: str = DEFAULT_LANGUAGE) -> str:
        """Build a SPARQL query for Official Journal acts on a given date.

        Args:
            date: Publication date in ISO format (e.g. "2025-03-27").
            language: ISO language code (default: "ENG").

        Returns:
            The SPARQL query string.

        Raises:
            QueryError: If the date format is invalid.
        """
        # Basic validation
        if not date or len(date) != 10 or date[4] != "-" or date[7] != "-":
            raise QueryError(f"Invalid date format: '{date}'. Expected YYYY-MM-DD.")

        lang_code = LANGUAGE_CODE_MAP.get(language)
        if lang_code is None:
            raise QueryError(
                f"Unsupported language: '{language}'. "
                f"Supported: {', '.join(sorted(LANGUAGE_CODE_MAP))}"
            )

        language_uri = (
            f"http://publications.europa.eu/resource/authority/language/{language}"
        )

        return f"""
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

  FILTER(?date = "{date}"^^xsd:date)
  FILTER(STRSTARTS(STR(?act), "http://publications.europa.eu/resource/celex/"))

  OPTIONAL {{ ?c_act cdm:official-journal-act_number ?actNumber . }}
}}
ORDER BY ?sectionCode ?subsectionCode ?categoryLabel ?institutionLabel
"""

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
            return response.json()
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
