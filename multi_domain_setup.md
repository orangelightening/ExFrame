# Multi-Domain Panel Discussion Setup

## Domains to Create (4 total)

### 1. ai_panel - Panel Organizer
**Persona:** Librarian
**Temperature:** 0.6
**Description:** Orchestrates multi-domain AI panel discussions, presents topics to Panelists, collects responses for Judge

**Key Configuration:**
```json
{
  "domain_id": "ai_panel",
  "persona": "librarian",
  "enable_pattern_override": true,
  "accumulator": {
    "enabled": false  // Panel organizes, doesn't need memory
  },
  "plugins": [
    {
      "plugin_id": "panel_coordinator",
      "name": "Panel Coordinator",
      "description": "Manages panel discussions, routes topics to panelists",
      "module": "plugins.specialists.panel_coordinator",
      "enabled": true
    }
  ]
}
```

### 2. panelist_alpha - Creative Contrarian (Poet)
**Persona:** Poet
**Temperature:** 0.8
**Description:** Creative voice in AI panel discussions. Takes unconventional positions, challenges assumptions, plays devil's advocate.

**Key Configuration:**
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

### 3. panelist_beta - Creative Voice 2 (Poet)
**Persona:** Poet
**Temperature:** 0.8
**Description:** Alternative creative voice in AI panel discussions. Imaginative, playful, takes wild ideas.

**Key Configuration:**
```json
{
  "domain_id": "panelist_beta",
  "persona": "poet",
  "temperature": 0.8,
  "enable_pattern_override": true,
  "ui_config": {
    "placeholder_text": "What if gravity is just a suggestion?",
    "example_queries": [
      "Should we ban all sharp objects?",
      "Is the moon made of cheese?"
    ]
  }
}
```

### 4. ai_judge - Multi-Domain Synthesizer
**Persona:** Librarian
**Temperature:** 0.7
**Description:** Reads from ALL domain logs (cooking, diy, exframe), synthesizes perspectives, creates summary decisions. Accesses shared `/app/project/panel_decisions.md` output file.

**Key Configuration:**
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
    "enabled": false  // Judges don't accumulate, just synthesize
  },
  "plugins": [
    {
      "plugin_id": "multi_domain_synthesizer",
      "name": "Multi-Domain Synthesizer",
      "description": "Synthesizes responses from all panelists and domains",
      "module": "plugins.specialists.multi_domain_synthesizer",
      "enabled": true
    }
  ]
}
```

## Panel Workflow

### 1. Panel Domain Receives Topic
```json
{
  "topic": "Organize a discussion about: Should AI art be censored?",
  "focus": 0.95
}
```

### 2. Panel Queries Panelists
```json
{
  "query": "What's your take on: Should AI art be censored?",
  "panelist_id": "panelist_alpha",
  "prompt": "You are the creative voice in panel discussions. Challenge conventional thinking, propose wild ideas, and argue from unique perspectives."
}
```

### 3. Panel Queries Panelist Beta
```json
{
  "query": "What's your take on: Should AI art be censored?",
  "panelist_id": "panelist_beta",
  "prompt": "You are the alternative creative voice. Be imaginative, playful, and take provocative positions when appropriate."
}
```

### 4. All Responses → Judge Domain
- Judge receives all panelist responses
- Reads domain logs from cooking, diy, exframe
- Synthesizes perspectives
- Creates decision report

### 5. Decision Report
- Written to `/app/project/panel_decisions.md`
- Accessible to all domains
- Contains final decision + panelist breakdown

## Implementation Approach

**Don't create panel_coordinator plugin from scratch!**

Instead:
1. ✅ **Use existing domain routing** - Judge domain calls other domains via API
2. ✅ **Leverage existing domain_log.md files** - Rich context already exists
3. ✅ **Add synthesizer plugin** to Judge domain
4. ✅ **Configure output file** - Shared `/app/project/panel_decisions.md`

## Next Steps

1. Create 4 domains via API (or confirm you want me to)
2. Add multi-domain synthesizer to Judge
3. Test query flow
4. Verify decision reports created

---

**This leverages existing rich conversation history rather than starting fresh!**