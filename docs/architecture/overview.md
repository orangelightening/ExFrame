# ExFrame Architecture Overview

<!--
CLARIFICATION: Phase 1 Architecture (February 2026)

This document describes the current Phase 1 architecture.
Previous version (v1.6.0) used domain types 1-5 with specialist plugins.

Key Changes:
- 5 domain types → 3 personas (poet/librarian/researcher)
- Complex plugin routing → Simple pattern override decision
- Type-specific specialists → Persona data sources (void/library/internet)
- 1000+ lines → 20 lines of query processing logic

The old plugin-based specialist system is still present in the codebase for
backward compatibility but is no longer the recommended approach.

See CHANGELOG.md Phase 1 section for complete migration guide.
-->

**Version:** 2.0 (Phase 1)
**Updated:** 2026-02-05

> **Architecture Change:** This document has been updated to reflect the Phase 1 persona system.
> Domain Types 1-5 (v1.6.0) were replaced with 3 Personas + Pattern Override.

---

## High-Level Architecture

ExFrame is a **persona-based knowledge system** that processes queries through configurable pipelines with pattern override capability.

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

---

## Core Components

### 1. GenericDomain (`core/domain.py`)

**Purpose:** Universal domain orchestrator

**Responsibilities:**
- Load `domain.json` configuration
- Initialize knowledge base plugin
- Load specialist plugins
- Load enricher plugins
- Route queries to appropriate specialist

**Key Methods:**
```python
async def initialize()     # Load config, plugins, patterns
async def process_query()  # Route to specialist, run enrichers
async def enrich()          # Apply enricher pipeline
```

### 2. Query Engine (`assist/engine.py`)

**Purpose:** Query orchestration and response building

**Pipeline:**
1. **Specialist Selection** - Find best specialist by confidence score
2. **Query Processing** - Specialist processes query, returns results
3. **Enricher Pipeline** - Apply enrichers (formatting, LLM, fallback)
4. **Response Building** - Assemble final response

**Data Flow:**
```python
query → specialist → response_data → enrichers → final_response
                       ↓
                [patterns, research_results, local_results]
                       ↓
                       enricher_input (includes research_results)
                       ↓
                LLMEnricher (uses web search context)
```

### 3. Persona System (`core/personas.py`)

**Purpose:** Define the three AI personas that determine query processing behavior

**Key Principle:** Simple decision tree - check patterns first, then use persona

**Persona Configurations:**
- **Poet (void)**: Pure LLM generation, no external sources, temperature 0.8
- **Librarian (library)**: Searches local document library with semantic search
- **Researcher (internet)**: Web search capability for current information

**Pattern Override:**
```python
if local_patterns_match:
    use local_patterns
else:
    use persona.data_source  # void/library/internet
```

### 4. Domain Factory (`core/domain_factory.py`)

**Status:** Legacy - Maintained for backward compatibility with domain types 1-5

**Note:** New domains should use `persona` field directly instead of `domain_type`

### 5. Scope Boundaries

**Purpose:** Per-domain rejection of out-of-scope queries

**Implementation:** `plugins/exframe/exframe_specialist.py`

**Flow:**
```
Query → Specialist checks scope → Out of scope? → Reject with message
                                      ↓ No
                                  Process normally
```

**Configuration:** `plugins[0].config.scope` in `domain.json`
```json
{
  "scope": {
    "enabled": true,
    "min_confidence": 0.0,
    "in_scope": ["Allowed topics"],
    "out_of_scope": ["Blocked topics"],
    "out_of_scope_response": "Rejection message"
  }
}
```

**Key Principle:** Per-domain, not domain-type specific. Each domain configures its own boundaries.

---

## Plugin Architecture

### Specialist Plugins

**Interface:** `core/specialist_plugin.py`

**Three Methods:**
```python
can_handle(query: str) → float          # Can I handle this? (0.0-1.0)
process_query(query, context) → Dict     # Process and return results
format_response(response_data) → str    # Format for display
```

**Implementations (Legacy):**
- Pattern-based specialists (when enable_pattern_override: true)
- Persona data sources replace specialist plugins in Phase 1

**Current Architecture:**
- Domains use `persona` field to determine behavior
- Pattern override checks local patterns first
- No specialist plugins needed for persona-based domains

### Enricher Plugins

**Interface:** `core/enrichment_plugin.py`

**Method:**
```python
enrich(response_data, context) → Dict    # Transform/enhance response
```

**Pipeline Order:**
1. **ReplyFormationEnricher** - Format web sources with URLs
2. **LLMEnricher** - Synthesize response from web + local patterns
3. **LLMFallbackEnricher** (Type 5) - Fallback when patterns weak

---

## Phase 1: Persona-Based Architecture

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

**Persona Data Sources:**

**Poet (void):**
```
Query → Pure LLM Generation → Response
(No external sources)
```

**Librarian (library):**
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

**Researcher (internet):**
```
Query → Web Search (DuckDuckGo)
    ↓
Parse results (title, snippet, URL)
    ↓
LLM synthesis with web context
    ↓
Response with sources
```

### Document Search (Librarian)

**Component:** `DocumentVectorStore` (`core/document_embeddings.py`)

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

**Performance:**
- Old: Load 50 files in filesystem order (~500ms)
- New: Compare embeddings + load 10 relevant (~200ms)
- Result: 60% faster + better relevance

---

## Data Structures

### Domain Configuration (`domain.json`)

**Phase 1 Configuration:**
```json
{
  "domain_id": "exframe",
  "domain_name": "ExFrame Guide",
  "persona": "librarian",
  "library_base_path": "/app/project",
  "enable_pattern_override": true,
  "document_search": {
    "algorithm": "semantic",
    "max_documents": 10,
    "min_similarity": 0.3,
    "auto_generate_embeddings": true
  },
  "enrichers": [
    {
      "module": "plugins.enrichers.reply_formation",
      "class": "ReplyFormationEnricher",
      "enabled": true,
      "config": {
        "show_sources": true
      }
    },
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

### Pattern Structure (`patterns.json`)

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

### Query Response (Stage 1: Local Only)

```json
{
  "query": "build me a dog house",
  "response": "Building a dog house is a fantastic project...",
  "specialist": "researcher",
  "patterns_used": ["diy_001", "diy_002"],
  "confidence": 0.78,
  "llm_used": true,
  "llm_enhancement": "Full AI response...",
  "can_extend_with_web_search": true
}
```

### Extended Search Response (Stage 2: Web + Local)

```json
{
  "query": "build me a dog house",
  "response": "### 🌐 Web Search: Free Dog House Plans\n**Source:** https://example.com...",
  "specialist": "researcher",
  "patterns_used": ["web_0", "web_1", "diy_001"],
  "confidence": 0.85,
  "llm_used": true,
  "llm_enhancement": "Based on web search results...",
  "research_results": [
    {
      "title": "Free Dog House Plans",
      "content": "Detailed plans...",
      "url": "https://example.com/dog-house"
    }
  ]
}
```

---

## Key Design Decisions

### Phase 1: Persona System

**1. Simple Decision Tree**
- **Before:** 1000+ lines of conditional logic across domain types
- **After:** ONE decision - patterns or persona
- **Impact:** 98% reduction in query processing code

**2. Three Personas Replace Five Types**
- **Before:** Types 1-5 with complex configurations
- **After:** poet/librarian/researcher with clear data sources
- **Benefit:** Easier to understand, configure, and maintain

**3. Pattern Override**
- **Before:** Complex routing logic
- **After:** Check patterns first, fall back to persona
- **Benefit:** Hybrid domains with curated + dynamic content

**4. Semantic Document Search**
- **Before:** Load 50 files in filesystem order
- **After:** Search embeddings, load top 10 relevant
- **Benefit:** 60% faster, better relevance

**5. Configuration Over Code**
- **Before:** domain_factory.py generates complex configs
- **After:** Simple persona field in domain.json
- **Benefit:** No code changes for new domains

### Legacy Design Decisions (Pre-Phase 1)

**1. Plugin-Based Architecture**
- Still used for enrichers and formatters
- Specialist plugins largely replaced by persona system

**2. Enricher Pipeline**
- **Still current:** Specialists/personas search, enrichers transform
- **Benefit:** Separation of concerns, composable

---

## File Locations

```
generic_framework/
├── api/
│   └── app.py                          # FastAPI, all endpoints
├── core/
│   ├── query_processor.py              # Phase 1 query processor
│   ├── personas.py                     # POET, LIBRARIAN, RESEARCHER
│   ├── persona.py                      # Persona dataclass
│   ├── phase1_engine.py                # Phase 1 orchestrator
│   ├── domain.py                       # GenericDomain orchestrator
│   ├── domain_factory.py               # Legacy - Type 1-5 config generator
│   ├── document_embeddings.py          # DocumentVectorStore for librarian
│   └── research/
│       ├── internet_strategy.py        # Web search for researcher
│       └── document_strategy.py        # Document discovery for librarian
├── plugins/
│   └── enrichers/
│       ├── llm_enricher.py            # LLM enhancement
│       └── reply_formation.py          # Source formatting
└── frontend/
    └── index.html                      # Alpine.js SPA
```

---

## Extension Points

### Current (Phase 1)
1. **New Persona** - Add to `core/personas.py` with data source
2. **New Enricher Plugin** - Implement `EnricherPlugin` interface
3. **Document Search Strategy** - Extend DocumentVectorStore

### Legacy
1. **New Specialist Plugin** - For pattern-based domains (legacy)
2. **New Domain Type** - domain_factory.py (backward compatibility only)

---

## Related Documentation

- [PLUGIN_ARCHITECTURE.md](../../PLUGIN_ARCHITECTURE.md) - Plugin development guide
- [README.md](../../README.md) - Persona system overview
- [CHANGELOG.md](../../CHANGELOG.md) - Phase 1 release notes
- [docs/reference/domain-config.md](../reference/domain-config.md) - Domain configuration reference
