# ExFrame Architecture Overview

**Version:** 1.0
**Updated:** 2026-01-29

---

## High-Level Architecture

ExFrame is a **plugin-based domain expert system** that processes queries through configurable pipelines.

```
User Query
    ↓
FastAPI App (app.py)
    ↓
Query Engine (engine.py)
    ↓
Specialist Selection (highest confidence)
    ↓
Specialist Plugin (process_query)
    ├─ Local Pattern Search (knowledge base)
    └─ Web Search (if Type 4 + confirmed)
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

### 3. Domain Factory (`core/domain_factory.py`)

**Purpose:** Generate domain configurations for Types 1-5

**Key Principle:** Single source of truth for domain type defaults

**Type Configurations:**
- **Type 1 (Creative)**: High temperature (0.8), creative keywords
- **Type 2 (Knowledge)**: Pattern-based retrieval, similarity threshold
- **Type 3 (Document Store)**: ExFrame specialist, document research, **scope boundaries**
- **Type 4 (Analytical)**: Research specialist, **web search enabled (default)**
- **Type 5 (Hybrid)**: LLM fallback, confirmation required

### 4. Scope Boundaries

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

**Implementations:**
- `ResearchSpecialistPlugin` (Type 4) - Two-stage query with web search
- `ExFrameSpecialistPlugin` (Type 3) - Document research + local patterns
- `GeneralistPlugin` (Types 1, 2, 5) - Keyword/category matching

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

## Type 4: Analytical Engine Architecture

### Two-Stage Query Flow

**Stage 1: Local Search (Immediate)**
```
User Query
    ↓
ResearchSpecialist.process_query(context={web_search_confirmed: false})
    ↓
Local pattern search (knowledge base)
    ↓
Return: {
    patterns: [...],
    can_extend_with_web_search: true
}
    ↓
UI: Shows "Extended Search (Internet)" button
```

**Stage 2: Web Search (On User Action)**
```
User clicks button
    ↓
POST /api/query/extend-web-search
    ↓
ResearchSpecialist.process_query(context={web_search_confirmed: true})
    ↓
InternetResearchStrategy.search()
    ├─ DuckDuckGo HTML search
    ├─ Parse results (title, snippet, URL)
    └─ Return 5-10 results
    ↓
Return: {
    research_results: [...],  # Web search results
    local_results: [...],      # Local patterns
    patterns: [...]            # Combined
}
    ↓
Enricher Pipeline:
├─ ReplyFormationEnricher: Format sources with 🌐 emoji + URLs
└─ LLMEnricher: Synthesize from web + local
    ↓
Response with sources displayed
```

### Web Search Integration

**Component:** `InternetResearchStrategy` (`core/research/internet_strategy.py`)

**Flow:**
```
Query → DuckDuckGo HTML → Parse Results → Return to Specialist
```

**Implementation:**
- Uses `html.duckduckgo.com/html/?q={query}`
- Parses HTML with regex to extract:
  - Title: `<a class="result__a">TITLE</a>`
  - Snippet: `<a class="result__snippet">SNIPPET</a>`
  - URL: Extract from `uddg=` parameter
- No API key required

---

## Data Structures

### Domain Configuration (`domain.json`)

```json
{
  "domain_id": "diy",
  "domain_name": "DIY Projects",
  "domain_type": "4",
  "plugins": [
    {
      "plugin_id": "researcher",
      "module": "plugins.research.research_specialist",
      "class": "ResearchSpecialistPlugin",
      "enabled": true,
      "config": {
        "enable_web_search": true,
        "max_research_steps": 10
      }
    }
  ],
  "enrichers": [
    {
      "module": "plugins.enrichers.reply_formation",
      "class": "ReplyFormationEnricher",
      "enabled": true,
      "config": {
        "show_sources": true,
        "show_results": true
      }
    }
  ],
  "knowledge_base": {
    "type": "json",
    "storage_path": "patterns.json"
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

### 1. Plugin-Based, Not Class-Based
- **Before:** Each domain was a custom class
- **After:** Domains are configuration, plugins are swappable
- **Benefit:** Add domains without code changes

### 2. Domain Types as Config Presets
- **Before:** Complex archetypes with workflows
- **After:** Domain type = config template
- **Benefit:** Simple, predictable, composable

### 3. Two-Stage Web Search
- **Before:** Immediate web search (no control)
- **After:** Local first, web on demand
- **Benefit:** User control, faster initial response

### 4. Single Source of Truth
- **Before:** UI and backend both defined defaults
- **After:** domain_factory.py is authoritative
- **Benefit:** No inconsistency, easier to maintain

### 5. Enricher Pipeline
- **Before:** Specialist did everything
- **After:** Specialists search, enrichers transform
- **Benefit:** Separation of concerns, composable

---

## File Locations

```
generic_framework/
├── api/
│   └── app.py                          # FastAPI, all endpoints
├── assist/
│   └── engine.py                       # Query orchestrator
├── core/
│   ├── domain.py                       # GenericDomain orchestrator
│   ├── domain_factory.py               # Type 1-5 config generator
│   ├── specialist_plugin.py            # Specialist interface
│   └── research/
│       ├── internet_strategy.py        # DuckDuckGo web search
│       └── document_strategy.py        # File discovery
├── plugins/
│   ├── research/
│   │   └── research_specialist.py      # Type 4 specialist
│   ├── exframe/
│   │   └── exframe_specialist.py       # Type 3 specialist
│   ├── generalist/
│   │   └── generalist_plugin.py        # Generalist specialist
│   └── enrichers/
│       ├── llm_enricher.py            # LLM enhancement
│       ├── reply_formation.py          # Source formatting
│       └── llm_fallback_enricher.py    # LLM fallback
└── frontend/
    └── index.html                      # Alpine.js SPA
```

---

## Extension Points

1. **New Specialist Plugin** - Implement `SpecialistPlugin` interface
2. **New Enricher Plugin** - Implement `EnricherPlugin` interface
3. **New Knowledge Base** - Implement `KnowledgeBasePlugin` interface
4. **New Domain Type** - Add method to `DomainConfigGenerator`

---

## Related Documentation

- [Plugin System](docs/architecture/plugin-system.md) - Detailed plugin architecture
- [Domain Types](docs/guides/domain-types.md) - Type 1-5 reference
- [Query Pipeline](docs/architecture/query-pipeline.md) - Detailed query flow
- [Enricher Chain](docs/architecture/enricher-chain.md) - Enricher pipeline details
