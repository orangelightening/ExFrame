# EEFrame - Consolidated Context Recovery File

**Purpose**: Complete context for resuming work on the EEFrame project after refactoring.

**Last Updated**: 2026-01-08  
**Status**: Refactored - AI Communications removed, OMV integrated into Generic Framework  
**Version**: 3.0.0

---

## System Overview

**EEFrame** is now a unified framework consisting of three integrated systems:

1. **Generic Framework**: Domain-agnostic assistant with pluggable domains
   - Unified architecture for any domain (OMV, Cooking, Python, etc.)
   - Specialist/Collector pattern for extensibility
   - FastAPI backend (port 3001)
   - Supports multiple domains simultaneously

2. **Expertise Scanner**: Pattern extraction and knowledge graph system
   - Extracts patterns from any domain
   - AI inbox workflow (GLM-4.7 → JSON → patterns)
   - 6 domains with patterns (cooking, python, omv, diy, first_aid, gardening)
   - FastAPI backend (port 8889), React frontend (port 5173)

3. **Docker Infrastructure**: Monitoring stack
   - Prometheus (9090), Grafana (3001), Loki (3100), Promtail
   - Auto-provisioned dashboards and datasources

**Removed**: AI Communications system (three-way chat protocol) - no longer needed

---

## Quick Start Commands

### Generic Framework

```bash
# Navigate to project
cd /home/peter/development/eeframe

# Activate virtual environment
source venv/bin/activate

# Start Generic Framework API (port 3001)
python -m generic_framework.api.app

# Access API docs
# http://localhost:3001/docs
```

### Expertise Scanner

```bash
# Navigate to expertise scanner
cd /home/peter/development/eeframe/expertise_scanner

# Start backend API (port 8889)
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8889 --reload

# Start frontend (port 5173)
cd frontend && npm run dev
```

### Monitoring Stack

```bash
# Start Docker Compose stack
docker-compose up -d

# Access services
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
# Loki: http://localhost:3100
```

**Access URLs**:
- Generic Framework API Docs: http://localhost:3001/docs
- Expertise Scanner API Docs: http://localhost:8889/docs
- Expertise Scanner UI: http://localhost:5173
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

---

## Generic Framework Details

### Current Status
- **Phase**: Refactored with OMV domain integration
- **Domains**: OMV (5 specialists), Cooking (4 specialists), LLM Consciousness (2 specialists)
- **Architecture**: Abstract base classes (Domain, Specialist, Collector, KnowledgeBase)
- **Extensibility**: Factory pattern for dynamic domain registration

### OMV Domain (New)

**Location**: `generic_framework/domains/omv/`

**Components**:
- **Domain**: `OMVDomain` - Manages OMV server management
- **Specialists** (5 total):
  1. `StorageSpecialist` - Disk management, RAID, filesystems
  2. `NetworkSpecialist` - Network configuration, interfaces
  3. `ServiceSpecialist` - Service management, SMB, NFS, SSH
  4. `PerformanceSpecialist` - CPU, memory, optimization
  5. `SecuritySpecialist` - Permissions, access control
- **Collectors** (3 total):
  1. `OMVSSHCollector` - Direct SSH command execution
  2. `OMVPrometheusCollector` - Metrics collection
  3. `OMVLokiCollector` - Log aggregation

**Usage**:
```python
from generic_framework.domains.omv import OMVDomain
from generic_framework.core.domain import DomainConfig

config = DomainConfig(
    domain_id="omv",
    domain_name="OpenMediaVault",
    version="1.0",
    description="Server management domain"
)

domain = OMVDomain(
    config=config,
    knowledge_base=kb,
    omv_host="192.168.1.100",
    prometheus_url="http://localhost:9090",
    loki_url="http://localhost:3100"
)

await domain.initialize()
specialist = domain.get_specialist_for_query("How do I configure storage?")
result = await specialist.process_query("How do I configure storage?")
```

### Key Components

- **FastAPI Backend**: Port 3001
- **Core Interfaces**: `Domain`, `Specialist`, `Collector`, `KnowledgeBase`
- **Domain Factory**: Dynamic domain registration
- **Assistant Engine**: Generic query processing
- **Knowledge Base**: JSON-based pattern storage

### Critical Configuration

```bash
# Generic Framework
FRAMEWORK_PORT=3001
FRAMEWORK_HOST=0.0.0.0

# OMV Domain (if using)
OMV_HOSTNAME=192.168.1.100
OMV_PORT=22
OMV_USERNAME=root
OMV_PASSWORD=[password]

# LLM (GLM-4.7)
LLM_API_ENDPOINT=https://api.z.ai/api/coding/paas/v4/chat/completions
LLM_API_KEY=[your-api-key]

# Monitoring
MONITORING_PROMETHEUS_URL=http://localhost:9090
MONITORING_LOKI_URL=http://localhost:3100
```

---

## Expertise Scanner Details

### Current Status
- **Validated and Working**: All core functionality operational
- **Domains Created**: cooking, python, omv, diy, first_aid, gardening
- **Test Patterns**: 14 synthetic patterns with proper structure
- **Pattern Relationships**: 22 edges (related, prerequisites, alternatives)
- **AI Inbox**: Primary data source via GLM-4.7 generated JSON files

### Key Components
- **FastAPI Backend**: Port 8889
- **React Frontend**: Port 5173 with Tailwind CSS v3
- **Pattern Storage**: JSON files per domain in `data/patterns/{domain}/`
- **Knowledge Graph**: Basic structure in `data/knowledge_graph/`
- **AI Inbox**: Directory at `/home/peter/development/eeframe/pattern-inbox/`

### Pattern Data Model

```python
class Pattern:
    id: str                    # "{domain}_{number:03d}"
    domain: str                # "cooking", "python", "omv", etc.
    name: str                  # Short descriptive name
    pattern_type: str          # "troubleshooting", "procedure", etc.
    description: str           # What this pattern does
    problem: str               # What problem does it solve?
    solution: str              # How is it solved?
    steps: List[str]           # Procedural steps
    conditions: Dict[str, str] # Decision points
    related_patterns: List[str] # IDs of related patterns
    prerequisites: List[str]   # Must do these first
    alternatives: List[str]    # Other ways to solve this
    confidence: float          # 0-1 reliability score
    sources: List[str]         # URLs, references
    tags: List[str]            # Free-form labels
    examples: List[str]        # Concrete examples
```

### AI Inbox Workflow
1. External GLM-4.7 generates JSON files with structured data
2. Saves to `/home/peter/development/eeframe/pattern-inbox/`
3. User clicks "Process" in AI Inbox section (frontend `/batch` page)
4. System converts JSON to patterns and stores in appropriate domain

---

## Architecture Changes (Refactoring)

### Before Refactoring
- 4 independent systems (OMV Co-Pilot, Expertise Scanner, Generic Framework, AI Communications)
- Port conflicts (OMV Co-Pilot and Generic Framework both on 3000)
- Duplicate functionality (pattern-based assistance in both OMV and Generic Framework)
- File-based message protocol (AI Communications)

### After Refactoring
- 3 integrated systems (Generic Framework, Expertise Scanner, Docker Infrastructure)
- Clear port allocation (Framework: 3001, Scanner: 8889/5173)
- Unified architecture (all domains use same interfaces)
- Direct API communication (no message queue)

### Benefits
- **Reduced Duplication**: Single pattern-based assistance pipeline
- **Improved Maintainability**: Clear separation of concerns
- **Better Extensibility**: New domains follow same pattern
- **Simplified Communication**: Direct API calls

---

## State Machine Overview

### Generic Framework States

```
IDLE → QUERY_RECEIVED → DOMAIN_SELECTION → SPECIALIST_SELECTION →
CONTEXT_COLLECTION → PATTERN_MATCHING → CONFIDENCE_CALCULATION →
PROMPT_BUILDING → LLM_GENERATION → RESPONSE_ASSEMBLY → IDLE
```

### Expertise Scanner States

```
IDLE → VALIDATING → SCRAPING → EXTRACTING → STORING → INDEXING → IDLE
```

**Alternative Inputs**: `json_input`, `text_input`, `manual_create` go directly to appropriate states

---

## Critical Configuration Details

### GLM API Endpoint (IMPORTANT)
```
https://api.z.ai/api/coding/paas/v4/chat/completions
```
**NOT** `open.bigmodel.com` - that's the Chinese platform endpoint.

### SSL Certificate Issue
GLM API requires `verify=False` in httpx.AsyncClient due to certificate verification failures.

### OMV SSH Collection
OMV 7.x restricts RPC API to localhost only. Primary collection method is SSH-based.

### Port Configuration
- Generic Framework API: 3001 (was 3000, now unified)
- Expertise Scanner API: 8889
- Expertise Scanner Frontend: 5173
- Prometheus: 9090
- Grafana: 3001
- Loki: 3100

### Python Version
- **Development**: Python 3.13.7
- **Minimum**: Python 3.11+
- **Tested**: 3.13.7

---

## Known Issues & Solutions

### Issue 1: Port Conflict (RESOLVED)
**Cause**: OMV Co-Pilot and Generic Framework both on port 3000
**Solution**: Generic Framework now on port 3001

### Issue 2: Duplicate Functionality (RESOLVED)
**Cause**: Both OMV Co-Pilot and Generic Framework implemented pattern-based assistance
**Solution**: OMV integrated into Generic Framework as a domain

### Issue 3: AI Communications Overhead (RESOLVED)
**Cause**: File-based message protocol added complexity
**Solution**: Removed AI Communications system, using direct API calls

### Issue 4: GLM API SSL Certificate Error
**Cause**: Certificate verification fails
**Solution**: Added `verify=False` to httpx.AsyncClient

### Issue 5: GLM API Returns `reasoning_content` Instead of `content`
**Cause**: GLM-4.7 response format difference
**Solution**: Updated `_extract_content()` to handle `reasoning_content` field

### Issue 6: AllRecipes Scraper Data Quality
**Cause**: Rule-based extraction produces malformed patterns
**Solution**: Deprioritized scraping in favor of AI-generated JSON inbox

### Issue 7: Tailwind CSS v4 White Screen Issue
**Cause**: Compatibility problem in Expertise Scanner frontend
**Solution**: Downgraded to Tailwind CSS v3

---

## Development Workflow

### Adding New Domains

1. Create domain directory: `generic_framework/domains/mydomain/`
2. Implement `Domain` subclass with abstract methods
3. Implement `Specialist` subclasses for domain expertise
4. Implement `Collector` subclasses for data collection
5. Register domain in factory
6. Add patterns to Expertise Scanner

### Adding New Specialists to OMV Domain

1. Create specialist class in `generic_framework/domains/omv/specialists.py`
2. Inherit from `OMVSpecialistBase`
3. Implement `can_handle()` and `process_query()` methods
4. Register in `OMVDomain.initialize()`

### Adding Knowledge Patterns

1. **Manual**: Use Expertise Scanner UI form
2. **AI Inbox**: Place JSON files in `pattern-inbox/`, process via UI
3. **API**: `POST /api/patterns/` with full pattern data

### Testing Changes

```bash
# Test Generic Framework
curl -s http://localhost:3001/docs

# Test Expertise Scanner
curl -s http://localhost:8889/api/patterns/ | jq '.patterns | length'

# Validate Expertise Scanner
cd expertise_scanner && python3 scripts/validate_system.py
```

---

## Documentation Structure

**Main Documentation** (`docs/` directory):
- `01-system-architecture.md` - High-level overview
- `02-domain-co-pilot-guide.md` - Generic Framework guide
- `03-expertise-scanner-guide.md` - Pattern extraction guide
- `04-state-machines.md` - State machine diagrams
- `05-api-reference.md` - API endpoints
- `06-pattern-catalog.md` - Pattern documentation
- `07-development-guide.md` - Development workflow

**Additional Resources**:
- `reverse.md` - System reverse engineering report
- `REFACTORING_SUMMARY.md` - Refactoring details and migration guide
- `claude.md` - This file (context recovery)

**Archived/Obsolete** (`archive/docs/`):
- Old design documents and specifications
- Kept for historical reference

---

## Next Phase Options

### High Priority
1. **Port Configuration**: Verify all ports are correctly configured
2. **Pattern Migration**: Convert OMV patterns from YAML to JSON
3. **Frontend Consolidation**: Decide on single vs multiple frontends
4. **Documentation**: Update all docs to reflect new architecture

### Medium Priority
5. **Add More Domains**: DIY, Gardening, First Aid from Expertise Scanner
6. **Enhanced Monitoring**: Integrate Prometheus/Grafana/Loki
7. **Pattern Learning**: Implement feedback-based pattern confidence adjustment
8. **Knowledge Graph**: Enhance with Neo4j for complex queries

### Low Priority
9. **User Authentication**: Basic auth for web interfaces
10. **Advanced Workflows**: Multi-step diagnostics, solution verification
11. **Community Features**: Pattern sharing, collaborative editing
12. **Production Hardening**: Security audit, HA configuration

---

## File Structure

```
generic_framework/
├── domains/
│   ├── omv/                    # OMV server management domain (NEW)
│   │   ├── __init__.py
│   │   ├── domain.py
│   │   ├── specialists.py
│   │   └── collectors.py
│   ├── cooking/
│   │   ├── __init__.py
│   │   ├── domain.py
│   │   └── specialists.py
│   └── llm_consciousness/
│       ├── __init__.py
│       ├── domain.py
│       └── specialists.py
├── core/
│   ├── domain.py
│   ├── specialist.py
│   ├── collector.py
│   ├── knowledge_base.py
│   └── factory.py
├── api/
│   └── app.py
└── assist/
    └── engine.py
```

---

## Verification Checklist

- [x] AI Communications directory deleted
- [x] OMV domain created with all components
- [x] 5 OMV specialists implemented
- [x] 3 OMV collectors implemented
- [x] Module exports configured
- [x] reverse.md updated with refactoring details
- [x] REFACTORING_SUMMARY.md created
- [x] README.md updated
- [x] claude.md updated
- [ ] docs/01-system-architecture.md updated
- [ ] Port configuration verified
- [ ] Pattern migration completed
- [ ] Frontend consolidation completed

---

**Document Version**: 3.0.0 (Refactored)  
**Based on**: Previous claude.md with refactoring updates  
**Implementation Status**: Generic Framework operational with OMV domain, Expertise Scanner operational, Docker Infrastructure ready
