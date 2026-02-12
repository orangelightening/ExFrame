# TRACE SYSTEM FIX - PETER DOMAIN

## Problem
When `include_trace=true`, trace data shows empty in UI.
Root cause: `response.trace` field never populated in query responses.

## Current Flow
1. Frontend: `include_trace=true` → POST /api/query/phase1
2. query_processor: Calls `persona.respond()`
3. persona.respond(): Calls LLM, returns response dict
4. Response dict has `response.trace` (always empty!)

## Required Fix
**File:** `/home/peter/development/eeframe/generic_framework/core/persona.py`
**Method:** `persona.respond()` (line ~155)

**Change:** When `self.trace=True` AND LLM returns reasoning, populate `response['trace']` with structured steps.

## Implementation
After line 640 (`if self.trace:`):
```python
# Parse LLM response to extract reasoning/thinking
if self.trace and llm_response_text and "Always show" in llm_response_text:
    # Extract reasoning/thinking content
    reasoning = extract_reasoning(llm_response_text)
    if reasoning:
        response['trace'] = [{
            "step": f"Step 1: {len(response['trace']) + 1}",
            "action": reasoning_content,
            "timestamp": datetime.now().isoformat()
        }]
```

**Before returning response:**
```python
response['trace'] = [{
    "step": f"Step 1: {len(response['trace']) + 1}",
    "action": reasoning_content,
    "timestamp": datetime.now().isoformat()
}]
```

This populates `response.trace` with actual data from LLM reasoning.

## Test
Query with `include_trace=true` → Check traces tab → Should show reasoning steps
