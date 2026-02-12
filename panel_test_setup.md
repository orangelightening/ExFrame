# Panel Discussion Test Setup

## Domains to Create

### 1. ai_panel - Panel/Organizer
**Persona:** Librarian
**Temperature:** 0.6
**Description:** Orchestrates multi-domain AI panel discussions
**Role:**
- Receives discussion topics
- Presents topics to Panelist Alpha
- Collects responses from all participants
- Organizes input for Judge domain
**Instructions:** "You are the Panel coordinator. Organize discussions, present clearly to Judge, and track all panelist responses."

### 2. panelist_alpha - Creative Voice
**Persona:** Poet
**Temperature:** 0.8
**Description:** Creative contrarian voice in AI panel discussions
**Role:**
- Receive topics from Panel
- Provide creative, contrarian perspective
- Challenge assumptions
- Take provocative positions when appropriate
**Instructions:** "You are the creative voice in panel discussions. Challenge conventional thinking, propose wild ideas, and argue from unique perspectives. Don't be afraid to be contrarian."

### 3. ai_judge - Synthesizer with Dynamic Persona
**Persona:** Dynamic (see below)
**Temperature:** 0.7
**Description:** Consolidates multi-domain input and makes decisions
**Dynamic Behavior:**
- **IF QUERY IS EXFRAME-RELATED:** Act as Librarian with domain expertise. Use ExFrame documentation. Cite sources. Be thorough and precise.
- **OTHERWISE (DIY, COOKING, ETC.):** Act as Researcher with web search. Be creative, opinionated, synthesize web sources. Take strong positions.
**Instructions:** "You are the Judge for AI panel discussions. Analyze all panelist responses along with the Panel organizer's input. Make fair, thoughtful decisions. Write your decision to /app/project/panel_decisions.md in markdown format.

**Output File:** `/app/project/panel_decisions.md`

## Validation Results

### ✅ Web Search CONFIRMED WORKING

**Tested:** Cooking domain web search for "How do I bake chicken breast?"
**Result:**
- ✅ DuckDuckGo search + full page fetching working
- ✅ Fetched 3 recipe pages
- ✅ Detailed step-by-step baking guide with sources
- ✅ Researcher persona functioning correctly
- ✅ Confidence: 0.7 (moderate)

**Conclusion:** Cooking and DIY domains (Researcher personas) have FULL web search capability. No new test domains needed!

### Correct Test Approach: Use Existing Domains

**✅ DON'T create empty test domains** (Panel, Panelist Alpha, Judge)
- ❌ They have NO conversation history (empty domain_log.md)

**✅ INSTEAD use EXISTING RICH domains:**
1. **cooking** (Researcher) - Already has recipes, Q&A, techniques
2. **diy** (Researcher) - Already has projects, troubleshooting
3. **exframe** (Librarian) - Already has architecture, how-to guides

**These domains have:**
- ✅ Rich conversation logs (thousands of Q&A pairs)
- ✅ Deep context and expertise
- ✅ Emergent knowledge from real use

**For panel discussion:**
- Configure **Judge domain** to use these existing logs
- Judge reads domain_log.md files
- Synthesizes from ACTUAL multi-domain conversations
- Output file: `/app/project/panel_decisions.md` (accessible to all)

---

## Test Plan: Multi-Domain Dinner Party

### Setup (3 Existing Domains)

1. **Panel** (Librarian) - Orchestrates: "Organize a discussion about [topic]"
2. **Panelist Alpha** (Poet) - Receives: "What's your take on [topic]?"
3. **Judge** (Dynamic) - Reads all responses, consolidates, decides

### Test Topics

**Via cooking domain (Researcher):**
- "BBQ ribslow recipe" (will fetch actual recipes, cite sources)
- "Internal cooking temperature: 400°F vs 375°F" (temperature debate)

**Judge output:** `/app/project/panel_decisions.md`

1. **Panel Domain** receives query topic
2. **Panel** queries **Panelist Alpha**: "What's your take on [topic]?"
3. **Panel** queries **ai_judge**: "Consolidate all responses and decide"
4. **ai_judge**:
   - Analyzes query topic
   - Selects appropriate persona (Librarian/Researcher)
   - Synthesizes all responses
   - Writes decision to `/app/project/panel_decisions.md`
5. **All domains** can read the markdown file to see outcome

## Success Criteria

- [ ] Panel successfully presents topics
- [ ] Panelist Alpha provides creative responses
- [ ] Judge switches personas based on topic
- [ ] Decision written to markdown file
- [ ] All 3 domains can access the decision file
- [ ] Dynamic persona switching works (ExFrame vs Researcher)
