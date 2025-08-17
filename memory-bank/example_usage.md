# Pendo MCP Server - Example Usage

## Once connected to Claude Desktop, you can use these natural language queries:

### 1. List Pages
**Query:** "Show me all the pages in Pendo"
- This will list up to 10 pages from your Pendo subscription
- Shows page IDs, names, app IDs, and creation dates

### 2. Get Visitor Details
**Query:** "Get details about visitor visitor123"
- Replace `visitor123` with an actual visitor ID from your Pendo data
- Returns visitor metadata, account associations, first visit date, and browser info

### 3. Get Active Visitors
**Query:** "Show me active visitor counts for the last 7 days"
- Returns daily visitor counts and event totals

**Query:** "Get hourly visitor activity for the last 24 hours"
- Returns hourly breakdown of visitor activity

## Example Responses

### List Pages Response:
```
Found 25 pages in Pendo.
Showing first 10 pages:

Page ID: _page123abc
Name: Dashboard
App ID: 12345
Created: 2024-01-15 10:30:00

---

Page ID: _page456def
Name: Settings
App ID: 12345
Created: 2024-01-16 14:22:00

... and 15 more pages.
```

### Visitor Details Response:
```
Visitor ID: user@example.com
Account ID: acme-corp
First Visit: 2024-01-10 09:15:00
Last Browser: Chrome

Custom Fields:
  role: admin
  department: Engineering
```

### Active Visitors Response:
```
Active Visitors Report - Last 7 days
==================================================
Date: 2025-01-09
  Unique Visitors: 1,234
  Total Events: 45,678

Date: 2025-01-10
  Unique Visitors: 1,456
  Total Events: 52,123

==================================================
Summary:
Total Events: 315,234
Peak Unique Visitors: 1,567
```

## Testing Without Claude Desktop

You can test the API calls directly using the test script:

```bash
python3 test_server.py
```

This will verify:
- Server can be imported
- Integration key is loaded
- All 3 tools are registered
- MCP server is ready to use

## Troubleshooting

1. **No data returned**: Check that your Pendo subscription has data (pages, visitors, events)
2. **API errors**: Verify your integration key has read permissions
3. **Server won't start**: Ensure PENDO_INTEGRATION_KEY is in .env file
4. **Import errors**: Run `pip3 install -r requirements.txt`
