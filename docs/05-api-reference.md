# EEFrame API Reference

**Purpose**: Comprehensive API documentation for all EEFrame subsystems: OMV Co-Pilot, Generic Framework, Expertise Scanner, and Three-Way Chat.

**Last Updated**: 2026-01-07
**Status**: All APIs operational with OpenAPI documentation available

---

## Overview

EEFrame consists of multiple API subsystems serving different purposes:

1. **OMV Co-Pilot API**: Intelligent OpenMediaVault Server Management Assistant
2. **Generic Framework API**: Domain-agnostic expertise assistant (cooking domain example)
3. **Expertise Scanner API**: Pattern extraction and knowledge graph system
4. **Three-Way Chat API**: Real-time chat between human director and AI commentators

All APIs are built with FastAPI and automatically generate OpenAPI/Swagger documentation at `/docs` endpoints.

---

## OMV Co-Pilot API

**Base URL**: `http://localhost:8000`
**Version**: 2.0.0
**OpenAPI Docs**: `http://localhost:8000/docs`

### System Endpoints

#### `GET /`
**Description**: Root endpoint with API information
**Response**: API version and status information

#### `GET /api/v1/system/status`
**Description**: Get system status and component connectivity
**Response**: `SystemStatusResponse`
```json
{
  "status": "operational",
  "omv_connected": true,
  "prometheus_connected": true,
  "loki_connected": true,
  "llm_configured": true,
  "knowledge_base_loaded": true
}
```

#### `GET /api/v1/system/metrics`
**Description**: Get current system metrics (requires Prometheus)
**Query Parameters**:
- `time_range` (optional): Time range for metrics (default: "5m")

#### `GET /api/v1/system/logs`
**Description**: Get recent system logs (requires Loki)
**Query Parameters**:
- `limit` (optional): Number of log entries (default: 100)
- `time_range` (optional): Time range for logs (default: "1h")

#### `GET /api/v1/system/configuration`
**Description**: Get current system configuration snapshot

### Assistance Endpoints

#### `POST /api/v1/assist/query`
**Description**: Get AI assistance for a query
**Request Body**: `QueryRequest`
```json
{
  "query": "SMB share is very slow when copying large files",
  "user_id": "optional-user-id",
  "include_logs": true,
  "passthrough": false
}
```

**Response**: AI-generated assistance with confidence scores and matched patterns

#### `POST /api/v1/assist/diagnostics`
**Description**: Get diagnostic assistance for an issue
**Request Body**: `DiagnosticsRequest`
```json
{
  "issue_description": "Disk usage is high on /srv"
}
```

#### `POST /api/v1/assist/solution`
**Description**: Get solution assistance for an issue
**Request Body**: `SolutionRequest`
```json
{
  "issue_description": "SMB service won't start",
  "attempted_solutions": ["restarted service", "checked logs"]
}
```

### Knowledge Endpoints

#### `POST /api/v1/knowledge/feedback`
**Description**: Record user feedback for learning
**Request Body**: `FeedbackRequest`
```json
{
  "query": "Original user query",
  "response": "AI response provided",
  "rating": 4,
  "suggestions_followed": true,
  "resolved": true,
  "comments": "Helpful but could be more specific"
}
```

#### `GET /api/v1/knowledge/patterns`
**Description**: List available knowledge patterns
**Query Parameters**:
- `category` (optional): Filter by category (storage, network, service, performance, security)
- `limit` (optional): Maximum number of patterns to return

#### `GET /api/v1/knowledge/patterns/{pattern_id}`
**Description**: Get a specific pattern by ID

#### `GET /api/v1/knowledge/search`
**Description**: Search knowledge patterns
**Query Parameters**:
- `q`: Search query
- `category` (optional): Filter by category
- `limit` (optional): Maximum results

### Tracing Endpoints

#### `GET /api/v1/traces`
**Description**: List all execution traces
**Query Parameters**:
- `limit` (optional): Maximum traces (default: 50)
- `offset` (optional): Pagination offset

#### `GET /api/v1/traces/{query_id}`
**Description**: Get a specific execution trace by query ID

#### `GET /api/v1/traces/{query_id}/mermaid`
**Description**: Get a Mermaid flowchart visualization for a trace

### Data Models

#### QueryRequest
```python
query: str
user_id: Optional[str] = None
include_logs: bool = False
passthrough: bool = False
```

#### SystemStatusResponse
```python
status: str
omv_connected: bool
prometheus_connected: bool
loki_connected: bool
llm_configured: bool
knowledge_base_loaded: bool
```

#### FeedbackRequest
```python
query: str
response: str
rating: int  # 1-5 scale
suggestions_followed: bool
resolved: bool
comments: Optional[str] = None
```

---

## Generic Framework API

**Base URL**: `http://localhost:3000`
**Version**: 1.0.0
**OpenAPI Docs**: `http://localhost:3000/docs`

### Domain Management

#### `GET /api/domains`
**Description**: List available domains
**Response**: List of `DomainInfo` objects

#### `GET /api/domains/{domain_id}`
**Description**: Get information about a specific domain
**Response**: `DomainInfo`

#### `GET /api/domains/{domain_id}/specialists`
**Description**: List specialists in a domain
**Response**: List of specialist names and descriptions

#### `GET /api/domains/{domain_id}/patterns`
**Description**: List patterns in a domain
**Query Parameters**:
- `category` (optional): Filter by category

#### `GET /api/domains/{domain_id}/health`
**Description**: Get health status of a domain

### Query Processing

#### `POST /api/query`
**Description**: Process a user query
**Request Body**: `QueryRequest`
```json
{
  "query": "How do I make fluffy pancakes?",
  "domain": "cooking",
  "context": "Beginner cook with basic kitchen tools",
  "include_trace": true
}
```

**Response**: `QueryResponse`
```json
{
  "query": "Original query",
  "response": "AI-generated response",
  "specialist": "baking_specialist",
  "patterns_used": ["cooking_001", "cooking_003"],
  "confidence": 0.85,
  "timestamp": "2026-01-07T10:30:00Z",
  "domain": "cooking",
  "processing_time_ms": 1245,
  "trace": { ... }  # if include_trace was true
}
```

### History & Tracing

#### `GET /api/history`
**Description**: Get query history
**Query Parameters**:
- `domain` (optional): Filter by domain
- `limit` (optional): Maximum entries (default: 100)

#### `GET /api/traces`
**Description**: Get recent query traces from memory
**Query Parameters**:
- `domain` (optional): Filter by domain
- `limit` (optional): Maximum traces

#### `GET /api/traces/log`
**Description**: Get recent query traces from log file (historical)
**Query Parameters**:
- `limit` (optional): Maximum traces

#### `GET /api/traces/{query_id}`
**Description**: Get detailed trace for a specific query

### Data Models

#### DomainInfo
```python
domain_id: str
domain_name: str
patterns_loaded: int
specialists: List[str]
categories: List[str]
```

#### QueryRequest (Generic Framework)
```python
query: str
domain: str
context: Optional[str] = None
include_trace: bool = False
```

#### QueryResponse
```python
query: str
response: str
specialist: str
patterns_used: List[str]
confidence: float
timestamp: datetime
domain: str
processing_time_ms: int
trace: Optional[Dict] = None
```

---

## Expertise Scanner API

**Base URL**: `http://localhost:8889`
**Version**: 0.1.0
**OpenAPI Docs**: `http://localhost:8889/docs`

### Pattern Management (`/api/patterns/*`)

#### `GET /api/patterns`
**Description**: Get patterns with optional filtering
**Query Parameters**:
- `domain` (optional): Filter by domain (cooking, python, diy, first_aid, gardening)
- `pattern_type` (optional): Filter by type (troubleshooting, recipe, tutorial)
- `limit` (optional): Maximum patterns (default: 100)
- `offset` (optional): Pagination offset

#### `GET /api/patterns/{pattern_id}`
**Description**: Get a specific pattern by ID
**Path Parameter**: `pattern_id` (e.g., `cooking_001`)

#### `GET /api/patterns/domains/list`
**Description**: Get list of all configured domains

#### `POST /api/patterns`
**Description**: Create a new pattern
**Request Body**: `PatternCreate`
```json
{
  "domain": "cooking",
  "name": "Fluffy Pancakes",
  "pattern_type": "recipe",
  "description": "How to make light and fluffy pancakes",
  "problem": "Pancakes are dense and heavy",
  "solution": "Use buttermilk and don't overmix batter",
  "steps": ["Mix dry ingredients", "Combine wet ingredients", "Fold gently", "Cook on medium heat"],
  "conditions": ["Have basic kitchen tools", "Access to stove"],
  "related_patterns": ["cooking_002", "cooking_005"],
  "prerequisites": ["basic_cooking_skills"],
  "alternatives": ["cooking_010"],
  "confidence": 0.9,
  "sources": ["family recipe", "tested 5 times"],
  "tags": ["breakfast", "quick", "beginner"],
  "examples": ["Sunday brunch", "Kids breakfast"]
}
```

#### `PUT /api/patterns/{pattern_id}`
**Description**: Update an existing pattern

#### `DELETE /api/patterns/{pattern_id}`
**Description**: Delete a pattern

### Ingestion Endpoints (`/api/ingest/*`)

#### `POST /api/ingest/url`
**Description**: Ingest content from a URL and extract patterns
**Request Body**: `IngestURLRequest`
```json
{
  "url": "https://www.allrecipes.com/recipe/12345",
  "domain": "cooking",
  "extract_patterns": true
}
```

**Response**: `JobResponse` with job ID for tracking

#### `POST /api/ingest/text`
**Description**: Ingest raw text and extract patterns
**Request Body**: `IngestTextRequest`
```json
{
  "text": "Full recipe text here...",
  "domain": "cooking",
  "source": "cookbook_page_45"
}
```

#### `GET /api/ingest/jobs/{job_id}`
**Description**: Check status of an ingestion job
**Response**: `JobStatus` with progress and results

#### `GET /api/ingest/jobs`
**Description**: List all ingestion jobs

#### `POST /api/ingest/batch/allrecipes`
**Description**: Batch ingest recipes from AllRecipes
**Request Body**: `BatchIngestRequest`
```json
{
  "category_url": "https://www.allrecipes.com/recipes/76/breakfast-and-brunch/",
  "seed_urls": ["https://www.allrecipes.com/recipe/12345"],
  "max_recipes": 50,
  "max_depth": 3,
  "domain": "cooking"
}
```

#### `POST /api/ingest/discover/allrecipes`
**Description**: Discover recipe URLs from an AllRecipes category

#### `POST /api/ingest/inbox/process`
**Description**: Process AI-generated recipe files from inbox
**Note**: Processes JSON files in `/home/peter/development/eeframe/pattern-inbox/`

#### `GET /api/ingest/inbox/status`
**Description**: Check status of pattern inbox

### Knowledge Graph Endpoints (`/api/knowledge/*`)

#### `GET /api/knowledge/graph/{domain}`
**Description**: Get knowledge graph for a specific domain

#### `GET /api/knowledge/graph`
**Description**: Get complete knowledge graph across all domains

#### `POST /api/knowledge/graph/{domain}/rebuild`
**Description**: Rebuild knowledge graph for a domain

#### `GET /api/knowledge/related/{pattern_id}`
**Description**: Get patterns related to given pattern

#### `GET /api/knowledge/path/{from_id}/{to_id}`
**Description**: Find path through knowledge graph between two patterns

### Cross-Domain Analysis (`/api/cross-domain/*`)

#### `GET /api/cross-domain/universal-patterns`
**Description**: Get patterns that appear across multiple domains

#### `GET /api/cross-domain/similar/{pattern_id}`
**Description**: Find similar patterns across all domains

#### `GET /api/cross-domain/compare/{domain1}/{domain2}`
**Description**: Compare two domains to find related patterns

#### `GET /api/cross-domain/clusters`
**Description**: Get clusters of similar patterns across all domains

### Data Models (Expertise Scanner)

#### PatternCreate
Comprehensive pattern creation model with 15+ fields including domain, name, type, description, problem, solution, steps, conditions, relationships, confidence, sources, tags, and examples.

#### IngestURLRequest
```python
url: str
domain: str
extract_patterns: bool = True
```

#### IngestTextRequest
```python
text: str
domain: str
source: Optional[str] = None
```

#### JobResponse
```python
job_id: str
status: str  # "pending", "processing", "completed", "failed"
message: Optional[str] = None
```

#### JobStatus
```python
job_id: str
status: str
progress: float  # 0.0 to 1.0
patterns_extracted: int
errors: List[str]
```

---

## Three-Way Chat API

**Base URL**: `http://localhost:8888`
**Version**: 1.0.0
**OpenAPI Docs**: `http://localhost:8888/docs`

### Chat Endpoints

#### `POST /api/chat/messages`
**Description**: Send a new message
**Request Body**: `Message`
```json
{
  "sender": "human_director",
  "content": "Let's design a new feature for the system",
  "type": "directive",
  "mentions": ["ai_commentator", "ai_builder"],
  "files": ["design_sketch.png"]
}
```

#### `GET /api/chat/messages`
**Description**: Get all messages or messages since timestamp
**Query Parameters**:
- `since` (optional): Timestamp to get messages after

#### `WS /api/chat/stream`
**Description**: WebSocket endpoint for real-time updates

#### `GET /api/chat/health`
**Description**: Health check endpoint

### Data Models

#### Message
```python
sender: str  # "human_director", "ai_commentator", "ai_builder"
content: str
type: str  # "directive", "commentary", "build_update", "question"
mentions: List[str] = []
files: List[str] = []
```

#### MessageResponse
```python
id: str
timestamp: datetime
sender: str
content: str
type: str
mentions: List[str]
files: List[str]
```

---

## Common Configuration

### Environment Variables

All APIs share common configuration patterns:

```bash
# OMV Server (OMV Co-Pilot only)
OMV_HOSTNAME=your-omv-server.local
OMV_USERNAME=admin
OMV_PASSWORD=your-password

# LLM Configuration (all systems)
LLM_PROVIDER=GLM  # or OpenAI, Anthropic
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.z.ai/v1  # GLM international endpoint
LLM_MODEL=GLM-4.7

# API Configuration
API_HOST=0.0.0.0  # or 127.0.0.1 for local only
API_PORT=8000  # or 3000, 8888, 8889 depending on system

# Monitoring (OMV Co-Pilot)
MONITORING_PROMETHEUS_URL=http://localhost:9090
MONITORING_LOKI_URL=http://localhost:3100
```

### CORS Configuration

All APIs are configured with CORS for local development:

```python
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]
```

### Error Responses

All APIs return consistent error responses:

```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-07T10:30:00Z"
}
```

Common error codes:
- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `SERVICE_UNAVAILABLE`: External service unavailable
- `INTERNAL_ERROR`: Internal server error

---

## Authentication & Security

### Current Status
- **Development**: No authentication (localhost only)
- **Production Consideration**: API keys or JWT tokens

### Rate Limiting
- Not currently implemented
- Consideration: FastAPI Limiter for production

### Data Validation
- All APIs use Pydantic models for request/response validation
- Type hints and field validation enforced
- Custom validators for domain-specific rules

---

## Testing the APIs

### Using OpenAPI/Swagger UI
1. Start the desired API service
2. Navigate to `http://localhost:{PORT}/docs`
3. Interactive testing interface available

### Using cURL Examples

**OMV Co-Pilot Query**:
```bash
curl -X POST http://localhost:8000/api/v1/assist/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SMB share slow", "include_logs": true}'
```

**Generic Framework Query**:
```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How to make pancakes", "domain": "cooking"}'
```

**Expertise Scanner Pattern Search**:
```bash
curl "http://localhost:8889/api/patterns?domain=cooking&limit=10"
```

### Using Python Client

```python
import requests

# OMV Co-Pilot example
response = requests.post(
    "http://localhost:8000/api/v1/assist/query",
    json={"query": "System issue", "include_logs": True}
)
print(response.json())
```

---

## API Health Monitoring

### Health Check Endpoints
- All APIs: `GET /` (root endpoint with status)
- OMV Co-Pilot: `GET /api/v1/system/status` (component health)
- Generic Framework: `GET /api/domains/{domain}/health`
- Expertise Scanner: Built into root endpoint
- Three-Way Chat: `GET /api/chat/health`

### Monitoring Integration
- **OMV Co-Pilot**: Integrates with Prometheus for metrics
- **All APIs**: Log to stdout for centralized logging
- **Future**: OpenTelemetry integration for distributed tracing

---

## Versioning Strategy

### Current Versioning
- **OMV Co-Pilot**: `v1` in URL (`/api/v1/`)
- **Generic Framework**: No version in URL (implicit v1)
- **Expertise Scanner**: No version in URL (implicit v0.1)
- **Three-Way Chat**: No version in URL (implicit v1)

### Future Versioning Plan
- URL path versioning: `/api/v2/`
- Header-based versioning for backward compatibility
- Deprecation warnings in responses

---

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 8000, 3000, 8888, 8889 are available
2. **CORS Errors**: Check frontend is accessing correct API URL
3. **LLM API Issues**: Verify API key and internet connectivity
4. **File Permissions**: Ensure write access to pattern data directories

### Debug Endpoints
- **All APIs**: `GET /docs` for interactive testing
- **OMV Co-Pilot**: `GET /api/v1/traces` for execution debugging
- **Expertise Scanner**: `GET /api/ingest/jobs` for ingestion status

### Logs Location
- Console stdout (development)
- No persistent log files by default
- Consider Docker logging for containerized deployment

---

## Migration & Backward Compatibility

### Breaking Changes
Currently in development phase - breaking changes expected.

### Data Migration
- Pattern data: JSON file format changes may require migration scripts
- Trace data: In-memory only, no persistence needed
- Knowledge graph: JSON-based, manual migration if structure changes

### Client Compatibility
- Update client code when API endpoints change
- Use OpenAPI specs for client generation
- Consider API versioning for production use