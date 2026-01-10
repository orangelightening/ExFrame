# Domain Co-Pilot Guide

**Purpose**: Complete documentation for the Domain Co-Pilot system - a generic AI-powered assistant framework for any domain expertise.

**Last Updated**: 2026-01-07
**Status**: Phase 0-2.5 Complete + Tracing + Passthrough Mode Operational (OMV domain example)

---

## Overview

Domain Co-Pilot is a generic AI-powered assistant framework for any domain expertise. It provides intelligent monitoring, contextual troubleshooting assistance, and proactive recommendations using GLM-4.7 as the LLM backend. The system has been validated with the OpenMediaVault (OMV) server management domain as an example implementation.

**Core Philosophy**: Provide immediate practical value through intelligent assistance, then iterate toward enhanced capabilities.

### Current Capabilities
- **Real-time Monitoring**: Domain-specific metrics, service status, system information
- **Troubleshooting Assistance**: Error analysis with explanations, diagnostic steps
- **Knowledge Base**: Curated patterns across multiple categories (24 patterns in OMV example)
- **Confidence Scoring**: AI responses rated by pattern matching quality
- **Execution Tracing**: Full visibility into AI decision pipeline
- **Passthrough Chat**: Direct LLM access bypassing knowledge base
- **CLI Interface**: System-wide command line tool

---

## Quick Start

### Prerequisites
- Python 3.11+ (tested on 3.13.7)
- Domain-specific data source (optional, e.g., OMV server with SSH access for OMV domain)
- GLM-4.7 API key (or compatible LLM provider)

### Installation
```bash
# Clone repository (if not already done)
cd /home/peter/development/eeframe

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Running the System (OMV Domain Example)
```bash
# Start API server for OMV domain (backend on port 8888)
./venv/bin/uvicorn omv_copilot.api.app:create_app --host 0.0.0.0 --port 8888 --reload

# Start frontend (on port 3000)
cd frontend && npm run dev

# Use CLI tool (OMV domain example)
omv-copilot query "My disk is full"
omv-copilot status
omv-copilot patterns
```

### Access URLs
- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8888/docs
- **API Endpoints**: http://localhost:8888/api/v1/*

---

## System Architecture

### Component Overview
```
┌─────────────────┐
│   USER LAYER    │
│  • Web UI (3000)│
│  • CLI Tool     │
└────────┬────────┘
         │
┌────────▼────────┐
│   API LAYER     │
│  • FastAPI (8888)│
│  • Routing      │
│  • Tracing      │
└────────┬────────┘
         │
┌────────▼────────┐
│   CORE LAYER    │
│  • Assistant    │
│  • Knowledge    │
│  • Data Collect │
└────────┬────────┘
         │
┌────────▼────────┐
│   DATA LAYER    │
│  • Domain Data  │
│  • GLM API      │
│  • Pattern Store│
└─────────────────┘
```

### Key Components

#### 1. Assistant Engine (`src/omv_copilot/assist/`)
- **Orchestration**: Coordinates data collection, pattern matching, LLM calls
- **Context Selection**: 6 specialist contexts (storage, network, service, performance, security, general)
- **Prompt Building**: Assembles context-aware prompts for LLM
- **Confidence Scoring**: Calculates response confidence based on pattern matches

#### 2. Data Collectors (`src/omv_copilot/collectors/` - OMV example)
- **Domain-specific Collectors**: Implement data collection for the target domain (e.g., SSH for OMV server)
- **Collection Scope**: Domain-specific metrics, status information, logs
- **Integration Methods**: SSH, API calls, file reading, or other domain-appropriate methods

#### 3. Knowledge Base (`src/omv_copilot/knowledge/` - OMV example)
- **Pattern Storage**: Domain-specific pattern storage (YAML, JSON, or database)
- **Pattern Matching**: Symptom-based scoring against domain state
- **Categories**: Domain-specific categories (e.g., Storage, Network, Services for OMV domain)

#### 4. LLM Integration (`src/omv_copilot/assist/llm_client.py`)
- **Provider**: GLM-4.7 via international endpoint
- **Configuration**: 120s timeout, verify=False for SSL issues
- **Response Handling**: Extracts `reasoning_content` from GLM-4.7 responses

#### 5. Execution Tracing (`src/omv_copilot/assist/trace.py`)
- **Decision Points**: 10 stages tracked with timing
- **Storage**: In-memory with JSON serialization
- **Visualization**: Mermaid diagrams in web UI

---

## Knowledge Base

### Pattern Structure
```yaml
- pattern_id: "omv-001"
  title: "SMB share inaccessible from Windows"
  category: "services"

  symptoms:
    - "Windows cannot access \\server\share"
    - "Network path not found error"
    - "Timeout when connecting"

  triggers:
    - "smb not working"
    - "can't access share"
    - "windows network error"

  diagnostics:
    - name: "Check SMB service status"
      command: "systemctl status smbd"
      expected_output: "active (running)"

    - name: "Verify share exists"
      command: "smbstatus -s"
      expected_output: "share listed"

  solutions:
    - priority: 1
      action: "Restart SMB service"
      command: "systemctl restart smbd"
      explanation: "Service may be hung"

    - priority: 2
      action: "Check firewall rules"
      command: "iptables -L -n | grep 445"
      explanation: "Port 445 may be blocked"

  confidence: 0.9
```

### Pattern Categories

#### Storage (6 patterns)
- Disk space issues
- RAID problems
- Filesystem errors
- ZFS administration
- Performance bottlenecks
- Backup failures

#### Network (5 patterns)
- Connectivity issues
- Firewall problems
- VPN configuration
- Interface errors
- DNS resolution

#### Services (4 patterns)
- SMB/NFS share problems
- Docker container issues
- Web server errors
- Authentication failures

#### Performance (3 patterns)
- High CPU usage
- Memory exhaustion
- Slow response times

#### Security (4 patterns)
- Permission errors
- Access control issues
- Vulnerability alerts
- Configuration hardening

### Adding New Patterns
1. Edit `patterns/manual.yaml`
2. Add pattern with proper structure (see above)
3. Save file - API server auto-reloads patterns
4. Test with query that triggers the pattern

**Pattern ID Format**: `omv-{number:03d}` (e.g., `omv-025`)

---

## Confidence Scoring System

### How It Works
1. **Base Confidence**: 0.5 (50%)
2. **Pattern Match Bonus**: Average of matched pattern scores added to base
3. **High-score Bonus**: +0.1 if top pattern score > 0.7
4. **Error Fallback**: 0.3 (30%) if errors occur
5. **Maximum Cap**: 0.98 (98%)

### Example Calculation
```
Base confidence: 0.5
Matched patterns: [0.8, 0.7, 0.6]
Average pattern score: (0.8 + 0.7 + 0.6) / 3 = 0.7
Pattern bonus: +0.7
High-score bonus: +0.1 (top pattern 0.8 > 0.7)
Total: 0.5 + 0.7 + 0.1 = 1.3 → Capped to 0.98
Final confidence: 98%
```

### Color Coding
- **Green** (≥80%): High confidence - likely accurate
- **Yellow** (60-79%): Medium confidence - reasonable but verify
- **Red** (<60%): Low confidence - use with caution

### Display
Confidence shown in AI Assistant response with:
- Percentage score
- Color-coded indicator
- Matched patterns and their scores
- Explanation of confidence factors

---

## Execution Tracing

### Purpose
Full visibility into the AI decision pipeline from query to response.

### Decision Points Traced (10 stages)
1. **`query_received`**: Query enters the system
2. **`context_selection`**: Which specialist context was chosen
3. **`system_context_collection`**: What data was gathered from domain data source
4. **`pattern_matching`**: Which patterns matched and their scores
5. **`confidence_calculation`**: How confidence was computed
6. **`llm_check`**: LLM availability check
7. **`prompt_building`**: Prompt assembly details
8. **`llm_generation`**: AI response generation (timing)
9. **`response_assembly`**: Final response composition
10. **`trace_complete`**: Trace finalized and stored

### API Endpoints
- `GET /api/v1/traces` - List all traces (paginated)
- `GET /api/v1/traces/{query_id}` - Get specific trace with full details
- `GET /api/v1/traces/{query_id}/mermaid` - Get Mermaid flowchart

### Trace Structure
```json
{
  "query_id": "uuid",
  "query": "original user query",
  "timestamp": "2026-01-07T10:30:00Z",
  "events": [
    {
      "stage": "query_received",
      "timestamp": "2026-01-07T10:30:00.100Z",
      "data": {"query": "My disk is full"},
      "duration_ms": 0
    },
    {
      "stage": "context_selection",
      "timestamp": "2026-01-07T10:30:00.150Z",
      "data": {"selected_context": "storage"},
      "duration_ms": 50
    }
    // ... more events
  ],
  "summary": {
    "total_duration_ms": 1250,
    "confidence": 0.88,
    "matched_patterns": ["omv-003", "omv-007"]
  }
}
```

### Mermaid Visualization
Traces can be visualized as Mermaid flowcharts showing the decision path:
```
graph TD
    A[query_received] --> B[context_selection]
    B --> C[system_context_collection]
    C --> D[pattern_matching]
    D --> E[confidence_calculation]
    E --> F[llm_check]
    F --> G[prompt_building]
    G --> H[llm_generation]
    H --> I[response_assembly]
    I --> J[trace_complete]
```

**Access**: http://localhost:3000/traces (5th page in web dashboard)

---

## Passthrough Chat Mode

### Purpose
Direct LLM access bypassing the knowledge base for general queries.

### Features
- **Toggle Switch**: In AI Assistant page UI
- **Bypassed Components**: Context selection, system context collection, pattern matching, confidence calculation
- **Direct Access**: Sends query directly to GLM with minimal overhead
- **Visual Indicator**: Shows "Direct Chat Mode" badge when active
- **Faster Response**: No system data collection or pattern matching delays

### Use Cases
1. **General Questions**: Not related to the specific domain expertise
2. **Testing**: Direct LLM functionality verification
3. **Speed**: Faster responses for simple queries
4. **Knowledge Gaps**: Questions outside knowledge base domain

### API Usage
Add `"passthrough": true` to query request body:
```json
{
  "query": "What is the capital of France?",
  "passthrough": true
}
```

### Limitations
- No system context (domain data not collected)
- No pattern matching or confidence scoring
- Generic responses without domain-specific expertise
- Still uses GLM-4.7 (same LLM, different prompt)

---

## Web Dashboard

### Pages Overview

#### 1. Dashboard (`/`)
- **System Overview**: Hostname, kernel, CPU, memory, network
- **Service Status**: SMB, NFS, SSH, nginx, PHP-FPM, cron
- **Storage Summary**: Disks, filesystems, usage percentages
- **Health Indicators**: Color-coded status indicators

#### 2. AI Assistant (`/assistant`)
- **Query Interface**: Text input for questions
- **Passthrough Toggle**: Switch between knowledge base and direct chat
- **Response Display**: Formatted responses with confidence indicators
- **Pattern Details**: Expandable matched pattern information

#### 3. Knowledge Base (`/knowledge`)
- **Pattern Browser**: All 24 patterns in expandable cards
- **Category Filter**: Filter by storage, network, services, etc.
- **Raw JSON View**: Toggle between formatted and raw JSON
- **Pattern Details**: Full pattern structure viewing

#### 4. Diagnostics (`/diagnostics`)
- **Health Checks**: Service status, filesystem health, storage
- **System Metrics**: Real-time metrics display
- **Configuration View**: Current domain configuration
- **Error Logs**: Recent error messages from journalctl

#### 5. Traces (`/traces`)
- **Trace History**: List of recent execution traces
- **Timeline View**: Decision point timeline with durations
- **Mermaid Diagrams**: Visual flowchart of execution path
- **Trace Details**: Expandable detailed view of each stage

### UI Features
- **Responsive Design**: Works on desktop and mobile
- **Dark Theme**: Tailwind CSS with custom styling
- **Real-time Updates**: Live metrics and status
- **Interactive Elements**: Expand/collapse, filtering, sorting
- **Progress Indicators**: Loading states for async operations

---

## CLI Tool

### Installation
```bash
# From project root (development)
cd /home/peter/development/eeframe
pip install -e .

# System-wide (production)
sudo ln -s /home/peter/development/eeframe/venv/bin/omv-copilot /usr/local/bin/
```

### Commands

#### `omv-copilot query "your question"`
Query the AI assistant from command line.
```bash
omv-copilot query "My disk is full"
omv-copilot query "SMB share not working" --passthrough
```

**Options**:
- `--passthrough` : Use direct chat mode (bypass knowledge base)
- `--verbose` : Show detailed trace information
- `--output json` : Output in JSON format

#### `omv-copilot status`
Show current system status.
```bash
omv-copilot status
```
Displays:
- Domain data source connection status
- Service/component status (up/down)
- Domain metrics summary (e.g., disk usage for OMV)
- System metrics overview

#### `omv-copilot patterns`
List knowledge base patterns.
```bash
omv-copilot patterns
omv-copilot patterns --category storage
omv-copilot patterns --search "smb"
```

**Options**:
- `--category` : Filter by category (storage, network, etc.)
- `--search` : Search pattern titles and symptoms
- `--format table|json` : Output format

#### `omv-copilot diagnose`
Run system diagnostics.
```bash
omv-copilot diagnose
omv-copilot diagnose --service smb
```

**Options**:
- `--service` : Check specific service
- `--disk` : Check specific disk
- `--full` : Run full diagnostic suite

### Output Formatting
- **Rich Library**: Colored output, tables, progress bars
- **JSON Support**: Machine-readable output with `--output json`
- **Table Views**: Formatted tables for status and patterns
- **Progress Indicators**: Spinners for long-running operations

---

## API Reference

### Base URL
```
http://localhost:8888/api/v1/
```

### Authentication
Currently none (development/local use). Future versions may add API keys.

### Endpoints

#### Assistance
- `POST /assist/query` - Get AI assistance for a query
- `POST /assist/diagnostics` - Get diagnostic suggestions
- `POST /assist/solution` - Get solution recommendations

#### System
- `GET /system/status` - Get system operational status
- `GET /system/metrics` - Get system metrics
- `GET /system/configuration` - Get domain configuration
- `GET /system/logs` - Get error logs (since=N seconds)

#### Knowledge
- `GET /knowledge/patterns` - List all patterns (full data)
- `GET /knowledge/patterns/{id}` - Get specific pattern
- `GET /knowledge/search` - Search patterns by query

#### Tracing
- `GET /traces` - List all execution traces
- `GET /traces/{query_id}` - Get specific trace
- `GET /traces/{query_id}/mermaid` - Get Mermaid flowchart

### Example Requests

#### Query Assistance
```bash
curl -X POST http://localhost:8888/api/v1/assist/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My disk is full",
    "passthrough": false
  }'
```

#### Get System Status
```bash
curl http://localhost:8888/api/v1/system/status
```

#### List Traces
```bash
curl http://localhost:8888/api/v1/traces
```

### Response Format
```json
{
  "query": "My disk is full",
  "response": {
    "analysis": "Disk full analysis...",
    "suggested_diagnostics": ["Check disk usage", "Identify large files"],
    "possible_causes": ["Log files", "Temporary files", "Backups"],
    "recommended_actions": ["Clean /var/log", "Remove old backups"],
    "explanation": "Detailed explanation...",
    "follow_up_questions": ["Which disk is full?", "What type of files?"]
  },
  "confidence": 0.88,
  "matched_patterns": [
    {"id": "omv-003", "score": 0.9, "title": "Disk space exhaustion"}
  ],
  "trace_id": "uuid",
  "timestamp": "2026-01-07T10:30:00Z"
}
```

---

## Configuration

### Environment Variables (`.env`)
```bash
# Domain-specific Settings (OMV example shown)
# Replace with your domain's data source configuration
DOMAIN_DATA_SOURCE_TYPE=ssh  # ssh, api, file, etc.
DOMAIN_HOSTNAME=your-domain-server.example.com
DOMAIN_PORT=22
DOMAIN_USERNAME=username
DOMAIN_PASSWORD=your-password
DOMAIN_USE_SSH=true

# LLM Integration
LLM_PROVIDER=GLM
LLM_MODEL=glm-4.7
LLM_API_KEY=your-api-key-here
LLM_API_ENDPOINT=https://api.z.ai/api/coding/paas/v4/chat/completions
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=120

# Knowledge Base
KNOWLEDGE_STORAGE_PATH=data/knowledge
KNOWLEDGE_MANUAL_PATTERNS_PATH=patterns/manual.yaml
KNOWLEDGE_USER_HISTORY_PATH=data/history

# Application Settings
ENVIRONMENT=development
DEBUG=true
API_PORT=8888
FRONTEND_PORT=3000
```

### Critical Configuration Notes

#### GLM API Endpoint
**IMPORTANT**: Use the international platform endpoint:
```
https://api.z.ai/api/coding/paas/v4/chat/completions
```

**NOT** `open.bigmodel.com` (Chinese platform).

#### SSL Certificate Issue
GLM API requires `verify=False` in httpx.AsyncClient due to certificate verification failures.

#### Domain Data Collection Methods
Different domains may require different data collection methods. For the OMV example domain, SSH-based collection is used because OMV 7.x restricts RPC API to localhost. Other domains might use API calls, file reading, or other collection methods.

#### Port Configuration
- **API Server**: 8888 (8000 was already in use)
- **Frontend**: 3000
- **Development**: Auto-reload enabled in development

---

## Development

### Project Structure
```
eeframe/
├── src/omv_copilot/
│   ├── api/
│   │   └── app.py                 # FastAPI application (port 8888)
│   ├── assist/
│   │   ├── llm_client.py          # GLM integration with timeout
│   │   ├── assistant_engine.py    # Main orchestration with tracing
│   │   ├── specialist_prompts.py  # 6 specialist contexts
│   │   └── trace.py               # Execution tracing system
│   ├── collectors/
│   │   ├── ssh_collector.py       # SSH-based data collection
│   │   └── domain_collector.py    # Domain-specific collectors (omv_collector.py for OMV example)
│   ├── knowledge/
│   │   ├── knowledge_base.py      # Pattern storage & matching
│   │   └── patterns.py            # Pattern dataclass
│   └── settings.py                # Pydantic settings
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/                  # 5 main pages
│   │   ├── services/
│   │   └── App.jsx
│   └── vite.config.js             # Proxy to :8888
├── cli/
│   └── main.py                    # Click-based CLI tool
├── patterns/
│   └── manual.yaml                # Domain-specific patterns (24 curated patterns in OMV example)
└── data/                          # Runtime data
    ├── knowledge/
    ├── history/
    └── traces/                    # Trace storage
```

### Adding New Features

#### 1. New Specialist Context
1. Add context definition in `specialist_prompts.py`
2. Add trigger keywords for context selection
3. Create prompt template for the context
4. Test with queries that should trigger the context

#### 2. New Data Collector
1. Create collector class in `collectors/` directory
2. Implement async data collection methods
3. Add to assistant engine data collection pipeline
4. Test collection and integration

#### 3. Enhanced Tracing
1. Add new trace event type in `trace.py`
2. Instrument relevant code section
3. Add to Mermaid diagram generation
4. Update trace visualization UI

### Testing
```bash
# Test backend
curl -s http://localhost:8888/api/v1/knowledge/patterns | jq '.patterns | length'

# Test frontend
npm run dev  # Then visit http://localhost:3000

# Test CLI
omv-copilot patterns

# View traces after a query
curl -s http://localhost:8888/api/v1/traces | jq '.traces | length'
```

### Common Development Tasks

#### Adding a New Pattern
```bash
# Edit pattern file
vim patterns/manual.yaml

# Test pattern matching
curl -X POST http://localhost:8888/api/v1/assist/query \
  -H "Content-Type: application/json" \
  -d '{"query": "pattern trigger words"}'
```

#### Debugging Tracing
```bash
# Get recent traces
curl http://localhost:8888/api/v1/traces

# Get specific trace details
curl http://localhost:8888/api/v1/traces/{query_id}

# View Mermaid diagram
curl http://localhost:8888/api/v1/traces/{query_id}/mermaid
```

#### Testing Passthrough Mode
```bash
# Via API
curl -X POST http://localhost:8888/api/v1/assist/query \
  -H "Content-Type: application/json" \
  -d '{"query": "general question", "passthrough": true}'

# Via CLI
omv-copilot query "general question" --passthrough
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Domain Data Source Connection Failed
**Symptoms**: Connection error, no domain data collected
**Solutions**:
1. Verify domain data source is reachable (e.g., `ping server.example.com` for OMV)
2. Check connection credentials in `.env` file
3. Test connection manually (e.g., `ssh username@server` for SSH-based domains)
4. Verify data source allows the required access method

#### Issue 2: GLM API Returns Empty Response
**Symptoms**: Empty or truncated responses from AI
**Solutions**:
1. Check GLM API key is valid and has quota
2. Verify endpoint URL is correct (international platform)
3. Check network connectivity to api.z.ai
4. Increase timeout in configuration (default 120s)

#### Issue 3: Pattern Matching Not Working
**Symptoms**: Low confidence scores, no patterns matched
**Solutions**:
1. Verify pattern YAML syntax is correct
2. Check trigger words match query keywords
3. Test pattern loading: `curl http://localhost:8888/api/v1/knowledge/patterns`
4. Check pattern file is in correct location

#### Issue 4: Web Dashboard Not Loading
**Symptoms**: White screen or connection errors
**Solutions**:
1. Verify frontend is running: `cd frontend && npm run dev`
2. Check browser console for errors
3. Verify API server is running on port 8888
4. Check vite.config.js proxy configuration

#### Issue 5: CLI Tool Not Found
**Symptoms**: "command not found: omv-copilot"
**Solutions**:
1. Install CLI tool: `pip install -e .` from project root
2. Create symlink manually: `sudo ln -s /path/to/venv/bin/omv-copilot /usr/local/bin/`
3. Use full path: `/home/peter/development/eeframe/venv/bin/omv-copilot`

### Debug Mode
Enable debug logging by setting in `.env`:
```bash
DEBUG=true
ENVIRONMENT=development
```

Check application logs for detailed error information.

---

## Performance Considerations

### Response Time Breakdown
- **Data Collection**: 2-5 seconds (depends on domain data source, e.g., SSH for OMV)
- **Pattern Matching**: <100ms (in-memory matching)
- **LLM API Call**: 3-10 seconds (network + processing)
- **Total Typical**: 5-15 seconds per query

### Optimization Tips
1. **Passthrough Mode**: Use for general questions (bypasses data collection)
2. **Caching**: Consider adding response caching for common queries
3. **Parallel Collection**: Collect system data in parallel where possible
4. **Pattern Indexing**: Current pattern set small, but consider indexing for larger sets

### Resource Usage
- **Memory**: ~200-300MB (Python + React development servers)
- **CPU**: Minimal for API, moderate for LLM processing
- **Storage**: <10MB for patterns and trace data
- **Network**: Connection to domain data source (e.g., SSH to OMV server), HTTPS to GLM API

---

## Future Development

### Planned Enhancements

#### Short Term (Next 1-2 Months)
1. **More Patterns**: Expand to 50+ curated domain patterns
2. **Improved Matching**: Semantic search instead of keyword matching
3. **Pattern Editing**: Web UI for editing patterns
4. **User Feedback**: Capture and learn from user feedback

#### Medium Term (3-6 Months)
1. **Monitoring Stack**: Prometheus + Grafana + Loki integration
2. **Smart Alerting**: Context-aware alerting with predictions
3. **Multi-step Workflows**: Guided diagnostic workflows
4. **Solution Verification**: Test suggested solutions automatically

#### Long Term (6+ Months)
1. **Production Deployment**: Docker Compose, authentication, scaling
2. **Multi-tenant**: Support multiple domain instances
3. **Community Patterns**: Shared pattern repository
4. **Advanced AI**: Fine-tuned models for specific domains

### Contributing
While currently a single-developer project, the architecture supports:
- **Modular Design**: Easy to add new components
- **Clear Interfaces**: Well-defined APIs between components
- **Documentation**: Comprehensive guides and references
- **Testing**: Validation scripts and test patterns

---

## Conclusion

Domain Co-Pilot provides practical AI assistance for any domain expertise, as demonstrated with the OpenMediaVault server management example:
- **Curated knowledge patterns** across domain-specific categories (24 patterns in OMV example)
- **Confidence scoring** based on pattern matching quality
- **Execution tracing** for full decision pipeline visibility
- **Passthrough chat mode** for general questions
- **Web dashboard, CLI tool, and API** for multiple access methods

The system is **operational and validated**, ready for use and further enhancement based on real-world usage patterns.