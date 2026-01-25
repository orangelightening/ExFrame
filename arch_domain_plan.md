# Domain Archetype Implementation Plan

**Version:** 1.0
**Date:** 2026-01-24
**Status:** DRAFT
**Purpose:** Detailed plan for implementing the Domain Archetype system

---

## Overview

This plan breaks down the implementation of the Domain Archetype system into manageable phases with clear deliverables, dependencies, and testing strategies.

**Goal:** Enable template-based domain creation where users select an archetype and get a fully configured domain with predefined query → process → reply workflows.

**Success Metrics:**
- ✅ New domains can be created by selecting an archetype
- ✅ All 6 archetypes are fully functional
- ✅ Workflow state machines are explicit and testable
- ✅ TEST_ASSISTANT provides flexible test space
- ✅ No production domains assigned to TEST_ASSISTANT
- ✅ Existing domains migrated to archetype system

---

## Phase 1: Foundation (Week 1)

**Goal:** Core infrastructure for archetype system

### 1.1 Create Archetype Module

**Tasks:**
- [ ] Create `generic_framework/core/archetypes.py`
- [ ] Define `DomainArchetype` dataclass
- [ ] Define 6 archetype constants
- [ ] Create `ARCHETYPE_MAP` registry
- [ ] Add archetype validation logic
- [ ] Unit tests for archetype definitions

**Files:**
```
generic_framework/core/archetypes.py
generic_framework/tests/test_archetypes.py
```

**Deliverables:**
- Archetype module with all 6 archetypes defined
- Validation that archetype configs are correct
- Unit tests passing

### 1.2 Domain Config Extension

**Tasks:**
- [ ] Extend domain schema to include `archetype` field
- [ ] Add `archetype_config` section
- [ ] Create config migration script for existing domains
- [ ] Update domain loader to read archetype field
- [ ] Validate archetype-specific configs

**Files:**
```
generic_framework/core/domain.py (update)
generic_framework/core/generic_domain.py (update)
universes/MINE/domains/*/domain.json (migrate)
scripts/migrate_to_archetypes.py (new)
```

**Deliverables:**
- Domain schema supports archetype declaration
- Migration script converts existing domains
- All existing domains declare an archetype

**Testing:**
- [ ] Run migration script on test universe
- [ ] Verify all domains load correctly
- [ ] Test validation with invalid archetype

---

## Phase 2: TEST_ASSISTANT First (Week 1-2)

**Goal:** Implement TEST_ASSISTANT archetype first as proof-of-concept

**Rationale:** TEST_ASSISTANT has no production dependencies, so we can iterate quickly and use it to test the archetype system itself.

### 2.1 TestEnricher Implementation

**Tasks:**
- [ ] Create `generic_framework/plugins/enrichers/test_enricher.py`
- [ ] Implement test mode handlers
  - [ ] `echo` mode - return query unchanged
  - [ ] `llm_only` mode - direct LLM call
  - [ ] `llm_with_patterns` mode - LLM with pattern context
  - [ ] `error_simulation` mode - simulate errors
  - [ ] `delay_simulation` mode - add artificial delay
- [ ] Add interaction logging
- [ ] Add timing capture
- [ ] Add performance metrics

**Files:**
```
generic_framework/plugins/enrichers/test_enricher.py
```

**Deliverables:**
- TestEnricher with all test modes
- Comprehensive logging
- Timing and metrics capture

**Testing:**
- [ ] Test each mode individually
- [ ] Test mode switching
- [ ] Verify logging captures all interactions
- [ ] Test error simulation mode
- [ ] Test delay simulation

### 2.2 Test Specialist Implementation

**Tasks:**
- [ ] Create `generic_framework/plugins/test_specialist.py`
- [ ] Implement configurable test handlers
- [ ] Add test mode routing logic
- [ ] Support runtime mode switching via config
- [ ] Add handler registration (for custom modes)

**Files:**
```
generic_framework/plugins/test_specialist.py
```

**Deliverables:**
- TestSpecialist with mode routing
- Handler registration system
- Runtime mode switching

**Testing:**
- [ ] Test all standard modes
- [ ] Test mode switching between queries
- [ ] Test custom handler registration
- [ ] Test invalid mode handling

### 2.3 Test Domain Configuration

**Tasks:**
- [ ] Configure `test_93` with TEST_ASSISTANT archetype
- [ ] Configure `test_domain` with TEST_ASSISTANT archetype
- [ ] Set default test mode (start with "echo")
- [ ] Enable interaction logging
- [ ] Add test mode switcher to UI config

**Files:**
```
universes/MINE/domains/test_93/domain.json
universes/MINE/domains/test_domain/domain.json
```

**Deliverables:**
- Both test domains using TEST_ASSISTANT
- Configurable test modes
- Ready for testing

**Testing:**
- [ ] Query test_domain in "echo" mode
- [ ] Switch to "llm_only" mode and query again
- [ ] Test "error_simulation" mode
- [ ] Verify interaction logs are captured
- [ ] Test mode switching between queries
- [ ] Verify no production domains use TEST_ASSISTANT

### 2.4 UI Test Panel

**Tasks:**
- [ ] Add test panel component to UI
- [ ] Test mode selector dropdown
- [ ] Interaction log panel
- [ ] Performance metrics display
- [ ] Test controls (simulate error, set delay)
- [ ] "Clear logs" button
- [ ] Debug panel toggle

**Files:**
```
static/test-panel.js (new)
static/test-panel.css (new)
```

**Deliverables:**
- Functional test panel UI
- All controls working
- Real-time log display

**Testing:**
- [ ] Manual testing of all controls
- [ ] Verify log updates in real-time
- [ ] Test mode switching via UI
- [ ] Verify metrics are accurate
- [ ] Test clear logs function

---

## Phase 3: Workflow Engine (Week 2)

**Goal:** Implement explicit workflow state machines for query → process → reply

### 3.1 Workflow Engine Core

**Tasks:**
- [ ] Create `generic_framework/core/workflow.py`
- [ ] Define `WorkflowState` dataclass
- [ ] Define `WorkflowTransition` dataclass
- [ ] Create `WorkflowEngine` class
- [ ] Implement state machine executor
- [ ] Add state transition logging
- [ ] Add workflow visualization support

**Files:**
```
generic_framework/core/workflow.py
generic_framework/core/states.py
generic_framework/tests/test_workflow.py
```

**Deliverables:**
- Workflow engine core
- State machine executor
- State transition logging
- Unit tests

**Testing:**
- [ ] Test simple state machine (2 states)
- [ ] Test branching state machine
- [ ] Test error handling in transitions
- [ ] Test state transition logging
- [ ] Verify workflow visualization output

### 3.2 Archetype Workflow Definitions

**Tasks:**
- [ ] Define workflow for CREATIVE_GENERATOR
  - [ ] States: QUERY → CREATIVE_LLM → RESPONSE
- [ ] Define workflow for KNOWLEDGE_RETRIEVAL
  - [ ] States: QUERY → PATTERN_SEARCH → LLM_SYNTHESIS → RESPONSE
- [ ] Define workflow for DOCUMENT_STORE_SEARCH
  - [ ] States: QUERY → DOC_SEARCH → PATTERN_FALLBACK → RESPONSE
- [ ] Define workflow for ANALYTICAL_ENGINE
  - [ ] States: QUERY → RESEARCH_PLAN → DATA_GATHER → ANALYSIS → REPORT
- [ ] Define workflow for HYBRID_ASSISTANT
  - [ ] States: QUERY → PATTERN_SEARCH → CONFIDENCE_CHECK → (PATTERN_RESPONSE or OFFER_FALLBACK or LLM_FALLBACK)
- [ ] Define workflow for TEST_ASSISTANT
  - [ ] States: QUERY → TEST_DISPATCH → [various] → LOG → RESPONSE
- [ ] Add workflow definitions to archetypes
- [ ] Validate workflow definitions

**Files:**
```
generic_framework/core/archetypes.py (update - add workflows)
```

**Deliverables:**
- All 6 archetypes have workflow definitions
- Workflow validation passes
- Workflow visualization works

**Testing:**
- [ ] Trace a query through each archetype's workflow
- [ ] Verify state transitions match documentation
- [ ] Test all branches (e.g., HYBRID confidence high/low)
- [ ] Test error states in workflows
- [ ] Generate workflow diagrams for docs

### 3.3 Engine Integration

**Tasks:**
- [ ] Update `generic_framework/assist/engine.py`
- [ ] Pass workflow through query pipeline
- [ ] Log state transitions in trace output
- [ ] Support workflow-specific error handling
- [ ] Add workflow metadata to response

**Files:**
```
generic_framework/assist/engine.py (update)
```

**Deliverables:**
- Engine uses workflow engine
- All queries log state transitions
- Workflow metadata in API response

**Testing:**
- [ ] Query each archetype domain
- [ ] Verify workflow in trace output
- [ ] Test error handling per workflow
- [ ] Verify backward compatibility

---

## Phase 4: Domain CREATIVE_GENERATOR (Week 2-3)

**Goal:** Implement creative generator archetype

### 4.1 LLM Enricher Creative Mode

**Tasks:**
- [ ] Extend `LLMEnricher` with explicit creative mode
- [ ] Add `creative_mode: true` config option
- [ ] Implement creative query detection (already done)
- [ ] Add creative keyword list to config
- [ ] Document creative mode behavior

**Files:**
```
generic_framework/plugins/enrichers/llm_enricher.py (update)
```

**Deliverables:**
- Creative mode is explicit (not implicit)
- Configurable creative keywords
- Documentation updated

**Testing:**
- [ ] Test poetry domain with creative mode
- [ ] Verify patterns are ignored
- [ ] Test creative query detection
- [ ] Test temperature is high (0.7-0.9)

### 4.2 Poetry Domain Migration

**Tasks:**
- [ ] Add `archetype: "creative_generator"` to poetry domain
- [ ] Remove workaround code (if any)
- [ ] Set creative keywords in config
- [ ] Set temperature to 0.8
- [ ] Test poetry domain still works
- [ ] Remove any pattern-based workarounds

**Files:**
```
universes/MINE/domains/poetry_domain/domain.json
```

**Deliverables:**
- Poetry domain uses archetype system
- All functionality preserved
- Cleaner configuration

**Testing:**
- [ ] Query "write a haiku about autumn"
- [ ] Verify single response (no 3-part issue)
- [ ] Test various creative queries
- [ ] Verify patterns not shown
- [ ] Compare with previous behavior

---

## Phase 5: Domain KNOWLEDGE_RETRIEVAL (Week 3)

**Goal:** Implement knowledge retrieval archetype (most common)

### 5.1 Pattern Enhancement Mode

**Tasks:**
- [ ] Set standard temperature (0.3-0.5)
- [ ] Configure pattern display
- [ ] Add "Patterns referenced" section
- [ ] Ensure pattern cards are clickable
- [ ] Test pattern synthesis

**Files:**
```
generic_framework/plugins/formatters/markdown_formatter.py (update)
```

**Deliverables:**
- Standard knowledge retrieval behavior
- Patterns shown with LLM response
- Clickable pattern cards

**Testing:**
- [ ] Test cooking domain
- [ ] Verify patterns found
- [ ] Verify LLM synthesizes results
- [ ] Test "Patterns referenced" section
- [ ] Verify pattern cards clickable

### 5.2 Domain Migrations

**Tasks:**
- [ ] Migrate cooking domain to KNOWLEDGE_RETRIEVAL
- [ ] Migrate python domain
- [ ] Migrate first_aid domain
- [ ] Migrate gardening domain
- [ ] Migrate diy domain
- [ ] Migrate binary_symmetry domain

**Files:**
```
universes/MINE/domains/cooking/domain.json
universes/MINE/domains/python/domain.json
universes/MINE/domains/first_aid/domain.json
universes/MINE/domains/gardening/domain.json
universes/MINE/domains/diy/domain.json
universes/MINE/domains/binary_symmetry/domain.json
```

**Deliverables:**
- All knowledge domains use archetype
- Config consistent across domains
- Behavior preserved

**Testing:**
- [ ] Test each migrated domain
- [ ] Verify patterns are found
- [ ] Verify LLM enhancement works
- [ ] Compare with previous behavior

---

## Phase 6: Domain DOCUMENT_STORE_SEARCH (Week 3-4)

**Goal:** Implement document store search archetype

### 6.1 Verify ExFrame Domain

**Tasks:**
- [ ] Add `archetype: "document_store_search"` to exframe
- [ ] Verify workflow matches documentation
- [ ] Test document store integration
- [ ] Test research strategy
- [ ] Verify "Sources searched" appears
- [ ] Test reply capture

**Files:**
```
universes/MINE/domains/exframe/domain.json
```

**Deliverables:**
- ExFrame domain declares archetype
- Workflow verified
- All features working

**Testing:**
- [ ] Test exframe domain queries
- [ ] Verify doc store search happens first
- [ ] Verify patterns are fallback
- [ ] Test "Sources searched" section
- [ ] Test reply capture workflow

---

## Phase 7: Domain HYBRID_ASSISTANT (Week 4)

**Goal:** Implement hybrid assistant archetype

### 7.1 LLM Fallback Enhancement

**Tasks:**
- [ ] Verify LLMFallbackEnricher workflow
- [ ] Test confidence-based routing
- [ ] Test user confirmation flow
- [ ] Test "Extend search?" button
- [ ] Verify patterns shown first

**Files:**
```
generic_framework/plugins/enrichers/llm_enricher.py (verify)
```

**Deliverables:**
- HYBRID_ASSISTANT workflow working
- Confidence-based routing works
- User confirmation flow works

**Testing:**
- [ ] Test with high confidence patterns
- [ ] Test with low confidence patterns
- [ ] Verify confirmation appears
- [ ] Test accept/decline LLM
- [ ] Verify response assembly

---

## Phase 8: Domain ANALYTICAL_ENGINE (Week 4-5)

**Goal:** Implement analytical engine archetype (future-proofing)

### 8.1 Research Specialist

**Tasks:**
- [ ] Create `generic_framework/plugins/research_specialist.py`
- [ ] Implement task decomposition
- [ ] Implement multi-step orchestration
- [ ] Add progress tracking
- [ ] Implement report generation
- [ ] Add timeout handling

**Files:**
```
generic_framework/plugins/research_specialist.py
```

**Deliverables:**
- Research specialist implemented
- Multi-step queries supported
- Progress tracking works

**Testing:**
- [ ] Test simple research query
- [ ] Test multi-step decomposition
- [ ] Verify progress updates
- [ ] Test report generation
- [ ] Test timeout handling

### 8.2 LLM Consciousness Migration (Optional)

**Tasks:**
- [ ] Evaluate if llm_consciousness fits ANALYTICAL_ENGINE
- [ ] If yes, migrate to archetype
- [ ] If no, keep as KNOWLEDGE_RETRIEVAL
- [ ] Test either way

**Files:**
```
universes/MINE/domains/llm_consciousness/domain.json
```

**Deliverables:**
- llm_consciousness assigned to appropriate archetype
- Behavior verified

**Testing:**
- [ ] Test llm_consciousness queries
- [ ] Verify workflow matches archetype

---

## Phase 9: Domain Creation UI (Week 5)

**Goal:** UI for creating domains from archetypes

### 9.1 API Endpoint

**Tasks:**
- [ ] Create `POST /api/domains/create-from-archetype`
- [ ] Implement archetype validation
- [ ] Implement domain generation from archetype
- [ ] Add archetype list endpoint
- [ ] Add archetype detail endpoint

**Files:**
```
generic_framework/api/routes/domains.py (update)
```

**Deliverables:**
- Domain creation API working
- Archetype list API
- Archetype detail API

**Testing:**
- [ ] Test creating domain from each archetype
- [ ] Test validation (invalid archetype)
- [ ] Test custom config overrides
- [ ] Verify domain files created correctly

### 9.2 Frontend Domain Creator

**Tasks:**
- [ ] Create archetype selection UI
- [ ] Create archetype cards (one per archetype)
- [ ] Add domain configuration form
- [ ] Implement custom config overrides
- [ ] Add preview functionality
- [ ] Add create/confirm/cancel flow

**Files:**
```
static/domain-creator.js (new)
static/domain-creator.css (new)
static/archetype-cards.js (new)
```

**Deliverables:**
- Domain creator UI
- Archetype cards with descriptions
- Configuration form
- Preview functionality

**Testing:**
- [ ] Manual UI testing
- [ ] Test archetype selection
- [ ] Test form validation
- [ ] Test domain creation
- [ ] Verify created domain works

---

## Phase 10: Testing & Documentation (Week 5-6)

**Goal:** Comprehensive testing and documentation

### 10.1 Test Suite

**Tasks:**
- [ ] Create archetype integration tests
- [ ] Create workflow engine tests
- [ ] Create cross-archetype tests
- [ ] Create migration tests
- [ ] Create regression tests
- [ ] Add to CI/CD pipeline

**Files:**
```
tests/test_archetypes_integration.py
tests/test_workflows.py
tests/test_cross_archetype.py
tests/test_migrations.py
```

**Deliverables:**
- Comprehensive test suite
- CI/CD integration
- All tests passing

**Testing:**
- [ ] Run full test suite
- [ ] Fix any failing tests
- [ ] Verify test coverage >80%
- [ ] Document any test limitations

### 10.2 Documentation

**Tasks:**
- [ ] Update README with archetype system
- [ ] Create ARCHETYPE_USAGE.md guide
- [ ] Update PLUGIN_ARCHITECTURE.md
- [ ] Create workflow diagrams
- [ ] Add API documentation
- [ ] Create migration guide
- [ ] Add troubleshooting section

**Files:**
```
ARCHETYPE_USAGE.md (new)
README.md (update)
PLUGIN_ARCHITECTURE.md (update)
docs/architecture/archetypes.md (new)
docs/api/archetypes.md (new)
docs/guides/migration.md (new)
```

**Deliverables:**
- Complete documentation
- User guide for archetype selection
- Developer guide for creating archetypes
- Migration guide

**Testing:**
- [ ] Verify docs are complete
- [ ] Test following user guide
- [ ] Test following migration guide
- [ ] Verify API docs are accurate

---

## Phase 11: Validation & Polish (Week 6)

**Goal:** Final validation and polish

### 11.1 Cross-Archetype Validation

**Tasks:**
- [ ] Test all 6 archetypes with real queries
- [ ] Verify workflow state machines are correct
- [ ] Verify UI patterns match archetypes
- [ ] Performance test each archetype
- [ ] Load test system with all archetypes

**Testing Matrix:**
| Archetype | Test Queries | Success Criteria |
|-----------|-------------|------------------|
| CREATIVE_GENERATOR | "write a poem about X" | Clean LLM response, no patterns |
| KNOWLEDGE_RETRIEVAL | "how do I X?" | Patterns found + LLM synthesis |
| DOCUMENT_STORE_SEARCH | "what does X say?" | Doc search results + LLM |
| ANALYTICAL_ENGINE | "research X" | Multi-step report generated |
| HYBRID_ASSISTANT | "help with X" | Patterns or LLM based on confidence |
| TEST_ASSISTANT | "test query" | Configurable behavior verified |

### 11.2 Edge Cases

**Tasks:**
- [ ] Test empty pattern database
- [ ] Test LLM API failure scenarios
- [ ] Test document store unavailability
- [ ] Test concurrent queries
- [ ] Test domain switching mid-session
- [ ] Test invalid archetype configs

### 11.3 Performance

**Tasks:**
- [ ] Benchmark query latency per archetype
- [ ] Profile memory usage
- [ ] Optimize slow workflows
- [ ] Add caching where appropriate
- [ ] Document performance characteristics

---

## Deliverables Summary

### Code
- `generic_framework/core/archetypes.py` - Archetype definitions
- `generic_framework/core/workflow.py` - Workflow engine
- `generic_framework/plugins/test_specialist.py` - Test specialist
- `generic_framework/plugins/enrichers/test_enricher.py` - Test enricher
- Updates to existing files

### Configuration
- All `domain.json` files updated with archetype field
- Migration scripts for existing domains

### API
- `POST /api/domains/create-from-archetype`
- `GET /api/archetypes`
- `GET /api/archetypes/{archetype_id}`

### Frontend
- Domain creator UI
- Test panel UI
- Archetype selection cards

### Documentation
- `DOMAIN_ARCHETYPES.md` (already created)
- `ARCHETYPE_USAGE.md` - User guide
- Migration guide
- API documentation
- Architecture diagrams

---

## Dependencies

### Critical Path
```
Phase 1 (Foundation)
  → Phase 2 (TEST_ASSISTANT)
    → Phase 3 (Workflow Engine)
      → Phase 4-8 (Individual Archetypes)
        → Phase 9 (UI)
          → Phase 10 (Testing & Docs)
            → Phase 11 (Validation)
```

### Parallel Opportunities
- Phase 4-8 can run in parallel after Phase 3
- Documentation can be written alongside implementation
- Frontend can be developed while backend is in Phase 3

### Blocked By
- Phase 2-8 blocked by Phase 1
- Phase 9 blocked by Phase 1 (needs archetype definitions)
- Phase 10-11 blocked by all implementation phases

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Archetype migration breaks existing domains | High | Comprehensive testing, rollback plan |
| Workflow engine adds complexity | Medium | Keep simple initially, add features incrementally |
| TEST_ASSISTANT accidentally used in production | Medium | Validation prevents production domain assignment |
| Performance degradation with workflows | Low | Benchmark early, optimize hot paths |
| UI complexity with 6 archetypes | Medium | Reusable components, clear UX patterns |

---

## Rollback Plan

If critical issues arise:
1. **Phase 1-2**: Keep existing domains as-is, add archetype field optionally
2. **Phase 3-8**: Can revert individual phases independently
3. **Phase 9**: UI is additive, won't break existing functionality
4. **Phase 10-11**: Documentation can be updated incrementally

---

## Success Criteria

The implementation is successful when:
- ✅ All 6 archetypes are defined and functional
- ✅ Workflow engine manages query → reply flow
- ✅ TEST_ASSISTANT provides flexible test space
- ✅ No production domains use TEST_ASSISTANT
- ✅ New domains can be created from archetype templates
- ✅ Existing domains migrated to archetype system
- ✅ UI supports archetype selection
- ✅ All tests pass
- ✅ Documentation is complete

---

## Open Questions for Discussion

1. **Should archetypes be versioned?**
   - What if we need to change an archetype's workflow?
   - Migration path for domains using old version?

2. **Can a domain change archetypes?**
   - What happens to existing data?
   - How to handle incompatibilities?

3. **Custom archetypes?**
   - Should advanced users be able to create custom archetypes?
   - How to validate custom workflows?

4. **Archetype inheritance?**
   - Can we extend archetypes (e.g., CREATIVE + TECHNICAL)?
   - How to handle conflicting settings?

5. **Performance monitoring?**
   - Metrics per archetype?
   - Alerting on unusual behavior?

---

## Next Steps

1. **Review this plan** - Is it comprehensive? Reasonable?
2. **Prioritize phases** - What's most important first?
3. **Adjust timeline** - Are estimates realistic?
4. **Identify blockers** - What are we waiting on?
5. **Start implementation** - Begin with Phase 1

---

**Status**: DRAFT - Ready for discussion and refinement
