#!/usr/bin/env python3
"""
Test script to verify the Pendo MCP Server can start and has correct tools
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_server():
    """Test that the server can be imported and tools are registered"""
    try:
        # Import the server module
        import pendo_mcp_server
        
        print("✅ Server module imported successfully")
        print(f"✅ Integration key found: {'Yes' if os.getenv('PENDO_INTEGRATION_KEY') else 'No'}")
        
        # Check that MCP instance exists
        if hasattr(pendo_mcp_server, 'mcp'):
            print("✅ MCP server instance created")
            
            # Check that our tool functions exist
            tools_defined = []
            if hasattr(pendo_mcp_server, 'list_pages'):
                tools_defined.append('list_pages')
            if hasattr(pendo_mcp_server, 'get_visitor_details'):
                tools_defined.append('get_visitor_details')
            if hasattr(pendo_mcp_server, 'get_active_visitors'):
                tools_defined.append('get_active_visitors')
            
            print(f"✅ Number of tools defined: {len(tools_defined)}")
            for tool_name in tools_defined:
                print(f"   - {tool_name}")
            
            if len(tools_defined) == 3:
                print("\n✅ All 3 tools are properly configured!")
            
            print("\n✅ Server is ready to use!")
            print("\nTo connect to Claude Desktop, add this to your claude_desktop_config.json:")
            print(f"""
{{
  "mcpServers": {{
    "pendo": {{
      "command": "python3",
      "args": ["{os.path.abspath('pendo_mcp_server.py')}"]
    }}
  }}
}}
""")
        else:
            print("❌ MCP server instance not found")
            
    except ImportError as e:
        print(f"❌ Failed to import server: {e}")
        print("Please make sure all dependencies are installed: pip3 install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
