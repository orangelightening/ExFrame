# WiseMan Design Document
## Honest Assessment of the Config-Driven Architecture

**Version**: 1.0.0
**Date**: 2026-02-04
**Author**: Claude with honest opinions enabled

**⚠️ NOTE**: This is the **long-term architecture** vision. For immediate implementation, see **PHASE1_PERSONA_DESIGN.md** which provides a simpler incremental approach (3 Personas + Pattern Override, 1 week implementation).

---

## Design Philosophy

### The Core Insight

The current mess exists because **domain logic got tangled with presentation logic**. When you mix "what to do" with "how to show it", you get 1100 lines of conditional spaghetti.

The solution: **Separate concerns completely**

- WiseMan = execution engine (knows HOW to process)
- DomainSequencer = configuration (knows WHAT to process)
- Tools = operations (knows WHAT operations exist)
- QueryOrchestrator = flow control (knows WHEN to do things)

**If you're tempted to add domain-specific logic to core code, STOP. Create a new tool or config option instead.**

---

## What This Design Gets Right

### 1. Composition Over Inheritance ✅

Instead of:
```
BasePoet
├── CreativePoet
├── DocumentPoet
└── WebPoet (which needs both Document and Web features... uh oh)
```

We have:
```
WiseMan(config) where config = {
    use_library: true,
    use_internet: true
}
```

**Why This Matters**: Adding a hybrid mode in the inheritance approach requires either multiple inheritance (messy) or duplicating code (worse). With composition, it's just a config change.

### 2. Single Responsibility ✅

Each component has ONE job:
- WiseMan: Execute with given config
- DomainSequencer: Define execution sequence
- Tool: Do one thing well
- QueryOrchestrator: Manage state flow

**Contrast with current code**: LLMEnricher has SEVEN responsibilities (see context.md lines 93-101). That's why it's 1450 lines.

### 3. Testability ✅

```python
# Easy to test - just pass different configs
def test_poet_mode():
    wiseman = WiseMan(WiseManConfig(use_void=True))
    response = wiseman.respond("Write a poem", domain)
    assert "library_search" not in wiseman.execution_log

def test_librarian_mode():
    wiseman = WiseMan(WiseManConfig(use_library=True))
    response = wiseman.respond("How to cook rice", domain)
    assert "library_search" in wiseman.execution_log
```

**Contrast with current code**: Testing requires mocking domain type strings, specialist IDs, and checking implicit behavior. Fragile and hard to understand.

### 4. Observable Behavior ✅

Every execution path is explicit in config:

```json
{
  "sequence": ["validate", "search", "check_contradictions", "respond"],
  "tools": {
    "validate": "query_validator",
    "search": "library_search",
    "check_contradictions": "contradiction_checker"
  }
}
```

You can SEE what will happen just by reading the config. No hidden control flow.

---

## What This Design Gets Wrong (Honest Assessment)

### 1. Configuration Complexity Risk ⚠️

**The Problem**: As domains grow, config files can become as complex as code.

**Example**:
```json
{
  "sequence": [
    "pre_validate",
    "scope_check",
    "library_search",
    "relevance_filter",
    "contradiction_check",
    "web_search_fallback",
    "llm_synthesis",
    "post_validate",
    "format",
    "log"
  ],
  "tools": {
    "pre_validate": "query_validator",
    "scope_check": "scope_checker",
    ...  // 10 more mappings
  },
  "tool_configs": {
    "scope_checker": {
      "threshold": 0.3,
      "fallback": "ask_user",
      ...  // More config
    }
  }
}
```

**Honest Opinion**: Config files can become "code in JSON" which is WORSE than actual code because:
- No syntax checking
- No IDE support
- No type safety
- Hard to debug

**Mitigation**: Set a limit - if a domain config exceeds 100 lines, that's a smell. Consider whether the domain is too complex or if you need intermediate abstractions.

### 2. The "Just One More Switch" Trap ⚠️

**The Problem**: Adding switches is easy. TOO easy.

**Slippery Slope**:
```python
class WiseMan:
    def __init__(self, config):
        self.trace = config.trace
        self.verbose = config.verbose
        self.show_thinking = config.show_thinking
        self.use_library = config.use_library
        self.use_internet = config.use_internet
        self.use_void = config.use_void
        self.enable_caching = config.enable_caching  # Month 1
        self.cache_ttl = config.cache_ttl  # Month 1
        self.enable_retry = config.enable_retry  # Month 2
        self.max_retries = config.max_retries  # Month 2
        self.enable_fallback = config.enable_fallback  # Month 3
        # ... 6 months later: 47 switches
```

**Honest Opinion**: The WiseMan will grow switches over time. This is inevitable. The question is whether you NOTICE when it's getting out of control.

**Rule of Thumb**: If WiseMan has > 15 switches, you're probably doing something wrong. Consider whether you need multiple WiseMen or whether some switches should be tool-level config instead.

### 3. Tool Composition Limits ⚠️

**The Problem**: Some operations need to COMBINE results from multiple tools, not just sequence them.

**Example**:
```python
# Sequence can't express this:
# "Search library AND web, then MERGE results, then pass to LLM"

# Current sequence model only allows:
# "Search library, THEN search web, THEN pass to LLM"
```

**Honest Opinion**: The sequence model is great for linear flow but breaks down for:
- Parallel execution
- Conditional branching
- Result merging
- Retry logic

**Future Problem**: When you need these, you'll be tempted to add them as special cases in WiseMan. Don't. At that point, consider whether you need a richer sequencing language (like DAG-based execution).

### 4. Debugging Config-Driven Systems is HARD 🔥

**The Problem**: When something breaks, the stack trace points to generic execution code, not the specific config that caused it.

**Error Message**:
```
File "wiseman.py", line 87, in respond
    context = self._get_context(query)
File "wiseman.py", line 120, in _get_context
    return self.tools.execute("library_search", query)
KeyError: 'library_search'
```

**Versus**:
```
File "cooking_domain.py", line 45, in process_query
    return self.library_search(query)  # Clear what went wrong
```

**Honest Opinion**: The generic nature that makes the architecture clean also makes debugging harder. You lose the directness of "this domain does this thing".

**Mitigation**: EXCELLENT logging and tracing are not optional - they're REQUIRED. Every config decision must be logged. Every tool execution must be traced.

### 5. Reference Code May Have Bugs ✅ (Not a Risk)

**The Situation**: Old code may have bugs that cancel each other out.

**Example**:
```python
# Old code (buggy but "works")
def process_query(query):
    query = query.lower()  # Bug 1: loses case info
    results = search(query)
    # Bug 2: compensates by case-insensitive search
    return format(results)

# New code (correct)
def process_query(query):
    results = search(query)  # Correct: preserves case
    return format(results)
```

**Honest Opinion**: You'll find bugs in the old system. That's GOOD - fix them!

**This is actually EASIER** - you're not constrained by old behavior. Build it right.

**Approach**: Use old code as reference for "what behaviors exist", not "what outputs must match".

---

## Design Tradeoffs

### Tradeoff 1: Flexibility vs. Simplicity

**Flexibility**: Config can express any execution flow
**Simplicity**: Config is simple JSON

**You can't have both.** Either:
- A) Simple config, limited flexibility (current design)
- B) Complex config language (like Rego, CEL), more flexibility

**Chosen**: A - Keep config simple, accept limited flexibility

**Consequence**: Some domains will need custom tools that encapsulate complex logic. That's OK. Better to have 10 simple tools than 1 complex config language.

### Tradeoff 2: Performance vs. Observability

**Performance**: Direct function calls, minimal overhead
**Observability**: Every execution step logged and traced

**You can't have both.** Logging adds overhead.

**Chosen**: Observability - make logging configurable

**Consequence**: Verbose mode will be SLOW. That's OK. Use it for debugging, not production.

### Tradeoff 3: Strictness vs. Adaptability

**Strictness**: Enforce architectural rules rigidly
**Adaptability**: Allow exceptions for special cases

**You can't have both.** Either rules are rules, or they're guidelines.

**Chosen**: Strictness - NO domain logic in core, period

**Consequence**: Some things will feel awkward. You'll want to add "just one if statement" for a special case. Don't. Create a tool instead.

---

## What Could Go Wrong (Risk Assessment)

### Risk 1: Config Files Become Unmaintainable
**Probability**: MEDIUM (40%)
**Impact**: Medium
**Mitigation**: Set line limits, use config validation, provide config editor UI

### Risk 2: Tool Explosion
**Probability**: MEDIUM (40%)
**Impact**: Medium
**Mitigation**: Periodic tool consolidation, strict naming conventions, tool documentation

### Risk 3: Performance Issues
**Probability**: LOW (20%)
**Impact**: Medium
**Mitigation**: Benchmark implementation, optimize hot paths, make logging optional

~~**Risk 4: Migration Stalls**~~ - NOT APPLICABLE (greenfield implementation)
~~**Risk 5: Outputs Don't Match**~~ - NOT APPLICABLE (no compatibility requirement)

---

## When NOT to Use This Architecture

### Don't Use If:

1. **Your domains are fundamentally different algorithms**
   - Example: One domain uses graph search, another uses neural networks
   - Why: WiseMan assumes shared execution model
   - Alternative: Separate implementations, shared interfaces

2. **You need real-time performance**
   - Example: Sub-10ms response requirements
   - Why: Config parsing, tool lookup, logging add overhead
   - Alternative: Compiled execution paths, skip abstraction

3. **Domains change frequently (daily)**
   - Example: Constantly adding/removing domains
   - Why: Config-driven is great for stable systems, not constant churn
   - Alternative: Code-driven with hot reload

4. **You have < 3 domains**
   - Why: Abstraction overhead not worth it
   - Alternative: Just write three classes

---

## Success Criteria

### What Success Looks Like:
- ✅ Can add new domain in < 1 hour (mostly writing config)
- ✅ Bugs are easy to isolate (config vs tool vs core)
- ✅ New developer understands system in < 1 day
- ✅ 95% of changes are config-only (no code changes)
- ✅ Query processing is clean and observable

### What Failure Looks Like:
- ❌ Config files are 500+ lines of nested JSON
- ❌ Debugging requires reading WiseMan source code
- ❌ Adding features requires changing core code
- ❌ "Just add a switch for this special case" becomes the norm

### The Test:

**In 6 months, will the architecture be CLEANER or MESSIER than today?**

If you're adding switches faster than you're removing complexity, you're losing.

**Advantage**: No migration baggage means you can enforce rules strictly from day one.

---

## Architectural Debt We're Taking On

### Debt 1: Configuration Schema Evolution
**What**: When you add switches to WiseMan, all existing configs may need updating
**Interest Rate**: Medium
**Payoff Plan**: Config versioning, migration tools, backward compatibility for 2 versions

### Debt 2: Tool Discoverability
**What**: 50 tools in a registry - which one do I use?
**Interest Rate**: Low initially, grows over time
**Payoff Plan**: Tool documentation, categorization, search/filter UI

### Debt 3: Error Messages in Generic Code
**What**: Errors point to WiseMan.respond(), not specific domain logic
**Interest Rate**: High (pays daily in debugging time)
**Payoff Plan**: Rich context in exceptions, config path in stack traces

---

## Final Honest Opinion

### The Good:
This architecture is MUCH cleaner than the current mess. It enforces separation of concerns, makes behavior explicit, and scales to many domains.

### The Bad:
Config-driven systems trade code complexity for configuration complexity. You're not eliminating complexity - you're MOVING it. Config is harder to debug than code.

### The Better News:
This is a **greenfield implementation**, not a migration. You're not constrained by old behavior, compatibility requirements, or production users. Build it RIGHT.

### The Verdict:
**Build it clean.**

You have the rare opportunity to start fresh without migration baggage. Use the old code as reference material, but don't let it constrain you.

**Approach**:
- Build it right from the start
- Test that it works correctly
- Don't worry about matching old outputs
- Delete old code when ready
- No rollback plan needed (no production migration)

---

## Design Principles (Reminders for Future You)

1. **Config should be boring**
   - If you're excited about your config file, it's probably too complex

2. **Tools should be obvious**
   - If you need to read the source to understand what a tool does, the name is bad

3. **WiseMan should be dumb**
   - If WiseMan has business logic, you've violated the architecture

4. **State machine should be generic**
   - If you add domain-specific states, you're recreating the old mess

5. **When in doubt, create a tool**
   - Don't add switches to WiseMan
   - Don't add logic to DomainSequencer
   - Create a tool instead

6. **Never say "just this once"**
   - That's how the old mess started
   - Architectural rules only work if you enforce them ALWAYS

---

## Questions for Review

Before implementing, answer these:

1. **Can you explain the architecture to a new developer in 5 minutes?**
   - If not, it's too complex

2. **Can you add a new domain without reading source code?**
   - If not, the config schema needs work

3. **Can you debug a query by reading logs alone?**
   - If not, your logging is insufficient

4. **Can you roll back if migration fails?**
   - If not, your migration plan is incomplete

5. **Can you measure whether the refactor succeeded?**
   - If not, define success criteria first

---

**Status**: Ready for implementation with eyes wide open

**Last Word**: This is a good design. Not perfect, but good. Execute it well, enforce the rules, and it will serve you for years. Execute it poorly, ignore the rules, and in 6 months you'll be writing "WISEMAN_REFACTOR_V2.md".

Your choice.
