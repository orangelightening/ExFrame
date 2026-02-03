# Plugin Refactor Design Document
## Making Plugins Modular, Configurable, and Understandable

**Status**: Design Draft
**Created**: 2026-02-02
**Author**: Claude (with user input)
**Target**: 4 releases over 4-6 weeks

---

## Executive Summary

**Problem**: Current plugin system has become unmanageable. LLMEnricher is 700+ lines of conditional logic. Domain types are strings, not behaviors. Configuration is scattered across multiple files.

**Solution**: Strategy Pattern + Configurable Behaviors. Plugins become behaviorless shells. All "personality" comes from domain config.

**Key Principle**: **Plugins should be LEGO bricks, not Swiss Army knives.**

---

## Current Problems (The "Why")

### 1. God Objects
```
LLMEnricher: 700+ lines
├── _generate_llm_response()      # 200 lines
├── _build_enhancement_prompt()    # 100 lines
├── _build_document_context_prompt() # 120 lines
├── _build_web_search_prompt()     # 90 lines
├── _build_direct_prompt()         # 50 lines
├── _call_llm()                    # 100 lines
└── ... scope checking, type detection, etc.
```

**Problem**: Every domain type requirement adds more `if` statements.

### 2. Hardcoded Personalities
```python
# In LLMEnricher._build_document_context_prompt():
scope_boundaries = """
**SCOPE BOUNDARIES:**
You are an ExFrame expert. Answer ONLY about:
- ExFrame architecture and design
...
If a question is clearly outside ExFrame's scope...
"""
```

**Problem**: Cooking domain gets ExFrame's scope boundaries because code path detects Type 3.

### 3. Brittle Type Detection
```python
is_type3_domain = (
    specialist_id == "exframe_specialist" or
    "combined_results" in response_data or  # BUG!
    response_data.get("search_strategy") == "research_primary"
)
```

**Problem**: Type detection via response_data keys is fragile.

### 4. Multiple Sources of Truth
```
universe.yaml → config_override
  ↓
domain.json (multiple locations)
  ↓
data/domains.json (registry, cached)
  ↓
in-memory Domain objects
```

**Problem**: Which config wins? Nobody knows.

---

## Proposed Architecture

### The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                     NEW ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Domain Config (domain.json)                                 │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ {                                                  │     │
│  │   "domain_type": "4",                               │     │
│  │   "specialist": "researcher",                       │     │
│  │   "behaviors": {                                    │     │
│  │     "scope": { "type": "none" },                    │     │
│  │     "llm": {                                         │     │
│  │       "mode": "replace",                             │     │
│  │       "personality": "professional_chef",            │     │
│  │       "prompts": { "type": "web_search" }           │     │
│  │     },                                               │     │
│  │     "web_search": { "type": "type4" }               │     │
│  │   }                                                 │     │
│  │ }                                                  │     │
│  └─────────────────────────────────────────────────────┘     │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │         DomainType (class, not string!)            │     │
│  │         Type4AnalyticDomain                         │     │
│  │                                                  │     │
│  │   - process_query()                                 │     │
│  │   - _search_local()                                 │     │
│  │   - _search_web()                                   │     │
│  │   - _is_local_sufficient()                          │     │
│  └─────────────────────────────────────────────────────┘     │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │         Plugins (LEGO bricks, not Swiss Army knives)│     │
│  │                                                  │     │
│  │   LLMEnricher(config)                               │     │
│  │     ├─→ scope_check: ScopeCheck (from config)       │     │
│  │     ├─→ prompt_builder: PromptBuilder (from config) │     │
│  │     └─→ web_strategy: WebSearchStrategy (from config)│     │
│  │                                                  │     │
│  │   CitationEnricher(config)                           │     │
│  │   QualityEnricher(config)                             │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  Single Responsibility: Each class does ONE thing            │
│  Configuration: Behavior defined in config, not code         │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### 1. Domain Types (First-Class Classes)

```python
# domain_type.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class QueryContext:
    """Simple, explicit context - no hidden flags"""
    query: str
    web_search_confirmed: bool = False
    show_thinking: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class QueryResult:
    """Simple, explicit result"""
    answer: str
    can_extend_with_web_search: bool = False
    local_results: List['Pattern'] = None
    web_results: List['WebResult'] = None
    llm_used: bool = False
    confidence: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.local_results is None:
            self.local_results = []
        if self.web_results is None:
            self.web_results = []
        if self.metadata is None:
            self.metadata = {}


class DomainType(ABC):
    """
    Base class for all domain types.

    Each domain type (1-5) is a class with its own query processing logic.
    No more type strings, no more if-else chains.
    """

    domain_type_id: str
    name: str
    description: str

    def __init__(self, config: Dict[str, Any], knowledge_base):
        self.config = config
        self.kb = knowledge_base

        # Load plugins from config
        self.plugins = self._load_plugins(config.get("plugins", []))

    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: QueryContext
    ) -> QueryResult:
        """Process a query - single entry point for each domain type"""
        pass

    def _load_plugins(self, plugin_configs: List[Dict]) -> List['Plugin']:
        """Load plugins from config"""
        plugins = []
        for cfg in plugin_configs:
            plugin = PluginFactory.create(cfg, self.kb)
            plugins.append(plugin)
        return plugins


class Type4AnalyticDomain(DomainType):
    """
    Type 4: Analytical Engine

    Characteristics:
    - Web search required for quality answers
    - Local patterns are fallback only
    - Single specialist (ResearchSpecialist)
    - Two-stage query (local → web extension)
    """

    domain_type_id = "4"
    name = "Analytical Engine"
    description = "Web search with local fallback"

    def __init__(self, config: Dict, knowledge_base):
        super().__init__(config, knowledge_base)

        # Type 4 specific configuration
        self.web_search_enabled = config.get("web_search", {}).get("enabled", True)
        self.local_relevance_threshold = config.get("web_search", {}).get("local_relevance_threshold", 0.5)

        # Load specialist
        specialist_config = config.get("specialist", {})
        self.specialist = SpecialistFactory.create("researcher", specialist_config, knowledge_base)

    async def process_query(
        self,
        query: str,
        context: QueryContext
    ) -> QueryResult:
        """
        Type 4 query flow:
        1. Local search (fast)
        2. Check if sufficient
        3. If not sufficient and web not enabled → request extension
        4. If web confirmed → web search + LLM synthesis
        """

        # Stage 1: Local search
        local_results = await self._search_local(query)

        # Stage 2: Check sufficiency
        if self._local_results_sufficient(local_results):
            # Good local results - use them
            answer = await self._form_answer_from_local(local_results, context)
            return QueryResult(
                answer=answer,
                local_results=local_results,
                confidence=self._calculate_confidence(local_results)
            )

        # Stage 3: Not sufficient
        if not self.web_search_enabled:
            # Can't search web - tell user
            return QueryResult(
                answer=self._form_fallback_message(query, local_results),
                local_results=local_results,
                can_extend_with_web_search=False,
                confidence=0.3
            )

        # Web search available
        if not context.web_search_confirmed:
            # Request web search
            return QueryResult(
                answer=self._form_extension_request(query, local_results),
                local_results=local_results,
                can_extend_with_web_search=True,
                confidence=0.5
            )

        # Stage 4: Web search
        web_results = await self._search_web(query)
        answer = await self._form_answer_from_web(web_results, context)

        return QueryResult(
            answer=answer,
            web_results=web_results,
            llm_used=True,
            confidence=0.9
        )

    async def _search_local(self, query: str) -> List['Pattern']:
        """Search local knowledge base"""
        return await self.kb.search(query, limit=10)

    def _local_results_sufficient(self, results: List) -> bool:
        """Type 4: High relevance required"""
        if not results:
            return False
        max_relevance = max(
            r.get('confidence', r.get('relevance', r.get('_semantic_score', 0)))
            for r in results
        )
        return max_relevance >= self.local_relevance_threshold

    async def _form_answer_from_local(self, results: List, context: QueryContext) -> str:
        """Form answer from local patterns using plugins"""
        response_data = {"query": context.query, "patterns": results}

        for plugin in self.plugins:
            response_data = await plugin.enrich(response_data, context)

        return response_data.get("answer", "No answer formed")

    def _form_extension_request(self, query: str, local_results: List) -> str:
        """Tell user to enable web search"""
        return f"I found {len(local_results)} local patterns, but they're not specific enough for '{query}'. Please click 'Extended Search (Internet)' for a proper answer."

    async def _search_web(self, query: str) -> List['WebResult']:
        """Search web using specialist"""
        return await self.specialist.search_web(query)
```

---

### 2. Plugins (LEGO Bricks)

```python
# plugins/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any

class Plugin(ABC):
    """Base plugin class"""

    name: str = "Plugin"

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def process(
        self,
        data: Dict[str, Any],
        context: QueryContext
    ) -> Dict[str, Any]:
        """Process data - single responsibility"""
        pass


class PluginFactory:
    """Create plugins from config"""

    @staticmethod
    def create(config: Dict, knowledge_base) -> Plugin:
        module_path = config["module"]
        class_name = config["class"]

        # Dynamic import
        import importlib
        module = importlib.import_module(module_path)
        plugin_class = getattr(module, class_name)

        return plugin_class(config.get("config", {}))
```

---

### 3. LLM Enricher (Refactored)

```python
# plugins/enrichers/llm_enricher.py

class LLMEnricher(Plugin):
    """
    Configurable LLM enricher.

    Behavior comes from config, not hardcoded logic.
    """

    name = "LLM Enricher"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Load behaviors from config
        self.mode = config.get("mode", "enhance")

        # Scope checking - STRATEGY PATTERN
        self.scope_check = ScopeCheckFactory.create(
            config.get("scope", {"type": "none"})
        )

        # Prompt building - STRATEGY PATTERN
        self.prompt_builder = PromptBuilderFactory.create(
            config.get("prompts", {"type": "general"})
        )

        # Web search behavior - STRATEGY PATTERN
        self.web_strategy = WebSearchStrategyFactory.create(
            config.get("web_search", {"type": "disabled"})
        )

        # LLM client
        self.llm = LLMClient(config.get("llm", {}))

    async def process(
        self,
        data: Dict[str, Any],
        context: QueryContext
    ) -> Dict[str, Any]:
        """Enrich using configured strategies"""

        query = data.get("query", "")
        patterns = data.get("patterns", [])

        # 1. Check scope (if configured)
        in_scope, scope_reason = self.scope_check.is_in_scope(
            query,
            patterns,
            context
        )

        if not in_scope:
            return {
                "out_of_scope": True,
                "reason": scope_reason,
                "answer": scope_reason
            }

        # 2. Select prompt builder based on context
        prompt_builder = self.web_strategy.select_prompt_builder(
            data,
            context
        )

        # 3. Build prompt
        prompt = prompt_builder.build(data, context)

        # 4. Call LLM
        answer = await self.llm.complete(
            prompt,
            show_thinking=context.show_thinking
        )

        return {
            "answer": answer,
            "llm_used": True
        }
```

---

### 4. Strategies (Configurable Behaviors)

```python
# plugins/strategies/scope_check.py

class ScopeCheck(ABC):
    """Base class for scope checking strategies"""

    @abstractmethod
    def is_in_scope(
        self,
        query: str,
        patterns: List,
        context: QueryContext
    ) -> tuple[bool, str]:
        """
        Returns (is_in_scope, reason_if_not)
        """
        pass


class NoOpScopeCheck(ScopeCheck):
    """No scope checking - always in scope"""

    def is_in_scope(self, query, patterns, context):
        return True, ""


class TopicScopeCheck(ScopeCheck):
    """Check if query matches allowed topics"""

    def __init__(self, config: Dict):
        self.allowed_topics = set(config.get("allowed_topics", []))
        self.out_of_scope_message = config.get(
            "out_of_scope_message",
            "I can only answer questions about specific topics."
        )

    def is_in_scope(self, query, patterns, context):
        query_lower = query.lower()

        # Check if any allowed topic is mentioned
        for topic in self.allowed_topics:
            if topic.lower() in query_lower:
                return True, ""

        return False, self.out_of_scope_message


class RelevanceScopeCheck(ScopeCheck):
    """Check if patterns meet relevance threshold"""

    def __init__(self, config: Dict):
        self.min_relevance = config.get("min_relevance", 0.3)
        self.no_match_message = config.get(
            "no_match_message",
            "I couldn't find relevant information."
        )

    def is_in_scope(self, query, patterns, context):
        if not patterns:
            return False, self.no_match_message

        max_relevance = max(
            p.get('confidence', p.get('relevance', 0))
            for p in patterns[:20]
        )

        if max_relevance < self.min_relevance:
            return False, self.no_match_message

        return True, ""


class ScopeCheckFactory:
    """Create scope check from config"""

    @staticmethod
    def create(config: Dict) -> ScopeCheck:
        check_type = config.get("type", "none")

        strategies = {
            "none": NoOpScopeCheck,
            "topics": TopicScopeCheck,
            "relevance": RelevanceScopeCheck,
        }

        strategy_class = strategies.get(check_type, NoOpScopeCheck)
        return strategy_class(config)
```

```python
# plugins/strategies/prompt_builder.py

class PromptBuilder(ABC):
    """Base class for prompt building strategies"""

    @abstractmethod
    def build(
        self,
        data: Dict[str, Any],
        context: QueryContext
    ) -> str:
        pass


class WebSearchPromptBuilder(PromptBuilder):
    """Build prompts for web search results"""

    def __init__(self, config: Dict):
        self.system_message = config.get(
            "system_message",
            "You are a helpful AI assistant."
        )

    def build(self, data, context):
        query = data.get("query", "")
        web_results = data.get("web_results", [])

        # Format web results as context
        context_text = self._format_web_results(web_results)

        return f"""{self.system_message}

A user asked: "{query}"

Here are the relevant web search results:

{context_text}

Please provide a comprehensive answer based on these results. Include specific details and cite sources when appropriate."""


class WebSearchRequestPromptBuilder(PromptBuilder):
    """Build prompts that request web search instead of hallucinating"""

    def __init__(self, config: Dict):
        self.domain_name = config.get("domain_name", "this domain")

    def build(self, data, context):
        query = data.get("query", "")
        local_count = len(data.get("local_results", []))

        return f"""You are a helpful AI assistant for {self.domain_name}.

A user asked: "{query}"

I found {local_count} local patterns, but they don't contain the specific information needed to answer this question.

**IMPORTANT:**
- Do NOT make up, hallucinate, or guess an answer
- Tell the user you need to search the web
- Ask them to click "Extended Search (Internet)"

Your response:"""


class PromptBuilderFactory:
    """Create prompt builder from config"""

    @staticmethod
    def create(config: Dict) -> PromptBuilder:
        builder_type = config.get("type", "general")

        strategies = {
            "web_search": WebSearchPromptBuilder,
            "web_search_request": WebSearchRequestPromptBuilder,
            "general": GeneralPromptBuilder,
        }

        strategy_class = strategies.get(builder_type, GeneralPromptBuilder)
        return strategy_class(config)
```

---

### 5. Web Search Strategies

```python
# plugins/strategies/web_search.py

class WebSearchStrategy(ABC):
    """Base class for web search behavior"""

    @abstractmethod
    def select_prompt_builder(
        self,
        data: Dict,
        context: QueryContext
    ) -> PromptBuilder:
        pass


class Type4WebSearchStrategy(WebSearchStrategy):
    """Type 4 web search: prioritize web, fallback to local"""

    def __init__(self, config: Dict):
        self.require_relevance = config.get("require_relevance", 0.5)

    def select_prompt_builder(self, data, context):
        # Has web search results?
        web_results = data.get("web_results", [])
        if web_results:
            return WebSearchPromptBuilder({})  # Use web results

        # Check local relevance
        patterns = data.get("patterns", [])
        if self._local_relevance_sufficient(patterns):
            return LocalPatternPromptBuilder({})  # Use local

        # Need web search
        return WebSearchRequestPromptBuilder({
            "domain_name": context.domain_id
        })

    def _local_relevance_sufficient(self, patterns):
        if not patterns:
            return False
        max_rel = max(p.get('confidence', 0) for p in patterns)
        return max_rel >= self.require_relevance


class WebSearchStrategyFactory:
    """Create web search strategy from config"""

    @staticmethod
    def create(config: Dict) -> WebSearchStrategy:
        strategy_type = config.get("type", "disabled")

        strategies = {
            "type4": Type4WebSearchStrategy,
            "disabled": NoWebSearchStrategy,
        }

        strategy_class = strategies.get(strategy_type, NoWebSearchStrategy)
        return strategy_class(config)
```

---

## Configuration Design

### Domain Config (Single Source of Truth)

```json
{
  "domain_id": "cooking",
  "domain_type": "4",
  "name": "Cooking & Recipes",
  "description": "Culinary knowledge with web search",

  "specialist": {
    "plugin_id": "researcher",
    "module": "plugins.research.research_specialist",
    "class": "ResearchSpecialistPlugin",
    "config": {
      "enable_web_search": true
    }
  },

  "behaviors": {
    "scope": {
      "type": "none"
    },
    "web_search": {
      "enabled": true,
      "type": "type4",
      "local_relevance_threshold": 0.5
    }
  },

  "plugins": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "enabled": true,
      "config": {
        "mode": "replace",
        "scope": {"type": "none"},
        "prompts": {
          "type": "web_search",
          "system_message": "You are a professional chef. Provide detailed, accurate recipes with measurements, temperatures, and timing."
        },
        "web_search": {
          "type": "type4",
          "require_relevance": 0.5
        },
        "llm": {
          "model": "deepseek-chat",
          "temperature": 0.6
        }
      }
    },
    {
      "module": "plugins.enrichers.citation_enricher",
      "class": "CitationEnricher",
      "enabled": true,
      "config": {
        "style": "recipe",
        "include_sources": true
      }
    }
  ]
}
```

### ExFrame Config (Different Behaviors, Same Plugin)

```json
{
  "domain_id": "exframe",
  "domain_type": "3",

  "behaviors": {
    "scope": {
      "type": "topics",
      "allowed_topics": ["exframe", "plugin", "architecture", "configuration"],
      "out_of_scope_message": "I can only answer questions about ExFrame's architecture, configuration, plugin system, and usage."
    },
    "web_search": {
      "enabled": false
    }
  },

  "plugins": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "scope": {"type": "topics"},
        "prompts": {
          "type": "document_context",
          "system_message": "You are an ExFrame expert..."
        }
      }
    }
  ]
}
```

---

## Traceability Design

### Goal: "Tick like a Swiss watch"

Every operation should be observable through the trace system.

### Trace Points

```python
# core/tracer.py

class Tracer:
    """Centralized tracing for all operations"""

    def __init__(self):
        self.hooks = []

    def add_hook(self, hook: TraceHook):
        """Add a hook for tracing (future: Release 4)"""
        self.hooks.append(hook)

    def trace_operation(
        self,
        component: str,
        operation: str,
        data: Dict
    ):
        """Trace an operation"""
        trace_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": component,
            "operation": operation,
            "data": data
        }

        # Log to state machine
        self._log_to_state_machine(trace_entry)

        # Log to query trace
        self._log_to_query_trace(trace_entry)

        # Call hooks (future)
        for hook in self.hooks:
            hook.on_trace(trace_entry)


# Usage throughout codebase:

class Type4AnalyticDomain:
    async def process_query(self, query, context):
        tracer.trace_operation(
            component="Type4AnalyticDomain",
            operation="process_query_start",
            data={"query": query, "context": context.as_dict()}
        )

        local_results = await self._search_local(query)

        tracer.trace_operation(
            component="Type4AnalyticDomain",
            operation="local_search_complete",
            data={"results_count": len(local_results), "max_relevance": ...}
        )

        # ... etc
```

### Trace Output (Human Readable)

```
[TRACE] Type4AnalyticDomain.process_query_start
  query: "recipe for raisin tart"

[TRACE] Type4AnalyticDomain.local_search_complete
  results: 10
  max_relevance: 0.3
  sufficient: false

[TRACE] Type4AnalyticDomain.forming_extension_request
  reason: "Low relevance local patterns"

[TRACE] LLMEnricher.process
  prompt_builder: "WebSearchRequestPromptBuilder"
  scope_check: "NoOpScopeCheck"

[TRACE] LLMEnricher.llm_call_start
  model: deepseek-chat

[TRACE] LLMEnricher.llm_call_complete
  duration_ms: 1523

[TRACE] Type4AnalyticDomain.process_query_complete
  can_extend_with_web_search: true
```

---

## Implementation Schedule

### Release 1: Foundation (Week 1)
**Goal**: Establish new architecture without breaking existing code

**Tasks**:
1. Create `domain_type.py` with base classes
   - `DomainType` (ABC)
   - `QueryContext`, `QueryResult`
2. Create `Type4AnalyticDomain` class
3. Create `Plugin` base class and `PluginFactory`
4. Add `tracer.py` with basic trace points
5. Run in parallel with existing code (no migration yet)

**Deliverable**: New code files, no breaking changes

---

### Release 2: Plugin Refactor (Week 2)
**Goal**: Refactor LLMEnricher to use strategies

**Tasks**:
1. Create strategy classes:
   - `ScopeCheck` + factory
   - `PromptBuilder` + factory
   - `WebSearchStrategy` + factory
2. Rewrite `LLMEnricher` to use strategies
3. Add config-based behavior selection
4. Update cooking domain config for new format
5. Test Type 4 with new LLMEnricher

**Deliverable**: Cooking domain using new LLMEnricher

---

### Release 3: Domain Type Migration (Week 3)
**Goal**: Migrate all domains to new domain type classes

**Tasks**:
1. Create `Type3DocumentDomain`
2. Create `Type1PatternDomain`
3. Migrate exframe domain to Type 3
4. Migrate other domains
5. Remove old query processing code

**Deliverable**: All domains using new domain type classes

---

### Release 4: Polish & Tracing (Week 4)
**Goal**: Complete traceability, remove technical debt

**Tasks**:
1. Add trace hooks throughout codebase
2. Build trace viewer UI
3. Remove old enricher code
4. Update documentation
5. Performance testing

**Deliverable**: Complete system with full traceability

---

## File Structure

```
generic_framework/
├── core/
│   ├── domain_type.py              # NEW: Domain type base classes
│   ├── tracer.py                    # NEW: Centralized tracing
│   └── ...
├── domain_types/                     # NEW: Domain type implementations
│   ├── __init__.py
│   ├── type1_pattern.py
│   ├── type3_document.py
│   └── type4_analytic.py
├── plugins/
│   ├── base.py                      # NEW: Plugin base class
│   ├── strategies/                  # NEW: Strategy implementations
│   │   ├── __init__.py
│   │   ├── scope_check.py
│   │   ├── prompt_builder.py
│   │   └── web_search.py
│   └── enrichers/
│       ├── llm_enricher.py         # REFACTORED: Now uses strategies
│       └── ...
└── ...
```

---

## Success Criteria

### Modularity
✓ Each class has single responsibility
✓ Plugins are < 200 lines
✓ Strategies are < 100 lines
✓ No cross-cutting concerns

### Configurability
✓ Behavior defined in config, not code
✓ Same plugin class serves different domains
✓ No code changes needed for new behaviors

### Understandability
✓ Clear class hierarchy
✓ Obvious data flow
✓ No "magic" type detection

### Traceability
✓ Every operation logged
✓ Human-readable trace output
✓ Easy debugging

---

## Risk Mitigation

### Risk: Breaking Changes
**Mitigation**: Run in parallel during Release 1-2

### Risk: Performance
**Mitigation**: Benchmark new vs old code

### Risk: Configuration Complexity
**Mitigation**: Provide config templates, validation

---

## Next Steps

1. **Review this design** - Does it address your concerns?
2. **Approve Release 1 scope** - Ready to start?
3. **Create task breakdown** - Detailed tasks for each release?

Let me know your thoughts and I'll adjust accordingly.
