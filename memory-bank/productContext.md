# Product Context - Pendo MCP Server

## Why This Project Exists

### Problem Statement
Pendo is a powerful product analytics and user guidance platform, but accessing its data programmatically requires:
- Direct API integration with authentication
- Understanding complex aggregation query syntax
- Manual data extraction and formatting
- Technical expertise to interpret API responses

AI assistants like Claude Desktop need a standardized way to access Pendo data through natural language queries, without users needing to understand API complexities.

### Solution
The Pendo MCP Server bridges this gap by:
- Providing a Model Context Protocol interface to Pendo's API
- Translating natural language requests into API calls
- Formatting responses in human-readable formats
- Handling authentication and error states gracefully

## How It Should Work

### User Experience Flow
1. **Setup Phase**
   - User obtains Pendo Integration Key from their account
   - Configures key in .env file
   - Adds server to Claude Desktop configuration
   - Restarts Claude Desktop

2. **Query Phase**
   - User asks natural language questions about Pendo data
   - Claude interprets intent and selects appropriate tool
   - Server makes authenticated API requests
   - Formatted results returned to user

3. **Response Format**
   - Clear, structured text output
   - Key metrics highlighted
   - Counts and summaries provided
   - Error messages are helpful and actionable

### Core Interactions

#### List Pages
- **Input**: Optional app ID for filtering
- **Process**: Query /api/v1/page endpoint
- **Output**: Formatted list with IDs, names, creation dates

#### Get Visitor Details  
- **Input**: Visitor ID
- **Process**: Query /api/v1/visitor/{id} endpoint
- **Output**: Visitor metadata, account info, activity history

#### Get Active Visitors
- **Input**: Time range and grouping preference
- **Process**: Build and execute aggregation query
- **Output**: Time-series data with visitor counts and events

## User Goals

### Product Managers
- Quick access to visitor behavior patterns
- Understanding page usage without complex queries
- Monitoring user activity trends

### Developers
- Testing API integrations
- Validating visitor tracking
- Debugging page tagging issues

### Analysts
- Extracting metrics for reports
- Identifying active user segments
- Tracking engagement over time

## Design Principles

1. **Simplicity First**: Tools should be intuitive with sensible defaults
2. **Helpful Errors**: Failed requests should explain why and suggest fixes
3. **Progressive Disclosure**: Show summary first, details on request
4. **Read-Only Safety**: Never modify data, only retrieve
5. **Performance Aware**: Limit results to prevent overwhelming responses
