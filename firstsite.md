# ExFrame System Assessment & Recommendations

## Executive Summary

Your system has **solid foundations** (universe architecture, plugin system, semantic search) but is experiencing **architectural strain** from accumulated complexity. You have ~10,000 lines of core/plugin code, 13 domains, multiple design documents pointing in different directions, and 87 `__pycache__` directories indicating active development.

## Current System State

### Strengths
- **Universe Architecture**: Clean isolation and portability
- **Plugin Pipeline**: Router → Specialist → Enricher → Formatter (good separation)
- **Semantic Search**: Working implementation with embeddings
- **Persona System**: Poet/Librarian/Researcher abstraction (Phase 1 complete)

### Areas of Concern

| Issue | Impact | Root Cause |
|-------|--------|------------|
| **Multiple competing designs** | Confusion, paralysis | 3 design docs with different approaches |
| **Complexity concentration** | Hard to modify | LLMEnricher ~700 lines, engine ~1000+ lines |
| **Accumulated technical debt** | Brittleness | Type-based conditionals scattered throughout |
| **Unclear accountability** | Difficult debugging | No single source of truth for query flow |
| **Missing modularity** | Coupling concerns | Domain logic mixed with presentation |

---

## Strategic Recommendations

### 1. Consolidate Design Vision ⚠️ URGENT

**Problem**: You have three architecture documents pulling in different directions:
- `PLUGIN_REFACTOR_DESIGN.md` - State machine approach (complex, 4-6 weeks)
- `WISEMAN_ARCHITECTURE.md` - Config-driven template approach (long-term vision)
- Current implementation - Works but accumulates complexity

**Recommendation**: **Choose ONE path and commit.**

For someone valuing **simplicity**, I recommend the **WiseMan approach**:

```
Current: 1100 lines of conditional logic
WiseMan: 1 class with config switches → behavior
```

**Action**: Archive `PLUGIN_REFACTOR_DESIGN.md` (too complex) and implement WiseMan incrementally.

### 2. Establish Single Source of Truth

Create a **canonical system map**:

```
docs/
├── ARCHITECTURE.md          # Core principles & components (write this)
├── QUERY_FLOW.md            # How queries flow through system (write this)
├── WISEMAN_IMPLEMENTATION.md  # Track WiseMan progress (rename from DESIGN)
└── archive/
    ├── PLUGIN_REFACTOR_DESIGN.md  # Old design
    └── ...
```

Every component should be traceable to these docs.

### 3. Simplify Core Components

**Current state** (from analysis):
- `engine.py`: Orchestrates everything (large)
- `llm_enricher.py`: 700+ lines, domain-specific logic
- `domain.py`: Abstract base (good)
- `generic_domain.py`: Implementation with conditionals

**Recommendation - Recursive Simplification**:

```
core/
├── wiseman.py          # NEW - One execution engine, config-driven
├── domain.py           # KEEP - Abstract interface
├── sequencer.py        # NEW - Config-driven domain sequencer
├── tools/
│   ├── search.py       # Standalone functions
│   ├── enrich.py
│   └── validate.py
└── registry.py         # Central tool registry

plugins/                # DELETE - Move to tools/
```

**Key insight**: Tools are functions, not classes. Domains are configs, not code.

### 4. Implement "Everything Viewable & Accountable"

Create a **system observability layer**:

```python
# core/observability.py
class SystemObserver:
    """Central logging and tracing for everything."""

    def log_state_transition(self, from_state, to_state, trigger, data)
    def log_tool_execution(self, tool_name, inputs, outputs, duration)
    def log_config_decision(self, component, config_key, value)
    def get_trace(self, query_id) -> CompleteTrace
```

**Benefits**:
- Every state change visible
- Every config decision accountable
- Every tool execution traceable
- Full query lifecycle replayable

### 5. File Structure Cleanup

**Current**: 87 `__pycache__` directories, scattered configs

**Recommended structure** (recursive, self-similar):

```
eeframe/
├── generic_framework/
│   ├── core/              # Framework core (wiseman, sequencer, registry)
│   ├── tools/             # All tools as pure functions
│   ├── config/            # ALL configuration
│   │   ├── domains/       # Domain configs (JSON/YAML)
│   │   ├── templates/     # WiseMan templates
│   │   └── universe.yaml  # Universe config
│   ├── api/               # REST interface
│   └── diagnostics/       # Health checks
├── universes/
│   └── MINE/
│       ├── domains/       # Domain data (patterns, embeddings)
│       └── universe.yaml
└── docs/
    ├── ARCHITECTURE.md
    ├── QUERY_FLOW.md
    └── API.md
```

**Principle**: Code in `generic_framework/`, configs in `universes/*/`, docs in `docs/`.

---

## Immediate Action Items (Priority Order)

### 1. Week 1: Foundation
- [ ] Choose architecture path (recommend: WiseMan)
- [ ] Create `ARCHITECTURE.md` documenting current state
- [ ] Create `QUERY_FLOW.md` mapping query lifecycle
- [ ] Implement `SystemObserver` for full traceability
- [ ] Add `.gitignore` for `__pycache__` (if not present)

### 2. Week 2: Core Simplification
- [ ] Implement `WiseMan` class with config switches
- [ ] Extract tools from plugins to standalone functions
- [ ] Create `ToolRegistry` for centralized access
- [ ] Implement `DomainSequencer` as config wrapper

### 3. Week 3: Integration
- [ ] Migrate one domain to new architecture (recommend: `cooking`)
- [ ] Verify traceability works end-to-end
- [ ] Update documentation
- [ ] Remove old implementation only when new works

### 4. Week 4: Polish
- [ ] Migrate remaining domains
- [ ] Performance optimization
- [ ] Complete observability dashboard
- [ ] Final documentation

---

## Specific Code Recommendations

### Delete/Archive
- `PLUGIN_REFACTOR_DESIGN.md` → `archive/` (too complex)
- All `__pycache__/` directories (add to `.gitignore`)
- Test files in root (`test_*.py`, `*.sh`) → `tests/`

### Create
- `core/wiseman.py` - Universal execution engine
- `core/sequencer.py` - Config-driven domain wrapper
- `core/observability.py` - Central tracing
- `tools/` directory with standalone functions
- `ARCHITECTURE.md` - Canonical system documentation

### Refactor
- `llm_enricher.py` → Split into tool functions
- `engine.py` → Simplify to use WiseMan
- `generic_domain.py` → Replace with sequencer

---

## Questions for You

Before I create detailed implementation plans, I need to understand:

1. **Architecture decision**: WiseMan config-driven vs state machine vs hybrid?

2. **Migration strategy**: Big bang rewrite vs incremental migration?

3. **Priority**: What's most painful right now - debugging, adding features, or performance?

4. **Scope**: Are you building a production system or a research/learning project?

5. **Timeline**: What's your realistic availability for this work?

---

## Next Steps

Once you review this document, I can:

- **A)** Create a detailed implementation plan for the WiseMan architecture
- **B)** Start implementing specific components (observer, tools, etc.)
- **C)** First create the `ARCHITECTURE.md` and `QUERY_FLOW.md` docs
- **D)** Something else based on your feedback

**Review the recommendations above and let me know your direction.**
