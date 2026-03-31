"""
Custom exceptions for the DOUE subpackage.
"""


class BulletinError(Exception):
    """Base exception for all bulletin errors."""


class QueryError(BulletinError):
    """Raised when a SPARQL query is malformed or cannot be built.

    Attributes:
        query: The SPARQL query string that caused the error, if available.
    """

    def __init__(self, message: str, query: str | None = None) -> None:
        super().__init__(message)
        self.query = query


class EndpointError(BulletinError):
    """Raised when the SPARQL endpoint returns an error or is unreachable.

    Attributes:
        status_code: The HTTP status code returned, if available.
        endpoint: The endpoint URL that was called.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        endpoint: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint
