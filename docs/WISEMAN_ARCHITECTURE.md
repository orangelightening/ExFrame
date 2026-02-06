# WiseMan Architecture Specification
## Config-Driven Query Processing System

**Version**: 1.0.0
**Status**: Design Phase (Long-term vision)
**Date**: 2026-02-04
**Replaces**: Current 1100-line conditional implementation

**⚠️ NOTE**: This is the **long-term architecture**. For immediate implementation, see **PHASE1_PERSONA_DESIGN.md** which provides a simpler incremental approach (Personas + Override, 1 week implementation).

---

## Executive Summary

**Problem**: The current query processing system has 1100+ lines of conditional logic, domain-specific code scattered throughout core components, and implicit query flow that's impossible to debug.

**Solution**: Replace with a template-based architecture where ONE execution engine (WiseMan) handles all query types through configuration switches, domains are simple config-driven sequencers, and all tools are standalone functions.

**Core Insight**: The mess came from tying domain logic to presentation layer. By separating domains into pure config sequencers and making the WiseMan handle all execution modes through switches, we eliminate the need for domain-specific code in core.

---

## The Three Components

### 1. WiseMan - The Universal Execution Engine

**Previously Called**: Poet, Librarian, Web Researcher (three separate implementations)

**Now**: ONE class with configuration switches that determine behavior.

```python
class WiseMan:
    """
    Universal query execution engine.

    All query types flow through the same engine - behavior is
    controlled by configuration switches, NOT by separate classes.
    """

    def __init__(self, config: WiseManConfig):
        # Logging & Debug Switches
        self.trace = config.trace              # Log query flow steps
        self.verbose = config.verbose          # Dump everything to logs
        self.show_thinking = config.show_thinking  # Request LLM reasoning

        # Source Switches (what to use for context)
        self.use_library = config.use_library  # Search document library
        self.use_internet = config.use_internet  # Search the web
        self.use_void = config.use_void        # Pure generation (no sources)

    def respond(self, query: str, domain: DomainSequencer) -> Response:
        """
        Process query through configured execution path.

        This is the ONLY entry point for all query processing.
        No if/elif on domain types. No special cases.
        """
        # 1. Get context from configured source
        context = self._get_context(query)

        # 2. Build prompt (including thinking request if needed)
        prompt = self._build_prompt(query, context)

        # 3. Execute LLM call
        response = self._call_llm(prompt)

        # 4. Log if configured
        if self.verbose:
            self._dump_everything(query, context, prompt, response)

        return response
```

**Key Point**: No domain-specific logic. The WiseMan doesn't know or care about domain types. It just follows its configuration.

---

### 2. DomainSequencer - Config-Driven Execution Flow

**Previously**: Complex domain objects with presentation logic mixed in

**Now**: Simple configuration that defines:
- Which tools to use
- In what order to run them
- What switches to set on WiseMan

```python
class DomainSequencer:
    """
    A domain is just a sequencer of operations.

    NO domain-specific logic lives here. Just configuration
    that says what to do and in what order.
    """

    def __init__(self, name: str, config: DomainConfig):
        self.name = name
        self.sequence = config.sequence    # ["validate", "search", "respond"]
        self.tools = config.tools          # {"search": "library_search"}
        self.wiseman_config = config.wiseman  # WiseMan switches

    def process(self, query: str) -> Response:
        """Execute the configured sequence"""
        wiseman = WiseMan(self.wiseman_config)

        # Execute sequence - just call tools in order
        for step in self.sequence:
            tool = self.tools.get(step)
            if tool:
                ToolRegistry.execute(tool, query, self)

        # Final response from WiseMan
        return wiseman.respond(query, self)
```

**Domain Configuration Example**:

```json
{
  "name": "cooking",
  "sequence": ["validate", "library_search", "check_contradictions", "respond"],
  "tools": {
    "validate": "query_validator",
    "library_search": "document_search",
    "check_contradictions": "contradiction_checker"
  },
  "wiseman": {
    "trace": true,
    "verbose": false,
    "show_thinking": true,
    "use_library": true,
    "use_internet": false,
    "use_void": false
  }
}
```

**Key Point**: Adding a new domain = writing a config file. NO code changes.

---

### 3. ToolRegistry - Standalone Function Catalog

**Previously**: Tools tied to specific plugins or domain implementations

**Now**: All tools are standalone functions registered in a central catalog.

```python
class ToolRegistry:
    """
    Central registry of all available tools.

    Tools are just functions - they don't know what domain
    is calling them or why.
    """

    _tools: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, func: Callable):
        """Register a tool function"""
        cls._tools[name] = func

    @classmethod
    def execute(cls, name: str, *args, **kwargs):
        """Execute a registered tool"""
        tool = cls._tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return tool(*args, **kwargs)


# Example tool registration
ToolRegistry.register("library_search", library_search_tool)
ToolRegistry.register("internet_search", internet_search_tool)
ToolRegistry.register("contradiction_check", contradiction_check_tool)
ToolRegistry.register("validate_query", query_validation_tool)
```

**Available Tools**:

| Tool Name | Purpose | Used By |
|-----------|---------|---------|
| `library_search` | Search document library | Document domains |
| `internet_search` | Search the web | Research domains |
| `contradiction_check` | Detect source contradictions | Closed document systems |
| `validate_query` | Validate query format | All domains |
| `format_response` | Format output | All domains |
| `log_trace` | Trace logging | Debugging |
| `dump_verbose` | Verbose dump | Debugging |

**Key Point**: Tools are reusable across any domain. No tool knows about domain types.

---

## WiseMan Configurations (Templates)

The WiseMan can operate in different modes through configuration templates:

### Poet Mode (Pure Generation)
```json
{
  "mode": "poet",
  "trace": true,
  "verbose": false,
  "show_thinking": false,
  "use_void": true,
  "use_library": false,
  "use_internet": false
}
```

**Behavior**: Pure LLM generation with no external sources.

---

### Librarian Mode (Document Search)
```json
{
  "mode": "librarian",
  "trace": true,
  "verbose": false,
  "show_thinking": true,
  "use_library": true,
  "use_internet": false,
  "use_void": false
}
```

**Behavior**: Search local documents, synthesize answer with thinking shown.

---

### Researcher Mode (Web Search)
```json
{
  "mode": "researcher",
  "trace": true,
  "verbose": true,
  "show_thinking": true,
  "use_library": false,
  "use_internet": true,
  "use_void": false
}
```

**Behavior**: Web search, full verbose logging, show reasoning process.

---

### Hybrid Mode (Library + Internet)
```json
{
  "mode": "hybrid",
  "trace": true,
  "verbose": false,
  "show_thinking": true,
  "use_library": true,
  "use_internet": true,
  "use_void": false
}
```

**Behavior**: Try library first, fall back to internet if insufficient.

---

## State Machine: Domain-Agnostic Query Orchestrator

```python
class QueryOrchestrator:
    """
    Domain-agnostic state machine for query processing.

    States:
    - INIT: Query received
    - ROUTE_DOMAIN: Determine which domain to use
    - PROCESS: Execute domain sequence
    - AGGREGATE: Combine results (if needed)
    - RESPOND: Send final response
    - ERROR: Handle errors
    """

    def __init__(self):
        self.state = QueryState.INIT
        self.transitions = {
            (QueryState.INIT, "query_received"): QueryState.ROUTE_DOMAIN,
            (QueryState.ROUTE_DOMAIN, "domain_selected"): QueryState.PROCESS,
            (QueryState.PROCESS, "sequence_complete"): QueryState.AGGREGATE,
            (QueryState.AGGREGATE, "aggregation_done"): QueryState.RESPOND,
            (QueryState.RESPOND, "response_sent"): QueryState.INIT
        }

    def transition(self, trigger: str, data: dict) -> bool:
        """
        Execute state transition.

        NO domain-specific logic here. Just generic state flow.
        """
        key = (self.state, trigger)
        next_state = self.transitions.get(key)

        if not next_state:
            self.state = QueryState.ERROR
            return False

        self.state = next_state
        self._log_transition(trigger, data)
        return True
```

**Key Point**: The state machine knows nothing about domains. It just manages generic query flow.

---

## Architectural Rules (DO NOT VIOLATE)

### Rule 1: NO Domain Conditionals in Core
```python
# ❌ WRONG - Domain-specific logic in core code
if domain.name == "cooking":
    response = handle_cooking(query)
elif domain.name == "diy":
    response = handle_diy(query)

# ✅ RIGHT - Config-driven execution
wiseman = WiseMan(domain.wiseman_config)
response = wiseman.respond(query, domain)
```

### Rule 2: Tools Are Functions, Not Classes
```python
# ❌ WRONG - Tool as class with domain awareness
class LibrarySearchTool:
    def execute(self, query, domain):
        if domain.type == "3":
            # Special Type 3 logic
            ...

# ✅ RIGHT - Tool as pure function
def library_search(query: str, max_results: int = 10) -> List[Document]:
    """Search library - doesn't care what domain called it"""
    return search_engine.search(query, limit=max_results)
```

### Rule 3: Configuration Drives Behavior
```python
# ❌ WRONG - Hardcoded behavior
if show_debug:
    self.enable_verbose_logging()

# ✅ RIGHT - Config-driven behavior
if self.config.verbose:
    self.dump_everything()
```

### Rule 4: State Machine Is Domain-Agnostic
```python
# ❌ WRONG - Domain-specific states
class QueryState(Enum):
    TYPE3_DOCUMENT_SEARCH = "type3_doc_search"
    TYPE4_WEB_SEARCH = "type4_web_search"

# ✅ RIGHT - Generic states
class QueryState(Enum):
    PROCESS = "process"  # Works for ALL domain types
    AGGREGATE = "aggregate"
    RESPOND = "respond"
```

---

## Success Criteria

### Architecture is Clean When:
- ✅ Adding a new domain = config file only (no code)
- ✅ NO `if domain_name ==` or `if domain_type ==` in core code
- ✅ WiseMan handles ALL modes (poet/librarian/researcher)
- ✅ Each tool is < 100 lines and domain-agnostic
- ✅ State machine has < 10 states total
- ✅ All behavior explained by reading config

### Implementation is Complete When:
- ✅ All 5 domain types implemented
- ✅ Old implementation completely removed
- ✅ All test/debug clutter cleaned up
- ✅ Query processing works correctly
- ✅ Production-ready code (no compatibility hacks needed)

---

## File Structure

```
generic_framework/
├── core/
│   ├── wiseman.py              # NEW - WiseMan execution engine
│   ├── domain_sequencer.py     # NEW - Config-driven domain
│   ├── tool_registry.py        # NEW - Central tool catalog
│   └── query_orchestrator.py  # NEW - Domain-agnostic state machine
│
├── tools/                       # NEW - All tools as functions
│   ├── __init__.py
│   ├── search_tools.py         # library_search, internet_search
│   ├── validation_tools.py     # validate_query, check_scope
│   ├── analysis_tools.py       # contradiction_check, relevance_check
│   └── logging_tools.py        # trace, verbose_dump
│
├── config/                      # NEW - Domain configurations
│   ├── domains/
│   │   ├── cooking.json
│   │   ├── diy.json
│   │   └── exframe.json
│   └── wiseman_templates.json  # poet, librarian, researcher configs
│
└── OLD_TO_DELETE/              # Archive during migration
    ├── llm_enricher.py         # DELETE after migration
    ├── domain_factory.py       # DELETE after migration
    └── ...
```

---

## Configuration Schema

### WiseManConfig
```json
{
  "trace": boolean,           // Enable trace logging
  "verbose": boolean,         // Enable verbose dumps
  "show_thinking": boolean,   // Request LLM reasoning
  "use_library": boolean,     // Use document library
  "use_internet": boolean,    // Use web search
  "use_void": boolean         // Pure generation (no sources)
}
```

### DomainConfig
```json
{
  "name": string,             // Domain name
  "description": string,      // Human-readable description
  "sequence": [string],       // Tool execution order
  "tools": {                  // Tool name mappings
    "step_name": "tool_name"
  },
  "wiseman": WiseManConfig    // WiseMan configuration
}
```

---

## Implementation Path

**Note**: This is a greenfield implementation, NOT a migration. The old code is reference material, not a compatibility target.

### Phase 1: Build Foundation (Week 1)
1. Create `WiseMan` class with all switches
2. Create `DomainSequencer` as config wrapper
3. Create `ToolRegistry` with basic tools
4. Create `QueryOrchestrator` state machine
5. Write tests for each component

### Phase 2: Implement Domains (Week 1-2)
1. Create domain configs for all 5 types
2. Implement required tools
3. Test each domain works correctly
4. **Goal**: Works correctly, not "matches old behavior"

### Phase 3: Integration (Week 2)
1. Wire new architecture into main engine
2. Delete old implementation code
3. Update imports and dependencies
4. Final testing and cleanup

---

## Open Design Questions

### 1. Can WiseMan Use Multiple Sources?
**Question**: Can `use_library` and `use_internet` both be true?

**Options**:
- A) Mutually exclusive (pick one)
- B) Priority-based (try library first, fall back to internet)
- C) Parallel (search both, merge results)

**Recommendation**: Option B - priority-based with fallback.

### 2. WiseMan Instance Scope
**Question**: One WiseMan per query or shared across queries?

**Options**:
- A) Create new WiseMan for each query (stateless)
- B) One WiseMan per domain (reusable)
- C) Single global WiseMan (singleton)

**Recommendation**: Option A - stateless, one per query.

### 3. Tool Error Handling
**Question**: If a tool fails mid-sequence, what happens?

**Options**:
- A) Abort entire sequence, return error
- B) Skip failed tool, continue sequence
- C) Try alternative tool (if configured)

**Recommendation**: Option A - fail fast, don't hide errors.

---

## Final Reminder

**This is a greenfield implementation with reference code.**

The old code shows what behaviors exist, but you're building the CORRECT implementation, not matching bugs.

- Build it right, not matching old behavior
- Test that it works, not that it matches
- Use old code as reference, not compatibility target
- Delete old code when new architecture is ready

**Timeline**: 2-3 weeks instead of 4-6 (no migration overhead)

---

**Status**: Design phase - ready for implementation
