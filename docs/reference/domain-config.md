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

  "domain_type": "4",

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

### Domain Type

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `domain_type` | string | ✅ | "1", "2", "3", "4", "5" | Determines plugin/enricher configuration |

**See:** [Domain Types Guide](docs/guides/domain-types.md)

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

## Type-Specific Fields

### Type 1: Creative Generator

```json
{
  "temperature": 0.8,
  "similarity_threshold": 0.2,
  "creative_keywords": "poem, story, write, create, compose",
  "max_patterns": 5
}
```

### Type 2: Knowledge Retrieval

```json
{
  "temperature": 0.4,
  "similarity_threshold": 0.3,
  "max_patterns": 10
}
```

### Type 3: Document Store Search

```json
{
  "temperature": 0.6,
  "similarity_threshold": 0.3,
  "document_store_type": "exframe_instance",
  "remote_url": "",
  "show_sources": true
}
```

**Plugin Config (Scope Boundaries):**
```json
{
  "plugins": [{
    "config": {
      "scope": {
        "enabled": true,
        "min_confidence": 0.0,
        "in_scope": ["Allowed topics"],
        "out_of_scope": ["Blocked topics"],
        "out_of_scope_response": "Rejection message"
      }
    }
  }]
}
```

**Scope Fields:**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | false | Enable scope checking |
| `min_confidence` | float | 0.0 | Min confidence for in-scope |
| `in_scope` | array | [] | Allowed topics |
| `out_of_scope` | array | [] | Blocked topics |
| `out_of_scope_response` | string | Default | Rejection message |

### Type 4: Analytical Engine

```json
{
  "temperature": 0.5,
  "max_research_steps": 10,
  "research_timeout": 300,
  "report_format": "structured",
  "enable_web_search": true
}
```

**Key Field:** `enable_web_search` (default: `true`)

### Type 5: Hybrid Assistant

```json
{
  "temperature": 0.5,
  "similarity_threshold": 0.3,
  "llm_min_confidence": 0.3,
  "require_confirmation": true,
  "research_on_fallback": false
}
```

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
