# EEFrame Project Context

**Date**: 2026-01-12
**Working Directory**: `/home/peter/development/eeframe`

---

## Current Focus: Autonomous Learning System

### Primary Goal

Build a **robust autonomous learning and certification system** for EEFrame that can:
1. Scrape web sources autonomously
2. Extract knowledge patterns
3. Certify patterns through **5-judge AI panel**
4. Store validated expertise
5. **Include hooks for future Research Generator**

### Strategy: Single Domain First

**Start with ONE domain** (e.g., Cooking or Python) to perfect the system before expanding.

**Why single domain?**
- Faster iteration and validation
- Easier to measure expertise quality
- Simplifies debugging and risk assessment
- Proves the concept before scaling

---

## EEFrame Hierarchy (Spatial Confirmation)

```
MULTIVERSE
    │
    │   Collection of isolated Universes
    │
    └── UNIVERSE
        │
        │   Complete, self-contained knowledge environment
        │   (e.g., "production", "testing", "research", "customer_A")
        │
        └── NEIGHBOURHOOD (NEW)
            │
            │   Logical grouping of related Domains
            │   (e.g., "culinary_arts", "technical_skills", "diy_home")
            │
            └── DOMAIN
                │
                │   Area of expertise
                │   (e.g., "cooking", "python", "gardening", "woodworking")
                │
                └── PATTERNS
                    │
                    │   Knowledge units
                    │   (individual recipes, code patterns, techniques)
```

### Level Definitions

| Level | Purpose | Examples | Contains |
|-------|---------|----------|----------|
| **Multiverse** | All Universes in system | Default installation | Multiple Universes |
| **Universe** | Complete knowledge environment | `production`, `testing`, `research` | Neighbourhoods |
| **Neighbourhood** | **Dynamic filter across domains** | User-defined: "baking under 30 min" | Filtered patterns from multiple domains |
| **Domain** | Area of expertise | `cooking`, `python`, `gardening` | Patterns |
| **Patterns** | Knowledge units | `recipe_001`, `list_comprehension` | Knowledge |

### Neighbourhood: User-Defined Filter (CRITICAL CONCEPT)

**Definition**: A **Neighbourhood** is a dynamic, user-defined filter that spans multiple domains to find patterns matching specific criteria.

**NOT** a static grouping of domains. Instead:
- The Surveyor defines a filter/criteria (e.g., "baking recipes under 30 minutes")
- The system searches across ALL domains in the universe
- Patterns matching the criteria are included in the survey
- Enables cross-cutting surveys without rigid domain boundaries

**Examples**:
| Neighbourhood Definition | Matches From |
|------------------------|--------------|
| "baking recipes under 30 minutes" | cooking, baking, dessert domains |
| "machine learning model evaluation" | python, data_science, ML domains |
| "authentication security best practices" | webdev, security, backend domains |

**Why this approach?**
- Flexible: Define surveys by *what you want*, not *where it lives*
- Cross-domain: Finds related patterns across domain boundaries
- Adaptive: As new domains are added, neighbourhoods automatically include matching content

**Domain vs Neighbourhood**:
- **Domain Survey**: "I want everything from the cooking domain"
- **Neighbourhood Survey**: "I want all quick recipes across ALL cooking-related domains"

### Example Hierarchy

```
Multiverse: EEFrame Installation
│
└── Universe: production
    │
    ├── Neighbourhood: culinary_arts
    │   ├── Domain: cooking
    │   │   └── Patterns: 150 recipes
    │   ├── Domain: baking
    │   │   └── Patterns: 80 techniques
    │   └── Domain: grilling
    │       └── Patterns: 45 methods
    │
    ├── Neighbourhood: technical_skills
    │   ├── Domain: python
    │   │   └── Patterns: 200 code patterns
    │   ├── Domain: javascript
    │   │   └── Patterns: 180 code patterns
    │   └── Domain: bash
    │       └── Patterns: 60 scripts
    │
    └── Neighbourhood: home_maintenance
        ├── Domain: woodworking
        │   └── Patterns: 90 techniques
        ├── Domain: gardening
        │   └── Patterns: 70 tips
        └── Domain: diy
            └── Patterns: 120 projects
```

### Surveyor Scope

Surveyor can operate at different hierarchy levels:

| Survey Level | Target | Example |
|--------------|--------|---------|
| **Domain Survey** | Single domain | "Learn cooking recipes" |
| **Neighbourhood Survey** | Multiple related domains | "Learn culinary_arts (cooking + baking + grilling)" |
| **Universe Survey** | Entire universe | "Learn all production knowledge" |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      HUMAN INTERFACE LAYER                          │
│              (Surveyor UI + Strategic Direction + LAST RESORT)      │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SURVEYOR UI (Replace Ingestions Tab)            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ Survey List     │  │ Survey Detail   │  │ Real-time       │   │
│  │ - Name/Desc     │  │ - Requirements  │  │ Metrics         │   │
│  │ - Status        │  │ - Timeline      │  │ - Pulse         │   │
│  │ - Domains/Patts │  │ - Controls      │  │ - Progress      │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
╔═════════════════════════════════════════════════════════════════════════╗
║                    PHASE 10: AGENT WRAPPER (Future Enhancement)       ║
║  "Keep the working LLM sane during boring repetitive tasks"         ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  ║
║  │ Pulse       │  │ Context     │  │ Guardrails  │                  ║
║  │ Monitor     │  │ Cleanup     │  │             │                  ║
║  └─────────────┘  └─────────────┘  └─────────────┘                  ║
╚═════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼ (v1: Direct connection)
┌─────────────────────────────────────────────────────────────────────┐
│                        AI SUPERVISOR                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │ Heartbeat   │  │ Focus       │  │ Refocus     │  │ Watchdog  │ │
│  │ Monitor     │  │ Drift Detect│  │ Strategies  │  │ Recovery  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
    │   SCRAPING        │   │  5-JUDGE PANEL    │   │  PATTERN          │
    │   ENGINE          │   │  CERTIFICATION    │   │  INGESTION        │
    │                   │   │                   │   │                   │
    │  • Stealth        │   │  1. Generalist    │   │  • Validation     │
    │  • Rate Limit     │   │  2. Specialist    │   │  • Deduplication  │
    │  • Error Recovery │   │  3. Skeptic       │   │  • De-dup         │
    │  • Proxy Rotation │   │  4. Contextualist │   │  • Storage        │
    │                   │   │  5. Human (Last)  │   │                   │
    └───────────────────┘   └───────────────────┘   └───────────────────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      ▼
                        ┌─────────────────────────────────┐
                        │     EEFrame Knowledge Base      │
                        │     (Certified Patterns)         │
                        └─────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
          ┌─────────────────────┐         ┌─────────────────────┐
          │   Expertise Scanner │         │   Generic Framework │
          │   (Pattern Storage) │         │   (Query Response)  │
          └─────────────────────┘         └─────────────────────┘

                    ╔═════════════════════════════════╗
                    ║     FUTURE: Research Generator  ║
                    ║     (Hooks in place)            ║
                    ╚═════════════════════════════════╝
```

---

## 5-Judge Certification Panel (CRITICAL COMPONENT)

### The Judges

| Judge | Role | Model | Temp | Purpose |
|-------|------|-------|------|---------|
| **1. Generalist** | Pattern structure review | GPT-4 / GLM-4 | 0.3 | Validates format, completeness |
| **2. Specialist** | Domain accuracy | Claude 3.5 Sonnet | 0.2 | Technical correctness |
| **3. Skeptic** | Find flaws | Claude 3 Opus | 0.5 | Critical analysis |
| **4. Contextualist** | Contextual fit | GLM-4 | 0.4 | Fits domain/applicability |
| **5. Human** | **LAST RESORT** | Human review | N/A | Break ties, critical flags |

### Certification Flow

```
Candidate Pattern
        │
        ▼
┌─────────────────────────────────────────┐
│  AI Judges 1-4 Review (Parallel)        │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐           │
│  │ J1 │ │ J2 │ │ J3 │ │ J4 │           │
│  └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘           │
└────┼─────┼─────┼─────┼──────────────────┘
     │     │     │     │
     └─────┴─────┴─────┴────┐
                           ▼
                 ┌──────────────────┐
                 │ Consensus Engine │
                 └────────┬─────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   Strong Consensus   Weak Consensus    Conflict
   (>0.8, unanimous)  (0.6-0.8)         (<0.6 or veto)
        │                 │                 │
        ▼                 ▼                 ▼
   CERTIFIED        PROVISIONAL     ╔─────────────╗
   (Auto)           (Auto)          ║ HUMAN JUDGE ║
                                     ║  (Judge 5)  ║
                                     ╚─────────────┘
```

### Decision Matrix

| Consensus | Unanimous | Skeptic Veto | Result | Human Review |
|-----------|-----------|--------------|--------|--------------|
| ≥0.8 | Yes | No | **CERTIFIED** | No |
| ≥0.8 | Yes | Yes | **FLAGGED** | **Yes (required)** |
| 0.6-0.79 | Any | No critical | **PROVISIONAL** | No |
| 0.6-0.79 | Any | Critical issues | **FLAGGED** | **Yes (required)** |
| <0.6 | Any | Any | **REJECTED** | Log only |
| Conflict | Any | Any | **ESCALATE** | **Yes (required)** |

---

## Agent Wrapper (The "Claude Code" Pattern) - PHASE 10 ENHANCEMENT

> **Status**: Deferred to Phase 10. v1 will use "black box" approach with status monitoring only.

### Problem: Boring Repetitive Work Breaks LLMs

**The Issue**: When LLMs perform autonomous scraping/certification tasks:
- Context fills with failures and repetitive operations
- LLM loses focus and starts "wandering" in chat mode
- Failures accumulate, pushing out important context
- LLM gives up or enters loops

**The Solution**: An Agent Wrapper that:
1. Monitors agent health (pulse)
2. Cleans context of failures/junk
3. Enforces guardrails to prevent wandering
4. Locks focus to prevent task drift
5. Detects and breaks loop/give-up patterns

### Agent Wrapper Architecture

```python
# autonomous_learning/agent_wrapper/wrapper.py

class AgentWrapper:
    """
    Claude Code-style wrapper for autonomous LLM agents.
    Keeps the working LLM sane during boring repetitive tasks.
    """

    def __init__(self, config: AgentWrapperConfig):
        self.pulse_monitor = PulseMonitor()
        self.context_manager = ContextCleaner()
        self.guardrails = Guardrails()
        self.focus_lock = FocusLock()
        self.sanity_checker = SanityChecker()

    async def wrap_agent(self, agent: WorkingAgent, task: Task) -> TaskResult:
        """Execute agent task with monitoring and guardrails"""

        # Start pulse monitoring
        pulse = self.pulse_monitor.start(agent.id)

        while not task.complete:
            # 1. Pulse check - is agent alive and responsive?
            if not await pulse.check():
                return await self._handle_unresponsive(agent, task)

            # 2. Context cleanup - prune failures, keep useful context
            await self.context_manager.cleanup(agent.context)

            # 3. Guardrails - prevent wandering outside task scope
            if not await self.guardrails.check(agent.state):
                await self._refocus_agent(agent, task)

            # 4. Focus lock - ensure agent stays on primary objective
            focus_score = await self.focus_lock.verify(agent, task)
            if focus_score < 0.7:
                await self._reinforce_focus(agent, task)

            # 5. Sanity check - detect loops, give-ups, hallucinations
            sanity = await self.sanity_checker.analyze(agent.recent_actions)
            if sanity.status == "looping":
                await self._break_loop(agent, task)
            elif sanity.status == "giving_up":
                await self._intervene_giveup(agent, task)
            elif sanity.status == "hallucinating":
                await self._reset_agent(agent, task)

            # Let agent continue
            await agent.step()

        return task.result
```

### Wrapper Components

#### Pulse Monitor
```python
class PulseMonitor:
    """Health check for autonomous agents"""

    async def check(self, agent_id: str) -> bool:
        """Is the agent responsive?"""
        # Check: last action within timeout
        # Check: agent not stuck in same state
        # Check: agent making progress (even if slow)
        return is_alive
```

#### Context Cleaner
```python
class ContextCleaner:
    """Prune failures and junk from agent context"""

    async def cleanup(self, context: AgentContext):
        """Keep context lean and focused"""
        # Remove: failed attempts (keep summary only)
        # Remove: redundant operations
        # Keep: successful patterns
        # Keep: current task and progress
        # Keep: important errors (summarized)
        return cleaned_context
```

#### Guardrails
```python
class Guardrails:
    """Prevent agent from wandering off-task"""

    async def check(self, agent_state: AgentState) -> bool:
        """Is agent staying within task bounds?"""
        # Check: agent not discussing unrelated topics
        # Check: agent not generating irrelevant content
        # Check: agent following established procedures
        return is_within_bounds
```

#### Focus Lock
```python
class FocusLock:
    """Ensure agent stays on primary objective"""

    async def verify(self, agent: WorkingAgent, task: Task) -> float:
        """Return focus score (0.0-1.0)"""
        # Return: how focused is the agent?
        return focus_score
```

#### Sanity Checker
```python
class SanityChecker:
    """Detect unhealthy patterns in agent behavior"""

    async def analyze(self, actions: List[AgentAction]) -> SanityReport:
        """Check for loops, give-ups, hallucinations"""
        # Loop detection: same action repeated > N times
        # Give-up detection: "I can't", refusal patterns
        # Hallucination detection: fact-check against known patterns
        return SanityReport(status="healthy"|"looping"|"giving_up"|"hallucinating")
```

### Integration Point

The Agent Wrapper sits **between the Surveyor UI and the AI Supervisor**:

```
Surveyor UI → Agent Wrapper → AI Supervisor → Workers (Scraping/Certification)
                ↓
           Keeps workers sane
```

**Decision**: Proceeding WITHOUT Agent Wrapper safeties for initial implementation.
- Surveyor will be a "black box" with status monitoring
- Pulse, progress, and metrics will be exposed
- No context cleanup, guardrails, focus lock, or sanity checking (v1)
- Agent Wrapper can be added as Phase 10 enhancement if needed

---

## Surveyor UI (Replace Ingestions Tab in Generic Framework)

### Purpose

Replace the **Ingestion tab** in `generic_framework/frontend/index.html` with a proper **Surveyor interface** for managing autonomous learning sessions ("surveys").

### What is a "Survey"?

A **Survey** = An autonomous learning session focused on a hierarchy level:
- **Domain Survey**: Single domain learning
- **Neighbourhood Survey**: Multiple related domains
- **Universe Survey**: Entire universe learning

Survey operations:
- Scrapes specified sources
- Extracts patterns
- Certifies through 5-judge panel
- Stores validated expertise
- Runs autonomously with monitoring

### Surveyor UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  EEFrame - Generic Framework                │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                       │
│ Query    │  SURVEYOR - Autonomous Learning Manager              │
│ Patterns │  ┌────────────────────────────────────────────────┐  │
│ Sources  │  │  ┌─────────┐ ┌─────────────────┐ ┌──────────┐ │  │
│ Domains  │  │  │ Survey  │ │  Survey Detail  │ │ Metrics  │ │  │
│ Surveyor │  │  │  List   │ │                 │ │          │ │  │
│          │  │  │ ┌─────┐ │ │ ┌─────────────┐ │ │ ┌──────┐ │ │  │
│          │  │  │ │Culin-│ │ │Culinary Arts  │ │ │Pulse │ │ │  │
│          │  │  │ │ary   │ │ │Survey         │ │ │●●●●●│ │ │  │
│          │  │  │ │Arts  │ │ │               │ │ │      │ │ │  │
│          │  │  │ │Survey│ │ │Desc: Auto-    │ │ │Progr │ │ │  │
│          │  │  │ ├─────┤ │ │matic recipe    │ │ │▓▓▓▓░│ │ │  │
│          │  │  │ │Python│ │ │ │extraction   │ │ │  85% │ │ │  │
│          │  │  │ │Survey│ │ │ │from 3       │ │ │      │ │ │  │
│          │  │  │ └─────┘ │ │ │domains...    │ │ │      │ │ │  │
│          │  │  └─────────┘ │ └─────────────┘ │ └──────┘ │ │  │
│          │  │              │ ┌─────────────┐ │          │ │  │
│          │  │              │ │Survey Prompt │ │          │ │  │
│          │  │              │ │ & Controls   │ │          │ │  │
│          │  │              │ └─────────────┘ │          │ │  │
│          │  │              │ ┌─────────────┐ │          │ │  │
│          │  │              │ │ Activity Log │ │          │ │  │
│          │  │              │ └─────────────┘ │          │ │  │
│          │  │              └─────────────────┘          │ │  │
│          │  └────────────────────────────────────────────┘  │
│          │                                                       │
└──────────┴──────────────────────────────────────────────────────┘
```

### Surveyor UI Components

#### 1. Survey List Panel

```
┌─────────────────────┐
│  SURVEYS            │
├─────────────────────┤
│ ▶ Quick Baking      │ ← Status (▶ running, ⏸ paused, ■ stopped, ○ idle)
│   🔍 Baking under   │    Level badge: 📁 Domain, 🔍 Neighbourhood, 🌌 Universe
│   30 minutes        │    Shows neighbourhood definition or domain name
│   Status: Running   │
│   P: 38/47  ⚠️3     │ ← Certified/Total, Flagged count
├─────────────────────┤
│ ○ Python Data Sci  │
│   🔍 Python ML and  │
│   data science...   │
│   Status: Idle      │
│   P: 0/0            │
├─────────────────────┤
│ ■ Cooking Domain    │
│   📁 cooking        │
│   Status: Paused    │
│   P: 118/134 ⚠️8   │
├─────────────────────┤
│ [+ New Survey]      │
└─────────────────────┘
```

#### 2. Survey Detail Panel

```
┌─────────────────────────────────────┐
│  Quick Baking Recipes               │
├─────────────────────────────────────┤
│ Description:                        │
│ Survey baking recipes that take     │
│ under 30 minutes from multiple      │
│ sources.                            │
│                                     │
│ Scope:                              │
│ 🔍 Neighbourhood                     │
│ "baking recipes under 30 minutes"   │
│                                     │
│ Progress:                           │
│ ████████████████░░░░░░░  34%        │
│                                     │
│ Requirements:                       │
│ • Target Patterns: 100              │
│ • Min Confidence: 0.8               │
│ • Universe: default                 │
│                                     │
│ Scraping Config:                    │
│ • Seed: allrecipes.com/cookies      │
│ • Sources: 2 additional URLs       │
│ • Focus: temperature, ratios...    │
│                                     │
│ Controls:                           │
│ [ ▶ START ] [ ⏸ PAUSE ] [ ■ STOP ] │
│ [ ✏️ EDIT ]                          │
│                                     │
│ Certification:                      │
│ ✅ 38 Certified  ⚠️3 Flagged        │
│ ❌ 2 Rejected  ⏳ 4 Pending         │
│                                     │
│ Activity Log:                       │
│ 22:19  Survey loaded                │
│ 10:30  Started scraping...          │
│ 10:32  Certified: Choc Chip Cookies │
│ 10:33  Flagged: Cake Temp Guide     │
└─────────────────────────────────────┘
```

#### 3. Scraping Control Panel (New Survey/Edit)

```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Scraping Control Panel                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔗 Seed URL                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ https://www.allrecipes.com/recipes/17215/cookies   │   │
│  └─────────────────────────────────────────────────────┘   │
│  The starting point. Scraper begins here and follows      │
│  relevant links.                                          │
│                                                             │
│  📎 Additional URLs (optional, one per line)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ https://www.foodnetwork.com/recipes/cookies         │   │
│  │ https://www.tasty.co/recipe/baking-101              │   │
│  └─────────────────────────────────────────────────────┘   │
│  Extra sources to include.                                 │
│                                                             │
│  🤖 Collection Instructions                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Focus on cookie baking techniques. Look for:        │   │
│  │ - Temperature settings and their effects            │   │
│  │ - Ingredient ratios and substitutions              │   │
│  │ - Baking times and pan types                        │   │
│  │ - Common mistakes and troubleshooting              │   │
│  └─────────────────────────────────────────────────────┘   │
│  Be specific about what patterns to extract. This guides  │
│  the AI on what to look for and how to traverse links.    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 4. Real-time Metrics Panel

```
┌─────────────────────┐
│  LIVE METRICS       │
├─────────────────────┤
│ Pulse: ●●●●●        │ ← Agent health
│                     │
│ Progress:           │
│ ▓▓▓▓▓▓▓▓▓▓░░ 85%   │
│                     │
│ Throughput:         │
│ 3.2 patterns/hr    │
│                     │
│ Certification:      │
│ ✅ 47 Certified     │
│ ⚠️  3 Flagged       │
│ ❌ 2 Rejected       │
│ ⏳ 5 Pending        │
│                     │
│ Judge Activity:     │
│ J1: ████████░░ 80%  │
│ J2: ████████░░ 82%  │
│ J3: ████████░░ 78%  │
│ J4: ████████░░ 85%  │
│ J5: ████░░░░░░ 20%  │ ← Human (low activity = good)
│                     │
│ Errors: 2 (handled) │
│ Focus: 94% (locked) │
└─────────────────────┘
```

### Surveyor API Endpoints

```typescript
// Base path: /api/learning (mounted to Generic Framework)
// Autonomous Learning API is mounted as a sub-app at /api/learning

// Survey management
GET    /api/learning/api/surveys                      // List all surveys
POST   /api/learning/api/surveys                      // Create new survey
GET    /api/learning/api/surveys/:id                  // Get survey details
PUT    /api/learning/api/surveys/:id                  // Update survey (edit)
DELETE /api/learning/api/surveys/:id                  // Delete survey

// Survey control
POST   /api/learning/api/surveys/:id/start            // Start survey
POST   /api/learning/api/surveys/:id/stop             // Stop survey
POST   /api/learning/api/surveys/:id/pause            // Pause survey
POST   /api/learning/api/surveys/:id/resume           // Resume survey

// Supervisor control
GET    /api/learning/api/supervisor/workers           // List workers
GET    /api/learning/api/supervisor/heartbeat         // Worker heartbeat
POST   /api/learning/api/supervisor/refocus/:worker   // Trigger refocus

// Certification control
GET    /api/learning/api/certification/judges         // List judge status
GET    /api/learning/api/certification/queue           // Get certification queue
POST   /api/learning/api/certification/submit          // Submit pattern for certification
GET    /api/learning/api/certification/status/:id      // Get certification status

// Scraping control
GET    /api/learning/api/scraping/status              // Get scraping status
POST   /api/learning/api/scraping/start               // Start scraping
POST   /api/learning/api/scraping/stop                // Stop scraping
POST   /api/learning/api/scraping/targets             // Add scraping targets
GET    /api/learning/api/scraping/targets             // List scraping targets
GET    /api/learning/api/scraping/results             // Get scraping results

// Real-time metrics (WebSocket or SSE)
WS     /api/learning/api/surveys/:id/metrics          // Live metrics stream

// Survey results
GET    /api/learning/api/surveys/:id/patterns         // Get patterns from survey
GET    /api/learning/api/surveys/:id/report           // Get survey report
```

### API Integration

The Autonomous Learning API is **mounted as a FastAPI sub-application** to the Generic Framework:

```python
# generic_framework/api/app.py

from autonomous_learning.api.app import app as learning_app

# Mount at /api/learning path
app.mount("/api/learning", learning_app)
```

**Frontend calls**:
```javascript
// Create survey
POST /api/learning/api/surveys
{
  "name": "Quick Baking Recipes",
  "level": "neighbourhood",
  "neighbourhood": "baking under 30 minutes",
  "seed_url": "https://allrecipes.com/cookies",
  "additional_urls": ["https://foodnetwork.com/cookies"],
  "scraping_prompt": "Focus on temperature, ratios...",
  "target_patterns": 100,
  "min_confidence": 0.8
}

// Update survey (edit)
PUT /api/learning/api/surveys/survey_001
{ "name": "Updated Name", "scraping_prompt": "New instructions" }
```

### Survey Data Model

```python
@dataclass
class Survey:
    id: str
    name: str
    description: str

    # Hierarchy Level
    level: SurveyLevel            # "domain", "neighbourhood", "universe"
    universe: str                 # Universe name
    neighbourhood: Optional[str]  # User-defined filter (if level is neighbourhood)
    domain: Optional[str]         # Domain name (if level is domain)

    # Requirements
    target_patterns: int
    min_confidence: float

    # Scraping Control (NEW)
    seed_url: Optional[str] = None         # Starting point for scraping
    additional_urls: Optional[List[str]] = None  # Extra sources to include
    scraping_prompt: Optional[str] = None   # Instructions for AI on what to collect

    # Legacy (for backward compatibility)
    sources: Optional[List[str]] = None    # URLs or source names (deprecated, use seed_url + additional_urls)
    timeline_hours: Optional[int] = None
    rate_limit: int = 1            # requests per second
    max_retries: int = 3
    enable_stealth: bool = True

    # Status
    status: SurveyStatus           # "idle", "running", "paused", "completed", "failed"
    progress: float                # 0.0 to 1.0

    # Results
    domains_created: int = 0
    patterns_created: int = 0
    patterns_certified: int = 0
    patterns_flagged: int = 0
    patterns_rejected: int = 0
    patterns_pending: int = 0

    # Metadata
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class SurveyLevel(str, Enum):
    DOMAIN = "domain"           # Single domain
    NEIGHBOURHOOD = "neighbourhood"  # Multiple related domains
    UNIVERSE = "universe"       # Entire universe

class SurveyStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

### Implementation Notes

**Frontend**: Plain HTML/JS + Alpine.js (matching Generic Framework)
**Styling**: Tailwind CSS v3 (via CDN, matching Generic Framework)
**Real-time**: Server-Sent Events (SSE) or polling for live metrics
**Charts**: Optional - plain CSS bars or minimal canvas drawing

**Location**: `generic_framework/frontend/index.html`
- Replace "Ingestion" tab with "Surveyor" tab
- Full-page Surveyor view matching Generic Framework style
- No React build step required

**Key Sections**:
- Survey list (left sidebar)
- Survey detail (center panel)
- Real-time metrics (right panel)
- Activity log (bottom panel)
- Control panel (survey prompt construction, activation, duration)

---

## Risk Management (CRITICAL)

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **LLM Hallucination** | Medium | High | 5-judge consensus, skeptic veto, human tiebreaker |
| **Low Quality Patterns** | Medium | High | Validation thresholds, provisional certification |
| **Scraping Detection** | Low | Medium | Stealth techniques, rate limiting, proxy rotation |
| **API Rate Limits** | Medium | Low | Exponential backoff, multiple API providers |
| **Judge Unavailability** | Low | Medium | Graceful degradation (3-judge minimum), human escalation |
| **System Crash** | Low | High | State persistence, watchdog restart, recovery logs |

### Human Intervention Triggers

**Humans are the LAST RESORT, but MUST intervene when:**

1. **Skeptic Judge finds critical issues** → Human review required
2. **Consensus < 0.6** → Human arbitration
3. **Judge disagreement > 30% variance** → Add 4th AI judge, then human if still conflicted
4. **Pattern rejected 3x** → Human review of source and extraction
5. **System failure** → Human root cause analysis
6. **User flag** → Human review of specific pattern

### Quality Assurance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Certification Accuracy** | >90% | Human spot-check of certified patterns |
| **False Positive Rate** | <5% | Human review of rejected patterns |
| **Pattern Utility** | >80% | User feedback on query responses |
| **Expertise Solidity** | TBD | Domain expert validation (pilot) |

---

## Probability of Solid Expertise

### Confidence Scoring

Each pattern receives a **confidence score** (0.0-1.0) based on:

```python
confidence = (
    judge_average * 0.4 +          # Average of all 5 judges
    unanimity_bonus * 0.2 +        # Bonus for unanimous agreement
    source_quality * 0.2 +         # Quality of data source
    validation_score * 0.1 +       # Schema validation
    cross_reference_score * 0.1    # Matches other patterns
)
```

### Expertise Solidity Estimate

Based on 5-judge panel with human tiebreaker:

| Confidence Range | Expected Quality | Action |
|-----------------|------------------|--------|
| 0.9-1.0 | **Excellent** | Deploy immediately |
| 0.8-0.89 | **Good** | Deploy, monitor for feedback |
| 0.6-0.79 | **Acceptable** | Provisional, review after use |
| <0.6 | **Poor** | Reject or require human rewrite |

**Expected distribution** (conservative estimate):
- 60% will score 0.8+ (Good to Excellent)
- 25% will score 0.6-0.79 (Acceptable, provisional)
- 15% will score <0.6 (Rejected or flagged)

**Human review rate target**: <5% of all candidates

---

## Project Structure

```
autonomous_learning/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py              # YAML configuration
│   ├── state.py               # State persistence
│   └── logger.py              # Structured logging
├── supervisor/
│   ├── __init__.py
│   ├── supervisor.py          # Main supervisor
│   ├── heartbeat.py           # Worker health monitoring
│   ├── focus.py               # Drift detection (text-based)
│   └── refocus.py             # Refocus strategies
├── certification/
│   ├── __init__.py
│   ├── panel.py               # 5-judge panel orchestrator
│   ├── judges/
│   │   ├── __init__.py
│   │   ├── base.py            # Base judge interface
│   │   ├── generalist.py      # Judge 1: Structure
│   │   ├── specialist.py      # Judge 2: Domain accuracy
│   │   ├── skeptic.py         # Judge 3: Critical analysis
│   │   ├── contextualist.py   # Judge 4: Context fit
│   │   └── human.py           # Judge 5: Human last resort
│   └── consensus.py           # Consensus calculation
├── scraping/
│   ├── __init__.py
│   ├── engine.py              # Scraping orchestrator
│   ├── stealth.py             # UA rotation, rate limiting
│   ├── errors.py              # Error handling strategies
│   └── extractors/
│       ├── __init__.py
│       ├── base.py
│       ├── html.py
│       └── {domain}_py        # Domain-specific extractors
├── ingestion/
│   ├── __init__.py
│   ├── pipeline.py            # Main ingestion pipeline
│   ├── validation.py          # Schema validation (Pydantic)
│   ├── deduplication.py       # Similarity check (text-based)
│   └── storage.py             # Integration with Expertise Scanner
├── api/
│   ├── __init__.py
│   ├── supervisor.py          # Supervisor control endpoints
│   ├── certification.py       # Certification endpoints
│   └── scraping.py            # Scraping control endpoints
└── research_hooks/            # ═══ FUTURE: Research Generator ═══
    ├── __init__.py
    ├── README.md              # "Future: Research Generator"
    └── interfaces.py          # Placeholder interfaces
```

---

## Implementation Phases (Revised)

### Phase 1: Foundation & Core Infrastructure (2-3 days)
- Project structure
- Configuration (YAML)
- State persistence
- Structured logging

### Phase 2: AI Supervisor (3-4 days)
- Supervisor core
- Heartbeat monitoring
- Focus drift detection (text-based)
- Refocus strategies
- Generic LLM client (GLM-4 compatible)

### Phase 3: 5-Judge Certification Panel (4-5 days)
- Certification panel orchestrator
- Judge 1: Generalist (structure review)
- Judge 2: Specialist (domain accuracy)
- Judge 3: Skeptic (critical analysis)
- Judge 4: Contextualist (context fit)
- Judge 5: Human interface (last resort)
- Consensus engine
- Human escalation triggers

### Phase 4: Scraping Engine (4-5 days)
- Scraping supervisor
- Stealth techniques (UA rotation, rate limiting, jitter)
- Error handling (404, 403, 429, 500, 503)
- Domain-specific extractors (start with ONE domain)
- Content parsing and validation

### Phase 5: Pattern Ingestion Pipeline (3-4 days)
- Main pipeline orchestrator
- Schema validation (Pydantic)
- Deduplication (text-based similarity)
- Integration with Expertise Scanner storage
- Pattern certification workflow

### Phase 6: API & Dashboard (4-5 days)
- Supervisor control endpoints
- Certification endpoints
- Scraping control endpoints
- Surveyor UI (Plain HTML/JS + Alpine.js in Generic Framework)
- Real-time monitoring (SSE/polling)

### Phase 7: Single Domain Pilot (3-4 days)
- Pilot Domain: Cooking ✓
- Pilot Neighbourhood: Parksville, BC ✓
- Configure domain-specific extractors
- Run 24-hour autonomous test
- Measure quality metrics
- Human spot-check validation
- Document findings

### Phase 8: Risk Assessment & Refinement (2-3 days)
- Analyze pilot results
- Adjust certification thresholds
- Refine human escalation triggers
- Document risk mitigations
- Create runbook for human interventions

### Phase 9: Production Hardening (2-3 days)
- Authentication
- Rate limiting
- Monitoring dashboards
- Backup/recovery
- Graceful shutdown
- Health checks

**Total Estimated**: 27-36 days (~6-7 weeks)

---

## FUTURE: Research Generator (Hooks)

### Placeholder Interfaces

```python
# autonomous_learning/research_hooks/interfaces.py

from abc import ABC, abstractmethod
from typing import Optional

class ResearchQueryInterface(ABC):
    """Hook for future Research Generator"""

    @abstractmethod
    async def submit_research_query(self, query: str, deadline: Optional[str] = None) -> str:
        """Submit a research query - FUTURE IMPLEMENTATION"""
        raise NotImplementedError("Research Generator: Coming in Phase 10")

    @abstractmethod
    async def get_research_status(self, research_id: str) -> dict:
        """Check research status - FUTURE IMPLEMENTATION"""
        raise NotImplementedError("Research Generator: Coming in Phase 10")


class PatternExtractionHook(ABC):
    """Hook for extracting patterns from research"""

    @abstractmethod
    async def extract_patterns_from_research(self, research_data: dict) -> list:
        """Extract expertise patterns from research findings - FUTURE"""
        raise NotImplementedError("Research Generator: Coming in Phase 10")
```

### Integration Points

- Pattern storage includes `research_id` field (nullable)
- Certification panel can validate research-derived patterns
- Scraping engine can be extended for research data sources
- Supervisor can manage research tasks (future)

---

## Configuration (YAML)

```yaml
# config/autonomous_learning.yaml

supervisor:
  api:
    url: https://api.z.ai/api/coding/paas/v4/chat/completions  # GLM-4
    model: glm-4
    max_tokens: 4096
    temperature: 0.7

  heartbeat:
    interval: 30
    timeout: 10
    max_missed: 3

  focus:
    window_size: 10
    drift_threshold: 0.3
    repetition_threshold: 0.95

certification:
  judges:
    - name: generalist
      role: structure_review
      api_url: https://api.z.ai/api/coding/paas/v4/chat/completions
      model: glm-4
      temperature: 0.3
      weight: 1.0

    - name: specialist
      role: domain_accuracy
      api_url: https://api.z.ai/api/coding/paas/v4/chat/completions
      model: glm-4
      temperature: 0.2
      weight: 1.0

    - name: skeptic
      role: critical_analysis
      api_url: https://api.z.ai/api/coding/paas/v4/chat/completions
      model: glm-4
      temperature: 0.5
      weight: 1.5  # Higher weight for critical issues

    - name: contextualist
      role: context_fit
      api_url: https://api.z.ai/api/coding/paas/v4/chat/completions
      model: glm-4
      temperature: 0.4
      weight: 1.0

    - name: human
      role: last_resort
      type: human
      escalation_only: true

  thresholds:
    certified: 0.8
    provisional: 0.6
    unanimous_bonus: 0.1
    skeptic_veto_critical: true

  human_triggers:
    - skeptic_critical_issues
    - consensus_below_threshold
    - judge_variance_high
    - user_flag

scraping:
  rate_limit:
    requests_per_second: 1
    burst: 5
    exponential_backoff: true

  stealth:
    user_agents:
      - "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
      - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
    jitter_percent: 20
    warm_up_requests: 3

  error_handling:
    max_retries: 3
    skip_404: true
    backoff_429: true

  pilot_domain: cooking  # Start with ONE domain

ingestion:
  validation:
    strict_mode: true
    required_fields: [name, description, problem, solution, steps]

  deduplication:
    similarity_threshold: 0.85
    method: text_based  # word_overlap, jaccard

  storage:
    pattern_directory: data/patterns/{domain}/
    backup_enabled: true

research_hooks:
  enabled: false  # FUTURE: Set to true in Phase 10
  pattern_storage_field: research_id
```

---

## Dependencies (All Free/Local)

```txt
# pyproject.toml or requirements.txt

httpx>=0.25.0           # Async HTTP client
pydantic>=2.0.0         # Data validation
asyncio                 # Async orchestration
pyyaml>=6.0             # Config parsing
tenacity>=8.2.0         # Retry logic
numpy>=1.24.0           # Calculations

# NOTE: Embeddings SKIPPED - using simple text-based similarity instead
# (no sentence-transformers, torch, or scikit-learn required)

# Optional: Research hooks (future)
geopy>=2.4.0            # Geographic calculations
pandas>=2.0.0           # Data analysis
```

---

## Success Criteria

### Phase 7 (Pilot Domain) Success

- [ ] 24-hour autonomous run completed
- [ ] >100 patterns ingested
- [ ] <5% required human review
- [ ] Certification accuracy >90% (human spot-check)
- [ ] No critical failures (crashes, data loss)
- [ ] Focus drift detected and corrected <5 occurrences
- [ ] Supervisor maintained stable operation

### Overall System Success

- [ ] Single domain operational
- [ ] 5-judge panel functional with human escalation
- [ ] Risk mitigation documented and tested
- [ ] Expertise quality validated (human spot-check)
- [ ] Dashboard functional and monitoring
- [ ] Research generator hooks in place
- [ ] Documentation complete

---

## Open Questions

1. **Pilot Domain**: Cooking ✓
2. **Pilot Neighbourhood**: Parksville, BC ✓ (geographic)
3. **Embeddings**: SKIPPED - No embedding model (simpler implementation, use text-based similarity only)
4. **Human Judge Interface**: Web UI, API, or email notifications?
5. **State Persistence**: File-based (JSON) or SQLite?
6. **Proxy Rotation**: Need for production? (Start without)
7. **Surveyor Activity Log**: What events to log? (Scrape start/end, certification results, errors, focus drift, refocus actions)

**Agent Wrapper**: Deferred to Phase 10. Proceeding with black box implementation (status monitoring only).

**Decisions Made**:
- Hierarchy: Multiverse → Universe → Neighbourhood → Domain → Patterns
- Pilot Domain: Cooking
- Pilot Neighbourhood: Parksville, BC (geographic region)
- Embeddings: SKIPPED (no sentence-transformers, use simple text-based similarity for dedup)

---

## GitHub Status

- **Repository**: https://github.com/orangelightening/ExFrame.git
- **Latest Commit**: `9895f23f` - "security: Remove .env from git and update credential setup"
- **Status**: Fully synced with GitHub

---

---

## RECOVERY POINT: 2026-01-14

**Status**: Pattern Health Diagnostics Implementation

### Completed Work

1. **Pattern Content Threshold Lowered** - Changed from 50 to 30 characters in `pattern_analyzer.py:208`
2. **Added `problematic_patterns` List** - PatternHealthReport now includes list of problematic pattern names for UI display
3. **Health Indicators on Patterns Page** - Added visual badges and colored borders (green/yellow/red) based on health status
4. **Diagnostics Page Enhancement** - Added problematic patterns list display in Diagnostics view
5. **Docker Container Rebuilt** - Changes deployed

### Files Modified

- `generic_framework/diagnostics/pattern_analyzer.py` - Threshold lowered to 30, added problematic_patterns tracking
- `generic_framework/frontend/index.html` - Health indicators on pattern cards, diagnostics page list display
- `generic_framework/diagnostics/health_checker.py` - JSON KB validation support

### Known Bug (RESOLVED)

**Health Indicator State Bug** (FIXED 2026-01-14): Health indicators now appear correctly on all domain changes.

**Previous Symptoms**:
- Health indicators showed "healthy" for all patterns (incorrect)
- When changing domains directly, health flags didn't appear at all
- Health data only loaded properly after going through Query flow first

**Root Cause**: `switchDomain()` called `loadDomainInfo()` which didn't fetch health data. `loadPatterns()` was the only function that fetched health data from `/api/diagnostics/patterns/health`.

**Fix Applied**: Modified `switchDomain()` in `index.html:2368-2374` to check if current view is 'patterns' and call `loadPatterns()` instead of `loadDomainInfo()` when on the Patterns tab.

**Location**: `generic_framework/frontend/index.html` line 2368-2374

---

**Last Updated**: 2026-01-14
**Status**: Health indicator bug fixed and deployed
**Next Action**: Monitor for any additional state-related issues

**Decisions Made**:
- Hierarchy: Multiverse → Universe → Neighbourhood → Domain → Patterns
- Pilot Domain: Cooking
- Pilot Neighbourhood: Parksville, BC (geographic)
- Surveyor UI: Plain HTML/JS + Alpine.js in Generic Framework (replace Ingestion tab)
- Agent Wrapper: Deferred to Phase 10 (black box with status monitoring for v1)
- Embeddings: SKIPPED (use simple text-based similarity, no ML dependencies)
- Judges: 5-judge panel (4 AI + 1 human last resort)
- All APIs: GLM-4 (existing config, no additional costs)
