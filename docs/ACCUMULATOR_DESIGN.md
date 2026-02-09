# Story Accumulator Design Document

**Status:** ✅ Implemented
**Version:** 1.0
**Last Updated:** 2026-02-09

---

## Overview

The **Accumulator** is a domain-level feature that provides **sequential context memory** for LLM conversations. It enables:

1. **Story writing** - Chapter-by-chapter novel creation
2. **Conversation memory** - Ongoing dialogue with full history
3. **Project continuity** - Long-running discussions that build context over time

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
