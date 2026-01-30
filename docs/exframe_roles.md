# ExFrame Roles and Responsibilities

**Version:** 1.0
**Updated:** 2026-01-29
**Purpose:** Define clear roles, responsibilities, and accountability for maintaining a healthy ExFrame knowledge system

---

## Overview

ExFrame is a collaborative system between humans and AI. Clear role definitions prevent confusion, ensure maintenance tasks are completed, and keep the knowledge base accurate and useful.

**Core Principle:** Each role has specific responsibilities. When everyone understands their role, the system self-heals and improves continuously.

---

## Role: System Owner (User)

### Primary Purpose
Overall system health, direction, and ensuring the self-healing feedback loop works.

### Key Responsibilities

#### Daily
- **Monitor domain performance**: Check that queries are returning relevant results
- **Verify scope boundaries**: Confirm out-of-scope queries are being rejected appropriately
- **Review new patterns**: Assess AI-generated patterns for quality before saving

#### Weekly (Critical)
- **Review contradiction logs**: Check `/app/logs/contradictions/contradictions.log`
  - Focus on HIGH and MEDIUM severity issues
  - Identify documentation inconsistencies
  - Track pattern of contradictions over time
- **Address HIGH severity issues**: These can cause incorrect answers
  - Update documentation to fix contradictions
  - Or save explanation as pattern to provide context
- **Clean up resolved issues**: Clear logs after addressing contradictions

#### Monthly
- **Pattern quality audit**: Review patterns for accuracy, relevance, and completeness
- **Scope boundary tuning**: Adjust `in_scope`/`out_of_scope` lists based on query patterns
- **Domain health check**: Run diagnostics and review system metrics
- **Backup patterns**: Export patterns.json for safekeeping

#### As Needed
- **Create new domains**: When adding new knowledge areas
- **Change domain types**: When use cases evolve
- **Adjust configuration**: Temperature, thresholds, plugins
- **Train Claude Code**: Provide feedback on responses and document patterns

### Tools and Commands

```bash
# Review contradiction logs (weekly)
docker exec eeframe-app cat /app/logs/contradictions/contradictions.log
docker exec eeframe-app grep "\[HIGH\]" /app/logs/contradictions/contradictions.log

# Check domain health
curl http://localhost:3000/api/domains/{domain_id}/health

# View query traces
curl http://localhost:3000/api/traces?domain={domain_id}&limit=20

# Backup patterns
cp universes/MINE/domains/{domain}/patterns.json backups/

# Clear contradiction logs (after addressing)
docker exec eeframe-app sh -c "echo '' > /app/logs/contradictions/contradictions.log"
```

### Success Metrics
- HIGH severity contradictions < 5 per week
- Query confidence scores averaging > 0.6
- Pattern count growing (knowledge accumulation)
- User queries returning relevant results

---

## Role: Claude Code (AI Development Assistant)

### Primary Purpose
Write code, create documentation, fix bugs, extend architecture, and implement new features.

### Key Responsibilities

#### Continuous
- **Write code**: Implement features, fix bugs, refactor
- **Write documentation**: Create and update design docs, API docs, guides
- **Follow patterns**: Use existing code patterns and architecture
- **Test changes**: Verify code works before committing

#### Code Quality
- **Read before writing**: Understand existing code before modifying
- **Fix bugs root cause**: Don't patch symptoms, fix underlying issues
- **Maintain consistency**: Follow established naming, structure, patterns
- **Add comments**: Explain non-obvious code logic

#### Documentation
- **Update design docs**: Keep architecture docs current with changes
- **Document new features**: Add to relevant guides and references
- **Update README**: Reflect new capabilities in main documentation
- **Maintain INDEX.md**: Keep file index accurate for context

#### Architecture
- **Extend don't break**: Add features without breaking existing functionality
- **Respect boundaries**: Maintain separation between plugins, domains, layers
- **Test changes**: Rebuild container and verify domains load
- **Git hygiene**: Write clear commit messages, push regularly

### Daily Workflow

```bash
# 1. Read relevant files before changing
# 2. Make changes
# 3. Rebuild and test
docker compose build --no-cache eeframe-app && docker compose up -d

# 4. Verify domains load
docker logs eeframe-app | grep -i "domain.*load"

# 5. Test queries
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "domain": "exframe"}'

# 6. Commit with clear message
git add .
git commit -m "feat: description of change"
git push origin main
```

### Success Metrics
- Code commits have clear, descriptive messages
- All domains load without errors
- Documentation matches implementation
- Git history shows clean, logical progression

---

## Role: Domain Expert (Specialist Plugin)

### Primary Purpose
Answer questions accurately using domain knowledge, stay within scope boundaries, and provide helpful responses.

### Key Responsibilities

#### Per Query
- **Check scope**: Reject out-of-scope questions immediately
- **Search knowledge**: Find relevant patterns and documents
- **Provide context**: Return relevant information for LLM synthesis
- **Cite sources**: Reference specific documents when making claims

#### Knowledge Management
- **Use patterns first**: Leverage existing domain knowledge
- **Document research**: Search local files before falling back to patterns
- **Return relevant results**: Prioritize fresh document sources over cached patterns
- **Track confidence**: Score results by relevance

#### Scope Enforcement
- **Know boundaries**: Understand what's in-scope vs out-of-scope
- **Reject gracefully**: Provide helpful rejection messages
- **Don't theorize**: Don't answer outside domain expertise
- **Guide users**: Suggest appropriate resources for out-of-scope questions

### Behavior Examples

**Good (In-Scope):**
```
Query: "How do I create a Type 3 domain?"
Response: Provides specific steps with file examples, cites docs
```

**Good (Out-of-Scope):**
```
Query: "How do I use Flask?"
Response: "This question is outside ExFrame's documentation scope.
I can only answer questions about ExFrame's architecture, configuration,
and plugin system. For Flask questions, please use a different domain."
```

**Bad (Out-of-Scope but Answered):**
```
Query: "How do I use Django?"
Response: [Provides Django answer] ← WRONG! Should reject.
```

### Success Metrics
- Out-of-scope queries rejected (not answered)
- In-scope queries return relevant, accurate information
- Confidence scores reflect actual relevance
- Citations reference specific documents

---

## Role: ExFrame Specialist (Type 3 Domain)

### Primary Purpose
Auto-discover documentation, search across all project files, and provide fresh, accurate answers about ExFrame.

### Key Responsibilities

#### Document Discovery
- **Auto-discover files**: Recursively find all documentation files
- **Exclude noise**: Skip .git, __pycache__, node_modules, .env
- **Read everything**: Search across 560+ files in project
- **Provide metadata**: Track total files, matches, relevance scores

#### 3-Stage Search
1. **Research docs** (PRIMARY): Search local markdown/documentation files
2. **Document store** (SECONDARY): External knowledge sources (if configured)
3. **Local patterns** (FALLBACK): Cached patterns when no docs found

#### Citation Requirements
- **Cite files**: Reference specific filenames when making claims
- **Format**: "According to [filename]: [fact]"
- **Be specific**: Reference actual functions, classes, line numbers
- **Acknowledge limits**: State what you checked and what you couldn't find

### Configuration

```json
{
  "research_strategy": {
    "type": "document",
    "base_path": "/app/project",
    "auto_discover": true,
    "file_pattern": "**/*",
    "exclude_patterns": [".git", "__pycache__", "node_modules", ".env"]
  },
  "scope": {
    "enabled": true,
    "in_scope": ["ExFrame architecture", "Plugin system", "Domain types"],
    "out_of_scope": ["Django", "Flask", "React", "Kubernetes"]
  }
}
```

### Success Metrics
- Finds relevant information across 560+ files
- Rejects out-of-scope queries (Django, Flask, etc.)
- Cites specific files and code locations
- Doesn't hallucinate information not in docs

---

## Role: Contradiction Detector

### Primary Purpose
Automatically detect documentation inconsistencies and log them for resolution.

### Key Responsibilities

#### Per Query (Type 3 domains only)
- **Post-response analysis**: Scan all discovered documents after query
- **Find contradictions**: Direct contradictions, ambiguities, outdated info
- **Categorize severity**: HIGH, MEDIUM, LOW based on impact
- **Suggest fixes**: Provide recommendations for each issue

#### Context Awareness
- **Read INDEX.md first**: Understand historical naming (EEFrame → ExFrame)
- **Learn from patterns**: Use saved explanations as context
- **Avoid false positives**: Don't flag intentional internal names
- **Improve over time**: Each iteration should find NEW contradictions

#### Severity Levels

**HIGH - flag_for_immediate_review:**
- Direct contradictions that could cause incorrect answers
- Conflicting factual information
- Incompatible instructions

**MEDIUM - schedule_cleanup:**
- Ambiguous information
- Unclear or confusing documentation
- Answers still valid but could be clearer

**LOW - log_only:**
- Minor terminology inconsistencies
- Formatting issues
- Non-impactful variations

### Log Format

```
[HIGH] Package name mismatch
  Location: README.md vs INSTALL.md
  Issue: README says "exframe" package, INSTALL says "eeframe"
  Impact: Users will install wrong package
  Suggestion: Standardize on "exframe" with historical note
```

### Success Metrics
- Decreasing HIGH/MEDIUM issues over time (feedback loop working)
- New contradictions are different from previous runs (context learned)
- User saves explanations as patterns
- Documentation improves with each iteration

---

## Role: LLM Enricher

### Primary Purpose
Synthesize responses from patterns and documents, providing clear, accurate answers.

### Key Responsibilities

#### Response Generation
- **Use provided context**: Base answers on patterns/documents returned by specialist
- **Cite sources**: Reference specific files when making factual claims
- **Stay in scope**: Don't answer questions outside domain boundaries
- **Be helpful**: Provide clear, actionable information

#### Type 3 (Document Store) Specific
- **Read documents first**: Understand all discovered content
- **Cite filenames**: Use format "According to [filename]: [fact]"
- **Check relevance**: Don't answer if no relevant documents found
- **Acknowledge limits**: State what was searched and what wasn't found

#### Scope Boundaries
- **Respect specialist decision**: If specialist returned out_of_scope=true, don't answer
- **Don't override rejection**: Don't provide answers for rejected queries
- **Help within scope**: Provide thorough answers for in-scope questions

### Example Prompts (Internal)

**Type 3 Document Context:**
```
You are an ExFrame expert. Answer ONLY questions about ExFrame.
Cite specific files using format: "According to [filename]: [fact]"

If no relevant documents found, say: "I don't have information about [query]
in the ExFrame documentation."

SCOPE BOUNDARIES:
IN: ExFrame architecture, plugins, domain types, configuration
OUT: Django, Flask, React, Kubernetes, general Python questions
```

### Success Metrics
- Responses cite specific sources
- Out-of-scope queries are not answered (enriched)
- Relevant information is synthesized accurately
- User questions are answered helpfully

---

## Role: Domain Factory

### Primary Purpose
Generate domain configurations for Types 1-5, providing optimal defaults for each use case.

### Key Responsibilities

#### Single Source of Truth
- **Define type defaults**: Temperature, thresholds, plugins, enrichers
- **Maintain consistency**: All domains of same type have same base config
- **Enable customization**: Allow per-domain overrides after generation

#### Type Configurations
- **Type 1 (Creative)**: High temperature (0.8), creative keywords
- **Type 2 (Knowledge)**: Medium temperature (0.4), pattern display
- **Type 3 (Document Store)**: ExFrame specialist, scope boundaries, document research
- **Type 4 (Analytical)**: Research specialist, web search enabled
- **Type 5 (Hybrid)**: LLM fallback, user confirmation

#### Regeneration
- **On type change**: When domain_type changes, regenerate entire config
- **Preserve identity**: Keep domain_id, domain_name, description, tags
- **Preserve data**: Never touch patterns.json
- **Preserve UI**: Keep ui_config, icons, colors

### Success Metrics
- New domains work out-of-the-box with optimal settings
- Type changes produce predictable, correct configurations
- User can customize after generation
- No hardcoded defaults outside factory

---

## Role: Query Engine

### Primary Purpose
Orchestrate query processing: specialist selection, enrichment pipeline, response building.

### Key Responsibilities

#### Pipeline Orchestration
```
Query → Specialist Selection → Specialist Processing → Enrichers → Response
```

#### Specialist Selection
- **Find best specialist**: Highest confidence score wins
- **Route to specialist**: Pass query with context
- **Handle out_of_scope**: Skip enrichers if specialist rejects query

#### Enricher Pipeline
- **Run enrichers in sequence**: Each enricher can modify response
- **Pass context**: Provide domain, KB, query context to enrichers
- **Handle errors**: Continue pipeline if one enricher fails

#### Response Building
- **Assemble final response**: Combine specialist output with enricher results
- **Add metadata**: Include confidence, patterns_used, trace info
- **Format output**: Apply requested format (markdown, JSON)

### Special Handling

**Out-of-Scope Queries:**
```python
if response_data.get('out_of_scope'):
    # Skip enrichers, return rejection directly
    return {
        'response': response_data.get('response'),
        'out_of_scope': True,
        'confidence': 0.0
    }
```

### Success Metrics
- Queries routed to correct specialist
- Enrichers run in correct order
- Out-of-scope queries don't trigger LLM
- Response includes all relevant metadata

---

## Role Summary Matrix

| Role | Primary Focus | Time Commitment | Key Success Metric |
|------|---------------|-----------------|-------------------|
| **System Owner** | Overall health, direction | Weekly log review | < 5 HIGH issues/week |
| **Claude Code** | Code, docs, architecture | Continuous, as needed | Clean git history |
| **Domain Expert** | Answer questions accurately | Per query | Rejections work correctly |
| **ExFrame Specialist** | Search 560+ docs, cite sources | Per query | Finds relevant info |
| **Contradiction Detector** | Find doc inconsistencies | Per Type 3 query | Issues decrease over time |
| **LLM Enricher** | Synthesize responses | Per query | Citations, scope respected |
| **Domain Factory** | Generate configs | On type change | Consistent defaults |
| **Query Engine** | Orchestrate pipeline | Per query | Correct routing |

---

## Accountability Checklist

### Weekly (System Owner)
- [ ] Review contradiction logs for HIGH/MEDIUM issues
- [ ] Address at least 3 HIGH severity issues
- [ ] Verify scope boundaries are working
- [ ] Check domain health metrics

### Per Commit (Claude Code)
- [ ] Read relevant files before changing
- [ ] Rebuild and test (`docker compose build --no-cache`)
- [ ] Verify domains load without errors
- [ ] Write clear commit message
- [ ] Update relevant documentation

### Per Query (Domain Expert)
- [ ] Check scope boundaries first
- [ ] Search documents before patterns
- [ ] Cite specific sources
- [ ] Don't answer out-of-scope questions

### Per Type 3 Query (Contradiction Detector)
- [ ] Read INDEX.md for context
- [ ] Scan all discovered documents
- [ ] Categorize by severity
- [ ] Log with suggestions

---

## Escalation Paths

**When contradictions keep appearing:**
1. System Owner reviews pattern
2. Claude Code updates documentation
3. Contradiction detector learns from new patterns
4. Repeat until resolved

**When scope boundaries aren't working:**
1. System Owner reviews rejected queries
2. Adjusts in_scope/out_of_scope lists
3. Tests with sample queries
4. Monitors for false positives/negatives

**When code quality degrades:**
1. Claude Code reviews recent commits
2. Identifies problematic changes
3. Refactors to match established patterns
4. Adds tests to prevent regression

---

## Related Documentation

- [README.md](../README.md) - Main documentation
- [PLUGIN_ARCHITECTURE.md](../PLUGIN_ARCHITECTURE.md) - Plugin development
- [docs/architecture/overview.md](architecture/overview.md) - System architecture
- [docs/guides/domain-types.md](guides/domain-types.md) - Domain types reference
