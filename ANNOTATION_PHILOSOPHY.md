# Annotation System Philosophy

**Date:** 2026-02-05
**Status:** Guiding Principles

---

## Core Philosophy

> **Annotations are auxiliary, not mandatory**

The annotation system is designed to enhance understanding when needed, not to create requirements or slow down documentation work.

---

## Key Principles

### 1. Optional Enhancement
- Annotations add value when they provide context that isn't obvious
- Missing annotations are **not a problem**
- Most documentation doesn't need annotations

### 2. Not Sticky
- Don't let annotation requirements block or slow documentation updates
- Add annotations when they help, skip them when they don't
- No enforcement, no mandatory fields

### 3. Gradual Adoption
- Add annotations as you update docs naturally
- Don't batch-add annotations to all files
- Let the system evolve organically

### 4. Value-Driven
- Annotate when: historical context prevents confusion, contradictions need acknowledgment, superseded systems need explanation
- Skip when: content is self-explanatory, documentation is straightforward, context is obvious

---

## What This Means in Practice

### ✅ Good Use of Annotations

**Historical context that prevents confusion:**
```markdown
<!-- HISTORICAL NOTE: EEFrame → ExFrame (January 2026)
Directory kept as eeframe/ for Docker volume compatibility
-->
```

**Known contradictions during migration:**
```markdown
<!-- CONTRADICTION: Plugin vs Persona terminology
Will be unified in Phase 3 refactor
-->
```

**Superseded systems:**
```markdown
<!-- SUPERSEDED: Domain Types 1-5 (v1.6.0)
Replaced by 3 personas in Phase 1
-->
```

### ✅ Good: No Annotations Needed

**Current, clear documentation:**
```markdown
## Installation

1. Install Docker
2. Run `docker-compose up`
3. Open http://localhost:8000
```
*No annotation needed - this is straightforward and current*

**Self-explanatory configuration:**
```json
{
  "persona": "librarian",
  "library_base_path": "/app/project"
}
```
*No annotation needed - the structure is clear*

---

## YAML Frontmatter: Also Optional

Same philosophy applies to Obsidian YAML frontmatter:

**Most docs don't need it:**
```markdown
# My Document

Content here...
```

**Use it when it adds value:**
```markdown
---
status: superseded
superseded_by: new-doc.md
---

# Old Document

This document has been replaced...
```

---

## When to Use Each Layer

### YAML Frontmatter (Optional)
- Document lifecycle tracking (superseded, deprecated)
- Obsidian graph relationships
- Document-wide metadata

### HTML Comments (Optional)
- Section-specific historical notes
- Inline clarifications
- Known contradictions

### Neither (Default)
- Current, straightforward documentation
- Self-explanatory content
- Temporary documentation

---

## Summary

**Default:** No annotations
**When helpful:** Add them
**Missing annotations:** Not a problem
**Philosophy:** Auxiliary information, not requirements

**Don't worry about missing annotations.** The semantic search and LLM enricher work fine without them. Annotations are just there to help when they help.

---

**End of Philosophy Document**
