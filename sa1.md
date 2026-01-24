# SA-1: Embeddings.py Smart Truncation Fix

**Date**: 2026-01-24  
**Component**: `generic_framework/core/embeddings.py`  
**Severity**: Medium (requires embedding regeneration)  
**Status**: PENDING

---

## Overview

This document outlines the procedure for applying a fix to the `encode_pattern()` method in the `EmbeddingService` class. The fix improves semantic diversity when truncating patterns that exceed the 256-token limit by implementing a smart truncation strategy with multiple fallback options.

---

## Change Summary

### Modified File
- `generic_framework/core/embeddings.py` (lines 143-172)

### What Changes
- **Before**: Simple truncation - keep name + solution (truncated to 1500 chars)
- **After**: Smart truncation with priority-based field inclusion:
  1. Priority 1: name + solution (800 chars) + description (200 chars)
  2. Priority 2: name + solution (800 chars) + problem (200 chars)
  3. Priority 3: name + solution (1000 chars)

### Why This Matters
- Improves semantic diversity between pattern embeddings
- Better search results due to richer context in embeddings
- More intelligent use of available token budget

---

## Pre-Implementation Checklist

### Environment Preparation
- [ ] Verify current system is running and healthy
  ```bash
  docker compose ps
  ```
- [ ] Note current application version
  ```bash
  curl http://localhost:3000/health
  ```
- [ ] Backup existing embeddings for all domains
  ```bash
  # For each domain in universes/MINE/domains/
  cp {domain}/embeddings.json {domain}/embeddings.json.backup
  ```

### Code Review
- [ ] Review the diff between `embeddings.py` and `fix_embeddings.py`
- [ ] Verify the smart truncation logic is correct
- [ ] Confirm token estimation approach is acceptable
- [ ] Check for any edge cases or potential issues

### Testing Plan
- [ ] Identify test domains to use for validation
- [ ] Prepare test queries for each domain
- [ ] Document expected search behavior before fix

---

## Implementation Checklist

### Step 1: Apply the Fix
- [ ] Stop the application
  ```bash
  docker compose down
  ```
- [ ] Backup original `embeddings.py`
  ```bash
  cp generic_framework/core/embeddings.py generic_framework/core/embeddings.py.backup
  ```
- [ ] Apply the fix (replace lines 143-172 with smart truncation logic)
- [ ] Verify the changes are correct
  ```bash
  diff generic_framework/core/embeddings.py.backup generic_framework/core/embeddings.py
  ```

### Step 2: Rebuild from Scratch
- [ ] Clean up Docker containers and images
  ```bash
  docker compose down
  docker system prune -f
  ```
- [ ] Rebuild the application image
  ```bash
  docker compose build --no-cache eeframe-app
  ```
- [ ] Start the application
  ```bash
  docker compose up -d
  ```
- [ ] Verify containers are running
  ```bash
  docker compose ps
  ```
- [ ] Check application logs for errors
  ```bash
  docker compose logs eeframe-app | tail -50
  ```
- [ ] Verify health endpoint
  ```bash
  curl http://localhost:3000/health
  ```

### Step 3: Regenerate Embeddings
- [ ] List all active domains
  ```bash
  curl http://localhost:3000/api/domains
  ```
- [ ] For each domain, regenerate embeddings:
  ```bash
  # Example for cooking domain
  curl -X POST "http://localhost:3000/api/embeddings/generate?domain=cooking"
  
  # Repeat for each domain: cooking, python, first_aid, gardening, etc.
  ```
- [ ] Monitor embedding generation logs
  ```bash
  docker compose logs eeframe-app -f | grep EMBED
  ```
- [ ] Verify embeddings were generated successfully
  ```bash
  # Check embeddings.json exists and has content
  ls -lh universes/MINE/domains/*/embeddings.json
  ```

### Step 4: Testing
- [ ] Test search functionality for each domain
  ```bash
  # Example query test
  curl -X POST http://localhost:3000/api/query \
    -H "Content-Type: application/json" \
    -d '{"query": "your test query", "domain": "cooking"}'
  ```
- [ ] Verify semantic scores are reasonable (0-1 range)
- [ ] Check trace logs for truncation behavior
  ```bash
  docker compose logs eeframe-app | grep "Truncated"
  ```
- [ ] Compare search results with expected behavior
- [ ] Test edge cases:
  - [ ] Patterns with very long names
  - [ ] Patterns with very long solutions
  - [ ] Patterns with missing description/problem fields
  - [ ] Patterns that exactly hit token limit

### Step 5: Validation
- [ ] Verify no errors in application logs
  ```bash
  docker compose logs eeframe-app | grep -i error
  ```
- [ ] Check embedding status endpoint
  ```bash
  curl http://localhost:3000/api/embeddings/status
  ```
- [ ] Verify pattern counts match expectations
- [ ] Confirm search performance is acceptable
- [ ] Validate semantic diversity improvement (qualitative assessment)

---

## Post-Implementation Checklist

### Documentation
- [ ] Update CHANGELOG.md with fix details
- [ ] Document the change in release notes
- [ ] Update any relevant architecture documentation
- [ ] Create commit message describing the fix

### Commit and Push
- [ ] Stage the modified file
  ```bash
  git add generic_framework/core/embeddings.py
  ```
- [ ] Create commit with descriptive message
  ```bash
  git commit -m "fix: improve semantic diversity in pattern embedding truncation

- Implement smart truncation strategy with priority-based field inclusion
- Prioritize name + solution + description/problem when token limit exceeded
- Improves search result quality by preserving more semantic context

Fixes: SA-1
Related: embeddings.py smart truncation"
  ```
- [ ] Update CHANGELOG.md commit
  ```bash
  git add CHANGELOG.md
  git commit -m "docs: update CHANGELOG for SA-1 embeddings fix"
  ```
- [ ] Push changes to remote repository
  ```bash
  git push origin main
  ```

### Monitoring
- [ ] Monitor application logs for 24 hours after deployment
- [ ] Watch for any embedding-related errors
- [ ] Track search performance metrics
- [ ] Gather user feedback on search quality

---

## Rollback Plan

If issues are encountered after deployment:

### Immediate Rollback
- [ ] Stop the application
  ```bash
  docker compose down
  ```
- [ ] Restore original `embeddings.py`
  ```bash
  cp generic_framework/core/embeddings.py.backup generic_framework/core/embeddings.py
  ```
- [ ] Restore original embeddings
  ```bash
  # For each domain
  cp {domain}/embeddings.json.backup {domain}/embeddings.json
  ```
- [ ] Rebuild and restart
  ```bash
  docker compose build --no-cache eeframe-app
  docker compose up -d
  ```

### Verification
- [ ] Verify application is running
- [ ] Test search functionality
- [ ] Confirm behavior matches pre-fix state

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking change to existing embeddings | High | High | Regenerate all embeddings after fix |
| Search result inconsistency | Medium | Medium | Document change; treat as improvement |
| Token estimation inaccuracy | Low | Low | Same estimation as before; fix doesn't worsen it |
| Increased complexity | Low | Low | Code is well-commented; logic is straightforward |
| Empty field edge cases | Low | Low | Handled by conditional checks |

**Overall Risk**: MEDIUM

---

## Success Criteria

The fix is considered successful when:

1. ✅ All embeddings regenerated without errors
2. ✅ Search functionality works for all domains
3. ✅ Semantic scores are in expected range (0-1)
4. ✅ No errors in application logs
5. ✅ Search results show improved semantic diversity (qualitative)
6. ✅ Application performance is acceptable
7. ✅ Documentation updated and committed

---

## Notes

- The fix uses rough token estimation (`len(text) // 4`) which is acceptable for this use case
- The 256-token limit is a constraint of the all-MiniLM-L6-v2 model
- Smart truncation prioritizes description over problem for semantic diversity
- Fallback to name + solution ensures no patterns are lost

---

## References

- Original file: `generic_framework/core/embeddings.py`
- Fix file: `generic_framework/core/fix_embeddings.py`
- Related documentation: `rag-search-design.md`
- Architecture: `PLUGIN_ARCHITECTURE.md`

---

**End of SA-1 Checklist**
