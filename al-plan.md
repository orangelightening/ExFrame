# AL-Plan: Autonomous Learning Implementation Plan

**Project**: EEFrame Self-Learning System
**Based on**: autonomouslearning (2026-01-12)
**Author**: Implementation Plan by Claude
**Status**: Ready for Development

---

## Executive Summary

This plan breaks down the implementation of EEFrame's autonomous learning system into 9 phases. The goal is **zero-touch pattern ingestion** - from web scraping to certified knowledge patterns with <5% human intervention, **plus autonomous research and report generation**.

### Key Addition: Research Generator

A research agent that can:
- Accept complex research requests (e.g., "survey 5km radius from Olive & Grove in San Clemente, CA")
- Decompose into sub-tasks (demographics, businesses, geography, etc.)
- Discover and scrape relevant data sources
- Correlate and analyze findings
- Generate comprehensive reports
- Store expertise patterns for instant future queries

### Target Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Patterns/day | 5-10 | 100+ |
| Human review | 100% | <5% |
| Certification accuracy | Unknown | >90% |
| System uptime | Manual | 24/7 |
| Scraping success | N/A | >80% |
| **Research requests/day** | 0 | 10+ |
| **Report delivery time** | N/A | <48 hours |

---

## Phase 1: Foundation & Core Infrastructure

### 1.1 Project Structure Setup

**Create new module**: `autonomous_learning/`

```
autonomous_learning/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── state.py           # State management
│   └── logger.py          # Structured logging
├── supervisor/
│   ├── __init__.py
│   ├── supervisor.py      # Main supervisor class
│   ├── heartbeat.py       # Heartbeat monitoring
│   ├── focus.py           # Focus drift detection
│   └── refocus.py         # Refocus strategies
├── certification/
│   ├── __init__.py
│   ├── panel.py           # Certification panel
│   ├── judges.py          # AI judge implementations
│   └── consensus.py       # Consensus calculation
├── scraping/
│   ├── __init__.py
│   ├── engine.py          # Scraping orchestrator
│   ├── stealth.py         # Stealth techniques
│   ├── errors.py          # Error handling
│   └── extractors/        # Content extractors
├── ingestion/
│   ├── __init__.py
│   ├── pipeline.py        # Main pipeline
│   ├── validation.py      # Schema validation
│   ├── deduplication.py   # Duplicate detection
│   └── storage.py         # Pattern storage
├── research/              # NEW: Research Generator
│   ├── __init__.py
│   ├── agent.py           # Main research agent
│   ├── planner.py         # Task decomposition
│   ├── sources/           # Data source handlers
│   │   ├── demographics.py
│   │   ├── geographic.py
│   │   ├── business.py
│   │   └── base.py
│   ├── analysis.py        # Data correlation
│   └── report.py          # Report generation
└── api/
    ├── __init__.py
    ├── supervisor.py      # Supervisor endpoints
    ├── certification.py   # Certification endpoints
    ├── scraping.py        # Scraping control
    └── research.py        # NEW: Research endpoints
```

**Tasks**:
1. Create directory structure
2. Set up package configuration (`pyproject.toml` or `setup.py`)
3. Create base configuration files (YAML)
4. Set up logging infrastructure
5. Create base state management classes

**Dependencies**:
- `httpx` - Async HTTP client
- `pydantic` - Data validation
- `asyncio` - Async orchestration
- `pyyaml` - Config parsing
- `tenacity` - Retry logic
- `numpy` - Similarity calculations
- `sentence-transformers` - **Local embeddings (no API costs)**
- `torch` - Backend for sentence-transformers
- `scikit-learn` - Alternative similarity algorithms
- `geopy` - Geographic calculations (research)
- `us` - US state/address parsing (research)
- `pandas` - Data analysis (research)

**Estimated**: 2-3 days

---

## Phase 2: AI Supervisor

### 2.1 Core Supervisor Class

**File**: `autonomous_learning/supervisor/supervisor.py`

```python
class AISupervisor:
    """Main supervisor for autonomous workers"""

    def __init__(self, config: SupervisorConfig):
        self.api_client = GenericLLMClient(config.api)
        self.heartbeat_monitor = HeartbeatMonitor(config.heartbeat)
        self.focus_detector = FocusDetector(config.focus)
        self.refocus_handler = RefocusHandler(config.refocus)
        self.workers: Dict[str, WorkerState] = {}

    async def monitor_worker(self, worker_id: str) -> MonitorResult:
        """Monitor a single worker"""
        heartbeat = await self.heartbeat_monitor.check(worker_id)
        focus = await self.focus_detector.analyze(worker_id)

        if not heartbeat.is_alive:
            return await self._handle_unresponsive(worker_id)
        if not focus.is_focused:
            return await self._handle_drift(worker_id, focus)

        return MonitorResult(status="healthy")

    async def assign_task(self, worker_id: str, task: SupervisorTask) -> TaskResult:
        """Assign a task to a worker"""
        # Implementation
```

### 2.2 Heartbeat Monitoring

**File**: `autonomous_learning/supervisor/heartbeat.py`

- Implement periodic health checks
- Track worker response times
- Detect hung/stuck workers
- State classification: active, sleeping, hung, looping, hallucinating

### 2.3 Focus Detection

**File**: `autonomous_learning/supervisor/focus.py`

- Implement conversation analysis
- Detect repetitive loops (>95% similarity)
- Detect topic drift (embedding distance)
- Detect hallucination patterns
- Generate focus reports with confidence scores

### 2.4 Refocus Strategies

**File**: `autonomous_learning/supervisor/refocus.py`

- `gentle_reminder` - Mild drift intervention
- `context_reset` - Moderate drift with full context
- `hard_reset` - Severe drift, fresh start

### 2.5 Generic LLM Client

**File**: `autonomous_learning/core/llm_client.py`

- LLM-agnostic interface
- Support OpenAI, Anthropic, GLM APIs
- Unified error handling
- Response parsing for different providers

**Tasks**:
1. Implement core supervisor class
2. Implement heartbeat monitoring
3. Implement focus detection with embeddings
4. Implement refocus strategies
5. Create generic LLM client interface
6. Add unit tests for each component
7. Create configuration schema

**Estimated**: 3-4 days

---

## Phase 3: Certification Panel

### 3.1 Panel Architecture

**File**: `autonomous_learning/certification/panel.py`

```python
class CertificationPanel:
    """Multi-AI consensus system for pattern validation"""

    def __init__(self, config: CertificationConfig):
        self.judges: List[AIJudge] = [
            GeneralistJudge(config.generalist),
            SpecialistJudge(config.specialist),
            SkepticJudge(config.skeptic),
        ]
        self.consensus_engine = ConsensusEngine(config.thresholds)

    async def certify_pattern(
        self, candidate: CandidatePattern
    ) -> CertificationResult:
        """Run pattern through certification panel"""
        reviews = await self._get_reviews(candidate)
        consensus = self.consensus_engine.calculate(reviews)

        # Skeptic veto for critical issues
        if consensus.has_critical_issues:
            return CertificationResult(status="rejected", issues=consensus.critical_issues)

        # Decision matrix
        if consensus.confidence >= 0.8 and consensus.unanimous:
            return CertificationResult(status="certified", confidence=consensus.confidence)
        elif consensus.confidence >= 0.6:
            return CertificationResult(status="provisional", requires_human_review=False)
        else:
            return CertificationResult(status="flagged", requires_human_review=True)
```

### 3.2 AI Judges

**File**: `autonomous_learning/certification/judges.py`

- `GeneralistJudge` - Pattern structure review (GPT-4, temp=0.3)
- `SpecialistJudge` - Domain accuracy (Claude 3.5 Sonnet, temp=0.2)
- `SkepticJudge` - Find flaws (Claude 3 Opus, temp=0.5)

### 3.3 Consensus Engine

**File**: `autonomous_learning/certification/consensus.py`

- Calculate average confidence
- Detect unanimity
- Apply bonus for unanimous agreement
- Identify critical issues from skeptic

**Tasks**:
1. Implement certification panel
2. Implement three AI judge types
3. Implement consensus calculation
4. Add retry logic for judge failures
5. Add fallback to 2 judges if one fails
6. Create certification result schema
7. Add unit tests

**Estimated**: 3-4 days

---

## Phase 4: Scraping Engine

### 4.1 Scraping Supervisor

**File**: `autonomous_learning/scraping/engine.py`

```python
class ScrapingSupervisor:
    """Orchestrate multiple scraping workers"""

    def __init__(self, config: ScrapingConfig):
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.stealth_manager = StealthManager(config.stealth)
        self.error_handler = ScrapingErrorHandler(config.error_handling)
        self.concurrency = config.concurrency

    async def orchestrate_scraping(self, targets: List[ScrapeTarget]):
        """Manage multiple scraping workers with coordination"""
        queue = asyncio.Queue()

        # Enqueue targets with priority
        for target in targets:
            await queue.put(target)

        # Spawn workers
        workers = [
            asyncio.create_task(self._worker(queue, i))
            for i in range(self.concurrency)
        ]

        # Supervise
        await asyncio.gather(*workers)
```

### 4.2 Stealth Techniques

**File**: `autonomous_learning/scraping/stealth.py`

- User agent rotation (pool of realistic browser UAs)
- Rate limiting with exponential backoff
- Request jitter (random timing within range)
- Warm-up sequence (gradual increase)
- Optional proxy rotation

### 4.3 Error Handling

**File**: `autonomous_learning/scraping/errors.py`

```python
class ScrapingErrorStrategy:
    ERROR_RESPONSES = {
        404: 'skip',
        403: 'backoff_and_retry',
        429: 'exponential_backoff',
        500: 'retry_with_care',
        503: 'backoff_long',
    }
```

### 4.4 Content Extractors

**Directory**: `autonomous_learning/scraping/extractors/`

- Base extractor interface
- HTML-based extractor (BeautifulSoup)
- JSON-based extractor
- Markdown-based extractor
- Domain-specific extractors (cooking, python, omv, etc.)

**Tasks**:
1. Implement scraping supervisor
2. Implement stealth techniques
3. Implement error handling strategy
4. Create base extractor interface
5. Implement HTML extractor
6. Implement JSON/Markdown extractors
7. Add rate limiting
8. Add unit tests

**Estimated**: 4-5 days

---

## Phase 5: Pattern Ingestion Pipeline

### 5.1 Main Pipeline

**File**: `autonomous_learning/ingestion/pipeline.py`

```python
class PatternIngestionPipeline:
    """From raw scrape to certified pattern"""

    def __init__(self, config: IngestionConfig):
        self.validator = PatternValidator()
        self.deduplicator = PatternDeduplicator()
        self.certification_panel = CertificationPanel(config.certification)
        self.storage = PatternStorage(config.storage)

    async def process_raw_content(self, raw: RawContent) -> IngestionResult:
        """Process raw content through the pipeline"""
        # Extract structured data
        candidate = await self._extract_candidate(raw)

        # Validate
        if not await self.validator.validate(candidate):
            return IngestionResult(status="rejected", reason="validation_failed")

        # De-duplicate
        duplicate = await self.deduplicator.check(candidate)
        if duplicate:
            return await self._handle_duplicate(candidate, duplicate)

        # Certify
        certification = await self.certification_panel.certify_pattern(candidate)

        # Store if certified
        if certification.status in ["certified", "provisional"]:
            await self.storage.store(candidate, certification)

        return IngestionResult(status=certification.status, certification=certification)
```

### 5.2 Validation

**File**: `autonomous_learning/ingestion/validation.py`

- Schema validation (Pydantic models)
- Required field checks
- Data type validation
- Format validation

### 5.3 Deduplication

**File**: `autonomous_learning/ingestion/deduplication.py`

- Text similarity (cosine similarity on **local embeddings**)
- Semantic similarity check
- Merge logic for near-duplicates
- Update logic for existing patterns

**Local Embedding Implementation**:
```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class LocalEmbeddingService:
    """Free local embeddings - no API costs"""

    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        # Model downloaded once, runs locally
        self.model = SentenceTransformer(model)
        self.dimension = 384  # for MiniLM-L6

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, show_progress_bar=False)

    def similarity(self, text1: str, text2: str) -> float:
        emb1 = self.embed([text1])
        emb2 = self.embed([text2])
        return cosine_similarity(emb1, emb2)[0][0]
```

### 5.4 Storage Integration

**File**: `autonomous_learning/ingestion/storage.py`

- Integrate with existing Expertise Scanner storage
- Store in `data/patterns/{domain}/`
- Update knowledge graph
- Log all certifications

**Tasks**:
1. Implement main pipeline
2. Implement validation logic
3. Implement deduplication with embeddings
4. Implement storage integration
5. Add merge/update logic
6. Add comprehensive logging
7. Add unit tests

**Estimated**: 3-4 days

---

## Phase 6: API & Dashboard

### 6.1 API Endpoints

**File**: `autonomous_learning/api/supervisor.py`

```python
# Supervisor control
POST   /api/supervisor/start
POST   /api/supervisor/stop
GET    /api/supervisor/status

# Task management
POST   /api/supervisor/assign
GET    /api/supervisor/tasks
GET    /api/supervisor/task/:id

# Monitoring
GET    /api/supervisor/heartbeat/:worker
GET    /api/supervisor/focus/:worker
POST   /api/supervisor/refocus/:worker
```

**File**: `autonomous_learning/api/certification.py`

```python
POST   /api/certification/submit
GET    /api/certification/status/:id
GET    /api/certification/queue
```

**File**: `autonomous_learning/api/scraping.py`

```python
POST   /api/scraping/start
POST   /api/scraping/stop
POST   /api/scraping/add-targets
GET    /api/scraping/status
GET    /api/scraping/results
```

### 6.2 Dashboard UI

**Create new frontend**: `autonomous_learning/dashboard/`

- Real-time supervisor status
- Worker heartbeat visualization
- Focus drift alerts
- Certification queue
- Scraping progress
- Pattern ingestion statistics

**Technology**:
- React (matching Expertise Scanner)
- Tailwind CSS v3
- WebSocket for real-time updates

**Tasks**:
1. Implement all API endpoints
2. Add WebSocket support for real-time updates
3. Create dashboard layout
4. Implement supervisor status view
5. Implement certification queue view
6. Implement scraping progress view
7. Add alert system
8. Add configuration UI

**Estimated**: 4-5 days

---

## Phase 7: Integration & Testing

### 7.1 Integration with EEFrame

**Tasks**:
1. Wire autonomous learning into Generic Framework
2. Add domain-specific extractors
3. Configure certification judges for each domain
4. Set up continuous learning loop

### 7.2 Testing

**Unit Tests**:
- Supervisor components
- Certification panel
- Scraping engine
- Ingestion pipeline

**Integration Tests**:
- End-to-end pipeline
- Supervisor + worker interaction
- Certification panel + storage

**24-Hour Test Run**:
- Deploy autonomous system
- Monitor for 24 hours
- Collect metrics
- Analyze results
- Document findings

**Tasks**:
1. Write unit tests (target: 80% coverage)
2. Write integration tests
3. Set up test environment
4. Run 24-hour autonomous test
5. Collect and analyze metrics
6. Document issues and fixes

**Estimated**: 3-4 days

---

## Phase 8: Human Escalation & Production Hardening

### 8.1 Human Escalation Triggers

Define when humans should be involved:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Low confidence certification | < 0.6 | Flag for review |
| Judge disagreement | No consensus | Add 4th judge |
| Critical system failure | Crash | Alert + log |
| Scraping failure rate | > 50% | Alert |
| Pattern rejection rate | > 20% | Alert |

### 8.2 Production Hardening

**Tasks**:
1. Add authentication for APIs
2. Add rate limiting for APIs
3. Set up monitoring dashboards
4. Configure alerts (Prometheus/Grafana)
5. Add backup/restore for state
6. Add graceful shutdown
7. Add health check endpoints

**Estimated**: 2-3 days

---

## Phase 9: Research Generator & Report System

### 9.1 Overview

The Research Generator accepts complex research requests and produces comprehensive reports. Example request:

> "I would like a survey of the area in a 5km radius from the corners of Olive and Grove in San Clemente, CA. I want the demographics of the residents and transients and the stores that service them. Write a report and deliver it within 2 days."

### 9.2 Research Agent

**File**: `autonomous_learning/research/agent.py`

```python
class ResearchAgent:
    """Autonomous research and report generation"""

    def __init__(self, config: ResearchConfig):
        self.planner = ResearchPlanner(config)
        self.supervisor = AISupervisor(config.supervisor)
        self.scraping_engine = ScrapingEngine(config.scraping)
        self.analyzer = DataAnalyzer(config.analysis)
        self.report_generator = ReportGenerator(config.reporting)
        self.storage = PatternStorage(config.storage)

    async def process_request(self, request: ResearchRequest) -> ResearchResult:
        """Process research request from query to report"""
        # 1. Parse and decompose request
        plan = await self.planner.create_plan(request)

        # 2. Execute research tasks
        findings = await self._execute_research_plan(plan)

        # 3. Analyze and correlate
        analysis = await self.analyzer.correlate(findings)

        # 4. Generate report
        report = await self.report_generator.generate(request, analysis)

        # 5. Store expertise patterns
        await self._store_expertise(request, analysis, report)

        return ResearchResult(report=report, patterns_created=analysis.patterns)
```

### 9.3 Research Planner (Task Decomposition)

**File**: `autonomous_learning/research/planner.py`

```python
class ResearchPlanner:
    """Decompose complex requests into actionable research tasks"""

    async def create_plan(self, request: ResearchRequest) -> ResearchPlan:
        """
        Example decomposition:
        Input: "survey 5km radius from Olive & Grove in San Clemente, CA..."

        Output: ResearchPlan with tasks:
        - Geocode location (Olive & Grove, San Clemente, CA)
        - Define 5km radius boundary
        - Collect demographics (Census API, citydata.com)
        - Identify businesses (Google Maps, Yelp, Yellow Pages)
        - Map retail/service categories
        - Analyze transient population patterns
        - Correlate demographics with business types
        """
        location = await self._geocode(request.location_query)
        boundary = self._define_radius(location, request.radius)

        tasks = [
            DemographicTask(location=location, boundary=boundary),
            BusinessTask(location=location, boundary=boundary),
            GeographicTask(location=location, boundary=boundary),
            # ... more tasks based on request
        ]

        return ResearchPlan(location=location, boundary=boundary, tasks=tasks)
```

### 9.4 Data Source Handlers

**Directory**: `autonomous_learning/research/sources/`

**Base Handler** (`base.py`):
```python
class DataSourceHandler(ABC):
    """Base class for data source handlers"""

    @abstractmethod
    async def fetch(self, task: ResearchTask) -> ResearchData:
        pass
```

**Demographics Handler** (`demographics.py`):
- Census API (data.census.gov)
- City-Data.com
- County records
- Income, age, population density

**Geographic Handler** (`geographic.py`):
- Geocoding (OpenStreetMap Nominatim - free)
- Boundary calculations (geopy)
- Maps and imagery

**Business Handler** (`business.py`):
- Google Maps (Places API)
- Yelp Fusion API
- Yellow Pages scraping
- Chamber of commerce directories

### 9.5 Data Analysis

**File**: `autonomous_learning/research/analysis.py`

```python
class DataAnalyzer:
    """Correlate and analyze research findings"""

    async def correlate(self, findings: List[ResearchData]) -> Analysis:
        """
        Example correlations:
        - Map demographics → business types served
        - Identify underserved segments
        - Compare transient vs resident patterns
        - Calculate market gaps
        """
        demographics = next(f for f in findings if f.type == "demographics")
        businesses = next(f for f in findings if f.type == "businesses")

        # Use embeddings to find patterns
        patterns = await self._extract_patterns(demographics, businesses)

        return Analysis(
            findings=findings,
            correlations=self._calculate_correlations(findings),
            patterns=patterns,
            insights=self._generate_insights(findings)
        )
```

### 9.6 Report Generation

**File**: `autonomous_learning/research/report.py`

```python
class ReportGenerator:
    """Generate comprehensive research reports"""

    async def generate(self, request: ResearchRequest, analysis: Analysis) -> Report:
        """
        Output formats:
        - Markdown (default)
        - PDF (with charts)
        - HTML (interactive)
        - JSON (API consumption)
        """

        sections = [
            ExecutiveSummary(request, analysis),
            Methodology(analysis.methodology),
            Findings(analysis.findings),
            Correlations(analysis.correlations),
            Insights(analysis.insights),
            Appendix(analysis.raw_data),
        ]

        report = Report(
            title=request.title,
            generated_at=datetime.now(),
            sections=sections,
            format=request.format
        )

        return await self._render_report(report)
```

### 9.7 Expertise Pattern Extraction

**Key Feature**: Every research project generates reusable patterns

```python
async def _store_expertise(self, request, analysis, report):
    """Extract and store patterns for future instant queries"""

    patterns = [
        Pattern(
            domain="location_analysis",
            name=f"{request.location}_demographics_profile",
            problem=f"Understanding demographics of {request.location}",
            solution=analysis.demographic_summary,
            conditions={"location_type": analysis.location_type},
            confidence=0.9
        ),
        Pattern(
            domain="business_analysis",
            name=f"{request.location}_business_landscape",
            problem=f"Business composition in {request.location}",
            solution=analysis.business_distribution,
            conditions={"market_segment": analysis.segments},
            confidence=0.85
        ),
        # ... more patterns
    ]

    for pattern in patterns:
        await self.storage.store(pattern)
```

### 9.8 Research API Endpoints

**File**: `autonomous_learning/api/research.py`

```typescript
// Submit research request
POST   /api/research/submit
Body: {
  query: string,
  deadline?: string,
  format: 'markdown' | 'pdf' | 'html' | 'json'
}
Response: { research_id: string, estimated_completion: string }

// Check status
GET    /api/research/status/:id
Response: {
  status: 'pending' | 'in_progress' | 'completed' | 'failed',
  progress: number,
  current_task: string
}

// Get results
GET    /api/research/results/:id
Response: { report: Report, patterns_created: number }

// List research projects
GET    /api/research/list
Response: [{ id, query, status, created_at }]

// Query expertise (instant results from stored patterns)
POST   /api/research/query
Body: { question: string, location?: string }
Response: { answer: string, sources: Pattern[] }
```

### 9.9 Example Research Flow

```
USER QUERY
"Survey 5km radius from Olive & Grove, San Clemente CA"
     │
     ▼
┌─────────────────────────────────────────┐
│  1. PARSE & GEOCODE                     │
│     - Identify location: 33.426, -117.6 │
│     - Define 5km radius boundary        │
└─────────────┬───────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  2. PLAN RESEARCH TASKS                 │
│     ☐ Demographics (Census, citydata)   │
│     ☐ Businesses (Yelp, Google Maps)    │
│     ☐ Geographic (OSM, maps)            │
│     ☐ Transients (tourism, hotels)      │
└─────────────┬───────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  3. EXECUTE (PARALLEL)                  │
│     ScrapingEngine → multiple sources   │
│     Supervisor → monitors progress      │
└─────────────┬───────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  4. ANALYZE & CORRELATE                 │
│     - Demographics vs Business types    │
│     - Market gaps                       │
│     - Service coverage                  │
└─────────────┬───────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  5. GENERATE REPORT                     │
│     - Executive summary                 │
│     - Detailed findings                 │
│     - Visualizations                    │
└─────────────┬───────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  6. STORE EXPERTISE                     │
│     3 patterns added to knowledge base  │
│     Future queries answered instantly   │
└─────────────────────────────────────────┘
              ▼
         DELIVER REPORT
```

**Tasks**:
1. Implement ResearchAgent orchestrator
2. Implement ResearchPlanner (task decomposition)
3. Create base DataSourceHandler class
4. Implement DemographicsHandler (Census, citydata)
5. Implement GeographicHandler (geocoding, boundaries)
6. Implement BusinessHandler (Yelp, Google Maps)
7. Implement DataAnalyzer (correlations)
8. Implement ReportGenerator (multiple formats)
9. Implement expertise pattern extraction
10. Add research API endpoints
11. Add research dashboard UI
12. Add unit tests for each component

**Data Sources** (free/accessible):
- **Geocoding**: OpenStreetMap Nominatim API (free)
- **Demographics**: US Census API (free), City-Data.com (scraping)
- **Businesses**: Yelp Fusion API (free tier), Google Places (paid, optional)
- **Geography**: OpenStreetMap, USGS

**Estimated**: 5-7 days

---

## Dependencies & Integration Points

### Existing EEFrame Components

| Component | Integration Point |
|-----------|-------------------|
| Expertise Scanner | Pattern storage (`data/patterns/`) |
| Generic Framework | Domain knowledge bases, research queries |
| GLM API | LLM client for supervisor/judges/research |
| Monitoring Stack | Metrics and logging |

### External Services (Free/Cheap)

| Service | Purpose | Config |
|---------|---------|--------|
| GLM API | Primary LLM (supervisor/research) | `LLM_API_ENDPOINT` |
| OpenAI API | Generalist judge (optional) | `OPENAI_API_KEY` |
| Anthropic API | Specialist/Skeptic judges (optional) | `ANTHROPIC_API_KEY` |
| **OpenStreetMap Nominatim** | Geocoding (free) | `NOMINATIM_API_URL` |
| **US Census API** | Demographics (free) | `CENSUS_API_KEY` |
| **Yelp Fusion API** | Business data (free tier) | `YELP_API_KEY` |

**Local Services** (no external costs):
- **sentence-transformers** - Local embeddings for similarity detection
- Models: `all-MiniLM-L6-v2` (lightweight, fast) or `all-mpnet-base-v2` (higher quality)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM hallucination | Multi-AI consensus, skeptic veto |
| API rate limits | Exponential backoff, multiple APIs |
| Scraping detection | Stealth techniques, proxy rotation |
| Judge disagreement | Add 4th judge, human escalation |
| System crash | State persistence, watchdog restart |
| Poor quality patterns | Validation, certification thresholds |
| Research data gaps | Multiple source aggregation, human escalation |

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1: Foundation | 2-3 days | None |
| 2: AI Supervisor | 3-4 days | Phase 1 |
| 3: Certification Panel | 3-4 days | Phase 1, 2 |
| 4: Scraping Engine | 4-5 days | Phase 1 |
| 5: Ingestion Pipeline | 3-4 days | Phase 1, 3, 4 |
| 6: API & Dashboard | 4-5 days | Phase 2, 3, 5 |
| 7: Integration & Testing | 3-4 days | All previous |
| 8: Production Hardening | 2-3 days | Phase 7 |
| **9: Research Generator** | **5-7 days** | **Phase 1, 2, 4** |

**Total Estimated**: 29-39 days (~6-8 weeks)

---

## Success Criteria

Phase is complete when:
- [ ] All components implemented per specification
- [ ] Unit tests pass with >80% coverage
- [ ] Integration tests pass
- [ ] 24-hour autonomous test run completes
- [ ] Success metrics met:
  - 100+ patterns/day
  - <5% human intervention
  - 10+ research requests/day capability
  - <48 hour report delivery
- [ ] Dashboard functional and monitoring
- [ ] Research generator accepts complex queries
- [ ] Expertise patterns extracted from research
- [ ] Documentation complete

---

## Open Questions

1. **Embedding Model**: Which local model? (`all-MiniLM-L6-v2` fast vs `all-mpnet-base-v2` accurate)
2. **Proxy Service**: Need for proxy rotation? If so, which provider?
3. **Domain Sources**: Initial seed URLs for each domain?
4. **Judge Models**: Use only GLM API for all judges, or configure separate APIs?
5. **State Persistence**: File-based or database for state storage?

---

## Cost Considerations

**Free/Local Options** (preferred):
- `sentence-transformers` - Local embeddings, no API costs
- GLM API - Already configured, primary LLM
- Built-in judges using GLM API
- **OpenStreetMap Nominatim** - Free geocoding
- **US Census API** - Free demographics data

**Optional Paid APIs** (if higher quality needed):
- OpenAI GPT-4 - Generalist judge
- Anthropic Claude 3.5/3 Opus - Specialist/Skeptic judges
- Yelp Fusion API - Business data (free tier: 5000 calls/day)
- Google Places API - Business data (paid, optional)

**Recommendation**: Start with GLM API for all LLM operations, upgrade specific judges if needed based on certification quality metrics. Use free data sources (Census, OSM) for research.

---

**Document Version**: 1.1
**Created**: 2026-01-12
**Updated**: 2026-01-12 (Added Phase 9: Research Generator)
**Status**: Ready for Development
