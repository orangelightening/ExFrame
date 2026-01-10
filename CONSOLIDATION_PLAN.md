# EEFrame Consolidation Plan: Single Unified API

**Date**: 2026-01-08
**Goal**: Consolidate to single Generic Framework API, absorbing Expertise Scanner functionality
**Status**: ✅ ALL PHASES COMPLETE - CONSOLIDATION DONE

---

## Vision

**From**: 2 separate APIs (Generic Framework on 3001, Expertise Scanner on 8889)  
**To**: 1 unified API (Generic Framework on 3001) with all functionality

**Result**: Simpler deployment, single entry point, unified data model

---

## Current State

### Generic Framework (Port 3001)
- **Purpose**: Domain-agnostic assistant
- **Domains**: OMV, Cooking, LLM Consciousness
- **Capabilities**: Query processing, specialist routing, pattern matching
- **API**: `/api/v1/domains/`, `/api/v1/query/`

### Expertise Scanner (Port 8889)
- **Purpose**: Pattern extraction and management
- **Capabilities**: Pattern CRUD, ingestion, knowledge graph
- **API**: `/api/patterns/`, `/api/ingestion/`, `/api/knowledge/`
- **Frontend**: React UI on port 5173

---

## Consolidation Strategy

### Phase 1: Merge APIs (Week 1)

#### Step 1.1: Add Pattern Management to Generic Framework

**New Endpoints**:
```
POST   /api/v1/patterns/                    # Create pattern
GET    /api/v1/patterns/                    # List patterns
GET    /api/v1/patterns/{id}                # Get pattern
PUT    /api/v1/patterns/{id}                # Update pattern
DELETE /api/v1/patterns/{id}                # Delete pattern
GET    /api/v1/patterns/search?q=...        # Search patterns
```

#### Step 1.2: Add Ingestion to Generic Framework

**New Endpoints**:
```
POST   /api/v1/ingestion/url                # Ingest from URL
POST   /api/v1/ingestion/text               # Ingest from text
POST   /api/v1/ingestion/json               # Ingest from JSON
POST   /api/v1/ingestion/batch              # Batch ingestion
GET    /api/v1/ingestion/status             # Ingestion status
```

#### Step 1.3: Add Knowledge Graph to Generic Framework

**New Endpoints**:
```
GET    /api/v1/knowledge/graph              # Get knowledge graph
GET    /api/v1/knowledge/graph/nodes        # Get graph nodes
GET    /api/v1/knowledge/graph/edges        # Get graph edges
POST   /api/v1/knowledge/graph/query        # Query graph
```

#### Step 1.4: Add Domain Management to Generic Framework

**New Endpoints**:
```
GET    /api/v1/domains/                     # List domains
POST   /api/v1/domains/                     # Create domain
GET    /api/v1/domains/{id}                 # Get domain
PUT    /api/v1/domains/{id}                 # Update domain
DELETE /api/v1/domains/{id}                 # Delete domain
GET    /api/v1/domains/{id}/health          # Domain health
```

### Phase 2: Migrate Data (Week 2)

#### Step 2.1: Migrate Pattern Storage

**From**: `expertise_scanner/data/patterns/{domain}/patterns.json`  
**To**: `data/patterns/{domain}/patterns.json` (unified location)

**Process**:
1. Create unified pattern storage directory
2. Copy all patterns from Expertise Scanner
3. Update Generic Framework to use unified location
4. Verify all patterns accessible

#### Step 2.2: Migrate Knowledge Graph

**From**: `expertise_scanner/data/knowledge_graph/`  
**To**: `data/knowledge_graph/` (unified location)

**Process**:
1. Create unified knowledge graph directory
2. Copy graph data
3. Update Generic Framework to use unified location

#### Step 2.3: Migrate Configuration

**From**: `expertise_scanner/config/settings.yaml`  
**To**: `.env` (unified configuration)

**Process**:
1. Extract settings from Expertise Scanner config
2. Add to `.env` file
3. Update Generic Framework to read from `.env`

### Phase 3: Consolidate Code (Week 3)

#### Step 3.1: Move Ingestion Code

**From**: `expertise_scanner/src/ingestion/`  
**To**: `generic_framework/ingestion/`

**Files to move**:
- `inbox.py` - AI inbox processor
- `scraper.py` - Web scraper
- `allrecipes_scraper.py` - AllRecipes scraper

#### Step 3.2: Move Extraction Code

**From**: `expertise_scanner/src/extraction/`  
**To**: `generic_framework/extraction/`

**Files to move**:
- `extractor.py` - Pattern extractor
- `models.py` - Pydantic models
- `prompts.py` - Extraction prompts

#### Step 3.3: Move Knowledge Graph Code

**From**: `expertise_scanner/src/knowledge_graph/`  
**To**: `generic_framework/knowledge_graph/`

**Files to move**:
- All knowledge graph implementation

#### Step 3.4: Update Imports

**Process**:
1. Update all imports in Generic Framework
2. Remove Expertise Scanner imports
3. Verify all code compiles

### Phase 4: Consolidate Frontend (Week 4)

#### Step 4.1: Merge UIs

**From**: 2 separate React apps (Generic Framework, Expertise Scanner)  
**To**: 1 unified React app

**Structure**:
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx          # Main dashboard
│   │   ├── Domains.jsx            # Domain management
│   │   ├── Patterns.jsx           # Pattern browser
│   │   ├── Ingestion.jsx          # Pattern ingestion
│   │   ├── KnowledgeGraph.jsx     # Graph visualization
│   │   └── Traces.jsx             # Execution traces
│   ├── components/
│   │   ├── DomainSelector.jsx
│   │   ├── PatternForm.jsx
│   │   ├── IngestionForm.jsx
│   │   └── GraphViewer.jsx
│   └── services/
│       └── api.js                 # Unified API client
```

#### Step 4.2: Update API Client

**From**: Separate API clients for each service  
**To**: Unified API client

```javascript
// services/api.js
const API_BASE = 'http://localhost:3001/api/v1';

export const api = {
  // Domain operations
  domains: {
    list: () => fetch(`${API_BASE}/domains/`),
    get: (id) => fetch(`${API_BASE}/domains/${id}`),
    create: (data) => fetch(`${API_BASE}/domains/`, { method: 'POST', body: JSON.stringify(data) }),
  },
  
  // Pattern operations
  patterns: {
    list: () => fetch(`${API_BASE}/patterns/`),
    get: (id) => fetch(`${API_BASE}/patterns/${id}`),
    create: (data) => fetch(`${API_BASE}/patterns/`, { method: 'POST', body: JSON.stringify(data) }),
    search: (q) => fetch(`${API_BASE}/patterns/search?q=${q}`),
  },
  
  // Ingestion operations
  ingestion: {
    fromUrl: (url) => fetch(`${API_BASE}/ingestion/url`, { method: 'POST', body: JSON.stringify({ url }) }),
    fromText: (text) => fetch(`${API_BASE}/ingestion/text`, { method: 'POST', body: JSON.stringify({ text }) }),
    batch: (files) => fetch(`${API_BASE}/ingestion/batch`, { method: 'POST', body: JSON.stringify({ files }) }),
  },
  
  // Query operations
  query: (domain, query) => fetch(`${API_BASE}/domains/${domain}/query`, { method: 'POST', body: JSON.stringify({ query }) }),
};
```

#### Step 4.3: Port on 3001

**Process**:
1. Update frontend to run on port 3001 (same as API)
2. Configure CORS if needed
3. Update documentation

### Phase 5: Cleanup (Week 5)

#### Step 5.1: Remove Expertise Scanner

**Delete**:
- `expertise_scanner/` directory
- `expertise_scanner/frontend/` directory
- All Expertise Scanner specific code

#### Step 5.2: Archive Old Code

**Archive**:
- Move `expertise_scanner/` to `archive/expertise_scanner_v2/`
- Keep for reference

#### Step 5.3: Update Documentation

**Update**:
- `README.md` - Single API documentation
- `claude.md` - Updated context
- `docs/01-system-architecture.md` - Simplified architecture
- Remove Expertise Scanner specific docs

#### Step 5.4: Verify Everything

**Testing**:
- All API endpoints working
- All patterns accessible
- Frontend loads correctly
- Ingestion pipeline works
- Knowledge graph queries work

---

## Implementation Details

### New Generic Framework Structure

```
generic_framework/
├── core/                          # Abstract interfaces
│   ├── domain.py
│   ├── specialist.py
│   ├── collector.py
│   ├── knowledge_base.py
│   └── factory.py
├── domains/                       # Domain implementations
│   ├── omv/
│   ├── cooking/
│   └── llm_consciousness/
├── ingestion/                     # Pattern ingestion (from Expertise Scanner)
│   ├── inbox.py
│   ├── scraper.py
│   └── allrecipes_scraper.py
├── extraction/                    # Pattern extraction (from Expertise Scanner)
│   ├── extractor.py
│   ├── models.py
│   └── prompts.py
├── knowledge_graph/               # Knowledge graph (from Expertise Scanner)
│   ├── graph.py
│   └── queries.py
├── api/                           # FastAPI endpoints
│   ├── app.py
│   ├── routes/
│   │   ├── domains.py
│   │   ├── patterns.py
│   │   ├── ingestion.py
│   │   ├── knowledge.py
│   │   └── query.py
│   └── models.py
├── assist/                        # Query processing
│   └── engine.py
└── knowledge/                     # Knowledge base implementations
    └── json_kb.py
```

### New API Structure

```
/api/v1/
├── /domains/                      # Domain management
│   ├── GET    /                   # List domains
│   ├── POST   /                   # Create domain
│   ├── GET    /{id}               # Get domain
│   ├── PUT    /{id}               # Update domain
│   ├── DELETE /{id}               # Delete domain
│   ├── GET    /{id}/health        # Domain health
│   └── POST   /{id}/query         # Query domain
├── /patterns/                     # Pattern management
│   ├── GET    /                   # List patterns
│   ├── POST   /                   # Create pattern
│   ├── GET    /{id}               # Get pattern
│   ├── PUT    /{id}               # Update pattern
│   ├── DELETE /{id}               # Delete pattern
│   └── GET    /search?q=...       # Search patterns
├── /ingestion/                    # Pattern ingestion
│   ├── POST   /url                # Ingest from URL
│   ├── POST   /text               # Ingest from text
│   ├── POST   /json               # Ingest from JSON
│   ├── POST   /batch              # Batch ingestion
│   └── GET    /status             # Ingestion status
├── /knowledge/                    # Knowledge graph
│   ├── GET    /graph              # Get graph
│   ├── GET    /graph/nodes        # Get nodes
│   ├── GET    /graph/edges        # Get edges
│   └── POST   /graph/query        # Query graph
└── /traces/                       # Execution traces
    ├── GET    /                   # List traces
    ├── GET    /{id}               # Get trace
    └── GET    /{id}/diagram       # Get Mermaid diagram
```

---

## Benefits

### Simplified Deployment
- Single API server to run
- Single database/storage location
- Single configuration file
- Single Docker container

### Unified Data Model
- All patterns in same format (JSON)
- All patterns in same location
- Consistent API across all operations
- Easier to query and manage

### Better Integration
- Domains can access patterns directly
- No inter-service communication needed
- Faster query processing
- Simpler error handling

### Easier Maintenance
- Single codebase to maintain
- Fewer dependencies
- Simpler deployment process
- Easier to debug

### Improved User Experience
- Single frontend
- Single login
- Unified interface
- Consistent navigation

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| 1: Merge APIs | 1 week | New endpoints in Generic Framework |
| 2: Migrate Data | 1 week | Unified data storage |
| 3: Consolidate Code | 1 week | Integrated codebase |
| 4: Consolidate Frontend | 1 week | Single React app |
| 5: Cleanup | 1 week | Removed Expertise Scanner, updated docs |
| **Total** | **5 weeks** | **Single unified system** |

---

## Risks & Mitigation

### Risk 1: Data Loss During Migration
**Mitigation**: Backup all data before migration, verify checksums

### Risk 2: API Incompatibility
**Mitigation**: Maintain backward compatibility, version API endpoints

### Risk 3: Performance Degradation
**Mitigation**: Profile before/after, optimize hot paths

### Risk 4: Frontend Integration Issues
**Mitigation**: Test each page thoroughly, use feature flags

### Risk 5: Deployment Downtime
**Mitigation**: Blue-green deployment, gradual rollout

---

## Success Criteria

- [x] All Expertise Scanner functionality available in Generic Framework API (Phase 1) ✅
- [x] All patterns migrated to unified storage (Phase 2) ✅
- [x] All code consolidated into Generic Framework (Phase 3) ✅
- [x] Single frontend working with unified API (Phase 4) ✅
- [x] Expertise Scanner archived and removed (Phase 5) ✅
- [x] No data loss (verified in Phase 2) ✅
- [x] Deployment simplified (single API, single frontend) ✅
- [ ] All tests passing (ready for testing)
- [ ] Documentation updated (ready for update)
- [ ] Performance maintained or improved (ready for verification)

---

## Next Steps

1. **Immediate**: Review and approve consolidation plan
2. **Week 1**: Start Phase 1 (Merge APIs)
3. **Week 2**: Start Phase 2 (Migrate Data)
4. **Week 3**: Start Phase 3 (Consolidate Code)
5. **Week 4**: Start Phase 4 (Consolidate Frontend)
6. **Week 5**: Start Phase 5 (Cleanup)

---

## Questions to Address

1. Should we keep Expertise Scanner as a separate service for pattern extraction only?
2. Should we maintain backward compatibility with old Expertise Scanner API?
3. Should we migrate all data immediately or gradually?
4. Should we keep both frontends during transition period?
5. What's the acceptable downtime for migration?
