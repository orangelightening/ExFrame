# Plugin Refactor Design Document
## State Machine Architecture: Rock-Solid Query Processing

> **⚠️ STATUS: DRAFT - NOT YET IMPLEMENTED**
>
> This is a design document for a future state machine refactor. The current system uses the plugin architecture documented in PLUGIN_ARCHITECTURE.md. This refactor has many open questions and is not scheduled for immediate implementation.

**Status**: Design Draft v2
**Created**: 2026-02-02
**Author**: Claude (with user input)
**Target**: 4 releases over 4-6 weeks

---

## Executive Summary

**Problem**: Current plugin system has become unmanageable. LLMEnricher is 700+ lines of conditional logic. Domain types are strings, not behaviors. Configuration is scattered across multiple files. Query flow is implicit and hard to debug.

**Solution**: **State Machine Architecture**. The entire query processing system is built as a proper state machine with nodes, edges, and triggers. Every transition is logged, verified, and 100% reliable.

**Key Principle**: **The State Machine is the source of truth. All logging, debugging, and monitoring flows from it.**

**Core Requirements**:
- **Rock Solid**: State transitions must be deterministic and verifiable
- **Observable**: Every state change is logged with context
- **Debuggable**: State machine trace directly maps to logs
- **Testable**: Every transition can be unit tested

---

## Core Architecture: State Machine First

```
┌─────────────────────────────────────────────────────────────┐
│                  QUERY PROCESSING STATE MACHINE                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │ START   │───→│ ROUTING │───→│ EXECUTE │                │
│   │         │    │         │    │         │                │
│   │  Query  │    │ Select  │    │ Domain  │                │
│   │ Received│    │ Specialist│    │ Type N  │                │
│   └─────────┘    └─────────┘    └────┬────┘                │
│                               │                          │
│                    ┌─────────────┴─────────────┐            │
│                    │     STATE TRANSITIONS      │            │
│                    │  (Explicit, Verifiable)    │            │
│                    │                            │            │
│                    │  trigger: query_received     │            │
│                    │  trigger: specialist_selected │            │
│                    │  trigger: local_search_done   │            │
│                    │  trigger: web_search_done    │            │
│                    │  trigger: llm_complete       │            │
│                    └────────────────────────────┘            │
│                               │                          │
│                    ┌─────────────┴─────────────┐            │
│                    │   LOGGING & TRACING        │            │
│                    │   (Automatic, Complete)     │            │
│                    │                            │            │
│                    │  - State entry/exit         │            │
│                    │  - Transition context       │            │
│                    │  - Duration                 │            │
│                    │  - Data snapshots (optional) │            │
│                    └────────────────────────────┘            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## State Machine: The Source of Truth

```python
# core/state_machine/query_sm.py

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod


class QueryState(Enum):
    """All possible states in query processing"""

    # Initial state
    START = "start"

    # Routing
    ROUTING_SELECT_SPECIALIST = "routing_select_specialist"

    # Domain Type states (each type has its own flow)
    TYPE4_LOCAL_SEARCH = "type4_local_search"
    TYPE4_REQUEST_WEB_SEARCH = "type4_request_web_search"
    TYPE4_WEB_SEARCH = "type4_web_search"
    TYPE4_LLM_SYNTHESIS = "type4_llm_synthesis"

    TYPE3_DOCUMENT_SEARCH = "type3_document_search"
    TYPE3_LLM_SYNTHESIS = "type3_llm_synthesis"

    TYPE1_PATTERN_SEARCH = "type1_pattern_search"

    # Common states
    ENRICHERS_EXECUTE = "enrichers_execute"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class StateContext:
    """Context data attached to state transitions"""
    query_id: str
    timestamp: datetime
    state: QueryState
    trigger: str
    data: Dict[str, Any]  # Any data relevant to this state

    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp.isoformat(),
            "state": self.state.value,
            "trigger": self.trigger,
            "data": self.data
        }


class StateTransition:
    """A state transition with validation"""

    def __init__(
        self,
        from_state: QueryState,
        to_state: QueryState,
        trigger: str,
        validator: Callable[[], bool] = None
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.trigger = trigger
        self.validator = validator or (lambda: True)

    def is_valid(self) -> bool:
        """Check if transition is valid"""
        return self.validator()


class QueryStateMachine:
    """
    Rock-solid state machine for query processing.

    Every transition is:
    - Explicitly defined
    - Logged with context
    - Verifiable and testable
    """

    def __init__(self, domain_type: str, query: str, verbose: bool = False):
        self.domain_type = domain_type
        self.query = query
        self.verbose = verbose

        self.current_state = QueryState.START
        self.query_id = self._generate_query_id()

        # State transitions: (from_state, trigger) -> to_state
        self.transitions = self._build_transitions()

        # State log: all transitions in order
        self.state_log: List[StateContext] = []

        # Hooks for logging/monitoring (Release 4)
        self.hooks: List[StateMachineHook] = []

    def _generate_query_id(self) -> str:
        """Generate unique query ID"""
        import uuid
        return f"q_{uuid.uuid4().hex[:12]}"

    def _build_transitions(self) -> Dict[Tuple[QueryState, str], StateTransition]:
        """
        Build state transition graph.

        Returns: {(from_state, trigger) -> StateTransition}
        """
        # Base transitions (all domain types)
        transitions = {
            (QueryState.START, "query_received"): StateTransition(
                QueryState.START,
                QueryState.ROUTING_SELECT_SPECIALIST,
                "query_received"
            ),

            (QueryState.ROUTING_SELECT_SPECIALIST, "specialist_selected"): StateTransition(
                QueryState.ROUTING_SELECT_SPECIALIST,
                QueryState.ENRICHERS_EXECUTE,  # Go to enrichers first
                "specialist_selected"
            ),

            (QueryState.ENRICHERS_EXECUTE, "enrichment_complete"): StateTransition(
                QueryState.ENRICHERS_EXECUTE,
                QueryState.COMPLETE,
                "enrichment_complete"
            ),
        }

        # Add domain-type specific transitions
        if self.domain_type == "4":
            transitions.update({
                (QueryState.ENRICHERS_EXECUTE, "type4_local_search"): StateTransition(
                    QueryState.ENRICHERS_EXECUTE,
                    QueryState.TYPE4_LOCAL_SEARCH,
                    "type4_local_search",
                    validator=lambda: self._can_do_local_search()
                ),

                (QueryState.TYPE4_LOCAL_SEARCH, "search_complete"): StateTransition(
                    QueryState.TYPE4_LOCAL_SEARCH,
                    QueryState.TYPE4_REQUEST_WEB_SEARCH,
                    "search_complete"
                ),

                (QueryState.TYPE4_REQUEST_WEB_SEARCH, "user_confirmed_web"): StateTransition(
                    QueryState.TYPE4_REQUEST_WEB_SEARCH,
                    QueryState.TYPE4_WEB_SEARCH,
                    "user_confirmed_web"
                ),

                (QueryState.TYPE4_WEB_SEARCH, "search_complete"): StateTransition(
                    QueryState.TYPE4_WEB_SEARCH,
                    QueryState.TYPE4_LLM_SYNTHESIS,
                    "search_complete"
                ),

                (QueryState.TYPE4_LLM_SYNTHESIS, "llm_complete"): StateTransition(
                    QueryState.TYPE4_LLM_SYNTHESIS,
                    QueryState.COMPLETE,
                    "llm_complete"
                ),
            })

        return transitions

    def transition_to(self, to_state: QueryState, trigger: str, data: Dict = None) -> bool:
        """
        Transition to a new state.

        Returns: True if transition succeeded, False otherwise
        """
        transition_key = (self.current_state, trigger)

        if transition_key not in self.transitions:
            self._log_error(f"Invalid transition: {self.current_state} --[{trigger}]--> {to_state}")
            self.current_state = QueryState.ERROR
            self._log_state(QueryState.ERROR, "invalid_transition", {"attempted_state": to_state.value})
            return False

        transition = self.transitions[transition_key]

        if transition.to_state != to_state:
            self._log_error(f"State mismatch: transition leads to {transition.to_state.value}, tried to go to {to_state.value}")
            self.current_state = QueryState.ERROR
            return False

        if not transition.is_valid():
            self._log_error(f"Transition validator failed: {self.current_state} --[{trigger}]--> {to_state}")
            self.current_state = QueryState.ERROR
            return False

        # Execute transition
        old_state = self.current_state
        self.current_state = to_state
        self._log_state(to_state, trigger, data or {})

        # Call hooks (Release 4)
        for hook in self.hooks:
            hook.on_transition(old_state, to_state, trigger, data or {})

        return True

    def _log_state(self, state: QueryState, trigger: str, data: Dict):
        """Log state entry"""
        context = StateContext(
            query_id=self.query_id,
            timestamp=datetime.utcnow(),
            state=state,
            trigger=trigger,
            data=data
        )
        self.state_log.append(context)

        # Also log to file (for persistence)
        self._persist_log(context)

    def _log_error(self, message: str):
        """Log error state"""
        import logging
        logger = logging.getLogger("state_machine")
        logger.error(f"[{self.query_id}] {message}")

    def _persist_log(self, context: StateContext):
        """Persist state log to file"""
        import json
        import pathlib

        log_dir = pathlib.Path("/app/logs/traces")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "state_machine.jsonl"

        with open(log_file, "a") as f:
            f.write(json.dumps(context.to_dict()) + "\n")

    # Domain-type specific validators
    def _can_do_local_search(self) -> bool:
        """Check if we can do local search"""
        return True  # Always can try local search
```

---

## Type 4 State Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      TYPE 4 STATE FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────┐   ┌──────────┐                                       │
│  │  START  │──→│ ROUTING   │                                       │
│  │         │   │          │──→ Select Domain Type Handler         │
│  └────────┘   └────┬─────┘                                       │
│                   │                                              │
│                   ▼                                              │
│        ┌──────────────────────┐                                   │
│        │ TYPE4_LOCAL_SEARCH  │ ◄── Domain-specific state          │
│        │                      │                                   │
│        │ trigger: search_done │                                   │
│        │ result: insufficient │                                   │
│        └──────┬───────────────┘                                   │
│                   │                                              │
│                   ▼                                              │
│        ┌──────────────────────┐                                   │
│        │ TYPE4_REQUEST_WEB   │ (if local insufficient)            │
│        │                      │                                   │
│        │ trigger: user_confirm│                                   │
│        └──────┬───────────────┘                                   │
│                   │                                              │
│                   ▼                                              │
│        ┌──────────────────────┐                                   │
│        │ TYPE4_WEB_SEARCH     │                                   │
│        │                      │                                   │
│        │ trigger: search_done │                                   │
│        └──────┬───────────────┘                                   │
│                   │                                              │
│                   ▼                                              │
│        ┌──────────────────────┐                                   │
│        │ TYPE4_LLM_SYNTHESIS  │                                   │
│        │                      │                                   │
│        │ trigger: llm_done    │                                   │
│        └──────┬───────────────┘                                   │
│                   │                                              │
│                   ▼                                              │
│        ┌──────────────────────┐     ┌──────────────┐              │
│        │ ENRICHERS_EXECUTE    │ ───►│  COMPLETE    │              │
│        │ (optional enrichment)│     │              │              │
│        └──────────────────────┘     └──────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## How State Machine Maps to Logging

Every state transition creates a log entry:

```json
{
  "query_id": "q_ab8d60ebd367",
  "timestamp": "2026-02-02T21:30:15.123456Z",
  "state": "type4_local_search",
  "trigger": "search_complete",
  "data": {
    "results_count": 10,
    "max_relevance": 0.3,
    "sufficient": false,
    "reason": "low_relevance"
  }
}
```

The trace log becomes **the story of the query** - each entry is a chapter in order.

---

## Domain Types Are State Handlers

```python
# domain_types/type4_analytic.py

class Type4AnalyticDomain:
    """
    Type 4: Analytical Engine

    Domain types ARE state handlers. They implement the
    domain-type-specific state transitions and logic.
    """

    domain_type_id = "4"
    name = "Analytic Engine"
    description = "Web search with local fallback"

    async def process_query(
        self,
        query: str,
        context: QueryContext
    ) -> QueryResult:
        """
        Entry point - all Type 4 queries flow through here.

        This method runs the state machine for Type 4 queries.
        """
        sm = QueryStateMachine("4", query, context.verbose)
        sm.add_hook(StateMachineLoggerHook())

        # Initial state
        sm.transition_to(QueryState.START, "query_received", {"query": query})

        # Routing
        specialist = self._select_specialist(query)
        sm.transition_to(
            QueryState.ROUTING_SELECT_SPECIALIST,
            "specialist_selected",
            {"specialist": specialist.specialist_id}
        )

        # Enrichers (prepare context)
        enriched_context = await self._prepare_enrichers(query, context)
        sm.transition_to(
            QueryState.ENRICHERS_EXECUTE,
            "enrichers_prepared",
            {"context": enriched_context}
        )

        # Type 4 specific flow
        if context.web_search_confirmed:
            # User confirmed web search - go straight to web
            return await self._web_search_flow(sm, query, context)
        else:
            # Standard Type 4 flow with local search first
            return await self._standard_flow(sm, query, context)

    async def _standard_flow(
        self,
        sm: QueryStateMachine,
        query: str,
        context: QueryContext
    ) -> QueryResult:
        """Standard Type 4 flow: local search → check → optionally web search"""

        # Local search
        sm.transition_to(
            QueryState.TYPE4_LOCAL_SEARCH,
            "local_search_start",
            {"query": query}
        )

        local_results = await self._search_local(query)
        sm.transition_to(
            QueryState.TYPE4_LOCAL_SEARCH,
            "search_complete",
            {
                "results_count": len(local_results),
                "max_relevance": self._max_relevance(local_results),
                "sufficient": self._is_local_sufficient(local_results)
            }
        )

        # Check if local results are sufficient
        if self._is_local_sufficient(local_results):
            # Good local results - use them
            return await self._use_local_results(sm, local_results, context)

        # Not sufficient - request web search
        sm.transition_to(
            QueryState.TYPE4_REQUEST_WEB_SEARCH,
            "local_insufficient",
            {
                "local_results_count": len(local_results),
                "max_relevance": self._max_relevance(local_results),
                "threshold": self.local_relevance_threshold
            }
        )

        # Return result requesting web search
        return QueryResult(
            answer=self._form_web_search_request(query, local_results),
            can_extend_with_web_search=True,
            local_results=local_results,
            confidence=self._calculate_confidence(local_results)
        )

    async def _web_search_flow(
        self,
        sm: QueryStateMachine,
        query: str,
        context: QueryContext
    ) -> QueryResult:
        """Web search flow (when user confirms)"""

        sm.transition_to(
            QueryState.TYPE4_WEB_SEARCH,
            "web_search_start",
            {"query": query}
        )

        web_results = await self._search_web(query)
        sm.transition_to(
            QueryState.TYPE4_WEB_SEARCH,
            "search_complete",
            {"results_count": len(web_results)}
        )

        # LLM synthesis
        sm.transition_to(
            QueryState.TYPE4_LLM_SYNTHESIS,
            "llm_start",
            {"web_results_count": len(web_results)}
        )

        answer = await self._synthesize_from_web(web_results, context)

        sm.transition_to(
            QueryState.TYPE4_LLM_SYNTHESIS,
            "llm_complete",
            {"answer_length": len(answer)}
        )

        # Go to common complete state
        sm.transition_to(QueryState.COMPLETE, "query_complete")

        return QueryResult(
            answer=answer,
            web_results=web_results,
            llm_used=True,
            confidence=0.9
        )
```

---

## Plugins Are Now Simple State Handlers

```python
# plugins/enrichers/llm_enricher.py

class LLMEnricher(Plugin):
    """
    LLM Enricher - now a simple state handler, not a god object.
    """

    name = "LLM Enricher"

    async def process(
        self,
        data: Dict[str, Any],
        context: QueryContext,
        state_machine: QueryStateMachine
    ) -> Dict[str, Any]:
        """
        Process LLM enrichment as a state transition.

        The state machine has already determined:
        - We need LLM processing
        - Which prompt builder to use
        - We just need to execute it
        """
        # Load strategies from config
        self.scope_check = ScopeCheckFactory.create(
            self.config.get("scope", {"type": "none"})
        )

        self.prompt_builder = PromptBuilderFactory.create(
            self.config.get("prompts", {"type": "general"})
        )

        # Check scope (if configured)
        query = data.get("query", "")
        patterns = data.get("patterns", [])

        in_scope, reason = self.scope_check.is_in_scope(query, patterns, context)

        state_machine.transition_to(
            QueryState.LLM_PROCESSING,
            "llm_scope_check",
            {"in_scope": in_scope, "reason": reason}
        )

        if not in_scope:
            return {"out_of_scope": True, "reason": reason}

        # Build prompt
        prompt = self.prompt_builder.build(data, context)

        state_machine.transition_to(
            QueryState.LLM_PROCESSING,
            "llm_prompt_built",
            {"prompt_length": len(prompt)}
        )

        # Call LLM
        answer = await self.llm.complete(prompt, context.show_thinking)

        state_machine.transition_to(
            QueryState.LLM_PROCESSING,
            "llm_complete",
            {"answer_length": len(answer)}
        )

        return {"answer": answer, "llm_used": True}
```

---

## Single Source of Truth: Domain Config

```
┌─────────────────────────────────────────────────────────────┐
│                   SINGLE SOURCE OF TRUTH                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Domain Config (domain.json)                                │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ {                                                  │     │
│  │   "domain_type": "4",  ←───┐                          │     │
│  │   "state_machine": "Type4AnalyticDomain",  ───────→ Class   │     │
│  │   "plugins": [...]                                  │     │
│  │ }                                                  │     │
│  └─────────────────────────────────────────────────────┘     │
│           │                                                     │
│           │    One domain.json per domain                     │
│           │    One DomainType class per domain type             │
│           │    State machine flow defined in class            │
│           │    Plugins configured in one place                │
│                                                           │
└─────────────────────────────────────────────────────────────┘
```

No more:
- Multiple config files
- Config override chains
- Domain registry caching
- Implicit type detection

---

## Testing: Verify State Machine Integrity

```python
# tests/test_state_machine.py

class TestType4StateMachine:
    """Verify Type 4 state machine is rock solid"""

    def test_all_transitions_defined(self):
        """Every transition must be explicitly defined"""
        sm = QueryStateMachine("4", "test query")

        # Get all defined transitions
        defined_states = set(s.value for s in QueryState)
        defined_transitions = sm.transitions.keys()

        # Verify all possible transitions are valid
        for from_state, trigger in defined_transitions:
            assert (from_state.value, trigger) in sm.transitions

    def test_invalid_transition_fails(self):
        """Invalid transitions must fail gracefully"""
        sm = QueryStateMachine("4", "test query")

        # Try to jump to COMPLETE directly from START
        result = sm.transition_to(QueryState.COMPLETE, "skip_all")
        assert result == False
        assert sm.current_state == QueryState.ERROR

    def test_state_log_completeness(self):
        """Every transition must be logged"""
        sm = QueryStateMachine("4", "test query")

        sm.transition_to(QueryState.START, "query_received")
        sm.transition_to(QueryState.ROUTING_SELECT_SPECIALIST, "specialist_selected")

        # Verify log has entries
        assert len(sm.state_log) == 2

        # Verify log structure
        for entry in sm.state_log:
            assert "query_id" in entry
            assert "timestamp" in entry
            assert "state" in entry
            assert "trigger" in entry

    def test_state_machine_trace_matches_logs(self):
        """Trace output should match state machine log"""
        # Run a query
        result = await domain.process_query("test query")

        # Get trace
        trace = result.get("state_machine", {})
        events = trace.get("events", [])

        # Verify each trace event has corresponding state log entry
        # This ensures trace is 1:1 with actual execution
        assert len(events) == len(sm.state_log)
```

---

## 100% Reliability Guarantees

### 1. No Implicit Transitions

```python
# WRONG: Implicit state change
if web_search_confirmed:
    # State changes implicitly - BAD
    await do_web_search()

# RIGHT: Explicit state transition
if web_search_confirmed:
    sm.transition_to(QueryState.TYPE4_WEB_SEARCH, "user_confirmed")
    await do_web_search()
```

### 2. No Silent Failures

Every transition either:
- Succeeds and logs
- Fails, logs error, transitions to ERROR state

### 3. Verifiable State

```bash
# Check state machine health
curl http://localhost:3000/api/state-machine/health

# Returns:
{
  "status": "healthy",
  "query_id": "q_abc123",
  "state": "type4_local_search",
  "last_transition": "search_complete",
  "transition_count": 5,
  "error_count": 0
}
```

### 4. Recovery from Errors

```python
if not sm.transition_to(...):
    # Transition failed - we're in ERROR state
    # Can attempt recovery:
    sm.transition_to(QueryState.COMPLETE, "error_recovery")
```

---

## Implementation Schedule

### Release 1: State Machine Foundation (Week 1)
**Goal**: Implement core state machine with Type 4 flow

**Tasks**:
1. Create `core/state_machine/query_sm.py`
2. Define `QueryState`, `QueryStateMachine`
3. Implement `Type4AnalyticDomain` with state machine
4. Add state machine logging to `/app/logs/traces/state_machine.jsonl`
5. Create state machine health endpoint

**Deliverable**: Type 4 queries run through state machine

---

### Release 2: Migrate to State Machine (Week 2)
**Goal**: All domains use state machine for query processing

**Tasks**:
1. Implement `Type3DocumentDomain` with state machine
2. Implement `Type1PatternDomain` with state machine
3. Migrate cooking and exframe domains
4. Remove old query processing code
5. Update all domain configs

**Deliverable**: All queries go through state machine

---

### Release 3: Plugin Refactor (Week 3)
**Goal**: Plugins become simple state handlers

**Tasks**:
1. Refactor `LLMEnricher` to use strategies
2. Implement strategy classes (ScopeCheck, PromptBuilder, etc.)
3. Create `PluginFactory`
4. Update domain configs for new plugin format

**Deliverable**: Plugins are < 200 lines, configured by domain.json

---

### Release 4: Hooks & Monitoring (Week 4)
**Goal**: Advanced tracing and monitoring

**Tasks**:
1. Implement `StateMachineHook` interface
2. Create monitoring dashboard that reads state machine logs
3. Add real-time state machine visualization
4. Performance monitoring and alerting

**Deliverable**: Full observability into query processing

---

## Success Metrics

### Reliability
✓ Zero implicit state changes
✓ All transitions logged
✓ Invalid transitions fail gracefully
✓ Error state is recoverable

### Observability
✓ Every query produces complete state trace
✓ State trace maps 1:1 to logs
✓ State machine health endpoint
✓ Real-time state visualization

### Maintainability
✓ Each domain type is a self-contained state machine
✓ State transitions are explicit and testable
✓ No config override chains
✓ Plugins are simple (<200 lines)

---

## Design Concerns & Open Questions

### Concern 1: State Flow Order Inconsistency

**Issue**: The Type 4 state flow diagram shows `ENRICHERS_EXECUTE → TYPE4_LOCAL_SEARCH`, but logically you should search first, THEN enrich.

**Current Diagram** (incorrect):
```
ROUTING → ENRICHERS_EXECUTE → TYPE4_LOCAL_SEARCH → ...
```

**Should be**:
```
ROUTING → TYPE4_LOCAL_SEARCH → ENRICHERS_EXECUTE → COMPLETE
```

**Question**: Should "enrichers" run before or after domain-specific processing?

### Concern 2: Missing LLM_PROCESSING State

**Issue**: The `QueryState` enum in the proposed design uses `LLM_PROCESSING` in the example LLMEnricher code, but this state is NOT defined in the `QueryState` enum.

**Resolution Needed**: Either:
- Add `LLM_PROCESSING` to the enum, OR
- Use existing states (`ENRICHERS_EXECUTED`) for LLM calls

### Concern 3: Contradiction Detection Scope

**User Feedback**: "Contradiction detection only ok in a closed document system type 3"

**Current Implementation**: Contradiction detection is in `LLMEnricher._detect_and_log_contradictions()` which:
- Only runs for Type 3 domains (document store search)
- Analyzes documents post-response
- Logs to `/app/logs/contradictions/`

**Design Question**: Should contradiction detection be:
- A Type 3 domain type strategy (in `Type3DocumentStrategy`), OR
- A separate enrichment plugin that can be configured per-domain?

### Concern 4: Domain Type Strategy Loading

**Question**: How do we determine which `DomainTypeStrategy` to load for LLMEnricher?

**Options**:
- **A**: From `domain.json` → `domain_type: "3"` (explicit, clean)
- **B**: Auto-detect from `specialist_id` (current approach, fragile)
- **C**: Pass through `EnrichmentContext.domain_type` (requires context population)

**Recommendation**: Option A - explicitly configure strategy in domain config.

### Concern 5: Show Thinking Logic Duplication

**Issue**: The "show_thinking" reasoning section is duplicated across 5 different prompt builders in LLMEnricher.

**Current Code** (repeated 5 times):
```python
if show_thinking:
    reasoning_section = """**IMPORTANT - Show your reasoning process:**
    Please show your step-by-step reasoning before giving the final answer:
    1. First, explain what patterns are relevant...
    [...]
    - **Reasoning:** [Your step-by-step analysis]
    - **Answer:** [Your final answer]
    """
else:
    reasoning_section = ""
```

**Solution**: Create a `ThinkingMixin` or `ReasoningSectionBuilder` for reuse.

### Concern 6: State Machine Ownership

**Question**: Who should drive state transitions?

**Options**:
- **A**: LLMEnricher drives transitions (`sm.transition_to(...)`)
- **B**: Domain type strategies handle transitions
- **C**: Engine/Coordinator handles all transitions (recommended)

**Current State Machine** (`state_machine.py`): The existing `QueryStateMachine` is already implemented and working. The proposed design should build on it, not replace it.

### Concern 7: Backward Compatibility

**Issue**: Existing `domain.json` files expect `LLMEnricher` with current behavior.

**Migration Strategy Needed**:
- How do we migrate existing domains?
- Can we run both old and new implementations side-by-side during transition?
- What's the rollback plan if the refactor breaks things?

### Concern 8: Type State Naming

**Issue**: The design shows `TYPE4_LOCAL_SEARCH`, `TYPE3_DOCUMENT_SEARCH`, etc. as states.

**Question**: Are these states, or are they just implementation details of domain type strategies?

**Alternative**: Keep states generic (`SPECIALIST_PROCESSING`), let domain strategies handle their internal flow.

---

## Next Steps

1. **Review this design** - Does it meet your requirements for rock-solid reliability?
2. **Approve Release 1** - Ready to start implementing?
3. **Prototype Type 4** - Want to see code example of Type4AnalyticDomain?

The key insight: **The state machine IS the architecture. Everything else follows from it.**
