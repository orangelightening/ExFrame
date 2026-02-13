# Current System State - ExFrame
**Date:** 2026-02-12
**Status:** Operational

## Overview
ExFrame is a personal AI assistant framework using:
- Phase 1 Engine (Persona + Pattern Override system) — primary query path
- Legacy Engine (GenericAssistantEngine) — still active for domain init, trace retrieval, legacy endpoints
- Domain-based configuration per persona
- Web interface for queries and traces

## Current Architecture

### Persona System
**Location:** `generic_framework/core/persona.py`
- **3 Personas available:**
  - **Poet** (void data source) - Used for personal journaling, creative domains
  - **Librarian** (library document search) - Used for knowledge retrieval, research domains
  - **Researcher** (internet data source) - Used for web search, current events

**Persona Configuration:**
- Each persona has: `name`, `data_source`, `show_thinking`, `trace`, `temperature`
- Personas are created once at startup and reused
- Configuration comes from `domain.json` files per domain

### Data Flow (Phase 1)
1. User query → Frontend → API (`/api/query/phase1`)
2. API calls `Phase1Engine.process_query()`
3. Phase1Engine calls `query_processor.process_query()`
4. query_processor:
   - Loads domain config
   - Gets persona (poet/librarian/researcher)
   - Loads conversation memory from `domain_log.md` (mode-dependent)
   - Searches patterns if enabled
   - Calls `persona.respond()` with context

### Conversation Memory Modes
**Location:** `generic_framework/core/query_processor.py`

Four modes available, configured per-domain in `conversation_memory.mode`:
- **`"all"`** — Load conversation history for every query
- **`"triggers"`** — Load only when trigger phrases match
- **`"question"`** — Load only when query starts with `**` prefix
- **`"journal"`** — Never load conversation memory (fast path)

### Domain Configuration (Peter Domain Example)
**File:** `universes/MINE/domains/peter/domain.json`
**Settings:**
```json
{
  "persona": "poet",
  "temperature": 0.3,
  "conversation_memory": {
    "enabled": true,
    "mode": "question",
    "max_context_chars": 5000,
    "trigger_phrases": ["**"]
  },
  "logging": {
    "enabled": true,
    "output_file": "domain_log.md"
  }
}
```

**Domain Log:** `universes/MINE/domains/peter/domain_log.md`
- Contains "Role Context" section with persona instructions
- Stores conversation history with timestamps
- Used as conversation memory source (when mode allows)

### Two Engines Coexisting
- **Phase1Engine** (`core/phase1_engine.py`) — new simplified path via `/api/query/phase1`
- **GenericAssistantEngine** (`assist/engine.py`) — legacy engine, still active for:
  - Domain initialization at startup
  - Trace log retrieval (`/api/traces/log`, `/api/traces/{query_id}`)
  - Legacy query endpoints

Domain configs contain fields for both engines. Do NOT remove old-schema fields (`plugins`, `specialists`, `knowledge_base`, etc.) until full migration to Phase 1 is complete.

## Recent Changes (2026-02-12)

### Completed
- Trace data capture with LLM timing breakdown
- Phase1 traces written to `/app/logs/traces/queries.log`
- Added `"question"` and `"journal"` conversation memory modes to `query_processor.py`
- Changed Peter domain from `"mode": "all"` to `"mode": "question"` (fixes 10+ second simple query latency)
- Deleted broken `query_processor_new.py` (consolidated into existing query_processor.py)
- Fixed duplicate import and unused variable in `persona.py`

### Pending Optimizations
1. **Separate persona from domain role**
   - Current: Poet persona defined at module level, hardcoded data_source="void"
   - Proposed: Make `data_source` configurable per domain in domain.json

2. **Full migration to Phase 1**
   - Migrate all legacy endpoints from GenericAssistantEngine to Phase1Engine
   - Once complete, old-schema config fields can be removed from domain.json files
