# Knowledge Cartography (KCart): Dialectical Knowledge Mapping in ExFrame

**Status:** Design Document
**Created:** 2026-02-15
**Purpose:** Personal knowledge mapping through dialectical query/response tracking

---

## Vision

ExFrame will capture and analyze the complete history of user interactions to build a **personal dialectical knowledge map** - a living representation of intellectual exploration, learning paths, and concept evolution.

By storing all query/response pairs with compression, we create the raw material for:
- Understanding what we seek (Questions/Yin) vs what we know (Answers/Yang)
- Tracing learning progressions and knowledge evolution
- Discovering concept relationships and cross-domain connections
- Identifying knowledge gaps and areas for growth
- Visualizing the dialectical flow of understanding

This implements the principles from "The dialectical Knowledge Map.md" but **organically grown from actual use** rather than pre-designed.

---

## The Dialectical Foundation

### From "The dialectical Knowledge Map"

**Yin (Questions):**
- Dark, absorbing, seeking
- Represents unknown territory, curiosity, gaps in knowledge
- The drive to understand

**Yang (Answers):**
- Bright, emitting, providing
- Represents knowledge gained, understanding achieved
- The resolution of uncertainty

**Tao (Transformation):**
- The process of moving from question to answer
- The synthesis that occurs through dialectical engagement
- The evocation of new questions from answers

### ExFrame's Implementation

**Questions = Queries**
- Every query is a seek, a knowledge gap, a curiosity
- Stored with timestamp, context, concepts

**Answers = Responses**
- Generated from patterns, LLM synthesis, web search
- Stored with confidence, source, patterns used

**Transformation = Query Processing**
- Pattern matching, semantic search, LLM synthesis
- Context-aware (last N queries inform current response)
- Evoked questions guide next exploration

---

## Technical Architecture

### Compressed Storage

**Why compression?**
- JSON text compresses 70-80% (gzip)
- 1 million Q/R pairs ≈ 260MB compressed (vs 1.3GB uncompressed)
- Decompression is fast (~50-100 MB/s)
- Enables storing complete interaction history

**Storage per domain:**
```
universes/MINE/domains/[domain_name]/
  patterns.json              # Knowledge patterns (teaching material)
  query_history.json.gz      # ALL Q/R pairs (compressed)
  embeddings.json            # Semantic vectors
  domain.json               # Configuration
```

**Entry structure:**
```json
{
  "id": 1,
  "timestamp": "2026-02-15T10:00:00-08:00",
  "query": "Explain Newton's second law",
  "response": "F=ma means force equals mass times acceleration...",
  "metadata": {
    "source": "pattern_match",
    "confidence": 0.85,
    "patterns_used": ["physics_001", "physics_042"],
    "evoked_questions": [
      "How does doubling mass affect force?",
      "What if multiple forces act on an object?"
    ]
  },
  "concepts": ["force", "mass", "acceleration", "newton"]
}
```

### Performance Characteristics

**Storage scaling:**
- 1,000 pairs = 400KB compressed (~1ms to compress one pair)
- 10,000 pairs = 4MB compressed (~60ms to load all)
- 100,000 pairs = 26MB compressed (~500ms to load all)
- 1,000,000 pairs = 260MB compressed (~5s to load all)

**Context loading:**
- Load last 20 pairs for context: ~60-80ms (decompress + parse)
- Acceptable latency for conversational memory
- Can cache decompressed data in memory if needed

**Real-world capacity:**
- Heavy-use domain: 10 entries/day × 10 years = 36,500 pairs = ~15MB
- 10 domains moderately used: 100,000 total pairs = ~26MB
- **Conclusion:** Storage is negligible, can store everything

---

## Knowledge Mapping Capabilities

### 1. Query → Pattern Links (RESOLVES_TO)

**Track which patterns answer which questions:**

```python
query_pattern_map = {
  "What is kinetic energy?": {
    "patterns": ["physics_energy_001", "physics_motion_023"],
    "confidence": 0.85,
    "timestamp": "2026-01-15T10:00:00"
  }
}
```

**Insights:**
- Which patterns are most useful? (usage frequency)
- Which questions never got good answers? (low confidence)
- Which patterns emerged from which questions? (autogeneration tracking)
- Pattern lifecycle: created → refined → frequently used

**Use cases:**
- Pattern quality scoring
- Identify patterns needing improvement
- Suggest pattern creation for common low-confidence queries

### 2. Answer → Question Chains (EVOKES)

**Track which answers evoke which next questions:**

```python
evocation_chain = [
  {
    "question": "What is kinetic energy?",
    "answer": "KE = ½mv²...",
    "evoked_question": "How does doubling velocity affect it?",
    "time_gap_seconds": 45
  },
  {
    "question": "How does doubling velocity affect it?",
    "answer": "Velocity is squared, so KE increases 4x...",
    "evoked_question": "What about doubling mass?",
    "time_gap_seconds": 30
  }
]
```

**Insights:**
- Depth of exploration (chain length)
- Topics that inspire deeper investigation
- Dead-end answers (no follow-up questions)
- Natural learning progressions

**Use cases:**
- Automatic Socratic tutoring (suggest next questions based on past patterns)
- Identify engaging vs boring topics
- Optimize answer structure to evoke curiosity

### 3. Concept Extraction & Networks

**Mine concepts from queries and responses:**

```python
concept_network = {
  "kinetic_energy": {
    "query_count": 15,
    "related_concepts": {
      "velocity": 12,      # co-occurred 12 times
      "mass": 10,
      "acceleration": 8,
      "momentum": 5
    },
    "domains": ["learn_physics", "engineering"],
    "first_seen": "2026-01-15",
    "last_seen": "2026-02-15"
  }
}
```

**Insights:**
- Concept clusters (what ideas group together?)
- Concept hierarchies (basic → intermediate → advanced)
- Concept evolution (how understanding deepens over time)
- Bridge concepts (appear across multiple domains)

**Use cases:**
- Suggest related topics to explore
- Identify prerequisite concepts for advanced topics
- Cross-domain knowledge transfer recommendations

### 4. Learning Path Visualization

**Trace evolution of understanding over time:**

```
Topic: "quantum physics"
Timeline: Jan 15 - Feb 15 (1 month)

[1] 2026-01-15 | Confidence: 0.75
Q: What is quantum mechanics?
Concepts: [quantum, mechanics, physics]

[2] 2026-01-15 | Confidence: 0.82 ↑
Q: How does wave-particle duality work?
Concepts: [wave, particle, duality, quantum]

[3] 2026-01-20 | Confidence: 0.88 ↑
Q: Explain the double-slit experiment
Concepts: [experiment, interference, observation]

[4] 2026-02-01 | Confidence: 0.91 ↑
Q: What are quantum entanglement implications?
Concepts: [entanglement, nonlocality, spooky_action]

Analysis:
- Progression: basic → advanced (4 stages)
- Confidence trend: improving (+0.16)
- Exploration style: systematic, building on concepts
- Next suggested: "quantum computing applications"
```

**Insights:**
- Learning velocity (how fast concepts are absorbed)
- Concept scaffolding (prerequisites followed in order)
- Plateau detection (repeated queries at same level)
- Spiral learning (returning to concepts at deeper levels)

**Use cases:**
- Adaptive tutoring (adjust pace to learning velocity)
- Prerequisite recommendations (fill gaps before advancing)
- Progress visualization (motivate continued learning)

### 5. Knowledge Gap Detection

**Find areas needing improvement:**

```python
knowledge_gaps = [
  {
    "concept": "quantum_tunneling",
    "query_count": 3,
    "avg_confidence": 0.45,
    "queries": [
      "How does quantum tunneling work?",
      "Explain tunneling through barriers",
      "Why can particles tunnel?"
    ],
    "pattern_available": False,
    "web_search_used": True,
    "action": "Create dedicated pattern or improve synthesis"
  }
]
```

**Insights:**
- Repeated low-confidence questions (persistent gaps)
- Topics with no good patterns (coverage gaps)
- Questions requiring web search (knowledge boundary)
- Domains needing expansion

**Use cases:**
- Pattern creation priorities
- Domain development roadmap
- Identify when to add new knowledge sources

### 6. Cross-Domain Knowledge Transfer

**Find similar concepts across domains:**

```python
cross_domain_connections = {
  "pressure": {
    "learn_physics": [
      "How does air pressure work?",
      "Pressure in fluids and gases"
    ],
    "cooking": [
      "Why does pressure cooking work faster?",
      "Altitude affects boiling point - pressure related?"
    ],
    "connection": "Physical pressure principle applies to cooking technique"
  },
  "recursion": {
    "learn_programming": [
      "Explain recursive functions",
      "When to use recursion vs iteration?"
    ],
    "math": [
      "What are recursive sequences?",
      "Fibonacci as recursive definition"
    ],
    "connection": "Recursion as general problem-solving pattern"
  }
}
```

**Insights:**
- Concepts that bridge domains
- Transfer learning opportunities
- Unified understanding across contexts
- Deep vs surface similarities

**Use cases:**
- "You explored X in domain A, similar to Y in domain B"
- Deepen understanding through analogies
- Discover unexpected connections

### 7. Personal Knowledge Graph

**Full graph representation:**

**Nodes:**
- Questions (Yin): Seeking, unknown, dark
- Answers (Yang): Providing, known, bright
- Concepts: Extracted entities and ideas

**Edges:**
- RESOLVES_TO: Question → Answer
- EVOKES: Answer → Next Question
- CONTAINS_CONCEPT: Question/Answer → Concept
- RELATES_TO: Concept → Concept (co-occurrence)
- PREREQUISITE: Concept → Concept (learning order)

**Graph structure:**
```json
{
  "nodes": [
    {
      "id": "q_001",
      "type": "question",
      "text": "What is kinetic energy?",
      "timestamp": "2026-01-15T10:00:00",
      "domain": "learn_physics",
      "concepts": ["kinetic_energy", "energy", "motion"]
    },
    {
      "id": "a_001",
      "type": "answer",
      "text": "Kinetic energy is...",
      "confidence": 0.85,
      "source": "pattern_match"
    },
    {
      "id": "c_kinetic_energy",
      "type": "concept",
      "label": "kinetic_energy",
      "query_count": 15,
      "domains": ["learn_physics"]
    }
  ],
  "edges": [
    {"from": "q_001", "to": "a_001", "type": "RESOLVES_TO", "confidence": 0.85},
    {"from": "a_001", "to": "q_002", "type": "EVOKES", "time_gap": 45},
    {"from": "q_001", "to": "c_kinetic_energy", "type": "CONTAINS_CONCEPT"}
  ]
}
```

**Visualization:**
- Force-directed graph (D3.js, Cytoscape)
- Timeline view (chronological exploration)
- Concept cluster view (topic groupings)
- Domain overlay (color by domain)
- Confidence heatmap (quality of understanding)

**Interactive features:**
- Click node to see full Q/A text
- Hover edge to see relationship type
- Filter by date range, domain, concept
- Search for specific queries or concepts
- Trace learning paths through graph

---

## Implementation Roadmap

### Phase 1: Compressed Storage (IMMEDIATE)

**Goal:** Store all Q/R pairs with compression, enable conversational context

**Tasks:**
1. ✅ Design document (this file)
2. Implement compressed storage functions:
   - `save_query_response(domain_path, query, response, metadata)`
   - `load_recent_context(domain_path, limit=20)`
3. Integrate into query_processor.py:
   - Save every query/response pair
   - Load last N for context in all domains
4. Add configuration to domain.json:
   - `query_history.enabled`
   - `query_history.context_window`
   - `query_history.compression`
5. Test with multiple domains:
   - Poet (journal entries)
   - Researcher (web searches)
   - Learn_physics (tutorial queries)

**Deliverables:**
- Working compressed storage across all domains
- Conversational context (20-turn memory)
- Configuration options per domain

**Timeline:** 1-2 hours

### Phase 2: Basic Analytics (NEXT)

**Goal:** Extract insights from stored Q/R history

**Tasks:**
1. Create `scripts/analyze_knowledge.py`
2. Implement basic analytics:
   - Total queries, date range, domains
   - Average confidence by domain
   - Query frequency over time
   - Most/least confident responses
3. Implement query→pattern mapping:
   - Which patterns answer which queries
   - Pattern usage frequency
   - Low-confidence queries (knowledge gaps)
4. Generate reports:
   - Domain summary (queries, confidence, coverage)
   - Pattern effectiveness scores
   - Knowledge gap identification

**Deliverables:**
- `python3 scripts/analyze_knowledge.py [domain]`
- Human-readable reports
- Actionable insights for domain improvement

**Timeline:** 2-3 hours

### Phase 3: Evocation Tracking (WEEK 2)

**Goal:** Track and analyze question→answer→question chains

**Tasks:**
1. Enhance storage to track evoked questions:
   - Store generated follow-up questions with Q/R pair
   - Link to next query if user clicked evoked question
2. Implement chain analysis:
   - `build_evocation_chains(domain_path)`
   - Identify exploration depth and patterns
   - Find dead-end answers vs engaging answers
3. Socratic tutor improvements:
   - Use evocation history to improve question generation
   - Suggest questions that led to deep exploration in past
4. Visualization:
   - Simple ASCII chain visualization
   - Export chains as JSON for graphing

**Deliverables:**
- Evocation chain analysis
- Improved Socratic questioning
- Chain visualization tools

**Timeline:** 3-4 hours

### Phase 4: Concept Extraction (WEEK 3)

**Goal:** Extract and network concepts from Q/R history

**Tasks:**
1. Implement concept extraction:
   - Use LLM to extract key concepts from queries and responses
   - Store concepts with each Q/R pair
   - Build concept co-occurrence matrix
2. Concept network analysis:
   - `build_concept_network(domain_path)`
   - Identify concept clusters
   - Find bridge concepts across domains
3. Cross-domain analysis:
   - Compare concepts across all domains
   - Identify knowledge transfer opportunities
   - Suggest related explorations
4. Concept-based search:
   - Search Q/R history by concept
   - Find all queries about a concept
   - Trace concept evolution over time

**Deliverables:**
- Concept extraction and storage
- Concept network visualization (JSON export)
- Cross-domain concept analysis

**Timeline:** 4-5 hours

### Phase 5: Learning Path Analysis (WEEK 4)

**Goal:** Visualize and optimize learning progressions

**Tasks:**
1. Learning path extraction:
   - Identify sequences of related queries
   - Detect progression from basic→advanced
   - Find prerequisite patterns
2. Learning velocity metrics:
   - Time between queries on a topic
   - Confidence improvement rate
   - Concept absorption speed
3. Adaptive recommendations:
   - Suggest next topics based on learning path
   - Identify prerequisites for advanced topics
   - Detect when user is ready to advance
4. Progress visualization:
   - Timeline of topic exploration
   - Confidence trends over time
   - Concept mastery heatmap

**Deliverables:**
- Learning path analysis tools
- Adaptive recommendation engine
- Progress visualization exports

**Timeline:** 5-6 hours

### Phase 6: Knowledge Graph Visualization (FUTURE)

**Goal:** Interactive visual exploration of knowledge map

**Tasks:**
1. Graph export format:
   - Export Q/R history as graph (nodes + edges)
   - Support Neo4j import format
   - Support D3.js/Cytoscape formats
2. Static visualization:
   - Generate graph images with GraphViz
   - Create HTML visualization with D3.js
3. Interactive explorer:
   - Web-based graph browser
   - Filter by domain, date, concept, confidence
   - Search and highlight capabilities
4. "Tao Viewer":
   - Dialectical view (Yin/Yang coloring)
   - Animate exploration over time
   - Show evocation flows

**Deliverables:**
- Graph export tools
- Static visualization generation
- Interactive web-based explorer
- "Tao Viewer" prototype

**Timeline:** 10-15 hours (future work)

---

## Configuration

### Global Settings (config.py or .env)

```bash
# Knowledge Cartography
KCART_ENABLED=true
KCART_DEFAULT_COMPRESSION=gzip
KCART_DEFAULT_CONTEXT_WINDOW=20
KCART_DEFAULT_MAX_ENTRIES=null  # unlimited
```

### Per-Domain Settings (domain.json)

```json
{
  "domain_id": "learn_physics",
  "persona": "researcher",
  "persona_mode": "socratic_tutor",

  "query_history": {
    "enabled": true,
    "compression": "gzip",
    "context_window": 20,
    "max_entries": null,
    "archive_after_days": null,
    "store_evoked_questions": true,
    "extract_concepts": true
  },

  "knowledge_cartography": {
    "enabled": true,
    "track_evocation_chains": true,
    "track_concept_networks": true,
    "cross_domain_analysis": true
  }
}
```

---

## Use Cases & Benefits

### 1. Personal Learning Enhancement

**Socratic Tutoring:**
- System references earlier concepts: "As we discussed about F=ma..."
- Suggests next questions based on successful past explorations
- Adapts pace to your learning velocity

**Progress Tracking:**
- See how far you've come on a topic
- Identify when you're ready for advanced material
- Celebrate milestones in understanding

**Gap Filling:**
- System detects repeated low-confidence queries
- Suggests prerequisite topics to study first
- Recommends pattern creation for common questions

### 2. Knowledge Discovery

**Concept Connections:**
- "You explored pressure in physics and cooking - they connect!"
- Discover unified principles across domains
- Deepen understanding through analogies

**Hidden Patterns:**
- Which topics do you naturally explore deeply?
- Which answers inspire curiosity?
- What's your learning style? (systematic vs exploratory)

**Serendipity:**
- Browse old queries and rediscover insights
- See unexpected connections in the graph
- Find forgotten explorations worth revisiting

### 3. System Improvement

**Pattern Development:**
- Identify high-value patterns to create
- Find patterns needing improvement
- Discover gaps in domain coverage

**Quality Metrics:**
- Which patterns are most useful?
- Which queries have low confidence?
- Where does web search get used most?

**Domain Evolution:**
- Track domain growth over time
- See which topics are explored most
- Guide future domain development

### 4. Research & Reflection

**Personal Knowledge Base:**
- "What did I learn about quantum physics last year?"
- Search entire Q/R history
- Export insights to external tools

**Meta-Cognition:**
- How do I explore new topics?
- What's my question-asking style?
- Where are my knowledge strengths and weaknesses?

**Intellectual Biography:**
- Your complete learning journey in ExFrame
- See how understanding evolved over years
- Share knowledge maps with others (if desired)

---

## Technical Considerations

### Storage Management

**Cleanup strategies:**
1. **Unlimited** (recommended): Keep everything, storage is cheap
2. **Rolling window**: Keep last N entries (e.g., 100,000)
3. **Archive by age**: Move old entries to archive files
4. **User-triggered**: Manual cleanup commands

**Backup:**
- Query history files are just JSON.gz
- Easy to backup with standard tools
- Version control friendly (if compressed efficiently)

### Performance Optimization

**Caching:**
- Keep last N decompressed entries in memory
- Invalidate cache on new query
- Reduces repeated decompression

**Incremental loading:**
- Load only last N for context (don't decompress all)
- Use streaming decompression if files get huge
- Index by timestamp for range queries

**Async processing:**
- Save Q/R pairs asynchronously (don't block response)
- Extract concepts in background
- Build analytics incrementally

### Privacy & Security

**Data ownership:**
- All data in user's local universe
- No external transmission (unless user exports)
- User controls retention and deletion

**Sensitive information:**
- User may ask sensitive questions
- Consider encryption option for query_history.json.gz
- Add ability to exclude queries from history (opt-out per query)

**Multi-user considerations:**
- If ExFrame becomes multi-user, add user_id to queries
- Separate history per user
- Privacy controls per user

### Extensibility

**Plugin architecture:**
- Allow custom analyzers to process Q/R history
- Export formats for external tools
- Webhooks for real-time analysis

**Integration points:**
- Neo4j for advanced graph queries
- Jupyter notebooks for custom analysis
- Export to Obsidian, Roam, or other PKM tools

---

## Related Documents

- **The dialectical Knowledge Map.md** - Philosophical foundation and inspiration
- **BRAVE_SEARCH_INTEGRATION.md** - Web search for knowledge augmentation
- **TODO.md** - Implementation tasks and priorities
- **ARCHITECTURE.md** - Overall ExFrame architecture

---

## Success Metrics

**Phase 1 (Storage):**
- ✅ All queries stored with compression
- ✅ Conversational context working (20-turn memory)
- ✅ Storage overhead < 50MB for typical use

**Phase 2 (Analytics):**
- ✅ Generate domain summary reports
- ✅ Identify knowledge gaps automatically
- ✅ Pattern effectiveness scoring working

**Phase 3+ (Advanced):**
- ✅ Evocation chains tracked and analyzed
- ✅ Concept networks built and visualized
- ✅ Cross-domain connections discovered
- ✅ Interactive knowledge graph viewer working

**Long-term:**
- Personal knowledge map becomes valuable reference tool
- System learns from usage patterns to improve responses
- User gains meta-cognitive insights from their learning patterns
- ExFrame becomes a true "second brain" with memory and understanding

---

## Philosophical Notes

**Knowledge as Dialectic:**
This system embodies the dialectical view of knowledge:
- Not static facts, but dynamic seeking and finding
- Not hierarchical, but networked and relational
- Not possessed, but participated in through inquiry

**The Tao of Learning:**
- Questions (Yin) and answers (Yang) in constant interplay
- The transformation between them (Tao) is where learning happens
- The map of this transformation is your intellectual journey

**Personal Epistemology:**
- What you ask reveals what you don't know (humility)
- What you find reveals what you do know (knowledge)
- The pattern of seeking reveals who you are (identity)

**ExFrame as Mirror:**
Knowledge cartography makes ExFrame not just a tool, but a mirror:
- Shows you your curiosity patterns
- Reveals your learning style
- Maps your intellectual growth
- Reflects your quest for understanding

---

**End of Design Document**

Implementation begins with Phase 1: Compressed Storage.
