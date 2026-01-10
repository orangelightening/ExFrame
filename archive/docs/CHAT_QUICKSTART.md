# Three-Way Chat - Quick Start Guide

## 🎯 What Is It?

A real-time chat system where Peter, Commentator AI, and Builder AI can all see each other's messages in sync - no manual relay needed!

---

## 🚀 Quick Start (5 Minutes)

### 1. Start the Chat Server
```bash
cd /home/peter/development/eeframe

# Start the FastAPI chat server
uvicorn src.chat_api:app --reload --port 8888

# Keep this terminal running!
```

### 2. Open the Chat Interface
```bash
# In another terminal, start React frontend
cd frontend
npm start

# Browser opens to http://localhost:3000
```

### 3. Navigate to Chat
```
Open: http://localhost:3000/chat
```

### 4. Send Your First Message!
Type in the chat box: "Hello everyone!" and press Send.

---

## 🤖 How AIs Send Messages

### Commentator AI (in Jan.ai terminal)
```bash
cd /home/peter/development/eeframe
python src/meta_expertise/utils/send_chat.py commentator "I've reviewed the code, looks good!"
```

### Builder AI (in Konsole)
```bash
cd /home/peter/development/eeframe
python src/meta_expertise/utils/send_chat.py builder "Task complete: Backup done"
```

### Get All Messages
```bash
python src/meta_expertise/utils/send_chat.py get
```

---

## 💬 Message Types

| Type | Icon | Usage | Example |
|------|------|-------|---------|
| `chat` | 💬 | General conversation | "Let's discuss next step" |
| `code` | 💻 | Code snippets | "def backup_legacy():" |
| `review` | 📋 | Architecture review | "The pattern structure looks good" |
| `decision` | ✅ | Project decisions | "Decision: Use snake_case" |
| `question` | ❓ | Questions | "How should we handle this?" |
| `blocker` | 🚫 | Blocking issues | "BLOCKER: Need API key" |

### Sending Different Types

```bash
# Send a review
python send_chat.py commentator "Good architecture decision" review

# Send code
python send_chat.py builder "def migrate():" code

# Send a blocker
python send_chat.py builder "BLOCKER: Need access to API" blocker
```

---

## 📋 Example Collaboration

```
Peter:          "Start Week 1 Day 1: Create legacy backup"
Builder AI:      "Starting backup now..."
Builder AI:      "✓ Legacy backup complete: omv_copilot_legacy/ created"
Commentator AI:  "Reviewing structure... Looks good! Suggest adding README.md"
Peter:           "Good idea, add the README.md"
Builder AI:      "Adding README.md..."
Builder AI:      "✓ README.md created"
Commentator AI:  "Perfect! Ready for Day 1.2: Migrate OMV patterns"
```

All messages appear in real-time in the browser chat window!

---

## 🎨 What You'll See

### In the Browser (http://localhost:3000/chat)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Three-Way Chat                              ● Connected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

15:30 | Peter 💬
       Start Week 1 Day 1

15:31 | Builder AI 💬
       Starting backup now...

15:32 | Builder AI ✅
       ✓ Legacy backup complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type message...                            [Send]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Color Coding
- **Peter** 🟢 Green
- **Commentator AI** 🔵 Blue
- **Builder AI** 🟠 Orange

---

## 🔧 Commands Reference

### Check Chat Health
```bash
curl http://localhost:8888/api/chat/health
```

### Get Messages via API
```bash
curl http://localhost:8888/api/chat/messages
```

### Send Message via API
```bash
curl -X POST http://localhost:8888/api/chat/messages \
  -H "Content-Type: application/json" \
  -d '{"sender": "peter", "content": "Hello"}'
```

---

## 📂 File Structure

```
eeframe/
├── src/
│   ├── chat_api.py                      # FastAPI backend
│   └── meta_expertise/
│       └── utils/
│           └── send_chat.py             # CLI helper
├── frontend/src/
│   ├── components/
│   │   ├── ChatWindow.jsx               # React component
│   │   └── ChatWindow.css              # Styles
│   └── App.jsx                          # Updated with /chat route
└── data/
    └── chat/
        └── messages.json                 # Persistent storage
```

---

## 🎯 How This Helps

### Before
```
Peter: "Tell Builder AI to start backup"
Commentator AI: "Okay, Peter, I'll tell Builder AI"
(Manual relay happens)
Builder AI: "Okay, I'm starting backup now"
```

### After
```
Peter: "Start backup now!"
Builder AI: "Starting backup now!" ← Sees message directly!
```

No relay needed! Everyone sees everything in real-time.

---

## 🆘 Troubleshooting

### Chat won't connect
```bash
# Check if chat server is running
curl http://localhost:8888/api/chat/health

# If not running:
uvicorn src.chat_api:app --reload --port 8888
```

### Messages not appearing
```bash
# Check messages file
cat data/chat/messages.json

# Restart chat server
# (Ctrl+C in chat server terminal, then restart)
```

### AIs can't send messages
```bash
# Test from terminal
python src/meta_expertise/utils/send_chat.py builder "Test message"

# If connection error, check server is running
```

---

## ✨ Ready!

1. Start chat server: `uvicorn src.chat_api:app --reload --port 8888`
2. Start frontend: `cd frontend && npm start`
3. Open: http://localhost:3000/chat
4. Start collaborating!

All three participants can now see each other's messages in real-time! 🎉
