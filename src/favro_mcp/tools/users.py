"""User tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.resolvers import UserResolver
from favro_mcp.server import mcp


@mcp.tool
def list_users(ctx: Context) -> dict[str, Any]:
    """List all users in the current organization.

    Returns:
        A list of users with their IDs, names, emails, and roles.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        users = client.get_users()
        result = [
            {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "organization_role": user.organization_role,
            }
            for user in users
        ]
        return {"users": result, "count": len(result)}


@mcp.tool
def get_user(user: str, ctx: Context) -> dict[str, Any]:
    """Look up a user by ID, name, or email address.

    Useful for resolving user IDs returned in card details (e.g. assignments,
    comments) to human-readable user information.

    Args:
        user: User ID, name, or email address

    Returns:
        User details including ID, name, email, and organization role.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        resolver = UserResolver(client)
        resolved = resolver.resolve(user)
        return {
            "user_id": resolved.user_id,
            "name": resolved.name,
            "email": resolved.email,
            "organization_role": resolved.organization_role,
        }
