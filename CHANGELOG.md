# Changelog

All notable changes to EEFrame will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.1] - 2026-01-24

### Fixed
- **Smart truncation for pattern embeddings** - Improved semantic diversity when patterns exceed the 256-token limit
  - Replaced simple truncation (name + solution only) with priority-based field inclusion
  - New strategy: name + solution (800 chars) + description (200 chars) when space permits
  - Fallback to name + solution (800 chars) + problem (200 chars) if no description
  - Final fallback to name + solution (1000 chars) only
  - This improves search result quality by preserving more semantic context in embeddings
  - See SA-1 checklist for implementation details

### Changed
- **Embedding regeneration required** - All existing embeddings must be regenerated after this update
  - Use `POST /api/embeddings/generate?domain={domain}` for each domain
  - All domains now show 100% embedding coverage

## [1.1.0] - 2026-01-09

### Router & Formatter Plugin Systems

This release completes the pluggable transformation architecture by adding Router and Formatter plugins. **All transformation logic is now pluggable.**

### Added

#### Router Plugin System
- **RouterPlugin Interface**: Abstract base for query routing strategies
- **RouteResult dataclass**: Structured routing results with strategy, confidence, and reasoning
- **Router configurations** in domain.json
- **4 router implementations**:
  - `ConfidenceBasedRouter` - Select highest-scoring specialist (default)
  - `MultiSpecialistRouter` - Route to top-N specialists
  - `ParallelRouter` - All specialists in parallel
  - `SequentialRouter` - Progressive refinement through specialists
  - `HierarchyRouter` - Specialist → fallback1 → fallback2 chains
- **GenericDomain.router_query()** - Full routing information API

#### Response Aggregation
- **ResponseAggregator class**: Merge multi-specialist responses
- **4 aggregation strategies**:
  - `merge_all` - Combine patterns, re-rank by combined score
  - `first_wins` - Use first specialist's response
  - `side_by_side` - Show each specialist's response separately
  - `best_pattern` - Select best pattern across all specialists
- **Deduplication** of patterns across specialists
- **Combined scoring** (pattern confidence × specialist confidence)

#### Formatter Plugin System
- **FormatterPlugin Interface**: Abstract base for output formatting
- **FormattedResponse dataclass**: Container with content, MIME type, and metadata
- **Formatter configurations** in domain.json
- **Runtime format override**: `format_response(data, format_type="json")`
- **7 formatter implementations**:
  - `MarkdownFormatter` - Full-featured Markdown (default)
  - `ConciseMarkdownFormatter` - Brief Markdown
  - `JSONFormatter` - Structured JSON
  - `CompactJSONFormatter` - Minified JSON
  - `PrettyJSONFormatter` - Formatted JSON
  - `CompactFormatter` - Terminal-friendly plain text
  - `UltraCompactFormatter` - Pattern names only
  - `TableFormatter` - Tabular format

#### Testing
- **Comprehensive formatter tests**: 7/7 passing
- **Test coverage**: All default formatters and aggregation strategies
- **Sample data**: Real pattern data from binary_symmetry domain

### Changed

#### GenericDomain Enhancements
- **Router loading**: `_initialize_router()` loads router from domain.json
- **Formatter loading**: `_initialize_formatter()` loads formatter from domain.json
- **Enhanced routing**: `route_query()` returns full RouteResult with metadata
- **Format override**: `get_formatter_for_type()` for runtime format selection
- **Backward compatibility**: Existing domains work without explicit router/formatter config

### Configuration Examples

**Router configuration** (domain.json):
```json
{
  "router": {
    "module": "plugins.routers.confidence_router",
    "class": "ConfidenceBasedRouter",
    "config": {
      "threshold": 0.30,
      "fallback_to_generalist": true
    }
  }
}
```

**Formatter configuration** (domain.json):
```json
{
  "formatter": {
    "module": "plugins.formatters.markdown_formatter",
    "class": "MarkdownFormatter",
    "config": {
      "include_metadata": true,
      "max_examples_per_pattern": 3
    }
  }
}
```

### Technical Details

**Architecture Progress: ~70% of transformation logic is pluggable**

| Component | Status |
|-----------|--------|
| Specialist Plugins | ✅ Complete |
| Knowledge Base Plugins | ✅ Complete |
| Router Plugins | ✅ Complete |
| Formatter Plugins | ✅ Complete |
| Response Aggregation | ✅ Complete |

**Still hardcoded** (future work):
- Query orchestration pipeline (specialist → aggregation → formatter)
- Specialist `format_response()` methods (to be deprecated)

### Migration Notes

**For domain developers**:
- No breaking changes - existing domains continue to work
- Add router config to customize routing strategy
- Add formatter config to customize output format
- Use `domain.route_query()` for full routing information
- Use `domain.format_response(data, format="json")` for format override

**For API developers**:
- Add `?format=json` parameter to `/api/query` endpoint
- Use `domain.get_formatter_for_type()` to handle format requests
- Return appropriate `Content-Type` headers based on formatter

### Performance Notes

- **Router overhead**: Negligible (<1ms per query)
- **Formatter overhead**: Minimal (mostly string formatting)
- **Parallel routing**: Multiple KB searches may increase latency
- **Aggregation cost**: O(n) where n = total patterns from all specialists

### Known Limitations

- **No format negotiation**: Accept-header content negotiation not implemented (v1.2)
- **Specialist formatting**: Specialists still have `format_response()` methods
- **Limited testing**: Multi-specialist scenarios need more coverage

### Future Roadmap (v1.2+)

- **v1.2**: Content negotiation (Accept headers), authentication
- **v1.3**: Additional formatters (HTML, Slack, Voice, Rich Terminal)
- **v1.4**: Advanced routers (category-based, semantic similarity)
- **v2.0**: Distributed architecture, multi-node deployment

---

## [1.0.0] - 2026-01-09

### Major Release - Plugin Architecture Foundation

This release establishes EEFrame as a domain-agnostic, plugin-based knowledge management system. The core philosophy: **data and composition are configuration, all transformation logic is pluggable.**

### Added

#### Core Plugin System
- **SpecialistPlugin Interface**: 3-method interface (can_handle, process_query, format_response)
- **KnowledgeBasePlugin Interface**: Abstract storage layer for pattern backends
- **GenericDomain**: Universal domain class supporting both static and dynamic specialists
- **Dynamic specialist loading** from domain.json configuration
- **Fallback specialist system** for handling unmatched queries

#### Knowledge Base Implementations
- **JSONKnowledgeBase**: Default file-based storage with pattern indexing
- **SQLiteKnowledgeBase**: Proof-of-concept alternative backend with FTS5 full-text search
- **Pattern search** with category filtering and relevance scoring
- **Pattern CRUD operations**: add, update, delete, record feedback

#### Domain Management
- **Domain auto-discovery**: Automatic domain loading from `data/patterns/*/`
- **Domain configuration via JSON**: domain.json for metadata, plugins, specialists
- **Specialist configuration**: JSON-based specialist definition and loading
- **7 production domains**:
  - binary_symmetry (16 patterns, 3 specialists)
  - cooking (21 patterns, 1 specialist)
  - llm_consciousness (11 patterns, 2 specialists)
  - python (6 patterns, 1 specialist)
  - gardening, first_aid, diy (template domains)

#### API & Frontend
- **Specialist listing endpoint**: `/api/domains/{domain_id}/specialists`
- **Pattern listing endpoint**: `/api/domains/{domain_id}/patterns`
- **Pattern detail endpoint**: `/api/domains/{domain_id}/patterns/{pattern_id}`
- **Domain health endpoint**: `/api/domains/{domain_id}/health`
- **Query tracing** with specialist selection details
- **Single-page Alpine.js frontend** with domain switching
- **Pattern browser** with category filtering
- **Specialist display** with keywords and categories

#### Monitoring & Observability
- **Prometheus metrics**: Query counts, specialist selection, response times
- **Health checks** at domain and system level
- **Grafana dashboards** for system monitoring
- **Loki log aggregation** with Promtail
- **Query trace storage** and retrieval

### Changed

#### Architecture
- Moved from **domain-specific code** to **plugin-based architecture**
- Separated **data (patterns)** from **transformation logic (plugins)**
- Domains are now **orchestrators**, not implementations
- Specialists are **plugins**, not hardcoded classes

#### API Structure
- Unified domain loading through `GenericDomain`
- Specialist plugins loaded dynamically from domain.json
- Knowledge base plugins loaded dynamically from domain.json
- Fallback to JSONKnowledgeBase if no plugin specified

### Fixed

- API endpoints now correctly access plugin attributes (keywords, categories)
- Pattern search returns all patterns when no category specified
- Pattern detail endpoint uses correct method name (`get_by_id`)
- Specialist endpoint handles missing descriptions gracefully
- Frontend displays specialists and patterns for all domains

### Technical Details

#### Plugin Interfaces

**SpecialistPlugin** (`core/specialist_plugin.py`)
```python
class SpecialistPlugin(ABC):
    name: str = "Specialist"

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """Return confidence score 0.0 to 1.0"""

    @abstractmethod
    async def process_query(self, query: str, context: Dict) -> Dict:
        """Process query and return response data"""

    @abstractmethod
    def format_response(self, response_data: Dict) -> str:
        """Format response for user consumption"""
```

**KnowledgeBasePlugin** (`core/knowledge_base_plugin.py`)
```python
class KnowledgeBasePlugin(ABC):
    name: str = "KnowledgeBase"

    @abstractmethod
    async def load_patterns(self) -> None:
        """Load patterns from storage"""

    @abstractmethod
    async def search(self, query: str, category: Optional[str], limit: int) -> List[Dict]:
        """Search for matching patterns"""

    @abstractmethod
    async def get_by_id(self, pattern_id: str) -> Optional[Dict]:
        """Get pattern by ID"""

    @abstractmethod
    def get_all_categories(self) -> List[str]:
        """Get all categories"""

    @abstractmethod
    def get_pattern_count(self) -> int:
        """Get total pattern count"""
```

#### Domain Configuration Structure

```json
{
  "domain_id": "example_domain",
  "domain_name": "Example Domain",
  "description": "Domain description",
  "version": "1.0.0",

  "knowledge_base": {
    "type": "json",
    "module": "knowledge.json_kb",
    "class": "JSONKnowledgeBase"
  },

  "plugins": [
    {
      "plugin_id": "specialist_1",
      "module": "plugins.example_domain.specialist_1",
      "class": "SpecialistPlugin",
      "enabled": true,
      "config": {
        "keywords": ["keyword1", "keyword2"],
        "categories": ["category1"],
        "threshold": 0.30
      }
    }
  ],

  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2"]
}
```

### Migration Notes

#### For Domain Developers

If you have existing domain code:

1. **Create domain.json**: Add domain configuration file
2. **Implement plugins**: Convert specialists to SpecialistPlugin
3. **Update imports**: Use `core.specialist_plugin` and `core.knowledge_base_plugin`
4. **Configure plugins**: Add plugin entries to domain.json

#### Pattern Structure

Patterns now support both old and new field names for compatibility:
- `type` or `pattern_type`
- `category` or `tags[0]`
- `id` or `pattern_id`

### Performance

- **7 domains** loaded in ~2 seconds
- **55+ patterns** indexed and searchable
- **9 specialists** with confidence-based routing
- **Average query time**: <500ms (excluding LLM calls)

### Known Limitations

- **Router logic** still hardcoded in GenericDomain (planned for v1.1)
- **Formatter logic** embedded in specialists (planned for v1.1)
- **No authentication** (planned for v1.2)
- **Single-node deployment** only (planned for v2.0)

### Future Roadmap

#### v1.1 - Router & Formatter Plugins
- RouterPlugin interface for query routing strategies
- FormatterPlugin interface for output formatting
- Multi-specialist routing (parallel, sequential)
- Multiple output formats (Markdown, JSON, HTML)

#### v1.2 - Enterprise Features
- User authentication and authorization
- Rate limiting and quotas
- Audit logging
- Pattern versioning

#### v2.0 - Distributed Architecture
- Multi-node deployment
- Distributed pattern storage
- Load balancing and failover
- GraphQL API

### Contributors

- Architecture design: Peter (user guidance)
- Implementation: Claude (Anthropic)

### Links

- **Repository**: [GitHub link TBD]
- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues link TBD]

---

## [0.9.0] - Previous Development

### Added
- Initial domain system
- Basic pattern storage
- Simple specialist classes
- Web UI prototype

### Changed
- Proof of concept implementation

---

For release notes before 0.9.0, see git history.
