# ExFrame Architecture

> **⚠️ IMPORTANT:** This is the CURRENT and AUTHORITATIVE architecture document for ExFrame v1.6.1.
>
> **DO NOT confuse with:**
> - `PLUGIN_ARCHITECTURE.md` (old, to be archived)
> - `ZAI_WEB_SEARCH_ARCHITECTURE.md` (old, to be archived)
> - `statemachine-design.md` (content consolidated here)
>
> **This file consolidates all architecture documentation.**

**Version:** 1.7.0
**Last Updated:** 2026-02-12
**Status:** Production (Phase 1 Persona System)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Plugin Architecture](#plugin-architecture)
3. [Persona System (Phase 1)](#persona-system-phase-1)
4. [State Machine](#state-machine)
5. [Multi-Turn API & Web Search](#multi-turn-api--web-search)
6. [Semantic Document Search](#semantic-document-search)
7. [Data Structures](#data-structures)
8. [Request/Response Flow](#requestresponse-flow)
9. [File Locations](#file-locations)
10. [Extension Points](#extension-points)

---

## System Overview

ExFrame is a **persona-based knowledge system** that processes queries through configurable pipelines with pattern override capability.

### High-Level Architecture

```
User Query
    ↓
FastAPI App (app.py)
    ↓
Query Processor (Phase 1)
    ↓
Pattern Override Decision
    ├─ Local Patterns Found? → Use Patterns
    └─ No Patterns? → Use Persona Data Source
    ↓
Persona Data Source
    ├─ Poet → Pure Generation (void)
    ├─ Librarian → Document Search (library)
    └─ Researcher → Web Search (internet)
    ↓
Enricher Pipeline
    ├─ ReplyFormationEnricher (format sources)
    └─ LLMEnricher (synthesize response)
    ↓
Response to User
```

### Key Principle

> **Data and composition are configuration. All transformation logic is pluggable.**

This means:
- ✅ **Patterns** are data (JSON files, not code)
- ✅ **Domains** are orchestrators (configuration, not plugins)
- ✅ **Personas** define behavior (poet/librarian/researcher)
- ✅ **Enrichers** are plugins (transformation logic)

---

## Plugin Architecture

### Core Philosophy

ExFrame separates concerns into three layers:

| Aspect | Approach | Benefit |
|--------|----------|---------|
| **Knowledge** | JSON data files | Easy to edit, version control, review |
| **Composition** | Domain configuration | No code changes to add domains |
| **Transformation** | Plugin system | Extensible, testable, swappable |

### Specialist Plugins

**Interface:** `core/specialist_plugin.py`

**Three Methods:**
```python
from abc import ABC, abstractmethod

class SpecialistPlugin(ABC):
    """A specialist answers questions in its domain."""

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """Can this specialist handle the query? Returns 0.0-1.0"""
        pass

    @abstractmethod
    async def process_query(self, query: str, context: Dict) -> Dict:
        """Process the query. Returns dict with answer, patterns, confidence"""
        pass

    @abstractmethod
    def format_response(self, response_data: Dict) -> str:
        """Format response for user. Returns string to display"""
        pass
```

**Note:** In Phase 1, specialist plugins are largely replaced by the persona system. Domains use `persona` field instead of specialist plugins for standard behavior.

### Enricher Plugins

**Interface:** `core/enrichment_plugin.py`

**Method:**
```python
class EnricherPlugin(ABC):
    @abstractmethod
    async def enrich(self, response_data: Dict, context: Dict) -> Dict:
        """Transform/enhance response data"""
        pass
```

**Built-in Enrichers:**
- **ReplyFormationEnricher** - Format web sources with URLs
- **LLMEnricher** - Synthesize response from web + local patterns
- **LLMFallbackEnricher** - Fallback when patterns weak

---

## Persona System (Phase 1)

### Overview

Phase 1 replaced the complex domain type system (Types 1-5) with three simple personas:

| Persona | Data Source | Use Case | Temperature |
|---------|-------------|----------|-------------|
| **Poet** | void | Creative writing, poems, stories | 0.8 |
| **Librarian** | library | Technical documentation, how-to guides | 0.6 |
| **Researcher** | internet | Current events, research, recipes | 0.5 |

### Pattern Override Flow

**Decision Tree:**
```
User Query
    ↓
search_patterns=true? ──┐
    ↓ yes                │ no
Local Patterns?         │
    ↓ yes    ↓ no       │
  Use      Use          │
Patterns  Persona ◄─────┘
```

### Persona Configurations

#### Poet (void)

```json
{
  "persona": "poet",
  "enable_pattern_override": true
}
```

**Behavior:** Pure LLM generation, no external sources

**Flow:**
```
Query → Pure LLM Generation → Response
```

#### Librarian (library)

```json
{
  "persona": "librarian",
  "library_base_path": "/app/project/docs",
  "enable_pattern_override": true,
  "document_search": {
    "algorithm": "semantic",
    "max_documents": 10,
    "min_similarity": 0.3,
    "auto_generate_embeddings": true
  }
}
```

**Behavior:** Searches local document library with semantic search

**Flow:**
```
Query → Semantic Document Search
    ↓
Find relevant docs (doc_embeddings.json)
    ↓
Load top 10 documents
    ↓
LLM synthesis with doc context
    ↓
Response with sources
```

**Performance:**
- Old: Load 50 files in filesystem order (~500ms)
- New: Compare embeddings + load 10 relevant (~200ms)
- Result: 60% faster + better relevance

#### Researcher (internet)

```json
{
  "persona": "researcher",
  "enable_pattern_override": true,
  "enable_web_search": true
}
```

**Behavior:** Web search with DuckDuckGo + source verification

**Flow:**
```
Query → Web Search (DuckDuckGo)
    ↓
Parse results (title, snippet, URL)
    ↓
Fetch full page content (top 3, 3000 chars each)
    ↓
LLM synthesis with web context
    ↓
Response with clickable source URLs
```

### Role Context

The `role_context` field in `domain.json` is the **system message** sent to the LLM on every query. It defines how the AI behaves for a specific domain.

- Stored in `domain.json` as a first-class config field
- Always loaded by `query_processor.py` and injected into the context dict
- Used as the OpenAI `system` message (or prepended to the prompt for Anthropic-format APIs)
- Independent of conversation memory mode — never skipped
- Falls back to `"You are a helpful assistant."` if not set

**Example (Peter journal domain):**
```json
{
  "role_context": "You are Peter's secretary. For queries starting with **, answer from the journal. For all other queries, timestamp and echo back.",
  "persona": "poet"
}
```

### Conversation Memory

**Location:** `generic_framework/core/query_processor.py`

Conversation memory loads previous interactions from `domain_log.md` into the LLM context. Loading is controlled per-domain by the `conversation_memory` config:

```json
{
  "conversation_memory": {
    "enabled": true,
    "mode": "question",
    "max_context_chars": 5000,
    "trigger_phrases": ["**"]
  }
}
```

**Four modes available:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| `"all"` | Load for every query | Domains needing full context always |
| `"triggers"` | Load only when trigger phrases match | Selective context loading |
| `"question"` | Load only when query starts with `**` | Journal domains with question support |
| `"journal"` | Never load | Pure logging, maximum speed |

**Important:** Conversation memory is separate from `role_context`. Role context always loads. Memory loading is optional and mode-dependent.

### Per-Domain LLM Config

**Location:** `domain.json` → `llm_config` field

Each domain can override the global LLM provider/model. This enables running lightweight local models (e.g., Ollama) for simple domains while keeping cloud models for complex ones.

```json
{
  "llm_config": {
    "base_url": "http://host.docker.internal:11434/v1",
    "model": "mistral:7b",
    "api_key": "ollama"
  }
}
```

**Fields:**
- **`base_url`** — LLM API endpoint (Ollama, OpenAI, z.ai, DeepSeek, etc.)
- **`model`** — Model name
- **`api_key`** — API key (Ollama uses "ollama" as placeholder)

**Fallback:** Domains without `llm_config` use global env vars (`OPENAI_BASE_URL`, `LLM_MODEL`, `OPENAI_API_KEY`).

**Flow:** `domain.json` → `query_processor` (injects into context) → `persona._call_llm` (reads from context before env vars)

**Compatibility:** Ollama, OpenAI, z.ai (GLM), DeepSeek, and any OpenAI-compatible API.

---

## State Machine

### Consolidated QueryState Enum

**Design Principle:** Each state represents substantive work, not just logging markers.

```python
class QueryState(Enum):
    """Consolidated query lifecycle states (6 core states)"""

    # Entry States
    QUERY_RECEIVED = "QUERY_RECEIVED"  # Query received, direct prompt check
    DIRECT_LLM = "DIRECT_LLM"          # Direct LLM bypass (// prefix)

    # Processing States
    ROUTING_SELECTION = "ROUTING_SELECTION"     # Specialist scoring
    SPECIALIST_PROCESSING = "SPECIALIST_PROCESSING"  # Search + response
    ENRICHERS_EXECUTED = "ENRICHERS_EXECUTED"    # LLM/enrichment

    # Terminal States
    COMPLETE = "COMPLETE"       # Query complete
    ERROR = "ERROR"             # Error occurred
    LOG_AND_EXIT = "LOG_AND_EXIT"  # Early exit (out of scope)
```

### Normal Query Flow

```
QUERY_RECEIVED
  └─→ ROUTING_SELECTION
       └─→ SPECIALIST_PROCESSING
            └─→ ENRICHERS_EXECUTED
                 └─→ COMPLETE
```

**Total states: 5** (down from 15 in pre-Phase 1)

### Direct Prompt Flow

```
QUERY_RECEIVED (direct_prompt=true)
  └─→ DIRECT_LLM
       └─→ COMPLETE
```

### State Data Dictionary

| State | Data Fields |
|-------|-------------|
| `QUERY_RECEIVED` | `query`, `original_query`, `include_trace`, `direct_prompt` |
| `ROUTING_SELECTION` | `specialists_available`, `selected_specialist`, `specialist_scores` |
| `SPECIALIST_PROCESSING` | `specialist`, `specialist_name`, `patterns_found` |
| `ENRICHERS_EXECUTED` | `enricher`, `input_size`, `output_size`, `duration_ms` |
| `COMPLETE` | `query_id`, `processing_time_ms`, `llm_used`, `confidence`, `response_size` |
| `DIRECT_LLM` | `model`, `endpoint` |
| `ERROR` | `error_type`, `error_message` |
| `LOG_AND_EXIT` | `reason`, `specialist` |

---

## Multi-Turn API & Web Search

### Multi-Turn Function Calling

GLM-4.7 supports function calling that requires multi-turn conversation:

**Step 1: Initial Request**
```python
messages = [{"role": "user", "content": "Weather in Nanaimo?"}]
tools = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        }
    }
}]

payload = {
    "model": "glm-4.7",
    "messages": messages,
    "tools": tools,
    "tool_choice": "auto"
}
```

**Step 2: GLM Returns tool_calls**
```python
# Response has tool_calls, not content
message = response.choices[0].message
tool_call = message.tool_calls[0]
# tool_call.function.arguments = '{"query": "weather Nanaimo BC"}'
```

**Step 3: Execute DuckDuckGo Search**
```python
search_strategy = InternetResearchStrategy({})
search_results = await search_strategy.search(function_args["query"], limit=5)
```

**Step 4: Fetch Full Page Content**
```python
# Fetch top 3 results, extract 3000 chars each
async with httpx.AsyncClient(timeout=15.0) as web_client:
    for result in search_results[:3]:
        response = await web_client.get(result['url'])
        text_content = extract_text(response.text)
        page_preview = text_content[:3000]
```

**Step 5: Send Tool Response**
```python
messages.append({
    "role": "tool",
    "tool_call_id": tool_call["id"],
    "content": formatted_search_results
})

# Get final answer
response = await client.post(endpoint, json=payload)
```

### Web Search Configuration

**Environment Variables (.env):**
```bash
OPENAI_API_KEY=your_zai_api_key
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
LLM_MODEL=glm-4.7
LOG_LEVEL=INFO
```

**Domain Configuration (Researcher):**
```json
{
  "persona": "researcher",
  "enable_web_search": true
}
```

### Tool Choice Modes

- **`tool_choice="required"`** - Must use tool (researcher persona)
- **`tool_choice="auto"`** - GLM decides if tool needed (casual queries)

### Source Verification

**UI shows clickable sources:**
```
📚 Sources (verify at these URLs):
✓ https://example.com/recipe1
✓ https://example.com/recipe2
✓ https://example.com/recipe3
```

**Backend response:**
```json
{
  "response": "Complete answer...",
  "web_search_used": true,
  "sources": [
    {"title": "Recipe", "url": "https://..."}
  ]
}
```

---

## Semantic Document Search

### DocumentVectorStore

**Component:** `core/document_embeddings.py`

**Purpose:** Semantic search for librarian persona document loading

**Flow:**
```
Query → Semantic Search (cosine similarity)
    ↓
Rank documents by relevance
    ↓
Load top N documents (default 10)
    ↓
Pass to LLM enricher
```

**Embedding Cache Format:**
```json
{
  "model": "all-MiniLM-L6-v2",
  "generated_at": "2026-02-04T18:00:00Z",
  "documents": {
    "/app/project/docs/intro.md": {
      "embedding": [0.123, -0.456, ...],
      "file_hash": "abc123...",
      "size": 1024,
      "modified_at": "2026-02-04T17:00:00Z"
    }
  }
}
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
- Initial: ~2-5 seconds for 100 documents (one-time)
- Incremental: ~50ms per new/modified document
- Cached: ~10ms to load from disk

---

## Data Structures

### Domain Configuration (domain.json)

**Complete Schema:**
```json
{
  "domain_id": "example",
  "domain_name": "Example Domain",
  "description": "What this domain covers",
  "version": "1.0.0",
  "created_at": "2026-01-09T00:00:00Z",
  "updated_at": "2026-01-09T00:00:00Z",

  "role_context": "You are a helpful librarian...",
  "persona": "librarian",
  "library_base_path": "/app/project/docs",
  "enable_pattern_override": true,

  "llm_config": {
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4",
    "api_key": "sk-..."
  },

  "conversation_memory": {
    "enabled": true,
    "mode": "all",
    "max_context_chars": 5000,
    "trigger_phrases": []
  },

  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "learning_log.md",
    "trigger_phrases": ["chapter", "continue"],
    "max_context_chars": 15000,
    "include_query_history": true,
    "format": "markdown"
  },

  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "enabled": true,
      "config": {
        "mode": "enhance",
        "temperature": 0.6
      }
    }
  ],

  "knowledge_base": {
    "type": "json",
    "storage_path": "patterns.json",
    "pattern_format": "embedded",
    "auto_save": true
  }
}
```

### Pattern Structure (patterns.json)

```json
[
  {
    "id": "diy_001",
    "name": "Build a Dog House",
    "pattern_type": "how_to",
    "problem": "Need outdoor shelter for pet",
    "solution": "Step-by-step construction guide...",
    "tags": ["dog", "housing", "carpentry"],
    "confidence": 0.9
  }
]
```

---

## Request/Response Flow

### Query Request

```json
POST /api/query
{
  "query": "build me a dog house",
  "domain": "diy",
  "format": "markdown",
  "include_trace": false
}
```

### Query Response (Librarian)

```json
{
  "query": "build me a dog house",
  "response": "Building a dog house is a fantastic project...",
  "specialist": "librarian",
  "patterns_used": ["diy_001", "diy_002"],
  "documents_used": [
    {
      "path": "/app/docs/dog-house.md",
      "similarity_score": 0.87
    }
  ],
  "confidence": 0.78,
  "llm_used": true
}
```

### Web Search Response (Researcher)

```json
{
  "query": "chicken shawarma recipe",
  "response": "### 🌐 Web Search Results\nHere's an authentic recipe...",
  "specialist": "researcher",
  "web_search_used": true,
  "sources": [
    {"title": "Chicken Shawarma", "url": "https://example.com/recipe1"}
  ],
  "confidence": 0.85
}
```

---

## File Locations

```
generic_framework/
├── api/
│   └── app.py                          # FastAPI, all endpoints
├── core/
│   ├── phase1_engine.py                # Phase 1 engine wrapper
│   ├── query_processor.py              # Phase 1 query processor
│   ├── personas.py                     # POET, LIBRARIAN, RESEARCHER
│   ├── persona.py                      # Persona class (LLM calls, prompt building)
│   ├── domain.py                       # GenericDomain orchestrator
│   ├── domain_factory.py               # Legacy - Type 1-5 config
│   ├── document_embeddings.py          # DocumentVectorStore
│   └── research/
│       ├── internet_strategy.py        # DuckDuckGo web search
│       └── document_strategy.py        # Document discovery
├── plugins/
│   └── enrichers/
│       ├── llm_enricher.py            # LLM enhancement
│       └── reply_formation.py          # Source formatting
└── frontend/
    └── index.html                      # Alpine.js SPA

universes/MINE/domains/{domain_id}/
├── domain.json       # Domain configuration
├── patterns.json     # Pattern storage
└── doc_embeddings.json # Document embeddings (librarian)
```

---

## Extension Points

### Current (Phase 1)

1. **New Persona** - Add to `core/personas.py` with data source
2. **New Enricher Plugin** - Implement `EnricherPlugin` interface
3. **Document Search Strategy** - Extend DocumentVectorStore

### Legacy

1. **New Specialist Plugin** - For pattern-based domains (backward compatibility)
2. **New Domain Type** - domain_factory.py (backward compatibility only)

---

## Key Design Decisions

### Phase 1: Persona System

1. **Simple Decision Tree**
   - Before: 1000+ lines of conditional logic
   - After: ONE decision - patterns or persona
   - Impact: 98% reduction in query processing code

2. **Three Personas Replace Five Types**
   - Before: Types 1-5 with complex configs
   - After: poet/librarian/researcher with clear data sources
   - Benefit: Easier to understand, configure, maintain

3. **Pattern Override**
   - Before: Complex routing logic
   - After: Check patterns first, fall back to persona
   - Benefit: Hybrid domains with curated + dynamic content

4. **Semantic Document Search**
   - Before: Load 50 files in filesystem order
   - After: Search embeddings, load top 10 relevant
   - Benefit: 60% faster, better relevance

5. **Configuration Over Code**
   - Before: domain_factory.py generates complex configs
   - After: Simple persona field in domain.json
   - Benefit: No code changes for new domains

---

## Related Documentation

- **README.md** - User-facing guide
- **CHANGELOG.md** - Version history
- **INDEX.md** - Documentation navigation
- **development-plan.md** - Current work and tasks

---

**End of Architecture Document**
