# Domain Types Guide

**Version:** 1.0
**Updated:** 2026-01-29

---

## Overview

ExFrame supports **5 domain types**, each optimized for different use cases. The type determines which plugins are loaded, how queries are processed, and what features are available.

**Key Principle:** Domain type is a **configuration preset**, not a rigid category. Changing type regenerates the entire domain configuration via `domain_factory.py`.

---

## Quick Reference

| Type | Name | Use For | Web Search | Temperature |
|------|------|---------|------------|-------------|
| **1** | Creative Generator | Poems, stories, creative content | ❌ No | 0.8 (high) |
| **2** | Knowledge Retrieval | How-to guides, FAQs, technical docs | ❌ No | 0.4 (low) |
| **3** | Document Store Search | External documentation, API docs, live data | ❌ No | 0.6 (medium) |
| **4** | Analytical Engine | Research, analysis, correlation, reports | ✅ Yes (default) | 0.5 (medium) |
| **5** | Hybrid Assistant | General purpose, flexible, user choice | ⚙️ Optional | 0.5 (medium) |

---

## Type 1: Creative Generator

**Use For:** Poems, stories, creative content, art

**Characteristics:**
- High temperature (0.8) for creative output
- Low similarity threshold (0.2) - broad pattern matching
- Creative keywords: poem, story, write, create, compose
- Max 5 patterns in results

**Plugin:**
```json
{
  "plugin_id": "creative",
  "module": "plugins.generalist",
  "class": "GeneralistPlugin",
  "config": {
    "keywords": ["poem", "story", "write", "create", "compose"],
    "threshold": 0.1
  }
}
```

**Enrichers:**
- LLMEnricher with `creative_mode: true`

**Example:** `poetry_domain`

---

## Type 2: Knowledge Retrieval

**Use For:** How-to guides, FAQs, technical documentation

**Characteristics:**
- Medium-low temperature (0.4) for factual accuracy
- Medium similarity threshold (0.3)
- Keyword-based matching
- Max 10 patterns in results

**Plugin:**
```json
{
  "plugin_id": "generalist",
  "module": "plugins.generalist",
  "class": "GeneralistPlugin",
  "config": {
    "keywords": ["how", "what", "explain", "guide"],
    "threshold": 0.2
  }
}
```

**Enrichers:**
- LLMEnricher for pattern synthesis

**Examples:** `cooking`, `python`, `first_aid`, `gardening`, `diy` (old)

---

## Type 3: Document Store Search

**Use For:** External documentation, API docs, live data

**Characteristics:**
- Medium temperature (0.6)
- Medium similarity threshold (0.3)
- Shows sources (default: true)
- Auto-discovers documents recursively
- **Scope boundaries** (per-domain, not type-specific)

**Plugin:**
```json
{
  "plugin_id": "exframe_specialist",
  "module": "plugins.exframe.exframe_specialist",
  "class": "ExFrameSpecialistPlugin",
  "config": {
    "document_store_enabled": true,
    "local_patterns_enabled": true,
    "document_store_config": {
      "type": "exframe_instance",
      "remote_url": ""
    },
    "research_strategy": {
      "type": "document",
      "base_path": "/app/project",
      "auto_discover": true,
      "file_pattern": "**/*",
      "exclude_patterns": [".git", "__pycache__", "node_modules"]
    },
    "scope": {
      "enabled": true,
      "min_confidence": 0.0,
      "in_scope": ["Allowed topics"],
      "out_of_scope": ["Blocked topics"],
      "out_of_scope_response": "This question is outside the documentation scope."
    }
  }
}
```

**Enrichers:**
- ReplyFormationEnricher with `show_sources: true`
- LLMEnricher

**Example:** `exframe`

**Key Features:**
1. **3-stage search strategy**
   - Document research (external docs, auto-discovered files)
   - Local pattern search (cached knowledge)
   - Combined results with sources

2. **Scope boundaries**
   - Reject out-of-scope queries before processing
   - Per-domain configuration (not type-specific)
   - Explicit keyword blocking
   - Framework detection (Django, Flask, etc.)
   - Relevance threshold checking

---

## Type 4: Analytical Engine ⭐

**Use For:** Research, analysis, correlation, reports, web search

**Characteristics:**
- **Two-stage query flow** (local → web)
- Medium temperature (0.5)
- **Web search enabled by default**
- Shows sources with URLs
- Max 10 research steps

**Plugin:**
```json
{
  "plugin_id": "researcher",
  "module": "plugins.research.research_specialist",
  "class": "ResearchSpecialistPlugin",
  "config": {
    "enable_web_search": true,
    "max_research_steps": 10,
    "research_timeout": 300,
    "search_provider": "auto",
    "max_results": 10,
    "timeout": 10
  }
}
```

**Enrichers:**
```json
[
  {
    "module": "plugins.enrichers.reply_formation",
    "class": "ReplyFormationEnricher",
    "config": {
      "show_sources": true,
      "show_results": true
    }
  },
  {
    "module": "plugins.enrichers.llm_enricher",
    "class": "LLMEnricher",
    "config": {
      "temperature": 0.5
    }
  }
]
```

**Two-Stage Query Flow:**

**Stage 1: Local Search (Immediate)**
1. User submits query
2. Local patterns searched immediately
3. Results returned with `can_extend_with_web_search: true`
4. UI shows "Extended Search (Internet)" button

**Stage 2: Web Search (On User Action)**
1. User clicks "Extended Search (Internet)"
2. POST to `/api/query/extend-web-search`
3. DuckDuckGo web search performed
4. Web results + local patterns combined
5. LLM synthesizes from both sources
6. Sources displayed with 🌐 emoji and URLs

**Examples:** `diy`, `cooking`

**Web Search Sources:**
- DuckDuckGo HTML search (no API key)
- 5-10 results per query
- Title, snippet, URL extracted
- Used as LLM context

---

## Type 5: Hybrid Assistant

**Use For:** General purpose, flexible, user choice

**Characteristics:**
- Medium temperature (0.5)
- Medium similarity threshold (0.3)
- LLM fallback on weak confidence
- User confirmation required (default: true)
- Research on fallback (optional)

**Plugin:**
```json
{
  "plugin_id": "hybrid",
  "module": "plugins.generalist",
  "class": "GeneralistPlugin",
  "config": {
    "threshold": 0.2
  }
}
```

**Enrichers:**
```json
{
  "module": "plugins.enrichers.llm_fallback_enricher",
  "class": "LLMFallbackEnricher",
  "config": {
    "mode": "fallback",
    "min_confidence": 0.3,
    "require_confirmation": true
  }
}
```

**Behavior:**
- Patterns shown first
- "Extend search with AI?" button if confidence < threshold
- User confirms before LLM used
- LLM appended if accepted

---

## Comparison Matrix

| Feature | Type 1 | Type 2 | Type 3 | Type 4 | Type 5 |
|---------|--------|--------|--------|--------|--------|
| **Primary Use** | Creative | Knowledge | Docs | Research | General |
| **Temperature** | 0.8 | 0.4 | 0.6 | 0.5 | 0.5 |
| **Similarity Threshold** | 0.2 | 0.3 | 0.3 | 0.3 | 0.3 |
| **Max Patterns** | 5 | 10 | 10 | 10 | 10 |
| **Web Search** | ❌ | ❌ | ❌ | ✅ Yes | ⚙️ Optional |
| **Shows Sources** | ❌ | ❌ | ✅ Yes | ✅ Yes | ❌ |
| **Specialist** | Generalist | Generalist | ExFrame | Research | Generalist |
| **LLM Fallback** | ❌ | ❌ | ❌ | ❌ | ✅ Yes |
| **User Confirmation** | ❌ | ❌ | ❌ | ❌ | ✅ Yes |

---

## Choosing a Domain Type

### Use Type 1 (Creative) when:
- Generating poems, stories, creative writing
- Output should be original and imaginative
- Factual accuracy is less important
- High variability is desired

### Use Type 2 (Knowledge) when:
- Answering how-to questions
- Providing technical documentation
- Retrieving FAQs
- Factual accuracy is important

### Use Type 3 (Document Store) when:
- Searching external documentation
- Accessing API docs
- Working with live data sources
- Need to show sources

### Use Type 4 (Analytical) when:
- Researching topics on the internet
- Analyzing information from multiple sources
- Correlating web and local knowledge
- Need fresh, up-to-date information

### Use Type 5 (Hybrid) when:
- General purpose assistance
- Want user control over LLM usage
- Prefer local knowledge first
- Need flexibility

---

## Changing Domain Type

**Important:** When you change domain_type in the UI, the **entire domain configuration is regenerated** via `domain_factory.py`.

**What Gets Regenerated:**
- `plugins[]` - New specialist plugin for the type
- `enrichers[]` - New enricher configuration
- `knowledge_base{}` - New KB settings
- Type-specific fields (temperature, thresholds, etc.)

**What Gets Preserved:**
- `domain_id`
- `domain_name` (if not changed)
- `description` (if not changed)
- `categories` (if not changed)
- `tags` (if not changed)
- `ui_config{}`
- `patterns.json` (your data is never touched)

**Example:**
```json
// Before: Type 2 (Knowledge)
{
  "domain_type": "2",
  "plugins": [{
    "module": "plugins.generalist",
    "class": "GeneralistPlugin"
  }],
  "temperature": 0.4
}

// After: Change to Type 4 (Analytical)
{
  "domain_type": "4",
  "plugins": [{
    "module": "plugins.research.research_specialist",
    "class": "ResearchSpecialistPlugin"
  }],
  "temperature": 0.5,
  "enable_web_search": true  // NEW!
}
```

---

## Type 4 Web Search Details

### DuckDuckGo Integration

**Implementation:** `InternetResearchStrategy` in `core/research/internet_strategy.py`

**Flow:**
```
Query → DuckDuckGo HTML → Parse Results → Return to Specialist
```

**URL Pattern:**
```
https://html.duckduckgo.com/html/?q={encoded_query}
```

**Result Parsing:**
- **Title:** `<a class="result__a">TITLE</a>`
- **Snippet:** `<a class="result__snippet">SNIPPET</a>`
- **URL:** Extracted from `uddg=` parameter

**No API Key Required**

### Source Display

Web search results are displayed with:
- 🌐 emoji indicator
- Clickable URLs
- Title and snippet

**Example:**
```markdown
### 🌐 Web Search: Free Dog House Plans
**Source:** https://example.com/dog-house
Detailed plans for building a dog house...
```

---

## Related Documentation

- [Domain Config Reference](docs/reference/domain-config.md) - Complete schema
- [Architecture Overview](docs/architecture/overview.md) - System architecture
- [Web Search Guide](docs/guides/web-search.md) - Using Type 4 web search
