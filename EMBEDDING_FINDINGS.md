# Embedding System Performance Analysis

## ✅ GOOD NEWS: Embeddings are FAST!

### Test Results (CPU-based):
- **Model load**: 0.20s (first query only, singleton pattern keeps it loaded)
- **Single encode**: 10.4ms
- **Batch encode (10)**: 13.7ms total = 1.4ms per item
- **Batch encode (100)**: 77.0ms total = 0.8ms per item

### Why It's Fast:
1. **Model stays loaded** - Singleton pattern working correctly
2. **Small model** - all-MiniLM-L6-v2 is only ~80MB
3. **Efficient batching** - Better throughput with batch encoding
4. **Good algorithm** - SentenceTransformers is well-optimized

## ❌ NOT Running on GPU (But Doesn't Matter)

The diagnostics show:
```
PyTorch version: 2.10.0+cpu
CUDA available: False
⚠ Running on CPU (this is SLOW!)
```

**However**, even on CPU, performance is excellent for this use case. Adding GPU support would only reduce encoding time from ~1ms to ~0.1ms per item - not worth the complexity.

## 🔍 Real Performance Bottlenecks

Since embeddings take < 100ms per query, your latency issues are coming from:

### 1. **LLM Query Processing** (model-runner.docker.internal:12434)
- Likely taking 2-10+ seconds per query
- Check if qwen3 model stays loaded or unloads after queries
- Check keep_alive setting (default: 5 minutes)

### 2. **Pattern Generation** (Background task)
- Runs async, shouldn't block responses
- Check if it's causing memory/CPU spikes

### 3. **Docker Networking**
- Container-to-host communication overhead
- Test with `time curl http://model-runner.docker.internal:12434/...`

### 4. **Document Search** (if using librarian persona)
- Loading many large documents
- Check max_documents and max_chars_per_document settings

## 📊 Profiling the Real Bottleneck

Add this timing code to query_processor.py to identify the slow component:

```python
import time

async def process_query(...):
    t0 = time.time()

    # Load config
    t1 = time.time()
    logger.info(f"⏱ Config load: {(t1-t0)*1000:.0f}ms")

    # Pattern search
    patterns = _search_domain_patterns(...)
    t2 = time.time()
    logger.info(f"⏱ Pattern search: {(t2-t1)*1000:.0f}ms")

    # LLM call
    response = await persona.respond(...)
    t3 = time.time()
    logger.info(f"⏱ LLM call: {(t3-t2)*1000:.0f}ms")  # <-- This is likely the slow part!

    # Logging
    _append_to_log(...)
    t4 = time.time()
    logger.info(f"⏱ Logging: {(t4-t3)*1000:.0f}ms")

    logger.info(f"⏱ TOTAL: {(t4-t0)*1000:.0f}ms")
```

## 🎯 Next Steps

1. **Profile the query pipeline** - Add timing logs to identify the slow component
2. **Check model-runner settings** - Is qwen3 staying loaded?
3. **Monitor during query** - Run `watch -n 1 nvidia-smi` to see GPU usage
4. **Test LLM latency** - Direct API call to model-runner to measure baseline

## 💡 Optimization Opportunities

### If LLM is slow:
- Set keep_alive=-1 to keep model loaded permanently
- Use smaller model variant
- Check GPU is being used
- Reduce max_tokens in LLM config

### If pattern search is slow:
- Embeddings are already optimized
- Consider caching search results
- Reduce number of patterns searched

### If everything is slow:
- Check Docker resource limits
- Check system load (CPU/RAM)
- Check disk I/O (especially if model cache is on slow disk)

## ✅ Conclusion

**Embeddings are NOT the problem!** They're fast even on CPU. The latency is almost certainly in:
1. LLM processing (most likely)
2. Document loading (if using librarian)
3. Docker networking (less likely)

Add timing logs to pinpoint the exact bottleneck.
