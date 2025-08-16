#!/usr/bin/env python3
"""
Pendo MCP Server - Model Context Protocol server for Pendo API integration
"""

import os
import sys
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
import json

import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to stderr only (not stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("pendo-server")

# Constants
PENDO_API_BASE = "https://app.pendo.io"
PENDO_INTEGRATION_KEY = os.getenv("PENDO_INTEGRATION_KEY")

if not PENDO_INTEGRATION_KEY:
    logger.error("PENDO_INTEGRATION_KEY not found in environment variables")
    sys.exit(1)

# Helper functions
async def make_pendo_request(
    endpoint: str, 
    method: str = "GET", 
    params: Optional[Dict] = None,
    json_body: Optional[Dict] = None
) -> Dict[str, Any] | None:
    """Make a request to the Pendo API with proper authentication and error handling."""
    headers = {
        "x-pendo-integration-key": PENDO_INTEGRATION_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"{PENDO_API_BASE}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=json_body, timeout=30.0)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error making Pendo API request: {str(e)}")
            return None

def format_page_info(page: Dict) -> str:
    """Format page information for readable output."""
    page_id = page.get('id', 'Unknown')
    page_name = page.get('name', 'Unnamed Page')
    app_id = page.get('appId', 'Unknown')
    created_at = page.get('createdAt', 0)
    
    # Convert timestamp to readable date
    if created_at:
        created_date = datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        created_date = 'Unknown'
    
    return f"""
Page ID: {page_id}
Name: {page_name}
App ID: {app_id}
Created: {created_date}
"""

def format_visitor_info(visitor: Dict) -> str:
    """Format visitor information for readable output."""
    visitor_id = visitor.get('id', 'Unknown')
    metadata = visitor.get('metadata', {})
    auto_metadata = metadata.get('auto', {})
    
    account_id = auto_metadata.get('accountId', 'None')
    first_visit = auto_metadata.get('firstvisit', 0)
    last_browser = auto_metadata.get('lastbrowsername', 'Unknown')
    
    # Convert timestamp to readable date
    if first_visit:
        first_visit_date = datetime.fromtimestamp(first_visit / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        first_visit_date = 'Unknown'
    
    # Extract custom metadata if available
    custom_metadata = metadata.get('custom', {})
    custom_fields = []
    for key, value in custom_metadata.items():
        custom_fields.append(f"  {key}: {value}")
    
    result = f"""
Visitor ID: {visitor_id}
Account ID: {account_id}
First Visit: {first_visit_date}
Last Browser: {last_browser}
"""
    
    if custom_fields:
        result += "\nCustom Fields:\n" + "\n".join(custom_fields)
    
    return result

# MCP Tool Implementations

@mcp.tool()
async def list_pages(app_id: Optional[str] = None) -> str:
    """
    List all tagged pages in Pendo.
    
    Args:
        app_id: Optional application ID for multi-app subscriptions
    """
    endpoint = "/api/v1/page"
    params = {}
    
    if app_id:
        params['appId'] = app_id
    
    data = await make_pendo_request(endpoint, params=params)
    
    if not data:
        return "Unable to fetch pages from Pendo API. Please check your integration key and permissions."
    
    if not isinstance(data, list):
        return "Unexpected response format from Pendo API."
    
    if not data:
        return "No pages found in your Pendo subscription."
    
    # Format the pages for output
    pages_info = []
    for page in data[:10]:  # Limit to first 10 pages for readability
        pages_info.append(format_page_info(page))
    
    result = f"Found {len(data)} pages in Pendo.\n"
    result += "Showing first 10 pages:\n"
    result += "\n---\n".join(pages_info)
    
    if len(data) > 10:
        result += f"\n\n... and {len(data) - 10} more pages."
    
    return result

@mcp.tool()
async def get_visitor_details(visitor_id: str) -> str:
    """
    Get detailed information about a specific visitor.
    
    Args:
        visitor_id: The Pendo visitor ID
    """
    if not visitor_id:
        return "Visitor ID is required."
    
    endpoint = f"/api/v1/visitor/{visitor_id}"
    
    data = await make_pendo_request(endpoint)
    
    if not data:
        return f"Unable to fetch visitor details for ID: {visitor_id}. The visitor may not exist or you may not have permission to view it."
    
    return format_visitor_info(data)

@mcp.tool()
async def get_active_visitors(
    days_back: int = 7,
    group_by: str = "day"
) -> str:
    """
    Get active visitor counts using Pendo's aggregation API.
    
    Args:
        days_back: Number of days to look back (default: 7)
        group_by: Group results by 'day' or 'hour' (default: 'day')
    """
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if group_by not in ['day', 'hour']:
        return "Group by must be either 'day' or 'hour'."
    
    # Build aggregation query
    period = "dayRange" if group_by == "day" else "hourRange"
    group_field = "day" if group_by == "day" else "hour"
    
    aggregation_query = {
        "response": {
            "mimeType": "application/json"
        },
        "request": {
            "name": "Active Visitors Query",
            "pipeline": [
                {
                    "source": {
                        "events": None,
                        "timeSeries": {
                            "period": period,
                            "first": "now()",
                            "count": -days_back
                        }
                    }
                },
                {
                    "group": {
                        "group": [group_field],
                        "fields": {
                            "uniqueVisitors": {
                                "count": "visitorId"
                            },
                            "totalEvents": {
                                "sum": "numEvents"
                            }
                        }
                    }
                },
                {
                    "sort": [group_field]
                }
            ]
        }
    }
    
    endpoint = "/api/v1/aggregation"
    data = await make_pendo_request(endpoint, method="POST", json_body=aggregation_query)
    
    if not data:
        return "Unable to fetch visitor activity data from Pendo API."
    
    results = data.get('results', [])
    
    if not results:
        return f"No visitor activity found in the last {days_back} days."
    
    # Format results
    output_lines = [f"Active Visitors Report - Last {days_back} days"]
    output_lines.append("=" * 50)
    
    total_unique_visitors = 0
    total_events = 0
    
    for row in results:
        if group_by == "day":
            timestamp = row.get('day', 0)
            if timestamp:
                date_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            else:
                date_str = 'Unknown'
            period_label = f"Date: {date_str}"
        else:
            timestamp = row.get('hour', 0)
            if timestamp:
                date_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:00')
            else:
                date_str = 'Unknown'
            period_label = f"Hour: {date_str}"
        
        unique_visitors = row.get('uniqueVisitors', 0)
        total_events_period = row.get('totalEvents', 0)
        
        total_unique_visitors = max(total_unique_visitors, unique_visitors)
        total_events += total_events_period
        
        output_lines.append(f"{period_label}")
        output_lines.append(f"  Unique Visitors: {unique_visitors:,}")
        output_lines.append(f"  Total Events: {total_events_period:,}")
        output_lines.append("")
    
    output_lines.append("=" * 50)
    output_lines.append("Summary:")
    output_lines.append(f"Total Events: {total_events:,}")
    output_lines.append(f"Peak Unique Visitors: {total_unique_visitors:,}")
    
    return "\n".join(output_lines)

# Main execution
if __name__ == "__main__":
    # Verify API key is configured
    logger.info(f"Starting Pendo MCP Server")
    logger.info(f"Using Pendo API base URL: {PENDO_API_BASE}")
    
    # Run the server
    mcp.run(transport='stdio')
