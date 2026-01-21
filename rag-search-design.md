# RAG Search Design Document

**Version:** 1.1
**Date:** 2026-01-20
**Status:** Implemented (Pure Semantic Search)

## Overview

This document describes the Retrieval-Augmented Generation (RAG) search system implemented for the Expertise Framework (EEFrame). The system uses **pure semantic similarity** using embeddings to find relevant patterns based on meaning, not keyword matching.

### Problem Statement

Previously, the search system relied solely on keyword matching:
- Query: "what is a cake?" → Returns patterns containing "cake"
- Query: "what is a pie?" → Returns patterns containing "pie"
- **Problem**: If no patterns contain the exact keywords, no results are returned

The semantic search solves this by understanding the **meaning** of queries and finding conceptually related patterns.

### Current Implementation: Pure Semantic Search ✅

As of 2026-01-20, the system uses **100% semantic similarity** (0% keyword component):
- Query encoding to 384-dimensional vectors
- Cosine similarity ranking
- Scores 0-1 (higher = more semantically related)
- All 10 domains have 100% embedding coverage (131 patterns)

---

## Current Implementation (v1.1 - Pure Semantic)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PURE SEMANTIC SEARCH FLOW                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. QUERY PROCESSING                                                      │
│     ├─ Lowercase query                                                   │
│     ├─ Strip punctuation (cake? → cake)                                  │
│     ├─ Filter stop words (what, is, a, the, etc.)                        │
│     └─ Extract content words                                             │
│                                                                           │
│  2. SEMANTIC ENCODING                                                     │
│     ├─ Encode query → embedding vector (384-dim)                         │
│     └─ Load all pattern embeddings from vector store                    │
│                                                                           │
│  3. SIMILARITY COMPUTATION                                                │
│     ├─ Compute cosine similarity (query, each pattern)                   │
│     └─ Return similarity scores (0-1 range)                             │
│                                                                           │
│  4. RANKING & SELECTION                                                   │
│     ├─ Sort by semantic score (descending)                               │
│     ├─ Return top N patterns (default: 10)                               │
│     └─ Fallback to LLM if no patterns meet threshold                     │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component 1: Embedding Service

**File:** `generic_framework/core/embeddings.py`

**Purpose:** Generate text embeddings using SentenceTransformers

```python
class EmbeddingService:
    """Manages sentence transformer model for embeddings."""

    model_name = "all-MiniLM-L6-v2"
    embedding_dim = 384

    def encode(self, text: str) -> np.ndarray:
        """Encode a single text string."""

    def encode_pattern(self, pattern: Dict) -> np.ndarray:
        """Encode a pattern (combines name, description, solution, etc.)"""

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute similarity between two vectors."""
```

**Key Features:**
- Lazy loading (model loads on first use)
- Combined text from multiple pattern fields
- 384-dimensional vectors (balance of speed/accuracy)

### Component 2: Vector Store

**File:** `generic_framework/core/embeddings.py`

**Purpose:** Persist and retrieve pattern embeddings

```python
class VectorStore:
    """Simple JSON-based vector storage."""

    storage_path = "universes/{domain}/embeddings.json"

    def load(self) -> None:
        """Load embeddings from disk."""

    def save(self) -> None:
        """Persist embeddings to disk."""

    def set(self, pattern_id: str, embedding: np.ndarray) -> None:
        """Store an embedding."""

    def get(self, pattern_id: str) -> Optional[np.ndarray]:
        """Retrieve an embedding."""
```

**Storage Format:**
```json
{
  "pattern_id_1": [0.12, -0.34, 0.56, ...],
  "pattern_id_2": [-0.23, 0.45, 0.12, ...]
}
```

### Component 3: Hybrid Search

**File:** `generic_framework/core/hybrid_search.py`

**Purpose:** Combine semantic and keyword scores with configurable weights

```python
class HybridSearchConfig:
    # Pure semantic search (v1.1 - 2026-01-20)
    semantic_weight: float = 1.0  # 100% semantic
    keyword_weight: float = 0.0   # 0% keyword
    min_semantic_score: float = 0.0
    min_keyword_score: int = 0

class HybridSearcher:
    def search(
        self,
        query: str,
        patterns: List[Dict],
        keyword_scores: Dict[str, int],
        top_k: int = 10
    ) -> List[HybridSearchResult]:
        """Return ranked patterns using combined scores."""
```

**Scoring Formula:**
```
normalized_keyword = keyword_score / max_keyword_score
combined_score = (semantic_score × semantic_weight) + (normalized_keyword × keyword_weight)
```

### Component 4: Knowledge Base Integration

**File:** `generic_framework/knowledge/json_kb.py`

**Key Methods:**

```python
class JSONKnowledgeBase:
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        exact_only: bool = False
    ) -> List[Dict]:
        """Hybrid search combining semantic + keyword."""

    async def generate_embeddings(self) -> Dict:
        """Generate embeddings for all patterns without them."""

    def get_embedding_status(self) -> Dict:
        """Get coverage statistics."""

    def set_hybrid_weights(self, semantic: float, keyword: float) -> None:
        """Adjust search balance dynamically."""
```

### Component 5: API Endpoints

**File:** `generic_framework/api/app.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/embeddings/status` | GET | Get embedding coverage per domain |
| `/api/embeddings/generate` | POST | Generate embeddings for a domain |
| `/api/embeddings/weights` | POST | Adjust semantic/keyword weights |
| `/api/embeddings/model` | GET | Get model information |

### Configuration

**docker-compose.yml:**
```yaml
environment:
  - TRANSFORMERS_CACHE=/app/cache/models
  - HF_HOME=/app/cache/huggingface

volumes:
  - eeframe_cache:/app/cache
```

**requirements.txt:**
```
sentence-transformers>=2.2.0
```

### Stop Words List

Filtered out during query processing:

```python
STOP_WORDS = {
    # Articles
    'a', 'an', 'the',

    # Verbs
    'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might',

    # Pronouns & prepositions
    'what', 'which', 'who', 'where', 'when', 'why', 'how',
    'there', 'here', 'this', 'that', 'these', 'those',
    'for', 'of', 'with', 'by', 'from', 'in', 'on', 'at', 'to',

    # Conjunctions
    'and', 'or', 'but', 'if', 'because', 'as', 'until', 'while',

    # Common query words
    'type', 'types', 'like', 'just', 'some', 'more', 'much', 'many'
}
```

---

## Search Behavior Examples

### Example 1: Keyword Match Found

**Query:** "reverse sear"
**Content Words:** ['reverse', 'sear']

| Pattern | Keyword | Semantic | Combined |
|---------|---------|----------|----------|
| Reverse Sear Method | 2 | 0.8 | 0.56 |
| Temperature Control | 1 | 0.3 | 0.28 |

### Example 2: No Keyword Match (Semantic Only)

**Query:** "what is a cake?"
**Content Words:** ['cake']

| Pattern | Keyword | Semantic | Combined |
|---------|---------|----------|----------|
| profitiroll pattern | 0 | 0.346 | 0.173 |
| gallette pattern | 0 | 0.331 | 0.166 |
| flatbread pattern | 0 | 0.260 | 0.130 |

*Note: None of the cooking patterns contain "cake", but semantic search finds related pastries.*

### Example 3: Different Queries, Different Results

**Query:** "what is a pie?"
**Content Words:** ['pie']

| Pattern | Semantic (pie) | Semantic (cake) | Delta |
|---------|----------------|-----------------|-------|
| profitiroll pattern | 0.435 | 0.346 | +0.089 |
| gallette pattern | 0.353 | 0.331 | +0.022 |

*Note: "Pie" has higher semantic similarity to profitirolls than "cake" does.*

---

## Current Limitations

1. **No feedback loop** - Pattern relevance doesn't improve with use
2. **Static embeddings** - Not updated when patterns are modified
3. **Fixed thresholds** - min_semantic_score is configurable but static
4. **No personalization** - All users get same results
5. **No domain-specific tuning** - Same weights for all domains
6. **Embedding regeneration** - Manual process (no auto-update on pattern change)

---

## Planned Enhancements (Future)

### Phase 1: Feedback & Learning

**Priority: High**

| Feature | Description | Benefit |
|---------|-------------|---------|
| Implicit feedback | Track pattern views, usage | Identify helpful patterns |
| Explicit feedback | User ratings (thumbs up/down) | Direct relevance signal |
| Usage decay | Reduce weight of unused patterns | Prevent stale results |
| Success tracking | Monitor which patterns lead to resolution | Quality metric |

**Implementation Sketch:**
```python
class PatternFeedback:
    views: int = 0
    selected: int = 0
    rating: float = 0.0  # -1 to 1
    success_rate: float = 0.0  # 0 to 1

    def get_boost_score(self) -> float:
        """Calculate relevance boost based on feedback."""
```

### Phase 2: Dynamic Weight Adjustment

**Priority: High**

| Scenario | Semantic | Keyword | Rationale |
|----------|----------|---------|-----------|
| Short query | 0.3 | 0.7 | Exact match more likely |
| Long query | 0.7 | 0.3 | Concept more important |
| Technical domain | 0.4 | 0.6 | Precision matters |
| Conceptual domain | 0.6 | 0.4 | Understanding matters |

```python
def adaptive_weights(query: str, domain: str) -> Tuple[float, float]:
    """Calculate weights based on context."""
    if len(query.split()) < 4:
        return (0.3, 0.7)  # Short queries → keyword
    if domain in ['python', 'first_aid']:
        return (0.4, 0.6)  # Technical → keyword
    if domain in ['poetry_domain', 'psycho']:
        return (0.6, 0.4)  # Conceptual → semantic
    return (0.5, 0.5)  # Default
```

### Phase 3: Auto-Embedding on Pattern Change

**Priority: Medium**

```python
class JSONKnowledgeBase:
    async def save_pattern(self, pattern: Dict) -> None:
        """Override to auto-update embeddings."""
        super().save_pattern(pattern)

        if self.embedding_service and self.embedding_service.is_loaded:
            pattern_id = pattern['id']
            embedding = self.embedding_service.encode_pattern(pattern)
            self.vector_store.set(pattern_id, embedding)
            self.vector_store.save()
```

### Phase 4: Pattern Discovery & Clustering

**Priority: Medium**

| Feature | Description | Use Case |
|---------|-------------|----------|
| Query clustering | Group similar queries | Identify missing patterns |
| Gap analysis | Find under-covered topics | Guide content creation |
| Redundancy detection | Find duplicate patterns | Consolidate knowledge |
| Auto-suggest patterns | Extract from successful LLM responses | Grow knowledge base |

```python
def find_coverage_gaps(
    queries: List[str],
    patterns: List[Pattern]
) -> List[str]:
    """Identify topics with insufficient pattern coverage."""
    # Cluster queries by semantic similarity
    # For each cluster, check if patterns exist
    # Return clusters with low pattern coverage
```

### Phase 5: Fine-tuning Embedding Model

**Priority: Low**

| Approach | Effort | Benefit |
|----------|--------|---------|
| Domain-specific fine-tuning | High | High |
| Use larger model | Low | Medium |
| Ensemble multiple models | Medium | Medium |

```python
# Option 1: Fine-tune on domain corpus
model = SentenceTransformer('all-MiniLM-L6-v2')
train_examples = [
    InputExample(texts=['cake recipe', 'how to make cake'], label=1.0),
    InputExample(texts=['cake recipe', 'car maintenance'], label=0.0),
]
model.fit(train_examples)

# Option 2: Use larger model
model = SentenceTransformer('all-mpnet-base-v2')  # 768-dim

# Option 3: Ensemble
semantic_1 = model1.encode(query)
semantic_2 = model2.encode(query)
combined = 0.6 * semantic_1 + 0.4 * semantic_2
```

### Phase 6: Advanced Features

**Priority: Low**

| Feature | Description |
|---------|-------------|
| Multi-lingual support | Use paraphrase-multilingual-MiniLM-L12-v2 |
| Image embeddings | CLIP model for visual patterns |
| Hierarchical embeddings | Category → subcategory → pattern |
| Temporal decay | Recent patterns weighted higher |
| User personalization | Learn individual preferences |

---

## Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| all-MiniLM-L6-v2 | 2026-01-20 | Fast, local, good English accuracy |
| 50/50 hybrid weight | 2026-01-20 | Balanced starting point |
| 384-dim vectors | 2026-01-20 | Balance speed/accuracy |
| JSON storage | 2026-01-20 | Simple, no external dependencies |
| Cosine similarity | 2026-01-20 | Standard for semantic search |
| Stop words filtering | 2026-01-20 | Reduce noise in queries |
| Lazy model loading | 2026-01-20 | Faster startup, load on demand |

---

## Performance Characteristics

### Startup
- Without embeddings: ~2 seconds
- With embeddings (cached): ~3 seconds
- First query (model loads): ~5 seconds
- Subsequent queries: ~50-100ms

### Storage
- Per pattern: 384 floats × 4 bytes = ~1.5 KB
- 100 patterns: ~150 KB
- 1000 patterns: ~1.5 MB

### Memory
- Model size: ~120 MB (all-MiniLM-L6-v2)
- Vector cache: proportional to pattern count

### Query Latency
- Keyword-only: ~10ms
- Hybrid search: ~50-100ms
- Embedding generation: ~500ms per 100 patterns

---

## Monitoring & Debugging

### Log Markers

```
[SEARCH] Query: '...'
[SEARCH] Content words: [...]
[SEARCH] Total patterns to check: N
[SEARCH] Using hybrid search (semantic enabled)

[EMBED] Loading model: all-MiniLM-L6-v2
[EMBED] Model loaded. Embedding dim: 384

[HYBRID] Query: '...'
[HYBRID] Weights: semantic=0.50, keyword=0.50
[HYBRID] Results: N patterns matched
[HYBRID]   1. Pattern Name (combined=X.XXX, kw=X, sem=X.XXX)
```

### Health Checks

```bash
# Check if semantic search is available
curl http://localhost:3000/api/embeddings/model

# Check embedding coverage
curl http://localhost:3000/api/embeddings/status?domain=cooking

# Test search with trace enabled
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "domain": "cooking", "include_trace": true}'
```

---

## References

- [SentenceTransformers Documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 Model Card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Vector Search Basics](https://www.pinecone.io/learn/vector-search/)
- [Hybrid Search Techniques](https://weaviate.io/blog/hybrid-search-explained)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-20 | Initial implementation - semantic + hybrid search |
| - | - | Feedback loop (planned) |
| - | - | Dynamic weights (planned) |
| - | - | Auto-embedding (planned) |
