# ExFrame - Current System State

**Date**: February 6, 2026
**Status**: ✅ Production Ready
**Version**: Phase1 Architecture

---

## Executive Summary

ExFrame is running a **stable, production-ready Phase1 implementation** with 11 active domains, 3 AI personas, and a clean web interface. The Wiseman experiment (February 2026) was abandoned due to complexity, and the system was restored to the last stable commit.

---

## What's Working ✅

### Core Architecture: Phase1 Engine

**Implementation**: `generic_framework/core/phase1_engine.py`

The Phase1 engine provides simple, reliable persona-based query processing:

```
Query → Phase1Engine → Persona Selection → Pattern Search → LLM Enrichment → Response
```

**3 Personas**:
| Persona | Domain Type | Data Source | Use Case |
|---------|-------------|-------------|----------|
| **Poet** | Type 1 | Void/creative | Poetry, creative writing |
| **Librarian** | Type 2 | Library/docs | Code, technical documentation |
| **Researcher** | Type 4 | Internet/web | Research, current information |

**Pattern Override**: If patterns found in domain → use patterns; else use persona's data source.

### 11 Active Domains

| Domain | Persona | Description | Status |
|--------|---------|-------------|--------|
| binary_symmetry | Researcher | Bitwise operations, binary patterns | ✅ Active |
| cooking | Researcher | Recipes, cooking techniques | ✅ Active |
| diy | Researcher | DIY projects, home improvement | ✅ Active |
| first_aid | Researcher | Medical advice, first aid | ✅ Active |
| gardening | Researcher | Plants, gardening techniques | ✅ Active |
| llm_consciousness | Poet | AI consciousness, philosophy | ✅ Active |
| python | Librarian | Python programming | ✅ Active |
| exframe | Librarian | System documentation | ✅ Active |
| poetry_domain | Poet | Poetry, creative writing | ✅ Active |
| psycho | Researcher | Psychology, "Doctor Twist" | ✅ Active |
| omv_library | Librarian | Document library | ✅ Active |

### Web Interface

**URL**: http://localhost:3000 (or http://192.168.3.29:3000 on local network)

**Features**:
- Domain selection dropdown
- Query input with placeholder text
- Response display with sources
- Thinking toggle (show/hide LLM reasoning)
- Example queries per domain

### API Endpoints

**Phase1 Query**:
```bash
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I bake chicken?", "domain": "cooking"}'
```

**Health Check**:
```bash
curl http://localhost:3000/api/health
```

**List Domains**:
```bash
curl http://localhost:3000/api/domains
```

**CORS**: Enabled for local network access (Claude Code integration)

---

## System Architecture

### Component Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Dashboard (Alpine.js)                │
│                    http://localhost:3000                     │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    FastAPI (app.py)                          │
│  /api/query/phase1  /api/health  /api/domains               │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  Phase1Engine                                │
│  - Persona selection (poet/librarian/researcher)             │
│  - Pattern search (semantic similarity)                      │
│  - LLM enrichment (Claude API)                               │
│  - Web search (researcher domains)                           │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌───────▼──────┐ ┌─────────▼────────┐
│  Pattern Store  │ │  LLM Service │ │  Web Search      │
│  (embeddings)   │ │  (Claude)    │ │  (DuckDuckGo)    │
└─────────────────┘ └──────────────┘ └──────────────────┘
```

### Query Flow

1. **Request**: User submits query via web GUI or API
2. **Domain Selection**: Domain specified or inferred from context
3. **Persona Selection**: Determined by domain type
4. **Pattern Search**: Semantic search against domain patterns
5. **Pattern Override**: If patterns found → use; else use persona data source
6. **Enrichment**: LLM enhances response with context
7. **Response**: Formatted response returned to user

---

## Configuration

### Domain Persona Configuration

Each domain has a `domain.json` file with persona setting:

```json
{
  "domain_id": "cooking",
  "domain_type": "4",
  "persona": "researcher",
  "enable_web_search": true,
  "temperature": 0.7
}
```

**Persona Types**:
- `"poet"` - Type 1 domains (creative, void-based)
- `"librarian"` - Type 2 domains (library, documentation)
- `"researcher"` - Type 4 domains (web search, current info)

### Universe Configuration

**File**: `universes/MINE/universe.yaml`

- **Load on startup**: `true`
- **Default universe**: `true`
- **11 domains enabled**
- Domain-level priorities and config overrides

---

## Deployment

### Docker Compose

**Production deployment** with monitoring stack:

```bash
docker compose up -d
```

**Services**:
- `app` - Main ExFrame application
- `prometheus` - Metrics collection
- `grafana` - Metrics visualization

### Health Check

```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "universe": "MINE",
  "domains": 11,
  "version": "1.6.0"
}
```

---

## Inter-System Communications

**Claude Code Integration**: Multiple ExFrame instances can communicate on the local network.

### Martha Machine
- **IP Address**: `192.168.3.29`
- **Port**: `3000`
- **URL**: http://192.168.3.29:3000
- **Status**: Active (tested February 6, 2026)

**Example Query** (Martha Machine):
```bash
curl -X POST http://192.168.3.29:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query": "What is binary symmetry?", "domain": "binary_symmetry"}'
```

**Health Check**:
```bash
curl http://192.168.3.29:3000/api/health
```

**CORS Configuration**: `allow_origins=["*"]` for local network access.

### Localhost Access
- **URL**: http://localhost:3000
- **Use Case**: Local development and testing

---

## Known Issues

### ISSUE-001: Domains Losing Persona Type on Reload

**Status**: Under Investigation

**Problem**: Some domains are not retaining their persona type (poet/librarian/researcher) after system restart or reload.

**Workaround**: Manually edit `domain.json` to set persona:
```json
{"persona": "researcher"}
```

**Status**: User testing all domain persona settings to identify affected domains.

See `ISSUES.md` for details.

---

## Historical Context

### Wiseman Experiment (February 2026)

**Status**: ❌ Abandoned

**What Was Wiseman**:
- Config-driven universal execution engine
- Dynamic persona switching based on query context
- Recursive config hierarchy (System → Universe → Domain → Pattern)

**Why Abandoned**:
- Complexity vs. simplicity trade-off failed
- Circular import errors (`ImportError: cannot import name 'WiseManPersona'`)
- Container crashes despite multiple rebuild attempts
- Violated KISS principle

**Decision Made**:
> "Clean it up. Better to use phase 1. I started to see the exceptions piling up and the import issues. Not worth the trouble."

**Resolution**:
- Git reset to commit `a9f80be3` (last stable push)
- All Wiseman files removed (~1,200 lines)
- Documentation archived to `.archive/wiseman-experiment/`
- Phase1 restored and working

**Lesson Learned**: Phase1 provides all the same user-facing features without the complexity. Architectural optimization that becomes complexity for complexity's sake should be abandoned early.

---

## Development Guidelines

### Principles

1. **Simplicity First**: KISS principle always wins
2. **Everything Viewable**: No hidden logic or magic
3. **Accountable**: Clear query path from request to response
4. **Modular**: Clean separation of concerns
5. **Recursive**: Self-similar patterns at all levels

### What Makes Code Good

- ✅ Simple, readable flow
- ✅ Clear separation of concerns
- ✅ Easy to debug
- ✅ No circular dependencies
- ✅ Transparent configuration

### What Makes Code Bad

- ❌ Complex conditionals
- ❌ Hidden state
- ❌ Circular imports
- ❌ Hard to debug
- ❌ Over-engineered

---

## Next Steps

### Immediate

1. ✅ **Complete domain persona testing** - User verifying all domains have correct persona
2. 🔧 **Resolve ISSUE-001** - Fix persona retention on reload
3. 📚 **Update documentation** - Clean up obsolete references

### Future Considerations

Only add complexity if:
- Clear user-facing benefit beyond Phase1
- No additional debugging complexity
- Simple, clean implementation
- Proven need for new features

**Remember**: Phase1 works. Ship it, don't architect it.

---

## System Status

| Component | Status |
|-----------|--------|
| Phase1 Engine | ✅ Working |
| 11 Domains | ✅ Loaded |
| Web Dashboard | ✅ http://localhost:3000 |
| API | ✅ Responding |
| Pattern Search | ✅ Functional |
| LLM Integration | ✅ Working |
| Web Search | ✅ Enabled (researcher) |
| Container | ✅ Stable |
| Health Check | ✅ Passing |

**Overall**: ✅ **PRODUCTION READY**

---

**Last Updated**: February 6, 2026
**Maintained By**: ExFrame Development Team
