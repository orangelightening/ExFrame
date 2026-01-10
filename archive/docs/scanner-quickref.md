# Expertise Scanner - Quick Reference

## Project Snapshot

**What:** General-purpose pattern extraction and knowledge mapping system
**Where:** `/home/peter/development/eeframe/expertise_scanner/`
**Duration:** 6 weeks
**Scope:** 6 domains, 500+ patterns, 20+ universal patterns

---

## Quick Commands

```bash
# Navigate to project
cd /home/peter/development/eeframe/expertise_scanner

# Start API server (development)
uvicorn src.api.main:app --reload --port 8889

# Start frontend (development)
cd frontend
npm run dev

# Run tests
pytest tests/

# Ingest from URL
python -m scripts.ingest_domain --url https://example.com --domain cooking

# Migrate OMV patterns
python -m scripts.migrate_omv

# Rebuild knowledge graph
python -m scripts.rebuild_graph

# Analyze cross-domain
python -m scripts.analyze_cross_domain

# Export patterns
python -m scripts.export_patterns --format json --output patterns.json
```

---

## Directory Quick-Look

```
expertise_scanner/
├── src/api/              # FastAPI endpoints (main.py starts here)
├── src/ingestion/        # Scraping and data collection
├── src/extraction/       # Pattern extraction logic
├── src/knowledge/        # Knowledge graph management
├── src/validation/       # Quality assurance
├── src/llm/             # GLM-4.7 integration
├── src/domains/         # Domain-specific scrapers
├── data/patterns/       # JSON pattern files
├── data/knowledge_graph/ # Graph exports
├── data/citations/      # Source attributions
├── data/raw/           # Raw scraped data
├── frontend/           # React UI
└── tests/               # Test suite
```

---

## Pattern JSON Structure

```json
{
  "id": "omv_001",
  "title": "RAID Array Degraded",
  "category": "Storage",
  "domain": "omv",
  "symptoms": ["array shows degraded"],
  "triggers": ["smartctl reports failure"],
  "diagnostics": {
    "commands": ["cat /proc/mdstat"],
    "checks": ["verify drive count"]
  },
  "solutions": [
    {
      "action": "Replace failed drive",
      "priority": 1,
      "reasoning": "Must replace to restore redundancy"
    }
  ],
  "metadata": {
    "confidence": 0.95,
    "complexity": 4,
    "source": "manual",
    "version": "1.0"
  },
  "relationships": {
    "relates_to": ["omv_002"],
    "component_of": [],
    "alternative_to": []
  }
}
```

---

## API Endpoints Quick-Look

```
Patterns:
  GET  /api/patterns/                    # Get all patterns
  GET  /api/patterns/?domain=omv         # Filter by domain
  GET  /api/patterns/{pattern_id}         # Get specific pattern
  GET  /api/patterns/domains/list        # List all domains
  POST /api/patterns/                    # Create pattern
  PUT  /api/patterns/{pattern_id}        # Update pattern

Ingestion:
  POST /api/ingest/url                   # Ingest from URL
  GET  /api/ingest/jobs/{job_id}         # Check job status

Cross-Domain:
  GET  /api/cross-domain/universal-patterns         # Get universal patterns
  GET  /api/cross-domain/similar/{pattern_id}        # Find similar patterns
```

---

## Week 1 Tasks at a Glance

### Day 1: Backup & Isolate
```bash
# Create legacy backup
cd /home/peter/development/eeframe
cp -r omv_copilot omv_copilot_backup_$(date +%Y%m%d)

# Create legacy directory
mkdir -p omv_copilot_legacy
cp -r omv_copilot_backup_$(date +%Y%m%d)/* omv_copilot_legacy/

# Create documentation
# (use scripts in scanner-design.md)
```

### Day 2-3: Migrate OMV Patterns
```bash
cd expertise_scanner

# Run migration script
python -m scripts.migrate_omv

# Verify output
ls -la data/patterns/omv/
# Should see: patterns.json, migration_report.json
```

### Day 3-4: Build Knowledge Graph
```bash
# Extract OMV knowledge
python -m scripts.extract_omv_knowledge

# Verify output
ls -la data/knowledge_graph/
# Should see: omv_graph.json
```

### Day 4-5: Create API
```bash
# Start API server
uvicorn src.api.main:app --reload --port 8889

# Test endpoint
curl http://localhost:8889/api/patterns/?domain=omv

# Should see: 24 OMV patterns
```

### Day 6-7: Testing
```bash
# Run tests
pytest tests/test_migration.py
pytest tests/test_api.py

# All should pass
```

---

## Environment Variables

```bash
# GLM-4.7 API Key (required)
export GLM_API_KEY="your-key-here"

# API Port (default: 8889)
export SCANNER_API_PORT=8889

# Log Level (default: INFO)
export LOG_LEVEL=INFO

# Python Environment
export PYTHON_ENV=development
```

---

## Common Issues

### GLM API Key Not Found
```bash
# Check environment
echo $GLM_API_KEY

# Set in .env file
echo "GLM_API_KEY=your-key-here" > .env
```

### Pattern File Not Found
```bash
# Check pattern directory
ls -la data/patterns/

# Re-run migration
python -m scripts.migrate_omv
```

### API Not Responding
```bash
# Check if running
ps aux | grep uvicorn

# Check logs
tail -f logs/api.log

# Restart server
uvicorn src.api.main:app --reload --port 8889
```

---

## File Locations

```
Configuration:
  config/settings.yaml       # Main settings
  config/domains.yaml       # Domain configs
  config/prompts.yaml       # LLM prompts

Patterns:
  data/patterns/omv/patterns.json
  data/patterns/cooking/patterns.json
  data/patterns/python/patterns.json
  ...

Knowledge Graphs:
  data/knowledge_graph/omv_graph.json
  data/knowledge_graph/cooking_graph.json
  ...

Citations:
  data/citations/omv/sources.json
  data/citations/cooking/sources.json
  ...

Logs:
  logs/api.log
  logs/ingestion.log
  logs/extraction.log
  logs/llm.log
```

---

## Pattern Extraction Examples

### Cooking: Substitution Pattern
```json
{
  "id": "cooking_045",
  "title": "Butter Substitutions",
  "category": "Substitutions",
  "solutions": [
    {"action": "Use olive oil", "priority": 1},
    {"action": "Use coconut oil", "priority": 2},
    {"action": "Use applesauce (baking only)", "priority": 3}
  ]
}
```

### Python: Error Handling Pattern
```json
{
  "id": "python_089",
  "title": "ImportError Handling",
  "category": "Error Handling",
  "solutions": [
    {"action": "Install missing package (pip install)", "priority": 1},
    {"action": "Check virtual environment", "priority": 2},
    {"action": "Verify Python path", "priority": 3}
  ]
}
```

### DIY: Diagnostic Pattern
```json
{
  "id": "diy_012",
  "title": "Water Leak Diagnosis",
  "category": "Diagnostics",
  "diagnostics": {
    "checks": ["Check visible pipes", "Check water meter", "Check ceilings"]
  },
  "solutions": [
    {"action": "Tighten loose connections", "priority": 1},
    {"action": "Replace faulty valve", "priority": 2},
    {"action": "Call plumber", "priority": 3}
  ]
}
```

---

## Cross-Domain Pattern Example

```json
{
  "id": "universal_progressive_isolation",
  "name": "Progressive Isolation",
  "domains_applied": ["omv", "cooking", "python", "diy"],
  "domain_variants": {
    "omv": {
      "example": "When server is slow, isolate to CPU, RAM, I/O, or network",
      "confidence": 0.92
    },
    "cooking": {
      "example": "When dish is bland, isolate to salt, acid, heat, or time",
      "confidence": 0.88
    }
  },
  "core_principle": "Divide and conquer - systematically test components"
}
```

---

## Testing Commands

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_ingestion.py

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_ingestion.py::test_url_scraper

# Run in verbose mode
pytest -v tests/
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/pattern-extractor

# Make changes
git add .
git commit -m "Add pattern extractor"

# Push to origin
git push origin feature/pattern-extractor

# Create pull request
# (via GitHub web interface)
```

---

## LLM Integration

```python
# Use GLM-4.7 for pattern extraction
from src.llm.client import GLMClient

client = GLMClient()

# Extract patterns from text
patterns = client.extract_patterns(
    text="If the sauce is too thick, add water gradually",
    domain="cooking"
)

# Analyze cross-domain patterns
universal = client.find_universal_patterns(
    domains=["omv", "cooking", "python"]
)
```

---

## Dashboard Access

```
Frontend: http://localhost:3001
API:      http://localhost:8889
Grafana:  http://localhost:3000
```

---

## Quick Tips

1. **Start Small**: Test with 5-10 patterns before scaling
2. **Check Logs**: Always check logs when something fails
3. **Use Tests**: Write tests as you go
4. **Back Up Often**: Use git for version control
5. **Document**: Add comments to complex code
6. **Monitor GLM Usage**: Track API calls and costs
7. **Validate Patterns**: Use the validation layer

---

## Emergency Commands

```bash
# Stop all services
docker-compose down

# Restart API
pkill -f uvicorn
uvicorn src.api.main:app --reload --port 8889

# Clear all patterns (DESTRUCTIVE)
rm -rf data/patterns/*

# Rebuild everything from scratch
python -m scripts.migrate_omv
python -m scripts.ingest_domain --domain cooking
python -m scripts.rebuild_graph

# Restore from backup
cp -r omv_copilot_backup_YYYYMMDD/* omv_copilot/
```

---

## Contact

**Peter**: Project lead, final decisions
**GLM-4.7 #1**: Architecture and design (this file)
**GLM-4.7 #2**: Implementation and coding

---

## Progress Tracking

Use this checklist:

```
Week 1:
  [ ] Legacy OMV preserved
  [ ] OMV patterns migrated
  [ ] Knowledge graph created
  [ ] API endpoints working
  [ ] Frontend adapted
  [ ] Tests passing

Week 2:
  [ ] URL scraper built
  [ ] Cooking patterns extracted
  [ ] Cross-domain analysis
  [ ] 2-3 universal patterns

Week 3:
  [ ] Stack Overflow integrated
  [ ] Python patterns extracted
  [ ] Cross-domain updated
  [ ] 5+ universal patterns

Week 4:
  [ ] Transcript parser built
  [ ] DIY patterns extracted
  [ ] Cross-domain updated
  [ ] 10+ universal patterns

Week 5:
  [ ] Pattern matching working
  [ ] Universal detection working
  [ ] Confidence scoring
  [ ] 15+ universal patterns

Week 6:
  [ ] 6 domains complete
  [ ] 500+ patterns
  [ ] 20+ universal patterns
  [ ] UI polished
  [ ] Demo ready
```

---

**Good luck!** 🚀
