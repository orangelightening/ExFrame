# Surveyor System - Current State & Implementation Plan

**Date**: February 7, 2026
**Status**: Partially Working - UI Complete, Backend Stubs
**Path Forward**: Use existing DuckDuckGo search instead of building scrapers

---

## Executive Summary

The Surveyor system has a **complete UI** and **working API endpoints**, but the actual scraping/extraction logic is **not connected**. The good news: **ExFrame already has working DuckDuckGo search** that we can leverage instead of building traditional web scrapers.

---

## What Works ✅

### 1. Frontend UI (100% Complete)
- ✅ Survey list view (left panel)
- ✅ Survey detail panel (center)
- ✅ Live metrics panel (right) - shows stub data
- ✅ Create survey modal (all fields)
- ✅ Edit survey modal (NOW WORKS!)
- ✅ Start/Pause/Stop buttons
- ✅ Progress bar
- ✅ Activity log (static/fake)

**File**: `generic_framework/frontend/index.html`

### 2. Backend API (Functional but Stub)
- ✅ `GET /api/learning/surveys` - List all surveys
- ✅ `POST /api/learning/surveys` - Create survey
- ✅ `GET /api/learning/surveys/{id}` - Get survey details
- ✅ `PUT /api/learning/surveys/{id}` - Update survey
- ✅ `POST /api/learning/surveys/{id}/start` - Start survey
- ✅ `POST /api/learning/surveys/{id}/stop` - Stop survey
- ✅ `POST /api/learning/surveys/{id}/pause` - Pause survey
- ✅ `GET /api/learning/surveys/{id}/metrics` - Get metrics

**Location**: `generic_framework/api/app.py` (lines 2970-3152)
**Storage**: In-memory Python dict (`_surveys_storage`)
**Note**: All endpoints work but don't do actual scraping - just update database state

### 3. Existing Scrapers (Not Connected)
- ✅ `AllRecipesScraper` - Full AllRecipes.com scraper (426 lines)
  - Category crawling
  - JSON-LD extraction
  - Recipe parsing
  - Rate limiting
- ✅ `URLScraper` - Generic web scraper (320 lines)
  - Content extraction
  - Error handling
  - Rate limiting

**Location**: `generic_framework/ingestion/`

### 4. Pattern Extraction (Not Connected)
- ✅ `PatternExtractor` - LLM-based pattern extraction (610 lines)
  - Rule-based fallback
  - Cooking-specific patterns
  - Multiple extraction modes

**Location**: `generic_framework/extraction/extractor.py`

### 5. DuckDuckGo Search (WORKING - Already Used!)
- ✅ `InternetResearchStrategy` - DuckDuckGo HTML search (275 lines)
  - No API key required
  - Used by researcher domains
  - Returns URLs + snippets
  - Parses DDG HTML results

**Location**: `generic_framework/core/research/internet_strategy.py`

---

## What Doesn't Work ❌

### 1. No Background Execution
When you click "Start":
- ✅ Database updates: `status = "running"`
- ❌ No worker process spawned
- ❌ No actual scraping happens
- ❌ No pattern extraction
- ❌ No progress updates

### 2. Activity Log is Fake
The activity log shows static HTML:
```html
<!-- Current: Static fake entries -->
<div>22:19 Survey loaded</div>
<div>10:30 Started scraping: allrecipes.com</div>
<div>10:32 Certified pattern: Chocolate Chip Cookies</div>
```

**Should be**: Real-time events from actual scraping

### 3. Metrics are Mock Data
- Pulse: Always shows ●●●●● or ○○○○○
- Judge activity: Static percentages (85%, 62%, 94%, 71%)
- Focus score: Always 0.95
- Errors: Always 0

**Should be**: Real metrics from actual work

### 4. No Patterns Created
Survey says "running" for hours but:
- No patterns added to domain
- No scraping actually happens
- No certification occurs

---

## Current Architecture (What Exists)

```
User clicks "Start"
  ↓
Frontend calls: POST /api/learning/surveys/{id}/start
  ↓
Backend updates database: status = "running"
  ↓
DATABASE UPDATE COMPLETE ✅
  ↓
(nothing else happens ❌)
```

---

## Missing Piece: The Orchestrator

```
What should happen:
User clicks Start
  ↓
Spawn background worker
  ↓
Worker: Search → Scrape → Extract → Certify → Save
  ↓
Update progress
  ↓
Repeat until target reached
```

**Current gap**: No worker/orchestrator to do the actual work

---

## Implementation Path: Use DuckDuckGo Instead of Scraping

### Key Insight

**Traditional scraping** (what we tried before):
```
URL → HTTP fetch → Parse HTML → Extract content → Patterns
```

**Search-based approach** (what we should do):
```
Query → DuckDuckGo Search → Get 10 results → Extract patterns from snippets
```

### Why This Is Better

1. **No HTML parsing** - DDG gives us clean snippets
2. **No rate limiting** - We search, don't scrape
3. **No site structure changes** - DDG abstracts that away
4. **Faster** - Search results vs page-by-page scraping
5. **Already working** - System uses DDG for researcher queries
6. **No blocking** - Search engines expect this traffic

---

## Proposed Implementation

### Phase 1: Simple Search-Based Collection (1-2 Days)

**Goal**: Make survey actually collect patterns

**Workflow**:
```
1. User creates survey for "pie recipes" on cooking domain
2. System runs multiple searches:
   - "pie recipes" → 10 results
   - "apple pie recipes" → 10 results
   - "cherry pie recipes" → 10 results
3. For each search result, extract patterns from snippet
4. Save to cooking domain
5. Update metrics
```

**Implementation**:
```python
async def run_survey(survey_id):
    survey = get_survey(survey_id)
    extractor = PatternExtractor(domain=survey.domain)
    searcher = InternetResearchStrategy(config)

    queries = generate_search_queries(survey)  # "pie recipes", etc.

    for query in queries:
        results = await searcher.search(query, limit=10)

        for result in results:
            # Extract pattern from search result
            patterns = extractor.extract_from_text(result.snippet)

            # Save to domain
            for pattern in patterns:
                domain.add_pattern(pattern)

            # Update metrics
            survey.patterns_created += len(patterns)
            survey.progress += 0.01
```

**Files to create/modify**:
- `autonomous_learning/worker.py` - Background worker (NEW)
- Hook up Start endpoint to spawn worker

### Phase 2: Full Page Scraping (Optional, 2-3 Days)

**If snippets aren't enough**, add full page scraping:

```
1. DDG search gives URLs
2. Fetch full page with URLScraper
3. Extract patterns from full content
4. Save to domain
```

**Use existing code**:
- `URLScraper` - Already working
- `AllRecipesScraper` - Already working
- `PatternExtractor` - Already working

### Phase 3: Real-Time Updates (1 Day)

**Make the UI come alive**:
- WebSocket or polling for progress updates
- Real-time activity log
- Live metrics

---

## Quick Win: Minimal Viable Implementation

**Could have working in 4 hours**:

```python
# In generic_framework/api/app.py

@app.post("/api/learning/surveys/{survey_id}/start")
async def start_survey_api(survey_id: str):
    """Start survey - spawn background task"""
    import asyncio

    survey = _surveys_storage[survey_id]
    survey["status"] = "running"

    # Spawn background task
    asyncio.create_task(run_survey_background(survey_id))

    return survey

async def run_survey_background(survey_id: str):
    """Background worker that does actual work"""
    from core.research.internet_strategy import InternetResearchStrategy
    from extraction.extractor import PatternExtractor

    survey = _surveys_storage[survey_id]

    # Initialize
    extractor = PatternExtractor(domain=survey.domain)
    searcher = InternetResearchStrategy({})

    # Generate search queries from domain name + survey name
    queries = [
        f"{survey.domain} recipes",
        f"{survey.name} {survey.domain}",
        survey.description
    ]

    for query in queries[:5]:  # 5 search rounds
        results = await searcher.search(query, limit=10)

        for result in results:
            # Extract pattern from search result snippet
            patterns = extractor.extract_from_text(result.snippet)

            # Save to domain
            if patterns:
                domain = get_domain(survey.domain)
                for pattern in patterns:
                    # Add pattern to domain
                    domain.patterns.append(pattern)

                # Update metrics
                survey["patterns_created"] += len(patterns)
                survey["progress"] = min(1.0, survey["patterns_created"] / survey["target_patterns"])

                logger.info(f"Survey {survey_id}: Extracted {len(patterns)} patterns from {result.url}")

    # Mark complete
    survey["status"] = "completed"
    logger.info(f"Survey {survey_id}: Completed with {survey['patterns_created']} patterns")
```

**That's it** - ~50 lines of code to make it actually work!

---

## Implementation Priority

### Option A: Quick Win (4 hours)
- Implement minimal background worker using DuckDuckGo search
- Extract patterns from search result snippets
- Actually creates patterns (vs just showing "running")

### Option B: Full Implementation (3-5 days)
- Phase 1: DuckDuckGo search (1 day)
- Phase 2: Full page scraping (2 days)
- Phase 3: Real-time updates (1 day)

### Option C: Document and Defer
- Document current state (what's working, what's not)
- Defer implementation until needed
- Focus on other priorities

---

## Why DuckDuckGo Instead of Scraping

| Aspect | Traditional Scraping | DuckDuckGo Search |
|--------|---------------------|-------------------|
| **Complexity** | High (HTML parsing, rate limits) | Low (just search API) |
| **Reliability** | Low (sites change structure) | High (DDG abstracts this) |
| **Speed** | Slow (page by page) | Fast (10 results at once) |
| **Maintenance** | Constant (site structure changes) | Rare (DDG handles it) |
| **Blocking** | Yes (sites may block) | No (search engines expect it) |
| **Existing Code** | Yes (scrapers exist) | Yes (researcher uses it) |

**DuckDuckGo is working right now** for researcher queries. We should reuse it!

---

## Technical Details: DuckDuckGo Search

### How It Currently Works

**File**: `generic_framework/core/research/internet_strategy.py`

```python
class InternetResearchStrategy:
    async def _search_with_mcp(self, query: str, limit: int):
        # Use DuckDuckGo HTML version
        ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ddg_url)
            results = self._parse_duckduckgo_results(response.text)

        return results  # List of {title, url, snippet}
```

### Search Result Structure

```python
SearchResult(
    content="Recipe snippet text...",
    source="https://sallysbakingaddiction.com/pie-recipe",
    relevance_score=0.8,
    metadata={
        'title': 'Classic Apple Pie',
        'url': 'https://...'
    }
)
```

---

## Questions

1. **Should we implement the quick win (4 hours) or full version (3-5 days)?**

2. **Is snippet extraction enough?** Or do we need full page scraping?

3. **Should patterns be auto-saved or require approval?**

4. **What should the "target patterns" number mean?**
   - Number of search queries to run?
   - Number of patterns to extract?
   - Both?

---

## Recommendation

**Start with Option A (Quick Win)**:
1. Implement background worker using existing DuckDuckGo search
2. Extract patterns from search result snippets
3. Actually save patterns to domain
4. Update metrics in real-time

**Time**: 4-6 hours
**Value**: Surveyor actually works instead of just looking like it works

**If snippets aren't enough**, add full page scraping (Option B Phase 2).

---

**What's your preference?** Quick win or full implementation?
