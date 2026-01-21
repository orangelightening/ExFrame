# EEFrame - Context for Claude (AI Assistant)

**Purpose**: Complete context for resuming work on the EEFrame project.
**Last Updated**: 2026-01-20
**Status**: Semantic Search Fully Implemented - Ready for Release
**Version**: 1.5.0

---

## CURRENT STATE (2026-01-20)

### Semantic Search Implementation - COMPLETE ✅

Pure semantic search is now fully operational across all domains:

- **Implementation**: 100% semantic similarity (0% keyword component)
- **Model**: all-MiniLM-L6-v2 (384-dimensional vectors)
- **Coverage**: All 10 domains have 100% embedding coverage
- **Scoring**: Cosine similarity (0-1 range) visible in traces
- **Status**: Production ready

### Domain Embedding Coverage

| Domain | Patterns | Embeddings | Coverage |
|--------|----------|------------|----------|
| binary_symmetry | 20 | 20 | ✅ 100% |
| cooking | 32 | 32 | ✅ 100% |
| diy | 10 | 10 | ✅ 100% |
| exframe_methods | 26 | 26 | ✅ 100% |
| first_aid | 3 | 3 | ✅ 100% |
| gardening | 3 | 3 | ✅ 100% |
| llm_consciousness | 12 | 12 | ✅ 100% |
| poetry_domain | 13 | 13 | ✅ 100% |
| psycho | 6 | 6 | ✅ 100% |
| python | 6 | 6 | ✅ 100% |

**Total**: 131 patterns, all with semantic embeddings

### Recent Fixes (2026-01-20)

1. **JSON Serialization Fix** - Convert numpy float32 to Python float
   - Fixed in `generic_framework/knowledge/json_kb.py:404`
   - Ensures semantic scores are JSON serializable

2. **Query Bug Fix** - Fixed unpacking error in keyword-only search
   - Fixed in `generic_framework/knowledge/json_kb.py:415-425`
   - Corrected pattern/score unpacking for keyword results

3. **Length Protection** - Pattern truncation for token limit
   - Added in `generic_framework/core/embeddings.py:104-164`
   - Warns when patterns exceed 256 tokens (all-MiniLM-L6-v2 limit)
   - Prioritizes name + solution fields when truncating

---

## QUICK RECOVERY GUIDE

### What is EEFrame?

**EEFrame** (ExFrame) is a domain-agnostic AI-powered knowledge management system with:
- Universe-based architecture (portable knowledge environments)
- Plugin-based pipeline (Router → Specialist → Enricher → Formatter)
- Pattern-based knowledge representation
- Pure semantic search using embeddings

### How Semantic Search Works

```
Query → Encode to embedding (384-dim) → Compare with all pattern embeddings
       → Rank by cosine similarity → Return top patterns with scores
```

**Key Characteristics**:
- No keyword matching (100% semantic)
- Scores 0-1 (higher = more semantically related)
- Visible in traces with `relevance_source: "semantic"`
- Whole document embedding (no chunking)

### Example: Semantic Search Results

Query: "How do I use a hammer?"

| Pattern | Semantic Score | Source |
|---------|---------------|--------|
| How do I hammer in a nail? | 0.7007 | semantic |
| How do I build a simple shelf? | 0.2882 | semantic |
| Laying the Foundation: How to Build a Floor | 0.1542 | semantic |
| Wall and Floor Construction Basics | 0.1314 | semantic |
| Choosing and Installing DIY Flooring | 0.0912 | semantic |

**Note**: "hammer in a nail" has highest semantic similarity to "use a hammer" even though the word "hammer" appears in both - the model understands the meaning, not just keywords.

---

## CRITICAL FILES

### Semantic Search Implementation

| File | Purpose | Key Changes |
|------|---------|-------------|
| `generic_framework/core/embeddings.py` | Embedding generation | Length protection, whole document encoding |
| `generic_framework/core/hybrid_search.py` | Hybrid search engine | Pure semantic mode (semantic_weight=1.0) |
| `generic_framework/knowledge/json_kb.py` | Knowledge base | Semantic search integration, JSON fix |
| `generic_framework/assist/engine.py` | Query engine | Semantic scores in traces |

### Design Documentation

| File | Purpose | Status |
|------|---------|--------|
| `rag-search-design.md` | Semantic search design | Complete, up-to-date |
| `query-rewrite.md` | Knowledge Dashboard spec | Complete, awaiting implementation |
| `query-todo.md` | Query system todos | Ready for implementation |

---

## SYSTEM ARCHITECTURE

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    EEFRAME APPLICATION                       │
├─────────────────────────────────────────────────────────────┤
│  1. Universe Manager                                         │
│     - Multi-universe support                                 │
│     - Domain auto-discovery                                  │
│     - Pattern storage (JSON files)                           │
│                                                              │
│  2. Query Pipeline                                           │
│     - Specialist Router                                      │
│     - Knowledge Base (JSON with semantic search)             │
│     - Enrichers (LLM, related patterns, code)                │
│     - Formatters (Markdown, JSON, HTML)                      │
│                                                              │
│  3. Semantic Search                                          │
│     - Embedding service (all-MiniLM-L6-v2)                  │
│     - Vector store (embeddings.json)                         │
│     - Cosine similarity ranking                              │
│                                                              │
│  4. Web Dashboard                                            │
│     - Query interface with semantic results                 │
│     - Pattern browser with health indicators                │
│     - Trace inspector for debugging                         │
│     - Domain management                                      │
│     - Diagnostics dashboard                                  │
└─────────────────────────────────────────────────────────────┘
```

### Plugin Architecture

**Pipeline**: Query → Router → Specialist → Enrichers → Formatter → Response

**Plugin Types**:
1. **Router Plugins** - Determine query handling strategy
2. **Specialist Plugins** - Domain expertise (3 methods: can_handle, process_query, format_response)
3. **Knowledge Base Plugins** - Pattern storage (JSON, SQLite)
4. **Enricher Plugins** - Response enhancement (LLM, related patterns, code generation)
5. **Formatter Plugins** - Output format (Markdown, JSON, HTML, Slack)

---

## INSTALLATION & DEPLOYMENT

### Prerequisites

**Required**:
- Docker Engine (official, NOT snap)
- Docker Compose v2
- Git

**Optional** (for LLM features):
- LLM API key (GLM, OpenAI, Anthropic, etc.)

### Quick Start

```bash
# Clone repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# Configure environment (optional - for LLM features)
cp .env.example .env
nano .env  # Edit with your API key

# Start application
docker compose up -d

# Access application
# Main UI: http://localhost:3000
# API Docs: http://localhost:3000/docs
# Health: http://localhost:3000/health
```

### LLM Configuration (.env)

**For GLM (z.ai) - RECOMMENDED**:
```bash
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-glm-key-here
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

**For OpenAI GPT**:
```bash
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**For Anthropic Claude**:
```bash
LLM_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=sk-ant-your-anthropic-api-key-here
OPENAI_BASE_URL=https://api.anthropic.com/v1
```

---

## DOMAIN MANAGEMENT

### Current Domains

| Domain | Patterns | Specialists | Categories |
|--------|----------|-------------|------------|
| binary_symmetry | 20 | 3 | symmetry, transformation, algorithm |
| cooking | 32 | 1 | technique, recipe, cooking_method |
| diy | 10 | 1 | building, flooring, tools |
| exframe_methods | 26 | - | methodology, pattern, design |
| first_aid | 3 | - | emergency, medical, treatment |
| gardening | 3 | - | planting, care, harvesting |
| llm_consciousness | 12 | 2 | failure_mode, monitoring, detection |
| poetry_domain | 13 | - | poetic, literary, verse |
| psycho | 6 | - | psychology, therapy, analysis |
| python | 6 | 1 | language_feature, best_practice |

### Adding New Domains

**Method 1: Web UI (Recommended)**
1. Go to **Domains** tab
2. Click **Create Domain**
3. Fill in domain details and specialists
4. Click **Save Domain**

**Method 2: Code-Based**
1. Create domain directory: `universes/{universe}/domains/{domain}/`
2. Create `domain.json` with configuration
3. Add `patterns.json` with patterns
4. Generate embeddings: `POST /api/embeddings/generate?domain={domain}`

---

## SEMANTIC SEARCH API

### Check Embedding Status

```bash
curl http://localhost:3000/api/embeddings/status
```

Returns embedding coverage per domain.

### Generate Embeddings

```bash
curl -X POST "http://localhost:3000/api/embeddings/generate?domain={domain}"
```

Generates embeddings for all patterns in a domain.

### Adjust Search Weights (Advanced)

```bash
curl -X POST http://localhost:3000/api/embeddings/weights \
  -H "Content-Type: application/json" \
  -d '{"semantic": 1.0, "keyword": 0.0}'
```

**Current setting**: semantic=1.0, keyword=0.0 (pure semantic)

---

## TROUBLESHOOTING

### Semantic Search Not Working

**Symptom**: Results show `relevance_source: "keyword"` instead of "semantic"

**Causes**:
1. Embeddings not generated for domain
2. Vector store not loaded
3. Model not loaded

**Solutions**:
1. Generate embeddings: `POST /api/embeddings/generate?domain={domain}`
2. Restart API server to reload vector store
3. Check logs for model loading errors

### "Object of type float32 is not JSON serializable"

**Status**: FIXED (2026-01-20)

If you see this error, the fix has been applied. Restart the server:
```bash
docker compose restart
```

### Pattern Truncation Warnings

**Symptom**: Logs show warnings about patterns exceeding token limit

**Meaning**: Some patterns are >256 tokens and being truncated

**Impact**: Truncated patterns use only name + solution fields

**Solution**: Review and shorten large patterns, or accept truncation

---

## DESIGN DOCUMENTATION

### Semantic Search Design

**Document**: `rag-search-design.md`

**Key Sections**:
- Architecture overview (search flow)
- Component details (EmbeddingService, VectorStore, HybridSearcher)
- Configuration (model, weights, thresholds)
- Search behavior examples
- Performance characteristics
- Monitoring & debugging

### Query System Redesign

**Document**: `query-rewrite.md`

**Philosophy**: "The query position is a knowledge dashboard where Responsible Agents (human domain experts) directly accept AI-generated knowledge into curated domains."

**Key Principle**: User acceptance IS the certification. No separate "candidate → certified" workflow.

**Status**: Design complete, implementation pending

---

## NEXT STEPS

### Immediate: Testing Phase

User is conducting testing of pure semantic search:
- Evaluate semantic similarity quality
- Identify patterns that rank incorrectly
- Note gaps in coverage
- Determine if chunking is needed

### Future Enhancements (Design Doc Ready)

**From rag-search-design.md**:
1. Feedback & Learning (implicit/explicit feedback, usage decay)
2. Dynamic Weight Adjustment (adaptive semantic/keyword weights)
3. Auto-Embedding on Pattern Change
4. Pattern Discovery & Clustering
5. Fine-tuning Embedding Model

**From query-rewrite.md**:
- Knowledge Dashboard UI implementation (4 phases, 8 weeks)
- External search integration (local_docs, web_search)
- Pattern acceptance workflow (direct creation, no intermediate state)

### Current Known Limitations

1. No feedback loop (pattern relevance doesn't improve with use)
2. Static embeddings (not updated when patterns modified)
3. Fixed thresholds (min_semantic_score configurable but static)
4. No personalization (all users get same results)
5. Embedding regeneration is manual process
6. Some patterns exceed token limit (truncation warnings in logs)

---

## DEVELOPMENT NOTES

### Pattern Encoding Strategy

**Current**: Whole document embedding (no chunking)

**Fields Combined** (in priority order):
1. Name (always included)
2. Solution (always included)
3. Description (if space permits)
4. Problem (if space permits)
5. Origin query (if space permits)
6. Tags (if space permits)

**Token Limit**: 256 tokens (all-MiniLM-L6-v2 limit)
**Estimation**: 1 token ≈ 4 characters

**Truncation Strategy**: If pattern exceeds limit:
1. Issue warning in logs
2. Keep name + solution[:1500] only
3. Drop secondary fields

### Stop Words Filtered from Queries

These words are removed during query processing:
- Articles: a, an, the
- Verbs: is, are, was, were, be, been, being, have, has, had, do, does, did, will, would, could, should, may, might
- Pronouns: what, which, who, where, when, why, how, there, here, this, that, these, those
- Prepositions: for, of, with, by, from, in, on, at, to
- Conjunctions: and, or, but, if, because, as, until, while
- Common query words: type, types, like, just, some, more, much, many

---

## GITHUB STATUS

**Repository**: https://github.com/orangelightening/ExFrame.git
**Working Directory**: `/home/peter/development/eeframe`
**Current Branch**: main
**Status**: Development changes pending commit

---

## DOCUMENTATION INDEX

### Main Documentation
- **README.md** - Project overview, installation, API reference
- **claude.md** - This file (context recovery)
- **context.md** - Detailed project context
- **CHANGELOG.md** - Version history

### Design Documents
- **rag-search-design.md** - Semantic search implementation
- **query-rewrite.md** - Knowledge Dashboard specification
- **query-todo.md** - Query system implementation todos

### Architecture Documentation
- **PLUGIN_ARCHITECTURE.md** - Plugin development guide
- **EXTENSION_POINTS.md** - Extension point reference

### Historical Documentation (Archive)
- **reverse.md** - System reverse engineering report
- **REFACTORING_SUMMARY.md** - Refactoring details
- **CONSOLIDATION_*.md** - Phase consolidation reports

---

**Last Updated**: 2026-01-20
**Status**: Semantic search complete, user testing phase
**Next Action**: Await user testing feedback, then commit
