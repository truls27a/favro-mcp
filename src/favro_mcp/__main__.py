"""Entry point for Favro MCP server."""

from favro_mcp.server import mcp


def main() -> None:
    """Start the Favro MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
