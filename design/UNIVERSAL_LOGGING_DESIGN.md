# Universal Conversation Logging Design Document

**Status:** ✅ Implemented with UI
**Version:** 3.0
**Last Updated:** 2026-02-09

---

## Overview

**Universal Conversation Logging** is a fundamental ExFrame feature that automatically saves every query and response across all domains to permanent archives. Combined with optional **Conversation Memory**, it creates a complete system where your AI not only remembers everything but can build on previous discussions.

**Key insight:** This isn't just a feature - it's a **paradigm shift** from ephemeral AI chats to a permanent knowledge base that builds itself:
- Every query → Automatically saved
- Every response → Permanently archived
- Every discussion → Searchable and reusable
- Optional memory → AI remembers and builds context

### The Promise

> **"Every conversation. Automatically saved. Forever."**

No more lost insights. No more "what did we discuss?" No more forgotten answers. Just use ExFrame, and your archive builds itself.

---

## Two Independent Features

### 1. Universal Logging (Always On)

**Purpose:** Create a permanent archive of all AI interactions

**Behavior:**
- Every query/response saved to `domain_log.md`
- Works automatically, no configuration needed
- Separate log file for each domain
- Searchable, reviewable, exportable

**Use Cases:**
- Debugging: "What went wrong in that query?"
- Learning: "What did I learn last week?"
- Documentation: "Turn conversations into resources"
- Audit: "Full history of all interactions"
- Recovery: "Find that important insight"

### 2. Conversation Memory (Opt-In)

**Purpose:** Load conversation history into AI context for learning and continuity

**Behavior:**
- Loads accumulated content into LLM context
- AI remembers and builds on previous discussions
- Two modes: "All" (everything) or "Triggers" (on-demand)
- Optional per domain

**Use Cases:**
- Learning domains that build knowledge over time
- Story writing with chapter continuity
- Research threads with cumulative context
- Project discussions that span days/weeks

---

## How It Works

### Core Architecture

```
User Query
  ↓
┌─────────────────────────────────────┐
│ Universal Logging (Always Active)   │
├─────────────────────────────────────┤
│ 1. Append query/response to log    │
│    → domain_log.md                  │
│ 2. Save to permanent archive        │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Conversation Memory (If Enabled)    │
├─────────────────────────────────────┤
│ 1. Check: Memory enabled?           │
│ 2. Check: Mode = "all" or trigger?  │
│ 3. Load accumulated content         │
│ 4. Inject into LLM context          │
└─────────────────────────────────────┘
  ↓
Send to LLM with context
  ↓
Append to memory file (if enabled)
```

### File Structure

Every domain has two files:

```
universes/MINE/domains/{domain_id}/
├── domain.json          # Domain config
├── patterns.json        # Pattern storage
├── domain_log.md        # ✅ Universal log (always created)
└── learning_log.md      # ✅ Optional memory (if enabled)
```

---

## Configuration

### Domain Config (`domain.json`)

```json
{
  "domain_id": "quantum_physics",

  "logging": {
    "enabled": true,
    "output_file": "domain_log.md",
    "format": "markdown"
  },

  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "learning_log.md",
    "max_context_chars": 15000,
    "trigger_phrases": ["chapter", "continue"]
  }
}
```

### Configuration Fields

#### Logging Configuration (Universal)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `logging.enabled` | boolean | No | `true` | Enable query/response logging |
| `logging.output_file` | string | No | `"domain_log.md"` | Log file path (relative to domain) |
| `logging.format` | string | No | `"markdown"` | Output format: "markdown" or "plain" |

#### Memory Configuration (Optional)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `accumulator.enabled` | boolean | No | `false` | Enable conversation memory |
| `accumulator.mode` | string | No | `"all"` | `"all"` - Load all history<br>`"triggers"` - Load on trigger phrases |
| `accumulator.output_file` | string | Yes | - | Memory file path (relative to domain) |
| `accumulator.trigger_phrases` | array | No | `[]` | Phrases that trigger memory loading |
| `accumulator.max_context_chars` | integer | No | `15000` | Maximum characters to load |
| `accumulator.format` | string | No | `"markdown"` | Output format |

---

## Creating Domains with Logging (Web UI)

You can configure logging and memory directly through the **web interface** - no need to edit JSON files manually.

### Step-by-Step: Create a New Domain

1. **Navigate to Domains tab**
2. **Click "Create New Domain" button**
3. **Fill in the basic info:**
   - Domain ID: `quantum_physics`
   - Domain Name: `Quantum Physics`
   - Description: `Learn quantum mechanics from basics to advanced`

4. **Select Persona:**
   - Choose "Researcher" for learning
   - Temperature auto-sets to 0.7 (balanced)

5. **Configure Logging (Green Section):**
   - ✅ **Enable logging** - Already checked by default
   - **Log File:** `domain_log.md` (or custom name)
   - This creates your permanent archive

6. **Configure Memory (Blue Section) - Optional:**
   - ☐ **Enable conversation memory** - Check if needed
   - **Mode:** Choose "All" (remember everything) or "Triggers" (on-demand)
   - **Memory File:** `learning_log.md` (separate from log)
   - **Max Context:** `15000` (adjust as needed)

7. **Click Save**

**Your domain is ready with automatic logging!**

### UI Sections

| Section | Color | Purpose | Default |
|---------|-------|---------|---------|
| **Domain Logging** | Green | Permanent archive of all queries | ✅ Always enabled |
| **Conversation Memory** | Blue | Load history into AI context | ☐ Opt-in |

---

## File Formats

### Log File Format (domain_log.md)

```markdown
# Domain Log: Quantum Physics
Domain ID: quantum_physics
Created: 2026-02-09 10:03:49
Description: Learn quantum mechanics from basics to advanced

---

*This log records all queries and responses for this domain.*

## 2026-02-09 10:04:15

**Query:** What is quantum superposition?

**Response:** Quantum superposition is a fundamental principle...

---

## 2026-02-09 10:15:22

**Query:** How does it relate to Schrödinger's cat?

**Response:** Schrödinger's cat is a thought experiment...

---
```

### Memory File Format (learning_log.md)

```markdown
# Accumulator: Quantum Physics
Started: 2026-02-09 10:03:49
Mode: all

---

*This accumulator stores conversation context for memory/learning.*

## 2026-02-09 10:04:15

**Query:** What is quantum superposition?

**Response:** Quantum superposition is a fundamental principle...

---

## 2026-02-09 10:15:22

**Query:** How does it relate to Schrödinger's cat?

**Response:** Schrödinger's cat is a thought experiment...

---
```

**Note:** Both files use the same format, but serve different purposes:
- **Log file**: Audit trail, always appended to
- **Memory file**: Context for AI, loaded into LLM prompts

---

## Memory Modes

### Mode: "all" (Remember Everything)

**Purpose:** Continuous learning and project continuity

**Behavior:**
- Loads entire conversation history into context
- Appends every query/response to memory
- Perfect for: Learning domains, research threads, projects

**Example Config:**
```json
{
  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "learning_log.md"
  }
}
```

**Usage:**
```
You: How do I bake bread?
AI: [Instructions for baking bread]

You: What about sourdough?
AI: [Explains sourdough, references bread conversation]

You: Can I add seeds?
AI: [Suggests seeds, remembers entire discussion]
```

### Mode: "triggers" (On-Demand Memory)

**Purpose:** Sequential content generation on demand

**Behavior:**
- Only loads/appends when trigger phrases detected
- Ignores casual queries that don't match triggers
- Perfect for: Novel writing, serialized stories

**Example Config:**
```json
{
  "accumulator": {
    "enabled": true,
    "mode": "triggers",
    "trigger_phrases": ["chapter", "continue", "next", "part"],
    "output_file": "stories/active_novel.md"
  }
}
```

**Usage:**
```
You: Tell me about a character named John
AI: [Character description - not saved to memory]

You: Write chapter 1
AI: [Chapter 1 - saved to memory]

You: Write chapter 2
AI: [Chapter 2 - loads chapter 1, continues story]
```

---

## Real-World Examples

### Example 1: Learning Domain (Logging + Memory)

**Setup:**
```json
{
  "domain_id": "rust_programming",
  "logging": { "enabled": true },
  "accumulator": { "enabled": true, "mode": "all" }
}
```

**Progression:**
```
Week 1: "I'm new to programming. Teach me Rust basics."
AI: [Explains ownership, borrowing]
[Logged to domain_log.md, saved to learning_log.md]

Week 2: "I still don't get borrowing."
AI: [Sees you've asked 3 times about borrowing]
    "Let me try a different approach. Think of borrowing like..."
[Logged, saved with full context]

Week 5: "Quiz me on ownership."
AI: [Reads 5 weeks of your learning journey]
    "You've mastered ownership but struggle with borrowing.
     Let's test you on some edge cases..."
[Logged, saved]

Week 10: "I'm ready for lifetimes."
AI: [Builds on 10 weeks of context]
    "Since you're solid on ownership and borrowing, lifetimes
     will make sense. They solve the 'when to free memory' problem..."
[Logged, saved]
```

**Result:** Complete learning journal + AI tutor that remembers everything

### Example 2: Story Writing (Logging + Triggered Memory)

**Setup:**
```json
{
  "domain_id": "mystery_novel",
  "logging": { "enabled": true },
  "accumulator": {
    "enabled": true,
    "mode": "triggers",
    "trigger_phrases": ["chapter", "continue"]
  }
}
```

**Process:**
```
You: "I want a mystery novel set in 1920s England."
AI: [Character ideas - NOT saved to memory]

You: "Write chapter 1"
AI: [Chapter 1 - saved to memory]

You: "What about a detective?"
AI: [Character discussion - NOT saved to memory]

You: "Write chapter 2"
AI: [Loads chapter 1, continues story with established characters]
```

**Result:** Log has everything, memory only has story chapters

### Example 3: Regular Domain (Logging Only)

**Setup:**
```json
{
  "domain_id": "quick_questions",
  "logging": { "enabled": true },
  "accumulator": { "enabled": false }
}
```

**Usage:**
```
You: "What's the capital of France?"
AI: "Paris"
[Logged to domain_log.md]

You: "How do I format a date in Python?"
AI: [Python code examples]
[Logged to domain_log.md]

You: "What's a REST API?"
AI: [Explanation]
[Logged to domain_log.md]
```

**Result:** Permanent archive of Q&A, no memory overhead

---

## Benefits

### Universal Logging Benefits

1. **No Regret**: Never wish you had enabled logging
2. **Debugging**: Full history of what worked and what didn't
3. **Documentation**: Conversations become reference material
4. **Audit Trail**: Complete record of all AI interactions
5. **Searchable**: Find past answers instantly
6. **Exportable**: Convert conversations to docs/guides
7. **Automatic**: No configuration required, just works

### Conversation Memory Benefits

1. **Continuous Learning**: AI builds knowledge over time
2. **Context Awareness**: Remembers previous discussions
3. **Adaptive Explanations**: Changes approach based on history
4. **Progress Tracking**: Can assess your learning journey
5. **Story Continuity**: Maintains characters, plot, setting
6. **Research Threads**: Builds on previous findings
7. **Project Memory**: Remembers decisions and context

---

## Implementation

### Backend Components

**1. API Models (`generic_framework/api/app.py`)**
```python
class DomainCreate(BaseModel):
    # Universal logging
    logging_enabled: Optional[bool] = True
    logging_output_file: Optional[str] = "domain_log.md"

    # Conversation memory
    accumulator: Optional[Dict[str, Any]] = None
```

**2. Domain Creation**
```python
# Always create log file
if logging_config.get("enabled", True):
    create_log_file(domain, "domain_log.md")

# Optionally create memory file
if accumulator_config.get("enabled", False):
    create_memory_file(domain, "learning_log.md")
```

**3. Query Processing (`generic_framework/core/query_processor.py`)**
```python
# Separate append operations
if logging_enabled:
    _append_to_log(domain, "domain_log.md", query, response)

if memory_enabled:
    _append_to_accumulator(domain, "learning_log.md", query, response)
    # Also loads into context for next query
```

### Frontend Components

**UI Sections:**

```html
<!-- Logging (Green) -->
📝 Domain Logging
☑ Enable logging (recommended)
  Log file: [domain_log.md]

<!-- Memory (Blue) -->
🧠 Conversation Memory
☐ Enable conversation memory
  Mode: [All / Triggers ▼]
  Memory file: [learning_log.md]
```

---

## Advanced Usage

### Cross-Domain Memory

The AI can reference conversations from other domains:

```
In quantum_physics domain:
"This wave interference is similar to something in music_theory
 that you learned about last month..."

In rust_programming domain:
"This ownership concept is like the borrowing we discussed
 in your economics_domain..."
```

### Progress Tracking

At any point, ask: "What have I learned so far?"

The AI reads your entire learning log and provides:
```
Mastery Assessment (30 sessions):

✓ Wave-particle duality (mastered - Day 1)
✓ Superposition (understood - Day 7)
→ Entanglement (just introduced - Day 25)
→ Uncertainty principle (covered briefly - Day 15)
→ Quantum tunneling (not yet covered)

Recommended next: Deep dive on entanglement, then tunneling
```

### Export and Reuse

Log files can be:
- Converted to documentation
- Published as tutorials
- Shared with team members
- Used as training data
- Analyzed for insights

---

## Managing Logs and Memory

### View Log Files

Log files are stored in domain directories:
```bash
universes/MINE/domains/{domain_id}/domain_log.md
```

Open in any text editor or markdown viewer.

### Reset Memory

To start fresh without losing logs:
```bash
# Rename old memory file
mv learning_log.md learning_log_archive_01.md

# Next query creates fresh memory
```

### Disable Memory

Keep logging, disable memory loading:
```json
{
  "logging": { "enabled": true },
  "accumulator": { "enabled": false }
}
```

### Delete Domain

Deleting a domain removes everything:
```bash
# Via API or UI
DELETE /api/admin/domains/{domain_id}

# Removes entire directory including logs and memory
```

---

## Future Enhancements

Potential improvements:

1. **Log Search API**: Search across all domain logs
2. **Log Viewing UI**: View logs directly in web interface
3. **Memory Analytics**: Visualize learning progress over time
3. **Cross-Domain Search**: Find relevant discussions across domains
4. **Auto-Summarization**: Summarize old content to save space
5. **Export Formats**: Export as PDF, EPUB, HTML
6. **Memory Merging**: Combine multiple memory files
7. **Selective Memory**: Choose which conversations to remember

---

## Comparison: Before vs After

| Before ExFrame 1.6 | After ExFrame 1.6 |
|-------------------|------------------|
| Ephemeral conversations | **Permanent archive** |
| One-off queries | **Searchable history** |
| "What did we discuss?" | **Check the log** |
| Manual note-taking | **Automatic logging** |
| No memory between sessions | **Optional AI memory** |
| Lost insights | **Everything saved** |
| Amnesia AI | **Perfect memory** |

---

## Technical Details

### File Location

```
universes/MINE/domains/{domain_id}/
├── domain.json          # Domain config
├── patterns.json        # Pattern storage
├── domain_log.md        # Universal log (always created)
└── {memory_file}.md     # Optional memory (if enabled)
```

### Character Encoding

All files use UTF-8 encoding for full Unicode support.

### Error Handling

- **File doesn't exist**: Returns `None`, starts fresh
- **Directory doesn't exist**: Creates automatically
- **Append fails**: Logs warning, doesn't break query
- **File too large**: Truncates to `max_context_chars`

### Performance

- **Logging**: Minimal overhead (< 10ms per query)
- **Memory loading**: Depends on file size (typically 100-500ms)
- **Context injection**: Included in LLM prompt time

---

## Summary

**Universal Conversation Logging** transforms ExFrame from a simple Q&A tool into a **knowledge base that builds itself**. Every conversation is automatically saved, creating a permanent archive that can be searched, reviewed, and reused.

**Conversation Memory** (optional) loads that history into AI context, enabling the AI to remember and build on previous discussions for learning, storytelling, and research.

**Two files. Infinite possibilities.**

---

## Related Documentation

- [Domain Configuration Reference](reference/domain-config.md) - Field reference
- [Architecture Overview](architecture/overview.md) - System architecture
- [INDEX.md](INDEX.md) - Master file index
