# ExFrame Release Notes

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
