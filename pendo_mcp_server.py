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

def format_feature_info(feature: Dict) -> str:
    """Format feature information for readable output."""
    feature_id = feature.get('id', 'Unknown')
    feature_name = feature.get('name', 'Unnamed Feature')
    app_id = feature.get('appId', 'Unknown')
    created_at = feature.get('createdAt', 0)
    color = feature.get('color', 'None')
    
    # Convert timestamp to readable date
    if created_at:
        created_date = datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        created_date = 'Unknown'
    
    # Get element path if available
    element_path = feature.get('elementPathRule', 'Not specified')
    
    return f"""
Feature ID: {feature_id}
Name: {feature_name}
App ID: {app_id}
Color: {color}
Created: {created_date}
Element Path: {element_path}
"""

def format_track_event_info(track_event: Dict) -> str:
    """Format track event information for readable output."""
    event_id = track_event.get('id', 'Unknown')
    event_name = track_event.get('name', 'Unnamed Event')
    app_id = track_event.get('appId', 'Unknown')
    created_at = track_event.get('createdAt', 0)
    
    # Convert timestamp to readable date
    if created_at:
        created_date = datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        created_date = 'Unknown'
    
    # Get last updated time
    last_updated = track_event.get('lastUpdatedAt', 0)
    if last_updated:
        last_updated_date = datetime.fromtimestamp(last_updated / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        last_updated_date = 'Unknown'
    
    return f"""
Track Event ID: {event_id}
Name: {event_name}
App ID: {app_id}
Created: {created_date}
Last Updated: {last_updated_date}
"""

def format_account_info(account: Dict) -> str:
    """Format account information for readable output."""
    account_id = account.get('id', account.get('accountId', 'Unknown'))
    metadata = account.get('metadata', {})
    auto_metadata = metadata.get('auto', {})
    
    # Auto metadata fields
    first_visit = auto_metadata.get('firstvisit', 0)
    last_visit = auto_metadata.get('lastvisit', 0)
    last_updated = auto_metadata.get('lastupdated', 0)
    
    # Convert timestamps to readable dates
    first_visit_date = 'Unknown'
    if first_visit:
        first_visit_date = datetime.fromtimestamp(first_visit / 1000).strftime('%Y-%m-%d %H:%M:%S')
    
    last_visit_date = 'Unknown'
    if last_visit:
        last_visit_date = datetime.fromtimestamp(last_visit / 1000).strftime('%Y-%m-%d %H:%M:%S')
    
    last_updated_date = 'Unknown'
    if last_updated:
        last_updated_date = datetime.fromtimestamp(last_updated / 1000).strftime('%Y-%m-%d %H:%M:%S')
    
    # Extract custom metadata if available
    custom_metadata = metadata.get('custom', {})
    agent_metadata = metadata.get('agent', {})
    
    result = f"""
Account ID: {account_id}
First Visit: {first_visit_date}
Last Visit: {last_visit_date}
Last Updated: {last_updated_date}
"""
    
    # Add custom fields if present
    if custom_metadata:
        result += "\nCustom Fields:"
        for key, value in custom_metadata.items():
            result += f"\n  {key}: {value}"
    
    # Add agent fields if present
    if agent_metadata:
        result += "\nAgent Fields:"
        for key, value in agent_metadata.items():
            result += f"\n  {key}: {value}"
    
    # Check for multi-app metadata
    for key in metadata.get('auto', {}).keys():
        if key.startswith('auto__'):
            app_id = key.replace('auto__', '')
            app_data = auto_metadata.get(key, {})
            if app_data:
                result += f"\n\nApp {app_id} Metadata:"
                for field, value in app_data.items():
                    result += f"\n  {field}: {value}"
    
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

# Phase 1: Features & Track Events Tools

@mcp.tool()
async def list_features(app_id: Optional[str] = None) -> str:
    """
    List all tagged features in Pendo.
    
    Args:
        app_id: Optional application ID for multi-app subscriptions
    """
    endpoint = "/api/v1/feature"
    params = {}
    
    if app_id:
        params['appId'] = app_id
    
    data = await make_pendo_request(endpoint, params=params)
    
    if not data:
        return "Unable to fetch features from Pendo API. Please check your integration key and permissions."
    
    if not isinstance(data, list):
        return "Unexpected response format from Pendo API."
    
    if not data:
        return "No features found in your Pendo subscription."
    
    # Format the features for output
    features_info = []
    for feature in data[:10]:  # Limit to first 10 features for readability
        features_info.append(format_feature_info(feature))
    
    result = f"Found {len(data)} features in Pendo.\n"
    result += "Showing first 10 features:\n"
    result += "\n---\n".join(features_info)
    
    if len(data) > 10:
        result += f"\n\n... and {len(data) - 10} more features."
    
    return result

@mcp.tool()
async def get_feature_details(feature_id: str) -> str:
    """
    Get detailed information about specific feature(s).
    
    Args:
        feature_id: The Pendo feature ID or comma-separated IDs
    """
    if not feature_id:
        return "Feature ID is required."
    
    endpoint = "/api/v1/feature"
    params = {'id': feature_id}
    
    data = await make_pendo_request(endpoint, params=params)
    
    if not data:
        return f"Unable to fetch feature details for ID(s): {feature_id}. The feature(s) may not exist or you may not have permission to view them."
    
    # Handle single feature or list of features
    if isinstance(data, dict):
        return format_feature_info(data)
    elif isinstance(data, list):
        if not data:
            return f"No features found for ID(s): {feature_id}"
        
        features_info = []
        for feature in data:
            features_info.append(format_feature_info(feature))
        
        result = f"Found {len(data)} feature(s):\n"
        result += "\n---\n".join(features_info)
        return result
    else:
        return "Unexpected response format from Pendo API."

@mcp.tool()
async def list_track_events(app_id: Optional[str] = None) -> str:
    """
    List all track event types in Pendo.
    
    Args:
        app_id: Optional application ID for multi-app subscriptions
    """
    endpoint = "/api/v1/tracktype"
    params = {}
    
    if app_id:
        params['appId'] = app_id
    
    data = await make_pendo_request(endpoint, params=params)
    
    if not data:
        return "Unable to fetch track events from Pendo API. Please check your integration key and permissions."
    
    if not isinstance(data, list):
        return "Unexpected response format from Pendo API."
    
    if not data:
        return "No track events found in your Pendo subscription."
    
    # Format the track events for output
    events_info = []
    for event in data[:10]:  # Limit to first 10 events for readability
        events_info.append(format_track_event_info(event))
    
    result = f"Found {len(data)} track event types in Pendo.\n"
    result += "Showing first 10 track events:\n"
    result += "\n---\n".join(events_info)
    
    if len(data) > 10:
        result += f"\n\n... and {len(data) - 10} more track events."
    
    return result

@mcp.tool()
async def search_track_events(
    event_name: Optional[str] = None,
    days_back: int = 7,
    visitor_id: Optional[str] = None,
    account_id: Optional[str] = None,
    limit: int = 100
) -> str:
    """
    Search for track events with filters.
    
    Args:
        event_name: Optional track event name to filter
        days_back: Number of days to search (default: 7, max: 90)
        visitor_id: Optional visitor ID filter
        account_id: Optional account ID filter
        limit: Maximum number of results to return (default: 100, max: 1000)
    """
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if limit < 1 or limit > 1000:
        return "Limit must be between 1 and 1000."
    
    # First, get the track type ID if event_name is provided
    track_type_id = None
    if event_name:
        endpoint = "/api/v1/tracktype"
        track_types = await make_pendo_request(endpoint)
        
        if track_types and isinstance(track_types, list):
            for track_type in track_types:
                if track_type.get('name') == event_name:
                    track_type_id = track_type.get('id')
                    break
            
            if not track_type_id:
                return f"Track event '{event_name}' not found. Please check the event name."
    
    # Build aggregation query
    pipeline = [
        {
            "source": {
                "trackEvents": {
                    "trackTypeId": track_type_id
                } if track_type_id else {},
                "timeSeries": {
                    "period": "dayRange",
                    "first": "now()",
                    "count": -days_back
                }
            }
        }
    ]
    
    # Add filters if provided
    filters = []
    if visitor_id:
        filters.append(f'visitorId == "{visitor_id}"')
    if account_id:
        filters.append(f'accountId == "{account_id}"')
    
    if filters:
        pipeline.append({
            "filter": " && ".join(filters)
        })
    
    # Add grouping to get event details
    pipeline.append({
        "group": {
            "group": ["visitorId", "accountId", "trackTypeId", "day"],
            "fields": {
                "eventCount": {
                    "sum": "numEvents"
                }
            }
        }
    })
    
    # Sort by day and limit results
    pipeline.append({"sort": ["-day", "-eventCount"]})
    pipeline.append({"limit": limit})
    
    aggregation_query = {
        "response": {
            "mimeType": "application/json"
        },
        "request": {
            "name": "Track Events Search",
            "pipeline": pipeline
        }
    }
    
    endpoint = "/api/v1/aggregation"
    data = await make_pendo_request(endpoint, method="POST", json_body=aggregation_query)
    
    if not data:
        return "Unable to fetch track events data from Pendo API."
    
    results = data.get('results', [])
    
    if not results:
        filter_desc = []
        if event_name:
            filter_desc.append(f"event '{event_name}'")
        if visitor_id:
            filter_desc.append(f"visitor '{visitor_id}'")
        if account_id:
            filter_desc.append(f"account '{account_id}'")
        
        if filter_desc:
            return f"No track events found in the last {days_back} days for {' and '.join(filter_desc)}."
        else:
            return f"No track events found in the last {days_back} days."
    
    # Format results
    output_lines = [f"Track Events Search Results - Last {days_back} days"]
    if event_name:
        output_lines.append(f"Event Name: {event_name}")
    if visitor_id:
        output_lines.append(f"Visitor Filter: {visitor_id}")
    if account_id:
        output_lines.append(f"Account Filter: {account_id}")
    output_lines.append("=" * 50)
    
    total_events = 0
    unique_visitors = set()
    unique_accounts = set()
    
    for row in results:
        day_timestamp = row.get('day', 0)
        if day_timestamp:
            date_str = datetime.fromtimestamp(day_timestamp / 1000).strftime('%Y-%m-%d')
        else:
            date_str = 'Unknown'
        
        visitor = row.get('visitorId', 'Unknown')
        account = row.get('accountId', 'None')
        event_count = row.get('eventCount', 0)
        
        unique_visitors.add(visitor)
        if account != 'None':
            unique_accounts.add(account)
        total_events += event_count
        
        output_lines.append(f"Date: {date_str}")
        output_lines.append(f"  Visitor: {visitor}")
        output_lines.append(f"  Account: {account}")
        output_lines.append(f"  Event Count: {event_count:,}")
        output_lines.append("")
    
    output_lines.append("=" * 50)
    output_lines.append("Summary:")
    output_lines.append(f"Total Events: {total_events:,}")
    output_lines.append(f"Unique Visitors: {len(unique_visitors):,}")
    output_lines.append(f"Unique Accounts: {len(unique_accounts):,}")
    output_lines.append(f"Results Shown: {len(results)} (limited to {limit})")
    
    return "\n".join(output_lines)

# Phase 2: Account Tools

@mcp.tool()
async def get_account_details(account_id: str) -> str:
    """
    Get detailed information about a specific account.
    
    Args:
        account_id: The Pendo account ID
    """
    if not account_id:
        return "Account ID is required."
    
    endpoint = f"/api/v1/account/{account_id}"
    
    data = await make_pendo_request(endpoint)
    
    if not data:
        return f"Unable to fetch account details for ID: {account_id}. The account may not exist or you may not have permission to view it."
    
    # Get visitor count for this account
    visitor_count = 0
    aggregation_query = {
        "response": {
            "mimeType": "application/json"
        },
        "request": {
            "name": "Account Visitor Count",
            "pipeline": [
                {
                    "source": {
                        "visitors": None
                    }
                },
                {
                    "filter": f'metadata.auto.accountId == "{account_id}" || contains(metadata.auto.accountIds, "{account_id}")'
                },
                {
                    "count": None
                }
            ]
        }
    }
    
    endpoint_agg = "/api/v1/aggregation"
    count_data = await make_pendo_request(endpoint_agg, method="POST", json_body=aggregation_query)
    
    if count_data and count_data.get('results'):
        results = count_data.get('results', [])
        if results and len(results) > 0:
            visitor_count = results[0].get('count', 0)
    
    # Format output
    result = format_account_info(data)
    result += f"\n\nVisitor Count: {visitor_count:,}"
    
    return result

@mcp.tool()
async def search_accounts_by_metadata(
    field_name: str,
    field_value: str,
    field_type: str = "custom"
) -> str:
    """
    Search accounts by metadata field values.
    
    Args:
        field_name: Name of the metadata field
        field_value: Value to search for
        field_type: Type of field - 'custom', 'agent', or 'auto' (default: 'custom')
    """
    if not field_name:
        return "Field name is required."
    
    if not field_value:
        return "Field value is required."
    
    if field_type not in ['custom', 'agent', 'auto']:
        return "Field type must be 'custom', 'agent', or 'auto'."
    
    # Build the field path based on type
    field_path = f"metadata.{field_type}.{field_name}"
    
    # Build aggregation query
    aggregation_query = {
        "response": {
            "mimeType": "application/json"
        },
        "request": {
            "name": "Account Metadata Search",
            "pipeline": [
                {
                    "source": {
                        "accounts": None
                    }
                },
                {
                    "filter": f'{field_path} == "{field_value}"'
                },
                {
                    "select": {
                        "accountId": "accountId",
                        "firstVisit": "metadata.auto.firstvisit",
                        "lastVisit": "metadata.auto.lastvisit",
                        "searchField": field_path
                    }
                },
                {
                    "limit": 100
                }
            ]
        }
    }
    
    endpoint = "/api/v1/aggregation"
    data = await make_pendo_request(endpoint, method="POST", json_body=aggregation_query)
    
    if not data:
        return "Unable to search accounts in Pendo API."
    
    results = data.get('results', [])
    
    if not results:
        return f"No accounts found with {field_type} field '{field_name}' = '{field_value}'"
    
    # Format results
    output_lines = [f"Account Search Results"]
    output_lines.append(f"Search Criteria: {field_type}.{field_name} = {field_value}")
    output_lines.append(f"Found {len(results)} matching account(s)")
    output_lines.append("=" * 50)
    
    for idx, account in enumerate(results[:20], 1):  # Limit display to 20
        account_id = account.get('accountId', 'Unknown')
        first_visit = account.get('firstVisit', 0)
        last_visit = account.get('lastVisit', 0)
        
        first_visit_str = 'Unknown'
        if first_visit:
            first_visit_str = datetime.fromtimestamp(first_visit / 1000).strftime('%Y-%m-%d')
        
        last_visit_str = 'Unknown'
        if last_visit:
            last_visit_str = datetime.fromtimestamp(last_visit / 1000).strftime('%Y-%m-%d')
        
        output_lines.append(f"\n{idx}. Account ID: {account_id}")
        output_lines.append(f"   First Visit: {first_visit_str}")
        output_lines.append(f"   Last Visit: {last_visit_str}")
        output_lines.append(f"   {field_name}: {account.get('searchField', 'N/A')}")
    
    if len(results) > 20:
        output_lines.append(f"\n... and {len(results) - 20} more accounts")
    
    return "\n".join(output_lines)

@mcp.tool()
async def list_account_visitors(
    account_id: str,
    include_metadata: bool = False
) -> str:
    """
    List all visitors associated with an account.
    
    Args:
        account_id: The Pendo account ID
        include_metadata: Include visitor metadata (default: False)
    """
    if not account_id:
        return "Account ID is required."
    
    # Build aggregation query
    pipeline = [
        {
            "source": {
                "visitors": None
            }
        },
        {
            "filter": f'metadata.auto.accountId == "{account_id}" || contains(metadata.auto.accountIds, "{account_id}")'
        }
    ]
    
    # Select fields based on include_metadata parameter
    if include_metadata:
        pipeline.append({
            "select": {
                "visitorId": "id",
                "accountId": "metadata.auto.accountId",
                "firstVisit": "metadata.auto.firstvisit",
                "lastBrowser": "metadata.auto.lastbrowsername",
                "customFields": "metadata.custom",
                "agentFields": "metadata.agent"
            }
        })
    else:
        pipeline.append({
            "select": {
                "visitorId": "id",
                "firstVisit": "metadata.auto.firstvisit",
                "lastBrowser": "metadata.auto.lastbrowsername"
            }
        })
    
    # Sort by first visit (most recent first) and limit
    pipeline.append({"sort": ["-firstVisit"]})
    pipeline.append({"limit": 100})
    
    aggregation_query = {
        "response": {
            "mimeType": "application/json"
        },
        "request": {
            "name": "Account Visitors List",
            "pipeline": pipeline
        }
    }
    
    endpoint = "/api/v1/aggregation"
    data = await make_pendo_request(endpoint, method="POST", json_body=aggregation_query)
    
    if not data:
        return f"Unable to fetch visitors for account {account_id} from Pendo API."
    
    results = data.get('results', [])
    
    if not results:
        return f"No visitors found for account ID: {account_id}"
    
    # Format results
    output_lines = [f"Visitors for Account: {account_id}"]
    output_lines.append(f"Total Visitors Found: {len(results)}")
    output_lines.append("=" * 50)
    
    for idx, visitor in enumerate(results[:50], 1):  # Limit display to 50
        visitor_id = visitor.get('visitorId', 'Unknown')
        first_visit = visitor.get('firstVisit', 0)
        last_browser = visitor.get('lastBrowser', 'Unknown')
        
        first_visit_str = 'Unknown'
        if first_visit:
            first_visit_str = datetime.fromtimestamp(first_visit / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        output_lines.append(f"\n{idx}. Visitor ID: {visitor_id}")
        output_lines.append(f"   First Visit: {first_visit_str}")
        output_lines.append(f"   Browser: {last_browser}")
        
        if include_metadata:
            # Add custom fields if present
            custom_fields = visitor.get('customFields', {})
            if custom_fields:
                output_lines.append("   Custom Fields:")
                for key, value in custom_fields.items():
                    output_lines.append(f"     {key}: {value}")
            
            # Add agent fields if present
            agent_fields = visitor.get('agentFields', {})
            if agent_fields:
                output_lines.append("   Agent Fields:")
                for key, value in agent_fields.items():
                    output_lines.append(f"     {key}: {value}")
    
    if len(results) > 50:
        output_lines.append(f"\n... and {len(results) - 50} more visitors")
        output_lines.append("\nNote: Results limited to 100 visitors. Use aggregation API directly for larger datasets.")
    
    return "\n".join(output_lines)

# Main execution
if __name__ == "__main__":
    # Verify API key is configured
    logger.info(f"Starting Pendo MCP Server")
    logger.info(f"Using Pendo API base URL: {PENDO_API_BASE}")
    
    # Run the server
    mcp.run(transport='stdio')
