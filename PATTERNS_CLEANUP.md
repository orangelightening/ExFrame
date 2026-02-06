# ExFrame Patterns Cleanup - Domain Types Removal

**Date**: 2026-02-05
**Issue**: Users kept seeing outdated "5 domain types" information despite documentation updates

---

## Root Cause

The problem was **NOT in the documentation files** - those were all updated correctly.

The problem was in **patterns.json** - the LLM-generated patterns from previous queries contained the outdated domain types information embedded in their solution text.

---

## What Was Happening

1. User queries the librarian about ExFrame
2. System searches **local patterns first** (pattern override enabled)
3. Finds patterns like "What is ExFrame?" that contain OLD information about Types 1-5
4. Returns that outdated information from the patterns
5. Even though the actual documentation files were updated, the patterns took precedence

---

## The Problematic Patterns

Found **8 patterns** with domain type references:

1. `exframe_c504f97c` - What is ExFrame and how do I get started?
2. `exframe_a360083f` - What is exframe
3. `exframe_6ea39a77` - What is ExFrame and how do I get started?
4. `exframe_f065a4e6` - What is ExFrame and how do I get started?
5. `exframe_43bde74b` - Are there any contradictions in how the plugin system is described vs implemented?
6. `exframe_879f8371` - What is ExFrame and how do I get started?
7. `exframe_a9e4906b` - What is exframe?
8. `exframe_424517e9` - Describe the current version of exframe

All of these contained text like:
- "Type 1: Creative Generator - Poems, stories (high temp 0.7-0.9)"
- "Type 2: Knowledge Retrieval - How-to guides, FAQs"
- "Domain Type System with 5 pre-configured archetypes"
- etc.

---

## Solution

### 1. Backed Up patterns.json
```bash
patterns.json.backup-20260205-180215
```

### 2. Removed Outdated Patterns

Filtered out all 8 patterns containing domain type references:
- **Before**: 17 patterns
- **After**: 9 patterns (clean)

### 3. Removed Document Embeddings

Deleted `doc_embeddings.json` to force regeneration from updated documentation.

### 4. Restarted Container

Loaded clean patterns and updated documentation.

---

## Why This Happened

**Pattern Override Logic** (Phase 1):
```python
if local_patterns_match:
    use local_patterns  # <-- Used old patterns with domain types
else:
    use persona.data_source
```

The system correctly followed the pattern override logic, but the **patterns themselves were stale**. This is a consequence of:

1. LLM-generated patterns being saved for reuse
2. Those patterns embedding documentation state at generation time
3. Pattern override making patterns take precedence over documents
4. No automatic invalidation of patterns when docs change

---

## Long-Term Solutions

### Option 1: Pattern Versioning
Add a `doc_version` field to patterns:
```json
{
  "id": "exframe_123",
  "doc_version": "2.0",  // Phase 1
  "solution": "..."
}
```

Invalidate patterns when doc version changes.

### Option 2: Pattern TTL
Add expiration to LLM-generated patterns:
```json
{
  "id": "exframe_123",
  "expires_at": "2026-03-05",
  "solution": "..."
}
```

### Option 3: Source Tracking
Tag patterns by source document:
```json
{
  "id": "exframe_123",
  "sources": ["README.md", "CHANGELOG.md"],
  "source_hashes": ["abc123", "def456"],
  "solution": "..."
}
```

Invalidate when source files change.

### Option 4: Manual Curation
Keep patterns.json curated - only manually-written patterns, not LLM-generated.

---

## Current State

✅ **All domain type references removed** from:
- Documentation files (README, CHANGELOG, RELEASE_NOTES, architecture docs)
- patterns.json (8 outdated patterns removed)
- doc_embeddings.json (regenerated from clean docs)

✅ **System now consistently returns Phase 1 information**:
- 3 Personas (poet/librarian/researcher)
- Pattern override behavior
- No more confusing domain types references

---

## Files Modified

- `universes/MINE/domains/exframe/patterns.json` - Removed 8 outdated patterns (17 → 9)
- `universes/MINE/domains/exframe/patterns.json.backup-20260205-180215` - Backup created
- `universes/MINE/domains/exframe/doc_embeddings.json` - Removed (will regenerate)

---

## Testing

Next query to the librarian about ExFrame should:
1. Not find old domain types in local patterns (removed)
2. Fall back to document search (librarian persona)
3. Find updated documentation with Phase 1 personas
4. Return correct, current information

If patterns get regenerated with new queries, they will now pull from the updated documentation files.

---

**Result**: System documentation and patterns are now aligned. No more outdated domain types information.
