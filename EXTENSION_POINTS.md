# Strategic Extension Points for GenericSpecialist

## The Four Critical Methods

After analyzing the specialist lifecycle, these are the 90% case:

### 1. Scoring Extension Point
**Where:** `can_handle(query: str) → float`

**Current behavior:**
```python
def can_handle(self, query: str) -> float:
    score = 0.0
    for keyword in self._config_data.get("expertise_keywords", []):
        if keyword in query:
            score += 0.2
    return min(score, 1.0)
```

**Extension needed when:**
- Bitwise domain wants to boost "0xFF" patterns more than "xor" patterns
- Cooking domain wants to weight "bake" + "chicken" together
- LLM domain wants to detect "hallucinate" but lower confidence for it

**Implementation:**
```python
# In domain.json, add:
{
  "specialist_id": "bitwise_master",
  "expertise_keywords": ["xor", "and", "or", ...],
  "scoring_rules": [
    {
      "if": "contains_any_prefix",  // predefined rule type
      "patterns": ["0x", "0b", "0o"],
      "boost": 0.3,
      "reason": "hex_notation_detected"
    },
    {
      "if": "keyword_combo",
      "keywords": ["detect", "power"],
      "boost": 0.2,
      "reason": "power_detection_query"
    }
  ]
}
```

**GenericSpecialist becomes:**
```python
def can_handle(self, query: str) -> float:
    # Base scoring from keywords
    score = super().can_handle(query)  # 0.2 per keyword match

    # Apply custom scoring rules from config
    for rule in self._config_data.get("scoring_rules", []):
        if self._matches_rule(query, rule):
            score += rule.get("boost", 0)

    return min(score, 1.0)
```

---

### 2. Pattern Filtering Extension Point
**Where:** `_search_patterns(query: str) → List[Pattern]`

**Current behavior:**
```python
async def _search_patterns(self, query: str) -> List[Dict]:
    category = self._config_data.get("expertise_categories", [])[0]
    return await self.knowledge_base.search(query, category=category, limit=10)
```

**Extension needed when:**
- Specialist wants to search multiple categories
- Specialist wants to exclude certain patterns
- Specialist wants to weight patterns by recency or rating

**Implementation:**
```python
# In domain.json:
{
  "specialist_id": "bitwise_master",
  "expertise_categories": ["symmetry", "transformation", "logic"],
  "pattern_filter": {
    "mode": "union",  // union of all categories
    "exclude": ["binary_015"],  // exclude specific patterns
    "boost_recent": 7,  // boost patterns from last 7 days
    "min_confidence": 0.7  // only high-confidence patterns
  }
}
```

**GenericSpecialist becomes:**
```python
async def _search_patterns(self, query: str) -> List[Dict]:
    filter_config = self._config_data.get("pattern_filter", {})

    if filter_config.get("mode") == "union":
        # Search across all specialist's categories
        patterns = []
        for category in self._config_data.get("expertise_categories", []):
            patterns.extend(await self.kb.search(query, category=category, limit=10))
        return self._deduplicate(patterns)
    else:
        # Default: search first category only
        category = self._config_data.get("expertise_categories", [])[0]
        return await self.kb.search(query, category=category, limit=10)
```

---

### 3. Formatting Extension Point
**Where:** `format_response(response_data: dict) → str`

**Current behavior:**
```python
def format_response(self, response_data: dict) -> str:
    template = self._config_data.get("response_template", "structured")
    if template == "structured":
        return self._format_structured(response_data)
    elif template == "concise":
        return self._format_concise(response_data)
    elif template == "narrative":
        return self._format_narrative(response_data)
```

**Extension needed when:**
- Medical domain needs disclaimer headers
- Code domain needs syntax highlighting
- Recipe domain needs structured ingredient lists
- Specialist wants custom layout

**Implementation:**
```python
# In domain.json:
{
  "specialist_id": "bitwise_master",
  "response_template": "structured",
  "format_overrides": {
    "prefix": "🔢 ",
    "suffix": "\n\n---\n\nNeed more bitwise help? Ask about specific operations.",
    "sections": ["name", "type", "solution", "examples", "mathematical_property"],
    "show_confidence": true,
    "show_patterns_used": true
  }
}
```

**GenericSpecialist becomes:**
```python
def _format_structured(self, response_data: dict) -> str:
    overrides = self._config_data.get("format_overrides", {})

    result = ""

    # Add prefix if specified
    if "prefix" in overrides:
        result += overrides["prefix"]

    # Add requested sections
    for section in overrides.get("sections", ["name", "solution"]):
        if section == "name":
            result += f"**{response_data.get('name', 'Unknown')}**\n"
        elif section == "solution":
            result += f"{response_data.get('solution', '')}\n"
        # ... etc

    # Add suffix if specified
    if "suffix" in overrides:
        result += overrides["suffix"]

    return result
```

---

### 4. Full Override Extension Point
**Where:** Entire specialist behavior

**Extension needed when:**
- Domain fundamentally different query processing
- Need external API calls in specialist
- Need complex multi-step reasoning

**Implementation:**
```python
# In domain.json:
{
  "specialist_id": "external_api_specialist",
  "extends": "GenericSpecialist",
  "custom_class": "domains.my_domain.specialists.ExternalAPISpecialist",
  "config": {...}
}
```

**Domain loading becomes:**
```python
async def _initialize_specialists(self) -> None:
    for spec_config in self._domain_config.get("specialists", []):
        # Check if specialist wants custom class
        if "custom_class" in spec_config:
            # Dynamically import and instantiate custom class
            module_path, class_name = spec_config["custom_class"].rsplit(".", 1)
            module = importlib.import_module(module_path)
            specialist_class = getattr(module, class_name)
            specialist = specialist_class(spec_config, self._knowledge_base)
        else:
            # Use GenericSpecialist
            specialist = GenericSpecialist(sc_config, self._knowledge_base)

        self._specialists[specialist.specialist_id] = specialist
```

---

## The Extension Hierarchy

```
Level 1: Configuration (data-only)
├─ Keywords: ["xor", "and", "or"]
├─ Categories: ["symmetry", "transformation"]
├─ Threshold: 0.30
└─ Template: "structured"

Level 2: Scoring Rules (configurable logic)
├─ Boost conditions: "if contains hex: +0.3"
├─ Combo conditions: "if 'bake' and 'chicken': +0.2"
└─ Penalty conditions: "if 'uncertain': -0.1"

Level 3: Pattern Filters (configurable retrieval)
├─ Multi-category search
├─ Exclusions
└─ Weighting

Level 4: Format Overrides (configurable presentation)
├─ Custom sections
├─ Prefix/suffix
└─ Toggles

Level 5: Full Custom Class (Python code)
├─ Custom can_handle()
├─ Custom process_query()
└─ Custom format_response()
```

---

## The 90% Rule

**Levels 1-4 cover 90% of cases** and are:
- Declarative (JSON config)
- Predictable (standard behavior)
- Composable (combine rules)
- Testable (validate config)

**Level 5 is for the 10%** that truly need custom Python.

---

## Implementation Priority

1. **Immediate: Level 1** (already done)
   - Keywords, categories, threshold, template

2. **Next: Level 2** (scoring rules)
   - Most common need: different scoring per domain
   - Implementation: 50 lines of code in GenericSpecialist

3. **Then: Level 4** (format overrides)
   - Common need: different presentation
   - Implementation: 80 lines of code in GenericSpecialist

4. **Last: Level 5** (custom classes)
   - Only if Levels 1-4 can't handle it
   - Already supported by Python inheritance

---

## My Recommendation

**Start with Level 2 (scoring rules)** because:
1. It's the most common customization need
2. It's purely additive (doesn't break existing)
3. It's declarative (easy to understand)
4. It can be added without breaking existing domains

**Example of Level 2 in action:**
```json
{
  "specialist_id": "bitwise_master",
  "expertise_keywords": ["xor", "and", "or", "not", ...],
  "scoring_rules": [
    {
      "trigger": "contains_hex",
      "patterns": ["0x", "0b", "0o"],
      "boost": 0.3,
      "description": "Hex notation indicates bitwise operation"
    },
    {
      "trigger": "question_words",
      "patterns": ["how", "what", "why", "explain"],
      "boost": 0.1,
      "description": "Question seeking explanation"
    }
  ]
}
```

This gives specialist creators fine-grained control WITHOUT writing Python code.

---

## The Question for You

**Which level do you think we'll hit first?**

My bet: Level 2 (scoring rules). I can already see cases where:
- "0xFF" should boost bitwise_master more than generic scoring
- "hallucinate" should boost failure_detection but with caveats
- "bake chicken" should boost cooking specialist more than individual words

Should I implement Level 2 now, or wait until we have a concrete need?
