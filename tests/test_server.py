#!/usr/bin/env python3
"""
Test script to verify the Pendo MCP Server can start and has correct tools
Updated for the 15-tool architecture
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
            
            # Check that our tool functions exist - Updated for 15-tool architecture
            tools_defined = []
            expected_tools = [
                # PRODUCT DISCOVERY (3 tools)
                'search_pages',
                'search_features',
                'search_track_events',
                # PEOPLE INSIGHTS (5 tools)
                'get_visitor_details',
                'search_visitors',
                'get_account_details',
                'search_accounts',
                'analyze_segments',
                # BEHAVIORAL ANALYTICS (6 tools)
                'analyze_usage',
                'analyze_feature_adoption',
                'analyze_retention',
                'analyze_funnels',
                'analyze_user_paths',
                'calculate_product_engagement',
                # FEEDBACK (1 tool)
                'analyze_nps_feedback'
            ]
            
            for tool_name in expected_tools:
                if hasattr(pendo_mcp_server, tool_name):
                    tools_defined.append(tool_name)
            
            print(f"✅ Number of tools defined: {len(tools_defined)}")
            
            # Group tools by category for display
            product_tools = ['search_pages', 'search_features', 'search_track_events']
            people_tools = ['get_visitor_details', 'search_visitors', 'get_account_details', 'search_accounts', 'analyze_segments']
            analytics_tools = ['analyze_usage', 'analyze_feature_adoption', 'analyze_retention', 'analyze_funnels', 'analyze_user_paths', 'calculate_product_engagement']
            feedback_tools = ['analyze_nps_feedback']
            
            print("\n📊 PRODUCT DISCOVERY TOOLS:")
            for tool in product_tools:
                status = "✅" if tool in tools_defined else "❌"
                print(f"   {status} {tool}")
            
            print("\n👥 PEOPLE INSIGHTS TOOLS:")
            for tool in people_tools:
                status = "✅" if tool in tools_defined else "❌"
                print(f"   {status} {tool}")
            
            print("\n📈 BEHAVIORAL ANALYTICS TOOLS:")
            for tool in analytics_tools:
                status = "✅" if tool in tools_defined else "❌"
                print(f"   {status} {tool}")
            
            print("\n💬 FEEDBACK TOOLS:")
            for tool in feedback_tools:
                status = "✅" if tool in tools_defined else "❌"
                print(f"   {status} {tool}")
            
            # Check if all expected tools are present
            missing_tools = [t for t in expected_tools if t not in tools_defined]
            if missing_tools:
                print(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
            
            if len(tools_defined) == len(expected_tools):
                print(f"\n🎉 All {len(expected_tools)} tools are properly configured!")
                print("✅ 15-tool architecture implementation complete!")
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
            
            print("\n🔧 Tool Capabilities Summary:")
            print("   • Product Discovery: Search pages/features with optional metrics")
            print("   • People Insights: Comprehensive visitor/account analysis")
            print("   • Behavioral Analytics: Usage patterns, adoption, retention, funnels")
            print("   • Engagement Scoring: PES calculation and user path analysis")
            print("   • Feedback Analysis: NPS scoring with flexible grouping")
            
        else:
            print("❌ MCP server instance not found")
            
    except ImportError as e:
        print(f"❌ Failed to import server: {e}")
        print("Please make sure all dependencies are installed: pip3 install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
