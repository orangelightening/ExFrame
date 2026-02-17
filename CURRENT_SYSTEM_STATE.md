# Current System State - ExFrame
**Date:** 2026-02-15
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

Five modes available, configured per-domain in `conversation_memory.mode`:
- **`"all"`** — Load conversation history for every query
- **`"triggers"`** — Load only when trigger phrases match
- **`"question"`** — Load only when query starts with `**` prefix (loads raw domain_log.md)
- **`"journal"`** — Never load conversation memory (fast path)
- **`"journal_patterns"`** — Auto-create pattern + embedding per entry; `**` queries use semantic pattern search instead of raw log loading

### Role Context
**Location:** `domain.json` → `role_context` field

The `role_context` field is the **system message** sent to the LLM on every query. It defines how the AI behaves for a domain. It is:
- Stored in `domain.json` (persistent, version controlled)
- Always injected as the LLM system message, independent of conversation memory mode
- Editable via the domain editor UI
- Falls back to `"You are a helpful assistant."` if not set

This is the most critical config field — without it, the LLM has no domain-specific instructions.

### Domain Configuration (Peter Domain Example)
**File:** `universes/MINE/domains/peter/domain.json`
**Key settings:**
```json
{
  "role_context": "You are Peter's secretary. Your behavior depends on the query format: ...",
  "persona": "poet",
  "temperature": 0.3,
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/llama3.2",
    "api_key": "not-needed"
  },
  "conversation_memory": {
    "enabled": true,
    "mode": "journal_patterns",
    "trigger_phrases": ["**"],
    "max_context_chars": 5000
  },
  "logging": {
    "enabled": true,
    "output_file": "domain_log.md"
  }
}
```

**Domain Log:** `universes/MINE/domains/peter/domain_log.md`
- Stores conversation history with timestamps (audit trail)
- NOT used for retrieval in `journal_patterns` mode (patterns.json + embeddings.json used instead)

**Journal Patterns:** Each journal entry auto-creates a pattern in `patterns.json` with `pattern_type: "journal_entry"` and a corresponding embedding in `embeddings.json`. Queries prefixed with `**` trigger semantic search over these patterns.

### Two Engines Coexisting
- **Phase1Engine** (`core/phase1_engine.py`) — new simplified path via `/api/query/phase1`
- **GenericAssistantEngine** (`assist/engine.py`) — legacy engine, still active for:
  - Domain initialization at startup
  - Trace log retrieval (`/api/traces/log`, `/api/traces/{query_id}`)
  - Legacy query endpoints

Domain configs contain fields for both engines. Do NOT remove old-schema fields (`plugins`, `specialists`, `knowledge_base`, etc.) until full migration to Phase 1 is complete.

### Tao Subsystem (Knowledge Cartography)
**Status:** Phase 2a Complete (2026-02-15)
**Location:** `tao/` directory

Tao is a standalone subsystem for capturing, analyzing, and visualizing learning journeys through query/response history.

**Architecture:**
```
tao/
├── storage/          # Compressed Q/R history (knowledge_cartography.py moved here)
├── analysis/         # 5 analysis modules (sessions, chains, relations, concepts, depth)
├── api/              # REST API with 8 endpoints mounted at /api/tao/*
├── cli/              # Command-line tools (python -m tao.cli.*)
├── frontend/         # Web UI at http://localhost:3000/tao
└── docs/             # Complete documentation (API.md, TESTING.md, README.md)
```

**Storage:**
- Files: `universes/MINE/domains/{domain}/query_history.json.gz`
- Format: Compressed JSON (70-80% size reduction)
- Typical: ~400KB per 1,000 Q/R pairs
- Append-only, never modifies history

**Integration:**
- `query_processor.py` imports from `tao.storage` (not `core/knowledge_cartography.py`)
- Conversational memory: Last 20 Q/R pairs loaded automatically
- Real-time: No caching, immediate visibility in Tao UI

**Analysis Features:**
- **Sessions**: Group queries by time gaps
- **Chains**: Trace before/after query sequences
- **Relations**: Find related queries (temporal/pattern/keyword)
- **Concepts**: Extract and rank keywords
- **Depth**: Identify deep explorations (3+ related queries)

**Access:**
- Web UI: http://localhost:3000/tao (3 tabs: Sessions, Concepts, Depth)
- REST API: `/api/tao/sessions`, `/api/tao/concepts`, etc. (8 endpoints)
- CLI: `python -m tao.cli.view_history`, `show_sessions`, etc.
- Legacy scripts: `scripts/*.py` still work (deprecated wrappers)

**Documentation:** See `KNOWLEDGE_CARTOGRAPHY.md`, `tao/docs/API.md`, `tao/docs/TESTING.md`

**Future Phases:**
- Phase 2b: Advanced analytics (pattern effectiveness, knowledge gaps)
- Phase 3: Evocation tracking (Socratic question chains)
- Phase 4: Advanced concept analysis (LLM-based, semantic networks)
- Phase 5: Learning paths (progression tracking)
- Phase 6: Knowledge graph visualization

## Recent Changes (2026-02-15)

### Completed
- **Tao Subsystem Refactoring** — Complete extraction of knowledge cartography into standalone subsystem:
  - Moved `core/knowledge_cartography.py` → `tao/storage/storage.py`
  - Created 5 analysis modules in `tao/analysis/` (sessions, chains, relations, concepts, depth)
  - Built REST API with 8 endpoints at `/api/tao/*`
  - Created web UI at `/tao` with 3 tabs (Sessions, Concepts, Depth) and 2 modals (Chain, Related)
  - Implemented CLI tools as modules (`python -m tao.cli.*`)
  - Updated all imports in `query_processor.py` to use `tao.storage`
  - Created comprehensive documentation (API.md, TESTING.md)
  - Updated ARCHITECTURE.md with Tao subsystem section
  - Updated README.md with Tao mention and link

## Recent Changes (2026-02-13)

### Completed
- **Patterns-as-Journal** — New `journal_patterns` conversation memory mode:
  - Auto-creates a pattern (`pattern_type: "journal_entry"`) for every journal entry
  - Generates embedding via `EmbeddingService.encode_pattern()` + `VectorStore`
  - `**` queries use semantic search over journal patterns instead of loading raw domain_log.md
  - Three new functions in `query_processor.py`: `_create_journal_pattern()`, `_generate_journal_embedding()`, `_search_journal_patterns()`
  - Low similarity threshold (0.1) — lets the LLM decide relevance from top 10 matches
  - Fallback to most recent N entries if embeddings unavailable
- **Docker Model Runner** — Peter domain switched from Ollama to Docker Desktop's built-in model runner
  - Endpoint: `http://model-runner.docker.internal:12434/engines/v1`
  - Tested with `ai/smollm2` (360M) and `ai/llama3.2` (3B)
  - Managed via `docker model pull/ls/rm`
- Peter domain conversation memory changed from `"question"` to `"journal_patterns"`

### Previous Changes (2026-02-12)
- Trace data capture with LLM timing breakdown
- Phase1 traces written to `/app/logs/traces/queries.log`
- Added `"question"` and `"journal"` conversation memory modes to `query_processor.py`
- Changed Peter domain from `"mode": "all"` to `"mode": "question"` (fixes 10+ second simple query latency)
- Deleted broken `query_processor_new.py` (consolidated into existing query_processor.py)
- Fixed duplicate import and unused variable in `persona.py`
- Implemented `role_context` as first-class domain config field — always sent as LLM system message
- Added `.obsidian/` to `.gitignore` and removed from tracking
- Injected current date/time (local timezone via APP_TIMEZONE) into all LLM system messages
- Fixed trace toggle — trace log and response trace now respect `include_trace` flag
- Implemented per-domain `llm_config` — each domain can use a different LLM provider/model

### Per-Domain LLM Config
**Location:** `domain.json` → `llm_config` field

Allows each domain to override the global LLM provider. Domains without `llm_config` fall back to env vars (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LLM_MODEL`).

```json
{
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/llama3.2",
    "api_key": "not-needed"
  }
}
```

**Flow:** `domain.json` → `query_processor` (injects into context) → `persona._call_llm` (reads from context, falls back to env vars)

**Peter domain:** Using Docker Model Runner with `ai/llama3.2`.

### TODO — Testing and Next Steps
1. **Find a better local model** for Peter domain — `smollm2` too weak (ignores instructions), `llama3.2` over-cautious (refuses benign queries). Try uncensored variants or larger models.
2. **Test `**` query quality** — semantic search finds correct patterns, but LLM response quality depends on model. Larger models handle the role_context instructions better.
3. **Test other domains** still work on cloud LLM (no `llm_config` = env var fallback)
4. **Run full test plan** from `testplan.md`

### Pending Optimizations
1. **Separate persona from domain role**
   - Current: Poet persona defined at module level, hardcoded data_source="void"
   - Proposed: Make `data_source` configurable per domain in domain.json

2. **Full migration to Phase 1**
   - Migrate all legacy endpoints from GenericAssistantEngine to Phase1Engine
   - Once complete, old-schema config fields can be removed from domain.json files
