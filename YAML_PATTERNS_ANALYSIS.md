# YAML Patterns Analysis

**Date**: 2026-01-08  
**Purpose**: Analyze the YAML pattern file and determine conversion strategy

---

## Current State

### File Location
- **Path**: `patterns/manual.yaml`
- **Size**: ~1265 lines
- **Format**: YAML
- **Content**: 24 OMV troubleshooting patterns

### Pattern Structure

Each pattern contains:
```yaml
pattern_id: "omv-001"
title: "SMB share inaccessible from Windows"
category: "services"
symptoms: [list of symptoms]
triggers: [list of keywords]
diagnostics: [list of diagnostic steps]
solutions: [list of solutions with priority]
related_patterns: [list of related pattern IDs]
references: [list of references]
confidence: 0.9
```

### Pattern Categories

| Category | Count | Pattern IDs |
|----------|-------|------------|
| Storage | 6 | omv-003, omv-004, omv-005, omv-006, omv-007, omv-008 |
| Network | 5 | omv-009, omv-010, omv-011, omv-012, omv-013 |
| Services | 4 | omv-001, omv-014, omv-015, omv-016, omv-017 |
| Performance | 3 | omv-018, omv-019, omv-020 |
| Security | 4 | omv-021, omv-022, omv-023, omv-024 |
| **Total** | **24** | |

---

## Source Analysis

### Where Did These Patterns Come From?

The YAML file appears to be **manually curated** based on:

1. **OMV Community Knowledge**: Common issues reported in OMV forums
2. **System Administration Best Practices**: Standard troubleshooting procedures
3. **Real-World Experience**: Practical solutions for OMV deployments
4. **OMV Documentation**: Official OMV guides and references

### Evidence of Manual Curation

- **Specific Commands**: Real Linux/OMV commands (e.g., `systemctl status smbd`, `mdadm --detail`)
- **Realistic Scenarios**: Actual problems users encounter
- **Practical Solutions**: Step-by-step troubleshooting procedures
- **Confidence Scores**: Manually assigned (0.75-0.95 range)
- **Related Patterns**: Cross-references between related issues

### Not Auto-Generated

The patterns are **NOT** auto-generated because:
- They contain domain-specific knowledge (OMV-specific commands)
- They have realistic confidence scores based on reliability
- They include practical diagnostic steps
- They reference OMV-specific tools and procedures
- They show human judgment in categorization and relationships

---

## Conversion Strategy

### Option 1: Keep YAML (Recommended for OMV Co-Pilot Standalone)

**Pros**:
- No conversion needed
- YAML is human-readable
- Easy to edit manually
- Works with existing OMV Co-Pilot code

**Cons**:
- Inconsistent with Expertise Scanner (uses JSON)
- Requires YAML parser in Generic Framework
- Not portable to other systems

**When to Use**: If keeping OMV Co-Pilot as standalone system

---

### Option 2: Convert to JSON (Recommended for Generic Framework)

**Pros**:
- Consistent with Expertise Scanner
- JSON is universal format
- Easier to integrate with Generic Framework
- Better for web APIs
- Portable across systems

**Cons**:
- One-time conversion effort
- Need to update OMV Co-Pilot code to use JSON

**When to Use**: If integrating OMV into Generic Framework

---

## Conversion Process

### Step 1: Create JSON Schema

```json
{
  "id": "omv_001",
  "domain": "omv",
  "name": "SMB share inaccessible from Windows",
  "pattern_type": "troubleshooting",
  "description": "Troubleshoot SMB share access issues from Windows clients",
  "problem": "Windows cannot access \\\\server\\share",
  "solution": "Check SMB service status and firewall rules",
  "category": "services",
  "symptoms": ["Windows cannot access \\\\server\\share", ...],
  "triggers": ["smb not working", ...],
  "diagnostics": [
    {
      "name": "Check SMB service status",
      "command": "systemctl status smbd",
      "expected_output": "active (running)"
    }
  ],
  "solutions": [
    {
      "priority": 1,
      "action": "Restart SMB service",
      "command": "systemctl restart smbd",
      "explanation": "Service may be hung"
    }
  ],
  "related_patterns": [],
  "prerequisites": [],
  "alternatives": [],
  "confidence": 0.9,
  "sources": [],
  "tags": ["smb", "windows", "network", "services"],
  "examples": []
}
```

### Step 2: Conversion Script

```python
import yaml
import json
from pathlib import Path

def convert_yaml_to_json():
    # Load YAML
    with open('patterns/manual.yaml') as f:
        data = yaml.safe_load(f)
    
    # Convert each pattern
    for pattern in data['patterns']:
        json_pattern = {
            'id': pattern['pattern_id'].replace('-', '_'),
            'domain': 'omv',
            'name': pattern['title'],
            'pattern_type': 'troubleshooting',
            'description': f"Troubleshoot: {pattern['title']}",
            'problem': pattern['symptoms'][0] if pattern['symptoms'] else '',
            'solution': pattern['solutions'][0]['action'] if pattern['solutions'] else '',
            'category': pattern['category'],
            'symptoms': pattern['symptoms'],
            'triggers': pattern['triggers'],
            'diagnostics': pattern['diagnostics'],
            'solutions': pattern['solutions'],
            'related_patterns': pattern['related_patterns'],
            'prerequisites': [],
            'alternatives': [],
            'confidence': pattern['confidence'],
            'sources': pattern['references'],
            'tags': [pattern['category']] + pattern['triggers'][:3],
            'examples': []
        }
        
        # Save to JSON
        output_path = f"expertise_scanner/data/patterns/omv/{pattern['pattern_id']}.json"
        with open(output_path, 'w') as f:
            json.dump(json_pattern, f, indent=2)
```

### Step 3: Storage Location

**Current**: `patterns/manual.yaml` (single file)

**After Conversion**: `expertise_scanner/data/patterns/omv/` (24 JSON files)
- `omv_001.json`
- `omv_002.json`
- ... (one file per pattern)

### Step 4: Update Code

**OMV Co-Pilot** (if keeping standalone):
- Update `src/omv_copilot/knowledge/knowledge_base.py` to read JSON instead of YAML
- Change pattern loading from YAML parser to JSON parser

**Generic Framework** (if integrating):
- OMV domain already uses JSON-based knowledge base
- Patterns automatically available through Expertise Scanner

---

## Recommendation

### For Current Refactoring (Generic Framework Integration)

**Recommended Approach**: Convert to JSON

**Rationale**:
1. **Consistency**: Matches Expertise Scanner format
2. **Portability**: Can be used by any domain
3. **Scalability**: Easier to manage 24 individual files than one large YAML
4. **Integration**: Works seamlessly with Generic Framework
5. **Future-Proof**: Aligns with unified architecture

**Implementation Steps**:
1. Create conversion script (Python)
2. Run conversion to generate 24 JSON files
3. Store in `expertise_scanner/data/patterns/omv/`
4. Update OMV domain to load from JSON
5. Delete `patterns/manual.yaml` (or archive)

### Timeline

- **Immediate**: Keep YAML as-is (no breaking changes)
- **Phase 1**: Create conversion script and test
- **Phase 2**: Run conversion and verify all patterns
- **Phase 3**: Update OMV domain code
- **Phase 4**: Archive YAML file

---

## Pattern Quality Assessment

### Strengths

1. **Comprehensive Coverage**: 24 patterns across 5 categories
2. **Practical Solutions**: Real commands and procedures
3. **Good Confidence Scores**: Realistic reliability metrics (0.75-0.95)
4. **Cross-References**: Related patterns linked together
5. **Diagnostic Steps**: Clear troubleshooting procedures
6. **Priority Ordering**: Solutions ordered by priority

### Areas for Enhancement

1. **Examples**: No concrete examples provided
2. **References**: Most patterns have empty references
3. **Prerequisites**: No prerequisite patterns defined
4. **Alternatives**: No alternative solutions listed
5. **Tags**: Could be more granular
6. **Descriptions**: Could be more detailed

### Suggested Improvements

```yaml
# Add to each pattern:
examples:
  - "Example 1: SMB share on NAS not accessible"
  - "Example 2: Windows 10 cannot see network share"

references:
  - "https://forum.openmediavault.org/..."
  - "https://wiki.openmediavault.org/..."

prerequisites:
  - "omv-009"  # Network interface must be working

alternatives:
  - "omv-014"  # NFS as alternative to SMB
```

---

## Conclusion

### Current State
- **24 manually curated OMV troubleshooting patterns**
- **YAML format** (human-readable, OMV Co-Pilot specific)
- **High quality** with realistic commands and solutions
- **Well-organized** by category and relationships

### Conversion Decision
- **Recommended**: Convert to JSON for Generic Framework integration
- **Effort**: Low (automated script)
- **Benefit**: Unified architecture, portability, scalability
- **Timeline**: Can be done in Phase 2 of refactoring

### Next Steps
1. Decide on conversion timing
2. Create and test conversion script
3. Verify all 24 patterns convert correctly
4. Update OMV domain code
5. Archive YAML file for reference
