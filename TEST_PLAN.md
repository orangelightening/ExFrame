# ExFrame Comprehensive Test Plan

## Test Status: 🧪 IN PROGRESS

**Last Updated**: 2026-02-14
**Test Environment**: Docker Desktop, llama3.2 (3.2B), all-MiniLM-L6-v2 embeddings

---

## Testing Strategy

### Test Phases:
1. ✅ **Quick Smoke Tests** - Verify system is running
2. 🧪 **Core Functionality** - Test all primary features
3. 🔍 **Edge Cases** - Test boundary conditions
4. 🚀 **Performance** - Verify speed meets targets
5. 🐛 **Bug Verification** - Confirm known issues are fixed

---

## 1. Quick Smoke Tests (5 minutes)

| Test | Expected | Status | Notes |
|------|----------|--------|-------|
| Container starts | App ready in < 10s | ⬜ | |
| Web UI loads | http://localhost:3000 | ⬜ | |
| Domains list | Shows all domains | ⬜ | |
| Health check | /health returns 200 | ⬜ | |

**Commands:**
```bash
# Start system
docker-compose up -d

# Check health
curl http://localhost:3000/health

# Check logs
docker logs eeframe-app --tail 20
```

---

## 2. Core Functionality Tests

### 2.1 Journal Domain (peter) - Regular Entries

| Test | Query | Expected Response | Status | Actual Time |
|------|-------|-------------------|--------|-------------|
| Simple entry | "buy milk" | `[YYYY-MM-DD HH:MM:SS] buy milk` | ⬜ | |
| Multi-word | "pick up dry cleaning" | Timestamped echo | ⬜ | |
| Special chars | "Dave's birthday @ 3pm!" | Timestamped echo | ⬜ | |
| Very long | 200 char entry | Timestamped echo | ⬜ | |
| Empty query | "" | Error or rejection | ⬜ | |

**Expected Performance**: < 300ms per query

**Verification:**
- Check `domain_log.md` for entries
- Check `patterns.json` for auto-generated patterns
- Verify NO duplicates created

---

### 2.2 Journal Domain (peter) - Search Queries (**)

| Test | Query | Expected | Status | Actual Time |
|------|-------|----------|--------|-------------|
| Simple search | `** what did I buy?` | Finds "buy milk" | ⬜ | |
| Semantic match | `** when is the party?` | Finds birthday entry | ⬜ | |
| No results | `** quantum mechanics` | "No entries found" | ⬜ | |
| Fuzzy match | `** dry clean` | Finds "dry cleaning" | ⬜ | |

**Expected Performance**: < 500ms (includes semantic search)

**Verification:**
- Semantic search finds relevant entries (not just recent)
- Returns top 5 most relevant patterns
- Does NOT create new patterns (read-only)

---

### 2.3 Librarian Domain (exframe)

| Test | Query | Expected | Status |
|------|-------|----------|--------|
| Basic query | "What is ExFrame?" | Retrieves from patterns | ⬜ |
| Doc search | "architecture design" | Searches documents | ⬜ |
| No match | "quantum physics" | Generates answer | ⬜ |

**Expected Performance**: < 1s

---

### 2.4 Other Personas

| Persona | Domain | Test Query | Status |
|---------|--------|------------|--------|
| Poet | poetry_domain | "Write a haiku about code" | ⬜ |
| Generalist | python | "How to sort a list?" | ⬜ |
| Librarian | cooking | "How to make pasta?" | ⬜ |

---

## 3. Pattern Management

### 3.1 Pattern Autogeneration

| Test | Action | Expected | Status |
|------|--------|----------|--------|
| Journal entry | Make entry in peter | Pattern created in patterns.json | ⬜ |
| Embedding gen | Check embeddings.json | New embedding added | ⬜ |
| NO duplicates | Make same entry twice | Only 1 pattern created | 🐛 **KNOWN BUG** |
| Search skip | Use ** query | NO new pattern created | ⬜ |

**🐛 Known Issue**: Duplicate patterns being created (seen in analytics)

---

### 3.2 Pattern Search

| Test | Query | Expected | Status |
|------|-------|----------|--------|
| Semantic match | Query similar to pattern | Finds relevant pattern | ⬜ |
| Threshold | Very different query | Returns nothing or low score | ⬜ |
| Multi-match | Generic query | Returns top 5 | ⬜ |

---

## 4. Edge Cases

### 4.1 Boundary Conditions

| Test | Input | Expected Behavior | Status |
|------|-------|-------------------|--------|
| Very long query | 1000 chars | Handles gracefully | ⬜ |
| Unicode | "❤️🎉こんにちは" | Processes correctly | ⬜ |
| SQL injection | `'; DROP TABLE--` | Sanitized/rejected | ⬜ |
| Empty query | "" | Error message | ⬜ |
| Null bytes | Query with \0 | Handles safely | ⬜ |

---

### 4.2 Concurrent Access

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| Multiple queries | 3 queries in parallel | All succeed | ⬜ |
| Pattern gen race | 2 identical entries simultaneously | Only 1 pattern | ⬜ |

---

## 5. Performance Tests

### 5.1 Query Response Times

**Target**: < 300ms for journal, < 500ms for search

| Test | Target | Status | Actual |
|------|--------|--------|--------|
| Journal entry | < 300ms | ⬜ | |
| Search query (**) | < 500ms | ⬜ | |
| Librarian query | < 1s | ⬜ | |
| Pattern search | < 50ms | ⬜ | |

**Measurement**:
```bash
# Watch timing logs
docker logs -f eeframe-app | grep "⏱"
```

---

### 5.2 Embedding Performance

| Metric | Target | Status | Actual |
|--------|--------|--------|--------|
| Model load | < 1s | ✅ | 0.2s |
| Single encode | < 20ms | ✅ | ~11ms |
| Batch (28 patterns) | < 50ms | ✅ | ~30ms |

---

### 5.3 Load Test

| Test | Description | Expected | Status |
|------|-------------|----------|--------|
| 10 queries/sec | Sustained load | No degradation | ⬜ |
| 100 total queries | Sequential | Consistent timing | ⬜ |

---

## 6. Data Integrity

### 6.1 Persistence

| Test | Action | Expected | Status |
|------|--------|----------|--------|
| Container restart | Restart container | Patterns persist | ⬜ |
| Domain log | Verify domain_log.md | All entries logged | ⬜ |
| Embeddings | Check embeddings.json | All patterns have embeddings | ⬜ |

---

### 6.2 Data Consistency

| Test | Check | Expected | Status |
|------|-------|----------|--------|
| Pattern count | patterns.json vs embeddings.json | Counts match | ⬜ |
| No corruption | Load all patterns | Valid JSON | ⬜ |
| No duplicates | Run analytics | < 5% duplicate rate | 🐛 **FAILED** (peter has 5 exact dupes) |

---

## 7. Known Issues to Verify

### 🐛 Critical Bugs

| Issue | Description | Test | Status |
|-------|-------------|------|--------|
| Pattern duplicates | Exact duplicates in peter domain | Make same entry twice | ⬜ TODO |
| Cooking dupes | 955 duplicates in cooking | Run cleanup | ⬜ TODO |

---

## 8. Test Execution

### Phase 1: Smoke Tests (5 min)
```bash
# 1. Start system
docker-compose up -d

# 2. Check health
curl http://localhost:3000/health

# 3. Load UI
open http://localhost:3000

# 4. Check logs
docker logs eeframe-app --tail 20 | grep -E "Ready|Error"
```

### Phase 2: Core Tests (20 min)
1. Test peter domain (journal + search)
2. Test exframe domain (librarian)
3. Test pattern autogeneration
4. Verify embeddings

### Phase 3: Performance (10 min)
1. Run 10 queries, measure timing
2. Check analytics output
3. Verify < 300ms target

### Phase 4: Bug Verification (10 min)
1. Test duplicate creation
2. Run analytics to detect
3. Document findings

---

## Test Results Template

### Test Run: [Date]
**Tester**:
**Duration**:
**Build**:

#### Summary:
- Tests Passed: X/Y
- Critical Bugs: X
- Performance: ✅/❌

#### Issues Found:
1. [Issue description]
2. [Issue description]

#### Recommendations:
1. [Action item]
2. [Action item]

---

## Success Criteria

### Must Pass (Blocking):
- ✅ All core functionality working
- ✅ Performance < 300ms for journal queries
- ✅ No data corruption
- ✅ Container restarts safely

### Should Pass (Important):
- ⚠️ No duplicate pattern creation
- ⚠️ Search finds relevant results
- ⚠️ All personas working

### Nice to Have:
- Concurrent access works
- Load test passes
- Edge cases handled

---

## Next Steps After Testing

1. **Document all bugs** found during testing
2. **Prioritize fixes**: Critical → Important → Nice-to-have
3. **Fix duplicate pattern bug** (highest priority)
4. **Clean up cooking domain** duplicates
5. **Re-test** after fixes
6. **Production ready** checklist
