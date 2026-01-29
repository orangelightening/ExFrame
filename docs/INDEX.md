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

**Package name**: `exframe` (pip install name, pyproject.toml)
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

generic_framework/plugins/enrichers/llm_enricher.py...LLMEnricher: synthesizes responses, supports web search context
generic_framework/plugins/enrichers/reply_formation.py...ReplyFormationEnricher: displays web sources with 🌐 emoji and URLs
generic_framework/plugins/enrichers/llm_fallback_enricher.py...LLMFallbackEnricher: provides LLM response when patterns are weak

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
docs/README.md...Quick start guide

## Archive

.archive/old-root-docs/...Archived documentation (not tracked): old planning docs, outdated concepts
.archive/old-concepts/...Archived concept docs: superseded by new documentation
