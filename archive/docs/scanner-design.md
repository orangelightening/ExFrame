# Expertise Scanner - Construction Plan

## General-Purpose Pattern Extraction and Knowledge Mapping System

---

## Project Overview

**Goal:** Build a tool that scans any well-documented domain, extracts expertise patterns, maps relationships between them, and discovers universal patterns across domains.

**Scope:** 6-week construction timeline, 6 domains (OMV, Cooking, Python, DIY, First Aid, Gardening), 500+ patterns, 20+ universal patterns.

**Approach:** Tool-first, content-second. The scanner is the product - domains are demonstrations.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Directory Structure](#directory-structure)
3. [Migration Plan](#migration-plan)
4. [Legacy Preservation](#legacy-preservation)
5. [Data Models](#data-models)
6. [API Design](#api-design)
7. [Week-by-Week Construction](#week-by-week-construction)
8. [Testing Strategy](#testing-strategy)
9. [Deployment](#deployment)
10. [Success Criteria](#success-criteria)

---

## System Architecture

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Domain       │  │ Pattern      │  │ Cross-Domain │         │
│  │ Explorer     │  │ Browser      │  │ Analysis     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                    API LAYER (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Pattern      │  │ Cross-       │  │ Ingestion    │         │
│  │ Endpoints    │  │ Domain       │  │ Endpoints    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Pattern      │  │ Knowledge    │  │ Cross-       │         │
│  │ Engine       │  │ Graph        │  │ Domain       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Ingestion    │  │ Validation   │  │ Confidence   │         │
│  │ Pipeline     │  │ Engine       │  │ Scoring      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    EXTRACTION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ URL          │  │ PDF          │  │ LLM          │         │
│  │ Scraper      │  │ Parser       │  │ Analyzer     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Pattern      │  │ Problem-     │  │ Decision     │         │
│  │ Extractor    │  │ Solution     │  │ Detector     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    STORAGE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Pattern      │  │ Knowledge    │  │ Citation     │         │
│  │ Store (JSON) │  │ Graph        │  │ Database     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Ingestion Pipeline
- **URL Scraper**: Fetch web content (HTML, text, API responses)
- **PDF Parser**: Extract text from PDF documents
- **Transcript Parser**: Process video/audio transcripts (future)
- **API Client**: Connect to Stack Overflow, Reddit, GitHub APIs

#### 2. Extraction Engine
- **Pattern Extractor**: Identify problem-solution patterns
- **Procedure Parser**: Extract step-by-step procedures
- **Decision Detector**: Find if/then branches and decision points
- **LLM Analyzer**: Use GLM-4.7 to identify complex patterns

#### 3. Knowledge Engine
- **Pattern Store**: JSON-based pattern database
- **Knowledge Graph**: NetworkX graph of pattern relationships
- **Cross-Domain Analyzer**: Discover universal patterns
- **Confidence Scorer**: Rate pattern reliability

#### 4. Validation Layer
- **Duplicate Detector**: Identify similar patterns
- **Consistency Checker**: Validate pattern structure
- **Source Verification**: Check citation quality
- **Quality Scorer**: Assess overall pattern value

---

## Directory Structure

### Full Project Structure

```
/home/peter/development/eeframe/
│
├── expertise_scanner/                    # NEW: Scanner system
│   ├── src/
│   │   ├── api/                          # FastAPI endpoints
│   │   │   ├── __init__.py
│   │   │   ├── main.py                   # FastAPI app
│   │   │   ├── routes/
│   │   │   │   ├── patterns.py          # Pattern CRUD
│   │   │   │   ├── ingestion.py         # Data ingestion
│   │   │   │   ├── cross_domain.py      # Cross-domain analysis
│   │   │   │   └── visualization.py     # Graph data exports
│   │   │   └── models/
│   │   │       ├── requests.py          # API request models
│   │   │       └── responses.py         # API response models
│   │   │
│   │   ├── ingestion/                    # Data collection
│   │   │   ├── __init__.py
│   │   │   ├── url_scraper.py           # Web scraping
│   │   │   ├── pdf_parser.py            # PDF extraction
│   │   │   ├── api_client.py            # Stack Overflow, Reddit, etc.
│   │   │   └── transcript_parser.py     # Video/audio (future)
│   │   │
│   │   ├── extraction/                   # Pattern extraction
│   │   │   ├── __init__.py
│   │   │   ├── pattern_extractor.py     # Main extraction logic
│   │   │   ├── problem_solution.py      # Q&A pattern detection
│   │   │   ├── procedure_parser.py      # Step-by-step extraction
│   │   │   ├── decision_finder.py       # Decision point detection
│   │   │   └── llm_analyzer.py          # GLM-4.7 analysis
│   │   │
│   │   ├── knowledge/                    # Knowledge management
│   │   │   ├── __init__.py
│   │   │   ├── pattern_store.py         # Pattern storage (JSON)
│   │   │   ├── knowledge_graph.py       # NetworkX graph
│   │   │   ├── cross_domain_analyzer.py # Universal pattern discovery
│   │   │   └── confidence_scorer.py     # Pattern reliability scoring
│   │   │
│   │   ├── validation/                   # Quality assurance
│   │   │   ├── __init__.py
│   │   │   ├── duplicate_detector.py    # Find similar patterns
│   │   │   ├── consistency_checker.py   # Validate pattern structure
│   │   │   ├── source_verifier.py       # Check citation quality
│   │   │   └── quality_scorer.py        # Assess pattern value
│   │   │
│   │   ├── llm/                          # GLM-4.7 integration
│   │   │   ├── __init__.py
│   │   │   ├── client.py                # GLM API client
│   │   │   ├── prompts.py               # Extraction prompts
│   │   │   └── response_parser.py       # Parse LLM responses
│   │   │
│   │   ├── utils/                        # Shared utilities
│   │   │   ├── __init__.py
│   │   │   ├── logger.py                # Logging setup
│   │   │   ├── config.py                # Configuration management
│   │   │   ├── helpers.py               # Helper functions
│   │   │   └── exceptions.py            # Custom exceptions
│   │   │
│   │   └── domains/                      # Domain-specific modules
│   │       ├── __init__.py
│   │       ├── base.py                  # Base domain class
│   │       ├── omv/                     # OMV domain
│   │       │   ├── __init__.py
│   │       │   ├── scraper.py
│   │       │   └── patterns.py
│   │       ├── cooking/                 # Cooking domain
│   │       │   ├── __init__.py
│   │       │   ├── scraper.py
│   │       │   └── patterns.py
│   │       ├── python/                  # Python/Stack Overflow
│   │       │   ├── __init__.py
│   │       │   ├── scraper.py
│   │       │   └── patterns.py
│   │       ├── diy/                      # DIY/Home Repair
│   │       │   ├── __init__.py
│   │       │   ├── scraper.py
│   │       │   └── patterns.py
│   │       ├── first_aid/               # First Aid/Medicine
│   │       │   ├── __init__.py
│   │       │   ├── scraper.py
│   │       │   └── patterns.py
│   │       └── gardening/               # Gardening
│   │           ├── __init__.py
│   │           ├── scraper.py
│   │           └── patterns.py
│   │
│   ├── data/                            # Data storage
│   │   ├── patterns/                    # Extracted patterns (JSON)
│   │   │   ├── universal/
│   │   │   ├── omv/
│   │   │   ├── cooking/
│   │   │   ├── python/
│   │   │   ├── diy/
│   │   │   ├── first_aid/
│   │   │   └── gardening/
│   │   ├── knowledge_graph/             # Graph exports
│   │   ├── citations/                   # Source attributions
│   │   └── raw/                         # Raw scraped data
│   │
│   ├── logs/                            # Application logs
│   │
│   ├── config/                          # Configuration files
│   │   ├── settings.yaml               # Main settings
│   │   ├── domains.yaml                 # Domain configurations
│   │   ├── prompts.yaml                 # LLM prompts
│   │   └── api_keys.yaml                # API keys (gitignored)
│   │
│   ├── tests/                           # Test suite
│   │   ├── __init__.py
│   │   ├── test_ingestion.py
│   │   ├── test_extraction.py
│   │   ├── test_knowledge.py
│   │   └── test_api.py
│   │
│   ├── scripts/                         # Utility scripts
│   │   ├── migrate_omv.py              # Migrate from legacy OMV
│   │   ├── ingest_domain.py            # Ingest new domain
│   │   ├── analyze_cross_domain.py      # Cross-domain analysis
│   │   ├── export_patterns.py          # Export patterns
│   │   └── rebuild_graph.py            # Rebuild knowledge graph
│   │
│   ├── frontend/                        # React UI (shared or new)
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── DomainExplorer.tsx
│   │   │   │   ├── PatternBrowser.tsx
│   │   │   │   ├── CrossDomainView.tsx
│   │   │   │   ├── PatternGraph.tsx
│   │   │   │   └── IngestionPanel.tsx
│   │   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Domains.tsx
│   │   │   ├── Patterns.tsx
│   │   │   └── CrossDomain.tsx
│   │   │   └── utils/
│   │   │       ├── api.ts
│   │   │       └── types.ts
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   ├── README.md
│   ├── requirements.txt
│   ├── docker-compose.yml
│   └── .env.example
│
├── omv_copilot_legacy/                  # PRESERVED: Legacy OMV system
│   ├── README.md                        # Documentation of original
│   ├── ORIGINAL_STRUCTURE.txt           # What was preserved
│   ├── BACKUP_NOTES.md                   # How to restore if needed
│   └── [Full backup of original system]
│
└── omv_copilot/                         # Current working OMV system
    ├── [Remains untouched during migration]
    └── [Continues to work normally]
```

---

## Migration Plan

### Phase 1: Backup and Isolate (Week 1 Day 1)

**Goal:** Safely preserve the legacy OMV system before any changes.

```bash
# 1. Create legacy backup
cd /home/peter/development/eeframe
cp -r omv_copilot omv_copilot_backup_$(date +%Y%m%d)

# 2. Create isolated legacy directory
mkdir -p omv_copilot_legacy
cp -r omv_copilot_backup_$(date +%Y%m%d)/* omv_copilot_legacy/

# 3. Document the original state
cat > omv_copilot_legacy/README.md << 'EOF'
# Legacy OMV Copilot System

## Backup Date
$(date)

## Original Structure
This is a complete backup of the OMV Co-Pilot system as it existed
before migration to the Expertise Scanner framework.

## Original Components
- src/omv_copilot/ - OMV-specific code
- patterns/manual.yaml - 24 OMV patterns
- src/config/ - Configuration files
- src/prompts/ - LLM prompts for OMV
- data/knowledge/ - Stored knowledge
- data/history/ - Decision history
- frontend/ - React UI (OMV-specific)

## How This Will Be Migrated
- Patterns → expertise_scanner/data/patterns/omv/
- Knowledge → expertise_scanner/data/knowledge_graph/
- Frontend → Adapted for multi-domain use
- API → Extended for cross-domain analysis

## Restoration
If needed, this backup can be restored by:
1. Stop current omv_copilot service
2. Copy contents back to omv_copilot/
3. Restart service

## Important Notes
- The legacy system is fully functional as-is
- Migration does not delete this backup
- Current omv_copilot/ continues working during migration
- Migration is additive, not destructive
EOF

# 4. Create original structure documentation
tree -L 3 omv_copilot_legacy/ > omv_copilot_legacy/ORIGINAL_STRUCTURE.txt

# 5. Create backup notes
cat > omv_copilot_legacy/BACKUP_NOTES.md << 'EOF'
# OMV Co-Pilot Legacy Backup Notes

## What Was Backed Up
- Complete source code
- All configuration files
- Pattern definitions
- Stored knowledge
- Decision history
- Frontend code
- Environment files

## What Was NOT Backed Up
- Docker volumes (separate backup)
- Temporary files
- Build artifacts
- Node modules (reinstallable)

## Verification Commands
# Check directory structure
ls -la omv_copilot_legacy/

# Verify key files exist
ls omv_copilot_legacy/patterns/
ls omv_copilot_legacy/src/omv_copilot/

# Count patterns
grep -c "^- id:" omv_copilot_legacy/patterns/manual.yaml

## Migration Process
See migration plan in scanner-design.md

## Rollback Process
1. Stop expertise_scanner services
2. Copy omv_copilot_legacy/* to omv_copilot/
3. Restart services
4. Verify OMV functionality
EOF
```

### Phase 2: Extract OMV Patterns (Week 1 Day 2-3)

**Goal:** Migrate OMV patterns from YAML to new JSON structure.

```python
# scripts/migrate_omv.py

import yaml
import json
from pathlib import Path
from datetime import datetime

def migrate_omv_patterns():
    """Migrate OMV patterns from legacy YAML to new JSON structure."""

    # Load legacy patterns
    legacy_file = Path("/home/peter/development/eeframe/omv_copilot_legacy/patterns/manual.yaml")
    with open(legacy_file, 'r') as f:
        legacy_data = yaml.safe_load(f)

    # New pattern structure
    migrated_patterns = []

    for pattern in legacy_data.get('patterns', []):
        migrated = {
            "id": f"omv_{pattern['id']}",
            "title": pattern['title'],
            "category": pattern['category'],
            "domain": "omv",
            "symptoms": pattern.get('symptoms', []),
            "triggers": pattern.get('triggers', []),
            "diagnostics": {
                "commands": pattern.get('diagnostics', {}).get('commands', []),
                "checks": pattern.get('diagnostics', {}).get('checks', [])
            },
            "solutions": [
                {
                    "action": sol['action'],
                    "priority": sol.get('priority', 5),
                    "reasoning": sol.get('reasoning', '')
                }
                for sol in pattern.get('solutions', [])
            ],
            "metadata": {
                "confidence": pattern.get('confidence', 0.8),
                "complexity": pattern.get('complexity', 3),
                "migrated_from": "manual.yaml",
                "migrated_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "relationships": {
                "relates_to": pattern.get('related_patterns', []),
                "component_of": [],
                "alternative_to": []
            }
        }
        migrated_patterns.append(migrated)

    # Save to new location
    output_dir = Path("/home/peter/development/eeframe/expertise_scanner/data/patterns/omv")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "patterns.json"
    with open(output_file, 'w') as f:
        json.dump(migrated_patterns, f, indent=2)

    # Generate migration report
    report = {
        "migration_date": datetime.now().isoformat(),
        "source": str(legacy_file),
        "destination": str(output_file),
        "patterns_migrated": len(migrated_patterns),
        "categories": set(p['category'] for p in migrated_patterns),
        "success": True
    }

    report_file = output_dir / "migration_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Migrated {len(migrated_patterns)} OMV patterns")
    print(f"Output: {output_file}")
    print(f"Report: {report_file}")

    return migrated_patterns

if __name__ == "__main__":
    migrate_omv_patterns()
```

### Phase 3: Extract OMV Knowledge (Week 1 Day 3-4)

**Goal:** Migrate existing knowledge base to new graph structure.

```python
# scripts/extract_omv_knowledge.py

import json
from pathlib import Path

def extract_omv_knowledge():
    """Extract OMV knowledge from legacy system."""

    # Load migrated patterns
    patterns_file = Path("/home/peter/development/eeframe/expertise_scanner/data/patterns/omv/patterns.json")
    with open(patterns_file, 'r') as f:
        patterns = json.load(f)

    # Build knowledge graph structure
    knowledge_graph = {
        "nodes": [],
        "edges": []
    }

    # Create pattern nodes
    for pattern in patterns:
        node = {
            "id": pattern['id'],
            "type": "pattern",
            "domain": "omv",
            "properties": {
                "title": pattern['title'],
                "category": pattern['category'],
                "confidence": pattern['metadata']['confidence'],
                "complexity": pattern['metadata']['complexity']
            }
        }
        knowledge_graph["nodes"].append(node)

    # Create category nodes
    categories = set(p['category'] for p in patterns)
    for category in categories:
        node = {
            "id": f"omv_category_{category.lower().replace(' ', '_')}",
            "type": "category",
            "domain": "omv",
            "properties": {
                "name": category
            }
        }
        knowledge_graph["nodes"].append(node)

    # Create edges
    for pattern in patterns:
        # Pattern to category
        edge = {
            "source": pattern['id'],
            "target": f"omv_category_{pattern['category'].lower().replace(' ', '_')}",
            "type": "belongs_to",
            "properties": {}
        }
        knowledge_graph["edges"].append(edge)

        # Pattern to related patterns
        for related in pattern['relationships']['relates_to']:
            edge = {
                "source": pattern['id'],
                "target": f"omv_{related}",
                "type": "relates_to",
                "properties": {}
            }
            knowledge_graph["edges"].append(edge)

    # Save knowledge graph
    output_dir = Path("/home/peter/development/eeframe/expertise_scanner/data/knowledge_graph")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "omv_graph.json"
    with open(output_file, 'w') as f:
        json.dump(knowledge_graph, f, indent=2)

    print(f"Created OMV knowledge graph with {len(knowledge_graph['nodes'])} nodes")
    print(f"Output: {output_file}")

    return knowledge_graph

if __name__ == "__main__":
    extract_omv_knowledge()
```

### Phase 4: Adapt Frontend (Week 1 Day 4-5)

**Goal:** Modify React UI to support multi-domain viewing while preserving OMV functionality.

```typescript
// expertise_scanner/frontend/src/utils/types.ts

export interface Pattern {
  id: string;
  title: string;
  category: string;
  domain: string;
  symptoms: string[];
  triggers: string[];
  diagnostics: {
    commands: string[];
    checks: string[];
  };
  solutions: Solution[];
  metadata: {
    confidence: number;
    complexity: number;
    migrated_from?: string;
    migrated_at?: string;
    version: string;
  };
  relationships: {
    relates_to: string[];
    component_of: string[];
    alternative_to: string[];
  };
}

export interface Domain {
  id: string;
  name: string;
  description: string;
  pattern_count: number;
  source_urls: string[];
}

export interface KnowledgeGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  id: string;
  type: 'pattern' | 'category' | 'universal_pattern';
  domain: string;
  properties: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}
```

```typescript
// expertise_scanner/frontend/src/components/DomainExplorer.tsx

import React, { useState, useEffect } from 'react';
import { Domain } from '../utils/types';

export const DomainExplorer: React.FC = () => {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);

  useEffect(() => {
    // Fetch domains from API
    fetchDomains();
  }, []);

  const fetchDomains = async () => {
    try {
      const response = await fetch('/api/domains');
      const data = await response.json();
      setDomains(data);
    } catch (error) {
      console.error('Failed to fetch domains:', error);
    }
  };

  return (
    <div className="domain-explorer">
      <h2>Domains</h2>
      <div className="domain-grid">
        {domains.map(domain => (
          <div
            key={domain.id}
            className={`domain-card ${selectedDomain?.id === domain.id ? 'selected' : ''}`}
            onClick={() => setSelectedDomain(domain)}
          >
            <h3>{domain.name}</h3>
            <p>{domain.pattern_count} patterns</p>
          </div>
        ))}
      </div>

      {selectedDomain && (
        <div className="domain-details">
          <h3>{selectedDomain.name}</h3>
          <p>{selectedDomain.description}</p>
          {/* Add pattern browser for selected domain */}
        </div>
      )}
    </div>
  );
};
```

### Phase 5: Create API Layer (Week 1 Day 5)

**Goal:** Build FastAPI endpoints for multi-domain pattern management.

```python
# expertise_scanner/src/api/routes/patterns.py

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
from pathlib import Path

router = APIRouter(prefix="/api/patterns", tags=["patterns"])

DATA_DIR = Path("/home/peter/development/eeframe/expertise_scanner/data")

@router.get("/")
async def get_patterns(
    domain: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100
):
    """Get patterns with optional filtering."""
    patterns = []

    if domain:
        pattern_file = DATA_DIR / "patterns" / domain / "patterns.json"
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                patterns = json.load(f)
    else:
        # Load from all domains
        for domain_dir in (DATA_DIR / "patterns").iterdir():
            if domain_dir.is_dir():
                pattern_file = domain_dir / "patterns.json"
                if pattern_file.exists():
                    with open(pattern_file, 'r') as f:
                        patterns.extend(json.load(f))

    # Filter by category
    if category:
        patterns = [p for p in patterns if p['category'] == category]

    # Limit results
    patterns = patterns[:limit]

    return {"patterns": patterns, "count": len(patterns)}

@router.get("/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get a specific pattern by ID."""
    # Parse pattern ID to determine domain
    parts = pattern_id.split('_', 1)
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid pattern ID")

    domain = parts[0]
    pattern_file = DATA_DIR / "patterns" / domain / "patterns.json"

    if not pattern_file.exists():
        raise HTTPException(status_code=404, detail="Domain not found")

    with open(pattern_file, 'r') as f:
        patterns = json.load(f)

    pattern = next((p for p in patterns if p['id'] == pattern_id), None)

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    return pattern

@router.get("/domains/list")
async def get_domains():
    """Get list of all domains."""
    domains = []
    patterns_dir = DATA_DIR / "patterns"

    for domain_dir in patterns_dir.iterdir():
        if domain_dir.is_dir():
            pattern_file = domain_dir / "patterns.json"
            count = 0
            if pattern_file.exists():
                with open(pattern_file, 'r') as f:
                    count = len(json.load(f))

            domains.append({
                "id": domain_dir.name,
                "name": domain_dir.name.title(),
                "pattern_count": count
            })

    return {"domains": domains}
```

### Phase 6: Testing and Verification (Week 1 Day 6-7)

**Goal:** Verify migration was successful and system works.

```python
# tests/test_migration.py

import pytest
import json
from pathlib import Path

def test_omv_patterns_migrated():
    """Verify OMV patterns were migrated successfully."""
    pattern_file = Path("/home/peter/development/eeframe/expertise_scanner/data/patterns/omv/patterns.json")
    assert pattern_file.exists(), "OMV patterns file not found"

    with open(pattern_file, 'r') as f:
        patterns = json.load(f)

    assert len(patterns) == 24, f"Expected 24 patterns, found {len(patterns)}"
    assert all('id' in p for p in patterns), "Missing pattern IDs"
    assert all('domain' in p for p in patterns), "Missing domain field"
    assert all(p['domain'] == 'omv' for p in patterns), "Incorrect domain"

def test_omv_graph_created():
    """Verify OMV knowledge graph was created."""
    graph_file = Path("/home/peter/development/eeframe/expertise_scanner/data/knowledge_graph/omv_graph.json")
    assert graph_file.exists(), "OMV graph file not found"

    with open(graph_file, 'r') as f:
        graph = json.load(f)

    assert 'nodes' in graph, "Missing nodes"
    assert 'edges' in graph, "Missing edges"
    assert len(graph['nodes']) > 0, "Graph has no nodes"

def test_legacy_preserved():
    """Verify legacy system is intact."""
    legacy_dir = Path("/home/peter/development/eeframe/omv_copilot_legacy")
    assert legacy_dir.exists(), "Legacy directory not found"

    pattern_file = legacy_dir / "patterns" / "manual.yaml"
    assert pattern_file.exists(), "Legacy patterns not found"

def test_api_responds():
    """Test API responds to pattern requests."""
    import requests

    response = requests.get("http://localhost:8888/api/patterns/?domain=omv")
    assert response.status_code == 200

    data = response.json()
    assert 'patterns' in data
    assert 'count' in data
```

---

## Legacy Preservation

### What Is Preserved

```
omv_copilot_legacy/
├── [Complete source code]
├── [All configuration files]
├── [Pattern definitions in YAML]
├── [Knowledge base]
├── [Decision history]
├── [Frontend code]
├── [Environment files]
├── README.md (original)
├── MIGRATION_DOCUMENTATION.md (new)
└── BACKUP_NOTES.md (new)
```

### Accessing Legacy System

If you ever need to run the legacy system:

```bash
# 1. Stop scanner services
docker-compose -f expertise_scanner/docker-compose.yml down

# 2. Restore legacy to working directory
cp -r omv_copilot_legacy/* omv_copilot/

# 3. Start legacy system
cd omv_copilot
docker-compose up -d

# 4. Verify it works
curl http://localhost:8888/health
```

### Documentation for Legacy System

Create comprehensive documentation in the legacy directory:

```markdown
# Legacy OMV Co-Pilot System Documentation

## Original Design
The OMV Co-Pilot was designed as a single-domain decision support
system for OpenMediaVault server management.

## Key Components
- Pattern-based knowledge base (24 patterns)
- SSH-based data collection from OMV server
- AI consultation via GLM-4.7
- Web dashboard (React)
- CLI tool with Rich formatting

## Limitations of Original Design
- Single domain (OMV only)
- No cross-domain analysis
- No pattern extraction pipeline
- Manual pattern creation only

## Why We're Migrating
To build a general-purpose expertise scanner that:
- Works on any domain
- Extracts patterns automatically
- Discovers cross-domain insights
- Scales to 500+ patterns

## How to Restore
1. Stop expertise_scanner services
2. Copy omv_copilot_legacy/* to omv_copilot/
3. Restart services
4. Verify OMV functionality

## Known Issues
None. The legacy system is stable and functional.
```

---

## Data Models

### Pattern Model

```json
{
  "id": "omv_001",
  "title": "RAID Array Degraded",
  "category": "Storage",
  "domain": "omv",
  "symptoms": [
    "RAID array shows degraded status",
    "One or more drives missing from array"
  ],
  "triggers": [
    "Smartctl reports drive failure",
    "Drive disappears from system"
  ],
  "diagnostics": {
    "commands": [
      "cat /proc/mdstat",
      "mdadm --detail /dev/md0",
      "smartctl -a /dev/sda"
    ],
    "checks": [
      "Verify drive count in array",
      "Check drive health status",
      "Identify failed drive"
    ]
  },
  "solutions": [
    {
      "action": "Replace failed drive and rebuild array",
      "priority": 1,
      "reasoning": "Failed drive must be replaced to restore redundancy"
    }
  ],
  "metadata": {
    "confidence": 0.95,
    "complexity": 4,
    "source": "manual",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "migrated_from": "manual.yaml",
    "migrated_at": "2024-01-04T12:00:00Z",
    "version": "1.0"
  },
  "relationships": {
    "relates_to": ["omv_002", "omv_003"],
    "component_of": [],
    "alternative_to": []
  }
}
```

### Universal Pattern Model

```json
{
  "id": "universal_progressive_isolation",
  "name": "Progressive Isolation",
  "description": "Systematically eliminate possibilities until the cause is isolated",
  "domains_applied": ["omv", "cooking", "python", "diy", "first_aid", "gardening"],
  "domain_variants": {
    "omv": {
      "example": "When server is slow, isolate to CPU, RAM, I/O, or network",
      "confidence": 0.92,
      "source_patterns": ["omv_015", "omv_016", "omv_017"]
    },
    "cooking": {
      "example": "When dish is bland, isolate to salt, acid, heat, or time",
      "confidence": 0.88,
      "source_patterns": ["cooking_045", "cooking_056", "cooking_078"]
    }
  },
  "core_principle": "Divide and conquer - systematically test components",
  "applicability": "High - applies to all troubleshooting scenarios",
  "complexity": 3,
  "metadata": {
    "discovered_at": "2024-01-15T00:00:00Z",
    "verified": true,
    "verification_sources": ["omv", "cooking", "python", "diy"],
    "confidence": 0.90
  }
}
```

### Domain Model

```json
{
  "id": "omv",
  "name": "OpenMediaVault",
  "description": "Network-attached storage management and troubleshooting",
  "pattern_count": 24,
  "source_urls": [
    "https://forum.openmediavault.org/",
    "https://openmediavault.readthedocs.io/"
  ],
  "scraping_config": {
    "enabled": true,
    "forums": true,
    "documentation": true,
    "last_scrape": "2024-01-04T00:00:00Z"
  },
  "categories": [
    "Storage",
    "Network",
    "Services",
    "Performance",
    "Security"
  ]
}
```

---

## API Design

### Pattern Endpoints

```yaml
GET /api/patterns/
  Query Parameters:
    - domain: string (optional) - Filter by domain
    - category: string (optional) - Filter by category
    - limit: integer (default: 100) - Max results to return
  Response:
    - patterns: array
    - count: integer

GET /api/patterns/{pattern_id}
  Path Parameters:
    - pattern_id: string
  Response:
    - pattern: object

GET /api/patterns/domains/list
  Response:
    - domains: array of domain objects

POST /api/patterns/
  Body:
    - pattern: object
  Response:
    - pattern_id: string
    - created_at: timestamp

PUT /api/patterns/{pattern_id}
  Path Parameters:
    - pattern_id: string
  Body:
    - pattern: object
  Response:
    - updated_at: timestamp
```

### Ingestion Endpoints

```yaml
POST /api/ingest/url
  Body:
    - url: string
    - domain: string
    - extract_patterns: boolean (default: true)
  Response:
    - job_id: string
    - status: "queued" | "processing" | "completed" | "failed"

GET /api/ingest/jobs/{job_id}
  Path Parameters:
    - job_id: string
  Response:
    - status: string
    - progress: integer (0-100)
    - patterns_extracted: integer
    - errors: array
```

### Cross-Domain Endpoints

```yaml
GET /api/cross-domain/universal-patterns
  Query Parameters:
    - min_domains: integer (default: 2) - Minimum domains to qualify
  Response:
    - patterns: array of universal pattern objects
    - count: integer

GET /api/cross-domain/similar/{pattern_id}
  Path Parameters:
    - pattern_id: string
  Query Parameters:
    - similarity_threshold: float (default: 0.7)
  Response:
    - similar_patterns: array
    - domain: array
```

---

## Week-by-Week Construction

### Week 1: Foundation & OMV Migration

**Goal:** Build core infrastructure and migrate OMV system.

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Backup and isolate legacy OMV system | omv_copilot_legacy/ directory |
| 2 | Create directory structure for expertise scanner | Full directory tree |
| 3 | Migrate OMV patterns to JSON structure | patterns/omv/patterns.json |
| 4 | Build OMV knowledge graph | knowledge_graph/omv_graph.json |
| 5 | Create FastAPI endpoints for patterns | Working API on port 8889 |
| 6 | Adapt React frontend for multi-domain | Working UI showing OMV patterns |
| 7 | Testing and verification | All tests passing |

### Week 2: Ingestion Pipeline & Cooking Domain

**Goal:** Build data ingestion and add cooking domain.

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | URL scraper implementation | ingestion/url_scraper.py |
| 2 | Pattern extractor for recipes | extraction/pattern_extractor.py |
| 3 | Scrape 100 recipes from food blog | raw/cooking/ directory |
| 4 | Extract substitution patterns | patterns/cooking/substitutions.json |
| 5 | Extract troubleshooting patterns | patterns/cooking/troubleshooting.json |
| 6 | Build cooking knowledge graph | knowledge_graph/cooking_graph.json |
| 7 | Cross-domain analysis (OMV + Cooking) | cross_domain/omv_cooking.json |

### Week 3: Python/Stack Overflow Domain

**Goal:** Add Python programming domain with API integration.

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Stack Overflow API client | ingestion/api_client.py |
| 2 | Query top 100 Python questions | raw/python/ directory |
| 3 | Extract error-handling patterns | patterns/python/error_handling.json |
| 4 | Extract debugging patterns | patterns/python/debugging.json |
| 5 | Extract performance patterns | patterns/python/performance.json |
| 6 | Build Python knowledge graph | knowledge_graph/python_graph.json |
| 7 | Cross-domain analysis (OMV + Cooking + Python) | Updated cross-domain patterns |

### Week 4: DIY/Home Repair Domain

**Goal:** Add DIY domain with transcript parsing.

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Transcript parser for videos | ingestion/transcript_parser.py |
| 2 | Scrape This Old House transcripts | raw/diy/ directory |
| 3 | Extract diagnostic patterns | patterns/diy/diagnostics.json |
| 4 | Extract tool selection patterns | patterns/diy/tools.json |
| 5 | Extract safety patterns | patterns/diy/safety.json |
| 6 | Build DIY knowledge graph | knowledge_graph/diy_graph.json |
| 7 | Cross-domain analysis update | 4 domains compared |

### Week 5: Pattern Discovery Engine

**Goal:** Build universal pattern discovery and confidence scoring.

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Pattern similarity algorithm | cross_domain/pattern_matcher.py |
| 2 | Universal pattern detection | cross_domain/universal_detector.py |
| 3 | Confidence scoring system | knowledge/confidence_scorer.py |
| 4 | Apply to all 4 domains | 20+ universal patterns found |
| 5 | Pattern clustering | duplicate_detector.py |
| 6 | Pattern evolution tracking | evolution_tracker.py |
| 7 | Visualization exports | Graph JSON files for UI |

### Week 6: Polish & Demonstrate

**Goal:** Add remaining domains, polish UI, final testing.

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | First Aid domain (Red Cross) | patterns/first_aid/ complete |
| 2 | Gardening domain (extension guides) | patterns/gardening/ complete |
| 3 | Cross-domain final analysis | All 6 domains integrated |
| 4 | UI improvements | "What else uses this pattern?" feature |
| 5 | Export and archival features | JSON export, CSV export |
| 6 | Final testing | All tests passing, demo ready |
| 7 | Documentation and deployment | README complete, deployed |

---

## Testing Strategy

### Unit Tests

```python
# tests/test_ingestion.py

def test_url_scraper():
    """Test URL scraper functionality."""
    scraper = URLScraper()
    content = scraper.scrape("https://example.com/recipe")
    assert content is not None
    assert len(content) > 0

def test_pdf_parser():
    """Test PDF parser."""
    parser = PDFParser()
    text = parser.parse("test.pdf")
    assert text is not None
    assert len(text) > 0

def test_pattern_extractor():
    """Test pattern extraction."""
    extractor = PatternExtractor()
    text = "If the sauce is too thick, add water gradually"
    patterns = extractor.extract(text)
    assert len(patterns) > 0
    assert all('solution' in p for p in patterns)
```

### Integration Tests

```python
# tests/test_integration.py

def test_full_ingestion_pipeline():
    """Test complete ingestion from URL to patterns."""
    # Scrape URL
    scraper = URLScraper()
    content = scraper.scrape("https://example.com/recipe")

    # Extract patterns
    extractor = PatternExtractor()
    patterns = extractor.extract(content)

    # Save patterns
    store = PatternStore()
    store.save("cooking", patterns)

    # Verify
    retrieved = store.load("cooking")
    assert len(retrieved) == len(patterns)

def test_cross_domain_analysis():
    """Test cross-domain pattern discovery."""
    # Load patterns from multiple domains
    omv_patterns = load_patterns("omv")
    cooking_patterns = load_patterns("cooking")

    # Find universal patterns
    analyzer = CrossDomainAnalyzer()
    universal = analyzer.find_universal([omv_patterns, cooking_patterns])

    assert len(universal) > 0
```

### End-to-End Tests

```python
# tests/test_e2e.py

def test_api_ingestion_to_ui():
    """Test from API ingestion to UI display."""
    # Trigger ingestion
    response = client.post("/api/ingest/url", json={
        "url": "https://example.com/recipe",
        "domain": "cooking"
    })
    job_id = response.json()["job_id"]

    # Wait for completion
    wait_for_job(job_id)

    # Verify patterns appear in UI
    response = client.get("/api/patterns/?domain=cooking")
    patterns = response.json()["patterns"]
    assert len(patterns) > 0
```

---

## Deployment

### Development Environment

```yaml
# docker-compose.yml

version: '3.8'

services:
  expertise-scanner-api:
    build: ./expertise_scanner
    ports:
      - "8889:8000"
    volumes:
      - ./expertise_scanner/data:/app/data
      - ./expertise_scanner/logs:/app/logs
    environment:
      - GLM_API_KEY=${GLM_API_KEY}
      - PYTHON_ENV=development
    depends_on:
      - redis

  expertise-scanner-frontend:
    build: ./expertise_scanner/frontend
    ports:
      - "3001:3000"
    environment:
      - VITE_API_URL=http://localhost:8889

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./expertise_scanner/config/grafana:/etc/grafana
```

### Production Considerations

1. **Environment Variables**
   - `GLM_API_KEY`: GLM-4.7 API key
   - `PYTHON_ENV`: development | production
   - `LOG_LEVEL`: DEBUG | INFO | WARNING | ERROR

2. **Database**
   - No database for MVP (JSON storage)
   - Consider SQLite or PostgreSQL for scale
   - Consider Neo4j for advanced graph queries

3. **Caching**
   - Redis for job queue
   - Cache API responses
   - Cache knowledge graph queries

4. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Log aggregation

---

## Success Criteria

### Week 1 Success
- [ ] Legacy OMV system preserved
- [ ] OMV patterns migrated to new structure
- [ ] Knowledge graph created for OMV
- [ ] API endpoints working
- [ ] Frontend showing OMV patterns
- [ ] All tests passing

### Week 2 Success
- [ ] URL scraper working
- [ ] Cooking patterns extracted (50+)
- [ ] Cooking knowledge graph created
- [ ] Cross-domain analysis (OMV + Cooking)
- [ ] 2-3 universal patterns identified

### Week 3 Success
- [ ] Stack Overflow API integrated
- [ ] Python patterns extracted (100+)
- [ ] Python knowledge graph created
- [ ] Cross-domain analysis updated
- [ ] 5+ universal patterns identified

### Week 4 Success
- [ ] Transcript parser working
- [ ] DIY patterns extracted (75+)
- [ ] DIY knowledge graph created
- [ ] Cross-domain analysis updated
- [ ] 10+ universal patterns identified

### Week 5 Success
- [ ] Pattern similarity algorithm working
- [ ] Universal pattern detection working
- [ ] Confidence scoring working
- [ ] 15+ universal patterns across 4 domains
- [ ] Pattern clustering working

### Week 6 Success (Final)
- [ ] 6 domains complete (OMV, Cooking, Python, DIY, First Aid, Gardening)
- [ ] 500+ total patterns
- [ ] 20+ universal patterns
- [ ] UI with cross-domain exploration
- [ ] "What else uses this pattern?" feature
- [ ] Export functionality (JSON, CSV)
- [ ] Complete documentation
- [ ] All tests passing
- [ ] Demo-ready

---

## Summary

This plan provides:

1. **Clear Structure**: Well-organized directory layout
2. **Safe Migration**: Legacy system preserved
3. **Data Models**: Explicit pattern and graph schemas
4. **API Design**: RESTful endpoints for all functionality
5. **Week-by-Week**: Concrete deliverables each week
6. **Testing**: Comprehensive test strategy
7. **Success Criteria**: Measurable goals each week

The system will be:
- **General-purpose**: Works on any domain
- **Extensible**: Easy to add new domains
- **Scalable**: Handles 500+ patterns efficiently
- **User-friendly**: Intuitive web interface
- **Well-tested**: Comprehensive test coverage

The Expertise Scanner is ready to build!
