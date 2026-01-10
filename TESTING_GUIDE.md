# EEFrame Consolidation - Testing Guide

**Date**: 2026-01-08  
**Purpose**: Verify all functionality after consolidation  
**Status**: Ready for testing

---

## Testing Overview

This guide provides comprehensive testing procedures to verify the consolidated EEFrame system is working correctly.

### Test Categories
1. **API Testing** - Verify all endpoints work
2. **Frontend Testing** - Verify all pages load and work
3. **Data Testing** - Verify all patterns are accessible
4. **Integration Testing** - Verify frontend ↔ API communication
5. **Performance Testing** - Verify system performance

---

## Prerequisites

### Required Tools
- `curl` or Postman for API testing
- Web browser for frontend testing
- Python 3.8+ for backend testing
- Node.js 16+ for frontend testing

### System Requirements
- Docker and Docker Compose (for deployment)
- 4GB RAM minimum
- 2GB disk space

### Setup

```bash
# 1. Navigate to project directory
cd /home/peter/development/eeframe

# 2. Verify data migration
ls -la data/patterns/
# Should show 7 directories: cooking, omv, first_aid, llm_consciousness, python, gardening, diy

# 3. Verify code consolidation
ls -la generic_framework/
# Should show: ingestion/, extraction/, knowledge_graph/ directories

# 4. Verify frontend consolidation
grep -c "Domains" frontend/src/App.jsx
# Should return: 1 (indicating Domains page is imported)
```

---

## API Testing

### 1. System Status

**Test**: Verify API is running

```bash
curl -X GET http://localhost:3001/api/v1/system/status
```

**Expected Response**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2026-01-08T15:17:29Z"
}
```

**Pass Criteria**: ✅ Status code 200, status = "ok"

### 2. List Patterns

**Test**: Verify all 72 patterns are accessible

```bash
curl -X GET http://localhost:3001/api/v1/patterns/
```

**Expected Response**:
```json
{
  "total": 72,
  "patterns": [
    {
      "id": "cooking_001",
      "name": "Mise en Place Setup",
      "domain": "cooking",
      ...
    },
    ...
  ]
}
```

**Pass Criteria**: ✅ Status code 200, total = 72

### 3. Filter Patterns by Domain

**Test**: Verify domain filtering works

```bash
# Test cooking domain
curl -X GET "http://localhost:3001/api/v1/patterns/?domain=cooking"

# Test omv domain
curl -X GET "http://localhost:3001/api/v1/patterns/?domain=omv"
```

**Expected Response**:
```json
{
  "total": 26,
  "domain": "cooking",
  "patterns": [...]
}
```

**Pass Criteria**: ✅ Status code 200, correct domain count

### 4. Get Specific Pattern

**Test**: Verify individual pattern retrieval

```bash
curl -X GET http://localhost:3001/api/v1/patterns/cooking_001
```

**Expected Response**:
```json
{
  "id": "cooking_001",
  "name": "Mise en Place Setup",
  "domain": "cooking",
  "pattern_type": "preparation",
  "description": "Prepare and organize all ingredients before cooking",
  ...
}
```

**Pass Criteria**: ✅ Status code 200, pattern data complete

### 5. Search Patterns

**Test**: Verify pattern search functionality

```bash
curl -X GET "http://localhost:3001/api/v1/patterns/search?q=knife"
```

**Expected Response**:
```json
{
  "query": "knife",
  "results": [
    {
      "id": "cooking_002",
      "name": "Knife Skills: Basic Cuts",
      ...
    }
  ]
}
```

**Pass Criteria**: ✅ Status code 200, relevant results returned

### 6. Create Pattern

**Test**: Verify pattern creation

```bash
curl -X POST http://localhost:3001/api/v1/patterns/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Pattern",
    "domain": "cooking",
    "pattern_type": "procedure",
    "description": "A test pattern",
    "problem": "Test problem",
    "solution": "Test solution",
    "steps": ["Step 1", "Step 2"]
  }'
```

**Expected Response**:
```json
{
  "id": "cooking_XXX",
  "name": "Test Pattern",
  "domain": "cooking",
  ...
}
```

**Pass Criteria**: ✅ Status code 201, pattern created with ID

### 7. Update Pattern

**Test**: Verify pattern update

```bash
curl -X PUT http://localhost:3001/api/v1/patterns/cooking_001 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Mise en Place Setup",
    "description": "Updated description"
  }'
```

**Expected Response**:
```json
{
  "id": "cooking_001",
  "name": "Updated Mise en Place Setup",
  ...
}
```

**Pass Criteria**: ✅ Status code 200, pattern updated

### 8. Delete Pattern

**Test**: Verify pattern deletion

```bash
curl -X DELETE http://localhost:3001/api/v1/patterns/cooking_XXX
```

**Expected Response**:
```json
{
  "message": "Pattern deleted successfully"
}
```

**Pass Criteria**: ✅ Status code 200, pattern deleted

### 9. Knowledge Graph

**Test**: Verify knowledge graph endpoints

```bash
# Get graph
curl -X GET http://localhost:3001/api/v1/knowledge/graph

# Get nodes
curl -X GET http://localhost:3001/api/v1/knowledge/graph/nodes

# Get edges
curl -X GET http://localhost:3001/api/v1/knowledge/graph/edges

# Get stats
curl -X GET http://localhost:3001/api/v1/knowledge/graph/stats
```

**Expected Response**:
```json
{
  "nodes": [...],
  "edges": [...],
  "stats": {
    "total_nodes": 72,
    "total_edges": 150,
    ...
  }
}
```

**Pass Criteria**: ✅ Status code 200, graph data returned

### 10. Ingestion Endpoints

**Test**: Verify ingestion endpoints

```bash
# Ingest from URL
curl -X POST http://localhost:3001/api/v1/ingestion/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/recipe",
    "domain": "cooking"
  }'

# Ingest from text
curl -X POST http://localhost:3001/api/v1/ingestion/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Recipe text here",
    "domain": "cooking"
  }'

# Get ingestion status
curl -X GET http://localhost:3001/api/v1/ingestion/status
```

**Expected Response**:
```json
{
  "status": "processing",
  "job_id": "job_123",
  "progress": 50
}
```

**Pass Criteria**: ✅ Status code 200, ingestion started

---

## Frontend Testing

### 1. Dashboard Page

**Test**: Verify dashboard loads

```
URL: http://localhost:3001/
```

**Verification**:
- [ ] Page loads without errors
- [ ] Dashboard displays correctly
- [ ] Navigation menu visible
- [ ] No console errors

### 2. Pattern Browser

**Test**: Verify pattern browser page

```
URL: http://localhost:3001/patterns
```

**Verification**:
- [ ] Page loads without errors
- [ ] All 72 patterns displayed
- [ ] Pagination works
- [ ] Search functionality works
- [ ] Filter by domain works
- [ ] No console errors

### 3. Create Pattern

**Test**: Verify pattern creation form

```
URL: http://localhost:3001/patterns/new
```

**Verification**:
- [ ] Form loads without errors
- [ ] All form fields present
- [ ] Form submission works
- [ ] Pattern created successfully
- [ ] Redirects to pattern detail
- [ ] No console errors

### 4. Pattern Detail

**Test**: Verify pattern detail page

```
URL: http://localhost:3001/patterns/cooking_001
```

**Verification**:
- [ ] Page loads without errors
- [ ] Pattern data displayed correctly
- [ ] Edit button works
- [ ] Delete button works
- [ ] Related patterns displayed
- [ ] No console errors

### 5. Ingestion Page

**Test**: Verify ingestion page

```
URL: http://localhost:3001/ingestion
```

**Verification**:
- [ ] Page loads without errors
- [ ] URL input field present
- [ ] Domain selector present
- [ ] Submit button works
- [ ] Ingestion starts successfully
- [ ] No console errors

### 6. Batch Ingestion

**Test**: Verify batch ingestion page

```
URL: http://localhost:3001/batch
```

**Verification**:
- [ ] Page loads without errors
- [ ] File upload works
- [ ] Domain selector present
- [ ] Submit button works
- [ ] Batch ingestion starts
- [ ] No console errors

### 7. Domain Management

**Test**: Verify domain management page

```
URL: http://localhost:3001/domains
```

**Verification**:
- [ ] Page loads without errors
- [ ] All domains listed
- [ ] Domain details displayed
- [ ] Create domain works
- [ ] Edit domain works
- [ ] Delete domain works
- [ ] No console errors

### 8. Assistant Page

**Test**: Verify AI assistant page

```
URL: http://localhost:3001/assistant
```

**Verification**:
- [ ] Page loads without errors
- [ ] Query input present
- [ ] Submit button works
- [ ] Response displayed
- [ ] No console errors

### 9. Knowledge Base

**Test**: Verify knowledge base page

```
URL: http://localhost:3001/knowledge
```

**Verification**:
- [ ] Page loads without errors
- [ ] Knowledge graph displayed
- [ ] Graph visualization works
- [ ] Node details displayed
- [ ] No console errors

### 10. Diagnostics

**Test**: Verify diagnostics page

```
URL: http://localhost:3001/diagnostics
```

**Verification**:
- [ ] Page loads without errors
- [ ] System status displayed
- [ ] Metrics displayed
- [ ] Logs displayed
- [ ] No console errors

### 11. Traces

**Test**: Verify traces page

```
URL: http://localhost:3001/traces
```

**Verification**:
- [ ] Page loads without errors
- [ ] Traces listed
- [ ] Trace details displayed
- [ ] Mermaid diagram displayed
- [ ] No console errors

---

## Data Testing

### 1. Pattern Count Verification

**Test**: Verify all 72 patterns are present

```bash
# Count patterns in each domain
for domain in cooking omv first_aid llm_consciousness python gardening diy; do
  count=$(jq 'length' data/patterns/$domain/patterns.json)
  echo "$domain: $count patterns"
done
```

**Expected Output**:
```
cooking: 26 patterns
omv: 24 patterns
first_aid: 8 patterns
llm_consciousness: 5 patterns
python: 4 patterns
gardening: 3 patterns
diy: 2 patterns
```

**Pass Criteria**: ✅ Total = 72 patterns

### 2. Pattern Data Integrity

**Test**: Verify pattern data structure

```bash
# Check pattern structure
jq '.[0] | keys' data/patterns/cooking/patterns.json
```

**Expected Keys**:
- id
- name
- domain
- pattern_type
- description
- problem
- solution
- steps
- related_patterns
- prerequisites
- alternatives
- confidence
- sources
- tags
- examples
- created_at
- updated_at

**Pass Criteria**: ✅ All required fields present

### 3. Domain Field Verification

**Test**: Verify all patterns have correct domain field

```bash
# Check domain fields
for domain in cooking omv first_aid llm_consciousness python gardening diy; do
  mismatches=$(jq --arg d "$domain" '.[] | select(.domain != $d) | .id' data/patterns/$domain/patterns.json | wc -l)
  echo "$domain: $mismatches mismatches"
done
```

**Expected Output**:
```
cooking: 0 mismatches
omv: 0 mismatches
first_aid: 0 mismatches
llm_consciousness: 0 mismatches
python: 0 mismatches
gardening: 0 mismatches
diy: 0 mismatches
```

**Pass Criteria**: ✅ All domains match

### 4. JSON Validity

**Test**: Verify all JSON files are valid

```bash
# Check JSON validity
for file in data/patterns/*/*.json; do
  if ! jq empty "$file" 2>/dev/null; then
    echo "Invalid JSON: $file"
  fi
done
```

**Expected Output**: No output (all files valid)

**Pass Criteria**: ✅ All JSON files valid

---

## Integration Testing

### 1. Frontend → API Communication

**Test**: Verify frontend can fetch patterns from API

```javascript
// In browser console
fetch('/api/v1/patterns/')
  .then(r => r.json())
  .then(d => console.log(`Fetched ${d.total} patterns`))
```

**Expected Output**: `Fetched 72 patterns`

**Pass Criteria**: ✅ Frontend can fetch data

### 2. Pattern Creation Flow

**Test**: Create pattern through frontend and verify in API

1. Go to `/patterns/new`
2. Fill in form with test data
3. Submit form
4. Verify pattern appears in `/patterns`
5. Verify pattern accessible via API

**Pass Criteria**: ✅ Pattern created and accessible

### 3. Search Integration

**Test**: Search through frontend and verify results

1. Go to `/patterns`
2. Enter search query
3. Verify results displayed
4. Verify results match API search

**Pass Criteria**: ✅ Search works end-to-end

### 4. Domain Filtering

**Test**: Filter patterns by domain

1. Go to `/patterns`
2. Select domain filter
3. Verify only patterns from selected domain displayed
4. Verify count matches API

**Pass Criteria**: ✅ Filtering works end-to-end

---

## Performance Testing

### 1. API Response Time

**Test**: Measure API response times

```bash
# Measure list patterns response time
time curl -s http://localhost:3001/api/v1/patterns/ > /dev/null

# Measure search response time
time curl -s "http://localhost:3001/api/v1/patterns/search?q=knife" > /dev/null
```

**Expected**: < 500ms for list, < 1000ms for search

**Pass Criteria**: ✅ Response times acceptable

### 2. Frontend Load Time

**Test**: Measure frontend page load times

```bash
# Using browser DevTools
# Open http://localhost:3001
# Check Network tab for total load time
```

**Expected**: < 3 seconds for initial load

**Pass Criteria**: ✅ Load time acceptable

### 3. Database Query Performance

**Test**: Verify database queries are efficient

```bash
# Check query logs
tail -f logs/database.log

# Look for slow queries (> 1 second)
```

**Expected**: No slow queries

**Pass Criteria**: ✅ All queries efficient

---

## Error Handling Testing

### 1. Invalid Pattern ID

**Test**: Verify error handling for invalid pattern ID

```bash
curl -X GET http://localhost:3001/api/v1/patterns/invalid_id
```

**Expected Response**:
```json
{
  "error": "Pattern not found",
  "status": 404
}
```

**Pass Criteria**: ✅ Status code 404, error message

### 2. Invalid Domain

**Test**: Verify error handling for invalid domain

```bash
curl -X GET "http://localhost:3001/api/v1/patterns/?domain=invalid"
```

**Expected Response**:
```json
{
  "total": 0,
  "patterns": []
}
```

**Pass Criteria**: ✅ Status code 200, empty results

### 3. Missing Required Fields

**Test**: Verify error handling for missing fields

```bash
curl -X POST http://localhost:3001/api/v1/patterns/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Pattern"
  }'
```

**Expected Response**:
```json
{
  "error": "Missing required fields: domain, pattern_type, description",
  "status": 400
}
```

**Pass Criteria**: ✅ Status code 400, error message

---

## Test Execution Checklist

### Pre-Testing
- [ ] System deployed and running
- [ ] All services started
- [ ] Database initialized
- [ ] Data migrated
- [ ] Frontend built

### API Testing
- [ ] System status test passed
- [ ] List patterns test passed
- [ ] Filter patterns test passed
- [ ] Get pattern test passed
- [ ] Search patterns test passed
- [ ] Create pattern test passed
- [ ] Update pattern test passed
- [ ] Delete pattern test passed
- [ ] Knowledge graph test passed
- [ ] Ingestion test passed

### Frontend Testing
- [ ] Dashboard loads
- [ ] Pattern browser loads
- [ ] Create pattern works
- [ ] Pattern detail works
- [ ] Ingestion page works
- [ ] Batch ingestion works
- [ ] Domain management works
- [ ] Assistant page works
- [ ] Knowledge base works
- [ ] Diagnostics works
- [ ] Traces works

### Data Testing
- [ ] Pattern count verified (72)
- [ ] Pattern structure verified
- [ ] Domain fields verified
- [ ] JSON validity verified

### Integration Testing
- [ ] Frontend ↔ API communication works
- [ ] Pattern creation flow works
- [ ] Search integration works
- [ ] Domain filtering works

### Performance Testing
- [ ] API response times acceptable
- [ ] Frontend load times acceptable
- [ ] Database queries efficient

### Error Handling
- [ ] Invalid pattern ID handled
- [ ] Invalid domain handled
- [ ] Missing fields handled

---

## Test Results Summary

| Test Category | Total Tests | Passed | Failed | Status |
|---------------|------------|--------|--------|--------|
| API Testing | 10 | | | |
| Frontend Testing | 11 | | | |
| Data Testing | 4 | | | |
| Integration Testing | 4 | | | |
| Performance Testing | 3 | | | |
| Error Handling | 3 | | | |
| **TOTAL** | **35** | | | |

---

## Sign-Off

**Tested By**: ___________________  
**Date**: ___________________  
**Status**: ☐ PASS ☐ FAIL  
**Notes**: ___________________

---

## Next Steps

If all tests pass:
1. ✅ System ready for production deployment
2. ✅ Update documentation
3. ✅ Deploy to production
4. ✅ Monitor system performance

If any tests fail:
1. ❌ Document failures
2. ❌ Investigate root causes
3. ❌ Fix issues
4. ❌ Re-run tests
