# Pendo MCP Server 🚀

[![MCP](https://img.shields.io/badge/Model_Context_Protocol-Enabled-blue)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org/)
[![Pendo](https://img.shields.io/badge/Pendo-Analytics-orange)](https://pendo.io/)

A comprehensive Model Context Protocol (MCP) server that provides AI assistants with powerful access to Pendo analytics through 15 specialized tools. Transform natural language questions into deep product insights with intelligent fallback strategies and LLM-optimized responses.

## ✨ Key Features

- **🔧 15 Comprehensive Tools** - Complete analytics toolkit organized by business function
- **🧠 Intelligent Fallbacks** - Never dead-end; always provides actionable insights
- **🔗 Tool Chaining** - Complex business intelligence through natural tool composition  
- **📊 LLM-Optimized Output** - Responses formatted specifically for AI consumption
- **⚡ Universal Segment Support** - Filter any analysis by user segments
- **🎯 Zero Required Parameters** - All tools work out-of-the-box with sensible defaults

## 📋 Tool Categories

### 🎯 Product Discovery (3 tools)
- **`search_pages`** - Find and analyze page usage with optional metrics
- **`search_features`** - Discover feature adoption and click patterns  
- **`search_track_events`** - Analyze custom event tracking data

### 👥 People Insights (5 tools)  
- **`get_visitor_details`** - Deep visitor profiles with activity history
- **`search_visitors`** - Find users by metadata, activity, and segments
- **`get_account_details`** - Account analysis with visitor metrics
- **`search_accounts`** - Advanced account discovery and filtering
- **`analyze_segments`** - Multi-purpose segment analysis and exports

### 📈 Behavioral Analytics (6 tools)
- **`analyze_usage`** - Activity patterns with intelligent fallbacks ⭐
- **`analyze_feature_adoption`** - Adoption rates and usage trends
- **`analyze_retention`** - User stickiness and churn analysis  
- **`analyze_funnels`** - Multi-step conversion tracking
- **`analyze_user_paths`** - Navigation pattern discovery
- **`calculate_product_engagement`** - PES scoring and engagement metrics

### 💬 Feedback (1 tool)
- **`analyze_nps_feedback`** - NPS scoring with sentiment analysis

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/AsherJN/pendo-mcp.git
cd pendo-mcp

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your Pendo Integration Key:

```env
PENDO_INTEGRATION_KEY=your_integration_key_here
```

### 3. Claude Desktop Setup

Add this configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "pendo": {
      "command": "python3",
      "args": ["/path/to/pendo-mcp/pendo_mcp_server.py"],
      "env": {
        "PENDO_INTEGRATION_KEY": "your_integration_key_here"
      }
    }
  }
}
```

### 4. Test the Connection

```bash
# Test server functionality
python test_server.py
```

## 💡 Usage Examples

### Basic Analytics Query
```
"Show me the top pages by traffic in the last 30 days"
→ Uses: search_pages(include_metrics=True, limit=10)
```

### Complex Business Intelligence
```
"What's the user engagement health of our platform?"  
→ Tool Chain:
  1. search_pages(include_metrics=True) - Discover key pages
  2. analyze_feature_adoption(days_back=30) - Check feature usage
  3. calculate_product_engagement() - Overall PES score
  4. analyze_retention(period_type="weekly") - Stickiness metrics
```

### Intelligent Fallback Example
```
Query: analyze_usage(days_back=30, group_by="week")

❓ Broad usage data unavailable.
🔄 **Fallback Analysis - Feature Usage:**
Feature Activity Found - 'Alarm Acknowledge Button': 245 clicks from 23 users
💡 **Tip**: For detailed feature analysis, try: analyze_feature_adoption()
```

## 🔧 Tool Reference

### Product Discovery Tools

#### `search_pages`
Search and analyze page usage with consolidated metrics.

**Parameters:**
- `page_id` (optional) - Specific page ID to retrieve
- `name_contains` (optional) - Filter by page name text
- `include_metrics` (optional) - Include usage metrics (default: False)
- `limit` (optional) - Max results (default: 100)

**Example:**
```
search_pages(name_contains="dashboard", include_metrics=True, limit=5)
```

#### `search_features`  
Discover feature engagement and click patterns.

**Parameters:**
- `feature_id` (optional) - Specific feature ID
- `name_contains` (optional) - Filter by feature name
- `include_metrics` (optional) - Include click metrics (default: False)
- `limit` (optional) - Max results (default: 100)

#### `search_track_events`
Analyze custom event tracking data.

**Parameters:**
- `event_name` (optional) - Specific event name filter
- `visitor_id` (optional) - Filter by visitor
- `days_back` (optional) - Analysis period (default: 7, max: 90)
- `limit` (optional) - Max results (default: 100)

### People Insights Tools

#### `get_visitor_details`
Get comprehensive visitor information and activity.

**Parameters:**
- `visitor_id` (required) - The Pendo visitor ID  
- `include_history` (optional) - Recent activity history (default: False)
- `include_events` (optional) - Event summary (default: False)

#### `search_visitors`
Advanced visitor discovery and filtering.

**Parameters:**
- `account_id` (optional) - Filter by account
- `segment_id` (optional) - Filter by segment
- `metadata_filter` (optional) - Custom metadata filter
- `active_since` (optional) - Only visitors active in last N days
- `limit` (optional) - Max results (default: 100)

#### `get_account_details`
Comprehensive account analysis with metrics.

**Parameters:**
- `account_id` (required) - The Pendo account ID
- `include_visitors` (optional) - List of visitors (default: False)  
- `include_metrics` (optional) - Activity metrics (default: False)

#### `search_accounts`
Advanced account search with segment support.

**Parameters:**
- `metadata_filter` (optional) - Custom metadata filter
- `segment_id` (optional) - Filter by segment
- `min_visitors` (optional) - Minimum visitor count
- `active_since` (optional) - Activity recency filter
- `limit` (optional) - Max results (default: 100)

#### `analyze_segments`
Multi-purpose segment analysis tool.

**Parameters:**
- `action` (required) - 'list', 'details', 'check', or 'export'
- `segment_id` (optional) - Required for details/check/export
- `visitor_id` (optional) - For membership check
- `account_id` (optional) - For membership check

### Behavioral Analytics Tools

#### `analyze_usage` ⭐
Activity patterns with intelligent fallback strategies.

**Parameters:**
- `segment_id` (optional) - Segment filter
- `visitor_id` (optional) - Visitor filter  
- `days_back` (optional) - Analysis period (default: 30, max: 90)
- `group_by` (optional) - 'day', 'week', or 'month' (default: 'day')
- `metric_type` (optional) - 'events', 'sessions', or 'time' (default: 'events')

**Special Feature:** Automatic fallback strategies provide alternative insights when primary queries fail.

#### `analyze_feature_adoption`
Track feature and page adoption with time series.

**Parameters:**
- `feature_ids` (optional) - List of feature IDs to analyze
- `page_ids` (optional) - List of page IDs to analyze
- `segment_id` (optional) - Segment filter
- `days_back` (optional) - Analysis period (default: 30)
- `group_by` (optional) - 'total', 'day', or 'week' (default: 'total')

#### `analyze_retention`
User and account stickiness analysis.

**Parameters:**
- `segment_id` (optional) - Segment filter
- `cohort_date` (optional) - Start date (YYYY-MM-DD format)
- `period_type` (optional) - 'daily', 'weekly', or 'monthly' (default: 'weekly')
- `group_by` (optional) - 'visitor' or 'account' (default: 'visitor')

#### `analyze_funnels`
Multi-step conversion analysis.

**Parameters:**
- `steps` (required) - List of page/feature IDs representing funnel steps
- `segment_id` (optional) - Segment filter
- `days_back` (optional) - Analysis period (default: 30)
- `group_by` (optional) - 'total' or 'day' (default: 'total')

#### `analyze_user_paths`
Navigation pattern discovery.

**Parameters:**
- `start_page` (optional) - Starting page ID
- `end_page` (optional) - Ending page ID  
- `segment_id` (optional) - Segment filter
- `max_steps` (optional) - Maximum path length (default: 5)
- `days_back` (optional) - Analysis period (default: 7)

#### `calculate_product_engagement`
Product Engagement Score (PES) calculation.

**Parameters:**
- `segment_id` (optional) - Segment filter
- `features_list` (optional) - List of feature IDs to include
- `days_back` (optional) - Analysis period (default: 30)
- `group_by` (optional) - 'total' or 'account' (default: 'total')

### Feedback Tools

#### `analyze_nps_feedback`
NPS scoring and sentiment analysis.

**Parameters:**
- `segment_id` (optional) - Segment filter
- `poll_id` (optional) - Specific poll ID
- `days_back` (optional) - Analysis period (default: 30)
- `group_by` (optional) - 'total', 'day', or 'account' (default: 'total')

## 🎯 Advanced Features

### Intelligent Fallback Strategies

When primary analytics queries fail, the system automatically tries alternative approaches:

1. **Primary Strategy** - Original aggregation query
2. **Fallback Strategy 1** - Feature usage analysis  
3. **Fallback Strategy 2** - Page activity analysis
4. **Fallback Strategy 3** - Basic visitor activity
5. **Final Fallback** - Comprehensive help with tool suggestions

### Tool Chaining Patterns

**Discovery → Analysis**
```
search_pages(name_contains="checkout") → get page_id
analyze_feature_adoption(page_ids=[page_id], segment_id=X)
```

**Segment-Driven Analysis**  
```
analyze_segments(action="list") → select segment_id
analyze_retention(segment_id=segment_id, period_type="weekly")
```

**Funnel Analysis Chain**
```
search_pages() → identify key pages  
analyze_funnels(steps=[signup_page, activation_page, purchase_page])
```

### Universal Design Principles

- **Verb-based naming** - Clear action-oriented tool names
- **Progressive refinement** - Start broad, narrow with parameters
- **Universal segment support** - segment_id works everywhere
- **Minimal required params** - Most tools work with no parameters
- **Consistent patterns** - Similar parameter structures across tools

## 🛠️ Development

### Project Structure
```
pendo-mcp/
├── pendo_mcp_server.py      # Main MCP server implementation
├── test_server.py           # Server validation tests
├── requirements.txt         # Python dependencies  
├── .env                     # Environment configuration
├── FALLBACK_IMPLEMENTATION.md # Fallback strategy docs
└── memory-bank/            # Project documentation
    ├── high_priority_task.md
    ├── projectbrief.md
    └── progress.md
```

### Testing

```bash
# Test server functionality
python test_server.py

# Test with real queries
python -c "
import asyncio
from pendo_mcp_server import search_pages
result = asyncio.run(search_pages(limit=5, include_metrics=True))
print(result)
"
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request with clear description

## 🔒 Security & Best Practices

- **API Key Security** - Store integration keys in environment variables only
- **Read-Only Access** - Server only performs GET operations and aggregations
- **Rate Limiting** - Respects Pendo API rate limits
- **Error Handling** - Comprehensive error handling with helpful messages
- **Logging** - All logs to stderr to avoid STDIO conflicts

## ❓ Troubleshooting

### Common Issues

**"PENDO_INTEGRATION_KEY not found"**
- Ensure your `.env` file exists and contains the integration key
- Check Claude Desktop MCP configuration includes the environment variable

**"Unable to fetch data from Pendo API"**  
- Verify your integration key has appropriate permissions
- Check Pendo API status and rate limits
- Try more specific queries with filters

**"No data found" responses**
- Use intelligent fallback suggestions provided in error messages
- Try different time ranges or filters
- Check if data exists in Pendo UI for comparison

### Getting Help

- Review tool documentation and parameter options
- Check the FALLBACK_IMPLEMENTATION.md for fallback strategies
- Test individual tools with simple parameters first
- Use the analyze_segments tool to understand available segments

## 📈 Recent Enhancements

### Version 2.0 - Intelligent Analytics Platform
- ✅ **Complete 15-Tool Architecture** - Comprehensive analytics coverage
- ✅ **Intelligent Fallback Strategies** - Never fail silently, always provide value
- ✅ **Tool Consolidation** - Unified search tools with optional detailed metrics
- ✅ **Enhanced Error Handling** - Context-aware suggestions for alternative queries
- ✅ **LLM-Optimized Output** - Formatted specifically for AI consumption
- ✅ **Universal Segment Support** - Consistent filtering across all analytics tools

### Performance Improvements
- Reduced API calls through intelligent caching
- Optimized aggregation queries for faster responses  
- Enhanced timeout handling for complex analytics
- Better handling of large result sets

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP framework
- [Pendo](https://pendo.io/) for the comprehensive analytics API
- [FastMCP](https://github.com/jlowin/fastmcp) for the server framework
- The Claude AI team for MCP integration support

---

**Transform your Pendo analytics into AI-powered business intelligence with natural language queries and intelligent insights.** 🚀
