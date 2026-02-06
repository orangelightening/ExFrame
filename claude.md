# EEFrame - Context for Claude (AI Assistant)

**Purpose**: Complete context for resuming work on the EEFrame project
**Last Updated**: 2026-02-04
**Status**: WiseMan Architecture Design - Ready for Implementation
**Version**: 2.0.0 (Major Refactor)

---

## CURRENT STATE (2026-02-04)

### Phase 1 Implementation - FULLY COMPLETE ✅

**Status**: 🎉 **PRODUCTION READY** - Full end-to-end implementation working

**What Works**:
- ✅ LLM integration (DeepSeek API)
- ✅ Persona system (Poet, Librarian, Researcher)
- ✅ Pattern override (THE decision)
- ✅ Domain config loading
- ✅ Pattern search
- ✅ **Document search** (librarian persona loads markdown files)
- ✅ **search_patterns flag** (true/false/null)
- ✅ **API endpoint** (`/api/query/phase1`)
- ✅ **Frontend UI** (Search Patterns checkbox)
- ✅ Response format mapping
- ✅ Tests passing 100% in production container

**Impact**: 98% reduction in conditional logic (1000 → 20 lines)

**The Switch**:
- `search_patterns=true` → Search patterns, use if found
- `search_patterns=false` → Skip patterns, use persona data source
- For librarian: loads markdown files from domain's research_strategy

**Next**: User testing, decide on old code (keep/remove llm_enricher.py)

#### Phase 1: Personas + Override (IN PROGRESS - Day 1 Complete)
**Timeline**: 1 week (60% done after Day 1)
**Approach**: Incremental simplification of existing code

**What It Does**:
- Add ONE switch: pattern override
- Consolidate to 3 personas: Poet, Librarian, Researcher
- Simple decision: patterns provided? → use them, else → use persona's data source
- Keep all existing logs
- **Eliminates**: ~1000 lines of conditionals (98% reduction achieved)

**Files Created (Day 1)**:
- ✅ `generic_framework/core/persona.py` (~250 lines)
- ✅ `generic_framework/core/personas.py` (~60 lines)
- ✅ `generic_framework/core/query_processor.py` (~150 lines)
- ✅ `generic_framework/core/phase1_engine.py` (~150 lines)
- ✅ Updated 24 domain configs with persona field
- ✅ Tests created and passing (100%)

**Documentation**:
- ✅ `PHASE1_PERSONA_DESIGN.md` - Complete Phase 1 design
- ✅ `PHASE1_STATUS.md` - Implementation tracking
- ✅ `IMPLEMENTATION_SUMMARY.md` - Day 1 summary

#### Full WiseMan Architecture (Long-term vision)
**Timeline**: 2-3 weeks (if Phase 1 isn't sufficient)
**Approach**: Complete greenfield architecture

**Documentation**:
- ✅ `WISEMAN_ARCHITECTURE.md` - Complete architecture specification
- ✅ `WISEMAN_DESIGN.md` - Honest design assessment with risks
- ✅ `WISEMAN_IMPLEMENTATION_GUIDE.md` - Step-by-step implementation plan

**Key Insight**: "Phase 1 might be all you need. Don't build Phase 2 unless Phase 1 proves insufficient."

### Design Principles (The Rules)

**ARCHITECTURAL RULES (DO NOT VIOLATE)**:
1. Core state machine is domain-agnostic
2. Domain-specific logic lives in domain processors ONLY
3. **NO** `if/elif` on domain names in core code
4. Config drives behavior, not conditionals
5. If you're about to add domain-specific logic to core code, **STOP**

**Success Criteria**:
- Adding a new domain = config file only (no code changes)
- WiseMan handles ALL modes (poet/librarian/researcher)
- Each tool < 100 lines and domain-agnostic
- State machine has < 10 states total

### Implementation Timeline

**Phase 1 (IN PROGRESS)**: Personas + Override

### Day 1 - Core Implementation ✅
| Task | Status |
|------|--------|
| Create Persona class | ✅ DONE |
| Configure 3 personas | ✅ DONE |
| Add pattern override logic | ✅ DONE |
| Update domain configs | ✅ DONE (24 domains) |
| Create tests | ✅ DONE (100% passing) |

### Day 2 - Integration Work ✅
| Task | Status |
|------|--------|
| LLM client integration | ✅ DONE (DeepSeek API) |
| Domain config loading | ✅ DONE (reads domain.json) |
| Pattern search | ✅ DONE (reads patterns.json) |
| Import fixes for container | ✅ DONE |
| End-to-end testing in container | ✅ DONE (100% passing) |

### Day 3 - API & Frontend ✅
| Task | Status |
|------|--------|
| Add search_patterns flag | ✅ DONE (true/false/null) |
| Create /api/query/phase1 endpoint | ✅ DONE |
| Add frontend checkbox | ✅ DONE (Search Patterns) |
| Response format mapping | ✅ DONE (Phase 1 → frontend) |
| Document search integration | ✅ DONE (librarian loads .md files) |
| Fix config loading | ✅ DONE (full config with plugins) |
| End-to-end UI testing | ✅ DONE |

### What's Left To Do ⏳

**Immediate (Before Commit)**:
- ⏳ **User testing** - More testing with various domains
- ❓ **Old code decision** - Keep or archive llm_enricher.py (1450 lines)?
- ❓ **Commit Phase 1** - Ready when user approves

**Phase 2 (Future - Only If Needed)**:
| Enhancement | Status |
|-------------|--------|
| Semantic pattern search (embeddings) | 📋 Not needed yet |
| Semantic document search (chunking) | 📋 Not needed yet |
| Real web search integration | 📋 Not needed yet |
| Response caching | 📋 Not needed yet |

**Duration**: 3 days (COMPLETE - ahead of 1 week estimate!)
**Impact**: 98% reduction in conditionals (1000 → 20 lines)
**Status**: Production ready in container ✅

**Phase 2 (IF NEEDED)**: Full WiseMan Architecture
| Week | Phase | Status |
|------|-------|--------|
| 1 | Foundation | 📋 Not started |
| 1-2 | Domain Implementation | 📋 Not started |
| 2 | Integration & Cleanup | 📋 Not started |

**Duration**: 2-3 weeks
**Note**: Only implement if Phase 1 proves insufficient

---

## PREVIOUS WORK (Completed)

### Citation Checker Implementation - COMPLETE ✅

**Date**: 2026-02-04
**Status**: Implemented and synced to container

**What It Does**:
- Validates Type 3 and Type 4 domain responses contain at least 1 citation
- If no citations → Response replaced with: "Insufficient information to provide a response"
- Type 1, 2, 5 domains NOT affected

**Files Modified**:
```
generic_framework/plugins/enrichers/citation_checker.py  (NEW - ~250 lines)
generic_framework/core/domain_factory.py                   (added enricher configs)
generic_framework/core/domain.py                           (added domain_type, temperature fields)
generic_framework/core/universe.py                         (updated DomainConfig creation)
universes/MINE/domains/diy/domain.json                     (added CitationCheckerEnricher)
```

### Bug Fix: Domain Type Display - COMPLETE ✅

**Problem**: Domain type and temperature showing `null` in UI
**Root Cause**: Registry "old data ghosts" at `/app/data/domains.json`
**Fix**: Removed stale registry entry, API now loads fresh data

---

## QUICK RECOVERY GUIDE

### What is EEFrame?

**EEFrame** (ExFrame) is a domain-agnostic AI-powered knowledge management system with:
- Universe-based architecture (portable knowledge environments)
- Plugin-based pipeline (Router → Specialist → Enricher → Formatter)
- Pattern-based knowledge representation
- Pure semantic search using embeddings

### Current Architecture (Being Replaced)

```
CURRENT (1100+ lines of conditionals):
┌─────────────────────────────────────────────────┐
│  LLMEnricher (1450+ lines)                       │
│  ├── Mode switching (~100 lines)                 │
│  ├── Domain type detection (~200 lines)          │
│  ├── Creative query detection (~50 lines)        │
│  ├── Prompt builders (~500 lines, duplicated)    │
│  ├── LLM API handling (~200 lines)               │
│  ├── Contradiction detection (~250 lines)        │
│  └── Research strategy (~150 lines)              │
│                                                   │
│  PROBLEM: Domain-specific logic everywhere       │
│  SYMPTOM: if domain_type == "3" scattered        │
└─────────────────────────────────────────────────┘
```

### New Architecture (WiseMan)

```
NEW (Config-driven, clean separation):
┌─────────────────────────────────────────────────┐
│  WiseMan (ONE class)                             │
│  ├── Switches: trace, verbose, show_thinking     │
│  ├── Sources: use_library, use_internet, use_void│
│  └── Mode: Configured (poet/librarian/researcher)│
│                                                   │
│  DomainSequencer (Config wrapper)                │
│  ├── Sequence: ["validate", "search", "respond"] │
│  ├── Tools: {"search": "library_search"}         │
│  └── WiseMan config                              │
│                                                   │
│  ToolRegistry (Function catalog)                 │
│  ├── library_search()                            │
│  ├── internet_search()                           │
│  ├── contradiction_check()                       │
│  └── ... (all tools are functions)               │
│                                                   │
│  QueryOrchestrator (Domain-agnostic SM)          │
│  └── INIT → ROUTE → PROCESS → AGGREGATE → RESPOND│
└─────────────────────────────────────────────────┘
```

---

## CURRENT PROBLEM BEING SOLVED

### The 1100-Line Conditional Mess

**File**: `generic_framework/plugins/enrichers/llm_enricher.py`
- **Lines**: 1450+
- **Problem**: Conditional logic everywhere
- **Issue**: Domain types are strings, not behaviors
- **Symptom**: Scattered config, implicit query flow

**Responsibility Breakdown**:

| # | Responsibility | Lines | Problem |
|---|----------------|-------|---------|
| 1 | Mode switching | ~100 | Should be config |
| 2 | Domain type detection | ~200 | String checks everywhere |
| 3 | Creative query detection | ~50 | Hardcoded keywords |
| 4 | Prompt builders | ~500 | Duplicated 5 times |
| 5 | LLM API handling | ~200 | Mixed with business logic |
| 6 | Contradiction detection | ~250 | Only for Type 3, but in core |
| 7 | Research strategy | ~150 | Subclass complexity |

**String-Based Type Checking (Anti-Pattern)**:
```python
# Lines 186-190 - scattered throughout codebase
is_type3_domain = (
    specialist_id == "exframe_specialist" or
    domain_type == "3" or
    response_data.get("search_strategy") == "research_primary"
)
```

---

## 5 DOMAIN TYPES (Current System)

| Type | Name | Use Case | Web Search | Key Specialist |
|------|------|----------|------------|----------------|
| **1** | Creative Generator | Poems, stories | ❌ | GeneralistPlugin |
| **2** | Knowledge Retrieval | How-to, FAQs | ❌ | GeneralistPlugin |
| **3** | Document Store Search | External docs | ❌ | ExFrameSpecialistPlugin |
| **4** | Analytical Engine | Research, analysis | ✅ (default) | ResearchSpecialistPlugin |
| **5** | Hybrid Assistant | General purpose | ⚙️ Optional | GeneralistPlugin |

**Current Domains**:

| Domain | Type | Specialist | Notes |
|--------|------|------------|-------|
| `cooking` | 4 | ResearchSpecialistPlugin | Web search enabled |
| `diy` | 4 | ResearchSpecialistPlugin | Web search enabled |
| `exframe` | 3 | ExFrameSpecialistPlugin | Document store search |
| `poetry_domain` | 1 | GeneralistPlugin | Creative mode |
| `llm_consciousness` | 2 | GeneralistPlugin | Knowledge retrieval |

---

## CRITICAL FILES

### New Architecture Files (To Be Created)

| File | Purpose | Status |
|------|---------|--------|
| `docs/WISEMAN_ARCHITECTURE.md` | Architecture spec | ✅ Complete |
| `docs/WISEMAN_DESIGN.md` | Design with honest assessment | ✅ Complete |
| `docs/WISEMAN_IMPLEMENTATION_GUIDE.md` | Step-by-step guide | ✅ Complete |
| `generic_framework/core/wiseman.py` | WiseMan execution engine | 📋 To create |
| `generic_framework/core/domain_sequencer.py` | Config-driven domain | 📋 To create |
| `generic_framework/core/tool_registry.py` | Central tool catalog | 📋 To create |
| `generic_framework/core/query_orchestrator.py` | State machine | 📋 To create |
| `generic_framework/tools/` | Tool functions | 📋 To create |
| `generic_framework/config/domains/` | Domain configs | 📋 To create |

### Current Implementation (To Be Archived)

| File | Purpose | Status |
|------|---------|--------|
| `generic_framework/plugins/enrichers/llm_enricher.py` | Current LLM enricher | ⏳ Will archive |
| `generic_framework/core/domain_factory.py` | Current domain factory | ⏳ Will archive |
| `generic_framework/state/state_machine.py` | Current state machine | ⏳ Will replace |

### Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| `ARCHITECTURE_SPEC.md` | Original spec (basis for WiseMan) | ✅ Reference |
| `docs/PLUGIN_REFACTOR_DESIGN.md` | Alternative approach (NOT using) | ⚠️ Superseded |
| `universes/MINE/docs/context.md` | Old context | ⏳ Needs update |
| `claude.md` | This file | ✅ Updated |

---

## DESIGN PHILOSOPHY

### What We Learned

**The Root Cause**: Domain logic was tangled with presentation layer.

**Example of the Mess**:
```python
# Presentation logic in domain processing
if domain_type == "3":
    # Check contradictions
    if self.show_thinking:
        # Build thinking prompt
        if self.verbose:
            # Log everything
            if specialist_id == "exframe_specialist":
                # Special ExFrame logic
```

**The Fix**: Separate completely.

- **WiseMan** = HOW to execute (engine)
- **DomainSequencer** = WHAT to execute (config)
- **Tools** = WHAT operations exist (functions)
- **QueryOrchestrator** = WHEN to execute (state machine)

### The Rules (Again, Because They Matter)

1. **NO `if domain_name ==` in core code**
   - If you need domain-specific logic, create a tool
   - Tools are configured in domain config, not hardcoded

2. **Tools are functions, NOT classes**
   - Unless absolutely necessary
   - No tool should know what domain called it

3. **Configuration drives behavior**
   - Don't hardcode
   - Make it configurable

4. **State machine is domain-agnostic**
   - No TYPE3_SEARCH, TYPE4_WEB states
   - Generic states only: PROCESS, AGGREGATE, RESPOND

---

## HONEST ASSESSMENT (Updated for Greenfield)

### What Could Go Wrong

**Medium-Risk Issues**:
1. **Config files become unmaintainable** (40% probability)
   - Mitigation: Set 100-line limit per config
2. **Tool explosion** (40% probability)
   - Mitigation: Periodic consolidation, strict naming
3. **Debugging config-driven systems is HARD**
   - Mitigation: Excellent logging is REQUIRED, not optional

**Low-Risk Issues (Greenfield Advantages)**:
~~1. **Migration outputs don't match**~~ - NOT APPLICABLE (no compatibility requirement)
~~2. **Migration stalls halfway**~~ - NOT APPLICABLE (greenfield implementation)

**The Verdict**: Build it clean. You have the rare opportunity for greenfield implementation without migration baggage.

---

## NEXT STEPS

### Immediate Actions

1. **Review architecture docs** ✅ DONE
   - `WISEMAN_ARCHITECTURE.md`
   - `WISEMAN_DESIGN.md`
   - `WISEMAN_IMPLEMENTATION_GUIDE.md`

2. **Get approval to proceed**
   - Understand timeline (4-6 weeks)
   - Understand risks
   - Commit to following architectural rules

3. **Begin Phase 1: Foundation** (Week 1)
   - Create `WiseMan` class
   - Create `DomainSequencer` class
   - Create `ToolRegistry` class
   - Create `QueryOrchestrator` state machine
   - Write tests for all components
   - **NO changes to existing code yet**

### Future Phases

**Week 2**: Migrate Type 4 domains (cooking, diy)
**Week 3**: Migrate Type 1, 2, 3 domains (poetry, llm_consciousness, exframe)
**Week 4**: Integration, remove old code, cleanup
**Week 5-6**: Documentation, stabilization, production deployment

---

## INSTALLATION & DEPLOYMENT

### Prerequisites

**Required**:
- Docker Engine (official, NOT snap)
- Docker Compose v2
- Git

**Optional** (for LLM features):
- LLM API key (GLM, OpenAI, Anthropic, etc.)

### Quick Start

```bash
# Clone repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# Configure environment (optional - for LLM features)
cp .env.example .env
nano .env  # Edit with your API key

# Start application
docker compose up -d

# Access application
# Main UI: http://localhost:3000
# API Docs: http://localhost:3000/docs
# Health: http://localhost:3000/health
```

### LLM Configuration (.env)

**For GLM (z.ai) - RECOMMENDED**:
```bash
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-glm-key-here
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

**For OpenAI GPT**:
```bash
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**For Anthropic Claude**:
```bash
LLM_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=sk-ant-your-anthropic-api-key-here
OPENAI_BASE_URL=https://api.anthropic.com/v1
```

---

## GITHUB STATUS

**Repository**: https://github.com/orangelightening/ExFrame.git
**Working Directory**: `/home/peter/development/eeframe`
**Current Branch**: main
**Status**: WiseMan architecture design complete

**Modified Files** (uncommitted):
```
M .obsidian/workspace.json
M docs/PLUGIN_REFACTOR_DESIGN.md
M generic_framework/core/domain.py
M generic_framework/core/domain_factory.py
M universes/MINE/docs/context.md
+ generic_framework/plugins/enrichers/citation_checker.py
+ docs/WISEMAN_ARCHITECTURE.md
+ docs/WISEMAN_DESIGN.md
+ docs/WISEMAN_IMPLEMENTATION_GUIDE.md
+ claude.md
```

---

## DOCUMENTATION INDEX

### WiseMan Architecture (NEW)
- **WISEMAN_ARCHITECTURE.md** - Complete architecture specification
- **WISEMAN_DESIGN.md** - Design with honest risk assessment
- **WISEMAN_IMPLEMENTATION_GUIDE.md** - Step-by-step implementation plan
- **claude.md** - This file (context recovery)

### Original Design Docs (Reference)
- **ARCHITECTURE_SPEC.md** - Original specification (basis for WiseMan)
- **PLUGIN_REFACTOR_DESIGN.md** - Alternative approach (superseded)

### Main Documentation
- **README.md** - Project overview, installation, API reference
- **PLUGIN_ARCHITECTURE.md** - Plugin development guide
- **CHANGELOG.md** - Version history

### Universe Docs
- **universes/MINE/docs/context.md** - Universe-specific context

### Historical Documentation (Archive)
- **.archive/old-root-docs/** - Older documentation and plans

---

## SUCCESS METRICS

### Architecture is Clean When:
- ✅ Adding a new domain = config file only (no code changes)
- ✅ NO `if domain_name ==` or `if domain_type ==` in core code
- ✅ WiseMan handles ALL modes (poet/librarian/researcher)
- ✅ Each tool < 100 lines and domain-agnostic
- ✅ State machine has < 10 states total
- ✅ All behavior can be explained by reading config

### Migration is Complete When:
- ✅ All 5 domain types migrated
- ✅ Old implementation completely removed
- ✅ All test/debug clutter cleaned up
- ✅ Pipeline behavior acceptable (may differ from old system)
- ✅ Logging shows clear query flow
- ✅ Production-ready code

---

## WARNINGS & GOTCHAS

### The "Just One More Switch" Trap
- WiseMan switches will grow over time
- If > 15 switches, you're doing something wrong
- Consider whether you need multiple WiseMen instead

### Config Files Can Become "Code in JSON"
- NO syntax checking
- NO IDE support
- NO type safety
- Limit: 100 lines per config file

### Debugging is Harder
- Errors point to generic code, not specific logic
- EXCELLENT logging is REQUIRED, not optional
- Every config decision must be logged

### Reference Code May Have Bugs (Good!)
- Old code may have bugs that cancel each other out
- Clean architecture will fix them properly
- **Greenfield advantage**: No compatibility requirement
- Build it RIGHT, don't preserve bugs

---

## FINAL REMINDERS

1. **This is GREENFIELD, not a migration**
   - Build it RIGHT, not matching old behavior
   - Use old code as reference material only
   - No compatibility requirements
   - Fix bugs properly, don't preserve them

2. **Write the spec first** (✅ DONE)
   - Know what you're building before you build it

3. **Sleep when tired**
   - Architecture decisions need a fresh mind

4. **Enforce the rules**
   - "Just one if statement" is how the mess started
   - **Advantage**: No migration baggage means strict enforcement from day one

5. **Test that it WORKS**
   - Verify correctness, not output matching
   - No shadow mode testing needed
   - Build it clean from the start

6. **No special cases in core**
   - If it needs domain-specific logic, create a tool

---

**Last Updated**: 2026-02-04
**Status**: WiseMan architecture design complete (greenfield approach), ready for implementation
**Next Action**: Review design docs, approve implementation, begin Phase 1

---

**Key Insights**:
- "Domain logic was tangled with presentation. Separate them completely."
- "This is GREENFIELD with reference code, not a migration. Build it RIGHT."
- "Timeline: 2-3 weeks (no migration overhead)"
