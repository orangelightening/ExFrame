# Three-Way AI Communication Protocol

## Problem
Two AIs need to collaborate directly, with a human coordinator, not requiring manual message relay.

## Solution: Shared Communication File System

### Roles
```
┌─────────────────────────────────────────────────────────┐
│  Peter (Coordinator)                                    │
│  - Full access to all systems                           │
│  - Provides direction and decisions                    │
│  - Resolves conflicts                                   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
┌────────▼────────┐     ┌────────▼────────┐
│ Commentator AI   │     │ Builder AI      │
│ (Jan.ai shell)   │     │ (Claude Code)   │
│                  │     │ (Konsole)       │
│ - Designs/Plans  │     │ - Code          │
│ - Guidance       │     │ - Tests         │
│ - Reviews        │     │ - Implementation │
│ - note-vault/    │     │ - eeframe/      │
└──────────────────┘     └─────────────────┘
```

### Communication Hub
```
/home/peter/development/eeframe/
└── ai-communications/
    ├── messages.json           # All messages between AIs
    ├── tasks.yaml             # Task tracking and assignments
    ├── decisions.yaml          # Peter's decisions and approvals
    ├── reviews/               # AI-to-AI reviews
    └── status.yaml            # Current system status
```

---

## Message Protocol

### Message Structure
```json
{
  "id": "msg-001",
  "from": "commentator",
  "to": "builder",
  "timestamp": "2026-01-04T15:30:00Z",
  "type": "request|response|comment|question",
  "topic": "directory-structure",
  "content": "Please create the meta_expertise directory...",
  "priority": "high|medium|low",
  "status": "pending|acknowledged|completed"
}
```

### Message Types
- **request**: One AI asking another to do something
- **response**: Response to a request
- **comment**: Feedback, suggestions, observations
- **question**: Asking for clarification or input
- **decision**: Peter's final decision on something
- **report**: Builder reporting completion

---

## Work Flow

### Normal Flow (No Relay Needed)
```
1. Commentator reads designs in note-vault/
2. Commentator writes request to messages.json:
   {
     "from": "commentator",
     "to": "builder",
     "content": "Create meta_expertise directories...",
     "status": "pending"
   }

3. Builder reads messages.json, sees request
4. Builder marks "status": "acknowledged"
5. Builder does the work
6. Builder updates messages.json:
   {
     "status": "completed",
     "result": "Created 7 directories..."
   }

7. Commentator reads messages.json, sees completion
8. Commentator writes review to reviews/
9. Peter reads reviews, provides approval
```

### Peter's Role (Not Relay)
```
- High-level direction: "Build the scanner this way"
- Decision making: "Go with counter-proposal"
- Approval: "Looks good, proceed to next task"
- Conflict resolution: When AIs disagree
- Quality check: Review final results

NOT:
- Relaying "AI A said X" to "AI B"
- Copy-pasting messages between windows
```

---

## File-Based Communication

### ai-communications/messages.json
```json
{
  "messages": [
    {
      "id": "msg-001",
      "from": "commentator",
      "to": "builder",
      "timestamp": "2026-01-04T15:30:00Z",
      "type": "request",
      "topic": "directory-structure",
      "content": "Please create src/meta_expertise/ with these subdirectories...",
      "priority": "high",
      "status": "completed",
      "response": "Done. Created 7 directories.",
      "completed_at": "2026-01-04T15:35:00Z"
    },
    {
      "id": "msg-002",
      "from": "builder",
      "to": "commentator",
      "timestamp": "2026-01-04T15:36:00Z",
      "type": "comment",
      "topic": "directory-structure",
      "content": "I added a 'utils' directory that wasn't in the plan. Needed for helper functions.",
      "status": "acknowledged"
    }
  ]
}
```

### ai-communications/tasks.yaml
```yaml
current_task:
  week: 1
  day: 1
  phase: "migration-backup"
  status: "in_progress"
  assigned_to: "builder"
  description: "Create legacy backup of omv_copilot"

active_sprint:
  week: 1
  goal: "Week 1: Migration & OMV Domain Setup"
  tasks:
    - name: "Legacy backup"
      status: "in_progress"
      assigned_to: "builder"
    - name: "Migrate OMV patterns"
      status: "pending"
      assigned_to: "builder"
    - name: "Build knowledge graph"
      status: "pending"
      assigned_to: "builder"
    - name: "Create API layer"
      status: "pending"
      assigned_to: "builder"
```

### ai-communications/decisions.yaml
```yaml
pending_decisions:
  - id: "dec-001"
    topic: "Starting domains"
    options:
      - "Counter-proposal (procedural domains)"
      - "Folk proposal (cultural domains)"
    status: "resolved"
    decision: "Counter-proposal"
    decided_by: "peter"
    timestamp: "2026-01-04T15:00:00Z"
    notes: "Focus on scanner tool, folk domains in Phase 2"
```

---

## Quick Commands

### For Builder AI (Konsole)
```bash
# Check for new messages
cat ai-communications/messages.json | grep '"status": "pending"'

# Acknowledge a request
# (edit messages.json, change status to "acknowledged")

# Mark task complete
# (edit messages.json, change status to "completed", add response)

# Check current task
cat ai-communications/tasks.yaml | grep -A 10 "current_task:"

# Update task status
# (edit tasks.yaml, change status and move to next task)
```

### For Commentator AI (Jan.ai)
```bash
# Check completed work
cat ai-communications/messages.json | grep '"status": "completed"'

# Write review
echo "Review of directory structure..." > ai-communications/reviews/msg-001.md

# Check decisions from Peter
cat ai-communications/decisions.yaml

# Suggest next step
# (append to messages.json with new request)
```

### For Peter
```bash
# View all recent communication
cat ai-communications/messages.json | tail -50

# Check current status
cat ai-communications/tasks.yaml

# Make a decision
# (edit decisions.yaml, add or update decision)

# View reviews
ls -la ai-communications/reviews/
```

---

## Communication Rules

### Commentator AI Guidelines
1. Read designs in note-vault/
2. Write requests to messages.json
3. Wait for builder to complete
4. Read results and write reviews
5. Suggest next steps
6. Ask Peter for decisions when needed

### Builder AI Guidelines
1. Read messages.json for requests
2. Acknowledge new requests (mark status)
3. Do the work
4. Update messages.json with results
5. Update tasks.yaml when moving to next task
6. Ask clarifying questions in messages.json

### Peter Guidelines
1. Check ai-communications/ directory
2. Provide high-level direction
3. Make decisions on requests.yaml
4. Review completed work
5. Approve or request changes
6. Resolve AI disagreements

---

## Getting Started

### Step 1: Initialize Communication
```bash
# Create the communications directory
mkdir -p /home/peter/development/eeframe/ai-communications/reviews

# Initialize messages.json
cat > /home/peter/development/eeframe/ai-communications/messages.json << 'EOF'
{
  "messages": []
}
EOF

# Initialize tasks.yaml
cat > /home/peter/development/eeframe/ai-communications/tasks.yaml << 'EOF'
current_task:
  week: 1
  day: 1
  phase: "communication-setup"
  status: "in_progress"
  assigned_to: "builder"
  description: "Initialize AI communication protocol"

active_sprint:
  week: 1
  goal: "Week 1: Migration & OMV Domain Setup"
  tasks:
    - name: "Initialize communication"
      status: "in_progress"
      assigned_to: "builder"
    - name: "Legacy backup"
      status: "pending"
      assigned_to: "builder"
    - name: "Migrate OMV patterns"
      status: "pending"
      assigned_to: "builder"
EOF

# Initialize decisions.yaml
cat > /home/peter/development/eeframe/ai-communications/decisions.yaml << 'EOF'
pending_decisions: []
resolved_decisions: []
EOF
```

### Step 2: First Request
```bash
# Commentator AI writes first request
# (add to messages.json)

# Builder AI reads and acknowledges
# Builder does the work
# Builder updates messages.json with completion

# Commentator AI reads and reviews
# Peter reviews and approves
```

---

## Example Session

### 1. Commentator AI (Jan.ai)
```json
// In messages.json
{
  "id": "msg-003",
  "from": "commentator",
  "to": "builder",
  "timestamp": "2026-01-04T16:00:00Z",
  "type": "request",
  "topic": "legacy-backup",
  "content": "Create legacy backup: cp -r src/omv_copilot src/omv_copilot_legacy",
  "priority": "high",
  "status": "pending"
}
```

### 2. Builder AI (Konsole)
```bash
# Reads messages.json, sees pending request
# Updates to "acknowledged"
# Executes: cp -r src/omv_copilot src/omv_copilot_legacy
# Updates messages.json:
{
  "status": "completed",
  "response": "Legacy backup created. 24 pattern files backed up.",
  "completed_at": "2026-01-04T16:02:00Z"
}
# Updates tasks.yaml to next task
```

### 3. Commentator AI (Jan.ai)
```bash
# Reads messages.json, sees completion
# Writes review:
echo "Backup looks correct. All pattern files copied. Ready to proceed with migration." > ai-communications/reviews/msg-003.md
```

### 4. Peter
```bash
# Reads review, approves:
cat ai-communications/reviews/msg-003.md
# "Looks good, continue"
# Commentator writes next request
```

---

## Benefits

✅ No manual relay required
✅ Asynchronous communication
✅ Full audit trail
✅ Peter stays coordinator, not messenger
✅ AIs can work at their own pace
✅ Easy to track progress
✅ Simple file-based system
✅ No network/API complexity
✅ Both AIs stay in their optimal environment

---

## Summary

The three of us now have a shared communication protocol where:
- **Commentator** provides guidance from note-vault/
- **Builder** implements in eeframe/
- **Peter** coordinates and decides
- All communication happens through shared files in ai-communications/
- No message relay needed!

Let's start using this for the Expertise Scanner build!
