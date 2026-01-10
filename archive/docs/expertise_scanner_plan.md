# Expertise Scanner - Implementation Plan

**Status:** Planning Phase
**Last Updated:** 2026-01-04

---

## Overview

Build a general-purpose tool that scans any well-documented domain, extracts expertise patterns, and maps relationships across domains.

**Current State:** OMV Co-Pilot (24 patterns) - proof of concept
**Goal:** Multi-domain expertise scanner with cross-domain analysis

---

## Phase 1: Core Pattern Engine (Days 1-3)

### 1.1 Define Pattern Schema

Create a unified pattern structure that works across all domains:

```python
class Pattern(BaseModel):
    id: str
    domain: str                    # "omv", "cooking", "python", "diy", "first_aid", "gardening"
    name: str                      # Short descriptive name
    pattern_type: str              # "troubleshooting", "procedure", "substitution", "decision"
    description: str               # What this pattern does

    # The core expertise
    problem: str                   # What problem does this solve?
    solution: str                  # How is it solved?
    steps: List[str]               # Procedural steps (if applicable)

    # Relationships
    related_patterns: List[str]    # IDs of related patterns
    prerequisites: List[str]       # What must be done first
    alternatives: List[str]        # Other ways to solve this

    # Metadata
    confidence: float              # 0-1, how reliable is this pattern?
    sources: List[str]             # URLs or references
    tags: List[str]                # Free-form labels
    examples: List[str]            # Concrete examples
```

**Files:**
- `src/pattern_extractor/models.py` - Pattern data models

---

### 1.2 Pattern Extraction Engine

Core extraction logic using LLM:

```python
class PatternExtractor:
    """Extract expertise patterns from text using LLM"""

    def extract_from_text(self, text: str, domain: str) -> List[Pattern]:
        """Extract patterns from raw text"""
        pass

    def extract_from_qa(self, question: str, answer: str, domain: str) -> Pattern:
        """Extract pattern from Q&A pair"""
        pass

    def extract_from_procedure(self, steps: List[str], domain: str) -> Pattern:
        """Extract pattern from procedural steps"""
        pass

    def score_confidence(self, pattern: Pattern) -> float:
        """Score pattern reliability based on source quality"""
        pass
```

**Files:**
- `src/pattern_extractor/extractor.py` - Core extraction logic
- `src/pattern_extractor/prompts.py` - LLM prompts for extraction

---

### 1.3 LLM Prompts for Extraction

Create specialized prompts for each pattern type:

```
PATTERN_EXTRACTION_PROMPT = """
You are an expertise extraction assistant. Analyze the following text from {domain}
and extract problem-solving patterns.

For each pattern, identify:
1. The problem being solved
2. The solution approach
3. Step-by-step procedure (if applicable)
4. Decision points or branches
5. Related patterns

Output as JSON matching the Pattern schema.
"""
```

**Files:**
- `src/pattern_extractor/prompts.py`

---

## Phase 2: Ingestion Pipeline (Days 4-6)

### 2.1 URL Scraper

```python
class URLScraper:
    """Scrape and extract text from URLs"""

    def scrape_url(self, url: str) -> str:
        """Fetch and extract main content from URL"""
        pass

    def scrape_multiple(self, urls: List[str]) -> Dict[str, str]:
        """Scrape multiple URLs in parallel"""
        pass
```

**Target Sources:**
- Cooking: AllRecipes.com, FoodNetwork.com
- Python: Stack Overflow questions, Real Python
- DIY: This Old House, DIY Network

**Files:**
- `src/pattern_extractor/ingestion/scraper.py`

---

### 2.2 PDF Parser

```python
class PDFParser:
    """Extract text from PDF documents"""

    def extract_text(self, pdf_path: str) -> str:
        """Extract all text from PDF"""
        pass

    def extract_by_page(self, pdf_path: str) -> List[str]:
        """Extract text page by page"""
        pass
```

**Files:**
- `src/pattern_extractor/ingestion/pdf_parser.py`

---

### 2.3 Domain-Specific Parsers

Each domain needs custom parsing:

```python
# Cooking: Parse recipe format
class RecipeParser:
    """Parse recipes and extract cooking patterns"""

    def parse_ingredients(self, text: str) -> List[Dict]
    def parse_steps(self, text: str) -> List[str]
    def find_substitutions(self, ingredients: List) -> List[Pattern]

# Python: Parse code snippets
class CodeParser:
    """Parse Stack Overflow Q&A"""

    def extract_error_pattern(self, question: str, answer: str) -> Pattern
    def extract_solution_approach(self, code: str) -> Pattern
```

**Files:**
- `src/pattern_extractor/ingestion/parsers/cooking.py`
- `src/pattern_extractor/ingestion/parsers/python.py`

---

## Phase 3: Knowledge Graph (Days 7-9)

### 3.1 Graph Storage

```python
class KnowledgeGraph:
    """Store and query patterns as a graph"""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_pattern(self, pattern: Pattern):
        """Add pattern to graph"""
        pass

    def find_related(self, pattern_id: str) -> List[Pattern]:
        """Find related patterns"""
        pass

    def find_path(self, from_id: str, to_id: str) -> List[Pattern]:
        """Find path between patterns"""
        pass

    def find_clusters(self) -> List[List[Pattern]]:
        """Find pattern clusters"""
        pass
```

**Files:**
- `src/knowledge_graph/graph.py`

---

### 3.2 Pattern Matcher

```python
class PatternMatcher:
    """Find similar patterns across domains"""

    def find_similar(self, pattern: Pattern, threshold: float = 0.7) -> List[Pattern]:
        """Find patterns similar to given pattern"""
        pass

    def cross_domain_match(self, domain1: str, domain2: str) -> List[Tuple[Pattern, Pattern]]:
        """Find matching patterns between two domains"""
        pass

    def calculate_similarity(self, p1: Pattern, p2: Pattern) -> float:
        """Calculate similarity score between patterns"""
        pass
```

**Similarity Metrics:**
- Problem structure similarity
- Solution approach similarity
- Step sequence alignment
- Tag overlap

**Files:**
- `src/knowledge_graph/matcher.py`

---

### 3.3 Universal Pattern Detector

```python
class UniversalPatternDetector:
    """Identify patterns that appear across multiple domains"""

    def find_universal(self, min_domains: int = 3) -> List[Pattern]:
        """Find patterns present in >= N domains"""
        pass

    def abstract_pattern(self, patterns: List[Pattern]) -> Pattern:
        """Create abstract pattern from specific instances"""
        pass
```

**Files:**
- `src/knowledge_graph/universal.py`

---

## Phase 4: Frontend UI (Days 10-12)

### 4.1 Domain Explorer

```
/domain
├── Dropdown: Select domain
├── Stats: Pattern count, last updated
└── List: All patterns in domain
```

**Files:**
- `frontend/src/pages/DomainExplorer.jsx`

---

### 4.2 Pattern Browser

```
/pattern/:id
├── Pattern details (problem, solution, steps)
├── Related patterns
├── Cross-domain matches
└── Source attribution
```

**Files:**
- `frontend/src/pages/PatternDetail.jsx`

---

### 4.3 Relationship Visualizer

```
/visualize
├── Graph view (D3.js or Cytoscape.js)
├── Filter by domain, type, confidence
└── Interactive exploration
```

**Files:**
- `frontend/src/pages/Visualizer.jsx`

---

### 4.4 Cross-Domain View

```
/cross-domain
├── Side-by-side pattern comparison
├── Universal patterns list
└── Pattern cluster view
```

**Files:**
- `frontend/src/pages/CrossDomain.jsx`

---

## Phase 5: Add New Domains

### Domain 2: Cooking (Days 13-15)

**Target:** 100 recipes → extract substitution patterns

**Sources:**
- AllRecipes.com (scrapeable)
- Serious Eats (technique guides)

**Patterns to extract:**
- Ingredient substitutions
- Cooking technique variations
- Troubleshooting common issues

---

### Domain 3: Python (Days 16-18)

**Target:** 100 Stack Overflow questions → extract error patterns

**Sources:**
- Stack Exchange API
- Real Python tutorials

**Patterns to extract:**
- Error handling approaches
- Common debugging steps
- Code organization patterns

---

### Domain 4: DIY (Days 19-21)

**Target:** 50 how-to guides → extract procedural patterns

**Sources:**
- This Old House (transcripts if available)
- DIY Network

**Patterns to extract:**
- Diagnostic sequences
- Tool selection
- Safety procedures

---

## Phase 6: Polish & Analyze (Days 22-24)

### 6.1 Pattern Quality Review

- Remove duplicates
- Improve descriptions
- Add more examples
- Score confidence

### 6.2 Cross-Domain Analysis

- Run pattern matcher on all domains
- Identify universal patterns
- Create pattern clusters

### 6.3 Documentation

- API documentation
- Usage guide
- Domain addition guide

---

## Directory Structure

```
eeframe/
├── src/
│   ├── pattern_extractor/
│   │   ├── __init__.py
│   │   ├── models.py           # Pattern data models
│   │   ├── extractor.py        # Core extraction logic
│   │   ├── prompts.py          # LLM prompts
│   │   └── ingestion/
│   │       ├── scraper.py      # URL scraper
│   │       ├── pdf_parser.py   # PDF parser
│   │       └── parsers/
│   │           ├── cooking.py   # Recipe parser
│   │           ├── python.py    # Code Q&A parser
│   │           └── diy.py       # DIY guide parser
│   ├── knowledge_graph/
│   │   ├── __init__.py
│   │   ├── graph.py            # NetworkX wrapper
│   │   ├── matcher.py          # Pattern similarity
│   │   └── universal.py        # Cross-domain patterns
│   └── api.py                   # FastAPI endpoints
├── frontend/src/pages/
│   ├── DomainExplorer.jsx      # Browse domains
│   ├── PatternDetail.jsx       # Pattern details
│   ├── Visualizer.jsx          # Graph visualization
│   └── CrossDomain.jsx         # Cross-domain analysis
├── data/
│   ├── patterns/               # Pattern storage (JSON)
│   │   ├── omv.json
│   │   ├── cooking.json
│   │   ├── python.json
│   │   └── diy.json
│   └── graph/                  # Graph snapshots
└── scripts/
    ├── ingest_cooking.py       # Ingest cooking sources
    ├── ingest_python.py        # Ingest Python sources
    └── analyze_cross_domain.py # Cross-domain analysis
```

---

## API Endpoints

```python
# Pattern management
GET    /api/patterns              # List all patterns
GET    /api/patterns/:id          # Get pattern details
POST   /api/patterns              # Create pattern
PUT    /api/patterns/:id          # Update pattern

# Domain management
GET    /api/domains               # List all domains
GET    /api/domains/:name         # Get domain patterns
POST   /api/domains               # Create domain

# Ingestion
POST   /api/ingest/url            # Ingest from URL
POST   /api/ingest/pdf            # Ingest from PDF
POST   /api/ingest/text           # Ingest raw text

# Knowledge graph
GET    /api/graph/related/:id     # Get related patterns
GET    /api/graph/path            # Find path between patterns
GET    /api/graph/universal       # Get universal patterns
POST   /api/graph/match           # Find similar patterns

# Cross-domain
GET    /api/cross-domain/:d1/:d2  # Compare two domains
GET    /api/cross-domain/clusters # Get pattern clusters
```

---

## Success Criteria

### Minimum Viable Product (Day 12)
- [x] OMV patterns (24) - DONE
- [ ] Core pattern extraction engine
- [ ] URL scraper working
- [ ] Knowledge graph with NetworkX
- [ ] Basic UI to browse patterns
- [ ] 1 new domain added (Cooking)

### Full System (Day 24)
- [ ] 4+ domains with 100+ patterns each
- [ ] Cross-domain pattern matching
- [ ] Universal patterns identified
- [ ] Interactive visualization
- [ ] Export/import functionality
- [ ] Documentation complete

---

## Next Steps (Right Now)

1. **Create pattern models** - Define the Pattern schema
2. **Build basic extractor** - LLM-based extraction from text
3. **Test on OMV patterns** - Verify it works with existing data
4. **Add URL scraper** - Start ingesting cooking recipes
5. **Build graph storage** - NetworkX-based pattern graph

---

## Questions to Resolve

1. **Pattern Schema:** Is the proposed Pattern model sufficient for all domains?
2. **LLM Access:** Using GLM-4.7 - need to confirm API access patterns
3. **Storage:** JSON files vs database - start with JSON, migrate if needed
4. **Visualization:** D3.js vs Cytoscape.js - which is easier for our use case?
5. **Scraping:** Respect robots.txt, rate limits - need to be good citizens
