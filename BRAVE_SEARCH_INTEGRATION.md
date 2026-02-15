# Brave Search API Integration

## Overview

ExFrame integrates with Brave Search API to provide AI-grounded web search capabilities. The Brave Answers API is OpenAI SDK compatible and provides fast, cited responses.

---

## Setup Instructions

### 1. Get a Brave Search API Account

**Sign up:** https://brave.com/search/api/

1. Create an account (free tier available)
2. Navigate to API section
3. Generate an API key
4. Copy the key (format: `BSA...`)

**Pricing:**
- **Free credits:** $5/month (~550 queries)
- **Paid:** $4 per 1,000 requests + $5 per million tokens
- **Average cost:** ~$0.004 per query

### 2. Add API Key to .env

Edit `/home/peter/development/eeframe/.env`:

```bash
# Brave Search API
BRAVE_API_KEY=BSAiZTKiIPhjMs9E68Soe_FwolsWwH2  # Your key here
BRAVE_SEARCH_MODE=single  # 'single' (fast) or 'research' (deep)
```

### 3. Restart Container

```bash
docker-compose down
docker-compose up -d
```

### 4. Test

Query in cooking domain:
```
recipe for apple pie. Include all source URLs.
```

Expected: Response in 15-25 seconds with recipe.

---

## API Details

**Endpoint:** `POST https://api.search.brave.com/res/v1/chat/completions`

**Authentication:**
- Header: `X-Subscription-Token: <API_KEY>`
- OR Header: `Authorization: Bearer <API_KEY>`

**Pricing:** $4 per 1,000 requests + $5 per million tokens

**Free Credits:** $5/month (~550 queries)

---

## Two Search Modes

### Single-Search (Default)
- **Speed:** ~2-3 seconds
- **Use:** Quick factual answers
- **Setting:** Default (no extra params)

**Example:**
```python
response = client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "What is quantum computing?"}],
    stream=False
)
```

### Research Mode
- **Speed:** ~5-10 seconds
- **Use:** Complex topics needing multi-source synthesis
- **Setting:** `extra_body={"enable_research": True}`

**Example:**
```python
response = client.chat.completions.create(
    model="brave",
    messages=[{"role": "user", "content": "Compare quantum computing approaches"}],
    extra_body={"enable_research": True},
    stream=False
)
```

---

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Brave Search API
BRAVE_API_KEY=your-brave-api-key-here
BRAVE_SEARCH_MODE=single  # or 'research'
```

### Domain Configuration

Enable web search in any domain's `domain.json`:

```json
{
  "domain_id": "research",
  "persona": "researcher",
  "enable_web_search": true,
  "brave_search_config": {
    "enabled": true,
    "mode": "single",
    "stream": false,
    "fallback_to_local": true
  }
}
```

---

## Usage in ExFrame

### Manual Search (Researcher Persona)

```bash
# In researcher domain
Query: "web search: How does CRISPR work?"
```

### Automatic Fallback

When patterns have low confidence, web search triggers automatically:

```python
if confidence < llm_min_confidence and enable_web_search:
    response = brave_search(query)
```

---

## Integration Code

### Basic Implementation

```python
from openai import OpenAI

def brave_search(query: str, mode: str = "single") -> dict:
    """
    Search using Brave Answers API.

    Args:
        query: Search query
        mode: 'single' for fast, 'research' for deep

    Returns:
        dict with answer, citations, sources
    """
    client = OpenAI(
        base_url="https://api.search.brave.com/res/v1",
        api_key=os.getenv("BRAVE_API_KEY"),
    )

    extra_body = {}
    if mode == "research":
        extra_body["enable_research"] = True

    response = client.chat.completions.create(
        model="brave",
        messages=[{"role": "user", "content": query}],
        stream=False,
        **({"extra_body": extra_body} if extra_body else {})
    )

    return {
        "answer": response.choices[0].message.content,
        "model": "brave-answers",
        "mode": mode
    }
```

### With Streaming

```python
def brave_search_stream(query: str):
    """Stream search results in real-time."""
    client = OpenAI(
        base_url="https://api.search.brave.com/res/v1",
        api_key=os.getenv("BRAVE_API_KEY"),
    )

    stream = client.chat.completions.create(
        model="brave",
        messages=[{"role": "user", "content": query}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

---

## Response Format

Brave returns standard OpenAI response format:

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "brave",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Answer with inline citations [1][2]..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200,
    "total_tokens": 250
  }
}
```

**Citations are inline:** Answer includes `[1]`, `[2]` references to sources.

---

## Performance Comparison

| Method | Speed | Cost | Quality |
|--------|-------|------|---------|
| **Brave Single** | ~3s | $0.009 | High (cited) |
| **Brave Research** | ~8s | $0.015 | Very High |
| **Local LLM** | ~8s | Free | Medium (no web data) |
| **Remote LLM only** | ~8s | $0.02 | Low (no web data) |

---

## Error Handling

```python
try:
    response = brave_search(query)
except Exception as e:
    logger.error(f"Brave search failed: {e}")
    # Fallback to local LLM
    response = local_llm_fallback(query)
```

**Common Errors:**
- `401`: Invalid API key
- `429`: Rate limit exceeded (2 queries/sec)
- `402`: Quota exceeded (check billing)
- `500`: Brave API error (retry with exponential backoff)

---

## Testing

### Test Brave API Key

```bash
curl -X POST "https://api.search.brave.com/res/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-Subscription-Token: ${BRAVE_API_KEY}" \
  -d '{
    "messages": [{"role": "user", "content": "Test query"}],
    "model": "brave",
    "stream": false
  }'
```

### Test in ExFrame

```python
# In researcher domain
Query: "web search: What is quantum computing?"

Expected response:
- Answer with citations [1][2][3]
- Response time: ~3s
- Source: brave-answers
```

---

## Best Practices

1. **Use Single-Search by default** - Faster and cheaper
2. **Enable Research mode** for complex queries only
3. **Cache common queries** - Save API costs
4. **Implement rate limiting** - Max 2 queries/sec
5. **Log token usage** - Track costs
6. **Fallback to local** - If Brave fails, use local LLM

---

## Monitoring

Track in logs:

```python
logger.info(f"Brave search: query={query}, mode={mode}, "
           f"tokens={usage.total_tokens}, time={elapsed_ms}ms")
```

**Key metrics:**
- Queries per day
- Average tokens per query
- Response time
- Error rate
- Monthly cost

---

## Upgrade Path

**Current (No Brave):**
- Web search: Unreliable or disabled
- Speed: N/A
- Cost: Free

**With Brave Single-Search:**
- Web search: Fast, cited, reliable
- Speed: ~3s
- Cost: $0.009/query (~$0.90/100 queries)

**With Brave Research:**
- Web search: Deep, multi-source, very reliable
- Speed: ~8s
- Cost: $0.015/query (~$1.50/100 queries)

---

## Implementation Status

### ✅ Completed (2026-02-14)
1. ✅ Brave Search API integration
2. ✅ Direct response (skips GLM synthesis)
3. ✅ LaTeX cleanup (removes $ symbols)
4. ✅ XML tool_call format handling
5. ✅ Both code paths (tool-calling + data source)
6. ✅ Live in production

### 🧪 Testing Phase
- **Status:** Actively testing query patterns
- **Goal:** Determine best prompts for URL citations
- **Cost:** ~$0.004/query (~1200 queries remaining)

---

## Current Performance (Actual)

**Single-Search Mode (Default):**
- **Speed:** 15-25 seconds
- **Tokens:** ~7,500-8,500 per query
- **Cost:** ~$0.042 per query
- **Quality:** High - AI-synthesized answers

**Comparison vs DuckDuckGo:**
- **Before:** 60-100+ seconds, frequent failures
- **After:** 15-25 seconds, stable
- **Improvement:** 5x faster, 100% reliable

---

## URL Citations - User Testing

**Current Understanding:**
- Brave AI decides whether to include URLs
- User can influence with prompt phrasing:
  - "Include all source URLs"
  - "with citations"
  - "List sources at the end"
- Results are **inconsistent** - requires experimentation

**Recommendation:** Users craft their own prompts and test what works.

---

## Technical Optimizations

### GLM Synthesis Removed
- **Before:** Brave (15s) + GLM synthesis (55s) = 70s
- **After:** Brave only (15-25s)
- **Savings:** 45-55 seconds per query

### LaTeX Cleanup
- Brave uses LaTeX formatting: `$40$` minutes, `$1\frac{1}{2}$` cups
- Automatically stripped via regex
- Clean output without `$` symbols

### Dual Code Path Support
1. **Tool-calling:** GLM → web_search tool → Brave
2. **Data source:** Researcher persona → data_source="internet" → Brave
3. Both paths skip GLM and return Brave results directly

---

**Last Updated:** 2026-02-14 (Production deployment)
