# Architecture Separation - Clean Code Verification

**Date:** February 16, 2026
**Status:** ✅ CLEAN - No Spaghetti Code

---

## Module Dependency Graph

```
ExFrame (generic_framework/)
    ↓
    Uses: Tao Core
    ↑
Tao Core (tao/storage, tao/analysis)
    ↑
    Uses: Tao Core (shared infrastructure)
    ↑
BrainUse (tao/vetting/)
    ↑
    NO dependencies on ExFrame
```

**Key Principle:** BrainUse is **parasitic** - it consumes Tao infrastructure but is isolated from ExFrame.

---

## Dependency Rules (Currently Enforced)

### ✅ BrainUse Module (`tao/vetting/`)

**Allowed Dependencies:**
- ✅ `from tao.storage import load_history` - Shared infrastructure
- ✅ `from tao.analysis import sophistication, depth, concepts` - Shared analysis
- ✅ `from fastapi import APIRouter` - Framework
- ✅ `from pydantic import BaseModel` - Framework

**Forbidden Dependencies:**
- ❌ `from generic_framework.*` - NO ExFrame imports
- ❌ `from core.*` - NO ExFrame core imports
- ❌ `from frontend.*` - NO ExFrame frontend imports
- ❌ `from assist.*` - NO ExFrame assist imports

**Verification:**
```bash
$ grep -r "from generic_framework" tao/vetting/
✓ No matches (clean)

$ grep -r "from.*core\." tao/vetting/
✓ No matches (clean)

$ grep -r "import.*frontend" tao/vetting/
✓ No matches (clean)
```

---

## Module Structure

### BrainUse Module (`tao/vetting/`)

```
tao/vetting/
├── __init__.py              # Module exports (clean interface)
├── models.py                # Pydantic models (no external deps)
├── candidate_manager.py     # Business logic (only uses Tao)
├── benchmark_engine.py      # Benchmarking (self-contained)
├── report_generator.py      # Report generation (only uses Tao)
├── api_router.py            # FastAPI router (clean REST API)
└── frontend/
    ├── index.html           # Standalone UI (Alpine.js)
    └── assets/
        └── brainuse.js      # Standalone logic (no ExFrame deps)
```

**Clean Properties:**
1. ✅ No imports from ExFrame
2. ✅ Only depends on Tao (shared infrastructure)
3. ✅ Self-contained frontend (no shared components)
4. ✅ Separate API namespace (`/api/brainuse`)
5. ✅ Separate static assets (`/brainuse/assets`)

---

## Integration Points (Minimal & Clean)

### 1. API Router Mounting (`app.py`)

```python
# Generic Framework app.py (line 262)

# CLEAN: Router is imported and mounted, but modules don't mix
from tao.vetting.api_router import router as brainuse_router
app.include_router(brainuse_router)
```

**Why this is clean:**
- BrainUse router is self-contained
- No direct imports of BrainUse logic into ExFrame
- Uses FastAPI's built-in router system (proper pattern)
- Can be removed by deleting 2 lines

### 2. Static Assets Mounting (`app.py`)

```python
# Generic Framework app.py (line 375)

brainuse_assets_path = Path(__file__).parent.parent / "tao" / "vetting" / "frontend" / "assets"
if brainuse_assets_path.exists():
    app.mount("/brainuse/assets", StaticFiles(directory=str(brainuse_assets_path)), name="brainuse_assets")
```

**Why this is clean:**
- Separate URL namespace (`/brainuse/assets`)
- No shared static files
- Can be removed by deleting 5 lines

### 3. Frontend Route (`app.py`)

```python
# Generic Framework app.py (line 935)

@app.get("/brainuse", response_class=HTMLResponse)
async def serve_brainuse():
    brainuse_html = Path(__file__).parent.parent / "tao" / "vetting" / "frontend" / "index.html"
    # ... serve HTML
```

**Why this is clean:**
- Separate route (`/brainuse`)
- No shared templates or components
- Serves completely independent HTML
- Can be removed by deleting 1 function

---

## Shared Infrastructure (By Design)

### Tao Core (Intentionally Shared)

```python
# BrainUse uses Tao (this is correct):
from tao.storage import load_history
from tao.analysis import sophistication, depth, concepts
```

**Why this is correct:**
- Tao is **shared infrastructure** (like a database)
- ExFrame writes Q/R pairs to Tao
- BrainUse reads Q/R pairs from Tao
- Neither knows about the other
- Both depend on Tao, not on each other

**Analogy:**
```
Database (Tao Storage)
    ↑
    ├── ExFrame writes data
    └── BrainUse reads data

    ✓ Clean separation through shared data layer
```

---

## Isolation Guarantees

### 1. No Code Mixing
- ✅ BrainUse code is in `tao/vetting/`
- ✅ ExFrame code is in `generic_framework/`
- ✅ No circular dependencies
- ✅ No shared business logic

### 2. No UI Mixing
- ✅ BrainUse UI is self-contained (`tao/vetting/frontend/`)
- ✅ ExFrame UI is self-contained (`generic_framework/frontend/`)
- ✅ No shared components or styles
- ✅ Different design systems (both use TailwindCSS but independently)

### 3. No API Mixing
- ✅ BrainUse API is `/api/brainuse/*`
- ✅ ExFrame API is `/api/query/*`, `/api/domains/*`
- ✅ Tao API is `/api/tao/*` (shared by both)
- ✅ Clear namespace separation

### 4. No Data Model Mixing
- ✅ BrainUse models: `Candidate`, `Assessment`, `Report`, `Benchmark`
- ✅ ExFrame models: `QueryRequest`, `DomainConfig`, `SpecialistConfig`
- ✅ Tao models: `SessionDetail`, `ConceptStats`, `QueryChain`
- ✅ No overlapping concerns

---

## Easy Extraction Path

If you ever want to move BrainUse to a separate codebase:

### Step 1: Copy Module
```bash
cp -r tao/vetting/ ../brainuse/
```

### Step 2: Update Imports
```python
# Change:
from tao.storage import load_history

# To:
from tao_client.storage import load_history  # Tao as a library
```

### Step 3: Remove from ExFrame
```python
# app.py - Delete 3 blocks:
# 1. Router mounting (2 lines)
# 2. Static assets (5 lines)
# 3. Frontend route (1 function)
```

### Step 4: Create Standalone App
```python
# brainuse/app.py (new file)
from fastapi import FastAPI
from .api_router import router

app = FastAPI(title="BrainUse")
app.include_router(router)
```

**Result:** Completely independent BrainUse application in 30 minutes.

---

## Anti-Patterns Avoided

### ❌ Spaghetti Code (NOT Present)
- ❌ Circular imports - NONE
- ❌ Shared global state - NONE
- ❌ Mixed concerns in single files - NONE
- ❌ Tightly coupled logic - NONE

### ✅ Clean Patterns (Currently Used)
- ✅ Module separation by domain
- ✅ Dependency injection (e.g., `BenchmarkEngine` passed to `ReportGenerator`)
- ✅ Single responsibility (each module has one job)
- ✅ Clear interfaces (Pydantic models define contracts)
- ✅ Shared infrastructure pattern (Tao as data layer)

---

## Code Quality Checklist

### BrainUse Module
- ✅ No imports from ExFrame
- ✅ Only depends on Tao (shared infrastructure)
- ✅ Self-contained frontend
- ✅ Clean API router
- ✅ Proper error handling
- ✅ Type hints throughout
- ✅ Pydantic validation
- ✅ Logging configured

### Integration
- ✅ Minimal mounting code (3 small blocks in app.py)
- ✅ No shared state between ExFrame and BrainUse
- ✅ Can be removed in <5 minutes
- ✅ No side effects on ExFrame functionality

### Testing
- ✅ BrainUse API endpoints work independently
- ✅ ExFrame API endpoints unaffected by BrainUse
- ✅ Can disable BrainUse without breaking ExFrame

---

## Maintenance Rules

### When Adding Features to BrainUse

**DO:**
- ✅ Add code to `tao/vetting/` only
- ✅ Use Tao infrastructure (storage, analysis)
- ✅ Add new API endpoints to `api_router.py`
- ✅ Keep frontend in `tao/vetting/frontend/`

**DON'T:**
- ❌ Import from `generic_framework/`
- ❌ Modify ExFrame core logic
- ❌ Share UI components with ExFrame
- ❌ Mix BrainUse and ExFrame concerns

### When Adding Features to ExFrame

**DO:**
- ✅ Add code to `generic_framework/` only
- ✅ Use Tao for query history storage
- ✅ Keep ExFrame-specific logic separate

**DON'T:**
- ❌ Import from `tao/vetting/`
- ❌ Reference BrainUse models or logic
- ❌ Create dependencies on BrainUse

---

## Summary

### Current State: ✅ CLEAN

**Separation Quality:**
- ✅ No spaghetti code
- ✅ No shortcuts
- ✅ Clean module boundaries
- ✅ Minimal integration points
- ✅ Easy to extract if needed

**Integration Points (All Clean):**
1. Router mounting (2 lines in app.py)
2. Static assets mounting (5 lines in app.py)
3. Frontend route (1 function in app.py)
4. Shared Tao infrastructure (by design)

**Total Integration Code:** ~20 lines in app.py (all removable)

**Conclusion:** Architecture is clean and maintainable. BrainUse is properly isolated as a parasitic use case that consumes Tao infrastructure without coupling to ExFrame.

---

**Verification Commands:**

```bash
# Verify no ExFrame imports in BrainUse
grep -r "from generic_framework" tao/vetting/
# Expected: No results ✓

# Verify no core imports in BrainUse
grep -r "from.*core\." tao/vetting/
# Expected: No results ✓

# Verify clean module structure
tree tao/vetting/ -I '__pycache__'
# Expected: Clean hierarchy ✓

# Test BrainUse API independently
curl http://localhost:3000/api/brainuse/health
# Expected: {"status": "healthy"} ✓

# Test ExFrame still works
curl http://localhost:3000/api/domains
# Expected: Domain list ✓
```

**Status: Architecture is clean with proper separation. No refactoring needed.**
