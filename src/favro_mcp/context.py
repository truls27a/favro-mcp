"""Favro MCP context and lifespan management."""

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator

from favro_mcp.api.client import FavroClient

if TYPE_CHECKING:
    from fastmcp import Context, FastMCP


@dataclass
class FavroContext:
    """Mutable session state for the Favro MCP server."""

    current_org_id: str | None = None
    current_board_id: str | None = None

    def get_client(self) -> FavroClient:
        """Create a configured Favro API client.

        Uses FAVRO_EMAIL and FAVRO_API_TOKEN environment variables.
        Includes the current organization ID if set.

        Returns:
            Configured FavroClient instance (use as context manager)

        Raises:
            ValueError: If credentials are not configured
        """
        email = os.environ.get("FAVRO_EMAIL")
        token = os.environ.get("FAVRO_API_TOKEN")
        if not email or not token:
            raise ValueError(
                "FAVRO_EMAIL and FAVRO_API_TOKEN environment variables are required."
            )
        return FavroClient(email, token, self.current_org_id)

    def require_org(self) -> str:
        """Require that an organization is selected.

        If no organization is selected but the user has access to exactly one,
        it will be auto-selected.

        Returns:
            The current organization ID

        Raises:
            ValueError: If no organization is selected and auto-selection not possible
        """
        if self.current_org_id:
            return self.current_org_id

        # Try auto-selection
        with self.get_client() as client:
            orgs = client.get_organizations()

        if len(orgs) == 0:
            raise ValueError("No organizations found for this account.")

        if len(orgs) == 1:
            self.current_org_id = orgs[0].organization_id
            return self.current_org_id

        # Multiple orgs - user must choose
        org_names = ", ".join(org.name for org in orgs)
        raise ValueError(
            f"Multiple organizations available ({org_names}). "
            "Use the set_organization tool to select one, "
            "or read favro://organizations to list available organizations."
        )

    def get_effective_board_id(self, board: str | None) -> str | None:
        """Get effective board ID from parameter or current selection.

        Args:
            board: Explicit board ID/name, or None to use current

        Returns:
            Board ID to use, or None if neither specified
        """
        return board if board else self.current_board_id


@asynccontextmanager
async def app_lifespan(server: "FastMCP[Any]") -> AsyncIterator[FavroContext]:
    """Application lifespan - yields mutable context for session state.

    This context persists for the lifetime of the server and is shared
    across all requests. It holds the current organization and board selection.
    """
    ctx = FavroContext()
    yield ctx
    # No cleanup needed currently


def get_favro_context(ctx: "Context") -> FavroContext:
    """Get FavroContext from MCP request context.

    Args:
        ctx: FastMCP Context from a tool/resource handler

    Returns:
        The FavroContext with session state

    Raises:
        RuntimeError: If request context is not available
    """
    if ctx.request_context is None:
        raise RuntimeError("Request context is not available")
    return ctx.request_context.lifespan_context  # type: ignore[return-value]
