# ExFrame System Architecture

**Version:** 2.0.0
**Date:** 2026-02-13
**Status:** Production

> This document is the merged authoritative architecture reference.
> Derived from code tracing (new-arch.md) and existing documentation (ARCHITECTURE.md).

---

## Table of Contents

1. [What ExFrame Is](#1-what-exframe-is)
2. [Runtime Environment](#2-runtime-environment)
3. [Startup Sequence](#3-startup-sequence)
4. [The Two Engines](#4-the-two-engines)
5. [Query Flow: Phase 1 (Primary Path)](#5-query-flow-phase-1-primary-path)
6. [Query Flow: Legacy Engine](#6-query-flow-legacy-engine)
7. [Domain System](#7-domain-system)
8. [Persona System](#8-persona-system)
9. [LLM Call Chain](#9-llm-call-chain)
10. [Conversation Memory](#10-conversation-memory)
11. [Pattern System](#11-pattern-system)
12. [Journal Patterns (Patterns-as-Journal)](#12-journal-patterns-patterns-as-journal)
13. [Embedding System](#13-embedding-system)
14. [Semantic Document Search](#14-semantic-document-search)
15. [Web Search (Researcher Persona)](#15-web-search-researcher-persona)
16. [Enricher Pipeline (Legacy Only)](#16-enricher-pipeline-legacy-only)
17. [Specialist System (Legacy Only)](#17-specialist-system-legacy-only)
18. [State Machine (Legacy Only)](#18-state-machine-legacy-only)
19. [Frontend](#19-frontend)
20. [API Reference](#20-api-reference)
21. [File Map](#21-file-map)
22. [Monitoring Stack](#22-monitoring-stack)
23. [Known Issues & Technical Debt](#23-known-issues--technical-debt)

---

## 1. What ExFrame Is

ExFrame is a persona-based knowledge system. Users send natural language queries to domains. Each domain has its own knowledge (patterns), behavior (persona + role_context), and optionally its own LLM provider. The system searches for relevant patterns, passes them to the LLM as context, and returns a synthesized response.

**Core principle:** Data and composition are configuration. All transformation logic is pluggable.

- **Patterns** are data (JSON files, not code)
- **Domains** are orchestrators (configuration, not plugins)
- **Personas** define behavior (poet/librarian/researcher)
- **role_context** defines personality (system message to LLM)

---

## 2. Runtime Environment

Single Docker container running FastAPI on port 3000, with source code bind-mounted for live editing.

```
Docker Host
├── generic_framework/     → mounted to /app/ (core, api, plugins, frontend)
├── universes/MINE/        → mounted to /app/universes/ (domain configs + data)
└── docker-compose.yml     → app + monitoring stack (Prometheus, Grafana, Loki)
```

**Key bind mounts** (from docker-compose.yml):
```
./generic_framework/core   → /app/core
./generic_framework/api    → /app/api
./generic_framework/plugins → /app/plugins
./universes                → /app/universes
.                          → /app/project (read-only, for document search)
```

**Important:** Code changes on the host are visible inside the container immediately, but the Python process caches imported modules. A container restart is required after changing `.py` files.

---

## 3. Startup Sequence

**File:** `api/app.py` → `startup_event()`

1. Fix file permissions on universe JSON files (git clone may set restrictive modes)
2. Create `UniverseManager(base_path="/app/universes", default="MINE")`
3. Load default universe → `universe.activate()`:
   - For each domain directory in `universes/MINE/domains/`:
     - Create `GenericDomain(config)` → loads domain.json, wires specialists, enrichers, knowledge base
     - Create `GenericAssistantEngine(domain)` → wraps domain for query processing
     - Store in global `engines[domain_id]` dict
4. If universe loading fails → fall back to legacy domain discovery from `/app/data/patterns`

**Result:** Global `engines` dict of `GenericAssistantEngine` instances. The `Phase1Engine` is NOT created at startup — it's instantiated per-request.

---

## 4. The Two Engines

The system has two separate query processing paths. This is the most important architectural fact.

### GenericAssistantEngine (Legacy)

**File:** `assist/engine.py` (~830 lines)

- Created at startup for every domain, stored in `engines` dict
- Complex: specialist scoring → knowledge base search → enricher pipeline → state machine
- Does NOT use personas, query_processor, conversation memory, or per-domain LLM config
- Writes to in-memory history only (not domain_log.md)

### Phase1Engine + query_processor (Primary)

**File:** `core/phase1_engine.py` → `core/query_processor.py` (~1070 lines)

- Created per-request (stateless)
- Simple: load config → memory → pattern search → persona → LLM → log
- Uses personas, role_context, per-domain LLM config, conversation memory, journal patterns
- Writes to domain_log.md

### Feature Comparison

| Feature | Legacy Engine | Phase1Engine |
|---------|-------------|--------------|
| **Used by frontend** | No | **Yes** (`/api/query/phase1`) |
| **Initialized at startup** | Yes | No (per-request) |
| **Specialists** | Yes | No |
| **Enrichers** | Yes | No |
| **Personas** | No | Yes (poet/librarian/researcher) |
| **role_context** | No | Yes (LLM system message) |
| **Conversation memory** | No | Yes (5 modes) |
| **Per-domain LLM config** | No | Yes |
| **domain_log.md** | Not written | Written every query |
| **Journal patterns** | No | Yes |
| **State machine tracing** | Yes (QueryStateMachine) | No (simple trace list) |
| **Pattern search** | Via JSONKnowledgeBase | Via `_search_domain_patterns()` |

**The frontend exclusively uses Phase1Engine.** The legacy engine is required for startup (domain initialization) and some admin/diagnostic endpoints, but all user-facing queries go through Phase1Engine.

---

## 5. Query Flow: Phase 1 (Primary Path)

This is the path the UI uses for every query.

```
Frontend (index.html)
  POST /api/query/phase1
  body: { query, domain, search_patterns, show_thinking, include_trace }
      │
      ▼
app.py: process_query_phase1()
  → Phase1Engine(enable_trace).process_query(query, domain, context, search_patterns)
      │
      ▼
phase1_engine.py: process_query()
  → query_processor.process_query(query, domain_name, context, search_patterns)
      │
      ▼
query_processor.py: process_query()

  1. _load_domain_config(domain_name)         ← reads domain.json from disk
  2. get_persona(config.persona)              ← poet, librarian, or researcher
  3. Inject role_context into context dict     ← always loaded
  4. Inject llm_config into context dict       ← if present in domain.json
  5. Conversation memory (mode-dependent):
     ├─ "all"              → load last N chars of domain_log.md
     ├─ "triggers"         → load if trigger phrases match
     ├─ "question"         → load if query starts with **
     ├─ "journal"          → skip (fast path)
     └─ "journal_patterns" → skip loading; set search flag if ** prefix
  6. Pattern search (if search_patterns != false):
     → _search_domain_patterns() reads patterns.json, returns first N
  7. Journal pattern search (if ** flag set):
     → _search_journal_patterns() → semantic search over journal_entry patterns
  8. THE DECISION:
     ├─ patterns found → persona.respond(query, override_patterns=patterns, context)
     └─ no patterns   → persona.respond(query, context=context)
  9. Log query+response to domain_log.md
  10. If journal_patterns mode and no ** prefix:
      → _create_journal_pattern() + _generate_journal_embedding()
  11. Return response with metadata
```

---

## 6. Query Flow: Legacy Engine

Used by `/api/query` endpoint. The frontend does not call this for queries.

```
app.py: _process_query_impl()
  → engine.process_query(query, context, include_trace, llm_confirmed)

GenericAssistantEngine.process_query()
  1. Check for // prefix → direct LLM bypass
  2. Score all specialists → select highest via can_handle()
  3. If specialist:
     → specialist.process_query(query, context)
  4. If no specialist:
     → knowledge_base.search(query, limit=10)
     → _general_processing(query, patterns, context)
  5. Enricher pipeline:
     → domain.enrich(response_data, context)
     → LLMFallbackEnricher calls LLM if confidence low
  6. _record_query() → in-memory only
  7. Return response
```

---

## 7. Domain System

### Domain Directory Structure

```
universes/MINE/domains/{domain_id}/
├── domain.json         # Configuration
├── patterns.json       # Knowledge patterns
├── embeddings.json     # Pattern embeddings (semantic search)
├── domain_log.md       # Conversation log (audit trail)
└── doc_embeddings.json # Document embeddings (librarian only)
```

### domain.json — Key Fields

**Phase 1 fields** (used by query_processor):

| Field | Type | Purpose |
|-------|------|---------|
| `persona` | string | `"poet"` / `"librarian"` / `"researcher"` |
| `role_context` | string | System message sent to LLM on every query |
| `temperature` | float | LLM temperature override |
| `llm_config` | object | Per-domain LLM provider (`base_url`, `model`, `api_key`) |
| `conversation_memory` | object | Memory mode config (`enabled`, `mode`, `max_context_chars`) |
| `logging` | object | Log config (`enabled`, `output_file`) |
| `enable_pattern_override` | bool | Whether to search patterns (default: true) |
| `library_base_path` | string | Document directory (librarian persona) |
| `document_search` | object | Semantic doc search config (`algorithm`, `max_documents`) |

**Legacy fields** (used by GenericAssistantEngine, keep until migration complete):

| Field | Type | Purpose |
|-------|------|---------|
| `plugins` | array | Specialist plugin definitions |
| `specialists` | array | Specialist configurations |
| `enrichers` | array | Enricher pipeline configuration |
| `knowledge_base` | object | KB configuration |
| `pattern_schema` | object | Pattern validation schema |

### Example: Peter Journal Domain

```json
{
  "domain_id": "peter",
  "persona": "poet",
  "role_context": "You are Peter's secretary. For ** queries, answer from journal. Otherwise, timestamp and echo.",
  "temperature": 0.3,
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/qwen3",
    "api_key": "not-needed"
  },
  "conversation_memory": {
    "enabled": true,
    "mode": "journal_patterns"
  },
  "logging": {
    "enabled": true,
    "output_file": "domain_log.md"
  }
}
```

---

## 8. Persona System

**Files:** `core/personas.py` (definitions), `core/persona.py` (class)

Three singleton personas created at import time:

| Persona | Data Source | Use Case |
|---------|------------|----------|
| **Poet** | `void` | Pure LLM generation — journals, creative writing |
| **Librarian** | `library` | Document search — technical docs, knowledge bases |
| **Researcher** | `internet` | Web search — current events, recipes, research |

### Persona.respond()

```
1. override_patterns provided?
   ├─ Yes → _format_patterns() → content string
   └─ No  → _get_data_source_content()
            ├─ void     → None (pure generation)
            ├─ library  → format loaded documents
            └─ internet → None (web search handled separately)
2. Prepend conversation memory prefix if present
3. _build_prompt(query, content) → "Context:\n{content}\n\nQuery: {query}"
4. _call_llm(prompt, context) → HTTP POST to LLM API
5. Return response dict
```

### Pattern Formatting

When patterns are passed as override, they're formatted as:
```
[Pattern 1] Pattern Name
Problem: ...
Solution:
...
```

This string becomes the `Context:` block in the LLM prompt.

---

## 9. LLM Call Chain

**File:** `core/persona.py` → `_call_llm()`

### Config Resolution

1. `context["llm_config"]` — per-domain override (from domain.json, injected by query_processor)
2. Environment variables — global fallback (`OPENAI_BASE_URL`, `LLM_MODEL`, `OPENAI_API_KEY`)

### Prompt Structure

```
System message:
  {role_context}
  Current date and time: 2026-02-13 11:30:00

User message:
  Context:
  {formatted patterns, documents, or memory}

  Query: {user's query}
```

### Supported LLM Providers

| Provider | base_url | api_key |
|----------|----------|---------|
| Docker Model Runner | `http://model-runner.docker.internal:12434/engines/v1` | `"not-needed"` |
| Ollama | `http://host.docker.internal:11434/v1` | `"ollama"` |
| OpenAI | `https://api.openai.com/v1` | `sk-...` |
| z.ai (GLM) | `https://api.z.ai/api/coding/paas/v4` | your key |
| Any OpenAI-compatible | varies | varies |

**Docker Model Runner:** Docker Desktop's built-in inference. Models managed via `docker model pull/ls/rm`. Requires `extra_hosts: model-runner.docker.internal:host-gateway` in docker-compose. Supports GPU acceleration with `--gpu cuda`.

---

## 10. Conversation Memory

**File:** `core/query_processor.py` — Phase 1 only

Conversation memory loads previous interactions into the LLM context. Configured per-domain:

```json
{
  "conversation_memory": {
    "enabled": true,
    "mode": "journal_patterns",
    "max_context_chars": 5000,
    "trigger_phrases": ["**"]
  }
}
```

### Five Modes

| Mode | Loads domain_log.md? | Creates patterns? | Search on **? | Use Case |
|------|---------------------|-------------------|---------------|----------|
| `all` | Every query | No | N/A | Full conversational context |
| `triggers` | When trigger phrases match | No | N/A | Selective context |
| `question` | When query starts with `**` | No | Raw text search | Journal with question support |
| `journal` | Never | No | N/A | Pure logging, max speed |
| `journal_patterns` | Never | Yes (every entry) | Semantic search | Journal with semantic retrieval |

### `journal_patterns` vs `question`

Both support `**` prefix queries. The key difference:

- **`question`** loads the last N chars of raw `domain_log.md` into the LLM context. Brute-force, truncates old entries, wastes tokens.
- **`journal_patterns`** creates a searchable pattern with embedding for every entry, then uses semantic similarity to find relevant entries. ~10ms retrieval, no truncation, scales indefinitely.

### Memory Injection

When loaded, memory content becomes a prefix to the LLM context:
```
Previous conversation:

{last N chars of domain_log.md}

---

Context:
{patterns or documents}

Query: {user query}
```

---

## 11. Pattern System

### Storage

Patterns live in `{domain_path}/patterns.json`:

```json
{
  "patterns": [
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
  ]
}
```

### Valid Pattern Types

`troubleshooting`, `procedure`, `substitution`, `decision`, `diagnostic`, `preparation`, `optimization`, `principle`, `solution`, `failure_mode`, `technique`, `concept`, `getting_started`, `knowledge`, `how_to`, `concepts`, `features`, `journal_entry`, and domain-specific types.

### Two Search Paths

**Phase 1** (`_search_domain_patterns`): Reads patterns.json directly, returns first N patterns. No semantic scoring.

**Legacy** (`JSONKnowledgeBase.search`): Supports semantic search via embeddings if available, falls back to keyword matching.

**Journal** (`_search_journal_patterns`): Filters to `journal_entry` type, uses semantic search via EmbeddingService, threshold 0.1.

---

## 12. Journal Patterns (Patterns-as-Journal)

**File:** `core/query_processor.py`

### Entry Creation

When `conversation_memory.mode == "journal_patterns"` and query has no `**` prefix:

```
User: "dentist Tuesday 3pm"
  → LLM responds: "[2026-02-13 10:30:00] dentist Tuesday 3pm"
  → _create_journal_pattern():
      pattern = {
        id: "peter_20260213_103000",
        name: "dentist Tuesday 3pm",
        pattern_type: "journal_entry",
        problem: "dentist Tuesday 3pm",
        solution: "[2026-02-13 10:30:00] dentist Tuesday 3pm",
        tags: ["journal"]
      }
      → Append to patterns.json
      → _generate_journal_embedding():
          → EmbeddingService.encode_pattern(pattern)
          → VectorStore.set(id, embedding)
          → VectorStore.save() → embeddings.json
```

### Semantic Search

When query starts with `**`:

```
User: "** when is my dentist appointment?"
  → Strip **, set journal_pattern_search flag
  → _search_journal_patterns():
      → Load patterns.json, filter to pattern_type == "journal_entry"
      → Load VectorStore(embeddings.json)
      → EmbeddingService.find_most_similar(query, journal_embeddings, top_k=10, threshold=0.1)
      → Return matched patterns
  → Pass to persona.respond() as override_patterns
  → LLM synthesizes answer from journal context
```

---

## 13. Embedding System

### Pattern Embeddings

**File:** `core/embeddings.py`

| Component | Purpose |
|-----------|---------|
| `EmbeddingService` | Singleton. Model: `all-MiniLM-L6-v2` (384-dim). Encodes text to vectors. |
| `VectorStore` | Per-domain store in `embeddings.json`. CRUD for pattern embeddings. |

**Key methods:**
- `encode(text)` → single text to numpy vector
- `encode_pattern(pattern)` → combines name, solution, description, problem fields
- `find_most_similar(query, embeddings, data, top_k, threshold)` → ranked results
- `cosine_similarity(a, b)` → similarity score

**Performance:** ~10ms to load from disk, ~5ms per similarity computation.

### Document Embeddings

**File:** `core/document_embeddings.py` — `DocumentVectorStore`

Separate system for librarian persona. Stores in `doc_embeddings.json`. Indexes markdown files by path, tracks file hashes for incremental updates.

---

## 14. Semantic Document Search

**Used by:** Librarian persona via `query_processor._search_domain_documents_semantic()`

```
Query → DocumentVectorStore.search(query, top_k=10, min_similarity=0.3)
  → Rank documents by cosine similarity
  → Load top N documents from disk
  → Pass to persona as context
```

**Configuration:**
```json
{
  "document_search": {
    "algorithm": "semantic",
    "max_documents": 10,
    "min_similarity": 0.3,
    "auto_generate_embeddings": true
  }
}
```

**Performance:**
- Initial embedding generation: ~2-5 seconds for 100 documents (one-time)
- Incremental: ~50ms per new/modified document
- Cached search: ~10ms

Falls back to filesystem search (load first N files) if semantic search is unavailable.

---

## 15. Web Search (Researcher Persona)

**File:** `core/research/internet_strategy.py`

The researcher persona uses multi-turn function calling for web search:

1. Send query to LLM with web_search tool definition
2. LLM returns `tool_calls` with search query
3. Execute DuckDuckGo search via `InternetResearchStrategy`
4. Fetch full page content for top 3 results (3000 chars each)
5. Send results back to LLM as tool response
6. LLM synthesizes final answer with source URLs

**Response includes clickable sources:**
```json
{
  "response": "Here's what I found...",
  "web_search_used": true,
  "sources": [
    {"title": "Page Title", "url": "https://..."}
  ]
}
```

---

## 16. Enricher Pipeline (Legacy Only)

**File:** `plugins/enrichers/llm_enricher.py`

Used only by GenericAssistantEngine, not by Phase1Engine.

Enrichers run in sequence after specialist processing:

```python
for enricher in domain._enrichers:
    response_data = await enricher.enrich(response_data, context)
```

| Enricher | Purpose |
|----------|---------|
| `LLMEnricher` | Base class — synthesizes response from patterns via LLM |
| `LLMFallbackEnricher` | Only triggers on low confidence. Auto-added to all domains. |
| `LLMSummarizerEnricher` | Summarizes long responses |
| `ReplyFormationEnricher` | Formats responses with source citations |
| `CitationCheckerEnricher` | Validates citations |
| `RelatedPatternEnricher` | Suggests related patterns |

---

## 17. Specialist System (Legacy Only)

**File:** `core/specialist_plugin.py`

Used only by GenericAssistantEngine. Three-method interface:

```python
class SpecialistPlugin(ABC):
    def can_handle(self, query: str) -> float:       # Score 0.0-1.0
    async def process_query(self, query, context):    # Process query
    def format_response(self, response_data) -> str:  # Format output
```

**Built-in:**
- `GeneralistPlugin` — Default, handles any query
- `ExFrameSpecialist` — Three-stage search for documentation domains

---

## 18. State Machine (Legacy Only)

**File:** `core/state/query_state_machine.py`

Used by GenericAssistantEngine for query lifecycle tracing.

```python
class QueryState(Enum):
    QUERY_RECEIVED = "QUERY_RECEIVED"
    DIRECT_LLM = "DIRECT_LLM"
    ROUTING_SELECTION = "ROUTING_SELECTION"
    SPECIALIST_PROCESSING = "SPECIALIST_PROCESSING"
    ENRICHERS_EXECUTED = "ENRICHERS_EXECUTED"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    LOG_AND_EXIT = "LOG_AND_EXIT"
```

**Normal flow:** `QUERY_RECEIVED → ROUTING_SELECTION → SPECIALIST_PROCESSING → ENRICHERS_EXECUTED → COMPLETE`

Phase1Engine does not use the state machine — it returns a simple trace list of `[{step, action, timestamp}]` entries.

---

## 19. Frontend

**File:** `frontend/index.html` — Alpine.js SPA (~4000 lines)

### Query Flow

1. User types query, selects domain, clicks Send
2. POST to `/api/query/phase1`:
   ```json
   {
     "query": "...",
     "domain": "peter",
     "search_patterns": false,
     "include_trace": true,
     "show_thinking": false
   }
   ```
3. Display response with trace steps
4. If `requires_confirmation` → show "Extend Search" / "Web Search" buttons

### Default UI State

| Setting | Default | Effect |
|---------|---------|--------|
| `searchPatterns` | **false** | `_search_domain_patterns()` skipped unless checked |
| `enableTrace` | false | Trace steps hidden |
| `enableVerbose` | false | No verbose data snapshots |
| `showThinking` | false | No LLM reasoning shown |

**Note:** `searchPatterns` defaulting to `false` means regular pattern override never fires from the UI unless the user checks the box. Journal pattern search (`**` queries in `journal_patterns` mode) works independently of this flag.

### Other UI Features

- Domain selector dropdown
- Domain editor (admin panel)
- Pattern browser and editor
- Diagnostics panel (pattern health, metrics)
- Candidate pattern management (promote/delete LLM-generated patterns)
- Trace viewer (expandable steps)
- Domain log viewer

---

## 20. API Reference

### Query Endpoints

| Endpoint | Method | Engine | Purpose |
|----------|--------|--------|---------|
| `/api/query/phase1` | POST | Phase1Engine | **Primary — frontend uses this** |
| `/api/query` | POST/GET | Legacy | Legacy query path |
| `/api/query/confirm-llm` | POST | Legacy | User-confirmed LLM fallback |
| `/api/query/extend-web-search` | POST | Legacy | Extended web search |

### Domain Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains` | GET | List all domains |
| `/api/domains/{id}` | GET | Domain info |
| `/api/domains/{id}/specialists` | GET | List specialists |
| `/api/domains/{id}/patterns` | GET | List patterns |
| `/api/domains/{id}/patterns/{pid}` | GET | Single pattern |
| `/api/domains/{id}/health` | GET | Health check |
| `/api/domains/{id}/log` | GET | Read domain_log.md |
| `/api/domains/{id}/log/archive` | POST | Archive log |
| `/api/domains/{id}/log/clear` | POST | Clear log |

### Admin Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/admin/domains` | GET | List (admin view) |
| `/api/admin/domains/{id}` | GET | Full config |
| `/api/admin/domains` | POST | Create domain |
| `/api/admin/domains/{id}` | PUT | Update domain |
| `/api/admin/domains/{id}` | DELETE | Delete domain |
| `/api/admin/domains/{id}/reload` | POST | Reload |
| `/api/admin/domains/{did}/patterns/{pid}` | PUT | Update pattern |
| `/api/admin/domains/{did}/patterns/{pid}` | DELETE | Delete pattern |
| `/api/admin/candidates` | GET | List candidates |
| `/api/admin/candidates/{did}/{pid}/promote` | POST | Promote candidate |
| `/api/patterns` | POST | Create pattern |

### Diagnostics Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/diagnostics/health` | GET | System health |
| `/api/diagnostics/metrics` | GET | Metrics |
| `/api/diagnostics/patterns/health` | GET | Pattern health (per domain) |
| `/api/diagnostics/patterns/health/all` | GET | Pattern health (all) |
| `/api/diagnostics/summary` | GET | Summary |
| `/api/diagnostics/self-test` | POST | Self-test |

### Embedding Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/embeddings/status` | GET | Status per domain |
| `/api/embeddings/generate` | POST | Generate embeddings |
| `/api/embeddings/model` | GET | Model info |

### Other

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Container health |
| `/` | GET | Serve frontend |
| `/api/traces` | GET | Query traces |
| `/api/universes` | GET | List universes |

---

## 21. File Map

```
generic_framework/
├── api/
│   └── app.py                          # FastAPI app, ALL endpoints (~3900 lines)
├── core/
│   ├── phase1_engine.py                # Phase1Engine wrapper
│   ├── query_processor.py              # Phase 1 core logic (~1070 lines)
│   ├── personas.py                     # POET, LIBRARIAN, RESEARCHER singletons
│   ├── persona.py                      # Persona class: prompts, LLM calls
│   ├── embeddings.py                   # EmbeddingService + VectorStore
│   ├── document_embeddings.py          # DocumentVectorStore
│   ├── generic_domain.py              # GenericDomain: config, specialists, enrichers
│   ├── domain_factory.py              # Legacy Type 1-5 factory
│   ├── specialist_plugin.py            # Specialist ABC
│   ├── enrichment_plugin.py            # Enricher ABC
│   ├── universe.py                     # UniverseManager
│   ├── state/
│   │   └── query_state_machine.py      # QueryStateMachine (legacy)
│   └── research/
│       ├── internet_strategy.py        # DuckDuckGo web search
│       └── document_strategy.py        # Document discovery
├── assist/
│   └── engine.py                       # GenericAssistantEngine (legacy, ~830 lines)
├── knowledge/
│   ├── json_kb.py                      # JSONKnowledgeBase
│   ├── sqlite_kb.py                    # SQLite backend (alternate)
│   └── document_store.py              # Document store
├── plugins/
│   ├── generalist.py                   # GeneralistPlugin
│   ├── enrichers/
│   │   ├── llm_enricher.py            # LLMEnricher, LLMFallbackEnricher (~1400 lines)
│   │   ├── reply_formation.py          # Source formatting
│   │   └── citation_checker.py         # Citation verification
│   └── exframe/
│       └── exframe_specialist.py       # ExFrame specialist
├── diagnostics/
│   ├── pattern_analyzer.py             # Pattern health
│   ├── health_checker.py               # System health
│   └── search_metrics.py              # Search metrics
└── frontend/
    └── index.html                      # Alpine.js SPA (~4000 lines)

universes/MINE/
├── universe.json
└── domains/
    ├── peter/
    │   ├── domain.json                 # poet, journal_patterns, qwen3 via DMR
    │   ├── patterns.json               # journal_entry patterns
    │   ├── embeddings.json             # pattern embeddings
    │   └── domain_log.md
    └── exframe/
        ├── domain.json                 # librarian, semantic search
        ├── patterns.json
        ├── embeddings.json
        ├── doc_embeddings.json         # document embeddings
        └── domain_log.md
```

---

## 22. Monitoring Stack

| Service | Port | Image |
|---------|------|-------|
| eeframe-app | 3000 | Custom (Dockerfile) |
| Prometheus | 9090 | prom/prometheus:v2.48.0 |
| Grafana | 3001 | grafana/grafana:10.2.2 |
| Loki | 3100 | grafana/loki:2.9.2 |
| Promtail | — | grafana/promtail:2.9.2 |

---

## 23. Known Issues & Technical Debt

1. **Two engines coexist** — GenericAssistantEngine is required at startup but serves no user queries. It adds ~2000 lines of active code that could be removed once Phase 1 migration is complete.

2. **Phase 1 reads config independently** — `_load_domain_config()` reads domain.json from disk on every request, separately from the GenericDomain loaded at startup. The two systems can see different configs.

3. **`_search_domain_patterns()` is naive** — Returns first N patterns without scoring. Only journal patterns use semantic search. Regular pattern search should use embeddings too.

4. **Frontend defaults `searchPatterns` to false** — Pattern override never fires from the UI unless the user checks the box. Intentional for journal domains, but may confuse users of other domain types.

5. **Journal pattern creation is synchronous** — Loads, appends, and saves entire `patterns.json` on every entry. Will slow as patterns grow. Consider append-only storage or batching.

6. **No journal deduplication** — Same entry submitted twice creates two patterns with separate embeddings.

7. **Container restart required for code changes** — Bind-mounted `.py` files are visible in the container but Python caches imported modules. Easy to forget.

8. **app.py is ~3900 lines** — Single file contains all endpoints, startup, helpers. Could be split into route modules.
