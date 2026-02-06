# ExFrame Documentation Annotation System

**Version:** 1.1 (with Obsidian Integration)
**Date:** 2026-02-05
**Purpose:** Inline documentation annotations for historical context, known issues, and superseded systems

> **New:** Obsidian YAML frontmatter integration! See [ANNOTATION_OBSIDIAN_INTEGRATION.md](ANNOTATION_OBSIDIAN_INTEGRATION.md) for complete guide.

---

## Overview

The annotation system allows documentation to be **self-documenting** by embedding context, warnings, and historical notes directly in the files where they matter. This eliminates the need for external tracking systems and ensures context lives with content.

**Dual-Layer System:**
1. **YAML Frontmatter** (Obsidian-compatible) - Document-level metadata
2. **HTML Comments** - Inline section-specific annotations

## Core Principle

> **Context lives with content**

Instead of maintaining separate files to explain contradictions, historical changes, or known issues, we annotate them inline where they occur. The semantic search and LLM enricher automatically discover and use these annotations.

## Philosophy: Optional Enhancement

**Annotations are auxiliary, not mandatory:**

- ✅ **Add when valuable** - Historical context, known issues, clarifications that help understanding
- ✅ **Skip when obvious** - Don't annotate things that are already clear
- ✅ **No enforcement** - Missing annotations are not a problem
- ✅ **Gradual adoption** - Add annotations as you update docs, not in batch operations
- ✅ **Not sticky** - Don't let annotation requirements slow down documentation updates

**When to annotate:**
- Explaining non-obvious historical decisions
- Marking superseded systems during migrations
- Documenting known contradictions that can't be immediately fixed
- Providing context that prevents future confusion

**When NOT to annotate:**
- Current, straightforward documentation
- Self-explanatory content
- Temporary documentation
- Content that will soon be removed

---

## Annotation Markers

Annotations use HTML comment syntax so they're invisible in rendered markdown but visible in source and to the LLM.

### Standard Markers

#### 1. `<!-- HISTORICAL NOTE: ... -->`

**Purpose:** Explain historical context, naming changes, or past decisions

**Use When:**
- Explaining old naming conventions (EEFrame → ExFrame)
- Documenting why something exists in a particular form
- Providing context about past architectural decisions

**Example:**
```markdown
# ExFrame Architecture

<!-- HISTORICAL NOTE: EEFrame → ExFrame (January 2026)
The project was renamed from EEFrame to ExFrame for clarity.
Directory names (eeframe/) kept for git history and Docker volume compatibility.
All user-facing content now uses "ExFrame" consistently.
-->

ExFrame is a domain-agnostic AI-powered knowledge system...
```

#### 2. `<!-- SUPERSEDED: ... -->`

**Purpose:** Mark systems, features, or approaches that have been replaced

**Use When:**
- An old system has been replaced by a new one
- Documentation describes a legacy approach
- Code still exists but is no longer recommended

**Example:**
```markdown
## Domain Configuration

<!-- SUPERSEDED: Domain Types 1-5 (v1.6.0 - January 2026)
Replaced by 3 Personas (poet/librarian/researcher) in Phase 1 (February 2026).
The domain_type field still exists for backward compatibility but is deprecated.
New domains should use the 'persona' field instead.
See CHANGELOG.md for migration guide.
-->

### Current System: 3 Personas

ExFrame uses a persona-based architecture...
```

#### 3. `<!-- CONTRADICTION: ... -->`

**Purpose:** Acknowledge known contradictions or inconsistencies that can't be immediately fixed

**Use When:**
- Two systems have overlapping but different terminology
- Legacy code contradicts new documentation
- Temporary inconsistency exists during migration

**Example:**
```markdown
# Plugin Architecture

<!-- CONTRADICTION: Plugin vs Persona terminology
The codebase uses "specialist plugins" (legacy) while documentation describes
"personas" (current). Both refer to query processing behavior. This will be
unified in Phase 3 when the plugin refactor is complete.
-->

The query processor uses personas to determine...
```

#### 4. `<!-- TODO: ... -->`

**Purpose:** Mark work that needs to be done

**Use When:**
- Documentation is incomplete
- Known issues need fixing
- Future improvements are planned

**Example:**
```markdown
## Performance Optimization

<!-- TODO: Document embedding generation time
Need to add benchmarks for first-time embedding generation vs cache hits.
Expected: ~30s for 100 docs first time, ~50ms for subsequent queries.
-->

Semantic search uses cached embeddings for fast retrieval...
```

#### 5. `<!-- CLARIFICATION: ... -->`

**Purpose:** Add additional context that might not be obvious

**Use When:**
- Explaining non-obvious design decisions
- Clarifying terminology that might be confusing
- Providing examples that help understanding

**Example:**
```markdown
## Pattern Override

<!-- CLARIFICATION: Why check patterns first?
Pattern override allows domains to have curated, high-quality answers for
common questions while still falling back to persona data sources for
uncommon queries. This hybrid approach gives best of both worlds:
- Speed and quality for known questions (patterns)
- Flexibility and freshness for new questions (persona)
-->

When search_patterns=true, the system checks local patterns...
```

#### 6. `<!-- DEPRECATED: ... -->`

**Purpose:** Mark features or APIs that should no longer be used

**Use When:**
- Functions, classes, or approaches are being phased out
- Old APIs still work but are not recommended
- Migration path to new approach exists

**Example:**
```markdown
## Domain Factory

<!-- DEPRECATED: DomainConfigGenerator (v1.6.0)
The domain_factory.py module generates configurations for domain types 1-5.
This approach is deprecated as of Phase 1. Use persona field directly instead.

Migration:
- Old: domain_type: "3" → New: persona: "librarian"
- Old: domain_type: "4" → New: persona: "researcher"

This module is maintained for backward compatibility only.
-->

```

---

## Annotation Best Practices

### 1. **Be Specific**
```markdown
<!-- GOOD -->
<!-- HISTORICAL NOTE: Docker snap incompatibility (January 2026)
Snap version of Docker has bind mount bugs that cause mounted directories
to appear empty in containers. Users must use official Docker Engine.
See Issue #42 for details.
-->

<!-- BAD -->
<!-- HISTORICAL NOTE: Docker issues
There were some Docker problems.
-->
```

### 2. **Include Dates**
```markdown
<!-- SUPERSEDED: Domain Types (v1.6.0 - January 2026)
Replaced by 3 Personas in Phase 1 (February 2026)
-->
```

### 3. **Provide Context**
```markdown
<!-- CONTRADICTION: Pattern vs Document terminology
"Patterns" are curated knowledge (patterns.json).
"Documents" are markdown files in the library.
Both can provide context to queries, but patterns are checked first.
-->
```

### 4. **Link to Resources**
```markdown
<!-- TODO: Add diagram
See issue #123 for architectural diagram mockup.
Target completion: Phase 3
-->
```

### 5. **Keep It Inline**
Place annotations immediately before or after the content they describe:

```markdown
## Query Processing

<!-- HISTORICAL NOTE: Pattern Override (Phase 1 - Feb 2026)
This simple decision tree replaced 1000+ lines of conditional logic.
98% code reduction while maintaining all functionality.
-->

The query processor follows this logic:
1. Check local patterns
2. If patterns found → use them
3. If no patterns → use persona data source
```

---

## Multi-line Annotations

For longer explanations, use multi-line HTML comments:

```markdown
<!--
CLARIFICATION: Why Three Personas?

The three personas emerged from analyzing actual use cases:

1. Poet (void) - Pure generation for creative content
   - No external sources needed
   - High temperature for creativity
   - Examples: poetry, stories, brainstorming

2. Librarian (library) - Document search for knowledge
   - Searches local documentation
   - Semantic ranking for relevance
   - Examples: technical docs, how-to guides, APIs

3. Researcher (internet) - Web search for current info
   - Searches the web
   - Synthesizes multiple sources
   - Examples: news, trends, recent events

This covers 95% of knowledge query patterns while keeping
complexity minimal (3 options instead of 5 domain types).
-->
```

---

## How Annotations Are Used

### 1. **Semantic Search Discovery**

The librarian persona searches all documents including annotations. When a query relates to historical changes or contradictions, the semantic search naturally finds annotated sections.

Example:
- Query: "Why is the directory called eeframe?"
- Semantic search finds: `<!-- HISTORICAL NOTE: EEFrame → ExFrame -->`
- Response includes the historical context automatically

### 2. **Contradiction Detection**

The LLM enricher's contradiction detector (`llm_enricher.py`) specifically looks for annotation markers:

```python
# Searches for:
"<!-- HISTORICAL NOTE"
"<!-- SUPERSEDED"
"<!-- CONTRADICTION"
```

When found, it includes the annotation context in the analysis prompt to avoid false-positive contradictions.

### 3. **Human Readability**

Annotations are visible in source files, making it easy for developers to understand context when reading or editing documentation.

### 4. **Version Control**

Annotations are tracked in git, providing a history of when context was added and why.

---

## Annotation Workflow

### When to Add Annotations (Optional Guidelines)

These are situations where annotations can add value, not requirements:

1. **Before Deprecating:** Consider `<!-- SUPERSEDED -->` if users might encounter old references
2. **During Migration:** Use `<!-- CONTRADICTION -->` for temporary inconsistencies that will confuse
3. **After Major Changes:** Add `<!-- HISTORICAL NOTE -->` when the "why" isn't obvious
4. **When Documenting Workarounds:** Use `<!-- CLARIFICATION -->` if the approach seems unusual
5. **Planning Future Work:** Use `<!-- TODO -->` when you want to capture future improvements

**Remember:** Skip annotations when the content is clear on its own.

### Example Migration Workflow

**Step 1: Deprecate old system**
```markdown
## Domain Types

<!-- SUPERSEDED: Domain Types 1-5 (v1.6.0)
See Phase 1 release notes for migration to personas.
-->
```

**Step 2: Document new system**
```markdown
## Persona System

<!-- HISTORICAL NOTE: Why personas replaced domain types
Domain types (1-5) had complex overlapping configurations.
Personas (3) provide clearer mental model and cover same use cases.
-->
```

**Step 3: Remove old system (when ready)**
```markdown
# Just document the new system
# Annotation stays in git history if needed
```

---

## Examples in Practice

### Example 1: Naming Standardization

**File:** `README.md`

```markdown
# ExFrame - Expertise Framework

<!-- HISTORICAL NOTE: Project Naming (January 2026)
Original name: "OMV Copilot" → renamed to "EEFrame"
EEFrame → standardized to "ExFrame" for clarity and consistency

Directory structure:
- eeframe/ - Kept for git history and Docker volumes
- generic_framework/ - Internal implementation (not user-facing)
- All documentation - Uses "ExFrame" consistently
-->

ExFrame is a domain-agnostic AI-powered knowledge system...
```

### Example 2: Architecture Evolution

**File:** `CHANGELOG.md`

```markdown
## [1.6.0] - 2026-01-27

<!-- SUPERSEDED: This release introduced domain types 1-5
Domain types were replaced by 3 personas in Phase 1 (Feb 2026).
This changelog entry preserved for historical reference.
-->

### Added - Domain Type System (LEGACY)

- Type 1: Creative Generator
- Type 2: Knowledge Retrieval
...
```

### Example 3: Known Issue

**File:** `INSTALL.md`

```markdown
## Docker Installation

<!-- CONTRADICTION: Docker snap vs official
Ubuntu's snap version has bind mount bugs (directories appear empty).
Our docs say "Docker Compose" which could mean either version.
Solution: We explicitly require official Docker Engine in prerequisites.
-->

**IMPORTANT:** Use official Docker Engine, NOT snap version:
```

### Example 4: Future Work

**File:** `docs/architecture/overview.md`

```markdown
## Extension Points

<!-- TODO: Plugin hot-reload (Phase 3)
Currently requires restart to load new plugins.
Phase 3 will add hot-reload capability for enrichers and formatters.
Specialists require restart (deeper integration).
-->

To add a new enricher plugin...
```

---

## Integration with Existing Systems

### Ignored Files

The `ignored.md` file determines which files are excluded from document discovery. Annotations live IN the discoverable files, not in ignored ones.

```
✅ Discoverable (can have annotations):
- README.md
- CHANGELOG.md
- docs/**/*.md
- All markdown files except those in ignored.md

❌ Not discoverable (won't see annotations):
- .git/
- __pycache__/
- venv/
- node_modules/
- *.log
(see ignored.md for full list)
```

### Semantic Search

The `DocumentVectorStore` generates embeddings for all discoverable markdown files, including HTML comments. This means annotations are searchable even though they're not rendered.

### LLM Enricher

The contradiction detector automatically extracts annotation context and includes it in analysis prompts. No manual intervention needed.

---

## Maintenance

### Regular Review

Periodically review annotations:

```bash
# Find all annotations
grep -r "<!-- HISTORICAL NOTE" docs/
grep -r "<!-- SUPERSEDED" docs/
grep -r "<!-- CONTRADICTION" docs/
grep -r "<!-- TODO" docs/
```

### Cleanup Old Annotations

When contradictions are resolved or migrations complete:
- Remove `<!-- CONTRADICTION -->` markers
- Convert `<!-- SUPERSEDED -->` to `<!-- HISTORICAL NOTE -->` if context is still useful
- Complete or remove `<!-- TODO -->` items

### Git History Preservation

Don't worry about annotation bloat. Git history preserves removed annotations if needed later.

---

## Tools and Scripts

### Find All Annotations

```bash
# Count annotations by type
echo "HISTORICAL NOTE: $(grep -r '<!-- HISTORICAL NOTE' docs/ | wc -l)"
echo "SUPERSEDED: $(grep -r '<!-- SUPERSEDED' docs/ | wc -l)"
echo "CONTRADICTION: $(grep -r '<!-- CONTRADICTION' docs/ | wc -l)"
echo "TODO: $(grep -r '<!-- TODO' docs/ | wc -l)"
echo "CLARIFICATION: $(grep -r '<!-- CLARIFICATION' docs/ | wc -l)"
```

### Generate Annotation Report

```bash
# List all TODOs
grep -rn "<!-- TODO" docs/ --color=never | sed 's/<!-- TODO:/TODO:/'
```

### Validate Annotations

```bash
# Check for unclosed comments
grep -r "<!-- " docs/ | grep -v " -->"
```

---

## Migration from INDEX.md

**Old system:**
- `docs/INDEX.md` - Static file listing with one-line summaries
- Manually maintained, went stale
- Contradiction detector looked for INDEX.md specifically

**New system:**
- Inline annotations in actual documentation files
- Self-maintaining (context lives with content)
- Contradiction detector looks for annotation markers
- Semantic search discovers annotations naturally

**Migration complete:** INDEX.md deleted, llm_enricher.py updated to look for annotation markers.

---

## Summary

| Marker | Purpose | When to Use |
|--------|---------|-------------|
| `<!-- HISTORICAL NOTE -->` | Explain past decisions | Naming changes, old approaches |
| `<!-- SUPERSEDED -->` | Mark replaced systems | Deprecated features, old architecture |
| `<!-- CONTRADICTION -->` | Acknowledge known issues | Temporary inconsistencies |
| `<!-- TODO -->` | Mark needed work | Incomplete docs, planned improvements |
| `<!-- CLARIFICATION -->` | Add context | Non-obvious decisions, examples |
| `<!-- DEPRECATED -->` | Phase out old features | Legacy APIs, old approaches |

**Benefits:**
- ✅ Context lives with content
- ✅ Semantic search finds it automatically
- ✅ No external tracking needed
- ✅ Git history preserves changes
- ✅ Human-readable in source
- ✅ LLM-friendly (included in embeddings)

**Best Practices:**
- Be specific (include dates, reasons, migration paths)
- Place inline (near the content they describe)
- Review regularly (clean up resolved issues)
- Keep concise (use multi-line for longer explanations)

---

**End of Annotation System Documentation**
