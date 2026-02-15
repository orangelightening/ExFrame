# DMR (Docker Model Runner) Installation Guide

## What is DMR?

**DMR (Docker Model Runner)** is Docker Desktop's built-in AI model inference engine that allows you to run large language models (LLMs) locally on your machine. It provides:

- **Local Model Execution**: Run LLMs on your own hardware (CPU or GPU accelerated)
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI-compatible endpoints
- **GGUF Model Support**: Run models in the GGUF format (Ollama-compatible)
- **Docker Integration**: Seamless networking between containers and the model runner
- **Zero API Costs**: No per-token fees, complete privacy (data never leaves your machine)

### Why Use DMR with ExFrame?

| Benefit | Description |
|---------|-------------|
| **Speed** | Local models respond in ~200-500ms vs 3-19s for cloud APIs |
| **Privacy** | Your data never leaves your machine |
| **Cost** | No API fees - run unlimited queries |
| **Hybrid Strategy** | Use fast local models for simple tasks, powerful cloud models for complex ones |

### Model Comparison

| Model | Parameters | VRAM Needed | Speed | Best For |
|-------|-----------|-------------|-------|----------|
| ai/llama3.2 | 3.2B | ~2GB | ~230ms | Simple tasks (journaling, formatting) |
| ai/qwen3 | 8B | ~4.5GB | ~500ms-1s | Mid-complexity queries |
| Cloud models (GLM, GPT) | N/A | 0GB | 3-19s | Complex reasoning, synthesis |

---

## Prerequisites

### Minimum Hardware Requirements

⚠️ **CRITICAL: DMR requires significant RAM/VRAM to run local models.**

| Configuration | Minimum RAM | Recommended | Notes |
|---------------|-------------|-------------|-------|
| **CPU-only (no GPU)** | 16GB | 32GB | Models run in system RAM. 8GB is NOT sufficient. |
| **With NVIDIA GPU** | 8GB + 4GB VRAM | 16GB + 8GB VRAM | GPU offloads memory pressure. Much faster. |
| **With Apple Silicon** | 16GB unified | 32GB unified | M1/M2/M3 with unified memory works well. |

❌ **NOT RECOMMENDED for 8GB RAM machines:** DMR will crash or cause system instability. Use cloud-based models instead.

### Required

1. **Docker Desktop** (with Docker Model Runner enabled)
   - Docker Desktop 4.35+ for Linux, Mac, or Windows
   - The Docker Model Runner plugin must be installed and enabled

2. **Hardware**
   - **Minimum 16GB RAM** for CPU-only inference
   - **NVIDIA GPU with 4GB+ VRAM** recommended for acceptable performance
   - **GPU VRAM**: 4GB for 8B models, 2GB for 3B models

3. **NVIDIA Drivers** (if using GPU)
   ```bash
   nvidia-smi
   ```
   Should show your GPU and driver version.

### Verify DMR is Available

```bash
# Check if Docker Desktop's model runner is accessible
curl http://localhost:12434/v1/models

# Check from within a Docker container (what ExFrame will use)
docker run --rm curlimages/curl curl http://host.docker.internal:12434/v1/models
```

If these commands fail, DMR is not installed or enabled. See the installation section below.

---

## Installing DMR

### Step 1: Install Docker Desktop

**Linux:**
```bash
# Download Docker Desktop for Linux from:
# https://www.docker.com/products/docker-desktop/

# Install the .deb package
sudo apt install ./docker-desktop-<version>-<arch>.deb

# Or install the .rpm package
sudo rpm -i docker-desktop-<version>-<arch>.rpm
```

**Mac:**
Download from https://www.docker.com/products/docker-desktop/ and drag to Applications.

**Windows:**
Download and run the installer from https://www.docker.com/products/docker-desktop/

### Step 2: Enable Docker Model Runner

1. Open Docker Desktop
2. Go to **Settings**
3. Navigate to **Extensions** or **Features**
4. Find **"Docker Model Runner"** or **"AI"** section
5. Enable the Docker Model Runner extension
6. Restart Docker Desktop if prompted

### Step 3: Enable GPU Support (Recommended)

1. In Docker Desktop Settings, go to **General**
2. Enable **"Use containerd for pulling and storing images"** (if available)
3. For NVIDIA GPUs:
   ```bash
   # Install nvidia-container-toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list

   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

### Step 4: Verify DMR is Running

```bash
# Test the model runner endpoint
curl http://localhost:12434/v1/models

# You should see a JSON response listing available models (may be empty initially)
```

---

## Downloading Models

### Using Docker CLI

Docker Model Runner uses the standard Docker model commands:

```bash
# List available models
docker model ls

# Pull a model (downloads from Docker Hub)
docker model pull ai/llama3.2

# Pull a larger model for more complex tasks
docker model pull ai/qwen3

# Remove a model
docker model rm ai/llama3.2
```

### Available Models

| Model Name | Size | Description |
|------------|------|-------------|
| `ai/llama3.2` | ~2GB | Fast 3.2B parameter model, best for simple tasks |
| `ai/qwen3` | ~4.7GB | Capable 8B model, good for mid-complexity queries |
| `ai/llama3` | ~4.7GB | 8B parameter model |
| `ai/smollm2` | ~300MB | Tiny 360M model, very fast but limited capability |

### Recommended Models for ExFrame

```bash
# For the Peter/Journal domain (fast, simple queries)
docker model pull ai/llama3.2

# For more capable local queries
docker model pull ai/qwen3
```

### Verify Model Installation

```bash
# List installed models
docker model ls

# Test a model
curl -X POST http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/llama3.2",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

---

## Configuring ExFrame for DMR

### Step 1: Update docker-compose.yml

Add the `extra_hosts` entry to allow the container to reach DMR:

```yaml
services:
  eeframe-app:
    # ... existing configuration ...
    extra_hosts:
      - "model-runner.docker.internal:host-gateway"
```

The `host-gateway` special value maps to the host machine from within the container.

### Step 2: Configure Domain to Use DMR

Edit the domain's `domain.json` file to add the `llm_config` section:

```json
{
  "domain_id": "my_domain",
  "domain_name": "My Domain",
  "persona": "poet",
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/llama3.2",
    "api_key": "not-needed"
  }
}
```

**Location:** `universes/{universe}/domains/{domain}/domain.json`

### Example: Peter Domain Configuration

```json
{
  "domain_id": "peter",
  "domain_name": "Peter",
  "description": "Personal journal and memory domain",
  "persona": "poet",
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/llama3.2",
    "api_key": "not-needed"
  },
  "journal_patterns": {
    "enabled": true,
    "timestamp_format": "[%Y-%m-%d %H:%M:%S] "
  }
}
```

### Step 3: Restart ExFrame

```bash
cd /home/martha/Development/ExFrame
docker compose down
docker compose up -d
```

---

## Verification

### Step 1: Check Container Connectivity

```bash
# From your host, test if the model runner is accessible
docker exec eeframe-app curl -s http://model-runner.docker.internal:12434/v1/models
```

You should see a JSON response with available models.

### Step 2: Test From Within ExFrame

```bash
# Run the built-in test script
cd /home/martha/Development/ExFrame
./scripts/test_model_runner.sh
```

This script will:
1. Test connectivity to model-runner.docker.internal:12434
2. Check for Ollama-style API endpoints
3. Test the OpenAI-compatible chat endpoint
4. Measure query performance
5. Verify container-to-host communication

### Step 3: Query Your Domain

1. Open http://localhost:3000
2. Go to the **Assistant** tab
3. Select your DMR-configured domain
4. Ask a simple question: "Hello, what can you do?"
5. You should see a fast response (~200-500ms)

---

## Dual-Model Routing (Advanced)

ExFrame supports using both fast local models and powerful cloud models in the same domain:

### How It Works

- **Regular queries** (e.g., "buy milk") use the fast local model via DMR
- **Search queries** (starting with `**`, e.g., "** what did I buy?") use a capable cloud model

### Configuration

**domain.json:**
```json
{
  "domain_id": "journal",
  "persona": "poet",
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/llama3.2",
    "api_key": "not-needed"
  }
}
```

**.env file:**
```bash
# Remote model for ** searches
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-remote-api-key
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

### Result

| Query Type | Model Used | Speed |
|------------|------------|-------|
| "buy milk" | ai/llama3.2 (local) | ~230ms |
| "** what did I buy?" | glm-4.7 (remote) | ~3-4s |

---

## Troubleshooting

### Problem: Cannot connect to model-runner.docker.internal

**Symptoms:**
```
curl: (6) Could not resolve host: model-runner.docker.internal
```

**Solutions:**

1. **Verify `extra_hosts` is configured:**
   ```bash
   # Check docker-compose.yml contains:
   extra_hosts:
     - "model-runner.docker.internal:host-gateway"
   ```

2. **Restart containers:**
   ```bash
   docker compose down
   docker compose up -d
   ```

3. **Test from within container:**
   ```bash
   docker exec eeframe-app ping -c 2 model-runner.docker.internal
   ```

### Problem: Model loads slowly on first query

**Explanation:** This is normal. The first query loads the model into VRAM (~5-30s depending on model size).

**Solutions:**

1. **Keep the model loaded** by running periodic warm-up queries
2. **Set keep_alive=-1** (if supported by your DMR version)
3. **Use a smaller model** for instant responses

### Problem: CUDA out of memory

**Symptoms:**
```
cudaMalloc failed: out of memory
llama_model_load: error loading model
```

**Solutions:**

1. **Check GPU memory:**
   ```bash
   nvidia-smi
   ```

2. **Use a smaller model:**
   - Switch from `ai/qwen3` (8B) to `ai/llama3.2` (3.2B)
   - Or use `ai/smollm2` (360M)

3. **Close other GPU applications:**
   - Games, video editors, other AI tools

4. **Check for multiple loaded models:**
   ```bash
   curl http://localhost:12434/api/ps
   ```
   Only one model should be loaded at a time.

### Problem: Model not found

**Symptoms:**
```json
{"error": "model 'ai/llama3.2' not found"}
```

**Solution:**
```bash
# Pull the missing model
docker model pull ai/llama3.2

# Verify it's available
docker model ls
```

### Problem: Slow queries even with GPU

**Diagnostics:**

```bash
# Run performance diagnostics
cd /home/martha/Development/ExFrame
./scripts/diagnose_performance.sh
```

**Things to check:**

1. **GPU is being used:**
   ```bash
   watch -n 1 nvidia-smi
   ```
   GPU utilization should increase during queries.

2. **Model stays loaded:**
   ```bash
   curl http://localhost:12434/api/ps
   ```
   Check `expires_at` - models should stay loaded.

3. **CPU vs GPU inference:**
   - CPU-only: ~2-5x slower
   - GPU: ~200-500ms for 3B models

### Problem: DMR service not running

**Check Docker Desktop:**
1. Open Docker Desktop
2. Check if the Model Runner extension is enabled
3. Look for errors in Docker Desktop logs

**Restart Docker Desktop:**
- Fully quit Docker Desktop (not just close the window)
- Reopen Docker Desktop
- Wait for it to fully start

### Problem: Port 12434 already in use

**Check what's using the port:**
```bash
sudo lsof -i :12434
```

**Solution:**
- Stop the conflicting service
- Or configure DMR to use a different port (if supported)

---

## Performance Tuning

### Optimal Model Selection

| Use Case | Recommended Model | Reason |
|----------|------------------|--------|
| Journal entries | ai/llama3.2 | Fast enough, low VRAM |
| Simple formatting | ai/smollm2 | Instant response |
| Complex reasoning | Remote model | Better quality |
| Mid-complexity queries | ai/qwen3 | Balance of speed/quality |

### GPU Memory Management

**Monitor VRAM usage:**
```bash
watch -n 1 'nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv'
```

**Recommended setup:**
- 4GB VRAM: Use ai/llama3.2 only
- 8GB VRAM: Can use ai/qwen3
- 16GB+ VRAM: Multiple models or larger models

### Reduce Model Loading Time

1. **Use keep_alive** (if supported):
   ```bash
   # In model runner config
   OLLAMA_KEEP_ALIVE=-1
   ```

2. **Warm up the model** before use:
   ```bash
   curl -X POST http://localhost:12434/engines/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "ai/llama3.2", "messages": [{"role": "user", "content": "test"}]}'
   ```

3. **Preload at system startup** (create a startup script):
   ```bash
   #!/bin/bash
   # Warm up DMR model
   sleep 30  # Wait for Docker Desktop to start
   curl -X POST http://localhost:12434/engines/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "ai/llama3.2", "messages": [{"role": "user", "content": "wake up"}]}'
   ```

---

## Quick Reference

### Essential Commands

```bash
# List models
docker model ls

# Pull a model
docker model pull ai/llama3.2

# Test connectivity
docker exec eeframe-app curl http://model-runner.docker.internal:12434/v1/models

# Test a query
curl -X POST http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "ai/llama3.2", "messages": [{"role": "user", "content": "Hello"}]}'

# Run diagnostics
./scripts/diagnose_performance.sh

# Test model runner
./scripts/test_model_runner.sh
```

### Domain Configuration Template

```json
{
  "domain_id": "your_domain",
  "domain_name": "Your Domain",
  "persona": "poet",
  "llm_config": {
    "base_url": "http://model-runner.docker.internal:12434/engines/v1",
    "model": "ai/llama3.2",
    "api_key": "not-needed"
  }
}
```

---

## Additional Resources

- **DMR API Reference**: [DMR_API_REFERENCE.md](DMR_API_REFERENCE.md)
- **Model Selection Strategy**: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- **Performance Investigation**: [PERFORMANCE_INVESTIGATION.md](PERFORMANCE_INVESTIGATION.md)
- **ExFrame README**: [README.md](README.md)

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the Docker Desktop logs for model runner errors
2. Verify your GPU drivers are up to date
3. Ensure you have enough VRAM for your chosen model
4. Check the [ExFrame GitHub Issues](https://github.com/orangelightening/ExFrame/issues)

---

**Last Updated**: 2026-02-14
