# ExFrame Project Context

**Date**: 2026-01-22
**Working Directory**: `/home/peter/development/eeframe`
**Status**: Self-Documenting Landing Page - Ready for Release
**Version**: 1.6.0
**Default Universe**: MINE
**Default Domain**: exframe

---

## EXECUTIVE SUMMARY

ExFrame is a domain-agnostic AI-powered knowledge management system featuring:
- **Emergent Personas**: Each domain has one specialist that evolves from its pattern corpus
- **Universe Architecture**: Complete isolation and portability of knowledge
- **Plugin Pipeline**: Router → Specialist → Enricher → Formatter
- **Pure Semantic Search**: 100% semantic similarity using embeddings
- **Pattern-Based Knowledge**: Structured representation with relationships
- **Self-Documenting**: New users are welcomed with an intro query that explains the system

### The Emergent Persona Theory

**Knowledge comes from patterns. Persona emerges from knowledge.**

1. Patterns capture human expertise
2. Knowledge is the corpus of patterns
3. The specialist is the AI persona that emerges from that corpus
4. As patterns increase, the specialist becomes more coherent and expert-like
5. The specialist is not a "person" - it's the collective voice of the domain

Each domain has **one specialist** whose personality comes entirely from:
- The domain's pattern corpus (what it knows)
- The domain's name and description (who it is)
- The domain's categories (what it cares about)

### Current Status: Production Ready ✅

Self-documenting landing page with semantic search fully operational across all 11 domains.

---

## CURRENT STATE (2026-01-22)

### New: Self-Documenting Landing Page

The landing page now welcomes new users with:
- **Default Universe**: MINE (renamed from "default")
- **Default Domain**: exframe (renamed from "exframe_methods")
- **Preloaded Query**: "What is ExFrame and how do I get started?"
- **Response**: Hits the intro pattern explaining where to go next

### Semantic Search Implementation

Pure semantic search using SentenceTransformers:

| Setting | Value |
|---------|-------|
| **Model** | all-MiniLM-L6-v2 |
| **Vector Dimensions** | 384 |
| **Similarity Metric** | Cosine similarity |
| **Semantic Weight** | 100% |
| **Keyword Weight** | 0% |
| **Coverage** | All 11 domains (145 patterns) |

### Domain Status

| Domain | Patterns | Embeddings | Status |
|--------|----------|------------|--------|
| binary_symmetry | 21 | 21 | ✅ Semantic |
| cooking | 33 | 33 | ✅ Semantic |
| diy | 12 | 12 | ✅ Semantic |
| exframe | 26 | 26 | ✅ Semantic |
| first_aid | 4 | 4 | ✅ Semantic |
| gardening | 3 | 3 | ✅ Semantic |
| llm_consciousness | 12 | 12 | ✅ Semantic |
| poetry_domain | 17 | 17 | ✅ Semantic |
| psycho | 8 | 8 | ✅ Semantic |
| python | 9 | 9 | ✅ Semantic |
| test_domain | 0 | 0 | Empty |

### Recent Changes (2026-01-22)

1. **Universe Rename** - "default" → "MINE" (never use "default" as a name)
2. **Domain Rename** - "exframe_methods" → "exframe"
3. **Landing Page Defaults** - Preloaded query for new users
4. **Research Strategy** - Read-only access to project documentation for LLM fallback
5. **Self-Documenting** - System introduces itself to new users automatically

---

## SEMANTIC SEARCH ARCHITECTURE

### Search Flow

```
Query Input
    ↓
Preprocessing (lowercase, remove stop words)
    ↓
Encode to 384-dim embedding (all-MiniLM-L6-v2)
    ↓
Compare with all pattern embeddings (cosine similarity)
    ↓
Rank by similarity score (0-1)
    ↓
Return top patterns with scores
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| EmbeddingService | `core/embeddings.py` | Generate embeddings, encode patterns |
| VectorStore | `core/embeddings.py` | Persist embeddings to JSON |
| HybridSearcher | `core/hybrid_search.py` | Combine semantic + keyword scores |
| JSONKnowledgeBase | `knowledge/json_kb.py` | Search integration |

### Pattern Encoding Strategy

**Whole document embedding** (no chunking):

1. **High-priority fields** (always included):
   - Name
   - Solution

2. **Secondary fields** (included if space permits):
   - Description
   - Problem
   - Origin query
   - Tags

3. **Token limit**: 256 tokens (all-MiniLM-L6-v2 constraint)
4. **Estimation**: 1 token ≈ 4 characters
5. **Truncation**: If exceeds limit, keep name + solution[:1500] only

---

## SYSTEM ARCHITECTURE

### Core Pipeline

```
Query → Router → Specialist → Knowledge Base → Enrichers → Formatter → Response
```

### Plugin Architecture

| Plugin Type | Interface | Purpose |
|-------------|-----------|---------|
| Router | RouterPlugin | Determine query handling strategy |
| Specialist | SpecialistPlugin | Domain expertise (can_handle, process_query, format_response) |
| Knowledge Base | KnowledgeBasePlugin | Pattern storage and retrieval |
| Enricher | EnricherPlugin | Response enhancement (LLM, related patterns, code) |
| Formatter | FormatterPlugin | Output format control |

### Universe Hierarchy

```
MULTIVERSE
    │
    └── UNIVERSE (e.g., "production", "testing")
        │
        └── DOMAIN (e.g., "cooking", "python")
            │
            └── PATTERNS (knowledge units)
```

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

### LLM Configuration

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

## API REFERENCE

### Semantic Search Endpoints

#### Check Embedding Status
```bash
curl http://localhost:3000/api/embeddings/status
```

Returns embedding coverage per domain.

#### Generate Embeddings
```bash
curl -X POST "http://localhost:3000/api/embeddings/generate?domain={domain}"
```

Generates embeddings for all patterns in a domain.

#### Adjust Search Weights
```bash
curl -X POST http://localhost:3000/api/embeddings/weights \
  -H "Content-Type: application/json" \
  -d '{"semantic": 1.0, "keyword": 0.0}'
```

**Current**: semantic=1.0, keyword=0.0 (pure semantic)

### Core Query Endpoints

#### Query a Domain
```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your question here",
    "domain": "cooking",
    "include_trace": true
  }'
```

#### List Domains
```bash
curl http://localhost:3000/api/domains
```

#### Get Domain Info
```bash
curl http://localhost:3000/api/domains/{domain_id}
```

#### List Patterns
```bash
curl "http://localhost:3000/api/domains/{domain_id}/patterns"
```

---

## EXAMPLE: SEMANTIC SEARCH IN ACTION

### Query: "How do I use a hammer?"

**Semantic Results**:
| Pattern | Similarity | Notes |
|---------|-----------|-------|
| How do I hammer in a nail? | 0.7007 | Highest semantic match |
| How do I build a simple shelf? | 0.2882 | Related DIY task |
| Laying the Foundation: How to Build a Floor | 0.1542 | Construction-related |
| Wall and Floor Construction Basics | 0.1314 | Construction-related |
| Choosing and Installing DIY Flooring | 0.0912 | DIY-related |

**Key Insight**: "hammer in a nail" has highest similarity even though both queries contain "hammer" - the model understands semantic meaning, not just keyword overlap.

### Different Queries, Different Results

**Query: "What is a cake?"**

| Pattern | Semantic Score |
|---------|---------------|
| profitiroll pattern | 0.346 |
| gallette pattern | 0.331 |
| flatbread pattern | 0.260 |

**Query: "What is a pie?"**

| Pattern | Semantic Score |
|---------|---------------|
| profitiroll pattern | 0.435 |
| gallette pattern | 0.353 |
| flatbread pattern | 0.217 |

**Note**: "Pie" has higher semantic similarity to profitirolls than "cake" does - the model captures these nuanced differences.

---

## TROUBLESHOOTING

### Semantic Search Not Working

**Symptom**: Results show `relevance_source: "keyword"` instead of "semantic"

**Solutions**:
1. Generate embeddings: `POST /api/embeddings/generate?domain={domain}`
2. Restart server to reload vector store
3. Check logs for model loading errors

### Pattern Truncation Warnings

**Symptom**: Logs show `[EMBED] WARNING: Pattern {id} may exceed token limit`

**Meaning**: Pattern is >256 tokens and being truncated

**Impact**: Truncated patterns use only name + solution fields

**Solution**: Review and shorten large patterns, or accept truncation

### Docker Issues

**Port 3000 already in use**:
```bash
sudo lsof -ti:3000 | xargs sudo kill -9
docker compose restart
```

**Patterns not showing** (Docker snap issue):
```bash
sudo snap remove docker
curl -fsSL https://get.docker.com | sh
docker compose down
docker compose up -d
```

---

## DESIGN DOCUMENTATION

### Semantic Search Design

**Document**: `rag-search-design.md`

**Contents**:
- Architecture overview
- Component details (EmbeddingService, VectorStore, HybridSearcher)
- Configuration (model, weights, thresholds)
- Search behavior examples
- Performance characteristics
- Monitoring & debugging
- Future enhancements (feedback loop, dynamic weights, auto-embedding)

### Query System Redesign

**Document**: `query-rewrite.md`

**Philosophy**: "The query position is a knowledge dashboard where Responsible Agents (human domain experts) directly accept AI-generated knowledge into curated domains."

**Key Principle**: User acceptance IS the certification. No separate "candidate → certified" workflow.

**Status**: Design complete, implementation pending (4 phases, 8 weeks)

---

## FUTURE ENHANCEMENTS

### Near-Term (Design Complete)

1. **Feedback & Learning**
   - Implicit feedback (pattern views, usage)
   - Explicit feedback (user ratings)
   - Usage decay for stale patterns

2. **Dynamic Weight Adjustment**
   - Adaptive semantic/keyword weights based on query context
   - Short queries → more keyword weight
   - Long queries → more semantic weight

3. **Auto-Embedding on Pattern Change**
   - Automatically update embeddings when patterns are modified
   - Eliminate manual embedding regeneration

### Long-Term (Conceptual)

4. **Pattern Discovery & Clustering**
   - Query clustering to identify missing patterns
   - Gap analysis for under-covered topics
   - Redundancy detection

5. **Fine-tuning Embedding Model**
   - Domain-specific fine-tuning
   - Use larger model (all-mpnet-base-v2: 768-dim)
   - Ensemble multiple models

---

## PROJECT STRUCTURE

```
eeframe/
├── generic_framework/          # Main framework
│   ├── api/                    # FastAPI application
│   ├── core/                   # Core interfaces
│   │   ├── embeddings.py       # Semantic search
│   │   ├── hybrid_search.py    # Hybrid search engine
│   │   ├── domain.py           # Domain base class
│   │   ├── specialist.py       # Specialist base class
│   │   └── knowledge_base.py   # Knowledge base interface
│   ├── knowledge/              # Knowledge base implementations
│   │   └── json_kb.py          # JSON-based KB with semantic search
│   ├── assist/                 # Assistant engine
│   │   └── engine.py           # Query orchestration
│   └── frontend/               # Web UI (Alpine.js + Tailwind)
├── universes/                  # Knowledge universes
│   └── default/                # Default universe
│       └── domains/            # Domain patterns and embeddings
├── config/                     # Monitoring configurations
├── docker-compose.yml          # Docker deployment
├── Dockerfile                  # Container definition
└── requirements.txt            # Python dependencies
```

---

## GITHUB STATUS

- **Repository**: https://github.com/orangelightening/ExFrame.git
- **Working Directory**: `/home/peter/development/eeframe`
- **Current Branch**: main
- **Status**: Development changes pending commit

---

## DOCUMENTATION INDEX

### Main Documentation
- **README.md** - Project overview, installation, API reference
- **claude.md** - Context recovery for Claude (AI assistant)
- **context.md** - This file (project context)
- **CHANGELOG.md** - Version history

### Design Documents
- **rag-search-design.md** - Semantic search implementation
- **query-rewrite.md** - Knowledge Dashboard specification
- **query-todo.md** - Query system implementation todos

### Architecture Documentation
- **PLUGIN_ARCHITECTURE.md** - Plugin development guide
- **EXTENSION_POINTS.md** - Extension point reference

### Historical Documentation
- **reverse.md** - System reverse engineering report
- **REFACTORING_SUMMARY.md** - Refactoring details
- **CONSOLIDATION_*.md** - Phase consolidation reports

---

## STOP WORDS (Filtered from Queries)

These words are removed during query processing:

**Articles**: a, an, the

**Verbs**: is, are, was, were, be, been, being, have, has, had, do, does, did, will, would, could, should, may, might

**Pronouns**: what, which, who, where, when, why, how, there, here, this, that, these, those

**Prepositions**: for, of, with, by, from, in, on, at, to

**Conjunctions**: and, or, but, if, because, as, until, while

**Common query words**: type, types, like, just, some, more, much, many

---

## NEXT STEPS

### Immediate: Testing Phase

User is conducting testing of pure semantic search:
- Evaluate semantic similarity quality
- Identify patterns that rank incorrectly
- Note gaps in coverage
- Determine if chunking is needed

### Pending: Commit

After testing phase complete:
1. Review semantic search results
2. Identify any issues or improvements
3. Commit current state to GitHub
4. Tag release (v1.5.0)

---

**Last Updated**: 2026-01-20
**Status**: Semantic search complete, user testing phase
**Next Action**: Await user testing feedback, then commit and tag release
