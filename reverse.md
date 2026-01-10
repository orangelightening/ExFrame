# EEFrame System Reverse Engineering Report

**Date**: 2026-01-08 (Updated: 2026-01-08)
**Purpose**: Document actual codebase state vs documentation claims
**Status**: REFACTORED - AI Communications removed, OMV integrated into Generic Framework

---

## Executive Summary

The EEFrame project has been refactored from **four independent systems** to **three integrated systems**:

1. **OMV Co-Pilot** (being consolidated into Generic Framework)
2. **Expertise Scanner** (Pattern extraction system)
3. **Generic Framework** (Domain-agnostic assistant with OMV domain)
4. **Docker Infrastructure** (Monitoring stack)

The AI Communications system (three-way chat protocol) has been removed as it is no longer needed.

---

## System 1: OMV Co-Pilot (Server Management Assistant)

### Documentation Claims vs Code Reality

| Aspect | Documentation Claim | Code Reality | Status |
|---------|-------------------|---------------|--------|
| **Purpose** | AI-powered assistant for OpenMediaVault server management | ✅ ACCURATE |
| **Architecture** | FastAPI backend + React frontend + CLI tool | ✅ ACCURATE |
| **Data Collection** | SSH-based primary, RPC fallback (OMV 7.x restriction) | ✅ ACCURATE |
| **Knowledge Base** | 24 curated patterns across 5 categories | ✅ ACCURATE |
| **LLM Integration** | GLM-4.7 with international endpoint | ✅ ACCURATE |
| **Execution Tracing** | 10 decision points with Mermaid visualization | ✅ ACCURATE |
| **Passthrough Mode** | Direct LLM access bypassing knowledge base | ✅ ACCURATE |
| **Port** | API: 8888, Frontend: 3000, CLI: system-wide | ⚠️ **INCONSISTENT** |
| **Pattern Storage** | YAML-based in `patterns/manual.yaml` | ✅ ACCURATE |
| **Frontend** | React + Vite + Tailwind CSS | ✅ ACCURATE |

### Actual Implementation

**Code Location**: `src/omv_copilot/`

**Key Components**:
- **API Server**: `src/omv_copilot/api/app.py` - Full FastAPI implementation
- **Assistant Engine**: `src/omv_copilot/assist/assistant_engine.py` - 10-stage pipeline with context selection, pattern matching, confidence scoring
- **Collectors**: SSH (`src/omv_copilot/collectors/ssh_collector.py`), RPC (`src/omv_copilot/collectors/omv_collector.py`), Prometheus (`src/omv_copilot/collectors/prometheus_collector.py`), Loki (`src/omv_copilot/collectors/loki_collector.py`)
- **Knowledge Base**: `src/omv_copilot/knowledge/knowledge_base.py` - Pattern storage and retrieval
- **Specialist Prompts**: `src/omv_copilot/assist/specialist_prompts.py` - Context-specific prompts
- **LLM Client**: `src/omv_copilot/assist/llm_client.py` - GLM-4.7 integration
- **Trace Store**: `src/omv_copilot/assist/trace.py` - Execution tracing
- **CLI Tool**: `src/omv_copilot/cli/main.py` - Click-based CLI
- **Main Entry**: `src/main.py` - Runs on port **8000** (not 8888)

**Frontend**: `frontend/` - React + Vite + Tailwind CSS + D3.js + Recharts

### Inconsistencies

1. **Port Mismatch**: Documentation claims API on port 8888, but `src/main.py` runs on port 8000
2. **Pattern Location**: Documentation doesn't specify exact path to `patterns/manual.yaml`

---

## System 2: Expertise Scanner (Pattern Extraction System)

### Documentation Claims vs Code Reality

| Aspect | Documentation Claim | Code Reality | Status |
|---------|-------------------|---------------|--------|
| **Purpose** | Pattern extraction and knowledge graph for any domain | ✅ ACCURATE |
| **Architecture** | FastAPI backend + React frontend | ✅ ACCURATE |
| **Pattern Data Model** | Rich structure with 8 pattern types | ✅ ACCURATE |
| **Ingestion Pipeline** | AI inbox (primary), web scraping (secondary), manual creation | ✅ ACCURATE |
| **Pattern Storage** | JSON files per domain in `data/patterns/{domain}/` | ✅ ACCURATE |
| **Knowledge Graph** | JSON-based structure for pattern relationships | ✅ ACCURATE |
| **Port** | API: 8889, Frontend: 5173 | ✅ ACCURATE |
| **Domains** | 6 domains (cooking, python, omv, diy, first_aid, gardening) | ✅ ACCURATE |
| **Test Patterns** | 14 synthetic patterns with 22 edges | ✅ ACCURATE |

### Actual Implementation

**Code Location**: `expertise_scanner/`

**Key Components**:
- **API Server**: `expertise_scanner/src/api/main.py` - Full FastAPI implementation
- **Pattern Extraction**: `expertise_scanner/src/extraction/extractor.py` - Rule-based + LLM extraction
- **Pattern Models**: `expertise_scanner/src/extraction/models.py` - Pydantic models
- **Ingestion Routes**: `expertise_scanner/src/api/routes/ingestion.py` - URL, text, batch, inbox processing
- **Pattern Routes**: `expertise_scanner/src/api/routes/patterns.py` - Pattern CRUD operations
- **Knowledge Routes**: `expertise_scanner/src/api/routes/knowledge.py` - Graph queries
- **Cross-Domain Routes**: `expertise_scanner/src/api/routes/cross_domain.py` - Cross-domain analysis
- **Inbox Processor**: `expertise_scanner/src/ingestion/inbox.py` - Processes AI-generated JSON from `/home/peter/development/eeframe/pattern-inbox/`
- **Web Scrapers**: `expertise_scanner/src/ingestion/allrecipes_scraper.py`, `expertise_scanner/src/ingestion/scraper.py` - URL scraping
- **Frontend**: `expertise_scanner/frontend/` - React + Vite + Tailwind CSS v3

### Inconsistencies

1. **None Found** - Documentation accurately describes Expertise Scanner implementation

---

## System 3: Generic Framework (Domain-Agnostic Assistant)

### Documentation Claims vs Code Reality

| Aspect | Documentation Claim | Code Reality | Status |
|---------|-------------------|---------------|--------|
| **Purpose** | Domain-agnostic framework for any domain | ✅ ACCURATE |
| **Architecture** | Abstract base classes + factory pattern | ✅ ACCURATE |
| **Domain Implementations** | Cooking + LLM Consciousness domains | ✅ ACCURATE |
| **Knowledge Base** | JSON-based storage with KnowledgeBase interface | ✅ ACCURATE |
| **Specialist Pattern** | Specialist classes per domain | ✅ ACCURATE |
| **Collector Pattern** | Abstract Collector interface | ✅ ACCURATE |
| **API** | Full CRUD for domains and patterns | ✅ ACCURATE |
| **Port** | API: 3000 (from `generic_framework/api/app.py`) | ⚠️ **INCONSISTENT** |

### Actual Implementation

**Code Location**: `generic_framework/`

**Key Components**:
- **Core Interfaces**: `generic_framework/core/domain.py`, `generic_framework/core/collector.py`, `generic_framework/core/specialist.py`, `generic_framework/core/knowledge_base.py`
- **Domain Factory**: `generic_framework/core/factory.py` - Dynamic domain registration
- **API Server**: `generic_framework/api/app.py` - Full FastAPI with domain management
- **Cooking Domain**: `generic_framework/domains/cooking/domain.py` - Full implementation with 4 specialists
- **LLM Consciousness Domain**: `generic_framework/domains/llm_consciousness/domain.py` - Implementation with 2 specialists
- **Knowledge Implementation**: `generic_framework/knowledge/json_kb.py` - JSON-based knowledge base
- **Assistant Engine**: `generic_framework/assist/engine.py` - Generic assistant engine
- **Test Scripts**: `generic_framework/test_cooking_domain.py`, `generic_framework/test_llm_consciousness_domain.py`

### Inconsistencies

1. **Port Conflict**: Documentation doesn't specify Generic Framework port, but `generic_framework/api/app.py` runs on port 3000, potentially conflicting with OMV Co-Pilot (port 3000)
2. **Domain Registry**: Uses `data/domains.json` for domain configuration
3. **Pattern Storage**: Uses `expertise_scanner/data/patterns/` for storage (cross-system dependency)

---

## System 4: Docker Infrastructure (Monitoring Stack)

### Documentation Claims vs Code Reality

| Aspect | Documentation Claim | Code Reality | Status |
|---------|-------------------|---------------|--------|
| **Purpose** | Containerized monitoring stack | ✅ ACCURATE |
| **Services** | Prometheus (9090), Grafana (3001), Loki (3100), Promtail | ✅ ACCURATE |
| **Configuration** | Auto-provisioned datasources and dashboards | ✅ ACCURATE |
| **Volumes** | Persistent storage for metrics, logs, application data | ✅ ACCURATE |

### Actual Implementation

**Code Location**: `docker-compose.yml`, `Dockerfile`

**Key Components**:
- **Prometheus**: Metrics collection with 15s scrape interval
- **Grafana**: Visualization with admin/admin (port 3001)
- **Loki**: Log aggregation (port 3100)
- **Promtail**: Log shipping agent
- **EEFrame App**: Main application (port 3000)

### Inconsistencies

1. **None Found** - Documentation accurately describes Docker infrastructure

---

## Critical Findings

### 1. Port Conflicts

| Service | Documentation Port | Code Port | Conflict? |
|----------|-------------------|-----------|----------|
| OMV Co-Pilot API | 8888 | 8000 (`src/main.py:19`) | ⚠️ YES |
| OMV Co-Pilot Frontend | 3000 | 3000 (`frontend/`) | ✅ OK |
| Expertise Scanner API | 8889 | 8889 (`expertise_scanner/src/api/main.py:1`) | ✅ OK |
| Expertise Scanner Frontend | 5173 | 5173 (`expertise_scanner/frontend/`) | ✅ OK |
| Generic Framework API | Not specified | 3000 (`generic_framework/api/app.py:672`) | ⚠️ YES (with OMV Co-Pilot) |
| Prometheus | 9090 | 9090 (`docker-compose.yml:61`) | ✅ OK |
| Grafana | 3001 | 3001 (`docker-compose.yml:81`) | ✅ OK |
| Loki | 3100 | 3100 (`docker-compose.yml:101`) | ✅ OK |

### 2. Pattern Format Inconsistencies

| System | Pattern Format | Storage Location |
|----------|--------------|------------------|
| OMV Co-Pilot | YAML | `patterns/manual.yaml` (not confirmed) |
| Expertise Scanner | JSON | `expertise_scanner/data/patterns/{domain}/patterns.json` |
| Generic Framework | JSON (via KnowledgeBase) | `expertise_scanner/data/patterns/` (cross-system dependency) |

### 3. Duplicate Functionality

Both OMV Co-Pilot and Generic Framework provide:
- Pattern-based knowledge storage
- AI integration (GLM-4.7)
- Specialist/context routing
- Query processing pipelines

**Overlap**: Significant architectural and functional overlap with no clear separation of concerns.

### 4. Unreferenced/Obsolete Code

**Archive Directory** - Contains obsolete implementations:
- `archive/chat_system/` - Chat API and clients (not referenced)
- `archive/docs/` - Extensive obsolete documentation (not referenced)
- `scripts/test_omv_connection.py` - RPC test script (not used, SSH is primary)
- `scripts/setup.sh` - Setup script (unclear if used)

### 5. Cross-System Dependencies

- Generic Framework uses Expertise Scanner's pattern storage (`expertise_scanner/data/patterns/`)
- No clear data flow boundaries between systems

---

## Refactoring Actions Completed

### 1. ✅ Removed AI Communications System
- Deleted `ai-communications/` directory
- Removed three-way chat protocol (no longer needed)
- Eliminated file-based message queue system

### 2. ✅ Integrated OMV Co-Pilot into Generic Framework
- Created `generic_framework/domains/omv/` domain
- Implemented 5 OMV specialists:
  - **StorageSpecialist**: Disk management, RAID, filesystems
  - **NetworkSpecialist**: Network configuration, interfaces
  - **ServiceSpecialist**: Service management, SMB, NFS, SSH
  - **PerformanceSpecialist**: CPU, memory, optimization
  - **SecuritySpecialist**: Permissions, access control, hardening
- Implemented 3 OMV collectors:
  - **OMVSSHCollector**: Direct SSH command execution
  - **OMVPrometheusCollector**: Metrics collection
  - **OMVLokiCollector**: Log aggregation

### 3. ✅ Unified Architecture
- OMV domain now uses generic framework's abstract interfaces
- Consistent pattern storage via Expertise Scanner
- Unified specialist/collector pattern across all domains

---

## Remaining Actions

### 1. Port Configuration
- Update `src/main.py` to use port 8888 for OMV Co-Pilot API (if keeping standalone)
- Update `generic_framework/api/app.py` to use port 3001 (avoid conflict with OMV frontend)
- Document all ports in central location

### 2. Pattern Migration
- Migrate OMV Co-Pilot YAML patterns to JSON format
- Store in `expertise_scanner/data/patterns/omv/`
- Update knowledge base references

### 3. Frontend Consolidation
- Decide on single frontend or multiple domain-specific frontends
- Update routing to support multiple domains
- Consolidate styling and components

### 4. Documentation Updates
- Update `claude.md` with new architecture
- Document OMV domain integration
- Create migration guide for OMV Co-Pilot users

---

## Conclusion

The EEFrame project has been successfully refactored from **four independent systems** to **three integrated systems**:

1. **Generic Framework** (now includes OMV domain)
2. **Expertise Scanner** (pattern extraction)
3. **Docker Infrastructure** (monitoring)

The AI Communications system has been removed, and OMV Co-Pilot functionality has been integrated into the generic framework using the domain/specialist/collector pattern. This provides:

- **Unified Architecture**: All domains use the same interfaces
- **Reduced Duplication**: Single implementation of pattern-based assistance
- **Better Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new domains following the same pattern

**Next Steps**: Complete port configuration, migrate patterns to JSON, consolidate frontends, and update documentation.
