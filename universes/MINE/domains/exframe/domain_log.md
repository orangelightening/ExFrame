# Domain Log
Created: 2026-02-10 18:26:33

## 2026-02-10 18:26:33

Query: What is ExFrame and how do I get started?

# ExFrame: Expertise Framework

**ExFrame** is a domain-agnostic AI-powered knowledge management system with a universe-based architecture and plugin-based pipeline. It stores knowledge as patterns in domains within universes, and lets you query that knowledge through natural language.

---

## What Makes ExFrame Unique

### Core Philosophy
> **"AI performs reliably when nurtured in the role it is filling as it emerges."**

### Key Features

| Feature | Description |
|---------|-------------|
| **Universal Conversation Logging** | Every query/response automatically saved to permanent archives |
| **Conversation Memory** | AI remembers everything, building on previous discussions across sessions |
| **Universe Architecture** | Complete isolation and portability of knowledge configurations |
| **3 AI Personas** | Poet (creative), Librarian (documentation), Researcher (web search) |
| **Domain-Agnostic** | Easy to add new knowledge domains without code changes |
| **Docker Ready** | One-command deployment with monitoring stack |

### Three Core Use Cases

1. **📚 Personal University** - Each domain becomes a personalized course with its own curriculum
2. **✍️ Novel Writing** - Create long-form content with perfect continuity
3. **🧠 Therapy & Dialogue** - Deep dialogue that builds over weeks and months

---

## Quick Start (5 Minutes)

### Prerequisites
- Docker Engine (official, NOT snap)
- Docker Compose v2
- An API key (OpenAI, Anthropic, Zhipu, or Ollama for local)

### Installation Steps

**1. Clone the repository**
```bash
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame
```

**2. Configure your AI provider**
```bash
cp .env.example .env
# Edit .env and add your API key
```

**Choose a provider:**
- **OpenAI** (Recommended): `gpt-4o-mini`
- **Zhipu GLM** (Cost-effective): `glm-4.7`
- **Anthropic Claude**: `claude-3-5-sonnet-20241022`
- **Ollama** (Local/Free): `llama3`

**Example .env for OpenAI:**
```bash
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**3. Start ExFrame**
```bash
docker compose up -d
```

**4. Open your browser**
Navigate to: **http://localhost:3000**

---

## Using ExFrame

### Web Interface Tabs

| Tab | Purpose |
|-----|---------|
| **Assistant** | Query the AI assistant with pattern-based knowledge |
| **Patterns** | Browse and search knowledge patterns |
| **Traces** | View historical query traces and debugging |
| **Domains** | Manage domains, specialists, and configuration |
| **Universes** | Create, switch, merge, and export knowledge universes |
| **Diagnostics** | System health, search metrics, and pattern analysis |

### How to Query

1. Select a domain from the dropdown (default: `llm_consciousness`)
2. Type your question in natural language
3. Click **Query** or press Enter
4. View the AI response with confidence score, patterns used, and processing time

---

## Enable Conversation Memory

To let AI remember everything across sessions:

1. Go to **Domains** → Create/Edit Domain
2. Scroll to "Conversation Memory" section
3. Check "Enable conversation memory"
4. Choose mode: "All" or "Triggers"
5. Start building context!

---

## Access URLs

| Service | URL |
|---------|-----|
| **Main Application** | http://localhost:3000 |
| **API Documentation** | http://localhost:3000/docs |
| **Health Check** | http://localhost:3000/health |

---

## Need Help?

- 📖 **Full Documentation**: [README.md](README.md)
- 🎓 **Universal Logging**: [entice.md](entice.md)
- 📚 **Personal University**: [university.md](university.md)
- 🔧 **Installation Guide**: [INSTALL.md](INSTALL.md)

---

**That's it!** ExFrame is now running. Create a domain and start asking questions. 🚀


---

