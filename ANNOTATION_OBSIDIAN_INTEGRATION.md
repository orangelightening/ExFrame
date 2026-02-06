# Annotation System + Obsidian Integration

**Date:** 2026-02-05
**Purpose:** Integrate Obsidian YAML frontmatter with the annotation system

---

## Overview

The annotation system now supports **dual-layer annotations**:

1. **YAML Frontmatter** (Obsidian-compatible) - Document-level metadata
2. **HTML Comments** - Inline section-specific annotations

This provides the best of both worlds: structured metadata at the document level and contextual annotations at the section level.

## Philosophy: Optional Enhancement

**YAML frontmatter is completely optional:**

- ✅ Use frontmatter when document-level metadata adds value
- ✅ Skip frontmatter for simple, straightforward documentation
- ✅ No requirement to add frontmatter to existing files
- ✅ Add gradually as documents are updated, not in batch
- ✅ Missing frontmatter is not a problem

**When frontmatter helps:**
- Tracking document lifecycle (superseded, deprecated, historical)
- Linking related documents in Obsidian graph view
- Managing known contradictions at document level
- Using Obsidian features (tags, aliases, dataview)

**When to skip frontmatter:**
- Current, simple documentation
- Files that rarely change
- Temporary documentation
- When HTML comments are sufficient

---

## YAML Frontmatter Integration

### Basic Structure

```markdown
---
title: ExFrame Architecture Overview
version: 2.0
updated: 2026-02-05
status: current
tags: [architecture, phase1, personas]
---

# ExFrame Architecture Overview

Document content here...
```

### Annotation-Specific Fields

#### 1. **status** - Document lifecycle state

```markdown
---
status: current        # Active, up-to-date documentation
---
```

**Valid values:**
- `current` - Active and accurate
- `draft` - Work in progress
- `superseded` - Replaced by another document
- `deprecated` - No longer recommended
- `historical` - Kept for reference only

#### 2. **superseded_by** - Replacement document

```markdown
---
status: superseded
superseded_by: docs/architecture/phase1-overview.md
superseded_date: 2026-02-04
---
```

Use when a document has been replaced by a newer version.

#### 3. **replaces** - Previous document

```markdown
---
status: current
replaces: docs/architecture/old-overview.md
---
```

Track what this document replaced.

#### 4. **historical_note** - Brief context

```markdown
---
historical_note: "Renamed from EEFrame to ExFrame in January 2026"
---
```

Short document-level historical context.

#### 5. **contradictions** - Known issues

```markdown
---
contradictions:
  - type: terminology
    description: "Uses 'specialist' and 'persona' interchangeably"
    tracking: "issue-123"
  - type: version
    description: "References v1.6.0 features no longer available"
    tracking: "phase1-migration"
---
```

Track known contradictions at document level.

#### 6. **aliases** - Alternative names

```markdown
---
aliases: [EEFrame, OMV Copilot]
---
```

Obsidian-compatible aliases for search and linking.

#### 7. **related** - Connected documents

```markdown
---
related:
  - CHANGELOG.md
  - docs/reference/domain-config.md
  - PLUGIN_ARCHITECTURE.md
---
```

Link to related documentation.

---

## Complete YAML Frontmatter Examples

### Example 1: Current Documentation

```markdown
---
title: ExFrame Architecture Overview
version: 2.0
updated: 2026-02-05
status: current
tags: [architecture, phase1, personas]
related:
  - CHANGELOG.md
  - docs/reference/domain-config.md
---

# ExFrame Architecture Overview

The current Phase 1 architecture uses 3 personas...
```

### Example 2: Superseded Documentation

```markdown
---
title: Domain Types Guide
version: 1.0
updated: 2026-01-29
status: superseded
superseded_by: README.md#persona-system
superseded_date: 2026-02-04
historical_note: "Domain types 1-5 replaced by 3 personas in Phase 1"
tags: [legacy, domain-types, v1.6.0]
aliases: [Domain Types, Type System]
---

# Domain Types Guide

<!-- SUPERSEDED: This document describes the v1.6.0 domain type system
Replaced by the Phase 1 persona system. See README.md for current approach.
-->

This guide describes domain types 1-5 (legacy system)...
```

### Example 3: Document with Known Contradictions

```markdown
---
title: Plugin Architecture Guide
version: 1.5
updated: 2026-01-15
status: current
contradictions:
  - type: terminology
    description: "Mixes 'specialist' and 'persona' terminology"
    resolution: "Phase 3 refactor will unify terminology"
    tracking: "phase3-plugin-refactor"
tags: [plugins, architecture]
---

# Plugin Architecture Guide

<!-- CONTRADICTION: Plugin vs Persona terminology
The codebase uses "specialist plugins" (legacy) while docs describe
"personas" (current). Both refer to query behavior. Unifying in Phase 3.
-->

ExFrame uses a plugin-based architecture...
```

### Example 4: Historical Reference

```markdown
---
title: EEFrame Original Design
version: 0.1
updated: 2025-12-01
status: historical
historical_note: "Original architecture before plugin system"
tags: [historical, archive, pre-v1.0]
aliases: [EEFrame, Original Design]
---

# EEFrame Original Design

<!-- HISTORICAL NOTE: Pre-Plugin Architecture (December 2025)
This was the original design before the plugin system was introduced
in v1.0. Kept for historical reference and understanding design evolution.
-->

Original domain-specific architecture...
```

---

## Dual-Layer Annotation Strategy

### Document-Level (YAML Frontmatter)

Use for:
- ✅ Document status and lifecycle
- ✅ Superseded/replacement tracking
- ✅ Document-wide tags and categorization
- ✅ Related document linking
- ✅ Overall historical context
- ✅ Known contradictions affecting whole document

### Section-Level (HTML Comments)

Use for:
- ✅ Specific historical notes for sections
- ✅ Inline superseded system explanations
- ✅ Localized contradictions
- ✅ Clarifications for specific concepts
- ✅ Section-specific TODOs

### Example Combined Usage

```markdown
---
title: Domain Configuration Reference
version: 2.0
updated: 2026-02-05
status: current
superseded_by: null
replaces: docs/guides/domain-types.md
tags: [configuration, reference, phase1]
historical_note: "Updated for Phase 1 persona system"
---

# Domain Configuration Reference

<!-- HISTORICAL NOTE: Schema Evolution
Version 1.x used domain_type field (1-5).
Version 2.x uses persona field (poet/librarian/researcher).
Old configs still work (backward compatibility).
-->

## Configuration Schema

### Persona Field

<!-- SUPERSEDED: domain_type field (v1.6.0)
The domain_type: "1-5" field is deprecated.
Use persona: "poet/librarian/researcher" instead.
See CHANGELOG.md for migration guide.
-->

```json
{
  "persona": "librarian",
  "library_base_path": "/app/project"
}
```

## Advanced Configuration

<!-- TODO: Add performance tuning section
Document embedding generation settings and cache optimization.
Target: Phase 2 documentation update.
-->
```

---

## Integration with Semantic Search

### YAML Parsing

The semantic search automatically includes YAML frontmatter in embeddings:

1. **Full document is embedded** - includes YAML metadata
2. **Structured fields are searchable** - tags, status, etc.
3. **Relationships are discoverable** - superseded_by, related links

### Query Examples

**Finding superseded docs:**
```
User: "What documentation has been replaced?"
→ Semantic search finds status: superseded
→ Returns list with superseded_by links
```

**Finding historical context:**
```
User: "Why was the project renamed?"
→ Semantic search finds historical_note: "Renamed from EEFrame..."
→ Returns complete context
```

**Finding related documentation:**
```
User: "What docs relate to plugin architecture?"
→ Semantic search finds related: [...] fields
→ Returns connected documentation
```

---

## LLM Enricher Integration

The contradiction detector automatically uses YAML frontmatter:

```python
# Extracts document metadata
metadata = extract_yaml_frontmatter(document)

# Checks status
if metadata.get('status') == 'superseded':
    # Don't flag as contradiction, it's known
    pass

# Reads known contradictions
contradictions = metadata.get('contradictions', [])
# Filters out documented contradictions from detection
```

### Example Detection Logic

```markdown
---
contradictions:
  - type: terminology
    description: "Mixes specialist/persona terms"
    tracking: "phase3-refactor"
---

Document uses both "specialist" and "persona" terms...
```

**Detection behavior:**
- ✅ Reads contradictions field
- ✅ Ignores documented terminology mix
- ✅ Only flags NEW contradictions
- ✅ Includes tracking reference in context

---

## Obsidian-Specific Features

### 1. **Graph View**

Using `related` and `superseded_by` fields creates navigable document graph in Obsidian:

```markdown
---
related:
  - "[[CHANGELOG]]"
  - "[[docs/architecture/overview]]"
superseded_by: "[[README#persona-system]]"
---
```

### 2. **Tag Navigation**

```markdown
---
tags: [phase1, personas, architecture]
---
```

Obsidian automatically creates tag index for fast navigation.

### 3. **Aliases**

```markdown
---
aliases: [EEFrame, ExFrame, Expertise Framework]
---
```

All aliases searchable and linkable in Obsidian.

### 4. **Dataview Queries**

Can query documents programmatically in Obsidian:

```dataview
TABLE status, updated, superseded_by
FROM ""
WHERE status = "superseded"
SORT updated DESC
```

Returns all superseded documents with replacement links.

---

## Migration Guide

### Adding YAML Frontmatter to Existing Docs

**Step 1: Identify document status**

```bash
# Find docs with superseded annotations
grep -r "SUPERSEDED" docs/

# Find docs with historical notes
grep -r "HISTORICAL NOTE" docs/
```

**Step 2: Add appropriate frontmatter**

For superseded docs:
```markdown
---
status: superseded
superseded_by: path/to/new-doc.md
superseded_date: YYYY-MM-DD
---
```

For current docs:
```markdown
---
status: current
updated: YYYY-MM-DD
tags: [relevant, tags]
---
```

**Step 3: Keep HTML comments for inline context**

Don't remove HTML comments - they provide section-specific context that frontmatter can't capture.

### Conversion Script

```bash
#!/bin/bash
# add_frontmatter.sh - Add YAML frontmatter to markdown files

for file in docs/**/*.md; do
    if ! head -1 "$file" | grep -q "^---$"; then
        # File doesn't have frontmatter
        echo "Adding frontmatter to $file"

        # Create temp file with frontmatter
        cat > temp_frontmatter.md <<EOF
---
title: $(basename "$file" .md)
updated: $(date -r "$file" +%Y-%m-%d)
status: current
---

EOF
        # Prepend to original file
        cat temp_frontmatter.md "$file" > temp_combined.md
        mv temp_combined.md "$file"
        rm temp_frontmatter.md
    fi
done
```

---

## Best Practices

### 1. **Frontmatter for Structure, Comments for Context**

```markdown
---
status: superseded
superseded_by: new-doc.md
---

# Old System

<!-- SUPERSEDED: Domain Types (v1.6.0)
The 5 domain types were complex and overlapping.
Replaced by 3 personas for simplicity.
Key improvement: 98% code reduction, clearer mental model.
-->
```

### 2. **Use Tags Consistently**

```markdown
---
tags: [phase1, personas, current]
---
```

Standard tags:
- `phase1`, `phase2`, `phase3` - Development phases
- `current`, `superseded`, `historical` - Status
- `architecture`, `configuration`, `guide` - Document type
- `legacy`, `deprecated` - Lifecycle
- `v1.6.0`, `v2.0.0` - Version associations

### 3. **Link Related Documents**

```markdown
---
related:
  - CHANGELOG.md
  - README.md
  - docs/architecture/overview.md
---
```

### 4. **Document Contradictions Explicitly**

```markdown
---
contradictions:
  - type: terminology
    description: "Clear explanation"
    resolution: "How it will be fixed"
    tracking: "issue-123 or phase3-refactor"
---
```

### 5. **Keep Frontmatter Minimal (or Skip It)**

Only include fields that add value. Most docs don't need frontmatter at all.

**No frontmatter (perfectly fine):**
```markdown
# My Documentation

Content here...
```

**Minimal when useful:**
```markdown
---
status: current
updated: 2026-02-05
---
```

**More detail when needed (superseded docs):**
```markdown
---
status: superseded
superseded_by: new-doc.md
superseded_date: 2026-02-04
historical_note: "Brief reason for replacement"
---
```

---

## Field Reference

### Core Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `title` | string | Document title | `"ExFrame Architecture"` |
| `version` | string | Doc version | `"2.0"` |
| `updated` | date | Last update | `2026-02-05` |
| `status` | enum | Lifecycle state | `current` \| `superseded` \| `deprecated` \| `historical` |
| `tags` | array | Categories | `[phase1, architecture]` |

### Lifecycle Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `superseded_by` | string | Replacement doc | `"docs/new-overview.md"` |
| `superseded_date` | date | When replaced | `2026-02-04` |
| `replaces` | string | Previous doc | `"docs/old-overview.md"` |
| `deprecated_date` | date | When deprecated | `2026-01-15` |

### Context Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `historical_note` | string | Brief context | `"Renamed from EEFrame"` |
| `contradictions` | array | Known issues | `[{type, description, tracking}]` |
| `related` | array | Connected docs | `["CHANGELOG.md", "README.md"]` |
| `aliases` | array | Alt names | `["EEFrame", "ExFrame"]` |

---

## Example Documents

### README.md with Frontmatter

```markdown
---
title: ExFrame - Expertise Framework
version: 2.0
updated: 2026-02-05
status: current
tags: [overview, getting-started, phase1]
aliases: [ExFrame, Expertise Framework, EEFrame]
historical_note: "Renamed from EEFrame to ExFrame in January 2026"
related:
  - CHANGELOG.md
  - INSTALL.md
  - PLUGIN_ARCHITECTURE.md
---

# ExFrame - Expertise Framework

<!-- HISTORICAL NOTE: Project Naming (January 2026)
Original: "OMV Copilot" → "EEFrame" → standardized to "ExFrame"
Directory structure:
- eeframe/ - Kept for git history and Docker volume compatibility
- generic_framework/ - Internal implementation detail (not user-facing)
- All user-facing content - Uses "ExFrame" consistently
See CHANGELOG.md for complete naming history.
-->

**Domain-Agnostic AI-Powered Knowledge Management System**
```

### CHANGELOG.md with Frontmatter

```markdown
---
title: ExFrame Changelog
version: current
updated: 2026-02-05
status: current
tags: [changelog, releases, history]
related:
  - RELEASE_NOTES.md
  - README.md
---

# Changelog

## [Phase 1] - 2026-02-04

<!--
SUPERSEDED: Domain Types 1-5 (v1.6.0 - January 2026)
Replaced by 3 Personas in Phase 1 (February 2026).
...
-->
```

---

## Summary

### Dual-Layer System

✅ **YAML Frontmatter** - Document-level structured metadata
✅ **HTML Comments** - Section-level contextual annotations

### Integration Points

✅ **Semantic Search** - Frontmatter included in embeddings
✅ **Contradiction Detector** - Reads frontmatter metadata
✅ **Obsidian** - Full compatibility with graph, tags, aliases
✅ **Git** - Version controlled, history tracked

### Benefits

✅ **Structured** - Machine-readable document metadata
✅ **Discoverable** - Semantic search finds all metadata
✅ **Navigable** - Obsidian graph view of relationships
✅ **Trackable** - Git history of all changes
✅ **Flexible** - Document-level + inline annotations
✅ **Compatible** - Works in Obsidian and standard markdown

---

**Next Steps:**
1. Add frontmatter to key documentation files
2. Update llm_enricher.py to parse YAML frontmatter
3. Test semantic search with frontmatter queries
4. Document frontmatter conventions in annotation.md

---

**Status:** Ready for implementation 🚀
