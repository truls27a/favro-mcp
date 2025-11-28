# Favro MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server for interacting with [Favro](https://favro.com/) project management through LLMs like Claude.

## Features

- **Read cards, boards, and organizations** through MCP resources
- **Create, update, delete, and move cards** through MCP tools
- **Search widgets by name** to find the right board
- **Full card details** including descriptions for LLM analysis
- **Strict typing** with Pydantic models
- **Rate limit handling** with automatic retry

## Installation

### Using uv (recommended)

```bash
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

## Configuration

### 1. Get Favro API credentials

1. Log into [Favro](https://favro.com/)
2. Click your account dropdown → **My profile**
3. Go to the **API Tokens** tab
4. Create a new token

### 2. Set environment variables

Create a `.env` file or set environment variables:

```bash
FAVRO_EMAIL=your-email@example.com
FAVRO_API_TOKEN=your-api-token-here

# Optional: Default organization ID
FAVRO_ORGANIZATION_ID=your-org-id
```

### 3. Configure Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "favro": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/favro-mcp", "favro-mcp"],
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "favro": {
      "command": "favro-mcp",
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Usage

### Resources (Read-only)

Browse Favro data through MCP resources:

| Resource | Description |
|----------|-------------|
| `favro://organizations` | List all accessible organizations |
| `favro://organization/{id}` | Get organization details |
| `favro://widgets` | List all boards/backlogs |
| `favro://widget/{id}` | Get widget with columns |
| `favro://widget/{id}/cards` | List cards in a widget |
| `favro://widget/{id}/columns` | List columns in a widget |
| `favro://card/{id}` | Get full card details |
| `favro://column/{id}/cards` | List cards in a column |
| `favro://collections` | List all collections |
| `favro://tags` | List all tags |

### Tools (Mutations)

Modify Favro data through MCP tools:

| Tool | Description |
|------|-------------|
| `set_organization` | Set active organization for API calls |
| `search_widgets` | Search widgets/boards by name |
| `create_card` | Create a new card |
| `update_card` | Update an existing card |
| `delete_card` | Delete a card |
| `move_card` | Move card to different column/widget |
| `add_comment` | Add comment to a card |
| `get_card_details` | Get detailed card information |

### Example Workflows

#### Create a card for an issue

```
User: Create a new Favro card for the login bug I found

Claude: I'll search for the right board and create a card.
[Uses search_widgets to find "Bugs" or relevant board]
[Uses create_card with the widget ID]
```

#### Find and fix a bug

```
User: Find a low-hanging bug to fix in the frontend project

Claude: Let me browse the bug board and find something manageable.
[Uses favro://widgets to list boards]
[Uses favro://widget/{id}/cards to read bugs]
[Analyzes card descriptions to find an easy fix]
```

#### Move a card to done

```
User: Move card ABC-123 to the Done column

Claude: [Uses move_card with the appropriate column_id]
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/favro-mcp.git
cd favro-mcp

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Type checking

```bash
pyright src/
```

### Linting

```bash
ruff check src/
ruff format src/
```

### Running locally

```bash
# With environment variables
FAVRO_EMAIL=... FAVRO_API_TOKEN=... python -m favro_mcp

# Or with .env file
python -m favro_mcp
```

## API Reference

This server wraps the [Favro REST API](https://favro.com/developer/). Key concepts:

- **Organization**: Top-level container
- **Collection**: Dashboard containing widgets
- **Widget**: Board or backlog
- **Column**: Status column in a widget
- **Card**: Task/issue

## License

MIT
