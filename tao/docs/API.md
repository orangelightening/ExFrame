# Tao API Documentation

Complete REST API reference for Tao (Knowledge Cartography) subsystem.

**Base URL:** `http://localhost:3000/api/tao`

---

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sessions/{domain}` | GET | Get exploration sessions |
| `/sessions/{domain}/summary` | GET | Get session statistics |
| `/chains/{domain}/{entry_id}` | GET | Get query chain (before/after) |
| `/related/{domain}/{entry_id}` | GET | Find related queries |
| `/concepts/{domain}` | GET | Get top concepts/keywords |
| `/concepts/{domain}/{concept}/cooccur` | GET | Get co-occurring concepts |
| `/depth/{domain}` | GET | Get deep explorations |
| `/history/{domain}` | GET | Get full query history |

---

## 1. Get Sessions

Get exploration sessions grouped by time gaps.

**Endpoint:** `GET /api/tao/sessions/{domain}`

**Parameters:**
- `gap_minutes` (int, optional) - Time gap to split sessions (default: 30)
- `min_queries` (int, optional) - Minimum queries per session (default: 1)

**Example:**
```bash
curl http://localhost:3000/api/tao/sessions/exframe?gap_minutes=30&min_queries=2
```

**Response:**
```json
[
  {
    "session_id": 1,
    "query_count": 3,
    "start_time": "2026-02-15 21:02:01",
    "end_time": "2026-02-15 21:11:10",
    "duration_minutes": 9.2,
    "sources": {
      "library": 3
    },
    "avg_confidence": 0.0,
    "queries": [
      "What is ExFrame and how do I get started?",
      "What is the next thing for exframe?",
      "2 + 2 ="
    ]
  }
]
```

---

## 2. Get Session Summary

Get aggregate statistics for all sessions.

**Endpoint:** `GET /api/tao/sessions/{domain}/summary`

**Parameters:**
- `gap_minutes` (int, optional) - Time gap to split sessions (default: 30)

**Example:**
```bash
curl http://localhost:3000/api/tao/sessions/exframe/summary
```

**Response:**
```json
{
  "session_count": 2,
  "total_queries": 4,
  "avg_queries_per_session": 2.0,
  "largest_session": 3,
  "smallest_session": 1,
  "avg_duration_minutes": 4.6,
  "longest_session_minutes": 9.2
}
```

---

## 3. Get Query Chain

Trace queries before and after a specific entry.

**Endpoint:** `GET /api/tao/chains/{domain}/{entry_id}`

**Parameters:**
- `before` (int, optional) - Number of queries before target (default: 3)
- `after` (int, optional) - Number of queries after target (default: 3)
- `gap_minutes` (int, optional) - Max time gap for continuity (default: 10)

**Example:**
```bash
curl http://localhost:3000/api/tao/chains/exframe/2?before=2&after=2
```

**Response:**
```json
{
  "target": {
    "id": 2,
    "timestamp": "2026-02-15T21:02:15.123456-08:00",
    "query": "What is the next thing for exframe?",
    "response": "The next milestone...",
    "metadata": {
      "source": "library",
      "confidence": 0.0
    }
  },
  "before": [
    {
      "id": 1,
      "query": "What is ExFrame...",
      "timestamp": "..."
    }
  ],
  "after": [
    {
      "id": 3,
      "query": "2 + 2 =",
      "timestamp": "..."
    }
  ],
  "summary": {
    "target_id": 2,
    "chain_length": 3,
    "before_count": 1,
    "after_count": 1,
    "duration_minutes": 9.0
  }
}
```

---

## 4. Find Related Queries

Find queries related to a specific entry using multiple strategies.

**Endpoint:** `GET /api/tao/related/{domain}/{entry_id}`

**Parameters:**
- `strategy` (string, optional) - Strategy to use: `temporal`, `pattern`, `keyword`, or `all` (default: `all`)
- `limit` (int, optional) - Max results per strategy (default: 5)
- `time_window` (int, optional) - Time window for temporal strategy in minutes (default: 60)
- `min_keywords` (int, optional) - Min shared keywords for keyword strategy (default: 2)

**Example:**
```bash
curl http://localhost:3000/api/tao/related/exframe/2?strategy=all&limit=5
```

**Response:**
```json
[
  {
    "entry_id": 1,
    "query": "What is ExFrame and how do I get started?",
    "score": 0.856,
    "reason": "Within 14.2 minutes",
    "strategy": "temporal"
  },
  {
    "entry_id": 3,
    "query": "2 + 2 =",
    "score": 0.234,
    "reason": "3 shared keywords: exframe, what, next",
    "strategy": "keyword"
  }
]
```

**Strategies:**
- **temporal**: Finds queries close in time
- **pattern**: Finds queries using same domain patterns
- **keyword**: Finds queries with common words
- **all**: Combines all strategies and removes duplicates

---

## 5. Get Top Concepts

Extract and rank top concepts (keywords) from query/response history.

**Endpoint:** `GET /api/tao/concepts/{domain}`

**Parameters:**
- `top_n` (int, optional) - Number of top concepts to return (default: 10)
- `min_freq` (int, optional) - Minimum frequency to include (default: 2)

**Example:**
```bash
curl http://localhost:3000/api/tao/concepts/exframe?top_n=5&min_freq=1
```

**Response:**
```json
[
  {
    "concept": "exframe",
    "frequency": 4,
    "first_seen": "2026-02-15T16:01:52.481318-08:00",
    "last_seen": "2026-02-15T21:11:10.989361-08:00",
    "entry_ids": [1, 2, 3, 4]
  },
  {
    "concept": "patterns",
    "frequency": 3,
    "first_seen": "2026-02-15T21:02:01.916808-08:00",
    "last_seen": "2026-02-15T21:11:10.989361-08:00",
    "entry_ids": [2, 3, 4]
  }
]
```

---

## 6. Get Concept Co-occurrence

Find concepts that frequently appear together with a target concept.

**Endpoint:** `GET /api/tao/concepts/{domain}/{concept}/cooccur`

**Parameters:**
- `min_cooccurrence` (int, optional) - Minimum times concepts must co-occur (default: 2)

**Example:**
```bash
curl http://localhost:3000/api/tao/concepts/exframe/patterns/cooccur
```

**Response:**
```json
[
  {
    "concept": "knowledge",
    "cooccurrence_count": 3
  },
  {
    "concept": "domain",
    "cooccurrence_count": 2
  }
]
```

---

## 7. Get Exploration Depth

Identify deep explorations (multiple related queries in sequence).

**Endpoint:** `GET /api/tao/depth/{domain}`

**Parameters:**
- `min_depth` (int, optional) - Minimum queries to count as deep (default: 2)
- `time_gap` (int, optional) - Max time gap between queries in minutes (default: 10)
- `concept` (string, optional) - Filter for specific concept (default: null)

**Example:**
```bash
curl http://localhost:3000/api/tao/depth/exframe?min_depth=2&time_gap=15
```

**Response:**
```json
[
  {
    "query_count": 3,
    "start_time": "2026-02-15T21:02:01.916808-08:00",
    "end_time": "2026-02-15T21:11:10.989361-08:00",
    "duration_minutes": 9.2,
    "unique_concepts": 623,
    "top_concepts": ["exframe", "patterns", "domain", "knowledge"],
    "sources": ["library"],
    "queries": [
      "What is ExFrame and how do I get started?",
      "What is the next thing for exframe?",
      "2 + 2 ="
    ],
    "focused_on": null
  }
]
```

---

## 8. Get Full History

Get complete query/response history for a domain.

**Endpoint:** `GET /api/tao/history/{domain}`

**Parameters:**
- `limit` (int, optional) - Limit number of entries (default: all)

**Example:**
```bash
curl http://localhost:3000/api/tao/history/exframe?limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "timestamp": "2026-02-15T16:01:52.481318-08:00",
    "query": "what is an array used in exframe",
    "response": "## Step-by-Step Reasoning...",
    "metadata": {
      "source": "library",
      "confidence": 0.0,
      "patterns_used": [],
      "persona": "kage"
    },
    "evoked_questions": []
  }
]
```

---

## Error Responses

All endpoints return standard HTTP status codes:

**Success:**
- `200 OK` - Request successful

**Client Errors:**
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Domain or entry not found

**Server Errors:**
- `500 Internal Server Error` - Server-side error

**Error Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. All endpoints are available for unlimited use.

---

## CORS

CORS is enabled for all origins in development mode. Adjust in production as needed.

---

## Authentication

Currently no authentication is required. All endpoints are publicly accessible within the network.

---

## Data Freshness

- Data is updated in real-time as queries are processed in ExFrame
- No caching is implemented - all requests fetch fresh data
- Query history is stored in compressed format (`query_history.json.gz`)

---

## Python Client Example

```python
import requests

# Get sessions
response = requests.get('http://localhost:3000/api/tao/sessions/exframe')
sessions = response.json()

for session in sessions:
    print(f"Session {session['session_id']}: {session['query_count']} queries")

# Get concepts
response = requests.get('http://localhost:3000/api/tao/concepts/exframe?top_n=5')
concepts = response.json()

for concept in concepts:
    print(f"{concept['concept']}: {concept['frequency']}x")

# Get query chain
response = requests.get('http://localhost:3000/api/tao/chains/exframe/2')
chain = response.json()
print(f"Chain: {chain['summary']['chain_length']} queries")
```

---

## JavaScript Client Example

```javascript
// Get sessions
const sessions = await fetch('/api/tao/sessions/exframe?gap_minutes=30')
  .then(r => r.json());

// Get related queries
const related = await fetch('/api/tao/related/exframe/2?strategy=all')
  .then(r => r.json());

// Get concepts
const concepts = await fetch('/api/tao/concepts/exframe?top_n=10')
  .then(r => r.json());
```

---

## WebSocket Support

Not currently implemented. All endpoints use REST/HTTP.

---

## Batch Operations

Not currently supported. Make individual requests for each operation.

---

## Version

API Version: `2.0.0` (Phase 2a)

Last Updated: February 2026
