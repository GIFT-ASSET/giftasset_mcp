# 🎁 Telegram Gifts Analyst | MCP Server

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-Enabled-brightgreen.svg)](#)
[![Platform](https://img.shields.io/badge/Platform-Telegram-0088CC.svg?logo=telegram&logoColor=white)](#)

Supercharge your AI agents with the **Telegram Gifts Analyst MCP Server**. 

Built on the Model Context Protocol (MCP), this server acts as a bridge to the `api.giftasset.dev` API. It equips AI agents (like Claude or custom LLM bots) with a comprehensive suite of tools to fetch real-time market data, analyze user inventories, and track deep analytics for the Telegram Gifts market.

---

## 🛠️ Exposed Tools (MCP Endpoints)

The server exposes the following tools, allowing AI agents to dynamically fetch and aggregate Telegram Gifts market data:

| Tool | Description | Key Arguments |
| :--- | :--- | :--- |
| **`get_gift_info`** | Fetches high-resolution data for a specific gift instance. | `slug` *(e.g., 'plushpepe-1')* |
| **`get_market_actions`** | Tracks global market movements (buys, listings, state changes) across all supported marketplaces. | `page`, `mode`, `action_type`, `gift`, price filters |
| **`get_gifts_aggregator`** | Queries highly-filtered, unified market data combining multiple parameters. | `page`, `name`, `model`, `symbol`, `backdrop`, price filters |
| **`get_unique_last_sales`** | Retrieves the most recent unique sales for a specified collection. | `collection_name`, `limit`, `model_name` |
| **`get_all_collections_last_sale`**| Gathers the absolute last sale data across all providers for all collections. | *None* |
| **`get_gifts_update_stat`** | Provides daily statistical tracking of gift improvements and upgrades. | *None* |
| **`get_user_gifts`** | Scans and returns the complete gift inventory of a specified Telegram user. | `username` or `telegram_id`, `limit`, `offset` |

---

## 🚀 Prerequisites

* **Python:** Version 3.11 or higher (or Docker installed).
* **API Key:** You need a valid `GIFTASSET_API_KEY` to connect to the GiftAsset API. 
    > 🔑 **Get your key here:** [@giftassetmcp_bot](https://t.me/giftassetmcp_bot)

---

## 🔌 Connecting to an AI Agent

You can connect this server to any MCP-compatible client (such as **Claude Desktop** or **Cursor**). The API key must be passed via the `GIFTASSET_API_KEY` environment variable.

### 🐳 Option 1: Using Docker (Recommended)

Docker provides the cleanest integration without polluting your local Python environment.

1. **Build the image:**
   ```bash
   docker-compose build

```

2. **Configure your MCP Client** (e.g., add to `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "telegram-gifts": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GIFTASSET_API_KEY=your_api_key_here",
        "telegram-gifts-mcp"
      ]
    }
  }
}

```



### 🐍 Option 2: Using a Local Python Environment

If you prefer running it locally via Python, follow these steps:

1. **Setup the environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```


2. **Configure your MCP Client** (e.g., add to `claude_desktop_config.json`):
*Note: You must use **absolute paths** for both the Python binary and the project directory.*
```json
{
  "mcpServers": {
    "telegram-gifts": {
      "command": "/absolute/path/to/your/venv/bin/python",
      "args": [
        "-m",
        "src.server"
      ],
      "env": {
          "PYTHONPATH": "/absolute/path/to/giftasset_mcp",
          "GIFTASSET_API_KEY": "your_api_key_here"
      }
    }
  }
}

```



---

## 💻 Standalone Testing

Want to test the server directly via standard I/O before hooking it up to an agent?

```bash
export GIFTASSET_API_KEY="your_api_key_here"
python -m src.server

```

*(Note: The server will start in MCP stdio mode, expecting JSON-RPC commands via stdin/stdout).*