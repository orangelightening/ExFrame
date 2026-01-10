# Dynamic Domain Refactor Plan

## Current Pain Points

1. **Manual Code Required** - Every domain needs custom Python classes
2. **App.py Edits** - Must edit main app file to add domains
3. **Frontend Edits** - Must edit index.html for each domain
4. **Container Rebuilds** - Code changes require full rebuild
5. **Error Prone** - Multiple files, import paths, abstract methods

## Target State

**Create a complete domain via UI form in < 5 minutes**

```
User fills form → Domain created → Patterns added → Ready to query
```

No code edits. No restarts. No rebuilds.

---

## Architecture Design

### 1. Domain Schema (JSON)

```json
{
  "domain_id": "binary_mathematics",
  "domain_name": "Binary Mathematics",
  "description": "Advanced binary operations and number theory",
  "version": "1.0.0",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z",

  "specialists": [
    {
      "specialist_id": "arithmetic_expert",
      "name": "Binary Arithmetic Expert",
      "description": "Expert in binary arithmetic operations",
      "expertise_keywords": ["add", "subtract", "multiply", "divide", "modulo"],
      "expertise_categories": ["arithmetic", "operation", "calculation"],
      "confidence_threshold": 0.7,
      "response_template": "structured"
    }
  ],

  "categories": ["arithmetic", "logic", "bitwise", "encoding"],
  "tags": ["binary", "math", "calculation", "algorithm"],

  "ui_config": {
    "placeholder_text": "Ask about binary arithmetic, operations, or calculations...",
    "example_queries": [
      "How do I add two binary numbers?",
      "What is binary multiplication?",
      "How do I detect overflow in binary addition?"
    ],
    "icon": "🔢",
    "color": "#4CAF50"
  },

  "links": {
    "related_domains": ["binary_symmetry", "computer_science"],
    "imports_patterns_from": [],
    "suggest_on_confidence_below": 0.3
  }
}
```

### 2. Pattern Schema (Enhanced)

```json
{
  "id": "binary_math_001",
  "name": "Binary Addition",
  "pattern_type": "arithmetic",
  "category": "operation",
  "domain": "binary_mathematics",

  "problem": "Add two binary numbers",
  "solution": "Use full-adder logic: sum = A XOR B XOR carry, carry = (A AND B) OR (B AND carry) OR (A AND carry)",

  "examples": [
    {
      "input": "01 + 01",
      "output": "10",
      "carry": "0",
      "notes": "1 + 1 = 10 in binary"
    }
  ],

  "confidence": 0.98,
  "complexity": "beginner",
  "estimated_time": "2 minutes",

  "risk_factors": ["overflow"],
  "applications": ["cpu_design", "cryptography", "error_detection"],

  "prerequisites": ["binary_math_000"],
  "related_patterns": ["binary_math_002", "binary_math_003"],

  "metadata": {
    "author": "system",
    "verified": true,
    "times_accessed": 0,
    "user_rating": null
  }
}
```

### 3. GenericDomain Class

**No more custom domain classes!**

```python
# core/generic_domain.py

class GenericDomain(Domain):
    """
    Fully configurable domain that loads from JSON.
    No custom code required.
    """

    def __init__(self, config: DomainConfig):
        super().__init__(config)
        self._domain_config = None  # Loaded from JSON
        self._specialists = {}

    async def initialize(self) -> None:
        """Load domain config from JSON file."""
        config_file = Path(self.config.pattern_storage_path) / "domain.json"

        if config_file.exists():
            with open(config_file) as f:
                self._domain_config = json.load(f)
        else:
            # Create default config
            self._domain_config = self._create_default_config()

        # Initialize knowledge base
        kb_config = KnowledgeBaseConfig(...)
        self._knowledge_base = JSONKnowledgeBase(kb_config)
        await self._knowledge_base.load_patterns()

        # Create generic specialists from config
        for spec_config in self._domain_config.get("specialists", []):
            self._specialists[spec_config["specialist_id"]] = \
                GenericSpecialist(spec_config, self._knowledge_base)

    @property
    def domain_id(self) -> str:
        return self._domain_config.get("domain_id", self.config.domain_id)

    @property
    def domain_name(self) -> str:
        return self._domain_config.get("domain_name", "Unknown Domain")

    # All other methods work with config, no overrides needed!
```

### 4. GenericSpecialist Class

**No more custom specialist classes!**

```python
# core/generic_specialist.py

class GenericSpecialist(Specialist):
    """
    Fully configurable specialist that works with any domain.
    """

    def __init__(self, config: dict, knowledge_base: KnowledgeBase):
        self._config_data = config
        self.knowledge_base = knowledge_base

    @property
    def specialist_id(self) -> str:
        return self._config_data["specialist_id"]

    @property
    def name(self) -> str:
        return self._config_data["name"]

    @property
    def config(self) -> SpecialistConfig:
        return SpecialistConfig(
            specialist_id=self._config_data["specialist_id"],
            name=self._config_data["name"],
            description=self._config_data.get("description", ""),
            expertise_keywords=self._config_data.get("expertise_keywords", []),
            expertise_categories=self._config_data.get("expertise_categories", []),
            confidence_threshold=self._config_data.get("confidence_threshold", 0.6)
        )

    def can_handle(self, query: str) -> float:
        """Score based on configured keywords and categories."""
        query_lower = query.lower()
        score = 0.0

        # Score keywords
        for keyword in self._config_data.get("expertise_keywords", []):
            if keyword.lower() in query_lower:
                score += 0.2

        return min(score, 1.0)

    async def process_query(self, query: str, context=None) -> dict:
        """Process query using knowledge base."""
        patterns = await self.knowledge_base.search(query, limit=10)
        return {
            "specialist_id": self.specialist_id,
            "patterns_found": len(patterns),
            "patterns": patterns[:5],
            "query": query,
            "confidence": self.can_handle(query)
        }

    def format_response(self, response_data: dict) -> str:
        """Format based on configured template style."""
        template = self._config_data.get("response_template", "structured")

        if template == "concise":
            return self._format_concise(response_data)
        elif template == "narrative":
            return self._format_narrative(response_data)
        else:
            return self._format_structured(response_data)
```

### 5. Dynamic Domain Loading

**No more app.py edits!**

```python
# api/app.py - Simplified startup

@app.on_event("startup")
async def startup_event():
    """Auto-discover and load all domains."""
    domains_dir = Path("/app/data/patterns")

    for domain_dir in domains_dir.iterdir():
        if domain_dir.is_dir():
            domain_id = domain_dir.name

            # Check if domain.json exists
            domain_config_file = domain_dir / "domain.json"
            patterns_file = domain_dir / "patterns.json"

            if domain_config_file.exists() and patterns_file.exists():
                # Create domain from config
                config = DomainConfig(
                    domain_id=domain_id,
                    domain_name=f"Auto-loaded: {domain_id}",
                    pattern_storage_path=str(domain_dir),
                    pattern_format="json"
                )

                domain = GenericDomain(config)
                await domain.initialize()

                engine = GenericAssistantEngine(domain)
                await engine.initialize()

                engines[domain_id] = engine

    logger.info(f"Loaded {len(engines)} domains automatically")
```

### 6. UI Components

#### Domain Creator Form

```javascript
// Frontend - Domain Creator

function DomainCreator() {
    return {
        domainId: '',
        domainName: '',
        description: '',
        categories: '',
        tags: '',

        specialists: [],

        uiConfig: {
            placeholderText: '',
            exampleQueries: [],
            icon: '📚',
            color: '#2196F3'
        },

        async createDomain() {
            const domainConfig = {
                domain_id: this.domainId,
                domain_name: this.domainName,
                description: this.description,
                categories: this.categories.split(',').map(s => s.trim()),
                tags: this.tags.split(',').map(s => s.trim()),
                specialists: this.specialists,
                ui_config: this.uiConfig,
                created_at: new Date().toISOString()
            };

            // Create domain directory
            await fetch('/api/admin/domains', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(domainConfig)
            });

            // Domain is now live!
        },

        addSpecialist() {
            this.specialists.push({
                specialist_id: `spec_${this.specialists.length + 1}`,
                name: '',
                expertise_keywords: [],
                expertise_categories: []
            });
        }
    }
}
```

#### Pattern Editor

```javascript
// Frontend - Pattern Editor

function PatternEditor() {
    return {
        domainId: 'binary_symmetry',

        pattern: {
            id: '',
            name: '',
            pattern_type: '',
            category: '',
            problem: '',
            solution: '',
            examples: [],
            confidence: 0.8
        },

        async savePattern() {
            await fetch(`/api/domains/${this.domainId}/patterns`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(this.pattern)
            });
        },

        addExample() {
            this.pattern.examples.push({input: '', output: '', notes: ''});
        }
    }
}
```

#### Domain Linker

```javascript
// Frontend - Domain Linker

function DomainLinker() {
    return {
        sourceDomain: 'binary_symmetry',
        targetDomain: 'binary_mathematics',
        linkType: 'related', // or 'imports', 'suggests', 'extends'

        relationship: {
            description: 'Both deal with binary operations',
            strength: 0.8,
            bidirectional: true
        },

        async createLink() {
            await fetch('/api/admin/domains/links', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(this.relationship)
            });
        }
    }
}
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Day 1)
- [ ] Create GenericDomain class
- [ ] Create GenericSpecialist class
- [ ] Implement dynamic domain discovery
- [ ] Remove hardcoded domain loading from app.py

### Phase 2: Domain Schema (Day 2)
- [ ] Define domain.json schema
- [ ] Define enhanced patterns.json schema
- [ ] Create domain.json for existing domains
- [ ] Migration script for existing domains

### Phase 3: API Endpoints (Day 3)
- [ ] POST /api/admin/domains - Create domain
- [ ] PUT /api/admin/domains/{id} - Update domain
- [ ] DELETE /api/admin/domains/{id} - Delete domain
- [ ] POST /api/domains/{id}/patterns - Add pattern
- [ ] POST /api/admin/domains/links - Link domains

### Phase 4: UI Components (Day 4)
- [ ] Domain creator form
- [ ] Pattern editor
- [ ] Domain linker
- [ ] Domain browser/listing

### Phase 5: Testing & Migration (Day 5)
- [ ] Migrate cooking domain
- [ ] Migrate llm_consciousness domain
- [ ] Migrate binary_symmetry domain
- [ ] Create new domain via UI (test)
- [ ] Remove old hardcoded classes

---

## Success Metrics

✅ **Before:** 4-8 hours to create a domain (manual code)
✅ **After:** 5-10 minutes to create a domain (form fill)

✅ **Before:** Edit 5+ files, container rebuild
✅ **After:** Fill 1 form, instant availability

✅ **Before:** Need Python knowledge
✅ **After:** Anyone can create domains

---

## File Structure After Refactor

```
data/patterns/
├── binary_symmetry/
│   ├── domain.json          # NEW - Domain config
│   └── patterns.json        # Existing - Patterns
├── llm_consciousness/
│   ├── domain.json          # NEW
│   └── patterns.json        # Existing
└── new_domain/              # Created via UI!
    ├── domain.json
    └── patterns.json

generic_framework/
├── core/
│   ├── generic_domain.py    # NEW - Universal domain
│   └── generic_specialist.py # NEW - Universal specialist
├── domains/
│   └── [DELETE OLD CUSTOM DOMAINS]  # No longer needed!
└── api/
    └── app.py               # SIMPLIFIED - Auto-discovers domains
```

---

## Key Benefits

1. **No Code Required** - Domains are data, not code
2. **Instant Deployment** - No restarts needed
3. **UI-Driven** - Non-technical users can create domains
4. **Linkable** - Domains can reference each other
5. **Versionable** - JSON configs can be git-tracked
6. **Testable** - Can validate schemas before deployment
7. **Documented** - Domain config is self-documenting
