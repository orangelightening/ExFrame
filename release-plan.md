# EEFrame Release Plan

**Version**: 1.0
**Target**: First production-ready release
**Status**: Implementation Ready
**Created**: 2026-01-18

---

## Executive Summary

**Goal**: Deliver a working system with persona-driven queries, heartbeat monitoring, and expert panel collaboration.

**Key Philosophy**: Panel of Experts replaces certification. Heartbeat prevents AI "chat mode drift."

**Timeline**: 4 weeks to MVP (Minimum Viable Product)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                    (Generic Framework Frontend)                  │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      QUERY PROCESSING ENGINE                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Persona Selector    →   Specialist Match                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Prompt Builder (Format-Agnostic)                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Panel of Experts (Replaces Certification Panel)           │  │
│  │  • Sequential  • Parallel  • Debate modes                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      HEARTBEAT MONITOR                           │
│  • Detects persona drift        • Recovery prompts              │
│  • Response quality checks      • Analytics logging             │
└─────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM INTEGRATION                             │
│  • GLM-4.7 support             • Multiple format support         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Release 1.0 - MVP (4 Weeks)

### Week 1: Core Persona System

**Goal**: Personas exist as trackable entities

| Task | File | Description |
|------|------|-------------|
| 1.1 | `generic_framework/core/persona_plugin.py` | PersonaPlugin abstract base class |
| 1.2 | `generic_framework/plugins/personas/__init__.py` | Persona registry |
| 1.3 | `generic_framework/plugins/personas/diy_expert.py` | First working persona example |
| 1.4 | `generic_framework/plugins/personas/cooking_expert.py` | Second persona example |
| 1.5 | `generic_framework/assist/persona_loader.py` | Load personas from domain config |
| 1.6 | Update domain.json files | Add persona_plugin references |

**Deliverable**: Personas load from config, can be listed via API

---

### Week 2: Prompt Builder + Panel of Experts

**Goal**: Format-agnostic prompts + collaborative expert panels

| Task | File | Description |
|------|------|-------------|
| 2.1 | `generic_framework/assist/prompt_builder.py` | Format-agnostic prompt construction |
| 2.2 | `generic_framework/assist/panel_manager.py` | Panel of Experts (replaces judges) |
| 2.3 | `generic_framework/plugins/personas/code_review_panel.py` | First panel persona |
| 2.4 | Update `assist/engine.py` | Integrate panel processing |
| 2.5 | Test script | Compare panel vs single persona |

**Panel Modes**:
- **Sequential**: Each expert builds on previous (default)
- **Parallel**: All experts respond independently
- **Debate**: Experts critique each other

**Deliverable**: Panel of Experts functional, replacing certification panel

---

### Week 3: Heartbeat System

**Goal**: Detect and recover from AI drift (CRITICAL)

| Task | File | Description |
|------|------|-------------|
| 3.1 | `generic_framework/assist/heartbeat_monitor.py` | Failure detection + recovery |
| 3.2 | `generic_framework/assist/recovery_prompts.py` | Per-persona recovery templates |
| 3.3 | `generic_framework/logs/heartbeat_log.py` | Heartbeat event logging |
| 3.4 | Update `assist/engine.py` | Wrap LLM calls with heartbeat |
| 3.5 | Heartbeat API endpoints | `/api/heartbeat/status`, `/api/heartbeat/config` |

**Heartbeat Triggers**:
| Trigger | Detection | Action |
|---------|-----------|--------|
| Response too short | < 100 chars | Recovery prompt |
| Generic language | "I'm an AI language model" | Recovery prompt |
| Missing keywords | Expected terms absent | Recovery prompt |
| Repetition | Same phrase repeated | Reset + retry |
| Persona drift | LLM loses voice | Context reminder |

**Deliverable**: AI stays in character, drift is detected and corrected

---

### Week 4: Analytics + UI Integration

**Goal**: Track performance, expose controls

| Task | File | Description |
|------|------|-------------|
| 4.1 | `generic_framework/api/personas.py` | Persona CRUD endpoints |
| 4.2 | `generic_framework/api/panels.py` | Panel configuration endpoints |
| 4.3 | `generic_framework/api/analytics.py` | Per-persona metrics |
| 4.4 | `generic_framework/frontend/index.html` | Add Personas tab |
| 4.5 | `generic_framework/frontend/index.html` | Add Panel configuration UI |
| 4.6 | `generic_framework/frontend/index.html` | Add Heartbeat dashboard |

**UI Components**:
- Persona list with edit capability
- Panel configuration (drag-drop experts)
- Real-time heartbeat monitoring
- Per-persona analytics dashboard

**Deliverable**: Full UI for persona and panel management

---

## Data Model

### Persona Entity

```json
{
  "persona_id": "diy_home_depot_expert",
  "name": "DIY Expert",
  "version": "1.0",

  "identity": {
    "role": "You are a knowledgeable home improvement specialist",
    "expertise": ["construction", "materials", "tools"],
    "tone": "practical and specific",
    "audience": "DIY enthusiasts"
  },

  "behaviors": [
    "Always mention specific measurements",
    "Include safety considerations"
  ],

  "example_phrases": [
    "For deck joists, you'll want 2x6 lumber..."
  ],

  "config": {
    "temperature": 0.7,
    "max_tokens": 8192,
    "preferred_format": "anthropic"
  },

  "heartbeat": {
    "enabled": true,
    "mode": "moderate",
    "triggers": {
      "response_too_short": true,
      "generic_language": true,
      "persona_drift": true
    },
    "recovery": {
      "max_attempts": 2,
      "recovery_prompt": "Remember: {persona_context}"
    }
  },

  "analytics": {
    "total_queries": 0,
    "avg_confidence": 0.0,
    "heartbeat_triggers": 0,
    "recovery_success_rate": 0.0
  }
}
```

### Panel Persona

```json
{
  "persona_id": "code_review_panel",
  "name": "Code Review Panel",
  "type": "panel",

  "panel": {
    "mode": "sequential",
    "max_rounds": 2,
    "consensus_threshold": 0.7,

    "experts": [
      {
        "persona_id": "security_expert",
        "role": "Security Specialist",
        "weight": 1.0
      },
      {
        "persona_id": "performance_expert",
        "role": "Performance Engineer",
        "weight": 1.0
      },
      {
        "persona_id": "readability_expert",
        "role": "Code Quality Specialist",
        "weight": 0.8
      }
    ],

    "facilitator": {
      "persona_id": "tech_lead",
      "role": "Synthesize expert opinions"
    }
  }
}
```

---

## API Endpoints

### Persona Management

```
GET    /api/personas                    # List all personas
POST   /api/personas                    # Create persona
GET    /api/personas/:id                # Get persona details
PUT    /api/personas/:id                # Update persona
DELETE /api/personas/:id                # Delete persona
```

### Panel Management

```
GET    /api/panels                      # List all panels
POST   /api/panels                      # Create panel
GET    /api/panels/:id                  # Get panel details
PUT    /api/panels/:id                  # Update panel
POST   /api/panels/:id/test             # Test panel with sample query
```

### Heartbeat Monitoring

```
GET    /api/heartbeat/status            # Current heartbeat status
GET    /api/heartbeat/logs              # Heartbeat event logs
PUT    /api/heartbeat/config/:persona   # Update heartbeat config
GET    /api/heartbeat/analytics         # Heartbeat analytics
```

### Analytics

```
GET    /api/analytics/personas          # Per-persona metrics
GET    /api/analytics/panels            # Per-panel metrics
GET    /api/analytics/heartbeat         # Heartbeat effectiveness
```

---

## File Structure

```
generic_framework/
├── core/
│   ├── persona_plugin.py          # PersonaPlugin ABC
│   └── generic_domain.py          # (existing, update for personas)
│
├── plugins/
│   ├── personas/
│   │   ├── __init__.py            # Persona registry
│   │   ├── diy_expert.py          # DIY persona
│   │   ├── cooking_expert.py      # Cooking persona
│   │   ├── code_review_panel.py   # Panel persona
│   │   └── ...                    # More personas
│   │
│   └── enrichers/                 # (existing)
│
├── assist/
│   ├── engine.py                  # (update for personas)
│   ├── persona_loader.py          # Load personas from config
│   ├── prompt_builder.py          # Format-agnostic prompts
│   ├── panel_manager.py           # Panel of Experts
│   ├── heartbeat_monitor.py       # Drift detection
│   ├── recovery_prompts.py        # Recovery templates
│   └── enricher.py                # (existing)
│
├── api/
│   ├── app.py                     # (update, mount new routes)
│   ├── personas.py                # Persona CRUD API
│   ├── panels.py                  # Panel management API
│   ├── heartbeat.py               # Heartbeat monitoring API
│   └── analytics.py               # Analytics API
│
├── logs/
│   ├── heartbeat_log.py           # Heartbeat event logging
│   └── query_log.py               # (existing, update)
│
└── frontend/
    └── index.html                 # Add Personas, Panels, Heartbeat tabs
```

---

## Configuration Updates

### Domain Config with Personas

**Before**:
```json
{
  "domain_id": "diy",
  "specialists": [{
    "specialist_id": "generalist",
    "name": "DIY Expert"
  }]
}
```

**After**:
```json
{
  "domain_id": "diy",
  "plugins": [
    {
      "module": "plugins.personas.diy_expert",
      "class": "DIYExpert",
      "enabled": true
    }
  ],
  "specialists": [{
    "specialist_id": "generalist",
    "name": "DIY Expert",
    "persona_plugin": "diy_expert"
  }]
}
```

---

## Success Criteria

### Week 1 Milestone
- [ ] PersonaPlugin interface defined
- [ ] At least 2 working personas
- [ ] Personas load from domain config
- [ ] API returns list of personas

### Week 2 Milestone
- [ ] PromptBuilder supports 3 formats
- [ ] Panel of Experts processes queries
- [ ] Sequential mode working
- [ ] Facilitator synthesis working

### Week 3 Milestone
- [ ] Heartbeat detects drift
- [ ] Recovery prompts improve responses
- [ ] Heartbeat events logged
- [ ] API exposes heartbeat status

### Week 4 Milestone
- [ ] Full persona CRUD API
- [ ] Panel configuration API
- [ ] Analytics tracking per persona
- [ ] UI for persona/panel management
- [ ] Heartbeat dashboard visible

### Release Criteria
- [ ] Panel of Experts replaces certification panel
- [ ] Heartbeat prevents AI drift
- [ ] Personas are trackable entities
- [ ] Analytics measure effectiveness
- [ ] UI provides full control
- [ ] Documentation complete

---

## Deferred to Future Releases

### Release 1.1 (Post-MVP)
- A/B testing framework for personas
- Additional panel modes (debate refinement)
- Persona marketplace/sharing
- Multi-persona per domain support

### Release 2.0
- Research Generator integration
- Autonomous learning with panel-validated patterns
- Advanced consensus algorithms
- Persona learning from feedback

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Persona drift acceptance | Heartbeat with recovery prompts |
| Panel performance overhead | Cache persona instances, parallel execution |
| Format lock-in | PromptBuilder abstraction, test empirically |
| UI complexity | Incremental rollout, start with API-first |
| Analytics overhead | Async logging, batch writes |

---

## Testing Strategy

### Unit Tests
- Persona loading and registration
- Prompt format generation
- Heartbeat trigger detection
- Panel contribution tracking

### Integration Tests
- End-to-end query with persona
- Panel processing (all modes)
- Heartbeat recovery flow
- API to frontend integration

### Quality Tests
- Persona strength measurement (heuristic)
- Panel consensus calculation
- Heartbeat recovery success rate
- Response quality comparison

---

## Next Steps

1. **Review this plan** - Confirm priorities and timeline
2. **Create detailed task breakdown** - Convert to GitHub issues
3. **Set up branch strategy** - `feature/personas`, `feature/heartbeat`, etc.
4. **Begin Week 1 implementation** - Start with PersonaPlugin interface

---

## Notes

- **Backward compatibility**: Existing domains work without personas (implicit fallback)
- **Incremental value**: Each week delivers working features
- **GitHub ready**: This plan can be committed and shared
- **Heartbeat is critical**: This is the feature that prevents AI "chat mode drift"

---

**Document Version**: 1.0
**Last Updated**: 2026-01-18
**Status**: Ready for implementation
