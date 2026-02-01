# Log Viewer Design

## Overview

A web-based UI for viewing and analyzing historical state machine logs. Provides debugging, pattern recognition, and performance analysis capabilities without requiring SSH access to the server.

## Goals

1. **Debug historical queries** - Investigate issues after they occur
2. **Pattern recognition** - Spot recurring problems across queries
3. **Performance analysis** - Identify bottlenecks and slow stages
4. **Post-mortem investigation** - Full context for error analysis
5. **No SSH required** - All log access through the web UI

## User Interface

### Location

- New tab: **"Logs"** (next to "Query Portal", "Knowledge", "Domains")

### Main View Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  ExFrame Logs                                    [Search...]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Filters:                                                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ Domain  │ │ Status  │ │  Date   │ │Export│  │              │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Recent Queries (showing 50 of 234)                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ #234 │ q_abc123 │ 17:45:23 │ llm_consciousness │ 2.3s │ ✓ │  │
│  │ #233 │ q_def456 │ 17:44:12 │ exframe          │ ERROR │ ✗ │  │
│  │ #232 │ q_ghi789 │ 17:43:01 │ binary_symmetry   │ 1.8s │ ✓ │  │
│  │ ...                                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Log Detail View (when clicking a row)

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Logs    Query: q_abc123    llm_consciousness    2.3s │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Query: "What is XOR?"                                          │
│  Timestamp: 2025-01-31T17:45:23Z                               │
│  Duration: 2.3s                                                 │
│  Status: Success                                                │
│                                                                 │
│  ┌─ State Machine Summary ─────────────────────────────────┐   │
│  │ Total Events: 13 | States: 10 | Errors: 0               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─ State Transitions ─────────────────────────────────────┐   │
│  │                                                          │   │
│  │ #1 QUERY_RECEIVED                                       │   │
│  │    17:45:23 • Trigger: api_request • Duration: 0ms      │   │
│  │    [IN] dict (100 bytes)                                │   │
│  │      query: "What is XOR?"                              │   │
│  │      domain: "llm_consciousness"                        │   │
│  │                                                          │   │
│  │ #2 QUERY_RECEIVED → ROUTING_SELECTION                   │   │
│  │    17:45:23 • Trigger: specialist_selection_start       │   │
│  │    specialists_available: 2                             │   │
│  │                                                          │   │
│  │ ... (expandable sections for each transition)           │   │
│  │                                                          │   │
│  │ #9 ENRICHMENT_PIPELINE → ENRICHMENT_COMPLETE            │   │
│  │    17:45:25 • Trigger: enrichment_complete • 45ms       │   │
│  │    ┌─ Verbose (user_enabled) ─────────────────────┐     │   │
│  │    │ [IN] dict (150 bytes)                        │     │   │
│  │    │   input_size: 215                            │     │   │
│  │    │   current_response: "Based on the docs..."   │     │   │
│  │    │                                               │     │   │
│  │    │ [OUT] dict (150 bytes)                       │     │   │
│  │    │   llm_used: false                            │     │   │
│  │    │   enriched_response: "Based on the docs..."  │     │   │
│  │    └───────────────────────────────────────────────┘     │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Download JSON] [Download CSV] [Copy to Clipboard]           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### 1. Log Browser (Main View)

**Columns:**
- **#** - Sequential log number
- **Query ID** - Clickable `q_abc123` format
- **Timestamp** - Human-readable time
- **Domain** - Domain ID
- **Duration** - Processing time
- **Status** - Success ✓ or Error ✗

**Filters:**
- **Domain** dropdown - All domains or specific domain
- **Status** dropdown - All, Success only, Errors only
- **Date Range** - Today, Last 7 days, Last 30 days, Custom
- **Search** - Free text search across query text

**Actions:**
- **Export** button - Download filtered logs as JSON

### 2. Log Detail View

**Summary Section:**
- Original query text
- Timestamp, duration, status
- State machine summary (event count, unique states, error flag)

**State Transitions:**
- Expandable accordion for each transition
- Shows full verbose data when available
- Syntax highlighting for JSON

**Actions:**
- Download this log as JSON
- Download as CSV
- Copy to clipboard

### 3. Search

**Full-text search:**
- Searches across query text, response text, error messages
- Case-insensitive
- Highlights matches in results

**Filters:**
- Find all ERROR states
- Find queries with verbose mode enabled
- Find queries exceeding duration threshold

### 4. Export

**Formats:**
- JSON - Full log data with all events
- CSV - Flattened summary (query_id, timestamp, domain, duration, status, error)

**Scope:**
- Single log - From detail view
- Filtered set - From main view with filters applied
- All logs - Complete export

## API Integration

Uses existing endpoints:

```
GET /api/traces/log?limit=100&offset=0
  - Returns paginated list of state machine logs

GET /api/traces/stream
  - Server-sent events for real-time log streaming

GET /api/traces/log/{query_id}
  - (To be added) Get specific log by query_id
```

## Data Storage

Logs are stored in `/app/logs/traces/state_machine.jsonl`:

```jsonl
{"query_id":"q_abc123","from_state":null,"to_state":"QUERY_RECEIVED","trigger":"api_request","timestamp":"2025-01-31T17:45:23.123Z","data":{...},"duration_ms":null,"verbose":{...}}
{"query_id":"q_abc123","from_state":"QUERY_RECEIVED","to_state":"ROUTING_SELECTION","trigger":"specialist_selection_start","timestamp":"2025-01-31T17:45:23.234Z","data":{...},"duration_ms":0,"verbose":{...}}
...
```

## Implementation Phases

### Phase 1: Basic Log Viewer
- Main view with log list
- Pagination
- Basic filters (domain, status, date)
- Click to view detail

### Phase 2: Enhanced Detail View
- Full state machine trace display
- Verbose data visualization
- Expandable sections

### Phase 3: Search & Export
- Full-text search
- JSON/CSV export
- Copy to clipboard

### Phase 4: Real-time Streaming
- Live log tail
- Auto-refresh on new queries
- Notification on errors

### Phase 5: Advanced Analytics
- Performance graphs
- Error frequency analysis
- State duration percentiles

## Technical Considerations

### Performance
- Paginate logs (50 per page by default)
- Lazy load verbose data (expand on demand)
- Consider log rotation (keep last N logs)

### Storage
- JSONL format for easy append/read
- Consider compression for old logs
- Archive option for long-term storage

### Security
- Logs may contain sensitive query data
- Consider authentication requirement
- Option to redact sensitive fields

## Future Enhancements

1. **Log Comparison** - Side-by-side view of two queries
2. **Replay Query** - Re-run a query with same parameters
3. **Log Annotations** - Add notes to specific logs for debugging
4. **Share Link** - Generate shareable URL for specific log
5. **Integration** - Link logs to issue tracking systems
