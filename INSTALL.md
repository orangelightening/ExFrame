# ExFrame Installation Guide

**Version:** 1.6.0
**Last Updated:** 2026-01-27

---

## Quick Start (5 minutes)

```bash
# Clone and start
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame
docker compose up -d

# Access at http://localhost:3000
```

That's it! ExFrame will start with pre-loaded demo domains.

---

## Requirements

### Required

| Component | Version | Notes |
|-----------|---------|-------|
| **Docker Engine** | 24.0+ | **Must be official, NOT snap** |
| **Docker Compose** | v2.x | Use `docker compose` (space), not `docker-compose` (hyphen) |
| **Git** | Any | For cloning the repository |
| **Internet** | - | For initial Docker image pull |

### Optional

| Component | Purpose |
|-----------|---------|
| **LLM API Key** | For LLM enrichment features (GLM, OpenAI, Anthropic, etc.) |

---

## Detailed Installation

### 1. Verify Docker Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 24.0.0 or higher

# Check Docker Compose version
docker compose version
# Expected: Docker Compose version v2.x.x
```

**⚠️ IMPORTANT:** If you have snap Docker installed, remove it first:
```bash
snap list docker  # If this shows docker, remove it
sudo snap remove docker
```

### 2. Install Docker (if needed)

```bash
# Install official Docker Engine
curl -fsSL https://get.docker.com | sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group change to take effect
# OR use: newgrp docker
```

### 3. Clone ExFrame

```bash
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame
```

### 4. Configure LLM (Optional)

**ExFrame works without LLM configuration for pattern-based queries.** LLM is only needed for:
- LLM enrichment fallback
- Extended search beyond local patterns
- Pattern creation from AI responses

Create `.env` file:
```bash
cp .env.example .env
nano .env
```

**Recommended: GLM (z.ai)**
```bash
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-glm-api-key
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

**OpenAI GPT:**
```bash
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**Anthropic Claude:**
```bash
LLM_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=sk-ant-your-key-here
OPENAI_BASE_URL=https://api.anthropic.com/v1
```

**Local LLM (Ollama):**
```bash
LLM_MODEL=llama3
OPENAI_API_KEY=not-needed
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
```

### 5. Start ExFrame

```bash
docker compose up -d
```

### 6. Verify Installation

```bash
# Check container status
docker compose ps

# Check health endpoint
curl http://localhost:3000/health
# Expected: {"status":"healthy"}

# List domains
curl http://localhost:3000/api/domains
```

---

## Accessing ExFrame

| Service | URL | Description |
|---------|-----|-------------|
| **Main Application** | http://localhost:3000 | Web dashboard |
| **API Documentation** | http://localhost:3000/docs | Swagger/OpenAPI |
| **Health Check** | http://localhost:3000/health | Status endpoint |

**Optional Monitoring (if enabled):**
- **Grafana Dashboards**: http://localhost:3001 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Loki Logs**: http://localhost:3100

---

## Troubleshooting

### Port 3000 Already in Use

```bash
# Find what's using port 3000
sudo lsof -ti:3000

# Kill the process
sudo kill -9 <PID>

# Restart ExFrame
docker compose up -d
```

### Patterns Not Showing (Docker snap issue)

```bash
# Remove snap Docker and install official
sudo snap remove docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Restart containers
docker compose down
docker compose up -d
```

### "docker-compose: command not found"

You're using the old v1 syntax. Use `docker compose` (space, not hyphen):
```bash
# WRONG
docker-compose up -d

# CORRECT
docker compose up -d
```

### Permission Denied While Trying to Connect to Docker

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, OR:
newgrp docker
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f eeframe-app

# Last 50 lines
docker compose logs --tail=50 eeframe-app
```

---

## Upgrading

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose down
docker compose build --no-cache eeframe-app
docker compose up -d
```

---

## Uninstallation

```bash
# Stop and remove containers
docker compose down

# Remove volumes (WARNING: deletes all patterns!)
docker compose down -v

# Remove images
docker rmi eeframe-eeframe-app
```

---

## Next Steps

After installation:

1. **Browse the Dashboard** - http://localhost:3000
2. **Try a Query** - Select a domain and ask a question
3. **Browse Patterns** - Click the Patterns tab to see knowledge
4. **Create a Domain** - Use the Domains tab to add your own
5. **Check Diagnostics** - View system health in the Diagnostics tab

---

## Support

- **Documentation**: See [README.md](README.md) for full documentation
- **Issues**: https://github.com/orangelightening/ExFrame/issues
- **Architecture**: See [PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md)
