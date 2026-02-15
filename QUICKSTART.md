# ⚡ ExFrame Quick Start

**Get ExFrame running in 5 minutes.**

---

## Prerequisites

- Docker and Docker Compose installed
- An API key from OpenAI, Anthropic, or Zhipu (recommended)
- Optional: GPU for local models (advanced optimization only)

---

## Installation (4 Steps)

### 1️⃣ Clone ExFrame

```bash
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame
```

### 2️⃣ Configure Your AI Provider

```bash
cp .env.example .env
```

Edit `.env` with your API key:

**OpenAI:**
```bash
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**Anthropic:**
```bash
LLM_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=your-anthropic-key-here
OPENAI_BASE_URL=https://api.anthropic.com/v1
```

**Zhipu (cost-effective):**
```bash
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-zhipu-key-here
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

**Ollama (local/free):**
```bash
LLM_MODEL=llama3
OPENAI_API_KEY=not-needed
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
```

**DMR / Docker Model Runner (optional - journal speed optimization only):**
```bash
LLM_MODEL=ai/llama3.2
OPENAI_API_KEY=not-needed
OPENAI_BASE_URL=http://model-runner.docker.internal:12434/engines/v1
```

> **Note**: Local models are optional and only optimize poet journal entry speed (~230ms vs ~4s). Requires GPU with 8GB+ VRAM. See [install-dmr.md](install-dmr.md) for setup. Most users should use remote models.

### 3️⃣ Start ExFrame

```bash
docker-compose up -d
```

Wait 30-60 seconds for containers to start.

### 4️⃣ Open Your Browser

Navigate to: **http://localhost:3000**

---

## Verify It Works

1. Click the **Assistant** tab
2. Select any domain from the dropdown
3. Type: "Hello, what can you do?"
4. Press Enter

**You should see a response!**

---

## What's Next?

- **Create your first domain**: Click **Domains** → **Create Domain**
- **Enable conversation memory**: Check the "Conversation Memory" box when creating a domain
- **Start learning**: Ask questions, build knowledge, never forget anything

---

## Need Help?

- **Full documentation**: [README.md](README.md)
- **Universal Logging**: [entice.md](entice.md)
- **Personal University**: [university.md](university.md)
- **Technical details**: [docs/UNIVERSAL_LOGGING_DESIGN.md](docs/UNIVERSAL_LOGGING_DESIGN.md)

---

**That's it!** You're ready to use ExFrame. 🚀
