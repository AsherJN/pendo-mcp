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
            expected_tools = [
                'list_pages',
                'get_visitor_details', 
                'get_active_visitors',
                'list_features',
                'get_feature_details',
                'list_track_events',
                'search_track_events',
                'get_account_details',
                'search_accounts_by_metadata',
                'list_account_visitors'
            ]
            
            for tool_name in expected_tools:
                if hasattr(pendo_mcp_server, tool_name):
                    tools_defined.append(tool_name)
            
            print(f"✅ Number of tools defined: {len(tools_defined)}")
            for tool_name in tools_defined:
                print(f"   - {tool_name}")
            
            # Check if all expected tools are present
            missing_tools = [t for t in expected_tools if t not in tools_defined]
            if missing_tools:
                print(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
            
            if len(tools_defined) == len(expected_tools):
                print(f"\n✅ All {len(expected_tools)} tools are properly configured!")
            else:
                print(f"\n⚠️  {len(tools_defined)}/{len(expected_tools)} tools configured")
            
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
