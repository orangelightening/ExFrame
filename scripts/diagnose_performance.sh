#!/bin/bash
# Performance Diagnostic Script for ExFrame

echo "=================================="
echo "ExFrame Performance Diagnostics"
echo "=================================="
echo ""

# 1. Check if model-runner is accessible
echo "[1] Checking model-runner connectivity..."
if curl -s --max-time 2 http://model-runner.docker.internal:12434 >/dev/null 2>&1; then
    echo "✓ model-runner is accessible"
else
    echo "✗ model-runner is NOT accessible"
fi
echo ""

# 2. Check Docker container status
echo "[2] Checking Docker containers..."
docker ps --filter "name=eeframe" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 3. Check GPU availability (if nvidia-smi exists)
echo "[3] Checking GPU status..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader
else
    echo "✗ nvidia-smi not found (no GPU or drivers not installed)"
fi
echo ""

# 4. Check embedding model cache
echo "[4] Checking embedding model cache..."
if [ -d "$HOME/.cache/huggingface" ]; then
    echo "Cache directory: $HOME/.cache/huggingface"
    du -sh "$HOME/.cache/huggingface"
else
    echo "✗ No HuggingFace cache found at $HOME/.cache/huggingface"
fi
echo ""

# 5. Check if sentence-transformers is installed in container
echo "[5] Checking sentence-transformers in container..."
docker exec eeframe-app python3 -c "
try:
    from sentence_transformers import SentenceTransformer
    print('✓ sentence-transformers is installed')
except ImportError:
    print('✗ sentence-transformers NOT installed')
" 2>/dev/null || echo "✗ Could not check (container not running?)"
echo ""

# 6. Test embedding speed
echo "[6] Testing embedding generation speed..."
docker exec eeframe-app python3 -c "
import time
try:
    from generic_framework.core.embeddings import get_embedding_service

    service = get_embedding_service()
    if not service:
        print('✗ Embedding service not available')
        exit(1)

    # Test load time
    start = time.time()
    service.load_model()
    load_time = time.time() - start
    print(f'Model load time: {load_time:.2f}s')

    # Test encoding time
    start = time.time()
    emb = service.encode('test query for performance measurement')
    encode_time = (time.time() - start) * 1000
    print(f'Single encode time: {encode_time:.1f}ms')

    # Test batch encoding
    texts = ['query ' + str(i) for i in range(10)]
    start = time.time()
    embs = service.encode_batch(texts)
    batch_time = (time.time() - start) * 1000
    print(f'Batch encode (10 items): {batch_time:.1f}ms ({batch_time/10:.1f}ms per item)')

except Exception as e:
    print(f'✗ Error: {e}')
" 2>/dev/null || echo "✗ Could not test (container not running?)"
echo ""

# 7. Check model-runner model status (if Ollama)
echo "[7] Checking model-runner loaded models..."
curl -s http://model-runner.docker.internal:12434/api/ps 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "✗ Could not check (not Ollama or not accessible)"
echo ""

# 8. Check Docker volume sizes
echo "[8] Checking Docker volume sizes..."
docker volume ls --filter "name=eeframe" --format "table {{.Name}}\t{{.Size}}" 2>/dev/null
echo ""

echo "=================================="
echo "Diagnostics complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Review PERFORMANCE_INVESTIGATION.md for detailed analysis"
echo "  2. Run 'watch -n 1 nvidia-smi' in separate terminal for GPU monitoring"
echo "  3. Check model-runner logs: docker logs <model-runner-container>"
echo "  4. Add timing logs to query_processor.py for detailed profiling"
