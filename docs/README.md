# ExFrame Documentation

**ExFrame** - Generic Expertise Enhancement Framework

A plugin-based domain expert system with configurable types, web search, and LLM integration.

---

## Quick Start

### 1. Run with Docker

```bash
docker-compose up -d eeframe-app
```

Access at: http://localhost:3000

### 2. Query a Domain

```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your question", "domain": "cooking"}'
```

### 3. Create a New Domain

1. Click "Admin" in the UI
2. Click "Create Domain"
3. Select Domain Type (1-5)
4. Fill in configuration
5. Click "Save"

---

## Domain Types

| Type | Name | Use For | Web Search |
|------|------|---------|------------|
| 1 | Creative Generator | Poems, stories, creative content | No |
| 2 | Knowledge Retrieval | How-to guides, FAQs, technical docs | No |
| 3 | Document Store Search | External documentation, API docs, live data | No |
| 4 | Analytical Engine | Research, analysis, correlation, reports | **Yes** |
| 5 | Hybrid Assistant | General purpose, flexible, user choice | Optional |

---

## Type 4: Analytical Engine (Web Search)

Type 4 domains support **two-stage query flow**:

1. **Local Search** (immediate)
   - Returns local pattern results
   - Shows "Extended Search (Internet)" button

2. **Extended Search** (on user action)
   - Performs DuckDuckGo web search
   - Returns results with source URLs
   - LLM synthesizes from web + local

**Example Type 4 Domains:**
- `diy` - DIY projects with web research
- `cooking` - Recipes with web search

---

## Architecture

```
Query → Specialist Plugin → Enricher Pipeline → Response
         ↓                    ↓
    [Local Patterns]    [LLM Enhancement]
    [Web Search]         [Source Formatting]
```

**Components:**
- **Specialist Plugins**: Answer queries, perform searches
- **Enricher Plugins**: Transform and enhance responses
- **Knowledge Base**: Store and retrieve patterns
- **Domain Factory**: Generate configurations for Types 1-5

---

## API Endpoints

### Query Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/query` | POST | Main query endpoint |
| `/api/query/extend-web-search` | POST | Extended web search (Type 4) |

### Domain Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/domains` | GET | List all domains |
| `/api/domains/{id}/query` | POST | Query specific domain |
| `/api/domains/{id}/health` | GET | Domain health check |

### Admin Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/admin/domains` | POST | Create domain |
| `/api/admin/domains/{id}` | PUT | Update domain |
| `/api/admin/domains/{id}` | DELETE | Delete domain |

---

## File Structure

```
generic_framework/
├── api/app.py                    # FastAPI app, all endpoints
├── assist/engine.py              # Query orchestrator
├── core/
│   ├── domain.py                 # GenericDomain class
│   ├── domain_factory.py         # Type 1-5 config generator
│   └── specialist_plugin.py      # Specialist interface
├── plugins/
│   ├── research/                 # Research specialist (Type 4)
│   ├── exframe/                  # ExFrame specialist (Type 3)
│   ├── generalist/               # Generalist plugin
│   └── enrichers/                # Response enrichers
└── frontend/index.html           # Alpine.js SPA

universes/MINE/domains/
├── {domain_id}/
│   ├── domain.json               # Domain configuration
│   └── patterns.json             # Pattern storage
```

---

## Configuration

### Domain Configuration (`domain.json`)

```json
{
  "domain_id": "example",
  "domain_name": "Example Domain",
  "domain_type": "4",
  "plugins": [...],
  "enrichers": [...],
  "knowledge_base": {...}
}
```

**Key Fields:**
- `domain_type`: "1" (Creative), "2" (Knowledge), "3" (Document), "4" (Analytical), "5" (Hybrid)
- `plugins`: List of specialist plugins
- `enrichers`: List of response enrichers
- `knowledge_base`: Pattern storage configuration

---

## Guides

- **[Architecture Overview](docs/architecture/overview.md)** - System architecture
- **[Domain Types Guide](docs/guides/domain-types.md)** - Complete Type 1-5 reference
- **[Creating Domains](docs/guides/creating-domains.md)** - How to create domains
- **[Web Search](docs/guides/web-search.md)** - Using Type 4 web search
- **[Plugin Development](docs/plugins/creating-plugins.md)** - Writing plugins

---

## Reference

- **[INDEX.md](docs/INDEX.md)** - Master file index
- **[Domain Config Reference](docs/reference/domain-config.md)** - domain.json schema
- **[API Endpoints](docs/api/endpoints.md)** - Complete API reference

---

## Development

See [Development Guide](docs/development/setup.md)

---

**License:** Apache 2.0
