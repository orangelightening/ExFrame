# Generic Domain Framework Design

## Overview

This document describes the design for abstracting the assistant framework into a generic, domain-agnostic system that can be configured for any domain (Cooking, OMV, Kubernetes, Docker, Python, DIY, etc.).

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GENERIC ASSISTANT FRAMEWORK                     │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     Domain Configuration Layer                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │ Domain Spec  │  │ Collectors   │  │ Specialists  │          │  │
│  │  │ (YAML/JSON)  │  │ Config       │  │ Config       │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                          ↓                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Core Abstraction Layer                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   Domain     │  │  Collector   │  │ Specialist   │          │  │
│  │  │   Interface  │  │  Interface   │  │  Interface   │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                          ↓                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Implementation Layer                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   Cooking    │  │ AllRecipes   │  │ Baking       │          │  │
│  │  │   Domain     │  │ WebCollector │  │ Specialist   │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │                                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   Python     │  │ GitHubAPI    │  │ Django       │          │  │
│  │  │   Domain     │  │ Collector    │  │ Specialist   │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                          ↓                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Assistant Engine                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │  Query       │  │  Context     │  │  Response    │          │  │
│  │  │  Processor   │  │  Selector    │  │  Formatter   │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Interfaces

### 1. Domain Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class CollectorType(Enum):
    """Types of data collectors."""
    WEB_SCRAPER = "web_scraper"
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    PROMETHEUS = "prometheus"
    LOKI = "loki"
    SSH = "ssh"
    RPC = "rpc"
    CUSTOM = "custom"


@dataclass
class DomainConfig:
    """Configuration for a specific domain."""
    domain_id: str
    domain_name: str
    version: str
    description: str

    # Data sources
    data_sources: List[str]  # URLs, APIs, file paths
    default_collector_type: CollectorType

    # Taxonomy
    categories: List[str]
    tags: List[str]

    # Knowledge base settings
    pattern_storage_path: str
    pattern_format: str  # 'yaml' or 'json'
    pattern_schema: Dict[str, Any]

    # Feature flags
    enabled_features: List[str]

    # Domain-specific settings
    domain_settings: Dict[str, Any]


class Domain(ABC):
    """Abstract base class for all domain implementations."""

    def __init__(self, config: DomainConfig):
        self.config = config
        self._collectors: Dict[str, 'Collector'] = {}
        self._specialists: Dict[str, 'Specialist'] = {}

    @property
    @abstractmethod
    def domain_id(self) -> str:
        """Unique identifier for this domain."""
        pass

    @property
    @abstractmethod
    def domain_name(self) -> str:
        """Human-readable name."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize domain-specific resources."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of domain services."""
        pass

    @abstractmethod
    def get_collector(self, collector_type: str) -> 'Collector':
        """Get a collector instance."""
        pass

    @abstractmethod
    def get_specialist(self, specialist_id: str) -> 'Specialist':
        """Get a specialist instance."""
        pass

    @abstractmethod
    def get_specialist_for_query(self, query: str) -> Optional['Specialist']:
        """Select appropriate specialist based on query."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up domain resources."""
        pass
```

### 2. Collector Interface

```python
@dataclass
class CollectorConfig:
    """Configuration for a data collector."""
    collector_type: CollectorType
    name: str
    description: str

    # Connection settings
    endpoint: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    headers: Dict[str, str] = None

    # Domain-specific configuration
    scraping_rules: Dict[str, Any] = None
    api_paths: Dict[str, str] = None


class Collector(ABC):
    """Abstract base class for data collectors."""

    def __init__(self, config: CollectorConfig):
        self.config = config
        self._initialized = False

    @property
    @abstractmethod
    def collector_type(self) -> CollectorType:
        """Type of this collector."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the collector."""
        pass

    @abstractmethod
    async def collect(self, source: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect data from a source."""
        pass

    @abstractmethod
    async def collect_batch(self, sources: List[str]) -> List[Dict[str, Any]]:
        """Collect data from multiple sources."""
        pass

    @abstractmethod
    async def is_available(self, source: str) -> bool:
        """Check if source is available."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources."""
        pass
```

### 3. Specialist Interface

```python
@dataclass
class SpecialistConfig:
    """Configuration for a domain specialist."""
    specialist_id: str
    name: str
    description: str

    # Expertise areas
    expertise_keywords: List[str]
    expertise_categories: List[str]

    # Knowledge base
    knowledge_categories: List[str]
    pattern_filters: Dict[str, Any] = None

    # Response preferences
    response_format: str = "structured"
    include_examples: bool = True
    confidence_threshold: float = 0.6


class Specialist(ABC):
    """Abstract base class for domain specialists."""

    def __init__(self, config: SpecialistConfig, knowledge_base: 'KnowledgeBase'):
        self.config = config
        self.knowledge_base = knowledge_base

    @property
    @abstractmethod
    def specialist_id(self) -> str:
        """Unique identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """Return confidence score for handling this query (0-1)."""
        pass

    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a query within this specialist's domain."""
        pass

    @abstractmethod
    def get_relevant_patterns(self, query: str) -> List[Any]:
        """Get relevant knowledge patterns for a query."""
        pass

    @abstractmethod
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format response for user."""
        pass
```

### 4. Knowledge Base Interface

```python
@dataclass
class KnowledgeBaseConfig:
    """Configuration for knowledge base storage."""
    storage_path: str
    pattern_format: str  # 'yaml' or 'json'
    pattern_schema: Dict[str, Any]

    # Search settings
    search_algorithm: str = "hybrid"  # "keyword", "semantic", "hybrid"
    similarity_threshold: float = 0.5
    max_results: int = 10

    # Learning settings
    enable_learning: bool = True
    feedback_decay: float = 0.95


class KnowledgeBase(ABC):
    """Abstract base class for knowledge base storage."""

    def __init__(self, config: KnowledgeBaseConfig):
        self.config = config
        self._patterns: List[Any] = []

    @abstractmethod
    async def load_patterns(self) -> List[Any]:
        """Load all patterns from storage."""
        pass

    @abstractmethod
    async def save_pattern(self, pattern: Any) -> None:
        """Save a pattern to storage."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Any]:
        """Search patterns by query text."""
        pass

    @abstractmethod
    async def find_similar(
        self,
        query: str,
        threshold: float = None
    ) -> List[tuple[Any, float]]:
        """Find patterns similar to query, sorted by similarity score."""
        pass

    @abstractmethod
    async def add_pattern(self, pattern: Any) -> str:
        """Add a new pattern, return pattern ID."""
        pass

    @abstractmethod
    async def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing pattern."""
        pass

    @abstractmethod
    async def delete_pattern(self, pattern_id: str) -> None:
        """Delete a pattern."""
        pass

    @abstractmethod
    async def record_feedback(
        self,
        pattern_id: str,
        feedback: Dict[str, Any]
    ) -> None:
        """Record user feedback for learning."""
        pass

    @abstractmethod
    def get_patterns_by_category(self, category: str) -> List[Any]:
        """Get all patterns in a category."""
        pass

    @abstractmethod
    def get_all_categories(self) -> List[str]:
        """Get all categories."""
        pass
```

---

## Domain Configuration Schema

### Example: Cooking Domain Config

```yaml
# config/domains/cooking.yaml
domain:
  domain_id: "cooking"
  domain_name: "Cooking & Recipes"
  version: "1.0.0"
  description: "Culinary knowledge, recipes, and cooking techniques"

data_sources:
  - type: "web"
    name: "AllRecipes"
    base_url: "https://www.allrecipes.com"
    enabled: true
  - type: "file"
    name: "Recipe Inbox"
    path: "/pattern-inbox"
    enabled: true

default_collector_type: "web_scraper"

categories:
  - "technique"
  - "preparation"
  - "cooking_method"
  - "ingredient_substitution"
  - "troubleshooting"
  - "equipment"
  - "recipe"

tags:
  - "baking"
  - "grilling"
  - "sautéing"
  - "roasting"
  - "chicken"
  - "vegetarian"
  - "quick"
  - "healthy"

knowledge_base:
  storage_path: "/expertise_scanner/data/patterns/cooking"
  pattern_format: "json"
  pattern_schema:
    required:
      - id
      - name
      - pattern_type
      - description
      - problem
      - solution
    optional:
      - steps
      - ingredients
      - conditions
      - tags
      - examples
      - confidence

specialists:
  - id: "baking"
    name: "Baking Specialist"
    description: "Expert in baking techniques, ingredients, and troubleshooting"
    expertise_keywords:
      - bake
      - oven
      - bread
      - cake
      - cookie
      - pastry
      - dough
      - yeast
      - rise
      - knead
    expertise_categories:
      - "technique"
      - "cooking_method"
      - "troubleshooting"
    knowledge_categories:
      - "baking"
      - "technique"

  - id: "chicken"
    name: "Poultry Specialist"
    description: "Expert in chicken preparation and cooking methods"
    expertise_keywords:
      - chicken
      - poultry
      - breast
      - thigh
      - wing
      - roast
      - grill
      - sauté
    expertise_categories:
      - "recipe"
      - "technique"
    knowledge_categories:
      - "chicken"
      - "cooking_method"

  - id: "quick_meals"
    name: "Quick Meals Specialist"
    description: "Expert in fast, easy meal preparation"
    expertise_keywords:
      - quick
      - fast
      - easy
      - simple
      - 30-minute
      - weeknight
    expertise_categories:
      - "recipe"
      - "preparation"
    knowledge_categories:
      - "quick"
      - "preparation"

  - id: "substitutions"
    name: "Ingredient Substitution Specialist"
    description: "Expert in ingredient alternatives and substitutions"
    expertise_keywords:
      - substitute
      - replacement
      - alternative
      - instead of
      - swap
    expertise_categories:
      - "ingredient_substitution"
    knowledge_categories:
      - "substitution"

collectors:
  - name: "allrecipes"
    type: "web_scraper"
    description: "Scrapes recipes from AllRecipes"
    config:
      base_url: "https://www.allrecipes.com"
      rate_limit: 2.0
      timeout: 30
      user_agent: "RecipeBot/1.0"
    enabled: true

  - name: "recipe_inbox"
    type: "file_system"
    description: "Reads JSON recipe files from inbox"
    config:
      path: "/pattern-inbox"
      file_pattern: "recipe_*.json"
    enabled: true
```

### Example: Python Programming Domain Config

```yaml
# config/domains/python.yaml
domain:
  domain_id: "python"
  domain_name: "Python Programming"
  version: "1.0.0"
  description: "Python programming knowledge and best practices"

data_sources:
  - type: "api"
    name: "GitHub"
    base_url: "https://api.github.com"
    enabled: false
  - type: "file"
    name: "Code Patterns"
    path: "/patterns/python"
    enabled: true

default_collector_type: "file_system"

categories:
  - "syntax"
  - "best_practice"
  - "debugging"
  - "optimization"
  - "library"
  - "framework"

tags:
  - "django"
  - "flask"
  - "asyncio"
  - "testing"
  - "data-science"

knowledge_base:
  storage_path: "/expertise_scanner/data/patterns/python"
  pattern_format: "json"

specialists:
  - id: "django"
    name: "Django Specialist"
    expertise_keywords:
      - django
      - model
      - view
      - template
      - orm
      - migration
    expertise_categories:
      - "framework"
      - "best_practice"

  - id: "asyncio"
    name: "Async Programming Specialist"
    expertise_keywords:
      - async
      - await
      - coroutine
      - future
      - task
      - event_loop
    expertise_categories:
      - "syntax"
      - "best_practice"
```

---

## Pattern Schema

### Cooking Pattern (JSON)

```json
{
  "id": "cooking_001",
  "name": "Pan-Searing Chicken Breast",
  "pattern_type": "technique",
  "domain": "cooking",
  "description": "Achieve perfectly cooked chicken breast with golden exterior",
  "problem": "Chicken breast often dry or overcooked",
  "solution": "Use high-heat searing followed by lower heat to finish",
  "steps": [
    "Pound chicken to even thickness",
    "Season generously with salt and pepper",
    "Heat oil in skillet over medium-high heat",
    "Sear 3-4 minutes per side until golden",
    "Reduce heat and cook until internal temp reaches 165°F"
  ],
  "ingredients": ["chicken breast", "oil", "salt", "pepper"],
  "conditions": {
    "cooking_method": "pan-searing",
    "protein": "chicken",
    "thickness": "even"
  },
  "tags": ["chicken", "quick", "technique", "pan-sear"],
  "examples": [
    "Spicy Garlic Lime Chicken",
    "Simple Lemon Herb Chicken"
  ],
  "confidence": 0.95,
  "sources": [
    "https://www.allrecipes.com/recipe/44868/spicy-garlic-lime-chicken/"
  ],
  "specialist_id": "chicken",
  "created_at": "2026-01-06T00:00:00Z",
  "updated_at": "2026-01-06T00:00:00Z",
  "times_accessed": 15,
  "user_rating": null
}
```

### Substitution Pattern

```json
{
  "id": "cooking_002",
  "name": "Butter to Oil Substitution",
  "pattern_type": "substitution",
  "domain": "cooking",
  "description": "Replace butter with oil in baking recipes",
  "problem": "Recipe calls for butter but you only have oil",
  "solution": "Use 3/4 cup of oil for every 1 cup of butter",
  "steps": [
    "Calculate the amount: butter amount × 0.75 = oil amount",
    "For cakes and muffins, use vegetable or canola oil",
    "For savory dishes, olive oil works well",
    "Note: texture will be more dense, less tender"
  ],
  "conditions": {
    "original": "butter",
    "replacement": "oil",
    "ratio": "0.75:1"
  },
  "tags": ["substitution", "baking", "ingredient"],
  "examples": [
    "1 cup butter → 3/4 cup oil in muffins",
    "1/2 cup butter → 6 tablespoons oil in cake"
  ],
  "confidence": 0.90,
  "sources": ["https://www.allrecipes.com/article/butter-oil-substitution/"],
  "specialist_id": "substitutions"
}
```

---

## Factory Pattern for Domain Instantiation

```python
class DomainFactory:
    """Factory for creating domain instances."""

    _domains: Dict[str, Type[Domain]] = {}

    @classmethod
    def register_domain(cls, domain_class: Type[Domain]) -> None:
        """Register a domain implementation class."""
        # Extract domain_id from class name (e.g., CookingDomain -> cooking)
        domain_id = domain_class.__name__.replace('Domain', '').lower()
        cls._domains[domain_id] = domain_class

    @classmethod
    def load_config(cls, config_path: str) -> DomainConfig:
        """Load domain configuration from YAML file."""
        import yaml
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return DomainConfig(**data['domain'])

    @classmethod
    def create_domain(
        cls,
        domain_id: str,
        config_path: Optional[str] = None
    ) -> Domain:
        """Create a domain instance."""
        if domain_id not in cls._domains:
            raise ValueError(f"Unknown domain: {domain_id}. Available: {list(cls._domains.keys())}")

        domain_class = cls._domains[domain_id]

        # Load config if path provided or use default
        if config_path is None:
            config_path = f"config/domains/{domain_id}.yaml"

        config = cls.load_config(config_path)

        return domain_class(config)

    @classmethod
    def list_domains(cls) -> List[str]:
        """List available domain types."""
        return list(cls._domains.keys())

    @classmethod
    def is_registered(cls, domain_id: str) -> bool:
        """Check if a domain is registered."""
        return domain_id in cls._domains
```

---

## Assistant Engine

### Generic Assistant Engine

```python
class GenericAssistantEngine:
    """
    Domain-agnostic assistant engine.

    Orchestrates query processing across specialists and knowledge base.
    """

    def __init__(
        self,
        domain: Domain,
        llm_client: Optional['LLMClient'] = None
    ):
        self.domain = domain
        self.llm_client = llm_client
        self.knowledge_base = self._create_knowledge_base()
        self.query_history: List[Dict[str, Any]] = []

    async def initialize(self) -> None:
        """Initialize the engine and domain."""
        await self.domain.initialize()
        await self.knowledge_base.load_patterns()

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query.

        Args:
            query: User's question or request
            context: Optional additional context

        Returns:
            Response dictionary with answer, sources, and metadata
        """
        # 1. Select appropriate specialist
        specialist = self.domain.get_specialist_for_query(query)

        # 2. Search knowledge base for relevant patterns
        patterns = await self.knowledge_base.search(query, limit=5)

        # 3. Process query through specialist
        if specialist:
            response_data = await specialist.process_query(query, context)
            response = specialist.format_response(response_data)
            specialist_id = specialist.specialist_id
        else:
            # General query processing
            response_data = await self._general_processing(query, patterns, context)
            response = self._format_general_response(response_data)
            specialist_id = None

        # 4. Record query for learning
        await self._record_query(query, response, specialist_id, patterns)

        return {
            'query': query,
            'response': response,
            'specialist': specialist_id,
            'patterns_used': [p.get('id') for p in patterns],
            'confidence': self._calculate_confidence(patterns, specialist),
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _general_processing(
        self,
        query: str,
        patterns: List[Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process query without a specific specialist."""
        return {
            'answer': self._synthesize_answer(query, patterns),
            'patterns': patterns,
            'suggestions': [p['name'] for p in patterns[:3]]
        }

    def _synthesize_answer(self, query: str, patterns: List[Any]) -> str:
        """Synthesize answer from multiple patterns."""
        if not patterns:
            return "I couldn't find specific information for your query."

        # Simple synthesis - in real implementation, would use LLM
        answer_parts = []
        for pattern in patterns[:3]:
            answer_parts.append(f"**{pattern['name']}**: {pattern['solution']}")

        return "\n\n".join(answer_parts)

    def _format_general_response(self, data: Dict[str, Any]) -> str:
        """Format general response for user."""
        return data['answer']

    def _calculate_confidence(
        self,
        patterns: List[Any],
        specialist: Optional[Specialist]
    ) -> float:
        """Calculate overall confidence in the response."""
        if not patterns:
            return 0.0

        # Base confidence from pattern matches
        pattern_confidence = sum(p.get('confidence', 0.5) for p in patterns) / len(patterns)

        # Boost if specialist matched
        if specialist:
            specialist_confidence = specialist.can_handle(patterns[0].get('name', ''))
            return (pattern_confidence + specialist_confidence) / 2

        return pattern_confidence

    async def _record_query(
        self,
        query: str,
        response: str,
        specialist_id: Optional[str],
        patterns: List[Any]
    ) -> None:
        """Record query for learning and analytics."""
        record = {
            'query': query,
            'response': response,
            'specialist': specialist_id,
            'patterns': [p.get('id') for p in patterns],
            'timestamp': datetime.utcnow().isoformat()
        }
        self.query_history.append(record)

    def _create_knowledge_base(self) -> KnowledgeBase:
        """Create knowledge base instance for domain."""
        from knowledge.json_kb import JSONKnowledgeBase
        config = KnowledgeBaseConfig(
            storage_path=self.domain.config.pattern_storage_path,
            pattern_format=self.domain.config.pattern_format,
            pattern_schema=self.domain.config.pattern_schema
        )
        return JSONKnowledgeBase(config)
```

---

## File Structure

```
src/
├── core/                              # Core abstractions
│   ├── __init__.py
│   ├── domain.py                      # Domain interface
│   ├── collector.py                   # Collector interface
│   ├── specialist.py                  # Specialist interface
│   ├── knowledge_base.py              # KnowledgeBase interface
│   └── factory.py                     # DomainFactory
│
├── domains/                           # Domain implementations
│   ├── cooking/
│   │   ├── __init__.py
│   │   ├── domain.py                  # CookingDomain class
│   │   ├── collectors/
│   │   │   ├── __init__.py
│   │   │   ├── allrecipes_scraper.py  # AllRecipes web scraper
│   │   │   └── inbox_collector.py     # Recipe inbox reader
│   │   └── specialists/
│   │       ├── __init__.py
│   │       ├── baking.py              # Baking Specialist
│   │       ├── chicken.py             # Poultry Specialist
│   │       ├── quick_meals.py         # Quick Meals Specialist
│   │       └── substitutions.py       # Substitution Specialist
│   │
│   ├── python/
│   │   ├── __init__.py
│   │   ├── domain.py                  # PythonDomain class
│   │   ├── collectors/
│   │   └── specialists/
│   │       ├── django.py
│   │       ├── asyncio.py
│   │       └── testing.py
│   │
│   └── diy/
│       ├── __init__.py
│       └── ...
│
├── knowledge/                         # Knowledge base implementations
│   ├── __init__.py
│   ├── json_kb.py                     # JSON-based storage
│   ├── yaml_kb.py                     # YAML-based storage
│   └── search.py                      # Similarity search algorithms
│
├── assist/                            # Generic assistant engine
│   ├── __init__.py
│   ├── engine.py                      # GenericAssistantEngine
│   ├── llm_client.py                  # LLM integration
│   └── response_formatter.py          # Response formatting
│
├── api/                               # API layer
│   ├── __init__.py
│   └── app.py                         # FastAPI app
│
└── settings/                          # Settings management
    ├── __init__.py
    └── loader.py                      # Config loader

config/
└── domains/                           # Domain configurations
    ├── cooking.yaml
    ├── python.yaml
    └── diy.yaml

expertise_scanner/
└── data/
    └── patterns/
        ├── cooking/
        │   └── patterns.json          # 22 current cooking patterns
        ├── python/
        └── diy/
```

---

## Implementation Phases

### Phase 1: Core Abstractions ✅
- [x] Create abstract base classes
- [x] Define domain configuration schema
- [x] Design pattern structure

### Phase 2: Cooking Domain Implementation (Current)
- [ ] Implement CookingDomain class
- [ ] Implement AllRecipesCollector
- [ ] Implement RecipeInboxCollector
- [ ] Implement 4 cooking specialists
- [ ] Implement JSONKnowledgeBase
- [ ] Create cooking.yaml config

### Phase 3: Assistant Engine
- [ ] Implement GenericAssistantEngine
- [ ] Implement query routing
- [ ] Implement pattern search
- [ ] Implement response formatting

### Phase 4: API Layer
- [ ] RESTful API endpoints
- [ ] Query endpoint
- [ ] Pattern management endpoints
- [ ] Domain switching

### Phase 5: Additional Domains
- [ ] Python programming domain
- [ ] DIY domain
- [ ] First aid domain

---

## Example Usage

```python
# Initialize cooking domain
from domains.cooking import CookingDomain
from core.factory import DomainFactory
from assist.engine import GenericAssistantEngine

# Register domain
DomainFactory.register_domain(CookingDomain)

# Create and initialize
cooking_domain = DomainFactory.create_domain('cooking')
engine = GenericAssistantEngine(cooking_domain)
await engine.initialize()

# Process queries
response1 = await engine.process_query("How do I cook chicken breast?")
# → Uses Chicken Specialist, returns pan-searing technique

response2 = await engine.process_query("My cake is too dense, what did I do wrong?")
# → Uses Baking Specialist, returns troubleshooting tips

response3 = await engine.process_query("Can I substitute oil for butter?")
# → Uses Substitution Specialist, returns ratio and tips
```

---

## Summary

The generic domain framework provides:

1. **Clean Abstraction**: Domain logic separated from core framework
2. **Configuration-Driven**: Domains defined by YAML configs
3. **Specialist System**: Expert knowledge organized by specialty
4. **Pattern-Based**: Knowledge stored as reusable patterns
5. **Extensible**: New domains added without framework changes
6. **Type-Safe**: Abstract base classes define contracts
7. **Testable**: Each component independently testable

**Cooking as Reference Domain:**
- 22 existing patterns demonstrate the system
- Clear specialist categories (baking, chicken, quick meals, substitutions)
- Simple, relatable domain for understanding the framework
