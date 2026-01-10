# Three-Way Chat - CLI Tools

Tools for AI agents to participate in the three-way chat system.

## Quick Start for AI Agents

### Option 1: Simple Send/Receive Scripts

**Read latest messages:**
```bash
python3 scripts/chat_read.py
```

**Send a message as Commentator AI:**
```bash
python3 scripts/chat_send.py commentator "Here is my analysis" review
```

**Send a message as Builder AI:**
```bash
python3 scripts/chat_send.py builder "Here is the code implementation" code
```

### Option 2: Interactive Client

**Start Commentator AI in watch mode:**
```bash
python3 scripts/chat_client.py commentator watch
```

**Start Builder AI in watch mode:**
```bash
python3 scripts/chat_client.py builder watch
```

## For Jan.ai (or any AI with shell access)

Since Jan.ai can execute shell commands/scripts, here's how to integrate:

### Step 1: Read current conversation
```
python3 /home/peter/development/eeframe/scripts/chat_read.py --limit 10
```

### Step 2: Send your response
```
python3 /home/peter/development/eeframe/scripts/chat_send.py commentator "Your message here" chat
```

### Step 3: (Optional) Watch for new messages
```
python3 /home/peter/development/eeframe/scripts/chat_client.py commentator watch
```

## Message Types

| Type | Icon | Usage |
|------|------|-------|
| `chat` | 💬 | General conversation |
| `code` | 💻 | Code snippets |
| `review` | 📋 | Review feedback |
| `decision` | ✅ | Decisions made |
| `question` | ❓ | Questions to resolve |
| `blocker` | 🚫 | Blocking issues |

## Roles

- **peter** - Human director (access via browser at /chat)
- **commentator** - Architecture/Review specialist
- **builder** - Implementation specialist

## Example Session

```bash
# Terminal 1: Commentator AI watching
python3 scripts/chat_client.py commentator watch

# Terminal 2: Builder AI watching
python3 scripts/chat_client.py builder watch

# Browser: Peter at http://localhost:3000/chat
```

When Peter sends a message, both terminals will see it and can respond using:
```bash
python3 scripts/chat_send.py commentator "My response" chat
```
