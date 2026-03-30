"""Public API layer for DOUE operations."""

from .client import DoueBulletinClient
from .models import DoueOfficialAct, parse_results

__all__ = [
    "DoueBulletinClient",
    "DoueOfficialAct",
    "parse_results",
]
