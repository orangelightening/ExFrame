"""
Tao - Knowledge Cartography Subsystem

Stores, analyzes, and visualizes learning journeys through query/response history.

Tao (道) represents the transformation between questions (Yin) and answers (Yang).
It provides a complete subsystem for knowledge mapping separate from ExFrame's core
query/response processing.

## Components

- **storage**: Persistent storage for query/response history with compression
- **analysis**: Analysis modules (sessions, chains, relations, concepts, depth)
- **api**: FastAPI router with REST endpoints for knowledge analysis
- **cli**: Command-line tools for exploring query history
- **frontend**: Web UI for interactive knowledge visualization

## Usage

### Python API

```python
from tao.storage import load_history
from tao.analysis import sessions, concepts

# Load query history
history = load_history('my_domain')

# Find exploration sessions
session_list = sessions.find_sessions(history, gap_minutes=30)

# Get top concepts
top_concepts = concepts.get_top_concepts(history, top_n=10)
```

### REST API

All analysis tools are available via REST API at `/api/tao/*`:

- `GET /api/tao/sessions/{domain}` - Get exploration sessions
- `GET /api/tao/concepts/{domain}` - Get top concepts
- `GET /api/tao/depth/{domain}` - Get deep explorations
- `GET /api/tao/chains/{domain}/{entry_id}` - Get query chain
- `GET /api/tao/related/{domain}/{entry_id}` - Find related queries

### Web UI

Access the Tao analysis interface at: `http://localhost:5001/tao`

### CLI Tools

```bash
# View sessions
python -m tao.cli.show_sessions peter

# View history
python -m tao.cli.view_history peter --limit 10

# Trace query chain
python -m tao.cli.trace_chain peter --entry 5
```

## Architecture

Tao is a standalone subsystem that:
- Receives Q/R pairs from ExFrame via `save_query_response()`
- Stores them in compressed format (`query_history.json.gz`)
- Provides multiple analysis views (sessions, concepts, depth, etc.)
- Exposes both programmatic and web interfaces

This separation allows ExFrame to focus on answering questions while Tao
handles all knowledge mapping and analysis.

## Version

Phase 2a: Sessions, chains, relations, concepts, depth analysis
"""

__version__ = "2.0.0"

# Export main interfaces
from .storage import get_kcart, KnowledgeCartography, load_history
from .analysis import sessions, chains, relations, concepts, depth

__all__ = [
    # Storage
    "get_kcart",
    "KnowledgeCartography",
    "load_history",
    # Analysis modules
    "sessions",
    "chains",
    "relations",
    "concepts",
    "depth",
]
