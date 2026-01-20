# Favro MCP

MCP server for interacting with Favro project management.

## Prerequisites

Install [uv](https://docs.astral.sh/uv/) (required to run the server):

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Getting Your Favro API Token

1. Log in to [Favro](https://favro.com)
2. Click your **profile picture** (top-right corner)
3. Select **My Profile**
4. Scroll down to **API Tokens**
5. Click **Create new token**
6. Give it a name (e.g., "Claude Desktop") and click **Create**
7. **Copy the token** — you won't be able to see it again!

## Setup for Claude Desktop

### Step 1: Open the Configuration File

**Windows:**
1. Press `Win + R`, type `%APPDATA%\Claude` and press Enter
2. Open (or create) `claude_desktop_config.json`

**macOS:**
1. Open Finder
2. Press `Cmd + Shift + G` and go to `~/Library/Application Support/Claude/`
3. Open (or create) `claude_desktop_config.json`

### Step 2: Add the Configuration

Paste this into the file (replace with your actual email and token):

```json
{
  "mcpServers": {
    "favro": {
      "command": "uvx",
      "args": ["favro-mcp"],
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

> **Already have other MCP servers?** Just add the `"favro": { ... }` block inside your existing `"mcpServers"` object.

### Step 3: Restart Claude Desktop

Completely quit Claude Desktop (check the system tray on Windows) and relaunch it.

If successful, you'll see a **🔨 hammer icon** in the chat input — click it to see available Favro tools.

---

## Setup for Claude Code

```bash
claude mcp add --transport stdio favro \
  -e FAVRO_EMAIL=your-email@example.com \
  -e FAVRO_API_TOKEN=your-token \
  -- uvx favro-mcp
```

---

## Running from Source (Development)

To run a local/modified version instead of the published package:

```json
{
  "mcpServers": {
    "favro": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\path\\to\\favro-mcp",
        "favro-mcp"
      ],
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

Replace `C:\\path\\to\\favro-mcp` with the actual path to your local repo.

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

| Tool                | Description                                      |
| ------------------- | ------------------------------------------------ |
| `list_boards`       | List boards (optionally filter by collection)    |
| `get_board`         | Get board with columns                           |
| `get_current_board` | Get current board                                |
| `set_board`         | Set active board                                 |

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
