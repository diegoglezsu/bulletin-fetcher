"""
High-level client for querying EU Official Journal (DOUE) acts.
"""

from ..repository._connector import DoueConnector
from ..constants import DEFAULT_LANGUAGE, SPARQL_ENDPOINT
from .models import DoueOfficialAct, parse_results


class DoueBulletinClient:
    """Client to query EU Official Journal acts."""

    def __init__(self, endpoint: str = SPARQL_ENDPOINT, timeout: int = 30):
        self._connector = DoueConnector(endpoint=endpoint, timeout=timeout)

    def get_acts(
        self, date: str, language: str = DEFAULT_LANGUAGE
    ) -> list[DoueOfficialAct]:
        """Fetch Official Journal acts for a given publication date.

        Args:
            date: Publication date in ISO format (e.g. "2025-03-27").
            language: Language code (default: "ENG"). Supported values are defined in `LANGUAGE_CODE_MAP`. Example: "ENG", "FRA", "DEU", "SPA".

        Returns:
            A list of DoueOfficialAct objects.
        """
        query = self._connector.build_acts_query(date, language=language)
        response = self._connector.execute_query(query)
        return parse_results(response)
