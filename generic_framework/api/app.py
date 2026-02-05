#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Generic Framework API - FastAPI backend for web interface.
"""

from fastapi import FastAPI, HTTPException, Response, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.factory import DomainFactory
from core.domain import DomainConfig
from core.generic_domain import GenericDomain  # NEW: Use GenericDomain
from core.universe import UniverseManager, UniverseMergeStrategy
from core.phase1_engine import Phase1Engine  # Phase 1: New simplified engine
from assist.engine import GenericAssistantEngine
from diagnostics.search_metrics import SearchMetrics, SearchTrace, SearchOutcome
from diagnostics.pattern_analyzer import PatternAnalyzer
from diagnostics.health_checker import HealthChecker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    domain: Optional[str] = "llm_consciousness"
    context: Optional[Dict[str, Any]] = None
    include_trace: Optional[bool] = False
    verbose: Optional[bool] = False  # Enable verbose mode with data snapshots
    show_thinking: Optional[bool] = False  # Show step-by-step reasoning before answer
    format: Optional[str] = None  # Output format: json, markdown, compact, table, etc.
    search_patterns: Optional[bool] = None  # Phase 1: Control pattern search (True/False/None=use config)


class ConfirmLLMRequest(BaseModel):
    query: str
    domain: Optional[str] = "llm_consciousness"
    include_trace: Optional[bool] = False
    verbose: Optional[bool] = False  # Enable verbose mode with data snapshots
    format: Optional[str] = None


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
    enrichers: Optional[List[Dict[str, Any]]] = None
    # Domain Type System (Types 1-5)
    domain_type: Optional[str] = None
    # Phase 1: Persona System
    persona: Optional[str] = None
    library_base_path: Optional[str] = None
    enable_pattern_override: Optional[bool] = None
    # Type 1: Creative
    creative_keywords: Optional[str] = None
    # Type 2: Knowledge Retrieval
    similarity_threshold: Optional[float] = None
    max_patterns: Optional[int] = None
    # Type 3: Document Store
    document_store_type: Optional[str] = None
    remote_url: Optional[str] = None
    api_key: Optional[str] = None
    show_sources: Optional[bool] = None
    # Type 4: Analytical
    max_research_steps: Optional[int] = None
    research_timeout: Optional[int] = None
    report_format: Optional[str] = None
    enable_web_search: Optional[bool] = None
    # Type 5: Hybrid
    require_confirmation: Optional[bool] = None
    research_on_fallback: Optional[bool] = None
    # Common to all types
    temperature: Optional[float] = None
    llm_min_confidence: Optional[float] = None


class DomainUpdate(BaseModel):
    domain_name: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    specialists: Optional[List[SpecialistConfig]] = None
    enrichers: Optional[List[Dict[str, Any]]] = None
    # Domain Type System (Types 1-5)
    domain_type: Optional[str] = None
    # Phase 1: Persona System
    persona: Optional[str] = None
    library_base_path: Optional[str] = None
    enable_pattern_override: Optional[bool] = None
    # Type 1: Creative
    creative_keywords: Optional[str] = None
    # Type 2: Knowledge Retrieval
    similarity_threshold: Optional[float] = None
    max_patterns: Optional[int] = None
    # Type 3: Document Store
    document_store_type: Optional[str] = None
    remote_url: Optional[str] = None
    api_key: Optional[str] = None
    show_sources: Optional[bool] = None
    # Type 4: Analytical
    max_research_steps: Optional[int] = None
    research_timeout: Optional[int] = None
    report_format: Optional[str] = None
    enable_web_search: Optional[bool] = None
    # Type 5: Hybrid
    require_confirmation: Optional[bool] = None
    research_on_fallback: Optional[bool] = None
    # Common to all types
    temperature: Optional[float] = None
    llm_min_confidence: Optional[float] = None


class QueryResponse(BaseModel):
    query: str
    response: str
    specialist: Optional[str]
    patterns_used: List[str]
    confidence: float
    timestamp: str
    domain: str
    processing_time_ms: Optional[int] = None
    # State machine trace (new format)
    query_id: Optional[str] = None
    state_machine: Optional[Dict[str, Any]] = None
    # Old trace format (deprecated, use state_machine instead)
    trace: Optional[Dict[str, Any]] = None
    llm_used: Optional[bool] = None
    llm_fallback: Optional[str] = None
    llm_enhancement: Optional[str] = None
    llm_response: Optional[str] = None
    ai_generated: Optional[bool] = None
    # LLM confirmation fields
    requires_confirmation: Optional[bool] = None
    confirmation_message: Optional[str] = None
    partial_response: Optional[Dict[str, Any]] = None
    # Web search extension field
    can_extend_with_web_search: Optional[bool] = None


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

# =============================================================================
# MOUNT AUTONOMOUS LEARNING API
# =============================================================================
# Mount the autonomous learning FastAPI app as a sub-application
# This allows the Surveyor UI to interact with the learning system
try:
    # Add autonomous_learning to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autonomous_learning"))
    from api.app import app as learning_app
    # Mount at /api/learning path
    app.mount("/api/learning", learning_app)
    logger.info("✓ Autonomous Learning API mounted at /api/learning")
except ImportError as e:
    logger.warning(f"✗ Could not mount Autonomous Learning API: {e}")
    logger.info("  Surveyor UI will run in stub mode")
except Exception as e:
    logger.warning(f"✗ Error mounting Autonomous Learning API: {e}")

# =============================================================================
# MOUNT PERSONAS API
# =============================================================================
# Mount the personas API router for persona plugin management
try:
    # Inside container: /app = generic_framework, so use relative import
    from api.personas import router as personas_router
    app.include_router(personas_router)
    logger.info("✓ Personas API router mounted at /api/personas")
except ImportError as e:
    logger.warning(f"✗ Could not mount Personas API: {e}")
except Exception as e:
    logger.warning(f"✗ Error mounting Personas API: {e}")

# =============================================================================
# CLAUDE CODE COMMUNICATION API
# =============================================================================
# Simple HTTP API for communication between Claude Code instances
from fastapi import APIRouter

kilo_router = APIRouter(prefix="/api/kilo")

# In-memory message store (simplest approach)
kilo_messages: List[Dict[str, Any]] = []

class KiloMessage(BaseModel):
    """Message from one Claude Code instance to another."""
    message: str
    sender_id: str
    timestamp: Optional[str] = None

class KiloMessageResponse(BaseModel):
    """Response when sending a message."""
    status: str
    message_id: int
    timestamp: str

@kilo_router.post("/communicate", response_model=KiloMessageResponse)
async def send_message(msg: KiloMessage) -> KiloMessageResponse:
    """
    Receive a message from another Claude Code instance.
    
    This allows Claude Code instances running on the same network to communicate
    with each other via simple HTTP API calls.
    
    Args:
        msg: Message containing text and sender identifier
    
    Returns:
        Confirmation with message ID and timestamp
    """
    msg_dict = msg.dict()
    msg_dict["timestamp"] = datetime.utcnow().isoformat()
    msg_dict["id"] = len(kilo_messages)
    kilo_messages.append(msg_dict)
    
    logger.info(f"[KILO] Received message from {msg.sender_id}: {msg.message[:50]}...")
    
    return KiloMessageResponse(
        status="received",
        message_id=msg_dict["id"],
        timestamp=msg_dict["timestamp"]
    )

@kilo_router.get("/messages")
async def get_messages() -> Dict[str, Any]:
    """
    Get all messages from other Claude Code instances.
    
    Returns:
        List of all received messages
    """
    return {"messages": kilo_messages, "count": len(kilo_messages)}

@kilo_router.delete("/messages")
async def clear_messages() -> Dict[str, Any]:
    """
    Clear all messages from the in-memory store.
    
    Returns:
        Confirmation of cleared messages
    """
    count = len(kilo_messages)
    kilo_messages.clear()
    logger.info(f"[KILO] Cleared {count} messages")
    return {"status": "cleared", "count": count}

# Mount the Claude Code communication router
app.include_router(kilo_router)
logger.info("✓ Claude Code communication API mounted at /api/kilo")

# Mount static files from built React app
frontend_dist_path = Path(__file__).parent.parent / "frontend" / "dist"
frontend_assets_path = frontend_dist_path / "assets"
if frontend_assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_assets_path)), name="assets")

# Global state
engines: Dict[str, GenericAssistantEngine] = {}  # Legacy: for backward compatibility
universe_manager: Optional[UniverseManager] = None  # New: Universe-based architecture


async def _regenerate_domain_embeddings(domain_id: str) -> None:
    """
    Regenerate embeddings for a domain after pattern changes.

    This ensures semantic search stays synchronized when patterns are
    added, updated, or deleted.
    """
    if domain_id not in engines:
        return

    try:
        kb = engines[domain_id].knowledge_base
        if hasattr(kb, 'generate_embeddings'):
            result = await kb.generate_embeddings()
            logger.info(f"[EMBED] Auto-regenerated embeddings for {domain_id}: {result}")
    except Exception as e:
        logger.error(f"[EMBED] Failed to regenerate embeddings for {domain_id}: {e}")


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


def _ensure_writable_permissions(universes_base: Path) -> None:
    """
    Ensure domain JSON files are writable by the container user.

    When files are cloned from git, they may have restrictive permissions (644).
    This fixes permissions to allow the app to write new patterns via AI extension.
    """
    try:
        import stat
        fixed_count = 0

        # Find all domain.json and patterns.json files
        for json_file in universes_base.rglob("*.json"):
            # Skip embeddings.json (large, read-only)
            if "embeddings.json" in str(json_file):
                continue

            try:
                # Get current permissions
                current_mode = json_file.stat().st_mode

                # Check if writable by others (least restrictive check)
                if not (current_mode & stat.S_IWOTH):
                    # Make writable by all (666)
                    json_file.chmod(0o666)
                    fixed_count += 1
            except Exception as e:
                logger.debug(f"Could not fix permissions for {json_file}: {e}")

        # Also ensure directories are writable
        for domain_dir in (universes_base / "MINE" / "domains").iterdir():
            if domain_dir.is_dir():
                try:
                    domain_dir.chmod(0o777)
                except Exception:
                    pass

        if fixed_count > 0:
            logger.info(f"✓ Fixed permissions on {fixed_count} JSON files for AI pattern creation")
    except Exception as e:
        logger.debug(f"Permission fix skipped: {e}")


@app.on_event("startup")
async def startup_event():
    """
    Initialize the ExFrame runtime with UniverseManager.

    Loads the default universe on startup, maintaining backward compatibility
    by populating the legacy engines dictionary.
    """
    global universe_manager, engines

    # Get the universes base path
    if os.getenv("APP_HOME"):
        universes_base = Path("/app/universes")
    else:
        universes_base = Path(os.getenv("UNIVERSES_BASE",
                                        "/home/peter/development/eeframe/universes"))

    logger.info(f"=" * 60)
    logger.info(f"ExFrame Runtime Starting")
    logger.info(f"Universes base: {universes_base}")
    logger.info(f"=" * 60)

    # Fix permissions on universe domain files
    # This ensures files from git clone are writable by the container user
    _ensure_writable_permissions(universes_base)

    # Initialize UniverseManager
    universe_manager = UniverseManager(
        universes_base_path=universes_base,
        default_universe_id="MINE"
    )

    # Load default universe
    try:
        default_universe = await universe_manager.load_default()
        await default_universe.activate()

        # Populate legacy engines dict for backward compatibility
        for domain_id, engine in default_universe.engines.items():
            engines[domain_id] = engine

        logger.info(f"✓ Default universe loaded: {default_universe.universe_id}")
        logger.info(f"  Domains: {', '.join(default_universe.list_domains())}")

        # Get pattern counts
        for domain_id in default_universe.list_domains():
            domain = default_universe.get_domain(domain_id)
            if domain and hasattr(domain, 'knowledge_base') and domain.knowledge_base:
                pattern_count = len(domain.knowledge_base._patterns)
                logger.info(f"    - {domain_id}: {pattern_count} patterns")

    except Exception as e:
        logger.error(f"✗ Failed to load default universe: {e}")
        logger.info(f"  Falling back to legacy domain discovery...")

        # Fallback to legacy loading
        await _legacy_domain_discovery()

    logger.info(f"=" * 60)
    logger.info(f"ExFrame Runtime Ready")
    logger.info(f"=" * 60)


async def _legacy_domain_discovery() -> None:
    """
    Fallback: Legacy domain discovery for backward compatibility.

    This is only used if the universe system fails to initialize.
    """
    global engines

    # Get the patterns directory directly
    if os.getenv("APP_HOME"):
        patterns_dir = Path("/app/data/patterns")
    else:
        patterns_dir = Path(os.getenv("PATTERN_STORAGE_BASE",
                                        "/home/peter/development/eeframe/data/patterns"))

    logger.info(f"Legacy domain discovery from: {patterns_dir}")

    # Track what we loaded
    loaded_domains = []

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

            # Create GenericDomain
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

            logger.info(f"  ✓ Loaded domain: {domain_id}")

        except Exception as e:
            logger.error(f"  ✗ Failed to load domain {domain_id}: {e}")

    # Log summary
    if loaded_domains:
        logger.info(f"  Loaded {len(loaded_domains)} domains via legacy discovery")


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
    # Cleanup universes
    if universe_manager:
        await universe_manager.unload_all()

    # Legacy cleanup
    for engine in engines.values():
        await engine.domain.cleanup()


# =============================================================================
# UNIVERSE MANAGEMENT ENDPOINTS
# =============================================================================

class UniverseCreateRequest(BaseModel):
    """Request to create a new universe."""
    universe_id: str
    name: str
    description: str = ""
    base_on: Optional[str] = None


class UniverseMergeRequest(BaseModel):
    """Request to merge universes."""
    source: str
    target: str
    strategy: str = "merge_patterns"  # source_wins, target_wins, merge, fail


@app.get("/api/universes")
async def list_universes() -> Dict[str, Any]:
    """List all available universes."""
    if not universe_manager:
        return {"universes": [], "loaded": [], "message": "UniverseManager not initialized"}

    available = universe_manager.list_universes()
    loaded = universe_manager.list_loaded_universes()

    # Get metadata for loaded universes
    universes_meta = []
    for universe_id in loaded:
        universe = await universe_manager.get_universe(universe_id)
        if universe:
            meta = universe.get_meta()
            universes_meta.append({
                "universe_id": meta.universe_id,
                "name": meta.name,
                "description": meta.description,
                "state": meta.state.value,
                "domain_count": meta.domain_count,
                "total_patterns": meta.total_patterns,
                "version": meta.version,
                "loaded_at": meta.loaded_at,
                "is_active": meta.state.value == "active"
            })

    return {
        "available": available,
        "loaded": loaded,
        "universes": universes_meta
    }


@app.get("/api/universes/{universe_id}")
async def get_universe_info(universe_id: str) -> Dict[str, Any]:
    """Get information about a specific universe."""
    if not universe_manager:
        raise HTTPException(status_code=503, detail="UniverseManager not initialized")

    universe = await universe_manager.get_universe(universe_id)
    if not universe:
        # Check if universe exists but is not loaded
        if universe_id in universe_manager.list_universes():
            return {
                "universe_id": universe_id,
                "state": "unloaded",
                "message": "Universe exists but is not loaded. Load it first."
            }
        raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found")

    meta = universe.get_meta()
    return {
        "universe_id": meta.universe_id,
        "name": meta.name,
        "description": meta.description,
        "state": meta.state.value,
        "domain_count": meta.domain_count,
        "total_patterns": meta.total_patterns,
        "version": meta.version,
        "created_at": meta.created_at,
        "loaded_at": meta.loaded_at,
        "checksum": meta.checksum,
        "domains": universe.list_domains()
    }


@app.post("/api/universes/{universe_id}/load")
async def load_universe(universe_id: str) -> Dict[str, Any]:
    """Load a universe on-demand."""
    if not universe_manager:
        raise HTTPException(status_code=503, detail="UniverseManager not initialized")

    try:
        universe = await universe_manager.load_universe(universe_id)
        await universe.activate()

        meta = universe.get_meta()
        return {
            "universe_id": universe_id,
            "status": "loaded",
            "state": meta.state.value,
            "domains": universe.list_domains(),
            "message": f"Universe '{universe_id}' loaded successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load universe: {e}")


@app.post("/api/universes")
async def create_universe(request: UniverseCreateRequest) -> Dict[str, Any]:
    """Create a new universe."""
    if not universe_manager:
        raise HTTPException(status_code=503, detail="UniverseManager not initialized")

    try:
        universe = await universe_manager.create_universe(
            universe_id=request.universe_id,
            name=request.name,
            description=request.description,
            base_on=request.base_on
        )

        meta = universe.get_meta()
        return {
            "universe_id": request.universe_id,
            "status": "created",
            "state": meta.state.value,
            "domains": universe.list_domains(),
            "message": f"Universe '{request.universe_id}' created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create universe: {e}")


@app.post("/api/admin/universes/merge")
async def merge_universes(request: UniverseMergeRequest) -> Dict[str, Any]:
    """Merge source universe into target universe."""
    if not universe_manager:
        raise HTTPException(status_code=503, detail="UniverseManager not initialized")

    # Validate strategy
    try:
        strategy = UniverseMergeStrategy(request.strategy)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy: {request.strategy}. Must be one of: source_wins, target_wins, merge_patterns, fail_on_conflict"
        )

    try:
        result = await universe_manager.merge_universes(request.source, request.target, strategy)
        return {
            "status": "merged",
            "result": result,
            "message": f"Merged {result['merged_domains']} domains from {request.source} to {request.target}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to merge universes: {e}")


@app.get("/api/universes/{universe_id}/domains")
async def list_universe_domains(universe_id: str) -> Dict[str, Any]:
    """List domains in a specific universe."""
    if not universe_manager:
        raise HTTPException(status_code=503, detail="UniverseManager not initialized")

    universe = await universe_manager.get_universe(universe_id)
    if not universe:
        raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found")

    domains_info = []
    for domain_id in universe.list_domains():
        domain = universe.get_domain(domain_id)
        if domain:
            pattern_count = len(domain.knowledge_base._patterns) if hasattr(domain, 'knowledge_base') and domain.knowledge_base else 0
            domains_info.append({
                "domain_id": domain_id,
                "domain_name": domain.config.domain_name,
                "patterns": pattern_count,
                "specialists": len(domain.list_specialists())
            })

    return {
        "universe_id": universe_id,
        "domains": domains_info
    }


@app.post("/api/universes/{universe_id}/domains/{domain_id}/query")
async def query_universe_domain(
    universe_id: str,
    domain_id: str,
    request: QueryRequest
) -> Response:
    """
    Process a query in a specific universe.

    This is the universe-aware version of the query endpoint.
    """
    if not universe_manager:
        raise HTTPException(status_code=503, detail="UniverseManager not initialized")

    universe = await universe_manager.get_universe(universe_id)
    if not universe:
        raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found")

    engine = universe.get_engine(domain_id)
    if not engine:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found in universe '{universe_id}'")

    try:
        result = await engine.process_query(
            request.query,
            request.context,
            request.include_trace
        )

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# =============================================================================


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
        "service": "ExFrame - Expertise Framework",
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
                "tags": p.get("tags", []),
                "status": p.get("status", "certified"),  # Include status
                "llm_generated": p.get("llm_generated", False),  # Include llm_generated flag
                "confidence": p.get("confidence", p.get("confidence_score", 0.5)),  # Include confidence
                "confidence_score": p.get("confidence_score", p.get("confidence", 0.5)),  # Include confidence_score
                "times_accessed": p.get("times_accessed", 0)
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


@app.post("/api/patterns")
async def create_pattern(request: Request) -> Dict[str, Any]:
    """
    Create a new pattern from LLM-generated content.

    This endpoint allows users to accept AI-generated knowledge as a new pattern
    in the knowledge base through the query portal. The pattern is immediately
    available for semantic search after creation.

    Expected JSON body:
    {
        "domain": "exframe_methods",
        "name": "Pattern Name",
        "problem": "What question does this answer?",
        "solution": "The answer/content",
        "description": "Brief description",
        "pattern_type": "knowledge",
        "origin": "llm_external_search",
        "origin_query": "original query",
        "llm_generated": true,
        "confidence": 0.8,
        "validated_by": "user_id",
        "validated_at": "2026-01-15T10:00:00Z",
        "validation_method": "query_portal_acceptance",
        "status": "validated",
        "tags": ["external_search", "llm_generated"],
        "code": "def my_function():\\n    return 'hello'"  // Optional executable code
    }
    """
    import time
    from datetime import datetime

    data = await request.json()
    domain_id = data.get("domain")

    if not domain_id:
        raise HTTPException(status_code=400, detail="domain is required")

    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]
    kb = engine.knowledge_base

    # Generate pattern ID if not provided
    import uuid
    pattern_id = data.get("id") or f"{domain_id}_{uuid.uuid4().hex[:8]}"

    # Build the pattern object
    pattern = {
        "id": pattern_id,
        "pattern_id": pattern_id,
        "name": data.get("name", "Untitled Pattern"),
        "domain": domain_id,
        "problem": data.get("problem", ""),
        "solution": data.get("solution", ""),
        "description": data.get("description", ""),
        "pattern_type": data.get("pattern_type", "knowledge"),
        "confidence": data.get("confidence", 0.5),
        "status": data.get("status", "validated"),
        "origin": data.get("origin", "llm_external_search"),
        "origin_query": data.get("origin_query", ""),
        "llm_generated": data.get("llm_generated", True),
        "validated_by": data.get("validated_by", "current_user"),
        "validated_at": data.get("validated_at", datetime.utcnow().isoformat() + "Z"),
        "validation_method": data.get("validation_method", "query_portal_acceptance"),
        "tags": data.get("tags", ["llm_generated"]),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "times_accessed": 0,
        "code": data.get("code")  # Optional executable code
    }

    # Add the pattern to the knowledge base
    try:
        # Use add_pattern method if available
        if hasattr(kb, 'add_pattern'):
            await kb.add_pattern(pattern)
        elif hasattr(kb, 'save_pattern'):
            await kb.save_pattern(pattern)
        else:
            raise HTTPException(status_code=500, detail="Knowledge base does not support adding patterns")

        # Auto-regenerate embeddings to keep search synchronized
        await _regenerate_domain_embeddings(domain_id)

        return {
            "success": True,
            "pattern_id": pattern_id,
            "message": f"Pattern '{pattern['name']}' created successfully",
            "pattern": pattern
        }
    except Exception as e:
        logger.error(f"Failed to create pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create pattern: {str(e)}")


@app.post("/api/query")
async def process_query(request: QueryRequest) -> Response:
    """
    Process a user query (POST method).

    Supports multiple output formats via the `format` parameter:
    - None/missing: Default structured JSON response (backward compatible)
    - "json": Structured JSON with full pattern details
    - "markdown": Human-readable Markdown format
    - "compact": Terminal-friendly compact format
    - "table": Tabular format
    - "json-compact": Minified JSON
    - "ultra-compact": Pattern names only

    Examples:
        curl -X POST http://localhost:3000/api/query \\
          -H "Content-Type: application/json" \\
          -d '{"query": "What is XOR?", "domain": "binary_symmetry", "format": "json"}'

        curl -X POST "http://localhost:3000/api/query" \\
          -H "Content-Type: application/json" \\
          -d '{"query": "What is XOR?", "domain": "binary_symmetry", "format": "markdown"}'
    """
    return await _process_query_impl(
        query=request.query,
        domain_id=request.domain,
        context=request.context,
        include_trace=request.include_trace,
        verbose=request.verbose,
        show_thinking=request.show_thinking,
        format_type=request.format
    )


@app.get("/api/query")
async def process_query_get(
    query: str,
    domain: Optional[str] = "llm_consciousness",
    format: Optional[str] = None,
    include_trace: Optional[bool] = False
) -> Response:
    """
    Process a user query (GET method).

    Easier to use from browsers and command line without POST body.
    Format can be specified as query parameter.

    Examples:
        # Markdown format
        curl "http://localhost:3000/api/query?query=What+is+XOR?&domain=binary_symmetry&format=markdown"

        # JSON format
        curl "http://localhost:3000/api/query?query=What+is+XOR?&domain=binary_symmetry&format=json"

        # Compact format
        curl "http://localhost:3000/api/query?query=What+is+XOR?&domain=binary_symmetry&format=compact"

        # Default format
        curl "http://localhost:3000/api/query?query=What+is+XOR?&domain=binary_symmetry"
    """
    return await _process_query_impl(
        query=query,
        domain_id=domain,
        context=None,
        include_trace=include_trace,
        verbose=False,
        format_type=format
    )


@app.post("/api/query/phase1")
async def process_query_phase1(request: QueryRequest) -> Response:
    """
    Process query using Phase 1 engine (3 Personas + Pattern Override).

    Phase 1 uses simplified architecture:
    - 3 Personas: Poet (void), Librarian (library), Researcher (internet)
    - Pattern Override: if patterns found → use them, else → use persona data source
    - search_patterns flag: True (search), False (skip), None (use domain config)

    Examples:
        # Search patterns (default)
        curl -X POST http://localhost:3000/api/query/phase1 \\
          -H "Content-Type: application/json" \\
          -d '{"query": "How to cook rice", "domain": "cooking"}'

        # Skip pattern search, use persona data source
        curl -X POST http://localhost:3000/api/query/phase1 \\
          -H "Content-Type: application/json" \\
          -d '{"query": "How to cook rice", "domain": "cooking", "search_patterns": false}'

        # Explicit pattern search
        curl -X POST http://localhost:3000/api/query/phase1 \\
          -H "Content-Type: application/json" \\
          -d '{"query": "How to cook rice", "domain": "cooking", "search_patterns": true}'
    """
    # Create Phase 1 engine instance
    phase1_engine = Phase1Engine(enable_trace=request.include_trace)

    try:
        # Process query with Phase 1 engine
        result = await phase1_engine.process_query(
            query=request.query,
            domain_name=request.domain,
            context=request.context,
            search_patterns=request.search_patterns,  # THE SWITCH
            show_thinking=request.show_thinking or False  # Show reasoning flag
        )

        # Map Phase 1 response format to frontend-expected format
        # Frontend expects: response, specialist, confidence, query, llm_used, ai_generated
        # Phase 1 returns: answer, persona_type, source, query, pattern_override_used
        frontend_response = {
            "response": result.get("answer", ""),  # Map answer → response
            "specialist": result.get("persona_type", "General"),  # Map persona_type → specialist
            "confidence": 0.9 if result.get("pattern_override_used") else 0.7,  # Synthetic confidence
            "query": result.get("query", ""),
            "llm_used": True,  # Phase 1 always uses LLM
            "ai_generated": not result.get("pattern_override_used", False),  # True if no patterns used
            "processing_time_ms": result.get("processing_time_ms", 0),
            # Keep Phase 1 metadata for debugging
            "phase1_metadata": {
                "source": result.get("source"),
                "persona_type": result.get("persona_type"),
                "pattern_override_used": result.get("pattern_override_used"),
                "search_patterns_enabled": result.get("search_patterns_enabled"),
                "pattern_count": result.get("pattern_count", 0),
                "engine_version": result.get("engine_version")
            }
        }

        # Return mapped result
        return JSONResponse(content=frontend_response)

    except Exception as e:
        logger.error(f"[Phase1] Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query/confirm-llm")
async def confirm_llm_fallback(request: ConfirmLLMRequest) -> Response:
    """
    Process query with user-confirmed LLM fallback.

    Called when user confirms they want to extend search beyond local data.
    This bypasses the confirmation prompt and directly uses LLM fallback.

    Example:
        curl -X POST http://localhost:3000/api/query/confirm-llm \\
          -H "Content-Type: application/json" \\
          -d '{"query": "What is gastronomy?", "domain": "cooking"}'
    """
    return await _process_query_impl(
        query=request.query,
        domain_id=request.domain,
        context={"llm_confirmed": True},  # Pass llm_confirmed flag
        include_trace=request.include_trace,
        verbose=request.verbose,
        format_type=request.format
    )


@app.post("/api/query/extend-web-search")
async def extend_web_search(request: ConfirmLLMRequest) -> Response:
    """
    Process query with extended web search.

    Called when user clicks "Extended Search (Internet)" button.
    Performs web search and returns results with NEW knowledge only.

    Example:
        curl -X POST http://localhost:3000/api/query/extend-web-search \\
          -H "Content-Type: application/json" \\
          -d '{"query": "What is gastronomy?", "domain": "cooking"}'
    """
    return await _process_query_impl(
        query=request.query,
        domain_id=request.domain,
        context={"web_search_confirmed": True},  # Pass web_search_confirmed flag
        include_trace=request.include_trace,
        verbose=request.verbose,
        format_type=request.format
    )


async def _process_query_impl(
    query: str,
    domain_id: Optional[str],
    context: Optional[Dict[str, Any]],
    include_trace: Optional[bool],
    verbose: Optional[bool],
    show_thinking: Optional[bool] = False,
    format_type: Optional[str] = None
) -> Response:
    """
    Internal implementation for query processing.

    Used by both GET and POST endpoints.
    """
    domain_id = domain_id or "llm_consciousness"

    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    engine = engines[domain_id]

    try:
        # Extract llm_confirmed from context if present
        llm_confirmed = False
        if context and isinstance(context, dict):
            llm_confirmed = context.get('llm_confirmed', False)

        # Process the query
        result = await engine.process_query(
            query,
            context,
            include_trace=include_trace,
            llm_confirmed=llm_confirmed,
            verbose=verbose or False,  # Pass verbose flag to engine
            show_thinking=show_thinking or False  # Pass show_thinking flag to engine
        )

        # If format is specified, use formatter and return formatted response
        if format_type:
            # Prepare response data for formatter
            response_data = {
                "query": result.get("query", query),
                "patterns": result.get("patterns_used", []),  # Note: engine returns pattern IDs
                "specialist_id": result.get("specialist", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "raw_answer": result.get("response", ""),
                "domain_id": domain_id,
                "timestamp": result.get("timestamp", datetime.utcnow().isoformat()),
                "processing_time_ms": result.get("processing_time_ms")
            }

            # Get patterns from knowledge base for formatter
            domain = engine.domain
            if hasattr(domain, '_knowledge_base'):
                kb = domain._knowledge_base
                # Get full pattern objects
                patterns_with_details = []
                pattern_ids = result.get("patterns_used", [])
                for pid in pattern_ids:
                    pattern = await kb.get_by_id(pid)
                    if pattern:
                        patterns_with_details.append(pattern)
                response_data["patterns"] = patterns_with_details

            # Format the response
            formatted = await domain.format_response(response_data, format_type=format_type)

            # Determine Content-Type based on formatter
            content_type = f"{formatted.mime_type}; charset={formatted.encoding}"

            # Return appropriate response type based on MIME type
            if formatted.mime_type == "application/json":
                return JSONResponse(
                    content=formatted.content,
                    media_type=content_type
                )
            else:
                # For markdown, text, etc.
                return PlainTextResponse(
                    content=formatted.content,
                    media_type=content_type
                )
        else:
            # No format specified - return default structured JSON response (backward compatible)
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


# ==================== STATE MACHINE TRACE ENDPOINTS ====================

STATE_MACHINE_LOG_PATH = Path("/app/logs/traces/state_machine.jsonl")


@app.get("/api/state-traces")
async def get_state_traces(
    limit: int = 50,
    domain: Optional[str] = None,
    state: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent state machine trace events from the state machine log.

    Args:
        limit: Maximum number of events to return (default: 50)
        domain: Filter by domain ID
        state: Filter by specific state (e.g., "COMPLETE", "ERROR")

    Returns:
        List of state transition events with metadata

    Example:
        curl "http://localhost:3000/api/state-traces?limit=10&domain=exframe"
        curl "http://localhost:3000/api/state-traces?state=ERROR"
    """
    events = []
    try:
        if STATE_MACHINE_LOG_PATH.exists():
            with open(STATE_MACHINE_LOG_PATH, 'r') as f:
                lines = f.readlines()[-limit:]  # Get last N lines
                for line in reversed(lines):  # Most recent first
                    try:
                        event = json.loads(line.strip())
                        # Apply filters
                        if domain and event.get('data', {}).get('domain') != domain:
                            continue
                        if state and event.get('to_state') != state:
                            continue
                        events.append(event)
                        if len(events) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"Error reading state machine log: {e}")

    return {
        "count": len(events),
        "limit": limit,
        "filters": {"domain": domain, "state": state},
        "events": events
    }


@app.get("/api/state-traces/query/{query_id}")
async def get_state_trace_for_query(query_id: str) -> Dict[str, Any]:
    """
    Get complete state machine trace for a specific query.

    Returns all state transitions for the given query_id in chronological order,
    along with summary statistics.

    Args:
        query_id: The query ID (e.g., "q_338b253ab48c")

    Returns:
        Complete state trace with summary

    Example:
        curl "http://localhost:3000/api/state-traces/query/q_338b253ab48c"
    """
    events = []
    try:
        if STATE_MACHINE_LOG_PATH.exists():
            with open(STATE_MACHINE_LOG_PATH, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        if event.get('query_id') == query_id:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"Error reading state machine log: {e}")

    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"Query '{query_id}' not found in state machine logs"
        )

    # Calculate summary statistics
    first_event = events[0]
    last_event = events[-1]

    # Calculate total duration
    total_duration_ms = None
    if len(events) >= 2:
        first_time = datetime.fromisoformat(first_event['timestamp'].replace('Z', ''))
        last_time = datetime.fromisoformat(last_event['timestamp'].replace('Z', ''))
        total_duration_ms = int((last_time - first_time).total_seconds() * 1000)

    # Extract unique states
    unique_states = list(set(e['to_state'] for e in events))

    # Check for errors
    has_error = any(e['to_state'] == 'ERROR' for e in events)

    # Extract components used
    components_used = []
    for event in events:
        if 'component' in event.get('data', {}):
            components_used.append(event['data']['component'])
        elif 'enricher' in event.get('data', {}):
            components_used.append(event['data']['enricher'])
        elif 'formatter' in event.get('data', {}):
            components_used.append(event['data']['formatter'])

    # Count state transitions
    state_counts = {}
    for event in events:
        to_state = event['to_state']
        state_counts[to_state] = state_counts.get(to_state, 0) + 1

    return {
        "query_id": query_id,
        "summary": {
            "total_events": len(events),
            "unique_states": unique_states,
            "total_duration_ms": total_duration_ms,
            "has_error": has_error,
            "components_used": components_used,
            "domain": events[0].get('data', {}).get('domain'),
            "first_state": first_event.get('to_state'),
            "final_state": last_event.get('to_state'),
            "state_counts": state_counts
        },
        "events": events
    }


@app.get("/api/state-traces/summary")
async def get_state_traces_summary(
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get summary statistics from recent state machine traces.

    Aggregates data from the last N events to provide insights like:
    - Average processing time
    - Error rate
    - LLM usage rate
    - Most common states

    Args:
        limit: Number of recent events to analyze (default: 100)

    Returns:
        Summary statistics

    Example:
        curl "http://localhost:3000/api/state-traces/summary?limit=100"
    """
    events = []
    try:
        if STATE_MACHINE_LOG_PATH.exists():
            with open(STATE_MACHINE_LOG_PATH, 'r') as f:
                lines = f.readlines()[-limit:]
                for line in lines:
                    try:
                        event = json.loads(line.strip())
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"Error reading state machine log: {e}")

    if not events:
        return {
            "analyzed_events": 0,
            "message": "No events found in state machine log"
        }

    # Group events by query_id
    queries = {}
    for event in events:
        query_id = event.get('query_id')
        if query_id not in queries:
            queries[query_id] = []
        queries[query_id].append(event)

    # Calculate statistics
    query_count = len(queries)
    error_count = sum(1 for e in events if e['to_state'] == 'ERROR')
    complete_count = sum(1 for e in events if e['to_state'] == 'COMPLETE')
    llm_used_count = sum(
        1 for e in events
        if e.get('data', {}).get('llm_used') or 'llm_' in str(e.get('trigger', ''))
    )

    # Calculate average duration from COMPLETE events
    durations = []
    for event in events:
        if event['to_state'] == 'COMPLETE' and event.get('duration_ms'):
            durations.append(event['duration_ms'])

    avg_duration_ms = sum(durations) / len(durations) if durations else 0

    # State frequency
    state_freq = {}
    for event in events:
        state = event['to_state']
        state_freq[state] = state_freq.get(state, 0) + 1

    # Domain distribution
    domains = {}
    for event in events:
        domain = event.get('data', {}).get('domain')
        if domain:
            domains[domain] = domains.get(domain, 0) + 1

    return {
        "analyzed_events": len(events),
        "unique_queries": query_count,
        "statistics": {
            "error_count": error_count,
            "error_rate": error_count / query_count if query_count > 0 else 0,
            "complete_count": complete_count,
            "llm_used_count": llm_used_count,
            "llm_usage_rate": llm_used_count / query_count if query_count > 0 else 0,
            "avg_duration_ms": int(avg_duration_ms)
        },
        "state_frequency": state_freq,
        "domain_distribution": domains
    }


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
    # Load from domain.json file first (source of truth)
    # Then merge with registry if needed
    from pathlib import Path
    import os
    universes_base = os.getenv("UNIVERSES_BASE", "/app/universes")
    domain_file = Path(universes_base) / "MINE" / "domains" / domain_id / "domain.json"

    if domain_file.exists():
        import json
        with open(domain_file) as f:
            domain_config = json.load(f)
    else:
        # Fall back to registry
        registry = _load_domain_registry()
        if domain_id in registry["domains"]:
            domain_config = registry["domains"][domain_id]
        else:
            # Fall back to loading from universe system
            if not universe_manager or not universe_manager.universes:
                raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

            # Get the active universe
            active_universe = None
            from core.universe import UniverseState
            for universe in universe_manager.universes.values():
                if universe.state == UniverseState.ACTIVE:
                    active_universe = universe
                    break

            if not active_universe:
                # Try to load MINE universe
                try:
                    active_universe = await universe_manager.load_universe("MINE")
                except Exception as e:
                    raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

            domain = active_universe.get_domain(domain_id)
            if not domain:
                raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

            # At this point, domain file should have been loaded above
            # If we're here, something went wrong
            raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    # Add live specialist data if domain is loaded
    if domain_id in engines:
        engine = engines[domain_id]
        live_specialists = []
        for spec_id in engine.domain.list_specialists():
            spec = engine.domain.get_specialist(spec_id)
            if spec:
                # Specialist plugins use config with keys: name, keywords, categories, threshold
                live_specialists.append({
                    "specialist_id": spec.specialist_id,
                    "name": spec.name,
                    "description": spec.config.get("description", ""),
                    "keywords": spec.config.get("keywords", []),
                    "categories": spec.config.get("categories", []),
                    "confidence_threshold": spec.config.get("threshold", 0.5)
                })
        domain_config["specialists"] = live_specialists

    return domain_config


@app.post("/api/admin/domains")
async def create_domain(request: DomainCreate) -> Dict[str, Any]:
    """Create a new domain using the domain type system."""
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

    # Import the domain factory
    from core.domain_factory import DomainConfigGenerator

    # Generate domain configuration using the factory
    try:
        domain_config = DomainConfigGenerator.generate(
            domain_id=request.domain_id,
            domain_name=request.domain_name,
            description=request.description,
            categories=request.categories or [],
            tags=request.tags or [],
            specialists=[{
                "specialist_id": s.specialist_id,
                "name": s.name,
                "description": s.description,
                "expertise_keywords": s.expertise_keywords,
                "expertise_categories": s.expertise_categories,
                "confidence_threshold": s.confidence_threshold
            } for s in request.specialists],
            domain_type=request.domain_type or "",
            # Type 1: Creative
            creative_keywords=request.creative_keywords,
            # Type 2: Knowledge
            similarity_threshold=request.similarity_threshold,
            max_patterns=request.max_patterns,
            # Type 3: Document Store
            document_store_type=request.document_store_type,
            remote_url=request.remote_url,
            api_key=request.api_key,
            show_sources=request.show_sources,
            # Type 4: Analytical
            max_research_steps=request.max_research_steps,
            research_timeout=request.research_timeout,
            report_format=request.report_format,
            enable_web_search=request.enable_web_search,
            # Type 5: Hybrid
            require_confirmation=request.require_confirmation,
            research_on_fallback=request.research_on_fallback,
            # Common
            temperature=request.temperature,
            llm_min_confidence=request.llm_min_confidence,
            storage_path=request.storage_path
        )

        # Add any custom enrichers if provided
        if request.enrichers:
            domain_config["enrichers"] = request.enrichers

        # Add Phase 1 persona fields if provided
        if request.persona:
            domain_config["persona"] = request.persona
        if request.library_base_path:
            domain_config["library_base_path"] = request.library_base_path
        if request.enable_pattern_override is not None:
            domain_config["enable_pattern_override"] = request.enable_pattern_override

    except Exception as e:
        print(f"Warning: Domain factory generation failed, using defaults: {e}")
        # Fall back to basic config if factory fails
        domain_config = {
            "domain_id": request.domain_id,
            "domain_name": request.domain_name,
            "description": request.description,
            "version": "1.0.0",
            "categories": request.categories or [],
            "tags": request.tags or [],
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        # Add Phase 1 fields to fallback config
        if request.persona:
            domain_config["persona"] = request.persona
        if request.library_base_path:
            domain_config["library_base_path"] = request.library_base_path
        if request.enable_pattern_override is not None:
            domain_config["enable_pattern_override"] = request.enable_pattern_override

    # Create domain.json file in the universe structure
    try:
        universes_base = os.getenv("UNIVERSES_BASE", "/app/universes")
        domain_file = Path(universes_base) / "MINE" / "domains" / request.domain_id / "domain.json"
        domain_file.parent.mkdir(parents=True, exist_ok=True)

        with open(domain_file, 'w') as f:
            json.dump(domain_config, f, indent=2)

        # Create empty patterns.json file
        patterns_file = domain_file.parent / "patterns.json"
        with open(patterns_file, 'w') as f:
            json.dump([], f)

        print(f"Created domain files: {domain_file}")
    except Exception as e:
        print(f"Warning: Failed to create domain files: {e}")

    # Save to registry
    registry["domains"][request.domain_id] = domain_config
    _save_domain_registry(registry)

    # Auto-load the domain into active engines
    try:
        if universe_manager:
            # Reload the universe to pick up the new domain
            current_universe = universe_manager.get_active_universe()
            if current_universe:
                # Try to load this specific domain
                domain = await current_universe._load_domain(request.domain_id)
                if domain:
                    engines[request.domain_id] = current_universe.engines[request.domain_id]
                    logger.info(f"✓ Auto-loaded domain: {request.domain_id}")
    except Exception as e:
        logger.warning(f"Failed to auto-load domain {request.domain_id}: {e}")
        logger.warning("Domain created but requires container restart to use")

    return {
        "domain_id": request.domain_id,
        "domain_type": request.domain_type,
        "status": "created",
        "message": f"Domain '{request.domain_name}' created successfully",
        "config": domain_config,
        "auto_loaded": request.domain_id in engines
    }


@app.put("/api/admin/domains/{domain_id}")
async def update_domain(domain_id: str, request: DomainUpdate) -> Dict[str, Any]:
    """Update an existing domain. Supports domain type system changes."""
    registry = _load_domain_registry()
    universes_base = os.getenv("UNIVERSES_BASE", "/app/universes")
    domain_file = Path(universes_base) / "MINE" / "domains" / domain_id / "domain.json"

    # Try to get existing domain config from registry or file
    domain_config = None
    if domain_id in registry["domains"]:
        domain_config = registry["domains"][domain_id]
    elif domain_file.exists():
        with open(domain_file, 'r') as f:
            domain_config = json.load(f)

    if not domain_config:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    # If domain_type is being set/changed, regenerate config using factory
    if request.domain_type is not None and request.domain_type != domain_config.get("domain_type", ""):
        from core.domain_factory import DomainConfigGenerator

        # When changing domain type, use type-specific plugins instead of existing specialists
        # Only use specialists if explicitly provided in the request
        specialists = []
        if request.specialists is not None and len(request.specialists) > 0:
            # Convert Pydantic SpecialistConfig objects to dictionaries
            for s in request.specialists:
                specialists.append({
                    "specialist_id": s.specialist_id,
                    "name": s.name,
                    "description": s.description,
                    "expertise_keywords": s.expertise_keywords,
                    "expertise_categories": s.expertise_categories,
                    "confidence_threshold": s.confidence_threshold
                })
        # Note: NOT using existing specialists when domain_type changes
        # This allows type-specific plugins (e.g., exframe_specialist for Type 3) to be used

        # Generate new config using factory
        new_config = DomainConfigGenerator.generate(
            domain_id=domain_id,
            domain_name=request.domain_name if request.domain_name is not None else domain_config.get("domain_name", ""),
            description=request.description if request.description is not None else domain_config.get("description", ""),
            categories=request.categories if request.categories is not None else domain_config.get("categories", []),
            tags=request.tags if request.tags is not None else domain_config.get("tags", []),
            specialists=specialists,
            domain_type=request.domain_type,
            # Type 1: Creative
            creative_keywords=request.creative_keywords if request.creative_keywords is not None else domain_config.get("creative_keywords"),
            # Type 2: Knowledge
            similarity_threshold=request.similarity_threshold if request.similarity_threshold is not None else domain_config.get("similarity_threshold"),
            max_patterns=request.max_patterns if request.max_patterns is not None else domain_config.get("max_patterns"),
            # Type 3: Document Store
            document_store_type=request.document_store_type if request.document_store_type is not None else domain_config.get("document_store_type"),
            remote_url=request.remote_url if request.remote_url is not None else domain_config.get("remote_url"),
            show_sources=request.show_sources if request.show_sources is not None else domain_config.get("show_sources"),
            # Type 4: Analytical
            max_research_steps=request.max_research_steps if request.max_research_steps is not None else domain_config.get("max_research_steps"),
            research_timeout=request.research_timeout if request.research_timeout is not None else domain_config.get("research_timeout"),
            report_format=request.report_format if request.report_format is not None else domain_config.get("report_format"),
            enable_web_search=request.enable_web_search if request.enable_web_search is not None else domain_config.get("enable_web_search"),
            # Type 5: Hybrid
            require_confirmation=request.require_confirmation if request.require_confirmation is not None else domain_config.get("require_confirmation"),
            research_on_fallback=request.research_on_fallback if request.research_on_fallback is not None else domain_config.get("research_on_fallback"),
            # Common
            temperature=request.temperature if request.temperature is not None else domain_config.get("temperature"),
            llm_min_confidence=request.llm_min_confidence if request.llm_min_confidence is not None else domain_config.get("llm_min_confidence"),
            storage_path=domain_config.get("storage_path")
        )

        # Merge with existing config to preserve any fields not in factory output
        for key, value in domain_config.items():
            if key not in new_config:
                new_config[key] = value

        domain_config = new_config
    else:
        # Simple field updates when domain_type is not changing
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
                    "expertise_keywords": s.expertise_keywords,
                    "expertise_categories": s.expertise_categories,
                    "confidence_threshold": s.confidence_threshold
                }
                for s in request.specialists
            ]
            # Also update plugins
            domain_config["plugins"] = []
            for s in request.specialists:
                domain_config["plugins"].append({
                    "plugin_id": s.specialist_id,
                    "name": s.name,
                    "description": s.description,
                    "module": "plugins.generalist",
                    "class": "GeneralistPlugin",
                    "enabled": True,
                    "config": {
                        "name": s.name,
                        "description": s.description,
                        "keywords": s.expertise_keywords,
                        "categories": s.expertise_categories,
                        "threshold": s.confidence_threshold
                    }
                })
        if request.enrichers is not None:
            domain_config["enrichers"] = request.enrichers

        # Update domain type fields
        if request.domain_type is not None:
            domain_config["domain_type"] = request.domain_type
        if request.temperature is not None:
            domain_config["temperature"] = request.temperature
        if request.llm_min_confidence is not None:
            domain_config["llm_min_confidence"] = request.llm_min_confidence
        if request.creative_keywords is not None:
            domain_config["creative_keywords"] = request.creative_keywords
        if request.similarity_threshold is not None:
            domain_config["similarity_threshold"] = request.similarity_threshold
        if request.max_patterns is not None:
            domain_config["max_patterns"] = request.max_patterns
        if request.document_store_type is not None:
            domain_config["document_store_type"] = request.document_store_type
        if request.remote_url is not None:
            domain_config["remote_url"] = request.remote_url
        if request.show_sources is not None:
            domain_config["show_sources"] = request.show_sources
        if request.max_research_steps is not None:
            domain_config["max_research_steps"] = request.max_research_steps
        if request.research_timeout is not None:
            domain_config["research_timeout"] = request.research_timeout
        if request.report_format is not None:
            domain_config["report_format"] = request.report_format
        if request.enable_web_search is not None:
            domain_config["enable_web_search"] = request.enable_web_search
        if request.require_confirmation is not None:
            domain_config["require_confirmation"] = request.require_confirmation
        if request.research_on_fallback is not None:
            domain_config["research_on_fallback"] = request.research_on_fallback

        # Phase 1: Persona system fields
        if request.persona is not None:
            domain_config["persona"] = request.persona
        if request.library_base_path is not None:
            domain_config["library_base_path"] = request.library_base_path
        if request.enable_pattern_override is not None:
            domain_config["enable_pattern_override"] = request.enable_pattern_override

    domain_config["updated_at"] = datetime.utcnow().isoformat()

    # Save to registry
    registry["domains"][domain_id] = domain_config
    _save_domain_registry(registry)

    # Save to universe domain.json file
    domain_file.parent.mkdir(parents=True, exist_ok=True)
    with open(domain_file, 'w') as f:
        json.dump(domain_config, f, indent=2)

    # Reload domain if it's currently loaded
    if domain_id in engines:
        try:
            await engines[domain_id].reload()
        except Exception as e:
            print(f"Warning: Failed to reload domain {domain_id}: {e}")

    return {
        "domain_id": domain_id,
        "status": "updated",
        "config": domain_config
    }


@app.delete("/api/admin/domains/{domain_id}")
async def delete_domain(domain_id: str) -> Dict[str, Any]:
    """Delete a domain."""
    import shutil
    from pathlib import Path

    registry = _load_domain_registry()

    # Track if domain was in registry
    was_in_registry = domain_id in registry["domains"]

    # Get domain config if in registry, otherwise create minimal config
    if was_in_registry:
        domain_config = registry["domains"][domain_id]

        # Unload domain if loaded
        if domain_id in engines:
            await engines[domain_id].domain.cleanup()
            del engines[domain_id]

        # Remove from registry
        del registry["domains"][domain_id]
        _save_domain_registry(registry)
    else:
        print(f"  Domain '{domain_id}' not in registry, checking if directory exists...")
        # Domain might exist on disk but not in registry (orphaned domain)
        domain_config = {"domain_id": domain_id, "domain_name": domain_id}

    # Delete the actual domain directory (even if not in registry)
    domain_path = _get_universes_domains_path() / domain_id

    deleted_dir = False
    if domain_path.exists():
        try:
            shutil.rmtree(domain_path)
            print(f"  Deleted domain directory: {domain_path}")
            deleted_dir = True
        except Exception as e:
            print(f"  Warning: Failed to delete domain directory {domain_path}: {e}")
            # Don't fail the deletion if directory removal fails
            # The domain is already removed from registry

    # If domain wasn't in registry and directory didn't exist, raise 404
    if not was_in_registry and not deleted_dir:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    return {
        "domain_id": domain_id,
        "status": "deleted",
        "message": f"Domain '{domain_config.get('domain_name', domain_id)}' deleted successfully"
    }


@app.post("/api/admin/domains/rebuild-registry")
async def rebuild_domain_registry() -> Dict[str, Any]:
    """
    Rebuild the domain registry from actual domain.json files.

    This updates the cached domains.json with current data from all domain configs.
    """
    from pathlib import Path

    registry = {"domains": {}, "next_id": 1}
    patterns_base = Path(__file__).parent.parent / "data" / "patterns"

    # Scan all domain directories
    for domain_dir in patterns_base.iterdir():
        if not domain_dir.is_dir():
            continue

        domain_file = domain_dir / "domain.json"
        if not domain_file.exists():
            continue

        try:
            with open(domain_file, 'r') as f:
                domain_config = json.load(f)
                domain_id = domain_config.get("domain_id")

                if domain_id:
                    registry["domains"][domain_id] = domain_config
                    print(f"  Added to registry: {domain_id}")
        except Exception as e:
            print(f"  Warning: Failed to load {domain_dir}: {e}")

    # Save updated registry
    _save_domain_registry(registry)

    return {
        "status": "rebuilt",
        "domains_updated": len(registry["domains"]),
        "message": f"Domain registry rebuilt with {len(registry['domains'])} domains"
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


# =============================================================================
# Candidate Pattern Management
# =============================================================================

@app.get("/api/admin/candidates")
async def list_all_candidates(
    domain: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    List all candidate patterns across all domains or a specific domain.

    Candidates are patterns auto-generated from LLM responses that await review.
    """
    all_candidates = []

    if domain:
        # List candidates for specific domain
        if domain not in engines:
            raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")

        kb = engines[domain].knowledge_base
        all_patterns = await kb.get_all_patterns()

        for pattern in all_patterns:
            if pattern.get("status") == "candidate":
                all_candidates.append({
                    "domain": domain,
                    "pattern_id": pattern.get("id"),
                    "name": pattern.get("name"),
                    "problem": pattern.get("problem")[:100] + "..." if pattern.get("problem") and len(pattern.get("problem")) > 100 else pattern.get("problem"),
                    "origin": pattern.get("origin"),
                    "generated_at": pattern.get("generated_at"),
                    "generated_by": pattern.get("generated_by"),
                    "confidence_score": pattern.get("confidence_score"),
                    "usage_count": pattern.get("usage_count", 0),
                    "solution_preview": pattern.get("solution", "")[:200] + "..." if len(pattern.get("solution", "")) > 200 else pattern.get("solution", "")
                })
    else:
        # List candidates across all domains
        for domain_id, engine in engines.items():
            kb = engine.knowledge_base
            try:
                all_patterns = await kb.get_all_patterns()

                for pattern in all_patterns:
                    if pattern.get("status") == "candidate":
                        all_candidates.append({
                            "domain": domain_id,
                            "pattern_id": pattern.get("id"),
                            "name": pattern.get("name"),
                            "problem": pattern.get("problem")[:100] + "..." if pattern.get("problem") and len(pattern.get("problem")) > 100 else pattern.get("problem"),
                            "origin": pattern.get("origin"),
                            "generated_at": pattern.get("generated_at"),
                            "generated_by": pattern.get("generated_by"),
                            "confidence_score": pattern.get("confidence_score"),
                            "usage_count": pattern.get("usage_count", 0),
                            "solution_preview": pattern.get("solution", "")[:200] + "..." if len(pattern.get("solution", "")) > 200 else pattern.get("solution", "")
                        })
            except Exception as e:
                # Skip domains that fail to load
                continue

    # Sort by generated_at (newest first)
    all_candidates.sort(key=lambda x: x.get("generated_at", ""), reverse=True)

    return {
        "candidates": all_candidates[:limit],
        "total": len(all_candidates),
        "domain_filter": domain,
        "status_filter": status
    }


@app.get("/api/admin/candidates/{domain_id}/{pattern_id}")
async def get_candidate_details(domain_id: str, pattern_id: str) -> Dict[str, Any]:
    """Get full details of a specific candidate pattern."""
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    kb = engines[domain_id].knowledge_base
    pattern = await kb.get_by_id(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    if pattern.get("status") != "candidate":
        raise HTTPException(status_code=400, detail=f"Pattern '{pattern_id}' is not a candidate")

    return {
        "domain": domain_id,
        "pattern": pattern
    }


@app.post("/api/admin/candidates/{domain_id}/{pattern_id}/promote")
async def promote_candidate(
    domain_id: str,
    pattern_id: str,
    reviewed_by: Optional[str] = "admin",
    review_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Promote a candidate pattern to certified status.

    This marks the pattern as trusted and removes the AI-generated badge.
    """
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    kb = engines[domain_id].knowledge_base
    pattern = await kb.get_by_id(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    if pattern.get("status") != "candidate":
        raise HTTPException(status_code=400, detail=f"Pattern '{pattern_id}' is not a candidate")

    # Update pattern to certified status
    from datetime import datetime, timedelta

    # Fix invalid pattern_type when certifying
    current_type = pattern.get("pattern_type", "")
    invalid_types = {"candidate", "", None}
    if current_type in invalid_types:
        # Set to a valid default type
        updates = {
            "status": "certified",
            "pattern_type": "how_to",  # Fix invalid type
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.utcnow().isoformat(),
            "review_notes": review_notes,
            "tags": list(set(pattern.get("tags", [])) - {"candidate", "llm_generated"}) + ["certified"]
        }
    else:
        updates = {
            "status": "certified",
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.utcnow().isoformat(),
            "review_notes": review_notes,
            "tags": list(set(pattern.get("tags", [])) - {"candidate", "llm_generated"}) + ["certified"]
        }

    await kb.update_pattern(pattern_id, updates)

    # Remove from candidate tags if present
    if "candidate" in pattern.get("tags", []):
        pattern["tags"].remove("candidate")
    if "llm_generated" in pattern.get("tags", []):
        pattern["tags"].remove("llm_generated")

    return {
        "domain": domain_id,
        "pattern_id": pattern_id,
        "status": "certified",
        "reviewed_by": reviewed_by,
        "reviewed_at": updates["reviewed_at"],
        "message": "Candidate pattern promoted to certified status"
    }


@app.delete("/api/admin/candidates/{domain_id}/{pattern_id}")
async def reject_candidate(domain_id: str, pattern_id: str) -> Dict[str, Any]:
    """
    Reject and delete a candidate pattern.

    Permanently removes the pattern from the knowledge base.
    """
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    kb = engines[domain_id].knowledge_base
    pattern = await kb.get_by_id(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    if pattern.get("status") != "candidate":
        raise HTTPException(status_code=400, detail=f"Pattern '{pattern_id}' is not a candidate")

    # Delete the pattern
    await kb.delete_pattern(pattern_id)

    return {
        "domain": domain_id,
        "pattern_id": pattern_id,
        "status": "deleted",
        "message": "Candidate pattern rejected and deleted"
    }


class PatternUpdate(BaseModel):
    """Model for pattern update requests."""
    status: Optional[str] = None
    llm_generated: Optional[bool] = None
    confidence_score: Optional[float] = None
    tags: Optional[List[str]] = None


@app.put("/api/admin/domains/{domain_id}/patterns/{pattern_id}")
async def update_pattern(
    domain_id: str,
    pattern_id: str,
    update_data: PatternUpdate
) -> Dict[str, Any]:
    """
    Update pattern properties.

    Allows editing:
    - status: "candidate" or "certified"
    - llm_generated: true/false flag for AI-generated badge
    - confidence_score: 0.0 to 1.0, affects search ranking
    - tags: array of tags for categorization
    """
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    kb = engines[domain_id].knowledge_base
    pattern = await kb.get_by_id(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    # Build updates dict with only provided fields
    updates = {}

    if update_data.status is not None:
        if update_data.status not in ["candidate", "certified"]:
            raise HTTPException(status_code=400, detail="status must be 'candidate' or 'certified'")
        updates["status"] = update_data.status

    if update_data.llm_generated is not None:
        updates["llm_generated"] = update_data.llm_generated

    if update_data.confidence_score is not None:
        if not 0.0 <= update_data.confidence_score <= 1.0:
            raise HTTPException(status_code=400, detail="confidence_score must be between 0.0 and 1.0")
        updates["confidence_score"] = update_data.confidence_score

    if update_data.tags is not None:
        updates["tags"] = update_data.tags

    # Apply updates
    if updates:
        await kb.update_pattern(pattern_id, updates)

    # Auto-update tags when status changes
    if update_data.status is not None:
        # Get the updated pattern to check current tags
        updated_pattern = await kb.get_by_id(pattern_id)
        if updated_pattern:
            current_tags = updated_pattern.get("tags", [])

            # Update tags based on status
            if update_data.status == "certified":
                # Remove candidate/llm_generated tags, add certified tag
                new_tags = [t for t in current_tags if t not in ["candidate", "llm_generated"]]
                if "certified" not in new_tags:
                    new_tags.append("certified")
                await kb.update_pattern(pattern_id, {"tags": new_tags})
            elif update_data.status == "candidate":
                # Add candidate tag back if it was removed
                if "candidate" not in current_tags:
                    current_tags.append("candidate")
                await kb.update_pattern(pattern_id, {"tags": current_tags})

    # Sync confidence field with confidence_score if confidence_score was updated
    if update_data.confidence_score is not None:
        await kb.update_pattern(pattern_id, {"confidence": update_data.confidence_score})

    # Auto-regenerate embeddings to keep search synchronized
    await _regenerate_domain_embeddings(domain_id)

    # Get updated pattern
    updated_pattern = await kb.get_by_id(pattern_id)

    return {
        "domain": domain_id,
        "pattern_id": pattern_id,
        "pattern": updated_pattern,
        "updates_applied": list(updates.keys()),
        "message": "Pattern updated successfully"
    }


@app.delete("/api/admin/domains/{domain_id}/patterns/{pattern_id}")
async def delete_pattern_admin(domain_id: str, pattern_id: str) -> Dict[str, Any]:
    """
    Delete any pattern from the knowledge base.

    Permanently removes the pattern.
    """
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    kb = engines[domain_id].knowledge_base
    pattern = await kb.get_by_id(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    # Delete the pattern
    await kb.delete_pattern(pattern_id)

    # Auto-regenerate embeddings to keep search synchronized
    await _regenerate_domain_embeddings(domain_id)

    return {
        "domain": domain_id,
        "pattern_id": pattern_id,
        "pattern_name": pattern.get("name", "Unknown"),
        "status": "deleted",
        "message": "Pattern deleted successfully"
    }


# =============================================================================
# DIAGNOSTICS ENDPOINTS
# =============================================================================

# Global diagnostics instances
_search_metrics_instance: Optional[SearchMetrics] = None
_pattern_analyzer_instance: Optional[PatternAnalyzer] = None
_health_checker_instance: Optional[HealthChecker] = None


def get_search_metrics_instance() -> SearchMetrics:
    """Get or create SearchMetrics instance."""
    global _search_metrics_instance
    if _search_metrics_instance is None:
        log_dir = Path(__file__).parent.parent / "logs" / "search_metrics"
        _search_metrics_instance = SearchMetrics(storage_path=log_dir)
    return _search_metrics_instance


def _get_universes_domains_path() -> Path:
    """Get the path to the domains directory within the default universe."""
    # Check if running in Docker (APP_HOME env var is set)
    if os.getenv("APP_HOME"):
        universes_base = Path("/app/universes")
    else:
        universes_base = Path(os.getenv("UNIVERSES_BASE",
                                        "/home/peter/development/eeframe/universes"))
    return universes_base / "MINE" / "domains"


def get_pattern_analyzer_instance() -> PatternAnalyzer:
    """Get or create PatternAnalyzer instance."""
    global _pattern_analyzer_instance
    if _pattern_analyzer_instance is None:
        pattern_path = _get_universes_domains_path()
        _pattern_analyzer_instance = PatternAnalyzer(pattern_path)
    return _pattern_analyzer_instance


def get_health_checker_instance() -> HealthChecker:
    """Get or create HealthChecker instance."""
    global _health_checker_instance
    if _health_checker_instance is None:
        pattern_path = _get_universes_domains_path()
        _health_checker_instance = HealthChecker(
            pattern_path,
            get_search_metrics_instance()
        )
    return _health_checker_instance


@app.get("/api/diagnostics/health")
async def diagnostics_health(
    domain_ids: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get overall system health status.

    Query params:
        domain_ids: Comma-separated domain IDs to check
    """
    checker = get_health_checker_instance()

    domains = domain_ids.split(',') if domain_ids else None

    report = checker.check_all(domain_ids=domains)
    return report.to_dict()


@app.get("/api/diagnostics/metrics")
async def diagnostics_metrics(
    hours: int = 24,
    domain_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get search quality metrics.

    Query params:
        hours: Time window in hours (default: 24)
        domain_id: Filter by domain
    """
    metrics = get_search_metrics_instance()

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    quality_metrics = metrics.calculate_metrics(
        start_time=start_time,
        end_time=end_time,
        domain_id=domain_id
    )

    return quality_metrics.to_dict()


@app.get("/api/diagnostics/traces")
async def diagnostics_traces(
    limit: int = 100,
    domain_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get recent search traces.

    Query params:
        limit: Maximum traces to return (default: 100)
        domain_id: Filter by domain
    """
    metrics = get_search_metrics_instance()

    traces = metrics.get_recent_traces(limit=limit, domain_id=domain_id)

    return [trace.to_dict() for trace in traces]


@app.get("/api/diagnostics/traces/low-confidence")
async def diagnostics_low_confidence(
    threshold: float = 0.5,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get searches with low confidence scores.

    Query params:
        threshold: Confidence threshold (default: 0.5)
        limit: Maximum results (default: 50)
    """
    metrics = get_search_metrics_instance()

    traces = metrics.identify_low_confidence_searches(
        threshold=threshold,
        limit=limit
    )

    return [trace.to_dict() for trace in traces]


@app.get("/api/diagnostics/traces/no-results")
async def diagnostics_no_results(
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get searches that returned no results.

    Query params:
        limit: Maximum results (default: 50)
    """
    metrics = get_search_metrics_instance()

    traces = metrics.identify_no_results_searches(limit=limit)

    return [trace.to_dict() for trace in traces]


@app.get("/api/diagnostics/patterns/health")
async def diagnostics_pattern_health(
    domain_id: str
) -> Dict[str, Any]:
    """
    Get pattern health report for a domain.

    Query params:
        domain_id: Domain ID to analyze
    """
    analyzer = get_pattern_analyzer_instance()

    report = analyzer.analyze_domain(domain_id)
    return report.to_dict()


@app.get("/api/diagnostics/patterns/health/all")
async def diagnostics_all_pattern_health(
    domain_ids: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get pattern health for all domains.

    Query params:
        domain_ids: Comma-separated domain IDs (default: all)
    """
    analyzer = get_pattern_analyzer_instance()

    if domain_ids:
        domains = domain_ids.split(',')
    else:
        # Get all domains
        pattern_path = Path(get_storage_path("dummy")).parent.parent
        domains = [d.name for d in pattern_path.iterdir() if d.is_dir()]

    reports = analyzer.analyze_universe(domains)

    return {
        domain_id: report.to_dict()
        for domain_id, report in reports.items()
    }


@app.get("/api/diagnostics/patterns/usage")
async def diagnostics_pattern_usage(
    pattern_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get pattern usage statistics.

    Query params:
        pattern_id: Specific pattern ID (default: all)
    """
    metrics = get_search_metrics_instance()

    stats = metrics.get_pattern_usage_stats(pattern_id=pattern_id)

    return stats


@app.get("/api/diagnostics/summary")
async def diagnostics_summary() -> Dict[str, Any]:
    """
    Get a comprehensive diagnostics summary.

    Combines health, metrics, and pattern analysis.
    """
    # Get system health
    health = await diagnostics_health()

    # Get search metrics (last 24 hours)
    metrics_data = await diagnostics_metrics(hours=24)

    # Get pattern health for all domains
    pattern_health = await diagnostics_all_pattern_health()

    return {
        "health": health,
        "search_metrics": metrics_data,
        "pattern_health": pattern_health,
        "generated_at": datetime.utcnow().isoformat(),
    }


@app.post("/api/diagnostics/self-test")
async def run_self_test(
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Run self-test suite and return results.

    Runs automated tests to validate:
    - Search quality
    - Performance
    - Regression detection
    """
    from diagnostics.self_test import SelfTestRunner

    runner = SelfTestRunner(
        api_base_url="http://localhost:3000",
        search_metrics=get_search_metrics_instance()
    )

    # Run tests in background
    import asyncio

    result = await runner.run_self_tests(suite_name="default")

    return result.to_dict()


# =============================================================================
# SEMANTIC SEARCH / EMBEDDING MANAGEMENT API
# =============================================================================

class HybridWeightsRequest(BaseModel):
    """Request to adjust hybrid search weights."""
    semantic: float = 0.5
    keyword: float = 0.5


@app.get("/api/embeddings/status")
async def get_embeddings_status(domain: Optional[str] = None) -> Dict[str, Any]:
    """
    Get embedding status for a domain or all domains.

    Returns:
        - total_patterns: Number of patterns
        - has_embeddings: Number with embeddings
        - needs_embeddings: Number needing embeddings
        - coverage_percent: Percentage covered
        - semantic_available: Whether sentence-transformers is installed
        - hybrid_enabled: Whether hybrid search is active
    """
    if domain:
        if domain not in engines:
            raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")

        kb = engines[domain].knowledge_base
        if hasattr(kb, 'get_embedding_status'):
            return kb.get_embedding_status()
        else:
            return {"error": "Embedding support not available for this knowledge base type"}
    else:
        # Return status for all domains
        results = {}
        for domain_id, engine in engines.items():
            kb = engine.knowledge_base
            if hasattr(kb, 'get_embedding_status'):
                results[domain_id] = kb.get_embedding_status()
        return {"domains": results}


@app.post("/api/embeddings/generate")
async def generate_embeddings(
    domain: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Generate embeddings for all patterns in a domain.

    This is a long-running operation. Patterns without embeddings
    will have them generated and saved to disk.

    Returns:
        - generated: Number of new embeddings created
        - skipped: Number already with embeddings
        - failed: Number that failed
        - total: Total patterns processed
    """
    if domain not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")

    kb = engines[domain].knowledge_base
    if not hasattr(kb, 'generate_embeddings'):
        return {"error": "Embedding generation not supported for this knowledge base type"}

    # Run synchronously for now (could be made async)
    result = await kb.generate_embeddings()
    return result


@app.post("/api/embeddings/weights")
async def set_hybrid_weights(
    request: HybridWeightsRequest,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Adjust hybrid search weights for semantic vs keyword matching.

    Args:
        semantic: Weight for semantic similarity (0-1)
        keyword: Weight for keyword matching (0-1)
        domain: Optional domain to apply weights to (default: all domains)

    Returns:
        Updated weights
    """
    if domain:
        if domain not in engines:
            raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")

        kb = engines[domain].knowledge_base
        if hasattr(kb, 'set_hybrid_weights'):
            kb.set_hybrid_weights(request.semantic, request.keyword)
        return {"domain": domain, "semantic": request.semantic, "keyword": request.keyword}
    else:
        # Apply to all domains
        results = {}
        for domain_id, engine in engines.items():
            kb = engine.knowledge_base
            if hasattr(kb, 'set_hybrid_weights'):
                kb.set_hybrid_weights(request.semantic, request.keyword)
                results[domain_id] = {"semantic": request.semantic, "keyword": request.keyword}
        return {"domains": results}


@app.get("/api/embeddings/model")
async def get_embedding_model_info() -> Dict[str, Any]:
    """
    Get information about the embedding model.

    Returns:
        - available: Whether sentence-transformers is installed
        - model_name: Name of the model
        - loaded: Whether model is loaded
        - embedding_dim: Dimension of embeddings
    """
    from core.embeddings import SENTENCE_TRANSFORMERS_AVAILABLE, get_embedding_service

    service = get_embedding_service()

    return {
        "available": SENTENCE_TRANSFORMERS_AVAILABLE,
        "model_name": "all-MiniLM-L6-v2" if service else None,
        "loaded": service.is_loaded if service else False,
        "embedding_dim": 384 if service else None,
        "description": "SentenceTransformers model for semantic search"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
