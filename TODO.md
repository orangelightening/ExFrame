# ExFrame TODO List

## Current Status (2026-02-14)

### ✅ Performance Optimization - COMPLETED
- Embeddings load in 0.2s (singleton pattern working)
- LLM queries: 231ms with llama3.2 (12.5x faster than qwen3)
- Semantic search: ~11ms for 28 patterns
- Pattern autogeneration: working (~25ms async)
- Comprehensive timing logs with ⏱ markers

### 🧪 Testing Phase - IN PROGRESS
- Need comprehensive testing of all features
- Verify stability across domains
- Document any edge cases or issues

---

## Future Enhancements

### Cross-Domain Semantic Search (Priority: Medium)
**Description:** Search patterns across ALL domains, not just the current domain

**Use Cases:**
- "Find all patterns about authentication across all domains"
- Discover related knowledge in different domains
- Unified knowledge base search

**Implementation:**
```python
# API endpoint
GET /api/search/patterns?query=authentication&domains=python,exframe,peter

# Backend
def search_all_domains(query, domains=None, threshold=0.3):
    results = []
    for domain in (domains or all_domains):
        domain_results = search_domain_patterns(domain, query, threshold)
        results.extend(domain_results)
    return rank_and_dedupe(results)
```

**Benefits:**
- Unlock knowledge across domain boundaries
- Better knowledge discovery
- Reduce pattern duplication

**Complexity:** Medium (2-3 hours)

---

## Deferred Items

### Pattern Analytics Dashboard
- Most used patterns
- Pattern quality scores
- Usage trends over time

### Advanced Embedding Models
- Upgrade to bge-small-en-v1.5 or e5-small-v2
- Better semantic understanding
- Domain-specific fine-tuning

### Hybrid Search
- Combine semantic + keyword matching
- Better precision for exact term matches
