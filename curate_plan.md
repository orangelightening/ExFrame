# Documentation Curation Plan

**Date:** 2026-01-29
**Status:** DRAFT
**Purpose:** Clean up, restructure, and regenerate all project documentation from source code

---

## Current State Analysis

### Problem: Documentation Sprawl
- 20+ markdown files in root directory
- Outdated/contradictory documentation
- Documentation conflicts with actual code
- No single source of truth
- Difficult to find relevant information

### Inventory of Existing Docs

**Root Level (to be archived):**
- AI-to-AI Communication Protocol for Claude Code.md
- EXframe 1st reply.md
- GITHUB_LAUNCH_GUIDE.md
- LAUNCH_CHECKLIST.md
- LAUNCH_MANIFESTO.md
- OPEN_SOURCE_GUIDE.md
- PLAN.md
- claude-exframe.md
- exframe-domain-design.md
- fresh-look.md
- query-todo.md
- al-plan.md
- claude.md
- context.md
- ready-set.md
- release-plan.md
- rag-search-design.md
- query-rewrite.md
- needed.md
- DEPENDENCY_LICENSES.md
- which-way.md
- CHANGELOG.md
- DOMAIN_TYPES_SIMPLIFIED.md
- EXTENSION_POINTS.md
- INSTALL.md
- PLUGIN_ARCHITECTURE.md
- README.md
- RELEASE_NOTES.md
- What is ExFrame.md

**Archive Level (already exists):**
- archive/docs/*.md

**Documentation Should Reflect:**
- Actual code structure
- Data structures (domain.json patterns)
- API endpoints
- Plugin interfaces
- Configuration options

---

## New Documentation Structure

```
/home/peter/development/eeframe/
├── .archive/                          # OLD DOCS (gitignored)
│   ├── old-root-docs/                 # All root-level .md files
│   ├── old-concepts/                   # Outdated concept docs
│   └── old-plans/                     # Old planning docs
│
├── docs/                              # NEW DOCUMENTATION (committed)
│   ├── INDEX.md                       # MASTER INDEX (see format below)
│   ├── README.md                      # Quick start overview
│   │
│   ├── architecture/                  # System Architecture
│   │   ├── overview.md                # High-level architecture
│   │   ├── plugin-system.md           # Plugin architecture
│   │   ├── domain-system.md           # Domain type system
│   │   ├── query-pipeline.md          # Query processing flow
│   │   └── enricher-chain.md          # Enricher pipeline
│   │
│   ├── api/                           # API Documentation
│   │   ├── endpoints.md               # All API routes
│   │   ├── query-api.md               # Query endpoint details
│   │   ├── domain-api.md              # Domain management
│   │   └── admin-api.md               # Admin operations
│   │
│   ├── guides/                        # User Guides
│   │   ├── quickstart.md              # Get started in 5 minutes
│   │   ├── creating-domains.md        # How to create domains
│   │   ├── domain-types.md            # Type 1-5 reference
│   │   ├── web-search.md              # Using web search
│   │   └── troubleshooting.md         # Common issues
│   │
│   ├── plugins/                       # Plugin Documentation
│   │   ├── specialists.md             # Specialist plugins
│   │   ├── enrichers.md               # Enricher plugins
│   │   ├── knowledge-bases.md         # KB plugins
│   │   └── creating-plugins.md        # How to write plugins
│   │
│   ├── reference/                     # Technical Reference
│   │   ├── domain-config.md           # domain.json schema
│   │   ├── pattern-schema.md          # pattern.json schema
│   │   ├── configuration.md           # All config options
│   │   └── error-codes.md             # Error handling
│   │
│   └── development/                   # Developer Docs
│       ├── setup.md                   # Dev environment setup
│       ├── testing.md                 # Running tests
│       ├── deployment.md              # Deployment guide
│       └── contributing.md            # Contribution guidelines
```

---

## Implementation Steps

### Step 1: Create .archive Directory and .gitignore

**Action:** Create `.archive/` and add to `.gitignore`

```bash
mkdir -p .archive/old-root-docs .archive/old-concepts .archive/old-plans
```

**Add to `.gitignore`:**
```
# Archived documentation (not tracked)
.archive/
```

### Step 2: Move Existing Docs to .archive

**Action:** Move all root-level docs to `.archive/old-root-docs/`

```bash
# List of files to move (NOT including: README.md, INSTALL.md, CHANGELOG.md)
mv "AI-to-AI Communication Protocol for Claude Code.md" .archive/old-root-docs/
mv "EXframe 1st reply.md" .archive/old-root-docs/
mv GITHUB_LAUNCH_GUIDE.md .archive/old-root-docs/
mv LAUNCH_CHECKLIST.md .archive/old-root-docs/
mv LAUNCH_MANIFESTO.md .archive/old-root-docs/
mv OPEN_SOURCE_GUIDE.md .archive/old-root-docs/
mv PLAN.md .archive/old-root-docs/
mv claude-exframe.md .archive/old-root-docs/
mv exframe-domain-design.md .archive/old-root-docs/
mv fresh-look.md .archive/old-root-docs/
mv query-todo.md .archive/old-root-docs/
mv al-plan.md .archive/old-root-docs/
mv claude.md .archive/old-root-docs/
mv context.md .archive/old-root-docs/
mv ready-set.md .archive/old-root-docs/
mv release-plan.md .archive/old-root-docs/
mv rag-search-design.md .archive/old-root-docs/
mv query-rewrite.md .archive/old-root-docs/
mv needed.md .archive/old-root-docs/
mv which-way.md .archive/old-root-docs/
mv "What is ExFrame.md" .archive/old-root-docs/

# Move old architecture docs
mv DOMAIN_TYPES_SIMPLIFIED.md .archive/old-concepts/
mv EXTENSION_POINTS.md .archive/old-concepts/
```

**KEEP in root (update these):**
- README.md (rewrite)
- INSTALL.md (keep current)
- CHANGELOG.md (keep current)

**MOVE to docs/ as base:**
- PLUGIN_ARCHITECTURE.md → docs/architecture/plugin-system.md

### Step 3: Create New Documentation Structure

**Action:** Create `docs/` directory structure

```bash
mkdir -p docs/{architecture,api,guides,plugins,reference,development}
```

### Step 4: Generate INDEX.md from Source Code

**Action:** Scan codebase and generate index

**Process:**
1. Scan `generic_framework/` for all Python files
2. Scan `universes/MINE/domains/` for domain configs
3. Scan `generic_framework/api/` for endpoint definitions
4. Generate INDEX.md with format specified below

### Step 5: Rewrite Documentation from Source

**Priority Order:**

1. **docs/INDEX.md** (from source code scan)
2. **docs/README.md** (quick overview)
3. **docs/architecture/overview.md** (from code structure)
4. **docs/guides/domain-types.md** (from domain_factory.py)
5. **docs/reference/domain-config.md** (from domain.json schema)
6. **docs/api/endpoints.md** (from app.py routes)
7. **docs/plugins/specialists.md** (from specialist plugins)

**Method:** Read source files, extract structure, write clear docs

---

## INDEX.md Format Specification

### Structure

```markdown
# ExFrame Documentation Index

**Generated:** 2026-01-29
**Source:** Codebase scan
**Purpose:** Fast navigation of all system files

## File Index

### Core Framework Files

generic_framework/api/app.py...FastAPI application with all endpoints (45 routes, query, domain management, admin operations)

generic_framework/assist/engine.py...Query processing engine with specialist selection, enricher pipeline, LLM integration (500 lines)

generic_framework/core/domain.py...Domain class that loads config, initializes plugins, handles queries via specialists

generic_framework/core/domain_factory.py...DomainConfigGenerator creates domain.json configs for Types 1-5 (Type 4: Analytical with web search)

generic_framework/core/specialist_plugin.py...SpecialistPlugin interface: can_handle(), process_query(), format_response()

generic_framework/plugins/research/research_specialist.py...ResearchSpecialistPlugin for Type 4: two-stage query (local patterns → web search on button click)

generic_framework/plugins/enrichers/llm_enricher.py...LLMEnricher: enhances responses using LLM, now supports web search results as context

generic_framework/plugins/enrichers/reply_formation.py...ReplyFormationEnricher: formats web search sources with URLs and emoji indicators

### API Endpoint Files

generic_framework/api/app.py:line@1578...PUT /api/admin/domains/{domain_id} - Update domain configuration

generic_framework/api/app.py:line@1430...POST /api/query - Main query endpoint

generic_framework/api/app.py:line@1488...POST /api/query/extend-web-search - Extended web search endpoint for Type 4

### Domain Configuration Files

universes/MINE/domains/{domain_id}/domain.json...Domain configuration: plugins, enrichers, knowledge_base, domain_type (1-5), ui_config

universes/MINE/domains/diy/domain.json...Type 4 Analytical Engine: ResearchSpecialistPlugin, enable_web_search=true, ReplyFormationEnricher

universes/MINE/domains/cooking/domain.json...Type 4 Analytical Engine: ResearchSpecialistPlugin, web search enabled

universes/MINE/domains/exframe/domain.json...Type 3 Document Store: ExFrameSpecialistPlugin, document research with auto-discovery

### Frontend Files

generic_framework/frontend/index.html...Alpine.js SPA: domain selection, query input, results display, domain management UI (3000+ lines)

### Documentation Files

docs/README.md...Quick start guide

docs/architecture/overview.md...System architecture overview

docs/guides/domain-types.md...Complete guide to domain Types 1-5

docs/reference/domain-config.md...domain.json schema reference

```

### Format Rules

1. **One line per file**
2. **Format:** `filepath...summary`
3. **Use @line for specific locations:** `filepath:line@123...summary`
4. **Maximum 100 chars per line**
5. **Group by directory/function**
6. **Alphabetical within groups**
7. **Summary must describe WHAT the file does, not HOW**

---

## Sample INDEX.md Snippet

```markdown
# ExFrame Documentation Index

**Generated:** 2026-01-29
**Source:** Codebase scan
**Purpose:** Fast navigation of all system files

## Core Framework

generic_framework/api/app.py...FastAPI app with 45 routes: query endpoints, domain CRUD, admin operations, traces, health

generic_framework/assist/engine.py...Query orchestrator: specialist selection, enricher pipeline, LLM fallback, response formatting

generic_framework/core/domain.py...GenericDomain loads domain.json, initializes plugins/kb, routes queries to specialists

generic_framework/core/domain_factory.py...DomainConfigGenerator: creates configs for Types 1-5, single source of truth for defaults

generic_framework/core/specialist_plugin.py...SpecialistPlugin interface: can_handle(score), process_query(results), format_response(string)

generic_framework/core/research/internet_strategy.py...DuckDuckGo web search: parses HTML results, extracts titles/snippets/URLs, no API key needed

generic_framework/core/research/document_strategy.py...DocumentResearchStrategy: auto-discovers files recursively using **/* pattern with exclusions

## Specialist Plugins

generic_framework/plugins/generalist/generalist_plugin.py...GeneralistPlugin: keyword/category matching, threshold-based scoring, KB search via specialist

generic_framework/plugins/research/research_specialist.py...ResearchSpecialistPlugin: Type 4 two-stage query (local → web), DuckDuckGo integration

generic_framework/plugins/exframe/exframe_specialist.py...ExFrameSpecialistPlugin: Type 3 document research + local patterns, 3-stage search strategy

## Enrichers

generic_framework/plugins/enrichers/llm_enricher.py...LLMEnricher: synthesizes responses from patterns/web results, supports web search context

generic_framework/plugins/enrichers/reply_formation.py...ReplyFormationEnricher: displays web sources with 🌐 emoji, formats combined results

generic_framework/plugins/enrichers/llm_fallback_enricher.py...LLMFallbackEnricher: provides LLM response when patterns are weak (Type 5)

## API Endpoints

POST /api/query...Main query endpoint: accepts query, domain, format, trace params; returns QueryResponse with patterns, llm_enhancement

POST /api/query/extend-web-search...Extended web search for Type 4: performs DuckDuckGo search, returns results with sources

PUT /api/admin/domains/{domain_id}...Update domain: regenerates config via domain_factory when domain_type changes

GET /api/domains/{domain_id}/health...Domain health check: patterns_loaded, categories, specialists, plugins status

## Domain Configurations

universes/MINE/domains/{domain_id}/domain.json...Domain config: domain_type (1-5), plugins[], enrichers[], knowledge_base{}, ui_config{}

universes/MINE/domains/diy/domain.json...Type 4 DIY: ResearchSpecialistPlugin, enable_web_search=true, DIY keywords: [diy, build, fix]

universes/MINE/domains/cooking/domain.json...Type 4 Cooking: ResearchSpecialistPlugin, enable_web_search=true, cooking keywords

universes/MINE/domains/exframe/domain.json...Type 3 ExFrame: ExFrameSpecialistPlugin, document_store with auto-discovery, show_sources=true

universes/MINE/domains/poetry_domain/domain.json...Type 1 Creative: GeneralistPlugin, creative_mode=true, temperature=0.8, creative keywords

universes/MINE/domains/llm_consciousness/domain.json...Type 2 Knowledge: GeneralistPlugin, patterns about hallucination, tool loops, failure modes

## Frontend

generic_framework/frontend/index.html...Alpine.js SPA (3000+ lines): domain dropdown, query input, "Extended Search" button, results, admin panel

generic_framework/frontend/index.html:line@3573...onDomainTypeChange(): logs type change, backend regenerates config on save

generic_framework/frontend/index.html:line@380...extendWithWebSearch(): calls /api/query/extend-web-search endpoint

## Documentation

docs/INDEX.md...This file: master index of all code files with one-line summaries

docs/README.md...Quick start: 5-minute setup, run with Docker, query domains, create new domain

docs/architecture/overview.md...System architecture: generic domain, plugin system, specialist selection, enricher pipeline

docs/guides/domain-types.md...Domain Types 1-5: Creative, Knowledge, Document Store, Analytical, Hybrid - when to use each

docs/reference/domain-config.md...domain.json reference: all fields, plugin config, enricher config, type-specific options

## Data Files

universes/MINE/domains/{domain_id}/patterns.json...Pattern storage: array of pattern objects with id, name, pattern_type, problem, solution, tags

data/patterns/{domain_id}/domain.json...Legacy domain configs (migrated to universes/MINE/domains/)

## Configuration

docker-compose.yml...Docker services: eeframe-app container, volume mounts, port 3000, health check

Dockerfile...Multi-stage build: Python 3.11, install torch via pip, copy code, run as appuser

requirements.txt...Python dependencies: fastapi, uvicorn, torch, numpy, httpx, anthropic, jinja2

## Tests

generic_framework/tests/...Test suite: plugin tests, API tests, integration tests (TODO: add comprehensive tests)

## Archive

.archive/old-root-docs/...Archived documentation (not tracked): old planning docs, outdated concepts, superseded guides

.archive/old-concepts/...Archived concept docs: DOMAIN_TYPES_SIMPLIFIED.md, EXTENSION_POINTS.md (superseded by new docs)
```

---

## Execution Order

1. Create `.archive/` structure and `.gitignore`
2. Move old docs to `.archive/`
3. Create `docs/` directory structure
4. Run code scanner to generate `docs/INDEX.md`
5. Write `docs/README.md` (quick start)
6. Write `docs/architecture/overview.md` (from code)
7. Write `docs/guides/domain-types.md` (from domain_factory.py)
8. Write `docs/reference/domain-config.md` (from schema)
9. Write remaining docs by priority
10. Commit: `docs: restructure and regenerate documentation from source code`
11. Push changes

---

## Success Criteria

✅ No documentation in root directory (except README.md, INSTALL.md, CHANGELOG.md)
✅ All old docs in `.archive/` (gitignored)
✅ New docs in `docs/` with clear structure
✅ `docs/INDEX.md` lists all files with one-line summaries
✅ Documentation matches actual code structure
✅ Documentation is navigable and findable
✅ Single source of truth: source code drives documentation

---

## Notes

- **INDEX.md is generated**: Can be regenerated when code changes
- **Documentation lives in code**: Comments and structure should be self-documenting
- **Keep it current**: Regenerate INDEX.md after significant changes
- **One source of truth**: domain_factory.py defines types, not separate docs
