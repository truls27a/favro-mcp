"""Column resolver (requires board context for name resolution)."""

from favro_mcp.api.client import FavroNotFoundError
from favro_mcp.api.models import Column

from .base import BaseResolver


class ColumnResolver(BaseResolver[Column]):
    """Resolver for columns.

    Note: Name resolution requires board_id context since column names
    are only unique within a board.
    """

    entity_type = "column"

    def _fetch_all(
        self, board_id: str | None = None, **context: str | None
    ) -> list[Column]:
        if board_id is None:
            raise ValueError("board_id is required to resolve columns by name")
        return self.client.get_columns(board_id)

    def _fetch_by_id(self, entity_id: str) -> Column | None:
        try:
            return self.client.get_column(entity_id)
        except FavroNotFoundError:
            return None

    def _get_id(self, entity: Column) -> str:
        return entity.column_id

    def _get_name(self, entity: Column) -> str:
        return entity.name
