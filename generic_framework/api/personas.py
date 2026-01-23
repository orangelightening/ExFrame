"""
Persona API Endpoints

Provides CRUD and management endpoints for persona plugins.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from assist.persona_loader import get_default_loader


router = APIRouter(prefix="/api/personas", tags=["personas"])


# Response models
class PersonaInfo(BaseModel):
    persona_id: str
    name: str
    identity: Dict[str, Any]
    behaviors: List[str]
    config: Dict[str, Any]
    heartbeat: Dict[str, Any]


class PersonaListResponse(BaseModel):
    personas: List[str]
    count: int


class PersonaDetailsResponse(BaseModel):
    persona: PersonaInfo
    system_prompt: str


# Initialize loader
_persona_loader = None


def get_loader():
    """Get or create the persona loader."""
    global _persona_loader
    if _persona_loader is None:
        _persona_loader = get_default_loader()
    return _persona_loader


@router.get("", response_model=PersonaListResponse)
async def list_personas():
    """
    List all available persona IDs.

    Returns a list of all registered persona plugins.
    """
    loader = get_loader()
    personas = loader.list_available_personas()
    return PersonaListResponse(
        personas=personas,
        count=len(personas)
    )


@router.get("/{persona_id}", response_model=PersonaDetailsResponse)
async def get_persona(persona_id: str):
    """
    Get detailed information about a persona.

    Includes identity, behaviors, config, and the generated system prompt.
    """
    loader = get_loader()
    info = loader.get_persona_info(persona_id)

    if not info:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")

    # Load the persona to get system prompt
    persona = loader.load_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Failed to instantiate persona '{persona_id}'")

    system_prompt = persona.build_system_prompt()

    return PersonaDetailsResponse(
        persona=PersonaInfo(**info),
        system_prompt=system_prompt
    )


@router.post("/test")
async def test_persona(persona_id: str, query: str):
    """
    Test a persona with a sample query.

    Returns the system prompt that would be used for the given query.
    """
    loader = get_loader()
    persona = loader.load_persona_by_id(persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")

    # For now, just return the system prompt and query
    # Full integration will come in Week 2 with PromptBuilder
    return {
        "persona_id": persona_id,
        "query": query,
        "system_prompt": persona.build_system_prompt(),
        "behaviors": persona.get_behaviors(),
        "identity": persona.get_identity()
    }


@router.get("/domain/{domain_id}/specialist/{specialist_id}")
async def get_specialist_persona(domain_id: str, specialist_id: str):
    """
    Get the persona configured for a specific specialist in a domain.

    This loads the domain configuration and returns the persona
    associated with the given specialist.
    """
    from pathlib import Path
    import json

    # Load domain config
    domain_path = Path(f"universes/MINE/domains/{domain_id}/domain.json")
    if not domain_path.exists():
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    with open(domain_path) as f:
        domain_config = json.load(f)

    # Load persona for specialist
    loader = get_loader()
    persona = loader.load_persona_for_specialist(domain_id, specialist_id, domain_config)

    if not persona:
        return {
            "domain_id": domain_id,
            "specialist_id": specialist_id,
            "persona": None,
            "message": "No persona configured for this specialist"
        }

    return {
        "domain_id": domain_id,
        "specialist_id": specialist_id,
        "persona": {
            "persona_id": persona.persona_id,
            "name": persona.name,
            "identity": persona.get_identity(),
            "behaviors": persona.get_behaviors(),
            "config": persona.get_config(),
            "heartbeat": persona.get_heartbeat_config()
        },
        "system_prompt": persona.build_system_prompt()
    }


@router.post("/register")
async def register_persona(
    persona_id: str,
    name: str,
    identity: Dict[str, Any],
    behaviors: List[str],
    example_phrases: List[str]
):
    """
    Register a new persona at runtime.

    This creates a dynamic persona class and registers it.
    Useful for testing and quick persona creation.
    """
    from typing import Dict as TypingDict, List as TypingList, Any as TypingAny
    from core.persona_plugin import PersonaPlugin
    from plugins.personas import PersonaRegistry

    # Create a dynamic persona class
    class DynamicPersona(PersonaPlugin):
        name = name
        persona_id = persona_id

        def __init__(self, config=None):
            super().__init__(config)
            self._identity = identity
            self._behaviors = behaviors
            self._example_phrases = example_phrases

        def get_identity(self):
            return self._identity

        def get_behaviors(self):
            return self._behaviors

        def get_example_phrases(self):
            return self._example_phrases

    # Register the persona
    PersonaRegistry.register(DynamicPersona)

    return {
        "message": f"Persona '{persona_id}' registered successfully",
        "persona_id": persona_id,
        "name": name
    }


@router.get("/health/check")
async def health_check():
    """
    Health check endpoint for personas.

    Returns the status of the persona system.
    """
    loader = get_loader()
    personas = loader.list_available_personas()

    return {
        "status": "healthy",
        "persona_count": len(personas),
        "personas": personas,
        "registry_initialized": loader._initialized
    }


# =============================================================================
# PANEL ENDPOINTS
# =============================================================================

from core.persona_plugin import PanelPersonaPlugin


class PanelInfo(BaseModel):
    """Panel information model."""
    panel_id: str
    name: str
    mode: str
    experts: List[str]
    facilitator: str
    max_rounds: int
    consensus_threshold: float


@router.get("/panels", response_model=Dict[str, Any])
async def list_panels():
    """
    List all available panel personas.

    Returns panels that coordinate multiple expert personas.
    """
    loader = get_loader()
    all_personas = loader.list_available_personas()

    # Filter to only panel personas
    panels = []
    for persona_id in all_personas:
        persona = loader.load_persona_by_id(persona_id)
        if persona and isinstance(persona, PanelPersonaPlugin):
            panels.append({
                "panel_id": persona.persona_id,
                "name": persona.name,
                "mode": persona.get_panel_mode(),
                "expert_count": len(persona.get_experts()),
                "facilitator": persona.get_facilitator_id()
            })

    return {
        "panels": panels,
        "count": len(panels)
    }


@router.get("/panels/{panel_id}", response_model=Dict[str, Any])
async def get_panel(panel_id: str):
    """
    Get detailed information about a panel persona.

    Includes experts, facilitator, mode, and configuration.
    """
    loader = get_loader()
    panel = loader.load_persona_by_id(panel_id)

    if not panel:
        raise HTTPException(status_code=404, detail=f"Panel '{panel_id}' not found")

    if not isinstance(panel, PanelPersonaPlugin):
        raise HTTPException(status_code=400, detail=f"Persona '{panel_id}' is not a panel")

    # Get expert details
    experts_info = []
    for expert_id in panel.get_experts():
        expert = loader.load_persona_by_id(expert_id)
        if expert:
            experts_info.append({
                "expert_id": expert.persona_id,
                "name": expert.name,
                "identity": expert.get_identity()
            })

    # Get facilitator details
    facilitator = loader.load_persona_by_id(panel.get_facilitator_id())
    facilitator_info = None
    if facilitator:
        facilitator_info = {
            "facilitator_id": facilitator.persona_id,
            "name": facilitator.name,
            "identity": facilitator.get_identity()
        }

    return {
        "panel_id": panel.persona_id,
        "name": panel.name,
        "mode": panel.get_panel_mode(),
        "experts": experts_info,
        "facilitator": facilitator_info,
        "max_rounds": panel.get_max_rounds(),
        "consensus_threshold": panel.get_consensus_threshold(),
        "system_prompt": panel.build_system_prompt()
    }


@router.post("/panels/{panel_id}/test", response_model=Dict[str, Any])
async def test_panel(panel_id: str, query: str):
    """
    Test a panel with a sample query.

    Returns the panel configuration and what would happen,
    without actually calling LLM (mock mode).
    """
    loader = get_loader()
    panel = loader.load_persona_by_id(panel_id)

    if not panel:
        raise HTTPException(status_code=404, detail=f"Panel '{panel_id}' not found")

    if not isinstance(panel, PanelPersonaPlugin):
        raise HTTPException(status_code=400, detail=f"Persona '{panel_id}' is not a panel")

    from assist.panel_manager import PanelManager

    # Create panel manager
    manager = PanelManager(loader)

    # Process with mock responses (no LLM handler)
    result = await manager.process_with_panel(
        query=query,
        panel_persona=panel,
        context={},
        llm_call_handler=None  # Mock mode
    )

    return {
        "panel_id": panel_id,
        "query": query,
        "mode": panel.get_panel_mode(),
        "result": result.to_dict()
    }


@router.post("/panels/process", response_model=Dict[str, Any])
async def process_with_panel(
    panel_id: str,
    query: str,
    context: Optional[Dict[str, Any]] = None
):
    """
    Process a query using a panel of experts.

    This is a mock endpoint for testing. Real LLM integration
    will be added when PromptBuilder is implemented.

    For now, returns mock responses showing how the panel would work.
    """
    loader = get_loader()
    panel = loader.load_persona_by_id(panel_id)

    if not panel:
        raise HTTPException(status_code=404, detail=f"Panel '{panel_id}' not found")

    if not isinstance(panel, PanelPersonaPlugin):
        raise HTTPException(status_code=400, detail=f"Persona '{panel_id}' is not a panel")

    from assist.panel_manager import PanelManager

    # Create panel manager
    manager = PanelManager(loader)

    # Process with panel
    result = await manager.process_with_panel(
        query=query,
        panel_persona=panel,
        context=context or {},
        llm_call_handler=None  # Mock mode for now
    )

    return result.to_dict()
