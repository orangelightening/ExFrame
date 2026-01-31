# ExFrame State Machine Design Document

**Version:** 1.0
**Date:** 2026-01-31
**Status:** Design Phase
**Author:** ExFrame Architecture Team

---

## Executive Summary

This document defines a state machine logging system for ExFrame that provides complete observability of the query-response lifecycle while remaining extensible to other system components.

**Core Principle:** One structured log, multiple consumers.

- **State Machine Logger** → Single JSONL log file
- **Trace System** → Consumer of state log
- **Debugging Tools** → Query state log
- **AI Bug Finder** → Analyze state log for patterns

---

## Table of Contents

1. [State Machine Overview](#state-machine-overview)
2. [Complete State Definitions](#complete-state-definitions)
3. [State Transitions](#state-transitions)
4. [Data Schema](#data-schema)
5. [Implementation Plan](#implementation-plan)
6. [Extensibility Considerations](#extensibility-considerations)
7. [Scoping & Boundaries](#scoping--boundaries)

---

## State Machine Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ExFrame Query Lifecycle                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │ QUERY_RECEIVED│  Entry: API/WebSocket/Direct                      │
│  └───────┬───────┘                                                   │
│          │                                                           │
│          ▼                                                           │
│  ┌──────────────────────────────────────────────┐                   │
│  │     DIRECT PROMPT CHECK (// prefix?)        │                   │
│  └──────┬────────────────────────────────────────┘                   │
│         │                                                          │
│    ┌────┴────┐                                                       │
│    │         │                                                       │
│  [Direct]   [Normal]                                                 │
│    │         │                                                       │
│    ▼         ▼                                                       │
│  ┌──────────────┐  ┌──────────────────┐                          │
│  │ DIRECT_LLM   │  │ ROUTING_SELECTION │                          │
│  └──────┬───────┘  └──────┬─────────────┘                          │
│         │                │                                           │
│         │         ┌──────┴─────────┐                                │
│         │         │                  │                               │
│         │    ┌────┴─────┐      ┌─────┴──────┐                           │
│         │    │           │      │            │                        │
│         │    │  Single   │      │  Multiple  │                        │
│         │    │ Specialist│      │ Specialists│                       │
│         │    └─────┬─────┘      └─────┬──────┘                           │
│         │          │                  │                               │
│         ▼          ▼                  ▼                               │
│  ┌────────────────────┐  ┌─────────────────────┐                    │
│  │SPECIALIST_PROCESSING│  │MULTI_SPECIALIST_    │                    │
│  │                     │  │PROCESSING           │                    │
│  └──────┬──────────────┘  └──────┬──────────────┘                    │
│         │                        │                                    │
│         ▼                        │                                    │
│  ┌────────────────────┐          │                                    │
│  │ OUT_OF_SCOPE_CHECK │          │                                    │
│  └──────┬──────────────┘          │                                    │
│         │                        │                                    │
│    ┌────┴────┐                    │                                    │
│    │         │                    │                                    │
│ [In Scope] [Out of Scope]         │                                    │
│    │         │                    │                                    │
│    │    ┌────┴────────────────────┴─────┐                           │
│    │    │                             │                           │
│    ▼    ▼                             ▼                           │
│  ┌────────────────┐         ┌────────────────┐                        │
│  │ENRICHMENT_     │         │RESPONSE_       │                        │
│  │PIPELINE        │         │AGGREGATION     │                        │
│  └──────┬─────────┘         └──────┬─────────┘                        │
│         │                        │                                    │
│         ▼                        │                                    │
│  ┌────────────────────────────────┴─────────┐                       │
│  │            FORMATTING_PHASE              │                       │
│  └──────────────────────┬──────────────────┘                       │
│                         │                                           │
│                         ▼                                           │
│  ┌─────────────────────────────────────────────┐                    │
│  │          RESPONSE_CONSTRUCTION              │                    │
│  └──────────────────────┬──────────────────────┘                    │
│                         │                                           │
│                         ▼                                           │
│  ┌─────────────────────────────────────────────┐                    │
│  │               LOG_AND_EXIT                  │                    │
│  └──────────────────────┬──────────────────────┘                    │
│                         │                                           │
│                         ▼                                           │
│              RESPONSE_RETURNED                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Error States (parallel to main flow)

```
ERROR_NO_SPECIALIST    → LOG_AND_EXIT
ERROR_NO_LLM_KEY       → LOG_AND_EXIT
ERROR_LLM_API         → LOG_AND_EXIT (continue without LLM)
ERROR_PATTERN_SEARCH  → ENRICHMENT_PIPELINE (continue)
ERROR_ENRICHER_FAILED → Next enricher (fail-safe)
ERROR_DOMAIN_LOAD     → Immediate failure
```

---

## Complete State Definitions

### Primary States

```python
class QueryState(Enum):
    """All possible states in the query lifecycle."""

    # Entry and Routing
    QUERY_RECEIVED = "QUERY_RECEIVED"               # Initial state
    DIRECT_PROMPT_CHECK = "DIRECT_PROMPT_CHECK"     # Check for // prefix
    DIRECT_LLM = "DIRECT_LLM"                       # Bypass to LLM
    ROUTING_SELECTION = "ROUTING_SELECTION"         # Select specialist(s)

    # Specialist Processing
    SINGLE_SPECIALIST_PROCESSING = "SINGLE_SPECIALIST_PROCESSING"
    MULTI_SPECIALIST_PROCESSING = "MULTI_SPECIALIST_PROCESSING"
    RESPONSE_AGGREGATION = "RESPONSE_AGGREGATION"   # Merge multi-specialist results

    # Content Processing
    OUT_OF_SCOPE_CHECK = "OUT_OF_SCOPE_CHECK"       # Check if query is in domain scope
    SEARCHING = "SEARCHING"                         # Knowledge base search
    CONTEXT_READY = "CONTEXT_READY"                 # Search complete, context prepared

    # Enrichment
    ENRICHMENT_PIPELINE = "ENRICHMENT_PIPELINE"     # Entry to enrichment phase
    LLM_CONFIRMATION_CHECK = "LLM_CONFIRMATION_CHECK" # Check if confirmation needed
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION" # Waiting for user
    LLM_PROCESSING = "LLM_PROCESSING"               # LLM call in progress
    LLM_POST_PROCESSING = "LLM_POST_PROCESSING"     # Clean contradictions
    ENRICHMENT_COMPLETE = "ENRICHMENT_COMPLETE"     # All enrichers done

    # Output
    FORMATTING_PHASE = "FORMATTING_PHASE"           # Apply formatter
    RESPONSE_CONSTRUCTION = "RESPONSE_CONSTRUCTION" # Build final response

    # Terminal States
    COMPLETE = "COMPLETE"                           # Success
    ERROR = "ERROR"                                 # Error occurred
    LOG_AND_EXIT = "LOG_AND_EXIT"                   # Logging and cleanup
    RESPONSE_RETURNED = "RESPONSE_RETURNED"         # Final state
```

### State Descriptions

| State | Description | Trigger | Next States |
|-------|-------------|---------|-------------|
| `QUERY_RECEIVED` | Query entered system | API request | `DIRECT_PROMPT_CHECK` |
| `DIRECT_PROMPT_CHECK` | Check if // prefix | Initial check | `DIRECT_LLM` or `ROUTING_SELECTION` |
| `ROUTING_SELECTION` | Select specialist(s) | Check complete | `SINGLE_SPECIALIST_PROCESSING`, `MULTI_SPECIALIST_PROCESSING`, `ERROR_NO_SPECIALIST` |
| `SINGLE_SPECIALIST_PROCESSING` | One specialist processes | Specialist selected | `OUT_OF_SCOPE_CHECK` |
| `MULTI_SPECIALIST_PROCESSING` | Multiple specialists | Router selected multiples | `RESPONSE_AGGREGATION` |
| `RESPONSE_AGGREGATION` | Merge specialist responses | All specialists done | `OUT_OF_SCOPE_CHECK` |
| `OUT_OF_SCOPE_CHECK` | Check domain scope | Specialist returned data | `COMPLETE` (if out of scope) or `ENRICHMENT_PIPELINE` |
| `SEARCHING` | Knowledge base search | Context needed | `CONTEXT_READY` |
| `CONTEXT_READY` | Search complete | Search returned | `ENRICHMENT_PIPELINE` |
| `ENRICHMENT_PIPELINE` | Run enrichers sequentially | Context ready | `LLM_CONFIRMATION_CHECK` |
| `LLM_CONFIRMATION_CHECK` | Check if user confirmation needed | Enrichment started | `AWAITING_CONFIRMATION` or `LLM_PROCESSING` |
| `AWAITING_CONFIRMATION` | Wait for user response | Confirmation needed | (async - user re-queries) |
| `LLM_PROCESSING` | LLM generates/enhances | Confirmed or auto-trigger | `LLM_POST_PROCESSING` |
| `LLM_POST_PROCESSING` | Clean up LLM response | LLM returned | `ENRICHMENT_COMPLETE` |
| `ENRICHMENT_COMPLETE` | All enrichers done | Last enricher finished | `FORMATTING_PHASE` |
| `FORMATTING_PHASE` | Apply formatter | Enrichment complete | `RESPONSE_CONSTRUCTION` |
| `RESPONSE_CONSTRUCTION` | Build final response | Format complete | `LOG_AND_EXIT` |
| `LOG_AND_EXIT` | Log and cleanup | Response ready | `RESPONSE_RETURNED` |
| `COMPLETE` | Success (terminal) | Process succeeded | (end) |
| `ERROR` | Error (terminal) | Error occurred | `LOG_AND_EXIT` |

---

## State Transitions

### Normal Query Flow (Single Specialist)

```
QUERY_RECEIVED
  └─→ DIRECT_PROMPT_CHECK
       └─→ ROUTING_SELECTION
            └─→ SINGLE_SPECIALIST_PROCESSING
                 └─→ OUT_OF_SCOPE_CHECK
                      ├─[out_of_scope=true]→ COMPLETE
                      └─[in_scope]→ ENRICHMENT_PIPELINE
                                    └─→ LLM_CONFIRMATION_CHECK
                                          ├─[confirmation_needed]→ AWAITING_CONFIRMATION
                                          ├─[llm_confirmed]→ LLM_PROCESSING
                                          └─[skip_llm]→ ENRICHMENT_COMPLETE
                                               └─→ FORMATTING_PHASE
                                                    └─→ RESPONSE_CONSTRUCTION
                                                         └─→ LOG_AND_EXIT
                                                              └─→ RESPONSE_RETURNED
```

### Direct Prompt Flow (// prefix)

```
QUERY_RECEIVED
  └─→ DIRECT_PROMPT_CHECK
       └─→ DIRECT_LLM
            └─→ LOG_AND_EXIT
                 └─→ RESPONSE_RETURNED
```

### Multi-Specialist Flow

```
QUERY_RECEIVED
  └─→ ROUTING_SELECTION
       └─→ MULTI_SPECIALIST_PROCESSING
            └─→ RESPONSE_AGGREGATION
                 └─→ OUT_OF_SCOPE_CHECK
                      └─→ ENRICHMENT_PIPELINE
                           └─→ [same as above]
```

### Error Transitions

```
[any state] ──[error]──> ERROR
                   └─→ LOG_AND_EXIT
```

---

## Data Schema

### State Event Schema

```json
{
  "query_id": "q_a1b2c3d4e5f6",
  "from_state": "ROUTING_SELECTION",
  "to_state": "SINGLE_SPECIALIST_PROCESSING",
  "trigger": "specialist_selected",
  "timestamp": "2026-01-31T01:23:45.123456Z",
  "data": {
    "specialist_id": "exframe_specialist",
    "specialist_name": "ExFrame Knowledge Specialist",
    "confidence": 0.85,
    "specialists_available": 3
  },
  "duration_ms": 15,
  "metadata": {
    "domain": "exframe",
    "trace_enabled": true,
    "session_id": "sess_123"
  }
}
```

### Data Dictionary by State

| State | Required Fields in `data` | Optional Fields |
|-------|-------------------------|-----------------|
| `QUERY_RECEIVED` | `query`, `domain`, `timestamp` | `context`, `llm_confirmed`, `format_type`, `session_id` |
| `ROUTING_SELECTION` | `routing_strategy` | `specialist_scores`, `all_specialists`, `selected_specialist` |
| `SINGLE_SPECIALIST_PROCESSING` | `specialist_id` | `confidence`, `search_strategy`, `patterns_found` |
| `OUT_OF_SCOPE_CHECK` | `out_of_scope` | `out_of_scope_reason` |
| `LLM_CONFIRMATION_CHECK` | `confirmation_required` | `partial_response` |
| `LLM_PROCESSING` | `llm_mode` | `model`, `prompt_tokens`, `research_strategy_used` |
| `ENRICHMENT_COMPLETE` | `enrichers_executed`, `llm_used` | `enrichment_summary` |
| `FORMATTING_PHASE` | `formatter`, `format_type` | `output_size` |
| `ERROR` | `error_type`, `error_message` | `exception_type`, `stack_trace` |

### Log File Format

**File:** `/app/logs/traces/state_machine.jsonl`

**Format:** JSONL (one JSON object per line)

**Rotation:** Daily files: `state_machine-YYYY-MM-DD.jsonl`

**Example:**
```
{"query_id":"q_abc123","from_state":null,"to_state":"QUERY_RECEIVED","trigger":"api_request","timestamp":"2026-01-31T01:00:00Z","data":{"query":"What is ExFrame?","domain":"exframe"},"duration_ms":null}
{"query_id":"q_abc123","from_state":"QUERY_RECEIVED","to_state":"ROUTING_SELECTION","trigger":"direct_prompt_check","timestamp":"2026-01-31T01:00:01Z","data":{"is_direct_prompt":false},"duration_ms":1}
```

---

## Implementation Plan

### Phase 1: Core State Machine (2 days)

**File:** `generic_framework/state/state_machine.py`

```python
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import json
import uuid

class QueryState(Enum):
    """Query lifecycle states."""
    QUERY_RECEIVED = "QUERY_RECEIVED"
    DIRECT_PROMPT_CHECK = "DIRECT_PROMPT_CHECK"
    DIRECT_LLM = "DIRECT_LLM"
    ROUTING_SELECTION = "ROUTING_SELECTION"
    SINGLE_SPECIALIST_PROCESSING = "SINGLE_SPECIALIST_PROCESSING"
    MULTI_SPECIALIST_PROCESSING = "MULTI_SPECIALIST_PROCESSING"
    RESPONSE_AGGREGATION = "RESPONSE_AGGREGATION"
    OUT_OF_SCOPE_CHECK = "OUT_OF_SCOPE_CHECK"
    ENRICHMENT_PIPELINE = "ENRICHMENT_PIPELINE"
    LLM_CONFIRMATION_CHECK = "LLM_CONFIRMATION_CHECK"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    LLM_PROCESSING = "LLM_PROCESSING"
    LLM_POST_PROCESSING = "LLM_POST_PROCESSING"
    ENRICHMENT_COMPLETE = "ENRICHMENT_COMPLETE"
    FORMATTING_PHASE = "FORMATTING_PHASE"
    RESPONSE_CONSTRUCTION = "RESPONSE_CONSTRUCTION"
    LOG_AND_EXIT = "LOG_AND_EXIT"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"

class QueryStateMachine:
    """State machine logger for query pipeline observability."""

    def __init__(self, query_id: Optional[str] = None):
        self.query_id = query_id or f"q_{uuid.uuid4().hex[:12]}"
        self.current_state: Optional[QueryState] = None
        self.state_entered_at: Optional[datetime] = None
        self.events: list = []
        self.log_path = Path("/app/logs/traces/state_machine.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def transition(self, to_state: QueryState, trigger: str,
                   data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log state transition."""
        now = datetime.utcnow()

        duration_ms = None
        if self.state_entered_at:
            duration_ms = int((now - self.state_entered_at).total_seconds() * 1000)

        event = {
            "query_id": self.query_id,
            "from_state": self.current_state.value if self.current_state else None,
            "to_state": to_state.value,
            "trigger": trigger,
            "timestamp": now.isoformat() + "Z",
            "data": data or {},
            "duration_ms": duration_ms
        }

        self.events.append(event)
        self._write_event(event)

        self.current_state = to_state
        self.state_entered_at = now

        return event

    def _write_event(self, event: Dict[str, Any]) -> None:
        """Async-safe event writing."""
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            # Log but don't fail the query
            print(f"[StateMachine] Failed to write event: {e}")

    def error(self, trigger: str, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transition to ERROR state."""
        return self.transition(QueryState.ERROR, trigger, error_data)

    def complete(self, final_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transition to COMPLETE state."""
        return self.transition(QueryState.COMPLETE, "query_complete", final_data)
```

### Phase 2: Integration into GenericAssistantEngine (3 days)

**File:** `generic_framework/assist/engine.py`

**Integration points:**
- Line 135: Initialize `QueryStateMachine` in `process_query()`
- Line 147-171: Wrap routing logic with state transitions
- Line 173-207: Wrap knowledge base search
- Line 208-272: Wrap specialist processing
- Line 274-350: Wrap enrichment pipeline
- Line 369-406: Wrap formatting

**Changes to `process_query()`:**

```python
async def process_query(self, query: str, context: Dict = None) -> Dict:
    """Process query with state machine logging."""

    # Initialize state machine
    sm = QueryStateMachine()

    try:
        # STATE: QUERY_RECEIVED
        sm.transition(QueryState.QUERY_RECEIVED, "api_request", {
            "query": query,
            "domain": self.domain_id,
            "context": context
        })

        # STATE: DIRECT_PROMPT_CHECK
        is_direct = query.strip().startswith('//')
        sm.transition(QueryState.DIRECT_PROMPT_CHECK, "direct_prompt_check", {
            "is_direct_prompt": is_direct
        })

        if is_direct:
            # Direct to LLM, skip routing
            sm.transition(QueryState.DIRECT_LLM, "direct_llm_bypass", {
                "original_query": query
            })
            response = await self._direct_llm_call(query)
            sm.complete({"response_size": len(str(response))})
            return response

        # STATE: ROUTING_SELECTION
        sm.transition(QueryState.ROUTING_SELECTION, "routing_start", {
            "routing_strategy": self.domain.routing_strategy
        })

        specialist = await self.domain.get_specialist_for_query(query)

        if not specialist:
            sm.error("no_specialist", {"error": "No specialist available"})
            return {"error": "No specialist available"}

        # STATE: SPECIALIST_PROCESSING
        sm.transition(QueryState.SINGLE_SPECIALIST_PROCESSING, "specialist_selected", {
            "specialist_id": specialist.specialist_id,
            "specialist_name": specialist.name
        })

        response_data = await specialist.process_query(query, context)

        # Check out_of_scope
        sm.transition(QueryState.OUT_OF_SCOPE_CHECK, "specialist_complete", {
            "out_of_scope": response_data.get("out_of_scope", False),
            "out_of_scope_reason": response_data.get("out_of_scope_reason")
        })

        if response_data.get("out_of_scope"):
            sm.complete({"response": response_data.get("response")})
            return response_data

        # STATE: ENRICHMENT_PIPELINE
        sm.transition(QueryState.ENRICHMENT_PIPELINE, "enrichment_start", {
            "enrichers_configured": len(self.domain.enrichers)
        })

        enriched_data = await self.domain.enrich(query, response_data, context)

        # STATE: FORMATTING_PHASE
        sm.transition(QueryState.FORMATTING_PHASE, "formatting_start", {
            "format_type": context.get("format") if context else "markdown"
        })

        formatted = await self.domain.format_response(enriched_data, context)

        # STATE: RESPONSE_CONSTRUCTION
        sm.transition(QueryState.RESPONSE_CONSTRUCTION, "response_ready", {
            "response_size": len(str(formatted))
        })

        # STATE: LOG_AND_EXIT
        sm.transition(QueryState.LOG_AND_EXIT, "logging_complete", {
            "query_logged": True
        })

        # STATE: COMPLETE
        sm.complete({"status": "success"})

        return formatted

    except Exception as e:
        sm.error("exception", {
            "error": str(e),
            "exception_type": type(e).__name__,
            "traceback": traceback.format_exc()
        })
        raise
```

### Phase 3: Trace Consumer Endpoint (1 day)

**File:** `generic_framework/api/app.py`

```python
@app.get("/api/query/{query_id}/trace")
async def get_query_trace(query_id: str):
    """Get state machine trace for a query."""

    trace_file = Path("logs/traces/state_machine.jsonl")

    if not trace_file.exists():
        raise HTTPException(404, "Trace not found")

    events = []
    with open(trace_file) as f:
        for line in f:
            try:
                event = json.loads(line)
                if event['query_id'] == query_id:
                    events.append(event)
            except json.JSONDecodeError:
                continue

    if not events:
        raise HTTPException(404, f"Query {query_id} not found")

    # Calculate total duration
    if len(events) >= 2:
        total_duration = (
            datetime.fromisoformat(events[-1]['timestamp'].replace('Z', ''))
            - datetime.fromisoformat(events[0]['timestamp'].replace('Z', ''))
        ).total_seconds() * 1000
    else:
        total_duration = 0

    return {
        "query_id": query_id,
        "events": events,
        "total_duration_ms": total_duration,
        "final_state": events[-1]['to_state'],
        "error_occurred": any(e['to_state'] == 'ERROR' for e in events)
    }
```

### Phase 4: AI Bug Finder (2 days)

**File:** `generic_framework/diagnostics/state_analyzer.py`

```python
class StateMachineAnalyzer:
    """Analyze state machine logs for bug patterns."""

    def __init__(self):
        self.log_path = Path("/app/logs/traces/state_machine.jsonl")
        self.bugs_path = Path("/app/logs/diagnostics/bugs.json")

    async def analyze_recent_queries(self, limit: int = 100) -> List[Dict]:
        """Analyze recent queries for bug patterns."""

        # Load recent events
        events = self._load_recent_events(limit)

        # Group by query_id
        by_query = {}
        for event in events:
            qid = event['query_id']
            if qid not in by_query:
                by_query[qid] = []
            by_query[qid].append(event)

        bugs = []

        for query_id, query_events in by_query.items():
            bug_patterns = self._detect_bug_patterns(query_events)
            if bug_patterns:
                bugs.append({
                    "query_id": query_id,
                    "patterns": bug_patterns,
                    "severity": self._calculate_severity(bug_patterns)
                })

        # Save bugs
        self._save_bugs(bugs)

        return bugs

    def _detect_bug_patterns(self, events: List[Dict]) -> List[str]:
        """Detect bug patterns in query events."""
        patterns = []

        # Pattern 1: LLM call with empty context
        for i, event in enumerate(events):
            if event['to_state'] == 'LLM_PROCESSING':
                context_size = events[i-1]['data'].get('context_size', 0)
                if context_size == 0:
                    patterns.append("LLM_CALLED_WITH_EMPTY_CONTEXT")

        # Pattern 2: Out of scope false with no patterns
        out_of_scope_event = next((e for e in events
                                     if e['to_state'] == 'OUT_OF_SCOPE_CHECK'), None)
        if out_of_scope_event and not out_of_scope_event['data'].get('out_of_scope'):
            specialist_event = next((e for e in events
                                        if e['to_state'] == 'SINGLE_SPECIALIST_PROCESSING'), None)
            if specialist_event and specialist_event['data'].get('patterns_found', 0) == 0:
                patterns.append("EMPTY_RESULT_NOT_MARKED_OUT_OF_SCOPE")

        # Pattern 3: LLM confirmation loop (same query re-enters)
        confirmation_events = [e for e in events if e['to_state'] == 'AWAITING_CONFIRMATION']
        if len(confirmation_events) > 1:
            patterns.append("CONFIRMATION_LOOP_DETECTED")

        return patterns

    def _calculate_severity(self, patterns: List[str]) -> str:
        """Calculate bug severity."""
        if 'LLM_CALLED_WITH_EMPTY_CONTEXT' in patterns:
            return 'HIGH'
        elif 'CONFIRMATION_LOOP_DETECTED' in patterns:
            return 'MEDIUM'
        else:
            return 'LOW'
```

---

## Extensibility Considerations

### Query-Response Focus (Primary)

The initial implementation focuses on the query-response lifecycle because:
1. It's the most critical path to observe
2. It has the most complex state transitions
3. Bug detection here has the highest impact
4. It's self-contained with clear boundaries

### Extension Points to Other Systems

#### 1. Domain Lifecycle (Secondary Priority)

**Additional States:**
- `DOMAIN_LOADING` - Domain being loaded
- `DOMAIN_ACTIVE` - Domain ready for queries
- `DOMAIN_ERROR` - Domain failed to load
- `DOMAIN_UNLOADING` - Domain being unloaded

**Integration Point:** `generic_framework/core/universe.py`

#### 2. Universe Management (Tertiary Priority)

**Additional States:**
- `UNIVERSE_CREATE` - Universe being created
- `UNIVERSE_SWITCH` - Switching universes
- `UNIVERSE_EXPORT` - Exporting universe
- `UNIVERSE_IMPORT` - Importing universe

**Integration Point:** `generic_framework/core/universe.py`

#### 3. Pattern CRUD (Tertiary Priority)

**Additional States:**
- `PATTERN_CREATE` - Pattern creation
- `PATTERN_UPDATE` - Pattern update
- `PATTERN_VALIDATE` - Pattern validation
- `PATTERN_DELETE` - Pattern deletion

**Integration Point:** API endpoints in `generic_framework/api/app.py`

### Unified State Machine Design

To keep this extensible, design a base `StateMachine` class:

```python
class StateMachine:
    """Base state machine for all ExFrame systems."""

    def __init__(self, system_name: str):
        self.system_name = system_name
        self.state_type = f"{system_name}_state"
        self.log_path = Path(f"/app/logs/traces/{system_name}_state_machine.jsonl")

class QueryStateMachine(StateMachine):
    """Query-specific state machine."""
    def __init__(self):
        super().__init__("query")

class DomainStateMachine(StateMachine):
    """Domain-specific state machine."""
    def __init__(self):
        super().__init__("domain")
```

---

## Scoping & Boundaries

### What's Included (Phase 1)

**✅ Query-Response Lifecycle:**
- API entry point → response exit
- All routing decisions
- All specialist processing
- All enrichment phases
- All formatting
- Error handling
- LLM fallback flows

**✅ Logging Infrastructure:**
- State machine core class
- JSONL log file format
- Daily log rotation
- Async-safe writes

**✅ Query Trace Endpoint:**
- Retrieve state log for query
- Visual trace output
- Bug pattern detection

### What's Excluded (For Now)

**❌ Out of Scope (Phase 1):**
- Domain lifecycle states (can be added later)
- Universe management states (can be added later)
- Pattern CRUD states (can be added later)
- Real-time state streaming via WebSocket
- State visualization dashboard
- Performance metrics aggregation

**❌ Explicitly Not Covered:**
- Internal service-to-service communication
- Background job processing
- Health check states
- Metrics collection

### "Every Action Traceable" - Too Big?

**Verdict: Yes, that's too big.**

**Why?**
1. **Overhead**: Logging every action would slow down the system
2. **Noise**: Most actions don't need state-level logging
3. **Maintenance Burden**: More states = more complexity
4. **Diminishing Returns**: Debug value decreases as granularity increases

**Recommended Approach:**
- **State-level logging**: Log major phase transitions (what we're doing)
- **Detailed logging for critical paths**: Add more detail for queries, less for other systems
- **Metrics for performance**: Use metrics for timing, not state transitions
- **Debug logging**: Keep existing debug logging for detailed troubleshooting

**Example distinction:**
```
✅ State Transition: "SPECIALIST_PROCESSING → ENRICHMENT_PIPELINE"
❌ Too Fine: "enricher_iteration_1 → enricher_iteration_2"
✅ Metrics: "enrichment_duration_ms: 450"
❌ Too Fine: "file_read_start → file_read_complete"
```

---

## Success Criteria

Phase 1 is complete when:
- [ ] `QueryStateMachine` class implemented
- [ ] All query phases log state transitions
- [ ] `/api/query/{id}/trace` returns state trace
- [ ] Bug detection finds empty context LLM calls
- [ ] Log rotation works correctly

Phase 2 is complete when:
- [ ] Domain lifecycle states tracked
- [ ] Universe management states tracked
- [ ] Unified `StateMachine` base class
- [ ] Cross-system trace correlation works

---

## Open Questions

1. **Query ID format**: Use UUID v4 or ULID? (ULID is time-sorted, better for logs)
2. **Async logging**: Use `aiofiles` or thread pool executor?
3. **State persistence**: Keep all events in memory or query on demand?
4. **Trace retention**: How long to keep state logs?
5. **Performance impact**: What's acceptable overhead for state logging?

---

## Next Steps

1. ✅ Design document complete
2. ⏳ Implement core `QueryStateMachine` class
3. ⏳ Integrate into `GenericAssistantEngine`
4. ⏳ Add trace endpoint
5. ⏳ Implement AI bug finder
6. ⏳ Test with real queries
7. ⏳ Extend to domain lifecycle

---

## Detailed Change Tracking (Option B)

**Purpose:** Provide complete visibility into what each enricher and formatter actually does to the response data.

### Enhanced Data Schema with Changes

Each state transition now includes a `changes` object that captures:

```json
{
  "query_id": "q_abc123",
  "from_state": "ENRICHMENT_PIPELINE",
  "to_state": "RelatedPatternEnricher",
  "trigger": "enricher_started",
  "timestamp": "2026-01-31T01:00:05.123456Z",
  "data": {
    "enricher": "RelatedPatternEnricher",
    "input_size": 1250,
    "output_size": 1450,
    "duration_ms": 15,
    "changes": {
      "added": {
        "related_patterns": {
          "count": 3,
          "ids": ["pattern_abc", "pattern_def", "pattern_123"],
          "summary": "Added 3 related patterns"
        }
      },
      "modified": {
        "response": {
          "before_size": 1250,
          "after_size": 1450,
          "size_delta": "+200"
        }
      },
      "removed": []
    }
  },
  "metadata": {
    "domain": "exframe",
    "session_id": "sess_123",
    "trace_enabled": true
  }
}
```

### Complete Example: Query Through Full Pipeline

#### 1. QUERY_RECEIVED
```json
{
  "to_state": "QUERY_RECEIVED",
  "data": {
    "query": "What is the pipeline system?",
    "domain": "exframe",
    "user_ip": "192.168.1.100"
  }
}
```

#### 2. ROUTING_SELECTION
```json
{
  "from_state": "QUERY_RECEIVED",
  "to_state": "ROUTING_SELECTION",
  "data": {
    "routing_strategy": "ConfidenceBasedRouter",
    "specialists_available": 3,
    "changes": {
      "removed": [],
      "added": {
        "selected_specialist": {
          "name": "ExFrameSpecialist",
          "confidence": 0.92
        }
      }
    }
  }
}
```

#### 3. SINGLE_SPECIALIST_PROCESSING
```json
{
  "from_state": "ROUTING_SELECTION",
  "to_state": "SINGLE_SPECIALIST_PROCESSING",
  "data": {
    "specialist": "ExFrameSpecialist",
    "search_strategy": "document",
    "changes": {
      "added": {
        "search_results": {
          "count": 2,
          "sources": ["README.md", "PLUGIN_ARCHITECTURE.md"]
        }
      }
    }
  }
}
```

#### 4. ENRICHMENT_PIPELINE - RelatedPatternEnricher
```json
{
  "from_state": "SINGLE_SPECIALIST_PROCESSING",
  "to_state": "RelatedPatternEnricher",
  "data": {
    "enricher": "RelatedPatternEnricher",
    "input_size": 850,
    "output_size": 1050,
    "duration_ms": 8,
    "changes": {
      "added": {
        "related_patterns": {
          "count": 2,
          "ids": ["exframe_domain", "exframe_patterns"],
          "names": ["ExFrame Domain Configuration", "Pattern Management"]
        }
      },
      "modified": {
        "response": {
          "before_size": 850,
          "after_size": 1050,
          "size_delta": "+200"
        }
      }
    }
  }
}
```

#### 5. ENRICHMENT_PIPELINE - LLMEnricher (Confirmation Needed)
```json
{
  "from_state": "RelatedPatternEnricher",
  "to_state": "LLM_CONFIRMATION_CHECK",
  "data": {
    "enricher": "LLMEnricher",
    "input_size": 1050,
    "changes": {
      "added": {
        "llm_suggestion": {
          "reason": "patterns_weak",
          "confidence": 0.45,
          "would_use_llm": true
        }
      },
      "modified": {
        "response": {
          "before": "has_patterns",
          "after": "awaiting_confirmation"
        }
      }
    }
  }
}
```

#### 6. RESPONSE_RETURNED (User Confirms)
```json
{
  "from_state": "AWAITING_CONFIRMATION",
  "to_state": "LLM_PROCESSING",
  "data": {
    "llm_confirmed": true,
    "changes": {
      "added": {
        "llm_call": {
          "model": "claude-sonnet-4",
          "mode": "enhance",
          "prompt_tokens": 1450
        }
      },
      "removed": {
        "awaiting_confirmation": {
          "reason": "user_confirmed_llm"
        }
      }
    }
  }
}
```

#### 7. ENRICHMENT_PIPELINE - LLMEnricher (Processing)
```json
{
  "from_state": "LLM_PROCESSING",
  "to_state": "LLM_POST_PROCESSING",
  "data": {
    "enricher": "LLMEnricher",
    "input_size": 1050,
    "output_size": 2800,
    "duration_ms": 1800,
    "changes": {
      "added": {
        "llm_response": {
          "content_preview": "Based on the documentation...",
          "tokens_used": 1350
        },
        "sources_cited": {
          "count": 5,
          "files": ["README.md", "PLUGIN_ARCHITECTURE.md", ...]
        }
      },
      "removed": {
        "raw_answer": {
          "reason": "cleaned_up_for_display"
        }
      },
      "modified": {
        "response": {
          "before": "pattern_based",
          "after": "llm_enhanced"
        }
      }
    }
  }
}
```

#### 8. FORMATTING_PHASE - MarkdownFormatter
```json
{
  "from_state": "ENRICHMENT_COMPLETE",
  "to_state": "MarkdownFormatter",
  "data": {
    "formatter": "MarkdownFormatter",
    "format_type": "markdown",
    "input_type": "dict",
    "output_type": "str",
    "changes": {
      "added": {
        "markdown_content": {
          "preview": "# What is the pipeline system?\n\nBased on..."
        }
      },
      "removed": {
        "response_dict": {
          "reason": "converted_to_string"
        }
      },
      "modified": {
        "structure": {
          "from": "nested_dict",
          "to": "markdown_string"
        }
      }
    }
  }
}
```

### Change Tracking Schema Definition

```python
class StateChangeTracker:
    """Track detailed changes during state transitions."""

    @staticmethod
    def log_changes(before: Dict, after: Dict, action: str, 
                    component: str) -> Dict[str, Any]:
        """Capture what changed between before and after states."""
        
        changes = {
            "added": {},
            "removed": {},
            "modified": {}
        }
        
        # Find added keys
        for key in after.keys():
            if key not in before:
                changes["added"][key] = _describe_value(after[key], action, component)
        
        # Find removed keys
        for key in before.keys():
            if key not in after:
                changes["removed"][key] = _describe_value(before[key], action, component)
        
        # Find modified keys
        for key in before.keys():
            if key in after and before[key] != after[key]:
                changes["modified"][key] = _compare_values(
                    before[key], after[key], action, component
                )
        
        return changes

    @staticmethod
    def _describe_value(value: Any, action: str, component: str) -> Dict:
        """Describe a single value change."""
        if isinstance(value, dict):
            return {
                "type": "dict",
                "count": len(value),
                "keys": list(value.keys())[:5],  # First 5 keys
                "summary": f"{action} to {component}"
            }
        elif isinstance(value, list):
            return {
                "type": "list",
                "count": len(value),
                "summary": f"{action} {len(value)} items"
            }
        else:
            return {
                "type": type(value).__name__,
                "preview": str(value)[:100]
            }

    @staticmethod
    def _compare_values(before: Any, after: Any, action: str, 
                          component: str) -> Dict:
        """Compare two values and describe the difference."""
        
        if isinstance(before, dict) and isinstance(after, dict):
            before_keys = set(before.keys())
            after_keys = set(after.keys())
            
            return {
                "type": "dict_modified",
                "keys_added": list(after_keys - before_keys),
                "keys_removed": list(before_keys - after_keys),
                "keys_modified": list(before_keys & after_keys),
                "size_delta": len(str(after)) - len(str(before))
            }
        
        return {
            "type": type(after).__name__,
            "before": str(before)[:100],
            "after": str(after)[:100]
        }
```

### Integration Pattern for Enrichers

Each enricher logs its changes:

```python
class RelatedPatternEnricher(EnrichmentPlugin):
    async def enrich(self, query, response_data, context):
        # Capture before state
        before = response_data.copy()
        
        # Perform enrichment
        related = await self._find_related(query, response_data)
        response_data['related_patterns'] = related
        
        # Log detailed changes
        state.transition(
            QueryState.ENRICHMENT,
            f"{self.__class__.__name__}_executed",
            {
                "enricher": self.__class__.__name__,
                "input_size": len(str(before)),
                "output_size": len(str(response_data)),
                "changes": self._log_changes(before, response_data)
            }
        )
        
        return response_data
    
    def _log_changes(self, before: Dict, after: Dict) -> Dict:
        """Log what this enricher changed."""
        return {
            "added": {
                "related_patterns": {
                    "count": len(after.get('related_patterns', [])),
                    "ids": [p['id'] for p in after.get('related_patterns', [])]
                }
            },
            "modified": {
                "response": {
                    "before_size": len(str(before)),
                    "after_size": len(str(after)),
                    "size_delta": len(str(after)) - len(str(before))
                }
            }
        }
```

### Integration Pattern for Formatters

```python
class MarkdownFormatter(FormatterPlugin):
    def format(self, response_data, format_type):
        # Capture before state
        before = {
            "type": type(response_data).__name__,
            "keys": list(response_data.keys()) if isinstance(response_data, dict) else [],
            "size": len(str(response_data))
        }
        
        # Perform formatting
        formatted = self._to_markdown(response_data)
        
        # Log detailed changes
        state.transition(QueryState.FORMATTING, "markdown_applied", {
            "formatter": self.__class__.__name__,
            "format_type": format_type,
            "input": before,
            "output": {
                "type": "str",
                "size": len(formatted)
            },
            "changes": {
                "added": {"markdown_content": {"size": len(formatted)}},
                "removed": {"response_dict": before},
                "modified": {"structure": {"from": before["type"], "to": "str"}}
            }
        })
        
        return formatted
```

### Example: Complete Query Trace (With Changes)

```
Query: "What is the pipeline system?"
Query ID: q_abc123def456

=== STATE TRANSITIONS ===

[1] QUERY_RECEIVED
    Data: {query: "What is the pipeline system?", domain: "exframe"}

[2] ROUTING_SELECTION
    Changes: +selected_specialist: "ExFrameSpecialist"

[3] SINGLE_SPECIALIST_PROCESSING  
    Changes: +search_results: {count: 2, sources: ["README.md", "PLUGIN_ARCHITECTURE.md"]}

[4] OUT_OF_SCOPE_CHECK
    Data: {out_of_scope: false}

[5] ENRICHMENT_PIPELINE (RelatedPatternEnricher)
    Changes: +related_patterns: {count: 2}
            response: 850 → 1050 bytes (+200)

[6] ENRICHMENT_PIPELINE (LLMEnricher)
    Data: {confirmation_required: true}
    Changes: +llm_suggestion: "patterns_weak, would_use_llm"
            response: "has_patterns" → "awaiting_confirmation"

[7] AWAITING_CONFIRMATION
    (User re-queries with llm_confirmed=true)

[8] LLM_PROCESSING
    Changes: +llm_call: {model: "claude-sonnet-4", tokens: 1450}
            +sources_cited: {count: 5}
            -awaiting_confirmation: "user_confirmed"

[9] LLM_POST_PROCESSING
    Data: {llm_used: true}
    Changes: -raw_answer: "cleaned_up_for_display"

[10] FORMATTING_PHASE (MarkdownFormatter)
    Changes: +markdown_content: 2800 chars
            -response_dict: "converted_to_string"

[11] COMPLETE
    Total duration: 4502ms
```

### Benefits of Detailed Change Tracking

1. **Debugging**: See exactly what each component changed
2. **Performance**: Identify slow enrichers/formatters
3. **Trust**: Verify system is working as expected
4. **Bug Detection**: Spot anomalies (e.g., enricher that removes data)
5. **Compliance**: Audit trail of what happened to user query

### Implementation Note

This level of detail (Option B) is achievable because:
- Enrichers already know what they changed
- Formatters already know the before/after states
- We're just capturing what they already know
- No semantic analysis required - just structured logging

---

