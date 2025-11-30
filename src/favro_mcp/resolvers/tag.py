"""Tag resolver."""

from favro_mcp.api.client import FavroNotFoundError
from favro_mcp.api.models import Tag

from .base import BaseResolver


class TagResolver(BaseResolver[Tag]):
    """Resolver for tags."""

    entity_type = "tag"

    def _fetch_all(self, **context: str | None) -> list[Tag]:
        return self.client.get_tags()

    def _fetch_by_id(self, entity_id: str) -> Tag | None:
        try:
            return self.client.get_tag(entity_id)
        except FavroNotFoundError:
            return None

    def _get_id(self, entity: Tag) -> str:
        return entity.tag_id

    def _get_name(self, entity: Tag) -> str:
        return entity.name
