# Domain Configuration Reference

**Version:** 1.0
**Updated:** 2026-01-29

---

## Overview

Domain configuration is stored in `domain.json` files located at:

```
universes/MINE/domains/{domain_id}/domain.json
```

Each domain has:
- **One** `domain.json` file (configuration)
- **One** `patterns.json` file (pattern data)

---

## Complete Schema

```json
{
  "domain_id": "example",
  "domain_name": "Example Domain",
  "description": "What this domain covers",
  "version": "1.0.0",
  "created_at": "2026-01-09T00:00:00Z",
  "updated_at": "2026-01-09T00:00:00Z",

  "persona": "librarian",
  "library_base_path": "/app/project/docs",
  "enable_pattern_override": true,

  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "learning_log.md",
    "trigger_phrases": ["chapter", "continue"],
    "max_context_chars": 15000,
    "include_query_history": true,
    "format": "markdown"
  },

  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2"],

  "pattern_schema": {
    "required_fields": ["id", "name", "pattern_type", "problem", "solution"],
    "optional_fields": ["description", "steps", "tags", "confidence", "sources"]
  },

  "plugins": [
    {
      "plugin_id": "specialist_1",
      "name": "First Specialist",
      "description": "Specializes in X",
      "module": "plugins.example_domain.specialist_1",
      "class": "SpecialistPlugin",
      "enabled": true,
      "config": {
        "keywords": ["keyword1", "keyword2"],
        "categories": ["category1"],
        "threshold": 0.30
      }
    }
  ],

  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "enabled": true,
      "config": {
        "mode": "enhance",
        "temperature": 0.5
      }
    }
  ],

  "knowledge_base": {
    "type": "json",
    "module": "knowledge.json_kb",
    "class": "JSONKnowledgeBase",
    "storage_path": "patterns.json",
    "pattern_format": "embedded",
    "auto_save": true,
    "similarity_threshold": 0.3
  },

  "ui_config": {
    "placeholder_text": "Ask about X...",
    "example_queries": ["Example 1", "Example 2"],
    "icon": "🔍",
    "color": "#9C27B0"
  },

  "links": {
    "related_domains": [],
    "imports_patterns_from": [],
    "suggest_on_confidence_below": 0.3
  }
}
```

---

## Field Reference

### Identity Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain_id` | string | ✅ | Unique identifier (used in URLs) |
| `domain_name` | string | ✅ | Display name (shown in UI) |
| `description` | string | ✅ | What this domain covers |
| `version` | string | ✅ | Configuration version |
| `created_at` | ISO datetime | ✅ | Creation timestamp |
| `updated_at` | ISO datetime | ✅ | Last update timestamp |

### Persona Configuration (Phase 1)

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `persona` | string | ✅ | "poet", "librarian", "researcher" | AI persona that determines query processing |
| `library_base_path` | string | ❌ | "/app/project/docs" | Document library path (librarian only) |
| `enable_pattern_override` | boolean | ❌ | true/false | If true, local patterns override persona |

**Personas:**
- `poet`: Pure generation (void) - no external sources
- `librarian`: Document search (library) - searches local docs
- `researcher`: Web search (internet) - searches the web

**Pattern Override:** When enabled, the domain checks local patterns first. If patterns match, use them. Otherwise, fall back to persona's data source.

### Accumulator Configuration

**Purpose:** Enable persistent conversation memory for learning and sequential content generation

```json
"accumulator": {
  "enabled": true,
  "mode": "all",
  "output_file": "learning_log.md",
  "trigger_phrases": ["chapter", "continue"],
  "max_context_chars": 15000,
  "include_query_history": true,
  "format": "markdown"
}
```

**Fields:**
| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `enabled` | boolean | ✅ | true/false | Enable accumulator for this domain |
| `mode` | string | ✅ | "all", "triggers" | "all" = Log every query (learning)<br>"triggers" = Log on trigger phrases (stories) |
| `output_file` | string | ✅ | - | Relative path to accumulator file (from domain directory) |
| `trigger_phrases` | array | ❌ | ["chapter", "continue"] | Phrases that trigger logging in "triggers" mode |
| `max_context_chars` | integer | ❌ | 1000-100000 | Maximum characters to load from accumulator (default: 15000) |
| `include_query_history` | boolean | ❌ | true/false | Include query history in context (default: true) |
| `format` | string | ❌ | "markdown", "plain" | Output format for accumulator file (default: "markdown") |

**Modes:**
- `all`: Remember everything - Perfect for learning, research threads, project continuity
- `triggers`: Remember on demand - Perfect for novel writing, serialized content

**Use Cases:**
- **Learning domains**: Enable with mode "all" for persistent educational memory
- **Novel writing**: Enable with mode "triggers" for sequential chapter generation
- **Research threads**: Enable with mode "all" for cumulative research logs
- **Project planning**: Enable with mode "all" for ongoing project discussions

**See also:** [Accumulator Design Document](docs/ACCUMULATOR_DESIGN.md)

### Organization

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `categories` | array | ❌ | Category list for patterns |
| `tags` | array | ❌ | Tag list for patterns |

### Pattern Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pattern_schema.required_fields` | array | ✅ | Required fields in patterns |
| `pattern_schema.optional_fields` | array | ✅ | Optional fields in patterns |

### Plugins

**Purpose:** Define which specialist plugins load for this domain

```json
"plugins": [
  {
    "plugin_id": "unique_id",
    "name": "Display Name",
    "description": "What this plugin does",
    "module": "plugins.path.to.module",
    "class": "PluginClassName",
    "enabled": true,
    "config": {
      "plugin-specific": "config"
    }
  }
]
```

**Plugin Modules:**
- `plugins.generalist.generalist_plugin` → `GeneralistPlugin`
- `plugins.research.research_specialist` → `ResearchSpecialistPlugin`
- `plugins.exframe.exframe_specialist` → `ExFrameSpecialistPlugin`

### Enrichers

**Purpose:** Transform and enhance specialist responses

```json
"enrichers": [
  {
    "module": "plugins.enrichers.reply_formation",
    "class": "ReplyFormationEnricher",
    "enabled": true,
    "config": {
      "show_sources": true,
      "show_results": true
    }
  },
  {
    "module": "plugins.enrichers.llm_enricher",
    "class": "LLMEnricher",
    "enabled": true,
    "config": {
      "mode": "enhance",
      "temperature": 0.5
    }
  }
]
```

**Enricher Classes:**
- `LLMEnricher` - LLM synthesis from patterns
- `ReplyFormationEnricher` - Format sources for display
- `LLMFallbackEnricher` - LLM fallback on weak patterns

### Knowledge Base

**Purpose:** Configure pattern storage

```json
"knowledge_base": {
  "type": "json",
  "module": "knowledge.json_kb",
  "class": "JSONKnowledgeBase",
  "storage_path": "patterns.json",
  "pattern_format": "embedded",
  "auto_save": true,
  "similarity_threshold": 0.3
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Storage backend type (currently "json" only) |
| `module` | string | Python module path |
| `class` | string | Python class name |
| `storage_path` | string | Path to patterns.json |
| `similarity_threshold` | float | Minimum similarity score (0.0-1.0) |

### UI Configuration

**Purpose:** Control domain appearance in UI

```json
"ui_config": {
  "placeholder_text": "Ask about X...",
  "example_queries": ["Example 1", "Example 2"],
  "icon": "🔍",
  "color": "#9C27B0"
}
```

---

## Persona-Specific Configuration

### Poet (void)

```json
{
  "persona": "poet",
  "enable_pattern_override": true,
  "temperature": 0.8
}
```

**Use for:** Creative writing, poems, stories
**Data source:** Pure generation (no external sources)

### Librarian (library)

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

**Use for:** Technical documentation, how-to guides, API references
**Data source:** Local document library (semantic search)

### Researcher (internet)

```json
{
  "persona": "researcher",
  "enable_pattern_override": true,
  "enable_web_search": true,
  "require_confirmation": false
}
```

**Use for:** Current events, research, analysis
**Data source:** Web search (internet)

---

## Domain Factory Defaults

**File:** `generic_framework/core/domain_factory.py`

**Key Principle:** `domain_factory.py` is the **single source of truth** for type-specific defaults.

When you change `domain_type`, the factory regenerates:
- `plugins[]`
- `enrichers[]`
- `knowledge_base{}`
- Type-specific fields

**Default Values:**

| Type | Temperature | Similarity | Max Patterns | Web Search |
|------|-------------|------------|--------------|------------|
| 1 | 0.8 | 0.2 | 5 | No |
| 2 | 0.4 | 0.3 | 10 | No |
| 3 | 0.6 | 0.3 | 10 | No |
| 4 | 0.5 | 0.3 | 10 | **Yes (default)** |
| 5 | 0.5 | 0.3 | 10 | Optional |

---

## Pattern Schema

Patterns are stored in `patterns.json`:

```json
[
  {
    "id": "unique_id",
    "name": "Pattern Name",
    "pattern_type": "technique",
    "problem": "The problem this solves",
    "solution": "How to solve it",
    "description": "More details",
    "steps": ["Step 1", "Step 2"],
    "conditions": ["When to use"],
    "prerequisites": ["Required knowledge"],
    "alternatives": ["Alternative approaches"],
    "related_patterns": ["pattern_id_1"],
    "tags": ["tag1", "tag2"],
    "categories": ["category1"],
    "confidence": 0.9,
    "sources": ["Source 1"],
    "examples": ["Example 1"],
    "domain": "domain_id",
    "created_at": "2026-01-09T00:00:00Z",
    "updated_at": "2026-01-09T00:00:00Z",
    "times_accessed": 10,
    "user_rating": null,
    "origin": "user",
    "origin_query": "original query",
    "llm_generated": false,
    "status": "active"
  }
]
```

---

## File Locations

```
universes/MINE/domains/{domain_id}/
├── domain.json       # This configuration
└── patterns.json     # Pattern storage
```

---

## Related Documentation

- [Domain Types Guide](docs/guides/domain-types.md) - Type 1-5 reference
- [Architecture Overview](docs/architecture/overview.md) - System architecture
- [INDEX.md](docs/INDEX.md) - Master file index
