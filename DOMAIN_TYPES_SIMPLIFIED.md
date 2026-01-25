# Domain Type System - Simplified Plan

**Version:** 2.0
**Date:** 2026-01-24
**Status:** REVISED
**Purpose:** Simple domain type selection with guided configuration

---

## Overview

Instead of complex "archetypes" with workflows and state machines, we use a **simple domain type selector**:

1. User selects **Domain Type 1-5** (dropdown)
2. System shows **relevant config fields** for that type
3. User fills in the form
4. System generates `domain.json`

**Test domains** have no type restriction - can be configured any way.

---

## The 5 Domain Types

### Type 1: Creative Generator

**Use for:** Poems, stories, creative content, art

**Config Fields:**
- Domain name
- Description
- Creative keywords (list): poem, story, write, create, etc.
- Temperature: 0.7-0.9 (slider)
- Show patterns: No (fixed)
- LLM provider: [dropdown]

**Generated Config:**
```json
{
  "plugins": [
    {
      "plugin_id": "creative",
      "class": "GeneralistPlugin",
      "config": {
        "name": "Creative",
        "keywords": ["poem", "story", "write", "create"],
        "threshold": 0.1
      }
    }
  ],
  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.8,
        "creative_mode": true
      }
    }
  ],
  "knowledge_base": {
    "similarity_threshold": 0.2
  }
}
```

**UI Hints:**
- Show creative keywords as tags
- Temperature slider (0.7 to 0.9)
- No pattern list shown
- "Regenerate" button prominent

---

### Type 2: Knowledge Retrieval

**Use for:** How-to guides, FAQs, technical documentation

**Config Fields:**
- Domain name
- Description
- Keywords (list)
- Similarity threshold: 0.3-0.5 (slider)
- Max patterns: 5-20 (slider)
- Temperature: 0.3-0.5 (slider)
- Show patterns: Yes (fixed)
- LLM provider: [dropdown]

**Generated Config:**
```json
{
  "plugins": [
    {
      "plugin_id": "generalist",
      "class": "GeneralistPlugin",
      "config": {
        "keywords": ["how", "what", "explain", "guide"],
        "threshold": 0.2
      }
    }
  ],
  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.4,
        "max_patterns": 10
      }
    }
  ],
  "knowledge_base": {
    "similarity_threshold": 0.3
  }
}
```

**UI Hints:**
- Pattern cards with "Patterns referenced" list
- Clickable patterns
- Standard LLM synthesis

---

### Type 3: Document Store Search

**Use for:** External documentation, API docs, live data

**Config Fields:**
- Domain name
- Description
- Document store type: [dropdown]
  - ExFrame Instance
  - Vector Store
  - Web Search
- Remote URL: [text input]
- API Key (if needed): [text input]
- Research strategy: [checkbox]
  - Local documents (file paths)
  - Document store first
- Temperature: 0.5-0.7 (slider)
- Show sources: Yes (fixed)

**Generated Config:**
```json
{
  "plugins": [
    {
      "plugin_id": "exframe_specialist",
      "class": "ExFrameSpecialistPlugin",
      "config": {
        "document_store_enabled": true,
        "local_patterns_enabled": true,
        "document_store_config": {
          "type": "exframe_instance",
          "remote_url": ""
        },
        "research_strategy": {
          "type": "document",
          "documents": [
            {"type": "file", "path": "README.md"}
          ]
        }
      }
    }
  ],
  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.6
      }
    }
  ]
}
```

**UI Hints:**
- "Sources searched" section
- Document titles
- Session history
- "Capture as pattern" button

---

### Type 4: Analytical Engine

**Use for:** Research, analysis, correlation, reports

**Config Fields:**
- Domain name
- Description
- Max research steps: 1-20 (slider)
- Timeout (seconds): 30-600 (slider)
- Research capabilities: [checkboxes]
  - Web search
  - Document search
  - Data correlation
- Temperature: 0.4-0.6 (slider)
- Report format: [dropdown]
  - Structured
  - Narrative
  - Bullets

**Generated Config:**
```json
{
  "plugins": [
    {
      "plugin_id": "researcher",
      "class": "ResearchSpecialistPlugin",
      "config": {
        "max_steps": 10,
        "timeout": 300
      }
    }
  ],
  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "config": {
        "mode": "enhance",
        "temperature": 0.5,
        "max_tokens": 8192
      }
    }
  ]
}
```

**UI Hints:**
- Progress indicator (step 3/10...)
- "Download report" button
- Interim results shown
- "Save as pattern" button

---

### Type 5: Hybrid Assistant

**Use for:** General purpose, flexible, user choice

**Config Fields:**
- Domain name
- Description
- Keywords (list)
- Similarity threshold: 0.3-0.5 (slider)
- Confidence threshold: 0.3-0.7 (slider)
- Require confirmation: [checkbox]
- Research on fallback: [checkbox]

**Generated Config:**
```json
{
  "plugins": [
    {
      "plugin_id": "hybrid",
      "class": "GeneralistPlugin",
      "config": {
        "threshold": 0.2
      }
    }
  ],
  "enrichers": [
    {
      "module": "plugins.enrichers.llm_fallback_enricher",
      "class": "LLMFallbackEnricher",
      "config": {
        "mode": "fallback",
        "min_confidence": 0.3,
        "require_confirmation": true
      }
    }
  ],
  "knowledge_base": {
    "similarity_threshold": 0.3
  }
}
```

**UI Hints:**
- Patterns shown first
- "Extend search with AI?" button
- Confirmation dialog
- LLM appended if accepted

---

### Test Domains (No Type Restriction)

**Use for:** Testing, experimentation, development

**Config Fields:**
- Domain name
- Description
- **All fields are configurable** (no preset)

**Behavior:**
- Can be configured like any of types 1-5
- Or completely custom configuration
- No validation on plugin combinations
- Free-form configuration

**UI Hints:**
- "Advanced mode" toggle
- Show all config fields
- Test panel
- Mode selector
- Interaction log

---

## Implementation Plan

### Phase 1: UI Domain Creator (Week 1)

**Tasks:**
- [ ] Create domain creation page
- [ ] Add domain type dropdown (5 types)
- [ ] Create config form builder
  - [ ] Show different fields based on type selection
  - [ ] Add validation per field type
- [ ] Add "Create Domain" button
- [ ] Add domain list page

**Files:**
```
static/domain-creator.html
static/domain-creator.js
static/domain-creator.css
```

**Testing:**
- [ ] Select each type, verify correct fields show
- [ ] Test validation (min/max values)
- [ ] Test domain creation
- [ ] Verify created domain works

### Phase 2: Config Generation Backend (Week 1)

**Tasks:**
- [ ] Create `POST /api/domains/create`
- [ ] Implement config generator for each type
- [ ] Add validation logic
- [ ] Add domain directory creation
- [ ] Add domain registration

**Files:**
```
generic_framework/api/routes/domains.py (update)
generic_framework/core/domain_factory.py (new)
```

**Testing:**
- [ ] Create domain of each type via API
- [ ] Verify generated config is correct
- [ ] Test validation
- [ ] Test domain loads successfully

### Phase 3: Migrate Existing Domains (Week 1-2)

**Tasks:**
- [ ] Add `type` field to existing domains
- [ ] Map existing domains to types:
  - poetry_domain → Type 1
  - cooking, python, first_aid, gardening, diy, binary_symmetry → Type 2
  - exframe → Type 3
  - (none) → Type 5
- [ ] Test all migrated domains
- [ ] Remove any workaround code

**Files:**
```
universes/MINE/domains/*/domain.json
```

**Testing:**
- [ ] Query each migrated domain
- [ ] Verify behavior unchanged
- [ ] Test new features work

### Phase 4: Documentation (Week 2)

**Tasks:**
- [ ] Update README with domain type system
- [ ] Create DOMAIN_TYPES.md reference
- [ ] Add examples for each type
- [ ] Update plugin docs

**Files:**
```
DOMAIN_TYPES.md (new)
README.md (update)
```

---

## Summary: The Simplified Approach

**Before (Complex):**
- Archetypes as objects with workflows
- State machines
- Plugin inheritance
- Complex metadata

**After (Simple):**
- Domain type = dropdown selection
- Config fields = form builder
- Type determines which fields to show
- Test domains = free-form configuration

**Benefits:**
1. ✅ **Simpler** - Easier to understand and maintain
2. ✅ **Flexible** - Can add types without breaking existing
3. ✅ **Clear boundaries** - Type is just a config preset
4. ✅ **User-friendly** - Guided creation experience
5. ✅ **Test-friendly** - Test domains have full freedom

---

## Open Questions

1. **Should we allow "custom type"** (user configures everything manually)?
   - Yes: Test domains already cover this
   - No: Force selection of 5 types

2. **Can a domain change its type?**
   - Maybe: Add "Change Type" button that reconfigures
   - Validation to ensure data compatibility

3. **Should types be versioned?**
   - Probably not needed if it's just config presets

---

**Status:** REVISED - Ready for implementation
