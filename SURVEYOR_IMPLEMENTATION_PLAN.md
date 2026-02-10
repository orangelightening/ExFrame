# Surveyor Implementation Plan

**Status**: 🎯 Planning Phase
**Created**: February 7, 2026
**Goal**: Implement autonomous batch pattern collection system

---

## Overview

The Surveyor system is designed to **autonomously collect knowledge patterns** from web sources at scale. It goes beyond query by actively scraping, extracting, and certifying patterns through AI judges.

**Value Proposition**: Batch pattern collection (100+ patterns in 24 hours) vs manual entry or one-by-one querying.

---

## Current State Assessment

### ✅ What Works (Completed)

**API Layer** (`autonomous_learning/api/surveys.py`):
- ✅ Full CRUD operations for surveys
- ✅ Survey lifecycle: Create, Start, Pause, Resume, Stop
- ✅ Metrics endpoint (stubs)
- ✅ Status tracking

**State Management** (`autonomous_learning/core/state.py`):
- ✅ Thread-safe file-based persistence (JSON)
- ✅ Automatic backups
- ✅ Survey state tracking
- ✅ Worker state monitoring

**Configuration** (`autonomous_learning/core/config.py`):
- ✅ YAML-based configuration
- ✅ Supervisor config
- ✅ 5-judge certification panel config
- ✅ Scraping config (rate limiting, stealth)
- ✅ Ingestion config

**Data Models**:
- ✅ `SurveyState` - Complete survey tracking
- ✅ `WorkerState` - Worker monitoring
- ✅ `SystemState` - Global state

**Frontend UI**:
- ✅ Surveyor tab in navigation
- ✅ Survey list view
- ✅ Survey detail panel
- ✅ Create/Edit survey modal
- ✅ Real-time metrics display
- ✅ Activity log

### ❌ What's Missing (To Implement)

**Scraping Engine** (`autonomous_learning/scraping/`):
- ❌ Web scraper implementation
- ❌ Rate limiting with exponential backoff
- ❌ Stealth mode (user agents, jitter)
- ❌ Error handling (404, 429, retries)
- ❌ Content extraction

**Pattern Extraction** (`autonomous_learning/ingestion/`):
- ❌ LLM-based pattern extraction from scraped content
- ❌ Pattern validation (required fields)
- ❌ Deduplication (similarity threshold)
- ❌ Backup before write

**Certification Panel** (`autonomous_learning/certification/`):
- ❌ 5 AI judges implementation
- ❌ Judge scoring logic
- ❌ Weighted voting (skeptic 1.5x)
- ❌ Threshold enforcement (0.8 certified, 0.6 provisional)
- ❌ Unanimous bonus (+0.1)
- ❌ Skeptic veto

**Supervisor** (`autonomous_learning/supervisor/`):
- ❌ AI supervisor orchestration
- ❌ Worker task assignment
- ❌ Focus monitoring (detect drift/repetition)
- ❌ Heartbeat monitoring
- ❌ Error recovery

**Workers** (Autonomous Agents):
- ❌ Worker pool implementation
- ❌ Task queue
- ❌ Scraping workers
- ❌ Extraction workers
- ❌ Certification workers

**Survey Execution Loop**:
- ❌ Main survey orchestration
- ❌ Scraping → Extraction → Certification pipeline
- ❌ Progress tracking
- ❌ Timeline enforcement
- ❌ Target achievement (stop when N patterns certified)

---

## Implementation Strategy

### Phase 1: Minimal Viable Survey (1 Week)

**Goal**: End-to-end survey with single domain, single URL

**Scope**:
```
User creates survey (cooking domain, allrecipes.com)
  → Scrapes pages from seed URL
  → Extracts patterns using LLM
  → Certifies using 1 judge (simplified)
  → Saves to domain patterns.json
  → Updates survey progress
```

**Tasks**:
1. **Simple Scraper** (2 days)
   - Basic HTTP requests
   - HTML parsing (BeautifulSoup)
   - Text extraction
   - No rate limiting yet (add in Phase 2)

2. **Pattern Extractor** (2 days)
   - LLM prompt: "Extract patterns from this content"
   - Parse LLM response into pattern JSON
   - Validate required fields
   - Save to temporary staging

3. **Single Judge** (1 day)
   - Use existing LLM endpoint
   - Score pattern (0-1 confidence)
   - If ≥0.8, save to domain patterns.json

4. **Survey Loop** (2 days)
   - Orchestrate: Scrape → Extract → Certify → Repeat
   - Stop when: N patterns OR timeline expires
   - Update progress metrics
   - Handle errors gracefully

**Success Criteria**:
- ✅ Can create survey via UI
- ✅ Survey runs autonomously
- ✅ Patterns appear in domain after completion
- ✅ Progress updates in UI

---

### Phase 2: Production-Grade Scraping (1 Week)

**Goal**: Robust, polite web scraping

**Tasks**:
1. **Rate Limiting** (1 day)
   - Implement token bucket
   - 1 request/second with burst of 5
   - Exponential backoff on errors

2. **Stealth Mode** (1 day)
   - Rotate user agents
   - Add jitter (±20%)
   - Warm-up requests
   - Respect robots.txt

3. **Error Handling** (2 days)
   - Retry logic (max 3 retries)
   - Skip 404s
   - Back off on 429 (rate limit)
   - Log all errors

4. **Content Extraction** (2 days)
   - Extract main content (ignore nav/footer)
   - Handle different page structures
   - Extract images/links
   - Clean text

5. **Crawl Depth** (1 day)
   - Follow links from seed URL
   - Limit crawl depth (configurable)
   - Domain restriction (stay on target)

**Success Criteria**:
- ✅ Can scrape 100+ pages without being blocked
- ✅ Respects rate limits
- ✅ Graceful error handling

---

### Phase 3: Multi-Judge Certification (1 Week)

**Goal**: 5-judge AI panel with weighted voting

**Tasks**:
1. **Judge Implementations** (3 days)
   - Generalist (structure review)
   - Specialist (domain accuracy)
   - Skeptic (critical analysis, 1.5x weight)
   - Contextualist (context fit)
   - Human (manual review)

2. **Voting Logic** (2 days)
   - Collect scores from all judges
   - Apply weights
   - Calculate weighted average
   - Check thresholds
   - Apply unanimous bonus

3. **Skeptic Veto** (1 day)
   - If skeptic score < 0.3, veto pattern
   - Flag for human review
   - Log veto reason

4. **Certification Workflow** (1 day)
   - Certified (≥0.8) → Save to domain
   - Provisional (0.6-0.8) → Flag for review
   - Rejected (<0.6) → Discard with log

**Success Criteria**:
- ✅ 5 judges score each pattern
- ✅ Weighted voting works correctly
- ✅ Skeptic veto functional
- ✅ Certification metrics accurate

---

### Phase 4: Supervisor & Workers (2 Weeks)

**Goal**: Autonomous worker pool with oversight

**Tasks**:
1. **Worker Pool** (3 days)
   - Create worker instances
   - Task queue (asyncio)
   - Worker lifecycle (spawn, monitor, reap)

2. **Task Assignment** (2 days)
   - Supervisor assigns tasks to workers
   - Task types: scrape, extract, certify
   - Load balancing

3. **Focus Monitoring** (3 days)
   - Detect drift (off-topic patterns)
   - Detect repetition (similar patterns)
   - Alert if focus < 0.7
   - Adjust collection instructions

4. **Heartbeat System** (2 days)
   - Workers send heartbeat every 30s
   - Supervisor detects missed heartbeats
   - Restart failed workers
   - Log worker failures

5. **Error Recovery** (3 days)
   - Retry failed tasks
   - Skip permanently broken URLs
   - Log all errors
   - Continue survey on errors

6. **Progress Tracking** (1 day)
   - Real-time progress updates
   - Throughput calculation (patterns/hour)
   - ETA to completion

**Success Criteria**:
- ✅ Multiple workers run in parallel
- ✅ Supervisor monitors all workers
- ✅ Failed tasks are retried
- ✅ Focus drift detected

---

### Phase 5: Advanced Features (1 Week)

**Goal**: Neighbourhood surveys, advanced UI

**Tasks**:
1. **Neighbourhood Surveys** (2 days)
   - Filter across multiple domains
   - User-defined filter criteria
   - Cross-domain pattern collection

2. **Advanced UI** (2 days)
   - Live activity log
   - Judge activity chart
   - Error visualization
   - Focus score graph

3. **Reporting** (2 days)
   - Survey completion report
   - Pattern statistics
   - Judge performance
   - Error summary

4. **Testing** (1 day)
   - Unit tests for components
   - Integration test for full survey
   - Edge case handling

**Success Criteria**:
- ✅ Neighbourhood surveys work
- ✅ UI shows real-time activity
- ✅ Reports generated on completion

---

## Technical Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Surveyor UI                           │
│  (Create surveys, monitor progress, view results)       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Survey API (FastAPI)                        │
│  /api/surveys - CRUD, lifecycle control                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Supervisor (Orchestrator)                     │
│  - Assigns tasks to workers                             │
│  - Monitors heartbeats                                  │
│  - Detects focus drift                                  │
│  - Handles errors                                       │
└─────────────┬───────────────┬───────────────┬───────────┘
              │               │               │
              ▼               ▼               ▼
     ┌────────────┐  ┌─────────────┐  ┌──────────────┐
     │  Worker 1  │  │  Worker 2   │  │  Worker N    │
     │  (Scrape)  │  │ (Extract)   │  │ (Certify)    │
     └─────┬──────┘  └──────┬──────┘  └──────┬───────┘
           │                │                │
           ▼                ▼                ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │  Scraper │    │ Extractor│    │  Judges  │
     └─────┬────┘    └────┬─────┘    └────┬─────┘
           │              │               │
           └──────────────┴───────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │  State Manager │
                 │  (Persistence) │
                 └────────────────┘
```

### Data Flow

```
1. User creates survey (via UI)
   → API: POST /api/surveys
   → State: Create SurveyState
   → Response: survey_id

2. User starts survey
   → API: POST /api/surveys/{id}/start
   → State: status = "running"
   → Supervisor: Spawn workers

3. Worker 1: Scrape
   → Fetch URL
   → Extract content
   → Return text

4. Worker 2: Extract
   → Send text to LLM
   → Prompt: "Extract patterns"
   → Parse response
   → Return patterns

5. Worker 3: Certify
   → Send pattern to 5 judges
   → Each judge scores (0-1)
   → Apply weights
   → Check thresholds
   → Return: certified/rejected/flagged

6. Supervisor: Loop
   → Assign new tasks
   → Monitor progress
   → Update state
   → Check: target reached OR timeline expired?

7. Survey complete
   → State: status = "completed"
   → API: Update metrics
   → UI: Show results
```

---

## Configuration File

Create `autonomous_learning.yaml`:

```yaml
# Autonomous Learning Configuration

supervisor:
  api:
    url: https://api.anthropic.com/v1/messages
    model: claude-sonnet-4-5-20250929
    max_tokens: 4096
    temperature: 0.7

  heartbeat:
    interval: 30  # seconds
    timeout: 10
    max_missed: 3

  focus:
    window_size: 10  # patterns
    drift_threshold: 0.3
    repetition_threshold: 0.95

certification:
  judges:
    - name: generalist
      role: structure_review
      api_url: https://api.anthropic.com/v1/messages
      model: claude-sonnet-4-5-20250929
      temperature: 0.3
      weight: 1.0

    - name: specialist
      role: domain_accuracy
      api_url: https://api.anthropic.com/v1/messages
      model: claude-sonnet-4-5-20250929
      temperature: 0.2
      weight: 1.0

    - name: skeptic
      role: critical_analysis
      api_url: https://api.anthropic.com/v1/messages
      model: claude-sonnet-4-5-20250929
      temperature: 0.5
      weight: 1.5  # Higher weight

    - name: contextualist
      role: context_fit
      api_url: https://api.anthropic.com/v1/messages
      model: claude-sonnet-4-5-20250929
      temperature: 0.4
      weight: 1.0

    - name: human
      role: last_resort
      is_human: true
      weight: 1.0

  thresholds:
    certified: 0.8
    provisional: 0.6
    unanimous_bonus: 0.1
    skeptic_veto_critical: true

scraping:
  rate_limit:
    requests_per_second: 1
    burst: 5
    exponential_backoff: true

  error_handling:
    max_retries: 3
    skip_404: true
    backoff_429: true

  stealth:
    enable: true
    user_agents:
      - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    jitter_percent: 20
    warm_up_requests: 3

  pilot_domain: cooking

ingestion:
  validation:
    strict_mode: true
    required_fields:
      - name
      - description
      - problem
      - solution

  deduplication:
    similarity_threshold: 0.85
    method: text_based  # or jaccard

  storage:
    pattern_directory: data/patterns/{domain}/
    backup_enabled: true

logging:
  level: INFO
  log_dir: logs/autonomous_learning
  json_output: true
```

---

## API Endpoints

### Survey Management

```
POST   /api/surveys                    # Create survey
GET    /api/surveys                    # List surveys
GET    /api/surveys/{id}               # Get survey details
PUT    /api/surveys/{id}               # Update survey
DELETE /api/surveys/{id}               # Delete survey
```

### Survey Control

```
POST /api/surveys/{id}/start           # Start survey
POST /api/surveys/{id}/stop            # Stop survey
POST /api/surveys/{id}/pause           # Pause survey
POST /api/surveys/{id}/resume          # Resume survey
```

### Monitoring

```
GET /api/surveys/{id}/metrics          # Real-time metrics
GET /api/surveys/{id}/patterns         # Get patterns from survey
GET /api/surveys/{id}/report           # Survey report
GET /api/surveys/{id}/activity         # Activity log
```

---

## Success Metrics

### Phase 1 (Week 1)
- ✅ Can run end-to-end survey
- ✅ Collects 10+ patterns
- ✅ Patterns validate correctly

### Phase 2 (Week 2)
- ✅ Can scrape 100+ pages
- ✅ No blocking/banning
- ✅ Error rate < 5%

### Phase 3 (Week 3)
- ✅ 5 judges score patterns
- ✅ Voting logic correct
- ✅ Certification rate > 60%

### Phase 4 (Week 5)
- ✅ 5+ workers run in parallel
- ✅ Supervisor detects failures
- ✅ Focus drift detected

### Phase 5 (Week 6)
- ✅ Neighbourhood surveys work
- ✅ UI shows live activity
- ✅ Reports generated

---

## Risk Mitigation

### Risk 1: Getting Blocked While Scraping
**Mitigation**:
- Conservative rate limits (1 req/sec)
- Stealth mode (user agents, jitter)
- Respect robots.txt
- Exponential backoff on errors

### Risk 2: Poor Pattern Quality
**Mitigation**:
- 5-judge certification panel
- Skeptic veto on critical issues
- Human review on flagged patterns
- Focus monitoring

### Risk 3: LLM Costs
**Mitigation**:
- Cache judge responses
- Batch pattern extraction
- Use smaller models where possible
- Set daily limits

### Risk 4: System Complexity
**Mitigation**:
- Incremental phases
- Test each phase thoroughly
- Keep code simple (KISS)
- Document everything

---

## Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Choose starting phase** - Phase 1 (MVP) recommended
3. **Set up dev environment** - Test survey creation
4. **Implement Phase 1** - End-to-end working survey
5. **Test thoroughly** - Before moving to Phase 2

---

## Questions for You

1. **Priority**: Which phase should we start with? (Recommend: Phase 1)

2. **LLM endpoint**: Use Claude API like the rest of ExFrame?

3. **Rate limiting**: 1 request/second OK for testing?

4. **Target domains**: Which domain for initial testing? (cooking?)

5. **Timeline**: How aggressive should we be? (6 weeks total)

6. **Parallel development**: Want to start multiple phases at once?

---

**Ready to implement when you are!** Let me know which phase to start with.
