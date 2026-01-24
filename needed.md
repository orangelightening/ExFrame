# Architectural Improvements Needed

## Root Cause Analysis

**Issue Discovered:** The `LLMFallbackEnricher.__init__` was hard-coding `config["mode"] = "fallback"`, making the domain.json config meaningless. This deep-hidden bug caused hours of debugging because the configuration appeared correct but was silently overridden.

---

## Architectural Proposals

### 1. Config Validation Layer
Add a central config validator that:
- Validates all configs at startup
- Logs warnings when hard-coded defaults override user configs
- Provides a `/api/config/validate` endpoint to see what's actually being used

### 2. Explicit vs Implicit Defaults
- Never hard-code defaults in `__init__` that silently override configs
- Use a config schema with declared defaults
- Log when defaults are applied vs user values

### 3. Order-of-Operations Pipeline
Instead of scattered logic (specialist → enricher → response), define explicit stages:
```
Query → [Stage 1: Primary Search] → [Stage 2: Secondary Search] → [Stage 3: Synthesis] → Response
```
Each stage is pluggable and orderable via config, not hard-coded.

### 4. Debug/Trace Mode
Add a `debug_order=true` flag that logs:
- Exactly what searches ran
- In what order
- What each returned
- Why something was skipped

### 5. Separation: "Document Search" from "LLM"
Currently conflated. Research strategy should be a first-class plugin, not buried inside LLM enricher.

---

## Implementation Workplan

### Phase 1: Config Transparency (Quick Wins)
**Goal:** Make config issues visible immediately

| Task | File(s) | Estimate |
|------|---------|----------|
| Add config validation at domain load time | `core/domain.py`, `generic_framework/api/app.py` | 2h |
| Log when defaults override user configs | All plugin `__init__` methods | 1h |
| Add `/api/config/:domain/validate` endpoint | `generic_framework/api/` | 1h |
| Add startup summary of all loaded configs | `core/universe.py` | 1h |

**Total Phase 1: ~5 hours**

---

### Phase 2: Debug/Trace Mode
**Goal:** Make order-of-operations visible

| Task | File(s) | Estimate |
|------|---------|----------|
| Add `debug_pipeline=true` flag to domain config | `core/domain.py` | 0.5h |
| Add stage logging to specialist plugins | `core/specialist_plugin.py` | 1h |
| Add stage logging to enricher plugins | `core/enrichment_plugin.py` | 1h |
| Add pipeline visualization to traces | `generic_framework/assist/engine.py` | 2h |
| Add UI toggle for debug mode | Frontend | 2h |

**Total Phase 2: ~6.5 hours**

---

### Phase 3: Pipeline Architecture (Core Refactor)
**Goal:** Explicit, configurable search stages

| Task | File(s) | Estimate |
|------|---------|----------|
| Design pipeline stage interface | `core/pipeline_stage.py` (new) | 2h |
| Extract document search from LLM enricher | `plugins/document_search/` (new) | 3h |
| Implement stage executor | `core/pipeline.py` (new) | 4h |
| Migrate specialist to use pipeline | `core/specialist_plugin.py` | 3h |
| Migrate enricher to use pipeline | `core/enrichment_plugin.py` | 2h |
| Update domain.json for pipeline config | All `domain.json` files | 1h |
| Remove old hard-coded mode logic | `plugins/enrichers/llm_enricher.py` | 0.5h |

**Total Phase 3: ~15.5 hours**

---

### Phase 4: Config Schema & Validation
**Goal:** Type-safe, validated configs

| Task | File(s) | Estimate |
|------|---------|----------|
| Define JSON schema for all configs | `config/schemas/` (new) | 3h |
| Add schema validation at load time | `core/domain.py` | 2h |
| Add config migration system | `core/config_migration.py` (new) | 2h |
| Document all config options | `/docs/configuration.md` | 2h |

**Total Phase 4: ~9 hours**

---

## Total Estimated Effort

| Phase | Hours | Priority |
|-------|-------|----------|
| Phase 1: Config Transparency | 5h | **HIGH** - Do first |
| Phase 2: Debug/Trace Mode | 6.5h | **HIGH** - Enables debugging |
| Phase 3: Pipeline Architecture | 15.5h | **MEDIUM** - Core refactor |
| Phase 4: Config Schema | 9h | **LOW** - Nice to have |

**Total: ~36 hours**

---

## Recommended Implementation Order

1. **Start with Phase 1** - Makes config issues visible immediately
2. **Then Phase 2** - Adds debugging visibility
3. **Phase 3 or 4** - Can be done in either order, or in parallel

---

## Implementation Log

### Increment 1.2: Detect Default Overrides (COMPLETED ✓)

**Date:** 2026-01-24

**What was implemented:**
- Added override detection in `generic_framework/plugins/enrichers/llm_enricher.py`
- Logs warning when hard-coded defaults override user configs
- Both logger.warning() and print() for visibility

**Changes made:**
```python
# Before (silent override):
def __init__(self, config: Optional[Dict[str, Any]] = None):
    config = config or {}
    config["mode"] = "fallback"  # Silently overrides user config!
    super().__init__(config)

# After (visible override):
def __init__(self, config: Optional[Dict[str, Any]] = None):
    config = config or {}
    # CONFIG OVERRIDE DETECTION: Log when hard-coded defaults override user config
    if "mode" in config and config["mode"] != "fallback":
        logger.warning(
            "[CONFIG] llm_enricher: hard-coded default 'mode=fallback' is overriding user config "
            f"'mode={config['mode']}'. User config value will be ignored."
        )
        print(
            f"  [CONFIG OVERRIDE WARNING] llm_enricher: hard-coded default 'mode=fallback' "
            f"is overriding user config 'mode={config['mode']}'"
        )
    config["mode"] = "fallback"
    super().__init__(config)
```

**Test checkpoint passed:**
- Set domain.json to `"mode": "always"`
- Loaded domain and saw warning in logs
- Warning: `[CONFIG OVERRIDE WARNING] llm_enricher: hard-coded default 'mode=fallback' is overriding user config 'mode=always'`

**Result:**
- Any hard-coded default overriding user config now immediately visible in logs
- The exact bug that caused hours of debugging is now caught at startup with a clear warning message

**Files modified:**
- `generic_framework/plugins/enrichers/llm_enricher.py`
  - Added `import logging`
  - Added `logger = logging.getLogger(__name__)`
  - Added override detection in `__init__` method

**Next steps:**
- Apply same pattern to other plugins (specialists, other enrichers)
- Scan codebase for other instances of hard-coded defaults in `__init__` methods

---

### Override Detection Applied (COMPLETED ✓)

**Date:** 2026-01-24 (continued)

All 3 remaining items from scan completed:

| File | Class | Hard-coded default | Status |
|------|-------|-------------------|--------|
| `generic_framework/plugins/enrichers/llm_enricher.py` | `LLMSummarizerEnricher` | `config["mode"] = "enhance"` | ✓ Fixed |
| `generic_framework/plugins/routers/multi_specialist_router.py` | `ParallelRouter` | `config["strategy"] = "parallel"` | ✓ Fixed |
| `generic_framework/plugins/routers/multi_specialist_router.py` | `SequentialRouter` | `config["strategy"] = "sequential"` | ✓ Fixed |

**Changes made:**
- Added `import logging` to `multi_specialist_router.py`
- Added override detection to all 3 classes
- All follow same pattern as `LLMFallbackEnricher`

**Result:**
- All hard-coded config overrides now visible at startup
- System started successfully with changes
- No errors or warnings (except expected document store warning)

---

## Current State (For Git Commit)

Changes made during debugging session:
- Fixed `specialist_id` attribute in `generic_framework/plugins/exframe/exframe_specialist.py`
- Added `_form_response` method to `generic_framework/plugins/exframe/exframe_specialist.py`
- Modified exframe specialist to always run both document AND pattern searches
- Added `_search_local_docs` method (currently returns 0 results - needs investigation)

**Open Issue:** Document search (research strategy) still runs after patterns, not before.
