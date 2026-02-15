# ExFrame TODO List

## Current Status (2026-02-14)

### ✅ Performance Optimization - COMPLETED
- Embeddings load in 0.2s (singleton pattern working)
- LLM queries: 231ms with llama3.2 (12.5x faster than qwen3)
- Dual-model routing: llama3.2 (local) for entries, glm-4.7 (remote) for ** searches
- Single GPU model strategy: avoids CUDA out-of-memory errors
- Semantic search: ~11ms for 28 patterns
- Pattern autogeneration: working (~25ms async)
- Comprehensive timing logs with ⏱ markers

### 🧪 Testing Phase - IN PROGRESS
- Need comprehensive testing of all features
- Verify stability across domains
- Document any edge cases or issues

---

## Minor Bugs / Enhancements

### Poet Response Format (Priority: Low)
**Issue**: Poet now includes "Query:" prefix in timestamped responses

**Current Behavior**:
```
Input: "dogs love beef"
Output: "[2026-02-14 13:04:38] Query: dogs love beef"
```

**Expected Behavior**:
```
Input: "dogs love beef"
Output: "[2026-02-14 13:04:38] dogs love beef"
```

**Notes**:
- Not critical - system works fine
- User doesn't want to mess with working prompt
- Fix when doing broader poet/journal improvements

**Workaround**: None needed, cosmetic issue only

---

### Duplicate Pattern Creation (Priority: Low - WORKING AS DESIGNED)
**Status**: Duplicates ARE created but analytics detects them

**Current Behavior**:
- Making same journal entry multiple times creates duplicate patterns
- Analytics script identifies duplicates (100% match)
- User can easily see and delete duplicates manually

**Example**: peter domain has 5 exact duplicate pairs (detected by analytics)

**Notes**:
- Manual cleanup works fine
- Not blocking for production
- Could add automatic deduplication later

**Workaround**: Run `python3 scripts/analyze_patterns.py` periodically and manually clean up duplicates

---

## Performance Optimizations

### Smart Pattern Filtering for ** Searches (Priority: High)
**Goal**: Reduce LLM synthesis time from 8s to 5-6s

**Current behavior:**
- Sends top 10 patterns with 0.3 threshold
- LLM processes all patterns regardless of relevance
- Takes ~8s for synthesis

**Proposed improvements:**
1. **Increase threshold**: 0.3 → 0.5 (only highly relevant patterns)
2. **Reduce pattern count**: 10 → 5 (less context to process)
3. **Keyword boosting**: Boost patterns with exact query term matches
4. **Recency boost**: Recent entries rank higher
5. **Smarter prompting**: Minimal, focused prompts (fewer tokens)

**Expected impact:**
- Speed: 8s → 5-6s (30-40% faster)
- Accuracy: Better (only send relevant patterns)
- Cost: Lower (fewer tokens processed)

**Implementation notes:**
- query_processor.py: Adjust similarity_threshold for ** queries
- Add keyword matching boost to semantic search
- Optimize LLM prompt length

---

### ✅ Internet Search Integration - COMPLETED (2026-02-14)
**Status**: Brave Search API integrated and working

**Implemented features:**
- Brave Search API integration ($4/1000 requests + $5/million tokens)
- Direct return (skips GLM synthesis for 5x speed improvement)
- LaTeX formatting cleanup (removes $ symbols)
- User-controlled prompts (experiment with phrasing for best results)
- Two code paths: tool-calling and data source

**Performance:**
- Response time: 15-25 seconds (vs 60-100s with DuckDuckGo)
- Cost: ~$0.004 per query
- Reliability: Stable, no HTTP 500 errors
- Quality: AI-synthesized answers with inline source mentions

**URL Citations:**
- Inconsistent - depends on query phrasing
- User can request: "Include all source URLs" or "with citations"
- Brave AI decides format (inline mentions vs structured URLs)

**Status:** Live in production, testing phase ongoing

**Free credit:** $4.87 remaining (~1200 queries)

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
