# Favro MCP

MCP server for interacting with Favro project management.

## Getting Your Favro API Token

1. Log in to [Favro](https://favro.com/l/login)
2. Click your **username** (top-left corner)
3. Select **My Profile**
4. Go to **API Tokens**
5. Click **Create new token**
6. Give it a name (e.g., "Favro MCP") and click **Create**
7. **Copy the token** — you won't be able to see it again!

## Setup for Claude Code

```bash
claude mcp add --transport stdio favro \
  -e FAVRO_EMAIL=your-email@example.com \
  -e FAVRO_API_TOKEN=your-token \
  -- favro-mcp
```

---

## Setup for Claude Desktop

Add the following to your `claude_desktop_config.json` (`~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude` on Windows):

```json
{
  "mcpServers": {
    "favro": {
      "command": "favro-mcp",
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

Then restart Claude Desktop.

---

## Tools

### Organizations

| Tool                       | Description              |
| -------------------------- | ------------------------ |
| `list_organizations`       | List all organizations   |
| `get_current_organization` | Get current organization |
| `set_organization`         | Set active organization  |

### Collections (Folders)

| Tool               | Description                    |
| ------------------ | ------------------------------ |
| `list_collections` | List all collections (folders) |

### Boards

| Tool                | Description            |
| ------------------- | ---------------------- |
| `list_boards`       | List boards            |
| `get_board`         | Get board with columns |
| `get_current_board` | Get current board      |
| `set_board`         | Set active board       |

### Cards

| Tool                 | Description          |
| -------------------- | -------------------- |
| `list_cards`         | List cards on board  |
| `get_card_details`   | Get card details     |
| `create_card`        | Create a card        |
| `update_card`        | Update a card        |
| `move_card`          | Move card to column  |
| `assign_card`        | Assign/unassign user |
| `tag_card`           | Add/remove tag       |
| `delete_card`        | Delete a card        |
| `list_custom_fields` | List custom fields   |

### Columns

| Tool            | Description           |
| --------------- | --------------------- |
| `list_columns`  | List columns on board |
| `create_column` | Create a column       |
| `rename_column` | Rename a column       |
| `move_column`   | Move column position  |
| `delete_column` | Delete a column       |

---

## Development

This project uses [uv](https://docs.astral.sh/uv/) for development.

### Setup

1. Install uv:

   **macOS / Linux:**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **Windows (PowerShell):**

   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/truls27a/favro-mcp.git
   cd favro-mcp
   ```

3. Install dependencies:
   ```bash
   uv sync --dev
   ```

### Running from Source

To run a local/modified version instead of the published package:

```json
{
  "mcpServers": {
    "favro": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/favro-mcp",
        "python",
        "-m",
        "favro_mcp"
      ],
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```
