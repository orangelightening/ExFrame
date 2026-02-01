#!/bin/bash
# State Machine Test Runner
# Runs the state machine test suite and displays results

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "State Machine Test Suite"
echo "=========================================="
echo ""

# Check if API is available
if ! curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${RED}ERROR: API not available at http://localhost:3000${NC}"
    echo "Please ensure the application is running first."
    exit 1
fi

# Run tests inside the container
echo "Running tests..."
echo ""

docker exec eeframe-app python /app/tests/test_statemachine.py --output both

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed!${NC}"
fi

exit $TEST_EXIT_CODE
