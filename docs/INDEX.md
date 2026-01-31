# ExFrame Documentation Index

**Generated:** 2026-01-29
**Source:** Codebase scan
**Purpose:** Fast navigation of all system files

## Historical Nomenclature Note

**EEFrame → ExFrame Migration (January 2026):**

The project underwent a naming standardization in January 2026 to unify all references under the name "ExFrame". Historical references to "EEFrame" and "omv-copilot" may still exist in some contexts:

- **Directory name**: `eeframe/` - Kept for git history, Docker volumes, and practical deployment reasons
- **Service/Container names**: `eeframe-app`, `eeframe-*` volumes - Kept for data preservation and deployment continuity
- **All user-facing content**: Standardized to "ExFrame" (README, documentation, package name)
- **Internal code paths**: `generic_framework/` - Internal implementation detail, not exposed to users

**Rationale**: The directory and service names are internal plumbing that don't affect end users. Changing them would break git history, Docker volumes, and existing deployments. All documentation and user-facing references now consistently use "ExFrame."

**Production deployment**: Docker Compose (recommended)
**Local development setup**: Clone + `pip install -e .` (editable install from source)
**Project identifier**: `exframe` (pyproject.toml package name)
**License**: Apache License 2.0

## Core Framework

generic_framework/api/app.py...FastAPI app with 45 routes: query endpoints, domain CRUD, admin operations
generic_framework/assist/engine.py...Query orchestrator: specialist selection, enricher pipeline, response formatting
generic_framework/core/domain.py...GenericDomain: loads domain.json, initializes plugins, routes queries
generic_framework/core/domain_factory.py...DomainConfigGenerator: creates configs for Types 1-5, single source of truth
generic_framework/core/specialist_plugin.py...SpecialistPlugin interface: can_handle(), process_query(), format_response()
generic_framework/core/research/internet_strategy.py...DuckDuckGo web search: parses HTML results, extracts titles/snippets/URLs
generic_framework/core/research/document_strategy.py...DocumentResearchStrategy: auto-discovers files recursively with exclusions

## Specialist Plugins

generic_framework/plugins/research/research_specialist.py...ResearchSpecialistPlugin: Type 4 two-stage query (local → web search)
generic_framework/plugins/exframe/exframe_specialist.py...ExFrameSpecialistPlugin: Type 3 document research + local patterns
generic_framework/plugins/generalist/generalist_plugin.py...GeneralistPlugin: keyword/category matching, threshold-based scoring

## Enrichers

generic_framework/plugins/enrichers/llm_enricher.py...LLMEnricher: synthesizes responses, supports web search context, contradiction detection
generic_framework/plugins/enrichers/reply_formation.py...ReplyFormationEnricher: displays web sources with 🌐 emoji and URLs
generic_framework/plugins/enrichers/llm_fallback_enricher.py...LLMFallbackEnricher: provides LLM response when patterns are weak

## Self-Healing Features

**Contradiction Detection System** (Type 3 domains)
- **Location**: `generic_framework/plugins/enrichers/llm_enricher.py` (_detect_and_log_contradictions)
- **Log Location**: `/app/logs/contradictions/contradictions.json` and `contradictions.log`
- **How it works**: Post-response analysis that searches for contradictions across all discovered documents
- **Severity levels**: high (immediate review), medium (cleanup), low (log only)
- **Feedback loop**: Save explanations as patterns → detector learns context → finds new contradictions
- **Nomenclature awareness**: Reads INDEX.md first to understand historical naming (EEFrame → ExFrame)

**Scope Boundaries System** (Per-domain configuration)
- **Location**: `generic_framework/plugins/exframe/exframe_specialist.py` (_is_out_of_scope)
- **Configuration**: `plugins[0].config.scope` in domain.json
- **How it works**: Pre-query check that rejects out-of-scope questions
- **Scope checks**: Explicit keywords, framework detection, relevance threshold
- **Per-domain**: Each domain configures its own boundaries (not type-specific)
- **Routing**: Reject (not route to generalist) - domain-specific behavior

**Self-Healing Documentation Workflow**:
```
1. Query → Contradiction detector analyzes all documents
2. Detector finds issues → Logs with severity and suggestions
3. AI explains the contradiction → User saves explanation as pattern
4. Next query → Detector reads the pattern, understands context
5. Detector finds NEW contradictions (previously addressed ones are gone)
```

## API Endpoints

POST /api/query...Main query endpoint: accepts query, domain, format, trace params
POST /api/query/extend-web-search...Extended web search for Type 4: performs DuckDuckGo search with sources
PUT /api/admin/domains/{domain_id}...Update domain: regenerates config via domain_factory when type changes
GET /api/domains/{domain_id}/health...Domain health check: patterns_loaded, categories, specialists status

## Domain Configurations

universes/MINE/domains/{domain_id}/domain.json...Domain config: domain_type (1-5), plugins[], enrichers[], knowledge_base{}
universes/MINE/domains/diy/domain.json...Type 4 DIY: ResearchSpecialistPlugin, enable_web_search=true
universes/MINE/domains/cooking/domain.json...Type 4 Cooking: ResearchSpecialistPlugin, web search enabled
universes/MINE/domains/exframe/domain.json...Type 3 ExFrame: ExFrameSpecialistPlugin, document auto-discovery
universes/MINE/domains/poetry_domain/domain.json...Type 1 Creative: creative_mode=true, temperature=0.8
universes/MINE/domains/llm_consciousness/domain.json...Type 2 Knowledge: patterns about hallucination, tool loops

## Frontend

generic_framework/frontend/index.html...Alpine.js SPA: domain dropdown, query input, results display, admin panel

## Documentation

docs/INDEX.md...This file: master index of all code files with one-line summaries
roles.md...Roles and responsibilities: System Owner, Claude Code, Domain Expert, etc.
README.md...Main documentation: overview, installation, self-healing features, domain types, API reference
INSTALL.md...Installation guide for Docker deployment
PLUGIN_ARCHITECTURE.md...Plugin development guide
RELEASE_NOTES.md...Version release notes
CHANGELOG.md...Complete version history

## Archive

.archive/old-root-docs/...Archived documentation (not tracked): old planning docs, outdated concepts
.archive/old-concepts/...Archived concept docs: superseded by new documentation
