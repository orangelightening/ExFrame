# Document Index Maintenance

**Date:** 2026-02-10  
**Status:** ✅ SYNCHRONIZED

## Overview

The librarian persona uses a **document embeddings index** to semantically search all `.md` files in the project directory. This index must be kept synchronized with the actual files.

## Current State

- **Total files indexed:** 43 markdown files
- **Index location:** `universes/MINE/domains/exframe/doc_embeddings.json`
- **Index size:** 493 KB
- **Last updated:** 2026-02-10 21:07

## How to Regenerate

When files are added/removed/modified:

```bash
docker exec eeframe-app python3 /app/project/regenerate_embeddings.py
```

## What Gets Indexed

All 43 `.md` files at project root:

**Core Documentation:**
- README.md
- CHANGELOG.md
- ARCHITECTURE.md
- development-plan.md
- INSTALL.md

**Architecture & Design:**
- MULTITURN.md
- statemachine-design.md
- PLUGIN_ARCHITECTURE.md

**Web Search Implementation:**
- WEB_SEARCH_COMPLETE.md
- WEB_SEARCH_WORKING.md
- WEB_SEARCH_STATUS.md
- GLM_WEB_SEARCH_FINAL.md
- ZAI_WEB_SEARCH_ARCHITECTURE.md
- ZAI_CREDIT_ISSUE.md

**Annotation System:**
- ANNOTATION_PHILOSOPHY.md
- ANNOTATION_SYSTEM_SETUP.md
- ANNOTATION_OBSIDIAN_INTEGRATION.md
- annotation.md

**Plans & Status:**
- doc-fix.md
- doc-stat.md
- CURRENT_STATE.md
- development-plan.md

**Creative/Other:**
- entice.md
- university.md
- firstsite.md
- easy-recipe.md
- claude.md
- aged.md
- etc.

## Maintenance Schedule

**After these operations, ALWAYS regenerate embeddings:**

1. ✅ Adding new `.md` files to project root
2. ✅ Removing `.md` files from project root
3. ✅ Major documentation updates
4. ✅ After archive phase (file structure changes)

## Technical Details

**Embedding model:** `all-MiniLM-L6-v2` (sentence-transformers)  
**Vector size:** 384 dimensions  
**Search method:** Cosine similarity  
**Cache location:** `universes/MINE/domains/exframe/doc_embeddings.json`

## Scripts

- `regenerate_embeddings.py` - Regenerates document embeddings for all .md files
- Located at project root
- Run inside container: `docker exec eeframe-app python3 /app/project/regenerate_embeddings.py`

## Archive Note

When Phase 6 (archive) is completed, the document index will need to be regenerated again because:
- Old files will be moved to `.archive/`
- File structure will change
- Some .md files will be in different locations

**Post-archive steps:**
1. Complete archive phase
2. Run `regenerate_embeddings.py`
3. Verify librarian can still find documents

---

**End of Document Index Maintenance Guide**
