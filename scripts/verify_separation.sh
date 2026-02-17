#!/bin/bash
#
# Verify Clean Architecture Separation
# Checks that BrainUse doesn't have spaghetti connections to ExFrame
#

echo "🔍 Verifying Architecture Separation..."
echo ""

FAILED=0

# Test 1: No imports from ExFrame generic_framework
echo "Test 1: Checking for ExFrame imports in BrainUse..."
if grep -r "from generic_framework" tao/vetting/ 2>/dev/null; then
    echo "❌ FAIL: Found imports from generic_framework"
    FAILED=1
else
    echo "✅ PASS: No imports from generic_framework"
fi
echo ""

# Test 2: No imports from ExFrame core
echo "Test 2: Checking for core imports in BrainUse..."
if grep -r "from.*core\." tao/vetting/*.py 2>/dev/null; then
    echo "❌ FAIL: Found imports from core"
    FAILED=1
else
    echo "✅ PASS: No imports from core"
fi
echo ""

# Test 3: No imports from ExFrame frontend
echo "Test 3: Checking for frontend imports in BrainUse..."
if grep -r "import.*frontend" tao/vetting/*.py 2>/dev/null; then
    echo "❌ FAIL: Found imports from frontend"
    FAILED=1
else
    echo "✅ PASS: No imports from frontend"
fi
echo ""

# Test 4: No imports from ExFrame assist
echo "Test 4: Checking for assist imports in BrainUse..."
if grep -r "from assist" tao/vetting/ 2>/dev/null; then
    echo "❌ FAIL: Found imports from assist"
    FAILED=1
else
    echo "✅ PASS: No imports from assist"
fi
echo ""

# Test 5: Verify module structure
echo "Test 5: Checking module structure..."
if [ -d "tao/vetting" ] && [ -f "tao/vetting/__init__.py" ] && [ -f "tao/vetting/api_router.py" ]; then
    echo "✅ PASS: Clean module structure"
else
    echo "❌ FAIL: Module structure incomplete"
    FAILED=1
fi
echo ""

# Test 6: Verify only allowed imports
echo "Test 6: Checking allowed imports (should only be Tao, FastAPI, Pydantic)..."
ALLOWED_IMPORTS=$(grep -h "^from " tao/vetting/*.py 2>/dev/null | grep -v "^from \." | sort -u)
DISALLOWED=$(echo "$ALLOWED_IMPORTS" | grep -v "tao\." | grep -v "fastapi" | grep -v "pydantic" | grep -v "typing" | grep -v "datetime" | grep -v "uuid" | grep -v "logging" | grep -v "numpy")

if [ -n "$DISALLOWED" ]; then
    echo "⚠️  WARNING: Found non-standard imports:"
    echo "$DISALLOWED"
else
    echo "✅ PASS: Only allowed imports (Tao, FastAPI, Pydantic, stdlib)"
fi
echo ""

# Test 7: Check frontend isolation
echo "Test 7: Checking frontend isolation..."
if [ -f "tao/vetting/frontend/index.html" ] && [ -f "tao/vetting/frontend/assets/brainuse.js" ]; then
    # Check for references to ExFrame frontend
    if grep -i "exframe\|generic" tao/vetting/frontend/index.html 2>/dev/null | grep -v "api/brainuse"; then
        echo "⚠️  WARNING: Found ExFrame references in BrainUse frontend"
    else
        echo "✅ PASS: Frontend is isolated"
    fi
else
    echo "❌ FAIL: Frontend files not found"
    FAILED=1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    echo "Architecture separation is clean!"
    echo ""
    echo "BrainUse is properly isolated:"
    echo "  - No imports from ExFrame"
    echo "  - Only depends on Tao (shared infrastructure)"
    echo "  - Self-contained frontend"
    echo "  - Clean API boundaries"
else
    echo "❌ SOME TESTS FAILED"
    echo "Check the output above for issues"
    echo ""
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit $FAILED
