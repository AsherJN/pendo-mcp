# Pendo MCP Server - Project Brief

## Project Overview
A Model Context Protocol (MCP) server that provides programmatic access to the Pendo platform through its REST API, enabling Claude Desktop and other MCP clients to interact with Pendo data.

## Core Requirements

### Functional Requirements
1. **Read-only Access**: Server must only perform GET operations and aggregation queries (no write operations)
2. **Three Core Tools**: 
   - List tagged pages from Pendo
   - Retrieve visitor details by ID
   - Get active visitor metrics
3. **Authentication**: Use Pendo Integration Key for API authentication
4. **MCP Compliance**: Follow MCP protocol standards for tool definitions and responses

### Technical Requirements
- Python 3.10+ compatibility
- FastMCP framework for MCP server implementation
- Async HTTP requests using httpx
- Environment variable management with python-dotenv
- STDIO transport for Claude Desktop integration
- Error handling and logging to stderr (not stdout)

## Project Goals

### Primary Goals
1. Create a functional proof-of-concept MCP server for Pendo API integration
2. Demonstrate search and read capabilities from Pendo platform
3. Provide a foundation for future tool expansion

### Success Criteria
- [x] Server starts without errors
- [x] Integration key loads from .env file
- [x] All 3 tools are registered and callable
- [x] Server can connect to Claude Desktop
- [x] API requests return valid data
- [x] Proper error handling for API failures

## Scope

### In Scope
- Read operations for pages, visitors, and activity metrics
- Basic authentication using integration keys
- Error handling and user-friendly responses
- Documentation and setup instructions

### Out of Scope
- Write operations (creating/updating data)
- Guide management
- Feedback/Listen module integration
- Multi-region support (US region only)
- Bulk data exports

## Constraints
- Must use existing Pendo REST API endpoints
- Limited to operations allowed by integration key permissions
- Rate limiting per Pendo API guidelines
- 5-minute runtime limit for aggregations
- 4GB output limit for aggregations

## Target Users
- Developers integrating Pendo with AI assistants
- Product managers querying Pendo data via natural language
- Analytics teams needing programmatic access to Pendo metrics
