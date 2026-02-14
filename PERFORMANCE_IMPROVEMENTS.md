# Performance Improvements & Diagnostics

## ✅ Completed Changes

### 1. **Added Comprehensive Timing Logs**

All query processing steps now have detailed timing logs with ⏱ markers:

**query_processor.py**:
- Config load time
- Pattern search time
- Document search time (librarian)
- LLM call time (total)
- Logging time
- **Total query time**

**persona.py**:
- HTTP request time to model runner

**Example Log Output**:
```
⏱ Config load: 2.3ms
⏱ Pattern search: 15.7ms
⏱ Starting HTTP request to http://model-runner.docker.internal:12434/engines/v1/chat/completions
⏱ HTTP request completed: 2847.2ms
⏱ LLM call (persona.respond): 2851.5ms
⏱ Logging: 4.1ms
⏱ TOTAL QUERY TIME: 2873.6ms
```

This tells you **exactly** where the time is being spent!

### 2. **Added Pattern Autogeneration Config**

Domains can now enable pattern autogeneration with:
```json
{
  "auto_create_patterns": true
}
```

- Legacy support: `conversation_memory.mode = "journal_patterns"` still works
- Excludes `**` queries (search-only queries)

### 3. **Fixed Pattern Autogeneration Bug**

Fixed the variable scope issue where `answer` was not accessible during pattern creation.

## 📊 Performance Analysis Results

### Embedding System: **NOT THE BOTTLENECK ✓**

- Model load: 0.20s (once per startup)
- Single encode: 10.4ms
- Batch encode: 0.8ms per item
- **Running on CPU is fine** - fast enough!

### Likely Bottleneck: **LLM (qwen3)**

Based on the timing logs, you'll likely see:
- Config/Pattern search: < 50ms
- **LLM call: 2000-10000ms** ← Most of the time!
- Logging: < 10ms

## 🔧 Next Steps

### 1. **Run a Test Query with Timing**

```bash
# Start ExFrame if not running
docker-compose up -d

# Watch the logs
docker logs -f eeframe-app

# Make a query and watch for ⏱ timing markers
```

You'll see output like:
```
[INFO] ⏱ Config load: 2.3ms
[INFO] ⏱ Pattern search: 15.7ms
[INFO] ⏱ Starting HTTP request to ...
[INFO] ⏱ HTTP request completed: 2847.2ms
[INFO] ⏱ TOTAL QUERY TIME: 2873.6ms
```

### 2. **Test Model Runner**

```bash
# Run diagnostic script
./scripts/test_model_runner.sh
```

This will:
- Check connectivity
- Identify the API type (Ollama/other)
- Test query latency
- Check keep_alive settings

### 3. **Optimize Based on Results**

**If LLM is slow (>5s per query):**

1. **Check if model stays loaded:**
   ```bash
   curl http://model-runner.docker.internal:12434/api/ps
   ```

2. **Set keep_alive to prevent unloading:**
   - Option A: Server config (if Ollama): `OLLAMA_KEEP_ALIVE=-1`
   - Option B: Per-request (modify persona.py payload to include `"keep_alive": -1`)

3. **Monitor GPU usage:**
   ```bash
   ./scripts/monitor_gpu.sh
   ```

4. **Consider model size:**
   - Smaller models = faster inference
   - Check qwen3 variant (qwen3:7b vs qwen3:14b vs qwen3:32b)

**If pattern search is slow (>100ms):**
- Already optimized (embeddings are fast)
- Consider reducing `max_patterns` in domain config

**If document search is slow (>500ms):**
- Reduce `max_documents` in domain config
- Reduce `max_chars_per_document`
- Check if semantic search is faster than filesystem search

## 📁 New Files Created

1. **PERFORMANCE_INVESTIGATION.md** - Detailed investigation checklist
2. **EMBEDDING_FINDINGS.md** - Embedding system analysis results
3. **DMR_API_REFERENCE.md** - Complete API documentation
4. **scripts/diagnose_performance.sh** - Full system diagnostics
5. **scripts/monitor_gpu.sh** - Real-time GPU monitoring
6. **scripts/test_model_runner.sh** - Model runner connectivity & performance

## 🎯 Quick Diagnosis

Run these commands to identify the bottleneck:

```bash
# 1. Check embedding performance (should be < 100ms)
docker exec eeframe-app python3 -c "
from generic_framework.core.embeddings import get_embedding_service
import time
service = get_embedding_service()
start = time.time()
service.load_model()
print(f'Load: {(time.time()-start)*1000:.0f}ms')
start = time.time()
service.encode('test')
print(f'Encode: {(time.time()-start)*1000:.0f}ms')
"

# 2. Check model runner (should be < 3s for loaded model)
./scripts/test_model_runner.sh

# 3. Watch timing logs during a real query
docker logs -f eeframe-app | grep "⏱"
```

## 🚀 Expected Performance Targets

After optimization:
- **Config/pattern search**: < 50ms
- **LLM call (model loaded)**: 500ms - 3s (depends on model size & complexity)
- **LLM call (model not loaded)**: 5s - 30s (includes load time)
- **Logging**: < 10ms
- **Total query**: 1s - 5s (for loaded model)

## 📝 Monitoring Going Forward

Add this to your development workflow:

1. **Always watch timing logs:**
   ```bash
   docker logs -f eeframe-app | grep "⏱"
   ```

2. **Monitor GPU usage** (if using GPU):
   ```bash
   watch -n 1 nvidia-smi
   ```

3. **Check model stay-loaded**:
   ```bash
   curl http://model-runner.docker.internal:12434/api/ps
   ```

4. **Benchmark regularly**:
   ```bash
   ./scripts/test_model_runner.sh
   ```

## ❓ Questions to Answer

1. **What model runner are you using?**
   - Ollama?
   - vLLM?
   - Custom solution?

2. **Is keep_alive configured?**
   - Check with `curl .../api/ps`
   - Should show model staying loaded

3. **What's the actual query latency?**
   - Check timing logs: `docker logs eeframe-app | grep "⏱"`

4. **Is GPU being used?**
   - Run `nvidia-smi` during query
   - Should show high GPU utilization

Once you have these answers, we can optimize the specific bottleneck!
