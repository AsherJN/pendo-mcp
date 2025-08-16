# Pendo MCP Server

A Model Context Protocol (MCP) server that provides tools for accessing and navigating the Pendo platform through its API.

## Features

This MCP server provides three main tools for read-only access to Pendo data:

### 1. `list_pages`
Lists all tagged pages in your Pendo subscription.
- Shows page IDs, names, app IDs, and creation dates
- Optional filtering by application ID for multi-app subscriptions
- Returns up to 10 pages with a count of total pages

### 2. `get_visitor_details`
Retrieves detailed information about a specific visitor.
- Input: Visitor ID
- Returns: Visitor metadata, account associations, first visit date, browser info, and custom fields

### 3. `get_active_visitors`
Gets active visitor counts and activity metrics using Pendo's aggregation API.
- Configurable time range (1-90 days)
- Group by day or hour
- Returns unique visitor counts and total events per period

## Setup

### Prerequisites

- Python 3.10 or higher
- A Pendo account with API access
- A Pendo Integration Key (found in Settings > Integrations)

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install "mcp[cli]" httpx python-dotenv
```

2. Configure your Pendo Integration Key:

The `.env` file should contain:
```
PENDO_INTEGRATION_KEY=your-integration-key-here
```

### Testing the Server

You can test the server directly:

```bash
python pendo_mcp_server.py
```

The server will start and listen for MCP commands on stdio.

## Connecting to Claude Desktop

To use this server with Claude Desktop, add the following to your Claude Desktop configuration file:

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pendo": {
      "command": "python",
      "args": ["/absolute/path/to/pendo_mcp/pendo_mcp_server.py"]
    }
  }
}
```

Make sure to replace `/absolute/path/to/pendo_mcp/` with the actual path to your project directory.

After updating the configuration, restart Claude Desktop. You should see the Pendo tools available in the tools menu.

## Usage Examples

Once connected to Claude Desktop, you can use natural language to interact with Pendo:

- "List all the pages in Pendo"
- "Get details about visitor [visitor-id]"
- "Show me active visitor counts for the last 7 days"
- "Get hourly visitor activity for the last 24 hours"

## API Endpoints Used

This server uses the following Pendo API endpoints:
- `GET /api/v1/page` - List pages
- `GET /api/v1/visitor/{visitorId}` - Get visitor details
- `POST /api/v1/aggregation` - Run aggregation queries for visitor activity

## Security Notes

- The integration key is stored in the `.env` file and should never be committed to version control
- This server only performs read operations (GET requests and aggregation queries)
- All API requests use HTTPS for secure communication
- Logging is configured to stderr to avoid interfering with MCP communication

## Troubleshooting

1. **Server won't start**: Check that your `PENDO_INTEGRATION_KEY` is set in the `.env` file
2. **API errors**: Verify your integration key has the necessary permissions
3. **No data returned**: Ensure your Pendo subscription has data (pages, visitors, events)
4. **Claude Desktop doesn't show tools**: Restart Claude Desktop after updating the configuration

## Future Enhancements

Potential additional tools that could be added:
- `list_features` - List tagged features
- `get_account_details` - Get account information
- `search_visitors_by_segment` - Find visitors in a specific segment
- `get_guide_analytics` - Retrieve guide performance metrics
- `get_nps_scores` - Get NPS survey results

## License

MIT
