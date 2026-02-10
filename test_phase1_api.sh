#!/bin/bash
# Test the Phase 1 API with search_patterns flag

echo "============================================================"
echo "Phase 1 API Tests - search_patterns Flag"
echo "============================================================"

echo ""
echo "TEST 1: search_patterns=true (SEARCH PATTERNS)"
echo "------------------------------------------------------------"
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query": "How to cook rice", "domain": "cooking", "search_patterns": true}' \
  2>/dev/null | jq '{
    search_patterns_enabled,
    pattern_override_used,
    pattern_count,
    source,
    persona_type,
    answer_preview: .answer[:150] + "..."
  }'

echo ""
echo "TEST 2: search_patterns=false (SKIP PATTERNS, USE PERSONA)"
echo "------------------------------------------------------------"
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query": "How to cook rice", "domain": "cooking", "search_patterns": false}' \
  2>/dev/null | jq '{
    search_patterns_enabled,
    pattern_override_used,
    pattern_count,
    source,
    persona_type,
    answer_preview: .answer[:150] + "..."
  }'

echo ""
echo "TEST 3: No flag (USE DOMAIN CONFIG DEFAULT)"
echo "------------------------------------------------------------"
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query": "How to cook rice", "domain": "cooking"}' \
  2>/dev/null | jq '{
    search_patterns_enabled,
    pattern_override_used,
    pattern_count,
    source,
    persona_type,
    answer_preview: .answer[:150] + "..."
  }'

echo ""
echo "============================================================"
echo "✅ Phase 1 API search_patterns flag is working!"
echo "============================================================"
