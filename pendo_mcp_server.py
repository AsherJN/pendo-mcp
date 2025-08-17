#!/usr/bin/env python3
"""
Pendo MCP Server - Model Context Protocol server for Pendo API integration
Expanded to 15 comprehensive tools for powerful analytics
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

def format_timestamp(timestamp: int) -> str:
    """Convert timestamp to readable date string."""
    if timestamp:
        return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return 'Unknown'

def format_date(timestamp: int) -> str:
    """Convert timestamp to readable date only."""
    if timestamp:
        return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
    return 'Unknown'

# =====================================
# PRODUCT DISCOVERY TOOLS (3 tools)
# =====================================

@mcp.tool()
async def search_pages(
    page_id: Optional[str] = None,
    name_contains: Optional[str] = None,
    app_id: Optional[str] = None,
    include_metrics: bool = False,
    limit: int = 100
) -> str:
    """
    Search and analyze page usage. Consolidates list and details functionality.
    
    Args:
        page_id: Optional specific page ID to retrieve
        name_contains: Optional text to search in page names
        app_id: Optional application ID for multi-app subscriptions
        include_metrics: Include usage metrics (default: False)
        limit: Maximum number of results (default: 100, max: 1000)
    """
    
    if limit < 1 or limit > 1000:
        return "Limit must be between 1 and 1000."
    
    # Get pages from API
    endpoint = "/api/v1/page"
    params = {}
    
    if page_id:
        params['id'] = page_id
    if app_id:
        params['appId'] = app_id
    
    data = await make_pendo_request(endpoint, params=params)
    
    if not data:
        return "Unable to fetch pages from Pendo API."
    
    # Convert to list if single page returned
    pages = data if isinstance(data, list) else [data]
    
    # Filter by name if specified
    if name_contains:
        pages = [p for p in pages if name_contains.lower() in p.get('name', '').lower()]
    
    if not pages:
        return f"No pages found matching criteria."
    
    # Limit results
    pages = pages[:limit]
    
    # If metrics requested, get usage data
    metrics_by_page = {}
    if include_metrics:
        page_ids = [p.get('id') for p in pages[:10]]  # Limit metrics to first 10 pages
        
        aggregation_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "name": "Page Usage Metrics",
                "pipeline": [
                    {
                        "source": {
                            "pageEvents": None,
                            "timeSeries": {
                                "period": "dayRange",
                                "first": "now()",
                                "count": -30
                            }
                        }
                    },
                    {
                        "filter": f'pageId in {page_ids}'
                    },
                    {
                        "group": {
                            "group": ["pageId"],
                            "fields": {
                                "views": {"sum": "numEvents"},
                                "uniqueVisitors": {"count": "visitorId"}
                            }
                        }
                    }
                ]
            }
        }
        
        metrics_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
        if metrics_data and metrics_data.get('results'):
            for result in metrics_data.get('results', []):
                metrics_by_page[result.get('pageId')] = {
                    'views': result.get('views', 0),
                    'visitors': result.get('uniqueVisitors', 0)
                }
    
    # Format output
    output_lines = [f"Page Search Results - Found {len(pages)} page(s)"]
    if name_contains:
        output_lines.append(f"Filter: Name contains '{name_contains}'")
    output_lines.append("=" * 50)
    
    for page in pages:
        page_id = page.get('id', 'Unknown')
        page_name = page.get('name', 'Unnamed Page')
        app_id = page.get('appId', 'Unknown')
        created = format_date(page.get('createdAt', 0))
        
        output_lines.append(f"\nPage: {page_name}")
        output_lines.append(f"  ID: {page_id}")
        output_lines.append(f"  App ID: {app_id}")
        output_lines.append(f"  Created: {created}")
        
        if include_metrics and page_id in metrics_by_page:
            metrics = metrics_by_page[page_id]
            output_lines.append(f"  Last 30 Days:")
            output_lines.append(f"    Views: {metrics['views']:,}")
            output_lines.append(f"    Unique Visitors: {metrics['visitors']:,}")
    
    return "\n".join(output_lines)

@mcp.tool()
async def search_features(
    feature_id: Optional[str] = None,
    name_contains: Optional[str] = None,
    color: Optional[str] = None,
    app_id: Optional[str] = None,
    include_metrics: bool = False,
    limit: int = 100
) -> str:
    """
    Search and analyze feature usage. Consolidates list and details functionality.
    
    Args:
        feature_id: Optional specific feature ID to retrieve
        name_contains: Optional text to search in feature names
        color: Optional color filter
        app_id: Optional application ID
        include_metrics: Include click metrics (default: False)
        limit: Maximum number of results (default: 100, max: 1000)
    """
    
    if limit < 1 or limit > 1000:
        return "Limit must be between 1 and 1000."
    
    # Get features from API
    endpoint = "/api/v1/feature"
    params = {}
    
    if feature_id:
        params['id'] = feature_id
    if app_id:
        params['appId'] = app_id
    
    data = await make_pendo_request(endpoint, params=params)
    
    if not data:
        return "Unable to fetch features from Pendo API."
    
    # Convert to list if single feature returned
    features = data if isinstance(data, list) else [data]
    
    # Filter by name and color if specified
    if name_contains:
        features = [f for f in features if name_contains.lower() in f.get('name', '').lower()]
    if color:
        features = [f for f in features if f.get('color', '').lower() == color.lower()]
    
    if not features:
        return f"No features found matching criteria."
    
    # Limit results
    features = features[:limit]
    
    # If metrics requested, get usage data
    metrics_by_feature = {}
    if include_metrics:
        feature_ids = [f.get('id') for f in features[:10]]  # Limit metrics to first 10
        
        aggregation_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "name": "Feature Click Metrics",
                "pipeline": [
                    {
                        "source": {
                            "featureEvents": None,
                            "timeSeries": {
                                "period": "dayRange",
                                "first": "now()",
                                "count": -30
                            }
                        }
                    },
                    {
                        "filter": f'featureId in {feature_ids}'
                    },
                    {
                        "group": {
                            "group": ["featureId"],
                            "fields": {
                                "clicks": {"sum": "numEvents"},
                                "uniqueUsers": {"count": "visitorId"}
                            }
                        }
                    }
                ]
            }
        }
        
        metrics_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
        if metrics_data and metrics_data.get('results'):
            for result in metrics_data.get('results', []):
                metrics_by_feature[result.get('featureId')] = {
                    'clicks': result.get('clicks', 0),
                    'users': result.get('uniqueUsers', 0)
                }
    
    # Format output
    output_lines = [f"Feature Search Results - Found {len(features)} feature(s)"]
    if name_contains:
        output_lines.append(f"Filter: Name contains '{name_contains}'")
    if color:
        output_lines.append(f"Filter: Color = '{color}'")
    output_lines.append("=" * 50)
    
    for feature in features:
        feature_id = feature.get('id', 'Unknown')
        feature_name = feature.get('name', 'Unnamed Feature')
        feature_color = feature.get('color', 'None')
        created = format_date(feature.get('createdAt', 0))
        
        output_lines.append(f"\nFeature: {feature_name}")
        output_lines.append(f"  ID: {feature_id}")
        output_lines.append(f"  Color: {feature_color}")
        output_lines.append(f"  Created: {created}")
        
        if include_metrics and feature_id in metrics_by_feature:
            metrics = metrics_by_feature[feature_id]
            output_lines.append(f"  Last 30 Days:")
            output_lines.append(f"    Clicks: {metrics['clicks']:,}")
            output_lines.append(f"    Unique Users: {metrics['users']:,}")
    
    return "\n".join(output_lines)

@mcp.tool()
async def search_track_events(
    event_name: Optional[str] = None,
    visitor_id: Optional[str] = None,
    account_id: Optional[str] = None,
    days_back: int = 7,
    limit: int = 100
) -> str:
    """
    Search and analyze custom track events.
    
    Args:
        event_name: Optional track event name to filter
        visitor_id: Optional visitor ID filter
        account_id: Optional account ID filter
        days_back: Number of days to search (default: 7, max: 90)
        limit: Maximum number of results (default: 100, max: 1000)
    """
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if limit < 1 or limit > 1000:
        return "Limit must be between 1 and 1000."
    
    # Get track type ID if event_name provided
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
                return f"Track event '{event_name}' not found."
    
    # Build aggregation query
    pipeline = [
        {
            "source": {
                "trackEvents": {"trackTypeId": track_type_id} if track_type_id else {},
                "timeSeries": {
                    "period": "dayRange",
                    "first": "now()",
                    "count": -days_back
                }
            }
        }
    ]
    
    # Add filters
    filters = []
    if visitor_id:
        filters.append(f'visitorId == "{visitor_id}"')
    if account_id:
        filters.append(f'accountId == "{account_id}"')
    
    if filters:
        pipeline.append({"filter": " && ".join(filters)})
    
    # Group and sort
    pipeline.extend([
        {
            "group": {
                "group": ["visitorId", "accountId", "trackTypeId", "day"],
                "fields": {"eventCount": {"sum": "numEvents"}}
            }
        },
        {"sort": ["-day", "-eventCount"]},
        {"limit": limit}
    ])
    
    aggregation_query = {
        "response": {"mimeType": "application/json"},
        "request": {"name": "Track Events Search", "pipeline": pipeline}
    }
    
    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
    
    if not data or not data.get('results'):
        return f"No track events found matching criteria in the last {days_back} days."
    
    results = data.get('results', [])
    
    # Format output
    output_lines = [f"Track Events - Last {days_back} days"]
    if event_name:
        output_lines.append(f"Event: {event_name}")
    if visitor_id:
        output_lines.append(f"Visitor: {visitor_id}")
    if account_id:
        output_lines.append(f"Account: {account_id}")
    output_lines.append(f"Results: {len(results)} (limited to {limit})")
    output_lines.append("=" * 50)
    
    total_events = sum(r.get('eventCount', 0) for r in results)
    unique_visitors = len(set(r.get('visitorId') for r in results))
    
    for row in results[:20]:  # Show first 20
        date = format_date(row.get('day', 0))
        visitor = row.get('visitorId', 'Unknown')
        account = row.get('accountId', 'None')
        count = row.get('eventCount', 0)
        
        output_lines.append(f"\n{date} - {visitor}")
        output_lines.append(f"  Account: {account}")
        output_lines.append(f"  Events: {count:,}")
    
    if len(results) > 20:
        output_lines.append(f"\n... and {len(results) - 20} more results")
    
    output_lines.append("\n" + "=" * 50)
    output_lines.append(f"Total Events: {total_events:,}")
    output_lines.append(f"Unique Visitors: {unique_visitors}")
    
    return "\n".join(output_lines)

# =====================================
# PEOPLE INSIGHTS TOOLS (5 tools)
# =====================================

@mcp.tool()
async def get_visitor_details(
    visitor_id: str,
    include_history: bool = False,
    include_events: bool = False
) -> str:
    """
    Get comprehensive details about a specific visitor.
    
    Args:
        visitor_id: The Pendo visitor ID
        include_history: Include recent activity history (default: False)
        include_events: Include recent event summary (default: False)
    """
    if not visitor_id:
        return "Visitor ID is required."
    
    # Get basic visitor details
    endpoint = f"/api/v1/visitor/{visitor_id}"
    data = await make_pendo_request(endpoint)
    
    if not data:
        return f"Unable to fetch visitor details for ID: {visitor_id}"
    
    # Format basic info
    metadata = data.get('metadata', {})
    auto_metadata = metadata.get('auto', {})
    custom_metadata = metadata.get('custom', {})
    
    output_lines = [f"Visitor Details: {visitor_id}"]
    output_lines.append("=" * 50)
    output_lines.append(f"Account ID: {auto_metadata.get('accountId', 'None')}")
    output_lines.append(f"First Visit: {format_timestamp(auto_metadata.get('firstvisit', 0))}")
    output_lines.append(f"Browser: {auto_metadata.get('lastbrowsername', 'Unknown')}")
    
    if custom_metadata:
        output_lines.append("\nCustom Fields:")
        for key, value in custom_metadata.items():
            output_lines.append(f"  {key}: {value}")
    
    # Include history if requested
    if include_history:
        # Get last 24 hours of history
        start_time = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        history_endpoint = f"/api/v1/visitor/{visitor_id}/history"
        history_data = await make_pendo_request(history_endpoint, params={'starttime': start_time})
        
        if history_data and isinstance(history_data, list):
            output_lines.append(f"\nLast 24 Hours Activity: {len(history_data)} events")
            for event in history_data[:10]:  # Show first 10
                event_type = event.get('type', 'Unknown')
                event_time = format_timestamp(event.get('ts', 0))
                output_lines.append(f"  {event_time} - {event_type}")
    
    # Include event summary if requested
    if include_events:
        aggregation_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "name": "Visitor Event Summary",
                "pipeline": [
                    {
                        "source": {
                            "events": None,
                            "timeSeries": {
                                "period": "dayRange",
                                "first": "now()",
                                "count": -7
                            }
                        }
                    },
                    {"filter": f'visitorId == "{visitor_id}"'},
                    {
                        "reduce": {
                            "totalEvents": {"sum": "numEvents"},
                            "totalMinutes": {"sum": "numMinutes"}
                        }
                    }
                ]
            }
        }
        
        event_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
        if event_data and event_data.get('results'):
            result = event_data['results'][0] if event_data['results'] else {}
            total_events = result.get('totalEvents', 0)
            total_minutes = result.get('totalMinutes', 0)
            
            output_lines.append(f"\nLast 7 Days Summary:")
            output_lines.append(f"  Total Events: {total_events:,}")
            output_lines.append(f"  Time Spent: {total_minutes:.1f} minutes")
    
    return "\n".join(output_lines)

@mcp.tool()
async def search_visitors(
    account_id: Optional[str] = None,
    segment_id: Optional[str] = None,
    metadata_filter: Optional[str] = None,
    active_since: Optional[int] = None,
    limit: int = 100
) -> str:
    """
    Search visitors by various criteria.
    
    Args:
        account_id: Filter by account ID
        segment_id: Filter by segment ID
        metadata_filter: Custom metadata filter (e.g., "custom.role == 'admin'")
        active_since: Only visitors active in last N days
        limit: Maximum results (default: 100, max: 1000)
    """
    
    if limit < 1 or limit > 1000:
        return "Limit must be between 1 and 1000."
    
    # Build aggregation pipeline
    pipeline = [{"source": {"visitors": None}}]
    
    # Add filters
    filters = []
    if account_id:
        filters.append(f'metadata.auto.accountId == "{account_id}" || contains(metadata.auto.accountIds, "{account_id}")')
    
    if metadata_filter:
        filters.append(f'metadata.{metadata_filter}')
    
    if active_since:
        days_ago_ms = int((datetime.now() - timedelta(days=active_since)).timestamp() * 1000)
        filters.append(f'metadata.auto.lastvisit >= {days_ago_ms}')
    
    if filters:
        pipeline.append({"filter": " && ".join(filters)})
    
    # Add segment filter if provided
    if segment_id:
        pipeline.append({"segment": {"id": segment_id}})
    
    # Select and limit
    pipeline.extend([
        {
            "select": {
                "visitorId": "id",
                "accountId": "metadata.auto.accountId",
                "firstVisit": "metadata.auto.firstvisit",
                "lastVisit": "metadata.auto.lastvisit",
                "browser": "metadata.auto.lastbrowsername"
            }
        },
        {"sort": ["-lastVisit"]},
        {"limit": limit}
    ])
    
    aggregation_query = {
        "response": {"mimeType": "application/json"},
        "request": {"name": "Visitor Search", "pipeline": pipeline}
    }
    
    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
    
    if not data or not data.get('results'):
        return "No visitors found matching criteria."
    
    results = data.get('results', [])
    
    # Format output
    output_lines = [f"Visitor Search Results - Found {len(results)} visitor(s)"]
    if account_id:
        output_lines.append(f"Account: {account_id}")
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    if active_since:
        output_lines.append(f"Active in last {active_since} days")
    output_lines.append("=" * 50)
    
    for idx, visitor in enumerate(results[:20], 1):
        visitor_id = visitor.get('visitorId', 'Unknown')
        account = visitor.get('accountId', 'None')
        last_visit = format_date(visitor.get('lastVisit', 0))
        browser = visitor.get('browser', 'Unknown')
        
        output_lines.append(f"\n{idx}. {visitor_id}")
        output_lines.append(f"   Account: {account}")
        output_lines.append(f"   Last Visit: {last_visit}")
        output_lines.append(f"   Browser: {browser}")
    
    if len(results) > 20:
        output_lines.append(f"\n... and {len(results) - 20} more visitors")
    
    return "\n".join(output_lines)

@mcp.tool()
async def get_account_details(
    account_id: str,
    include_visitors: bool = False,
    include_metrics: bool = False
) -> str:
    """
    Get comprehensive details about a specific account.
    
    Args:
        account_id: The Pendo account ID
        include_visitors: Include list of visitors (default: False)
        include_metrics: Include activity metrics (default: False)
    """
    if not account_id:
        return "Account ID is required."
    
    # Get basic account details
    endpoint = f"/api/v1/account/{account_id}"
    data = await make_pendo_request(endpoint)
    
    if not data:
        return f"Unable to fetch account details for ID: {account_id}"
    
    # Format basic info
    metadata = data.get('metadata', {})
    auto_metadata = metadata.get('auto', {})
    custom_metadata = metadata.get('custom', {})
    
    output_lines = [f"Account Details: {account_id}"]
    output_lines.append("=" * 50)
    output_lines.append(f"First Visit: {format_timestamp(auto_metadata.get('firstvisit', 0))}")
    output_lines.append(f"Last Visit: {format_timestamp(auto_metadata.get('lastvisit', 0))}")
    output_lines.append(f"Last Updated: {format_timestamp(auto_metadata.get('lastupdated', 0))}")
    
    if custom_metadata:
        output_lines.append("\nCustom Fields:")
        for key, value in custom_metadata.items():
            output_lines.append(f"  {key}: {value}")
    
    # Get visitor count
    visitor_count_query = {
        "response": {"mimeType": "application/json"},
        "request": {
            "name": "Account Visitor Count",
            "pipeline": [
                {"source": {"visitors": None}},
                {"filter": f'metadata.auto.accountId == "{account_id}"'},
                {"count": None}
            ]
        }
    }
    
    count_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=visitor_count_query)
    if count_data and count_data.get('results'):
        visitor_count = count_data['results'][0].get('count', 0) if count_data['results'] else 0
        output_lines.append(f"\nTotal Visitors: {visitor_count:,}")
    
    # Include visitor list if requested
    if include_visitors:
        visitors_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "name": "Account Visitors",
                "pipeline": [
                    {"source": {"visitors": None}},
                    {"filter": f'metadata.auto.accountId == "{account_id}"'},
                    {"select": {"visitorId": "id", "firstVisit": "metadata.auto.firstvisit"}},
                    {"sort": ["-firstVisit"]},
                    {"limit": 10}
                ]
            }
        }
        
        visitors_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=visitors_query)
        if visitors_data and visitors_data.get('results'):
            output_lines.append("\nRecent Visitors:")
            for visitor in visitors_data['results']:
                visitor_id = visitor.get('visitorId', 'Unknown')
                first_visit = format_date(visitor.get('firstVisit', 0))
                output_lines.append(f"  {visitor_id} (joined {first_visit})")
    
    # Include metrics if requested
    if include_metrics:
        metrics_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "name": "Account Metrics",
                "pipeline": [
                    {
                        "source": {
                            "events": None,
                            "timeSeries": {
                                "period": "dayRange",
                                "first": "now()",
                                "count": -30
                            }
                        }
                    },
                    {"filter": f'accountId == "{account_id}"'},
                    {
                        "reduce": {
                            "totalEvents": {"sum": "numEvents"},
                            "uniqueVisitors": {"count": "visitorId"}
                        }
                    }
                ]
            }
        }
        
        metrics_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=metrics_query)
        if metrics_data and metrics_data.get('results'):
            result = metrics_data['results'][0] if metrics_data['results'] else {}
            total_events = result.get('totalEvents', 0)
            unique_visitors = result.get('uniqueVisitors', 0)
            
            output_lines.append(f"\nLast 30 Days Activity:")
            output_lines.append(f"  Total Events: {total_events:,}")
            output_lines.append(f"  Active Visitors: {unique_visitors:,}")
    
    return "\n".join(output_lines)

@mcp.tool()
async def search_accounts(
    metadata_filter: Optional[str] = None,
    segment_id: Optional[str] = None,
    min_visitors: Optional[int] = None,
    active_since: Optional[int] = None,
    limit: int = 100
) -> str:
    """
    Search accounts by various criteria.
    
    Args:
        metadata_filter: Custom metadata filter (e.g., "custom.industry == 'SaaS'")
        segment_id: Filter by segment ID
        min_visitors: Minimum number of visitors
        active_since: Only accounts active in last N days
        limit: Maximum results (default: 100, max: 1000)
    """
    
    if limit < 1 or limit > 1000:
        return "Limit must be between 1 and 1000."
    
    # Build aggregation pipeline
    pipeline = [{"source": {"accounts": None}}]
    
    # Add filters
    filters = []
    if metadata_filter:
        filters.append(f'metadata.{metadata_filter}')
    
    if active_since:
        days_ago_ms = int((datetime.now() - timedelta(days=active_since)).timestamp() * 1000)
        filters.append(f'metadata.auto.lastvisit >= {days_ago_ms}')
    
    if filters:
        pipeline.append({"filter": " && ".join(filters)})
    
    # Add segment filter if provided
    if segment_id:
        pipeline.append({"segment": {"id": segment_id}})
    
    # Select and sort
    pipeline.extend([
        {
            "select": {
                "accountId": "accountId",
                "firstVisit": "metadata.auto.firstvisit",
                "lastVisit": "metadata.auto.lastvisit"
            }
        },
        {"sort": ["-lastVisit"]},
        {"limit": limit * 2}  # Get extra to filter by visitor count if needed
    ])
    
    aggregation_query = {
        "response": {"mimeType": "application/json"},
        "request": {"name": "Account Search", "pipeline": pipeline}
    }
    
    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
    
    if not data or not data.get('results'):
        return "No accounts found matching criteria."
    
    results = data.get('results', [])
    
    # Filter by min_visitors if specified
    if min_visitors:
        filtered_results = []
        for account in results:
            account_id = account.get('accountId')
            # Get visitor count for this account
            count_query = {
                "response": {"mimeType": "application/json"},
                "request": {
                    "pipeline": [
                        {"source": {"visitors": None}},
                        {"filter": f'metadata.auto.accountId == "{account_id}"'},
                        {"count": None}
                    ]
                }
            }
            count_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=count_query)
            if count_data and count_data.get('results'):
                visitor_count = count_data['results'][0].get('count', 0) if count_data['results'] else 0
                if visitor_count >= min_visitors:
                    account['visitorCount'] = visitor_count
                    filtered_results.append(account)
                    if len(filtered_results) >= limit:
                        break
        results = filtered_results
    
    # Limit final results
    results = results[:limit]
    
    # Format output
    output_lines = [f"Account Search Results - Found {len(results)} account(s)"]
    if metadata_filter:
        output_lines.append(f"Filter: {metadata_filter}")
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    if min_visitors:
        output_lines.append(f"Min Visitors: {min_visitors}")
    if active_since:
        output_lines.append(f"Active in last {active_since} days")
    output_lines.append("=" * 50)
    
    for idx, account in enumerate(results[:20], 1):
        account_id = account.get('accountId', 'Unknown')
        last_visit = format_date(account.get('lastVisit', 0))
        visitor_count = account.get('visitorCount', 'N/A')
        
        output_lines.append(f"\n{idx}. {account_id}")
        output_lines.append(f"   Last Visit: {last_visit}")
        if visitor_count != 'N/A':
            output_lines.append(f"   Visitors: {visitor_count}")
    
    if len(results) > 20:
        output_lines.append(f"\n... and {len(results) - 20} more accounts")
    
    return "\n".join(output_lines)

@mcp.tool()
async def analyze_segments(
    action: str,
    segment_id: Optional[str] = None,
    visitor_id: Optional[str] = None,
    account_id: Optional[str] = None
) -> str:
    """
    Multi-purpose segment analysis tool.
    
    Args:
        action: Action to perform - 'list', 'details', 'check', or 'export'
        segment_id: Segment ID (required for details, check, export)
        visitor_id: Visitor ID (for check action)
        account_id: Account ID (for check action)
    """
    
    if action not in ['list', 'details', 'check', 'export']:
        return "Action must be 'list', 'details', 'check', or 'export'."
    
    if action == 'list':
        # List all shared segments
        endpoint = "/api/v1/segment"
        data = await make_pendo_request(endpoint)
        
        if not data:
            return "Unable to fetch segments from Pendo API."
        
        segments = data if isinstance(data, list) else [data]
        
        output_lines = [f"Available Segments - Found {len(segments)} segment(s)"]
        output_lines.append("=" * 50)
        
        for segment in segments:
            seg_id = segment.get('id', 'Unknown')
            seg_name = segment.get('name', 'Unnamed')
            created = format_date(segment.get('createdAt', 0))
            
            output_lines.append(f"\nSegment: {seg_name}")
            output_lines.append(f"  ID: {seg_id}")
            output_lines.append(f"  Created: {created}")
        
        return "\n".join(output_lines)
    
    elif action == 'details':
        if not segment_id:
            return "Segment ID is required for details action."
        
        endpoint = f"/api/v1/segment/{segment_id}"
        data = await make_pendo_request(endpoint)
        
        if not data:
            return f"Unable to fetch segment details for ID: {segment_id}"
        
        # Get visitor count in segment
        count_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "pipeline": [
                    {"source": {"visitors": None}},
                    {"segment": {"id": segment_id}},
                    {"count": None}
                ]
            }
        }
        
        count_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=count_query)
        visitor_count = 0
        if count_data and count_data.get('results'):
            visitor_count = count_data['results'][0].get('count', 0) if count_data['results'] else 0
        
        output_lines = [f"Segment Details: {data.get('name', 'Unnamed')}"]
        output_lines.append("=" * 50)
        output_lines.append(f"ID: {segment_id}")
        output_lines.append(f"Created: {format_timestamp(data.get('createdAt', 0))}")
        output_lines.append(f"Last Updated: {format_timestamp(data.get('lastUpdatedAt', 0))}")
        output_lines.append(f"Visitors in Segment: {visitor_count:,}")
        
        return "\n".join(output_lines)
    
    elif action == 'check':
        if not segment_id:
            return "Segment ID is required for check action."
        
        if not visitor_id and not account_id:
            return "Either visitor_id or account_id is required for check action."
        
        # Build filter based on what was provided
        if visitor_id and account_id:
            filter_expr = f'visitorId == "{visitor_id}" && accountId == "{account_id}"'
        elif visitor_id:
            filter_expr = f'visitorId == "{visitor_id}"'
        else:
            filter_expr = f'accountId == "{account_id}"'
        
        # Check membership
        check_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "pipeline": [
                    {"source": {"visitors": None}},
                    {"filter": filter_expr},
                    {"segment": {"id": segment_id}},
                    {"count": None}
                ]
            }
        }
        
        data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=check_query)
        
        if data and data.get('results'):
            count = data['results'][0].get('count', 0) if data['results'] else 0
            is_member = count > 0
            
            output_lines = [f"Segment Membership Check"]
            output_lines.append("=" * 50)
            output_lines.append(f"Segment ID: {segment_id}")
            if visitor_id:
                output_lines.append(f"Visitor ID: {visitor_id}")
            if account_id:
                output_lines.append(f"Account ID: {account_id}")
            output_lines.append(f"Is Member: {'Yes' if is_member else 'No'}")
            
            return "\n".join(output_lines)
        
        return "Unable to check segment membership."
    
    elif action == 'export':
        if not segment_id:
            return "Segment ID is required for export action."
        
        # Get first 100 visitors in segment
        export_query = {
            "response": {"mimeType": "application/json"},
            "request": {
                "pipeline": [
                    {"source": {"visitors": None}},
                    {"segment": {"id": segment_id}},
                    {
                        "select": {
                            "visitorId": "id",
                            "accountId": "metadata.auto.accountId",
                            "firstVisit": "metadata.auto.firstvisit"
                        }
                    },
                    {"limit": 100}
                ]
            }
        }
        
        data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=export_query)
        
        if not data or not data.get('results'):
            return f"No visitors found in segment {segment_id}"
        
        results = data.get('results', [])
        
        output_lines = [f"Segment Export - {len(results)} visitors (limited to 100)"]
        output_lines.append(f"Segment ID: {segment_id}")
        output_lines.append("=" * 50)
        
        for visitor in results[:20]:
            visitor_id = visitor.get('visitorId', 'Unknown')
            account_id = visitor.get('accountId', 'None')
            first_visit = format_date(visitor.get('firstVisit', 0))
            
            output_lines.append(f"{visitor_id} | {account_id} | {first_visit}")
        
        if len(results) > 20:
            output_lines.append(f"\n... and {len(results) - 20} more visitors")
            output_lines.append("\nNote: Use Pendo UI or API endpoint for full export")
        
        return "\n".join(output_lines)

# =====================================
# BEHAVIORAL ANALYTICS TOOLS (6 tools)
# =====================================

# Helper functions for fallback strategies
async def _try_feature_usage_fallback(days_back: int) -> Optional[str]:
    """Fallback strategy: Get feature usage summary"""
    try:
        # Get top 5 features
        features_data = await make_pendo_request("/api/v1/feature", params={'limit': 5})
        if features_data and isinstance(features_data, list) and len(features_data) > 0:
            feature_ids = [f.get('id') for f in features_data[:3] if f.get('id')]
            
            if feature_ids:
                # Try to get feature adoption data
                for feature_id in feature_ids:
                    pipeline = [
                        {
                            "source": {
                                "featureEvents": {"featureId": feature_id},
                                "timeSeries": {
                                    "period": "dayRange",
                                    "first": "now()",
                                    "count": -days_back
                                }
                            }
                        },
                        {
                            "reduce": {
                                "totalClicks": {"sum": "numEvents"},
                                "uniqueUsers": {"count": "visitorId"}
                            }
                        }
                    ]
                    
                    query = {
                        "response": {"mimeType": "application/json"},
                        "request": {"pipeline": pipeline}
                    }
                    
                    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=query)
                    if data and data.get('results'):
                        result = data['results'][0]
                        clicks = result.get('totalClicks', 0)
                        users = result.get('uniqueUsers', 0)
                        if clicks > 0 or users > 0:
                            feature_name = next((f.get('name', 'Unknown') for f in features_data if f.get('id') == feature_id), 'Unknown')
                            return f"Feature Activity Found - '{feature_name}': {clicks:,} clicks from {users:,} users"
                
                return "Features found but no recent activity detected"
    except Exception as e:
        logger.info(f"Feature fallback failed: {e}")
    return None

async def _try_visitor_activity_fallback(days_back: int) -> Optional[str]:
    """Fallback strategy: Basic visitor activity summary"""
    try:
        # Get recent visitors
        pipeline = [
            {"source": {"visitors": None}},
            {
                "filter": f'metadata.auto.lastvisit >= {int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)}'
            },
            {"limit": 10}
        ]
        
        query = {
            "response": {"mimeType": "application/json"},
            "request": {"pipeline": pipeline}
        }
        
        data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=query)
        if data and data.get('results'):
            visitor_count = len(data.get('results', []))
            return f"Recent Activity Found - {visitor_count} visitors active in last {days_back} days"
    except Exception as e:
        logger.info(f"Visitor activity fallback failed: {e}")
    return None

async def _try_page_activity_fallback(days_back: int) -> Optional[str]:
    """Fallback strategy: Page activity summary"""
    try:
        # Get pages with metrics
        pages_data = await make_pendo_request("/api/v1/page", params={'limit': 3})
        if pages_data and isinstance(pages_data, list) and len(pages_data) > 0:
            page_ids = [p.get('id') for p in pages_data[:2] if p.get('id')]
            
            if page_ids:
                for page_id in page_ids:
                    pipeline = [
                        {
                            "source": {
                                "pageEvents": {"pageId": page_id},
                                "timeSeries": {
                                    "period": "dayRange",
                                    "first": "now()",
                                    "count": -days_back
                                }
                            }
                        },
                        {
                            "reduce": {
                                "totalViews": {"sum": "numEvents"},
                                "uniqueUsers": {"count": "visitorId"}
                            }
                        }
                    ]
                    
                    query = {
                        "response": {"mimeType": "application/json"},
                        "request": {"pipeline": pipeline}
                    }
                    
                    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=query)
                    if data and data.get('results'):
                        result = data['results'][0]
                        views = result.get('totalViews', 0)
                        users = result.get('uniqueUsers', 0)
                        if views > 0 or users > 0:
                            page_name = next((p.get('name', 'Unknown') for p in pages_data if p.get('id') == page_id), 'Unknown')
                            return f"Page Activity Found - '{page_name}': {views:,} views from {users:,} visitors"
    except Exception as e:
        logger.info(f"Page activity fallback failed: {e}")
    return None

@mcp.tool()
async def analyze_usage(
    segment_id: Optional[str] = None,
    visitor_id: Optional[str] = None,
    account_id: Optional[str] = None,
    days_back: int = 30,
    group_by: str = "day",
    metric_type: str = "events"
) -> str:
    """
    Analyze activity patterns and usage metrics with automatic fallbacks.
    
    Args:
        segment_id: Optional segment filter
        visitor_id: Optional visitor filter
        account_id: Optional account filter
        days_back: Number of days to analyze (default: 30, max: 90)
        group_by: Group by 'day', 'week', or 'month' (default: 'day')
        metric_type: Type of metric - 'events', 'sessions', or 'time' (default: 'events')
    """
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if group_by not in ['day', 'week', 'month']:
        return "Group by must be 'day', 'week', or 'month'."
    
    if metric_type not in ['events', 'sessions', 'time']:
        return "Metric type must be 'events', 'sessions', or 'time'."
    
    # PRIMARY STRATEGY: Try original broad aggregation
    try:
        # Build aggregation query
        period_map = {'day': 'dayRange', 'week': 'weekRange', 'month': 'monthRange'}
        period = period_map[group_by]
        
        pipeline = [
            {
                "source": {
                    "events": None,
                    "timeSeries": {
                        "period": period,
                        "first": "now()",
                        "count": -days_back if group_by == 'day' else -4
                    }
                }
            }
        ]
        
        # Add filters
        filters = []
        if visitor_id:
            filters.append(f'visitorId == "{visitor_id}"')
        if account_id:
            filters.append(f'accountId == "{account_id}"')
        
        if filters:
            pipeline.append({"filter": " && ".join(filters)})
        
        # Add segment filter
        if segment_id:
            pipeline.append({"segment": {"id": segment_id}})
        
        # Group and aggregate
        group_field = group_by
        pipeline.append({
            "group": {
                "group": [group_field],
                "fields": {
                    "totalEvents": {"sum": "numEvents"},
                    "totalMinutes": {"sum": "numMinutes"},
                    "uniqueVisitors": {"count": "visitorId"},
                    "uniqueAccounts": {"count": "accountId"}
                }
            }
        })
        
        pipeline.append({"sort": [group_field]})
        
        aggregation_query = {
            "response": {"mimeType": "application/json"},
            "request": {"name": "Usage Analysis", "pipeline": pipeline}
        }
        
        data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
        
        # If primary strategy succeeds, return full results
        if data and data.get('results'):
            results = data.get('results', [])
            
            # Format output
            output_lines = [f"Usage Analysis - Last {days_back} days"]
            if segment_id:
                output_lines.append(f"Segment: {segment_id}")
            if visitor_id:
                output_lines.append(f"Visitor: {visitor_id}")
            if account_id:
                output_lines.append(f"Account: {account_id}")
            output_lines.append(f"Grouped by: {group_by}")
            output_lines.append(f"Metric focus: {metric_type}")
            output_lines.append("=" * 50)
            
            total_events = 0
            total_minutes = 0
            max_visitors = 0
            
            for row in results:
                period_timestamp = row.get(group_field, 0)
                if period_timestamp:
                    if group_by == 'day':
                        period_str = format_date(period_timestamp)
                    elif group_by == 'week':
                        period_str = f"Week of {format_date(period_timestamp)}"
                    else:
                        period_str = datetime.fromtimestamp(period_timestamp / 1000).strftime('%B %Y')
                else:
                    period_str = 'Unknown'
                
                events = row.get('totalEvents', 0)
                minutes = row.get('totalMinutes', 0)
                visitors = row.get('uniqueVisitors', 0)
                accounts = row.get('uniqueAccounts', 0)
                
                total_events += events
                total_minutes += minutes
                max_visitors = max(max_visitors, visitors)
                
                output_lines.append(f"\n{period_str}:")
                
                if metric_type == 'events':
                    output_lines.append(f"  Events: {events:,}")
                    output_lines.append(f"  Unique Visitors: {visitors:,}")
                elif metric_type == 'sessions':
                    avg_session = (minutes / visitors) if visitors > 0 else 0
                    output_lines.append(f"  Unique Visitors: {visitors:,}")
                    output_lines.append(f"  Avg Session: {avg_session:.1f} minutes")
                else:  # time
                    output_lines.append(f"  Total Time: {minutes:.1f} minutes")
                    output_lines.append(f"  Unique Visitors: {visitors:,}")
                
                if accounts > 0:
                    output_lines.append(f"  Unique Accounts: {accounts:,}")
            
            output_lines.append("\n" + "=" * 50)
            output_lines.append("Summary:")
            output_lines.append(f"Total Events: {total_events:,}")
            output_lines.append(f"Total Time: {total_minutes:.1f} minutes")
            output_lines.append(f"Peak Unique Visitors: {max_visitors:,}")
            
            return "\n".join(output_lines)
            
    except Exception as e:
        logger.info(f"Primary usage analysis failed: {e}")
    
    # FALLBACK STRATEGY 1: Try feature usage analysis
    feature_fallback = await _try_feature_usage_fallback(days_back)
    if feature_fallback:
        return f"""❓ Broad usage data unavailable.
🔄 **Fallback Analysis - Feature Usage:**

{feature_fallback}

💡 **Tip**: For detailed feature analysis, try: analyze_feature_adoption()"""
    
    # FALLBACK STRATEGY 2: Try page activity analysis  
    page_fallback = await _try_page_activity_fallback(days_back)
    if page_fallback:
        return f"""❓ Detailed usage metrics unavailable.
🔄 **Fallback Analysis - Page Activity:**

{page_fallback}

💡 **Tip**: For page-specific analysis, try: search_pages(include_metrics=True)"""
    
    # FALLBACK STRATEGY 3: Try basic visitor activity
    visitor_fallback = await _try_visitor_activity_fallback(days_back)
    if visitor_fallback:
        return f"""❓ Event-level usage data unavailable.
🔄 **Fallback Analysis - Visitor Activity:**

{visitor_fallback}

💡 **Tip**: For visitor details, try: search_visitors(active_since={days_back})"""
    
    # FINAL FALLBACK: Helpful suggestions
    return f"""❓ No usage data found for the specified criteria.

🔧 **Try these alternatives:**
• search_pages(include_metrics=True) - Page-level usage data
• search_features(include_metrics=True) - Feature engagement data  
• search_visitors(active_since={days_back}) - Recent visitor activity
• analyze_feature_adoption() - Specific feature performance

💡 **Platform Status**: This may indicate a new platform with limited tracking data.
   Consider checking if events are being properly instrumented."""

@mcp.tool()
async def analyze_feature_adoption(
    feature_ids: Optional[List[str]] = None,
    page_ids: Optional[List[str]] = None,
    segment_id: Optional[str] = None,
    days_back: int = 30,
    group_by: str = "total"
) -> str:
    """
    Analyze feature and page adoption rates.
    
    Args:
        feature_ids: List of feature IDs to analyze
        page_ids: List of page IDs to analyze
        segment_id: Optional segment filter
        days_back: Number of days to analyze (default: 30)
        group_by: Group by 'total', 'day', or 'week' (default: 'total')
    """
    
    if not feature_ids and not page_ids:
        return "At least one feature_id or page_id is required."
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if group_by not in ['total', 'day', 'week']:
        return "Group by must be 'total', 'day', or 'week'."
    
    # Get total visitor count for adoption calculation
    total_visitors_query = {
        "response": {"mimeType": "application/json"},
        "request": {
            "pipeline": [
                {"source": {"visitors": None}}
            ]
        }
    }
    
    if segment_id:
        total_visitors_query["request"]["pipeline"].append({"segment": {"id": segment_id}})
    
    total_visitors_query["request"]["pipeline"].append({"count": None})
    
    total_data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=total_visitors_query)
    total_visitors = 1  # Default to avoid division by zero
    if total_data and total_data.get('results'):
        total_visitors = total_data['results'][0].get('count', 1) if total_data['results'] else 1
    
    results_by_item = {}
    
    # Analyze features
    if feature_ids:
        for feature_id in feature_ids:
            period = "dayRange" if group_by == 'day' else "weekRange" if group_by == 'week' else "dayRange"
            
            pipeline = [
                {
                    "source": {
                        "featureEvents": {"featureId": feature_id},
                        "timeSeries": {
                            "period": period,
                            "first": "now()",
                            "count": -days_back if group_by == 'day' else -4
                        }
                    }
                }
            ]
            
            if segment_id:
                pipeline.append({"segment": {"id": segment_id}})
            
            if group_by == 'total':
                pipeline.append({
                    "reduce": {
                        "totalClicks": {"sum": "numEvents"},
                        "uniqueUsers": {"count": "visitorId"}
                    }
                })
            else:
                group_field = 'day' if group_by == 'day' else 'week'
                pipeline.append({
                    "group": {
                        "group": [group_field],
                        "fields": {
                            "clicks": {"sum": "numEvents"},
                            "users": {"count": "visitorId"}
                        }
                    }
                })
                pipeline.append({"sort": [group_field]})
            
            query = {
                "response": {"mimeType": "application/json"},
                "request": {"pipeline": pipeline}
            }
            
            data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=query)
            if data and data.get('results'):
                results_by_item[f"feature_{feature_id}"] = data['results']
    
    # Analyze pages
    if page_ids:
        for page_id in page_ids:
            period = "dayRange" if group_by == 'day' else "weekRange" if group_by == 'week' else "dayRange"
            
            pipeline = [
                {
                    "source": {
                        "pageEvents": {"pageId": page_id},
                        "timeSeries": {
                            "period": period,
                            "first": "now()",
                            "count": -days_back if group_by == 'day' else -4
                        }
                    }
                }
            ]
            
            if segment_id:
                pipeline.append({"segment": {"id": segment_id}})
            
            if group_by == 'total':
                pipeline.append({
                    "reduce": {
                        "totalViews": {"sum": "numEvents"},
                        "uniqueUsers": {"count": "visitorId"}
                    }
                })
            else:
                group_field = 'day' if group_by == 'day' else 'week'
                pipeline.append({
                    "group": {
                        "group": [group_field],
                        "fields": {
                            "views": {"sum": "numEvents"},
                            "users": {"count": "visitorId"}
                        }
                    }
                })
                pipeline.append({"sort": [group_field]})
            
            query = {
                "response": {"mimeType": "application/json"},
                "request": {"pipeline": pipeline}
            }
            
            data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=query)
            if data and data.get('results'):
                results_by_item[f"page_{page_id}"] = data['results']
    
    # Format output
    output_lines = [f"Feature Adoption Analysis - Last {days_back} days"]
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    output_lines.append(f"Total Visitors in Scope: {total_visitors:,}")
    output_lines.append(f"Grouping: {group_by}")
    output_lines.append("=" * 50)
    
    for item_key, results in results_by_item.items():
        item_type, item_id = item_key.split('_', 1)
        
        output_lines.append(f"\n{item_type.title()}: {item_id}")
        
        if group_by == 'total':
            if results:
                result = results[0]
                if item_type == 'feature':
                    clicks = result.get('totalClicks', 0)
                    users = result.get('uniqueUsers', 0)
                    adoption_rate = (users / total_visitors * 100) if total_visitors > 0 else 0
                    
                    output_lines.append(f"  Total Clicks: {clicks:,}")
                    output_lines.append(f"  Unique Users: {users:,}")
                    output_lines.append(f"  Adoption Rate: {adoption_rate:.1f}%")
                else:  # page
                    views = result.get('totalViews', 0)
                    users = result.get('uniqueUsers', 0)
                    adoption_rate = (users / total_visitors * 100) if total_visitors > 0 else 0
                    
                    output_lines.append(f"  Total Views: {views:,}")
                    output_lines.append(f"  Unique Visitors: {users:,}")
                    output_lines.append(f"  Adoption Rate: {adoption_rate:.1f}%")
        else:
            for row in results[:10]:  # Limit to 10 periods
                period_field = 'day' if group_by == 'day' else 'week'
                period_timestamp = row.get(period_field, 0)
                
                if period_timestamp:
                    if group_by == 'day':
                        period_str = format_date(period_timestamp)
                    else:
                        period_str = f"Week of {format_date(period_timestamp)}"
                else:
                    period_str = 'Unknown'
                
                if item_type == 'feature':
                    clicks = row.get('clicks', 0)
                    users = row.get('users', 0)
                    output_lines.append(f"  {period_str}: {users} users, {clicks} clicks")
                else:
                    views = row.get('views', 0)
                    users = row.get('users', 0)
                    output_lines.append(f"  {period_str}: {users} visitors, {views} views")
    
    return "\n".join(output_lines)

@mcp.tool()
async def analyze_retention(
    segment_id: Optional[str] = None,
    cohort_date: Optional[str] = None,
    period_type: str = "weekly",
    group_by: str = "visitor"
) -> str:
    """
    Analyze user retention and stickiness.
    
    Args:
        segment_id: Optional segment filter
        cohort_date: Start date for cohort (YYYY-MM-DD format)
        period_type: Period type - 'daily', 'weekly', or 'monthly' (default: 'weekly')
        group_by: Group by 'visitor' or 'account' (default: 'visitor')
    """
    
    if period_type not in ['daily', 'weekly', 'monthly']:
        return "Period type must be 'daily', 'weekly', or 'monthly'."
    
    if group_by not in ['visitor', 'account']:
        return "Group by must be 'visitor' or 'account'."
    
    # Use stickiness operator for retention analysis
    first_day = f'date("{cohort_date}")' if cohort_date else "dateAdd(now(), -30, \"days\")"
    
    config = {
        "userBase": "visitors" if group_by == "visitor" else "accounts",
        "numerator": "daily" if period_type == "daily" else "weekly",
        "denominator": "weekly" if period_type == "daily" else "monthly"
    }
    
    pipeline = [
        {
            "stickiness": {
                "appId": None,
                "firstDay": first_day,
                "dayCount": 30 if period_type == "daily" else 12 if period_type == "weekly" else 3,
                "config": config
            }
        }
    ]
    
    if segment_id:
        pipeline[0]["stickiness"]["segment"] = {"id": segment_id}
    
    aggregation_query = {
        "response": {"mimeType": "application/json"},
        "request": {"name": "Retention Analysis", "pipeline": pipeline}
    }
    
    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
    
    if not data or not data.get('results'):
        return "Unable to calculate retention metrics."
    
    results = data.get('results', [])
    
    # Format output
    output_lines = [f"Retention Analysis"]
    if cohort_date:
        output_lines.append(f"Cohort Start: {cohort_date}")
    else:
        output_lines.append(f"Analysis Period: Last 30 days")
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    output_lines.append(f"Period Type: {period_type}")
    output_lines.append(f"Grouped by: {group_by}")
    output_lines.append("=" * 50)
    
    if results:
        result = results[0]
        
        # Extract stickiness score
        stickiness_score = result.get('stickiness', 0)
        output_lines.append(f"\nStickiness Score: {stickiness_score:.2%}")
        
        # Additional metrics if available
        if 'details' in result:
            details = result.get('details', {})
            active_users = details.get('activeUsers', 0)
            total_users = details.get('totalUsers', 0)
            
            output_lines.append(f"Active {group_by.title()}s: {active_users:,}")
            output_lines.append(f"Total {group_by.title()}s: {total_users:,}")
            
            if total_users > 0:
                retention_rate = (active_users / total_users) * 100
                output_lines.append(f"Retention Rate: {retention_rate:.1f}%")
        
        output_lines.append("\nInterpretation:")
        if stickiness_score > 0.5:
            output_lines.append("High stickiness - users are regularly engaged")
        elif stickiness_score > 0.2:
            output_lines.append("Moderate stickiness - room for improvement in engagement")
        else:
            output_lines.append("Low stickiness - consider engagement strategies")
    
    return "\n".join(output_lines)

@mcp.tool()
async def analyze_funnels(
    steps: List[str],
    segment_id: Optional[str] = None,
    days_back: int = 30,
    group_by: str = "total"
) -> str:
    """
    Analyze conversion funnels through multiple steps.
    
    Args:
        steps: List of page/feature IDs representing funnel steps
        segment_id: Optional segment filter
        days_back: Number of days to analyze (default: 30)
        group_by: Group by 'total' or 'day' (default: 'total')
    """
    
    if not steps or len(steps) < 2:
        return "At least 2 steps are required for funnel analysis."
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if group_by not in ['total', 'day']:
        return "Group by must be 'total' or 'day'."
    
    # For simplicity, we'll track visitors who complete each step
    visitors_by_step = []
    
    for step_id in steps:
        # Determine if it's a page or feature
        # Try page first
        pipeline = [
            {
                "source": {
                    "pageEvents": {"pageId": step_id},
                    "timeSeries": {
                        "period": "dayRange",
                        "first": "now()",
                        "count": -days_back
                    }
                }
            }
        ]
        
        if segment_id:
            pipeline.append({"segment": {"id": segment_id}})
        
        pipeline.append({
            "group": {
                "group": ["visitorId"],
                "fields": {"events": {"sum": "numEvents"}}
            }
        })
        
        query = {
            "response": {"mimeType": "application/json"},
            "request": {"pipeline": pipeline}
        }
        
        data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=query)
        
        if data and data.get('results'):
            visitor_set = set(r.get('visitorId') for r in data['results'])
            visitors_by_step.append(visitor_set)
        else:
            # Try as feature
            pipeline[0]["source"] = {
                "featureEvents": {"featureId": step_id},
                "timeSeries": {
                    "period": "dayRange",
                    "first": "now()",
                    "count": -days_back
                }
            }
            
            query["request"]["pipeline"] = pipeline
            data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=query)
            
            if data and data.get('results'):
                visitor_set = set(r.get('visitorId') for r in data['results'])
                visitors_by_step.append(visitor_set)
            else:
                visitors_by_step.append(set())
    
    # Calculate funnel metrics
    output_lines = [f"Funnel Analysis - Last {days_back} days"]
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    output_lines.append(f"Steps: {len(steps)}")
    output_lines.append("=" * 50)
    
    # Calculate conversion rates
    for i, step_id in enumerate(steps):
        step_visitors = len(visitors_by_step[i]) if i < len(visitors_by_step) else 0
        
        if i == 0:
            output_lines.append(f"\nStep {i+1}: {step_id}")
            output_lines.append(f"  Visitors: {step_visitors:,}")
            output_lines.append(f"  Entry Rate: 100.0%")
        else:
            prev_visitors = len(visitors_by_step[i-1]) if visitors_by_step[i-1] else 1
            # Get visitors who completed both steps
            if i < len(visitors_by_step):
                completed_both = visitors_by_step[i-1].intersection(visitors_by_step[i])
                conversion_rate = (len(completed_both) / prev_visitors * 100) if prev_visitors > 0 else 0
            else:
                conversion_rate = 0
            
            output_lines.append(f"\nStep {i+1}: {step_id}")
            output_lines.append(f"  Visitors: {step_visitors:,}")
            output_lines.append(f"  Conversion from Step {i}: {conversion_rate:.1f}%")
            
            if i == len(steps) - 1:
                # Overall conversion
                first_step_visitors = len(visitors_by_step[0]) if visitors_by_step[0] else 1
                overall_conversion = (step_visitors / first_step_visitors * 100) if first_step_visitors > 0 else 0
                output_lines.append(f"  Overall Conversion: {overall_conversion:.1f}%")
    
    return "\n".join(output_lines)

@mcp.tool()
async def analyze_user_paths(
    start_page: Optional[str] = None,
    end_page: Optional[str] = None,
    segment_id: Optional[str] = None,
    max_steps: int = 5,
    days_back: int = 7
) -> str:
    """
    Analyze common user navigation paths.
    
    Args:
        start_page: Optional starting page ID
        end_page: Optional ending page ID
        segment_id: Optional segment filter
        max_steps: Maximum path length (default: 5)
        days_back: Number of days to analyze (default: 7)
    """
    
    if days_back < 1 or days_back > 30:
        return "Days back must be between 1 and 30."
    
    if max_steps < 2 or max_steps > 10:
        return "Max steps must be between 2 and 10."
    
    # Build aggregation for path analysis
    pipeline = [
        {
            "source": {
                "pageEvents": None,
                "timeSeries": {
                    "period": "dayRange",
                    "first": "now()",
                    "count": -days_back
                }
            }
        }
    ]
    
    # Add filters
    filters = []
    if start_page:
        filters.append(f'pageId == "{start_page}"')
    if end_page:
        # This would need more complex logic to track paths
        pass
    
    if filters:
        pipeline.append({"filter": " || ".join(filters)})
    
    if segment_id:
        pipeline.append({"segment": {"id": segment_id}})
    
    # Group by visitor and page sequence
    pipeline.extend([
        {
            "group": {
                "group": ["visitorId", "pageId", "day"],
                "fields": {"views": {"sum": "numEvents"}}
            }
        },
        {"sort": ["visitorId", "day"]},
        {"limit": 1000}
    ])
    
    aggregation_query = {
        "response": {"mimeType": "application/json"},
        "request": {"name": "Path Analysis", "pipeline": pipeline}
    }
    
    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
    
    if not data or not data.get('results'):
        return "No path data found for the specified criteria."
    
    results = data.get('results', [])
    
    # Analyze paths (simplified - would need more complex processing for real paths)
    paths_count = {}
    current_visitor = None
    current_path = []
    
    for row in results:
        visitor = row.get('visitorId')
        page = row.get('pageId')
        
        if visitor != current_visitor:
            if current_path and len(current_path) <= max_steps:
                path_str = " → ".join(current_path)
                paths_count[path_str] = paths_count.get(path_str, 0) + 1
            current_visitor = visitor
            current_path = [page]
        else:
            if len(current_path) < max_steps:
                current_path.append(page)
    
    # Add last path
    if current_path and len(current_path) <= max_steps:
        path_str = " → ".join(current_path)
        paths_count[path_str] = paths_count.get(path_str, 0) + 1
    
    # Format output
    output_lines = [f"User Path Analysis - Last {days_back} days"]
    if start_page:
        output_lines.append(f"Starting Page: {start_page}")
    if end_page:
        output_lines.append(f"Ending Page: {end_page}")
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    output_lines.append(f"Max Path Length: {max_steps}")
    output_lines.append("=" * 50)
    
    if paths_count:
        # Sort by frequency
        sorted_paths = sorted(paths_count.items(), key=lambda x: x[1], reverse=True)
        
        output_lines.append("\nTop Navigation Paths:")
        for i, (path, count) in enumerate(sorted_paths[:10], 1):
            output_lines.append(f"\n{i}. {path}")
            output_lines.append(f"   Occurrences: {count}")
    else:
        output_lines.append("\nNo paths found matching criteria.")
    
    return "\n".join(output_lines)

@mcp.tool()
async def calculate_product_engagement(
    segment_id: Optional[str] = None,
    features_list: Optional[List[str]] = None,
    days_back: int = 30,
    group_by: str = "total"
) -> str:
    """
    Calculate Product Engagement Score (PES) metrics.
    
    Args:
        segment_id: Optional segment filter
        features_list: Optional list of feature IDs to include
        days_back: Number of days to analyze (default: 30)
        group_by: Group by 'total' or 'account' (default: 'total')
    """
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if group_by not in ['total', 'account']:
        return "Group by must be 'total' or 'account'."
    
    # Build PES query
    config = {
        "stickiness": {
            "userBase": "visitors",
            "numerator": "daily",
            "denominator": "monthly"
        },
        "adoption": {
            "userBase": "visitors"
        },
        "growth": {
            "userBase": "visitors"
        }
    }
    
    # Add features to adoption config if provided
    if features_list:
        config["adoption"]["events"] = [
            {"kind": "feature", "id": fid} for fid in features_list
        ]
    
    pes_query = {
        "appId": None,
        "firstDay": "dateAdd(now(), -30, \"days\")",
        "lastDay": "now()",
        "config": config
    }
    
    if segment_id:
        pes_query["segment"] = {"id": segment_id}
    
    if group_by == "account":
        pes_query["groupBy"] = "account"
    
    aggregation_query = {
        "response": {"mimeType": "application/json"},
        "request": {
            "name": "PES Calculation",
            "pipeline": [{"pes": pes_query}]
        }
    }
    
    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
    
    if not data or not data.get('results'):
        return "Unable to calculate PES metrics."
    
    results = data.get('results', [])
    
    # Format output
    output_lines = [f"Product Engagement Score (PES) - Last {days_back} days"]
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    if features_list:
        output_lines.append(f"Features Tracked: {len(features_list)}")
    output_lines.append(f"Grouped by: {group_by}")
    output_lines.append("=" * 50)
    
    if results:
        for result in results[:10]:  # Limit to 10 if grouped by account
            if group_by == "account":
                account_id = result.get('accountId', 'Unknown')
                output_lines.append(f"\nAccount: {account_id}")
            else:
                output_lines.append("\nOverall Metrics:")
            
            # Extract scores
            pes_score = result.get('pes', 0)
            stickiness = result.get('stickiness', 0)
            adoption = result.get('adoption', 0)
            growth = result.get('growth', 0)
            
            output_lines.append(f"  PES Score: {pes_score:.2f}")
            output_lines.append(f"  Components:")
            output_lines.append(f"    Stickiness: {stickiness:.2%}")
            output_lines.append(f"    Adoption: {adoption:.2%}")
            output_lines.append(f"    Growth: {growth:.2%}")
            
            # Interpretation
            if pes_score > 70:
                interpretation = "Excellent engagement"
            elif pes_score > 50:
                interpretation = "Good engagement"
            elif pes_score > 30:
                interpretation = "Moderate engagement"
            else:
                interpretation = "Low engagement - needs attention"
            
            output_lines.append(f"  Interpretation: {interpretation}")
    
    return "\n".join(output_lines)

# =====================================
# FEEDBACK TOOL (1 tool)
# =====================================

@mcp.tool()
async def analyze_nps_feedback(
    segment_id: Optional[str] = None,
    poll_id: Optional[str] = None,
    days_back: int = 30,
    group_by: str = "total"
) -> str:
    """
    Analyze NPS scores and feedback sentiment.
    
    Args:
        segment_id: Optional segment filter
        poll_id: Optional specific poll ID
        days_back: Number of days to analyze (default: 30)
        group_by: Group by 'total', 'day', or 'account' (default: 'total')
    """
    
    if days_back < 1 or days_back > 90:
        return "Days back must be between 1 and 90."
    
    if group_by not in ['total', 'day', 'account']:
        return "Group by must be 'total', 'day', or 'account'."
    
    # Build aggregation for NPS analysis
    pipeline = [
        {
            "source": {
                "pollsSeen": {"pollId": poll_id} if poll_id else {},
                "timeSeries": {
                    "period": "dayRange",
                    "first": "now()",
                    "count": -days_back
                }
            }
        }
    ]
    
    if segment_id:
        pipeline.append({"segment": {"id": segment_id}})
    
    # Calculate NPS categories
    pipeline.append({
        "eval": {
            "isPromoter": "if(pollResponse >= 9, 1, 0)",
            "isDetractor": "if(pollResponse < 7, 1, 0)",
            "isPassive": "if(pollResponse >= 7 && pollResponse < 9, 1, 0)"
        }
    })
    
    # Group based on parameter
    if group_by == 'total':
        pipeline.append({
            "reduce": {
                "promoters": {"sum": "isPromoter"},
                "detractors": {"sum": "isDetractor"},
                "passives": {"sum": "isPassive"},
                "totalResponses": {"count": None},
                "avgScore": {"avg": "pollResponse"}
            }
        })
    elif group_by == 'day':
        pipeline.append({
            "group": {
                "group": ["day"],
                "fields": {
                    "promoters": {"sum": "isPromoter"},
                    "detractors": {"sum": "isDetractor"},
                    "passives": {"sum": "isPassive"},
                    "responses": {"count": None}
                }
            }
        })
        pipeline.append({"sort": ["day"]})
    else:  # account
        pipeline.append({
            "group": {
                "group": ["accountId"],
                "fields": {
                    "promoters": {"sum": "isPromoter"},
                    "detractors": {"sum": "isDetractor"},
                    "passives": {"sum": "isPassive"},
                    "responses": {"count": None},
                    "avgScore": {"avg": "pollResponse"}
                }
            }
        })
        pipeline.append({"sort": ["-responses"]})
        pipeline.append({"limit": 20})
    
    aggregation_query = {
        "response": {"mimeType": "application/json"},
        "request": {"name": "NPS Analysis", "pipeline": pipeline}
    }
    
    data = await make_pendo_request("/api/v1/aggregation", method="POST", json_body=aggregation_query)
    
    if not data or not data.get('results'):
        return "No NPS feedback found for the specified criteria."
    
    results = data.get('results', [])
    
    # Format output
    output_lines = [f"NPS Feedback Analysis - Last {days_back} days"]
    if segment_id:
        output_lines.append(f"Segment: {segment_id}")
    if poll_id:
        output_lines.append(f"Poll ID: {poll_id}")
    output_lines.append(f"Grouped by: {group_by}")
    output_lines.append("=" * 50)
    
    if group_by == 'total':
        if results:
            result = results[0]
            promoters = result.get('promoters', 0)
            detractors = result.get('detractors', 0)
            passives = result.get('passives', 0)
            total = result.get('totalResponses', 0)
            avg_score = result.get('avgScore', 0)
            
            if total > 0:
                nps_score = ((promoters - detractors) / total) * 100
            else:
                nps_score = 0
            
            output_lines.append(f"\nNPS Score: {nps_score:.1f}")
            output_lines.append(f"Average Rating: {avg_score:.1f}")
            output_lines.append(f"\nResponse Distribution:")
            output_lines.append(f"  Promoters (9-10): {promoters} ({promoters/total*100:.1f}%)" if total > 0 else f"  Promoters (9-10): {promoters}")
            output_lines.append(f"  Passives (7-8): {passives} ({passives/total*100:.1f}%)" if total > 0 else f"  Passives (7-8): {passives}")
            output_lines.append(f"  Detractors (0-6): {detractors} ({detractors/total*100:.1f}%)" if total > 0 else f"  Detractors (0-6): {detractors}")
            output_lines.append(f"  Total Responses: {total}")
            
            output_lines.append("\nInterpretation:")
            if nps_score > 50:
                output_lines.append("Excellent - Strong customer loyalty")
            elif nps_score > 0:
                output_lines.append("Good - More promoters than detractors")
            elif nps_score > -50:
                output_lines.append("Needs Improvement - More detractors than promoters")
            else:
                output_lines.append("Critical - Urgent attention needed")
    
    elif group_by == 'day':
        for row in results:
            day = format_date(row.get('day', 0))
            promoters = row.get('promoters', 0)
            detractors = row.get('detractors', 0)
            responses = row.get('responses', 0)
            
            if responses > 0:
                nps_score = ((promoters - detractors) / responses) * 100
            else:
                nps_score = 0
            
            output_lines.append(f"\n{day}:")
            output_lines.append(f"  NPS Score: {nps_score:.1f}")
            output_lines.append(f"  Responses: {responses}")
    
    else:  # account
        for row in results[:10]:
            account_id = row.get('accountId', 'Unknown')
            promoters = row.get('promoters', 0)
            detractors = row.get('detractors', 0)
            responses = row.get('responses', 0)
            avg_score = row.get('avgScore', 0)
            
            if responses > 0:
                nps_score = ((promoters - detractors) / responses) * 100
            else:
                nps_score = 0
            
            output_lines.append(f"\n{account_id}:")
            output_lines.append(f"  NPS Score: {nps_score:.1f}")
            output_lines.append(f"  Avg Rating: {avg_score:.1f}")
            output_lines.append(f"  Responses: {responses}")
    
    return "\n".join(output_lines)

# Main execution
if __name__ == "__main__":
    # Verify API key is configured
    logger.info(f"Starting Pendo MCP Server with 15 comprehensive tools")
    logger.info(f"Using Pendo API base URL: {PENDO_API_BASE}")
    
    # Run the server
    mcp.run(transport='stdio')
