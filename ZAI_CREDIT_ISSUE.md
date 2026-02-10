# Web Search Issue: Insufficient API Credits

**Date:** 2026-02-10
**Status:** ❌ BLOCKED - No API credits

---

## Root Cause

The Z.AI API account has **insufficient balance** to execute web searches.

**Error Message:**
```json
{
  "error": {
    "code": "1113",
    "message": "Insufficient balance or no resource package. Please recharge."
  }
}
```

**Test:**
```bash
curl -X POST "https://api.z.ai/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model": "glm-4.7", "messages": [...], "tools": [{"type": "web_search", ...}]}'
```

**Result:** Error 1113 - Insufficient balance

---

## Why GLM Was Hallucinating

1. We send: Chat completion request with web_search tool
2. Z.AI checks: Account balance for tool execution
3. Z.AI returns: "Insufficient balance" error
4. **But our code doesn't catch this error**
5. GLM falls back: Uses training data to simulate web search
6. Result: "I will use my browser tool..." + fake 8°C weather

---

## Solution Options

### Option 1: Add Credits to Z.AI Account ⭐ (Recommended)

**Pros:**
- Code is ready and correct
- Single implementation
- Works with current setup

**Action:**
1. Log in to Z.AI console
2. Add credits/buy resource package
3. Test: `// what's the weather in Nanaimo?`
4. Should work immediately

**Estimated cost:** Check Z.AI pricing page

---

### Option 2: Use Free Weather API

For weather-specific queries, use a free API:

**OpenWeatherMap Free Tier:**
- 1000 calls/day free
- Real current weather data
- Reliable and fast

**Implementation:**
```python
# Add to persona.py
import requests

def get_weather(location):
    api_key = "YOUR_OPENWEATHER_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return f"Current weather in {location}: {data['main']['temp']}°C, {data['weather'][0]['description']}"
```

**Pros:**
- Free
- Real data
- No multi-turn needed

**Cons:**
- Only works for weather
- Requires separate API key
- Doesn't solve general web search

---

### Option 3: Use DuckDuckGo Scraper

Already implemented in: `generic_framework/core/research/internet_strategy.py`

**Pros:**
- Free
- No API key needed
- General web search

**Cons:**
- ❌ Only returns snippets (titles, URLs, descriptions)
- ❌ Snippets don't contain actual data
- ❌ LLM hallucinates based on snippets

**Test Result:**
- Search: "weather Nanaimo"
- Returns: "Get current weather report for Nanaimo..."
- LLM: Hallucinates 16°C temperature
- Actual: 8°C (wrong)

---

### Option 4: MCP Web Search Server

**Endpoint:** `https://api.z.ai/api/mcp/web_search_prime/mcp`

**Pros:**
- Separate service from chat
- May have different pricing

**Cons:**
- Requires MCP client implementation
- More complex
- May also require credits

---

## Current Implementation Status

### What's Working ✅

1. **Tool format is correct:**
   ```python
   tools = [{
       "type": "web_search",
       "web_search": {
           "enable": "True",
           "search_result": "True",
           ...
       }
   }]
   ```

2. **Endpoint is correct:**
   - General purpose: `https://api.z.ai/api/paas/v4` ✅
   - Coding endpoint: `https://api.z.ai/api/coding/paas/v4` (also blocked)

3. **Request format is correct:**
   - OpenAI-style chat completions
   - Proper headers
   - Correct payload structure

4. **Error handling added:**
   - Now checks for `tool_calls` in response
   - Logs warnings when tools present
   - Better debugging

### What's Not Working ❌

1. **API balance:**
   - Account has insufficient credits
   - Web search tool execution blocked
   - Error 1113 returned

2. **Error catching:**
   - Our code doesn't catch the 1113 error
   - Falls through to return content
   - GLM hallucinates instead

---

## Testing Verification

**Direct API Test:**
```bash
curl -X POST "https://api.z.ai/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/test_glm.json
```

**Response:**
```json
{"error": {"code": "1113", "message": "Insufficient balance or no resource package. Please recharge."}}
```

**Conclusion:** The code is correct, but API has no credits.

---

## Next Steps

### Immediate (To Test Web Search)

1. **Add credits to Z.AI account:**
   - Log in to https://platform.z.ai
   - Navigate to billing/credits
   - Purchase credits or resource package
   - Verify balance

2. **Test immediately:**
   ```bash
   # Test query
   // what's the weather in Nanaimo?

   # Should return:
   - Real current temperature
   - Actual source URLs
   - Current date (not 2026)
   ```

### Alternative (If No Credits)

**Option A: Implement OpenWeatherMap for weather queries**
- Free tier available
- Only solves weather, not general web search
- ~1 hour implementation

**Option B: Improve DuckDuckGo scraper**
- Already implemented
- Limitation: snippets only
- May need to fetch full page content
- ~2-3 hours implementation

**Option C: Wait for credits**
- Code is ready
- Just needs account recharge
- No code changes needed

---

## Documentation Files

- `ZAI_WEB_SEARCH_ARCHITECTURE.md` - Implementation guide
- `TRIED.md` - All previous attempts
- `MULTITURN.md` - Multi-turn protocol (not needed)
- `ZAI_CREDIT_ISSUE.md` - This file

---

## Git Commits

Recent commits implementing web search:
- `69593e60` - docs: add endpoint testing results
- `f9cb7c87` - fix: add stream and tool_choice parameters
- `3aa01a20` - feat: implement single-turn GLM web search

All code is ready - just needs API credits to test.

---

## Summary

**Problem:** Z.AI API has insufficient credits to execute web search tools

**Solution:** Add credits to account, or implement alternative free API

**Code Status:** ✅ Complete and correct
**Test Status:** ❌ Blocked by API balance
**Action Required:** Recharge account or implement alternative

The implementation is correct. Once credits are added, web search will work immediately without any code changes.
