# OMV Co-Pilot: Complete Implementation Guide

_A comprehensive deep-dive covering architecture, knowledge mapping, and practical implementation strategies_

---

## Table of Contents

1. [Executive Summary](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#executive-summary)
2. [Project Scope and Philosophy](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#project-scope-and-philosophy)
3. [Scalability to Other Domains](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#scalability-to-other-domains)
4. [Intellectual Property Strategy](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#intellectual-property-strategy)
5. [Sustainable Development Approach](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#sustainable-development-approach)
6. [OMV RPC Deep Dive](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#omv-rpc-deep-dive)
7. [Knowledge Mapping System](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#knowledge-mapping-system)
8. [Implementation Roadmap](https://claude.ai/chat/b6e5c95c-91fb-4f2a-970f-f018637b2c7e#implementation-roadmap)

---

## Executive Summary

OMV Co-Pilot is a domain-specific AI assistant for OpenMediaVault server management that uses a novel **knowledge mapping architecture** rather than traditional RAG or fine-tuning approaches. The system combines:

- **Structured pattern library** (manually curated troubleshooting patterns)
- **Specialist prompt routing** (context-aware AI specialization)
- **User context tracking** (learning from history and preferences)
- **OMV RPC integration** (real-time system state collection)

### Key Innovation

Rather than trying to make an LLM "know" OpenMediaVault, we provide it with:

- A **map** to navigate OMV expertise
- **Coordinates** (system state from RPC)
- A **compass** (user context and history)

This architecture is highly generalizable to other specialized domains: law, medicine, engineering, and beyond.

---

## Project Scope and Philosophy

### Core Philosophy

**"Provide immediate practical value through intelligent assistance, then iterate toward enhanced capabilities."**

This is not a research project exploring the boundaries of AI—it's a pragmatic tool that solves real problems for OMV administrators.

### What This Is

- ✅ Practical troubleshooting assistant
- ✅ Intelligent monitoring and alerting
- ✅ Knowledge management system
- ✅ Proactive maintenance advisor
- ✅ Context-aware diagnostic guide

### What This Is NOT

- ❌ Fully autonomous system administrator
- ❌ General-purpose AI research platform
- ❌ Replacement for human expertise
- ❌ Enterprise monitoring stack competitor

### Simplified vs Complex Architecture

**Version 1 (Overly Complex):**

- Multi-agent cognitive architecture
- Custom monitoring infrastructure
- Graph databases and vector stores
- 18-week timeline

**Version 2 (Pragmatic):**

- Prompt-based specialist routing
- Leverage existing tools (Prometheus/Grafana/Loki)
- SQLite with JSON extensions
- 20-week timeline (realistically 6-12 months at sustainable pace)

### The Trojan Horse Strategy

**What it looks like:** An OMV troubleshooting tool

**What it actually is:** A generalizable cognitive augmentation framework

This allows validation in a bounded domain before tackling larger, more complex domains.

---

## Scalability to Other Domains

### Why This Architecture Scales

The fundamental components are **domain-agnostic**:

```
Data Collector    →  Domain-Specific Information Gatherer
Knowledge Base    →  Structured Expertise Repository
Specialist Router →  Context-Aware AI Specialization
Assistant Engine  →  Reasoning and Response Generator
```

### Domain Comparison Matrix

|Aspect|OMV (Proof of Concept)|Legal|Medical|Engineering|
|---|---|---|---|---|
|**Complexity**|1x (baseline)|100-1000x|50-500x|20-200x|
|**Pattern Count**|~1,000|~100,000|~50,000|~25,000|
|**Data Size**|~10MB|~100GB|~500GB|~50GB|
|**Specialist Count**|5|100-150|120-160|60|
|**Update Frequency**|Monthly|Daily|Weekly|Quarterly|
|**Liability Risk**|Low|Critical|Critical|High|

### Universal Pattern Structure

Patterns are structurally identical across domains:

```yaml
# Domain-agnostic template
pattern:
  identification:
    symptoms: [observable conditions]
    triggers: [keyword patterns]
  
  diagnostics:
    - [investigation steps]
  
  analysis:
    possible_causes: [root causes]
  
  solutions:
    - [remediation steps]
  
  relationships:
    related: [connected patterns]
```

**OMV Example:** "SMB share inaccessible"

- Symptoms: Connection timeout, access denied
- Diagnostics: Check service, verify permissions
- Solutions: Restart service, fix permissions

**Legal Example:** "Breach of non-compete clause"

- Symptoms: Employee working for competitor
- Diagnostics: Verify dates, check clause validity
- Solutions: Cease and desist, negotiate settlement

**Medical Example:** "Chest pain with exertion"

- Symptoms: Substernal pressure, radiating pain
- Diagnostics: ECG, troponin levels, stress test
- Solutions: Aspirin, nitrates, cardiology consult

### The Meta-Platform Vision

```
┌─────────────────────────────────────────────────────────┐
│            Co-Pilot Platform Core                       │
│  • Knowledge Base Framework                             │
│  • Specialist Router                                    │
│  • LLM Integration Layer                                │
│  • User Context Management                              │
│  • Feedback Loop Engine                                 │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ OMV Co-Pilot │  │Legal Co-Pilot│  │ Med Co-Pilot │
│              │  │              │  │              │
│ • OMV RPC    │  │ • Case DB    │  │ • EHR Data   │
│ • Server KB  │  │ • Legal KB   │  │ • Clinical KB│
│ • Sys Prompts│  │ • Law Prompts│  │ • Med Prompts│
└──────────────┘  └──────────────┘  └──────────────┘
```

### Scaling Challenges

**1. Knowledge Base Size**

- OMV: ~1,000 patterns, ~10MB
- Legal: ~100,000 patterns, ~100GB case law
- Solution: Vector databases (Pinecone, Weaviate) + metadata in SQLite

**2. Specialist Count**

- OMV: 5 specialists
- Legal: 100-150 specialists (practice areas × skill levels)
- Solution: Hierarchical routing (domain → subdomain → specialist)

**3. LLM Cost**

- OMV: ~$10-20/month for 100 users
- Legal: ~$500-1000/month for 100 attorneys
- Solution: Hybrid model (small LLM for routing, large for reasoning)

### Commercialization Potential

**OMV Co-Pilot:** Free/Open Source

- Builds community
- Proves architecture
- Reference implementation

**Professional Domains:** Commercial

- Legal Co-Pilot: $200-500/month per attorney
- Medical Co-Pilot: $150-400/month per clinician
- Engineering Co-Pilot: $100-300/month per engineer

**Value Proposition:** Leverage, not replacement. A lawyer billing $400/hr who saves 2-3 hours/week = $40k-60k/year value for $6k/year cost.

---

## Intellectual Property Strategy

### The Challenge

You need to:

1. Get credit for your work
2. Protect your intellectual property
3. Enable open collaboration
4. Preserve commercialization options
5. Not get overwhelmed or burned out

### Asset Inventory

**What You've Created:**

1. **The Framework Document** - Novel architecture for domain-specific AI assistance
2. **The Abstraction Pattern** - Specialist routing + manual knowledge curation
3. **Implementation Code** - Working software (once complete)
4. **Domain Patterns** - Curated OMV troubleshooting knowledge base

### Multi-Layered Protection Strategy

#### Layer 1: Copyright (Immediate)

**Action:** Add copyright notices to all work

```
Copyright (c) 2025 [Your Name]. All Rights Reserved.
Licensed under Apache 2.0 with Commons Clause
```

**Cost:** $65 for official registration at copyright.gov **Timeline:** Do this week **Protection:** Your exact expression of ideas

#### Layer 2: Open Source with Attribution (Week 1)

**License Strategy:**

- Apache 2.0 with Commons Clause
- Code is open and free to use
- Companies can't resell as SaaS without permission
- You retain commercialization rights

**Why This Works:**

- Gets your name attached permanently
- Creates prior art (prevents others from patenting)
- Enables collaboration
- Doesn't prevent commercial licensing

#### Layer 3: Academic Publication (Months 3-6)

**arXiv Preprint:**

- Free, instant public record
- Establishes priority date
- Citeable and prestigious
- Critical for prior art

**Paper Structure:**

```
1. Introduction
   - Problem: General LLMs struggle with specialized domains
   - Solution: Specialist routing + curated knowledge patterns

2. Architecture
   - Component breakdown
   - Why this vs RAG/fine-tuning/agents

3. Implementation (OMV Case Study)
   - Technical details
   - Pattern structure
   - Specialist prompt design

4. Evaluation
   - Effectiveness metrics
   - Comparison to baselines
   - User satisfaction data

5. Generalization
   - Extension to law/medicine/engineering
   - Scaling considerations

6. Future Work & Conclusion
```

**Timeline:**

- Draft as you build (documentation = development)
- Submit to arXiv when beta ready
- Conference submission 3-6 months later

#### Layer 4: Trademark (Months 2-3)

**What to Trademark:**

- Avoid "Co-Pilot" (GitHub conflict)
- Consider: "Domain Specialist Framework" or "Cognitive Augmentation Toolkit"

**Cost:** $250-500 to register **Protection:** Your brand/name

#### Layer 5: Patent (Optional, Expensive)

**What's Patentable:**

- Method for routing queries to domain specialists
- System for augmenting LLMs with curated knowledge
- Apparatus for proactive AI-powered issue detection

**Provisional Patent:**

- Cost: $3,000-5,000
- Buys 12 months to decide
- Establishes priority date

**Full Patent:**

- Cost: $15,000-30,000 over 2-3 years
- 20 years protection
- Can license to others

**Recommendation:** Patents are expensive and slow. For AI/software, **papers + open source + trademark** are often more effective.

### Recommended Timeline

**Week 1 (Now):**

1. ✅ Add copyright to framework document
2. ✅ Create public GitHub repo
3. ✅ Add CITATION.cff file
4. ✅ Write announcement blog post

**Month 1:** 5. ✅ Draft arXiv paper outline 6. ✅ Document architecture decisions 7. ✅ Start building community

**Month 3:** 8. ✅ Submit to arXiv 9. ✅ Target conference workshop 10. ✅ Launch OMV Co-Pilot beta

**Month 6:** 11. ✅ Case studies from real users 12. ✅ Speaking engagement 13. ✅ Decide on commercialization path

### Building Your Brand

**Personal Branding Strategy:**

1. **Domain Name:** Register something memorable
    
    - domaincopilot.com
    - cognitiveframework.com
    - [yourname].tech
2. **Professional Presence:**
    
    - LinkedIn articles
    - Twitter/X technical threads
    - Conference talks
    - Community engagement
3. **Case Studies:**
    
    - Document successful deployments
    - "How we reduced MTTR by 40%"
    - Video testimonials
4. **Thought Leadership:**
    
    - "Why specialist routing beats RAG"
    - "Economics of manual curation"
    - "The future of domain-specific AI"

### Commercialization Models

**Option A: Consulting**

- Framework is open source
- You charge for expertise ($150-300/hr)
- "The framework is free, my expertise isn't"

**Option B: Dual License**

- Open source for individuals/non-commercial
- Commercial license for companies
- $5k-50k per deployment

**Option C: SaaS Platform**

- Core framework is open
- You run hosted platform
- Recurring revenue model

**Option D: Acquisition Target**

- Build prototype + user base
- Document generalization potential
- Approach larger companies
- Exit via acquisition

### The Key Insight

**Your value isn't in hiding the ideas—it's in being known as the person who created them.**

Examples:

- **Andrej Karpathy** - Open sourced nanoGPT, built reputation, hired by OpenAI/Tesla
- **Stable Diffusion** - Open sourced model, built commercial services, raised $101M

Open source + strong attribution + thoughtful branding = sustainable value.

---

## Sustainable Development Approach

### The Real Risk: Cognitive Overload

You're not just building software—you're simultaneously:

- Learning OMV internals
- Learning monitoring stacks
- Learning LLM integration
- Designing novel architectures
- Planning IP strategy
- Considering commercialization
- Absorbing AI/ML concepts
- Planning academic publishing

**That's at least 6 different cognitive domains competing for bandwidth.**

### The "One Thing" Rule

**Core Principle:** At any given time, you should only be learning/figuring out **ONE new thing**. Everything else should use known patterns.

### Phase-Based Learning

**Phase 0-1: Foundation (Weeks 1-6)**

- **The ONE thing:** OMV RPC integration + data collection
- **NOT learning yet:** Advanced LLM, complex monitoring, IP strategy, academic writing

**Phase 2: UI (Weeks 7-10)**

- **The ONE thing:** React + D3.js visualization
- **NOT learning yet:** Advanced assistant features, smart alerting, multi-user

**Phase 3: Intelligence (Weeks 11-16)**

- **The ONE thing:** Specialist prompt engineering + pattern matching
- **NOT learning yet:** ML/AI theory, scaling concerns

### Time-Boxing Strategy

**Sustainable Weekly Schedule:**

```
Monday:    2 hours - New learning (documentation, research)
Tuesday:   OFF (or light coding with known patterns)
Wednesday: 2 hours - Implementation/debugging
Thursday:  OFF
Friday:    2 hours - Testing, integration
Weekend:   1 hour - Reflection, planning next week

Total: 5-7 hours/week, not 20-40 hours
```

### Brutal Prioritization Framework

**Ask yourself:** "If I only ship ONE feature this month, which moves me closest to a working demo?"

#### Essential Path (MVP Only)

```
Month 1: Data In → LLM → Response Out
├─ Week 1: OMV connection working
├─ Week 2: One metric collected
├─ Week 3: One LLM call working
└─ Week 4: CLI tool shows result

Month 2: Make It Useful
├─ Week 5: Add 5 manual patterns
├─ Week 6: Basic pattern matching
├─ Week 7: Simple web UI
└─ Week 8: Query + see suggestions

Month 3: Make It Real
├─ Week 9: Test with real OMV issues
├─ Week 10: Refine based on feedback
├─ Week 11: Document what works
└─ Week 12: Show to 3 people, get reactions
```

**Everything else is optional.**

### The Parking Lot Technique

Create a `FUTURE.md` file for ideas you're explicitly deferring:

```markdown
# Future Enhancements (Not Now)

## IP Protection
- [ ] Draft arXiv paper - DEFER TO MONTH 6
- [ ] Copyright registration - DEFER TO MONTH 4
- [ ] Community building - DEFER TO MONTH 5

## Advanced Features
- [ ] Smart alerting - Phase 3
- [ ] Multi-specialist routing - Phase 3
- [ ] Grafana dashboards - Phase 4

## Other Domains
- [ ] Legal co-pilot - After OMV ships
- [ ] Platform extraction - After 2 domains working
```

**Rule:** Add anytime, but only pull from it when current phase is **completely done**.

### Energy Budget Metaphor

Think of learning capacity like tokens:

**You have 10 "learning tokens" per month:**

```
Month 1 Spending:
├─ 5 tokens: OMV RPC (new domain)
├─ 2 tokens: FastAPI basics (new framework)
├─ 2 tokens: LLM API integration (new skill)
├─ 1 token: Git/deployment (known, rusty)
└─ 0 tokens remaining

Month 2: Everything from Month 1 is now "known"
├─ 5 tokens: React + D3 (new)
├─ 3 tokens: UI/UX design (new)
├─ 2 tokens: WebSocket real-time (new)
└─ 0 tokens remaining
```

**The trap:** Trying to spend 15-20 tokens/month → cognitive overload → burnout

### Red Flags to Watch For

**Stop immediately if you notice:**

- Dreading opening the project
- Perfectionism paralysis
- Constantly rewriting instead of adding features
- Reading more than coding
- Sacrificing sleep
- Losing interest in other hobbies

### Realistic Timeline Adjustment

**Your plan says:** 20 weeks

**Conservative (1 year):**

- Months 1-3: Foundation (working demo)
- Months 4-6: Make it useful (patterns, UI)
- Months 7-9: Polish and test with users
- Months 10-12: Documentation, IP, launch

**Ultra-Conservative (2 years):**

- Year 1: Get it working for YOU
- Year 2: Make it work for others

**Both are fine.** Linux took years. Bitcoin took years. Slow and steady beats fast and burned out.

### "Good Enough" Milestones

```
❌ "Complete data collection system with error handling,
    retry logic, caching, and comprehensive logging"

✅ "Gets current CPU usage from Prometheus and prints it"
```

Ship the second one. Add the rest later **if needed**.

### Copy-Paste is Not Cheating

Especially early on:

- Use example Prometheus configs verbatim
- Copy FastAPI boilerplate from tutorials
- Use standard LLM API examples
- Borrow alert rules from existing systems

**You're building an OMV assistant, not a monitoring platform.**

### Weekly "Discharge" Sessions

Once a week, brain dump everything:

- What you learned
- What confused you
- What you want to try
- What you're worried about

**Then close the file and don't look until next week.** Prevents the 3am "oh I should also..." spiral.

### The Question

**What feels like a sustainable pace for YOU?**

- Hours per week without it feeling like work?
- How long in "exploration" mode before needing results?
- Natural project rhythm (sprint/rest or steady)?

**Answer these, then shape the timeline around them—not the other way around.**

---

## OMV RPC Deep Dive

### What is RPC?

**Remote Procedure Call** - Execute functions on a remote system as if they were local:

```python
# Instead of this (local):
result = get_disk_usage()

# You do this (remote):
result = omv_server.call('FileSystemMgmt', 'getList')
```

### What is OMV RPC?

OpenMediaVault exposes its **entire configuration and management system** through a JSON-RPC 2.0 API.

**The Endpoint:**

```
http://your-omv-server/rpc
```

**Authentication:** HTTP Basic Auth

**This single endpoint is your gateway to everything OMV does.**

### How OMV Uses RPC Internally

```
┌─────────────────────────────────────┐
│   OMV Web UI (JavaScript)          │
│   - Every button click              │
│   - Every page load                 │
│   - Every configuration change      │
└──────────────┬──────────────────────┘
               │ Makes RPC calls
               ▼
┌─────────────────────────────────────┐
│   RPC Endpoint (/rpc)               │
│   - Validates authentication        │
│   - Routes to appropriate service   │
│   - Returns JSON response           │
└──────────────┬──────────────────────┘
               │ Executes
               ▼
┌─────────────────────────────────────┐
│   OMV Backend Services              │
│   - FileSystemMgmt                  │
│   - ShareMgmt (SMB, NFS, FTP)       │
│   - System                          │
│   - Network                         │
└─────────────────────────────────────┘
```

**Key insight:** Anything the web UI can do, you can do via RPC.

### JSON-RPC 2.0 Format

**Request:**

```json
{
  "service": "ServiceName",
  "method": "methodName",
  "params": {
    "param1": "value1"
  },
  "options": null
}
```

**Response:**

```json
{
  "response": {
    // actual data
  },
  "error": null
}
```

### Core OMV Services

#### 1. System Service

```python
# Get system information
{
  "service": "System",
  "method": "getInformation",
  "params": {}
}

# Response:
{
  "hostname": "omv-server",
  "version": "6.x.x",
  "cpuModelName": "Intel Core i5",
  "memTotal": 8192,
  "uptime": "5 days, 3:42"
}

# Other methods:
- reboot()
- shutdown()
- getSystemLogs()
```

#### 2. FileSystemMgmt Service

```python
# List all filesystems
{
  "service": "FileSystemMgmt",
  "method": "getList",
  "params": {
    "start": 0,
    "limit": 25
  }
}

# Response:
{
  "total": 3,
  "data": [
    {
      "devicefile": "/dev/sda1",
      "uuid": "xxx-xxx-xxx",
      "label": "storage1",
      "type": "ext4",
      "mounted": true,
      "used": "50%",
      "available": 500000000000
    }
  ]
}

# Other methods:
- create(), delete(), mount(), umount()
- getDetails(), resize()
```

#### 3. ShareMgmt Service (SMB)

```python
# List SMB shares
{
  "service": "ShareMgmt",
  "method": "getList",
  "params": {
    "start": 0,
    "limit": 25
  }
}

# Get specific share
{
  "service": "ShareMgmt",
  "method": "get",
  "params": {
    "uuid": "share-uuid-here"
  }
}

# Create new share
{
  "service": "ShareMgmt",
  "method": "set",
  "params": {
    "uuid": null,
    "name": "MyShare",
    "sharedfolderref": "folder-uuid",
    "readonly": false
  }
}
```

#### 4. Services Service

```python
# Get status of all services
{
  "service": "Services",
  "method": "getStatus",
  "params": {}
}

# Response:
{
  "smb": {
    "enabled": true,
    "running": true
  },
  "nfs": {
    "enabled": true,
    "running": false
  }
}

# Start/stop services
{
  "service": "Services",
  "method": "start",
  "params": {"id": "smb"}
}
```

#### 5. Network Service

```python
# Get network interfaces
{
  "service": "Network",
  "method": "getInterfaceList",
  "params": {}
}

# Get DNS settings
{
  "service": "Network",
  "method": "getDNSNameServers",
  "params": {}
}
```

#### 6. LogFile Service

```python
# Get system logs
{
  "service": "LogFile",
  "method": "getList",
  "params": {
    "start": 0,
    "limit": 50
  }
}

# Get specific log content
{
  "service": "LogFile",
  "method": "getContent",
  "params": {
    "id": "syslog",
    "start": 0,
    "limit": 100
  }
}
```

### Building Your RPC Client

```python
import requests
from typing import Dict, Any

class OMVRPCClient:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.auth = (username, password)
        self.endpoint = f"http://{host}/rpc"
    
    def call(self, service: str, method: str, params: Dict = None) -> Dict[str, Any]:
        """Make an RPC call to OMV"""
        payload = {
            "service": service,
            "method": method,
            "params": params or {},
            "options": None
        }
        
        response = requests.post(
            self.endpoint,
            auth=self.auth,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("error"):
            raise Exception(f"RPC Error: {data['error']}")
            
        return data.get("response")

# Usage
omv = OMVRPCClient("192.168.1.100", "admin", "password")

# Get system info
info = omv.call("System", "getInformation")
print(f"Hostname: {info['hostname']}")

# List filesystems
filesystems = omv.call("FileSystemMgmt", "getList", {
    "start": 0,
    "limit": 25
})
for fs in filesystems['data']:
    print(f"Device: {fs['devicefile']}, Used: {fs['used']}")
```

### Discovering Available Methods

**Method 1: Browser Dev Tools**

1. Open OMV web interface
2. Open dev tools (F12)
3. Go to Network tab
4. Click around in OMV
5. Watch the RPC calls being made

**Method 2: OMV Source Code**

```bash
ls /usr/share/openmediavault/engined/rpc/
# filesystemmgmt.inc
# sharemgmt.inc
# network.inc
# system.inc
```

### Why RPC is Critical for Your Project

**OMV RPC is the data source** for everything:

1. **System State** → Context for LLM
2. **Service Status** → Diagnostic capabilities
3. **Configuration** → Understanding setup
4. **Logs** → Error pattern matching
5. **Metrics** → Trend analysis

**Without RPC, you have no data to work with.** It's the foundation.

### Practical Examples

#### 1. Real-Time State Collection

```python
def collect_system_state(omv):
    """Gather comprehensive system state"""
    return {
        'system': omv.call('System', 'getInformation'),
        'filesystems': omv.call('FileSystemMgmt', 'getList'),
        'services': omv.call('Services', 'getStatus'),
        'network': omv.call('Network', 'getInterfaceList'),
        'shares': omv.call('ShareMgmt', 'getList'),
        'timestamp': datetime.now().isoformat()
    }
```

#### 2. Context for LLM

```python
def build_llm_context(omv):
    """Build context for LLM query"""
    state = collect_system_state(omv)
    
    context = f"""
Current OMV System State:
- Hostname: {state['system']['hostname']}
- Uptime: {state['system']['uptime']}
- Memory: {state['system']['memUsed']}/{state['system']['memTotal']}

Filesystems ({len(state['filesystems']['data'])} total):
"""
    
    for fs in state['filesystems']['data']:
        context += f"  - {fs['devicefile']}: {fs['used']} used\n"
    
    return context
```

#### 3. Diagnostic Commands

```python
def diagnose_smb_issue(omv):
    """Run SMB diagnostics"""
    diagnostics = {}
    
    # Check service status
    services = omv.call('Services', 'getStatus')
    diagnostics['smb_running'] = services['smb']['running']
    
    # List shares
    shares = omv.call('ShareMgmt', 'getList')
    diagnostics['share_count'] = shares['total']
    
    # Get recent logs
    logs = omv.call('LogFile', 'getContent', {
        'id': 'syslog',
        'start': 0,
        'limit': 100
    })
    diagnostics['recent_errors'] = [
        line for line in logs 
        if 'smb' in line.lower() and 'error' in line.lower()
    ]
    
    return diagnostics
```

### Common Pitfalls

**1. Paginated Results**

```python
# Wrong: Only gets first 25
result = omv.call('FileSystemMgmt', 'getList', {'start': 0, 'limit': 25})

# Right: Get all
def get_all_filesystems(omv):
    all_fs = []
    start = 0
    limit = 25
    
    while True:
        result = omv.call('FileSystemMgmt', 'getList', {
            'start': start,
            'limit': limit
        })
        all_fs.extend(result['data'])
        
        if len(all_fs) >= result['total']:
            break
        start += limit
    
    return all_fs
```

**2. UUID References**

```python
# Wrong: Can't look up by name
share = omv.call('ShareMgmt', 'get', {'name': 'MyShare'})  # Error!

# Right: List all, find by name, use UUID
shares = omv.call('ShareMgmt', 'getList')
my_share = next(s for s in shares['data'] if s['name'] == 'MyShare')
details = omv.call('ShareMgmt', 'get', {'uuid': my_share['uuid']})
```

### Security Considerations

**1. Never Hardcode Credentials**

```python
# ❌ NO
password = "mysecretpassword"

# ✅ YES
import os
password = os.environ.get('OMV_RPC_PASSWORD')
```

**2. Use HTTPS if Remote**

```python
self.endpoint = f"https://{host}/rpc"  # Not http://
```

**3. Rate Limiting**

```python
from functools import wraps
import time

def rate_limit(calls_per_second=2):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

class
```