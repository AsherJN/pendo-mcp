# Tech Context - Pendo MCP Server

## Technologies Used

### Core Language
- **Python 3.10+**
  - Chosen for async support
  - Wide ecosystem of libraries
  - FastMCP SDK availability

### Primary Dependencies

#### MCP Framework
- **mcp[cli] >= 1.0.0**
  - FastMCP for simplified server creation
  - Built-in tool registration
  - STDIO transport support
  - CLI utilities for testing

#### HTTP Client
- **httpx >= 0.25.0**
  - Async HTTP client
  - Connection pooling
  - Timeout support
  - Better error handling than requests

#### Configuration
- **python-dotenv >= 1.0.0**
  - Environment variable management
  - .env file loading
  - Secure credential storage

### Development Dependencies
- **typer**: CLI framework (installed with mcp[cli])
- **rich**: Terminal formatting (installed with typer)
- **pydantic**: Data validation (installed with mcp)

## Development Setup

### Prerequisites
```bash
# Verify Python version
python3 --version  # Should be 3.10 or higher

# Install pip if needed
python3 -m ensurepip --upgrade
```

### Installation Steps
```bash
# Clone or create project directory
cd /Users/joshnelson/Desktop/pendo_mcp

# Install dependencies
pip3 install -r requirements.txt

# Or install individually
pip3 install "mcp[cli]" httpx python-dotenv
```

### Environment Configuration
Create `.env` file:
```
PENDO_INTEGRATION_KEY=your-key-here
```

### Running the Server
```bash
# Direct execution
python3 pendo_mcp_server.py

# Test mode
python3 test_server.py
```

## Technical Constraints

### MCP Protocol Requirements
- Must use STDIO transport for Claude Desktop
- Tools must return strings, not JSON
- All tool functions must be async
- Logging must go to stderr, not stdout

### Pendo API Constraints
- Rate limiting (undocumented limits)
- 5-minute maximum for aggregation queries
- 4GB maximum response size
- US region only (app.pendo.io)

### Python Constraints
- Type hints required for FastMCP
- Async/await syntax throughout
- Exception handling required to prevent crashes

## Dependencies Details

### Version Compatibility
```
mcp[cli]>=1.0.0       # Latest MCP protocol
httpx>=0.25.0         # Async HTTP support
python-dotenv>=1.0.0  # Environment management
```

### Dependency Tree
```
mcp[cli]
├── anyio>=4.5
├── httpx-sse>=0.4
├── jsonschema>=4.20.0
├── pydantic>=2.8.0
├── pydantic-settings>=2.5.2
├── starlette>=0.27
├── typer>=0.16.0
└── uvicorn>=0.23.1

httpx
├── certifi
├── httpcore==1.*
└── idna

python-dotenv
└── (no dependencies)
```

## Tool Usage Patterns

### FastMCP Tool Registration
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
async def tool_name(param: str) -> str:
    """Tool description"""
    return "result"

mcp.run(transport='stdio')
```

### Async HTTP Requests
```python
async with httpx.AsyncClient() as client:
    response = await client.get(url, headers=headers, timeout=30.0)
    response.raise_for_status()
    return response.json()
```

### Environment Loading
```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("PENDO_INTEGRATION_KEY")
```

## Configuration Files

### pyproject.toml
```toml
[project]
name = "pendo-mcp-server"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]",
    "httpx",
    "python-dotenv",
]
```

### requirements.txt
```
mcp[cli]>=1.0.0
httpx>=0.25.0
python-dotenv>=1.0.0
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "pendo": {
      "command": "python3",
      "args": ["/absolute/path/to/pendo_mcp_server.py"]
    }
  }
}
```

## Platform Considerations

### macOS
- Use `python3` command (not `python`)
- Use `pip3` for installation
- Config at `~/Library/Application Support/Claude/`

### Windows
- May need full Python path
- Config at `%APPDATA%\Claude\`
- Use forward slashes or double backslashes in paths

### Linux
- Claude Desktop not yet available
- Can test with custom MCP clients
- Standard Python commands work

## Debugging Tools

### Logging Configuration
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Critical: not stdout
)
```

### Test Script
```python
# test_server.py verifies:
- Server imports successfully
- Integration key loads
- Tools are registered
- No runtime errors
```

### Common Issues
1. **Import Error**: Missing dependencies
   - Solution: `pip3 install -r requirements.txt`

2. **No Integration Key**: Environment not loaded
   - Solution: Check .env file exists and contains key

3. **Server Won't Start**: Stdout interference
   - Solution: Ensure logging to stderr only

4. **API Errors**: Invalid key or permissions
   - Solution: Verify key in Pendo settings

## Future Tech Considerations

### Potential Upgrades
- **Caching**: Redis for response caching
- **Database**: SQLite for offline data storage
- **Monitoring**: Prometheus metrics
- **Testing**: pytest with async support

### Scaling Considerations
- Connection pooling for high volume
- Rate limit tracking
- Request queuing
- Concurrent request handling
