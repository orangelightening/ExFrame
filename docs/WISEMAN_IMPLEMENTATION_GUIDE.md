# WiseMan Implementation Guide
## Step-by-Step Implementation Plan

**Version**: 2.0.0 (Greenfield Edition)
**Date**: 2026-02-04
**Estimated Duration**: 2-3 weeks
**Skill Level Required**: Intermediate Python
**Approach**: Greenfield implementation with reference code

**⚠️ IMPORTANT**: This guide describes the **full WiseMan architecture**. For a **simpler, incremental approach**, see **PHASE1_PERSONA_DESIGN.md** which can be implemented in 1 week and eliminates 99% of conditionals with minimal changes.

**Recommended Path**:
1. Implement Phase 1 first (Personas + Override) - 1 week
2. Evaluate if Phase 2 (full WiseMan) is even needed
3. If needed, use this guide for Phase 2

---

## Prerequisites

Before starting, ensure:

1. **Understand the domain types**
   - Review all 5 domain types (see old code for reference)
   - Understand what behaviors each type needs
   - Use old code as reference, not compatibility target

2. **Branching strategy**
   - Create `wiseman-implementation` branch
   - No rollback plan needed (greenfield, not migration)

3. **Logging infrastructure ready**
   - Ensure `/app/logs/traces/` directory exists
   - Set up log rotation
   - Verbose logging support

---

## Phase 1: Foundation (Week 1)

**Goal**: Build new architecture components WITHOUT touching existing code.

### Step 1.1: Create WiseMan Class

**File**: `generic_framework/core/wiseman.py`

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
import logging


class SourceMode(Enum):
    """Where WiseMan gets context from"""
    VOID = "void"          # Pure generation
    LIBRARY = "library"    # Document search
    INTERNET = "internet"  # Web search


@dataclass
class WiseManConfig:
    """Configuration for WiseMan execution"""
    # Logging switches
    trace: bool = False
    verbose: bool = False
    show_thinking: bool = False

    # Source switches
    use_library: bool = False
    use_internet: bool = False
    use_void: bool = False

    def validate(self):
        """Ensure exactly one source is selected"""
        sources = [self.use_library, self.use_internet, self.use_void]
        if sum(sources) != 1:
            raise ValueError("Exactly one source must be enabled")


class WiseMan:
    """
    Universal query execution engine.

    Handles all query types through configuration, not conditionals.
    """

    def __init__(self, config: WiseManConfig):
        config.validate()
        self.config = config
        self.logger = logging.getLogger("wiseman")

    def respond(self, query: str, domain: 'DomainSequencer') -> Dict[str, Any]:
        """
        Process query through configured execution path.

        Args:
            query: User query string
            domain: Domain sequencer (for context)

        Returns:
            Response dictionary with answer and metadata
        """
        if self.config.trace:
            self.logger.info(f"WiseMan processing: {query}")

        # Get context from configured source
        context = self._get_context(query, domain)

        # Build prompt
        prompt = self._build_prompt(query, context)

        # Call LLM
        response = self._call_llm(prompt)

        # Verbose dump if configured
        if self.config.verbose:
            self._dump_verbose(query, context, prompt, response)

        return {
            "answer": response,
            "source": self._get_source_mode(),
            "metadata": {
                "thinking_shown": self.config.show_thinking,
                "traced": self.config.trace
            }
        }

    def _get_context(self, query: str, domain: 'DomainSequencer') -> Optional[str]:
        """Get context from configured source"""
        if self.config.use_library:
            return self._library_search(query, domain)
        elif self.config.use_internet:
            return self._internet_search(query)
        elif self.config.use_void:
            return None
        else:
            raise RuntimeError("No source configured")

    def _build_prompt(self, query: str, context: Optional[str]) -> str:
        """Build LLM prompt"""
        if context:
            prompt = f"Context:\n{context}\n\nQuery: {query}\n"
        else:
            prompt = query

        if self.config.show_thinking:
            prompt += "\n\nBefore answering, briefly explain your reasoning."

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with prompt.

        TODO: Implement actual LLM call
        """
        # Placeholder - replace with actual LLM integration
        return "LLM response placeholder"

    def _library_search(self, query: str, domain: 'DomainSequencer') -> str:
        """
        Search document library.

        TODO: Integrate with existing knowledge base
        """
        # Placeholder
        return f"Library context for: {query}"

    def _internet_search(self, query: str) -> str:
        """
        Search the internet.

        TODO: Integrate with web search API
        """
        # Placeholder
        return f"Internet context for: {query}"

    def _dump_verbose(self, query, context, prompt, response):
        """Dump everything to logs"""
        self.logger.debug("=" * 80)
        self.logger.debug(f"QUERY: {query}")
        self.logger.debug(f"CONTEXT: {context}")
        self.logger.debug(f"PROMPT: {prompt}")
        self.logger.debug(f"RESPONSE: {response}")
        self.logger.debug("=" * 80)

    def _get_source_mode(self) -> str:
        """Get current source mode name"""
        if self.config.use_library:
            return "library"
        elif self.config.use_internet:
            return "internet"
        elif self.config.use_void:
            return "void"
        return "unknown"
```

**Test**:
```python
# test_wiseman.py
def test_wiseman_void_mode():
    config = WiseManConfig(use_void=True, trace=True)
    wiseman = WiseMan(config)
    response = wiseman.respond("Test query", None)
    assert response["source"] == "void"

def test_wiseman_library_mode():
    config = WiseManConfig(use_library=True)
    wiseman = WiseMan(config)
    response = wiseman.respond("Test query", None)
    assert response["source"] == "library"
```

**Validation**:
- ✅ WiseMan can be instantiated with config
- ✅ Config validation prevents invalid source combinations
- ✅ Each source mode produces different context
- ✅ Logging works correctly

---

### Step 1.2: Create DomainSequencer Class

**File**: `generic_framework/core/domain_sequencer.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Any
from .wiseman import WiseMan, WiseManConfig


@dataclass
class DomainConfig:
    """Configuration for domain execution sequence"""
    name: str
    description: str
    sequence: List[str]           # Tool execution order
    tools: Dict[str, str]         # Step -> Tool name mapping
    wiseman: WiseManConfig        # WiseMan configuration


class DomainSequencer:
    """
    Config-driven domain execution sequencer.

    NO domain-specific logic here. Just config interpretation.
    """

    def __init__(self, config: DomainConfig):
        self.config = config
        self.name = config.name

    def process(self, query: str) -> Dict[str, Any]:
        """
        Execute configured sequence for query.

        Returns:
            Response dictionary
        """
        # Execute pre-processing tools in sequence
        for step in self.config.sequence:
            if step == "respond":
                # Final step - get WiseMan response
                break

            # Execute tool for this step
            tool_name = self.config.tools.get(step)
            if tool_name:
                self._execute_tool(tool_name, query)

        # Final response from WiseMan
        wiseman = WiseMan(self.config.wiseman)
        return wiseman.respond(query, self)

    def _execute_tool(self, tool_name: str, query: str):
        """
        Execute a registered tool.

        TODO: Integrate with ToolRegistry
        """
        # Placeholder - will integrate with ToolRegistry in Step 1.3
        pass
```

**Test**:
```python
# test_domain_sequencer.py
def test_domain_sequencer_execution():
    config = DomainConfig(
        name="test_domain",
        description="Test domain",
        sequence=["validate", "respond"],
        tools={"validate": "query_validator"},
        wiseman=WiseManConfig(use_void=True)
    )
    domain = DomainSequencer(config)
    response = domain.process("Test query")
    assert response is not None
```

**Validation**:
- ✅ DomainSequencer executes sequence in order
- ✅ WiseMan is called at end of sequence
- ✅ Config is cleanly separated from execution

---

### Step 1.3: Create ToolRegistry

**File**: `generic_framework/core/tool_registry.py`

```python
from typing import Callable, Dict, Any
import logging


class ToolRegistry:
    """
    Central registry of all executable tools.

    Tools are pure functions - they don't know about domains.
    """

    _tools: Dict[str, Callable] = {}
    _logger = logging.getLogger("tool_registry")

    @classmethod
    def register(cls, name: str, func: Callable, description: str = ""):
        """
        Register a tool function.

        Args:
            name: Tool identifier (used in domain configs)
            func: Callable tool function
            description: Human-readable description
        """
        if name in cls._tools:
            cls._logger.warning(f"Overwriting tool: {name}")

        cls._tools[name] = func
        cls._logger.info(f"Registered tool: {name}")

    @classmethod
    def execute(cls, name: str, *args, **kwargs) -> Any:
        """
        Execute a registered tool.

        Args:
            name: Tool identifier
            *args, **kwargs: Arguments to pass to tool

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        tool = cls._tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")

        cls._logger.debug(f"Executing tool: {name}")
        return tool(*args, **kwargs)

    @classmethod
    def list_tools(cls) -> List[str]:
        """Get list of all registered tools"""
        return list(cls._tools.keys())

    @classmethod
    def clear(cls):
        """Clear all registered tools (for testing)"""
        cls._tools.clear()
```

**File**: `generic_framework/tools/__init__.py`

```python
"""
Tool functions - standalone, reusable operations.

Each tool is a pure function that does ONE thing.
"""
from ..core.tool_registry import ToolRegistry


def query_validator(query: str) -> bool:
    """
    Validate query format.

    Args:
        query: User query string

    Returns:
        True if valid, False otherwise
    """
    if not query or len(query.strip()) == 0:
        return False
    if len(query) > 1000:  # Arbitrary limit
        return False
    return True


def library_search_tool(query: str, max_results: int = 10) -> list:
    """
    Search document library.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        List of matching documents
    """
    # TODO: Integrate with existing knowledge base
    return []


def internet_search_tool(query: str, max_results: int = 5) -> list:
    """
    Search the internet.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        List of search results
    """
    # TODO: Integrate with web search API
    return []


# Register all tools on import
ToolRegistry.register("query_validator", query_validator)
ToolRegistry.register("library_search", library_search_tool)
ToolRegistry.register("internet_search", internet_search_tool)
```

**Test**:
```python
# test_tool_registry.py
def test_tool_registration():
    ToolRegistry.clear()

    def test_tool(x):
        return x * 2

    ToolRegistry.register("test", test_tool)
    result = ToolRegistry.execute("test", 5)
    assert result == 10

def test_tool_not_found():
    ToolRegistry.clear()
    with pytest.raises(ValueError):
        ToolRegistry.execute("nonexistent", 5)
```

**Validation**:
- ✅ Tools can be registered and executed
- ✅ Tool not found raises clear error
- ✅ Tools are independent of domains

---

### Step 1.4: Create QueryOrchestrator State Machine

**File**: `generic_framework/core/query_orchestrator.py`

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import logging


class QueryState(Enum):
    """States in query processing flow"""
    INIT = "init"
    ROUTE_DOMAIN = "route_domain"
    PROCESS = "process"
    AGGREGATE = "aggregate"
    RESPOND = "respond"
    ERROR = "error"


@dataclass
class StateTransition:
    """Record of a state transition"""
    from_state: QueryState
    to_state: QueryState
    trigger: str
    timestamp: datetime
    data: Dict[str, Any]


class QueryOrchestrator:
    """
    Domain-agnostic state machine for query processing.

    Manages query flow WITHOUT knowing about specific domain types.
    """

    def __init__(self, query_id: str):
        self.query_id = query_id
        self.state = QueryState.INIT
        self.history: List[StateTransition] = []
        self.logger = logging.getLogger("query_orchestrator")

        # Valid transitions
        self.transitions = {
            (QueryState.INIT, "query_received"): QueryState.ROUTE_DOMAIN,
            (QueryState.ROUTE_DOMAIN, "domain_selected"): QueryState.PROCESS,
            (QueryState.PROCESS, "processing_complete"): QueryState.AGGREGATE,
            (QueryState.AGGREGATE, "aggregation_done"): QueryState.RESPOND,
            (QueryState.RESPOND, "response_sent"): QueryState.INIT,
        }

    def transition(self, trigger: str, data: Dict[str, Any] = None) -> bool:
        """
        Execute state transition.

        Args:
            trigger: Event triggering transition
            data: Context data for transition

        Returns:
            True if transition succeeded, False otherwise
        """
        key = (self.state, trigger)
        next_state = self.transitions.get(key)

        if not next_state:
            self.logger.error(
                f"Invalid transition: {self.state.value} --[{trigger}]--> ???"
            )
            self.state = QueryState.ERROR
            return False

        # Record transition
        transition = StateTransition(
            from_state=self.state,
            to_state=next_state,
            trigger=trigger,
            timestamp=datetime.utcnow(),
            data=data or {}
        )
        self.history.append(transition)

        # Execute transition
        old_state = self.state
        self.state = next_state

        self.logger.info(
            f"[{self.query_id}] {old_state.value} --[{trigger}]--> {next_state.value}"
        )

        return True

    def get_trace(self) -> List[Dict[str, Any]]:
        """Get complete state trace for debugging"""
        return [
            {
                "from": t.from_state.value,
                "to": t.to_state.value,
                "trigger": t.trigger,
                "timestamp": t.timestamp.isoformat(),
                "data": t.data
            }
            for t in self.history
        ]
```

**Test**:
```python
# test_query_orchestrator.py
def test_valid_transition_flow():
    orch = QueryOrchestrator("test-query-1")

    assert orch.transition("query_received")
    assert orch.state == QueryState.ROUTE_DOMAIN

    assert orch.transition("domain_selected")
    assert orch.state == QueryState.PROCESS

def test_invalid_transition():
    orch = QueryOrchestrator("test-query-2")

    # Try invalid transition
    result = orch.transition("invalid_trigger")
    assert result is False
    assert orch.state == QueryState.ERROR
```

**Validation**:
- ✅ State machine enforces valid transitions
- ✅ Invalid transitions move to ERROR state
- ✅ Complete trace is recorded
- ✅ No domain-specific logic in state machine

---

### Phase 1 Checkpoint

**Deliverables**:
- ✅ WiseMan class with all switches
- ✅ DomainSequencer as config wrapper
- ✅ ToolRegistry with basic tools
- ✅ QueryOrchestrator state machine
- ✅ All components have unit tests
- ✅ NO changes to existing code yet

**Validation Test**:
```python
# test_integration_phase1.py
def test_end_to_end_new_architecture():
    """Test new components work together"""
    # Create domain config
    config = DomainConfig(
        name="test",
        description="Test domain",
        sequence=["validate", "respond"],
        tools={"validate": "query_validator"},
        wiseman=WiseManConfig(use_void=True, trace=True)
    )

    # Create orchestrator
    orch = QueryOrchestrator("test-1")
    orch.transition("query_received")
    orch.transition("domain_selected")

    # Process query
    domain = DomainSequencer(config)
    response = domain.process("Test query")

    # Verify
    assert response is not None
    assert response["source"] == "void"
    assert len(orch.get_trace()) == 2
```

---

## Phase 2: Domain Implementation (Week 1-2)

**Goal**: Implement all 5 domain types correctly.

### Step 2.1: Understand Domain Behaviors (Reference Old Code)

Review old implementation to understand:
- What each domain type does
- What tools/operations each type needs
- Special behaviors (web search, contradiction check, etc.)

**Goal**: Understand behaviors, not match old outputs.

### Step 2.2: Create Domain Configs

**File**: `generic_framework/config/domains/cooking.json`

```json
{
  "name": "cooking",
  "description": "Cooking techniques and recipes",
  "domain_type": "4",
  "sequence": [
    "validate",
    "local_search",
    "relevance_check",
    "respond"
  ],
  "tools": {
    "validate": "query_validator",
    "local_search": "library_search",
    "relevance_check": "relevance_checker"
  },
  "wiseman": {
    "trace": true,
    "verbose": false,
    "show_thinking": true,
    "use_library": true,
    "use_internet": false,
    "use_void": false
  },
  "tool_configs": {
    "relevance_checker": {
      "threshold": 0.5,
      "on_insufficient": "request_web_search"
    }
  }
}
```

### Step 2.4: Implement Required Tools

**File**: `generic_framework/tools/relevance_tools.py`

```python
from ..core.tool_registry import ToolRegistry


def relevance_checker(
    patterns: list,
    threshold: float = 0.5,
    on_insufficient: str = "request_web_search"
) -> dict:
    """
    Check if search results meet relevance threshold.

    Args:
        patterns: List of pattern matches
        threshold: Minimum relevance score
        on_insufficient: Action if threshold not met

    Returns:
        Decision dictionary
    """
    if not patterns:
        return {
            "sufficient": False,
            "action": on_insufficient,
            "reason": "no_results"
        }

    max_relevance = max(p.get("relevance", 0) for p in patterns)

    if max_relevance < threshold:
        return {
            "sufficient": False,
            "action": on_insufficient,
            "max_relevance": max_relevance,
            "threshold": threshold
        }

    return {
        "sufficient": True,
        "max_relevance": max_relevance
    }


ToolRegistry.register("relevance_checker", relevance_checker)
```

### Step 2.5: Test Domain Works

**Goal**: Verify domain processes queries correctly.

**File**: `tests/domains/test_cooking.py`

```python
import pytest
from generic_framework.core.domain_sequencer import DomainSequencer
from generic_framework.config.loader import load_domain_config


@pytest.mark.parametrize("query,expected_behavior", [
    ("How do I cook rice?", "use_local_patterns"),
    ("What is molecular gastronomy?", "request_web_search"),
    ("Recipe for chocolate cake", "use_local_patterns")
])
def test_cooking_domain(query, expected_behavior):
    """Test cooking domain works correctly"""
    config = load_domain_config("cooking")
    domain = DomainSequencer(config)
    result = domain.process(query)

    # Verify it works - not that it matches old output
    assert result is not None
    assert "answer" in result

    # Verify expected behavior occurred
    if expected_behavior == "use_local_patterns":
        assert result["source"] == "library"
    elif expected_behavior == "request_web_search":
        assert result.get("can_extend_with_web_search") is True
```

**No shadow mode testing - just verify it works correctly.**

### Step 2.6: Implement All Domains

Implement all 5 domain types:

1. **Type 1**: Creative Generator (poetry)
2. **Type 2**: Knowledge Retrieval (llm_consciousness)
3. **Type 3**: Document Store Search (exframe)
4. **Type 4**: Analytical Engine (cooking, diy)
5. **Type 5**: Hybrid Assistant (if needed)

---

## Phase 3: Integration & Cleanup (Week 2)

**Goal**: Wire new architecture into system, delete old code.

### Step 3.1: Remove Old Implementation

When ready (all domains working):

```bash
# Move old code to archive
mkdir -p .archive/old_implementation
git mv generic_framework/plugins/enrichers/llm_enricher.py .archive/
git mv generic_framework/core/domain_factory.py .archive/

# Update imports
find generic_framework -name "*.py" -exec sed -i 's/from.*llm_enricher/# REMOVED/g' {} \;
```

**No rollback plan needed** - this is greenfield, not production migration.

### Step 3.2: Update Main Engine

**File**: `generic_framework/assist/engine.py`

```python
# Before:
from ..plugins.enrichers.llm_enricher import LLMEnricher

# After:
from ..core.domain_sequencer import DomainSequencer
from ..config.loader import load_domain_config


class QueryEngine:
    def process(self, query: str, domain_name: str):
        # Old way:
        # domain = self.domain_factory.create(domain_name)
        # enricher = LLMEnricher(...)

        # New way:
        config = load_domain_config(domain_name)
        domain = DomainSequencer(config)
        return domain.process(query)
```

### Step 3.3: Final Testing

Run full test suite:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/
```

**No regression tests needed** - not comparing to old system.

### Step 3.4: Performance Testing

Verify performance is acceptable:

```python
# benchmark.py
import time

def benchmark_domain(domain_name, queries):
    """Benchmark query processing time"""
    config = load_domain_config(domain_name)
    domain = DomainSequencer(config)

    times = []
    for query in queries:
        start = time.time()
        domain.process(query)
        times.append(time.time() - start)

    return {
        "avg": sum(times) / len(times),
        "max": max(times),
        "min": min(times)
    }
```

**Acceptance Criteria**:
- Average response time < 2 seconds for local queries
- Web search queries < 10 seconds

---

## Phase 4: Documentation (Week 2-3)

### Step 4.1: Update Documentation

**Files to Update**:
1. `README.md` - Architecture overview
2. `docs/PLUGIN_ARCHITECTURE.md` - New plugin model
3. `universes/MINE/docs/context.md` - Current status

### Step 4.2: Create Developer Guide

**File**: `docs/WISEMAN_DEVELOPER_GUIDE.md`

Topics:
- How to add a new domain
- How to create a new tool
- How to configure WiseMan
- How to debug queries
- Common mistakes and solutions

### Step 4.3: Create Operations Runbook

**File**: `docs/WISEMAN_OPERATIONS.md`

Topics:
- How to roll back if needed
- How to monitor system health
- How to debug production issues
- Common error patterns

---

## Success Checklist

Before considering implementation complete:

- [ ] All 5 domain types implemented
- [ ] All tests passing (unit, integration, e2e)
- [ ] Performance is acceptable
- [ ] Domains work correctly
- [ ] Old code removed from codebase
- [ ] Documentation updated
- [ ] System is ready for use

---

## Timeline (Greenfield)

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Foundation | New components built and tested |
| 1-2 | Domain Implementation | All 5 domain types working |
| 2 | Integration | Old code removed, system integrated |
| 2-3 | Documentation | Docs complete, system ready |

**Total**: 2-3 weeks (no migration overhead)

**Why Faster**: No shadow testing, no output matching, no rollback planning, no production migration concerns.

---

## Support & Questions

If you get stuck:

1. **Check logs** - Verbose mode shows everything
2. **Read config** - Most issues are config errors
3. **Reference old code** - See how it worked (but don't match it)
4. **Consult design docs** - Architectural rules are there for a reason
5. **Ask for help** - Don't struggle alone

---

## Key Advantages of Greenfield Approach

1. **No compatibility requirements** - Build it right, not matching bugs
2. **No shadow testing overhead** - Just test it works
3. **No rollback planning** - No production users to worry about
4. **Faster timeline** - 2-3 weeks instead of 4-6
5. **Cleaner code** - No backward compatibility hacks
6. **Less stress** - Focus on correctness, not matching

---

**Status**: Ready for implementation
**Approach**: Greenfield with reference code
**Timeline**: 2-3 weeks
**Next Step**: Begin Phase 1 - Create WiseMan class
