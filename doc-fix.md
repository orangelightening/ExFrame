# Documentation Cleanup Plan - Conservative Approach

**Date:** 2026-02-10
**Status:** READY FOR IMPLEMENTATION
**Philosophy:** Minimal documentation - only what's essential
**Approach:** Create new files first, review, then archive
**Archive Principle:** NO DELETION - Annotate files and move to .archive/

---

## Target Structure

```
/
├── README.md              # Entry point for all users
├── CHANGELOG.md           # Version history
├── ARCHITECTURE.md        # Current system design (NEW)
├── development-plan.md    # Working context, daily notes (NEW)
├── INDEX.md               # Navigation index (moved from docs/)
├── new-docs/              # Draft area for new files (TEMPORARY)
└── ...                    # Existing files stay until review complete
```

**Core files: 4** (all at root level)
**INDEX.md:** Navigation index (at root, different from README)
**docs/ directory:** ELIMINATED - all content consolidated into the 4 core files
**No files deleted** until new files are reviewed and approved

---

## ⚠️ CRITICAL: Case Sensitivity & File Conflicts

**PROBLEM:** Multiple architecture files exist, causing confusion:

| File | Size | Status | Action |
|------|------|--------|--------|
| `ARCHITECTURE.md` | 16K | **NEW - Current** | KEEP ✅ |
| `PLUGIN_ARCHITECTURE.md` | 41K | Old - superseded | Archive 📦 |
| `ZAI_WEB_SEARCH_ARCHITECTURE.md` | 15K | Old - consolidated | Archive 📦 |
| `statemachine-design.md` | 12K | Old - consolidated | Archive 📦 |

**IMPORTANT:**
- New file is **ALL CAPS**: `ARCHITECTURE.md`
- Old files to be archived have similar names
- New ARCHITECTURE.md has warning header explaining it's the current doc
- Archive phase will remove confusion by moving old files

---

## Implementation Strategy

### Phase 1: Setup Draft Area (Safe, no deletions)

```bash
# Create temporary directory for drafting new docs
mkdir -p new-docs

# Git tag for safety
git tag pre-doc-reorg-2026-02-10
```

### Phase 2: Create development-plan.md

**Source material:**
- Current working context from various status files
- Recent work (web search, Phase 1 completion)
- Outstanding tasks

**Content structure:**
```markdown
# ExFrame Development Plan

*Working context and daily notes*

## Current State (2026-02-10)
- System: Version 1.6.1, Phase 1 persona system complete
- Container: Running and healthy
- Recent work: Web search implementation with source verification

## Active Projects
- [ ] Documentation reorganization (this file)
- [ ] Surveyor feature (planned, not implemented)
- [ ] WiseMan experiment (architectural exploration)

## Known Issues
- None critical

## Next Tasks
1. Complete documentation cleanup
2. Review ARCHITECTURE.md for accuracy
3. Update README.md to version 1.6.1

## Completed Recently
- 2026-02-10: Web search fully functional with DuckDuckGo
- 2026-02-04: Phase 1 persona system shipped
- 2026-02-05: Annotation system documentation

## Reference
- ARCHITECTURE.md - System design
- CHANGELOG.md - Version history
- docs/INDEX.md - Documentation navigation
```

### Phase 3: Create ARCHITECTURE.md

**Source material to consolidate:**
- `PLUGIN_ARCHITECTURE.md` (41,258 bytes) - Current plugin system
- `docs/architecture/overview.md` - System overview
- `docs/reference/domain-config.md` - Domain configuration reference
- `statemachine-design.md` (12,069 bytes) - State machine v2.0
- `MULTITURN.md` (24,140 bytes) - Multi-turn API
- `docs/PHASE2_SEMANTIC_DOCS.md` - Semantic document search
- `WEB_SEARCH_COMPLETE.md` - Web search implementation

**Files to move (not consolidate):**
- `docs/INDEX.md` → Move to `INDEX.md` at root (navigation index)

**Content structure:**
```markdown
# ExFrame Architecture

**Version:** 1.6.1
**Last Updated:** 2026-02-10

## System Overview
[From docs/architecture/overview.md]

## Plugin Architecture
[From PLUGIN_ARCHITECTURE.md - core system]

### Domain Types
Type 1: Generation-only (poet, etc.)
Type 2: Document-only (librarian)
Type 4: Full system with plugins (researcher, etc.)

### Plugin System
- Enrichers
- Researchers
- Validators
- [Full details from PLUGIN_ARCHITECTURE.md]

## State Machine
[From statemachine-design.md - 6-state system]

## Multi-Turn API
[From MULTITURN.md - API reference for function calling]

## Semantic Document Search
[From docs/PHASE2_SEMANTIC_DOCS.md]
- Embeddings-based semantic search
- Document pattern matching
- [Implementation details]

## Web Search Implementation
[From WEB_SEARCH_COMPLETE.md implementation section]
- DuckDuckGo client-side search
- Multi-turn function calling with GLM-4.7
- Source verification system
- Full page content fetching

## Persona System
- Researcher (data_source="internet")
- Librarian (data_source="library")
- Poet (data_source="void")

## Future Plans
- WiseMan experiment (archived to .archive/ or design/ at root)
- State machine refactor (archived to .archive/ or design/ at root)
- Surveyor feature (summarized in development-plan.md)
```

**Requirements:**
- All technical details must be accurate
- All code references must match current implementation
- All version numbers must be correct
- Librarian and coder will use this as reference

### Phase 4: Review and Validate

**Before archiving anything:**

1. **Read through ARCHITECTURE.md**
   - Does it accurately describe the current system?
   - Are all component descriptions correct?
   - Are code examples accurate?
   - Are API signatures correct?

2. **Read through development-plan.md**
   - Is current state accurate?
   - Are version numbers correct?
   - Are tasks properly tracked?

3. **Test with Librarian**
   - Can librarian find answers in ARCHITECTURE.md?
   - Are there any contradictions or errors?

4. **Test with Coder**
   - Can coder understand system from ARCHITECTURE.md?
   - Are implementation details sufficient?

**Validation checklist:**
- [ ] ARCHITECTURE.md reviewed for technical accuracy
- [ ] All version numbers verified (1.6.1)
- [ ] All code references checked against source
- [ ] development-plan.md reviewed for completeness
- [ ] Librarian tested: can answer architecture questions
- [ ] Coder tested: can implement from documentation
- [ ] No broken links or references
- [ ] Container still runs successfully

### Phase 5: Update README.md

**Changes needed:**
1. Version: 1.3.0 → 1.6.1
2. Remove domain type references (superseded by personas)
3. Update for Phase 1 persona system
4. Add link to ARCHITECTURE.md
5. Add link to development-plan.md
6. Verify all external references point to correct files

### Phase 6: Archive Old Files (ONLY AFTER APPROVAL)

**After review and approval, archive these:**

```bash
# Create archive directory (dated for reference)
mkdir -p .archive/2026-02-10-doc-reorg

# Archive Phase 1 artifacts
mv STATUS.md PHASE1_STATUS.md IMPLEMENTATION_SUMMARY.md .archive/2026-02-10-doc-reorg/
mv TOMORROW.md DONE.md PHASE1_COMPLETE.md .archive/2026-02-10-doc-reorg/
mv WHATS_LEFT.md TESTING_GUIDE.md .archive/2026-02-10-doc-reorg/

# Archive old architecture (consolidated into ARCHITECTURE.md)
mv ARCHITECTURE_SPEC.md Three_wise_men.md .archive/2026-02-10-doc-reorg/
mv roles.md sa1.md state-log-ideas.md logviewer-design.md .archive/2026-02-10-doc-reorg/
mv "Creation myth exframe style.md" dream_loom.md .archive/2026-02-10-doc-reorg/
mv PLUGIN_ARCHITECTURE.md .archive/2026-02-10-doc-reorg/  # Consolidated into ARCHITECTURE.md
mv statemachine-design.md .archive/2026-02-10-doc-reorg/  # Consolidated into ARCHITECTURE.md
mv MULTITURN.md .archive/2026-02-10-doc-reorg/  # Consolidated into ARCHITECTURE.md

# Archive web search implementation docs (consolidated into ARCHITECTURE.md)
mv WEB_SEARCH_COMPLETE.md WEB_SEARCH_WORKING.md .archive/2026-02-10-doc-reorg/
mv WEB_SEARCH_STATUS.md GLM_WEB_SEARCH_FINAL.md .archive/2026-02-10-doc-reorg/
mv ZAI_WEB_SEARCH_ARCHITECTURE.md ZAI_CREDIT_ISSUE.md .archive/2026-02-10-doc-reorg/

# Archive Surveyor docs (summarized in development-plan.md)
mv SURVEYOR_IMPLEMENTATION_PLAN.md SURVEYOR_STATUS.md .archive/2026-02-10-doc-reorg/
mv SURVEYOR_STATUS_AND_PLAN.md SURVEYOR_USER_REDESIGN.md .archive/2026-02-10-doc-reorg/

# Archive status tracking
rm ISSUES.md RESOLVED.md titled.md  # Empty files
mv CURRENT_STATE.md SYSTEM_RESTORED.md .archive/2026-02-10-doc-reorg/

# Archive meta docs
mv DOCUMENTATION_UPDATE.md PATTERNS_CLEANUP.md .archive/2026-02-10-doc-reorg/

# Move INDEX.md to root BEFORE archiving docs/
cp docs/INDEX.md INDEX.md

# Archive docs/ directory (content consolidated into 4 core files)
mv docs/ .archive/2026-02-10-doc-reorg/docs-directory

# Archive creative content
mkdir -p creative/essays creative/narratives
mv entice.md university.md firstsite.md easy-recipe.md creative/essays/
mv "Notes from the Originator.md" creative/narratives/notes-from-originator.md

# Optional: Keep design docs at root or archive them
mkdir -p design
mv .archive/2026-02-10-doc-reorg/docs-directory/WISEMAN_*.md design/
mv .archive/2026-02-10-doc-reorg/docs-directory/PLUGIN_REFACTOR_DESIGN.md design/
mv .archive/2026-02-10-doc-reorg/docs-directory/UNIVERSAL_LOGGING_DESIGN.md design/

# Remove venv directory
rm -rf venv/

# Remove draft directory
rm -rf new-docs/
```

---

## Directory Structure After Cleanup

```
/
├── README.md                           # Entry point
├── CHANGELOG.md                        # Version history
├── ARCHITECTURE.md                     # System design (NEW)
├── development-plan.md                 # Working context (NEW)
├── INDEX.md                            # Navigation index (moved from docs/)
├── INSTALL.md                          # User installation
├── annotation.md                       # Annotation system
├── ANNOTATION_PHILOSOPHY.md
├── ANNOTATION_SYSTEM_SETUP.md
├── ANNOTATION_OBSIDIAN_INTEGRATION.md
├── DEPENDENCY_LICENSES.md              # Legal
├── RELEASE_NOTES.md                    # (or merge into CHANGELOG)
├── ignored.md                          # Security feature
├── claude.md                           # Development notes (out of scope)
│
├── design/                             # Future architecture plans (optional)
│   ├── WISEMAN_ARCHITECTURE.md         # Or move to .archive/
│   ├── WISEMAN_DESIGN.md
│   ├── WISEMAN_IMPLEMENTATION_GUIDE.md
│   └── PLUGIN_REFACTOR_DESIGN.md
│
├── creative/                           # Separated from technical
│   ├── essays/
│   │   ├── entice.md
│   │   ├── university.md
│   │   ├── firstsite.md
│   │   └── easy-recipe.md
│   └── narratives/
│       └── notes-from-originator.md
│
└── .archive/                           # Preserved but out of way
    └── 2026-02-10-doc-reorg/           # All archived docs including docs/ directory
```

---

## Step-by-Step Implementation

### Step 1: Create Draft Area

```bash
# Create draft directory
mkdir -p new-docs
cd new-docs
```

### Step 2: Draft development-plan.md

```bash
# Create from current context
cat > new-docs/development-plan.md << 'EOF'
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
1. **Documentation Reorganization** (current)
   - Creating ARCHITECTURE.md
   - Creating development-plan.md
   - Consolidating scattered docs

2. **Surveyor Feature** (planned)
   - Status: Design phase
   - See docs/design/ for plans

3. **WiseMan Experiment** (exploration)
   - Status: Architectural research
   - See docs/design/WISEMAN_*.md

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
- Documentation scattered across 44 files (being addressed)
- Some status files need archiving
- Creative content mixed with technical docs

### Next Tasks
1. Complete ARCHITECTURE.md draft
2. Review both new docs for accuracy
3. Update README.md to 1.6.1
4. Get approval for archive phase
5. Execute archive (only after approval)

### Reference Links
- **ARCHITECTURE.md** (when created) - System design
- **CHANGELOG.md** - Version history
- **INDEX.md** - Documentation navigation (at root)
- **README.md** - User guide

EOF
```

### Step 3: Draft ARCHITECTURE.md (Manual Work)

This requires careful consolidation of multiple files. Must ensure:
- All technical details are accurate
- All version numbers are 1.6.1
- All code references match current implementation
- Librarian can use this to answer questions
- Coder can use this to understand the system

**Template:** See "Content structure" in Phase 3 above

**Sources to read and consolidate:**
1. `PLUGIN_ARCHITECTURE.md`
2. `docs/architecture/overview.md`
3. `statemachine-design.md`
4. `MULTITURN.md`
5. `docs/PHASE2_SEMANTIC_DOCS.md`
6. `WEB_SEARCH_COMPLETE.md` (implementation sections)

### Step 4: Review Phase (CRITICAL)

**Before archiving anything:**

```bash
# Review drafts
cat new-docs/development-plan.md
cat new-docs/ARCHITECTURE.md

# Test with librarian
# Ask questions about system architecture
# Verify librarian can find answers in ARCHITECTURE.md

# Test with coder
# Can coder understand the system from ARCHITECTURE.md?
# Are implementation details sufficient?

# Verify container still works
docker ps | grep eeframe
```

### Step 5: Move to Root (After Approval)

```bash
# Only after review and approval
mv new-docs/development-plan.md .
mv new-docs/ARCHITECTURE.md .
rmdir new-docs
```

### Step 6: Update README.md

**Required changes:**
1. Version header: 1.3.0 → 1.6.1
2. Remove/replace domain type references
3. Update Phase 1 description (it's shipped, not planned)
4. Add section: "Documentation"
   - Link to ARCHITECTURE.md
   - Link to development-plan.md
   - Link to docs/INDEX.md
5. Verify all links work

### Step 7: Archive Old Files (Final Step)

**Only after all above complete and approved.**
See Phase 6 commands above.

---

## Critical Requirements

### Accuracy is Mandatory

**Why this matters:**
- **Librarian** uses documentation to answer questions
  - Wrong info → librarian gives wrong answers
  - Outdated versions → confusion about current state
  - Incorrect code references → impossible to implement

- **Coder** uses documentation to understand system
  - Wrong architecture → code won't work
  - Incorrect APIs → integration failures
  - Missing details → wasted time searching source

**Validation before completion:**
- [ ] Every technical fact verified against source code
- [ ] Every version number checked (1.6.1)
- [ ] Every code snippet tested
- [ ] Every API signature verified
- [ ] Every file path confirmed to exist
- [ ] All links tested and working

### Librarian Testing

Test questions librarian should be able to answer from ARCHITECTURE.md:
- What are the three persona types?
- How does web search work in ExFrame?
- What is the state machine flow?
- How do plugins work?
- What is the difference between researcher and librarian?
- How does semantic document search work?

### Coder Testing

Test coder should be able to understand from ARCHITECTURE.md:
- Overall system architecture
- How to add a new domain
- How plugins are loaded and executed
- How multi-turn API calls work
- How web search is integrated
- How to implement a new enricher

---

## Safety Measures

### Git Protection

```bash
# Tag before any changes
git tag pre-doc-reorg-2026-02-10

# If something goes wrong
git reset --hard pre-doc-reorg-2026-02-10
```

### Review Gates

1. **Draft gate:** Don't leave new-docs/ until reviewed
2. **Accuracy gate:** Don't move to root until verified
3. **Librarian gate:** Don't proceed if librarian confused
4. **Coder gate:** Don't proceed if coder can't implement
5. **Archive gate:** Don't delete anything until all above passed

### Rollback Plan

If issues found after moving to root:
```bash
# Revert
git checkout pre-doc-reorg-2026-02-10 -- README.md
rm ARCHITECTURE.md development-plan.md
# Start over
```

If issues found after archiving:
```bash
# Restore from archive
cp -r .archive/2026-02-10-doc-reorg/* .
# Revert git commit
git revert HEAD
```

---

## Commands Summary

```bash
# Phase 1: Setup
git tag pre-doc-reorg-2026-02-10
mkdir -p new-docs

# Phase 2: Draft development-plan.md
# (use template above)

# Phase 3: Draft ARCHITECTURE.md
# (manual work - read sources, consolidate carefully)

# Phase 4: Review
cat new-docs/development-plan.md
cat new-docs/ARCHITECTURE.md
# Test with librarian
# Test with coder
docker ps | grep eeframe

# Phase 5: Move to root (AFTER APPROVAL)
mv new-docs/*.md .
rmdir new-docs

# Phase 6: Update README.md
# (manual edit)

# Phase 7: Archive (AFTER APPROVAL)
# (use commands from Phase 6 above)

# Final commit
git add .
git commit -m "docs: minimal documentation reorganization

- Created ARCHITECTURE.md consolidating all technical docs
- Created development-plan.md for working context
- Archived Phase 1 artifacts and old architecture docs
- Updated README.md to version 1.6.1
- Preserved docs/ directory for reference documentation
- Separated creative content to creative/

Core documentation: README.md, CHANGELOG.md, ARCHITECTURE.md, development-plan.md"

git push
git push origin pre-doc-reorg-2026-02-10
```

---

## Success Criteria

✅ **Four core files at root:**
- README.md (updated to 1.6.1)
- CHANGELOG.md (current)
- ARCHITECTURE.md (accurate, complete)
- development-plan.md (current, useful)

✅ **INDEX.md at root:**
- Navigation index (moved from docs/INDEX.md)

✅ **docs/ directory eliminated:**
- All content consolidated into the 4 core files
- Future design docs moved to design/ or archived

✅ **All technical content accurate:**
- Librarian can answer architecture questions
- Coder can implement from documentation
- No wrong version numbers
- No broken code references
- All links work

✅ **Historical content preserved:**
- Archived in .archive/2026-02-10-doc-reorg/
- Nothing lost, all in git history

✅ **System still functional:**
- Container runs successfully
- No broken imports or references
- Documentation matches code

---

## Timeline Estimate

- Phase 1-2: 15 minutes (setup, development-plan.md)
- Phase 3: 1-2 hours (ARCHITECTURE.md consolidation - careful work)
- Phase 4: 30 minutes (review, testing)
- Phase 5-6: 30 minutes (move files, update README)
- Phase 7: 15 minutes (archive)

**Total:** 2.5-3.5 hours (mostly careful consolidation and review)

---

**End of Conservative Documentation Fix Plan**
