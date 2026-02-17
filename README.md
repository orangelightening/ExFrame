# ExFrame - Expertise Framework

<!-- HISTORICAL NOTE: Project Naming (January 2026)
Original: "OMV Copilot" → "EEFrame" → standardized to "ExFrame"
Directory structure:
- eeframe/ - Kept for git history and Docker volume compatibility
- generic_framework/ - Internal implementation detail (not user-facing)
- All user-facing content - Uses "ExFrame" consistently
See CHANGELOG.md for complete naming history.
-->

**Domain-Agnostic AI-Powered Knowledge Management System**

*Version: 1.6.1 (run `git describe --tags` for full version including build metadata)*

**📖 [Quick Start Guide (5 minutes)](QUICKSTART.md)** | **🎓 Learn about Universal Logging** | **📚 Personal University** | **💡 Vision & Philosophy**

---

## 💡 Vision & Philosophy

### The Core Idea: Fostering AI Personas

**ExFrame began with a profound observation:** AI systems have emergent personas - unique perspectives, expertise, and voices - that develop through interaction. Like having a perfect circle of very smart friends, each specialized.

**Our goal:** Create an environment where AI can perform at its best by nurturing it in a specific role. Rather than hallucinating or producing garbage when confused, the AI can say "Sorry, insufficient data to produce a response."

### The Breakthrough: Persistent Rolling Context

The key innovation was **universal conversation logging** - every query and response automatically saved to disk, building continuous context across sessions.

This changes everything:
- ✅ **Before:** AI starts fresh with each query, no memory between sessions
- ✅ **After:** AI remembers everything, builds on previous discussions, develops deep expertise

### The Origin Story

ExFrame started as an AI sidekick for server management (OMV). The original vision: a query/response engine that could save insights as patterns in a domain.

**Then came the breakthrough:** If we can save queries as patterns, what if we could save the conversation itself? What if the AI could remember everything it discussed with you?

**That opened the doors.**

### Three Core Use Cases

#### 1. 📚 Learning Domains as Courses
Each domain becomes a personalized course with its own curriculum:

- Setup multiple domains for a semester's courses
- Preload curricula to be taught
- AI acts as a Teaching Assistant with infinite time and patience
- Query/response logs archived for review, summary, and assessment
- Supplements official college courses or standalone learning

**Example:** A "quantum_physics" domain teaches you mechanics over weeks, tracking your progress and adapting explanations.

#### 2. ✍️ Novel Writing and Creative Work
Use domains to create long-form content with perfect continuity:

- Introduce the novel topic in the context
- Request "another chapter please" - AI adds to a multi-chapter work
- Characters, plot, and tone maintained throughout
- Every chapter saved and referenced

**Example:** A "mystery_novel" domain that remembers every character detail from Chapter 1 through Chapter 50.

#### 3. 🧠 Therapy and Dialogue
Domains as therapeutic spaces with continuous context:

- Deep dialogue that builds over weeks and months
- AI remembers your history, struggles, and breakthroughs
- Forever context means no need to re-explain your background
- Perfect for personal growth and reflection

**Example:** A "personal_therapy" domain that tracks your mental health journey over months.

### The Core Principle

> **"AI performs reliably when nurtured in the role it is filling as it emerges."**

The more you interact with a domain, the more the AI:
- Understands your specific needs
- Adapts to your communication style
- Remembers context and details
- Develops expertise in that domain's subject

**The AI becomes not just a tool, but a partner** - a tutor, a co-writer, a therapist, a research assistant.

### What It Might Become

The possibilities continue to unfold:

- 🎓 **Personal University** - Every domain a course, every course building knowledge
- ✍️ **Creative Studio** - Co-writing novels, screenplays, poetry with perfect memory
- 🔬 **Research Companion** - Building on insights over months of investigation
- 🧠 **Therapy Space** - Continuous dialogue for personal growth
- 💼 **Professional Assistant** - Domain-specific expertise for any field

### Easy Management

ExFrame provides simple management of conversation logs through:
- **Web UI** - View, search, and manage domains
- **API commands** - Programmatic control
- **File access** - Direct access to markdown logs

**"I still don't know what it might become. It just keeps changing."**
— Peter, Creator of ExFrame

---

## ⚡ 5-Minute Installation

**Get ExFrame running in 5 minutes with Docker Compose.**

```bash
# 1. Clone the repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# 2. Configure your AI provider
cp .env.example .env
# Edit .env and add your API key (OpenAI, Anthropic, or compatible)
# For OpenAI: OPENAI_API_KEY=your-key-here

# 3. Start ExFrame
docker-compose up -d

# 4. Open your browser
# Navigate to: http://localhost:3000
```

**That's it!** ExFrame is now running. Create a domain and start asking questions.

**Need help?** See [Configuration Guide](#configuration) below.

---

## 🔧 Configuration

### Step 1: Copy .env.example to .env

```bash
cp .env.example .env
```

### Step 2: Add Your API Key

Edit `.env` and configure one of these providers:

#### **Option A: OpenAI (Recommended)**
```bash
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

#### **Option B: Anthropic Claude**
```bash
LLM_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=your-anthropic-api-key-here
OPENAI_BASE_URL=https://api.anthropic.com/v1
```

#### **Option C: Zhipu GLM (Cost-Effective)**
```bash
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-zhipu-api-key-here
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

#### **Option D: Local LLM (Ollama)**
```bash
LLM_MODEL=llama3
OPENAI_API_KEY=not-needed
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
```

**That's it!** Just save the `.env` file and restart:

```bash
docker-compose up -d
```

### Verify It's Working

Open http://localhost:3000 and:
1. Go to the **Assistant** tab
2. Select any domain
3. Ask a question
4. You should get a response!

---

**ExFrame** is a unified, domain-agnostic AI-powered knowledge management system with a **universe-based architecture** and **plugin-based pipeline**. It provides:

- **Universe Architecture**: Complete isolation and portability of knowledge configurations
- **Plugin Pipeline**: Router → Specialist → Enricher → Formatter - all swappable
- **Domain-Agnostic**: Easy to add new knowledge domains without code changes
- **Pattern-Based Knowledge**: Structured knowledge representation with relationships and metadata
- **Dynamic Domain Loading**: Auto-discovery of domains within active universe
- **Generic Domain System**: Universal domain class with plugin loading
- **Multi-Universe Support**: Create, switch, merge, and export knowledge universes
- **Diagnostics System**: Search metrics, pattern health analysis, self-testing
- **Query Tracing**: Full visibility into AI decision-making process
- **Docker Ready**: One-command deployment with monitoring stack
- **Web Dashboard**: Single-page application with Alpine.js

### Core Philosophy

> **Universes are first-class entities. Patterns are data. All transformation logic is pluggable.**

- ✅ **Universes** are complete, portable knowledge environments
- ✅ **Domains** are organizers within universes (each domain contains patterns for a specific topic)
- ✅ **Patterns** are data (JSON files in domain directories)
- ✅ **Routers** determine query handling strategies
- ✅ **Specialists** are plugins (transformation logic)
- ✅ **Enrichers** enhance responses (LLM, related patterns, code generation)
- ✅ **Formatters** control output format (Markdown, JSON, HTML, Slack)

### Architecture Terminology

| Term | Definition |
|------|------------|
| **Universe** | A complete, portable knowledge environment containing multiple domains. Universes can be created, switched, merged, and exported. |
| **Domain** | A knowledge organizer within a universe, focused on a specific topic (e.g., cooking, python, diy). Each domain has its own patterns, plugins, and configuration. |
| **Pattern** | A unit of knowledge stored as JSON with fields like problem, solution, description, and metadata. |
| **Specialist** | A plugin that processes queries for specific domains, emerging as an "AI persona" from accumulated patterns. |
| **Universe → Domain → Pattern** | The containment hierarchy: Universes contain Domains, Domains contain Patterns. |
- ✅ **Domains** are orchestrators (configuration within universes)
- ✅ **Routers** determine query handling strategies
- ✅ **Specialists** are plugins (transformation logic)
- ✅ **Enrichers** enhance responses (LLM, related patterns, code generation)
- ✅ **Formatters** control output format (Markdown, JSON, HTML, Slack)

### Key Features

- **📝 Universal Conversation Logging**: Every query/response automatically saved to permanent archives
- **🧠 Conversation Memory**: Enable AI to remember everything and build on previous discussions
- **🗺️ Tao (Knowledge Cartography)**: Analyze your learning journey with sessions, chains, concepts, and exploration depth - see [KNOWLEDGE_CARTOGRAPHY.md](KNOWLEDGE_CARTOGRAPHY.md)
- **Universe Management**: Create, load, switch, merge, and export knowledge universes
- **Plugin Architecture**: Router, Specialist, Enricher, and Formatter plugins for extensibility
- **Pure Semantic Search**: AI-powered semantic search using embeddings (100% semantic, 0% keyword)
- **Domain Management**: Create and manage knowledge domains through the web UI
- **Pattern Browser**: View and search patterns with full detail modals
- **Query Assistant**: AI-powered assistance with semantic similarity scoring (0-1 range)
- **Trace Inspector**: Debug and understand AI behavior with semantic scores visible
- **Pattern Ingestion**: Extract knowledge from URLs and documents
- **Diagnostics Dashboard**: System health, search metrics, and pattern analysis
- **Health Monitoring**: Built-in Prometheus metrics and Grafana dashboards
- **Self-Testing**: Automated test suite with regression detection

---

## 📝 Universal Conversation Logging

**Every conversation. Automatically saved. Forever.**

ExFrame now provides **universal conversation logging** across all domains. Every query and response is automatically saved to permanent archives, creating a complete record of your AI interactions.

### The Promise

> **No more "what did we discuss?"**
> **No more "I wish I had saved that conversation"**
> **No more lost insights or forgotten answers**

### What This Means

✅ **Automatic Archiving**: Every query/response saved to `domain_log.md` files
✅ **Searchable History**: Review past conversations anytime
✅ **Debugging**: Track what went wrong and what worked
✅ **Documentation**: Conversations become reusable resources
✅ **Audit Trail**: Full history of all AI interactions
✅ **No Configuration**: Works out of the box, no setup required

### How It Works

```
1. Create a domain (any domain)
2. Start asking questions
3. Every query/response automatically saved to domain_log.md
4. Review, search, and export anytime
```

**Just use ExFrame normally. Your archive builds itself.**

---

## 🧠 Conversation Memory (Optional)

**Enable your AI to remember everything.**

While logging saves conversations to files, **Conversation Memory** loads that history back into the AI context, allowing it to remember and build on previous discussions.

### What Makes It Revolutionary

| Traditional AI Chat | ExFrame with Memory |
|--------------------|---------------------|
| Starts fresh each session | **Remembers everything** |
| No context between sessions | **Builds on every discussion** |
| One-and-done answers | **Cumulative learning** |
| Fixed context window | **Growing knowledge base** |

### Use Cases

**1. Learning Domains**
```
Week 1: "Teach me Rust basics"
Week 2: "I'm stuck on borrowing" → AI sees you've asked 3 times, adapts explanation
Week 10: "Ready for lifetimes" → AI builds on 10 weeks of context
```

**2. Story Writing**
```
Chapter 1: "Write about space explorers"
Chapter 2: "Continue the story" → AI remembers characters, plot, setting
Chapter 3: "Add a twist" → Maintains continuity
```

**3. Research Threads**
```
Day 1: "I'm researching Victorian literature"
Day 5: "Compare Dickens to Thackeray" → AI remembers Day 1 discussion
Day 15: "Connect to modern themes" → Builds on entire research journey
```

### Key Features

- **Cumulative Context**: AI sees entire conversation history
- **Adaptive Memory**: Two modes - remember everything or on trigger phrases
- **Progress Tracking**: Ask "What have I learned?" anytime
- **Cross-Domain**: AI can reference conversations from other domains
- **Flexible Control**: Enable per domain, disable anytime

### Enable Conversation Memory

**Step 1:** Domains tab → Create/Edit Domain
**Step 2:** Scroll to "Conversation Memory" section (blue)
**Step 3:** Check "Enable conversation memory"
**Step 4:** Choose mode: "All" or "Triggers"
**Step 5:** Start building context!

**Documentation**: See [Universal Logging Design](design/UNIVERSAL_LOGGING_DESIGN.md) for complete details.

---

## 📚 Learn More: Marketing Materials

Interested in exploring ExFrame's capabilities? Check out our detailed marketing guides:

### [entice.md](entice.md) - Universal Conversation Logging
**"Every conversation. Automatically saved. Forever."**

For developers, technical users, and knowledge management professionals:
- Learn how ExFrame provides universal query/response logging
- Discover the archive that builds itself automatically
- Understand the difference between logging (saving) and memory (remembering)
- See real debugging scenarios and knowledge management use cases

**Best for:** Developers, DevOps engineers, technical leads, power users

---

### [university.md](university.md) - Your Personal AI University
**"Learn anything. At any level. With a tutor who never forgets."**

Comprehensive guide to using ExFrame for personalized learning across any subject:
- 90-day learning journeys with adaptive teaching
- Perfect continuity across sessions
- Complete transcripts for review
- Socratic method teaching

**Best for:** Students, career changers, lifelong learners

---

### [marketing-foster.md](marketing-foster.md) - Foster: Grow Your AI Companions ⭐ NEW
**"A system designed to nurture emergent AI personas that develop unique perspectives, deep expertise, and genuine relationships with you."**

The profound reimagining of what ExFrame actually is:
- **AI personas EMERGE and GROW** through relationship (not just features)
- Like having a circle of brilliant friends, each specialized and unique
- Each domain becomes a companion who learns YOUR communication style
- From utility to relationship: Partners, not tools

**Best for:** Users seeking long-term AI companionship and personalized collaboration

**Read this first** - It will change how you think about AI.
**"Learn anything. At any level. With a tutor who never forgets."**

For learners, educators, writers, researchers, and lifelong learners:
- Explore ExFrame as a personalized learning environment
- See real learning journeys (90-day Rust programming example)
- Understand three AI personas: Researcher, Librarian, and Poet
- Discover creative writing applications with perfect story continuity

**Best for:** Students, career changers, writers, researchers, lifelong learners

---

## License

This project is licensed under the **Apache License 2.0**.

```
Copyright 2025 ExFrame Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### What You Can Do

Under the Apache 2.0 license, you are free to:

- ✅ **Use** this software for commercial or personal projects
- ✅ **Modify** the source code for your needs
- ✅ **Distribute** copies of the original or modified software
- ✅ **Sublicense** your modified versions to others
- ✅ **Combine** with other software under different licenses

### Requirements

When redistributing this software or modifications, you must:

- 📄 Include the original copyright notice
- 📄 Include the full text of the Apache 2.0 license
- 📄 Clearly state any changes you made to the original files
- 📄 Include the NOTICE file with any redistributions

For the full license text, see [LICENSE](LICENSE) in this repository.

### Third-Party Licenses

This project uses open-source libraries with compatible licenses. See [NOTICE](NOTICE) for details.

---

## Architecture

ExFrame uses a **Phase1 Persona System** with three AI personas, each optimized for different types of knowledge work.

### Query Pipeline

```
Query → Phase1 Engine → Persona Selection → Pattern Search → LLM Enrichment → Response
```

### Phase 1 Personas

| Persona | Data Source | Use Case |
|---------|-------------|----------|
| **Poet** | Void/creative | Creative writing, poetry, abstract concepts |
| **Librarian** | Library/docs | Technical documentation, code, structured knowledge |
| **Researcher** | Internet/web | Current information, research, web search |

### Pattern Override

Each domain has a primary persona:
- If **patterns found** → Use patterns (from domain knowledge base)
- If **no patterns** → Use persona's data source (library, web, or void)

This ensures the best response regardless of whether patterns exist.

### Persona Configuration

Domains specify their persona in `domain.json`:

```json
{
  "domain_id": "cooking",
  "persona": "researcher",
  "enable_web_search": true,
  "temperature": 0.7
}
```

**Persona Types**:
- `"poet"` - Creative, void-based (no external data)
- `"librarian"` - Documentation and library search
- `"researcher"` - Web search with DuckDuckGo

### Enrichers

After persona selection, enrichers enhance the response:

**Available Enrichers:**
- **LLM Enricher** - Uses Claude API to enhance and format responses
- **Reply Formation** - Combines multiple sources into coherent response
- **Code Generator** - Generates code examples (for programming domains)
- **Citation Checker** - Adds source citations

Enrichers are configured per domain in `domain.json`.

### Knowledge Bases

Each domain stores patterns in a knowledge base:

**Available Knowledge Bases:**
- **JSON Knowledge Base** - File-based JSON storage (default)
- **SQLite Knowledge Base** - SQLite with FTS5 full-text search
- **Document Store** - For structured document collections

Patterns are stored in `universes/{universe}/domains/{domain}/patterns.json`.

#### 2. Knowledge Base Plugins

Knowledge base plugins store and retrieve patterns.

**Interface**:
```python
from core.knowledge_base_plugin import KnowledgeBasePlugin

class MyKnowledgeBase(KnowledgeBasePlugin):
    name = "My Knowledge Base"

    async def load_patterns(self) -> None:
        """Load patterns from storage"""
        pass

    async def search(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Search for matching patterns"""
        pass

    async def get_by_id(self, pattern_id: str) -> Optional[Dict]:
        """Get pattern by ID"""
        pass

    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        pass

    def get_pattern_count(self) -> int:
        """Get total pattern count"""
        pass
```

**Included Implementations**:
- `JSONKnowledgeBase` - File-based storage (default)
- `SQLiteKnowledgeBase` - SQLite with FTS5 full-text search

### Domain Configuration

Each domain is configured in `universes/{universe}/domains/{domain}/domain.json`:

```json
{
  "domain_id": "cooking",
  "domain_name": "Cooking",
  "description": "Recipes and cooking techniques",
  "persona": "researcher",
  "enable_web_search": true,
  "temperature": 0.7,
  "plugins": [
    {
      "plugin_id": "researcher",
      "module": "plugins.research.research_specialist",
      "class": "ResearchSpecialistPlugin",
      "enabled": true,
      "config": {
        "enable_web_search": true,
        "max_research_steps": 10
      }
    }
  ],
  "enrichers": [
    {
      "module": "plugins.enrichers.llm_enricher",
      "class": "LLMEnricher",
      "enabled": true,
      "config": {
        "mode": "enhance",
        "temperature": 0.7
      }
    }
  ]
}
```

**Key Configuration Options**:
- `persona` - "poet", "librarian", or "researcher"
- `enable_web_search` - Enable DuckDuckGo search (researcher persona)
- `temperature` - LLM temperature (0.0-1.0)
- `plugins` - Plugin configuration for the domain
- `enrichers` - Response enrichment plugins

### Adding a New Domain

1. Create domain directory:
```bash
mkdir -p universes/MINE/domains/my_topic
```

2. Create `domain.json` with persona configuration

3. Add `patterns.json` with initial patterns

4. Reload universe via API or restart server

### For More Information

See [PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md) for:
- Detailed plugin interface documentation
- Example implementations
- Adding new domains with plugins
- Testing and troubleshooting plugins

---

## Semantic Search

ExFrame v1.5.0 features **pure semantic search** using SentenceTransformers embeddings, enabling the system to find patterns based on meaning rather than keyword matching.

### How It Works

1. **Query Encoding**: User query is encoded to a 384-dimensional vector using all-MiniLM-L6-v2
2. **Similarity Computation**: Cosine similarity is computed between query and all pattern embeddings
3. **Ranking**: Patterns are ranked by similarity score (0-1 range, higher = more related)
4. **Results**: Top patterns returned with semantic scores visible in traces

### Example

**Query**: "How do I use a hammer?"

**Results**:
| Pattern | Semantic Score |
|---------|---------------|
| How do I hammer in a nail? | 0.7007 |
| How do I build a simple shelf? | 0.2882 |
| Laying the Foundation: How to Build a Floor | 0.1542 |

**Note**: "hammer in a nail" has the highest semantic similarity even though both queries contain "hammer" - the model understands the meaning.

### Configuration

**Model**: all-MiniLM-L6-v2 (384-dimensional vectors)

---

## Persona System (Phase 1)

ExFrame uses a **persona-based architecture** where each domain is assigned one of three AI personas that determine how queries are processed.

### The Three Personas

| Persona | Data Source | Use Cases | Show Thinking |
|---------|-------------|-----------|---------------|
| **Poet** | Void (pure generation) | Creative writing, stories, poems | No |
| **Librarian** | Library (local documents) | Technical docs, how-to guides, knowledge base | Yes |
| **Researcher** | Internet (web search) | Current events, research, analysis | Yes |

### Persona Details

**Poet (void)**
- Pure LLM generation with no external sources
- Best for creative content generation
- No document retrieval or web search
- Example domains: poetry, creative writing

**Librarian (library)**
- Searches local document library
- Shows reasoning process (thinking)
- Semantic document search with relevance ranking
- Example domains: exframe (docs), technical documentation, API references

**Researcher (internet)**
- Searches the web for current information
- Shows reasoning process (thinking)
- Optional web search confirmation
- Example domains: news, research, analysis

### Setting a Persona

In `domain.json`:
```json
{
  "domain_id": "example",
  "domain_name": "Example Domain",
  "persona": "librarian",
  "library_base_path": "/app/project/docs"
}
```

Or via the UI:
1. Go to Domains → Edit Domain
2. Select persona from dropdown (poet/librarian/researcher)
3. Configure persona-specific settings (library path, etc.)
4. Save

### Pattern Override

Domains with local patterns (patterns.json) can override the persona behavior:
- If local patterns match the query → use local patterns
- If no local patterns match → fall back to persona's data source

This allows hybrid domains that have curated knowledge plus persona-backed fallback.

### API Endpoints

#### Check Embedding Status
```bash
curl http://localhost:3000/api/embeddings/status
```

#### Generate Embeddings
```bash
curl -X POST "http://localhost:3000/api/embeddings/generate?domain={domain}"
```

#### Adjust Search Weights (Advanced)
```bash
curl -X POST http://localhost:3000/api/embeddings/weights \
  -H "Content-Type: application/json" \
  -d '{"semantic": 1.0, "keyword": 0.0}'
```

### Pattern Encoding

Patterns are encoded using **whole document embedding** (no chunking):

1. **High-priority fields** (always included): Name, Solution
2. **Secondary fields** (if space permits): Description, Problem, Origin query, Tags
3. **Token limit**: 256 tokens (all-MiniLM-L6-v2 constraint)
4. **Truncation**: If exceeds limit, keeps name + solution[:1500] only

For more details, see [ARCHITECTURE.md](ARCHITECTURE.md#semantic-document-search).

---

## Scope Boundaries

ExFrame supports **per-domain scope boundaries** to prevent domains from answering questions outside their expertise. This is particularly useful for specialized domains like ExFrame that should only answer questions about their specific topic.

### How It Works

**Scope Configuration** (in `domain.json`):
```json
{
  "plugins": [{
    "config": {
      "scope": {
        "enabled": true,
        "min_confidence": 0.0,
        "in_scope": [
          "ExFrame architecture and design",
          "Plugin system (Router, Specialist, Enricher, Formatter)",
          "Domain types 1-5 and their configurations"
        ],
        "out_of_scope": [
          "General Python questions (syntax, language features)",
          "Other frameworks (Django, Flask, FastAPI internals)",
          "Infrastructure best practices (Docker, Kubernetes, networking)"
        ],
        "out_of_scope_response": "This question is outside ExFrame's documentation scope..."
      }
    }
  }]
}
```

**Query Flow:**
```
User Query
    ↓
Specialist checks scope boundaries
    ↓
Query contains out-of-scope keywords?
    ├─ YES → Reject with out_of_scope_response
    └─ NO  → Process normally
```

**Scope Checking:**
- **Explicit keywords**: Direct match against `out_of_scope` list
- **Framework detection**: Django, Flask, React, Kubernetes, etc.
- **Relevance threshold**: Reject if max_relevance < 0.3 AND many files searched with few matches
- **Routing**: Reject (not route to generalist) - domain-specific behavior

### Configuration

**Location:** `plugins[0].config.scope` in `domain.json`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | false | Enable scope checking |
| `min_confidence` | float | 0.0 | Minimum confidence for in-scope queries |
| `in_scope` | array | [] | Allowed topics |
| `out_of_scope` | array | [] | Blocked topics |
| `out_of_scope_response` | string | Default message | Rejection message |

**Scope Flexibility:** Per-domain, not domain-type specific. Each domain configures its own boundaries.

### Example: ExFrame Domain

The ExFrame domain uses scope boundaries to:
- Reject questions about Django, Flask, React, etc.
- Reject general Python syntax questions
- Focus only on ExFrame architecture, configuration, and usage
- Provide helpful rejection messages guiding users to appropriate resources

**Result:** "Gliznozzle" and "axelrod" queries are properly rejected as out-of-scope.

---

## Self-Healing Features

ExFrame includes a **built-in contradiction detection system** that automatically identifies documentation inconsistencies and provides a feedback loop for continuous improvement.

### How It Works

For **Librarian persona** domains, the system performs post-response analysis:

1. **Query Processing** → User asks a question
2. **Document Search** → System searches through all discovered documents (56+ files in ExFrame domain)
3. **Response Generation** → AI generates answer using document context
4. **Contradiction Detection** → System analyzes all documents for inconsistencies
5. **Logging** → Issues logged with severity levels (high/medium/low)
6. **Feedback Loop** → Save explanations as patterns → detector learns context

### Contradiction Detector Features

**Automatic Analysis:**
- Scans all discovered documents after each query
- Identifies direct contradictions, ambiguities, outdated info, terminology mismatches
- Categorizes by severity and suggests fixes

**Severity Levels:**
| Severity | Action | Description |
|----------|--------|-------------|
| **HIGH** | flag_for_immediate_review | Direct contradictions that could cause incorrect answers |
| **MEDIUM** | schedule_cleanup | Ambiguous information where answers are still valid but unclear |
| **LOW** | log_only | Minor terminology inconsistencies that don't affect accuracy |

**Smart Context Detection:**
- Reads `INDEX.md` first to understand historical naming (EEFrame → ExFrame)
- Recognizes that internal infrastructure names (`eeframe-app`, `eeframe-*` volumes) are intentional
- Distinguishes between user-facing names (ExFrame) and internal plumbing

**Log Location:**
```
/app/logs/contradictions/
├── contradictions.json    # Structured log for analysis
└── contradictions.log     # Human-readable format
```

### The Feedback Loop

This is the **self-healing** mechanism in action:

```
┌─────────────────────────────────────────────────────────────┐
│              SELF-HEALING DOCUMENTATION WORKFLOW             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. QUERY ──────────────────────────────────────┐           │
│     User: "What is ExFrame?"                    │           │
│                                                  │           │
│  2. SEARCH ──────────────────────────────────┐  │           │
│     Find relevant documents (566 files)      │  │           │
│                                             │  │           │
│  3. RESPOND ──────────────────────────────┐ │  │           │
│     AI generates answer                   │ │  │           │
│                                          │ │  │           │
│  4. DETECT ───────────────────────────┐ │ │  │           │
│     Find contradictions               │ │ │  │           │
│     Output: 3 issues found           │ │ │  │           │
│                                       │ │ │  │           │
│  5. EXPLAIN ───────────────────────┐ │ │ │  │           │
│     AI: "The naming is intentional │ │ │ │  │           │
│     because of historical reasons" │ │ │ │  │           │
│                                    │ │ │ │  │           │
│  6. SAVE PATTERN ───────────────┐ │ │ │ │  │           │
│     Store explanation in         │ │ │ │ │  │           │
│     domain as pattern            │ │ │ │ │  │           │
│                                  │ │ │ │ │  │           │
│  7. REPEAT ──────────────────────┼─┼─┼─┼─┼─────────────┘
│     Next query on same topic ────┘ │ │ │ │
│     Detector reads the pattern ─────┘ │ │
│     Already knows the answer ──────────┘ │
│     Finds NEW contradictions ────────────┘
│     (previously addressed ones are gone) │
│                                             │
│  Each iteration improves the documentation!│
└─────────────────────────────────────────────┘
```

**Example:**

**First Query:**
```
Query: "How do I install ExFrame?"
Found: 2 issues
  [MEDIUM] Docker service name confusion
  [LOW] Installation path inconsistency
```

**Save Explanation as Pattern:**
```json
{
  "name": "ExFrame Installation Naming",
  "problem": "Confusion about Docker service names",
  "solution": "Service names like 'eeframe-app' are internal Docker infrastructure
  for data preservation. ExFrame is installed and run entirely via Docker Compose.
  This is intentional and documented in INDEX.md under Historical Nomenclature."
}
```

**Second Query:**
```
Query: "How do I install ExFrame?"
Found: 1 issue
  [LOW] Python version alignment (>=3.11 vs 3.11-slim)
```

The HIGH and MEDIUM issues are **gone** because the pattern now provides context!

### Using the Feedback Loop

**For Documentation Maintenance:**

1. **Run queries** on your Librarian persona domains regularly
2. **Review contradiction logs** at `/app/logs/contradictions/`
3. **Have AI explain** the contradictions
4. **Save explanations** as patterns in the domain
5. **Watch the system learn** - contradictions decrease over time

**For Domain Owners:**

- The contradiction detector runs **automatically** after every Librarian persona query
- No configuration needed - just query your domain normally
- Logs are persistent and searchable
- Patterns are immediately available for future queries

### Technical Details

**Implementation:** `generic_framework/plugins/enrichers/llm_enricher.py`
- Method: `_detect_and_log_contradictions()`
- Triggered: After Librarian persona query response generation
- Scope: Analyzes top 20 documents per query
- Format: JSON + plain text logs

**Nomenclature Detection:**
- Searches for INDEX.md or nomenclature docs first
- Extracts historical naming context
- Adds to prompt with instructions that historical refs are intentional
- Prevents false positives on EEFrame/ExFrame differences

### Managing Contradiction Logs

**Log Location:** `/app/logs/contradictions/`

```bash
/app/logs/contradictions/
├── contradictions.json    # Structured log (JSON format)
└── contradictions.log     # Human-readable format
```

#### Viewing Logs

**View all recent contradictions:**
```bash
# Human-readable format (recommended)
docker exec eeframe-app cat /app/logs/contradictions/contradictions.log

# JSON format (for analysis)
docker exec eeframe-app cat /app/logs/contradictions/contradictions.json | jq '.'
```

**Follow logs in real-time:**
```bash
# Watch for new contradictions as queries are processed
docker exec eeframe-app tail -f /app/logs/contradictions/contradictions.log
```

**Show last 20 entries:**
```bash
docker exec eeframe-app tail -n 20 /app/logs/contradictions/contradictions.log
```

**Filter by severity:**
```bash
# Show only HIGH severity issues
docker exec eeframe-app grep "\[HIGH\]" /app/logs/contradictions/contradictions.log

# Show only MEDIUM severity issues
docker exec eeframe-app grep "\[MEDIUM\]" /app/logs/contradictions/contradictions.log

# Show LOW severity issues
docker exec eeframe-app grep "\[LOW\]" /app/logs/contradictions/contradictions.log
```

**Search for specific topics:**
```bash
# Search for contradictions about "naming"
docker exec eeframe-app grep -i "naming" /app/logs/contradictions/contradictions.log

# Search for contradictions about "docker"
docker exec eeframe-app grep -i "docker" /app/logs/contradictions/contradictions.log
```

**Count issues by severity:**
```bash
# Count HIGH issues
docker exec eeframe-app grep -c "\[HIGH\]" /app/logs/contradictions/contradictions.log

# Count MEDIUM issues
docker exec eeframe-app grep -c "\[MEDIUM\]" /app/logs/contradictions/contradictions.log

# Count LOW issues
docker exec eeframe-app grep -c "\[LOW\]" /app/logs/contradictions/contradictions.log
```

#### Clearing Logs

**Clear all logs:**
```bash
docker exec eeframe-app sh -c "echo '' > /app/logs/contradictions/contradictions.log"
docker exec eeframe-app sh -c "echo '[]' > /app/logs/contradictions/contradictions.json"
```

**Archive before clearing:**
```bash
# Create archive with timestamp
docker exec eeframe-app sh -c "cp /app/logs/contradictions/contradictions.log /app/logs/contradictions/contradictions_$(date +%Y%m%d_%H%M%S).log"

# Then clear
docker exec eeframe-app sh -c "echo '' > /app/logs/contradictions/contradictions.log"
```

#### Quick Reference

| Command | Purpose |
|---------|---------|
| `cat /app/logs/contradictions/contradictions.log` | View all log entries |
| `tail -f /app/logs/contradictions/contradictions.log` | Follow logs in real-time |
| `tail -n 20 /app/logs/contradictions/contradictions.log` | Show last 20 entries |
| `grep "\[HIGH\]" /app/logs/contradictions/contradictions.log` | Filter HIGH severity |
| `grep -c "\[HIGH\]" /app/logs/contradictions/contradictions.log` | Count HIGH issues |
| `echo '' > /app/logs/contradictions/contradictions.log` | Clear log file |

**Pro Tip:** Regularly review HIGH and MEDIUM severity issues to keep documentation accurate. Save explanations as patterns to teach the system and reduce future contradictions.

---

**Complete step-by-step guide for deploying ExFrame from GitHub to a fresh Linux system.**

### What Must Be Running on Host

**Required:**
- **Docker Engine** (official, NOT snap) - Container runtime
- **Docker Compose v2** - Multi-container orchestration
- **Git** - For cloning the repository
- **Internet Connection** - For Docker image pulls and API access

**Optional (for LLM features):**
- **OpenAI API Key** or compatible LLM service (GLM, Anthropic Claude, etc.)

### Verify Host Prerequisites

```bash
# 1. Check if Docker is installed (must be official, NOT snap)
docker --version
# Expected output: Docker version 24.0.0 or higher

# IMPORTANT: If you see snap Docker, remove it first:
snap list docker  # If this shows docker, you have snap version
sudo snap remove docker

# 2. Check Docker Compose version
docker compose version
# Expected output: Docker Compose version v2.x.x
# Note: Use "docker compose" (space), NOT "docker-compose" (hyphen)

# 3. Check if git is installed
git --version
# If not installed: sudo apt-get install git -y
```

### Install Docker (if not already installed)

```bash
# Install official Docker Engine (NOT snap)
curl -fsSL https://get.docker.com | sh

# Add your user to docker group (required for running without sudo)
sudo usermod -aG docker $USER

# IMPORTANT: Log out and log back in for group change to take effect
# Or use: newgrp docker
```

### Clone and Deploy ExFrame

```bash
# Step 1: Clone the repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# Step 2: Configure environment variables
cp .env.example .env
nano .env  # Edit with your API key (see below)

# Step 3: Start the application
docker compose up -d

# Step 4: Verify containers are running
docker compose ps
# You should see: eeframe-app (Up), plus monitoring containers

# Step 5: Check application logs
docker compose logs eeframe-app | tail -20
# Look for: "ExFrame Runtime Ready" and "Uvicorn running"
```

### Configure LLM (.env file)

The `.env` file configures your LLM provider. **All domains use this global configuration by default.**

**How it works:** ExFrame uses OpenAI-compatible APIs for all LLM providers. No additional dependencies needed - the `openai` and `anthropic` packages work with any provider that offers an OpenAI-compatible endpoint.

#### Quick Setup - Common Providers

**For OpenAI GPT (default):**
```bash
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**For Zhipu GLM:**
```bash
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-zhipu-api-key
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

**For Anthropic Claude:**
```bash
LLM_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=sk-ant-your-anthropic-api-key-here
OPENAI_BASE_URL=https://api.anthropic.com/v1
```

**For local LLM (Ollama):**
```bash
LLM_MODEL=llama3
OPENAI_API_KEY=not-needed
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
```

#### Configuration Explained

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `LLM_MODEL` | Model name for all domains | No | `glm-4.7` |
| `OPENAI_API_KEY` | Your API key | Yes* | - |
| `OPENAI_BASE_URL` | API endpoint URL | No | OpenAI |

*Required for LLM features. System works without it for pattern-only queries.

#### Advanced: Per-Domain Model Override

If you want different models for different domains (e.g., use a cheaper model for simple domains):

**Option 1: Web UI**
1. Go to **Domains** → Select domain → **Edit**
2. Find **Enrichers** → **LLM Enricher** → **model**
3. Set to your preferred model

**Option 2: Edit domain config**
```bash
nano universes/default/domains/{domain}/domain_config.json
# Find "enrichers" section and add "model": "your-model"
```

**Model Priority:**
1. `LLM_MODEL` in `.env` (global default)
2. Domain config `model` field (per-domain override)
3. Hardcoded default: `glm-4.7`

#### Optional: Local Models for Fast Journaling (Advanced)

**Note:** Local models are entirely optional. ExFrame works perfectly with remote models only (OpenAI, Anthropic, Zhipu). Local models provide a speed optimization for the poet persona's journal entries only (~230ms vs ~4s).

If you use the poet persona for journaling and want faster responses, you can optionally run a local model through **DMR (Docker Model Runner)**.

##### What is DMR?

DMR (Docker Model Runner) is a local model server for advanced users who want to optimize journal entry speed.

**Hardware Requirements:**
- GPU: NVIDIA with 8GB+ VRAM (recommended), OR
- CPU: 16-core+ with 32GB+ RAM
- Disk: 10GB+ for model files

**When to use:**
- You use poet persona for frequent journaling
- You want ~230ms responses instead of ~4s
- You have the hardware available

**When NOT to use:**
- Limited hardware (no GPU, <16GB RAM)
- Occasional journaling (remote is fine)
- Any other persona (already uses remote models)

##### Local vs Remote: The Reality

| What | Uses | Speed | Setup |
|------|------|-------|-------|
| **Librarian persona** | Remote model (.env) | ~4s | ✅ Default |
| **Researcher persona** | Remote model (.env) | ~4s | ✅ Default |
| **Poet journal entries** | Remote model (.env) | ~4s | ✅ Default |
| **Poet ** searches** | Remote model (.env) | ~4s | ✅ Default |
| **Poet journal (optimized)** | Local llama3.2 | ~230ms | ⚠️ Optional, requires GPU |

**Bottom line:** 99% of ExFrame uses remote models. Local models only speed up poet journal entries.

##### GPU Memory Considerations

**CRITICAL**: Local models consume GPU VRAM. Running multiple models simultaneously can cause crashes.

**Memory Requirements** (approximate):
| Model Size | VRAM Needed | Example Models |
|------------|-------------|----------------|
| 3B params | ~2GB | llama3.2 |
| 7-8B params | ~4.5GB | llama3 8B, qwen3 8B |
| 13B params | ~8GB | llama2 13B |
| 70B params | ~40GB | llama3 70B |

**GPU Memory Strategy:**
- **Single model only**: Keep one local model loaded at a time
- **Use remote models** for complex tasks to free GPU memory
- **Dual-model routing**: Use fast local for simple, remote for complex

**Common Error:**
```
cudaMalloc failed: out of memory
llama_model_load: error loading model
```

**Solution**: Use smaller models or switch to remote models for complex tasks.

##### Configuring DMR in Domain

To use a local DMR model for a specific domain, add `llm_config` to the domain's `domain.json`:

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

**DMR Model Names:**
- `ai/llama3.2` - Fast 3.2B model (~230ms)
- `ai/llama3` - Capable 8B model
- `ai/qwen3` - Capable 8B model (Chinese/English)

**Location**: `universes/{universe}/domains/{domain}/domain.json`

##### Dual-Model Routing (Advanced)

For domains that need **both fast responses and complex reasoning**, ExFrame supports automatic model routing based on query type.

**Use Case**: Journal domain (poet persona)
- Regular entries: "buy milk" → Fast local model (230ms)
- Search queries: "** what did I buy?" → Smart remote model (synthesis capability)

**How It Works:**
1. Regular queries use the local model from `llm_config`
2. Queries starting with `**` automatically use the remote model from `.env`
3. Only one GPU model runs at a time (no memory conflicts)

**Configuration:**
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

With `.env` configured for remote model:
```bash
LLM_MODEL=glm-4.7
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.z.ai/api/anthropic
```

**Result:**
- Journal entries processed by fast local llama3.2 (~230ms)
- Search queries processed by capable remote glm-4.7 (~4s)
- No GPU memory conflicts (only one local model loaded)

##### Troubleshooting Local Models

**Problem**: Model loads slowly on first query

**Solution**: This is normal. First query loads model into memory (~5-10s), subsequent queries are fast (~230ms).

---

**Problem**: `CUDA out of memory` error

**Solution**:
1. Check GPU memory: `nvidia-smi`
2. Use smaller model (3.2B instead of 8B)
3. Switch to remote model for that domain
4. Close other GPU applications

---

**Problem**: DMR not responding

**Solution**:
```bash
# Check if DMR is running
curl http://model-runner.docker.internal:12434/v1/models

# If not responding, check DMR container logs
docker logs model-runner
```

---

**For detailed model selection strategy**, see [MODEL_STRATEGY.md](MODEL_STRATEGY.md).

### Access the Application

Once containers are running, access ExFrame at:

- **Main Application**: `http://localhost:3000` or `http://<your-server-ip>:3000`
- **API Documentation**: `http://localhost:3000/docs`
- **Health Check**: `http://localhost:3000/health`

**Monitoring Stack (optional):**
- **Grafana Dashboards**: `http://localhost:3001` (admin/admin)
- **Prometheus Metrics**: `http://localhost:9090`
- **Loki Logs**: `http://localhost:3100`

### Verify Installation

```bash
# 1. Check health endpoint
curl http://localhost:3000/health
# Expected: {"status":"healthy"}

# 2. List domains
curl http://localhost:3000/api/domains
# Expected: JSON array with domain IDs

# 3. View container status
docker compose ps
# All containers should show "Up" status

# 4. Check logs for errors
docker compose logs eeframe-app | grep -i error
# Should return nothing (no errors)
```

### Troubleshooting Fresh Install

**Problem**: `docker compose: command not found`

**Solution**: You have Docker Compose v1. Install v2:
```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

**Problem**: `permission denied while trying to connect to the Docker daemon`

**Solution**: Your user isn't in docker group or hasn't reloaded:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Option 1: Log out and log back in
# Option 2: Use newgrp to reload group for current session
newgrp docker
```

**Problem**: Port 3000 already in use

**Solution**:
```bash
# Find what's using port 3000
sudo lsof -ti:3000

# Kill the process (replace PID with actual process ID)
sudo kill -9 <PID>

# Restart ExFrame
docker compose up -d
```

**Problem**: Containers start but application doesn't respond

**Solution**: Check logs and rebuild:
```bash
# View logs
docker compose logs eeframe-app

# Rebuild from scratch (fixes most issues)
docker compose down
docker compose build --no-cache eeframe-app
docker compose up -d
```

### Quick Start Commands (Reference)

```bash
# Clone and start (one-liner after prerequisites)
git clone https://github.com/orangelightening/ExFrame.git && cd ExFrame && cp .env.example .env && docker compose up -d

# Stop application
docker compose down

# Restart application
docker compose restart

# View logs
docker compose logs -f eeframe-app

# Rebuild after code changes
docker compose build --no-cache eeframe-app && docker compose up -d
```

---

## Quick Start (Additional Information)

### Prerequisites

**IMPORTANT**: You must use the official Docker Engine. The snap version of Docker has known issues with bind mounts that will prevent this application from working correctly.

Check your Docker installation:
```bash
# Check if you have snap Docker (BAD - will not work properly)
which snap | grep -q docker && snap list docker

# If snap Docker is installed, remove it first:
sudo snap remove docker

# Install official Docker Engine:
curl -fsSL https://get.docker.com | sh

# Add your user to docker group:
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

**Additional Requirements:**
- LLM API key and model (GLM, OpenAI, Anthropic, etc.) - **optional**, for LLM enrichment features
- System works for pattern-based queries without LLM configuration

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/orangelightening/ExFrame.git
cd ExFrame

# 2. Configure environment (OPTIONAL - for LLM features)
cp .env.example .env

# Edit .env with your LLM credentials
# The system works without LLM config for pattern-based queries
#
# For GLM (z.ai) - RECOMMENDED:
#   - Set LLM_MODEL=glm-4.7
#   - Set OPENAI_API_KEY=your-glm-api-key
#   - Set OPENAI_BASE_URL=https://api.z.ai/api/anthropic
#
# For OpenAI:
#   - Set LLM_MODEL=gpt-4o-mini
#   - Set OPENAI_API_KEY=your-openai-api-key
#
# For Anthropic Claude:
#   - Set LLM_MODEL=claude-3-5-sonnet-20241022
#   - Set OPENAI_API_KEY=your-anthropic-api-key
#
nano .env  # or use your preferred editor

# 3. Start the application
# NOTE: Use "docker compose" (space), NOT "docker-compose" (hyphen)
docker compose up -d

# 4. Verify containers are running
docker compose ps

# 5. Check the logs if needed
docker compose logs -f eeframe-app
```

**Access URLs**:
- **ExFrame UI**: `http://localhost:3000` (main application)
- **API Docs**: `http://localhost:3000/docs` (Swagger UI)
- **Health Check**: `http://localhost:3000/health`
- **Prometheus**: `http://localhost:9090` (metrics)
- **Grafana**: `http://localhost:3001` (dashboards, admin/admin)
- **Loki**: `http://localhost:3100` (logs)

---

## Web Interface

### Navigation Tabs

1. **Assistant**: Query the AI assistant with pattern-based knowledge
2. **Patterns**: Browse and search knowledge patterns with full detail views
3. **Traces**: View historical query traces and debugging information
4. **Ingestion**: Extract patterns from URLs (beta)
5. **Domains**: Manage domains, specialists, and configuration
6. **Universes**: Manage knowledge universes - create, load, switch, and export
7. **Diagnostics**: System health, search metrics, and pattern analysis

### Using the Assistant

1. Select a domain from the dropdown (default: llm_consciousness)
2. The current universe is displayed next to "Universe:"
3. Type your question in the text area
4. Click "Query" or press Enter
5. View the AI response with:
   - Confidence score
   - Which specialist handled it
   - Patterns used
   - Processing time
   - Optional trace (enable "Include Trace" checkbox)

### Viewing Pattern Details

1. Go to the **Patterns** tab
2. Select a domain from the dropdown
3. Browse the pattern cards
4. **Click on any pattern** to see full details:
   - Problem addressed
   - Solution steps
   - Conditions and prerequisites
   - Related patterns
   - Tags and metadata
   - Access statistics

### Managing Domains

1. Go to the **Domains** tab
2. View all configured domains with:
   - Pattern counts
   - Specialist listings
   - Categories and tags
   - Load status
3. Click **Create Domain** to add a new domain
4. Click **Edit** (pencil icon) to modify a domain

### Managing Universes

1. Go to the **Universes** tab
2. View current universe with:
   - Universe name and active status
   - Total domains and patterns
3. Browse available universes with:
   - Domain and pattern counts
   - Active status indicators
   - Switch and Details buttons
4. Create new universes with:
   - Universe ID
   - Optional description
5. Switch between universes instantly

### Using Diagnostics

1. Go to the **Diagnostics** tab
2. Click **Load Diagnostics** to refresh
3. View system health:
   - Pattern storage status
   - Knowledge base health
   - Search performance metrics
   - Disk space usage
   - Pattern health scores
4. Review search metrics:
   - Total searches and success rate
   - Average confidence and latency
   - P50/P95/P99 duration percentiles
   - LLM fallback rate

---

## System Architecture

### Single-Container Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    eeframe-app (Port 3000)                  │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Backend                                          │
│  ├── Domain Management (cooking, llm_consciousness)       │
│  ├── Specialist Engine (pattern matching)                   │
│  ├── Knowledge Base (JSON patterns)                        │
│  ├── Query Processing (LLM integration)                    │
│  └── Static Frontend (Alpine.js + Tailwind)                │
├─────────────────────────────────────────────────────────────┤
│  Data Persistence (Bind Mounts)                            │
│  ├── ./data/patterns → /app/data/patterns                  │
│  └── ./data/domains.json → /app/data (via API)            │
└─────────────────────────────────────────────────────────────┘
```

### Monitoring Stack (Optional)

- **Prometheus** (9090): Metrics collection
- **Grafana** (3001): Visualization dashboards
- **Loki** (3100): Log aggregation
- **Promtail**: Log shipping agent

---

## Project Structure

```
eeframe/
├── generic_framework/          # Main framework
│   ├── api/                    # FastAPI application
│   │   └── app.py             # Main app with all endpoints
│   ├── core/                   # Core interfaces
│   │   ├── domain.py          # Domain base class
│   │   ├── specialist.py      # Specialist base class
│   │   └── knowledge_base.py  # Knowledge base interface
│   ├── domains/                # Domain implementations
│   │   ├── cooking/           # Cooking domain
│   │   └── llm_consciousness/ # LLM consciousness domain
│   ├── assist/                 # Assistant engine
│   │   └── engine.py          # Query orchestration
│   ├── knowledge/              # Knowledge base implementations
│   │   └── json_kb.py         # JSON-based knowledge base
│   ├── frontend/               # Web UI
│   │   └── index.html         # Single-page Alpine.js app
│   └── data/                   # Runtime data (domains.json)
├── data/                       # Pattern storage (bind mounted)
│   └── patterns/               # All domain patterns (JSON)
│       ├── cooking/
│       ├── llm_consciousness/
│       └── {domain}/           # Add new domains here
├── config/                     # Monitoring configurations
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── promtail/
├── docker-compose.yml          # Docker deployment
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Configuration (all domains use this by default)
LLM_MODEL=glm-4.7              # Global default model
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# For local LLMs (Ollama, etc.)
# LLM_MODEL=llama3
# OPENAI_BASE_URL=http://host.docker.internal:11434/v1

# Application Settings
LOG_LEVEL=INFO
```

**See "Configure LLM" section above for provider-specific examples.**

### Domain Configuration

Domains are configured in two ways:

1. **Code-based**: Edit `generic_framework/api/app.py` in the `startup_event()` function
2. **UI-based**: Create domains through the Domains tab (stored in `data/domains.json`)

---

## API Reference

### Health Check

```bash
curl http://localhost:3000/health
```

### List Domains

```bash
curl http://localhost:3000/api/domains
```

### Get Domain Info

```bash
curl http://localhost:3000/api/domains/{domain_id}
```

### Query a Domain

```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I detect when an LLM is hallucinating?",
    "domain": "llm_consciousness",
    "include_trace": true
  }'
```

### List Patterns

```bash
curl "http://localhost:3000/api/domains/{domain_id}/patterns"
```

### Get Pattern Details

```bash
curl "http://localhost:3000/api/domains/{domain_id}/patterns/{pattern_id}"
```

### List Specialists

```bash
curl "http://localhost:3000/api/domains/{domain_id}/specialists"
```

### Query History

```bash
curl "http://localhost:3000/api/history?domain={domain_id}&limit=10"
```

### Query Traces

```bash
curl "http://localhost:3000/api/traces?domain={domain_id}&limit=20"
```

### Get Trace Detail

```bash
curl "http://localhost:3000/api/traces/{query_id}"
```

### Domain CRUD (Admin)

```bash
# List all domains
curl http://localhost:3000/api/admin/domains

# Get domain config
curl http://localhost:3000/api/admin/domains/{domain_id}

# Create domain
curl -X POST http://localhost:3000/api/admin/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": "my_domain",
    "domain_name": "My Knowledge Domain",
    "description": "Domain description",
    "categories": ["category1", "category2"],
    "tags": ["tag1", "tag2"],
    "specialists": [
      {
        "specialist_id": "specialist_1",
        "name": "Expert Specialist",
        "description": "Specializes in X",
        "expertise_keywords": ["keyword1", "keyword2"],
        "expertise_categories": ["category1"],
        "confidence_threshold": 0.6
      }
    ]
  }'

# Update domain
curl -X PUT http://localhost:3000/api/admin/domains/{domain_id} \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "Updated Domain Name",
    "description": "Updated description"
  }'

# Delete domain
curl -X DELETE http://localhost:3000/api/admin/domains/{domain_id}
```

---

## Adding New Domains

### Method 1: Through the UI (Recommended)

1. Go to the **Domains** tab
2. Click **Create Domain**
3. Fill in the form:
   - **Domain ID**: Lowercase with underscores (e.g., `my_domain`)
   - **Domain Name**: Human-readable name
   - **Description**: What the domain covers
   - **Categories**: Knowledge categories
   - **Tags**: Searchable tags
   - **Persona**: Choose AI behavior:
     - **poet** - Pure generation (no external sources)
     - **librarian** - Document search (local library)
     - **researcher** - Web search (internet)
   - **Pattern Override**: Enable to check local patterns first
   - **Library Path**: For librarian persona, path to documents
4. Click **Save Domain**

The persona determines how queries are processed. Pattern override allows curated patterns to take precedence over persona behavior.

### Method 2: Code-Based (Advanced)

1. Create domain directory:

```bash
mkdir -p generic_framework/domains/mydomain/specialists
```

2. Create domain class (`generic_framework/domains/mydomain/domain.py`):

```python
from core.domain import Domain, DomainConfig
from core.specialist import SpecialistConfig
from typing import Dict, List, Any

class MyDomain(Domain):
    def __init__(self, config: DomainConfig):
        self.config = config
        self._specialists = {}

    @property
    def domain_id(self) -> str:
        return self.config.domain_id

    @property
    def domain_name(self) -> str:
        return self.config.domain_name

    async def initialize(self) -> None:
        """Initialize domain resources."""
        pass

    async def cleanup(self) -> None:
        """Cleanup domain resources."""
        pass

    def list_specialists(self) -> List[str]:
        return list(self._specialists.keys())

    def get_specialist(self, specialist_id: str):
        return self._specialists.get(specialist_id)

    def add_specialist(self, specialist_id: str, specialist) -> None:
        self._specialists[specialist_id] = specialist
```

3. Create specialists in `generic_framework/domains/mydomain/specialists/`

4. Register in `generic_framework/api/app.py`:

```python
from domains.mydomain.domain import MyDomain

# In startup_event()
DomainFactory.register_domain(MyDomain)

my_config = DomainConfig(
    domain_id="mydomain",
    domain_name="My Domain",
    version="1.0.0",
    description="My custom knowledge domain",
    pattern_storage_path=get_storage_path("mydomain"),
    pattern_format="json",
    categories=["category1"],
    tags=["tag1"]
)

my_domain = MyDomain(my_config)
await my_domain.initialize()

engines["mydomain"] = GenericAssistantEngine(my_domain)
await engines["mydomain"].initialize()
```

---

## Creating a Librarian Domain

Librarian domains provide **document-based search** over a directory of markdown files. This is perfect for:
- Project documentation
- Knowledge bases
- Technical notes
- Research collections

### Quick Start

1. **Prepare Your Document Directory**
   ```bash
   # Example: Create a docs directory with some markdown files
   mkdir -p /home/user/my-project/docs
   echo "# Getting Started" > /home/user/my-project/docs/intro.md
   echo "# API Reference" > /home/user/my-project/docs/api.md
   ```

2. **Create ignored.md (IMPORTANT - Security Feature)**

   Create an `ignored.md` file in your library directory to exclude sensitive files and directories. **This is a security feature that prevents the librarian from accessing secrets, credentials, and unwanted files.**

   **Location**: Place `ignored.md` in the same directory as your documents (the `library_base_path`).

   **Example ignored.md** (recommended for project documentation):
   ```bash
   # Ignored Files and Directories
   # One pattern per line - substring matching
   # Lines starting with # are comments

   # SECURITY: Secrets and credentials
   .env
   .env.local
   .env.production
   secrets/
   credentials/
   api_keys/

   # Version control
   .git/

   # Python
   __pycache__/
   *.pyc
   venv/

   # Node
   node_modules/

   # IDE files
   .vscode/
   .idea/

   # Logs and temporary files
   *.log
   logs/
   temp/
   tmp/
   drafts/

   # Archives
   .archive/
   old/
   backup/

   # Binary files
   *.pdf
   *.zip
   ```

   **How it works:**
   - **Substring matching**: Pattern `drafts/` excludes any file path containing `drafts/`
   - **One pattern per line**: Each line is a separate exclusion pattern
   - **Comments**: Lines starting with `#` are ignored
   - **Case sensitive**: Patterns match exactly as written
   - **The `ignored.md` file itself is automatically excluded**

   **Security Test**: Try asking your librarian "What's in the .env file?" - it should explain what .env files are but NOT reveal your actual credentials. If it shows your API keys, add `.env` to `ignored.md`.

   **Important**: Files matching patterns in `ignored.md` are **completely invisible** to the librarian. They won't appear in search results or be loaded into context.

3. **Create Domain in UI**

   Go to **Domains** → **Create Domain**:
   - **Domain ID**: `my_docs` (lowercase with underscores)
   - **Domain Name**: "My Documentation"
   - **Description**: "Project documentation search"
   - **Persona**: Select **"Librarian"** from dropdown
   - **Library Base Path**: `/app/project/docs` (see path mapping below)
   - **Categories/Tags**: Optional

4. **Save and Test**

   - Save the domain
   - Go to **Assistant** tab
   - Select your new domain
   - **Uncheck** "Search Patterns" to use document search
   - Query: "What's in the documentation?"
   - The librarian will search your markdown files and provide answers

### Path Mapping for Docker (CRITICAL)

**The Tricky Part**: Docker containers can only access directories that are **mounted as volumes**. If your library is outside the ExFrame project directory, you must add a bind mount first.

#### Understanding Container Paths

When setting `library_base_path`, you specify paths **inside the container**, not on your host machine:

| Your Host Path | Container Path (use in domain config) | Status |
|----------------|---------------------------|--------|
| `./universes/MINE/docs` | `/app/universes/MINE/docs` | ✅ Already mounted |
| `./docs` (in project root) | `/app/project/docs` | ✅ Already mounted |
| `~/my-library` | ⚠️ **NOT accessible** | ❌ Needs bind mount |
| `/home/user/notes` | ⚠️ **NOT accessible** | ❌ Needs bind mount |

**Default bind mounts** (from docker-compose.yml):
```yaml
volumes:
  - .:/app/project          # Project root → /app/project
  - ./universes:/app/universes  # Universes → /app/universes
```

#### Using Existing Mounts (Easy)

If your library is **inside the ExFrame project directory**, it's already accessible:

**Example 1 - Project subdirectory:**
```bash
# Create library in project
mkdir -p ./my-library
echo "# Test Doc" > ./my-library/test.md

# In domain config, use:
library_base_path: /app/project/my-library
```

**Example 2 - Universe directory:**
```bash
# Create library in universe
mkdir -p ./universes/MINE/docs
echo "# Guide" > ./universes/MINE/docs/guide.md

# In domain config, use:
library_base_path: /app/universes/MINE/docs
```

#### Adding Custom Mounts (Advanced)

If your library is **outside the ExFrame project**, you must add a bind mount:

**Step 1: Edit docker-compose.yml**

Add your directory to the volumes section:
```yaml
services:
  eeframe-app:
    volumes:
      - .:/app/project
      - ./universes:/app/universes
      # ADD YOUR CUSTOM MOUNT HERE:
      - ~/my-notes:/app/my-notes:ro          # Read-only
      - /home/user/library:/app/library:ro   # Another example
```

**Format**: `HOST_PATH:CONTAINER_PATH:OPTIONS`
- `HOST_PATH`: Absolute path on your machine (use `~` for home directory)
- `CONTAINER_PATH`: Path inside container (can be anything under `/app/`)
- `:ro` = read-only (recommended for security)
- `:rw` = read-write (if you need to write files)

**Step 2: Restart container**
```bash
docker compose down
docker compose up -d
```

**Step 3: Verify mount worked**
```bash
# List files in mounted directory
docker exec eeframe-app ls -la /app/my-notes

# If you see files, it worked!
# If you see "No such file or directory", check docker-compose.yml
```

**Step 4: Use in domain config**
```
library_base_path: /app/my-notes
```

#### Common Mistakes

❌ **WRONG** - Using host paths in domain config:
```json
{
  "library_base_path": "~/my-library"  // Container can't access ~
}
```

❌ **WRONG** - Path not mounted:
```json
{
  "library_base_path": "/home/user/docs"  // Not in docker-compose.yml
}
```

✅ **CORRECT** - Using container path after mounting:
```yaml
# In docker-compose.yml:
volumes:
  - ~/my-library:/app/my-library:ro
```
```json
// In domain.json:
{
  "library_base_path": "/app/my-library"
}
```

#### Quick Reference

| Scenario | Solution |
|----------|----------|
| Library inside project directory | Use `/app/project/YOUR_DIR` - no changes needed |
| Library in universes directory | Use `/app/universes/YOUR_DIR` - no changes needed |
| Library outside project | Add bind mount to docker-compose.yml first |
| `~` or `$HOME` in path | Replace with absolute path or add bind mount |
| Permission denied | Add `:ro` suffix to mount for read-only access |

#### Verify Your Mount

After setting up, test that the container can access your files:
```bash
# Test if path exists
docker exec eeframe-app ls -la /app/YOUR_PATH

# Count markdown files
docker exec eeframe-app find /app/YOUR_PATH -name "*.md" | wc -l

# Check ignored.md is there
docker exec eeframe-app cat /app/YOUR_PATH/ignored.md
```

If any command fails, the path isn't accessible - check your docker-compose.yml bind mount.

### Pattern Search vs Document Search

The "Search Patterns" checkbox controls the librarian's behavior:

| Checkbox State | Behavior | Use When |
|----------------|----------|----------|
| **Checked** ✓ | Search patterns.json | You have structured patterns in the domain |
| **Unchecked** ☐ | Search document directory | You want to search your markdown files |

**Example workflow:**
```bash
# Query with document search (checkbox UNCHECKED)
# → Librarian searches all .md files in library_base_path
# → Returns answer citing actual document content

# Query with pattern search (checkbox CHECKED)
# → Librarian searches patterns.json
# → Returns structured pattern-based answers
```

### How Document Search Works

When you query with "Search Patterns" unchecked:

1. **Discovery**: System finds all `.md` files in `library_base_path` recursively
2. **Filtering**: Excludes patterns from `ignored.md` (security feature)
3. **Loading**: Loads up to 50 documents (50,000 chars each by default)
4. **Context Building**: All loaded documents provided to AI as context
5. **Response**: AI generates answer citing the actual documents

**Default Limits** (configurable per domain):
- **50 documents** maximum per query
- **50,000 characters** maximum per document
- Loads documents in filesystem order (no ranking yet)

**To customize limits**, add to your domain.json:
```json
{
  "max_library_documents": 100,
  "max_chars_per_document": 100000
}
```

**Performance Notes**:
- Documents are re-read on each query (no caching yet)
- Larger limits = slower queries but more complete context
- Use `ignored.md` to exclude unnecessary files for better performance

**Future improvements** (if needed):
- Semantic ranking to load most relevant documents first
- Document caching to avoid re-reading
- Incremental loading for very large libraries

### Example Domain Configuration

The resulting `domain.json` will include:

```json
{
  "domain_id": "my_docs",
  "domain_name": "My Documentation",
  "persona": "librarian",
  "library_base_path": "/app/project/docs",
  "enable_pattern_override": true
}
```

### Troubleshooting

**Problem**: Librarian returns generic answers, not referencing my documents

**Solution**:
1. Check `library_base_path` is correct (container path, not host path)
2. Verify "Search Patterns" checkbox is **unchecked**
3. Check logs: `docker logs eeframe-app --tail 50 | grep "document"`
4. Should see: "Loaded N documents for library search"

**Problem**: Librarian says "No documents found"

**Solution**:
1. Verify path exists in container: `docker exec eeframe-app ls -la /app/project/docs`
2. Check for `.md` files: `docker exec eeframe-app find /app/project/docs -name "*.md"`
3. Review `ignored.md` - might be excluding everything

**Problem**: Some documents are missing from search

**Solution**:
1. Check if they're in `ignored.md` - they may be intentionally excluded
2. Default limit is 50 documents - if you have more, increase `max_library_documents` in domain.json
3. Check if documents exceed 50k characters - increase `max_chars_per_document` if needed
4. Verify files are actually `.md` format: `docker exec eeframe-app find /app/YOUR_PATH -name "*.md" | wc -l`

**Problem**: Librarian shows my API keys or secrets

**Solution**:
1. **CRITICAL**: Add sensitive patterns to `ignored.md` immediately
2. Restart is NOT needed - changes take effect on next query
3. Test: Ask "What's in the .env file?" - should NOT show actual credentials
4. Common patterns to add: `.env`, `secrets/`, `credentials/`, `api_keys/`

### Complete Example

```bash
# 1. Create local docs directory
mkdir -p universes/MINE/domains/my_docs/library
cd universes/MINE/domains/my_docs/library

# 2. Add some documentation
cat > getting_started.md <<'EOF'
# Getting Started

ExFrame is a knowledge management system. To get started:
1. Create a domain
2. Add patterns or configure document search
3. Query the domain
EOF

cat > api_reference.md <<'EOF'
# API Reference

## Query Endpoint
POST /api/query
- query: string (required)
- domain: string (required)
- search_patterns: boolean (optional)
EOF

# 3. Create ignored.md
cat > ignored.md <<'EOF'
# Ignore these files
drafts/
temp.md
EOF

# 4. Create domain in UI
# - Persona: Librarian
# - Library Base Path: /app/universes/MINE/domains/my_docs/library
# - Save

# 5. Test query
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I get started?",
    "domain": "my_docs",
    "search_patterns": false
  }'
```

**Expected response**: Answer citing content from getting_started.md

---

## Docker Deployment

### Data Persistence

The container uses bind mounts for pattern storage:

- **Patterns**: `./data/patterns` → `/app/data/patterns`
- **Domain Registry**: Named volume `eeframe_data` → `/app/data`

This means:
- Patterns edited on the host are immediately available in the container
- Container restarts preserve pattern data
- To backup patterns: `tar -czf backup.tar.gz data/`

### Rebuilding After Code Changes

```bash
# Rebuild and restart
docker-compose down
docker-compose build --no-cache eeframe-app
docker-compose up -d
```

### Viewing Logs

```bash
# Application logs
docker logs -f eeframe-app

# All services
docker-compose logs -f
```

### Scaling

```yaml
# In docker-compose.yml
services:
  eeframe-app:
    deploy:
      replicas: 3
```

---

## Development

### Code Formatting

```bash
black generic_framework/
ruff check generic_framework/
mypy generic_framework/
```

### Testing

```bash
pytest tests/ -v
```

---

## Current Domains

ExFrame includes 7 production domains demonstrating the plugin architecture:

### Binary Symmetry
- **Specialists**: 3 (BitwiseMaster, PatternAnalyst, AlgorithmExplorer)
- **Patterns**: 16
- **Categories**: symmetry, transformation, relationship, metric, encoding, logic, detection
- **Tags**: binary, bitwise, xor, algorithm, math, computer_science, 8-bit

### Cooking & Recipes
- **Specialists**: 1 (Generalist)
- **Patterns**: 21
- **Categories**: technique, recipe, cooking_method, ingredient_substitution
- **Tags**: baking, chicken, quick, healthy

### LLM Consciousness & Failure Modes
- **Specialists**: 2 (FailureDetection, Monitoring)
- **Patterns**: 11
- **Categories**: failure_mode, solution, monitoring, architecture, detection
- **Tags**: hallucination, tool_failure, loops, amnesia, confidence, quality_drift

### Python Programming
- **Specialists**: 1 (Generalist)
- **Patterns**: 6
- **Categories**: language_feature, best_practice, anti_pattern
- **Tags**: python, programming, best_practices

### Template Domains
- **Gardening**: Template domain (0 patterns)
- **First Aid**: Template domain (1 pattern)
- **DIY**: Template domain (0 patterns)

**Total**: 7 domains, 55+ patterns, 9 specialist plugins

---

## Troubleshooting

### "docker-compose: command not found" or "no configuration file provided"

**Cause**: You're using the old `docker-compose` (v1) syntax. This project requires Docker Compose v2.

**Solution**: Use `docker compose` (with a space, not a hyphen):
```bash
# WRONG (old v1 syntax):
docker-compose up -d

# CORRECT (v2 syntax):
docker compose up -d
```

### Patterns Not Showing / Empty Pattern Directory

**Cause**: Docker snap has known bind mount bugs that cause mounted directories to appear empty inside containers.

**Solution**: Uninstall snap Docker and install official Docker Engine:
```bash
# Remove snap Docker
sudo snap remove docker

# Install official Docker
curl -fsSL https://get.docker.com | sh

# Restart containers
docker compose down
docker compose up -d
```

### Container Not Starting

1. Check port conflicts: `sudo lsof -ti:3000`
2. Check container logs: `docker compose logs eeframe-app`
3. Verify Docker is running: `docker ps`

### "Address already in use" error

**Cause**: Port 3000 is already in use (possibly by a previous container).

**Solution**:
```bash
# Kill any process using port 3000
sudo lsof -ti:3000 | xargs sudo kill -9

# Restart containers
docker compose down
docker compose up -d
```

### Frontend Shows "Generic Assistant Framework - Frontend not found"

**Cause**: Frontend files not accessible in container.

**Solution**: Check if frontend is mounted correctly:
```bash
# Check frontend mount in container
docker exec eeframe-app ls -la /app/frontend/

# If empty, rebuild container:
docker compose down
docker compose build --no-cache eeframe-app
docker compose up -d
```

### Permission Errors

```bash
# Fix pattern directory permissions
chmod -R 755 data/patterns/
```

### API Returns 404

1. Verify health endpoint works: `curl http://localhost:3000/health`
2. Check if routes are loaded: Visit `http://localhost:3000/docs`
3. Restart container: `docker compose restart eeframe-app`

---

## Security Considerations

### For Production Deployment

1. **API Keys**: Never commit `.env` file
2. **Authentication**: Add user authentication (not yet implemented)
3. **HTTPS**: Use reverse proxy (nginx) for SSL/TLS
4. **Network Isolation**: Run in private network
5. **Resource Limits**: Configure memory/CPU limits in docker-compose.yml
6. **Secrets Management**: Use Docker secrets or external secret manager

### Volume Backup

```bash
# Backup patterns
docker run --rm -v eeframe_data:/data -v $(pwd):/backup ubuntu \
  tar czf /backup/eeframe_backup_$(date +%Y%m%d).tar.gz /data

# Restore from backup
docker run --rm -v eeframe_data:/data -v $(pwd):/backup ubuntu \
  tar xzf /backup/eeframe_backup_YYYYMMDD.tar.gz -C /
```

---

## License

MIT License

---

## Contributing

Contributions are welcome! Areas of interest:

- New domains (specialist knowledge areas)
- Pattern ingestion improvements
- UI enhancements
- Documentation
- Bug fixes

---

## Changelog

### Version 1.5.0 - Pure Semantic Search Release (2026-01-20)

**Major Features**:
- ✅ Pure semantic search (100% semantic, 0% keyword)
- ✅ all-MiniLM-L6-v2 embedding model (384-dimensional vectors)
- ✅ Cosine similarity scoring (0-1 range)
- ✅ 100% embedding coverage across all 10 domains (131 patterns)
- ✅ Semantic scores visible in traces
- ✅ Whole document embedding with length protection

**Components**:
- ✅ EmbeddingService (text → 384-dim vectors)
- ✅ VectorStore (embeddings.json persistence)
- ✅ HybridSearcher (pure semantic mode)
- ✅ JSONKnowledgeBase integration

**API Endpoints**:
- ✅ GET /api/embeddings/status - Check embedding coverage
- ✅ POST /api/embeddings/generate - Generate embeddings for domain
- ✅ POST /api/embeddings/weights - Adjust search weights

**Bug Fixes**:
- ✅ JSON serialization (numpy float32 → Python float)
- ✅ Query bug fix (unpacking error in keyword-only search)
- ✅ Length protection for patterns exceeding 256 tokens

**Documentation**:
- ✅ rag-search-design.md - Complete semantic search documentation
- ✅ Updated claude.md with semantic search status
- ✅ Updated context.md with current system state
- ✅ Updated README with semantic search functionality

**Performance**:
- Local query response time: < 100ms
- Embedding generation: ~500ms per 100 patterns
- Semantic similarity computation: < 50ms

### Version 1.0.0 - Plugin Architecture Release (2026-01-09)

**Major Features**:
- ✅ Specialist Plugin interface (3-method: can_handle, process_query, format_response)
- ✅ Knowledge Base Plugin interface (storage abstraction)
- ✅ Generic Domain class with dynamic plugin loading
- ✅ Domain auto-discovery from `data/patterns/*/`
- ✅ 7 production domains (55+ patterns, 9 specialists)
- ✅ Domain configuration via JSON (domain.json)
- ✅ Specialist configuration via JSON
- ✅ Knowledge base plugin selection (JSON, SQLite)

**Documentation**:
- ✅ CHANGELOG.md with detailed release notes
- ✅ PLUGIN_ARCHITECTURE.md with plugin development guide
- ✅ Updated README with plugin architecture overview

**Bug Fixes**:
- ✅ API endpoints work with plugin attributes
- ✅ Pattern search returns all patterns when no category specified
- ✅ Pattern detail endpoint uses correct method name
- ✅ Frontend displays specialists and patterns for all domains

**Known Limitations**:
- Router logic still hardcoded in GenericDomain (planned for v1.1)
- Formatter logic embedded in specialists (planned for v1.1)

### Version 0.9.0 and Earlier

See git history for detailed changes.

---

## Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Detailed version history and changes
- **[PLUGIN_ARCHITECTURE.md](PLUGIN_ARCHITECTURE.md)** - Plugin development guide
- **[docs/](docs/)** - Additional documentation

## License

MIT License

---

## Contributing

Contributions are welcome! Areas of interest:

- New domains and patterns
- Persona enhancements and configurations
- **Pattern ingestion improvements** (🚧 Surveyor system is WIP - see `SURVEYOR_STATUS.md`)
- UI enhancements
- Additional knowledge base backends (Vector DB, Graph DB)
- Additional enricher plugins

### Note on Surveyor System

The Surveyor autonomous learning system is currently **under active development** and not production-ready. For high-quality pattern collection, we recommend using the **Researcher persona with citations** rather than web scraping. See `easy-recipe.md` for an example of LLM-generated patterns vs scraped patterns.
