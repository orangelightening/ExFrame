Core Principle
One log, multiple consumers:

State machine events → structured log
Trace system → reads from same log
Debugging → queries the log
AI bug finder → analyzes the log


State Machine Schema
pythonclass QueryState(Enum):
    RECEIVED = "RECEIVED"
    ROUTING = "ROUTING"
    SPECIALIST_PROCESSING = "SPECIALIST_PROCESSING"
    CONTEXT_READY = "CONTEXT_READY"
    ENRICHMENT = "ENRICHMENT"
    FORMATTING = "FORMATTING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"

class StateTransition:
    query_id: str
    from_state: QueryState | None  # None for initial state
    to_state: QueryState
    trigger: str  # What caused this transition
    timestamp: datetime
    data: dict  # State-specific data
    duration_ms: int | None  # Time in previous state

Event Log Format
Single JSONL file: /app/logs/state_machine.jsonl
jsonl{"query_id":"q_20260130_152301_abc","from_state":null,"to_state":"RECEIVED","trigger":"api_request","timestamp":"2026-01-30T15:23:01.234Z","data":{"query":"How do I create a domain?","domain":"exframe"},"duration_ms":null}

{"query_id":"q_20260130_152301_abc","from_state":"RECEIVED","to_state":"ROUTING","trigger":"query_parsed","timestamp":"2026-01-30T15:23:01.245Z","data":{"specialists_available":3},"duration_ms":11}

{"query_id":"q_20260130_152301_abc","from_state":"ROUTING","to_state":"SPECIALIST_PROCESSING","trigger":"specialist_selected","timestamp":"2026-01-30T15:23:01.256Z","data":{"specialist":"ExFrameSpecialist","confidence":0.85},"duration_ms":11}

{"query_id":"q_20260130_152301_abc","from_state":"SPECIALIST_PROCESSING","to_state":"CONTEXT_READY","trigger":"search_complete","timestamp":"2026-01-30T15:23:01.567Z","data":{"documents_found":3,"context_size":1250,"out_of_scope":false},"duration_ms":311}

{"query_id":"q_20260130_152301_abc","from_state":"CONTEXT_READY","to_state":"ENRICHMENT","trigger":"enricher_started","timestamp":"2026-01-30T15:23:01.789Z","data":{"enricher":"LLMEnricher","input_size":1250},"duration_ms":222}

{"query_id":"q_20260130_152301_abc","from_state":"ENRICHMENT","to_state":"ENRICHMENT","trigger":"llm_call","timestamp":"2026-01-30T15:23:01.890Z","data":{"model":"claude-sonnet-4","prompt_tokens":1300,"context_provided":true},"duration_ms":101}

{"query_id":"q_20260130_152301_abc","from_state":"ENRICHMENT","to_state":"FORMATTING","trigger":"enrichment_complete","timestamp":"2026-01-30T15:23:02.012Z","data":{"enricher":"LLMEnricher","output_size":450,"llm_called":true},"duration_ms":122}

{"query_id":"q_20260130_152301_abc","from_state":"FORMATTING","to_state":"COMPLETE","trigger":"response_ready","timestamp":"2026-01-30T15:23:02.123Z","data":{"total_duration_ms":889,"response_size":450},"duration_ms":111}

Bug Case (Empty Context)
jsonl{"query_id":"q_bug_xyz","from_state":"SPECIALIST_PROCESSING","to_state":"CONTEXT_READY","trigger":"search_complete","timestamp":"2026-01-30T15:23:01.567Z","data":{"documents_found":0,"context_size":0,"out_of_scope":false},"duration_ms":311}

{"query_id":"q_bug_xyz","from_state":"CONTEXT_READY","to_state":"ENRICHMENT","trigger":"enricher_started","timestamp":"2026-01-30T15:23:01.789Z","data":{"enricher":"LLMEnricher","input_size":0},"duration_ms":222}

{"query_id":"q_bug_xyz","from_state":"ENRICHMENT","to_state":"ENRICHMENT","trigger":"llm_call","timestamp":"2026-01-30T15:23:01.890Z","data":{"model":"claude-sonnet-4","prompt_tokens":150,"context_provided":false},"duration_ms":101}

{"query_id":"q_bug_xyz","from_state":"ENRICHMENT","to_state":"ERROR","trigger":"hallucination_detected","timestamp":"2026-01-30T15:23:02.012Z","data":{"error":"LLM called with empty context","enricher":"LLMEnricher"},"duration_ms":122}
Pattern visible: context_size:0 → llm_call → ERROR

Implementation
State Machine Logger
pythonimport json
from datetime import datetime
from enum import Enum
from pathlib import Path

class QueryStateMachine:
    def __init__(self, query_id: str):
        self.query_id = query_id
        self.current_state = None
        self.state_entered_at = None
        self.log_path = Path("/app/logs/state_machine.jsonl")
        
    def transition(self, to_state: QueryState, trigger: str, data: dict = None):
        """Log state transition"""
        now = datetime.now()
        
        # Calculate duration in previous state
        duration_ms = None
        if self.state_entered_at:
            duration_ms = int((now - self.state_entered_at).total_seconds() * 1000)
        
        # Create event
        event = {
            "query_id": self.query_id,
            "from_state": self.current_state.value if self.current_state else None,
            "to_state": to_state.value,
            "trigger": trigger,
            "timestamp": now.isoformat(),
            "data": data or {},
            "duration_ms": duration_ms
        }
        
        # Write to log (append)
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Update state
        self.current_state = to_state
        self.state_entered_at = now
        
        return event
    
    def error(self, trigger: str, data: dict):
        """Transition to ERROR state"""
        return self.transition(QueryState.ERROR, trigger, data)

Integration into Query Engine
pythondef process_query(query: str, domain: str, trace: bool = False):
    """Process query through pipeline with state machine logging"""
    
    # Generate unique query ID
    query_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Initialize state machine
    sm = QueryStateMachine(query_id)
    
    try:
        # STATE: RECEIVED
        sm.transition(QueryState.RECEIVED, "api_request", {
            "query": query,
            "domain": domain,
            "trace_enabled": trace
        })
        
        # STATE: ROUTING
        sm.transition(QueryState.ROUTING, "query_parsed", {
            "specialists_available": len(get_specialists(domain))
        })
        
        specialist = select_specialist(query, domain)
        
        # STATE: SPECIALIST_PROCESSING
        sm.transition(QueryState.SPECIALIST_PROCESSING, "specialist_selected", {
            "specialist": specialist.name,
            "confidence": specialist.confidence
        })
        
        context = specialist.process(query)
        
        # STATE: CONTEXT_READY
        context_size = len(str(context.get('context', '')))
        documents_found = len(context.get('documents', []))
        out_of_scope = context.get('out_of_scope', False)
        
        sm.transition(QueryState.CONTEXT_READY, "search_complete", {
            "documents_found": documents_found,
            "context_size": context_size,
            "out_of_scope": out_of_scope
        })
        
        # GUARD: Check for bug condition
        if context_size == 0 and not out_of_scope:
            sm.error("invalid_state", {
                "error": "Context empty but out_of_scope=false",
                "specialist": specialist.name,
                "bug_condition": True
            })
            return {"error": "Invalid specialist response"}
        
        if out_of_scope:
            sm.transition(QueryState.COMPLETE, "out_of_scope_rejection", {
                "message": context.get('message', 'Out of scope')
            })
            return context
        
        # STATE: ENRICHMENT
        for enricher in get_enrichers(domain):
            sm.transition(QueryState.ENRICHMENT, "enricher_started", {
                "enricher": enricher.name,
                "input_size": len(str(context))
            })
            
            # GUARD: Prevent LLM call with empty context
            if isinstance(enricher, LLMEnricher) and len(str(context)) < 50:
                sm.error("empty_context_llm_call", {
                    "error": "LLM enricher received insufficient context",
                    "enricher": enricher.name,
                    "context_size": len(str(context)),
                    "bug_condition": True
                })
                return {"error": "Insufficient context for enrichment"}
            
            result = enricher.enrich(query, context)
            
            # Log LLM calls specifically
            if result.get('llm_called'):
                sm.transition(QueryState.ENRICHMENT, "llm_call", {
                    "model": result.get('model'),
                    "prompt_tokens": result.get('prompt_tokens'),
                    "context_provided": len(str(context)) > 0
                })
            
            sm.transition(QueryState.ENRICHMENT, "enrichment_complete", {
                "enricher": enricher.name,
                "output_size": len(str(result)),
                "llm_called": result.get('llm_called', False)
            })
            
            context = result
        
        # STATE: FORMATTING
        sm.transition(QueryState.FORMATTING, "formatter_started", {
            "format": request.format
        })
        
        formatted = format_response(context, request.format)
        
        # STATE: COMPLETE
        sm.transition(QueryState.COMPLETE, "response_ready", {
            "response_size": len(str(formatted))
        })
        
        # If trace requested, include state log
        if trace:
            formatted['trace'] = load_trace(query_id)
        
        return formatted
        
    except Exception as e:
        sm.error("exception", {
            "error": str(e),
            "exception_type": type(e).__name__
        })
        raise

Trace Endpoint (reads from state log)
pythondef load_trace(query_id: str) -> dict:
    """Load trace by reading state machine log"""
    
    events = []
    with open("/app/logs/state_machine.jsonl") as f:
        for line in f:
            event = json.loads(line)
            if event['query_id'] == query_id:
                events.append(event)
    
    # Transform into trace format
    return {
        "query_id": query_id,
        "states": events,
        "total_duration_ms": events[-1]['timestamp'] - events[0]['timestamp'] if events else 0,
        "final_state": events[-1]['to_state'] if events else None,
        "error_occurred": any(e['to_state'] == 'ERROR' for e in events)
    }

AI Bug Finder Queries
Feed the log to Claude:
pythondef find_bugs_with_ai():
    """Use LLM to analyze state machine log for bugs"""
    
    # Load recent logs
    with open("/app/logs/state_machine.jsonl") as f:
        recent_logs = f.readlines()[-1000:]  # Last 1000 events
    
    prompt = f"""
Analyze these query state machine logs for bug patterns.

Focus on:
1. LLM calls with context_size=0 or context_provided=false
2. Transitions to ERROR state
3. out_of_scope=false when documents_found=0
4. Unusual state sequences

Logs:
{chr(10).join(recent_logs)}

Identify bug patterns and suggest fixes.
"""
    
    analysis = llm.generate(prompt)
    return analysis
AI will find patterns like:

"I found 5 instances where CONTEXT_READY had context_size:0 but out_of_scope:false, followed by ENRICHMENT with llm_call. This suggests the specialist is failing to mark empty results as out_of_scope. Fix: Add guard in specialist or routing logic."


Query Analysis Tools
bash# Find all queries with bug condition
jq 'select(.data.bug_condition == true)' state_machine.jsonl

# Find queries that called LLM with no context
jq 'select(.trigger == "llm_call" and .data.context_provided == false)' state_machine.jsonl

# State transition frequency
jq -s 'group_by(.to_state) | map({state: .[0].to_state, count: length})' state_machine.jsonl

# Average duration per state
jq -s 'group_by(.to_state) | map({state: .[0].to_state, avg_ms: (map(.duration_ms // 0) | add / length)})' state_machine.jsonl

The Win
Single system does everything:
✅ State machine - Clear state model
✅ Trace - Reads from state log when requested
✅ Debugging - Query logs for patterns
✅ AI analysis - Feed logs to LLM to find bugs
✅ Reproducibility - Bug conditions captured in data field
No separate trace system. The state log IS the trace.

This is cleaner, simpler, and more powerful.
Want me to write the full implementation with guards for the empty context bug?I love state machines. What size is a leggings block.08:57Did you just have a stroke, or did autocorrect betray you spectacularly? 😄
I'm guessing you meant one of:

================================================================================
CRITIQUE / ANALYSIS / FEASIBILITY / PLANNING
================================================================================

## Critique of Proposed Design

### Strengths
✅ **Single Source of Truth**: One log file eliminates synchronization issues between multiple logging systems
✅ **Queryable Format**: JSONL is perfect for jq, Python, and LLM analysis
✅ **Explicit State Model**: Clear state transitions make pipeline behavior visible
✅ **Bug Pattern Detection**: The empty context example shows how bugs become obvious
✅ **Multiple Consumers**: Trace, debugging, and AI analysis all read same log

### Potential Issues
⚠️ **Sequential States**: The current model assumes linear progression (RECEIVED→ROUTING→PROCESSING), but:
   - Enrichment may loop (multiple enrichers in sequence)
   - LLM fallback may retry
   - The ENRICHMENT→ENRICHMENT self-transition in the example is actually correct
   - Suggestion: Allow self-transitions or add SUBSTATE field

⚠️ **Query ID Generation**: Timestamp-based IDs may collide under high load
   - Suggestion: Use UUID v4 or ULID for guaranteed uniqueness

⚠️ **File Write Performance**: Synchronous file I/O on every transition could bottleneck
   - Suggestion: Use async logging or buffer writes

⚠️ **Log Rotation**: Single file grows indefinitely
   - Suggestion: Daily rotation: `state_machine-YYYY-MM-DD.jsonl`

⚠️ **Missing States**: Based on codebase exploration, add:
   - SEARCHING (knowledge base search phase)
   - out_of_scope handling needs explicit state path

## Feasibility Analysis

### Complexity: MEDIUM
- **New Code Required**: ~300-500 lines
- **Files to Modify**: 4-6 core files
- **Breaking Changes**: None (additive feature)
- **Testing Required**: Medium (state transitions, error paths)

### Current Codebase Compatibility
✅ **Existing Foundation**: 
  - `assist/engine.py` already has trace logging infrastructure
  - `SearchTrace` class (diagnostics/search_metrics.py) can be extended
  - `UniverseState` enum pattern already exists in codebase

❌ **Gaps to Fill**:
  - No centralized state machine currently
  - Current trace logs are unstructured text
  - No correlation between trace entries for same query

### Implementation Touch Points

**Primary Files:**
1. `generic_framework/assist/engine.py:101-469` - Main query orchestrator
2. `generic_framework/core/generic_domain.py:403-654` - Enrichment and formatting
3. `generic_framework/core/router_plugin.py:74-91` - Routing logic
4. `generic_framework/diagnostics/search_metrics.py:42-93` - Search tracing

**Minimal Integration Approach:**
- Add state_machine.py module (new file)
- Inject state machine instance into engine.py via dependency injection
- Wrap existing processing steps with state.transition() calls
- No changes to specialist/enricher interfaces required

## Implementation Plan

### Phase 1: Core State Machine (1-2 days)
**File**: `generic_framework/state/state_machine.py`

```python
# Requirements
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import json
import uuid

class QueryState(Enum):
    RECEIVED = "RECEIVED"
    ROUTING = "ROUTING"
    SEARCHING = "SEARCHING"
    SPECIALIST_PROCESSING = "SPECIALIST_PROCESSING"
    CONTEXT_READY = "CONTEXT_READY"
    ENRICHMENT = "ENRICHMENT"
    FORMATTING = "FORMATTING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"

class QueryStateMachine:
    """State machine logger for query pipeline events."""
    
    def __init__(self, query_id: Optional[str] = None):
        self.query_id = query_id or self._generate_id()
        self.current_state: Optional[QueryState] = None
        self.state_entered_at: Optional[datetime] = None
        self.log_path = Path("/app/logs/traces/state_machine.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def _generate_id() -> str:
        """Generate unique query ID using UUID."""
        return f"q_{uuid.uuid4().hex[:12]}"
    
    def transition(self, to_state: QueryState, trigger: str, 
                   data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log state transition and return event data."""
        now = datetime.utcnow()
        
        # Calculate duration
        duration_ms = None
        if self.state_entered_at:
            duration_ms = int((now - self.state_entered_at).total_seconds() * 1000)
        
        # Create event
        event = {
            "query_id": self.query_id,
            "from_state": self.current_state.value if self.current_state else None,
            "to_state": to_state.value,
            "trigger": trigger,
            "timestamp": now.isoformat() + "Z",
            "data": data or {},
            "duration_ms": duration_ms
        }
        
        # Async write (don't block pipeline)
        self._write_event(event)
        
        # Update state
        self.current_state = to_state
        self.state_entered_at = now
        
        return event
    
    def _write_event(self, event: Dict[str, Any]) -> None:
        """Write event to log file."""
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            # Don't fail query if logging fails
            print(f"State machine logging error: {e}")
    
    def error(self, trigger: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Transition to ERROR state."""
        return self.transition(QueryState.ERROR, trigger, data)
    
    def complete(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Transition to COMPLETE state."""
        return self.transition(QueryState.COMPLETE, "query_complete", data)
```

### Phase 2: Integration into Query Engine (2-3 days)
**File**: `generic_framework/assist/engine.py`

Key integration points:
- Line 101: Initialize state_machine in `process_query()`
- Line 147: Log ROUTING state when selecting specialist
- Line 173: Log SEARCHING state during knowledge base search
- Line 208: Log SPECIALIST_PROCESSING state
- Line 274: Log ENRICHMENT state (may repeat for multiple enrichers)
- Line 369: Log FORMATTING state
- Line 406: Log COMPLETE state
- Wrap error handlers to call `sm.error()`

### Phase 3: Trace Consumer (1 day)
**File**: `generic_framework/api/app.py`

Add endpoint to retrieve state machine log:
```python
@app.get("/api/query/{query_id}/trace")
async def get_query_trace(query_id: str):
    """Return state machine log for query."""
    events = []
    try:
        with open("logs/traces/state_machine.jsonl") as f:
            for line in f:
                event = json.loads(line)
                if event['query_id'] == query_id:
                    events.append(event)
        return {"query_id": query_id, "events": events}
    except FileNotFoundError:
        raise HTTPException(404, f"Query {query_id} not found")
```

### Phase 4: AI Bug Finder (2-3 days)
**New File**: `generic_framework/diagnostics/state_analyzer.py`

Implement periodic analysis that:
1. Reads last N events from state_machine.jsonl
2. Identifies bug patterns (empty context, ERROR states, unusual sequences)
3. Feeds to LLM for analysis
4. Stores findings in `logs/diagnostics/bugs.json`

### Phase 5: Enhancements (Optional)
- State visualization dashboard
- Real-time state streaming via WebSocket
- Performance metrics aggregation
- Alert system for repeated error patterns

## Code Example: Full Integration

See next section for complete working example integrated into GenericAssistantEngine.

================================================================================
