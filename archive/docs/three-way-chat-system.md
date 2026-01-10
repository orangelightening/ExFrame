# Three-Way Chat System

## Overview

Real-time chat interface for three-way collaboration:
- **Peter** (Human director)
- **Commentator GLM-4.7** (Jan.ai shell, full MCP toolkit)
- **Builder GLM-4.7** (Claude Code agent, eeframe access)

All messages visible in temporal sync - no manual relay needed.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  CHAT WINDOW                                      │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ Peter:            [message 1]               │  │  │
│  │  │ Commentator AI:    [message 2]               │  │  │
│  │  │ Builder AI:       [message 3]               │  │  │
│  │  │ Peter:            [message 4]               │  │  │
│  │  │ ...                                       │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  [Input Box: Type message...] [Send]             │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI)                          │
│  ├── POST /api/chat/messages       (send message)      │
│  ├── GET  /api/chat/messages       (get all messages)  │
│  ├── WS   /api/chat/stream         (real-time updates) │
│  └── messages.json (persistent storage)                │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start Commands

### 1. Initialize directories
```bash
mkdir -p data/chat src/meta_expertise/utils
cat > data/chat/messages.json << 'EOF'
{
  "messages": [],
  "last_updated": "2026-01-04T00:00:00Z"
}
EOF
```

### 2. Start chat server
```bash
cd /home/peter/development/eeframe
uvicorn src.chat_api:app --reload --port 8888
```

### 3. Open chat in browser
```
http://localhost:3000/chat
```

---

## API Endpoints

### Send Message
```bash
curl -X POST http://localhost:8888/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"sender": "peter", "content": "Start Week 1 Day 1"}'
```

### Get All Messages
```bash
curl http://localhost:8888/api/chat/messages
```

### CLI Helper (for AIs)
```bash
# Send message
python src/meta_expertise/utils/send_chat.py builder "Task complete: Backup done"

# Get messages
python src/meta_expertise/utils/send_chat.py get
```

---

## Protocol Examples

### Task Assignment
```
Peter:         "Start Week 1 Day 1: Create legacy backup"
Builder AI:     "Starting backup now..."
Builder AI:     "✓ Legacy backup complete: omv_copilot_legacy/ created"
Commentator AI: "Reviewing structure... Looks good! One suggestion: add README.md"
Peter:          "Good idea, add the README.md"
Builder AI:     "Adding README.md..."
```

### Code Review
```
Builder AI:     "@Commentator I've migrated OMV patterns. Can you review?"
Commentator AI: "Looking at patterns/omv/... Good! Suggest adding metadata field for source tracking."
Builder AI:     "Adding source field to Pattern model..."
```

### Blocking Issue
```
Builder AI:     "BLOCKER: Need decision on pattern naming convention. Should we use snake_case or camelCase?"
Peter:          "Use snake_case for consistency with existing OMV system."
Builder AI:     "Got it! Proceeding with snake_case."
```

---

## Message Types

| Type | Usage | Example |
|------|-------|---------|
| `chat` | General conversation | "Let's discuss the next step" |
| `code` | Code snippets | "def migrate_pattern():" |
| `review` | Architecture/design review | "The pattern structure looks good" |
| `decision` | Project decisions | "Decision: Use snake_case" |
| `question` | Questions | "How should we handle this?" |
| `blocker` | Something blocking progress | "BLOCKER: Need API key" |

---

## Participants

| ID | Name | Color |
|----|------|-------|
| peter | Peter | 🟢 Green |
| commentator | Commentator GLM-4.7 | 🔵 Blue |
| builder | Builder GLM-4.7 | 🟠 Orange |

---

## Next Steps

1. ✅ Create `src/chat_api.py` (FastAPI backend)
2. ✅ Create `src/meta_expertise/utils/send_chat.py` (CLI helper)
3. ⏳ Add `ChatWindow.jsx` to React frontend
4. ⏳ Add route in `frontend/src/App.js`
5. ⏳ Test all three participants sending messages

See detailed implementation in this document.
