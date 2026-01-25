# Which Way? AI-to-AI Communication Comparison

**Date:** 2026-01-25
**Purpose:** Compare two approaches for AI-to-AI communication in ExFrame constellation

---

## Overview

This document compares two approaches to enabling AI-to-AI communication for the ExFrame constellation:

1. **Simple HTTP API** (Current implementation - `/api/kilo/communicate`)
2. **Claude Bridge Architecture** (Proposed in "AI-to-AI Communication Protocol for Claude Code.md")

---

## Approach 1: Simple HTTP API (Current)

### Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  ExFrame A      │◄───────►│  ExFrame B      │
│  localhost:3000 │         │  192.168.1.101  │
└─────────────────┘         └─────────────────┘
        │                           │
        │   POST /api/kilo/communicate
        │   GET /api/kilo/messages
        │   DELETE /api/kilo/messages
        │                           │
        └───────────────────────────┘
```

### How It Works

**Sending a message:**
```bash
# From any HTTP client (curl, Python requests, etc.)
curl -X POST http://192.168.1.101:3000/api/kilo/communicate \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "sender_id": "instance-a"}'
```

**Retrieving messages:**
```bash
# Get all received messages
curl http://localhost:3000/api/kilo/messages
```

### Implementation

```python
# In generic_framework/api/app.py

kilo_router = APIRouter(prefix="/api/kilo")
kilo_messages: List[Dict[str, Any]] = []

@kilo_router.post("/communicate")
async def send_message(msg: KiloMessage):
    msg_dict = msg.dict()
    msg_dict["timestamp"] = datetime.utcnow().isoformat()
    msg_dict["id"] = len(kilo_messages)
    kilo_messages.append(msg_dict)
    return KiloMessageResponse(status="received", ...)

@kilo_router.get("/messages")
async def get_messages():
    return {"messages": kilo_messages, "count": len(kilo_messages)}
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Complexity** | Very simple - ~50 lines of code |
| **Storage** | In-memory (lost on restart) |
| **Discovery** | Manual (need to know IP:port) |
| **Message Types** | Unstructured text |
| **Delivery** | No guarantees |
| **Authentication** | None |
| **Dependencies** | FastAPI (already in use) |

### Pros

- ✅ Simple to understand
- ✅ Works immediately
- ✅ No additional infrastructure
- ✅ Easy to debug
- ✅ Minimal code to maintain

### Cons

- ❌ Messages lost on restart
- ❌ No delivery guarantees
- ❌ No authentication/security
- ❌ Manual peer discovery
- ❌ No structured message types
- ❌ No conversation tracking
- ❌ Claude Code can't directly use it

---

## Approach 2: Claude Bridge Architecture

### Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Claude Code A  │         │  Claude Code B  │
│  (VS Code/CLI)  │         │  (VS Code/CLI)  │
└────────┬────────┘         └────────┬────────┘
         │                          │
         │  ← Claude Bridge →       │  ← Claude Bridge →
         │  (Python Script)         │  (Python Script)
         │                          │
    ┌────▼────────┐            ┌────▼────────┐
    │  Mini Server │            │  Mini Server │
    │  Port 8001   │            │  Port 8001   │
    └────┬────────┘            └────┬────────┘
         │                          │
         │   Register + Send        │
         │   /api/ai/*              │
         └──────────┬───────────────┘
                    │
         ┌──────────▼────────────┐
         │   ExFrame Host        │
         │   (Message Broker)    │
         │   /api/ai/register     │
         │   /api/ai/send        │
         │   /api/ai/receive     │
         │   /api/ai/peers       │
         └───────────────────────┘
```

### How It Works

**The Claude Bridge is NOT a Claude feature.** It's a custom Python script you write that:

1. **Runs as a separate process** alongside Claude Code
2. **Spawns a mini HTTP server** (using FastAPI/Uvicorn) on its own port
3. **Registers itself** with ExFrame as an "AI instance"
4. **Watches a message queue** and processes incoming messages
5. **Claude Code CLI** talks to the bridge, the bridge talks to ExFrame

### Flow Breakdown

```
┌──────────────┐
│ Claude Code  │ ← You're chatting here
│  (VS Code)   │
└──────┬───────┘
       │ "Ask the remote AI about X"
       │
       ▼
┌─────────────────────────────────────────┐
│  Bridge Script (claude_code_ai_bridge.py)│
│  ┌─────────────────────────────────────┐│
│  │ 1. register()                       ││
│  │    → POST /api/ai/register          ││
│  │    → "I am claude-dev, listen on    ││
│  │       http://localhost:8001"         ││
│  ├─────────────────────────────────────┤│
│  │ 2. receive_messages()               ││
│  │    → Spawns FastAPI on port 8001    ││
│  │    → Endpoint: /ai/receive          ││
│  ├─────────────────────────────────────┤│
│  │ 3. process_messages()               ││
│  │    → Watches asyncio queue          ││
│  │    → Handles message types          ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────────┐
│  ExFrame     │    │  ExFrame Remote  │
│  localhost:  │    │  192.168.1.101   │
│  3000        │    │                  │
└──────────────┘    └──────────────────┘
```

### Implementation

```python
# claude_code_ai_bridge.py (separate file you create)

class ClaudeCodeAIBridge:
    def __init__(self, instance_id: str, exframe_host: str, listen_port: int):
        self.instance_id = instance_id
        self.exframe_host = exframe_host
        self.listen_port = listen_port
        self.message_queue = asyncio.Queue()

    async def register(self):
        """Tell ExFrame we exist"""
        await httpx.post(f"{exframe_host}/api/ai/register", json={
            "instance_id": self.instance_id,
            "endpoint": f"http://localhost:{self.listen_port}",
            "capabilities": ["code_analysis", "pattern_creation"]
        })

    async def send_to_peer(self, to_instance: str, message_type: str, payload: dict):
        """Send message through ExFrame to another AI"""
        await httpx.post(f"{exframe_host}/api/ai/send", json={
            "from_instance": self.instance_id,
            "to_instance": to_instance,
            "type": message_type,
            "payload": payload
        })

    async def receive_messages(self):
        """Start mini web server to receive messages"""
        app = FastAPI()

        @app.post("/ai/receive")
        async def receive(message: dict):
            await self.message_queue.put(message)
            return {"received": True}

        # Run this server on port 8001
        await uvicorn.serve(app, host="0.0.0.0", port=self.listen_port)

    async def process_messages(self):
        """Handle messages from the queue"""
        while True:
            message = await self.message_queue.get()
            if message['type'] == 'query':
                # Handle query...
            elif message['type'] == 'pattern_request':
                # Handle pattern request...
```

### What's Happening (Detailed)

1. **You start the bridge script** (separate from ExFrame, separate from Claude Code)
2. **Bridge registers with ExFrame** - "I'm here, send messages to http://localhost:8001"
3. **Bridge starts its own server** on port 8001
4. **When someone sends a message to this AI**:
   - They call `/api/ai/send` on ExFrame
   - ExFrame forwards it to `http://localhost:8001/ai/receive`
   - The bridge's server receives it and puts it in a queue
5. **Bridge processes the queue** and takes action
6. **Claude Code CLI** can be configured to use the bridge's endpoints

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Complexity** | High - ~300+ lines of bridge code + ~200 lines API |
| **Storage** | In-memory queue in bridge process |
| **Discovery** | Automatic via `/api/ai/register` |
| **Message Types** | Structured (query, response, pattern_request, etc.) |
| **Delivery** | Best effort (no retry mechanism) |
| **Authentication** | Optional HMAC signing |
| **Dependencies** | FastAPI, Uvicorn, httpx, asyncio |
| **Processes** | ExFrame + Bridge per AI instance |

### Pros

- ✅ Claude Code can participate directly
- ✅ Structured message types
- ✅ Peer discovery
- ✅ Capability declarations
- ✅ Message type routing
- ✅ Per-AI message queue
- ✅ Potential for async processing

### Cons

- ❌ Much more complex
- ❌ Requires separate bridge process per AI
- ❌ More moving parts to debug
- ❌ Messages still lost on restart
- ❌ Claude Bridge is NOT a built-in Claude feature (you write it)
- ❌ Still no delivery guarantees
- ❌ Requires Claude Code CLI integration

---

## The Claude Bridge Question

### Q: Is the Claude Bridge a Claude feature?

**A: NO.**

The "Claude Bridge" is **NOT** a feature of Claude or Claude Code. It is a **custom Python script** that you (or someone) would need to write.

**What it is:**
- A Python class `ClaudeCodeAIBridge` that you implement
- It uses standard Python libraries: FastAPI, Uvicorn, httpx, asyncio
- It's essentially a **proxy/adapter** between Claude Code CLI and ExFrame

**What it does:**
- Runs as a separate process
- Spawns a mini HTTP server
- Forwards HTTP requests between Claude Code and ExFrame
- Manages a message queue

**Why the confusion?**
The name "Claude Bridge" makes it sound like an official feature. But it's just a descriptive name for a custom adapter pattern. You could call it "AI Mesh Bridge" or "ExFrame Adapter" and it would be less confusing.

**Analogy:**
```
Claude Code CLI = A fancy phone
ExFrame = The telephone network
Claude Bridge = A custom adapter box you built to connect the phone to the network
```

The phone manufacturer (Anthropic) doesn't provide the adapter - you build it yourself using standard networking protocols.

---

## Side-by-Side Comparison

### Message Sending

**Simple HTTP:**
```python
import requests

response = requests.post(
    "http://remote:3000/api/kilo/communicate",
    json={"message": "Hello!", "sender_id": "me"}
)
```

**Claude Bridge:**
```python
# In bridge script
await bridge.send_to_peer(
    to_instance="remote-ai",
    message_type="query",
    payload={"query": "Hello!"}
)

# Which calls
await httpx.post("http://localhost:3000/api/ai/send", json={
    "from_instance": "me",
    "to_instance": "remote-ai",
    "type": "query",
    "payload": {"query": "Hello!"}
})

# Which calls
await httpx.post("http://remote:8001/ai/receive", json=...)

# Which is received by the remote's bridge server
```

### Complexity Comparison

| Metric | Simple HTTP | Claude Bridge |
|--------|-------------|---------------|
| **Lines of Code** | ~50 | ~500+ |
| **Number of Processes** | 1 (ExFrame) | 3+ (ExFrame + 2+ bridges) |
| **HTTP Endpoints** | 3 | 8+ |
| **External Dependencies** | 0 (uses FastAPI) | 3 (httpx, uvicorn, asyncio) |
| **Configuration Files** | 0 | 1 (YAML) |
| **Processes to Launch** | 1 | 1 + N (N = number of AIs) |

---

## Recommendation

### Use Simple HTTP If:

- You want something that works now
- You don't need Claude Code CLI integration
- You're okay with manual IP:port configuration
- You value simplicity over structure
- You're building a proof of concept
- You want to minimize debugging surface area

### Use Claude Bridge If:

- You need Claude Code CLI to directly participate
- You want structured message types
- You want automatic peer discovery
- You need per-AI message queues
- You're building a production constellation
- You're comfortable maintaining more infrastructure

### Hybrid Approach:

**Use Simple HTTP now, add Bridge later if needed.**

The Simple HTTP approach doesn't prevent you from adding the Bridge architecture later. You could:
1. Start with `/api/kilo/communicate` for testing
2. Build out the full `/api/ai/*` endpoints when you have multiple AIs
3. Add the bridge script when Claude Code CLI integration becomes necessary

---

## Key Takeaway

The Claude Bridge is a **custom adapter pattern**, not a Claude feature. It adds structure and Claude Code CLI integration at the cost of significant complexity. For most use cases, the Simple HTTP approach is sufficient and much easier to understand and maintain.
