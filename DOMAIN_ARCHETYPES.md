# Domain Archetypes: Query Flow Classifications

**Version:** 1.1
**Date:** 2026-01-24
**Status:** DESIGN
**Purpose:** Classify domains by query flow behavior to enable template-based domain creation

---

## Executive Summary

Currently, ExFrame has domains that behave very differently from each other:

- **Poetry Domain** → Creative LLM generation, ignores patterns
- **Cooking Domain** → Pattern search + LLM enhancement
- **ExFrame Domain** → Document store + external knowledge + sessions
- **Test Domains** → Need flexible behavior for testing

This creates architectural complexity where each domain may need custom code. The solution is to **classify domains into archetypes** with pre-defined query flows and configurations.

**Key Insight:** Each archetype defines the **complete workflow** from query to reply:

```
QUERY → SPECIALIST → ENRICHER → FORMATTER → REPLY
```

When creating a new domain, you select an archetype, and the system provides:
- Pre-configured query pipeline
- Specialist type and behavior
- Enricher chain configuration
- Response formatting logic
- UI/UX patterns

---

## The 6 Domain Archetypes

### Archetype 1: CREATIVE_GENERATOR

**Purpose:** Generate original creative content (poems, stories, code, etc.)

**Query Flow:**
```
Query → Specialist (routes to LLM) → LLM Enricher (creative mode) → Response
```

**Characteristics:**
- Ignores pattern search results
- Direct LLM generation
- High temperature (0.7-0.9)
- No "Patterns referenced" section
- Focus on originality, not accuracy

**Configuration Template:**
```json
{
  "archetype": "creative_generator",
  "specialist": {
    "type": "GeneralistPlugin",
    "threshold": 0.1,
    "keywords": ["write", "create", "make", "generate", "compose"],
    "creative_keywords": ["poem", "story", "haiku", "sonnet", "code"]
  },
  "enrichers": [
    {
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.8,
        "creative_mode": true
      }
    }
  ],
  "response_format": "direct_llm_only"
}
```

**Domains Using This:**
- `poetry_domain` - Poems, haikus, verse
- `psycho` - Psychological analysis (creative)

**UI/UX Pattern:**
- Single clean response
- No pattern list
- "Regenerate" button prominent
- Optional style/format controls

---

### Archetype 2: KNOWLEDGE_RETRIEVAL

**Purpose:** Search and retrieve factual information from curated patterns

**Query Flow:**
```
Query → Pattern Search (semantic) → Specialist → LLM Enhancement → Response
```

**Characteristics:**
- Semantic search on local patterns
- LLM synthesizes results
- Shows "Patterns referenced"
- Medium temperature (0.3-0.5)
- Focus on accuracy

**Configuration Template:**
```json
{
  "archetype": "knowledge_retrieval",
  "specialist": {
    "type": "GeneralistPlugin",
    "threshold": 0.2
  },
  "knowledge_base": {
    "similarity_threshold": 0.3,
    "max_results": 10
  },
  "enrichers": [
    {
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.4,
        "max_patterns": 10
      }
    }
  ],
  "response_format": "llm_synthesis_with_sources"
}
```

**Domains Using This:**
- `cooking` - Recipes, techniques
- `python` - Python programming
- `first_aid` - Medical information
- `gardening` - Gardening advice
- `diy` - DIY projects
- `binary_symmetry` - Binary operations

**UI/UX Pattern:**
- LLM response first
- "Patterns referenced" section at end
- Pattern cards clickable for details
- Source links shown

---

### Archetype 3: DOCUMENT_STORE_SEARCH

**Purpose:** Search external knowledge sources (docs, web, other instances)

**Query Flow:**
```
Query → Document Store Search → Local Patterns (fallback) → Response
```

**Characteristics:**
- External document search PRIMARY
- Local patterns SECONDARY/fallback
- Session-based tracking
- Research strategy integration
- Shows "Sources searched"

**Configuration Template:**
```json
{
  "archetype": "document_store_search",
  "specialist": {
    "type": "ExFrameSpecialistPlugin",
    "document_store_enabled": true,
    "local_patterns_enabled": true,
    "reply_capture_enabled": true
  },
  "document_store": {
    "type": "exframe_instance",
    "config": {
      "remote_url": "",
      "timeout": 30
    }
  },
  "research_strategy": {
    "type": "document",
    "documents": [
      {"type": "file", "path": "README.md"},
      {"type": "file", "path": "context.md"}
    ]
  },
  "enrichers": [
    {
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.6
      }
    }
  ],
  "response_format": "llm_first_sources_last"
}
```

**Domains Using This:**
- `exframe` - External documentation search

**UI/UX Pattern:**
- LLM synthesis first
- "Sources searched" section at end
- Document titles clickable
- Session history sidebar
- "Capture as pattern" button

---

### Archetype 4: ANALYTICAL_ENGINE

**Purpose:** Complex analysis, correlation, research synthesis

**Query Flow:**
```
Query → Research Agent (multi-step) → Data Gathering → Analysis → Report
```

**Characteristics:**
- Multi-step research
- Task decomposition
- Data correlation
- Report generation
- Slower (seconds to minutes)

**Configuration Template:**
```json
{
  "archetype": "analytical_engine",
  "specialist": {
    "type": "ResearchSpecialistPlugin",
    "max_steps": 10,
    "timeout": 300
  },
  "research_capabilities": {
    "web_search": true,
    "document_search": true,
    "data_correlation": true,
    "report_generation": true
  },
  "enrichers": [
    {
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.5,
        "max_tokens": 8192
      }
    }
  ],
  "response_format": "structured_report"
}
```

**Domains Using This:**
- `llm_consciousness` - LLM behavior analysis (potential)
- Future: `research` - General research domain

**UI/UX Pattern:**
- Progress indicator (step 1/5...)
- Interim results shown
- Final formatted report
- "Download report" button
- "Save as pattern" button

---

### Archetype 5: HYBRID_ASSISTANT

**Purpose:** Combines multiple behaviors (fallback to LLM when patterns weak)

**Query Flow:**
```
Query → Pattern Search → Confidence Check
       ├─ High confidence → Pattern-based response
       └─ Low confidence → LLM fallback (with confirmation)
```

**Workflow States:**
```
STATE 1: PATTERN_SEARCH
  ├─ Input: User query
  ├─ Action: Semantic pattern search
  ├─ Output: Top N patterns
  └─ Next: CONFIDENCE_CHECK

STATE 2: CONFIDENCE_CHECK
  ├─ Input: Pattern results
  ├─ Action: Calculate confidence score
  ├─ Decision: confidence >= threshold?
  │   ├─ YES → STATE 3: PATTERN_RESPONSE
  │   └─ NO → STATE 4: OFFER_FALLBACK
  └─ Next: Based on decision

STATE 3: PATTERN_RESPONSE
  ├─ Input: Selected patterns
  ├─ Action: Format pattern-based response
  ├─ Output: Response with patterns
  └─ End

STATE 4: OFFER_FALLBACK
  ├─ Input: Low confidence patterns
  ├─ Action: Show patterns + "Extend search?" button
  ├─ Output: Partial response + confirmation request
  ├─ User Action: Accept/Decline LLM
  └─ Next: If accepted → STATE 5: LLM_FALLBACK

STATE 5: LLM_FALLBACK
  ├─ Input: User confirmed LLM
  ├─ Action: Call LLM (with optional research)
  ├─ Output: LLM-generated response
  └─ End
```

**Characteristics:**
- Pattern search first
- Confidence-based routing
- LLM as fallback
- User confirmation for LLM
- Best of both worlds

**Configuration Template:**
```json
{
  "archetype": "hybrid_assistant",
  "workflow": "confidence_based_routing",
  "states": ["PATTERN_SEARCH", "CONFIDENCE_CHECK", "PATTERN_RESPONSE", "OFFER_FALLBACK", "LLM_FALLBACK"],
  "specialist": {
    "type": "GeneralistPlugin",
    "threshold": 0.2
  },
  "knowledge_base": {
    "similarity_threshold": 0.4,
    "min_confidence": 0.3
  },
  "enrichers": [
    {
      "class": "LLMFallbackEnricher",
      "config": {
        "mode": "fallback",
        "min_confidence": 0.3,
        "require_confirmation": true,
        "research_strategy": {
          "type": "internet",
          "search_provider": "auto"
        }
      }
    }
  ],
  "response_format": "pattern_first_llm_fallback"
}
```

**Domains Using This:**
- Most domains could use this as default
- Flexible for different use cases

**UI/UX Pattern:**
- Pattern results shown first
- "Extend search with AI?" button
- Confirmation dialog
- LLM response appended if confirmed

---

### Archetype 6: TEST_ASSISTANT

**Purpose:** Flexible domain for testing, experimentation, development

**Query Flow:**
```
Query → [Configurable Pipeline] → Response
```

**Workflow States (Highly Configurable):**
```
STATE 1: QUERY_RECEIVE
  ├─ Input: User query
  ├─ Action: Log query, extract metadata
  ├─ Configuration: query_capture_mode
  └─ Next: Based on test_mode

STATE 2: TEST_MODE_DISPATCHER
  ├─ Input: Query + test_mode
  ├─ Action: Route to test handler
  ├─ Options:
  │   ├─ "echo" → ECHO_MODE (return query as-is)
  │   ├─ "pattern_search" → PATTERN_SEARCH_MODE
  │   ├─ "llm_only" → LLM_ONLY_MODE
  │   ├─ "llm_with_patterns" → LLM_WITH_PATTERNS_MODE
  │   ├─ "error_simulation" → ERROR_MODE (return test error)
  │   ├─ "delay_simulation" → DELAY_MODE (simulate slow response)
  │   └─ "custom" → CUSTOM_MODE (run custom handler)
  └─ Next: Based on selection

STATE 3: RESPONSE_LOGGER
  ├─ Input: Generated response
  ├─ Action: Log full interaction
  ├─ Metadata: timing, patterns_used, llm_used, etc.
  └─ End
```

**Characteristics:**
- **No assigned domains** - pure test space
- Fully configurable pipeline
- Test mode selection via config
- Extensive logging/metrics
- Error simulation for testing
- Response timing simulation

**Configuration Template:**
```json
{
  "archetype": "test_assistant",
  "workflow": "configurable_test_pipeline",
  "description": "Flexible test domain for experimentation",

  "test_mode": "echo",
  "available_modes": [
    "echo",
    "pattern_search",
    "llm_only",
    "llm_with_patterns",
    "error_simulation",
    "delay_simulation",
    "custom"
  ],

  "specialist": {
    "type": "GeneralistPlugin",
    "threshold": 0.0,
    "test_handlers": {
      "echo": "return query unchanged",
      "pattern_search": "standard semantic search",
      "llm_only": "direct LLM call",
      "llm_with_patterns": "LLM with pattern context",
      "error": "simulate specific error",
      "delay": "add artificial delay"
    }
  },

  "enrichers": [
    {
      "class": "TestEnricher",
      "config": {
        "log_all_interactions": true,
        "capture_timing": true,
        "capture_patterns": true,
        "capture_llm_requests": true,
        "simulation_delay_ms": 0
      }
    }
  ],

  "response_format": "configurable",
  "ui_hints": {
    "show_test_panel": true,
    "show_mode_selector": true,
    "show_interaction_log": true,
    "show_performance_metrics": true
  }
}
```

**Domains Using This:**
- **NONE** - This archetype is not assigned to any production domain
- Used for:
  - `test_93` - Testing new features
  - `test_domain` - General test domain
  - Future: Any new test domain

**UI/UX Pattern:**
- Test mode selector dropdown
- Interaction log panel
- Performance metrics display
- "Simulate error" controls
- "Clear logs" button
- Debug panel toggle

---

## Mapping Existing Domains to Archetypes

**Purpose:** Combines multiple behaviors (fallback to LLM when patterns weak)

**Query Flow:**
```
Query → Pattern Search → Confidence Check
       ├─ High confidence → Pattern-based response
       └─ Low confidence → LLM fallback (with confirmation)
```

**Characteristics:**
- Pattern search first
- Confidence-based routing
- LLM as fallback
- User confirmation for LLM
- Best of both worlds

**Configuration Template:**
```json
{
  "archetype": "hybrid_assistant",
  "specialist": {
    "type": "GeneralistPlugin",
    "threshold": 0.2
  },
  "knowledge_base": {
    "similarity_threshold": 0.4,
    "min_confidence": 0.3
  },
  "enrichers": [
    {
      "class": "LLMFallbackEnricher",
      "config": {
        "mode": "fallback",
        "min_confidence": 0.3,
        "require_confirmation": true,
        "research_strategy": {
          "type": "internet",
          "search_provider": "auto"
        }
      }
    }
  ],
  "response_format": "pattern_first_llm_fallback"
}
```

**Domains Using This:**
- Most domains could use this as default
- Flexible for different use cases

**UI/UX Pattern:**
- Pattern results shown first
- "Extend search with AI?" button
- Confirmation dialog
- LLM response appended if confirmed

---

## Decision Tree: Which Archetype?

When creating a new domain, ask these questions:

```
Q1: Is this a TEST/EXPERIMENTAL domain?
    YES → TEST_ASSISTANT (provides flexible test space)

    NO → Q2: Is the domain generating ORIGINAL creative content?
    YES → CREATIVE_GENERATOR

    NO → Q3: Does it need EXTERNAL/REAL-TIME data?
    YES → Q4: Is it complex multi-step research?
        YES → ANALYTICAL_ENGINE
        NO → DOCUMENT_STORE_SEARCH

    NO → Q5: Should LLM only be used as FALLBACK (with user confirmation)?
    YES → HYBRID_ASSISTANT
    NO → KNOWLEDGE_RETRIEVAL
```

**Quick Reference:**

| Your Need | Use Archetype |
|-----------|--------------|
| Testing/Development | TEST_ASSISTANT |
| Poems, stories, art | CREATIVE_GENERATOR |
| How-to, FAQs, docs | KNOWLEDGE_RETRIEVAL |
| External docs, API docs | DOCUMENT_STORE_SEARCH |
| Research, analysis | ANALYTICAL_ENGINE |
| General purpose, flexible | HYBRID_ASSISTANT |

---

## Implementation Plan

### Phase 1: Archetype Configuration Schema

Create archetype definitions that can be selected when creating a domain:

```python
# generic_framework/core/archetypes.py

@dataclass
class DomainArchetype:
    """Base class for domain archetypes."""
    archetype_id: str
    name: str
    description: str

    # Default configuration
    specialist_type: str
    specialist_config: Dict[str, Any]
    enricher_configs: List[Dict[str, Any]]
    kb_config: Dict[str, Any]
    response_format: str

    # UI/UX hints
    ui_pattern: str
    show_patterns: bool
    show_sources: bool
    enable_regenerate: bool
    enable_capture: bool

# Predefined archetypes
ARCHETYPE_CREATIVE = DomainArchetype(
    archetype_id="creative_generator",
    name="Creative Generator",
    description="Generate original creative content",
    # ... (see templates above)
)

ARCHETYPE_KNOWLEDGE = DomainArchetype(
    archetype_id="knowledge_retrieval",
    name="Knowledge Retrieval",
    description="Search and retrieve factual information",
    # ...
)

ARCHETYPE_DOC_STORE = DomainArchetype(
    archetype_id="document_store_search",
    name="Document Store Search",
    description="Search external knowledge sources",
    # ...
)

ARCHETYPE_ANALYTICAL = DomainArchetype(
    archetype_id="analytical_engine",
    name="Analytical Engine",
    description="Complex analysis and research",
    # ...
)

ARCHETYPE_HYBRID = DomainArchetype(
    archetype_id="hybrid_assistant",
    name="Hybrid Assistant",
    description="Pattern-first with LLM fallback",
    # ...
)

ARCHETYPE_MAP = {
    "creative_generator": ARCHETYPE_CREATIVE,
    "knowledge_retrieval": ARCHETYPE_KNOWLEDGE,
    "document_store_search": ARCHETYPE_DOC_STORE,
    "analytical_engine": ARCHETYPE_ANALYTICAL,
    "hybrid_assistant": ARCHETYPE_HYBRID,
}
```

### Phase 2: Domain Creation API

```python
# API endpoint for creating domains with archetype selection

@router.post("/api/domains/create-from-archetype")
async def create_domain_from_archetype(request: DomainCreateRequest):
    """
    Create a new domain by selecting an archetype.

    Request:
    {
        "domain_id": "my_new_domain",
        "domain_name": "My New Domain",
        "archetype": "creative_generator",
        "custom_config": { ... }  // optional overrides
    }

    Response:
    {
        "domain_id": "my_new_domain",
        "status": "created",
        "config": { ... }  // generated config
    }
    """
    archetype = ARCHETYPE_MAP.get(request.archetype)
    if not archetype:
        raise HTTPException(404, f"Unknown archetype: {request.archetype}")

    # Generate domain config from archetype
    domain_config = generate_domain_config(archetype, request.custom_config)

    # Create domain directory and files
    await create_domain_directory(request.domain_id, domain_config)

    return {"domain_id": request.domain_id, "status": "created", "config": domain_config}
```

### Phase 3: Frontend Domain Creator

```javascript
// Frontend: Domain creation form with archetype selection

function DomainCreator() {
    const archetypes = [
        {
            id: "creative_generator",
            name: "Creative Generator",
            description: "Generate original creative content (poems, stories, code)",
            examples: ["Poetry", "Creative Writing", "Code Generation"],
            icon: "wand-magic-sparkles"
        },
        {
            id: "knowledge_retrieval",
            name: "Knowledge Retrieval",
            description: "Search curated knowledge base",
            examples: ["Cooking", "Technical Docs", "FAQ"],
            icon: "database"
        },
        {
            id: "document_store_search",
            name: "Document Store Search",
            description: "Search external documentation/knowledge",
            examples: ["API Documentation", "Research Papers"],
            icon: "magnifying-glass"
        },
        {
            id: "analytical_engine",
            name: "Analytical Engine",
            description: "Complex multi-step research and analysis",
            examples: ["Research Assistant", "Data Analyst"],
            icon: "brain-circuit"
        },
        {
            id: "hybrid_assistant",
            name: "Hybrid Assistant",
            description: "Patterns first, LLM fallback",
            examples: ["General Purpose", "Support"],
            icon: "layers"
        }
    ];

    // Render archetype selection UI
    return (
        <div class="domain-creator">
            <h2>Create New Domain</h2>

            <div class="archetype-grid">
                {archetypes.map(arch => (
                    <ArchetypeCard
                        key={arch.id}
                        archetype={arch}
                        onSelect={() => selectArchetype(arch)}
                    />
                ))}
            </div>

            {selectedArchetype && (
                <DomainConfigForm
                    archetype={selectedArchetype}
                    onCreate={handleCreateDomain}
                />
            )}
        </div>
    );
}
```

---

## Mapping Existing Domains to Archetypes

| Domain | Current Archetype | Notes |
|--------|------------------|-------|
| `poetry_domain` | CREATIVE_GENERATOR | Uses creative mode, ignores patterns |
| `psycho` | CREATIVE_GENERATOR | Creative analysis |
| `cooking` | KNOWLEDGE_RETRIEVAL | Standard pattern search |
| `python` | KNOWLEDGE_RETRIEVAL | Technical patterns |
| `first_aid` | KNOWLEDGE_RETRIEVAL | Medical knowledge |
| `gardening` | KNOWLEDGE_RETRIEVAL | Practical knowledge |
| `diy` | KNOWLEDGE_RETRIEVAL | How-to patterns |
| `binary_symmetry` | KNOWLEDGE_RETRIEVAL | Technical patterns |
| `exframe` | DOCUMENT_STORE_SEARCH | External docs + research |
| `llm_consciousness` | KNOWLEDGE_RETRIEVAL | Could be ANALYTICAL_ENGINE |
| `test_domain` | TEST_ASSISTANT | ✅ Test domain |
| `test_93` | TEST_ASSISTANT | ✅ Test domain |

**Test Domains (Non-Production):**
- `test_domain` - General testing
- `test_93` - Feature testing

**Note:** TEST_ASSISTANT archetype is **intentionally unassigned** from production domains to preserve test space.

---

## Benefits of Archetype System

1. **Consistency** - Domains of same type behave the same way
2. **Simplification** - No custom code needed for most domains
3. **Discoverability** - Users can understand domain capabilities
4. **Maintenance** - Fix once, applies to all domains of archetype
5. **Extensibility** - New archetypes can be added without core changes
6. **Testing** - Test archetype once, all domains inherit tests

---

## Next Steps

### Immediate (this session)
1. ✅ Document the 5 archetypes
2. ⏳ Get user feedback on classification
3. ⏳ Refine archetype definitions

### Short-term (next few days)
1. Create `archetypes.py` module
2. Add archetype selection to domain creation API
3. Update existing domains to declare their archetype
4. Add archetype metadata to domain.json

### Medium-term (next sprint)
1. Frontend archetype selector
2. Per-archetype UI components
3. Archetype-specific testing suite
4. Documentation for each archetype

### Long-term (future)
1. Custom archetype creation (advanced users)
2. Archetype inheritance (extend base archetypes)
3. Archetype marketplace (share custom archetypes)
4. ML-powered archetype recommendation

---

## Open Questions

1. **Should domains be able to switch archetypes?**
   - Migration path needed
   - Data compatibility concerns

2. **Should archetypes be inheritable?**
   - Create "creative_technical" = CREATIVE + technical knowledge
   - Complex but powerful

3. **How to handle domains that don't fit neatly?**
   - Custom archetype option
   - Multiple primary archetypes?

4. **Should archetypes evolve over time?**
   - Versioned archetypes?
   - Migration strategies?

---

## Appendix: Quick Reference

### 1. CREATIVE_GENERATOR
- **Use for**: Poems, stories, creative writing, art
- **LLM Mode**: Direct generation (high temp 0.7-0.9)
- **Patterns**: Ignored/minimal
- **Response**: Clean LLM output only
- **UI**: Regenerate button prominent

### 2. KNOWLEDGE_RETRIEVAL
- **Use for**: Technical docs, FAQs, how-to guides
- **LLM Mode**: Synthesize patterns (medium temp 0.3-0.5)
- **Patterns**: Primary source
- **Response**: LLM + "Patterns referenced"
- **UI**: Pattern cards clickable

### 3. DOCUMENT_STORE_SEARCH
- **Use for**: External docs, live data, research
- **LLM Mode**: Synthesize docs + patterns (medium temp 0.5-0.7)
- **Patterns**: Fallback/secondary
- **Response**: LLM + "Sources searched"
- **UI**: Session history, capture button

### 4. ANALYTICAL_ENGINE
- **Use for**: Research, analysis, correlation
- **LLM Mode**: Multi-step generation (medium temp 0.4-0.6)
- **Patterns**: Context only
- **Response**: Structured report
- **UI**: Progress indicator, download button

### 5. HYBRID_ASSISTANT
- **Use for**: General purpose, flexible
- **LLM Mode**: Fallback on low confidence
- **Patterns**: Primary
- **Response**: Patterns or LLM (user choice)
- **UI**: "Extend search?" button

### 6. TEST_ASSISTANT
- **Use for**: Testing, development, experimentation
- **LLM Mode**: Configurable (direct, with patterns, etc.)
- **Patterns**: Configurable
- **Response**: Configurable (echo, error, delay, etc.)
- **UI**: Test panel, mode selector, interaction log
- **IMPORTANT**: No production domains assigned - pure test space

---

## Workflow State Machine Format

Each archetype defines a workflow as a state machine. States are shown as:

```
STATE_NAME:
  ├─ Input: What comes in
  ├─ Action: What happens
  ├─ Output: What goes out
  └─ Next: Which state follows
```

This makes the query → process → reply flow **explicit** and **configurable**.

---

## Archetype Metadata in Domain Config

Domains declare their archetype in `domain.json`:

```json
{
  "domain_id": "my_domain",
  "archetype": "knowledge_retrieval",
  "archetype_config": {
    "workflow": "standard_pattern_search",
    "custom_settings": {
      "similarity_threshold": 0.25,
      "show_patterns": true,
      "enable_regenerate": false
    }
  }
}
```

The system validates that:
1. The archetype exists
2. The config matches the archetype's requirements
3. Custom settings don't break the archetype's workflow

---

**Status**: Updated with 6 archetypes including TEST_ASSISTANT
**Ready for**: Review, feedback, implementation
