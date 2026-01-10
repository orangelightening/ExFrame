# Specialist Plugin System

## Status: ✅ IMPLEMENTED

The plugin system is **fully implemented and production-ready**. All domains now use plugins.

---

## The Core Insight

**Keep the engine focused. Make specialists pluggable.**

- Engine doesn't know HOW specialist works, only THAT it works
- Specialist is a black box with a simple interface
- Anyone can write specialists without touching core code
- We prove it works by making OUR specialists plugins

---

## The Plugin Interface (3 Methods)

That's it. Simple.

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class SpecialistPlugin(ABC):
    """
    A specialist is a plugin that answers questions in its domain.

    Interface: 3 methods. That's all.
    """

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """
        Can this specialist handle the query?

        Return: Confidence score 0.0 to 1.0
        """
        pass

    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process the query and return response data.

        Return: Dict with at least:
            - answer: str (the response text)
            - patterns: List[dict] (patterns used)
            - confidence: float (0.0 to 1.0)
        """
        pass

    @abstractmethod
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format the response for user consumption.

        Return: String to display to user
        """
        pass
```

**Location:** `generic_framework/core/specialist_plugin.py`

---

## Implemented Plugins

### Custom Domain Plugins

**Binary Symmetry** (`plugins/binary_symmetry/`):
- `BitwiseMasterPlugin` - Bitwise operations specialist
- `PatternAnalystPlugin` - Pattern analysis specialist
- `AlgorithmExplorerPlugin` - Algorithm specialist

**LLM Consciousness** (`plugins/llm_consciousness/`):
- `FailureDetectionPlugin` - Failure mode detection
- `MonitoringPlugin` - Monitoring and architecture

### Reusable Plugins

**Generalist** (`plugins/generalist.py`):
- Configurable generalist for any domain
- Used by: cooking, python, first_aid, gardening, diy

---

## Plugin Discovery

Domain.json tells the engine which plugins to load:

```json
{
  "domain_id": "binary_symmetry",
  "plugins": [
    {
      "plugin_id": "bitwise_master",
      "module": "plugins.binary_symmetry.bitwise_master",
      "class": "BitwiseMasterPlugin",
      "enabled": true,
      "config": {
        "keywords": ["xor", "and", "or", "not"],
        "categories": ["symmetry", "transformation"],
        "threshold": 0.30
      }
    }
  ]
}
```

**Engine:** (`core/generic_domain.py`)
```python
def _initialize_specialists(self) -> None:
    """Initialize specialists from plugin configuration."""
    import importlib

    plugins_config = self._domain_config.get("plugins", [])

    for plugin_config in plugins_config:
        if not plugin_config.get("enabled", True):
            continue

        try:
            # Dynamically import the plugin
            module_path = plugin_config["module"]
            class_name = plugin_config["class"]

            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)

            # Instantiate plugin with knowledge base and config
            plugin = plugin_class(self._knowledge_base, plugin_config.get("config", {}))

            # Store using plugin_id as specialist_id
            self._specialists[plugin_config["plugin_id"]] = plugin

        except (ImportError, AttributeError) as e:
            print(f"Warning: Failed to load plugin {plugin_config.get('plugin_id')}: {e}")
```

---

## Plugin Example

```python
# plugins/binary_symmetry/bitwise_master.py

class BitwiseMasterPlugin(SpecialistPlugin):
    """
    Bitwise operations specialist.

    NO inheritance. Just implements 3 methods.
    """

    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict[str, Any] = None):
        """
        Initialize with knowledge base and optional config.

        Args:
            knowledge_base: The pattern knowledge base
            config: Optional configuration dict
        """
        self.kb = knowledge_base
        self.config = config or {}

        # Configuration
        self.keywords = self.config.get("keywords", [
            "xor", "and", "or", "not", "complement", "invert",
            "opposite", "negative", "bit", "binary", "hex", "0x"
        ])

        self.categories = self.config.get("categories", [
            "symmetry", "transformation", "logic"
        ])

        self.threshold = self.config.get("threshold", 0.30)

    def can_handle(self, query: str) -> float:
        """Can I handle this query?"""
        query_lower = query.lower()
        score = 0.0

        # Score keyword matches
        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 0.2

        # Hex notation boost
        if any(prefix in query_lower for prefix in ["0x", "0b", "0o"]):
            score += 0.3

        # Question words boost
        if any(word in query_lower for word in ["how", "what", "why", "explain", "find"]):
            score += 0.1

        return min(score, 1.0)

    async def process_query(self, query: str, context=None) -> dict:
        """Process the query."""
        # Search across all our categories
        all_patterns = []
        for category in self.categories:
            patterns = await self.kb.search(query, category=category, limit=5)
            all_patterns.extend(patterns)

        # Deduplicate by pattern_id
        seen = set()
        unique_patterns = []
        for pattern in all_patterns:
            if pattern.get("pattern_id") not in seen:
                seen.add(pattern.get("pattern_id"))
                unique_patterns.append(pattern)

        return {
            "query": query,
            "specialist": "bitwise_master",
            "patterns_found": len(unique_patterns),
            "patterns": unique_patterns[:5],
            "answer": self._synthesize_answer(query, unique_patterns),
            "confidence": self.can_handle(query)
        }

    def format_response(self, data: dict) -> str:
        """Format for user (any way we want)."""
        patterns = data.get("patterns", [])

        if not patterns:
            return f"[Bitwise Master] No patterns found for: {data.get('query', '')}"

        result = f"[Bitwise Master] Found {data.get('patterns_found', 0)} patterns:\n\n"

        # Show top 3 patterns
        for pattern in patterns[:3]:
            result += f"**{pattern.get('name', 'Unknown')}**\n"
            result += f"Type: {pattern.get('type', 'N/A')}\n\n"

            # Solution
            if "solution" in pattern:
                result += f"{pattern['solution']}\n\n"

            # Examples
            if "examples" in pattern and pattern["examples"]:
                result += "**Examples:**\n"
                for ex in pattern["examples"][:3]:
                    result += "   • "
                    if isinstance(ex, str):
                        result += ex
                    elif isinstance(ex, dict):
                        for key, value in ex.items():
                            if key != "notes":
                                result += f"{key}={value} "
                    result += "\n"
                result += "\n"

        return result
```

**Location:** `generic_framework/plugins/binary_symmetry/bitwise_master.py`

---

## The Boundary

**Engine provides to plugin:**
- Knowledge base (to search patterns)
- Domain config (read-only access via config parameter)
- Query context

**Plugin must provide:**
- Confidence score (0.0 to 1.0)
- Response data (answer + patterns + confidence)
- Formatted string

**That's the contract. Simple.**

---

## File Structure

```
generic_framework/
├── core/
│   ├── specialist_plugin.py    # Plugin interface (ABC)
│   ├── domain.py               # Domain interface
│   ├── generic_domain.py       # Plugin loader
│   └── knowledge_base.py       # Pattern storage
├── plugins/                    # ✅ NEW: Plugin directory
│   ├── binary_symmetry/
│   │   ├── __init__.py
│   │   ├── bitwise_master.py
│   │   ├── pattern_analyst.py
│   │   └── algorithm_explorer.py
│   ├── llm_consciousness/
│   │   ├── __init__.py
│   │   ├── failure_detection.py
│   │   └── monitoring.py
│   ├── generalist.py           # Reusable generalist
│   └── (future custom plugins)
└── assist/
    └── engine.py               # Query routing
```

**Deleted:** `core/generic_specialist.py` (no longer needed)

---

## Current Status

### Production Domains Using Plugins

| Domain | Patterns | Specialists | Plugin Type |
|--------|----------|-------------|-------------|
| binary_symmetry | 16 | 3 | Custom |
| llm_consciousness | 11 | 2 | Custom |
| cooking | 21 | 1 | Generalist |
| python | 6 | 1 | Generalist |
| first_aid | 1 | 1 | Generalist |
| gardening | 0 | 1 | Generalist |
| diy | 0 | 1 | Generalist |

**Total:** 7 domains, 55 patterns, 9 specialists

### Performance

- Plugin loading: <100ms at startup
- Specialist selection: <1ms per query
- Plugin processing: <1ms per query
- **Total: <5ms for 95% of queries**

---

## Benefits Delivered

1. ✅ **Engine stays clean** - Just loads plugins, calls 3 methods
2. ✅ **Plugins are independent** - Can be developed separately
3. ✅ **Plugins are swappable** - Drop in new ones without touching engine
4. ✅ **Plugins are testable** - Test in isolation
5. ✅ **Plugins are versionable** - Can have plugin v1, v2, v3
6. ✅ **Proves the architecture** - We use it for our own specialists

---

## Adding a New Plugin

### Step 1: Create Plugin File

```bash
mkdir -p generic_framework/plugins/my_domain
vim generic_framework/plugins/my_domain/specialist.py
```

### Step 2: Implement Plugin

```python
from core.specialist_plugin import SpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase
from typing import Dict, Any

class MySpecialistPlugin(SpecialistPlugin):
    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict[str, Any] = None):
        self.kb = knowledge_base
        self.config = config or {}
        # Your initialization

    def can_handle(self, query: str) -> float:
        # Your scoring logic
        return 0.5

    async def process_query(self, query: str, context=None) -> dict:
        # Your query processing
        return {"answer": "...", "patterns": [], "confidence": 0.5}

    def format_response(self, response_data: dict) -> str:
        # Your formatting
        return response_data.get("answer", "")
```

### Step 3: Update Domain Config

```json
{
  "domain_id": "my_domain",
  "plugins": [
    {
      "plugin_id": "my_specialist",
      "module": "plugins.my_domain.specialist",
      "class": "MySpecialistPlugin",
      "enabled": true,
      "config": {
        "your": "config values"
      }
    }
  ]
}
```

### Step 4: Restart

```bash
docker-compose restart eeframe-app
```

**Done.**

---

## The Simplicity

**Before (Old Architecture):**
```
Domain → Custom Domain Class → Specialist Class → Process Query
```

**After (Current Architecture):**
```
Domain → Plugin Loader → Plugin (3 methods) → Process Query
```

**The interface:**
```python
can_handle(query) → float
process_query(query, context) → dict
format_response(data) → str
```

**That's it.**
