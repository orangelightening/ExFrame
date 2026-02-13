# Analysis: Patterns as Domain Log — Response to Thursday Night Thoughts

**Date:** 2026-02-13

## The Proposal

Replace `domain_log.md` (sequential markdown file) with auto-generated patterns for every query/response cycle. Use the existing pattern search infrastructure (semantic search, embeddings, 10ms retrieval) instead of loading raw markdown tail.

## Why This Is Architecturally Sound

The domain_log was always a workaround. Here's what it actually does:

1. Appends query + response as markdown
2. On `**` questions, loads the last 5000 chars as raw text into the LLM context
3. The LLM then does a brute-force search through that text to find relevant entries

That's the LLM doing a job that the pattern search system already does better, faster, and with less token cost.

**What patterns already have that domain_log doesn't:**

| Capability | domain_log.md | Patterns |
|-----------|---------------|----------|
| Storage | Append-only markdown | Structured JSON |
| Search | Load last N chars (dumb truncation) | Semantic search (~10ms) |
| Retrieval | LLM scans raw text | Cosine similarity, ranked results |
| Curation | Edit markdown manually | Pattern editor UI, delete, archive |
| Scaling | Degrades as file grows (truncation loses old entries) | Scales with embeddings |
| Human readable | Yes (markdown) | Yes (JSON with clear fields) |
| Archival | None | Can archive by range (nn to nw) |

## The 10ms Argument

This is the killer advantage. Right now, a `**` question in Peter's domain:

1. Loads 5000 chars of markdown (~few ms)
2. Sends it all to the cloud LLM as context (~8-100 seconds)
3. LLM scans through the text to find the answer

With patterns:

1. Semantic search across all entries (~10ms)
2. Returns top N most relevant entries
3. Send only those entries to the LLM (much less context, faster response)

The LLM gets a focused, relevant subset instead of a raw dump of the last N characters. Less tokens in = faster response + cheaper + more accurate.

## How It Would Work

### Every query/response becomes a pattern:

```json
{
  "id": "peter_20260213_204800",
  "name": "Journal: 2026-02-13 20:48:00",
  "pattern_type": "journal_entry",
  "problem": "Haircut tomorrow at 10. Luigis",
  "solution": "[2026-02-13 20:48:00] Haircut tomorrow at 10. Luigis",
  "tags": ["haircut", "luigi", "appointment"],
  "created_at": "2026-02-13T20:48:00",
  "origin": "journal",
  "llm_generated": false
}
```

- **`problem`** = the original query (what the user said)
- **`solution`** = the timestamped response (what got echoed back)
- **`created_at`** = sequential timestamp for ordering
- **`pattern_type`** = "journal_entry" to distinguish from curated knowledge patterns

### For `**` questions:

1. Strip the `**` prefix
2. Semantic search across journal_entry patterns
3. Return top 10 most relevant entries
4. Send those to the LLM: "Based on these journal entries, answer the question: ..."

### For regular journal entries:

1. Timestamp and echo (as now — fast, local model)
2. Auto-generate a pattern from the query/response
3. Generate embedding for semantic search
4. Store in patterns.json

### For curation:

- **Archive all:** Move all patterns to archive file, start fresh
- **Archive range:** Move patterns nn-nw to archive
- **Delete individual:** Already works via pattern editor UI
- **Edit:** Already works via pattern editor UI

## Concerns and Mitigations

### 1. Pattern volume
Journal domains could accumulate thousands of patterns. Current pattern search uses in-memory cosine similarity which is fast for hundreds but needs testing at thousands.

**Mitigation:** The embedding model (all-MiniLM-L6-v2) handles 10K+ embeddings in <100ms. Not a problem until you hit 50K+ entries, which would take years of daily journaling.

### 2. Pattern schema fit
The current schema (`problem`/`solution`) is designed for knowledge patterns, not journal entries. Using `problem` for a journal entry like "pick up milk" feels semantically wrong.

**Mitigation:** Two options:
- (a) Just use it — the fields are just labels, the search works on embeddings not field names
- (b) Add a `query`/`response` alias that maps to `problem`/`solution` for journal types

Option (a) is simpler and works. The pattern editor already shows these fields.

### 3. The "recent entries" query
"What have I been up to recently?" needs chronological ordering, not semantic relevance.

**Mitigation:** For recency queries, sort by `created_at` descending and return the last N entries. The `**` handler can detect recency keywords ("recently", "today", "this week") and switch to chronological mode.

### 4. Embedding generation overhead
Every journal entry needs an embedding generated. On CPU this takes ~50ms per entry with all-MiniLM-L6-v2.

**Mitigation:** 50ms is invisible to the user — the entry is already echoed back before the embedding is generated. Embedding generation can be async/background.

## What Code Already Exists

This is the strongest part of the proposal — almost everything is already built:

- **Pattern CRUD:** `app.py` has full create/read/update/delete endpoints
- **Pattern search:** `query_processor.py` `_search_domain_patterns()` — semantic search with cosine similarity
- **Embedding generation:** `document_embeddings.py` — DocumentVectorStore with all-MiniLM-L6-v2
- **Pattern editor UI:** Frontend already has pattern view, edit, delete
- **Pattern override in persona:** `persona.respond()` already handles `override_patterns`
- **Archive/clear endpoints:** `app.py` has pattern management endpoints

What needs to be written:
1. Auto-pattern generation after each query/response (~20 lines in query_processor)
2. Switch `**` question handler from "load domain_log" to "search patterns" (~15 lines)
3. A `pattern_type: "journal_entry"` filter so journal entries don't pollute knowledge queries

## Recommendation

**Do it.** This maps naturally onto the system's existing architecture. The pattern system was designed for exactly this kind of structured, searchable, human-readable storage. The domain_log was a detour.

### Implementation order:
1. Auto-generate journal patterns on each query/response (keep domain_log as backup initially)
2. Switch `**` handler to search patterns instead of loading domain_log
3. Test with real journal entries
4. Once validated, remove domain_log dependency
5. Add archive-by-range support

### What you keep:
- The domain_log.md can remain as a human-readable audit trail (append-only, never read by the system)
- Or remove it entirely once patterns are proven

### What you gain:
- 10ms semantic search instead of 5000-char raw text dump
- Better answers (relevant entries, not just recent ones)
- Scalable (embeddings handle thousands of entries)
- Curateable (pattern editor, archive, delete)
- Less LLM token usage (focused context, not raw dump)
- Works with local models (less context = smaller models can handle it)

## The Local Model Angle

This is where it gets interesting. With patterns:
- The journal persona (Ollama, local, fast) handles the echo/timestamp
- Auto-pattern generation happens server-side (no LLM needed, just formatting + embedding)
- The `**` question persona could use a smarter model (cloud) but with minimal context (just the top 5 relevant patterns instead of 5000 chars of raw log)

The combination of local model + pattern search could bring the full cycle (journal entry + semantic storage) to under 2 seconds total.
