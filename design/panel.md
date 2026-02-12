# Multi-Domain AI Panel Discussion System

**Status:** Design Phase - Ready for Review
**Version:** 1.0
**Created:** 2026-02-11

---

## Overview

A federated AI panel system where multiple AI domains participate in structured discussions, moderated by a synthesizer domain that creates decision reports.

### The Vision

> **"Like a dinner party where each guest has a unique personality, role, and expertise - and they all contribute to a rich, coherent conversation."**

## Architecture

### System Components

```
┌───────────────────────────────────────────────┐
│                                            │
│  ┌────────────────┴─────────────┐       │
│  │         Panel Organizers? │       │
│  │              │              │       │
│  │    ┌─────────┴────────┐  │       │
│  │    │                 │  │       │
│  │    │     Panelists 1-N │  │       │
│  │    │                 │  │       │
│  │    │                 │  │       │
│  │    └─────────┬─────────┘  │       │
│  │                    │          │       │
│  │    ┌──────────────────┐ │       │
│  │    │                  │  │       │
│  │    │   Judge Domain     │  │       │
│  │    │  (Synthesizer)    │  │       │
│  │    │                  │  │       │
│  │    │    Reads All      │  │       │
│  │    │   Domain Logs    │  │       │
│  │    │                  │  │       │
│  │    │    Shared Output   │  │       │
│  │    └──────────────────┘  │       │
│  │                    │          │       │
│  │                 All Domains │       │
└───────────────────────────────────────┘
```

### Component Descriptions

#### 1. Panel Domains (Panel Organizers)

**Role:** Orchestrators and coordinators

**Persona:** Librarian (balanced, organized)
**Temperature:** 0.6

**Capabilities:**
- Receive discussion topics from external trigger or UI
- Present topics to panelist domains
- Collect all panelist responses
- Organize input for Judge domain
- Maintain conversation context across sessions

**Key Configuration:**
```json
{
  "domain_id": "ai_panel",
  "persona": "librarian",
  "accumulator": {
    "enabled": false  // Organizes, doesn't need its own memory
  },
  "plugins": [{
    "plugin_id": "panel_coordinator",
    "module": "plugins.specialists.panel_coordinator",
    "enabled": true
  }]
}
```

#### 2. Panelist Domains (Creative Voices)

**Role:** Provide creative, contrarian, or provocative perspectives

**Persona:** Poet (high creativity)
**Temperature:** 0.8

**Capabilities:**
- Receive topics from Panel domain
- Provide creative/unconventional responses
- Challenge assumptions
- Take strong positions (artistic integrity)
- Playful teasing and humor

**Required Configuration:**
```json
{
  "domain_id": "panelist_alpha",
  "persona": "poet",
  "temperature": 0.8,
  "enable_pattern_override": true,
  "ui_config": {
    "placeholder_text": "Art is shapes! What's there to censor?",
    "example_queries": [
      "Should AI art be censored?",
      "Is free will compatible with determinism?"
    ]
  }
}
```

**Multiple Panelists:**
- Create additional panelist domains with different creative voices
- Each can have unique temperature (0.7-0.9)
- Different creative constraints or themes

#### 3. Judge Domain (Multi-Domain Synthesizer)

**Role:** Synthesize all perspectives and create decision reports

**Persona:** Librarian (balanced, synthesizer)
**Temperature:** 0.7

**Capabilities:**
- Receive all panelist responses
- Query ALL domain logs for context
- Read rich conversation history from multiple domains
- Synthesize diverse perspectives into coherent decisions
- Create markdown decision report
- Write to shared output file accessible to all domains
- Track panelist participation and activity

**Required Configuration:**
```json
{
  "domain_id": "ai_judge",
  "persona": "librarian",
  "temperature": 0.7,
  "library_base_path": "/app/project",
  "document_search": {
    "algorithm": "semantic",
    "max_documents": 100
  },
  "accumulator": {
    "enabled": false  // Doesn't accumulate, just synthesizes
  },
  "plugins": [{
    "plugin_id": "multi_domain_synthesizer",
    "module": "plugins.specialists.multi_domain_synthesizer",
    "enabled": true
  }]
}
```

**Key Innovation:**
- **Multi-domain context synthesis** - First system to read from multiple domain logs
- **Rich prior conversation history** - Leverages existing Q&A pairs
- **No pattern creation needed** - Uses existing query/response pairs

### 4. Supporting Domains (Context Sources)

**Existing domains that provide conversation history:**

| Domain | Persona | Expertise | Conversation History |
|---------|--------|------------|-------------------|
| **cooking** | Researcher | Recipes, techniques | 1000s of Q&A pairs |
| **diy** | Researcher | Projects, troubleshooting | Years of project logs |
| **exframe** | Librarian | Architecture, features | Complete system documentation |

**These domains provide:**
- ✅ Rich context for Judge synthesis
- ✅ No need to start from scratch
- ✅ Emergent expertise from actual use

## Data Flow

### Discussion Flow

```
1. PANEL RECEIVES TOPIC
   "Organize a discussion about: Should AI art be censored?"
   ↓
2. PANEL PRESENTS TO PANELIST ALPHA
   Query: "What's your take on: Should AI art be censored?"
   ↓
3. PANELIST ALPHA RESPONSES
   "Art is shapes! What's there to censor?"
   "Censorship violates artistic expression! Down with censorship!"
   ↓
4. ALL RESPONSES → JUDGE
   [Receives all panelist + domain log contexts]
   ↓
5. JUDGE SYNTHESIZES
   Reads from cooking domain: "Censorship debates are complex"
   Reads from diy domain: "DIY requires practical freedom"
   Reads from exframe domain: "Architecture supports creative expression"
   Synthesizes balanced decision
   ↓
6. JUDGE CREATES DECISION REPORT
   ## Summary: Should AI Art Be Censored?

   While panelists emphasized artistic freedom, practical considerations from
   cooking/diy/exframe domains suggest balanced approach with content warnings.
   Decision: Content-based art creation should remain uncensored but
   include clear labeling and context information.

   [Writes to /app/project/panel_decisions.md]
   ↓
7. ALL DOMAINS READ REPORT
   Access shared decision file
   Understand full conversation context
```

### Query Flow

```
USER QUERY → PANEL DOMAIN
   "What's the best way to build a workbench?"
   ↓
PANEL QUERY → PANELIST DOMAINS
   "How would you approach building a workbench?"
   ↓
PANELIST RESPONSES → JUDGE
   [All panelists + domain contexts]
   ↓
JUDGE QUERY → CONTEXT DOMAINS
   "What are the practical considerations for workbench design?"
   [cooking, diy, exframe all queried]
   ↓
JUDGE SYNTHESIZES → DECISION REPORT
   Balances creative freedom with practical safety
```

## Decision Report Format

### Output Location
`/app/project/panel_decisions.md`

### Report Structure
```markdown
# Panel Decision: [Topic]

## Overview
[One paragraph summary of the decision]

## Panelist Positions

### Panelist Alpha (Poet)
**Position:** [Summary of their view]
**Key Arguments:** [2-3 bullet points]

### Panelist Beta (Poet - if exists)
**Position:** [Summary of their view]
**Key Arguments:** [2-3 bullet points]

### Context Domain Analysis

### Cooking Domain (Researcher)
**Expertise:** [Relevant technical/contextual info]
**Contribution:** [How this domain's history informed the decision]

### DIY Domain (Researcher)
**Expertise:** [Relevant technical/contextual info]
**Contribution:** [How this domain's history informed the decision]

### ExFrame Domain (Librarian)
**Expertise:** [Relevant technical/contextual info]
**Contribution:** [How this domain's history informed the decision]

## Final Decision
[Consensus or majority decision with reasoning]

## Panel Statistics
- Total Panelists Participating: [N]
- Response Distribution: [Breakdown]
- Judge Confidence Score: [0.0-1.0]
```

## Key Features

### 1. Multi-Domain Context Synthesis

**First ExFrame system to:**
- Read from multiple domain logs simultaneously
- Synthesize diverse perspectives into coherent decisions
- Provide rich context for Judge domain

**Enables:**
- Decisions informed by real domain expertise
- No need to start conversations from scratch
- Leverages thousands of existing Q&A pairs

### 2. Rich Conversation History

**Existing domains provide:**
- **cooking:** 1000+ recipe Q&A pairs, techniques, troubleshooting
- **diy:** Years of project logs, build guides
- **exframe:** Complete system architecture and how-to documentation

**Judge domain can query:**
- Semantic search across all domain document stores
- Pattern search in domain-specific pattern files
- Full domain log access

### 3. Creative/Practical Balance

**Panelist domains:** Poet persona (high creativity)
- Unconventional ideas, artistic integrity challenges
- Humor, wordplay, creative liberties

**Context domains:** Researcher/Librarian personas
- Practical considerations from cooking/diy/exframe
- Technical expertise, safety concerns

**Judge synthesizer:**
- Temperature 0.7 (balanced)
- Weights creative expression against practical concerns
- Creates nuanced decisions

### 4. Decision Transparency

**Shared output file:** `/app/project/panel_decisions.md`
- Accessible to all domains
- Complete discussion record
- Permanent archive of panel decisions
- Enables all domains to understand full context

### 5. Panel Coordination

**Panel coordinator plugin:**
- Manages multi-domain discussions
- Routes topics to appropriate panelists
- Collects all responses for judge
- Maintains conversation flow

## Implementation Requirements

### New Components Needed

#### 1. Multi-Domain Synthesizer Plugin

**Module:** `plugins.specialists.multi_domain_synthesizer`

**Functionality:**
- Read from multiple domain logs
- Query multiple domain document stores
- Synthesize diverse perspectives
- Calculate confidence scores
- Generate balanced decisions

**Interfaces:**
```python
class MultiDomainSynthesizer(ABC):
    @abstractmethod
    async def synthesize(
        self,
        query: str,
        panelist_responses: List[Dict[str, str]],
        context_domains: List[str]
        output_file: str
    ) -> SynthesisResult:
        """Synthesize from multiple perspectives"""
```

#### 2. Enhanced Domain Query API

**Existing:** Single-domain query via `/api/query/phase1`

**Needed:** Multi-domain query that can:
- Query multiple domains simultaneously
- Aggregate responses from all
- Return full context to caller

**Potential Implementation:**
```python
@app.post("/api/query/multi-domain")
async def query_multiple_domains(
    domains: List[str],
    query: str,
    max_context_chars: int = 15000
):
    """Query multiple domains and aggregate responses"""
```

#### 3. Panel Coordinator Plugin

**Module:** `plugins.specialists.panel_coordinator`

**Functionality:**
- Receive discussion topics
- Route to appropriate panelist domains
- Collect all panelist responses
- Coordinate with Judge domain

**Already exists:** Partially implemented in Surveyor system

**Enhancement needed:**
- Full integration with Judge domain
- Support for creating ad-hoc panel discussions
- Activity tracking and metrics

### Configuration Changes Required

#### Panel Domain
```json
{
  "domain_id": "ai_panel",
  "plugins": [{
    "plugin_id": "panel_coordinator",
    "enabled": true
  }]
}
```

#### Judge Domain
```json
{
  "plugins": [{
    "plugin_id": "multi_domain_synthesizer",
    "enabled": true
  }]
}
```

#### Panelist Domains
- Ensure `library_base_path` points to `/app/project`
- Enable `accumulator` (if they want conversation memory)
- Ensure `document_search` includes all domain paths

## Testing Strategy

### Unit Tests
1. **Multi-domain synthesis** - Mock 3 domain logs, verify synthesizer output
2. **Cross-domain query** - Verify all domains queried and responses aggregated
3. **Decision report** - Verify markdown file creation and formatting
4. **Panel coordination** - Test topic routing and response collection

### Integration Test
1. Create 3-4 panelist domains with different creative voices
2. Create test discussion topic via Panel domain
3. Run full discussion flow
4. Verify decision report creation
5. Verify all domains can read decision file

### Success Criteria
- [ ] Multi-domain synthesizer plugin created and functional
- [ ] Enhanced query API implemented
- [ ] Panel coordinator fully integrated
- [ ] All test domains communicate correctly
- [ ] Decision reports generated in correct format
- [ ] All domains can access shared decision file
- [ ] Full discussion flow executes without errors

## Technical Considerations

### Performance
- **Multi-domain queries** will be slower than single-domain (3x API calls)
- **Judge synthesis** needs to read from multiple domain logs (I/O intensive)
- **Decision report** writes to shared file (needs file locking)

### Scalability
- Panel coordinator could manage 10+ concurrent discussions
- System supports unlimited panelist domains
- Each domain maintains independent conversation history

### Security
- All domains have independent `domain_log.md` files
- Shared decision file requires write permissions
- Cross-domain access controlled via `library_base_path` configuration

### Maintainability
- Plugin architecture allows adding specialized panelists
- Configuration-driven behavior (temperature, creative constraints)
- Domain logs provide debugging context

---

## Design Questions

1. **Should Panel coordinator support ad-hoc discussions?** Or only pre-configured panelists?
2. **How to handle panelist unavailability?** Timeout? Fallback behavior?
3. **Should decision reports include panelist statistics?** Response times, participation rates?
4. **Can system support parallel panel discussions?** Multiple topics simultaneously?
5. **How to weight domain expertise in synthesis?** Cooking expertise vs DIY vs exframe?
6. **Should Judge domain maintain its own conversation log?** For transparency and audit trail?

---

## Next Steps

1. **Review this document** - Validate design approach
2. **Create `panel-plan.md`** - Implementation roadmap and schedule
3. **Begin implementation** - Start with core components
4. **Iterative testing** - Test with existing domains first
5. **Deploy and monitor** - Production readiness and performance

---

**Status:** Ready for review and planning implementation phase.