# ExFrame Development Plan

*Working context and daily notes*

## Current State (2026-02-10)
**System Version:** 1.6.1
**Status:** Production ready, container healthy

### Recent Completions
- **2026-02-10:** Web search fully functional
  - DuckDuckGo client-side search implemented
  - Source verification with clickable URLs
  - Multi-turn function calling with GLM-4.7
  - Full page content fetching (3000 chars/page)
  - Forced tool execution for researcher persona

- **2026-02-05:** Annotation system documentation
  - ANNOTATION_PHILOSOPHY.md
  - ANNOTATION_OBSIDIAN_INTEGRATION.md
  - Complete setup guide

- **2026-02-04:** Phase 1 persona system shipped
  - Type 4 domains with full plugin support
  - Researcher, Librarian, Poet personas
  - Document and web search strategies

### Active Projects
1. **Documentation Reorganization** ✅ COMPLETED
   - ✅ Created ARCHITECTURE.md (663 lines, 16K)
   - ✅ Created development-plan.md (4.1K)
   - ✅ Consolidated scattered docs
   - ✅ Eliminated docs/ directory
   - ✅ Archived 18 files to .archive/2026-02-10-doc-reorg/
   - ✅ Separated creative content to creative/
   - ✅ Moved design docs to design/
   - ✅ Updated README.md to version 1.6.1
   - ✅ Fixed librarian file access (56 documents accessible)

2. **Surveyor Feature** (planned)
   - Status: Design phase
   - See design/SURVEYOR_*.md (archived from planning phase)

3. **WiseMan Experiment** (exploration)
   - Status: Architectural research
   - See design/WISEMAN_*.md (in design/ directory)

### System Components
- **Generic Framework:** Plugin architecture for domain management
- **Frontend:** Web UI at http://localhost:3000
- **Backend:** Python/FastAPI in Docker container
- **LLM:** GLM-4.7 via Z.AI coding plan
- **Search:**
  - Library search: Semantic + pattern matching
  - Web search: DuckDuckGo with source verification

### Known Issues
None critical

### Technical Debt
- ✅ Documentation reorganized (44 → 20 files)
- ✅ Status files archived
- ✅ Creative content separated to creative/
- ✅ docs/ directory eliminated
- ✅ Core documentation: 4 files at root

### Next Tasks - ALL COMPLETED ✅
- [x] Complete ARCHITECTURE.md draft (663 lines, 16K)
- [x] Move files to root (development-plan.md, ARCHITECTURE.md)
- [x] Review both new docs for accuracy (Librarian approved)
- [x] Test with Librarian (access to 56 documents confirmed)
- [x] Test with Coder (ARCHITECTURE.md verified accurate)
- [x] Update README.md to 1.6.1
- [x] Execute archive (annotated and moved to .archive/)
- [x] Fix librarian file access (56 documents now accessible)
- [x] Regenerate document embeddings

### Documentation Reorganization - COMPLETE ✅

**Files Created:**
- `development-plan.md` (4.1K) ✅ AT ROOT
- `ARCHITECTURE.md` (663 lines, 16K) ✅ AT ROOT
- `DOCUMENT_INDEX_MAINTENANCE.md` ✅ AT ROOT
- `regenerate_embeddings.py` ✅ AT ROOT

**Files Archived (18 total):**
- Architecture: PLUGIN_ARCHITECTURE.md, statemachine-design.md, MULTITURN.md
- Web search: WEB_SEARCH_*.md, GLM_*.md, ZAI_*.md (6 files)
- Surveyor: SURVEYOR_*.md (4 files)
- Status: CURRENT_STATE.md, SYSTEM_RESTORED.md
- Meta: DOCUMENTATION_UPDATE.md, PATTERNS_CLEANUP.md

**Creative Content (5 files):**
- Moved to creative/essays/ (entice, university, firstsite, easy-recipe)
- Moved to creative/narratives/ (Notes from the Originator.md)

**Design Docs (2 files):**
- Moved to design/ (PLUGIN_REFACTOR_DESIGN.md, UNIVERSAL_LOGGING_DESIGN.md)

**Final State:**
- Core files: 4 (README, CHANGELOG, ARCHITECTURE, development-plan)
- Root markdown files: 20 (down from 44)
- docs/ directory: ELIMINATED
- Librarian access: 56 documents accessible
- All technical details verified accurate

### Reference Links
- **ARCHITECTURE.md** (when created) - System design
- **CHANGELOG.md** - Version history
- **INDEX.md** (after moving from docs/) - Documentation navigation
- **README.md** - User guide

### Archive Principle
**No deletion.** All files to be archived will be:
1. Annotated with a note at the top explaining why archived
2. Moved to `.archive/2026-02-10-doc-reorg/`
3. Preserved in git history

---

## Maintenance Tasks

### Document Index Synchronization

**Critical:** The librarian's document embeddings must stay synchronized with all `.md` files in the project directory.

**Current state:**
- Total markdown files: 43
- Document embeddings: `universes/MINE/domains/exframe/doc_embeddings.json` (493K)
- Last regenerated: 2026-02-10 21:07

**When to regenerate embeddings:**
- After adding new `.md` files to project root
- After removing `.md` files from project root
- After major edits to documentation files
- After archive phase (file structure changes)

**How to regenerate:**
```bash
# Run the regeneration script
docker exec eeframe-app python3 /app/project/regenerate_embeddings.py
```

**Maintenance schedule:**
- Manual: Run script after significant documentation changes
- TODO: Automated via git hook or cron job

**Files tracked by document index:**
All 43 `.md` files at project root, including:
- Core: README.md, CHANGELOG.md, ARCHITECTURE.md, development-plan.md
- Technical: MULTITURN.md, statemachine-design.md, etc.
- Web search: WEB_SEARCH_*.md, GLM_*.md, ZAI_*.md
- Annotation: ANNOTATION_*.md, annotation.md
- Plans/Status: doc-fix.md, doc-stat.md, etc.
