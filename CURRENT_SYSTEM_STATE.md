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
    "base_url": "http://host.docker.internal:11434/v1",
    "model": "mistral:7b",
    "api_key": "ollama"
  }
}
```

**Flow:** `domain.json` → `query_processor` (injects into context) → `persona._call_llm` (reads from context, falls back to env vars)

**Peter domain:** Configured with Ollama placeholder (needs Ollama running to test).

### TODO — Testing and Next Steps
1. **Install and run Ollama** on host with a small model (e.g., `ollama pull mistral:7b`)
2. **Test Peter domain** with local Ollama — journal entries should respond in <2 seconds
3. **Test other domains** still work on cloud LLM (no `llm_config` = env var fallback)
4. **Run full test plan** from `testplan.md`
5. **Evaluate local model quality** — does mistral:7b follow the role_context instructions correctly?
6. **Try other local models** if needed (llama3:8b, phi3, gemma2:9b)

### Pending Optimizations
1. **Separate persona from domain role**
   - Current: Poet persona defined at module level, hardcoded data_source="void"
   - Proposed: Make `data_source` configurable per domain in domain.json

2. **Full migration to Phase 1**
   - Migrate all legacy endpoints from GenericAssistantEngine to Phase1Engine
   - Once complete, old-schema config fields can be removed from domain.json files
