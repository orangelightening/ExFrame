# Knowledge Cartography Analysis Scripts

This directory contains scripts for analyzing query history stored by ExFrame's Knowledge Cartography system.

## Overview

All scripts work with the compressed query history files stored at:
```
universes/MINE/domains/{domain}/query_history.json.gz
```

**Common patterns:**
- All scripts take domain name as first argument
- Most support `--json` for machine-readable output
- Most support `--help` or `-h` for usage information
- Results sorted by relevance or frequency

---

## Storage & Viewing

### view_history.py
**Purpose:** View raw query/response history

**Basic usage:**
```bash
python3 scripts/view_history.py peter
python3 scripts/view_history.py peter --limit 10
python3 scripts/view_history.py peter --stats-only
```

**Advanced filtering:**
```bash
# Filter by date range
python3 scripts/view_history.py peter --from 2026-02-01 --to 2026-02-15

# Filter by source
python3 scripts/view_history.py peter --source "pattern_library"

# Filter by confidence
python3 scripts/view_history.py peter --min-confidence 0.8

# Export to JSON
python3 scripts/view_history.py peter --json > export.json
```

**When to use:**
- View raw history entries
- Export data for external analysis
- Check storage statistics
- Debug query/response issues

---

## Session Analysis

### show_sessions.py
**Purpose:** Group queries into exploration sessions based on time gaps

**Basic usage:**
```bash
# Default: 30 minute gap between sessions
python3 scripts/show_sessions.py peter

# Custom gap threshold
python3 scripts/show_sessions.py peter --gap 15

# Only sessions with 3+ queries
python3 scripts/show_sessions.py peter --min-queries 3

# Just the statistics
python3 scripts/show_sessions.py peter --stats-only
```

**What it shows:**
- Session boundaries (when you started/stopped exploring)
- Queries per session
- Session duration
- Sources used in each session
- Average confidence per session

**When to use:**
- Understand your exploration patterns
- Find periods of intense activity
- See how long exploration sessions typically last
- Identify usage patterns over time

**Example output:**
```
Session 1
─────────────────────────────────────
Time:       2026-02-15 09:23:15 → 2026-02-15 09:45:32
Duration:   22.3 minutes
Queries:    8
Confidence: 0.742

Sources:
  pattern_library      5
  web_search          2
  embedding_search     1

Queries:
  1. What are embeddings?
  2. How do I create embeddings in Python?
  ...
```

---

## Chain Analysis

### trace_chain.py
**Purpose:** Trace query chains before and after a specific entry

**Basic usage:**
```bash
# Show 3 before and 3 after entry #5
python3 scripts/trace_chain.py peter --entry 5

# Custom chain length
python3 scripts/trace_chain.py peter --entry 5 --before 5 --after 10

# Tighter time gap (default: 10 minutes)
python3 scripts/trace_chain.py peter --entry 5 --gap 5
```

**What it shows:**
- Queries leading up to the target
- The target query itself
- Queries following from the target
- Time gaps between queries
- Chain duration

**When to use:**
- Understand how you arrived at a question
- See what followed from a specific query
- Trace the evolution of an exploration
- Understand question sequences

**Example output:**
```
▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
BEFORE (3 queries leading up to this)
▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
  ↓ [3] 2026-02-15 14:10:23
     Query: What are patterns?
     ...

████████████████████████████
TARGET ENTRY
████████████████████████████
  ➤ [5] 2026-02-15 14:15:45
     Query: How do I add a new pattern?
     ...

▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
AFTER (3 queries following from this)
▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
  ↑ [6] 2026-02-15 14:18:12
     Query: What pattern types are available?
     ...
```

---

## Relationship Discovery

### find_related.py
**Purpose:** Find queries related to a specific entry using multiple strategies

**Basic usage:**
```bash
# Find related using all strategies
python3 scripts/find_related.py peter --entry 5

# Use only temporal strategy (nearby in time)
python3 scripts/find_related.py peter --entry 5 --strategy temporal

# Use only pattern strategy (shared domain patterns)
python3 scripts/find_related.py peter --entry 5 --strategy pattern

# Use only keyword strategy (shared keywords)
python3 scripts/find_related.py peter --entry 5 --strategy keyword
```

**Advanced options:**
```bash
# More results per strategy
python3 scripts/find_related.py peter --entry 5 --limit 10

# Wider time window (default: 60 minutes)
python3 scripts/find_related.py peter --entry 5 --time-window 120

# Require more shared keywords (default: 2)
python3 scripts/find_related.py peter --entry 5 --min-keywords 3
```

**Strategies explained:**
- **Temporal:** Queries close in time (within time window)
- **Pattern:** Queries using same domain patterns
- **Keyword:** Queries with overlapping keywords (Jaccard similarity)

**When to use:**
- Find similar questions you've asked
- Discover related explorations
- Connect queries across time
- Understand topic clustering

**Example output:**
```
RELATED BY TEMPORAL (5 results)
─────────────────────────────────────
1. [4] 2026-02-15 14:12:30
   Score:  0.892
   Reason: Within 3.2 minutes
   Query:  What are pattern templates?

RELATED BY PATTERN (3 results)
─────────────────────────────────────
1. [7] 2026-02-15 15:20:15
   Score:  0.667
   Reason: Shared patterns: template_pattern, example_pattern
   Query:  Show me template examples

RELATED BY KEYWORD (4 results)
─────────────────────────────────────
1. [9] 2026-02-15 16:45:22
   Score:  0.425
   Reason: 5 shared keywords: pattern, template, example, create, domain
   Query:  How do I create domain-specific patterns?
```

---

## Concept Analysis

### concept_timeline.py
**Purpose:** Extract and track concepts (keywords) across query history

**Basic usage:**
```bash
# Show top 10 most frequent concepts
python3 scripts/concept_timeline.py peter

# Show top 20
python3 scripts/concept_timeline.py peter --top 20

# Only concepts appearing 5+ times
python3 scripts/concept_timeline.py peter --min-freq 5
```

**Specific concept analysis:**
```bash
# Timeline for specific concept
python3 scripts/concept_timeline.py peter --concept "embedding"

# With co-occurring concepts
python3 scripts/concept_timeline.py peter --concept "embedding" --cooccurrence
```

**Date filtering:**
```bash
# Concepts from specific date range
python3 scripts/concept_timeline.py peter --date-from 2026-02-01 --date-to 2026-02-15
```

**What it shows:**
- Most frequent concepts
- When concepts first/last appeared
- Which entries contain each concept
- Co-occurring concepts (which concepts appear together)

**When to use:**
- Discover main topics in your history
- Track when you started exploring a topic
- Find related topics via co-occurrence
- Understand conceptual evolution

**Example output:**
```
Top Concepts: peter
─────────────────────────────────────
1. EMBEDDING
   Frequency:  12 times
   First seen: 2026-02-10 08:15:23
   Last seen:  2026-02-15 16:32:45
   Entries:    #3, #7, #11, #15, #22, #28...

2. PATTERN
   Frequency:  9 times
   First seen: 2026-02-11 10:22:11
   Last seen:  2026-02-15 14:55:32
   Entries:    #5, #8, #12, #19, #25...

Co-occurring Concepts: embedding
─────────────────────────────────────
1. vector               8 co-occurrences
2. semantic             6 co-occurrences
3. similarity           5 co-occurrences
4. search               4 co-occurrences
```

---

## Exploration Depth

### analyze_depth.py
**Purpose:** Measure how deeply topics were explored

**Basic usage:**
```bash
# Find deep explorations (2+ related queries)
python3 scripts/analyze_depth.py peter

# Only show very deep explorations (5+ queries)
python3 scripts/analyze_depth.py peter --min-depth 5

# Tighter time gap (default: 10 minutes)
python3 scripts/analyze_depth.py peter --time-gap 5
```

**Specific concept depth:**
```bash
# How deeply was "embedding" explored?
python3 scripts/analyze_depth.py peter --concept "embedding"
```

**Show everything:**
```bash
# Include shallow (single query) topics
python3 scripts/analyze_depth.py peter --show-shallow
```

**What it shows:**
- Deep explorations (sequences of related queries)
- Exploration depth (query count)
- Duration of exploration
- Dominant topics in each exploration
- Shallow vs deep exploration patterns

**When to use:**
- Identify topics you explored deeply
- Find focused exploration sessions
- Understand follow-up patterns
- Measure engagement with topics

**Example output:**
```
Exploration 1: EMBEDDING
─────────────────────────────────────
Depth:     8 queries
Duration:  35.2 minutes
Started:   2026-02-15 14:10:15
Ended:     2026-02-15 14:45:28

Top topics:
  embedding            8 times
  vector               6 times
  similarity           5 times
  search               4 times
  semantic             3 times

Queries in exploration:
  1. [12] What are embeddings?
  2. [13] How do embeddings work?
  3. [14] Can I create custom embeddings?
  4. [15] What's the difference between word and sentence embeddings?
  5. [16] How do I compare embeddings?
  ...
```

---

## Common Workflows

### Understanding a Topic's Evolution
```bash
# 1. Find when the concept appeared
python3 scripts/concept_timeline.py peter --concept "patterns"

# 2. Look at one of those entries in detail
python3 scripts/view_history.py peter --entry 15

# 3. Trace the chain around that entry
python3 scripts/trace_chain.py peter --entry 15

# 4. Find related queries
python3 scripts/find_related.py peter --entry 15

# 5. Measure exploration depth
python3 scripts/analyze_depth.py peter --concept "patterns"
```

### Analyzing a Session
```bash
# 1. Find sessions
python3 scripts/show_sessions.py peter

# 2. Look at a specific time range
python3 scripts/view_history.py peter --from "2026-02-15 14:00:00" --to "2026-02-15 15:00:00"

# 3. Find deep explorations in that period
python3 scripts/analyze_depth.py peter --min-depth 3
```

### Discovering Knowledge Gaps
```bash
# 1. Find low-confidence queries
python3 scripts/view_history.py peter | grep "Confidence: 0\.[0-4]"

# 2. What topics are they about?
python3 scripts/concept_timeline.py peter --top 30

# 3. Were you exploring deeply or just touching topics?
python3 scripts/analyze_depth.py peter
```

### Exporting for External Analysis
```bash
# Export full history as JSON
python3 scripts/view_history.py peter --json > history.json

# Export session analysis
python3 scripts/show_sessions.py peter --json > sessions.json

# Export concept data
python3 scripts/concept_timeline.py peter --json > concepts.json

# Export depth analysis
python3 scripts/analyze_depth.py peter --json > depth.json
```

---

## Technical Notes

### Append-Only Architecture
All analysis scripts compute relationships on-demand from timestamps. The stored history is never modified - only appended to. This means:

- **Storage layer:** Simple append-only compressed JSON
- **Analysis layer:** Derives relationships from timestamps
- **Benefits:** Analysis can evolve without data migration

### Performance
- Reading full history: ~100-200ms for 10k entries
- Session detection: ~50-100ms
- Concept extraction: ~200-500ms (depends on history size)
- All scripts suitable for interactive use

### Concept Extraction
Current implementation uses simple keyword extraction:
- Splits text into words
- Filters stop words and short words
- Case-insensitive matching

Future Phase 4 will add LLM-based semantic concept extraction.

---

## Getting Help

- **Script usage:** Run any script with `--help` or `-h`
- **General docs:** See [KNOWLEDGE_CARTOGRAPHY.md](../KNOWLEDGE_CARTOGRAPHY.md)
- **Design docs:** See [kcart.md](../kcart.md)
- **Issues:** Check [TODO.md](../TODO.md) or GitHub issues

---

**Last Updated:** 2026-02-15 (Phase 2a Complete)
