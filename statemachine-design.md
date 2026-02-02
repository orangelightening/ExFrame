# ExFrame State Machine Design Document

**Version:** 2.0 (Consolidated)
**Date:** 2026-01-31
**Status:** Implemented
**Author:** ExFrame Architecture Team

---

## Executive Summary

This document defines a consolidated state machine logging system for ExFrame that provides complete observability of the query-response lifecycle with minimal overhead.

**Core Design Principle:** Each state represents substantive work, not just logging markers.

**Consolidation:** Reduced from 16 states to 6 core states by eliminating pure marker states that only logged metadata without doing actual work.

---

## Table of Contents

1. [State Machine Overview](#state-machine-overview)
2. [State Definitions](#state-definitions)
3. [State Transitions](#state-transitions)
4. [Data Schema](#data-schema)
5. [Implementation Status](#implementation-status)

---

## State Machine Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Consolidated Query Lifecycle                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │ QUERY_RECEIVED│  Entry: API/WebSocket/Direct                      │
│  └──────┬───────┘  Includes direct prompt check                      │
│         │                                                           │
│    ┌────┴────┐                                                       │
│    │         │                                                       │
│ [Direct]   [Normal]                                                 │
│ [// prefix]                                                          │
│    │         │                                                       │
│    ▼         ▼                                                       │
│  ┌──────────┐  ┌──────────────────┐                                │
│  │ DIRECT_  │  │ ROUTING_         │                                │
│  │   LLM    │  │ SELECTION        │  Specialist scoring + selection  │
│  └────┬─────┘  └──────┬───────────┘                                │
│       │              │                                               │
│       │              ▼                                               │
│       │       ┌──────────────────┐                                 │
│       │       │ SPECIALIST_      │  Search + pattern aggregation +   │
│       │       │ PROCESSING       │  response generation              │
│       │       └──────┬───────────┘                                 │
│       │              │                                               │
│       │              ▼                                               │
│       │       ┌──────────────────┐                                 │
│       │       │ ENRICHERS_       │  LLM fallback/enhancement +       │
│       │       │ EXECUTED         │  enrichment                      │
│       │       └──────┬───────────┘                                 │
│       │              │                                               │
│       └──────┬───────┘                                               │
│              │                                                       │
│              ▼                                                       │
│       ┌──────────────┐                                              │
│       │   COMPLETE   │  Response return included                     │
│       └──────────────┘                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Error Handling

```
[any state] ──[error]──> ERROR ──> LOG_AND_EXIT (for out-of-scope rejection)
```

---

## State Definitions

### Consolidated QueryState Enum

```python
class QueryState(Enum):
    """Consolidated query lifecycle states.

    Design principle: Each state represents substantive work, not just logging markers.
    Reduced from 16 to 6 core states for minimal overhead while maintaining observability.
    """

    # Entry States
    QUERY_RECEIVED = "QUERY_RECEIVED"  # Query received, direct prompt check included
    DIRECT_LLM = "DIRECT_LLM"          # Direct LLM bypass (// prefix)

    # Processing States (where real work happens)
    ROUTING_SELECTION = "ROUTING_SELECTION"  # Specialist scoring and selection
    SPECIALIST_PROCESSING = "SPECIALIST_PROCESSING"  # Specialist search + response generation
    ENRICHERS_EXECUTED = "ENRICHERS_EXECUTED"  # Enrichers executed (LLM calls)

    # Terminal States
    COMPLETE = "COMPLETE"     # Query complete, includes response return
    ERROR = "ERROR"           # Error occurred
    LOG_AND_EXIT = "LOG_AND_EXIT"  # Early exit (e.g., out of scope)
```

### State Descriptions

| State | Description | What Work Is Done |
|-------|-------------|-------------------|
| `QUERY_RECEIVED` | Query entered system | Parse query, check for // prefix, log metadata |
| `DIRECT_LLM` | Direct LLM bypass | Bypass specialist/search, call LLM directly |
| `ROUTING_SELECTION` | Select specialist | Score all specialists against query, select winner |
| `SPECIALIST_PROCESSING` | Specialist processes query | Pattern search, aggregation, response generation |
| `ENRICHERS_EXECUTED` | Enrichers executed | LLM fallback/enhancement, quality scoring |
| `COMPLETE` | Query complete | Final summary, response returned to client |
| `ERROR` | Error occurred | Log error details |
| `LOG_AND_EXIT` | Early exit | Handle out-of-scope rejection |

---

## State Transitions

### Normal Query Flow (Single Specialist)

```
QUERY_RECEIVED (includes direct prompt check)
  └─→ ROUTING_SELECTION (specialist scoring + selection)
       └─→ SPECIALIST_PROCESSING (search + response generation)
            └─→ ENRICHERS_EXECUTED (LLM/enrichment)
                 └─→ COMPLETE (response returned)
```

**Total states: 5** (down from 15)

### Direct Prompt Flow (// prefix)

```
QUERY_RECEIVED (direct_prompt=true)
  └─→ DIRECT_LLM
       └─→ COMPLETE
```

**Total states: 3** (down from 6)

### Out of Scope Rejection

```
SPECIALIST_PROCESSING
  └─→ LOG_AND_EXIT (out_of_scope=true)
```

### Error Transitions

```
[any state] ──[error]──> ERROR
```

---

## Data Schema

### State Event Schema

```json
{
  "query_id": "q_a1b2c3d4e5f6",
  "from_state": "ROUTING_SELECTION",
  "to_state": "SPECIALIST_PROCESSING",
  "trigger": "specialist_selected",
  "timestamp": "2026-01-31T01:23:45.123456Z",
  "data": {
    "specialist_id": "exframe_specialist",
    "specialist_name": "ExFrame Knowledge Specialist",
    "specialist_scores": [...]
  },
  "duration_ms": 15,
  "metadata": {
    "domain": "exframe",
    "verbose": false
  }
}
```

### Data Dictionary by State

| State | Data Fields |
|-------|-------------|
| `QUERY_RECEIVED` | `query`, `original_query`, `include_trace`, `direct_prompt` |
| `ROUTING_SELECTION` | `specialists_available`, `selected_specialist`, `specialist_name`, `specialist_scores` |
| `SPECIALIST_PROCESSING` | `specialist`, `specialist_name` (or `patterns_found` for general) |
| `ENRICHERS_EXECUTED` | `enricher`, `input_size`, `output_size`, `duration_ms`, `changes` |
| `COMPLETE` | `query_id`, `processing_time_ms`, `llm_used`, `confidence`, `patterns_found`, `response_size`, `ai_generated` |
| `DIRECT_LLM` | `model`, `endpoint` |
| `ERROR` | `error_type`, `error_message` |
| `LOG_AND_EXIT` | `reason`, `specialist` |

---

## Implementation Status

### Consolidation Summary

| Before (16 states) | After (6 states) | Action |
|-------------------|------------------|--------|
| `QUERY_RECEIVED` | `QUERY_RECEIVED` | ✅ Keep (merged direct_prompt_check) |
| `DIRECT_PROMPT_CHECK` | - | ❌ Eliminated (merged into QUERY_RECEIVED) |
| `DIRECT_LLM` | `DIRECT_LLM` | ✅ Keep |
| `DIRECT_LLM_COMPLETE` | - | ❌ Eliminated (go straight to COMPLETE) |
| `ROUTING_SELECTION` | `ROUTING_SELECTION` | ✅ Keep (merged SPECIALIST_SELECTED) |
| `SPECIALIST_SELECTED` | - | ❌ Eliminated (merged into ROUTING_SELECTION) |
| `SEARCHING` | - | ❌ Eliminated (marker only) |
| `SINGLE_SPECIALIST_PROCESSING` | `SPECIALIST_PROCESSING` | ✅ Keep (renamed) |
| `MULTI_SPECIALIST_PROCESSING` | - | ❌ Eliminated (not used) |
| `RESPONSE_AGGREGATION` | - | ❌ Eliminated (not used) |
| `CONTEXT_READY` | - | ❌ Eliminated (marker only) |
| `OUT_OF_SCOPE_CHECK` | - | ❌ Eliminated (inline check) |
| `ENRICHMENT_PIPELINE` | - | ❌ Eliminated (marker only) |
| `ENRICHERS_EXECUTED` | `ENRICHERS_EXECUTED` | ✅ Keep |
| `LLM_CONFIRMATION_CHECK` | - | ❌ Eliminated (inline in enrichers) |
| `AWAITING_CONFIRMATION` | - | ❌ Eliminated (not used) |
| `LLM_PROCESSING` | - | ❌ Eliminated (logging only) |
| `LLM_POST_PROCESSING` | - | ❌ Eliminated (marker only) |
| `ENRICHMENT_COMPLETE` | - | ❌ Eliminated (marker only) |
| `FORMATTING_PHASE` | - | ❌ Eliminated (not used) |
| `RESPONSE_CONSTRUCTION` | - | ❌ Eliminated (logging only) |
| `LOG_AND_EXIT` | `LOG_AND_EXIT` | ✅ Keep |
| `COMPLETE` | `COMPLETE` | ✅ Keep (merged RESPONSE_RETURNED) |
| `ERROR` | `ERROR` | ✅ Keep |
| `RESPONSE_RETURNED` | - | ❌ Eliminated (merged into COMPLETE) |

### Files Modified

1. `generic_framework/state/state_machine.py` - Updated QueryState enum
2. `generic_framework/assist/engine.py` - Updated all state transitions
3. `statemachine-design.md` - This document (consolidated)
4. `tests/test_statemachine.py` - Updated test expectations (TODO)

### Expected Results

- **Simple query:** 5 states (down from 15)
- **Direct prompt:** 3 states (down from 6)
- **Overhead:** ~67% reduction in state transitions
- **Observability:** Maintained - all substantive work still tracked

---

## Design Rationale

### Why These 6 States?

1. **QUERY_RECEIVED** - Entry point, includes direct prompt check (simple string operation)
2. **ROUTING_SELECTION** - Specialist scoring is real work (iterates all specialists)
3. **SPECIALIST_PROCESSING** - Specialist does pattern search + response generation
4. **ENRICHERS_EXECUTED** - LLM call happens here (substantive work)
5. **COMPLETE** - Terminal state, includes response return
6. **ERROR/LOG_AND_EXIT** - Error handling

### What Was Eliminated?

- **Marker states** - States that only logged metadata without doing work
- **Duplicate states** - States that were essentially the same as their predecessor
- **Unused states** - States defined but never reached in actual flow
- **Simple check states** - States that only did a simple dict/string check

### Benefits

1. **Less overhead** - Fewer state transitions = less processing
2. **Clearer flow** - Each state represents actual work
3. **Easier debugging** - Fewer states to trace through
4. **Same observability** - All important operations still logged
