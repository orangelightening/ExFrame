# Web Search Implementation Attempts

**Date:** 2026-02-10
**Goal:** Enable web search functionality for queries starting with `//`
**Status:** Partially working - simple queries work, web queries still time out

---

## Problem Statement

Web search was working 2-3 days ago with real citations and internet data. Now returns "no internet disclaimer" or times out. User wants `//` prefix to trigger web search for current information (weather, news, etc.).

---

## What We Tried

### 1. DuckDuckGo Scraper Approach
**File:** `generic_framework/core/research/internet_strategy.py`

**What we did:**
- Already implemented DuckDuckGo HTML scraper
- Returns search result snippets (titles, URLs, short descriptions)
- Issue: Snippets don't contain actual data (just "Get current weather report..." not the temperature itself)
- LLM was hallucinating based on snippets

**Result:** ❌ Scraper works but only returns meta-descriptions, not actual data

### 2. Research Specialist Two-Stage Flow
**File:** `generic_framework/plugins/research/research_specialist.py`

**What we did:**
- Has `enable_web_search: true` in config
- Requires `web_search_confirmed: True` in context to perform web search
- Extended Search button calls `/api/query/extend-web-search` with flag set
- DuckDuckGo finds URLs → LLM should process results

**Issues found:**
- Button not appearing initially (sidekick domain using old `query_processor` not GenericAssistantEngine)
- Sidekick domain had `domain_type: ""` instead of `"4"` (Type 4)
- No LLM enricher configured to process web search results

**Fixes applied:**
- Set sidekick `domain_type: "4"`
- Added LLM enricher to sidekick domain config
- Restored two-stage flow: local search first → Extended Search button → web search

**Result:** ❌ Button appeared but web search still not working

### 3. GLM Native Web Search Tool

**Files:** `generic_framework/assist/engine.py`, `generic_framework/core/persona.py`

**What we tried:**

#### Attempt 1: Tools parameter without name
```python
payload["tools"] = [{"type": "web_search"}]
```
**Error:** HTTP 422 - "Field required: name"

#### Attempt 2: Added name field
```python
payload["tools"] = [{"type": "web_search", "name": "web_search"}]
```
**Error:** HTTP 422 - Still missing name field

#### Attempt 3: Function format with tool-level name
```python
payload["tools"] = [{
    "type": "function",
    "name": "web_search",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        }
    }
}]
```
**Error:** HTTP 400 - "Unknown Model, please check the model code"

#### Attempt 4: Different model names
- `glm-4-alltools` - HTTP 400 Unknown Model
- `glm-4-flash` - Not tested
- Back to `glm-4.7` - Works but without tools

**Result:** ❌ Tools format rejected or model not found

### 4. Endpoint Discovery

**Original:** `https://api.z.ai/api/anthropic` (Anthropic-compatible)

**User found correct endpoint:** `https://api.z.ai/api/coding/paas/v4` (Native Z.AI GLM)

**What we changed:**
```bash
# .env file
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
```

**Result:** ✅ Endpoint changed, but...

### 5. Timeout Issues

**Error:** `httpx.ReadTimeout` after 120 seconds

**Symptoms:**
- `// hello` - Long delay then timeout
- GLM trying to use tools but request hanging

**Fix applied:**
- Increased timeout: 120s → 180s
- Smart tool detection: Only enable tools for queries that need current info
  - Keywords: weather, news, current, latest, price, stock, temperature, forecast, today, now, recent
  - Simple greetings skip tools

**Result:** ⚠️ Needs testing

---

## Current State

### Working
- ✅ `//` prefix recognition
- ✅ Correct Z.AI endpoint: `https://api.z.ai/api/coding/paas/v4`
- ✅ Model: `glm-4.7`
- ✅ Simple queries without tools should work fast
- ✅ Increased timeout (180s)

### Not Working / Needs Testing
- ❓ Web search tool calls still timing out
- ❓ Whether GLM actually executes web search or returns tool_calls
- ❓ Need to test if weather queries now return real data

---

## Root Cause Analysis

### Why Was It Working Before?

**Theory:** GLM's web search functionality requires:
1. **Correct endpoint** - Native Z.AI endpoint not Anthropic-compatible
2. **Correct tools format** - Proper function-calling format with all required fields
3. **Model that supports tools** - GLM-4.7 does, but only through native endpoint
4. **Tool call handling** - When GLM returns `tool_calls`, we may need to send second request

The issue was likely using wrong endpoint (`/api/anthropic` instead of `/api/coding/paas/v4`).

---

## What To Do Next

### Immediate (Test Current Implementation)
1. **Test simple query:** `// hello`
   - Should respond quickly without tools
   - Verify no timeout

2. **Test weather query:** `// what's the weather in Nanaimo?`
   - Should use web_search tool
   - Should return real current temperature
   - Check if still times out

3. **Check logs** for tool_calls:
   ```bash
   docker logs eeframe-app | grep -i "tool_call\|web_search"
   ```

### If Still Timing Out (Tool Call Handling)

GLM may be returning `tool_calls` in the response that we're not handling. Need to implement multi-turn flow:

1. **First request:** Send query with tools
2. **GLM responds:** Returns `tool_calls` instead of `content`
3. **Second request:** Send tool call confirmation back to GLM
4. **GLM executes:** Actually performs web search
5. **Final response:** Returns answer with web data

**Code changes needed in** `generic_framework/core/persona.py`:
```python
# Check if response has tool_calls instead of content
if "tool_calls" in data:
    # Extract tool calls and send confirmation
    # Then make second request to get actual answer
```

### Alternative Approaches

#### Option A: Use Z.AI MCP Web Search Server
**Documentation:** https://docs.z.ai/llms.txt (Web Search MCP Server)

**Endpoint:** `https://api.z.ai/api/mcp/web_search_prime/mcp`

**Pros:**
- Dedicated web search service
- Separates concerns (LLM + web search)
- Better quota management

**Cons:**
- Requires MCP client implementation
- More complex integration
- Additional service dependency

#### Option B: Weather API for Weather Queries
Use OpenWeatherMap or similar for weather-specific queries:
- Free tier: 1000 calls/day
- Reliable, fast, no tool call complexity
- Only solves weather, not general web search

**Implementation:** Add weather API call when query contains "weather"

#### Option C: Remove Tools, Use System Prompt
Tell GLM in the prompt to use its internal web search:
```
"You have access to web search. For queries about current information,
use your browser to search online."
```

**Pros:** Simple
**Cons:** May not actually trigger GLM's web search - depends on training

---

## Configuration Reference

### Current Working Config

```bash
# .env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
LLM_MODEL=glm-4.7
```

### Sidekick Domain Config

```json
{
  "domain_id": "sidekick",
  "domain_type": "4",
  "persona": "researcher",
  "specialists": [
    {
      "specialist_id": "research_specialist",
      "config": {
        "enable_web_search": true
      }
    }
  ],
  "enrichers": [
    {
      "plugin_id": "llm_enricher",
      "config": {
        "mode": "enhance"
      }
    }
  ]
}
```

---

## Lessons Learned

1. **Endpoint Matters:** Z.AI has multiple endpoints, only some support tools properly
   - `/api/anthropic` - Anthropic-compatible, limited tool support
   - `/api/coding/paas/v4` - Native GLM, full tool support

2. **Tools Format is Strict:** GLM requires exact format:
   - Type must be "function"
   - Must have "name" at tool level
   - Must have "function" object with schema
   - All fields required or get 422 error

3. **Model Names:** Not all GLM variants support tools
   - `glm-4.7` - Supports tools (with correct endpoint)
   - `glm-4-alltools` - Unknown model, 400 error
   - `glm-4-flash` - Not tested

4. **Tool Call Flow:** May require multi-turn conversation:
   - Request with tools → tool_calls response → confirmation → final answer
   - Not a single request/response cycle

5. **Timeouts Matter:** Tool calls take longer than normal queries
   - Normal: 10-30 seconds
   - With tools: 60-180 seconds

---

## Git Commits Reference

```
37ee8709 - fix: increase timeout and only use tools for web-requiring queries
d4d23c5d - fix: use correct Z.AI coding endpoint and enable web search
4ae5551a - revert: use glm-4.7 standard model, web search disabled
bfdf5b9 - debug: disable web_search to test if model works
859b6b46 - fix: add name field at tool level for GLM
e47d87ad - fix: add web_search tool for GLM-4.7
c7d6818e - fix: remove tools parameter, let GLM use automatic web search
69b967f8 - fix: explicitly tell GLM to use web search in prompt
3c98812c - fix: add name field to GLM web_search tool
5c2a03b8 - fix: enable GLM web_search for // direct prompts
7381c787 - fix: add LLM enricher to sidekick domain for web search processing
46a17962 - fix: set sidekick domain_type to 4 for specialist system
7021d5c4 - revert: restore web_search_confirmed flag requirement
471932ab - fix: auto-enable web search for researcher persona
```

---

## Testing Checklist

- [ ] `// hello` - Should respond quickly (< 10 seconds)
- [ ] `// what's the weather in Nanaimo?` - Should return real weather
- [ ] `// latest news about AI` - Should return recent news
- [ ] Normal query without `//` - Should use local patterns only
- [ ] Extended Search button appears after local search
- [ ] Extended Search button triggers web search
- [ ] No HTTP 422/400 errors
- [ ] No ReadTimeout errors
- [ ] Real citations from actual websites
- [ ] Current data (not hallucinated)

---

## Status Summary

**Fixed:**
- Correct Z.AI endpoint configuration
- Domain type set correctly for Type 4
- LLM enricher configured
- Smart tool detection (only for web-requiring queries)
- Increased timeout

**Broken/Unknown:**
- Web search actually working (still times out)
- Tool call response handling
- Real-time data returned

**Next Step:** Test current implementation to see if correct endpoint + smart detection fixes the timeout issue.
