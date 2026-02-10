# Multi-Turn Tool Call Handling Design Document

**Purpose:** Implement proper conversation loop for GLM-4.7 tool usage
**Date:** 2026-02-10
**Status:** Design - Not Implemented

---

## Z.AI SDK Protocol (ACTUAL - VERIFIED)

Source: https://github.com/zai-org/zai-sdk-python/examples/function_call_example.py

### The Actual Multi-Turn Flow

**Step 1: Initial Request with Tools**
```python
messages = [
    {"role": "user", "content": "What's the weather in Nanaimo?"}
]
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {...}
    }
}]

response = client.chat.completions.create(
    model="glm-4.7",
    messages=messages,
    tools=tools
)
```

**Step 2: GLM Returns tool_calls**
```python
# Response has tool_calls, not content
message = response.choices[0].message
# message.tool_calls = [
#     {
#         "type": "function",
#         "id": "call_abc123",
#         "function": {
#             "name": "get_weather",
#             "arguments": '{"location": "Nanaimo"}'
#         }
#     }
# ]

tool_call = message.tool_calls[0]
args = tool_call.function.arguments
```

**Step 3: Execute Function Locally**
```python
# Call the actual function
function_result = get_weather(**json.loads(args))
```

**Step 4: Send Back Tool Message with Results**
```python
messages.append({
    "role": "tool",
    "content": json.dumps(function_result),
    "tool_call_id": tool_call.id
})

response = client.chat.completions.create(
    model="glm-4.7",
    messages=messages,
    tools=tools
)
```

**Step 5: GLM Returns Final Answer**
```python
final_message = response.choices[0].message
content = final_message.content  # Final answer with function results
```

---

## Key Implementation Details

### 1. Tool Message Format

**NOT** `"role": "assistant"` but **`"role": "tool"`**

```python
messages.append({
    "role": "tool",  # IMPORTANT: Not "assistant"
    "content": json.dumps(function_result),
    "tool_call_id": tool_call.id
})
```

### 2. Function Execution

For web_search, GLM handles execution server-side:
- We just send back confirmation (maybe with empty content?)
- GLM executes search internally
- Returns final answer with search results

### 3. For Web Search Specifically

From Z.AI types:
```python
class WebSearchMessageToolCall:
    id: str
    search_intent: Optional[SearchIntent]
    search_result: Optional[SearchResult]
    search_recommend: Optional[SearchRecommend]
    type: str
```

Web search might be a **special built-in tool** not a generic function.

---

## Problem Statement

Current implementation sends tool definitions to GLM-4.7 but only handles single request/response cycle. GLM returns `tool_calls` requiring confirmation, but we never send it. Result: Truncated responses like "I'll search..." with no actual search execution.

---

## How GLM Tools API Works

### Single-Turn (Current - Broken)

```
Client → GLM: "What's the weather?" + tools parameter
GLM → Client: "I'll search..." (tool_call response)
❌ Client tries to extract content → Gets truncated message
```

### Multi-Turn (Required - Not Implemented)

```
Client → GLM: "What's the weather?" + tools parameter
GLM → Client: "I'll search..." (tool_call with web_search tool call)
Client → GLM: Tool call confirmation (tool_calls echoed back)
GLM → Client: Executes search + Returns answer with actual data
✅ Client extracts content → Gets real weather
```

---

## Design Solution

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│  Query Processing                           │
│  - User: "// weather in Nanaimo"            │
│  - Detects // prefix                         │
│  - Identifies need for web search           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  API Call 1: Request with Tools             │
│  - model: glm-4.7                          │
│  - tools: [web_search function]             │
│  - messages: [{role: user, content}]        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  GLM Response 1: Tool Call                 │
│  - content: "I'll search..."                │
│  - tool_calls: [{                          │
│      type: "function",                      │
│      function: {name: "web_search"}         │
│    }]                                       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ tool_calls?  │
         └──────┬───────┘
                │
         Yes │
                ▼
┌─────────────────────────────────────────────┐
│  Tool Call Handling (NEW CODE NEEDED)      │
│  1. Extract tool_calls                     │
│  2. Build confirmation payload              │
│  3. Append tool_calls to messages[]        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  API Call 2: Confirmation with Tool Calls   │
│  - messages: [                             │
│      {role: user, content: "..."},          │
│      {role: assistant, tool_calls: [...]}   │
│    ]                                       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  GLM Response 2: Final Answer               │
│  - content: "Current weather in Nanaimo..."  │
│  - Actual search results included            │
└─────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Tool Call Detection

**File:** `generic_framework/core/persona.py`
**Function:** `_call_llm()`

```python
async def _call_llm(self, prompt: str, context: Dict) -> str:
    # ... existing payload construction ...

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [...]  # Tools definition
    }

    response = await client.post(endpoint, json=payload)
    data = response.json()

    # NEW: Check for tool_calls
    if "choices" in data:
        msg = data["choices"][0]["message"]
        if "tool_calls" in msg:
            # Multi-turn required
            return await self._handle_tool_calls(
                prompt,
                msg["tool_calls"],
                model,
                temperature
            )

    # Single-turn response (normal case)
    return data["choices"][0]["message"]["content"]
```

### Phase 2: Tool Call Handler

**New function in** `generic_framework/core/persona.py`

```python
async def _handle_tool_calls(
    self,
    prompt: str,
    tool_calls: List[Dict],
    model: str,
    temperature: float
) -> str:
    """
    Handle GLM tool_calls by sending confirmation.

    Args:
        prompt: Original user prompt
        tool_calls: Tool calls from GLM's response
        model: Model name
        temperature: Temperature setting

    Returns:
        Final GLM response after tool execution
    """
    self.logger.info(f"Tool calls detected: {len(tool_calls)} tools")

    # Build confirmation payload
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "tool_calls": tool_calls}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    self.logger.info(f"Sending tool call confirmation to GLM")

    # Send confirmation
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    # Extract final content
    if "choices" in data:
        final_msg = data["choices"][0]["message"]

        # Check if there are more tool_calls (rare but possible)
        if "tool_calls" in final_msg:
            self.logger.warning(f"Multiple rounds of tool calls detected - not implemented")
            return "[Error: Multi-round tool calls not supported]"

        content = final_msg.get("content", "")
        self.logger.info(f"Final response received: {len(content)} chars")
        return content

    return "[Error: No content in final response]"
```

### Phase 3: Error Handling

**Scenarios to handle:**

1. **Tool call timeout**
   ```python
   timeout = httpx.Timeout(timeout=180.0, connect=60.0, pool=60.0)
   ```

2. **Invalid tool call format**
   ```python
   try:
       response = await client.post(...)
       response.raise_for_status()
   except HTTPStatusError as e:
       logger.error(f"Tool call failed: {e}")
       return f"[Error: Tool execution failed: {e}]"
   ```

3. **Empty content in final response**
   ```python
   if not content:
       logger.error("Tool executed but returned empty content")
       return "[Error: Tool returned no data]"
   ```

4. **Multiple rounds of tool calls** (not supported initially)
   ```python
   if "tool_calls" in final_msg:
       logger.warning("Multiple tool call rounds not supported")
       return "[Error: Multi-round tools require recursive implementation]"
   ```

---

## Code Changes Required

### Implementation Plan (UPDATED with Z.AI SDK Knowledge)

#### Phase 1: Tool Call Detection

**File:** `generic_framework/core/persona.py`
**Function:** `_call_llm()`

**Location:** After line 372 (response parsing)

**Current code:**
```python
data = response.json()

# Parse response based on API format
if "code" in data and "success" in data:
```

**New code:**
```python
data = response.json()

# Check for tool_calls (multi-turn required)
if "choices" in data:
    msg = data["choices"][0]["message"]

    # Tool calls detected - need multi-turn
    if "tool_calls" in msg and len(msg.get("tool_calls", [])) > 0:
        self.logger.info(f"Tool calls detected - entering multi-turn conversation")
        self.logger.debug(f"Tool calls: {msg['tool_calls']}")

        return await self._handle_tool_calls(prompt, msg['tool_calls'], messages)

    # No tool_calls - extract content directly
    content = msg.get("content", "")
    if content:
        return content

# ... rest of response parsing
```

#### Phase 2: Tool Call Handler (UPDATED)

**New function in** `generic_framework/core/persona.py`

```python
async def _handle_tool_calls(
    self,
    prompt: str,
    tool_calls: List[Dict],
    messages: List[Dict]
) -> str:
    """
    Handle GLM tool_calls by sending confirmation with results.

    Z.AI SDK Protocol:
    1. Append {"role": "tool", "content": result, "tool_call_id": id}
    2. Send back to GLM
    3. GLM executes and returns final answer

    For web_search: We might not execute it ourselves, just confirm.
    """
    import httpx
    import json

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Process each tool call
    for tool_call in tool_calls:
        tool_id = tool_call.get("id", "")
        tool_name = tool_call.get("function", {}).get("name", "")
        tool_args = tool_call.get("function", {}).get("arguments", "{}")

        self.logger.info(f"Processing tool: {tool_name} (id: {tool_id})")

        # Check if this is web_search (built-in) or custom function
        if tool_name == "web_search":
            # Web search is handled by GLM server-side
            # Just send confirmation without executing
            self.logger.info(f"Web search tool - sending confirmation only")
            messages.append({
                "role": "tool",
                "content": "",  # Empty content, GLM will execute
                "tool_call_id": tool_id,
                "name": tool_name
            })
        else:
            # Custom function - we would execute it here
            # For now, return error saying not implemented
            self.logger.error(f"Unknown tool: {tool_name}")
            return f"[Error: Tool '{tool_name}' not implemented]"

    # Build payload for second request
    model = os.getenv("LLM_MODEL", "glm-4.7")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }

    endpoint = f"{base_url.rstrip('/')}/chat/completions"

    self.logger.info(f"Sending tool confirmation to GLM (messages: {len(messages)})")

    # Increased timeout for tool execution
    timeout = httpx.Timeout(timeout=240.0, connect=60.0, pool=60.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        self.logger.info(f"Tool execution completed, parsing final response")

        # Extract final response
        if "choices" in data:
            final_msg = data["choices"][0]["message"]

            # Check for recursive tool calls (not supported)
            if "tool_calls" in final_msg and len(final_msg.get("tool_calls", [])) > 0:
                self.logger.warning(f"Recursive tool calls detected - not supported")
                return "[Error: Multi-round tool calls not supported]"

            content = final_msg.get("content", "")

            if not content:
                self.logger.error("Tool executed but returned empty content")
                return "[Error: Tool returned no data]"

            self.logger.info(f"Final response received: {len(content)} chars")
            return content

        self.logger.error(f"Unexpected response format: {list(data.keys())}")
        return "[Error: Unexpected tool response format]"

    except httpx.HTTPStatusError as e:
        self.logger.error(f"HTTP error during tool execution: {e}")
        return f"[Error: Tool execution failed - HTTP {e.response.status_code}]"

    except Exception as e:
        self.logger.error(f"Unexpected error during tool execution: {e}", exc_info=True)
        return f"[Error: Tool execution failed - {str(e)}]"
```

---

## Key Differences from Original Design

### Original Design (WRONG)
- ✅ Detect tool_calls
- ❌ **Wrong:** Send back `{"role": "assistant", "tool_calls": [...]}``

### Z.AI Protocol (CORRECT)
- ✅ Detect tool_calls
- ✅ **Correct:** Send back `{"role": "tool", "content": results, "tool_call_id": "id"}`

### Why This Matters

The `"role": "tool"` message type is **critical**. Using `"role": "assistant"` will not work - GLM won't recognize it as tool confirmation.

---

## Implementation Plan
```python
data = response.json()

# Parse response based on API format
if "code" in data and "success" in data:
    # ... Chinese API wrapper format
```

**New code:**
```python
data = response.json()

# Check for tool_calls (multi-turn required)
if "choices" in data:
    msg = data["choices"][0]["message"]

    # Tool calls detected - need multi-turn
    if "tool_calls" in msg and len(msg["tool_calls"]) > 0:
        self.logger.info(f"Tool calls detected - entering multi-turn conversation")
        return await self._handle_tool_calls(prompt, msg["tool_calls"], model, temperature)

    # No tool calls - extract content directly
    content = msg.get("content", "")
    if content:
        return content

# ... rest of response parsing
```

#### Change 2: Add new `_handle_tool_calls()` method

**Location:** Add as new method after `_call_llm()`

```python
async def _handle_tool_calls(
    self,
    prompt: str,
    tool_calls: List[Dict],
    model: str,
    temperature: float
) -> str:
    """
    Handle GLM tool_calls by sending confirmation.

    This implements the multi-turn conversation required for GLM tools:
    1. User sends query with tools
    2. GLM responds with tool_calls (permission request)
    3. System sends back tool_calls to confirm
    4. GLM executes tools and returns final answer
    """
    import httpx

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    self.logger.info(f"Building tool call confirmation message")
    self.logger.debug(f"Tool calls: {tool_calls}")

    # Build messages with tool_calls
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "tool_calls": tool_calls}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    # Use correct endpoint
    endpoint = f"{base_url.rstrip('/')}/chat/completions"

    self.logger.info(f"Sending tool call confirmation to GLM")

    # Increased timeout for tool execution
    timeout = httpx.Timeout(timeout=240.0, connect=60.0, pool=60.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        self.logger.info(f"Tool execution completed, parsing response")

        # Extract final response
        if "choices" in data:
            final_msg = data["choices"][0]["message"]

            # Check for recursive tool calls (not implemented)
            if "tool_calls" in final_msg:
                self.logger.warning(f"Multiple rounds of tool calls - not supported")
                return "[Error: Multi-round tool calls not supported yet]"

            content = final_msg.get("content", "")

            if not content:
                self.logger.error("Tool executed but returned empty content")
                return "[Error: Tool returned no data]"

            self.logger.info(f"Final response: {len(content)} chars")
            return content

        self.logger.error(f"Unexpected response format: {list(data.keys())}")
        return "[Error: Unexpected tool execution response]"

    except httpx.HTTPStatusError as e:
        self.logger.error(f"HTTP error during tool execution: {e}")
        return f"[Error: Tool execution failed - HTTP {e.response.status_code}]"

    except Exception as e:
        self.logger.error(f"Unexpected error during tool execution: {e}", exc_info=True)
        return f"[Error: Tool execution failed - {str(e)}]"
```

---

## Testing Strategy

### Test 1: Simple Tool Call (Weather)
**Query:** `// what's the weather in Nanaimo?`

**Expected flow:**
1. First API call with tools
2. GLM responds: `tool_calls: [{function: "web_search"}]`
3. Second API call with tool_calls confirmation
4. GLM returns actual weather data

**Expected result:** Real current temperature with citations

### Test 2: No Tool Call (Simple Query)
**Query:** `// hello`

**Expected flow:**
1. Single API call (no tools needed based on keyword detection)
2. GLM responds directly with greeting

**Expected result:** Fast response (< 10 seconds)

### Test 3: Timeout Handling
**Query:** `// latest stock prices`

**Expected flow:**
1. Tool call initiated
2. Search takes time but completes within 240s timeout
3. Final response with stock data

**Expected result:** Response with actual stock prices

---

## Configuration

### Environment Variables (No changes needed)
```bash
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
LLM_MODEL=glm-4.7
```

### Timeout Settings

**Current timeouts:**
```python
timeout = httpx.Timeout(
    timeout=240.0,      # Read timeout (4 minutes)
    connect=60.0,     # Connection timeout
    pool=60.0          # Pool acquisition timeout
)
```

**Rationale:**
- Tool calls take longer: 60-180 seconds
- Buffer for slow queries: 240 seconds
- Prevents premature timeout during web search

---

## Limitations

### Current Implementation
- ❌ No multi-turn tool call handling
- ❌ Truncated responses when GLM requests tools
- ❌ No actual web search data retrieved

### After Implementation
- ✅ Multi-turn conversation for tool calls
- ✅ Tool call confirmation sent to GLM
- ✅ Final answers with actual web data
- ⚠️ Single round only (no recursive tool calls)

### Future Enhancements
- Recursive tool calls (tools calling tools)
- Parallel tool execution
- Tool result streaming
- Tool call timeout and retry logic

---

## Alternative Approaches Considered

### Option A: MCP Web Search Server
**Pros:**
- Dedicated service, separate from LLM
- No tool call complexity in our code

**Cons:**
- Requires MCP client implementation
- Additional service dependency
- API quota limits

### Option B: Automatic Web Search (No Tools)
**Pros:**
- Simple single request/response
- No conversation loop needed

**Cons:**
- Not documented if GLM-4.7 has this
- May not work reliably
- Can't force web search when needed

### Option C: Hybrid Approach
**Pros:**
- Use automatic search for simple queries
- Fall back to tools for complex queries

**Cons:**
- Complex logic
- Unpredictable behavior
- Hard to debug

**Selected:** Multi-turn tool calls (Option B in "Implementation Plan")

---

## Rollback Plan

If implementation causes issues:

1. **Revert to current state:**
   ```bash
   git revert <commit-hash>
   docker compose restart
   ```

2. **Disable `//` prefix entirely:**
   - Remove tool detection code
   - Treat `//` as regular query prefix
   - Users rely on Extended Search button for web search

3. **Document known issue:**
   - Update TRIED.md with rollback steps
   - Add user-facing notice about `//` limitation

---

## Success Criteria

Implementation is successful when:

- [ ] `// hello` responds quickly (< 10 seconds)
- [ ] `// weather in Nanaimo` returns real current temperature
- [ ] Response contains actual data, not truncated
- [ ] No timeout errors under 240 seconds
- [ ] Logs show "Tool calls detected" and "Tool execution completed"
- [ ] Final response has citations or source references
- [ ] No multi-round tool calls (error message if attempted)

---

## References

- **Z.AI GLM-4.7 Documentation:** https://docs.z.ai
- **Z.AI Coding Endpoint:** https://api.z.ai/api/coding/paas/v4
- **OpenAI Function Calling:** https://platform.openai.com/docs/guides/function-calling
- **TRIED.md:** Complete history of attempted solutions

---

## Next Steps

1. **Implement Phase 1:** Tool call detection in `_call_llm()`
2. **Implement Phase 2:** Add `_handle_tool_calls()` method
3. **Test:** Run test cases from Testing Strategy
4. **Monitor:** Check logs for "Tool calls detected" messages
5. **Iterate:** Fix any issues found during testing
6. **Document:** Update TRIED.md with success/failure

---

**Last Updated:** 2026-02-10
**Status:** Ready for Implementation
