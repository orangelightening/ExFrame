# EEFrame Plugin Pipeline

## Overview

EEFrame processes user queries through a configurable **plugin pipeline** with four stages:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EEFRAME QUERY PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   USER QUERY                    ┌───────────────────────────────────┐       │
│      "What is tool             │                                   │       │
│       confidence collapse?"     │    1. ROUTER STAGE                │       │
│             │                   │    ┌─────────────────────────┐    │       │
│             ▼                   │    │ ConfidenceBasedRouter   │    │       │
│       ┌─────────┐               │    │ MultiSpecialistRouter  │    │       │
│       │  User   │               │    │ ParallelRouter         │    │       │
│       └────┬────┘               │    │ SequentialRouter       │    │       │
│            │                    │    │ HierarchyRouter        │    │       │
│            │                    │    └─────────────────────────┘    │       │
│            │                    │    Config: threshold = 0.30      │       │
│            └────────────────────>│                                   │       │
│                                 └───────────────────────────────────┘       │
│                                                │                          │
│                                                ▼                          │
│                                 ┌───────────────────────────────────┐       │
│                                 │    2. SPECIALIST STAGE             │       │
│                                 │    ┌─────────────────────────┐    │       │
│                                 │    │ FailureDetectionPlugin │    │       │
│                                 │    │ MonitoringPlugin       │    │       │
│                                 │    │ CookingSpecialist      │    │       │
│                                 │    │ BinarySymmetryExpert   │    │       │
│                                 │    │ ...                    │    │       │
│                                 │    └─────────────────────────┘    │       │
│                                 │    Returns: patterns + confidence │       │
│                                 └───────────────────────────────────┘       │
│                                                │                          │
│                                                ▼                          │
│                                 ┌───────────────────────────────────┐       │
│                                 │    3. ENRICHER STAGE              │       │
│                                 │    (Optional - Multiple)          │       │
│                                 │                                   │       │
│                                 │    ┌─────────────────────────┐   │       │
│                                 │    │ LLMFallbackEnricher    │   │       │
│                                 │    │ Fills gaps with LLM    │   │       │
│                                 │    └─────────────────────────┘   │       │
│                                 │                                   │       │
│                                 │    ┌─────────────────────────┐   │       │
│                                 │    │ QualityScoreEnricher   │   │       │
│                                 │    │ Adds quality metrics   │   │       │
│                                 │    └─────────────────────────┘   │       │
│                                 │                                   │       │
│                                 │    ┌─────────────────────────┐   │       │
│                                 │    │ UsageStatsEnricher     │   │       │
│                                 │    │ Tracks pattern usage   │   │       │
│                                 │    └─────────────────────────┘   │       │
│                                 │                                   │       │
│                                 │    ┌─────────────────────────┐   │       │
│                                 │    │ CodeGeneratorEnricher  │   │       │
│                                 │    │ Generates code         │   │       │
│                                 │    └─────────────────────────┘   │       │
│                                 │                                   │       │
│                                 └───────────────────────────────────┘       │
│                                                │                          │
│                                                ▼                          │
│                                 ┌───────────────────────────────────┐       │
│                                 │    4. FORMATTER STAGE              │       │
│                                 │    ┌─────────────────────────┐    │       │
│                                 │    │ MarkdownFormatter      │    │       │
│                                 │    │ JSONFormatter          │    │       │
│                                 │    │ HTMLFormatter          │    │       │
│                                 │    │ SlackFormatter         │    │       │
│                                 │    │ CompactFormatter       │    │       │
│                                 │    └─────────────────────────┘    │       │
│                                 │    Config: max_examples = 3       │       │
│                                 └───────────────────────────────────┘       │
│                                                │                          │
│                                                ▼                          │
│   FORMATTED RESPONSE          ┌───────────────────────────────────┐       │
│      "**Tool Confidence       │                                   │       │
│       Collapse**              │    Response to User               │       │
│       Problem: Small..."      │                                   │       │
│             │                 └───────────────────────────────────┘       │
│             ▼                                                                       │
│       ┌─────────┐                                                                      │
│       │  User   │                                                                      │
│       └─────────┘                                                                      │
│                                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages Explained

### Stage 1: Router

**Purpose**: Determines which specialist(s) should handle the query.

**Available Routers**:

| Router | Description | Use Case |
|--------|-------------|----------|
| `ConfidenceBasedRouter` | Routes to specialist with highest confidence | General purpose |
| `MultiSpecialistRouter` | Sends to multiple specialists | Complex queries |
| `ParallelRouter` | All specialists process simultaneously | Speed prioritized |
| `SequentialRouter` | Specialists process in order | Dependent reasoning |
| `HierarchyRouter` | Hierarchical specialist selection | Organized domains |

**Key Configuration**:
- `threshold`: Minimum confidence (0.0-1.0) to accept pattern matches
- Lower threshold = more matches, less precision
- Higher threshold = fewer matches, more precision

```
Example:
threshold: 0.30  →  Accept patterns with ≥30% confidence
threshold: 0.70  →  Only accept patterns with ≥70% confidence
```

---

### Stage 2: Specialist

**Purpose**: Domain experts that search patterns and match against queries.

**Specialist Types**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPECIALIST PLUGINS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  llm_consciousness/                                             │
│  ├── FailureDetectionPlugin   →  Detects LLM failure modes     │
│  └── MonitoringPlugin         →  Monitoring & architecture     │
│                                                                 │
│  cooking/                                                      │
│  └── CookingSpecialist        →  Recipes & techniques          │
│                                                                 │
│  binary_symmetry/                                               │
│  ├── BitManipulationExpert    →  Binary operations             │
│  ├── PatternMatcher           →  Bit patterns                  │
│  └── SymmetryAnalyzer         →  Symmetry detection            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**What Specialists Do**:
1. Receive query from router
2. Search pattern database for matches
3. Calculate confidence scores for each match
4. Return ranked patterns to pipeline

---

### Stage 3: Enrichers

**Purpose**: Post-process results to add value, fill gaps, or enhance presentation.

**Enricher Types**:

| Enricher | Function | Mode |
|----------|----------|------|
| `LLMFallbackEnricher` | Fills gaps with LLM when no patterns match | `fallback` |
| `QualityScoreEnricher` | Adds quality metrics to results | `enhance` |
| `UsageStatsEnricher` | Tracks pattern access frequency | `enhance` |
| `CodeGeneratorEnricher` | Generates code examples from patterns | `enhance` |
| `CitationEnricher` | Adds source citations | `enhance` |
| `SummaryEnricher` | Creates summaries of multiple patterns | `enhance` |

**Enricher Modes**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENRICHER MODES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ENHANCE MODE                                    │
│  ┌──────────────┐         ┌──────────────┐                        │
│  │   Patterns   │────────>│   Enricher   │──> Enhanced Results  │
│  └──────────────┘         └──────────────┘                        │
│  Adds extra info without changing original response               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FALLBACK MODE                                   │
│  ┌──────────────┐         ┌──────────────┐                        │
│  │   Patterns   │  Empty? │   Enricher   │──> LLM Generated      │
│  └──────────────┘────────>│   (LLM)      │    Response          │
│                                  │            │                     │
│                                  └────────────┘                     │
│  Only triggers if no patterns found or low confidence              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  REPLACE MODE                                   │
│  ┌──────────────┐         ┌──────────────┐                        │
│  │   Patterns   │────────>│   Enricher   │──> Replaced Response  │
│  └──────────────┘         └──────────────┘                        │
│  Replaces original response entirely                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Configuration**:
- `enabled`: true/false
- `mode`: "enhance", "fallback", or "replace"
- `min_confidence`: Trigger threshold (0.0-1.0)
- `model`: LLM model to use (e.g., "gpt-4o-mini")

---

### Stage 4: Formatter

**Purpose**: Formats the final output for the user.

**Available Formatters**:

| Formatter | Output Style | Use Case |
|-----------|--------------|----------|
| `MarkdownFormatter` | Styled Markdown | Web UI, documentation |
| `JSONFormatter` | Structured JSON | APIs, integrations |
| `HTMLFormatter` | Rendered HTML | Web pages |
| `SlackFormatter` | Slack-friendly | Slack bots |
| `CompactFormatter` | Minimal text | Quick answers |

**Key Configuration**:
- `max_examples_per_pattern`: How many examples to show (default: 3)

---

## Configuration Example

### Domain: llm_consciousness

```json
{
  "domain_id": "llm_consciousness",
  "router": {
    "module": "plugins.routers.confidence_router",
    "class": "ConfidenceBasedRouter",
    "config": {
      "threshold": 0.30
    }
  },
  "formatter": {
    "module": "plugins.formatters.markdown_formatter",
    "class": "MarkdownFormatter",
    "config": {
      "max_examples_per_pattern": 3
    }
  },
  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMFallbackEnricher",
      "enabled": true,
      "config": {
        "mode": "fallback",
        "min_confidence": 0.40,
        "model": "gpt-4o-mini",
        "max_patterns": 3
      }
    },
    {
      "module": "plugins.enrichers.usage_stats_enricher",
      "class": "QualityScoreEnricher",
      "enabled": true,
      "config": {}
    }
  ],
  "plugins": [
    {
      "plugin_id": "failure_detection",
      "module": "plugins.llm_consciousness.failure_detection",
      "class": "FailureDetectionPlugin",
      "enabled": true,
      "config": {
        "keywords": ["hallucination", "tool loop", "loop", "perseveration"],
        "categories": ["failure_mode", "detection"],
        "threshold": 0.3
      }
    },
    {
      "plugin_id": "monitoring",
      "module": "plugins.llm_consciousness.monitoring",
      "class": "MonitoringPlugin",
      "enabled": true,
      "config": {
        "keywords": ["monitor", "detect", "alert", "architecture"],
        "categories": ["monitoring", "architecture", "solution"],
        "threshold": 0.3
      }
    }
  ]
}
```

---

## Pipeline Behavior by Use Case

### High-Precision Domain (Medical, Legal)

```
Configuration:
- Router threshold: 0.70 (high confidence required)
- Enrichers: None or minimal (no LLM fallback)
- Formatter: Compact (just facts)

Result: Fewer but highly accurate matches, no AI-generated content
```

### Creative Domain (Ideation, Brainstorming)

```
Configuration:
- Router threshold: 0.20 (allow lower confidence)
- Enrichers: Multiple with enhance mode
- Formatter: Markdown with rich examples

Result: More suggestions, enhanced with related concepts
```

### Real-Time Domain (Chatbots, Live Support)

```
Configuration:
- Router: ParallelRouter (speed)
- Enrichers: Minimal (fast response)
- Formatter: Compact or Slack

Result: Fast, concise answers
```

---

## Current State

**As of v1.2.0**, pipeline configuration requires:

1. Manual editing of `data/patterns/{domain_id}/domain.json`
2. Container restart for changes to take effect

**Planned Feature**: Web UI for pipeline configuration (currently in development).

---

## File Locations

```
eeframe/
├── generic_framework/
│   ├── plugins/
│   │   ├── routers/           # Router implementations
│   │   ├── formatters/        # Formatter implementations
│   │   └── enrichers/         # Enricher implementations
│   └── api/
│       └── app.py             # Pipeline orchestration
│
└── data/
    └── patterns/
        └── {domain_id}/
            └── domain.json     # Pipeline configuration
```

---

## Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     PIPELINE QUICK REFERENCE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   STAGE          COMPONENT         PURPOSE                      │
│   ──────         ─────────         ───────                      │
│                                                                 │
│   1. Router      ConfidenceBased   Route to right specialist    │
│                  MultiSpecialist   Query multiple experts       │
│                  Parallel          Fast parallel processing     │
│                                                                 │
│   2. Specialist  DomainPlugin      Match patterns              │
│                  ExpertPlugin      Apply domain expertise        │
│                                                                 │
│   3. Enrichers   LLMFallback       Fill gaps with AI            │
│                  QualityScore      Add quality metrics          │
│                  UsageStats        Track usage                  │
│                  CodeGenerator     Create code examples         │
│                                                                 │
│   4. Formatter   Markdown          Web UI display               │
│                  JSON              API responses                │
│                  HTML              Web pages                    │
│                  Slack             Chat integration             │
│                  Compact           Brief answers                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
