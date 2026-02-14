# DMR (Docker Model Runner) API Reference

## Overview

The model-runner at `model-runner.docker.internal:12434` appears to be an **Ollama-compatible API** or similar local LLM server.

## Connection Info

- **Host**: `model-runner.docker.internal:12434`
- **Protocol**: HTTP (OpenAI-compatible endpoints)
- **Current Model**: `qwen3` (configured in peter domain)

## API Endpoints

### 1. OpenAI-Compatible Chat Completion

**Endpoint**: `POST /engines/v1/chat/completions`

Used by ExFrame for LLM queries.

**Request Format**:
```json
{
  "model": "ai/qwen3",
  "max_tokens": 8192,
  "temperature": 0.3,
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant.\n\nCurrent date and time: 2026-02-14 12:34:56"
    },
    {
      "role": "user",
      "content": "Query text here"
    }
  ],
  "stream": false
}
```

**Response Format**:
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Response text here"
      }
    }
  ]
}
```

### 2. List Models (Ollama-style)

**Endpoint**: `GET /api/tags`

Lists all available models.

**Test Command**:
```bash
curl http://model-runner.docker.internal:12434/api/tags
```

**Expected Response**:
```json
{
  "models": [
    {
      "name": "qwen3",
      "model": "qwen3",
      "size": 4700000000,
      "digest": "sha256:...",
      "modified_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Show Running Models (Ollama-style)

**Endpoint**: `GET /api/ps`

Shows currently loaded models in memory.

**Test Command**:
```bash
curl http://model-runner.docker.internal:12434/api/ps
```

**Expected Response**:
```json
{
  "models": [
    {
      "name": "qwen3",
      "model": "qwen3",
      "size": 4700000000,
      "size_vram": 4700000000,
      "expires_at": "2026-02-14T13:00:00Z"
    }
  ]
}
```

### 4. Model Info (Ollama-style)

**Endpoint**: `POST /api/show`

Get detailed information about a model.

**Request**:
```json
{
  "name": "qwen3"
}
```

**Test Command**:
```bash
curl -X POST http://model-runner.docker.internal:12434/api/show \
  -d '{"name":"qwen3"}'
```

## Critical Configuration: keep_alive

The `keep_alive` parameter controls how long the model stays loaded in memory after a query.

### Default Behavior (Ollama)
- **Default**: 5 minutes
- After 5 minutes of inactivity, the model unloads from VRAM
- Next query requires reload (slow!)

### Setting keep_alive

**Option 1: Per-Request (in generate/chat API)**
```json
{
  "model": "qwen3",
  "prompt": "test",
  "keep_alive": -1  // -1 = keep loaded indefinitely
}
```

**Option 2: Server Config (if using Ollama)**

Edit `~/.ollama/config.json`:
```json
{
  "keep_alive": -1
}
```

Or set environment variable:
```bash
OLLAMA_KEEP_ALIVE=-1
```

**Option 3: Per-Model Config**

Create a Modelfile:
```
FROM qwen3
PARAMETER keep_alive -1
```

### Recommended Settings for ExFrame

For best performance, set `keep_alive=-1` to keep the model loaded permanently:

1. **If using Ollama**: Add to environment or config
2. **If using custom runner**: Check documentation for equivalent setting
3. **Monitor with**: `curl http://model-runner.docker.internal:12434/api/ps`

## Performance Monitoring

### Check if Model is Loaded
```bash
# Shows loaded models and their expiration time
curl http://model-runner.docker.internal:12434/api/ps

# If "expires_at" is present, model will unload at that time
# If "expires_at" is far in the future or null, model stays loaded
```

### Test Query Latency
```bash
time curl -X POST http://model-runner.docker.internal:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer not-needed" \
  -d '{
    "model": "ai/qwen3",
    "max_tokens": 100,
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "stream": false
  }'
```

**Expected Times**:
- Model loaded: 500ms - 2s
- Model not loaded (first query): 5s - 30s (includes model load time)

## Docker Desktop Integration

The `model-runner.docker.internal` hostname is a Docker Desktop feature that allows containers to reach services on the host machine.

### Architecture:
```
┌─────────────────────┐
│   eeframe-app       │
│   (container)       │
│                     │
│   ExFrame code      │
│   → HTTP request    │
└──────────┬──────────┘
           │
           │ model-runner.docker.internal:12434
           ↓
┌─────────────────────┐
│   Host Machine      │
│                     │
│   Model Runner      │
│   (Ollama/etc)      │
│   Port 12434        │
└─────────────────────┘
```

### Benefits:
1. **Easy setup**: No network configuration needed
2. **GPU access**: Model runner on host can use GPU directly
3. **Separate resources**: Model doesn't compete with container for RAM

## Troubleshooting

### Model Not Responding
```bash
# 1. Check if model-runner is running
curl http://model-runner.docker.internal:12434/api/tags

# 2. Check what's loaded
curl http://model-runner.docker.internal:12434/api/ps

# 3. Check logs (if using Ollama)
journalctl -u ollama -f
```

### Slow Queries
1. **Check if model is loaded** (api/ps)
2. **Set keep_alive=-1** to prevent unloading
3. **Monitor GPU usage** (`nvidia-smi`)
4. **Check ExFrame logs** for timing breakdown (now includes ⏱ markers)

### Connection Refused
```bash
# Check if service is listening on host
netstat -tuln | grep 12434

# Check Docker can reach host
docker exec eeframe-app ping model-runner.docker.internal
```

## Integration with ExFrame

### Current Usage:
- **File**: `universes/MINE/domains/peter/domain.json`
- **Config**:
  ```json
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/qwen3",
    "api_key": "not-needed"
  }
  ```

### Adding keep_alive Support

To add keep_alive support to ExFrame, modify `persona.py`:

```python
payload = {
    "model": model,
    "max_tokens": 8192,
    "temperature": temperature,
    "messages": [...],
    "stream": False,
    "keep_alive": -1  # Keep model loaded
}
```

## Next Steps

1. **Identify the actual runner**: Check what's running on port 12434
   ```bash
   lsof -i :12434
   ps aux | grep ollama
   ```

2. **Configure keep_alive**: Set to -1 for best performance

3. **Monitor with timing logs**: Use new ⏱ logs to verify improvement

4. **Benchmark**: Test query time before/after keep_alive change
