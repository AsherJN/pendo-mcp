# System Patterns - Pendo MCP Server

## System Architecture

### Component Overview
```
┌─────────────────────────────────────┐
│         Claude Desktop              │
│    (or other MCP Client)            │
└──────────────┬──────────────────────┘
               │ STDIO
               ▼
┌─────────────────────────────────────┐
│      Pendo MCP Server               │
│  ┌─────────────────────────────┐    │
│  │    FastMCP Framework        │    │
│  ├─────────────────────────────┤    │
│  │    Tool Handlers            │    │
│  │  - list_pages              │    │
│  │  - get_visitor_details     │    │
│  │  - get_active_visitors     │    │
│  ├─────────────────────────────┤    │
│  │    HTTP Client (httpx)      │    │
│  └─────────────────────────────┘    │
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│         Pendo REST API              │
│       (app.pendo.io)                │
└─────────────────────────────────────┘
```

### Data Flow
1. **Request Phase**
   - User query → Claude Desktop
   - Claude selects appropriate tool
   - Tool invocation → MCP Server
   - Parameter validation

2. **API Phase**
   - Build API request with auth headers
   - Execute async HTTP request
   - Handle response or errors
   - Parse JSON response

3. **Response Phase**
   - Format data for readability
   - Convert timestamps
   - Limit result sets
   - Return formatted string

## Key Technical Decisions

### Async Architecture
All operations are async to prevent blocking:
```python
async def make_pendo_request(...) -> Dict[str, Any] | None
async def list_pages(...) -> str
async def get_visitor_details(...) -> str
async def get_active_visitors(...) -> str
```

### Error Handling Strategy
Three-layer error handling:
1. **HTTP Errors**: Caught and logged with status codes
2. **JSON Parsing**: Safe extraction with .get() methods
3. **User Feedback**: Friendly messages with suggestions

### Authentication Pattern
```python
headers = {
    "x-pendo-integration-key": PENDO_INTEGRATION_KEY,
    "Content-Type": "application/json"
}
```
Single integration key for all operations, loaded from environment.

## Design Patterns in Use

### Decorator Pattern
FastMCP's @mcp.tool() decorator for automatic tool registration:
```python
@mcp.tool()
async def tool_name(param: Type) -> str:
    """Docstring becomes tool description"""
```

### Factory Pattern
Centralized request creation in make_pendo_request():
- Consistent headers
- Unified error handling
- Standard timeout configuration

### Template Method Pattern
Common structure across all tools:
1. Validate inputs
2. Build API request
3. Execute request
4. Format response
5. Return string

## Component Relationships

### Core Dependencies
```
pendo_mcp_server.py
    ├── mcp.server.fastmcp (FastMCP)
    ├── httpx (AsyncClient)
    ├── dotenv (load_dotenv)
    ├── datetime (timestamp conversion)
    └── logging (stderr output)
```

### Tool Relationships
- **Independent Tools**: Each tool is self-contained
- **Shared Utilities**: Common helper functions (make_pendo_request, formatting)
- **No Inter-tool Dependencies**: Tools don't call each other

## Critical Implementation Paths

### 1. Server Initialization
```python
load_dotenv()  # Load environment
mcp = FastMCP("pendo-server")  # Create server
# Register tools with decorators
mcp.run(transport='stdio')  # Start server
```

### 2. API Request Path
```python
endpoint = "/api/v1/page"
data = await make_pendo_request(endpoint)
if not data:
    return error_message
# Process and format data
```

### 3. Aggregation Query Path
```python
aggregation_query = {
    "request": {
        "pipeline": [
            {"source": {...}},
            {"group": {...}},
            {"sort": [...]}
        ]
    }
}
data = await make_pendo_request(endpoint, "POST", json_body=aggregation_query)
```

## Data Structures

### API Response Format
```python
# Pages/Features
{
    "id": "string",
    "name": "string", 
    "appId": number,
    "createdAt": number  # milliseconds
}

# Visitors
{
    "id": "string",
    "metadata": {
        "auto": {
            "accountId": "string",
            "firstvisit": number
        },
        "custom": {...}
    }
}

# Aggregation Results
{
    "results": [
        {
            "day": number,
            "uniqueVisitors": number,
            "totalEvents": number
        }
    ]
}
```

## Security Considerations

### Authentication
- Integration key stored in .env file
- Never logged or exposed in responses
- Transmitted via HTTPS headers only

### Input Validation
- Parameter type checking
- Range validation for numeric inputs
- String sanitization implicit in httpx

### Output Safety
- No sensitive data in error messages
- Truncated results to prevent data overload
- Read-only operations only

## Performance Optimizations

### Result Limiting
```python
for page in data[:10]:  # Limit to first 10
    pages_info.append(format_page_info(page))
```

### Async Operations
- Non-blocking HTTP requests
- Concurrent capability (though not currently utilized)

### Caching Strategy
- No caching implemented (stateless design)
- Could add in-memory cache for repeated queries

## Extension Points

### Adding New Tools
1. Define async function with @mcp.tool() decorator
2. Add parameter validation
3. Call make_pendo_request() with appropriate endpoint
4. Format response
5. Return string

### Supporting New Endpoints
1. Identify endpoint and parameters
2. Add to make_pendo_request() if special handling needed
3. Create formatting function
4. Implement tool function

### Multi-Region Support
Would require:
- Region detection from integration key
- Dynamic base URL selection
- Region-specific error handling
