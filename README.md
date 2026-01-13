# EEFrame - Expertise Framework

**Domain-Agnostic AI-Powered Knowledge Management System**

Version 1.3.0 - Universe Architecture & Diagnostics Release

---

## Overview

EEFrame is a unified, domain-agnostic framework for building AI-powered knowledge assistants with a **universe-based architecture** and **plugin-based pipeline**. It provides:

- **Universe Architecture**: Complete isolation and portability of knowledge configurations
- **Plugin Pipeline**: Router → Specialist → Enricher → Formatter - all swappable
- **Domain-Agnostic**: Easy to add new knowledge domains without code changes
- **Pattern-Based Knowledge**: Structured knowledge representation with relationships and metadata
- **Dynamic Domain Loading**: Auto-discovery of domains within active universe
- **Generic Domain System**: Universal domain class with plugin loading
- **Multi-Universe Support**: Create, switch, merge, and export knowledge universes
- **Diagnostics System**: Search metrics, pattern health analysis, self-testing
- **Query Tracing**: Full visibility into AI decision-making process
- **Docker Ready**: One-command deployment with monitoring stack
- **Web Dashboard**: Single-page application with Alpine.js

### Core Philosophy

> **Universes are first-class entities. Patterns are data. All transformation logic is pluggable.**

- ✅ **Universes** are complete, portable knowledge environments
- ✅ **Patterns** are data (JSON files in universe directories)
- ✅ **Domains** are orchestrators (configuration within universes)
- ✅ **Routers** determine query handling strategies
- ✅ **Specialists** are plugins (transformation logic)
- ✅ **Enrichers** enhance responses (LLM, related patterns, code generation)
- ✅ **Formatters** control output format (Markdown, JSON, HTML, Slack)

### Key Features

- **Universe Management**: Create, load, switch, merge, and export knowledge universes
- **Plugin Architecture**: Router, Specialist, Enricher, and Formatter plugins for extensibility
- **Domain Management**: Create and manage knowledge domains through the web UI
- **Pattern Browser**: View and search patterns with full detail modals
- **Query Assistant**: AI-powered assistance with confidence scoring
- **Trace Inspector**: Debug and understand AI behavior
- **Pattern Ingestion**: Extract knowledge from URLs and documents
- **Diagnostics Dashboard**: System health, search metrics, and pattern analysis
- **Health Monitoring**: Built-in Prometheus metrics and Grafana dashboards
- **Self-Testing**: Automated test suite with regression detection

---

## Plugin Architecture

EEFrame v1.3.0 features a complete pluggable pipeline that separates **data** (patterns) from **transformation logic** (plugins).

### Pipeline Overview

```
Query → Router → Specialist → Enrichers → Formatter → Response
```

### Plugin Types

#### 1. Router Plugins

Router plugins determine which specialist(s) should handle a query.

**Available Routers:**
- `ConfidenceBasedRouter` - Selects highest-scoring specialist
- `MultiSpecialistRouter` - Routes to top-N specialists
- `ParallelRouter` - All specialists in parallel

#### 2. Specialist Plugins

Specialist plugins answer questions in specific domain areas.

**Interface**:
```python
from core.specialist_plugin import SpecialistPlugin

class MySpecialist(SpecialistPlugin):
    name = "My Specialist"
    specialist_id = "my_specialist"

    def can_handle(self, query: str) -> float:
        """Return confidence score 0.0 to 1.0"""
        pass

    async def process_query(self, query: str, context: Dict = None) -> Dict:
        """Process query and return response data"""
        pass

    def format_response(self, response_data: Dict) -> str:
        """Format response for user display"""
        pass
```

**Included Specialists**:
- `BitwiseMasterPlugin` - Binary and bitwise operations
- `PatternAnalystPlugin` - Binary pattern detection
- `AlgorithmExplorerPlugin` - Bitwise algorithms
- `FailureDetectionPlugin` - LLM failure mode detection
- `MonitoringPlugin` - System architecture patterns
- `GeneralistPlugin` - Fallback for unmatched queries

#### 2. Knowledge Base Plugins

Knowledge base plugins store and retrieve patterns.

**Interface**:
```python
from core.knowledge_base_plugin import KnowledgeBasePlugin

class MyKnowledgeBase(KnowledgeBasePlugin):
    name = "My Knowledge Base"

    async def load_patterns(self) -> None:
        """Load patterns from storage"""
        pass

    async def search(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Search for matching patterns"""
        pass

    async def get_by_id(self, pattern_id: str) -> Optional[Dict]:
        """Get pattern by ID"""
        pass

    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        pass

    def get_pattern_count(self) -> int:
        """Get total pattern count"""
        pass
```

**Included Implementations**:
- `JSONKnowledgeBase` - File-based storage (default)
- `SQLiteKnowledgeBase` - SQLite with FTS5 full-text search

### Adding Plugins

Plugins are configured in `data/patterns/{domain}/domain.json`:

```json
{
  "plugins": [
    {
      "plugin_id": "my_specialist",
      "name": "My Specialist",
      "module": "plugins.my_domain.my_specialist",
      "class": "MySpecialistPlugin",
      "enabled": true,
      "config": {
        "keywords": ["keyword1", "keyword2"],
        "categories": ["category1"],
        "threshold": 0.30
      }
    }
  ]
}
```

### For More Information

See [PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md) for:
- Detailed plugin interface documentation
- Example implementations
- Adding new domains with plugins
- Testing and troubleshooting plugins

---

## Quick Start

### Prerequisites

**IMPORTANT**: You must use the official Docker Engine. The snap version of Docker has known issues with bind mounts that will prevent this application from working correctly.

Check your Docker installation:
```bash
# Check if you have snap Docker (BAD - will not work properly)
which snap | grep -q docker && snap list docker

# If snap Docker is installed, remove it first:
sudo snap remove docker

# Install official Docker Engine:
curl -fsSL https://get.docker.com | sh

# Add your user to docker group:
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

**Additional Requirements:**
- OpenAI API key (or compatible LLM like GLM) - optional, for LLM enrichment features

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# 2. Configure environment (REQUIRED for LLM features)
cp .env.example .env

# Edit .env with your API credentials
# For OpenAI:
#   - Set OPENAI_API_KEY=your-openai-api-key
#   - Leave OPENAI_BASE_URL as is (or remove to use default)
#
# For GLM (z.ai):
#   - Set OPENAI_API_KEY=your-glm-api-key
#   - Set OPENAI_BASE_URL=https://api.z.ai/api/anthropic
#
# For Anthropic Claude:
#   - Set OPENAI_API_KEY=your-anthropic-api-key
#   - Set OPENAI_BASE_URL=https://api.anthropic.com/v1
#
nano .env  # or use your preferred editor

# 3. Start the application
# NOTE: Use "docker compose" (space), NOT "docker-compose" (hyphen)
docker compose up -d

# 4. Verify containers are running
docker compose ps

# 5. Check the logs if needed
docker compose logs -f eeframe-app
```

**Access URLs**:
- **EEFrame UI**: `http://localhost:3000` (main application)
- **API Docs**: `http://localhost:3000/docs` (Swagger UI)
- **Health Check**: `http://localhost:3000/health`
- **Prometheus**: `http://localhost:9090` (metrics)
- **Grafana**: `http://localhost:3001` (dashboards, admin/admin)
- **Loki**: `http://localhost:3100` (logs)

---

## Web Interface

### Navigation Tabs

1. **Assistant**: Query the AI assistant with pattern-based knowledge
2. **Patterns**: Browse and search knowledge patterns with full detail views
3. **Traces**: View historical query traces and debugging information
4. **Ingestion**: Extract patterns from URLs (beta)
5. **Domains**: Manage domains, specialists, and configuration
6. **Universes**: Manage knowledge universes - create, load, switch, and export
7. **Diagnostics**: System health, search metrics, and pattern analysis

### Using the Assistant

1. Select a domain from the dropdown (default: llm_consciousness)
2. The current universe is displayed next to "Universe:"
3. Type your question in the text area
4. Click "Query" or press Enter
5. View the AI response with:
   - Confidence score
   - Which specialist handled it
   - Patterns used
   - Processing time
   - Optional trace (enable "Include Trace" checkbox)

### Viewing Pattern Details

1. Go to the **Patterns** tab
2. Select a domain from the dropdown
3. Browse the pattern cards
4. **Click on any pattern** to see full details:
   - Problem addressed
   - Solution steps
   - Conditions and prerequisites
   - Related patterns
   - Tags and metadata
   - Access statistics

### Managing Domains

1. Go to the **Domains** tab
2. View all configured domains with:
   - Pattern counts
   - Specialist listings
   - Categories and tags
   - Load status
3. Click **Create Domain** to add a new domain
4. Click **Edit** (pencil icon) to modify a domain

### Managing Universes

1. Go to the **Universes** tab
2. View current universe with:
   - Universe name and active status
   - Total domains and patterns
3. Browse available universes with:
   - Domain and pattern counts
   - Active status indicators
   - Switch and Details buttons
4. Create new universes with:
   - Universe ID
   - Optional description
5. Switch between universes instantly

### Using Diagnostics

1. Go to the **Diagnostics** tab
2. Click **Load Diagnostics** to refresh
3. View system health:
   - Pattern storage status
   - Knowledge base health
   - Search performance metrics
   - Disk space usage
   - Pattern health scores
4. Review search metrics:
   - Total searches and success rate
   - Average confidence and latency
   - P50/P95/P99 duration percentiles
   - LLM fallback rate

---

## System Architecture

### Single-Container Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    eeframe-app (Port 3000)                  │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Backend                                          │
│  ├── Domain Management (cooking, llm_consciousness)       │
│  ├── Specialist Engine (pattern matching)                   │
│  ├── Knowledge Base (JSON patterns)                        │
│  ├── Query Processing (LLM integration)                    │
│  └── Static Frontend (Alpine.js + Tailwind)                │
├─────────────────────────────────────────────────────────────┤
│  Data Persistence (Bind Mounts)                            │
│  ├── ./data/patterns → /app/data/patterns                  │
│  └── ./data/domains.json → /app/data (via API)            │
└─────────────────────────────────────────────────────────────┘
```

### Monitoring Stack (Optional)

- **Prometheus** (9090): Metrics collection
- **Grafana** (3001): Visualization dashboards
- **Loki** (3100): Log aggregation
- **Promtail**: Log shipping agent

---

## Project Structure

```
eeframe/
├── generic_framework/          # Main framework
│   ├── api/                    # FastAPI application
│   │   └── app.py             # Main app with all endpoints
│   ├── core/                   # Core interfaces
│   │   ├── domain.py          # Domain base class
│   │   ├── specialist.py      # Specialist base class
│   │   └── knowledge_base.py  # Knowledge base interface
│   ├── domains/                # Domain implementations
│   │   ├── cooking/           # Cooking domain
│   │   └── llm_consciousness/ # LLM consciousness domain
│   ├── assist/                 # Assistant engine
│   │   └── engine.py          # Query orchestration
│   ├── knowledge/              # Knowledge base implementations
│   │   └── json_kb.py         # JSON-based knowledge base
│   ├── frontend/               # Web UI
│   │   └── index.html         # Single-page Alpine.js app
│   └── data/                   # Runtime data (domains.json)
├── data/                       # Pattern storage (bind mounted)
│   └── patterns/               # All domain patterns (JSON)
│       ├── cooking/
│       ├── llm_consciousness/
│       └── {domain}/           # Add new domains here
├── config/                     # Monitoring configurations
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── promtail/
├── docker-compose.yml          # Docker deployment
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# For local LLMs (Ollama, etc.)
# OPENAI_BASE_URL=http://host.docker.internal:11434/v1

# Application Settings
LOG_LEVEL=INFO
```

### Domain Configuration

Domains are configured in two ways:

1. **Code-based**: Edit `generic_framework/api/app.py` in the `startup_event()` function
2. **UI-based**: Create domains through the Domains tab (stored in `data/domains.json`)

---

## API Reference

### Health Check

```bash
curl http://localhost:3000/health
```

### List Domains

```bash
curl http://localhost:3000/api/domains
```

### Get Domain Info

```bash
curl http://localhost:3000/api/domains/{domain_id}
```

### Query a Domain

```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I detect when an LLM is hallucinating?",
    "domain": "llm_consciousness",
    "include_trace": true
  }'
```

### List Patterns

```bash
curl "http://localhost:3000/api/domains/{domain_id}/patterns"
```

### Get Pattern Details

```bash
curl "http://localhost:3000/api/domains/{domain_id}/patterns/{pattern_id}"
```

### List Specialists

```bash
curl "http://localhost:3000/api/domains/{domain_id}/specialists"
```

### Query History

```bash
curl "http://localhost:3000/api/history?domain={domain_id}&limit=10"
```

### Query Traces

```bash
curl "http://localhost:3000/api/traces?domain={domain_id}&limit=20"
```

### Get Trace Detail

```bash
curl "http://localhost:3000/api/traces/{query_id}"
```

### Domain CRUD (Admin)

```bash
# List all domains
curl http://localhost:3000/api/admin/domains

# Get domain config
curl http://localhost:3000/api/admin/domains/{domain_id}

# Create domain
curl -X POST http://localhost:3000/api/admin/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": "my_domain",
    "domain_name": "My Knowledge Domain",
    "description": "Domain description",
    "categories": ["category1", "category2"],
    "tags": ["tag1", "tag2"],
    "specialists": [
      {
        "specialist_id": "specialist_1",
        "name": "Expert Specialist",
        "description": "Specializes in X",
        "expertise_keywords": ["keyword1", "keyword2"],
        "expertise_categories": ["category1"],
        "confidence_threshold": 0.6
      }
    ]
  }'

# Update domain
curl -X PUT http://localhost:3000/api/admin/domains/{domain_id} \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "Updated Domain Name",
    "description": "Updated description"
  }'

# Delete domain
curl -X DELETE http://localhost:3000/api/admin/domains/{domain_id}
```

---

## Adding New Domains

### Method 1: Through the UI (Recommended)

1. Go to the **Domains** tab
2. Click **Create Domain**
3. Fill in the form:
   - **Domain ID**: Lowercase with underscores (e.g., `my_domain`)
   - **Domain Name**: Human-readable name
   - **Description**: What the domain covers
   - **Categories**: Knowledge categories
   - **Tags**: Searchable tags
   - **Specialists**: Add one or more specialists
4. Click **Save Domain**

### Method 2: Code-Based (Advanced)

1. Create domain directory:

```bash
mkdir -p generic_framework/domains/mydomain/specialists
```

2. Create domain class (`generic_framework/domains/mydomain/domain.py`):

```python
from core.domain import Domain, DomainConfig
from core.specialist import SpecialistConfig
from typing import Dict, List, Any

class MyDomain(Domain):
    def __init__(self, config: DomainConfig):
        self.config = config
        self._specialists = {}

    @property
    def domain_id(self) -> str:
        return self.config.domain_id

    @property
    def domain_name(self) -> str:
        return self.config.domain_name

    async def initialize(self) -> None:
        """Initialize domain resources."""
        pass

    async def cleanup(self) -> None:
        """Cleanup domain resources."""
        pass

    def list_specialists(self) -> List[str]:
        return list(self._specialists.keys())

    def get_specialist(self, specialist_id: str):
        return self._specialists.get(specialist_id)

    def add_specialist(self, specialist_id: str, specialist) -> None:
        self._specialists[specialist_id] = specialist
```

3. Create specialists in `generic_framework/domains/mydomain/specialists/`

4. Register in `generic_framework/api/app.py`:

```python
from domains.mydomain.domain import MyDomain

# In startup_event()
DomainFactory.register_domain(MyDomain)

my_config = DomainConfig(
    domain_id="mydomain",
    domain_name="My Domain",
    version="1.0.0",
    description="My custom knowledge domain",
    pattern_storage_path=get_storage_path("mydomain"),
    pattern_format="json",
    categories=["category1"],
    tags=["tag1"]
)

my_domain = MyDomain(my_config)
await my_domain.initialize()

engines["mydomain"] = GenericAssistantEngine(my_domain)
await engines["mydomain"].initialize()
```

---

## Docker Deployment

### Data Persistence

The container uses bind mounts for pattern storage:

- **Patterns**: `./data/patterns` → `/app/data/patterns`
- **Domain Registry**: Named volume `eeframe_data` → `/app/data`

This means:
- Patterns edited on the host are immediately available in the container
- Container restarts preserve pattern data
- To backup patterns: `tar -czf backup.tar.gz data/`

### Rebuilding After Code Changes

```bash
# Rebuild and restart
docker-compose down
docker-compose build --no-cache eeframe-app
docker-compose up -d
```

### Viewing Logs

```bash
# Application logs
docker logs -f eeframe-app

# All services
docker-compose logs -f
```

### Scaling

```yaml
# In docker-compose.yml
services:
  eeframe-app:
    deploy:
      replicas: 3
```

---

## Development

### Running Locally (Without Docker)

```bash
# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key
export PYTHONPATH=generic_framework:$PYTHONPATH

# Run the application
cd generic_framework
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 3000
```

### Code Formatting

```bash
black generic_framework/
ruff check generic_framework/
mypy generic_framework/
```

### Testing

```bash
pytest tests/ -v
```

---

## Current Domains

EEFrame includes 7 production domains demonstrating the plugin architecture:

### Binary Symmetry
- **Specialists**: 3 (BitwiseMaster, PatternAnalyst, AlgorithmExplorer)
- **Patterns**: 16
- **Categories**: symmetry, transformation, relationship, metric, encoding, logic, detection
- **Tags**: binary, bitwise, xor, algorithm, math, computer_science, 8-bit

### Cooking & Recipes
- **Specialists**: 1 (Generalist)
- **Patterns**: 21
- **Categories**: technique, recipe, cooking_method, ingredient_substitution
- **Tags**: baking, chicken, quick, healthy

### LLM Consciousness & Failure Modes
- **Specialists**: 2 (FailureDetection, Monitoring)
- **Patterns**: 11
- **Categories**: failure_mode, solution, monitoring, architecture, detection
- **Tags**: hallucination, tool_failure, loops, amnesia, confidence, quality_drift

### Python Programming
- **Specialists**: 1 (Generalist)
- **Patterns**: 6
- **Categories**: language_feature, best_practice, anti_pattern
- **Tags**: python, programming, best_practices

### Template Domains
- **Gardening**: Template domain (0 patterns)
- **First Aid**: Template domain (1 pattern)
- **DIY**: Template domain (0 patterns)

**Total**: 7 domains, 55+ patterns, 9 specialist plugins

---

## Troubleshooting

### "docker-compose: command not found" or "no configuration file provided"

**Cause**: You're using the old `docker-compose` (v1) syntax. This project requires Docker Compose v2.

**Solution**: Use `docker compose` (with a space, not a hyphen):
```bash
# WRONG (old v1 syntax):
docker-compose up -d

# CORRECT (v2 syntax):
docker compose up -d
```

### Patterns Not Showing / Empty Pattern Directory

**Cause**: Docker snap has known bind mount bugs that cause mounted directories to appear empty inside containers.

**Solution**: Uninstall snap Docker and install official Docker Engine:
```bash
# Remove snap Docker
sudo snap remove docker

# Install official Docker
curl -fsSL https://get.docker.com | sh

# Restart containers
docker compose down
docker compose up -d
```

### Container Not Starting

1. Check port conflicts: `sudo lsof -ti:3000`
2. Check container logs: `docker compose logs eeframe-app`
3. Verify Docker is running: `docker ps`

### "Address already in use" error

**Cause**: Port 3000 is already in use (possibly by a previous container).

**Solution**:
```bash
# Kill any process using port 3000
sudo lsof -ti:3000 | xargs sudo kill -9

# Restart containers
docker compose down
docker compose up -d
```

### Frontend Shows "Generic Assistant Framework - Frontend not found"

**Cause**: Frontend files not accessible in container.

**Solution**: Check if frontend is mounted correctly:
```bash
# Check frontend mount in container
docker exec eeframe-app ls -la /app/frontend/

# If empty, rebuild container:
docker compose down
docker compose build --no-cache eeframe-app
docker compose up -d
```

### Permission Errors

```bash
# Fix pattern directory permissions
chmod -R 755 data/patterns/
```

### API Returns 404

1. Verify health endpoint works: `curl http://localhost:3000/health`
2. Check if routes are loaded: Visit `http://localhost:3000/docs`
3. Restart container: `docker compose restart eeframe-app`

---

## Security Considerations

### For Production Deployment

1. **API Keys**: Never commit `.env` file
2. **Authentication**: Add user authentication (not yet implemented)
3. **HTTPS**: Use reverse proxy (nginx) for SSL/TLS
4. **Network Isolation**: Run in private network
5. **Resource Limits**: Configure memory/CPU limits in docker-compose.yml
6. **Secrets Management**: Use Docker secrets or external secret manager

### Volume Backup

```bash
# Backup patterns
docker run --rm -v eeframe_data:/data -v $(pwd):/backup ubuntu \
  tar czf /backup/eeframe_backup_$(date +%Y%m%d).tar.gz /data

# Restore from backup
docker run --rm -v eeframe_data:/data -v $(pwd):/backup ubuntu \
  tar xzf /backup/eeframe_backup_YYYYMMDD.tar.gz -C /
```

---

## License

MIT License

---

## Contributing

Contributions are welcome! Areas of interest:

- New domains (specialist knowledge areas)
- Pattern ingestion improvements
- UI enhancements
- Documentation
- Bug fixes

---

## Changelog

### Version 1.0.0 - Plugin Architecture Release (2026-01-09)

**Major Features**:
- ✅ Specialist Plugin interface (3-method: can_handle, process_query, format_response)
- ✅ Knowledge Base Plugin interface (storage abstraction)
- ✅ Generic Domain class with dynamic plugin loading
- ✅ Domain auto-discovery from `data/patterns/*/`
- ✅ 7 production domains (55+ patterns, 9 specialists)
- ✅ Domain configuration via JSON (domain.json)
- ✅ Specialist configuration via JSON
- ✅ Knowledge base plugin selection (JSON, SQLite)

**Documentation**:
- ✅ CHANGELOG.md with detailed release notes
- ✅ PLUGIN_ARCHITECTURE.md with plugin development guide
- ✅ Updated README with plugin architecture overview

**Bug Fixes**:
- ✅ API endpoints work with plugin attributes
- ✅ Pattern search returns all patterns when no category specified
- ✅ Pattern detail endpoint uses correct method name
- ✅ Frontend displays specialists and patterns for all domains

**Known Limitations**:
- Router logic still hardcoded in GenericDomain (planned for v1.1)
- Formatter logic embedded in specialists (planned for v1.1)

### Version 0.9.0 and Earlier

See git history for detailed changes.

---

## Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Detailed version history and changes
- **[PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md)** - Plugin development guide
- **[docs/](docs/)** - Additional documentation

## License

MIT License

---

## Contributing

Contributions are welcome! Areas of interest:

- New domains and specialist plugins
- Pattern ingestion improvements
- UI enhancements
- Additional knowledge base backends (Vector DB, Graph DB)
- Router and formatter plugins (v1.1)
