# ExFrame Architecture (Derived from Code)

**Generated:** 2026-02-13
**Method:** Traced from running codebase, not from existing documentation

---

## 1. System Overview

ExFrame is a FastAPI application that processes natural language queries against configurable domains. Each domain has its own patterns (knowledge), persona (behavior), and optional LLM configuration.

**Container:** Single Docker container (`eeframe-app`) running uvicorn on port 3000.

**Runtime:** Python 3, FastAPI, with bind-mounted source code from host for live editing.

```
Docker Host
├── generic_framework/     → mounted to /app/ (core, api, plugins, etc.)
├── universes/MINE/        → mounted to /app/universes/ (domain configs + data)
└── docker-compose.yml     → orchestrates app + monitoring stack
```

---

## 2. Startup Sequence

**File:** `generic_framework/api/app.py` → `startup_event()` (line 431)

1. Fix file permissions on universe JSON files
2. Create `UniverseManager` with base path `/app/universes`, default universe `"MINE"`
3. Load default universe → calls `universe.activate()`
4. For each domain in the universe:
   - Create `GenericDomain` → loads `domain.json`, creates specialists, enrichers, knowledge base
   - Create `GenericAssistantEngine(domain)` → wraps the domain for query processing
   - Store in global `engines[domain_id]` dict
5. If universe loading fails, fall back to legacy domain discovery from `/app/data/patterns`

**Result:** A global `engines` dict mapping `domain_id → GenericAssistantEngine` instances, used by most API endpoints.

---

## 3. Two Engines (The Core Duality)

The system has **two completely separate query processing paths**. This is the most important architectural fact.

### 3.1 GenericAssistantEngine (Legacy Engine)

**File:** `generic_framework/assist/engine.py`

- Created at startup for every domain
- Stored in global `engines` dict
- Used by: `/api/query` (POST/GET), `/api/query/confirm-llm`, `/api/query/extend-web-search`, universe query endpoint
- Has its own: specialist selection, knowledge base search, enricher pipeline, state machine
- Does NOT use `query_processor.py` or personas

**Query flow:**
```
GenericAssistantEngine.process_query()
  → Select specialist (via can_handle() scoring)
  → Specialist searches knowledge base (or does its own search)
  → specialist.process_query() → specialist.format_response()
  → Enricher pipeline (LLMFallbackEnricher, etc.)
  → _record_query() (in-memory only, no domain_log.md)
  → Return result
```

### 3.2 Phase1Engine + query_processor (New Engine)

**File:** `generic_framework/core/phase1_engine.py` → calls `generic_framework/core/query_processor.py`

- Created on-demand per request (not stored globally)
- Used by: `/api/query/phase1` (the **only** endpoint the frontend actually calls)
- Uses personas (poet/librarian/researcher)
- Has: conversation memory, role_context injection, per-domain LLM config, journal patterns, domain_log.md logging

**Query flow:**
```
Phase1Engine.process_query()
  → query_processor.process_query()
    → _load_domain_config() from domain.json
    → Load role_context → inject into context
    → Load llm_config → inject into context
    → Conversation memory (mode-dependent: all/triggers/question/journal/journal_patterns)
    → Pattern search (_search_domain_patterns or _search_journal_patterns)
    → persona.respond(query, override_patterns, context)
      → _build_prompt() → _call_llm()
    → Log to domain_log.md
    → If journal_patterns mode: _create_journal_pattern()
    → Return result
```

### 3.3 Which Engine Does What

| Feature | GenericAssistantEngine | Phase1Engine (query_processor) |
|---------|----------------------|-------------------------------|
| **Used by frontend** | No | Yes (`/api/query/phase1`) |
| **Domain init** | Yes (startup) | No |
| **Specialists** | Yes (can_handle scoring) | No |
| **Enrichers** | Yes (LLMFallbackEnricher, etc.) | No |
| **Personas** | No | Yes (poet/librarian/researcher) |
| **Conversation memory** | No | Yes (5 modes) |
| **role_context** | No (uses enricher system prompt) | Yes (injected as LLM system message) |
| **Per-domain LLM config** | No (uses global env vars) | Yes |
| **domain_log.md writing** | No | Yes |
| **Journal patterns** | No | Yes |
| **State machine tracing** | Yes (QueryStateMachine) | No (simple trace list) |
| **Pattern search** | Via JSONKnowledgeBase | Via _search_domain_patterns() |

**Key insight:** The frontend exclusively uses Phase1Engine. The GenericAssistantEngine is still required for startup (domain/specialist/enricher initialization) and some admin/diagnostics endpoints, but all user-facing queries go through Phase1Engine.

---

## 4. API Endpoints

**File:** `generic_framework/api/app.py` (~3900 lines)

### Query Endpoints

| Endpoint | Method | Engine | Purpose |
|----------|--------|--------|---------|
| `/api/query/phase1` | POST | Phase1Engine | **Primary query path (frontend uses this)** |
| `/api/query` | POST | GenericAssistantEngine | Legacy query path |
| `/api/query` | GET | GenericAssistantEngine | Legacy query (browser/curl) |
| `/api/query/confirm-llm` | POST | GenericAssistantEngine | User-confirmed LLM fallback |
| `/api/query/extend-web-search` | POST | GenericAssistantEngine | Extended web search |

### Domain Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains` | GET | List all domains |
| `/api/domains/{id}` | GET | Get domain info |
| `/api/domains/{id}/specialists` | GET | List specialists |
| `/api/domains/{id}/patterns` | GET | List patterns |
| `/api/domains/{id}/patterns/{pid}` | GET | Get single pattern |
| `/api/domains/{id}/health` | GET | Domain health check |
| `/api/domains/{id}/log` | GET | Read domain_log.md |
| `/api/domains/{id}/log/archive` | POST | Archive domain log |
| `/api/domains/{id}/log/clear` | POST | Clear domain log |

### Admin

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/admin/domains` | GET | List domains (admin view) |
| `/api/admin/domains/{id}` | GET | Full domain config |
| `/api/admin/domains` | POST | Create domain |
| `/api/admin/domains/{id}` | PUT | Update domain |
| `/api/admin/domains/{id}` | DELETE | Delete domain |
| `/api/admin/domains/{id}/reload` | POST | Reload domain |
| `/api/admin/candidates` | GET | List candidate patterns |
| `/api/admin/candidates/{did}/{pid}/promote` | POST | Promote candidate to pattern |
| `/api/admin/domains/{did}/patterns/{pid}` | PUT | Update pattern |
| `/api/admin/domains/{did}/patterns/{pid}` | DELETE | Delete pattern |
| `/api/patterns` | POST | Create pattern |

### Diagnostics

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/diagnostics/health` | GET | System health |
| `/api/diagnostics/metrics` | GET | System metrics |
| `/api/diagnostics/patterns/health` | GET | Pattern health (per domain) |
| `/api/diagnostics/patterns/health/all` | GET | Pattern health (all domains) |
| `/api/diagnostics/summary` | GET | System summary |
| `/api/diagnostics/self-test` | POST | Run self-test |

### Other

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Container health check |
| `/` | GET | Serve frontend (index.html) |
| `/api/traces` | GET | Query traces |
| `/api/traces/log` | GET | Trace log file |
| `/api/embeddings/status` | GET | Embedding system status |
| `/api/embeddings/generate` | POST | Generate embeddings |
| `/api/universes` | GET | List universes |

---

## 5. Domain Configuration

**File:** `universes/MINE/domains/{domain_id}/domain.json`

Each domain is a directory containing:

```
universes/MINE/domains/{domain_id}/
├── domain.json         # Configuration (persona, role_context, llm_config, etc.)
├── patterns.json       # Pattern storage (knowledge base)
├── embeddings.json     # Pattern embeddings (for semantic search)
├── domain_log.md       # Conversation log (audit trail)
└── doc_embeddings.json # Document embeddings (librarian domains only)
```

### Key Config Fields (domain.json)

```
domain_id           - Unique identifier
persona             - "poet" | "librarian" | "researcher"
role_context         - System message sent to LLM on every query
temperature         - LLM temperature override
llm_config          - Per-domain LLM provider override
  base_url          - API endpoint
  model             - Model name
  api_key           - API key
conversation_memory - Memory loading configuration
  enabled           - true/false
  mode              - "all" | "triggers" | "question" | "journal" | "journal_patterns"
  max_context_chars - Max chars to load from domain_log.md
  trigger_phrases   - Phrases that trigger memory loading
logging             - Log configuration
  enabled           - true/false
  output_file       - Log file name (default: domain_log.md)
enable_pattern_override - Whether to search patterns (default: true)
library_base_path   - Document directory for librarian persona
document_search     - Semantic document search config
  algorithm         - "filesystem" | "semantic"
  max_documents     - Max docs to return
  min_similarity    - Minimum similarity threshold
```

### Fields Used Only by Legacy Engine

These exist for GenericAssistantEngine compatibility and are not used by Phase1Engine:

```
plugins             - Specialist plugin definitions
specialists         - Specialist configurations
enrichers           - Enricher pipeline configuration
knowledge_base      - Knowledge base configuration
pattern_schema      - Pattern validation schema
```

---

## 6. Persona System

### Persona Definitions

**File:** `generic_framework/core/personas.py`

Three singleton instances created at import time:

| Persona | Data Source | Behavior |
|---------|------------|----------|
| POET | `void` | Pure LLM generation, no external data |
| LIBRARIAN | `library` | Loads documents from `library_base_path`, passes to LLM |
| RESEARCHER | `internet` | Web search via DuckDuckGo, passes results to LLM |

### Persona Class

**File:** `generic_framework/core/persona.py`

**`respond(query, override_patterns, context)`** — Main entry point:

1. If `override_patterns` provided → format patterns as context string
2. Else → get data source content (void=None, library=documents, internet=web results)
3. Prepend conversation memory if present in context
4. `_build_prompt(query, content, show_thinking)` → builds `"Context:\n{content}\n\nQuery: {query}"`
5. `_call_llm(prompt, context)` → calls OpenAI-compatible API
6. Return response dict

**`_call_llm(prompt, context)`** — LLM call:

1. Check context for `llm_config` (per-domain override)
2. Fall back to env vars: `OPENAI_BASE_URL`, `LLM_MODEL`, `OPENAI_API_KEY`
3. Check context for `role_context` → use as system message
4. Inject current date/time (local timezone via `APP_TIMEZONE`) into system message
5. Call OpenAI chat completions API
6. For researcher persona: multi-turn with tool calling (web search)

---

## 7. Query Processor (Phase 1 Core Logic)

**File:** `generic_framework/core/query_processor.py`

**`process_query(query, domain_name, context, search_patterns, show_thinking)`**

### Step-by-step flow:

1. **Load domain config** — `_load_domain_config()` reads `domain.json` from disk (not cached)
2. **Get persona** — from `domain.json` → `persona` field
3. **Inject role_context** — always loaded, added to context dict
4. **Inject llm_config** — if present in domain.json, added to context dict
5. **Conversation memory** — mode-dependent:
   - `all` → load domain_log.md for every query
   - `triggers` → load if trigger phrases match
   - `question` → load if query starts with `**`
   - `journal` → never load (fast path)
   - `journal_patterns` → no log loading; sets `journal_pattern_search` flag on `**` queries
6. **Pattern search** — if enabled, `_search_domain_patterns()` reads `patterns.json`, returns first N
7. **Journal pattern search** — if `journal_pattern_search` flag set, `_search_journal_patterns()` does semantic search over `journal_entry` patterns, overrides patterns list
8. **Persona response** — `persona.respond(query, override_patterns=patterns, context=context)`
9. **Logging** — append query+response to `domain_log.md`
10. **Journal pattern creation** — if mode is `journal_patterns` and query has no `**` prefix, `_create_journal_pattern()` creates pattern + embedding

---

## 8. Journal Patterns (Patterns-as-Journal)

**File:** `generic_framework/core/query_processor.py`

### Entry creation flow:

```
User: "dentist Tuesday 3pm"
  → _create_journal_pattern("peter", "dentist Tuesday 3pm", "[timestamp] dentist Tuesday 3pm")
    → Create pattern dict: {id, name, pattern_type: "journal_entry", problem, solution, tags: ["journal"]}
    → Load patterns.json, append, save
    → _generate_journal_embedding(domain_path, pattern_id, pattern)
      → EmbeddingService.encode_pattern(pattern) → VectorStore.set() → VectorStore.save()
```

### Search flow:

```
User: "** when is my dentist appointment?"
  → Conversation memory mode strips "**", sets journal_pattern_search=True
  → _search_journal_patterns("peter", "when is my dentist appointment?")
    → Load patterns.json, filter to pattern_type == "journal_entry"
    → Load VectorStore (embeddings.json)
    → EmbeddingService.find_most_similar(query, journal_embeddings, threshold=0.1)
    → Return top 10 matching patterns
  → Patterns passed to persona.respond() as override_patterns
```

---

## 9. Embedding System

### Pattern Embeddings

**File:** `generic_framework/core/embeddings.py`

- **EmbeddingService** — Singleton, uses `all-MiniLM-L6-v2` (384-dim)
  - `encode(text)` → single text to vector
  - `encode_pattern(pattern)` → combines name, solution, description, problem fields
  - `find_most_similar(query, embeddings, pattern_data, top_k, threshold)` → semantic search
  - `cosine_similarity(a, b)` → similarity scoring

- **VectorStore** — Per-domain, stores in `{domain_path}/embeddings.json`
  - `load()` / `save()` — JSON persistence
  - `set(id, embedding)` / `get(id)` / `get_all()` — CRUD
  - Storage format: `{pattern_id: [float, float, ...], ...}`

### Document Embeddings

**File:** `generic_framework/core/document_embeddings.py`

- **DocumentVectorStore** — For librarian persona document search
  - Stores in `{domain_path}/doc_embeddings.json`
  - Indexes documents by file path
  - Tracks file hashes for incremental updates
  - Used by `_search_domain_documents_semantic()` in query_processor

---

## 10. Knowledge Base (Patterns)

**File:** `generic_framework/knowledge/json_kb.py` — `JSONKnowledgeBase`

- Loads patterns from `patterns.json`
- Supports semantic search if embeddings available
- Used by GenericAssistantEngine (legacy) for pattern search
- Phase1Engine reads patterns.json directly via `_search_domain_patterns()`

### Pattern Structure

```json
{
  "id": "unique_id",
  "name": "Short title",
  "pattern_type": "how_to | knowledge | journal_entry | ...",
  "problem": "What this addresses",
  "solution": "The answer/content",
  "description": "Optional longer description",
  "tags": ["optional", "tags"],
  "confidence": 0.9,
  "created_at": "ISO timestamp"
}
```

---

## 11. Enricher Pipeline (Legacy Engine Only)

**File:** `generic_framework/plugins/enrichers/llm_enricher.py`

Used only by GenericAssistantEngine, not by Phase1Engine.

- **LLMEnricher** — Base class. Calls LLM to synthesize response from patterns + query.
- **LLMFallbackEnricher** — Extends LLMEnricher. Only triggers when pattern confidence is low. Auto-added to all domains that don't configure enrichers.
- **LLMSummarizerEnricher** — Summarizes long responses.
- **LLMExplanationEnricher** — Adds explanations.

**Other enrichers:** `ReplyFormationEnricher` (source formatting), `CitationCheckerEnricher`, `RelatedPatternEnricher`, `CodeGeneratorEnricher`, `UsageStatsEnricher`.

---

## 12. Specialist System (Legacy Engine Only)

**File:** `generic_framework/core/specialist_plugin.py` — Abstract interface

Used only by GenericAssistantEngine. Specialists are plugins that handle queries:

- `can_handle(query) → float` — scoring (0.0 to 1.0)
- `process_query(query, context) → dict` — processing
- `format_response(data) → str` — formatting

**Built-in specialists:**
- `GeneralistPlugin` (`plugins/generalist.py`) — Default, handles any query
- `ExFrameSpecialist` (`plugins/exframe/`) — Three-stage search for documentation domains
- Domain-specific specialists (binary_symmetry, llm_consciousness, etc.)

---

## 13. Frontend

**File:** `generic_framework/frontend/index.html` — Alpine.js SPA

### Query Flow

1. User types query, clicks Send
2. Frontend POSTs to `/api/query/phase1` with:
   ```json
   {
     "query": "...",
     "domain": "peter",
     "include_trace": true/false,
     "verbose": true/false,
     "show_thinking": true/false,
     "search_patterns": true/false
   }
   ```
3. If response has `requires_confirmation` → show "Extend Search" buttons
4. User clicks "Confirm LLM" → POST to `/api/query/confirm-llm`
5. User clicks "Web Search" → POST to `/api/query/extend-web-search`

### Key UI State

- `searchPatterns` — defaults to `false` (checkbox in UI)
- `enableTrace` — show trace steps
- `enableVerbose` — verbose data snapshots
- `showThinking` — show LLM reasoning

**Note:** `searchPatterns` defaults to `false`, meaning the Phase1Engine skips `_search_domain_patterns()` unless the user checks the box. Journal pattern search (`**` queries) works independently of this flag.

---

## 14. LLM Configuration

### Global (Environment Variables)

```
OPENAI_API_KEY    - API key
OPENAI_BASE_URL   - API endpoint (default: https://api.openai.com/v1)
LLM_MODEL         - Model name (default: glm-4.7)
APP_TIMEZONE      - Timezone for date injection (default: America/Vancouver)
```

### Per-Domain Override (domain.json → llm_config)

```json
{
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/qwen3",
    "api_key": "not-needed"
  }
}
```

**Resolution order** (in `persona._call_llm`):
1. `context["llm_config"]` (per-domain, injected by query_processor)
2. Environment variables (global fallback)

### Supported Providers

- **Docker Model Runner** — `http://model-runner.docker.internal:12434/engines/v1` (requires `extra_hosts` in docker-compose)
- **Ollama** — `http://host.docker.internal:11434/v1`
- **OpenAI** — `https://api.openai.com/v1`
- **z.ai (GLM)** — `https://api.z.ai/api/coding/paas/v4`
- Any OpenAI-compatible API

---

## 15. File Map

```
generic_framework/
├── api/
│   └── app.py                          # FastAPI app, ALL endpoints (~3900 lines)
├── core/
│   ├── phase1_engine.py                # Phase1Engine wrapper (calls query_processor)
│   ├── query_processor.py              # Phase 1 core: memory, patterns, personas, journal (~1070 lines)
│   ├── personas.py                     # POET, LIBRARIAN, RESEARCHER singletons
│   ├── persona.py                      # Persona class: prompt building, LLM calls
│   ├── embeddings.py                   # EmbeddingService + VectorStore
│   ├── document_embeddings.py          # DocumentVectorStore (librarian doc search)
│   ├── generic_domain.py               # GenericDomain: loads config, wires specialists/enrichers
│   ├── domain_factory.py               # Legacy domain type factory (Types 1-5)
│   ├── specialist_plugin.py            # Specialist abstract interface
│   ├── enrichment_plugin.py            # Enricher abstract interface
│   ├── state/
│   │   └── query_state_machine.py      # QueryStateMachine (legacy engine tracing)
│   └── research/
│       ├── internet_strategy.py        # DuckDuckGo web search
│       └── document_strategy.py        # Document discovery
├── assist/
│   └── engine.py                       # GenericAssistantEngine (legacy, ~830 lines)
├── knowledge/
│   ├── json_kb.py                      # JSONKnowledgeBase (pattern storage/search)
│   ├── sqlite_kb.py                    # SQLite backend (alternative)
│   └── document_store.py              # Document store
├── plugins/
│   ├── generalist.py                   # GeneralistPlugin (default specialist)
│   ├── enrichers/
│   │   ├── llm_enricher.py            # LLMEnricher, LLMFallbackEnricher (~1400 lines)
│   │   ├── reply_formation.py          # Source formatting
│   │   └── citation_checker.py         # Citation verification
│   └── exframe/
│       └── exframe_specialist.py       # ExFrame documentation specialist
├── diagnostics/
│   ├── pattern_analyzer.py             # Pattern health analysis
│   ├── health_checker.py               # System health
│   └── search_metrics.py               # Search metrics/tracing
└── frontend/
    └── index.html                      # Alpine.js SPA (~4000 lines)

universes/MINE/
├── universe.json                       # Universe metadata
└── domains/
    ├── peter/                          # Journal domain
    │   ├── domain.json                 # Config: poet persona, journal_patterns mode, qwen3
    │   ├── patterns.json               # Journal entry patterns
    │   ├── embeddings.json             # Pattern embeddings
    │   └── domain_log.md               # Conversation log
    └── exframe/                        # Documentation domain
        ├── domain.json                 # Config: librarian persona, semantic search
        ├── patterns.json               # Knowledge patterns
        ├── embeddings.json             # Pattern embeddings
        ├── doc_embeddings.json         # Document embeddings
        └── domain_log.md               # Conversation log
```

---

## 16. Monitoring Stack

**File:** `docker-compose.yml`

| Service | Port | Purpose |
|---------|------|---------|
| eeframe-app | 3000 | Main application |
| prometheus | 9090 | Metrics collection |
| grafana | 3001 | Dashboards |
| loki | 3100 | Log aggregation |
| promtail | — | Log shipping |

---

## 17. Known Architectural Issues

1. **Two engines coexist** — GenericAssistantEngine is required for startup but all queries go through Phase1Engine. The legacy engine adds complexity without serving user queries.

2. **Config is loaded from disk on every query** — `_load_domain_config()` reads `domain.json` on each request. Not cached. Fast for small files but wasteful.

3. **`_search_domain_patterns()` is naive** — Returns first N patterns from `patterns.json` without semantic search. Only journal patterns use semantic search. Regular pattern search would benefit from the same embedding approach.

4. **Frontend defaults `searchPatterns` to false** — Regular domain patterns are never searched unless the user checks the box. This is intentional for journal domains but may confuse users of other domain types.

5. **Pattern creation is synchronous** — `_create_journal_pattern()` loads, appends, and saves the entire `patterns.json` on every journal entry. Will slow down as patterns grow.

6. **No deduplication** — Journal patterns are created for every entry, including duplicates. The same entry submitted twice creates two patterns.
