# EEFrame Plugin Architecture

**Version 1.0.0**

## Core Philosophy

EEFrame is built on a simple principle:

> **Data and composition are configuration. All transformation logic is pluggable.**

This means:
- ✅ **Patterns** are data (JSON files, not code)
- ✅ **Domains** are orchestrators (configuration, not plugins)
- ✅ **Specialists** are plugins (transformation logic)
- ✅ **Knowledge bases** are plugins (storage backends)

## Why This Architecture?

### Separation of Concerns

| Aspect | Approach | Benefit |
|--------|----------|---------|
| **Knowledge** | JSON data files | Easy to edit, version control, review |
| **Composition** | Domain configuration | No code changes to add domains |
| **Transformation** | Plugin system | Extensible, testable, swappable |

### Before vs After

#### Before (Domain-Specific Code)
```python
# Each domain was a custom class
class CookingDomain(Domain):
    def __init__(self):
        self._specialists = {
            "chicken": ChickenSpecialist(),  # Hardcoded
            "baking": BakingSpecialist(),    # Hardcoded
        }

# Adding a domain required:
# 1. Creating a new domain class
# 2. Creating specialist classes
# 3. Registering in app.py
# 4. Code changes and deployment
```

#### After (Plugin Architecture)
```python
# Domain is generic, loads from config
domain = GenericDomain(domain_config)

# Adding a domain requires:
# 1. Create data/patterns/mydomain/patterns.json
# 2. Create data/patterns/mydomain/domain.json
# 3. Restart application
# 4. No code changes!
```

## Plugin Types

### 1. Specialist Plugins

**Purpose**: Answer questions in a specific domain area.

**Interface**: `core/specialist_plugin.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SpecialistPlugin(ABC):
    """
    A specialist answers questions in its domain.

    Interface: 3 methods. That's all.
    """

    name: str = "Specialist"

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """
        Can this specialist handle the query?

        Returns: Confidence score 0.0 to 1.0
        """
        pass

    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process the query.

        Returns: Dict with at least:
            - answer: str
            - patterns: List[dict]
            - confidence: float
        """
        pass

    @abstractmethod
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format response for user.

        Returns: String to display
        """
        pass
```

**Example Implementation**:

```python
# plugins/llm_consciousness/failure_detection.py
from core.specialist_plugin import SpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase

class FailureDetectionPlugin(SpecialistPlugin):
    name = "Failure Detection"
    specialist_id = "failure_detection"

    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict = None):
        self.kb = knowledge_base
        self.config = config or {}

        self.keywords = self.config.get("keywords", [
            "hallucination", "tool loop", "detect"
        ])
        self.categories = self.config.get("categories", [
            "failure_mode", "detection"
        ])
        self.threshold = self.config.get("threshold", 0.30)

    def can_handle(self, query: str) -> float:
        """Calculate confidence score."""
        score = 0.0
        query_lower = query.lower()

        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 0.15

        return min(score, 1.0)

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process query against knowledge base."""
        patterns = await self.kb.search(
            query,
            category="failure_mode",
            limit=5
        )

        return {
            "query": query,
            "specialist": "failure_detection",
            "patterns_found": len(patterns),
            "patterns": patterns,
            "answer": self._synthesize_answer(query, patterns),
            "confidence": self.can_handle(query)
        }

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format for user display."""
        patterns = response_data.get("patterns", [])

        if not patterns:
            return f"No patterns found for: {response_data.get('query', '')}"

        result = f"[Failure Detection] Found {len(patterns)} patterns:\n\n"

        for pattern in patterns[:3]:
            result += f"**{pattern.get('name', 'Unknown')}**\n"
            result += f"Type: {pattern.get('pattern_type', 'N/A')}\n\n"

            if "problem" in pattern:
                result += f"**Problem:** {pattern['problem']}\n\n"

            if "solution" in pattern:
                result += f"**Solution:** {pattern['solution']}\n\n"

        return result

    def _synthesize_answer(self, query: str, patterns: List) -> str:
        """Create answer from patterns."""
        if not patterns:
            return "No relevant patterns found."
        return f"See {patterns[0].get('name')}: {patterns[0].get('solution', '')[:100]}..."
```

**Key Points**:
- No inheritance required (just implement 3 methods)
- Configuration via constructor (keywords, categories, threshold)
- Access to knowledge base for pattern search
- Simple, testable interface

### 2. Knowledge Base Plugins

**Purpose**: Store and retrieve patterns.

**Interface**: `core/knowledge_base_plugin.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class KnowledgeBasePlugin(ABC):
    """
    A knowledge base stores and retrieves patterns.

    This abstraction enables different backends while keeping
    the interface consistent for specialists.
    """

    name: str = "KnowledgeBase"

    @abstractmethod
    async def load_patterns(self) -> None:
        """Load patterns from storage."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        **filters
    ) -> List[Dict[str, Any]]:
        """Search for patterns."""
        pass

    @abstractmethod
    async def get_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get pattern by ID."""
        pass

    @abstractmethod
    def get_all_categories(self) -> List[str]:
        """Get all categories."""
        pass

    @abstractmethod
    def get_pattern_count(self) -> int:
        """Get total pattern count."""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Check knowledge base health."""
        return {
            "status": "healthy",
            "patterns_loaded": self.get_pattern_count(),
            "categories": self.get_all_categories(),
            "backend": self.name
        }
```

**Example Implementation** (JSON):

```python
# knowledge/json_kb.py
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from core.knowledge_base_plugin import KnowledgeBasePlugin

class JSONKnowledgeBase(KnowledgeBasePlugin):
    """JSON file-based knowledge base."""

    name = "JSON Knowledge Base"

    def __init__(self, config):
        self.config = config
        self.storage_file = Path(config.storage_path) / "patterns.json"
        self._patterns = []
        self._pattern_index = {}
        self._loaded = False

    async def load_patterns(self) -> None:
        """Load patterns from JSON file."""
        with open(self.storage_file, 'r') as f:
            self._patterns = json.load(f)

        # Build index for fast lookup
        self._pattern_index = {}
        for p in self._patterns:
            key = p.get('pattern_id') or p.get('id') or p.get('name', '')
            if key:
                self._pattern_index[key] = p

        self._loaded = True

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        **filters
    ) -> List[Dict[str, Any]]:
        """Search patterns by keyword matching."""
        query_lower = query.lower()
        query_terms = self._extract_terms(query_lower)

        scored_patterns = []
        for pattern in self._patterns:
            # Category filter
            if category:
                pattern_cats = pattern.get('pattern_type', '')
                pattern_tags = pattern.get('tags', [])
                if category != pattern_cats and category not in pattern_tags:
                    continue

            score = self._calculate_relevance(pattern, query_lower, query_terms)
            if score > 0:
                scored_patterns.append((pattern, score))

        # Sort by score
        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored_patterns[:limit]]

    async def get_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get pattern by ID."""
        return self._pattern_index.get(pattern_id)

    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set()
        for p in self._patterns:
            if 'pattern_type' in p:
                categories.add(p['pattern_type'])
            if 'tags' in p:
                categories.update(p['tags'])
        return sorted(list(categories))

    def get_pattern_count(self) -> int:
        """Get total pattern count."""
        return len(self._patterns)

    def _extract_terms(self, query: str) -> List[str]:
        """Extract significant terms from query."""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on'}
        words = re.findall(r'\b\w+\b', query.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _calculate_relevance(self, pattern: Dict, query_lower: str, terms: List[str]) -> float:
        """Calculate relevance score."""
        score = 0.0

        # Name matches (highest weight)
        name = pattern.get('name', '').lower()
        for term in terms:
            if term in name:
                score += 2.0

        # Description matches
        description = pattern.get('description', '').lower()
        for term in terms:
            if term in description:
                score += 1.0

        # Tag matches
        tags = [t.lower() for t in pattern.get('tags', [])]
        for term in terms:
            if term in tags:
                score += 1.5

        # Apply confidence
        confidence = pattern.get('confidence', 0.5)
        return score * confidence
```

**Example Implementation** (SQLite):

```python
# knowledge/sqlite_kb.py
import aiosqlite
from core.knowledge_base_plugin import KnowledgeBasePlugin

class SQLiteKnowledgeBase(KnowledgeBasePlugin):
    """SQLite-based knowledge base with FTS5."""

    name = "SQLite Knowledge Base"

    def __init__(self, config):
        self.config = config
        self.db_path = config.storage_path / "patterns.db"

    async def load_patterns(self) -> None:
        """Initialize database."""
        await self._init_db()

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        **filters
    ) -> List[Dict[str, Any]]:
        """Full-text search using FTS5."""
        async with aiosqlite.connect(self.db_path) as db:
            if category:
                sql = """
                    SELECT p.* FROM patterns p
                    LEFT JOIN patterns_fts fts ON p.rowid = fts.rowid
                    WHERE p.pattern_type = ? OR p.tags LIKE ?
                    AND patterns_fts MATCH ?
                    LIMIT ?
                """
                params = (category, f"%{category}%", query, limit)
            else:
                sql = """
                    SELECT p.* FROM patterns p
                    LEFT JOIN patterns_fts fts ON p.rowid = fts.rowid
                    WHERE patterns_fts MATCH ?
                    LIMIT ?
                """
                params = (query, limit)

            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
```

**Key Points**:
- Same interface, different backends
- JSON for simplicity, SQLite for performance
- Easy to add Vector DB, Graph DB, etc.
- Async interface throughout

## Domain Configuration

### Structure

```json
{
  "domain_id": "example_domain",
  "domain_name": "Example Knowledge Domain",
  "description": "What this domain covers",
  "version": "1.0.0",
  "created_at": "2026-01-09T00:00:00Z",
  "updated_at": "2026-01-09T00:00:00Z",

  "knowledge_base": {
    "type": "json",
    "module": "knowledge.json_kb",
    "class": "JSONKnowledgeBase",
    "description": "JSON file storage"
  },

  "plugins": [
    {
      "plugin_id": "specialist_1",
      "name": "First Specialist",
      "description": "Specializes in X",
      "module": "plugins.example_domain.specialist_1",
      "class": "SpecialistPlugin",
      "enabled": true,
      "config": {
        "keywords": ["keyword1", "keyword2"],
        "categories": ["category1", "category2"],
        "threshold": 0.30
      }
    }
  ],

  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2"],

  "ui_config": {
    "placeholder_text": "Ask about X...",
    "example_queries": [
      "Example question 1",
      "Example question 2"
    ],
    "icon": "🔍",
    "color": "#9C27B0"
  }
}
```

### Location

```
data/patterns/
├── binary_symmetry/
│   ├── domain.json          # Domain configuration
│   └── patterns.json        # Pattern data
├── cooking/
│   ├── domain.json
│   └── patterns.json
├── llm_consciousness/
│   ├── domain.json
│   └── patterns.json
└── my_new_domain/
    ├── domain.json          # Add your domain here
    └── patterns.json
```

## Generic Domain

The `GenericDomain` class is the universal orchestrator that loads configuration and plugins.

**File**: `core/generic_domain.py`

### Key Responsibilities

1. **Load domain configuration** from `domain.json`
2. **Initialize knowledge base** plugin
3. **Load specialist plugins** from configuration
4. **Route queries** to appropriate specialist
5. **Provide fallback** to generalist

### Usage

```python
from core.generic_domain import GenericDomain
from core.domain_config import DomainConfig

# Create domain config
config = DomainConfig(
    domain_id="mydomain",
    domain_name="My Domain",
    storage_path=Path("data/patterns/mydomain")
)

# Create generic domain
domain = GenericDomain(config)

# Initialize (loads config, plugins, patterns)
await domain.initialize()

# Use the domain
result = await domain.process_query("What is X?")
```

### Plugin Loading

```python
async def _initialize_specialists(self) -> None:
    """Load specialist plugins from domain.json."""
    plugin_specs = self._domain_config.get("plugins", [])

    for spec in plugin_specs:
        if not spec.get("enabled", True):
            continue

        # Dynamic import
        module = importlib.import_module(spec["module"])
        plugin_class = getattr(module, spec["class"])

        # Instantiate with KB and config
        plugin = plugin_class(self._knowledge_base, spec.get("config"))

        # Register specialist
        self._specialists[plugin.specialist_id] = plugin
```

## Adding a New Domain

### Step 1: Create Domain Structure

```bash
mkdir -p data/patterns/my_new_domain
```

### Step 2: Create Patterns

```json
// data/patterns/my_new_domain/patterns.json
[
  {
    "id": "my_new_domain_001",
    "name": "Example Pattern",
    "pattern_type": "technique",
    "description": "What this pattern covers",
    "problem": "The problem it solves",
    "solution": "How to solve it",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "tags": ["tag1", "tag2"],
    "confidence": 0.90
  }
]
```

### Step 3: Create Domain Configuration

```json
// data/patterns/my_new_domain/domain.json
{
  "domain_id": "my_new_domain",
  "domain_name": "My New Domain",
  "description": "What this domain is about",
  "version": "1.0.0",
  "created_at": "2026-01-09T00:00:00Z",
  "updated_at": "2026-01-09T00:00:00Z",

  "knowledge_base": {
    "type": "json",
    "module": "knowledge.json_kb",
    "class": "JSONKnowledgeBase"
  },

  "plugins": [
    {
      "plugin_id": "my_specialist",
      "name": "My Specialist",
      "description": "What this specialist does",
      "module": "plugins.my_new_domain.my_specialist",
      "class": "MySpecialistPlugin",
      "enabled": true,
      "config": {
        "keywords": ["keyword1", "keyword2"],
        "categories": ["category1"],
        "threshold": 0.30
      }
    }
  ],

  "categories": ["category1", "category2"],
  "tags": ["tag1", "tag2"],

  "ui_config": {
    "placeholder_text": "Ask about my domain...",
    "example_queries": [
      "Example question 1",
      "Example question 2"
    ],
    "icon": "🔍",
    "color": "#9C27B0"
  }
}
```

### Step 4: Create Specialist Plugin

```python
# generic_framework/plugins/my_new_domain/my_specialist.py
from core.specialist_plugin import SpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase
from typing import Dict, Any, Optional

class MySpecialistPlugin(SpecialistPlugin):
    name = "My Specialist"
    specialist_id = "my_specialist"

    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict = None):
        self.kb = knowledge_base
        self.config = config or {}

        self.keywords = self.config.get("keywords", [])
        self.categories = self.config.get("categories", [])
        self.threshold = self.config.get("threshold", 0.30)

    def can_handle(self, query: str) -> float:
        score = 0.0
        query_lower = query.lower()

        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 0.15

        return min(score, 1.0)

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        patterns = await self.kb.search(query, limit=5)

        return {
            "query": query,
            "specialist": "my_specialist",
            "patterns_found": len(patterns),
            "patterns": patterns,
            "answer": self._synthesize_answer(query, patterns),
            "confidence": self.can_handle(query)
        }

    def format_response(self, response_data: Dict[str, Any]) -> str:
        patterns = response_data.get("patterns", [])

        if not patterns:
            return "No patterns found."

        result = f"[My Specialist] Found {len(patterns)} patterns:\n\n"
        for pattern in patterns[:3]:
            result += f"**{pattern.get('name')}**\n"
            result += f"{pattern.get('solution', '')}\n\n"

        return result

    def _synthesize_answer(self, query: str, patterns: list) -> str:
        if not patterns:
            return "No relevant patterns found."
        return f"See {patterns[0].get('name')}: {patterns[0].get('solution', '')[:100]}..."
```

### Step 5: Restart Application

```bash
docker-compose restart eeframe-app
```

Your new domain will be auto-discovered and loaded!

## Future Plugin Types

### Router Plugins (v1.1)

For flexible query routing strategies:

```python
class RouterPlugin(ABC):
    @abstractmethod
    async def route(
        self,
        query: str,
        specialists: Dict[str, SpecialistPlugin]
    ) -> RouterResult:
        """Select which specialist(s) should handle the query."""
        pass
```

**Implementations**:
- `ConfidenceBasedRouter` (current behavior)
- `MultiSpecialistRouter` (parallel routing)
- `HierarchyRouter` (specialist → fallback → generalist)

### Formatter Plugins (v1.1)

For multiple output formats:

```python
class FormatterPlugin(ABC):
    @abstractmethod
    def format(self, response_data: Dict[str, Any]) -> str:
        """Format response for user."""
        pass
```

**Implementations**:
- `MarkdownFormatter`
- `JSONFormatter`
- `HTMLFormatter`
- `ConciseFormatter`

### Monitoring Plugins (v1.2)

For health and performance:

```python
class MonitoringPlugin(ABC):
    @abstractmethod
    async def check_health(self, domain) -> HealthStatus:
        """Check domain health."""
        pass

    @abstractmethod
    async def track_metrics(self, event: Event) -> None:
        """Track domain events."""
        pass
```

## Best Practices

### 1. Keep Plugins Simple

Each plugin should do one thing well:

- ✅ Specialist: Answer questions in a domain
- ✅ Knowledge Base: Store and retrieve patterns
- ✅ Router: Route queries to specialists

### 2. Use Configuration

Make plugins configurable via JSON, not code:

```python
# Good
self.keywords = self.config.get("keywords", ["default"])

# Bad
self.keywords = ["hardcoded", "keywords"]
```

### 3. Implement All Methods

Even if a method seems unnecessary, implement it:

```python
def format_response(self, response_data: Dict) -> str:
    """Always provide formatted output."""
    return str(response_data)
```

### 4. Handle Errors Gracefully

```python
async def process_query(self, query: str, context: Dict = None) -> Dict:
    try:
        patterns = await self.kb.search(query)
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "patterns": [],
            "confidence": 0.0
        }
```

### 5. Document Your Plugin

```python
class MySpecialistPlugin(SpecialistPlugin):
    """
    My domain specialist.

    Handles queries about:
    - Topic 1
    - Topic 2

    Configuration:
        keywords: List of keywords for matching
        categories: List of categories to search
        threshold: Minimum confidence score (0.0-1.0)
    """
```

## Testing Plugins

### Unit Test Example

```python
import pytest
from plugins.my_new_domain.my_specialist import MySpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase

@pytest.fixture
def specialist():
    kb = JSONKnowledgeBase(test_config)
    plugin = MySpecialistPlugin(kb, {"keywords": ["test"]})
    return plugin

def test_can_handle(specialist):
    assert specialist.can_handle("test query") > 0
    assert specialist.can_handle("unrelated query") == 0

@pytest.mark.asyncio
async def test_process_query(specialist):
    result = await specialist.process_query("test query")
    assert "answer" in result
    assert "confidence" in result
```

## Troubleshooting

### Plugin Not Loading

1. Check `domain.json` syntax: `python3 -m json.tool domain.json`
2. Verify module path: `from plugins.my_domain.my_plugin import MyPlugin`
3. Check specialist_id is unique
4. Look for import errors in container logs

### Patterns Not Found

1. Verify `patterns.json` exists in domain directory
2. Check pattern IDs are unique
3. Ensure patterns are valid JSON
4. Test search directly: `curl http://localhost:3000/api/domains/{id}/patterns`

### Specialist Not Selected

1. Check `can_handle()` returns scores > threshold
2. Verify keywords match query terms
3. Ensure specialist is enabled in `domain.json`
4. Check domain health endpoint

## Resources

- **Core Interfaces**: `core/specialist_plugin.py`, `core/knowledge_base_plugin.py`
- **Generic Domain**: `core/generic_domain.py`
- **Examples**: `plugins/llm_consciousness/`, `plugins/binary_symmetry/`
- **Configuration**: `data/patterns/*/domain.json`

## Version History

- **1.0.0** (2026-01-09): Initial plugin architecture
  - SpecialistPlugin interface
  - KnowledgeBasePlugin interface
  - GenericDomain orchestrator
  - 7 production domains
  - 9 specialist plugins
