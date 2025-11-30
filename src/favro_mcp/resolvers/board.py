"""Board (Widget) resolver."""

from favro_mcp.api.client import FavroNotFoundError
from favro_mcp.api.models import Widget

from .base import BaseResolver


class BoardResolver(BaseResolver[Widget]):
    """Resolver for boards/widgets."""

    entity_type = "board"

    def _fetch_all(self, **context: str | None) -> list[Widget]:
        return self.client.get_widgets()

    def _fetch_by_id(self, entity_id: str) -> Widget | None:
        try:
            return self.client.get_widget(entity_id)
        except FavroNotFoundError:
            return None

    def _get_id(self, entity: Widget) -> str:
        return entity.widget_common_id

    def _get_name(self, entity: Widget) -> str:
        return entity.name
