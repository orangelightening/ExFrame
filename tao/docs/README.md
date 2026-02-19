# Tao (道) - Knowledge Cartography Subsystem

> "The Tao that can be told is not the eternal Tao"
> Yet we map the questions and answers anyway.

Tao is ExFrame's knowledge cartography subsystem. It stores, analyzes, and visualizes learning journeys through query/response history, providing insights into exploration patterns, concept evolution, and knowledge depth.

## Overview

**Tao (道)** represents the dialectical transformation between:
- **Yin (陰)**: Questions - The seeking, the unknown, receptive energy
- **Yang (陽)**: Answers - The knowing, the revealed, active energy

Just as Yin and Yang transform into each other in an endless cycle, questions lead to answers which evoke new questions. Tao maps this eternal cycle of learning.

## Architecture

Tao is a **standalone subsystem** separate from ExFrame's core:

```
ExFrame (Answers questions)
    ↓ saves Q/R pairs
Tao (Maps knowledge)
    ↓ provides analysis
User (Views insights)
```

### Components

```
tao/
├── storage/        # Compressed Q/R history storage
├── analysis/       # Analysis modules (sessions, chains, concepts, depth)
├── api/            # FastAPI router for REST endpoints
├── cli/            # Command-line tools
├── frontend/       # Web UI (HTML/JS)
└── docs/           # Documentation
```

## Features

### Phase 2a (Current)

**Storage:**
- Compressed query/response history (gzip)
- Timezone-aware timestamps
- Metadata storage (source, confidence, patterns used)

**Analysis Tools:**
1. **Sessions** - Group queries into exploration sessions based on time gaps
2. **Chains** - Trace query chains before/after specific entries
3. **Relations** - Find related queries using temporal, pattern, or keyword similarity
4. **Concepts** - Extract and track concept keywords across history
5. **Depth** - Identify deep explorations vs shallow touches

**Interfaces:**
- REST API at `/api/tao/*`
- Web UI at `/tao`
- CLI tools: `python -m tao.cli.*`
- Python API: `from tao.analysis import sessions`

## Usage

### Web Interface

Navigate to `http://localhost:5001/tao` to access the interactive analysis interface.

Features:
- **Sessions Tab**: View exploration sessions with queries grouped by time
- **Concepts Tab**: See most frequent concepts and when they appeared
- **Depth Tab**: Identify deep explorations (multiple related queries)
- **Domain Selector**: Switch between domains to compare learning patterns

### REST API

#### Get Sessions

```bash
GET /api/tao/sessions/{domain}?gap_minutes=30&min_queries=2
```

Returns exploration sessions grouped by time gaps.

#### Get Top Concepts

```bash
GET /api/tao/concepts/{domain}?top_n=10&min_freq=2
```

Returns most frequent concepts extracted from queries/responses.

#### Get Deep Explorations

```bash
GET /api/tao/depth/{domain}?min_depth=2&time_gap=10
```

Returns explorations with multiple related queries in short timespan.

#### Get Query Chain

```bash
GET /api/tao/chains/{domain}/{entry_id}?before=3&after=3
```

Returns queries before and after a specific entry.

#### Find Related Queries

```bash
GET /api/tao/related/{domain}/{entry_id}?strategy=all&limit=5
```

Finds related queries using temporal, pattern, or keyword strategies.

### CLI Tools

#### View History

```bash
python -m tao.cli.view_history peter
python -m tao.cli.view_history peter --limit 10 --source brave-search
```

#### Show Sessions

```bash
python -m tao.cli.show_sessions peter
python -m tao.cli.show_sessions peter --gap 30 --min-queries 2
```

#### Trace Query Chain

```bash
python -m tao.cli.trace_chain peter --entry 5
python -m tao.cli.trace_chain peter --entry 5 --before 3 --after 5
```

### Python API

```python
from tao.storage import load_history
from tao.analysis import sessions, concepts, depth

# Load domain history
history = load_history('peter')

# Find exploration sessions
session_list = sessions.find_sessions(history, gap_minutes=30)
for session in session_list:
    stats = sessions.analyze_session(session)
    print(f"Session: {stats['query_count']} queries, {stats['duration_minutes']} minutes")

# Get top concepts
top_concepts = concepts.get_top_concepts(history, top_n=10, min_freq=2)
for concept_stats in top_concepts:
    print(f"{concept_stats['concept']}: {concept_stats['frequency']} times")

# Find deep explorations
explorations = depth.find_deep_explorations(history, min_depth=3, time_gap=10)
for exploration in explorations:
    print(f"Deep dive: {exploration['query_count']} queries on {exploration['top_concepts'][:3]}")
```

## Integration with ExFrame

Tao automatically stores all query/response pairs processed by ExFrame:

1. **Automatic Storage**: When ExFrame processes a query, it calls `kcart.save_query_response()` to save the Q/R pair
2. **No Interference**: Tao storage is non-blocking and doesn't affect query processing
3. **Domain-Specific**: Each domain has its own query history file
4. **Configurable**: Query history can be enabled/disabled per domain via `domain.json`

### Domain Configuration

In `domain.json`:

```json
{
  "query_history": {
    "enabled": true,
    "compression": "gzip",
    "context_window": 20,
    "max_entries": null,
    "store_evoked_questions": true
  }
}
```

## Data Storage

Query history is stored in: `domains/{domain}/query_history.json.gz`

### Entry Format

```json
{
  "id": 1,
  "timestamp": "2025-02-15T10:30:00-08:00",
  "query": "What are patterns?",
  "response": "Patterns are reusable knowledge units...",
  "metadata": {
    "source": "pattern_match",
    "confidence": 0.95,
    "patterns_used": ["core_concept_patterns"],
    "persona": "kage"
  },
  "evoked_questions": [
    "How do patterns differ from templates?",
    "When should I create a new pattern?"
  ]
}
```

## Future Phases

### Phase 2b: Advanced Analytics
- Pattern effectiveness scoring
- Knowledge gap detection
- Confidence trend analysis

### Phase 3: Evocation Tracking
- Store and analyze evoked questions
- Question chain visualization
- Curiosity pattern detection

### Phase 4: Semantic Similarity
- Embedding-based query similarity
- Topic clustering
- Concept drift detection

### Phase 5: Learning Path Discovery
- Automatic learning path extraction
- Prerequisites detection
- Knowledge dependency graphs

### Phase 6: Interactive Graph Visualization
- D3.js/Cytoscape integration
- Interactive concept graphs
- Time-based animation

## Philosophy

Tao embodies the cyclical nature of learning:

1. **Questions arise** (Yin) from the unknown
2. **Answers emerge** (Yang) to illuminate
3. **New questions form** from understanding
4. **The cycle continues** eternally

By mapping this cycle, Tao reveals:
- **Exploration patterns**: How we navigate the unknown
- **Concept evolution**: How understanding deepens
- **Knowledge gaps**: Where curiosity leads next
- **Learning depth**: Surface touches vs deep dives

Just as water finds its way by following the Tao, learning flows through the path of questions and answers.

## Contributing

When adding new analysis features to Tao:

1. **Analysis Module**: Add core logic to `tao/analysis/`
2. **API Endpoint**: Add REST endpoint to `tao/api/router.py`
3. **CLI Tool**: Add CLI wrapper to `tao/cli/`
4. **Frontend**: Add UI component to `tao/frontend/tao.html` and `tao.js`
5. **Documentation**: Update this README and `API.md`

## References

- [Knowledge Cartography Plan](../../KNOWLEDGE_CARTOGRAPHY.md)
- [API Documentation](./API.md)
- [Architecture Documentation](./ARCHITECTURE.md)
