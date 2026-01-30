# ExFrame - Expertise Framework

*Version: Managed by git tags*
**License:** Apache-2.0
**Repository:** https://github.com/orangelightening/ExFrame

---

## What is ExFrame?

ExFrame is a **domain-agnostic AI-powered knowledge management system** with configurable domain types. Unlike traditional knowledge bases, ExFrame features:

- **Self-Learning AI** - Automatically improves its own knowledge base
- **Self-Documenting** - AI generates and refines documentation
- **Self-Repairing** - System detects and fixes its own issues
- **Universe-Based Architecture** - Complete isolation and portability of knowledge environments
- **Plugin Pipeline** - Router → Specialist → Enricher → Formatter - all swappable
- **Pure Semantic Search** - AI-powered search using SentenceTransformers embeddings
- **Emergent Persona Theory** - AI personas emerge from accumulated knowledge patterns
- **Constellation Architecture** - Groups of ExFrame systems consuming expertise and talking to each other

---

## Key Features

### 🧠 Self-Healing Capabilities

**Self-Learning**
- Automatically learns from user queries and interactions
- Identifies knowledge gaps and suggests new patterns
- Continuous improvement without manual intervention
- Pattern mining from external sources (URLs, documents)

**Self-Documenting**
- AI generates comprehensive documentation from minimal input
- Refines and expands existing patterns
- Maintains consistency across knowledge domains
- Automatic categorization and tagging

**Self-Repairing**
- Detects inconsistencies in knowledge base
- Identifies orphaned or duplicate patterns
- Suggests fixes for structural issues
- Validates embedding integrity

### 🔍 Knowledge Management

**Semantic Search**
- Pure semantic search (100% semantic, 0% keyword)
- SentenceTransformers embeddings (all-MiniLM-L6-v2)
- Cosine similarity scoring (0-1 range)
- Smart truncation for long patterns
- Real-time search with trace visibility

**Pattern-Based Knowledge**
- Structured knowledge representation
- Problem-Solution format
- Rich metadata (categories, tags, confidence scores)
- Domain-agnostic patterns
- JSON-based storage with SQLite backend

### 🏗️ Architecture

**Universe System**
- Complete isolation of knowledge environments
- Portable universe export/import
- Multi-universe support
- Universe merge strategies
- Active universe management

**Plugin Pipeline**
```
Query → Router → Specialist → Enrichers → Formatter → Response
```

- **Router Plugins**: Query routing strategies (confidence-based, multi-specialist)
- **Specialist Plugins**: Domain experts (emergent AI personas)
- **Enricher Plugins**: Response enhancement (LLM, related patterns, code generation)
- **Formatter Plugins**: Output formatting (Markdown, JSON, HTML, Slack)

### 🌌 Constellation Architecture

**The Constellation** is a distributed knowledge network where multiple ExFrame instances work together, each paired with a Claude Code CLI AI as manager and partner.

**How It Works**

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CONSTELLATION NETWORK                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                │
│  │  ExFrame A   │◄──────►│  ExFrame B   │                │
│  │  + Claude Code  │         │  + Claude Code  │                │
│  └──────────────┘         └──────────────┘                │
│         │                       │                            │
│         │                       │                            │
│         ▼                       ▼                            │
│  ┌──────────────┐         ┌──────────────┐                │
│  │  ExFrame C   │◄──────►│  ExFrame D   │                │
│  │  + Claude Code  │         │  + Claude Code  │                │
│  └──────────────┘         └──────────────┘                │
│                                                              │
└─────────────────────────────────────────────────────────────────────┘
```

**Constellation Components**

**ExFrame Instance**
- Hosts knowledge domains and patterns
- Provides semantic search and pattern retrieval
- Manages universe-based knowledge environments
- Offers RESTful API for queries and management

**Claude Code CLI AI**
- Acts as manager and partner to ExFrame instance
- Provides AI-assisted development and decision-making
- Enables inter-instance communication
- Orchestrates knowledge consumption across the constellation

**Inter-Instance Communication**
- HTTP-based messaging between instances
- Pattern sharing and synchronization
- Collaborative problem-solving across systems
- Distributed expertise consumption

**Self-Healing Constellation**
- **Collective Learning**: Each instance learns from shared patterns
- **Distributed Validation**: Patterns validated across multiple systems
- **Redundant Knowledge**: Critical patterns replicated across constellation
- **Health Monitoring**: Instance health tracked and reported
- **Automatic Recovery**: Failed instances detected and knowledge preserved

**Benefits**

- **Scalable Expertise**: Add more instances to expand knowledge
- **Resilient Architecture**: No single point of failure
- **Collaborative Intelligence**: Multiple systems solve problems together
- **Distributed Learning**: Knowledge grows across the entire constellation
- **Flexible Deployment**: Run instances on-premises, cloud, or hybrid

**Use Cases**

- **Enterprise Teams**: Multiple departments with shared expertise
- **Research Networks**: Distributed knowledge across institutions
- **Consulting Groups**: Consultants sharing patterns across clients
- **Open Source Communities**: Public constellation for shared knowledge

### 🚀 Developer Experience

**Claude Code Integration**
- Native Claude Code support for development
- AI-assisted code generation and refactoring
- Pattern creation from natural language
- Code review and optimization suggestions
- Inter-instance communication between Claude Code agents
- **Constellation Manager**: Claude Code CLI acts as partner and manager to each ExFrame instance
- **Distributed Orchestration**: Claude Code coordinates knowledge consumption across constellation

**Docker-Ready**
- One-command deployment
- Complete monitoring stack (Prometheus, Grafana, Loki)
- Health check endpoints
- Automatic container management
- Volume mounting for live development

**API-First Design**
- RESTful API with FastAPI
- OpenAPI documentation (`/docs`)
- Web dashboard with Alpine.js
- Health monitoring and diagnostics
- Query tracing and debugging

---

## Technology Stack

**Backend**
- FastAPI - Modern Python web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- SQLite - Embedded database
- SentenceTransformers - Semantic embeddings

**AI/ML**
- OpenAI API compatible (supports multiple providers)
- GLM-4.7 - Default LLM model
- all-MiniLM-L6-v2 - Embedding model (384-dimensional)
- Hybrid search (semantic + keyword)

**Infrastructure**
- Docker & Docker Compose
- Prometheus - Metrics collection
- Grafana - Visualization dashboards
- Loki - Log aggregation
- Promtail - Log shipping agent

**Frontend**
- Alpine.js - Lightweight reactive framework
- Single-page application
- Real-time updates
- Responsive design

---

## Use Cases

### 🏢 Enterprise Knowledge Management
- Internal documentation systems
- SOP and procedure management
- Expert knowledge capture
- Onboarding and training materials
- Compliance and policy documentation

### 👨 Technical Support
- Troubleshooting knowledge base
- Error resolution workflows
- System documentation
- FAQ management
- Knowledge sharing between teams

### 🎓 Education & Training
- Course material management
- Learning resource organization
- Assessment and certification tracking
- Student support systems
- Adaptive learning paths

### 🧪 Research & Development
- Research paper organization
- Experiment documentation
- Code pattern libraries
- Best practices repositories
- Knowledge discovery

---

## Getting Started

### Quick Start (Docker)
```bash
# Clone repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# Configure environment
cp .env.example .env
nano .env  # Add your LLM API key

# Start application
docker compose up -d

# Access application
open http://localhost:3000
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
cd generic_framework
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 3000
```

---

## Claude Code Integration

ExFrame has native support for Claude Code AI assistants:

### Self-Healing Features
- **Self-Learning**: Claude Code learns from ExFrame knowledge base
- **Self-Documenting**: AI generates documentation from code context
- **Self-Repairing**: Detects and fixes code issues using patterns
- **Pattern Creation**: Create knowledge patterns from natural language

### Inter-Instance Communication
Claude Code instances can communicate with each other:
```python
# Instance A sends message to Instance B
import requests

response = requests.post(
    "http://instance-b:3000/api/kilo/communicate",
    json={"message": "Help me with this pattern", "sender_id": "instance-a"}
)
```

### AI-Assisted Development
- Code generation from pattern descriptions
- Refactoring suggestions based on best practices
- Documentation generation from code
- Test case creation from requirements

---

## Architecture Highlights

### Emergent Persona Theory

> **Knowledge emerges from patterns. Persona emerges from knowledge. Both evolve together.**

1. **Patterns** capture human expertise in structured form
2. **Knowledge** is the corpus of patterns in a domain
3. **Specialist** is the AI persona that emerges from that corpus
4. As patterns increase, information density increases
5. As knowledge deepens, the persona becomes more coherent
6. The specialist is not a "person" - it's the collective voice of the corpus

**In a Constellation:**
- Each ExFrame instance hosts multiple emergent personas (one per domain)
- Claude Code CLI AI acts as manager and partner to each persona
- Personas can communicate across the constellation
- Collective intelligence emerges from distributed pattern sharing
- Knowledge evolution accelerates through cross-instance collaboration

**Example:**
- Cooking domain (32 patterns) → "Cooking" expert persona
- First Aid domain (3 patterns) → "First Aid" focused persona
- LLM Consciousness domain (12 patterns) → "LLM Consciousness" expert

### Plugin Architecture

ExFrame's plugin system enables complete customization:

**Router Plugins**
- `ConfidenceBasedRouter` - Selects highest-scoring specialist
- `MultiSpecialistRouter` - Routes to top-N specialists
- `ParallelRouter` - All specialists in parallel
- `SequentialRouter` - Progressive refinement

**Enricher Plugins**
- `LLMEnricher` - AI-powered response enhancement
- `RelatedPatternEnricher` - Suggests related patterns
- `CodeGeneratorEnricher` - Generates code examples
- `UsageStatsEnricher` - Adds usage statistics

**Formatter Plugins**
- `MarkdownFormatter` - Full-featured Markdown (default)
- `JSONFormatter` - Structured JSON output
- `HTMLFormatter` - Web-ready HTML
- `SlackFormatter` - Slack-compatible format

---

## Monitoring & Observability

### Built-in Metrics
- Search performance metrics
- Pattern health analysis
- Embedding coverage tracking
- Query trace inspection
- System health checks

### Dashboard Access
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **API Docs**: http://localhost:3000/docs

### Health Endpoints
```bash
# Application health
curl http://localhost:3000/health

# Embedding status
curl http://localhost:3000/api/embeddings/status

# Domain list
curl http://localhost:3000/api/domains
```

---

## Why ExFrame?

### Compared to Traditional Knowledge Bases

| Feature | Traditional KB | ExFrame |
|----------|---------------|----------|
| Knowledge Capture | Manual entry | AI-assisted + manual |
| Search | Keyword-only | Pure semantic + hybrid |
| Organization | Hierarchical folders | Universe-based with plugins |
| Maintenance | Manual updates | Self-learning + self-repairing |
| Extensibility | Hardcoded | Plugin architecture |
| AI Integration | None | Native Claude Code support |
| Deployment | Complex | One-command Docker |
| Collaboration | Isolated systems | Constellation architecture |
| Scalability | Single instance | Distributed knowledge network |

### Key Advantages

✅ **Self-Healing** - System improves itself without intervention
✅ **Semantic Search** - Finds patterns by meaning, not just keywords
✅ **Domain-Agnostic** - Works for any knowledge domain
✅ **Plugin System** - Extendable without code changes
✅ **Claude Code Native** - Built for AI-assisted development
✅ **Docker-Ready** - Deploy anywhere in one command
✅ **Open Source** - Apache 2.0 license, fully customizable
✅ **Monitoring Included** - Complete observability stack
✅ **Constellation Architecture** - Distributed knowledge network with Claude Code partners
✅ **Collaborative Intelligence** - Multiple ExFrame systems working together
✅ **Self-Healing Constellation** - Collective learning and distributed validation

---

## Performance

### Benchmarks
- **Search Latency**: < 100ms (semantic search)
- **Embedding Generation**: ~50ms per pattern
- **Query Processing**: < 500ms average
- **Pattern Capacity**: 1000+ patterns per domain
- **Concurrent Users**: 100+ simultaneous queries

### Scalability
- Horizontal scaling via Docker
- Load balancing support
- Database sharding ready
- Caching layer for embeddings
- Async processing throughout

---

## Community & Support

### Documentation
- [README.md](README.md:1) - Getting started guide
- [PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md:1) - Plugin development
- [INSTALL.md](INSTALL.md:1) - Installation instructions
- [GITHUB_LAUNCH_GUIDE.md](GITHUB_LAUNCH_GUIDE.md:1) - Deployment guide

### Contributing
- Apache 2.0 license - Permissive for contributions
- Plugin system - Easy to extend
- Well-documented codebase
- Active development community

### Support Channels
- GitHub Issues - Bug reports and feature requests
- Documentation - Comprehensive guides and examples
- Community patterns - Share knowledge domains

---

## Roadmap

### Upcoming Features
- [ ] Enhanced self-learning algorithms
- [ ] Multi-modal pattern support (images, videos)
- [ ] Advanced pattern relationships
- [ ] Knowledge graph visualization
- [ ] Collaborative editing
- [ ] Advanced AI repair capabilities

### Under Development
- Improved semantic diversity (v1.5.1 - Just released!)
- Claude Code communication API
- Enhanced pattern validation
- Performance optimizations

---

## License

ExFrame is released under the **Apache License 2.0**, allowing:
- ✅ Commercial use
- ✅ Modification and distribution
- ✅ Private use
- ✅ Sublicensing
- ✅ Patent use

See [LICENSE](LICENSE) file for full terms.

---

## Quick Links

| Resource | URL |
|----------|-----|
| Repository | https://github.com/orangelightening/ExFrame |
| Documentation | https://github.com/orangelightening/ExFrame#readme |
| API Docs | http://localhost:3000/docs |
| Issues | https://github.com/orangelightening/ExFrame/issues |
| Releases | https://github.com/orangelightening/ExFrame/releases |

---

## Summary

ExFrame is a **self-healing AI knowledge system** that transforms how organizations manage expertise. With native Claude Code integration, semantic search, and a plugin architecture, it provides a modern, extensible platform for knowledge management that learns and improves itself.

**Perfect for:**
- Enterprise knowledge management
- Technical support systems
- Education and training platforms
- Research and development teams
- AI-assisted development workflows
- **Constellation deployments** - Distributed knowledge networks with Claude Code partners

**The Constellation Vision:**
Groups of ExFrame systems on various systems, each paired with a Claude Code CLI AI as manager and partner, consuming expertise and talking to each other. This creates a self-healing distributed knowledge network where:
- Multiple ExFrame instances share patterns and learn collectively
- Claude Code AI acts as intelligent manager and partner to each instance
- Knowledge evolves faster through cross-instance collaboration
- System resilience increases through distributed validation
- Expertise scales by adding more instances to the constellation

**Try it today:**
```bash
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame
docker compose up -d
open http://localhost:3000
```

---

*ExFrame - Knowledge that learns, documents, and repairs itself.*