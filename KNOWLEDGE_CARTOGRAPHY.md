# Knowledge Cartography - Quick Start

**Status:** Phase 1 Complete ✅ (as of 2026-02-15)

ExFrame now captures and stores all query/response pairs with compression, enabling conversational memory and dialectical knowledge mapping.

---

## What Is It?

**Knowledge Cartography** stores every interaction you have with ExFrame as compressed query/response pairs. This creates:
- **Conversational memory** - AI remembers your last 20 interactions
- **Complete history** - Never lose a query or answer
- **Dialectical data** - Questions (Yin) and Answers (Yang) ready for analysis
- **Personal knowledge map** - Your intellectual journey through ExFrame

---

## Quick Start

### View Your History
```bash
# See all queries in a domain
python3 scripts/view_history.py peter

# Last 10 entries only
python3 scripts/view_history.py peter --limit 10

# Just statistics
python3 scripts/view_history.py peter --stats-only
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
- Files: `universes/MINE/domains/{domain}/query_history.json.gz`
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

## What's Working Now (Phase 1)

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

## What's Next (Phases 2-6)

### Phase 2: Analytics (Next)
- Pattern effectiveness scoring
- Knowledge gap detection
- Confidence trends over time
- Domain health metrics

### Phase 3: Evocation Tracking
- Question → Answer → Next Question chains
- Socratic tutoring improvements
- Exploration depth analysis

### Phase 4: Concept Extraction
- Mine concepts from Q/R pairs
- Build concept co-occurrence networks
- Cross-domain concept discovery

### Phase 5: Learning Paths
- Visualize progression from basic → advanced
- Detect prerequisites and dependencies
- Adaptive recommendations

### Phase 6: Knowledge Graph
- Interactive visual explorer
- "Tao Viewer" (dialectical visualization)
- Graph-based knowledge navigation

See [kcart.md](kcart.md) for complete roadmap.

---

## Common Tasks

### Clear History (Fresh Start)
```bash
rm universes/MINE/domains/*/query_history.json.gz
```
Files will auto-recreate on next query.

### Check Storage Usage
```bash
ls -lh universes/MINE/domains/*/query_history.json.gz
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
3. Verify permissions on universes/MINE/domains/{domain}/

### Wrong Timezone
- Set `APP_TIMEZONE=America/Vancouver` in `.env`
- Restart container: `docker-compose restart eeframe-app`
- Old entries keep old timezone, new entries use new timezone

### Viewer Shows Nothing
- Check file exists: `ls universes/MINE/domains/{domain}/query_history.json.gz`
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
