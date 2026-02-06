# ExFrame Release Notes

## Phase 1 - "3 Personas + Pattern Override"

**Release Date:** February 4, 2026
**Status:** Production Ready ✅

---

## Overview

Phase 1 **replaces the 5 domain types** with a simpler **3-persona system**:
- **Poet** (void) - Pure generation
- **Librarian** (library) - Document search
- **Researcher** (internet) - Web search

### Key Innovation: Pattern Override

Domains check local patterns first. If no match, fall back to persona's data source. This simple decision replaced 1000+ lines of conditional logic.

### Configuration

```json
{
  "persona": "librarian",
  "library_base_path": "/app/project/docs",
  "enable_pattern_override": true
}
```

### Phase 2: Semantic Document Search

Added semantic search for librarian persona using DocumentVectorStore:
- Single `doc_embeddings.json` per domain
- Hash-based staleness detection
- Cosine similarity search
- 60% performance improvement

---

## Version 1.6.0 - "Domain Type System" (SUPERSEDED)

> **Deprecated:** Domain types 1-5 were replaced by the Phase 1 persona system (Feb 2026).
> This release is maintained for historical reference only.

**Release Date:** January 27, 2026
**Status:** ~~Production Ready~~ **Superseded by Phase 1**

---

## Overview

ExFrame v1.6.0 introduced a domain type system with 5 archetypes. This was later superseded by the simpler 3-persona system.

---

## What's New

### 🎯 Domain Type System (LEGACY)

> **Deprecated:** Replaced by 3-persona system in Phase 1

**Legacy Feature:** 5 domain archetypes (now superseded by personas)

- **Type 1** → Use `persona: "poet"` instead
- **Type 2** → Use `persona: "librarian"` instead
- **Type 3** → Use `persona: "librarian"` instead
- **Type 4** → Use `persona: "researcher"` instead
- **Type 5** → Use `persona: "researcher"` instead

### 🎨 User Interface Improvements

- **Domain Creator UI** - Type selector with colored settings panels for each type
- **Temperature control** - Slider + number input with visual badge on query screen
- **Domain type indicator** - Shows current type (1-5) on dashboard

### 🔧 Backend Enhancements

- **DomainConfigGenerator** - Factory class creates optimized configs for each type
- **Type-specific configurations** - Each type has optimized plugins, enrichers, and settings
- **Automatic config generation** - Single source of truth for domain types

### 🐛 Bug Fixes

- **Create Pattern button** - Added missing modal for pattern creation
- **Markdown rendering** - Pattern fields now render markdown instead of raw text
- **Temperature display** - Fixed slider/number input visual mismatch
- **Domain save refresh** - Temperature badge updates immediately after saving

---

## Installation

### New Installation

```bash
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame
docker compose up -d
```

### Upgrading from v1.5.0

```bash
git pull
docker compose down
docker compose build --no-cache eeframe-app
docker compose up -d
```

**Note:** Existing domains will be automatically migrated to appropriate types.

---

## Breaking Changes

**None** - This release is fully backward compatible with v1.5.0.

---

## API Changes

### New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/domains/{domain_id}` | PUT | Update domain with type-specific config |

### Updated Endpoints

| Endpoint | Change |
|----------|--------|
| Domain create/update | Now supports `domain_type` field (1-5) |
| `/api/query` | Temperature passes through to LLM API correctly |

---

## Configuration

### Domain Type Selection

When creating a domain via UI or API, select the appropriate type:

```bash
curl -X POST http://localhost:3000/api/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": "my_knowledge_base",
    "domain_name": "My Knowledge Base",
    "domain_type": "2",
    "description": "Technical documentation and FAQs"
  }'
```

### Type-Specific Settings

Each domain type automatically configures:
- **Plugins** - Research specialist, generalist, or creative specialists
- **Enrichers** - LLM synthesis, web search, or code generation
- **Temperature** - Optimized for the use case
- **Search strategies** - Pattern-based, document-first, or web-enhanced

---

## Known Limitations

1. **Type switching** - Changing domain type requires manual verification of plugins
2. **Custom configurations** - Advanced users may want to fine-tune type defaults

**Planned Enhancements:** Type upgrade/downgrade wizard with config preview.

---

## Support

- **Issues:** https://github.com/orangelightening/ExFrame/issues
- **Documentation:** See [README.md](README.md)
- **Installation:** See [INSTALL.md](INSTALL.md)

---

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

## Version 1.5.0 - "Semantic Search"

**Release Date:** January 21, 2026
**Status:** Production Ready ✅

---

## Overview

ExFrame v1.5.0 introduces **pure semantic search** powered by SentenceTransformers, enabling the system to find patterns based on meaning rather than keyword matching. This release also includes bug fixes, documentation cleanup, and improved pattern management.

---

## What's New

### 🧠 Pure Semantic Search

**New Feature:** AI-powered semantic search using embeddings

- **Model:** all-MiniLM-L6-v2 (384-dimensional vectors)
- **Scoring:** Cosine similarity (0-1 range, higher = more related)
- **Coverage:** 100% embedding coverage across 10 domains (131 patterns)
- **Configuration:** 100% semantic, 0% keyword (fully configurable)
- **Performance:** < 100ms query response time

**Why it matters:** The system now understands meaning, not just keywords. Query "how to use a hammer?" correctly matches "hammer in a nail" even without shared keywords.

### 🔧 Pattern Creation with Code Support

**New Feature:** Patterns can now include executable code

- **New Field:** `code` field in pattern schema for storing executable code
- **Immediate Availability:** Newly created patterns are instantly searchable via semantic search
- **Auto-Embedding:** Embeddings are automatically generated when patterns are created

**API Usage:**
```bash
curl -X POST http://localhost:3000/api/patterns \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "python",
    "name": "My Pattern",
    "code": "def hello(): return 42",
    "problem": "...",
    "solution": "..."
  }'
```

### 🐛 Bug Fixes

- **JSON Serialization:** Fixed numpy float32 to Python float conversion
- **Query Bug:** Fixed unpacking error in keyword-only search path
- **Pattern Deletion:** Fixed pattern deletion and removal from embeddings
- **Duplicate Patterns:** Fixed frontend deduplication when merging patterns + candidates
- **Candidate Status:** Fixed candidates showing with red borders (now green/healthy)

### 📚 Documentation

- **Removed:** ~30 obsolete analysis and phase report documents
- **Removed:** 190MB of old React frontend code
- **Added:** `INSTALL.md` - Comprehensive installation guide
- **Updated:** `README.md` - Current feature set and usage
- **Updated:** `claude.md` - AI context recovery for development

---

## Installation

### New Installation

```bash
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame
docker compose up -d
```

### Upgrading from v1.0.0

```bash
git pull
docker compose down
docker compose build --no-cache eeframe-app
docker compose up -d
```

**Note:** Existing embeddings will be preserved. No manual migration needed.

---

## Breaking Changes

**None** - This release is fully backward compatible with v1.0.0.

---

## API Changes

### New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/embeddings/status` | GET | Check embedding coverage per domain |
| `/api/embeddings/generate` | POST | Generate embeddings for a domain |
| `/api/embeddings/weights` | POST | Adjust semantic/keyword search weights |
| `/api/patterns` | POST | Create new pattern with optional code field |

### Updated Endpoints

| Endpoint | Change |
|----------|--------|
| `/api/domains/{domain}/patterns` | Returns `_semantic_score` and `_relevance_source` in results |
| `/api/query` | Shows semantic scores in trace when enabled |

---

## Configuration

### New Environment Variables

No new environment variables required. Semantic search uses local embeddings (no API calls).

### Embedding Configuration

Semantic search is configured via API or code:

**Python (generic_framework/core/hybrid_search.py):**
```python
class HybridSearchConfig:
    semantic_weight: float = 1.0  # 100% semantic
    keyword_weight: float = 0.0   # 0% keyword
    min_semantic_score: float = 0.0
    min_keyword_score: int = 0
```

**API Adjustment:**
```bash
curl -X POST http://localhost:3000/api/embeddings/weights \
  -H "Content-Type: application/json" \
  -d '{"semantic": 1.0, "keyword": 0.0}'
```

---

## Known Limitations

1. **No feedback loop** - Pattern relevance doesn't improve with use
2. **Static embeddings** - Not updated when patterns are modified (requires manual regeneration)
3. **Fixed thresholds** - `min_semantic_score` is configurable but static
4. **No personalization** - All users get same results
5. **Token limit** - Patterns >256 tokens are truncated during embedding

**Planned Enhancements:** See `rag-search-design.md` for future improvements.

---

## Included Domains

| Domain | Patterns | Categories |
|--------|----------|------------|
| binary_symmetry | 20 | symmetry, transformation, algorithm |
| cooking | 32 | technique, recipe, cooking_method |
| diy | 10 | building, flooring, tools |
| exframe_methods | 26 | methodology, pattern, design |
| first_aid | 3 | emergency, medical, treatment |
| gardening | 3 | planting, care, harvesting |
| llm_consciousness | 12 | failure_mode, monitoring, detection |
| poetry_domain | 13 | poetic, literary, verse |
| psycho | 6 | psychology, therapy, analysis |
| python | 6 | language_feature, best_practice |

**Total:** 10 domains, 131 patterns with semantic embeddings

---

## Performance

| Metric | Value |
|--------|-------|
| Local query response time | < 100ms |
| Embedding generation | ~500ms per 100 patterns |
| Semantic similarity computation | < 50ms |
| Memory per pattern (embedding) | ~1.5 KB |
| Model size (all-MiniLM-L6-v2) | ~120 MB |

---

## Credits

**Semantic Search:** SentenceTransformers by UKP Lab
https://www.sbert.net/

**Embedding Model:** all-MiniLM-L6-v2
https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

---

## Migration Guide

### From v1.0.0 to v1.5.0

**No special migration needed.** Simply pull and restart:

```bash
git pull
docker compose down
docker compose build --no-cache eeframe-app
docker compose up -d
```

### Generate Embeddings for Existing Patterns

If upgrading from a version without semantic search:

```bash
# Generate embeddings for all domains
for domain in cooking python binary_symmetry; do
  curl -X POST "http://localhost:3000/api/embeddings/generate?domain=$domain"
done
```

---

## Support

- **Issues:** https://github.com/orangelightening/ExFrame/issues
- **Documentation:** See [README.md](README.md)
- **Installation:** See [INSTALL.md](INSTALL.md)

---

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.
