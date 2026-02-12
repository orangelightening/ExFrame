# Human Notes Implementation - Peter Domain

**Status:** ✓ WORKING
**Date:** 2026-02-12
**Implementation:** Poet persona as proxy for human personal journal

---

## What Works

### 1. Journal Entry Mode (no `**` prefix)
**Query:** `hockey game at 3pm tomorrow`
**Response:** `[2026-02-12 09:12:00] hockey game at 3pm tomorrow`

Behavior:
- Timestamps query and echoes back
- No conversation (when prompt is followed)
- Creates permanent journal entry

### 2. Question Mode (`**` prefix)
**Query:** `** what is in fashion`
**Response:** `Pogo is in fashion.`

Behavior:
- Strips `**` prefix
- Reads domain log context
- Answers from journal entries only
- No timestamp added

---

## Technical Implementation

### Domain Configuration
**File:** `universes/MINE/domains/peter/domain.json`

Key settings:
```json
{
  "domain_id": "peter",
  "domain_name": "Peter",
  "persona": "poet",
  "temperature": 0.3,

  "conversation_memory": {
    "enabled": true,
    "mode": "all",
    "max_context_chars": 3000
  }
}
```

### Secretary Prompt
**File:** `universes/MINE/domains/peter/domain_log.md`

The Role Context section contains strict instructions:
- **RULE 1:** `**` prefix → strip and answer from log
- **RULE 2:** Normal queries → timestamp and echo ONLY
- **CRITICAL:** "STOP after responding. DO NOT continue"

### Why Poet Persona Works
The poet persona (void data source) works because:
1. **conversation_memory** includes domain log in LLM context
2. **Low temperature** (0.3) makes it follow instructions strictly
3. **Clear prompt** tells it exactly what to do

The system reads domain_log.md automatically and includes it as context.

---

## Key Learnings

### Prompt Engineering
1. **"STOP after responding"** needed - prevents LLM from continuing conversation
2. **Temperature 0.3** critical for deterministic behavior (0.6 was too creative)
3. **Explicit prohibitions** - "DO NOT ask questions", "DO NOT engage in conversation"
4. **Conversation memory mode "all"** works better than "triggers" (avoids false matches in history)

### Conversation Memory Configuration
- **mode: "all"** - Loads log for every query
- **mode: "triggers"** - Only on trigger phrases (problematic, matches old queries)
- **max_context_chars: 3000** - Limits context to prevent slow processing

### Frontend Issues
- Backend responses complete successfully (200 OK)
- Frontend sometimes hangs on "Processing..."
- **Workaround:** Hard refresh (Ctrl+F5) or check browser console
- **Root cause:** Unknown (needs investigation)

---

## Ready for Panel Testing

All infrastructure is in place:
- ✓ Human Notes (peter domain) working
- ✓ Journal mode operational
- ✓ Question mode operational
- ✓ Domain log reading functional
- ✓ Conversation memory enabled

**Next:** Panel discussion system testing with multiple domains
