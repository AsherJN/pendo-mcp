# Active Context - Pendo MCP Server

## Current Work Focus

### Completed Phase: Proof of Concept
- Successfully created functional MCP server with 3 core tools
- Verified server starts and tools are registered
- Tested integration with Pendo API using live integration key
- Documentation and examples created

### Active Decisions

#### Tool Selection
Implemented three read-only tools as proof of concept:
1. **list_pages** - Most basic API call, lists resources
2. **get_visitor_details** - Demonstrates targeted data retrieval
3. **get_active_visitors** - Shows complex aggregation capabilities

These tools demonstrate the full range of Pendo API interactions: simple GET requests, parameterized queries, and aggregation pipelines.

#### Authentication Strategy
- Using environment variables for integration key storage
- Single key for all operations (no user-specific auth)
- Headers-based authentication (x-pendo-integration-key)

#### Response Formatting
- Human-readable text output instead of raw JSON
- Timestamp conversion to readable dates
- Limiting results to prevent overwhelming responses (e.g., 10 pages max)
- Summary statistics for aggregated data

## Recent Changes

### Initial Implementation (2025-01-16)
1. Created project structure with pyproject.toml and requirements.txt
2. Implemented pendo_mcp_server.py with three tools
3. Added comprehensive error handling
4. Created test_server.py for verification
5. Documented setup and usage

### Memory Bank Creation (2025-01-16)
- Initialized memory bank structure
- Documenting project context and decisions
- Capturing implementation patterns for future reference

## Next Steps

### Immediate
- [ ] Test with real Pendo data if available
- [ ] Validate Claude Desktop integration
- [ ] Monitor for API rate limiting issues

### Future Enhancements
- [ ] Add `list_features` tool for feature tracking
- [ ] Implement `get_account_details` for account information
- [ ] Add segment-based visitor search
- [ ] Include guide analytics tools
- [ ] Support for NPS score retrieval

## Important Patterns and Preferences

### Error Handling
- Never let exceptions crash the server
- Return user-friendly error messages
- Log technical details to stderr
- Suggest fixes when possible

### API Integration
```python
async def make_pendo_request(endpoint, method="GET", params=None, json_body=None):
    # Consistent pattern for all API calls
    # Includes timeout, error handling, and logging
```

### Tool Definition Pattern
```python
@mcp.tool()
async def tool_name(param: type) -> str:
    """Clear docstring for LLM understanding"""
    # Validation
    # API call
    # Format response
    # Return string
```

### Data Formatting
- Convert millisecond timestamps to readable dates
- Extract nested metadata safely with .get() methods
- Provide counts and summaries for large datasets
- Use clear section headers in output

## Learnings and Insights

### Pendo API Characteristics
1. **Timestamps**: All in milliseconds since epoch
2. **Nested Data**: Heavy use of nested objects in responses
3. **Aggregations**: Complex but powerful query language
4. **Rate Limits**: Not explicitly documented, monitor usage

### MCP Integration
1. **FastMCP**: Simplifies tool registration with decorators
2. **STDIO Transport**: Standard for Claude Desktop
3. **String Returns**: Tools should return formatted strings, not JSON
4. **Async Required**: All tool functions must be async

### Development Environment
- Python 3.13 works but some users may have 3.10-3.12
- Use python3 command (not python) on macOS
- pip3 for package installation
- Absolute paths required in Claude Desktop config

## Current State Assessment

### What's Working
✅ Server starts and initializes
✅ Integration key loads from environment
✅ All three tools registered successfully
✅ Error handling prevents crashes
✅ Logging configured to stderr

### Known Issues
- Rate limiting not yet tested at scale
- Multi-app subscription support untested
- Large dataset handling may need pagination

### Configuration State
- Integration key: Loaded from .env
- API Base URL: https://app.pendo.io (US region)
- Transport: STDIO
- Logging: INFO level to stderr
