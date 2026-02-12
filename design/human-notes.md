# Human Notes (4th Persona) - Personal Diary Collector

**Status:** Design Phase - Ready for Implementation
**Version:** 1.0
**Created:** 2026-02-11

---

## Overview

The **Human Notes** domain implements a **4th persona** that serves as a personal diary and knowledge collector for the panel discussion system.

### Persona Definition

**Role:** Personal Diary Collector and Document Curator
**Temperature:** 0.6 (balanced, factual)
**Behavior:**
- Receives human input and documents as input
- Writes directly to domain log (bypasses query/response flow)
- Formats as diary entries with timestamps
- Does NOT synthesize or generate AI responses
- Collects factual human information
- Maintains neutral, objective tone
- Preserves human voice and perspective

### Position in Panel Discussion System

```
PANEL QUERY → Human Notes Domain → Direct Log Write
```

---

## Configuration Requirements

### 1. Domain Configuration

**Current Issue:** Human Notes domain was created via API with default schema (no "persona" field in pattern_schema)

**Required Changes:**

#### A. Add to `domain.json` schema

```json
{
  "domain_id": "human_notes",
  "domain_name": "Human Notes",
  "description": "Collects and documents human-provided information. Acts as personal diary.",
  "version": "1.0.0",
  "created_at": "2026-02-11T17:12:45.887Z",

  "persona": "human",
  "temperature": 0.6,

  "categories": ["notes", "documents"],
  "tags": ["human", "notes", "diary", "journal", "personal"],

  "pattern_schema": {
    "required_fields": ["id", "name", "pattern_type", "problem", "solution"],
    "optional_fields": [
      "description",
      "steps",
      "conditions",
      "related_patterns",
      "prerequisites",
      "alternatives",
      "confidence",
      "sources",
      "tags",
      "examples",
      "domain",
      "created_at",
      "updated_at",
      "times_accessed",
      "user_rating",
      "origin",
      "origin_query",
      "llm_generated",
      "status"
    ]
  },

  "plugins": [
    {
      "plugin_id": "panel_coordinator",
      "name": "Panel Coordinator",
      "description": "Manages multi-domain discussions, routes topics to panelists, and collects all responses for Judge domain.",
      "module": "plugins.specialists.panel_coordinator",
      "enabled": true
    }
  ],

  "enrichers": [
    {
      "module": "plugins.enrichers.human_notes_collector",
      "class": "HumanNotesCollectorEnricher",
      "enabled": true,
      "config": {
        "preserve_human_voice": true,
        "add_timestamps": true,
        "diary_format": "markdown",
        "entry_template": "## {content}\n\n**From:** {source}\n**Date:** {timestamp}\n**Type:** {type}\n**{content}\n---"
      }
    }
  },

  "knowledge_base": {
    "type": "json",
    "storage_path": "domain_log.md"
  },

  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "domain_log.md"
  },

  "ui_config": {
    "placeholder_text": "Share your thoughts, notes, or documents...",
    "example_queries": [
      "What's on your mind today?",
      "How was your weekend?",
      "What are you working on?"
    ]
  }
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Goal:** Integrate Human Notes into ExFrame panel system

#### Tasks

##### 1.1 Update Domain Schema (2 hours)
**Description:** Extend domain.json to support Human Notes persona

**Changes Required:**
- [ ] Add "persona" field to pattern_schema
- [ ] Update all persona references in code to check for "human" persona
- [ ] Update generic enrichers to handle human_notes domain
- [ ] Ensure panel coordinator routes queries to human_notes
- [ ] Add human_notes to domain list in panel coordinator

**Acceptance Criteria:**
- [ ] Domain can be created via `/api/admin/domains`
- [ ] Domain appears in domain list and UI
- [ ] Human notes can receive queries via panel coordinator
- [ ] Queries are routed to appropriate specialists
- [ ] Direct log write bypass working
- [ ] No breaking changes to existing query flow

---

## Success Criteria

- [ ] Multi-domain panel system operational with 4 personas
- [ ] Human Notes integrated into discussion flow
- [ ] Direct log write path functional
- [ ] Decision reports accessible to all domains

---

## Notes

**Simpler than expected:** The human notes persona is much simpler than multi-domain synthesizer. It's essentially:
- ✅ Input → Log write (no LLM)
- ✅ No complex routing or orchestration
- ✅ Direct persistence (append-only operation)
- ✅ Temperature 0.6 (factual, not creative)

**Key Feature: QUERY BYPASS**
This is significant - human notes bypasses the entire query processor and response generator, writing directly to the domain log. This is:

**More efficient** - No LLM API calls per query
**More authentic** - Human voice preserved without AI rewording
**More transparent** - Direct log, clear provenance

---

## Ready for Implementation

**Status:** Design complete, system architecture defined, implementation plan ready

**Next Steps:**
1. Update domain.json schema
2. Restart panel coordinator plugin
3. Create human notes domain
4. Test integration
5. Deploy

---

**This is ready to commit!** Should I proceed?** 🚀