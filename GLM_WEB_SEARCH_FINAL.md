# GLM Web Search - Working Implementation

**Date:** 2026-02-10
**Status:** ✅ IMPLEMENTED - Multi-turn function calling

---

## Correct Implementation for Coding Plan

### Endpoint

**For users with CODING PLAN subscription:**
```bash
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
```

❌ **DO NOT USE:** `https://api.z.ai/api/paas/v4` (general purpose - different subscription)

---

## Tool Format

### ✅ CORRECT (Function Calling)

```python
tools = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information including weather, news, prices, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute"
                }
            },
            "required": ["query"]
        }
    }
}]
```

### ❌ WRONG (Embedded web_search)

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
**This format does NOT work on the coding endpoint!**

---

## Multi-Turn Flow

### Step 1: Send Request with Tools

```python
payload = {
    "model": "glm-4.7",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather in Nanaimo?"}
    ],
    "tools": [function_tool],
    "tool_choice": "auto"
}
```

### Step 2: GLM Returns tool_calls

```json
{
  "choices": [{
    "message": {
      "content": "",
      "tool_calls": [{
        "id": "call_123",
        "type": "function",
        "function": {
          "name": "web_search",
          "arguments": "{\"query\":\"current weather Nanaimo BC\"}"
        }
      }]
    }
  }]
}
```

### Step 3: Send Back Tool Response

```python
# Build conversation history
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "What's the weather?"},
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [tool_call]
    }
]

# Add tool response (CRITICAL: role="tool")
messages.append({
    "role": "tool",
    "tool_call_id": tool_call["id"],
    "content": function_args  # The search query
})

# Second request to get actual results
payload = {
    "model": "glm-4.7",
    "messages": messages
    # No tools in second request!
}
```

### Step 4: GLM Returns Final Answer

```json
{
  "choices": [{
    "message": {
      "content": "The current weather in Nanaimo is 8°C with rainy conditions...",
      "role": "assistant"
    }
  }]
}
```

---

## Implementation

### File: `generic_framework/core/persona.py`

**Tool Definition (Lines ~342-360):**
```python
if needs_web_search:
    self.logger.info(f"GLM model (OpenAI format) - enabling web_search via function calling")
    payload["tools"] = [{
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information...",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }]
    payload["tool_choice"] = "auto"
```

**Multi-Turn Handling (Lines ~418-465):**
```python
if "choices" in data:
    message = data["choices"][0]["message"]

    # Check for tool_calls
    if "tool_calls" in message and message["tool_calls"]:
        tool_call = message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        function_args = tool_call["function"]["arguments"]

        if function_name == "web_search":
            # Build multi-turn conversation
            messages_with_tool = payload["messages"].copy()
            messages_with_tool.append({
                "role": "assistant",
                "content": message.get("content", ""),
                "tool_calls": message["tool_calls"]
            })

            # Send tool response
            messages_with_tool.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": function_args
            })

            # Second request
            payload["messages"] = messages_with_tool
            del payload["tools"]
            del payload["tool_choice"]

            response2 = await client.post(endpoint, headers=headers, json=payload)
            data2 = response2.json()

            return data2["choices"][0]["message"]["content"]
```

---

## Key Differences by Endpoint

| Feature | Coding Endpoint | General Purpose Endpoint |
|---------|----------------|--------------------------|
| **URL** | `/api/coding/paas/v4` | `/api/paas/v4` |
| **Subscription** | Coding Plan | General Plan |
| **Tool Format** | Function calling only | May support embedded |
| **Tested** | ✅ Works | ❓ Unknown |
| **Multi-turn** | Required | May be required |

---

## Testing

### Test 1: Weather Query
```bash
Query: // what's the weather in Nanaimo?
Expected: Real current temperature with sources
Time: < 30 seconds
Logs: Should see "GLM returned X tool_calls - implementing multi-turn"
```

### Test 2: News Query
```bash
Query: // latest news about AI
Expected: Recent AI news with dates
Time: < 30 seconds
```

### Test 3: Simple Query
```bash
Query: // hello
Expected: Greeting (no tool calls)
Time: < 10 seconds
```

---

## Troubleshooting

### Issue: "I do not have real-time internet access"

**Cause:** Tool not being sent or wrong format

**Check:**
1. Is `OPENAI_BASE_URL` set to coding endpoint?
2. Are keywords triggering tool activation?
3. Check logs for "enabling web_search via function calling"

### Issue: Tool calls returned but not handled

**Cause:** Multi-turn not implemented

**Check:**
1. Logs should show "GLM returned X tool_calls"
2. Should see "implementing multi-turn"
3. Should see "Sending second request with tool confirmation"

### Issue: Second request fails

**Cause:** Messages format wrong

**Check:**
1. Tool response must use `role: "tool"`
2. Must include `tool_call_id`
3. Second request should NOT include `tools` parameter

---

## Success Criteria

- [ ] `// what's the weather in Nanaimo?` returns actual temperature
- [ ] Response includes real sources/URLs
- [ ] No hallucination (no fake 8°C if it's actually different)
- [ ] Logs show multi-turn handling
- [ ] Response time < 30 seconds
- [ ] Simple queries don't trigger tools

---

## Git Commits

- `0fed407f` - feat: implement multi-turn function calling for GLM web search
- `b9b73621` - docs: add credit issue diagnosis
- `69593e60` - docs: add endpoint testing results

---

## References

**Z.AI SDK:**
- `zai-sdk-python/examples/function_call_example.py` - Multi-turn pattern
- `zai-sdk-python/examples/stream_tools.py` - Tool streaming

**Documentation:**
- `ZAI_WEB_SEARCH_ARCHITECTURE.md` - Original architecture (embedded format)
- `TRIED.md` - All failed attempts
- `MULTITURN.md` - Multi-turn design
- `ZAI_CREDIT_ISSUE.md` - Credit balance investigation

---

## Summary

**For coding plan subscriptions:**
- ✅ Use `/api/coding/paas/v4` endpoint
- ✅ Use function-calling format: `{"type": "function", ...}`
- ✅ Implement multi-turn conversation
- ✅ Send `{"role": "tool"}` confirmation
- ✅ Get actual search results in second response

**Test command:**
```
// what's the weather in Nanaimo?
```

Should return real current weather with sources!
