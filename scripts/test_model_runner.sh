#!/bin/bash
# Test Model Runner Connection and Performance

echo "=================================="
echo "Model Runner Diagnostics"
echo "=================================="
echo ""

HOST="model-runner.docker.internal:12434"

# 1. Test basic connectivity
echo "[1] Testing connectivity to $HOST..."
if curl -s --max-time 2 http://$HOST >/dev/null 2>&1; then
    echo "✓ Connection successful"
else
    echo "✗ Cannot connect to $HOST"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Is the model runner service running?"
    echo "  2. Check what's listening on port 12434:"
    echo "     netstat -tuln | grep 12434"
    echo "     lsof -i :12434"
    echo "  3. Try from within container:"
    echo "     docker exec eeframe-app curl http://model-runner.docker.internal:12434"
    exit 1
fi
echo ""

# 2. Test Ollama-style API
echo "[2] Checking for Ollama API..."
if curl -s --max-time 2 http://$HOST/api/tags >/dev/null 2>&1; then
    echo "✓ Ollama API detected"
    echo ""
    echo "Available models:"
    curl -s http://$HOST/api/tags | python3 -m json.tool | grep '"name"' || echo "  (could not parse)"
    echo ""
    echo "Currently loaded models:"
    curl -s http://$HOST/api/ps | python3 -m json.tool || echo "  (could not parse)"
else
    echo "✗ Not Ollama API (or not responding)"
fi
echo ""

# 3. Test OpenAI-compatible endpoint
echo "[3] Testing OpenAI-compatible endpoint..."
RESPONSE=$(curl -s --max-time 5 -X POST http://$HOST/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer not-needed" \
  -d '{
    "model": "ai/qwen3",
    "max_tokens": 50,
    "messages": [
      {"role": "user", "content": "Say hello"}
    ],
    "stream": false
  }' 2>&1)

if echo "$RESPONSE" | grep -q "choices\|content"; then
    echo "✓ OpenAI-compatible endpoint works"
    echo ""
    echo "Response preview:"
    echo "$RESPONSE" | python3 -m json.tool | head -20
else
    echo "✗ OpenAI-compatible endpoint failed"
    echo ""
    echo "Response:"
    echo "$RESPONSE"
fi
echo ""

# 4. Performance test
echo "[4] Performance test (if available)..."
if curl -s --max-time 2 http://$HOST >/dev/null 2>&1; then
    echo "Running 3 test queries to measure latency..."
    for i in 1 2 3; do
        echo -n "  Query $i: "
        START=$(date +%s%3N)
        curl -s --max-time 30 -X POST http://$HOST/engines/v1/chat/completions \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer not-needed" \
          -d '{
            "model": "ai/qwen3",
            "max_tokens": 20,
            "messages": [
              {"role": "user", "content": "test"}
            ],
            "stream": false
          }' >/dev/null 2>&1
        END=$(date +%s%3N)
        DURATION=$((END - START))
        echo "${DURATION}ms"
        sleep 1
    done
    echo ""
    echo "Note: First query may be slower (model loading)"
    echo "      Subsequent queries should be faster if keep_alive is set"
fi
echo ""

# 5. Check from within container
echo "[5] Testing from within eeframe-app container..."
docker exec eeframe-app curl -s --max-time 2 http://model-runner.docker.internal:12434/api/tags >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Container can reach model-runner"
else
    echo "✗ Container cannot reach model-runner"
    echo "  This is a Docker networking issue"
fi
echo ""

echo "=================================="
echo "Diagnostics Complete"
echo "=================================="
echo ""
echo "See DMR_API_REFERENCE.md for detailed API documentation"
echo "See PERFORMANCE_INVESTIGATION.md for performance tuning"
