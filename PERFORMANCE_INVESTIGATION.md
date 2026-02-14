# Performance Investigation Checklist

## Issue: High Latency in Semantic Search & Query Processing

### Symptoms
1. Slow embeddings AI loading
2. Slow query response times
3. Previous RAAG system was much faster

---

## 1. Model Runner (qwen3) Investigation

### Check Model Runner Status
- [ ] Is model-runner service running? `docker ps | grep model-runner`
- [ ] What's the actual service? (Ollama? vLLM? Custom?)
- [ ] Check model-runner logs
- [ ] What port is it listening on? (12434 confirmed in domain.json)

### JIT/Lazy Loading Settings
```bash
# If using Ollama:
curl http://model-runner.docker.internal:12434/api/tags
curl http://model-runner.docker.internal:12434/api/ps  # Check loaded models

# Check keep_alive setting (Ollama default: 5 minutes)
# Location: ~/.ollama/config.json or via API
```

**Question: Does model-runner unload models after each query?**
- Check `keep_alive` parameter
- Default Ollama: keeps model for 5 minutes
- Setting to -1 keeps it loaded permanently

### Commands to Check:
```bash
# Check if model-runner is Docker or host service
docker ps -a | grep model

# If Ollama on host:
curl http://localhost:12434/api/ps

# Check GPU usage while idle
nvidia-smi

# Check GPU usage during query
watch -n 1 nvidia-smi
```

---

## 2. Embedding Model (sentence-transformers) Investigation

### Current Status
- **Model**: all-MiniLM-L6-v2 (384-dim, ~80MB)
- **Loading**: Lazy (first query only)
- **Persistence**: Singleton pattern - should stay loaded
- **Cache**: `/app/cache/models` (docker volume)
- **Offline Mode**: ENABLED (HF_HUB_OFFLINE=1)

### Check Embedding Performance:
```python
# Add timing to embeddings.py load_model():
import time
start = time.time()
self._model = SentenceTransformer(self.config.model_name)
print(f"[EMBED] Model load time: {time.time() - start:.2f}s")
```

### Verify Model Stays Loaded:
```python
# Add to ensure_loaded():
if not self.is_loaded:
    print("[EMBED] Loading model (NOT CACHED)")
    self.load_model()
else:
    print("[EMBED] Model already loaded (CACHED)")
```

### Test Embedding Speed:
```bash
# Inside container:
python3 -c "
from generic_framework.core.embeddings import get_embedding_service
import time

service = get_embedding_service()
start = time.time()
service.load_model()
print(f'Load time: {time.time() - start:.2f}s')

# Test encoding speed
start = time.time()
emb = service.encode('test query')
print(f'Encode time: {time.time() - start:.3f}s')
"
```

---

## 3. Docker Networking Overhead

### Check Network Latency:
```bash
# From host to container
ping model-runner.docker.internal

# From container to host
docker exec eeframe-app ping model-runner.docker.internal

# Test API latency
time curl -X POST http://model-runner.docker.internal:12434/api/generate \
  -d '{"model": "qwen3", "prompt": "test", "stream": false}'
```

---

## 4. GPU Monitoring Setup

### Install GPU Monitor:
```bash
# Terminal 1: Watch GPU usage
watch -n 0.5 nvidia-smi

# Terminal 2: Detailed GPU stats
nvidia-smi dmon -s u -c 1000

# Terminal 3: Run queries
# Monitor VRAM usage, GPU utilization, temperature
```

### Check GPU Settings:
```bash
# Check CUDA availability
docker exec eeframe-app python3 -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA devices: {torch.cuda.device_count()}')
"

# Check if sentence-transformers uses GPU
docker exec eeframe-app python3 -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f'Model device: {model.device}')
"
```

---

## 5. Query Processing Bottlenecks

### Add Timing to query_processor.py:
```python
import time

# At start of process_query():
start_time = time.time()

# After pattern search:
logger.info(f"Pattern search: {time.time() - start_time:.3f}s")

# After LLM call:
logger.info(f"LLM call: {time.time() - start_time:.3f}s")

# After embedding generation:
logger.info(f"Embedding gen: {time.time() - start_time:.3f}s")
```

---

## 6. Comparison with Previous RAAG System

### What was different?
- [ ] What embedding model did RAAG use?
- [ ] Was RAAG using GPU acceleration?
- [ ] Was RAAG keeping models loaded in memory?
- [ ] What was the query latency in RAAG?
- [ ] What was the embedding generation time?

---

## 7. Quick Wins / Optimizations

### Immediate Actions:
1. **Verify model-runner keep_alive is set correctly**
   - Set to -1 or high value to keep model loaded

2. **Ensure embeddings model uses GPU**
   - Check if sentence-transformers has CUDA support
   - Verify GPU is available in Docker

3. **Add timing logs to identify bottlenecks**
   - See which component is slow

4. **Check if offline mode is causing issues**
   - Verify model is cached properly
   - Try disabling HF_HUB_OFFLINE temporarily

### Performance Targets:
- Embedding model load: < 2s (first time only)
- Single embedding generation: < 100ms
- Pattern search (10 patterns): < 200ms
- LLM query: < 2s (depends on model size)
- Total query time: < 5s

---

## Next Steps

1. Run GPU monitor in separate terminal
2. Check model-runner settings (keep_alive, JIT, etc.)
3. Add timing logs to query_processor.py
4. Test embedding speed with timing script
5. Compare results with RAAG system
6. Identify bottleneck and optimize
