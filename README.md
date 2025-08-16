# Pendo MCP Server

A Model Context Protocol (MCP) server that provides tools for accessing and navigating the Pendo platform through its API.

## Features

This MCP server provides ten tools for read-only access to Pendo data:

### Core Tools

#### 1. `list_pages`
Lists all tagged pages in your Pendo subscription.
- Shows page IDs, names, app IDs, and creation dates
- Optional filtering by application ID for multi-app subscriptions
- Returns up to 10 pages with a count of total pages

#### 2. `get_visitor_details`
Retrieves detailed information about a specific visitor.
- Input: Visitor ID
- Returns: Visitor metadata, account associations, first visit date, browser info, and custom fields

#### 3. `get_active_visitors`
Gets active visitor counts and activity metrics using Pendo's aggregation API.
- Configurable time range (1-90 days)
- Group by day or hour
- Returns unique visitor counts and total events per period

### Features & Events Tools

#### 4. `list_features`
Lists all tagged features in your Pendo subscription.
- Shows feature IDs, names, colors, element paths, and creation dates
- Optional filtering by application ID for multi-app subscriptions
- Returns up to 10 features with a count of total features

#### 5. `get_feature_details`
Retrieves detailed information about specific features.
- Input: Feature ID or comma-separated list of IDs
- Returns: Feature metadata, element paths, colors, and timestamps

#### 6. `list_track_events`
Lists all track event types in your Pendo subscription.
- Shows event IDs, names, app IDs, and timestamps
- Optional filtering by application ID for multi-app subscriptions
- Returns up to 10 track events with a count of total events

#### 7. `search_track_events`
Searches for track events with advanced filtering options.
- Filter by event name, visitor ID, account ID
- Configurable time range (1-90 days)
- Limit results (1-1000, default: 100)
- Returns event occurrences with counts and summaries

### Account Tools (New)

#### 8. `get_account_details`
Retrieves detailed information about a specific account.
- Input: Account ID
- Returns: Account metadata, custom fields, visitor count
- Shows first visit, last visit, and last updated timestamps
- Includes multi-app metadata for subscriptions with multiple applications

#### 9. `search_accounts_by_metadata`
Searches accounts by metadata field values.
- Filter by custom, agent, or auto metadata fields
- Input: Field name, value, and field type
- Returns matching accounts with metadata
- Shows up to 100 accounts with summaries

#### 10. `list_account_visitors`
Lists all visitors associated with an account.
- Input: Account ID
- Optional: Include detailed visitor metadata
- Returns visitor list sorted by most recent activity
- Shows visitor IDs, first visits, browsers, and custom fields

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

**Pages & Features:**
- "List all the pages in Pendo"
- "List all features tagged in Pendo"
- "Get details about feature [feature-id]"

**Visitors & Activity:**
- "Get details about visitor [visitor-id]"
- "Show me active visitor counts for the last 7 days"
- "Get hourly visitor activity for the last 24 hours"

**Track Events:**
- "List all track events in Pendo"
- "Search for track events named 'Button Click' in the last 30 days"
- "Find all track events for visitor [visitor-id] in the last week"
- "Search track events for account [account-id]"

**Accounts:**
- "Get details about account [account-id]"
- "Search for accounts where industry equals 'Technology'"
- "Find accounts with custom field 'plan' set to 'Enterprise'"
- "List all visitors in account [account-id]"
- "Show visitors in account [account-id] with their metadata"

## API Endpoints Used

This server uses the following Pendo API endpoints:
- `GET /api/v1/page` - List pages
- `GET /api/v1/feature` - List features and get feature details
- `GET /api/v1/tracktype` - List track event types
- `GET /api/v1/visitor/{visitorId}` - Get visitor details
- `GET /api/v1/account/{accountId}` - Get account details
- `POST /api/v1/aggregation` - Run aggregation queries for:
  - Visitor activity metrics
  - Track event searches
  - Account metadata searches
  - Account visitor listings

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

### Next Phase (Segments):
- `list_segments` - List all shared segments
- `get_segment_details` - Get segment information
- `get_segment_visitors` - Export visitors from a segment
- `check_visitor_in_segment` - Check if visitor belongs to segment

### Additional Tools:
- `list_guides` - List all guides with filtering
- `get_guide_analytics` - Retrieve guide performance metrics
- `get_report_results` - Execute and retrieve report data
- `get_nps_scores` - Get NPS survey results
- `run_aggregation_query` - Execute custom aggregation pipelines

## License

MIT
