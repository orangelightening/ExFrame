# Changelog

All notable changes to EEFrame will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
