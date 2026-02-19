# Knowledge Cartography (Tao) - Quick Start

**Status:** Phase 2a Complete ✅ | Tao Subsystem Refactored (2026-02-15)

ExFrame now captures and stores all query/response pairs with compression, enabling conversational memory and dialectical knowledge mapping. The knowledge cartography functionality has been extracted into a standalone **Tao** subsystem with web UI, REST API, and CLI tools.

---

## What Is It?

**Knowledge Cartography** stores every interaction you have with ExFrame as compressed query/response pairs. This creates:
- **Conversational memory** - AI remembers your last 20 interactions
- **Complete history** - Never lose a query or answer
- **Dialectical data** - Questions (Yin) and Answers (Yang) ready for analysis
- **Personal knowledge map** - Your intellectual journey through ExFrame

---

## Quick Start

### 🌐 Web Interface (Recommended)

The easiest way to explore your knowledge map:

```
http://localhost:3000/tao
```

**Features:**
- **Sessions Tab**: View exploration sessions with expandable query details
- **Concepts Tab**: See most frequent keywords across your queries
- **Depth Tab**: Identify deep explorations (multiple related queries)
- **Interactive Modals**: View query chains and find related queries
- **Real-time Updates**: New queries appear immediately

### 📊 REST API

Access analysis programmatically:

```bash
# Get sessions
curl http://localhost:3000/api/tao/sessions/peter | jq

# Get top concepts
curl http://localhost:3000/api/tao/concepts/peter | jq

# Get query chain
curl http://localhost:3000/api/tao/chains/peter/5 | jq

# Find related queries
curl http://localhost:3000/api/tao/related/peter/5 | jq

# Get deep explorations
curl http://localhost:3000/api/tao/depth/peter | jq

# Get full history
curl http://localhost:3000/api/tao/history/peter | jq
```

See `tao/docs/API.md` for complete API documentation.

### 💻 Command Line Tools

**New module-based CLI** (recommended):
```bash
# View history
python -m tao.cli.view_history peter

# Show sessions
python -m tao.cli.show_sessions peter --gap 30

# Trace query chain
python -m tao.cli.trace_chain peter --entry 5
```

**Legacy scripts** (still work):
```bash
python3 scripts/view_history.py peter
python3 scripts/show_sessions.py peter
python3 scripts/trace_chain.py peter --entry 5
```

**Find related queries:**
```bash
# Find queries related to entry #5
python3 scripts/find_related.py peter --entry 5

# Use specific strategy (temporal, pattern, keyword)
python3 scripts/find_related.py peter --entry 5 --strategy temporal
```

**Track concepts over time:**
```bash
# Show top concepts
python3 scripts/concept_timeline.py peter --top 20

# Timeline for specific concept
python3 scripts/concept_timeline.py peter --concept "embedding"

# Show co-occurring concepts
python3 scripts/concept_timeline.py peter --concept "embedding" --cooccurrence
```

**Analyze exploration depth:**
```bash
# Find deep explorations (3+ related queries)
python3 scripts/analyze_depth.py peter --min-depth 3

# Depth analysis for specific concept
python3 scripts/analyze_depth.py peter --concept "patterns"
```

### Configure a Domain
Enable/disable features in `domain.json`:

```json
{
  "persona": "poet",
  "use_simple_echo": true,          // Journal mode (instant echo, no AI)
  "query_history": {
    "enabled": true,                 // Store all Q/R pairs
    "compression": "gzip",           // Compress with gzip
    "context_window": 20,            // Remember last 20 turns
    "max_entries": null,             // No limit (store everything)
    "store_evoked_questions": true   // Save Socratic follow-ups
  }
}
```

### Storage Location
- Files: `domains/{domain}/query_history.json.gz`
- Format: Compressed JSON (70-80% size reduction)
- Typical: ~400KB per 1,000 query/response pairs

---

## Documentation

### 📘 Core Documents

**[kcart.md](kcart.md)** - Complete design document
- Vision and philosophy (dialectical knowledge)
- Technical architecture
- All 6 phases of implementation
- Configuration options
- Use cases and benefits

**[VIEW_HISTORY.md](VIEW_HISTORY.md)** - CLI Viewer Guide
- How to view stored history
- Filtering and search options
- Examples and use cases

### 📗 Related Systems

**[BRAVE_SEARCH_INTEGRATION.md](BRAVE_SEARCH_INTEGRATION.md)** - Web Search Setup
- Brave Search API configuration
- Performance and costs
- Integration with researcher persona

**[The dialectical Knowledge Map.md](The%20dialectical%20Knowledge%20Map.md)** - Philosophical Foundation
- DeepSeek's Yin-Yang dialectical system
- Inspiration for ExFrame's approach
- Questions (Yin) ↔ Answers (Yang) dynamic

**[TODO.md](TODO.md)** - Project Status
- What's completed (Phase 1)
- What's next (analytics, visualization)
- Known issues and enhancements

### 📕 General ExFrame

**[ARCHITECTURE.md](ARCHITECTURE.md)** - System Architecture
**[QUICKSTART.md](QUICKSTART.md)** - Getting Started
**[README.md](README.md)** - Project Overview

---

## What's Working Now

### Phase 1: Storage & Context ✅

✅ **Compressed Storage**
- All queries and responses stored with gzip compression
- Metadata: source, confidence, patterns used, timestamps
- Timezone-aware (Vancouver/Pacific time)

✅ **Conversational Context**
- Last 20 Q/R pairs loaded automatically
- Passed to LLM for memory across interactions
- Works with all personas (poet, researcher, librarian)

✅ **CLI Viewer**
- View history with `scripts/view_history.py`
- Filter by date, source, confidence
- Summary statistics and entry details

✅ **Configuration**
- Per-domain settings in `domain.json`
- Opt-in simple echo for journal domains
- Configurable context window and limits

### Phase 2a: Relationship Analysis ✅

✅ **Session Detection**
- Group queries by time gaps (`show_sessions.py`)
- Identify exploration periods and breaks
- Analyze session duration, sources, confidence

✅ **Chain Tracing**
- Trace query chains before/after entries (`trace_chain.py`)
- Understand how questions evolved
- Show exploration flow through time

✅ **Related Query Finding**
- Find related queries by temporal, pattern, or keyword similarity (`find_related.py`)
- Multiple strategies: time proximity, shared patterns, keyword overlap
- Discover connections between queries

✅ **Concept Tracking**
- Extract and track concepts over time (`concept_timeline.py`)
- Show when concepts appeared and how often
- Identify co-occurring concepts

✅ **Exploration Depth**
- Measure how deeply topics were explored (`analyze_depth.py`)
- Identify deep dives vs shallow touches
- Track follow-up patterns

**Architecture:** Append-only storage with derived relationships
- All relationships computed on-demand from timestamps
- No modification of stored history
- Analysis can evolve without data migration

---

## Persona Modes

### Poet (Journal) - Simple Echo
**Example:** peter domain
```json
{
  "persona": "poet",
  "use_simple_echo": true
}
```
**Behavior:** Instant timestamp + echo (no AI, <2ms)
**Use case:** Fast journal entries

### Poet (Creative) - LLM
**Example:** poetry_domain
```json
{
  "persona": "poet"
}
```
**Behavior:** Uses LLM to generate creative content
**Use case:** Write poems, creative writing

### Researcher - Web Search
**Example:** psycho domain
```json
{
  "persona": "researcher",
  "enable_web_search": true
}
```
**Behavior:** Brave Search integration for current info
**Use case:** Research queries, current events

---

## What's Next

### Phase 2b: Advanced Analytics (Next)
- Pattern effectiveness scoring (which patterns work best?)
- Knowledge gap detection (what's missing from the domain?)
- Confidence trends over time (is quality improving?)
- Domain health metrics (usage patterns, answer quality)
- Query complexity analysis (simple vs complex questions)

### Phase 3: Evocation Tracking
- Store evoked questions from Socratic mode
- Question → Answer → Next Question chains
- Socratic tutoring improvements
- Measure teaching effectiveness

### Phase 4: Advanced Concept Analysis
- LLM-based concept extraction (vs simple keyword extraction)
- Build concept co-occurrence networks
- Cross-domain concept discovery
- Semantic similarity between queries

### Phase 5: Learning Paths
- Visualize progression from basic → advanced
- Detect prerequisites and dependencies
- Adaptive recommendations
- Personalized learning suggestions

### Phase 6: Knowledge Graph Visualization
- Interactive visual explorer
- "Tao Viewer" (dialectical visualization)
- Graph-based knowledge navigation
- Web-based UI for exploration

See [kcart.md](kcart.md) for complete roadmap.

---

## Common Tasks

### Clear History (Fresh Start)
```bash
rm domains/*/query_history.json.gz
```
Files will auto-recreate on next query.

### Check Storage Usage
```bash
ls -lh domains/*/query_history.json.gz
```

### Export History as JSON
```bash
python3 scripts/view_history.py peter --json > peter_history.json
```

### View Recent Activity
```bash
python3 scripts/view_history.py peter --limit 5
```

### Find Low-Confidence Queries
```bash
python3 scripts/view_history.py peter | grep "Confidence: 0\.[0-5]"
```

---

## Configuration Reference

### query_history Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable query history storage |
| `compression` | string | `"gzip"` | Compression method |
| `context_window` | number | `20` | Number of recent turns for context |
| `max_entries` | number | `null` | Maximum entries (null = unlimited) |
| `store_evoked_questions` | boolean | `true` | Save Socratic follow-ups |
| `extract_concepts` | boolean | `false` | Extract concepts (Phase 4) |

### Simple Echo Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `use_simple_echo` | boolean | `false` | Enable instant echo (no AI) |

**Note:** Simple echo only works with poet persona and non-** queries.

---

## Troubleshooting

### History Not Being Created
1. Check domain.json has `"query_history": {"enabled": true}`
2. Check container logs: `docker logs eeframe-app --tail 50`
3. Verify permissions on domains/{domain}/

### Wrong Timezone
- Set `APP_TIMEZONE=America/Vancouver` in `.env`
- Restart container: `docker-compose restart eeframe-app`
- Old entries keep old timezone, new entries use new timezone

### Viewer Shows Nothing
- Check file exists: `ls domains/{domain}/query_history.json.gz`
- Try: `python3 scripts/view_history.py {domain} --stats-only`
- Check if domain name is correct

### Simple Echo on Wrong Domain
- Set `"use_simple_echo": false` in domain.json (or remove the setting)
- Restart container
- Default is false (opt-in), so only enable for journal domains

---

## Philosophy

Knowledge Cartography embodies the **dialectical view of knowledge**:

**Yin (Questions)** - Dark, seeking, unknown
- What we ask reveals what we don't know
- Curiosity drives exploration
- Questions are the seeds of understanding

**Yang (Answers)** - Bright, providing, known
- What we find becomes crystallized knowledge
- Answers satisfy but also evoke new questions
- Knowledge is dynamic, not static

**Tao (Transformation)** - The flow between them
- Query processing transforms seeking into finding
- Each answer plants seeds for new questions
- The map of this transformation IS your learning journey

This is not just storage - it's **capturing the dialectical process of coming to know**.

See [The dialectical Knowledge Map.md](The%20dialectical%20Knowledge%20Map.md) for the philosophical foundation.

---

## Architecture

### Storage Layer
- **File:** `query_history.json.gz` per domain
- **Format:** Compressed JSON array
- **Compression:** gzip (70-80% reduction)
- **Typical size:** 400KB per 1,000 entries

### Context Layer
- **Module:** `generic_framework/core/knowledge_cartography.py`
- **Function:** Loads last N entries on each query
- **Integration:** query_processor.py → persona.py → LLM
- **Performance:** ~60ms to load 20 entries

### Query Flow
```
User Query
    ↓
query_processor.py (loads last 20 from history)
    ↓
persona.py (injects history into LLM context)
    ↓
LLM Response (with conversational memory)
    ↓
knowledge_cartography.py (saves Q/R pair)
    ↓
query_history.json.gz (compressed storage)
```

---

## Performance

### Storage
- 1,000 entries ≈ 400KB compressed
- 10,000 entries ≈ 4MB compressed
- 100,000 entries ≈ 26MB compressed
- 1,000,000 entries ≈ 260MB compressed

### Speed
- Save entry: <1ms (async)
- Load context (20 entries): ~60-80ms
- Decompress entire file (10k entries): ~100ms
- View history command: ~200ms

### Overhead
- Per query: +60-80ms for context loading
- Negligible compared to LLM call (500-8000ms)
- No impact on simple echo mode (<2ms total)

---

## Getting Help

- **Design questions:** See [kcart.md](kcart.md)
- **Usage questions:** See [VIEW_HISTORY.md](VIEW_HISTORY.md)
- **General ExFrame:** See [README.md](README.md)
- **Installation:** See [INSTALL.md](INSTALL.md)
- **Issues:** See [TODO.md](TODO.md) or GitHub issues

---

**Last Updated:** 2026-02-15 (Phase 1 Complete)
