"""Entity name resolvers for Favro CLI."""

from .base import AmbiguousMatchError, NotFoundError, ResolverError
from .board import BoardResolver
from .card import CardResolver
from .column import ColumnResolver
from .organization import OrganizationResolver
from .tag import TagResolver
from .user import UserResolver

__all__ = [
    "AmbiguousMatchError",
    "BoardResolver",
    "CardResolver",
    "ColumnResolver",
    "NotFoundError",
    "OrganizationResolver",
    "ResolverError",
    "TagResolver",
    "UserResolver",
]
