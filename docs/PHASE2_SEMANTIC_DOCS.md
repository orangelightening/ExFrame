# Phase 2: Semantic Document Search

**Date**: 2026-02-04
**Status**: PLANNED
**Priority**: HIGH (performance issue)

---

## Problem

**Current State (Phase 1)**:
- Librarian domains load first 50 documents from filesystem
- No semantic ranking - just alphabetical/filesystem order
- Performance issues with large document collections
- No relevance scoring for documents

**We Already Have**:
- ✅ Full semantic search for patterns (hybrid_search.py)
- ✅ EmbeddingService with SentenceTransformers
- ✅ VectorStore for embeddings
- ✅ HybridSearcher combining semantic + keyword

**What's Missing**:
- ❌ Document embeddings generation
- ❌ Semantic ranking for document loading
- ❌ Document-specific VectorStore
- ❌ Integration with query_processor.py

---

## Solution: Extend Semantic Search to Documents

### Architecture

```
Query comes in (librarian domain, patterns=false)
    ↓
Generate query embedding
    ↓
Load document embeddings from cache
    ↓
Compute similarity scores
    ↓
Rank documents by relevance
    ↓
Load TOP N most relevant documents (not first N)
    ↓
Pass to LLM with context
```

### Key Benefits

1. **Performance**: Only load relevant documents (not first 50)
2. **Accuracy**: Documents ranked by semantic similarity to query
3. **Reuse**: Leverage existing semantic search infrastructure
4. **Caching**: Document embeddings cached on disk

---

## Implementation Plan

### Phase 2.1: Document Embeddings (Week 1)

**Goal**: Generate and cache embeddings for all documents in library

**Files to Create**:
```
generic_framework/core/document_embeddings.py
  - DocumentEmbeddingService class
  - generate_embeddings(library_path) → embeddings.json
  - load_embeddings(library_path) → VectorStore
```

**Files to Modify**:
- `query_processor.py` - Add document embedding generation/loading

**Key Functions**:
```python
class DocumentEmbeddingService:
    """Generate and manage embeddings for document library."""

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    async def generate_embeddings(
        self,
        library_path: str,
        ignored_patterns: List[str]
    ) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for all documents in library.

        Returns:
            Dict mapping file paths to embedding vectors
        """
        # 1. Find all .md files (respecting ignored.md)
        # 2. Read each document
        # 3. Generate embedding
        # 4. Cache to embeddings.json
        pass

    async def load_embeddings(
        self,
        library_path: str
    ) -> VectorStore:
        """Load cached embeddings from disk."""
        pass
```

**Embedding Cache Format**:
```json
{
  "model": "all-MiniLM-L6-v2",
  "generated_at": "2026-02-04T18:00:00Z",
  "documents": {
    "/app/project/docs/intro.md": {
      "embedding": [0.123, -0.456, ...],
      "file_hash": "abc123...",
      "size": 1024,
      "modified_at": "2026-02-04T17:00:00Z"
    }
  }
}
```

### Phase 2.2: Semantic Document Ranking (Week 1-2)

**Goal**: Rank documents by relevance to query

**Files to Modify**:
- `query_processor.py` - Replace `_search_domain_documents()`

**Current Code** (Phase 1):
```python
def _search_domain_documents(domain_name, domain_config):
    # Load ALL markdown files
    all_files = glob.glob(str(base_dir / "**/*.md"), recursive=True)
    # Filter with ignored.md
    filtered_files = [...]
    # Load first N (NO RANKING!)
    for file_path in filtered_files[:max_docs]:
        documents.append(...)
    return documents
```

**New Code** (Phase 2):
```python
async def _search_domain_documents_semantic(
    query: str,
    domain_name: str,
    domain_config: Dict
) -> List[Dict]:
    """Search documents with semantic ranking."""

    # 1. Load or generate document embeddings
    doc_embeddings = await doc_embed_service.load_embeddings(library_path)

    # 2. Generate query embedding
    query_embedding = embedding_service.encode(query)

    # 3. Compute similarity scores
    similarities = doc_embeddings.compute_similarities(query_embedding)

    # 4. Rank documents by relevance
    ranked_docs = sorted(similarities, key=lambda x: x[1], reverse=True)

    # 5. Load TOP N most relevant documents
    top_docs = ranked_docs[:max_docs]
    documents = []
    for doc_path, score in top_docs:
        if score >= min_similarity:  # Configurable threshold
            with open(doc_path) as f:
                documents.append({
                    "path": doc_path,
                    "content": f.read()[:max_chars],
                    "similarity_score": score
                })

    return documents
```

### Phase 2.3: Performance Optimization (Week 2)

**Goal**: Fast queries, minimal overhead

**Optimizations**:
1. **Lazy Loading**: Only generate embeddings on first query
2. **Incremental Updates**: Only re-embed modified files
3. **Memory Caching**: Keep embeddings in memory for hot domains
4. **Background Jobs**: Generate embeddings async in background

**Config Options** (domain.json):
```json
{
  "persona": "librarian",
  "library_base_path": "/app/project/docs",
  "document_search": {
    "algorithm": "semantic",
    "max_documents": 10,
    "min_similarity": 0.3,
    "auto_generate_embeddings": true,
    "cache_embeddings": true
  }
}
```

---

## Migration Path

### Step 1: Keep Phase 1 as Default
- Phase 1 (filesystem order) remains default
- Add `document_search.algorithm` config option
- Values: "filesystem" (Phase 1) or "semantic" (Phase 2)

### Step 2: Opt-In Semantic Search
- Domains can enable semantic search via config
- Users test and validate
- No breaking changes

### Step 3: Make Semantic Default
- After validation, switch default to semantic
- Phase 1 still available for simple cases

---

## Performance Targets

### Current (Phase 1)
- Load time: ~500ms for 50 documents
- No relevance ranking
- All documents loaded regardless of relevance

### Target (Phase 2)
- Load time: ~200ms for 10 relevant documents
- Semantic ranking by relevance
- Only load what's needed

### Embedding Generation
- Initial: ~2-5 seconds for 100 documents (one-time)
- Incremental: ~50ms per new/modified document
- Cached: ~10ms to load from disk

---

## Success Metrics

### Accuracy
- ✅ Top 3 results contain answer to query (>90%)
- ✅ Irrelevant documents not loaded
- ✅ Similarity scores correlate with relevance

### Performance
- ✅ Query time < 300ms for semantic search
- ✅ Embedding cache hit rate > 95%
- ✅ Memory usage < 100MB for embeddings

### User Experience
- ✅ No manual configuration needed (auto-generate embeddings)
- ✅ Works out of box with existing librarian domains
- ✅ Clear logging of semantic scores in traces

---

## API Changes

### New Endpoint: Generate Embeddings
```bash
POST /api/admin/domains/{domain_id}/embeddings/generate
{
  "force_regenerate": false
}
```

### Response Format Enhancement
```json
{
  "answer": "...",
  "documents_used": [
    {
      "path": "/app/project/docs/intro.md",
      "similarity_score": 0.87,
      "rank": 1
    }
  ]
}
```

---

## Testing Plan

### Unit Tests
- [ ] DocumentEmbeddingService generates correct embeddings
- [ ] Embeddings cache correctly to disk
- [ ] Semantic ranking produces expected order
- [ ] Incremental updates only re-embed changed files

### Integration Tests
- [ ] Query exframe domain with semantic search
- [ ] Verify top results are relevant
- [ ] Compare Phase 1 vs Phase 2 accuracy
- [ ] Test with 100+ document library

### Performance Tests
- [ ] Benchmark embedding generation time
- [ ] Benchmark query time with semantic ranking
- [ ] Memory profiling with large libraries
- [ ] Cache hit rate monitoring

---

## Rollout Plan

### Week 1
- [ ] Implement DocumentEmbeddingService
- [ ] Add embedding generation script
- [ ] Test on exframe domain (14 patterns + docs)

### Week 2
- [ ] Integrate with query_processor.py
- [ ] Add config options to domain.json
- [ ] Test on omv_library domain

### Week 3
- [ ] Performance optimization
- [ ] Background embedding generation
- [ ] Memory caching

### Week 4
- [ ] User testing and feedback
- [ ] Documentation updates
- [ ] Make semantic search default

---

## Known Limitations

### Phase 2 Will NOT Address
- **Large file handling**: Still limited to max_chars_per_document
- **Multi-language**: English-only embeddings (model limitation)
- **Real-time updates**: Embeddings cached, not live

### Future Phase 3 Could Add
- Chunking for large documents
- Multi-language models
- Real-time embedding generation
- Cross-domain semantic search

---

## Questions to Resolve

1. **Embedding Cache Location**: Store in domain directory or centralized?
   - Option A: `/app/universes/MINE/domains/{domain}/doc_embeddings.json`
   - Option B: `/app/data/embeddings/{domain}_docs.json`

2. **Incremental Updates**: How to detect file changes?
   - Option A: File hash comparison
   - Option B: Modification timestamp
   - Option C: User-triggered regeneration

3. **Memory vs Disk**: Cache embeddings in memory or load per query?
   - Option A: Load all embeddings on domain startup (fast queries, more memory)
   - Option B: Load on first query and cache (lazy, medium memory)
   - Option C: Load from disk per query (slow queries, low memory)

4. **Hybrid Search for Docs**: Should documents use keyword + semantic like patterns?
   - Patterns use hybrid search (keyword + semantic)
   - Documents currently keyword-only (via ignored.md)
   - Should documents also use hybrid?

---

**Status**: Ready to implement
**Estimated Time**: 2-3 weeks
**Priority**: HIGH - Addresses performance issue
**Dependencies**: None (reuses existing semantic search infrastructure)
