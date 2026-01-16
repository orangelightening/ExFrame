# Query System Rewrite - Implementation Todo List

**Project**: Knowledge Dashboard Query System
**Specification**: query-rewrite.md (v1.0)
**Timeline**: 8 weeks (4 phases)
**Status**: Ready to begin

---

## Phase 1: Foundation (Week 1-2)
**Goal**: Basic workflow without external search

### Landing Page & Query Initiation
- [ ] Implement fresh state landing page (always starts at top)
- [ ] Add domain dropdown with visual feedback
- [ ] Display pattern count and last update timestamp
- [ ] Implement sample query chips (click to populate, don't auto-submit)
- [ ] Add Submit Query button as primary CTA
- [ ] Add Enter key keyboard shortcut
- [ ] Add loading indicator on submit
- [ ] Ensure 2-3 second max response time for local results

### Local Results Display
- [ ] Separate local results from LLM results (no auto-LLM)
- [ ] Display formatted response from local patterns
- [ ] Show pattern count (e.g., "5 patterns found")
- [ ] Show confidence score (e.g., "83% Confidence")
- [ ] Show source validation status (e.g., "All sources validated by experts")
- [ ] Make pattern names clickable to view individual patterns
- [ ] Ensure results persist until new query submitted
- [ ] Add "Extend Search" button to local results

### Acceptance Criteria
- [ ] Query doesn't submit until button clicked
- [ ] Local results display in < 500ms
- [ ] Extend button appears after local results
- [ ] No LLM called unless extend clicked

---

## Phase 2: External Search Integration (Week 3-4)
**Goal**: Connect LLM to domain-specific data sources

### Domain Configuration
- [ ] Add `data_sources` config to domain schema
- [ ] Implement `local_docs` source type
- [ ] Implement `web_search` source type
- [ ] Implement `hybrid` source type
- [ ] Add fallback configuration
- [ ] Update exframe_methods domain config with local_docs
- [ ] Update other domains with web_search config

### LLM Integration
- [ ] Implement local_docs search strategy (search /app/docs/*.md)
- [ ] Implement web_search fallback strategy
- [ ] Update LLM prompts to use document names (not "Source X")
- [ ] Add source attribution to responses
- [ ] Add `_clean_pattern_text()` function to remove legacy Source X references
- [ ] Update research-enhanced prompt to use document filenames

### API & Backend
- [ ] Create `/api/query/confirm-llm` endpoint (already exists, verify works)
- [ ] Ensure confirmation data flows through pipeline correctly
- [ ] Add data source configuration loading
- [ ] Implement source-specific search logic

### Acceptance Criteria
- [ ] exframe_methods searches /app/docs/*.md
- [ ] Other domains search internet
- [ ] Response lists documentation files used
- [ ] Fallback works if docs unavailable
- [ ] No "Source X" references in LLM responses

---

## Phase 3: Acceptance & Creation UI (Week 5-6)
**Goal**: Direct acceptance workflow (no intermediate state)

### External Search Results Display
- [ ] Show extended search results clearly distinguished from local results
- [ ] Display source statistics (files searched, processing time)
- [ ] Show "AI-generated from external sources" label
- [ ] Don't show confidence score for external results (not relevant)
- [ ] Add "Accept as New Pattern" button
- [ ] Add "Discard" button

### Acceptance Flow
- [ ] Implement pattern acceptance confirmation UI
- [ ] Add optional editing form before pattern creation
- [ ] Implement editable pattern name field
- [ ] Show pattern preview (problem, solution, confidence)
- [ ] Add "View Pattern" button after creation
- [ ] Add "Continue Querying" button after creation

### Pattern Creation
- [ ] Create pattern immediately upon user acceptance
- [ ] Set `validated_by` to current user
- [ ] Set `validated_at` to current timestamp
- [ ] Set `validation_method` to "query_portal_acceptance"
- [ ] Set `origin` to "llm_external_search"
- [ ] Add `data_sources` array with searched sources
- [ ] Include pattern in local search index immediately
- [ ] Show confirmation message briefly
- [ ] Ensure pattern appears in subsequent queries

### Acceptance Criteria
- [ ] Accept button clearly visible after external search
- [ ] Edit form is optional (can accept as-is)
- [ ] Pattern created in < 1 second after acceptance
- [ ] Pattern appears in subsequent queries
- [ ] Pattern marked with "External Search" origin

---

## Phase 4: Polish & Testing (Week 7-8)
**Goal**: Production-ready implementation

### End-to-End Testing
- [ ] Test complete workflow with exframe_methods domain
- [ ] Test complete workflow with cooking domain (web search)
- [ ] Test with sample query "What is a pattern?"
- [ ] Test with sample query that has no local results
- [ ] Test with sample query that has high local confidence
- [ ] Test error conditions (docs unavailable, LLM failure)
- [ ] Test multiple rapid queries
- [ ] Test domain switching mid-query

### Performance Optimization
- [ ] Ensure local query response time < 500ms
- [ ] Ensure external search response time < 3 seconds
- [ ] Ensure pattern creation time < 1 second
- [ ] Add caching for frequently accessed patterns
- [ ] Optimize LLM prompt sizes to reduce token usage

### Error Handling
- [ ] Handle documentation files unavailable gracefully
- [ ] Handle LLM API failures gracefully
- [ ] Handle web search API failures gracefully
- [ ] Add user-friendly error messages
- [ ] Add retry logic with exponential backoff
- [ ] Add cancel button for long-running external searches

### Documentation
- [ ] Update user guide with new workflow
- [ ] Add screenshots of new UI flow
- [ ] Document domain configuration format
- [ ] Create training guide for users
- [ ] Update API documentation
- [ ] Document data source configuration options

### Acceptance Criteria
- [ ] All domains working with their data sources
- [ ] External search < 3 seconds
- [ ] Graceful degradation on errors
- [ ] Documentation complete
- [ ] Training materials delivered

---

## Open Questions (To Be Decided)

### Q1: Multiple Extension Rounds
- [ ] Decide: Only one extension per query (A) or Allow multiple extensions (B)?
- [ ] Document decision in query-rewrite.md

### Q2: Concurrent Query Sessions
- [ ] Decide: Single query session (A) or Multiple tabs/sessions (B)?
- [ ] Document decision in query-rewrite.md

### Q3: Bulk Pattern Operations
- [ ] Confirm: Query portal is single-pattern workflow only
- [ ] Bulk operations are separate admin feature (later phase)

### Q4: Confidence Boost Formula
- [ ] Decide: Fixed boost (A) or Percentage boost (B) or No boost (C)?
- [ ] Document decision in query-rewrite.md

### Q5: User Roles & Permissions
- [ ] Decide: Any authenticated user (A) or Domain-approved only (B) or Admin only (C)?
- [ ] Document decision in query-rewrite.md

### Q6: Scale Considerations (Separate Discussion)
- [ ] Multiple users creating patterns simultaneously
- [ ] Pattern count growth over time
- [ ] Search performance with many patterns
- [ ] Duplicate pattern detection
- [ ] Document scale strategy

---

## Success Metrics

### User Engagement
- [ ] Measure baseline query submission rate
- [ ] Target: Extend search usage rate 20-30% of queries
- [ ] Target: Pattern creation rate 5-10% of extended searches

### Quality Metrics
- [ ] Target: Average confidence of created patterns > 0.80
- [ ] Target: User satisfaction with extended results > 4.0/5.0
- [ ] Target: Pattern edit rate before acceptance < 30%

### Performance Metrics
- [ ] Target: Local query response time < 500ms
- [ ] Target: External search response time < 3 seconds
- [ ] Target: Pattern creation time < 1 second

### Knowledge Growth
- [ ] Target: New patterns per domain per week 5-10
- [ ] Measure: Domain coverage (pattern count) growth rate
- [ ] Measure: External search contribution to knowledge base

---

## Files to Modify

### Frontend
- [ ] `generic_framework/frontend/index.html`
  - Landing page (fresh state)
  - Submit Query button
  - Local results display
  - Extend Search button
  - External search results display
  - Accept as New Pattern button
  - Pattern creation confirmation UI
  - Remove modal confirmation (current implementation)

### Backend
- [ ] `generic_framework/assist/engine.py`
  - Confidence calculation (already moved before enrichers)
  - Remove duplicate LLM response logging
  - Update pattern creation to set validation fields

- [ ] `generic_framework/plugins/enrichers/llm_enricher.py`
  - Remove Source X references with `_clean_pattern_text()`
  - Update prompts to use pattern names
  - Update research-enhanced prompt for document names

- [ ] `generic_framework/api/app.py`
  - Verify `/api/query/confirm-llm` endpoint works correctly
  - Add pattern creation endpoint (if needed)

- [ ] `generic_framework/core/generic_domain.py`
  - Add data_sources configuration loading
  - Add data source fallback logic

### Data Model
- [ ] Update pattern schema with new fields:
  - `origin` (local | llm_external_search | human_created)
  - `validated_by` (user ID)
  - `validated_at` (timestamp)
  - `validation_method` (query_portal_acceptance, etc.)
  - `data_sources` (array of source names)

- [ ] Update domain schema with:
  - `data_sources` configuration object
  - `type` (local_docs | web_search | hybrid)
  - `paths` or URL patterns
  - `fallback` configuration

---

## Non-Goals (Explicitly Out of Scope)

- Candidate/Certified workflow (user acceptance IS the certification)
- Multi-step approval process (direct creation upon acceptance)
- Real-time collaboration (single user session only)
- Multi-domain queries (one domain per query)
- Social features (comments, voting, sharing - later phase)
- Analytics dashboards (usage metrics later phase)
- Mobile apps (web interface only for now)
- API access (UI-driven workflow only)

---

## Dependencies

### Existing (Already Working)
- Document research strategy (existing)
- LLM API integration (existing - GLM-4)
- Pattern storage system (existing)
- User authentication system (existing)
- `/api/query/confirm-llm` endpoint (already created)

### Need to Implement
- Domain data_sources configuration
- Domain-specific search strategies
- Source attribution in responses
- Pattern validation tracking fields
- Acceptance UI components

---

## Notes

- The `///PR` flag in documents indicates notes from Peter (user) that need review/discussion
- Obsidian vault set up at project root for convenient document access
- Multiple AI personas and consensus approach noted for future discussion (not for now)

---

**Status**: Ready to begin Phase 1 once user approves
**Next Step**: User reviews query-rewrite.md and provides feedback
**Timeline**: 8 weeks total across 4 phases
