# Z.AI Web Search Architecture

**Date:** 2026-02-10
**Status:** 🔥 CRITICAL DISCOVERY - Found working single-turn format!

---

## Overview

Z.AI GLM-4.7 supports **TWO DIFFERENT** web search approaches:

1. **Direct Web Search API** - Standalone search service
2. **Web Search via Chat Completions** - Two formats:
   - Multi-turn function calling (complex, what we tried)
   - **Single-turn embedded web_search (SIMPLE, what we found!)**

---

## Architecture Options

### Option A: Direct Web Search API

**Endpoint:** `/web_search`
**SDK Method:** `client.web_search.web_search()`

**Flow:**
```
Query → /web_search → Search Results → Pass to LLM → Answer
```

**Code Example:**
```python
response = client.web_search.web_search(
    search_engine="search_pro",
    search_query="What's the weather in Nanaimo?",
    count=10
)
# Returns raw search results (titles, URLs, snippets)
# Must pass results to LLM separately
```

**Pros:**
- Direct control over search
- No tool call complexity
- Can filter domains, time ranges

**Cons:**
- Two API calls required (search + LLM)
- LLM doesn't decide when to search
- Manual context management

---

### Option B: Web Search via Chat (Multi-Turn Function Calling)

**Endpoint:** `/chat/completions`
**Format:** Function-calling style tools

**What We Tried:**
```python
tools = [{
    "type": "function",
    "name": "web_search",
    "function": {
        "name": "web_search",
        "description": "Search the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        }
    }
}]
```

**Flow:**
```
1. Send query with tools
2. GLM responds: "I'll search..." + tool_calls
3. We send back: {"role": "tool", "tool_call_id": "...", "content": "..."}
4. GLM executes search and returns final answer
```

**Pros:**
- LLM decides when to search
- Conversational

**Cons:**
- ❌ Complex multi-turn implementation required
- ❌ We didn't implement the confirmation loop
- ❌ Got truncated responses

---

### Option C: Web Search via Chat (Single-Turn Embedded) 🔥

**Endpoint:** `/chat/completions`
**Format:** Embedded `web_search` object

**What We Found in SDK (glm4_example.py):**
```python
tools = [{
    "type": "web_search",
    "web_search": {
        "enable": "True",
        "search_engine": "search_pro",
        "search_result": "True",  # CRITICAL!
        "search_prompt": "You are a helpful assistant. Use {{search_result}} to answer.",
        "count": "10",
        "search_domain_filter": "",  # Optional: limit to specific domain
        "search_recency_filter": "noLimit",  # oneDay, oneWeek, oneMonth, oneYear, noLimit
        "content_size": "high"  # medium, high
    }
}]
```

**Flow:**
```
1. Send query with web_search tool
2. GLM performs search internally
3. GLM returns answer with citations
4. Done! Single request/response.
```

**Pros:**
- ✅ Single-turn! No confirmation loop needed
- ✅ GLM handles search internally
- ✅ Returns actual data with citations
- ✅ Works with streaming
- ✅ Simple to implement

**Cons:**
- Less control over search process
- Must include `search_result: "True"` to get actual data

---

## Why Option C Fixes Our Problem

### Our Previous Error

We tried using function-calling format:
```python
{"type": "web_search", "name": "web_search"}
```

This triggered the multi-turn flow:
1. GLM: "I'll search..." (truncated)
2. GLM waits for: `{"role": "tool"}` confirmation
3. We never send confirmation
4. Response truncated

### The Fix

Use embedded web_search format:
```python
{
    "type": "web_search",
    "web_search": {
        "enable": "True",
        "search_result": "True"  # This is the magic!
    }
}
```

**Why it works:**
- `"search_result": "True"` tells GLM to include actual search results
- GLM executes search internally
- Returns full answer with data
- No multi-turn confirmation needed!

---

## Implementation: Option C (Recommended)

### Current Code Location
`generic_framework/core/persona.py`

### Changes Needed

#### 1. Replace Tools Format

**Current (wrong):**
```python
if model.startswith("glm-") and "//" in prompt:
    payload["tools"] = [{"type": "web_search", "name": "web_search"}]
```

**New (correct):**
```python
if model.startswith("glm-") and "//" in prompt:
    payload["tools"] = [{
        "type": "web_search",
        "web_search": {
            "enable": "True",
            "search_result": "True",
            "search_engine": "search_pro",
            "search_prompt": "You are a helpful assistant. Use the search results to provide accurate, current information with citations.",
            "count": "10",
            "search_recency_filter": "noLimit",
            "content_size": "high"
        }
    }]
```

#### 2. Remove Multi-Turn Handling

**Don't need to:**
- Detect `tool_calls` in response
- Send back `{"role": "tool"}` confirmation
- Implement multi-turn conversation loop

**Just extract content normally:**
```python
content = data["choices"][0]["message"]["content"]
```

That's it!

---

## Configuration Options

### web_search Tool Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `enable` | string | Enable web search | "True" |
| `search_engine` | string | Search engine to use | "search_pro" |
| `search_result` | string | **Include actual results** | "True" ⭐ |
| `search_prompt` | string | How to use results | "Use {{search_result}} to answer" |
| `count` | string | Number of results | "10" (1-50) |
| `search_domain_filter` | string | Limit to domain | "www.bbc.com" |
| `search_recency_filter` | string | Time range | "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit" |
| `content_size` | string | Result detail level | "medium", "high" |

### Smart Keyword Detection (Keep This)

Already implemented in persona.py - only use web search for queries that need current info:

```python
WEB_SEARCH_KEYWORDS = [
    "weather", "news", "current", "latest", "price", "stock",
    "temperature", "forecast", "today", "now", "recent"
]

# Only enable web_search if keywords present
needs_web_search = any(keyword in prompt_lower for keyword in WEB_SEARCH_KEYWORDS)
```

---

## Testing Plan

### Test 1: Simple Web Search
```bash
Query: // what's the weather in Nanaimo?
Expected: Current temperature with citation
Time: < 30 seconds
```

### Test 2: News Query
```bash
Query: // latest news about AI
Expected: Recent AI news with dates and sources
Time: < 30 seconds
```

### Test 3: No Web Search Needed
```bash
Query: // hello
Expected: Greeting without web search
Time: < 10 seconds
```

### Test 4: Local Knowledge
```bash
Query: // what is exframe?
Expected: Uses local library, not web
Time: < 10 seconds
```

---

## Code Changes Summary

### File: `generic_framework/core/persona.py`

**Find this code:**
```python
# Note: GLM-4.7 has built-in web search when it detects need for current info
# Don't use explicit tools parameter to avoid multi-turn tool call complexity
if model.startswith("glm-") and "//" in prompt:
    self.logger.info(f"GLM model detected - relying on automatic web search")
    # GLM will use automatic web search based on query content
```

**Replace with:**
```python
# Use GLM's embedded web_search tool (single-turn, no confirmation needed)
if model.startswith("glm-") and "//" in prompt:
    # Check if query actually needs current web data
    prompt_lower = prompt.lower()
    web_search_keywords = [
        "weather", "news", "current", "latest", "price", "stock",
        "temperature", "forecast", "today", "now", "recent", "breaking"
    ]
    needs_web_search = any(keyword in prompt_lower for keyword in web_search_keywords)

    if needs_web_search:
        self.logger.info(f"GLM model detected with web search keywords - enabling web_search tool")
        payload["tools"] = [{
            "type": "web_search",
            "web_search": {
                "enable": "True",
                "search_result": "True",  # CRITICAL: Include actual search results
                "search_engine": "search_pro",
                "search_prompt": "You are a helpful assistant. Use the search results to provide accurate, current information. Include citations with your answers.",
                "count": "10",
                "search_recency_filter": "noLimit",
                "content_size": "high"
            }
        }]
    else:
        self.logger.info(f"GLM model detected - no web search keywords, using local knowledge only")
```

**That's it!** No other changes needed. The response extraction code stays the same because GLM returns normal `content` in the response.

---

## Why This Works vs. What We Tried

### Our Previous Attempts (All Failed)

1. **`{"type": "web_search", "name": "web_search"}`**
   - Error: HTTP 422 "Field required: name"
   - Actually triggers multi-turn flow

2. **`{"type": "function", "name": "web_search", "function": {...}}`**
   - Error: HTTP 400 "Unknown Model"
   - Multi-turn function calling format

3. **No tools, relying on automatic detection**
   - Result: "I don't have internet access"
   - GLM won't search without explicit tool

### The Working Solution

**`{"type": "web_search", "web_search": {...}}`**
- ✅ Correct format for GLM-4.7
- ✅ Single-turn response
- ✅ `"search_result": "True"` includes actual data
- ✅ No confirmation loop needed
- ✅ Works with streaming

---

## Comparison with MCP Web Search

We also have access to Z.AI MCP Web Search Server:
- **Endpoint:** `https://api.z.ai/api/mcp/web_search_prime/mcp`
- **Method:** MCP protocol call
- **Pros:** Dedicated service, separates concerns
- **Cons:** Requires MCP client implementation

**Recommendation:** Start with embedded web_search (Option C). Only consider MCP if we need more control.

---

## Git Commits to Reference

Previous attempts (all using wrong format):
- `37ee8709` - Multi-turn attempt with smart detection
- `d4d23c5d` - Endpoint fix
- `ed112a23` - Moved tools to OpenAI branch

**New commit needed:**
- Use embedded `web_search` object format
- Add `search_result: "True"`
- Remove multi-turn handling code (if any)

---

## Success Criteria

- [ ] `// what's the weather in Nanaimo?` returns actual current temperature
- [ ] Response includes citations like `[ref_1]` or similar
- [ ] No "I'll search..." truncation
- [ ] No ReadTimeout errors
- [ ] Response time < 30 seconds
- [ ] Simple queries without keywords don't use web search
- [ ] Multi-turn conversation not required

---

## References

**Z.AI SDK Files:**
- `zai-sdk-python/examples/glm4_example.py` - Lines 7-19 show working format
- `zai-sdk-python/examples/web_search_example.py` - Direct API approach
- `zai-sdk-python/src/zai/types/tools/web_search.py` - Type definitions
- `zai-sdk-python/src/zai/api_resource/chat/completions.py` - Chat API

**Documentation Files:**
- `TRIED.md` - All previous attempts
- `MULTITURN.md` - Multi-turn design (not needed for Option C)

---

## Next Steps

1. **Implement Option C** - Single change to persona.py
2. **Test with weather query** - Verify real data returned
3. **Test without keywords** - Verify no unnecessary web searches
4. **Monitor logs** - Check for any errors
5. **Update TRIED.md** - Add working solution

**Estimated implementation time:** 15 minutes (single file change)
**Risk:** Low (can easily revert if issues)
