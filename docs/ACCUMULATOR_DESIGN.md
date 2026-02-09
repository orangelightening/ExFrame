# Accumulator Design Document

**Status:** ✅ Implemented with UI
**Version:** 2.0
**Last Updated:** 2026-02-09

---

## Overview

The **Accumulator** is a domain-level feature that provides **persistent conversation memory** for LLM conversations. It transforms each domain into a personalized learning environment where the AI remembers everything discussed.

**Key insight:** This is not just a feature - it's a **personal university system** where:
- Each domain = A course or subject
- The accumulator = Your learning log
- The LLM = Your personal tutor who remembers EVERYTHING

### Use Cases

1. **Story Writing** - Chapter-by-chapter novel creation
2. **Conversation Memory** - Ongoing dialogue with full history
3. **Learning Domains** - Personalized education on any topic
4. **Project Continuity** - Long-running discussions that build context

---

## How It Works

### Core Concept

Every query/response pair is logged to a file. When a new query comes in, the accumulated history is loaded and provided to the LLM as context.

**The LLM sees:**
```
Story so far:
[Previous query 1]
[AI response 1]

[Previous query 2]
[AI response 2]

---
Current Query: [Your new question]
```

### Architecture

```
User Query
  ↓
Check: Accumulator enabled?
  ↓ Yes
Check: Mode = "all" or "triggers"?
  ↓ Yes
Load accumulator file
  ↓
Inject into prompt context
  ↓
Send to LLM
  ↓
Append query + response to accumulator file
```

---

## Configuration

### Domain Config (`domain.json`)

```json
{
  "domain_id": "prose",
  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "stories/active_story.md",
    "trigger_phrases": ["next chapter", "continue", "write chapter"],
    "max_context_chars": 15000,
    "format": "markdown"
  }
}
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | boolean | Yes | - | Enable accumulator for this domain |
| `mode` | string | No | "triggers" | `"all"` - Log every query<br>`"triggers"` - Log only on trigger phrases |
| `output_file` | string | Yes | - | Relative path to accumulator file (from domain directory) |
| `trigger_phrases` | array | No | [] | Phrases that trigger logging in "triggers" mode |
| `max_context_chars` | integer | No | 15000 | Maximum characters to load from accumulator (truncates if too long) |
| `format` | string | No | "markdown" | Output format: "markdown" or "plain" |

---

## Creating Domains with Accumulator (Web UI)

You can now create domains with accumulator enabled directly through the **web interface** - no need to edit JSON files manually.

### Step-by-Step: Create a Learning Domain

1. **Navigate to Domains tab**
2. **Click "Create New Domain" button**
3. **Fill in the basic info:**
   - Domain ID: `quantum_physics` (unique identifier)
   - Domain Name: `Quantum Physics` (display name)
   - Description: `Learn quantum mechanics from basics to advanced`

4. **Select Persona:**
   - Choose **"Researcher - Research and analysis"** for learning
   - Temperature will auto-set to 0.7 (balanced)
   - Researcher uses LLM knowledge and research capabilities

5. **Configure Accumulator (Memory):**
   - ✅ **Enable accumulator** - Check the checkbox
   - **Mode:** Choose "All - Remember everything"
   - **Output File:** `learning_log.md` (or any name you want)
   - **Max Context Length:** `15000` (adjustable 1000-100000)

6. **Click Save**

**Your learning domain is ready!**

### UI Fields

| Field | Description | Recommendation for Learning |
|-------|-------------|-------------------------------|
| Enable accumulator | Turn on memory for this domain | ✅ Always enable for learning |
| Mode | "all" or "triggers" | Choose "all" for learning |
| Output file | Where conversation log is stored | `learning_log.md` or similar |
| Max context length | How much history to load (chars) | 15000-30000 for deep learning |

### Editing Existing Domains

1. **Domains tab** → Click domain name
2. **Edit** button
3. **Enable accumulator** (if not already enabled)
4. **Save**

---

## Modes

### Mode: "all"

**Purpose:** Conversation memory for every query

**Behavior:**
- Every query/response is logged
- Every query loads full conversation history
- Perfect for: Ongoing discussions, project planning, research threads

**Example config:**
```json
{
  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "conversation_log.md"
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
AI: [Suggests seeds, remembers entire bread discussion]
```

### Mode: "triggers"

**Purpose:** Sequential content generation on demand

**Behavior:**
- Only logs when trigger phrases detected
- Only loads context when trigger phrases detected
- Perfect for: Novel writing, serialized content, episodic stories

**Example config:**
```json
{
  "accumulator": {
    "enabled": true,
    "mode": "triggers",
    "trigger_phrases": ["chapter", "continue", "next", "part"],
    "output_file": "stories/active_story.md"
  }
}
```

**Usage:**
```
You: Tell me about a character named John
AI: [Character description - not saved]

You: Write chapter 1
AI: [Chapter 1 - saved to accumulator]

You: Write chapter 2
AI: [Chapter 2 - loads chapter 1, continues story, saved]
```

---

## File Format

### Markdown Format (default)

```markdown
# Story Accumulator
Started: 2026-02-09 07:51:53

## 2026-02-09 07:51:53

**Query:** Write chapter 1 about space explorers

[Full AI response...]

---

## 2026-02-09 08:15:22

**Query:** Write chapter 2

[Full AI response...]

---
```

---

## Implementation

### Components

1. **Query Processor** (`generic_framework/core/query_processor.py`)
   - Checks accumulator config
   - Determines if mode matches
   - Loads accumulator content
   - Passes to persona as context

2. **Persona** (`generic_framework/core/persona.py`)
   - Receives accumulator content in context
   - Prepends to prompt
   - Generates response with full context

3. **Accumulator Helper Functions**
   - `_check_accumulator_trigger()` - Tests for trigger phrases
   - `_load_accumulator_content()` - Reads accumulator file
   - `_append_to_accumulator()` - Writes to accumulator file

### Code Flow

```python
# In query_processor.py - process_query()

# 1. Check if accumulator enabled
if accumulator_config.get("enabled", False):
    mode = accumulator_config.get("mode", "triggers")

    # 2. Determine if should load context
    if mode == "all" or (mode == "triggers" and trigger_detected):
        accumulator_content = _load_accumulator_content(...)

        # 3. Inject into prompt context
        context["accumulator_prefix"] = f"Story so far:\n\n{accumulator_content}\n\n---\n\n"

# 4. Generate response (persona uses accumulator_prefix)
response = await persona.respond(query, context=context)

# 5. Append to accumulator
if should_append:
    _append_to_accumulator(domain_name, output_file, query, response)
```

---

## Use Cases

### Novel Writing (triggers mode)

**Setup:**
```json
{
  "mode": "triggers",
  "trigger_phrases": ["chapter", "continue"]
}
```

**Workflow:**
1. "I want a mystery novel set in 1920s England. Write chapter 1."
2. "Write chapter 2" → Continues from chapter 1
3. "What happens in chapter 3?" → Continues story
4. Novel builds chapter by chapter

### Recipe Development (all mode)

**Setup:**
```json
{
  "mode": "all",
  "output_file": "recipe_development.md"
}
```

**Workflow:**
1. "I'm developing a sourdough bread recipe" → Logged
2. "What flour should I use?" → Sees previous context
3. "How about hydration?" → Remembers flour discussion
4. "Add a starter recipe" → Remembers entire development thread

### Research Threads (all mode)

**Setup:**
```json
{
  "mode": "all",
  "output_file": "research_log.md"
}
```

**Workflow:**
1. "I'm researching Victorian literature" → Logged
2. "What about Dickens?" → Sees context
3. "Compare to Thackeray" → Remembers Dickens discussion
4. Builds complete research log over time

---

## Starting Fresh

To start a new story or conversation:

```bash
# Rename old accumulator
mv universes/MINE/domains/prose/stories/active_story.md \
   universes/MINE/domains/prose/stories/completed_story_01.md

# Or delete it
rm universes/MINE/domains/prose/stories/active_story.md
```

Next query starts with blank slate.

---

## Advantages

1. **Domain-specific memory** - Each domain has its own context
2. **Persistent across sessions** - Survives container restarts
3. **Configurable per domain** - Opt-in, different modes per domain
4. **Simple to use** - Just talk naturally, AI remembers everything
5. **Backward compatible** - Domains without config work as before

---

## Limitations

1. **Context window** - LLMs have token limits (handled by `max_context_chars`)
2. **File size** - Very long conversations will be truncated
3. **Manual management** - Starting fresh requires file deletion/renaming

---

## 🎓 The Personal University: Primary Use Case

### What Is It?

The Accumulator transforms ExFrame into a **personalized university system** where:
- Each domain = A course or subject
- Each accumulator = Your learning log/transcript
- The LLM = Your personal tutor who remembers EVERYTHING

### Why It's Revolutionary

**Traditional Education vs ExFrame University:**

| Aspect | Traditional University | ExFrame University |
|--------|----------------------|-------------------|
| **Memory** | Teacher forgets between sessions | AI remembers EVERYTHING |
| **Continuity** | Starts fresh each lesson | Builds on every discussion |
| **Pacing** | Fixed curriculum for everyone | Adapts to YOUR learning speed |
| **Availability** | Scheduled hours (10-15 weeks) | 24/7/365, forever |
| **Cost** | $50-100/hour for tutoring | ~$5/month for unlimited AI |
| **Personalization** | One-size-fits-all | Tailored to your struggles |

### Real Example: Learning Rust Programming

**Week 1: Foundations**
```
You: "I'm new to programming. Teach me Rust basics."
AI: "Great choice! Let's start with ownership..."
[Saved to rust_programming/learning_log.md]
```

**Week 2: Struggling**
```
You: "I still don't get borrowing."
AI: [Sees you've asked 3 times about borrowing]
    "Let me try a different approach. Remember when we compared
     ownership to library books? Think of borrowing like..."
[Saved to rust_programming/learning_log.md]
```

**Week 5: Progress Check**
```
You: "Quiz me on ownership and borrowing."
AI: [Reads 5 weeks of your learning journey]
    """
    You've struggled with borrowing but have shown improvement.
    You mastered ownership immediately.
    Let's test you on some edge cases...
    """
[Saved to rust_programming/learning_log.md]
```

**Week 10: Advanced Topics**
```
You: "I'm ready for lifetimes."
AI: [Sees 10 weeks of context]
    "Since you're solid on ownership and borrowing, lifetimes
     will make sense. They solve the 'when to free memory' problem..."
[Saved to rust_programming/learning_log.md]
```

### The Socratic Method

The accumulator enables AI-guided Socratic learning:

**Day 1:**
```
You: "What is entropy?"
AI: [Explains entropy with examples]
```

**Day 5:**
```
You: "How does entropy relate to information theory?"
AI: [Sees your Day 1 discussion]
    "Great connection! Remember when we discussed entropy as disorder?
    In information theory, entropy measures uncertainty..."
```

**Day 15:**
```
You: "Connect entropy to both thermodynamics AND information."
AI: [Reads your entire learning journey]
    "Perfect synthesis! You've grasped that entropy is the bridge between
     thermodynamic disorder and information content..."
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

### Creating Your University

**Example: Complete Curriculum**

```javascript
{
  "my_university": {
    "physics": {
      "quantum_mechanics": {
        "domain_id": "quantum_physics",
        "persona": "researcher",
        "accumulator": {
          "enabled": true,
          "mode": "all",
          "output_file": "learning_log.md"
        }
      },
      "relativity": {
        "domain_id": "relativity_theory",
        "persona": "researcher",
        "accumulator": {
          "enabled": true,
          "mode": "all",
          "output_file": "learning_log.md"
        }
      }
    },
    "programming": {
      "rust": {
        "domain_id": "rust_programming",
        "persona": "researcher",
        "accumulator": {
          "enabled": true,
          "mode": "all",
          "output_file": "learning_log.md"
        }
      },
      "python": {
        "domain_id": "python_basics",
        "persona": "librarian",
        "accumulator": {
          "enabled": true,
          "mode": "all",
          "output_file": "learning_log.md"
        }
      }
    },
    "history": {
      "renaissance": {
        "domain_id": "renaissance_history",
        "persona": "researcher",
        "accumulator": {
          "enabled": true,
          "mode": "all",
          "output_file": "learning_log.md"
        }
      }
    }
  }
}
```

Each domain is a self-contained course with its own memory.

### Cross-Domain Connections

The AI can reference your other learning:

```
In quantum_physics domain:
"This wave interference is similar to something in music_theory
 that you learned about last month..."

In rust_programming domain:
"This ownership concept is like the borrowing we discussed
 in your economics_domain..."
```

### The Cost

**Traditional tutoring:** $50-100/hour × 3 hours/week × 12 weeks = $1,800-3,600 per course

**ExFrame University:** $5/month for UNLIMITED courses, tutoring, and progress tracking

### Key Insight

> "Learn anything."

That's not hyperbole. The accumulator gives you:

1. **Persistent memory** - Never forgets what you discussed
2. **Adaptive pacing** - Slows down when you're stuck, speeds up when you're confident
3. **Always available** - 24/7/365, no appointments needed
4. **Cumulative context** - Each session builds on all previous ones
5. **Cross-references** - Connects topics across your different domains

**This is your personal university for $5/month.**

---

## Future Enhancements

Potential improvements:

1. **Multiple accumulators per domain** - Different topics in same domain
2. **Automatic summarization** - Summarize old content to save space
3. **Search within accumulator** - Jump to specific topics
4. **Branching** - Save multiple story paths
5. **Time-based decay** - Weight recent content higher than old
6. **Export options** - Export as PDF, EPUB, etc.

---

## Example Configurations

### Prose Domain (Novel Writing)

```json
{
  "domain_id": "prose",
  "accumulator": {
    "enabled": true,
    "mode": "triggers",
    "trigger_phrases": ["chapter", "continue", "part", "section"],
    "output_file": "stories/active_novel.md",
    "max_context_chars": 20000,
    "format": "markdown"
  }
}
```

### Cooking Domain (Recipe Development)

```json
{
  "domain_id": "cooking",
  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "recipe_development.md",
    "max_context_chars": 10000,
    "format": "markdown"
  }
}
```

### Research Domain (Knowledge Building)

```json
{
  "domain_id": "research",
  "accumulator": {
    "enabled": true,
    "mode": "all",
    "output_file": "knowledge_thread.md",
    "max_context_chars": 25000,
    "format": "markdown"
  }
}
```

---

## Technical Details

### File Location

Accumulator files are stored in domain directories:

```
universes/MINE/domains/
  prose/
    stories/
      active_story.md
  cooking/
    recipe_development.md
  research/
    knowledge_thread.md
```

### Character Encoding

All files use UTF-8 encoding for full Unicode support.

### Error Handling

- If file doesn't exist: Returns `None`, starts fresh
- If directory doesn't exist: Creates automatically
- If append fails: Logs warning, doesn't break query
- File truncated if exceeds `max_context_chars`

---

## Testing

### Test Conversation Memory

```bash
# Message 1
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query":"My name is Peter","domain":"prose"}'

# Message 2 - should remember
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query":"What is my name?","domain":"prose"}'
```

Expected: AI responds "Peter"

### Test Novel Writing

```bash
# Chapter 1
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query":"Write chapter 1 about space","domain":"prose"}'

# Chapter 2
curl -X POST http://localhost:3000/api/query/phase1 \
  -H "Content-Type: application/json" \
  -d '{"query":"Write chapter 2","domain":"prose"}'
```

Expected: Chapter 2 continues story from Chapter 1

---

## Summary

The Accumulator provides **persistent, domain-specific conversation memory** that makes the LLM appear to remember everything you've discussed. It's simple to configure, easy to use, and works for any domain that needs sequential context.

**Two modes:**
- `"all"` - Remember everything (conversation memory)
- `"triggers"` - Remember on demand (story writing)

**Key insight:** It's like giving each domain its own long-term memory!
