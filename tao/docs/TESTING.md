# Tao Testing Guide

Comprehensive testing guide for the Tao (Knowledge Cartography) subsystem.

---

## Quick Test Checklist

### ✅ Backend Tests

**1. Module Imports**
```bash
python3 -c "from tao.storage import get_kcart, load_history; print('✓ Storage OK')"
python3 -c "from tao.analysis import sessions, chains, concepts; print('✓ Analysis OK')"
python3 -c "from tao import sessions, concepts, load_history; print('✓ Top-level OK')"
```

**2. API Endpoints**
```bash
# Sessions
curl http://localhost:3000/api/tao/sessions/exframe | jq

# Concepts
curl http://localhost:3000/api/tao/concepts/exframe | jq

# Depth
curl http://localhost:3000/api/tao/depth/exframe | jq

# History
curl http://localhost:3000/api/tao/history/exframe | jq '.[0]'

# Chain (replace 1 with actual entry ID)
curl http://localhost:3000/api/tao/chains/exframe/1 | jq

# Related (replace 1 with actual entry ID)
curl http://localhost:3000/api/tao/related/exframe/1 | jq
```

**3. Analysis Modules**
```python
from tao.storage import load_history
from tao.analysis import sessions, concepts, depth

history = load_history('exframe')
print(f"✓ Loaded {len(history)} entries")

# Test sessions
session_list = sessions.find_sessions(history, gap_minutes=30)
print(f"✓ Found {len(session_list)} sessions")

# Test concepts
top_concepts = concepts.get_top_concepts(history, top_n=5)
print(f"✓ Found {len(top_concepts)} concepts")

# Test depth
explorations = depth.find_deep_explorations(history, min_depth=2)
print(f"✓ Found {len(explorations)} deep explorations")
```

### ✅ Frontend Tests

**1. Web UI Access**
- Visit: http://localhost:3000/tao
- ✓ Page loads without errors
- ✓ Domain selector shows domains
- ✓ All 3 tabs are visible (Sessions, Concepts, Depth)

**2. Sessions Tab**
- ✓ Sessions load and display
- ✓ Click "▶ View" expands query details
- ✓ Full query and response visible
- ✓ Metadata shown (source, confidence)
- ✓ Click "▼ Hide" collapses details
- ✓ Click "View Chain" opens modal
- ✓ Click "Find Related" opens modal

**3. Concepts Tab**
- ✓ Concepts load and display
- ✓ Frequency counts visible
- ✓ First/last seen timestamps shown
- ✓ Grid layout works

**4. Depth Tab**
- ✓ Deep explorations load
- ✓ Query counts shown
- ✓ Duration visible
- ✓ Top concepts listed
- ✓ Queries expandable

**5. Modals**
- ✓ Chain modal opens with timeline view
- ✓ Before/target/after sections visible
- ✓ Color coding works (blue/green/purple)
- ✓ Click outside closes modal
- ✓ Escape key closes modal
- ✓ Related modal shows similarity scores
- ✓ Strategy badges visible (temporal/pattern/keyword)
- ✓ "View Chain" button in related modal works

### ✅ Integration Tests

**1. ExFrame → Tao Integration**
- Go to http://localhost:3000/ (ExFrame)
- Submit a query in any domain
- Go to http://localhost:3000/tao
- ✓ Query appears in Sessions tab
- ✓ New concepts extracted
- ✓ Full Q/R accessible via "View" button

**2. Navigation**
- From ExFrame, click "Analysis" link
- ✓ Navigates to Tao interface
- From Tao, click "← Back to Query Interface"
- ✓ Returns to ExFrame

---

## Detailed Testing Scenarios

### Scenario 1: First Time User

**Setup:** Empty domain with no query history

**Test Steps:**
1. Visit Tao interface
2. Select empty domain from dropdown
3. **Expected:** All tabs show "No data" messages
4. Go to ExFrame and submit 3-5 queries
5. Return to Tao
6. **Expected:** Data appears in all tabs

**Validation:**
- Sessions tab shows at least 1 session
- Concepts tab shows extracted keywords
- Depth tab may or may not show (depends on timing)

---

### Scenario 2: Session Exploration

**Setup:** Domain with multiple query sessions

**Test Steps:**
1. Go to Sessions tab
2. Find session with multiple queries
3. Click "View" on first query
4. **Expected:** Query expands inline
5. Verify full query text visible
6. Verify response is markdown-rendered
7. Verify metadata visible
8. Click "View Chain" button
9. **Expected:** Modal opens with timeline
10. Verify before/target/after sections
11. Close modal (Escape or click outside)
12. Click "Find Related" button
13. **Expected:** Related modal opens
14. Verify related queries with scores
15. Click "View Chain" on related query
16. **Expected:** First modal closes, new chain modal opens

**Validation:**
- Inline expansion works smoothly
- Modals display correctly
- Navigation between modals works
- No console errors

---

### Scenario 3: Concept Discovery

**Setup:** Domain with rich query history

**Test Steps:**
1. Go to Concepts tab
2. Note top 3 concepts
3. Go to ExFrame
4. Submit query containing top concept
5. Return to Tao Concepts tab
6. **Expected:** Concept frequency increased by 1
7. **Expected:** "Last seen" timestamp updated

**Validation:**
- Real-time updates work
- Frequency counts accurate
- Timestamps update correctly

---

### Scenario 4: Deep Exploration Tracking

**Setup:** Empty session

**Test Steps:**
1. Go to ExFrame
2. Submit 3+ related queries within 5 minutes
3. Go to Tao Depth tab
4. **Expected:** New deep exploration appears
5. Verify query count matches
6. Verify duration is accurate
7. Verify top concepts extracted

**Validation:**
- Depth detection works
- Time gap threshold respected
- Concept extraction accurate

---

## Performance Testing

### Load Testing

**Test API response times:**
```bash
# Test sessions endpoint
time curl -s http://localhost:3000/api/tao/sessions/exframe > /dev/null

# Test concepts endpoint
time curl -s http://localhost:3000/api/tao/concepts/exframe > /dev/null

# Test history endpoint
time curl -s http://localhost:3000/api/tao/history/exframe > /dev/null
```

**Expected:** All endpoints < 500ms for domains with < 1000 entries

**Large Dataset Test:**
- Domain with 1000+ query entries
- **Expected:** UI remains responsive
- **Expected:** API calls complete in < 2s

---

## Error Handling Testing

### Test Invalid Inputs

**1. Invalid Domain**
```bash
curl http://localhost:3000/api/tao/sessions/nonexistent_domain
# Expected: [] (empty array, not 404)
```

**2. Invalid Entry ID**
```bash
curl http://localhost:3000/api/tao/chains/exframe/99999
# Expected: 404 with error message
```

**3. Invalid Parameters**
```bash
curl http://localhost:3000/api/tao/sessions/exframe?gap_minutes=-10
# Expected: Handles gracefully or returns error
```

### Frontend Error Handling

**1. Network Error Simulation**
- Stop Docker container
- Refresh Tao page
- **Expected:** Error message displayed
- **Expected:** No console crashes

**2. Empty Data Handling**
- Select domain with no history
- **Expected:** "No data" messages in all tabs
- **Expected:** No JavaScript errors

---

## Browser Compatibility

### Test Browsers

- ✓ Chrome/Chromium (primary)
- ✓ Firefox
- ✓ Safari (if available)
- ✓ Edge

### Test Responsive Design

- ✓ Desktop (1920x1080)
- ✓ Laptop (1366x768)
- ✓ Tablet (768x1024)
- ✓ Mobile (375x667)

---

## Regression Testing

### After Code Changes

Run this checklist after any code modifications:

1. **Module imports still work**
   ```bash
   python3 -c "from tao import *; print('OK')"
   ```

2. **API endpoints still respond**
   ```bash
   curl http://localhost:3000/api/tao/sessions/exframe | jq length
   ```

3. **Frontend loads without errors**
   - Open browser console
   - Visit http://localhost:3000/tao
   - Check for errors (should be none)

4. **ExFrame integration works**
   - Submit query in ExFrame
   - Verify appears in Tao

5. **Modals still work**
   - Open chain modal
   - Open related modal
   - Both should display correctly

---

## Common Issues & Solutions

### Issue: "No domains in selector"

**Cause:** API returning unexpected format
**Fix:** Check `/api/domains` returns `{domains: [...]}`
**Test:** `curl http://localhost:3000/api/domains | jq`

### Issue: "Depth tab always empty"

**Cause:** Time gap too restrictive
**Fix:** Lower `time_gap` parameter
**Test:** `curl http://localhost:3000/api/tao/depth/exframe?time_gap=60`

### Issue: "Modal not closing"

**Cause:** JavaScript error or Alpine.js issue
**Fix:** Check browser console for errors
**Test:** Press Escape key, should close

### Issue: "Query details not expanding"

**Cause:** Missing full history data
**Fix:** Verify `/api/tao/history/{domain}` works
**Test:** `curl http://localhost:3000/api/tao/history/exframe`

---

## Automated Testing (Future)

### Unit Tests (To Be Implemented)

```python
# tests/test_storage.py
def test_load_history():
    history = load_history('test_domain')
    assert isinstance(history, list)

# tests/test_sessions.py
def test_find_sessions():
    sessions = sessions.find_sessions(mock_history, 30)
    assert len(sessions) > 0
```

### Integration Tests (To Be Implemented)

```python
# tests/test_api.py
def test_sessions_endpoint(client):
    response = client.get('/api/tao/sessions/exframe')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

## Test Data Generation

### Create Test Query History

```python
from tao.storage import KnowledgeCartography

kcart = KnowledgeCartography('test_domain')

# Generate test queries
for i in range(10):
    kcart.save_query_response(
        query=f"Test query {i}",
        response=f"Test response {i}",
        metadata={'source': 'test', 'confidence': 0.9}
    )
```

---

## Monitoring in Production

### Health Checks

```bash
# Check API is responsive
curl http://localhost:3000/api/tao/sessions/exframe

# Check frontend is accessible
curl -I http://localhost:3000/tao
```

### Metrics to Track

- API response times (< 500ms target)
- Query history file sizes (compression working)
- Number of sessions per domain
- Concept extraction accuracy
- Modal open/close events

---

## Testing Checklist Summary

Before marking Tao as "production ready":

- [ ] All module imports work
- [ ] All 8 API endpoints return valid data
- [ ] Web UI loads without errors
- [ ] All 3 tabs display data
- [ ] Query detail expansion works
- [ ] Chain modal displays correctly
- [ ] Related modal displays correctly
- [ ] ExFrame → Tao integration works
- [ ] Navigation between interfaces works
- [ ] Responsive design tested
- [ ] Error handling tested
- [ ] Performance acceptable (< 500ms)
- [ ] No console errors
- [ ] Documentation complete

---

**Last Updated:** February 2026
**Version:** 2.0.0 (Phase 2a)
