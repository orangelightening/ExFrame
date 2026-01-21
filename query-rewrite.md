# Query System Rewrite: Knowledge Dashboard Design Specification

**Version:** 1.1 (APPROVED)
**Status:** Approved for Implementation - Phase 1
**Author:** EEFrame Product Team
**Date:** 2025-01-15

---

## Executive Summary

This specification redefines the Query interface as a **Knowledge Dashboard** - where Responsible Agents (human domain experts) directly accept AI-generated knowledge into curated domains. This represents a fundamental shift from "AI answers" to "human-validated expertise."

### Core Philosophy
> "The query position is a knowledge dashboard where Responsible Agents declare the truth about guided/authenticated AI-curated domains of expertise."

**Key Principle:** User acceptance IS the certification. When a Responsible Agent clicks "Accept as Pattern," that decision IS the validation. No separate "candidate → certified" workflow exists.

Other interfaces may take AI responses at face value. This interface explicitly puts human judgment at the center of knowledge creation.

---

## Current State (Reference Only)

### How It Works Now
1. User queries system (e.g., "What is a pattern?" in `exframe_methods` domain)
2. System immediately replies with local hit summary:
   - 5 patterns found
   - Confidence: 83%
   - Invitation to extend search with AI
3. User clicks extend → 2.5 second wait → AI-generated answer
4. Response marked: "83% Confidence, AI-Generated"
5. **ISSUE:** No clear path to accept AI response into knowledge base

### What Works
- ✅ Local pattern search is fast and accurate
- ✅ Confidence scoring provides quality signal
- ✅ Extend with AI button provides optionality
- ✅ Partial response shows before LLM commitment

### What Doesn't Work
- ❌ No human validation step before knowledge acceptance
- ❌ No clear workflow to accept AI responses as patterns
- ❌ No distinction between "curated" and "generated" content
- ❌ Missing mechanism to grow knowledge base from queries

---

## Proposed Workflow: Knowledge Dashboard

### The Simplified Model

**OLD (Overcomplicated):**
```
Query → Extend → LLM → Create CANDIDATE → Later CERTIFY → Finally Use
```

**NEW (Your Vision):**
```
Query → Extend → LLM → User Accepts → Pattern Created & IMMEDIATELY USED
```

**Key Insight:** The user's acceptance at query time **IS** the certification. There is no separate "candidate → certified" workflow. The act of a Responsible Agent clicking "Yes, make this a pattern" **is** the validation.

---

### Phase 1: Domain Entry & Query Initiation

#### Step 1: Landing Page Display
**Behavior:** Query screen for domain displays from top (fresh state)

**Rationale:** Each query session should start fresh, not where user left off. This encourages deliberate domain selection and reduces context contamination.

**UI Requirements:**
- Domain dropdown defaults to `[Select Domain]` or most recently used
- Query input is empty
- Previous results are not displayed
- Sample queries are visible but not auto-populated

#### Step 2: Domain Selection
**Behavior:** User explicitly selects domain (e.g., `exframe_methods`)

**UI Requirements:**
- Domain dropdown with visual feedback
- Domain description/context shown on selection
- Pattern count for domain displayed
- Last update timestamp shown

#### Step 3: Sample Query Selection (Optional)
**Behavior:** User can click sample query to populate input field

**UI Requirements:**
- Sample queries displayed as clickable chips
- Clicking populates query input but does NOT auto-submit
- User can edit sample query before submission
- Visual distinction between "sample" and "custom" queries

#### Step 4: Query Submission
**DECISION:** Require Submit Query button ✅ (User confirmed)

**Rationale:** This dashboard is about deliberate knowledge creation, not casual exploration. The submit action represents a formal query to the knowledge base.

**UI Requirements:**
- Submit Query button is primary CTA
- Keyboard shortcut (Enter) works
- Button state changes on submit (loading indicator)
- 2-3 second max response time for local results

---

### Phase 2: Local Results Display

#### Step 5: Present Local Results
**Behavior:** System displays results from local curated patterns

**UI Requirements:**
```
┌─────────────────────────────────────────────────┐
│  Results: "What is a pattern?"                  │
│                                                 │
│  [Response Content - from curated patterns]     │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 📊 Query Statistics                       │  │
│  │ • 5 patterns found                        │  │
│  │ • 83% Confidence                           │  │
│  │ • All sources validated by experts        │  │
│  │                                           │  │
│  │ [🔍 Extend Search with Documentation]    │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Data Displayed:**
- Response content (formatted from local patterns)
- Pattern count (e.g., "5 patterns found")
- Confidence score (e.g., "83% Confidence")
- Source validation status (e.g., "All sources validated by experts")
- Pattern names used (clickable to view individual patterns)

**State Behavior:**
- Results persist until new query submitted
- Extend Search button is always available
- No auto-timeout or dismissal
- User can navigate away and return to same state

---

### Phase 3: External Search (Extend)

#### Step 6: User Initiates External Search
**Behavior:** User clicks "Extend Search with Documentation" button

**UI Requirements:**
- Button changes to loading state: "Searching Documentation..."
- Progress indicator (2-5 second expected duration)
- Source indicator: "Searching 3 documentation files..."
- Cancel button appears (allows abort)

#### Step 7: LLM Searches Domain Data Source
**Behavior:** LLM searches domain-specific external data source

**Data Source Mapping:**
```
exframe_methods → /app/docs/*.md (local documentation files)
cooking         → Internet search (recipe sites, food blogs)
python          → Internet search (Python docs, StackOverflow)
first_aid       → Internet search (medical sites, Red Cross)
```

**Search Strategy:**
- Domain-specific source configuration in `domain.json`
- Source type: `local_docs` | `web_search` | `hybrid`
- Source list/URL patterns in domain config
- Fallback to general web search if domain source unavailable

**Example Config:**
```json
{
  "domain_id": "exframe_methods",
  "data_sources": {
    "type": "local_docs",
    "paths": ["/app/docs/*.md"],
    "fallback": "web_search"
  }
}
```

#### Step 8: Present External Search Results
**Behavior:** System displays LLM-generated response from external search

**UI Requirements:**
```
┌─────────────────────────────────────────────────┐
│  🔍 Extended Search Results                     │
│                                                 │
│  [LLM-Generated Content from Documentation]    │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ 📊 Source Statistics                       │  │
│  │ • Searched: 3 documentation files          │  │
│  │ • References: user-guide.md, README.md    │  │
│  │ • Processing time: 3.2 seconds            │  │
│  │                                           │  │
│  │ This content is AI-generated from          │  │
│  │ external sources.                         │  │
│  │                                           │  │
│  │ [✓ Accept as New Pattern]  [✗ Discard]   │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Critical Distinctions:**
- **Visual Separation:** External results clearly distinguished from local results
- **Source Attribution:** Which documentation files were searched
- **Clear Labeling:** "AI-generated from external sources" (not "unvalidated")
- **No Confidence Score:** External results don't show confidence (not relevant yet)

**User Actions:**
1. Read through the extended response
2. Click "Accept as New Pattern" to proceed
3. Click "Discard" to reject (returns to local results)
4. Navigate away (equivalent to Discard)

---

### Phase 4: Pattern Creation (Immediate)

#### Step 9: Pattern Acceptance & Creation
**Behavior:** User accepts external search results → Pattern created immediately

**The Key Change:** There is NO intermediate validation step. User acceptance IS the validation.

**UI Requirements:**
```
┌─────────────────────────────────────────────────┐
│  📝 New Pattern Created                         │
│                                                 │
│  Pattern added to exframe_methods domain:      │
│  • Name: "EEFrame Pattern Structure Extended"  │
│  • Origin: External search (LLM + docs)        │
│  • Confidence: 84%                             │
│  • Status: Validated by your acceptance        │
│                                                 │
│  This pattern is now part of the knowledge     │
│  base and will appear in future queries.       │
│                                                 │
│  [View Pattern]  [Continue Querying]           │
└─────────────────────────────────────────────────┘
```

**What Happens:**
1. Pattern is created with user as the validator
2. Pattern is immediately added to local search index
3. Pattern will appear in future queries
4. Pattern is marked with origin="llm_external_search"
5. User who accepted is recorded as validated_by

**Pattern Metadata:**
```json
{
  "id": "exframe_methods_027",
  "name": "LLM-Generated or User-Edited Name",
  "pattern_type": "knowledge",
  "status": "validated",  // Informational, not a gate
  "confidence": 0.84,
  "origin": "llm_external_search",
  "origin_query": "What is a pattern?",
  "data_sources": ["user-guide.md", "README.md"],
  "validated_by": "current_user_id",
  "validated_at": "2025-01-15T10:00:00Z",
  "validation_method": "query_portal_acceptance"
}
```

**Post-Creation State:**
- Confirmation message briefly displayed
- Pattern immediately searchable in future queries
- Pattern visible in Patterns tab
- Pattern marked with "External Search" origin
- No further certification needed

---

## Data Model Changes

### Simplified Pattern Schema

```javascript
{
  // Core identity
  "id": "exframe_methods_027",
  "name": "Pattern Name",
  "pattern_type": "knowledge",
  "domain": "exframe_methods",

  // Content
  "problem": "What is a pattern?",
  "solution": "LLM-generated + human-edited content",
  "description": "Brief description",

  // Quality signals
  "confidence": 0.84,
  "status": "validated",  // INFORMATIONAL ONLY - not a gate

  // Origin tracking
  "origin": "llm_external_search",  // "local" | "llm_external_search" | "human_created"
  "origin_query": "What is a pattern?",
  "data_sources": ["user-guide.md", "README.md"],

  // Validation tracking (informational)
  "validated_by": "user_123",
  "validated_at": "2025-01-15T10:00:00Z",
  "validation_method": "query_portal_acceptance",

  // Existing fields
  "created_at": "2025-01-15T10:00:00Z",
  "times_accessed": 0,
  "tags": ["external_search", "documentation"]
}
```

**Key Changes:**
- `status` is informational only, NOT a gate for inclusion in search
- `validated_by` records who accepted the pattern (not who "certified" it)
- `validation_method` tracks how it was created (query portal, bulk import, etc.)
- No "candidate" state - patterns are either created or not created

### Domain Config: Data Sources

```json
{
  "domain_id": "exframe_methods",
  "data_sources": {
    "type": "local_docs",
    "paths": ["/app/docs/*.md"],
    "exclude_paths": ["*.draft.md"],
    "max_results": 3,
    "fallback": {
      "type": "web_search",
      "max_results": 5
    }
  }
}
```

---

## Build Plan

### Phase 1: Foundation (Week 1-2)
**Goal:** Basic workflow without external search

**Tasks:**
1. Implement "fresh state" landing page
2. Add Submit Query button requirement (user confirmed)
3. Separate local results display from LLM results
4. Remove auto-LLM from initial query flow
5. Add "Extend Search" button to local results

**Deliverables:**
- Landing page always starts fresh
- Submit button required for all queries
- Local results show without LLM involvement
- Extend button available but optional

**Acceptance Criteria:**
- Query doesn't submit until button clicked
- Local results display < 500ms
- Extend button appears after local results
- No LLM called unless extend clicked

---

### Phase 2: External Search Integration (Week 3-4)
**Goal:** Connect LLM to domain-specific data sources

**Tasks:**
1. Add `data_sources` config to domain schema
2. Implement `local_docs` search strategy
3. Implement `web_search` fallback strategy
4. Update LLM prompts for external search
5. Add source attribution to responses

**Deliverables:**
- Domain config supports data source definition
- LLM searches configured sources
- Response shows which sources were used
- Fallback to web search if configured source unavailable

**Acceptance Criteria:**
- exframe_methods searches /app/docs/*.md
- Other domains search internet
- Response lists documentation files used
- Fallback works if docs unavailable

---

### Phase 3: Acceptance & Creation UI (Week 5-6)
**Goal:** Direct acceptance workflow (no intermediate state)

**Tasks:**
1. Implement "Accept as New Pattern" button
2. Add editable pattern details form (optional edit before creation)
3. Implement pattern creation endpoint
4. Update pattern schema with origin tracking
5. Add immediate inclusion in search index

**Deliverables:**
- Accept button appears after external search
- User can optionally edit pattern before creation
- Pattern created immediately upon acceptance
- Pattern immediately searchable in future queries

**Acceptance Criteria:**
- Accept button clearly visible
- Edit form is optional (can accept as-is)
- Pattern created < 1 second after acceptance
- Pattern appears in subsequent queries

---

### Phase 4: Polish & Testing (Week 7-8)
**Goal:** Production-ready implementation

**Tasks:**
1. End-to-end testing with real domains
2. Performance optimization (< 3s external search)
3. Error handling (source unavailable, LLM failure)
4. Documentation updates
5. User training materials

**Deliverables:**
- Full workflow tested across domains
- Performance benchmarks met
- Error states handled gracefully
- Complete documentation
- Training guide for users

**Acceptance Criteria:**
- All domains working with their data sources
- External search < 3 seconds
- Graceful degradation on errors
- Documentation complete
- Training materials delivered

---

## Open Questions for Discussion

### Q1: Multiple Extension Rounds
**Question:** Can user extend search multiple times for same query?

**Options:**
- A) Only one extension per query (simpler)
- B) Allow multiple extensions (more comprehensive)

**Impact:** UI complexity, state management

**DECISION:** Option A - Only one extension per query (simpler) 
---

### Q2: Concurrent Query Sessions
**Question:** Should user be able to have multiple queries active simultaneously?

**Options:**
- A) Single query session (simpler, focused)
- B) Multiple tabs/sessions (more power user)

**Impact:** UI complexity, state management

**DECISION:** Option A - Single query session (simpler, focused)
---

### Q3: Bulk Pattern Operations
**Question:** How does this interact with bulk pattern creation/management?

**Considerations:**
- Bulk create from external sources
- Import/export of patterns
- Batch operations from admin interface

**DECISION:** Query portal is single-pattern workflow. Bulk operations are separate admin feature (later phase).
---

### Q4: Confidence Boost Formula
**Question:** Is `local_confidence + 0.01` the right formula?

**Options:**
- A) Fixed boost (simple, predictable)
- B) Percentage boost (scales with confidence)
- C) No boost (use local confidence as-is)

**Impact:** Pattern quality signals, search ranking

**DECISION:** Option A - Fixed boost (+0.01 for simplicity, evaluate after real-world usage)
---

### Q5: User Roles & Permissions
**Question:** Who can create patterns through query portal?

**Options:**
- A) Any authenticated user (most open)
- B) Domain-approved users only (more controlled)
- C) Admin only (most restrictive)

**Impact:** Knowledge quality, community contribution

**DECISION:** Option A - Any authenticated user can create patterns (monitor quality, adjust if needed)
---

### Q6: Scale Considerations
**Question:** How does this work at scale?

**Considerations:**
- Multiple users creating patterns simultaneously
- Pattern count growth over time
- Search performance with many patterns
- Duplicate pattern detection

**DECISION:** Defer scale discussion until after base workflow is implemented and tested.
---

## Success Metrics

**DECISION:** Defer complex metrics for initial implementation. Track only essential metrics below.

### Essential Metrics (Phase 1-4)
- Local query response time (target: < 500ms)
- External search response time (target: < 3 seconds)
- Pattern creation success rate (basic tracking)

### Deferred Metrics (Future Phase)
- Query submission rate baseline
- Extend search usage rate
- Pattern creation rate
- Average confidence of created patterns
- User satisfaction scores
- Pattern edit rate before acceptance
- New patterns per domain per week
- Domain coverage growth rate

**Rationale:** Focus on getting the workflow working correctly before adding analytics complexity.

---

## Risks & Mitigations

### Risk 1: Low Adoption of Extend Feature
**Mitigation:** Make button prominent, show value in sample queries

### Risk 2: Pattern Quality Concerns
**Mitigation:** User acceptance IS validation, optional editing before creation, easy deletion

### Risk 3: External Search Unreliable
**Mitigation:** Fallback strategies, error handling, source diversity

### Risk 4: Duplicate Patterns
**Mitigation:** Check for similar patterns before creation, suggest viewing existing

### Risk 5: User Resistance to Workflow Changes
**Mitigation:** Gradual rollout, clear documentation, highlight benefits

---

## Dependencies

### Technical Dependencies
- Document research strategy (existing)
- LLM API integration (existing)
- Pattern storage system (existing)
- User authentication system (existing)

### Domain Dependencies
- Domain config updates (data_sources field)
- Documentation file availability
- Internet connectivity for web search domains

### External Dependencies
- LLM API reliability
- Web search API availability
- Documentation file maintenance

---

## Non-Goals (Explicitly Out of Scope)

1. **Candidate/Certified workflow** - User acceptance IS the certification
2. **Multi-step approval process** - Direct creation upon acceptance
3. **Real-time collaboration** - Single user session only
4. **Multi-domain queries** - One domain per query
5. **Social features** - Comments, voting, sharing (later phase)
6. **Analytics dashboards** - Usage metrics later phase
7. **Mobile apps** - Web interface only for now
8. **API access** - UI-driven workflow only

---

## Glossary

- **Knowledge Dashboard:** The query interface where human experts accept AI-generated knowledge
- **Local Search:** Search of existing patterns in the domain's knowledge base
- **External Search:** LLM-powered search of domain-specific data sources (docs, web)
- **Pattern Acceptance:** User decision to add external search results to knowledge base
- **Responsible Agent:** Human domain expert who accepts knowledge into the system
- **Origin:** Where the pattern came from (local, external search, human-created)
- **Validation Method:** How the pattern was created (query portal, bulk import, etc.)

---

## Next Steps

1. **Review this specification** - Confirm simplified model matches vision
2. **Discuss open questions** - Make decisions on Q1-Q6
3. **Discuss scale considerations** - Separate conversation about scale
4. **Approve Phase 1** - Begin implementation once aligned
5. **Establish review cadence** - Weekly check-ins during implementation

---

**Document Status:** APPROVED - Phase 1 Implementation Started
**Last Updated:** 2026-01-15
**Decisions Made:** All Q1-Q6 resolved, metrics simplified
**Next Milestone:** Phase 1 Foundation (Week 1-2)
