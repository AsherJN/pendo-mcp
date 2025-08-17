# High Priority Task: Pendo MCP Tool Expansion

## Objective
Expand the Pendo MCP server from 10 tools to a comprehensive 15-tool architecture that provides powerful analytics capabilities while maintaining clarity for LLM ReAct agents.

## Constraints
- Maximum 15 tools to prevent LLM confusion
- Focus areas: Product (pages/features), People (visitors/accounts/segments), Analytics, NPS
- Exclude: Guides, Listen/Feedback modules
- Tools must be clear, chainable, and have distinct purposes

## Final 15-Tool Architecture

### PRODUCT DISCOVERY (3 tools)

#### 1. `search_pages`
- **Purpose**: Find and analyze page usage
- **Parameters**:
  - Required: None
  - Optional: `page_id`, `name_contains`, `app_id`, `include_metrics`, `limit`
- **Returns**: Page details + optional usage metrics
- **API Endpoint**: `/api/v1/page` + aggregation for metrics

#### 2. `search_features`  
- **Purpose**: Find and analyze feature usage
- **Parameters**:
  - Required: None
  - Optional: `feature_id`, `name_contains`, `color`, `app_id`, `include_metrics`, `limit`
- **Returns**: Feature details + optional click metrics
- **API Endpoint**: `/api/v1/feature` + aggregation for metrics

#### 3. `search_track_events`
- **Purpose**: Find and analyze custom events
- **Parameters**:
  - Required: None  
  - Optional: `event_name`, `visitor_id`, `account_id`, `days_back`, `limit`
- **Returns**: Event occurrences with context
- **API Endpoint**: `/api/v1/tracktype` + aggregation

### PEOPLE INSIGHTS (5 tools)

#### 4. `get_visitor_details`
- **Purpose**: Deep dive on specific visitor
- **Parameters**:
  - Required: `visitor_id`
  - Optional: `include_history`, `include_events`
- **Returns**: Visitor metadata, accounts, activity
- **API Endpoint**: `/api/v1/visitor/{id}` + `/history`

#### 5. `search_visitors`
- **Purpose**: Find visitors by criteria
- **Parameters**:
  - Required: None
  - Optional: `account_id`, `segment_id`, `metadata_filter`, `active_since`, `limit`
- **Returns**: Matching visitors with metadata
- **API Endpoint**: Aggregation with visitors source

#### 6. `get_account_details`
- **Purpose**: Deep dive on specific account
- **Parameters**:
  - Required: `account_id`
  - Optional: `include_visitors`, `include_metrics`
- **Returns**: Account metadata, visitor count, activity
- **API Endpoint**: `/api/v1/account/{id}` + aggregation

#### 7. `search_accounts`
- **Purpose**: Find accounts by criteria
- **Parameters**:
  - Required: None
  - Optional: `metadata_filter`, `segment_id`, `min_visitors`, `active_since`, `limit`
- **Returns**: Matching accounts with metadata
- **API Endpoint**: Aggregation with accounts source

#### 8. `analyze_segments`
- **Purpose**: Work with user segments
- **Parameters**:
  - Required: `action` (list|details|check|export)
  - Optional: `segment_id`, `visitor_id`, `account_id`
- **Returns**: Segment info or membership data
- **API Endpoints**: `/api/v1/segment`, `/api/v1/segment/{id}/visitors`

### BEHAVIORAL ANALYTICS (6 tools)

#### 9. `analyze_usage`
- **Purpose**: Understand activity patterns
- **Parameters**:
  - Required: None
  - Optional: `segment_id`, `visitor_id`, `account_id`, `days_back`, `group_by`, `metric_type`
- **Returns**: Events, sessions, time metrics
- **API Endpoint**: Aggregation with events source

#### 10. `analyze_feature_adoption`
- **Purpose**: Track feature/page uptake
- **Parameters**:
  - Required: None
  - Optional: `feature_ids`, `page_ids`, `segment_id`, `days_back`, `group_by`
- **Returns**: Adoption rates, usage frequency
- **API Endpoint**: Aggregation with adoption operator

#### 11. `analyze_retention`
- **Purpose**: Measure user/account stickiness
- **Parameters**:
  - Required: None
  - Optional: `segment_id`, `cohort_date`, `period_type`, `group_by`
- **Returns**: Retention curves, churn analysis
- **API Endpoint**: Aggregation with stickiness operator

#### 12. `analyze_funnels`
- **Purpose**: Multi-step conversion tracking
- **Parameters**:
  - Required: `steps` (list of page/feature IDs)
  - Optional: `segment_id`, `days_back`, `group_by`
- **Returns**: Conversion rates, drop-off points
- **API Endpoint**: Custom aggregation pipeline

#### 13. `analyze_user_paths`
- **Purpose**: Journey and navigation patterns
- **Parameters**:
  - Required: None
  - Optional: `start_page`, `end_page`, `segment_id`, `max_steps`, `days_back`
- **Returns**: Common paths, navigation flows
- **API Endpoint**: Custom aggregation with pageEvents

#### 14. `calculate_product_engagement`
- **Purpose**: PES metrics (growth, stickiness, adoption)
- **Parameters**:
  - Required: None
  - Optional: `segment_id`, `features_list`, `days_back`, `group_by`
- **Returns**: PES scores and components
- **API Endpoint**: Aggregation with PES operator

### FEEDBACK (1 tool)

#### 15. `analyze_nps_feedback`
- **Purpose**: NPS scores and sentiment
- **Parameters**:
  - Required: None
  - Optional: `segment_id`, `poll_id`, `days_back`, `group_by`
- **Returns**: NPS scores, response distribution
- **API Endpoint**: Aggregation with pollsSeen source

## Implementation Strategy

### Phase 1: Consolidate Existing Tools (Keep 7)
- Keep: `get_visitor_details`, `get_account_details` 
- Enhance: `search_track_events` (already has search capability)
- Remove: Redundant list_* tools (will be merged into search_* tools)

### Phase 2: Build Product Tools (2 new)
- Implement `search_pages` (merge list_pages + get by ID + metrics)
- Implement `search_features` (merge list_features + get by ID + metrics)

### Phase 3: Build People Tools (2 new)
- Implement `search_visitors` (metadata search + segment filtering)
- Implement `search_accounts` (enhance existing search_accounts_by_metadata)
- Implement `analyze_segments` (new comprehensive segment tool)

### Phase 4: Build Analytics Tools (6 new)
- Implement `analyze_usage` (events aggregation)
- Implement `analyze_feature_adoption` (adoption operator)
- Implement `analyze_retention` (stickiness operator)
- Implement `analyze_funnels` (custom pipeline)
- Implement `analyze_user_paths` (path analysis)
- Implement `calculate_product_engagement` (PES operator)

### Phase 5: Build Feedback Tool (1 new)
- Implement `analyze_nps_feedback` (polls aggregation)

## Tool Chaining Patterns

### Pattern 1: Discovery → Analysis
```
search_pages(name_contains="checkout") → page_id
analyze_feature_adoption(page_ids=[page_id], segment_id=X)
```

### Pattern 2: Segment → Filter → Analyze
```
analyze_segments(action="list") → segment_id
analyze_retention(segment_id=segment_id, cohort_date="2025-01-01")
```

### Pattern 3: Multi-dimensional Analysis
```
search_accounts(min_visitors=100) → account_ids
search_visitors(account_id=account_ids[0]) → visitor_ids
analyze_usage(visitor_id=visitor_ids[0], group_by="feature")
```

### Pattern 4: Funnel Analysis
```
search_pages(name_contains="signup") → signup_page
search_pages(name_contains="activate") → activation_page
search_pages(name_contains="purchase") → purchase_page
analyze_funnels(steps=[signup_page, activation_page, purchase_page])
```

## Key Design Principles

1. **Verb-based naming**: Actions are clear (search, get, analyze, calculate)
2. **Progressive refinement**: Start broad, add parameters to narrow
3. **Universal segment support**: segment_id works everywhere
4. **Minimal required params**: Most tools work with no parameters
5. **Consistent patterns**: Similar tools have similar parameters

## API Aggregation Patterns to Implement

### Events Aggregation
```json
{
  "source": {
    "events": null,
    "timeSeries": {
      "period": "dayRange",
      "first": "now()",
      "count": -30
    }
  }
}
```

### Visitor Search with Metadata
```json
{
  "source": {
    "visitors": null
  },
  "filter": "metadata.custom.role == 'admin'",
  "limit": 100
}
```

### PES Calculation
```json
{
  "pes": {
    "appId": null,
    "firstDay": "date(2025,1,1)",
    "lastDay": "now()",
    "config": {
      "stickiness": {...},
      "adoption": {...},
      "growth": {...}
    }
  }
}
```

### Funnel Analysis
```json
{
  "source": {
    "pageEvents": null,
    "timeSeries": {...}
  },
  "filter": "pageId in [page1, page2, page3]",
  "group": {
    "group": ["visitorId", "pageId"],
    "fields": {...}
  }
}
```

## Success Metrics

- All 15 tools implemented and tested
- Clear documentation with examples
- Each tool returns formatted, readable output
- Tools chain naturally without confusion
- LLM can understand tool purposes from names/descriptions
- Complex analytics queries possible through tool composition

## Next Steps

1. Review and consolidate existing 10 tools
2. Implement new search_* tools with combined functionality
3. Build analytics tools using aggregation API
4. Create comprehensive test cases
5. Document example queries and expected tool chains
6. Update README with all 15 tools

## Notes

- Priority on readability of output for LLM consumption
- Error messages should suggest next steps
- Include result counts and summaries
- Format timestamps as human-readable dates
- Limit default results to prevent overwhelming responses
