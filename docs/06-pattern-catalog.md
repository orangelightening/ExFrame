# EEFrame Pattern Catalog

**Purpose**: Comprehensive catalog of all knowledge patterns across EEFrame subsystems, including OMV Co-Pilot troubleshooting patterns and Expertise Scanner multi-domain patterns.

**Last Updated**: 2026-01-07
**Status**: 32 active patterns across 6 domains, plus OMV Co-Pilot manual patterns

---

## Overview

EEFrame uses pattern-based knowledge representation across both main subsystems:

1. **OMV Co-Pilot Patterns**: Manual YAML patterns for OpenMediaVault troubleshooting (symptom/diagnostic/solution format)
2. **Expertise Scanner Patterns**: Multi-domain JSON patterns for general expertise (cooking, Python, OMV, DIY, first aid, gardening)

While the pattern formats differ between systems, they share the core philosophy of structured knowledge representation for AI-assisted problem solving.

---

## Pattern Storage Locations

### OMV Co-Pilot Patterns
- **File**: `patterns/manual.yaml`
- **Format**: YAML with structured troubleshooting patterns
- **Lines**: ~1265 lines containing multiple patterns
- **Usage**: Symptom-based matching for OMV server issues

### Expertise Scanner Patterns
- **Directory**: `expertise_scanner/data/patterns/`
- **Format**: JSON files per domain
- **Domains**: `cooking`, `python`, `omv`, `diy`, `first_aid`, `gardening`
- **Structure**: Each domain has `patterns.json` containing array of Pattern objects

---

## Pattern Counts by Domain

| Domain | Pattern Count | File Size | Status | Primary Pattern Types |
|--------|---------------|-----------|--------|----------------------|
| **Cooking** | 22 patterns | 842 lines | Active | procedure, substitution, troubleshooting |
| **Python** | 6 patterns | 220 lines | Active | optimization, readability, generators |
| **OMV** | 3 patterns | 122 lines | Active | troubleshooting, procedure, docker |
| **DIY** | 0 patterns | 1 line | Empty | - |
| **First Aid** | 1 pattern | 27 lines | Minimal | procedure |
| **Gardening** | 0 patterns | 1 line | Empty | - |
| **Total** | **32 patterns** | **1213 lines** | | |

**Note**: OMV Co-Pilot patterns in `patterns/manual.yaml` are separate and not included in this count.

---

## Pattern Schema (Expertise Scanner)

### Core Pattern Structure

Defined in `expertise_scanner/src/extraction/models.py`:

```python
class Pattern(BaseModel):
    # Identity
    id: str                    # "{domain}_{number:03d}" (e.g., "cooking_001")
    domain: str                # Domain identifier
    name: str                  # Short descriptive name
    pattern_type: PatternType  # Type enum

    # Core expertise
    description: str           # What this pattern does
    problem: str               # What problem does this solve?
    solution: str              # How is it solved?
    steps: List[str] = []      # Procedural steps

    # Decision points
    conditions: Dict[str, str] = {}  # "if X then Y" conditions

    # Relationships
    related_patterns: List[str] = []  # IDs of related patterns
    prerequisites: List[str] = []     # Must do these first
    alternatives: List[str] = []      # Other ways to solve

    # Metadata
    confidence: float = 0.5           # Reliability score 0-1
    sources: List[str] = []           # URLs, references
    tags: List[str] = []              # Free-form labels
    examples: List[str] = []          # Concrete examples

    # Tracking
    created_at: datetime
    updated_at: datetime
    times_accessed: int = 0
    user_rating: Optional[float] = None
```

### Pattern Types (Enum)

```python
class PatternType(str, Enum):
    TROUBLESHOOTING = "troubleshooting"  # Diagnose and fix problems
    PROCEDURE = "procedure"              # Step-by-step process
    SUBSTITUTION = "substitution"        # Replace X with Y
    DECISION = "decision"                # Decision tree/branching
    DIAGNOSTIC = "diagnostic"            # Identify what's wrong
    PREPARATION = "preparation"          # Setup requirements
    OPTIMIZATION = "optimization"        # Improve performance
    PRINCIPLE = "principle"              # Fundamental rule/concept
```

---

## OMV Co-Pilot Pattern Format

### Manual YAML Structure

Example pattern from `patterns/manual.yaml`:

```yaml
pattern_id: "omv-001"
title: "SMB share inaccessible from Windows"
category: "services"

symptoms:
  - "Windows cannot access \\\\server\\share"
  - "Network path not found error"
  - "Access denied message"

triggers:
  - "user reports cannot access share"
  - "windows_network_access_failure"

diagnostics:
  - name: "Check SMB service status"
    command: "systemctl status smbd"
    expected: "active (running)"

  - name: "Check firewall rules"
    command: "ufw status"
    expected: "SMB ports open"

solutions:
  - priority: 1
    action: "Restart SMB service"
    command: "systemctl restart smbd"
    explanation: "Service may be hung"

  - priority: 2
    action: "Check share permissions"
    command: "cat /etc/samba/smb.conf"
    explanation: "Permissions may be misconfigured"

related_patterns:
  - "omv-002"
  - "omv-005"

references:
  - "OMV Forum: SMB troubleshooting guide"
  - "Samba documentation"

confidence: 0.85
```

### OMV Co-Pilot Categories
- `services` - SMB, NFS, Docker services
- `storage` - RAID, ZFS, disk usage, filesystems
- `docker` - Container management, Docker Compose
- `networking` - Firewall, ports, network interfaces

---

## Domain Configuration

### Cooking Domain Example

File: `generic_framework/config/domains/cooking.yaml`

```yaml
domain:
  domain_id: "cooking"
  domain_name: "Cooking & Recipes"
  version: "1.0.0"
  description: "Culinary knowledge, recipes, and cooking techniques"

  data_sources:
    - "/expertise_scanner/data/patterns/cooking"

  pattern_storage_path: "/expertise_scanner/data/patterns/cooking"
  pattern_format: "json"
  default_collector_type: "file_system"

  categories:
    - "technique"
    - "preparation"
    - "cooking_method"
    - "ingredient_substitution"
    - "troubleshooting"
    - "equipment"
    - "procedure"

  tags:
    - "baking"
    - "grilling"
    - "sautéing"
    - "roasting"
    - "chicken"
    - "vegetarian"
    - "quick"
    - "healthy"

  enabled_features:
    - "pattern_search"
    - "specialist_routing"
    - "feedback_learning"

  domain_settings:
    temperature_unit: "F"
    serving_size_unit: "servings"
```

### Domain-Specific Categories

| Domain | Primary Categories | Example Tags |
|--------|-------------------|--------------|
| **Cooking** | technique, preparation, cooking_method, ingredient_substitution, troubleshooting, equipment, procedure | baking, grilling, chicken, vegetarian, quick |
| **Python** | optimization, readability, memory, generators | performance, clean_code, memory_efficient |
| **OMV** | troubleshooting, procedure, docker, disk | services, storage, networking, containers |

---

## Pattern Examples

### Cooking Pattern Example

```json
{
  "id": "cooking_001",
  "domain": "cooking",
  "name": "Fluffy Pancakes",
  "pattern_type": "procedure",
  "description": "How to make light and fluffy pancakes",
  "problem": "Pancakes are dense and heavy",
  "solution": "Use buttermilk and don't overmix batter",
  "steps": [
    "Mix dry ingredients separately",
    "Combine wet ingredients separately",
    "Fold wet into dry gently (lumps are okay)",
    "Cook on medium heat until bubbles form",
    "Flip once and cook until golden brown"
  ],
  "conditions": {
    "if_using_buttermilk": "reduce baking powder slightly",
    "if_no_buttermilk": "use milk with lemon juice/vinegar"
  },
  "related_patterns": ["cooking_002"],
  "prerequisites": [],
  "alternatives": ["cooking_010"],
  "confidence": 0.9,
  "sources": ["family recipe", "tested 5 times"],
  "tags": ["breakfast", "quick", "beginner", "pancakes"],
  "examples": ["Sunday brunch", "Kids breakfast", "Quick breakfast"],
  "created_at": "2025-12-15T10:30:00Z",
  "updated_at": "2025-12-20T14:45:00Z",
  "times_accessed": 0,
  "user_rating": null
}
```

### Python Pattern Example

```json
{
  "id": "python_001",
  "domain": "python",
  "name": "Generator Memory Efficiency",
  "pattern_type": "optimization",
  "description": "Use generators for memory-efficient iteration",
  "problem": "Processing large datasets causes memory issues",
  "solution": "Replace list comprehensions with generator expressions",
  "steps": [
    "Identify memory-intensive loops",
    "Replace [] with () for generator expressions",
    "Use yield in functions for custom generators",
    "Process items one at a time instead of all at once"
  ],
  "conditions": {
    "if_sequential_access": "generators are ideal",
    "if_random_access": "consider other data structures"
  },
  "related_patterns": ["python_002", "python_003"],
  "prerequisites": ["basic_python_knowledge"],
  "alternatives": ["chunk_processing", "memory_mapped_files"],
  "confidence": 0.95,
  "sources": ["Python docs", "Fluent Python book"],
  "tags": ["performance", "memory", "iteration", "generators"],
  "examples": ["Processing large log files", "Streaming data analysis"],
  "created_at": "2025-12-10T09:15:00Z",
  "updated_at": "2025-12-10T09:15:00Z",
  "times_accessed": 0,
  "user_rating": null
}
```

### OMV Troubleshooting Pattern Example

```json
{
  "id": "omv_001",
  "domain": "omv",
  "name": "Docker Container Won't Start",
  "pattern_type": "troubleshooting",
  "description": "Diagnose and fix Docker container startup issues",
  "problem": "Docker container exits immediately or fails to start",
  "solution": "Check logs, port conflicts, and resource limits",
  "steps": [
    "Check container logs: docker logs [container]",
    "Verify port isn't already in use",
    "Check resource limits (memory, CPU)",
    "Verify volume mounts exist",
    "Check Docker Compose configuration"
  ],
  "conditions": {
    "if_port_conflict": "change port or stop conflicting service",
    "if_memory_issue": "increase memory limit or add swap",
    "if_volume_missing": "create required directories"
  },
  "related_patterns": ["omv_002"],
  "prerequisites": ["docker_installed"],
  "alternatives": ["manual_service_installation"],
  "confidence": 0.85,
  "sources": ["Docker documentation", "OMV forum posts"],
  "tags": ["docker", "containers", "troubleshooting", "services"],
  "examples": ["Nextcloud container failing", "Jellyfin won't start"],
  "created_at": "2025-12-12T11:20:00Z",
  "updated_at": "2025-12-12T11:20:00Z",
  "times_accessed": 0,
  "user_rating": null
}
```

---

## Pattern Relationships

### Relationship Types

1. **Related Patterns**: Similar or complementary patterns (e.g., `cooking_001` → `cooking_002`)
2. **Prerequisites**: Must complete before this pattern (e.g., `basic_python_knowledge` before `python_001`)
3. **Alternatives**: Different ways to achieve same goal (e.g., `cooking_010` as alternative to `cooking_001`)
4. **Specialization**: More specific version of a general pattern
5. **Generalization**: More general version of a specific pattern

### Relationship Examples

```json
// From cooking_001
"related_patterns": ["cooking_002"],
"prerequisites": [],
"alternatives": ["cooking_010"]

// From python_001
"related_patterns": ["python_002", "python_003"],
"prerequisites": ["basic_python_knowledge"],
"alternatives": ["chunk_processing", "memory_mapped_files"]
```

---

## Pattern Metadata and Statistics

### Tracking Fields

| Field | Description | Example Value |
|-------|-------------|---------------|
| `created_at` | Pattern creation timestamp | `2025-12-15T10:30:00Z` |
| `updated_at` | Last modification timestamp | `2025-12-20T14:45:00Z` |
| `times_accessed` | Usage counter | `0` (currently unused) |
| `user_rating` | Optional user feedback | `null` (currently unused) |
| `confidence` | Reliability score (0-1) | `0.9` |

### Current Statistics

- **Total patterns**: 32 across all domains
- **Most active domain**: Cooking (22 patterns, 68.75% of total)
- **Average confidence**: ~0.9 across all patterns
- **Most common pattern type**: `procedure` (cooking domain)
- **Pattern creation period**: December 2025 (all patterns)

### Confidence Score Distribution

| Confidence Range | Pattern Count | Percentage |
|------------------|---------------|------------|
| 0.9 - 1.0 | 28 patterns | 87.5% |
| 0.8 - 0.89 | 3 patterns | 9.4% |
| 0.7 - 0.79 | 1 pattern | 3.1% |
| < 0.7 | 0 patterns | 0% |

---

## Pattern Ingestion Process

### AI Inbox Pipeline

1. **Source**: AI-generated JSON recipe files in `pattern-inbox/` directory
2. **Processing**: `PatternIngestionQueue` in `expertise_scanner/src/ingestion/inbox.py`
3. **Extraction**: `PatternExtractor` converts recipes to patterns
4. **Storage**: Patterns saved to domain-specific JSON files

### Recipe JSON Format (Input)

```json
{
  "title": "Creamy Tuscan Chicken",
  "url": "https://www.allrecipes.com/recipe/285238/creamy-tuscan-chicken/",
  "description": "A creamy, sun-dried tomato and spinach chicken dish...",
  "ingredients": ["4 boneless chicken breasts", "2 tbsp olive oil", ...],
  "steps": ["Season chicken", "Heat oil in skillet", "Cook chicken 5-7 min per side", ...],
  "prep_time": "15 minutes",
  "cook_time": "20 minutes",
  "total_time": "35 minutes",
  "servings": "4",
  "category": "dinner",
  "tags": ["chicken", "quick", "italian-inspired"],
  "rating": 4.7
}
```

### Ingestion API Endpoints

- `POST /api/ingest/url` - Ingest content from URL
- `POST /api/ingest/text` - Ingest raw text
- `POST /api/ingest/batch/allrecipes` - Batch ingest recipes
- `POST /api/ingest/inbox/process` - Process AI inbox files
- `GET /api/ingest/jobs/{job_id}` - Check ingestion status

---

## API Access to Patterns

### Base Endpoints

**Expertise Scanner API** (`http://localhost:8889`):
- `GET /api/patterns` - List patterns with filtering
- `POST /api/patterns` - Create new pattern
- `GET /api/patterns/{id}` - Get specific pattern
- `PUT /api/patterns/{id}` - Update pattern
- `DELETE /api/patterns/{id}` - Delete pattern
- `GET /api/patterns/domains/list` - List all domains

**OMV Co-Pilot API** (`http://localhost:8000`):
- `GET /api/v1/knowledge/patterns` - List OMV patterns
- `GET /api/v1/knowledge/patterns/{pattern_id}` - Get OMV pattern
- `GET /api/v1/knowledge/search` - Search OMV patterns

### Filtering Options

**Domain Filtering**:
```bash
GET /api/patterns?domain=cooking
GET /api/patterns?domain=python
GET /api/patterns?domain=omv
```

**Pattern Type Filtering**:
```bash
GET /api/patterns?pattern_type=procedure
GET /api/patterns?pattern_type=troubleshooting
GET /api/patterns?pattern_type=optimization
```

**Combined Filtering**:
```bash
GET /api/patterns?domain=cooking&pattern_type=procedure&limit=10
```

**Pagination**:
```bash
GET /api/patterns?limit=20&offset=40
```

---

## Pattern Usage in AI Systems

### OMV Co-Pilot Pattern Matching

1. **Symptom Matching**: User query matched against pattern symptoms
2. **Confidence Scoring**: Base 0.5 + pattern score bonus + high-score bonus
3. **Context Assembly**: Matched patterns included in LLM prompt
4. **Solution Ranking**: Patterns with higher confidence prioritized

### Generic Framework Specialist Routing

1. **Domain Selection**: Query routed to appropriate domain (cooking, python, etc.)
2. **Pattern Retrieval**: Relevant patterns fetched based on query
3. **Prompt Assembly**: Patterns included as context for LLM
4. **Response Generation**: LLM generates response using pattern knowledge

### Confidence Scoring Algorithm

```python
# OMV Co-Pilot example
base_confidence = 0.5
pattern_score = matched_pattern.confidence * 0.3  # Pattern weight
high_score_bonus = 0.1 if matched_pattern.confidence > 0.8 else 0
total_confidence = base_confidence + pattern_score + high_score_bonus
```

---

## Pattern Maintenance

### Creating New Patterns

#### Manual Creation (OMV Co-Pilot):
1. Edit `patterns/manual.yaml`
2. Add new pattern with unique `pattern_id`
3. Define symptoms, diagnostics, solutions
4. Set confidence score (0.5-1.0)

#### API Creation (Expertise Scanner):
```bash
curl -X POST http://localhost:8889/api/patterns \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "cooking",
    "name": "New Recipe Pattern",
    "pattern_type": "procedure",
    "description": "...",
    "problem": "...",
    "solution": "..."
  }'
```

#### AI-Generated Patterns:
1. Place JSON recipe files in `pattern-inbox/`
2. Call `POST /api/ingest/inbox/process`
3. System automatically extracts patterns

### Updating Patterns

#### Manual Update:
```bash
curl -X PUT http://localhost:8889/api/patterns/cooking_001 \
  -H "Content-Type: application/json" \
  -d '{"confidence": 0.95, "tags": ["updated"]}'
```

#### Bulk Operations:
- Currently manual file editing
- Future: Import/export functionality planned

### Deleting Patterns

```bash
curl -X DELETE http://localhost:8889/api/patterns/cooking_001
```

**Note**: Deletion is permanent. Consider archiving instead.

---

## Quality Assurance

### Pattern Validation

**Required Fields**:
- `id`: Must match format `{domain}_{number:03d}`
- `domain`: Must be configured domain
- `name`: Non-empty string
- `pattern_type`: Valid enum value
- `description`: Non-empty string
- `problem`: Non-empty string
- `solution`: Non-empty string
- `confidence`: 0.0 to 1.0

**Relationship Validation**:
- `related_patterns`: IDs must exist
- `prerequisites`: IDs must exist
- `alternatives`: IDs must exist

### Consistency Checks

1. **ID Uniqueness**: No duplicate pattern IDs
2. **Domain Consistency**: Pattern domain matches storage location
3. **Relationship Integrity**: Related patterns exist and are in same domain
4. **Confidence Bounds**: 0.0 ≤ confidence ≤ 1.0

### Testing Patterns

```python
# Example test script
import json
from expertise_scanner.src.extraction.models import Pattern

def validate_pattern_file(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    for pattern_data in data:
        try:
            pattern = Pattern(**pattern_data)
            print(f"✓ Valid pattern: {pattern.id}")
        except Exception as e:
            print(f"✗ Invalid pattern: {e}")
```

---

## Future Enhancements

### Pattern System Roadmap

1. **Unified Pattern Format**: Common structure across OMV Co-Pilot and Expertise Scanner
2. **Pattern Versioning**: Track changes and maintain history
3. **User Feedback Integration**: Update confidence scores based on usage
4. **Pattern Discovery**: Suggest new patterns based on query gaps
5. **Cross-Domain Patterns**: Identify universal patterns across domains
6. **Pattern Testing Framework**: Automated validation of pattern effectiveness
7. **Export Formats**: JSON, YAML, Markdown, PDF exports
8. **Visual Relationships**: Graph visualization of pattern connections
9. **Batch Operations**: Bulk import/export, update, delete
10. **Backup & Restore**: Versioned pattern storage

### Integration Opportunities

1. **Pattern Sharing**: Export OMV Co-Pilot patterns to Expertise Scanner
2. **Cross-System Search**: Unified search across all pattern systems
3. **Common API Layer**: Single endpoint for all pattern operations
4. **Shared Storage**: Centralized pattern database (SQLite/PostgreSQL)

---

## Troubleshooting Pattern Issues

### Common Problems

1. **Pattern Not Loading**:
   - Check file permissions
   - Validate JSON/YAML syntax
   - Verify domain configuration

2. **Pattern Not Matching**:
   - Check symptom definitions
   - Verify confidence thresholds
   - Review pattern categories

3. **API Access Issues**:
   - Verify API server is running
   - Check CORS configuration
   - Validate authentication (if configured)

4. **Ingestion Failures**:
   - Check AI inbox directory permissions
   - Verify JSON recipe format
   - Review extraction rules

### Diagnostic Commands

```bash
# Check pattern file syntax
python -m json.tool expertise_scanner/data/patterns/cooking/patterns.json

# Validate YAML syntax (OMV Co-Pilot)
python -c "import yaml; yaml.safe_load(open('patterns/manual.yaml'))"

# Test API access
curl http://localhost:8889/api/patterns?domain=cooking&limit=1

# Check ingestion status
curl http://localhost:8889/api/ingest/inbox/status
```

---

## Summary

The EEFrame pattern catalog represents a comprehensive knowledge base across multiple domains:

- **32 active patterns** across 6 domains (cooking, python, omv, diy, first_aid, gardening)
- **OMV Co-Pilot patterns** for server troubleshooting in YAML format
- **Expertise Scanner patterns** for general expertise in JSON format
- **Rich metadata** including relationships, confidence scores, and tracking
- **Multiple ingestion methods**: manual, API, AI-generated
- **Comprehensive API access** with filtering and search capabilities

The pattern system forms the foundation of EEFrame's AI-assisted expertise, providing structured knowledge that enhances LLM responses with domain-specific patterns and proven solutions.