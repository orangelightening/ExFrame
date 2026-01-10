# EEFrame System Architecture

**Purpose**: High-level architectural overview of the refactored EEFrame system.

**Last Updated**: 2026-01-08
**Status**: Refactored - OMV integrated into Generic Framework, AI Communications removed
**Version**: 3.0.0

---

## Overview

EEFrame is now a unified framework consisting of three integrated systems:

1. **Generic Framework**: Domain-agnostic assistant with pluggable domains (including OMV)
2. **Expertise Scanner**: Pattern extraction and knowledge graph system for any domain
3. **Docker Infrastructure**: Monitoring stack (Prometheus, Grafana, Loki)

The systems share philosophical alignment around pattern-based knowledge representation and unified architecture patterns.

---

## Generic Framework Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                           │
│  • Web Dashboards (domain-specific)                          │
│  • CLI Tools (domain-specific)                               │
│  • REST APIs (unified)                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              FastAPI (port 3001)                             │
│  • Domain management and routing                             │
│  • Specialist selection and execution                        │
│  • Pattern matching and confidence scoring                   │
│  • Unified knowledge base interface                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
┌───────▼──────┐ ┌──▼───────┐ ┌──▼────────┐ ┌──▼──────────┐
│  Collectors  │ │Knowledge │ │  GLM-4.7  │ │   Domains   │
│ (SSH, HTTP,  │ │  Base    │ │ (AI)      │ │ (OMV,       │
│  Prometheus) │ │ (JSON)   │ │           │ │  Cooking,   │
└──────────────┘ └──────────┘ └───────────┘ │  LLM, ...)  │
                                             └─────────────┘
```

### Core Components

#### 1. Domain Layer
- **Abstract Domain Interface**: Base class for all domains
- **OMV Domain**: Server management with 5 specialists
- **Cooking Domain**: Recipe and cooking expertise
- **LLM Consciousness Domain**: AI consciousness exploration
- **Extensible**: Easy to add new domains

#### 2. Specialist Layer
- **Abstract Specialist Interface**: Base class for domain experts
- **OMV Specialists**: Storage, Network, Service, Performance, Security
- **Specialist Selection**: Query-based routing to best specialist
- **Confidence Scoring**: 0-1 reliability metrics

#### 3. Collector Layer
- **Abstract Collector Interface**: Base class for data sources
- **OMV Collectors**: SSH (commands), Prometheus (metrics), Loki (logs)
- **Pluggable**: Easy to add new data sources
- **Async Support**: Non-blocking data collection

#### 4. Knowledge Base Layer
- **Abstract KnowledgeBase Interface**: Unified pattern storage
- **JSON Storage**: File-based pattern persistence
- **Pattern Matching**: Similarity search and scoring
- **Relationship Tracking**: Related patterns, prerequisites, alternatives

#### 5. AI Integration Layer
- **LLM Provider**: GLM-4.7 via international endpoint
- **Prompt Engineering**: Context-specific prompts per specialist
- **Response Formatting**: Structured JSON with confidence scores
- **Error Handling**: Graceful degradation on API failures

### Data Flow

```
User Query → Domain Selection → Specialist Selection → Context Collection →
Pattern Matching → Confidence Calculation → Prompt Building → LLM Generation →
Response Assembly → User Response
```

**Specialist Selection**: Automatic routing based on query keywords and expertise areas.

---

## Expertise Scanner Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  • React Frontend (port 5173)                               │
│  • 4 main pages: Patterns, Domains, Ingestion, Batch        │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│                 FASTAPI BACKEND (port 8889)                   │
│  • Pattern CRUD operations                                   │
│  • Ingestion pipeline (URL, text, JSON, batch)               │
│  • Knowledge graph management                                │
└─────────────────────┬────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────────┐
        │             │             │                  │
┌───────▼──────┐ ┌───▼────────┐ ┌─▼───────────┐ ┌────▼─────────┐
│   INGESTION   │ │ PATTERN    │ │ KNOWLEDGE   │ │   STORAGE    │
│   PIPELINE    │ │ EXTRACTION │ │   GRAPH     │ │   LAYER      │
│ (URL, text,   │ │ (Rule-based│ │ (JSON-based)│ │ (JSON files) │
│  JSON, batch) │ │  or LLM)   │ │             │ │              │
└───────────────┘ └────────────┘ └─────────────┘ └──────────────┘
        │
        ▼
┌─────────────────┐
│   DATA SOURCES  │
│  • AI Inbox     │  (Primary: GLM-4.7 generated JSON)
│  • URLs         │  (Secondary: web scraping)
│  • Manual input │  (Tertiary: form-based)
└─────────────────┘
```

### Core Components

#### 1. Pattern Data Model
- **Domain-based IDs**: `{domain}_{number:03d}` (e.g., `cooking_001`)
- **Rich Structure**: Problem, solution, steps, conditions, relationships
- **Relationships**: Related patterns, prerequisites, alternatives
- **Confidence**: 0-1 reliability score with user rating support

#### 2. Ingestion Pipeline
- **Primary Source**: AI-generated JSON files (GLM-4.7 → inbox → patterns)
- **Secondary Source**: Web scraping (deprioritized due to quality issues)
- **Manual Creation**: Full-featured form for synthetic/test patterns
- **Batch Processing**: Real-time progress tracking for large ingestions

#### 3. Storage Layer
- **Pattern Storage**: JSON files per domain in `data/patterns/{domain}/`
- **Knowledge Graph**: JSON-based graph structure in `data/knowledge_graph/`
- **AI Inbox**: Directory at `/home/peter/development/eeframe/pattern-inbox/`

#### 4. Knowledge Graph
- **Nodes**: Patterns with rich metadata
- **Edges**: Relationships (related, prerequisites, alternatives)
- **Cross-Domain**: Basic structure for connecting patterns across domains
- **Status**: Implemented but not fully utilized in main workflow

#### 5. User Interface Layer
- **Web Frontend**: React + Vite on port 5173 with Tailwind CSS v3
- **API**: FastAPI on port 8889 with OpenAPI documentation
- **Pages**: Pattern browser, domain overview, ingestion forms, batch processing

### Data Flow

```
       ┌─────────────┐
       │   INPUT     │
       │   SOURCES   │
       └─────┬───────┘
             │
   ┌─────────┼─────────┐
   │         │         │
┌──▼──┐  ┌──▼──┐  ┌──▼──┐
│ AI  │  │ Web │  │Manual│
│Inbox│  │Scrape│  │Form │
└──┬──┘  └──┬──┘  └──┬──┘
   │        │        │
   └────────┼────────┘
            │
      ┌─────▼─────┐
      │EXTRACTION │
      │  LAYER    │
      └─────┬─────┘
            │
      ┌─────▼─────┐
      │  STORAGE  │
      │  LAYER    │
      └─────┬─────┘
            │
      ┌─────▼─────┐
      │KNOWLEDGE  │
      │  GRAPH    │
      └───────────┘
```

**Philosophy**: Domain experts configure their own domains; system provides general pattern extraction tools.

---

## Shared Architectural Principles

### 1. Pattern-Based Knowledge Representation
Both systems use structured patterns, though with different formats:
- **OMV Co-Pilot**: Symptom/diagnostic/solution patterns for troubleshooting
- **Expertise Scanner**: General problem/solution patterns for any domain

### 2. AI Integration Strategy
- **Primary LLM**: GLM-4.7 via international endpoint
- **Fallback Strategy**: Error handling for API failures
- **Prompt Engineering**: Contextual prompts for different use cases

### 3. Data Persistence
- **Simple Storage**: JSON/YAML files instead of complex databases
- **Recovery**: State persistence for interrupted operations
- **Backup**: File-based storage allows easy backup/version control

### 4. User Interface Consistency
- **React + Vite**: Both frontends use same technology stack
- **Tailwind CSS**: Consistent styling (v3 for Expertise Scanner, latest for OMV)
- **API-First**: Clear separation between frontend and backend

### 5. Development Philosophy
- **Pragmatic Over Perfect**: Working software over theoretical purity
- **Incremental Enhancement**: Add features based on real usage
- **Clear Value Proposition**: Solve immediate problems vs. abstract enhancement

---

## System Integration Points

### Current Integration
- **Unified Architecture**: Generic Framework provides base for all domains
- **Shared Concepts**: Pattern-based knowledge representation
- **Common Interfaces**: Domain, Specialist, Collector, KnowledgeBase
- **Pattern Sharing**: Expertise Scanner provides patterns for all domains

### Technical Compatibility
- **Python Backends**: All use FastAPI with async/await
- **React Frontends**: Consistent technology stack (Vite, Tailwind CSS)
- **Configuration**: Unified environment variable patterns
- **Development**: Common virtual environment approach
- **Deployment**: Docker Compose for monitoring stack

### Data Model Alignment
All systems support:
- **Unique Identifiers**: Pattern IDs for reference
- **Confidence Scoring**: 0-1 reliability metrics
- **Relationship Mapping**: Connections between patterns
- **Metadata**: Sources, timestamps, usage tracking
- **JSON Storage**: File-based persistence for portability

---

## Deployment Architecture

### Development Environment
```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT WORKSTATION                   │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ Generic Framework│  │  Expertise       │  │   OMV      │ │
│  │   Ports:         │  │   Scanner        │  │   Server   │ │
│  │   3001 (API)     │  │   Ports:         │  │   192.168. │ │
│  │                  │  │   8889 (API)     │  │    3.68:22 │ │
│  │ Domains:         │  │   5173 (UI)      │  │            │ │
│  │ • OMV            │  │                  │  │            │ │
│  │ • Cooking        │  │ Domains:         │  │            │ │
│  │ • LLM Conscious  │  │ • cooking        │  │            │ │
│  └──────────────────┘  │ • python         │  └────────────┘ │
│                        │ • omv            │                  │
│  ┌──────────────────┐  │ • diy            │                  │
│  │ Docker Stack     │  │ • first_aid      │                  │
│  │ Ports:           │  │ • gardening      │                  │
│  │ • 9090 (Prom)    │  └──────────────────┘                  │
│  │ • 3001 (Grafana) │                                        │
│  │ • 3100 (Loki)    │                                        │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

### Network Configuration
- **Generic Framework**: Localhost only (development)
- **Expertise Scanner**: Localhost only (development)
- **Docker Stack**: Localhost only (development)
- **OMV Server**: SSH access via local network (192.168.3.68)
- **GLM API**: External HTTPS endpoint (api.z.ai)

### Resource Requirements
- **Memory**: ~1GB total for all services (development)
- **CPU**: Minimal for API servers, moderate for LLM calls
- **Storage**: <200MB for patterns and data
- **Network**: Internet access for GLM API calls

---

## Security Architecture

### Authentication & Authorization
- **Current**: None (development/local use only)
- **Future Consideration**: API keys for production deployment

### Data Security
- **OMV Credentials**: Stored in `.env` file (not in version control)
- **API Keys**: Environment variables for LLM access
- **SSH Connection**: Password-based (consider key-based for production)

### Network Security
- **Local Development**: All services bind to localhost
- **SSH**: Encrypted connection to OMV server
- **HTTPS**: All external API calls use HTTPS (GLM API)

### Privacy Considerations
- **OMV Data**: System information collected via SSH (no personal data)
- **Pattern Data**: Public domain knowledge (recipes, troubleshooting)
- **User Queries**: May contain sensitive system information (logged in traces)

---

## Monitoring & Observability

### Current Monitoring
- **Execution Tracing**: OMV Co-Pilot tracks 10 decision points with timing
- **API Health**: Basic endpoint availability
- **Error Logging**: Application logs to stdout

### Future Enhancement Areas
- **Metrics Collection**: Prometheus integration for system metrics
- **Log Aggregation**: Loki for centralized log management
- **Alerting**: Smart alerts based on system state
- **Performance Tracing**: Distributed tracing for complex workflows

---

## Scalability Considerations

### Current Scale (Development)
- **OMV Co-Pilot**: Single OMV server, ~24 patterns
- **Expertise Scanner**: 6 domains, ~14 patterns
- **Users**: Single developer/local use

### Scaling Paths
1. **Vertical Scaling**: More memory/CPU for current architecture
2. **Horizontal Scaling**: Multiple instances with load balancing
3. **Database Migration**: SQLite/PostgreSQL for larger pattern sets
4. **Caching**: Redis for frequent pattern queries
5. **Async Processing**: Celery for long-running ingestion jobs

### Bottleneck Analysis
- **LLM API Calls**: Rate limits and latency (120s timeout configured)
- **SSH Collection**: Sequential commands on OMV server
- **File I/O**: JSON file reads/writes for patterns
- **Memory**: In-memory trace storage

---

## Failure Modes & Recovery

### Known Failure Points
1. **GLM API Unavailable**: Fallback to cached responses or error message
2. **OMV SSH Failure**: Limited functionality (no system context)
3. **File Corruption**: Regular backups of pattern files
4. **Memory Exhaustion**: Trace store cleanup mechanisms

### Recovery Strategies
- **State Persistence**: File-based storage allows restart recovery
- **Graceful Degradation**: Passthrough mode when knowledge base unavailable
- **Incremental Saves**: Batch ingestion saves progress incrementally
- **Validation Scripts**: System validation on startup (Expertise Scanner)

### Disaster Recovery
- **Backup**: Git repository for code, manual backup for data files
- **Restore**: Simple file copy for pattern data
- **Recreation**: Scripts to regenerate test patterns
- **Documentation**: Context recovery file (`claude.md`) for system state

---

## Future Architecture Evolution

### Near-Term Enhancements
1. **Monitoring Stack**: Prometheus/Grafana/Loki integration
2. **Pattern Sharing**: Export/import between systems
3. **Enhanced Graph**: Neo4j migration for complex queries
4. **User Authentication**: Basic auth for web interfaces

### Long-Term Vision
1. **Unified Pattern Format**: Common pattern structure across systems
2. **Federated Knowledge**: Pattern sharing across instances
3. **Plugin Architecture**: Domain-specific extensions
4. **Production Deployment**: Docker Compose, HA configuration

### Architectural Debt
- **Expertise Scanner Scraping**: Deprioritized but code remains
- **Knowledge Graph**: Implemented but underutilized
- **OMV RPC Collection**: Code exists but unused (OMV 7.x restriction)
- **Multiple Pattern Formats**: Different structures for similar concepts

---

## Summary

The EEFrame architecture represents a unified approach to AI-assisted knowledge management:

### Key Principles
- **Unified Framework**: Single architecture for all domains (Generic Framework)
- **Pattern-Based Knowledge**: Structured knowledge representation with relationships
- **Specialist/Collector Pattern**: Extensible architecture for new domains
- **Proven Technology**: FastAPI, React, GLM-4.7, Docker
- **Development Focus**: Working software with clear value

### System Components
1. **Generic Framework**: Domain-agnostic assistant with pluggable domains
   - OMV (Server Management), Cooking, LLM Consciousness, extensible
   - 5 OMV specialists, 3 collectors
   - Unified API on port 3001

2. **Expertise Scanner**: Pattern extraction and knowledge graph
   - 6 domains with patterns
   - AI inbox workflow for pattern generation
   - API on port 8889, UI on port 5173

3. **Docker Infrastructure**: Monitoring and observability
   - Prometheus, Grafana, Loki, Promtail
   - Auto-provisioned dashboards

### Benefits of Refactoring
- **Reduced Duplication**: Single pattern-based pipeline
- **Improved Maintainability**: Clear separation of concerns
- **Better Extensibility**: New domains follow same pattern
- **Unified Architecture**: Consistent interfaces across all domains
- **Simplified Communication**: Direct API calls instead of message queues

The refactored EEFrame demonstrates a cohesive approach to extracting, organizing, and applying knowledge patterns across multiple domains using a unified, extensible architecture.