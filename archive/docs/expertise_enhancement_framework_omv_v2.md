# OMV Co-Pilot: Intelligent Server Management Assistant
## Domain: OpenMediaVault Server Operations & Troubleshooting

**Version**: 2.3.0
**Last Updated**: 2026-01-04
**Status**: Phase 0-2 Complete + Tracing + Passthrough Mode

---

## Executive Summary

OMV Co-Pilot is a focused, practical AI-powered assistant for OpenMediaVault server management. Rather than attempting full cognitive augmentation, this system provides intelligent monitoring, contextual troubleshooting assistance, and proactive maintenance recommendations.

**Core Philosophy**: Provide immediate practical value through intelligent assistance, then iterate toward enhanced capabilities.

**Current Status**:
- Fully functional web dashboard with 5 pages
- 24 knowledge patterns across 5 categories
- Execution tracing system with full decision pipeline visibility
- Passthrough chat mode for direct LLM access
- CLI tool with Rich formatting
- GLM-4.7 integration with confidence scoring

---

## 1. System Architecture

### 1.1 Simplified Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                       │
│  • Web Dashboard (React + Vite)                              │
│  • CLI Tool (Python Click + Rich)                            │
│  • 5 Pages: Dashboard, Assistant, Knowledge, Diagnostics, Traces│
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│                 ASSISTANCE ENGINE                             │
│  • Context-aware suggestions                                 │
│  • Prompt-based specialist routing                           │
│  • User feedback integration                                 │
│  • Execution tracing (9 decision points)                    │
│  • Passthrough chat mode                                     │
└─────────────────────┬────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────────┐
        │             │             │                  │
┌───────▼──────┐ ┌───▼────────┐ ┌─▼───────────┐ ┌────▼─────────┐
│ OMV DATA     │ │ KNOWLEDGE  │ │ LLM         │ │ TRACE        │
│ COLLECTOR    │ │ BASE       │ │ INTEGRATION │ │ STORE        │
│ (SSH + Logs) │ │ (24 Manual │ │ (GLM-4.7)   │ │ (In-Memory)  │
│              │ │ Patterns)  │ │             │ │              │
└──────────────┘ └────────────┘ └────────────┘ └──────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │ OMV Server      │
            │ (192.168.3.68)  │
            └─────────────────┘
```

### 1.2 Core Components (Simplified)

#### OMV Data Collector
- **SSH Integration**: Execute commands on OMV server (primary method)
- **RPC Integration**: Pull configuration via OMV RPC API (fallback, OMV 7.x+ restricts to localhost)
- **Log Collection**: Parse syslog, service logs, error patterns via SSH
- **Metrics Collector**: CPU, memory, disk, network statistics via system commands

#### Knowledge Base
- **Manual Pattern Repository**: Curated OMV issue/solution pairs
- **Documentation Index**: OMV docs, forum knowledge, common fixes
- **Configuration Templates**: Best practice configurations
- **User Context**: System history, previous issues, user preferences

#### LLM Integration
- **Context Router**: Select appropriate specialist prompt
- **Specialist Prompts**: Storage, Network, Performance, Security contexts
- **Response Formatter**: Structure AI responses for consistency
- **Feedback Loop**: Capture user acceptance of suggestions

#### Monitoring & Alerting
- **Prometheus Integration**: Standard metrics collection
- **Grafana Dashboards**: Visual system health representation
- **Smart Alerting**: Context-aware thresholds, not just static limits
- **Trend Analysis**: Simple forecasting for capacity planning

---

## 2. OMV Domain Focus (Practical)

### 2.1 Target Capabilities

```yaml
Core_Capabilities:
  System_Monitoring:
    - Real-time metrics dashboard
    - Service status tracking
    - Resource utilization alerts
    - Health score calculation

  Troubleshooting_Assistance:
    - Error log analysis with explanations
    - Suggested diagnostic steps
    - Solution recommendations
    - Related known issues

  Proactive_Maintenance:
    - Disk space forecasting
    - Update impact analysis
    - Configuration drift detection
    - Backup verification reminders

  Knowledge_Management:
    - Issue history tracking
    - Solution documentation
    - Configuration snapshots
    - User notes and learnings
```

### 2.2 Specialist Contexts (Prompt-Based)

```yaml
Specialist_Prompts:
  Storage_Context:
    trigger: ["disk", "storage", "zfs", "raid", "filesystem"]
    expertise: "Storage systems, RAID, ZFS, disk management"
    focus: "Data integrity, performance optimization, failure recovery"

  Network_Context:
    trigger: ["network", "connection", "firewall", "vpn", "interface"]
    expertise: "Network configuration, services, security"
    focus: "Connectivity, performance, access control"

  Service_Context:
    trigger: ["smb", "nfs", "ftp", "ssh", "plex", "service"]
    expertise: "Service configuration and troubleshooting"
    focus: "Availability, performance, integration"

  Performance_Context:
    trigger: ["slow", "performance", "cpu", "memory", "load"]
    expertise: "System performance analysis"
    focus: "Bottlenecks, optimization, resource allocation"

  Security_Context:
    trigger: ["permission", "access", "security", "auth", "vulnerability"]
    expertise: "Security hardening and access control"
    focus: "Best practices, vulnerability mitigation"
```

---

## 3. Technical Stack (Pragmatic)

### 3.1 Backend System

```yaml
Core_Framework:
  language: "Python 3.11+ (tested on 3.13.7)"
  framework: "FastAPI"
  architecture: "Monolithic first, microservices if needed"
  api_port: 8888

Knowledge_Storage:
  primary: "SQLite with JSON extension (start simple)"
  document_store: "File-based with search index (whoosh)"
  upgrade_path: "PostgreSQL when needed"
  graph_db: "Deferred until proven requirement"

AI_Integration:
  primary_llm: "GLM-4.7"
  api_endpoint: "https://api.z.ai/api/coding/paas/v4/chat/completions"
  fallback_llms: ["Claude", "GPT-4"]
  approach: "Prompt-based context switching"

Monitoring_Stack:
  metrics: "Prometheus + node_exporter"
  visualization: "Grafana with custom dashboards"
  alerting: "Alertmanager with custom routing"
  logs: "Promtail + Loki (lighter than ELK)"
```

### 3.2 Data Flow (Simplified)

```
┌──────────────┐
│ OMV Server   │
│ - SSH        │─────┐ (Primary)
│ - RPC API    │─────┤ (Fallback/Localhost)
│ - Log Files  │     │
└──────────────┘     │
                    │
        ┌───────────▼─────────────┐
        │  Data Collector Service│
        │  - Execute SSH commands│
        │  - Parse system output │
        │  - Monitor log files   │
        └───────────┬─────────────┘
                    │
        ┌───────────▼─────────────┐
        │  Context Builder        │
        │  - Assemble state       │
        │  - Match patterns       │
        │  - Calculate metrics    │
        └───────────┬─────────────┘
                    │
        ┌───────────▼─────────────┐         ┌──────────────┐
        │  Assistant Engine       │◄────────│ User Query   │
        │  - Select context       │         └──────────────┘
        │  - Build prompt         │
        │  - Call LLM             │
        │  - Format response      │
        └───────────┬─────────────┘
                    │
        ┌───────────▼─────────────┐
        │  Response & UI          │
        │  - Display suggestions  │
        │  - Capture feedback     │
        │  - Update knowledge     │
        └─────────────────────────┘
```

### 3.3 Core Service Modules

#### 1. Data Collector Service
```python
class OMVSSHCollector:
    """Collects OMV data via SSH (primary method)"""

    def __init__(self, hostname: str, username: str, password: str, port: int = 22):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self._client: asyncssh.SSHClientConnection | None = None

    async def _run_command(self, command: str) -> str:
        """Execute command via SSH and return output"""
        await self._connect()
        result = await self._client.run(command, timeout=self.timeout)
        return result.stdout

    async def collect_system_info(self) -> dict[str, Any]:
        """Collect system information"""
        hostname = await self._run_command("hostname")
        uptime = await self._run_command("uptime -s")
        kernel = await self._run_command("uname -r")
        # ... parse and return structured data

    async def get_all_service_status(self) -> dict[str, Any]:
        """Get status of all OMV services"""
        services = ["smbd", "nfsd", "ssh", "nginx", "php-fpm", ...]
        status = {}
        for service in services:
            result = await self._run_command(f"systemctl is-active {service}")
            status[service] = {"status": result.strip()}
        return status

# RPC Fallback (for localhost or OMV 6.x)
class OMVDataCollector:
    """RPC-based collector (fallback method)"""
    # OMV 7.x+ restricts RPC to localhost only
```

#### 2. Knowledge Base Service
```python
class KnowledgeBase:
    """Manual and structured knowledge storage"""

    def __init__(self):
        self.patterns = self.load_manual_patterns()
        self.history = UserHistoryStore()

    def load_manual_patterns(self):
        """Load manually curated issue/solution patterns"""
        # Example pattern structure:
        return [
            {
                'id': 'omv-001',
                'title': 'SMB share not accessible',
                'symptoms': ['connection timeout', 'access denied'],
                'diagnostics': ['check_service_status', 'verify_permissions', 'test_network'],
                'solutions': ['restart_smb', 'fix_permissions', 'check_firewall'],
                'related_patterns': ['omv-005', 'omv-012']
            },
            # ... more patterns
        ]

    def find_similar_issues(self, current_state):
        """Find historically similar issues"""
        return self.history.search_similar(current_state)

    def get_user_context(self, user_id):
        """Get user's system history and preferences"""
        return {
            'previous_issues': self.history.get_issues(user_id),
            'system_snapshot': self.history.get_last_snapshot(user_id),
            'successful_fixes': self.history.get_successful_fixes(user_id)
        }
```

#### 3. Assistant Engine Service
```python
class AssistantEngine:
    """Core assistance and LLM integration logic"""

    def __init__(self, llm_client):
        self.llm = llm_client
        self.specialists = self.load_specialist_prompts()

    def load_specialist_prompts(self):
        """Load prompt templates for different contexts"""
        return {
            'storage': open('prompts/storage_specialist.txt').read(),
            'network': open('prompts/network_specialist.txt').read(),
            'service': open('prompts/service_specialist.txt').read(),
            'performance': open('prompts/performance_specialist.txt').read(),
            'security': open('prompts/security_specialist.txt').read(),
        }

    def select_context(self, query, system_state):
        """Select appropriate specialist context"""
        query_lower = query.lower()
        for context_name, config in SPECIALIST_CONTEXTS.items():
            if any(trigger in query_lower for trigger in config['triggers']):
                return context_name
        return 'general'

    def build_prompt(self, context, query, system_state, user_context):
        """Build contextual prompt for LLM"""
        specialist_prompt = self.specialists.get(context, self.specialists['general'])

        return f"""
{specialist_prompt}

CURRENT SYSTEM STATE:
{json.dumps(system_state, indent=2)}

USER CONTEXT:
{json.dumps(user_context, indent=2)}

USER QUERY:
{query}

Provide your response in the following JSON format:
{{
    "analysis": "Brief analysis of the situation",
    "suggested_diagnostics": ["step1", "step2", ...],
    "possible_causes": ["cause1", "cause2", ...],
    "recommended_actions": ["action1", "action2", ...],
    "explanation": "Clear explanation for the user",
    "follow_up_questions": ["question1", "question2", ...]
}}
"""

    def assist(self, query, system_state, user_context):
        """Generate contextual assistance"""
        context = self.select_context(query, system_state)
        prompt = self.build_prompt(context, query, system_state, user_context)
        response = self.llm.generate(prompt)
        return self.format_response(response)

    def format_response(self, llm_response):
        """Format LLM response for UI"""
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            # Fallback formatting if LLM doesn't return valid JSON
            return {
                'raw_response': llm_response,
                'suggested_diagnostics': [],
                'recommended_actions': []
            }
```

#### 4. Alerting Service
```python
class SmartAlerting:
    """Context-aware alerting system"""

    def __init__(self):
        self.rules = self.load_alert_rules()
        self.history = AlertHistory()

    def load_alert_rules(self):
        """Load smart alerting rules"""
        return [
            {
                'name': 'disk_space_prediction',
                'metric': 'disk_usage_percent',
                'condition': lambda trend: self.predict_exhaustion(trend) < 7,  # days
                'severity': 'warning',
                'message': 'Disk space will be exhausted in less than 7 days at current trend'
            },
            {
                'name': 'service_down',
                'metric': 'service_status',
                'condition': lambda status: status == 'down',
                'severity': 'critical',
                'message': 'Critical service is not running'
            },
            # ... more rules
        ]

    def evaluate_alerts(self, system_state):
        """Evaluate all alert rules"""
        alerts = []
        for rule in self.rules:
            if rule['condition'](system_state.get(rule['metric'])):
                alerts.append({
                    'rule': rule['name'],
                    'severity': rule['severity'],
                    'message': rule['message'],
                    'timestamp': datetime.now()
                })
        return self.deduplicate_alerts(alerts)

    def predict_exhaustion(self, usage_trend):
        """Simple linear prediction for resource exhaustion"""
        if len(usage_trend) < 2:
            return float('inf')
        rate = (usage_trend[-1] - usage_trend[0]) / len(usage_trend)
        if rate <= 0:
            return float('inf')
        remaining = 100 - usage_trend[-1]
        return remaining / rate
```

---

## 4. Implementation Roadmap (Realistic)

### Phase 0: Validation & Setup (Week 1) ✅ COMPLETED

**Goals:** Validate feasibility and set up foundation

- [x] Set up development environment (Python 3.13.7, venv, git)
- [x] Spin up OMV test instance or use existing server (192.168.3.68)
- [x] Test OMV connectivity (SSH-based, not RPC due to OMV 7.x restrictions)
- [ ] Set up Prometheus + node_exporter for metrics (deferred)
- [ ] Set up Loki + Promtail for log collection (deferred)
- [x] Create basic project structure
- [x] Validate GLM-4.7 API access

**Deliverables:**
- [x] Working dev environment
- [x] OMV SSH connection documented and tested
- [ ] Metrics and logs flowing to storage (deferred to Phase 1)

**Notes:**
- OMV 7.x restricts RPC API to localhost only; pivoted to SSH-based collection
- GLM API endpoint: https://api.z.ai/api/coding/paas/v4/chat/completions (international platform)
- API server running on port 8888

---

### Phase 1: Foundation (Weeks 2-6)

**Week 2-3: Data Collection**
- [ ] Implement OMV RPC client wrapper
- [ ] Build metrics collector from Prometheus
- [ ] Build log collector from Loki
- [ ] Create configuration snapshot system
- [ ] Build context assembly service

**Week 4-5: Knowledge Base**
- [ ] Design knowledge base schema
- [ ] Implement manual pattern storage
- [ ] Create initial 20-30 curated OMV patterns
- [ ] Build user history tracking
- [ ] Implement similarity search

**Week 6: Basic LLM Integration**
- [ ] Create specialist prompt templates
- [ ] Implement context router
- [ ] Build basic assistant engine
- [ ] Create response formatter
- [ ] Test with sample queries

**Deliverables:**
- Collecting data from OMV
- Knowledge base with initial patterns
- LLM providing basic suggestions

---

### Phase 2: User Interface (Weeks 7-10)

**Week 7-8: Web Dashboard**
- [ ] Set up React + D3.js project
- [ ] Create system overview page (metrics, status)
- [ ] Build query interface
- [ ] Display suggestions and diagnostics
- [ ] Add feedback mechanism

**Week 9-10: Enhanced Features**
- [ ] Add historical analysis view
- [ ] Build alert center
- [ ] Create configuration diff viewer
- [ ] Add knowledge base browser
- [ ] Implement user preferences

**Deliverables:**
- Functional web dashboard
- User can query and get suggestions
- System monitoring visible

---

### Phase 2.5: Tracing & Passthrough (Completed) ✅

**Execution Tracing System**
- [x] Trace data structures (ExecutionTrace, TraceEvent, TraceStore)
- [x] 9 decision point tracing in assistant engine
- [x] Trace storage and retrieval API
- [x] Mermaid diagram generation for visual flow
- [x] Traces visualization UI in web dashboard

**Passthrough Chat Mode**
- [x] Passthrough parameter in API and assist method
- [x] Direct LLM access bypassing knowledge base
- [x] Toggle UI in AI Assistant page
- [x] "Direct Chat Mode" badge indicator

**Deliverables:**
- Full visibility into AI decision pipeline
- Faster general-purpose chat mode
- Mermaid flowcharts for execution paths
- Trace history with timing data

**API Endpoints Added:**
- `GET /api/v1/traces` - List all traces
- `GET /api/v1/traces/{query_id}` - Get specific trace
- `GET /api/v1/traces/{query_id}/mermaid` - Get Mermaid diagram

---

### Phase 3: Intelligence & Features (Weeks 11-16)

**Week 11-12: Smart Alerting**
- [ ] Implement alert rule engine
- [ ] Create prediction algorithms
- [ ] Build alert management UI
- [ ] Add notification channels (email, webhook)
- [ ] Implement alert deduplication

**Week 13-14: Enhanced Assistance**
- [ ] Implement multi-step diagnostic workflows
- [ ] Add learning from feedback
- [ ] Create contextual explanations
- [ ] Build follow-up question generation
- [ ] Implement solution verification

**Week 15-16: Proactive Features**
- [ ] Capacity planning predictions
- [ ] Configuration drift detection
- [ ] Automated health reports
- [ ] Update impact analysis
- [ ] Backup verification

**Deliverables:**
- Proactive alerting
- Enhanced troubleshooting assistance
- Capacity planning features

---

### Phase 4: Polish & Production (Weeks 17-20)

**Week 17-18: CLI Tool**
- [ ] Build Click-based CLI interface
- [ ] Implement all dashboard features in CLI
- [ ] Add configuration management commands
- [ ] Create batch operation support

**Week 19-20: Production Hardening**
- [ ] Security audit and hardening
- [ ] Performance optimization
- [ ] Error handling and recovery
- [ ] Documentation completion
- [ ] Deployment automation (Docker Compose)
- [ ] Testing and bug fixes

**Deliverables:**
- Production-ready system
- Complete documentation
- Easy deployment

---

## 5. Knowledge Base Pattern Structure

### 5.1 Manual Pattern Template

```yaml
pattern_id: "omv-001"
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

  - name: "Test network connectivity"
    command: "ping {client_ip}"
    expected_output: "responses received"

solutions:
  - priority: 1
    action: "Restart SMB service"
    command: "systemctl restart smbd"
    explanation: "Service may be hung"

  - priority: 2
    action: "Check firewall rules"
    command: "iptables -L -n | grep 445"
    explanation: "Port 445 may be blocked"

  - priority: 3
    action: "Verify share permissions"
    command: "omv-rpc Smb shareList"
    explanation: "Permissions may be misconfigured"

related_patterns:
  - "omv-005: Network connectivity issues"
  - "omv-012: Permission problems"

references:
  - "https://forum.openmediavault.org/t/..."
  - "OMV documentation: SMB configuration"

confidence: 0.9
```

### 5.2 Specialist Prompt Template

```text
You are an OpenMediaVault Storage Specialist with deep expertise in:
- ZFS administration and troubleshooting
- RAID configuration and recovery
- File system optimization
- Disk health monitoring
- Data integrity and recovery

Your role is to assist OMV server administrators with storage-related issues.

Guidelines:
1. Be practical and actionable
2. Explain technical concepts clearly
3. Prioritize data safety
4. Suggest diagnostics before fixes
5. Consider performance implications
6. Reference OMV-specific tools when available

When analyzing issues:
- Start with non-invasive diagnostics
- Consider both hardware and software factors
- Provide clear warning signs to watch for
- Suggest data protection measures

Always respond in the specified JSON format.
```

---

## 6. Configuration & Setup

### 6.1 Environment Configuration

```yaml
# .env file (actual configuration)

# OMV Server Settings (SSH-based collection)
OMV_HOSTNAME=192.168.3.68
OMV_PORT=22
OMV_USERNAME=root
OMV_PASSWORD=your-password
OMV_USE_SSH=true

# RPC-based collection (alternative, if SSH not available)
# OMV_RPC_ENDPOINT=http://192.168.3.68/rpc
# OMV_RPC_USERNAME=admin
# OMV_RPC_PASSWORD=your-password

# LLM Integration
LLM_PROVIDER=GLM
LLM_MODEL=glm-4.7
LLM_API_KEY=your-api-key-here
LLM_API_ENDPOINT=https://api.z.ai/api/coding/paas/v4/chat/completions
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7

# Optional: Fallback LLM
# LLM_FALLBACK_PROVIDER=Anthropic
# LLM_FALLBACK_MODEL=claude-sonnet-4-20250514
# LLM_FALLBACK_API_KEY=your-anthropic-api-key

# Monitoring Stack (optional, not yet deployed)
# MONITORING_PROMETHEUS_URL=http://localhost:9090
# MONITORING_LOKI_URL=http://localhost:3100
# MONITORING_GRAFANA_URL=http://localhost:3001

# Knowledge Base
KNOWLEDGE_STORAGE_PATH=data/knowledge
KNOWLEDGE_MANUAL_PATTERNS_PATH=patterns/manual.yaml
KNOWLEDGE_USER_HISTORY_PATH=data/history

# Application Settings
ENVIRONMENT=development
DEBUG=true
```

### 6.2 Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/omv-copilot.git
cd omv-copilot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OMV server details and GLM API key

# Test SSH connection to OMV server
python scripts/test_ssh_connection.py

# Run development server
PYTHONPATH=/path/to/project/src ./venv/bin/uvicorn omv_copilot.api.app:create_app --host 0.0.0.0 --port 8888
```

### 6.3 Docker Compose for Monitoring Stack

```yaml
# docker-compose.yml

version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./config/grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - ./config/promtail:/etc/promtail
    command: -config.file=/etc/promtail/config.yml

volumes:
  prometheus_data:
  grafana_data:
```

---

## 7. API Interface

### 7.1 REST API Endpoints

```yaml
# API endpoints

# System State
GET  /api/v1/system/status
GET  /api/v1/system/metrics
GET  /api/v1/system/logs?since=3600
GET  /api/v1/system/configuration

# Assistance
POST /api/v1/assist/query
POST /api/v1/assist/diagnostics
POST /api/v1/assist/solution

# Knowledge Base
GET  /api/v1/knowledge/patterns
GET  /api/v1/knowledge/patterns/{id}
GET  /api/v1/knowledge/search?q=query
POST /api/v1/knowledge/feedback

# Alerts
GET  /api/v1/alerts
GET  /api/v1/alerts/{id}
POST /api/v1/alerts/acknowledge/{id}

# History
GET  /api/v1/history/issues
GET  /api/v1/history/snapshots
POST /api/v1/history/note
```

### 7.2 Example API Usage

```python
# Query assistant
response = requests.post('http://localhost:8000/api/v1/assist/query', json={
    'query': 'SMB share is very slow when copying large files',
    'context': 'storage'
})

# Response
{
    'analysis': 'Slow SMB performance with large files is typically caused by...',
    'suggested_diagnostics': [
        'Check disk I/O performance during transfer',
        'Verify network interface speed and duplex',
        'Check SMB configuration options'
    ],
    'possible_causes': [
        'Disk I/O bottleneck',
        'Network congestion',
        'SMB buffer misconfiguration'
    ],
    'recommended_actions': [
        'Run iostat during file transfer',
        'Test with iperf to verify network capacity',
        'Consider enabling SMB3 multi-channel'
    ],
    'explanation': 'Large file transfers over SMB require...',
    'follow_up_questions': [
        'What is the actual transfer speed you are seeing?',
        'Are other network services slow as well?',
        'Is this happening on all shares or specific ones?'
    ]
}
```

---

## 8. Success Metrics

### 8.1 Practical Metrics

```yaml
Effectiveness_Metrics:
  Problem_Solving:
    - "Mean time to resolution (MTTR) reduction"
    - "First-time fix rate improvement"
    - "Issue recurrence reduction"
    - "User-reported satisfaction"

  System_Health:
    - "System uptime improvement"
    - "Proactive issue detection rate"
    - "Backup completion success rate"
    - "Security vulnerability response time"

  Adoption:
    - "Daily active users"
    - "Query success rate"
    - "Feedback acceptance rate"
    - "Feature utilization"
```

### 8.2 Data Collection Plan

```python
class MetricsCollector:
    """Track system effectiveness"""

    def track_resolution(self, issue_id, start_time, success, user_feedback):
        """Track problem resolution metrics"""
        return {
            'issue_id': issue_id,
            'time_to_resolution': time.time() - start_time,
            'success': success,
            'user_rating': user_feedback.get('rating'),
            'suggestions_followed': user_feedback.get('suggestions_used', [])
        }

    def track_prevention(self, alert_id, resolved_before_impact):
        """Track proactive issue prevention"""
        return {
            'alert_id': alert_id,
            'prevented_outage': resolved_before_impact,
            'time_before_impact': self.estimate_time_to_impact(alert_id)
        }
```

---

## 9. Future Enhancements

### 9.1 Potential Upgrades

```yaml
Version_3_Considerations:
  Advanced_ML:
    - "Anomaly detection for proactive monitoring"
    - "Automated pattern extraction from successful resolutions"
    - "Predictive maintenance scheduling"

  Collaboration:
    - "Multi-user collaboration features"
    - "Community knowledge sharing"
    - "Expert review and validation"

  Automation:
    - "Automated remediation for safe operations"
    - "Integration with OMV plugin system"
    - "Configuration deployment automation"

  Expansion:
    - "Support for additional NAS platforms"
    - "Docker/Kubernetes cluster management"
    - "General Linux administration"
```

### 9.2 Extension Points

```yaml
Integration_Opportunities:
  Monitoring:
    - "Existing Prometheus/Grafana setups"
    - "Netdata for detailed metrics"
    - "Zabbix for enterprise environments"

  Automation:
    - "Ansible playbooks for remediation"
    - "Rundeck/Apache Airflow for job scheduling"
    - "Custom OMV plugins"

  Notification:
    - "Email notifications"
    - "Slack/Discord webhooks"
    - "Pushover/Pushbullet for mobile"
```

---

## Conclusion

OMV Co-Pilot takes a pragmatic approach to AI-assisted server management. By focusing on immediate practical value and iterating based on real usage, we avoid the research-heavy complexities of full cognitive augmentation while still delivering significant benefits.

**Key Differentiators from v1:**

1. **Simpler Architecture**: Monolithic first, proven patterns
2. **Practical AI**: Prompt-based context switching vs complex multi-agent system
3. **Existing Tools**: Leverages Prometheus/Grafana/Loki instead of building from scratch
4. **Manual Knowledge**: Curated patterns vs unproven automatic extraction
5. **Realistic Timeline**: 20 weeks vs 18 weeks for substantially less scope
6. **Clear Value Proposition**: Solves immediate problems vs abstract enhancement

**Next Steps:**

1. Set up development environment
2. Validate OMV RPC API access
3. Deploy monitoring stack
4. Build initial data collector
5. Create first specialist prompts
6. Deploy to test OMV instance

The goal is working software that provides real value, not a research project exploring the boundaries of AI.

---

## 10. Implementation Status

### Current State (January 4, 2026)

```yaml
Phase_0_Status: "COMPLETED"
Phase_1_Status: "COMPLETED"
Phase_2_Status: "COMPLETED"
Phase_2.5_Status: "COMPLETED"
Core_Functionality: "OPERATIONAL WITH TRACING AND PASSTHROUGH"

Implemented_Components:
  Data_Collection:
    - "SSH-based OMV collector (OMVSSHCollector)"
    - "System info collection (hostname, kernel, CPU, memory, network)"
    - "Service status monitoring (SMB, NFS, SSH, nginx, PHP-FPM, cron)"
    - "Disk and filesystem information"
    - "Network interface enumeration"
    - "SMB/NFS share listing"
    - "Error log parsing from journalctl"

  Knowledge_Base:
    - "Pattern storage (YAML-based, 24 patterns implemented)"
    - "Pattern loading and matching"
    - "Pattern search with symptom scoring"
    - "User history tracking (JSON-based)"
    - "Feedback recording system"
    - "Pattern categories: Storage (6), Network (5), Services (4), Performance (3), Security (4)"

  LLM_Integration:
    - "GLM-4.7 client with international endpoint"
    - "Context-aware specialist routing (storage, network, service, performance, security, general)"
    - "JSON response parsing with GLM-4.7 reasoning_content handling"
    - "Async HTTP client with configurable timeout (120s default)"
    - "Confidence scoring based on pattern matching"

  API_Server:
    - "FastAPI application on port 8888"
    - "/api/v1/assist/query - AI assistance with confidence scores (supports passthrough mode)"
    - "/api/v1/assist/diagnostics - Diagnostic suggestions"
    - "/api/v1/system/status - System operational status"
    - "/api/v1/system/configuration - Full OMV configuration"
    - "/api/v1/system/metrics - System metrics"
    - "/api/v1/knowledge/patterns - List all patterns (full data)"
    - "/api/v1/knowledge/patterns/{id} - Get specific pattern"
    - "/api/v1/knowledge/search - Search patterns"
    - "/api/v1/traces - List all execution traces"
    - "/api/v1/traces/{query_id} - Get specific trace with full details"
    - "/api/v1/traces/{query_id}/mermaid - Get Mermaid flowchart for trace"
    - "/docs - Interactive API documentation"

  Web_Dashboard:
    - "React + Vite frontend on port 3000"
    - "Tailwind CSS styling with custom dark theme"
    - "5 main pages: Dashboard, AI Assistant, Knowledge Base, Diagnostics, Traces"
    - "Real-time system metrics display"
    - "AI query interface with confidence indicators and passthrough toggle"
    - "Pattern browser with expand/collapse and raw JSON view"
    - "Health check summary (services, filesystems, storage)"
    - "Execution trace viewer with decision point timeline"
    - "Mermaid diagram generation for trace visualization"

  Execution_Tracing:
    - "9 decision point tracing (query_received → response_assembly)"
    - "In-memory trace store with JSON serialization"
    - "Timing data for each stage (milliseconds)"
    - "Mermaid flowchart generation"
    - "Trace history with pagination"

  Passthrough_Mode:
    - "Direct LLM access bypassing knowledge base"
    - "Toggle switch in AI Assistant UI"
    - "Shows 'Direct Chat Mode' badge when active"
    - "Faster response time (no system context collection)"

  CLI_Tool:
    - "Click-based CLI with Rich formatting"
    - "Commands: query, status, patterns, diagnose"
    - "System-wide installation via symlink"
    - "Colored output and progress indicators"
    - "Table formatting for service status and disks"

OMV_Server_Environment:
  - "OMV 7.7.21-1 (Sandworm/Debian 12)"
  - "7 storage devices (SATA, NVMe, eMMC)"
  - "11 network interfaces"
  - "14 SMB shares configured"

Completed_Phases:
  Phase_0:
    - "Development environment setup (Python 3.13.7)"
    - "OMV SSH connection validated"
    - "GLM-4.7 API access confirmed"
    - "Basic project structure created"

  Phase_1:
    - "Data collectors operational"
    - "24 knowledge patterns implemented"
    - "Specialist prompts created (6 contexts)"
    - "LLM integration with confidence scoring"
    - "Knowledge base with search and matching"

  Phase_2:
    - "React + Vite project created"
    - "Dashboard with system overview"
    - "AI Assistant query interface"
    - "Knowledge Base browser"
    - "Diagnostics page"
    - "API client integration"
    - "Responsive layout with sidebar navigation"

  Phase_2.5:
    - "Execution tracing system implemented"
    - "9 decision points tracked with timing"
    - "Trace storage and retrieval API"
    - "Mermaid diagram generation"
    - "Traces visualization UI (5th page)"
    - "Passthrough chat mode for direct LLM access"
    - "Direct chat toggle in AI Assistant UI"

Known_Limitations:
  - "Monitoring stack (Prometheus/Loki) not yet deployed"
  - "Smart alerting not yet implemented"
  - "User feedback loop not yet connected to learning"
  - "Capacity planning predictions not implemented"
  - "Configuration diff viewer not built"

Next_Phase_Options:
  Option_1:
    - "Add more knowledge patterns (aim for 50+)"
    - "Improve pattern matching with semantic search"
    - "Add pattern editing in the web UI"

  Option_2:
    - "Deploy monitoring stack (Prometheus + Grafana + Loki)"
    - "Implement smart alerting with predictions"
    - "Add alert management UI"

  Option_3:
    - "Implement user feedback capture"
    - "Build learning from feedback system"
    - "Add pattern confidence adjustment"

  Option_4:
    - "Add multi-step diagnostic workflows"
    - "Implement solution verification"
    - "Build follow-up question generation"

  Option_5:
    - "Production hardening (security audit)"
    - "Docker Compose deployment"
    - "Complete documentation"
```

### LLM + Knowledge Map Integration

The relationship between the LLM and Knowledge Map works as follows:

```
User Query → Context Selection → System Data Collection → Pattern Matching → Prompt Assembly → LLM Response

1. CONTEXT SELECTION (specialist_prompts.py)
   - Query analyzed for keywords (cpu, disk, smb, etc.)
   - Appropriate specialist context selected (performance, storage, service, etc.)
   - Specialist prompt provides domain expertise

2. SYSTEM DATA COLLECTION (assistant_engine.py)
   - OMV configuration collected via SSH
   - Service status retrieved
   - Current system state assembled

3. PATTERN MATCHING (knowledge_base.py)
   - Current symptoms extracted from system state
   - Knowledge patterns scored by symptom match
   - Top patterns (up to 5) selected with scores

4. PROMPT ASSEMBLY (assistant_engine.py)
   [Specialist Prompt] - Domain expertise
   [System State] - Current OMV data (truncated to 5000 chars)
   [Matched Patterns] - Relevant knowledge from KB
   [User Query] - Original question
   [Response Format] - JSON structure requirement

5. CONFIDENCE CALCULATION
   - Base confidence: 0.5
   - Pattern score bonus: average score added to base
   - High-score bonus: +0.1 if top pattern score > 0.7
   - Final confidence capped at 0.98

6. LLM RESPONSE
   - Analysis of the situation
   - Suggested diagnostics
   - Possible causes
   - Recommended actions
   - Explanation
   - Follow-up questions
   - Confidence score (included in response)
   - Matched patterns (included in response)
```

### Project Structure

```
eeframe/
├── src/omv_copilot/
│   ├── api/
│   │   └── app.py                 # FastAPI application (port 8888)
│   ├── assist/
│   │   ├── llm_client.py          # GLM integration with timeout
│   │   ├── assistant_engine.py    # Main assistance orchestration
│   │   └── specialist_prompts.py  # 6 specialist contexts
│   ├── collectors/
│   │   ├── ssh_collector.py       # SSH-based data collection
│   │   ├── omv_collector.py       # OMV-specific collectors
│   │   ├── prometheus_collector.py # Prometheus metrics
│   │   └── loki_collector.py      # Loki log collection
│   ├── knowledge/
│   │   ├── knowledge_base.py      # Pattern storage and matching
│   │   └── patterns.py            # Pattern dataclass
│   ├── alerting/
│   │   └── alert_engine.py        # Alert rule engine (not yet used)
│   └── settings.py                # Pydantic configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx         # Sidebar navigation
│   │   │   └── UI.jsx              # Reusable components
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx       # System overview
│   │   │   ├── Assistant.jsx       # AI query interface
│   │   │   ├── Knowledge.jsx       # Pattern browser
│   │   │   └── Diagnostics.jsx     # Health checks
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   ├── App.jsx                # React Router setup
│   │   └── main.jsx               # Entry point
│   ├── package.json
│   └── vite.config.js             # Proxy to :8888
├── patterns/
│   └── manual.yaml                # 24 curated OMV patterns
├── scripts/
│   └── test_ssh_connection.py     # Connection testing
├── data/                          # Runtime data directory
│   ├── knowledge/                 # User history
│   └── history/                   # Knowledge snapshots
├── .env                           # Environment configuration
├── pyproject.toml                 # Python project config
├── claude.md                      # Context recovery file
└── nodes.md                       # Pattern documentation
```

### Key Implementation Notes

1. **SSH vs RPC**: OMV 7.x restricts external RPC access. SSH collector is the primary method.
2. **GLM Endpoint**: Use `https://api.z.ai/api/coding/paas/v4/chat/completions` (not `open.bigmodel.com`)
3. **SSL Verification**: Disabled for GLM API (`verify=False`) due to certificate issues
4. **Port**: API server runs on port 8888 (8000 was already in use)
5. **Python Version**: Developed on Python 3.13.7 (compatible with 3.11+)

---

## Appendices

### Appendix A: Specialist Prompt Templates
[Complete prompt templates for each specialist context]

### Appendix B: Manual Pattern Library
[Initial set of curated OMV patterns]

### Appendix C: Prometheus Queries
[Useful PromQL queries for OMV monitoring]

### Appendix D: Alert Rules Reference
[Complete alert rule configuration reference]

---

*Document Version: 2.3.0*
*Last Updated: January 4, 2026*
*Based on: expertise_enhancement_framework_omv.md v1.0.0*
*Implementation Status: Phase 0-2.5 Complete - Tracing and Passthrough Mode Operational*
