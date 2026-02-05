# Phase 1: Persona + Override Design
## Simplify Existing Code with Minimal Changes

**Version**: 1.0.0
**Date**: 2026-02-04
**Duration**: 1 week
**Approach**: Incremental simplification, not replacement

---

## Overview

**Goal**: Eliminate ~1000 lines of conditional logic by consolidating to 3 personas with one override switch.

**Key Insight**: Most of the complexity comes from trying to handle 5 domain types with scattered conditionals. Simplify to 3 personas (Poet, Librarian, Researcher) with pattern override capability.

---

## Core Concept

### The One Switch: Pattern Override

```
Query comes in → Check domain for patterns
                ↓
        Patterns found?
       ↙              ↘
     YES               NO
      ↓                ↓
Use patterns    Use persona's data source
(override)      (void/library/internet)
      ↓                ↓
      └────→ LLM ←────┘
```

**That's it.** No more domain type checking, no more specialist ID matching, no more search strategy strings.

---

## Three Personas

### Poet (Pure Generation)
```python
POET = Persona(
    name="poet",
    data_source="void",      # No external sources
    show_thinking=False       # Don't show reasoning
)
```

**Use For**:
- Creative writing (poems, stories)
- Pure generation tasks
- When no external data needed

**Example Domains**: poetry, creative_writing

---

### Librarian (Document Search)
```python
LIBRARIAN = Persona(
    name="librarian",
    data_source="library",   # Search local documents
    show_thinking=True        # Show reasoning
)
```

**Use For**:
- Knowledge retrieval from documents
- Closed document systems
- Pattern-based knowledge

**Example Domains**: exframe, llm_consciousness

---

### Researcher (Web Search)
```python
RESEARCHER = Persona(
    name="researcher",
    data_source="internet",  # Search the web
    show_thinking=True        # Show reasoning
)
```

**Use For**:
- Web research
- Current information
- When local docs insufficient

**Example Domains**: cooking, diy

---

## Implementation

### Persona Class

```python
"""
generic_framework/core/persona.py

Simple persona class - one per data source type.
"""

from typing import Optional, Dict, List, Any
import logging


class Persona:
    """
    A persona is a configured LLM responder with a data source.

    Core behavior:
    - If patterns provided → use patterns (override)
    - Else → use configured data source

    That's the entire decision tree.
    """

    def __init__(
        self,
        name: str,
        data_source: str,
        show_thinking: bool = False,
        trace: bool = False
    ):
        """
        Initialize persona.

        Args:
            name: Persona name (poet/librarian/researcher)
            data_source: Data source type (void/library/internet)
            show_thinking: Whether to request LLM reasoning
            trace: Whether to log trace information
        """
        self.name = name
        self.data_source = data_source
        self.show_thinking = show_thinking
        self.trace = trace
        self.logger = logging.getLogger(f"persona.{name}")

    def respond(
        self,
        query: str,
        override_patterns: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Respond to query using persona's data source.

        THE CORE DECISION: If patterns provided, use them.
        Otherwise, use persona's configured data source.

        Args:
            query: User query
            override_patterns: Optional patterns to override data source

        Returns:
            Response dict with answer and metadata
        """
        if self.trace:
            self.logger.info(f"Processing query: {query}")

        # THE ONE DECISION
        if override_patterns:
            if self.trace:
                self.logger.info(f"Using pattern override ({len(override_patterns)} patterns)")
            context = self._format_patterns(override_patterns)
            source = "patterns_override"
        else:
            if self.trace:
                self.logger.info(f"Using data source: {self.data_source}")
            context = self._get_data_source_context(query)
            source = self.data_source

        # Build prompt
        prompt = self._build_prompt(query, context)

        # Call LLM
        answer = self._call_llm(prompt)

        return {
            "answer": answer,
            "source": source,
            "persona": self.name,
            "query": query,
            "show_thinking": self.show_thinking
        }

    def _get_data_source_context(self, query: str) -> Optional[str]:
        """
        Get context from persona's configured data source.

        Args:
            query: User query

        Returns:
            Context string or None (for void)
        """
        if self.data_source == "void":
            # Pure generation - no context needed
            return None

        elif self.data_source == "library":
            # Search local document library
            from ..knowledge.json_kb import search_library
            results = search_library(query, max_results=10)
            return self._format_library_results(results)

        elif self.data_source == "internet":
            # Search the web
            from ..research.web_search import search_internet
            results = search_internet(query, max_results=5)
            return self._format_web_results(results)

        else:
            raise ValueError(f"Unknown data source: {self.data_source}")

    def _format_patterns(self, patterns: List[Dict]) -> str:
        """
        Format patterns into context string.

        Args:
            patterns: List of pattern dicts

        Returns:
            Formatted context string
        """
        formatted = []
        for p in patterns:
            formatted.append(f"""
Pattern: {p.get('name', 'Untitled')}
{p.get('solution', p.get('content', ''))}
""")
        return "\n\n".join(formatted)

    def _format_library_results(self, results: List[Dict]) -> str:
        """Format library search results"""
        if not results:
            return None

        formatted = []
        for r in results:
            formatted.append(f"""
Document: {r.get('title', 'Untitled')}
{r.get('content', '')}
""")
        return "\n\n".join(formatted)

    def _format_web_results(self, results: List[Dict]) -> str:
        """Format web search results"""
        if not results:
            return None

        formatted = []
        for r in results:
            formatted.append(f"""
Source: {r.get('title', 'Untitled')} ({r.get('url', '')})
{r.get('snippet', '')}
""")
        return "\n\n".join(formatted)

    def _build_prompt(self, query: str, context: Optional[str]) -> str:
        """
        Build LLM prompt.

        Args:
            query: User query
            context: Context string or None

        Returns:
            Complete prompt for LLM
        """
        if context:
            prompt = f"Context:\n{context}\n\nQuery: {query}\n"
        else:
            prompt = query

        if self.show_thinking:
            prompt += "\n\nBefore answering, briefly explain your reasoning."

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with prompt.

        TODO: Integrate with actual LLM client

        Args:
            prompt: Complete prompt

        Returns:
            LLM response
        """
        # TODO: Replace with actual LLM integration
        from ..llm.client import call_llm
        return call_llm(prompt, show_thinking=self.show_thinking)
```

---

### The Three Personas (Configured Once)

```python
"""
generic_framework/core/personas.py

The three personas - configured once at startup.
"""

from .persona import Persona


# Poet: Pure generation, no external sources
POET = Persona(
    name="poet",
    data_source="void",
    show_thinking=False,
    trace=True
)


# Librarian: Document search, show reasoning
LIBRARIAN = Persona(
    name="librarian",
    data_source="library",
    show_thinking=True,
    trace=True
)


# Researcher: Web search, show reasoning
RESEARCHER = Persona(
    name="researcher",
    data_source="internet",
    show_thinking=True,
    trace=True
)


def get_persona(name: str) -> Persona:
    """
    Get persona by name.

    Args:
        name: Persona name (poet/librarian/researcher)

    Returns:
        Persona instance

    Raises:
        ValueError: If persona name unknown
    """
    personas = {
        "poet": POET,
        "librarian": LIBRARIAN,
        "researcher": RESEARCHER
    }

    persona = personas.get(name.lower())
    if not persona:
        raise ValueError(f"Unknown persona: {name}")

    return persona
```

---

### Query Processor (The Glue)

```python
"""
generic_framework/core/query_processor.py

Process queries with pattern override logic.
"""

from typing import Dict, Any
from .personas import get_persona
from ..knowledge.json_kb import search_domain_patterns


def process_query(query: str, domain_name: str) -> Dict[str, Any]:
    """
    Process query with pattern override logic.

    Decision tree:
    1. Load domain config to get persona type
    2. Search domain for patterns matching query
    3. If patterns found → persona.respond(query, patterns)
    4. Else → persona.respond(query)

    Args:
        query: User query
        domain_name: Domain name

    Returns:
        Response dict with answer and metadata
    """
    # Load domain config
    from ..config.loader import load_domain_config
    config = load_domain_config(domain_name)

    # Get persona
    persona_type = config.get("persona", "librarian")
    persona = get_persona(persona_type)

    # Search domain patterns (if override enabled)
    patterns = None
    if config.get("enable_pattern_override", True):
        patterns = search_domain_patterns(domain_name, query, max_results=5)

    # THE DECISION: Override or not?
    if patterns and len(patterns) > 0:
        # Use patterns (override)
        response = persona.respond(query, override_patterns=patterns)
    else:
        # Use persona's data source
        response = persona.respond(query)

    # Add domain metadata
    response["domain"] = domain_name
    response["pattern_override_used"] = bool(patterns)

    return response
```

---

## Domain Configuration (Simplified)

### Before (Complex):
```json
{
  "name": "cooking",
  "domain_type": "4",
  "specialists": [...],
  "plugins": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "domain_type": "4",
        "specialist_id": "research_specialist",
        ...
      }
    }
  ]
}
```

### After (Simple):
```json
{
  "name": "cooking",
  "persona": "researcher",
  "enable_pattern_override": true,
  "settings": {
    "show_thinking": true,
    "trace": true
  }
}
```

**That's it.** 90% smaller config.

---

## Domain Type → Persona Mapping

| Old Type | Old Name | New Persona | Rationale |
|----------|----------|-------------|-----------|
| Type 1 | Creative Generator | Poet | Pure generation, no sources |
| Type 2 | Knowledge Retrieval | Librarian | Uses local documents |
| Type 3 | Document Store Search | Librarian | Uses local documents |
| Type 4 | Analytical Engine | Researcher | Uses web + local |
| Type 5 | Hybrid Assistant | Researcher | Uses web + local |

**5 types → 3 personas**

---

## What Gets Eliminated

### Conditionals Removed (~1000 lines):

```python
# ❌ DELETE ALL OF THIS
if domain_type == "3":
    if specialist_id == "exframe_specialist":
        if search_strategy == "research_primary":
            # Type 3 logic

elif domain_type == "4":
    if web_search_enabled:
        if patterns_insufficient:
            # Request web search
    else:
        # Type 4 local logic

# ... 1000+ more lines of conditionals
```

### Replaced With (~20 lines):

```python
# ✅ SIMPLE LOGIC
patterns = search_domain_patterns(domain, query)

if patterns:
    response = persona.respond(query, override_patterns=patterns)
else:
    response = persona.respond(query)
```

---

## Migration Steps

### Step 1: Create Persona Class (Day 1-2)
- Write `persona.py` (~200 lines)
- Write tests for Persona class
- Verify can instantiate and respond

### Step 2: Configure Three Personas (Day 2)
- Write `personas.py` (~50 lines)
- Test each persona independently
- Verify data sources work

### Step 3: Add Query Processor (Day 3)
- Write `query_processor.py` (~100 lines)
- Implement pattern override logic
- Test with sample queries

### Step 4: Update Domain Configs (Day 4)
- Convert all domain.json files to new format
- Map domain types to personas
- Test each domain

### Step 5: Wire Into Engine (Day 5)
- Update `engine.py` to use query_processor
- Delete old LLMEnricher
- Run full test suite
- Deploy

---

## Testing Strategy

### Unit Tests

```python
# test_persona.py
def test_poet_no_override():
    """Poet uses void data source"""
    response = POET.respond("Write a poem")
    assert response["source"] == "void"
    assert response["persona"] == "poet"

def test_librarian_with_override():
    """Librarian uses patterns when provided"""
    patterns = [{"name": "Test", "solution": "Content"}]
    response = LIBRARIAN.respond("Test query", override_patterns=patterns)
    assert response["source"] == "patterns_override"

def test_researcher_no_patterns():
    """Researcher uses internet when no patterns"""
    response = RESEARCHER.respond("Current news")
    assert response["source"] == "internet"
```

### Integration Tests

```python
# test_query_processor.py
def test_cooking_domain_with_patterns():
    """Cooking domain uses patterns if found"""
    response = process_query("How to cook rice", "cooking")
    assert response["domain"] == "cooking"
    # Will use patterns if found, else web search

def test_poetry_domain_no_patterns():
    """Poetry domain uses poet (void)"""
    response = process_query("Write a haiku", "poetry")
    assert response["persona"] == "poet"
    assert response["source"] in ["void", "patterns_override"]
```

---

## Success Metrics

### Lines of Code
- Before: 1450+ lines (LLMEnricher)
- After: ~350 lines (Persona + query_processor)
- **Reduction**: 75%

### Conditionals
- Before: ~1000 lines of `if domain_type ==`
- After: 1 conditional (`if patterns:`)
- **Reduction**: 99%

### Domain Config Size
- Before: ~50 lines per domain
- After: ~5 lines per domain
- **Reduction**: 90%

---

## What We Keep

1. **All existing logs** - No observability loss
2. **All existing behavior** - Outputs work the same
3. **Trace infrastructure** - Still works
4. **Verbose mode** - Still works

**What changes**: HOW the code is organized, not WHAT it does.

---

## Advantages

1. **Incremental** - Can roll back easily
2. **Simple** - 3 personas, 1 override
3. **Fast** - 1 week implementation
4. **No breaking changes** - User-facing behavior unchanged
5. **Foundation** - Sets up for future improvements

---

## Future Evolution (Maybe)

If Phase 1 works well, Phase 2 could be:
- More personas?
- More sophisticated override logic?
- Plugin system for personas?

But Phase 1 might be sufficient. Keep it simple.

---

**Status**: Design complete, ready for implementation
**Timeline**: 1 week
**Risk**: LOW (incremental change)
**Impact**: HIGH (eliminates 1000 lines of conditionals)
