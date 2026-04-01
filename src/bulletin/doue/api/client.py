"""
High-level client for querying EU Official Journal (DOUE) acts.
"""

from ..repository._connector import DoueConnector
from ..constants import DEFAULT_LANGUAGE, SPARQL_ENDPOINT
from ..converters import acts_to_csv, parse_results
from .models import DoueOfficialAct


class DoueBulletinClient:
    """Client to query EU Official Journal acts."""

    def __init__(self, endpoint: str = SPARQL_ENDPOINT, timeout: int = 30):
        self._connector = DoueConnector(endpoint=endpoint, timeout=timeout)

    def get_acts(
        self, date: str, language: str = DEFAULT_LANGUAGE, date_end: str | None = None, title_contains: str | None = None
    ) -> list[DoueOfficialAct]:
        """Fetch Official Journal acts for a given publication date.

        Args:
            date: Publication date in ISO format (e.g. "2025-03-27").
            date_end: End date in ISO format (e.g. "2025-03-27"). If provided, fetch acts published between `date` and `date_end` inclusive.
            title_contains: Case-insensitive substring filter on title.
            language: Language code (default: "ENG"). Supported values are defined in `LANGUAGE_CODE_MAP`. Examples: "ENG", "FRA", "DEU", "SPA"...

        Returns:
            A list of DoueOfficialAct objects.
        """
        query = self._connector.build_acts_query(date, language=language, date_end=date_end, title_contains=title_contains)
        response = self._connector.execute_query(query)
        return parse_results(response)

    def get_acts_csv(self, date: str, date_end: str | None = None, title_contains: str | None = None, language: str = DEFAULT_LANGUAGE) -> str:
        """
        Fetch Official Journal acts for a given date and return CSV output.

        Args:
            date: Publication date in ISO format (e.g. "2025-03-27").
            date_end: End date in ISO format (e.g. "2025-03-27"). If provided, fetch acts published between `date` and `date_end` inclusive.
            title_contains: Case-insensitive substring filter on title.
            language: Language code (default: "ENG"). Supported values are defined in `LANGUAGE_CODE_MAP`. Example: "ENG", "FRA", "DEU", "SPA".
        Returns:
            A string containing the CSV representation of the acts.

        """
        acts = self.get_acts(date, language=language, date_end=date_end, title_contains=title_contains)
        return acts_to_csv(acts)
