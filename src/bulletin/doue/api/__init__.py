"""Public API layer for DOUE operations."""

from .client import DoueBulletinClient
from .models import DoueOfficialAct, CategoryType, InstitutionType

__all__ = [
    "DoueBulletinClient",
    "DoueOfficialAct",
    "CategoryType",
    "InstitutionType",
]
