# Documentation Cleanup Plan

**Date**: 2026-01-29
**Purpose**: Fix all documentation inconsistencies identified by contradiction detection

---

## Summary of Changes

### 1. Project Name Standardization
- **Target**: `ExFrame` (not EEFrame, not OMV-Copilot)
- **Scope**: 43+ occurrences across 20+ files

### 2. License Correction
- **Target**: Apache License 2.0 (not MIT)
- **Scope**: pyproject.toml, advert.md, badges

### 3. Version Alignment
- **Target**: Git-based versioning (v1.5.0-45-g04778ad0)
- **Scope**: README.md, CHANGELOG.md, advert.md, RELEASE_NOTES.md

### 4. Python Version Alignment
- **Target**: Python 3.11 (current container version)
- **Scope**: pyproject.toml, Dockerfile, documentation

---

## Files to Modify

### HIGH PRIORITY: Core Identity Files

| File | Changes Needed |
|------|----------------|
| `pyproject.toml` | 1. Name: ExFrame, 2. License: Apache, 3. Version: remove hardcoded, 4. Python: 3.11, 5. Author: real data, 6. Description: fix |
| `README.md` | 1. Version: dynamic/git, 2. Badge: Apache, 3. Verify ExFrame spelling |
| `CHANGELOG.md` | 1. All references: ExFrame not EEFrame |
| `advert.md` | 1. License: Apache, 2. Version: remove, 3. Name: ExFrame |
| `LICENSE` | Verify Apache 2.0 text (should be correct) |
| `Dockerfile` | 1. Comments: ExFrame not EEFrame |
| `docker-compose.yml` | 1. Comments: ExFrame not EEFrame |
| `PLUGIN_ARCHITECTURE.md` | 1. All references: ExFrame not EEFrame |
| `RELEASE_NOTES.md` | 1. All references: ExFrame |

### MEDIUM PRIORITY: Code Files

| File | Changes Needed |
|------|----------------|
| `generic_framework/plugins/exframe/exframe_specialist.py` | Verify ExFrame references |
| `generic_framework/core/research/__init__.py` | EEFrame → ExFrame |
| `generic_framework/core/research/document_strategy.py` | EEFrame → ExFrame |
| `generic_framework/diagnostics/__init__.py` | EEFrame → ExFrame |
| `generic_framework/diagnostics/pattern_analyzer.py` | EEFrame → ExFrame |
| `autonomous_learning/__init__.py` | EEFrame → ExFrame |
| `autonomous_learning/api/app.py` | EEFrame → ExFrame |
| `test_formatters.py` | EEFrame → ExFrame |
| `test_enrichers.py` | EEFrame → ExFrame |

### LOW PRIORITY: Archive & Config

| File | Changes Needed |
|------|----------------|
| `config/autonomous_learning.yaml` | EEFrame → ExFrame |
| `.archive/` files | Consider updating or leave as historical |
| `config/prometheus/*.yml` | omv-copilot → exframe (in comments/labels) |

---

## Detailed Changes by File

### 1. pyproject.toml

**Current issues:**
- Name: "omv-copilot" ❌
- License: "MIT" ❌
- Version: "2.0.0" ❌ (hardcoded)
- Python: ">=3.11" ❌ (ambiguous)
- Author: "Your Name" ❌ (placeholder)
- Description: "OMV Co-Pilot..." ❌ (wrong)

**Changes:**
```toml
name = "exframe"
license = "Apache-2.0"
# Version will be managed by git tags
requires-python = ">=3.11"
authors = [
    {name = "ExFrame Contributors", email = "noreply@exframe.dev"}
]
description = "Domain-agnostic AI-powered knowledge management system"
```

### 2. README.md

**Changes:**
- Remove hardcoded "Version 1.5.0" - use git describe
- Update badges: License → Apache
- Verify all "ExFrame" references are correct

### 3. CHANGELOG.md

**Changes:**
- Replace all "EEFrame" with "ExFrame"
- Keep version history as-is (historical record)
- Ensure current version references git

### 4. advert.md

**Changes:**
- License: MIT → Apache-2.0
- Version: Remove hardcoded version
- All EEFrame → ExFrame

### 5. Dockerfile

**Changes:**
- Comments: EEFrame → ExFrame
- Python version: Keep python:3.11-slim (matches container)
- Add comment about Python version support

### 6. docker-compose.yml

**Changes:**
- Comments: EEFrame → ExFrame
- Service names: Keep as-is (functional)
- Labels: Update if any EEFrame references

### 7. PLUGIN_ARCHITECTURE.md

**Changes:**
- Replace all "EEFrame" with "ExFrame"
- Update any OMV-Copilot references

---

## Python Version Clarification

**Finding**: Container runs Python 3.11.14

**Decision**:
- Keep `python:3.11-slim` in Dockerfile ✓
- Keep `requires-python = ">=3.11"` in pyproject.toml ✓
- **Add documentation**: "Tested on Python 3.11+. May work on 3.12 but not tested."

---

## Execution Order

### Phase 1: Core Identity (Do First)
1. `pyproject.toml` - Source of truth for package metadata
2. `README.md` - Public facing
3. `LICENSE` - Verify Apache 2.0 text
4. `CHANGELOG.md` - Historical record

### Phase 2: Infrastructure
5. `Dockerfile`
6. `docker-compose.yml`
7. `PLUGIN_ARCHITECTURE.md`

### Phase 3: Code References
8. Python files with EEFrame references
9. Test files
10. Config files

### Phase 4: Cleanup
11. Archive files (optional - can leave as-is for historical context)
12. Verify no remaining EEFrame/OMV-Copilot in active code
13. Run contradiction detection again to verify fixes

---

## Validation Checklist

After changes, verify:

- [ ] No "EEFrame" in active code (except git history)
- [ ] No "omv-copilot" in active code
- [ ] All license references say Apache-2.0
- [ ] Python version is consistent (3.11+)
- [ ] No hardcoded version numbers (use git describe)
- [ ] Author metadata is real or generic placeholder
- [ ] Description matches "domain-agnostic framework"
- [ ] Run contradiction detection - should show 0 high/medium issues

---

## Commands to Verify Changes

```bash
# Check for remaining EEFrame
grep -r "EEFrame" --include="*.py" --include="*.md" . | grep -v ".git" | grep -v ".archive"

# Check for remaining omv-copilot
grep -ri "omv.copilot" --include="*.py" --include="*.md" . | grep -v ".git" | grep -v ".archive"

# Check license references
grep -ri "license.*mit" --include="*.toml" --include="*.md" .

# Verify Python version
grep -r "python.*3\." Dockerfile pyproject.toml

# Test contradiction detection
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ExFrame?", "domain": "exframe"}'
```

---

## Notes

- **Archive files**: Can leave EEFrame/OMV-Copilot references as historical
- **Import statements**: Keep actual Python import paths as-is (functional)
- **Documentation**: All user-facing text should say "ExFrame"
- **Comments**: Update for consistency but not critical
