"""
Generic Framework API - FastAPI backend for web interface.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.factory import DomainFactory
from core.domain import DomainConfig
from core.generic_domain import GenericDomain  # NEW: Use GenericDomain
from assist.engine import GenericAssistantEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    domain: Optional[str] = "llm_consciousness"
    context: Optional[Dict[str, Any]] = None
    include_trace: Optional[bool] = False


class SpecialistConfig(BaseModel):
    specialist_id: str
    name: str
    description: str
    expertise_keywords: List[str]
    expertise_categories: List[str]
    confidence_threshold: float = 0.6


class DomainCreate(BaseModel):
    domain_id: str
    domain_name: str
    description: str
    categories: List[str]
    tags: List[str]
    specialists: List[SpecialistConfig]
    storage_path: Optional[str] = None


class DomainUpdate(BaseModel):
    domain_name: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    specialists: Optional[List[SpecialistConfig]] = None


class QueryResponse(BaseModel):
    query: str
    response: str
    specialist: Optional[str]
    patterns_used: List[str]
    confidence: float
    timestamp: str
    domain: str
    processing_time_ms: Optional[int] = None
    trace: Optional[Dict[str, Any]] = None


class DomainInfo(BaseModel):
    domain_id: str
    domain_name: str
    patterns_loaded: int
    specialists: List[str]
    categories: List[str]


# Create FastAPI app
app = FastAPI(
    title="Generic Assistant Framework",
    description="Domain-agnostic expertise assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from built React app
frontend_dist_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_path / "assets")), name="assets")

# Global state
engines: Dict[str, GenericAssistantEngine] = {}


def get_storage_path(domain_id: str) -> str:
    """
    Get the storage path for a domain's patterns.

    Uses environment variable PATTERN_STORAGE_BASE if set, otherwise falls back
    to /app/data/patterns for Docker or development path. This allows the app
    to work both in Docker and in development environments.
    """
    # Check if running in Docker (APP_HOME env var is set)
    if os.getenv("APP_HOME"):
        base = "/app/data/patterns"
    else:
        base = os.getenv("PATTERN_STORAGE_BASE",
                         "/home/peter/development/eeframe/data/patterns")
    return str(Path(base) / domain_id)


def get_domain_registry_path() -> Path:
    """Get the path to the domain registry file."""
    base = os.getenv("DOMAIN_REGISTRY_PATH",
                     str(Path(__file__).parent.parent / "data"))
    return Path(base) / "domains.json"


@app.on_event("startup")
async def startup_event():
    """
    Auto-discover and load all domains dynamically.

    NO MORE MANUAL DOMAIN REGISTRATION!
    Domains are discovered automatically from the filesystem.
    """
    # Get the patterns directory directly
    if os.getenv("APP_HOME"):
        patterns_dir = Path("/app/data/patterns")
    else:
        patterns_dir = Path(os.getenv("PATTERN_STORAGE_BASE",
                                        "/home/peter/development/eeframe/data/patterns"))

    logger.info(f"Auto-discovering domains from: {patterns_dir}")

    # Track what we loaded
    loaded_domains = []
    failed_domains = []

    # Iterate through domain directories
    for domain_dir in patterns_dir.iterdir():
        if not domain_dir.is_dir():
            continue

        domain_id = domain_dir.name
        patterns_file = domain_dir / "patterns.json"

        # Check if patterns.json exists (required)
        if not patterns_file.exists():
            logger.debug(f"Skipping {domain_id}: no patterns.json found")
            continue

        try:
            # Create domain configuration
            config = DomainConfig(
                domain_id=domain_id,
                domain_name=f"Auto-loaded: {domain_id}",
                version="1.0.0",
                description=f"Dynamically loaded domain: {domain_id}",
                pattern_storage_path=str(domain_dir),
                pattern_format="json",
                pattern_schema=None,
                categories=[],
                tags=[]
            )

            # Create GenericDomain (no custom class needed!)
            domain = GenericDomain(config)
            await domain.initialize()

            # Create engine
            engine = GenericAssistantEngine(domain)
            await engine.initialize()

            # Store engine
            engines[domain_id] = engine

            loaded_domains.append({
                "domain_id": domain_id,
                "domain_name": domain.domain_name,
                "patterns": len(domain.knowledge_base._patterns) if domain.knowledge_base else 0,
                "specialists": len(domain.list_specialists())
            })

            logger.info(f"✓ Loaded domain: {domain_id} ({domain.domain_name})")

        except Exception as e:
            failed_domains.append({"domain_id": domain_id, "error": str(e)})
            logger.error(f"✗ Failed to load domain {domain_id}: {e}")

    # Log summary
    logger.info(f"=" * 60)
    logger.info(f"Domain Loading Complete:")
    logger.info(f"  Loaded: {len(loaded_domains)} domains")
    logger.info(f"  Failed: {len(failed_domains)} domains")

    if loaded_domains:
        logger.info(f"\nActive Domains:")
        for domain in loaded_domains:
            logger.info(f"  - {domain['domain_id']}: {domain['patterns']} patterns, {domain['specialists']} specialists")

    if failed_domains:
        logger.warning(f"\nFailed Domains:")
        for domain in failed_domains:
            logger.warning(f"  - {domain['domain_id']}: {domain['error']}")

    logger.info(f"=" * 60)

    # Initialize domain registry
    await _initialize_domain_registry(loaded_domains)


async def _initialize_domain_registry(loaded_domains: List[Dict[str, Any]]) -> None:
    """Initialize or update domain registry with loaded domains."""
    registry = _load_domain_registry()

    for domain_info in loaded_domains:
        domain_id = domain_info["domain_id"]

        if domain_id not in registry["domains"]:
            # Create new registry entry
            registry["domains"][domain_id] = {
                "domain_id": domain_id,
                "domain_name": domain_info["domain_name"],
                "description": f"Dynamically loaded domain",
                "version": "1.0.0",
                "storage_path": get_storage_path(domain_id),
                "pattern_format": "json",
                "categories": [],
                "tags": [],
                "specialists": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

    _save_domain_registry(registry)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    for engine in engines.values():
        await engine.domain.cleanup()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend HTML from built React app."""
    # Try to serve from built dist folder first
    html_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if html_path.exists():
        with open(html_path) as f:
            return f.read()
    
    # Fallback to old location for development
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        with open(html_path) as f:
            return f.read()
    
    return """
    <html>
    <head><title>Generic Assistant Framework</title></head>
    <body>
        <h1>Generic Assistant Framework</h1>
        <p>Frontend not found. Please check the frontend directory.</p>
    </body>
    </html>
    """


# SPA catch-all route removed - using simple Alpine.js UI instead


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {
        "status": "healthy",
        "service": "EEFrame - Expertise Framework",
        "version": "1.0.0",
        "domains_loaded": len(engines),
        "domains": list(engines.keys())
    }


@app.get("/api/domains")
async def list_domains() -> Dict[str, Any]:
    """List available domains."""
    return {
        "domains": list(engines.keys()),
        "default": "llm_consciousness"
    }


@app.get("/api/domains/{domain_id}")
async def get_domain_info(domain_id: str) -> DomainInfo:
    """Get information about a domain."""
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]
    status = await engine.get_domain_status()

    return DomainInfo(
        domain_id=status["domain"],
        domain_name=status["domain_name"],
        patterns_loaded=status["patterns_loaded"],
        specialists=status["specialists_available"],
        categories=status["categories"]
    )


@app.get("/api/domains/{domain_id}/specialists")
async def list_specialists(domain_id: str) -> Dict[str, Any]:
    """List specialists in a domain."""
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]

    specialists_info = []
    for spec_id in engine.domain.list_specialists():
        specialist = engine.domain.get_specialist(spec_id)
        if specialist:
            # Plugins have keywords, categories as instance attributes
            # Try to get description from config or use name as fallback
            description = ""
            if hasattr(specialist, 'config'):
                description = specialist.config.get('description', '')
            if not description:
                description = specialist.name

            specialists_info.append({
                "id": specialist.specialist_id,
                "name": specialist.name,
                "description": description,
                "keywords": specialist.keywords if hasattr(specialist, 'keywords') else [],
                "categories": specialist.categories if hasattr(specialist, 'categories') else []
            })

    return {
        "domain": domain_id,
        "specialists": specialists_info
    }


@app.get("/api/domains/{domain_id}/patterns")
async def list_patterns(domain_id: str, category: Optional[str] = None) -> Dict[str, Any]:
    """List patterns in a domain."""
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]
    kb = engine.knowledge_base

    # Ensure patterns are loaded
    await kb.load_patterns()

    # Get patterns - try to use async method if available, otherwise use sync method
    if category:
        # For category filtering, we need to use the sync method
        # Check if KB has get_patterns_by_category method
        if hasattr(kb, 'get_patterns_by_category'):
            patterns = kb.get_patterns_by_category(category)
        else:
            # Fallback to search
            patterns = await kb.search(query=category or "", limit=100)
    else:
        # Get all patterns - try async method first
        if hasattr(kb, 'get_all_patterns'):
            patterns = await kb.get_all_patterns(limit=100)
        elif hasattr(kb, 'get_patterns_by_category'):
            patterns = kb.get_patterns_by_category(None)
        else:
            # Last resort: search with a broad query
            patterns = await kb.search(query="", limit=100)

    return {
        "domain": domain_id,
        "category": category,
        "count": len(patterns),
        "patterns": [
            {
                "id": p.get("id") or p.get("pattern_id"),
                "name": p.get("name"),
                "type": p.get("type") or p.get("pattern_type"),
                "description": p.get("description"),
                "tags": p.get("tags", [])
            }
            for p in patterns[:50]  # Limit to 50 for performance
        ]
    }


@app.get("/api/domains/{domain_id}/patterns/{pattern_id}")
async def get_pattern_detail(domain_id: str, pattern_id: str) -> Dict[str, Any]:
    """Get full details of a specific pattern."""
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]
    kb = engine.knowledge_base

    # Ensure patterns are loaded
    await kb.load_patterns()

    # Find the pattern by ID using the KB plugin interface method
    pattern = await kb.get_by_id(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    return pattern


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """Process a user query."""
    domain_id = request.domain or "llm_consciousness"

    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]

    try:
        result = await engine.process_query(
            request.query,
            request.context,
            include_trace=request.include_trace
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/domains/{domain_id}/health")
async def domain_health(domain_id: str) -> Dict[str, Any]:
    """Get health status of a domain."""
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]
    health = await engine.domain.health_check()

    return {
        "domain": domain_id,
        **health
    }


@app.get("/api/history")
async def get_history(domain: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Get query history."""
    domain_id = domain or "llm_consciousness"

    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]
    history = engine.get_history(limit)

    return {
        "domain": domain_id,
        "count": len(history),
        "history": history
    }


@app.get("/api/traces")
async def get_traces(domain: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """Get recent query traces from memory."""
    domain_id = domain or "llm_consciousness"

    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]
    traces = engine.get_recent_traces(limit)

    return {
        "domain": domain_id,
        "count": len(traces),
        "traces": traces
    }


@app.get("/api/traces/log")
async def get_traces_from_log(limit: int = 50) -> Dict[str, Any]:
    """Get recent query traces from log file (historical)."""
    traces = GenericAssistantEngine.get_trace_from_log(limit)

    return {
        "count": len(traces),
        "traces": traces
    }


@app.get("/api/traces/{query_id}")
async def get_trace_detail(query_id: str) -> Dict[str, Any]:
    """Get detailed trace for a specific query."""
    trace = GenericAssistantEngine.get_trace_for_query(query_id)

    if not trace:
        raise HTTPException(status_code=404, detail=f"Query trace '{query_id}' not found")

    return trace


# ==================== DOMAIN CRUD ENDPOINTS ====================

# Domain registry storage
def _get_registry_file_path() -> Path:
    """Get the registry file path, ensuring parent directories exist."""
    registry_path = get_domain_registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    return registry_path


def _load_domain_registry() -> Dict[str, Any]:
    """Load domain registry from file."""
    registry_path = _get_registry_file_path()
    if registry_path.exists():
        with open(registry_path, 'r') as f:
            return json.load(f)
    return {"domains": {}, "next_id": 1}


def _save_domain_registry(registry: Dict[str, Any]) -> None:
    """Save domain registry to file."""
    registry_path = _get_registry_file_path()
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)


@app.get("/api/admin/domains")
async def list_all_domains() -> Dict[str, Any]:
    """List all domains with full configuration."""
    registry = _load_domain_registry()
    domains_list = []

    for domain_id, domain_config in registry["domains"].items():
        # Get live stats if domain is loaded
        live_stats = {}
        if domain_id in engines:
            status = await engines[domain_id].get_domain_status()
            live_stats = {
                "patterns_loaded": status["patterns_loaded"],
                "queries_processed": len(engines[domain_id].get_history(1000))
            }

        domains_list.append({
            "domain_id": domain_id,
            **domain_config,
            **live_stats,
            "is_loaded": domain_id in engines
        })

    return {
        "domains": domains_list,
        "total": len(domains_list)
    }


@app.get("/api/admin/domains/{domain_id}")
async def get_domain_config(domain_id: str) -> Dict[str, Any]:
    """Get full domain configuration including specialists."""
    registry = _load_domain_registry()

    if domain_id not in registry["domains"]:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    domain_config = registry["domains"][domain_id]

    # Add live specialist data if domain is loaded
    if domain_id in engines:
        engine = engines[domain_id]
        live_specialists = []
        for spec_id in engine.domain.list_specialists():
            spec = engine.domain.get_specialist(spec_id)
            if spec:
                live_specialists.append({
                    "specialist_id": spec.specialist_id,
                    "name": spec.name,
                    "description": spec.config.description,
                    "keywords": spec.config.expertise_keywords,
                    "categories": spec.config.expertise_categories,
                    "confidence_threshold": spec.config.confidence_threshold
                })
        domain_config["specialists"] = live_specialists

    return domain_config


@app.post("/api/admin/domains")
async def create_domain(request: DomainCreate) -> Dict[str, Any]:
    """Create a new domain."""
    registry = _load_domain_registry()

    # Validate domain_id is unique
    if request.domain_id in registry["domains"]:
        raise HTTPException(status_code=400, detail=f"Domain '{request.domain_id}' already exists")

    # Validate domain_id format (alphanumeric and underscore only)
    import re
    if not re.match(r'^[a-z][a-z0-9_]*$', request.domain_id):
        raise HTTPException(
            status_code=400,
            detail="Domain ID must start with a lowercase letter and contain only lowercase letters, numbers, and underscores"
        )

    # Create storage directory
    storage_path = request.storage_path or get_storage_path(request.domain_id)
    Path(storage_path).mkdir(parents=True, exist_ok=True)

    # Create domain config
    domain_config = {
        "domain_id": request.domain_id,
        "domain_name": request.domain_name,
        "description": request.description,
        "version": "1.0.0",
        "categories": request.categories,
        "tags": request.tags,
        "storage_path": storage_path,
        "pattern_format": "json",
        "specialists": [
            {
                "specialist_id": s.specialist_id,
                "name": s.name,
                "description": s.description,
                "keywords": s.expertise_keywords,
                "categories": s.expertise_categories,
                "confidence_threshold": s.confidence_threshold
            }
            for s in request.specialists
        ],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    # Save to registry
    registry["domains"][request.domain_id] = domain_config
    _save_domain_registry(registry)

    return {
        "domain_id": request.domain_id,
        "status": "created",
        "message": f"Domain '{request.domain_name}' created successfully",
        "config": domain_config
    }


@app.put("/api/admin/domains/{domain_id}")
async def update_domain(domain_id: str, request: DomainUpdate) -> Dict[str, Any]:
    """Update an existing domain."""
    registry = _load_domain_registry()

    if domain_id not in registry["domains"]:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    domain_config = registry["domains"][domain_id]

    # Update fields
    if request.domain_name is not None:
        domain_config["domain_name"] = request.domain_name
    if request.description is not None:
        domain_config["description"] = request.description
    if request.categories is not None:
        domain_config["categories"] = request.categories
    if request.tags is not None:
        domain_config["tags"] = request.tags
    if request.specialists is not None:
        domain_config["specialists"] = [
            {
                "specialist_id": s.specialist_id,
                "name": s.name,
                "description": s.description,
                "keywords": s.expertise_keywords,
                "categories": s.expertise_categories,
                "confidence_threshold": s.confidence_threshold
            }
            for s in request.specialists
        ]

    domain_config["updated_at"] = datetime.utcnow().isoformat()

    _save_domain_registry(registry)

    # Reload domain if it's currently loaded
    if domain_id in engines:
        # In production, you'd want to reload the domain here
        pass

    return {
        "domain_id": domain_id,
        "status": "updated",
        "config": domain_config
    }


@app.delete("/api/admin/domains/{domain_id}")
async def delete_domain(domain_id: str) -> Dict[str, Any]:
    """Delete a domain."""
    registry = _load_domain_registry()

    if domain_id not in registry["domains"]:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    domain_config = registry["domains"][domain_id]

    # Unload domain if loaded
    if domain_id in engines:
        await engines[domain_id].domain.cleanup()
        del engines[domain_id]

    # Remove from registry
    del registry["domains"][domain_id]
    _save_domain_registry(registry)

    return {
        "domain_id": domain_id,
        "status": "deleted",
        "message": f"Domain '{domain_config['domain_name']}' deleted successfully"
    }


@app.post("/api/admin/domains/{domain_id}/reload")
async def reload_domain(domain_id: str) -> Dict[str, Any]:
    """Reload a domain (apply configuration changes)."""
    registry = _load_domain_registry()

    if domain_id not in registry["domains"]:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    # Unload if loaded
    if domain_id in engines:
        await engines[domain_id].domain.cleanup()
        del engines[domain_id]

    # TODO: Re-import and initialize the domain
    # This requires dynamic module loading which is complex
    # For now, return a message that server restart is needed

    return {
        "domain_id": domain_id,
        "status": "requires_restart",
        "message": "Domain configuration updated. Server restart required to load changes."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
