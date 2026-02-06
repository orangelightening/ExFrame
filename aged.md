# ExFrame Documentation Audit Report

**Generated**: 2026-02-05
**Purpose**: Identify outdated, redundant, or obsolete documentation
**Goal**: Simplest possible documentation set

---

## Executive Summary

**Total Markdown Files Audited**: 39 files

**Recommendation Summary**:
- **KEEP**: 16 files (core documentation + future designs)
- **DELETE**: 15 files (outdated, redundant, or development notes)
- **EDIT**: 4 files (remove venv instructions, add status warnings)
- **MERGE**: 0 files
- **OUT OF SCOPE**: 2 files (development notes, explicitly excluded)

**Impact**: Reducing from 39 to 20 active documentation files (49% reduction)

---

## Root Directory Files

| File | Status | Action | Notes |
|------|--------|--------|-------|
| README.md | Current | KEEP | Main user-facing documentation, up to date with Phase 1 |
| INSTALL.md | Current | KEEP | Docker installation guide, accurate |
| CHANGELOG.md | Current | KEEP | Version history, needed |
| RELEASE_NOTES.md | Current | KEEP | Release documentation, needed |
| PLUGIN_ARCHITECTURE.md | Current | KEEP | Plugin development guide, still relevant |
| ARCHITECTURE_SPEC.md | Outdated | DELETE | Pre-plugin architecture, superseded by PLUGIN_ARCHITECTURE.md |
| DEPENDENCY_LICENSES.md | Current | KEEP | Legal requirement, keep |
| STATUS.md | Outdated | DELETE | Describes Phase 1 as "planned" but it's now complete and shipped |
| PHASE1_STATUS.md | Outdated | DELETE | Phase 1 implementation notes, historical only |
| IMPLEMENTATION_SUMMARY.md | Outdated | DELETE | Day 1 summary, historical only |
| TOMORROW.md | Outdated | DELETE | Next day work plan from Feb 4, obsolete |
| DONE.md | Outdated | DELETE | Completion report, redundant with STATUS.md |
| PHASE1_COMPLETE.md | Outdated | DELETE | Completion status, historical |
| WHATS_LEFT.md | Outdated | DELETE | Task list from Phase 1, obsolete |
| TESTING_GUIDE.md | Outdated | DELETE | Phase 1 testing, no longer needed |
| ignored.md | Current | KEEP | Security feature, actively used |
| sa1.md | Unknown | DELETE | Appears to be old design notes about "systematic approach" |
| roles.md | Outdated | DELETE | Roles and responsibilities, mostly historical |
| state-log-ideas.md | Historical | DELETE | Design ideas, not implemented |
| logviewer-design.md | Historical | DELETE | Design doc for feature not built |
| statemachine-design.md | Current | KEEP | State machine design v2.0 - Status: Implemented (2026-01-31) |
| Creation myth exframe style.md | Creative | DELETE | Narrative/creative writing, not documentation |
| dream_loom.md | Creative | DELETE | Narrative/creative writing, not documentation |
| Three_wise_men.md | Historical | DELETE | Old "wisemen" concept, replaced by personas |
| claude.md | Dev Notes | OUT OF SCOPE | Development session notes, outside ExFrame |

---

## docs/ Directory Files

| File | Status | Action | Notes |
|------|--------|--------|-------|
| docs/INDEX.md | Current | KEEP | File navigation index, useful |
| docs/PLUGIN_REFACTOR_DESIGN.md | Draft | EDIT | State machine design v2, has open questions and concerns, needs status update |
| docs/PHASE1_PERSONA_DESIGN.md | Historical | DELETE | Design doc for Phase 1 (now complete), keep for reference but archivable |
| docs/PHASE2_SEMANTIC_DOCS.md | Current | KEEP | Phase 2 design (semantic document search) - JUST IMPLEMENTED in this session |
| docs/WISEMAN_ARCHITECTURE.md | Future Design | KEEP | Long-term vision, not yet implemented, marked as design phase |
| docs/WISEMAN_DESIGN.md | Future Design | KEEP | Supporting design doc for WiseMan architecture |
| docs/WISEMAN_IMPLEMENTATION_GUIDE.md | Future Design | KEEP | Implementation guide for future WiseMan refactor |

---

## universes/MINE/docs/ Files

| File | Status | Action | Notes |
|------|--------|--------|-------|
| universes/MINE/docs/README.md | Outdated | EDIT | Contains venv setup instructions (lines 677-689), remove and keep Docker-only |
| universes/MINE/docs/user-guide.md | Unknown | EDIT | Check for venv/pip install references, keep Docker-only |
| universes/MINE/docs/context.md | Dev Notes | OUT OF SCOPE | Development session context, outside ExFrame scope |

---

## Detailed Analysis by Category

### 1. Current & Essential (KEEP - 11 files)

These are accurate, relevant, and necessary:

1. **README.md** - Main user guide, updated with Phase 1 personas
2. **INSTALL.md** - Docker installation instructions
3. **CHANGELOG.md** - Version history
4. **RELEASE_NOTES.md** - Release documentation
5. **PLUGIN_ARCHITECTURE.md** - Plugin development guide
6. **DEPENDENCY_LICENSES.md** - Legal compliance
7. **ignored.md** - Security feature documentation
8. **docs/INDEX.md** - File navigation index

### 2. Outdated Phase 1 Documentation (DELETE - 9 files)

Phase 1 is now complete and shipped. These implementation/planning docs are historical:

1. **STATUS.md** - Describes Phase 1 as "PLANNED" but it's SHIPPED
2. **PHASE1_STATUS.md** - Day-by-day implementation tracking
3. **IMPLEMENTATION_SUMMARY.md** - Day 1 summary
4. **TOMORROW.md** - Next day work plan (Feb 4, 2026)
5. **DONE.md** - Phase 1 completion report
6. **PHASE1_COMPLETE.md** - Another completion report
7. **WHATS_LEFT.md** - To-do list for Phase 1
8. **TESTING_GUIDE.md** - Phase 1 testing instructions
9. **docs/PHASE1_PERSONA_DESIGN.md** - Design doc (implementation complete)

**Rationale**: Phase 1 is in production. Keep one summary in CHANGELOG/RELEASE_NOTES, delete the implementation breadcrumbs.

### 3. Pre-Plugin Architecture (DELETE - 1 file)

1. **ARCHITECTURE_SPEC.md** - Describes old architecture before plugin system

**Rationale**: Superseded by PLUGIN_ARCHITECTURE.md. The plugin system is the current architecture.

### 4. Unimplemented/Historical Designs (DELETE - 2 files)

Design documents for features that were never built or are obsolete:

1. **state-log-ideas.md** - Ideas for logging, not implemented
2. **logviewer-design.md** - Log viewer design, never built

**Rationale**: Design docs are useful during development, but if the feature isn't built or is replaced, the docs should go.

### 5. Old Concepts (DELETE - 3 files)

Documents about superseded concepts:

1. **Three_wise_men.md** - Old "wisemen" concept, replaced by personas in Phase 1
2. **roles.md** - Roles and responsibilities, mostly about old system
3. **sa1.md** - Appears to be old "systematic approach" notes

**Rationale**: These describe concepts that no longer exist in the current system.

### 6. Creative/Narrative (DELETE - 2 files)

Non-technical creative writing:

1. **Creation myth exframe style.md** - Narrative story about ExFrame
2. **dream_loom.md** - Narrative/creative writing

**Rationale**: Not documentation, not needed for using or developing ExFrame.

### 7. Needs Updates (EDIT - 4 files)

1. **docs/PLUGIN_REFACTOR_DESIGN.md**
   - Status: Draft with many open questions
   - Action: Add note at top: "STATUS: DRAFT - State machine architecture design v2. Many open questions remain. Implementation not yet started. See PLUGIN_ARCHITECTURE.md for current plugin system."

2. **universes/MINE/docs/README.md**
   - Status: Contains outdated venv setup instructions
   - Action: Remove lines 677-689 (venv setup section). Everything is Docker-only now.

3. **universes/MINE/docs/user-guide.md**
   - Status: May contain pip install references
   - Action: Remove any venv/pip setup instructions. Docker-only deployment.

### 8. Out of Scope (OUT OF SCOPE - 2 files)

Development session notes, explicitly outside ExFrame documentation scope:

1. **claude.md** - Development session notes with Claude
2. **universes/MINE/docs/context.md** - Development context tracking

**Rationale**: User noted these are "development session notes" outside ExFrame scope.

---

## Recommendations Summary Table

### Keep (16 files)
```
/home/peter/development/eeframe/README.md
/home/peter/development/eeframe/INSTALL.md
/home/peter/development/eeframe/CHANGELOG.md
/home/peter/development/eeframe/RELEASE_NOTES.md
/home/peter/development/eeframe/PLUGIN_ARCHITECTURE.md
/home/peter/development/eeframe/DEPENDENCY_LICENSES.md
/home/peter/development/eeframe/ignored.md
/home/peter/development/eeframe/statemachine-design.md
/home/peter/development/eeframe/docs/INDEX.md
/home/peter/development/eeframe/docs/PHASE2_SEMANTIC_DOCS.md
/home/peter/development/eeframe/docs/WISEMAN_ARCHITECTURE.md
/home/peter/development/eeframe/docs/WISEMAN_DESIGN.md
/home/peter/development/eeframe/docs/WISEMAN_IMPLEMENTATION_GUIDE.md
/home/peter/development/eeframe/docs/architecture/overview.md
/home/peter/development/eeframe/docs/guides/domain-types.md
/home/peter/development/eeframe/docs/reference/domain-config.md
```

### Edit (4 files)
```
/home/peter/development/eeframe/docs/PLUGIN_REFACTOR_DESIGN.md
  → Add "STATUS: DRAFT - Not yet implemented" warning at top

/home/peter/development/eeframe/universes/MINE/docs/README.md
  → Remove venv setup section (lines 677-689) - Docker-only now

/home/peter/development/eeframe/universes/MINE/docs/user-guide.md
  → Remove any venv/pip install references - Docker-only now
```

### Delete (15 files)
```
# Phase 1 implementation breadcrumbs (obsolete)
/home/peter/development/eeframe/STATUS.md
/home/peter/development/eeframe/PHASE1_STATUS.md
/home/peter/development/eeframe/IMPLEMENTATION_SUMMARY.md
/home/peter/development/eeframe/TOMORROW.md
/home/peter/development/eeframe/DONE.md
/home/peter/development/eeframe/PHASE1_COMPLETE.md
/home/peter/development/eeframe/WHATS_LEFT.md
/home/peter/development/eeframe/TESTING_GUIDE.md
/home/peter/development/eeframe/docs/PHASE1_PERSONA_DESIGN.md

# Old architecture/concepts
/home/peter/development/eeframe/ARCHITECTURE_SPEC.md
/home/peter/development/eeframe/Three_wise_men.md
/home/peter/development/eeframe/roles.md
/home/peter/development/eeframe/sa1.md

# Unimplemented designs
/home/peter/development/eeframe/state-log-ideas.md
/home/peter/development/eeframe/logviewer-design.md

# Creative/narrative (not technical docs)
/home/peter/development/eeframe/Creation myth exframe style.md
/home/peter/development/eeframe/dream_loom.md
```

### Out of Scope (2 files - leave as-is)
```
/home/peter/development/eeframe/claude.md
/home/peter/development/eeframe/universes/MINE/docs/context.md
```

---

## Rationale for Simplification

### Current State
- 39 total markdown files
- Many outdated implementation notes
- Multiple Phase 1 completion reports
- Historical design docs for replaced features

### Desired State
- 16 core documentation files (current) + 3 future design files
- Clear purpose for each file
- No redundancy or outdated information
- Easy for new users to navigate
- Docker-only deployment (no venv references)

### Benefits
1. **New User Experience**: Clear, minimal doc set
2. **Maintenance**: Less to keep updated
3. **Clarity**: No confusion about what's current
4. **Focus**: Documentation matches current codebase

---

## Implementation Plan

### Step 1: Archive (Recommended)
Create `.archive/old-docs/` and move deleted files there rather than deleting permanently:

```bash
mkdir -p .archive/old-docs
mv STATUS.md .archive/old-docs/
mv PHASE1_STATUS.md .archive/old-docs/
# ... etc for all DELETE recommendations
```

### Step 2: Update Files
Add status warnings to PLUGIN_REFACTOR_DESIGN.md and PHASE2_SEMANTIC_DOCS.md

### Step 3: Update INDEX.md
Remove references to archived files

### Step 4: Update README
Ensure README points to correct current documentation

---

## Notes

1. **Preservation**: Consider archiving rather than deleting for historical reference
2. **Git History**: All content is preserved in git history even if deleted
3. **Phase 2**: When Phase 2 is implemented, PHASE2_SEMANTIC_DOCS.md becomes current documentation
4. **Plugin Refactor**: If state machine refactor happens, PLUGIN_REFACTOR_DESIGN.md becomes current
5. **Development Notes**: claude.md and context.md are explicitly out of scope per user

---

## Quick Command Summary

### To archive all DELETE recommendations:
```bash
cd /home/peter/development/eeframe
mkdir -p .archive/old-docs

# Archive root-level obsolete files
mv STATUS.md PHASE1_STATUS.md IMPLEMENTATION_SUMMARY.md TOMORROW.md \
   DONE.md PHASE1_COMPLETE.md WHATS_LEFT.md TESTING_GUIDE.md \
   ARCHITECTURE_SPEC.md Three_wise_men.md roles.md sa1.md \
   state-log-ideas.md logviewer-design.md \
   "Creation myth exframe style.md" dream_loom.md \
   .archive/old-docs/

# Archive docs/ files
mv docs/PHASE1_PERSONA_DESIGN.md .archive/old-docs/

# Remove venv directory entirely (no longer needed)
rm -rf venv/
```

### Result
Clean documentation set with clear purpose and no obsolete files.

---

## Additional Cleanup: Remove venv Directory

The project has a `venv/` directory at the root that should be completely removed since everything runs in Docker now:

```bash
# Remove the entire venv directory
rm -rf /home/peter/development/eeframe/venv
```

The `.gitignore` already excludes `venv/` so it won't be committed, but it's taking up disk space and is no longer needed.

---

**End of Audit Report**
