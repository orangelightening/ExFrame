"""
Survey API - Stubs for Surveyor UI

Endpoints for managing autonomous learning surveys.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Pydantic models
class SurveyLevel(str, Enum):
    DOMAIN = "domain"
    NEIGHBOURHOOD = "neighbourhood"
    UNIVERSE = "universe"


class SurveyStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SurveyRequest(BaseModel):
    name: str
    description: str
    level: SurveyLevel
    universe: str
    neighbourhood: Optional[str] = None
    domain: Optional[str] = None
    sources: List[str] = []
    target_patterns: int = 100
    min_confidence: float = 0.8
    timeline_hours: int = 24


class SurveyResponse(BaseModel):
    id: str
    name: str
    description: str
    level: str
    universe: str
    neighbourhood: Optional[str]
    domain: Optional[str]
    status: str
    progress: float
    patterns_created: int
    patterns_certified: int
    patterns_flagged: int
    patterns_rejected: int
    patterns_pending: int
    domains_created: int
    neighbourhoods_created: int
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]


class SurveyMetrics(BaseModel):
    survey_id: str
    pulse: str  # "●●●●●" or similar
    status: str
    progress: float
    throughput: float  # patterns per hour
    certification: dict
    judge_activity: dict
    errors: int
    focus: float


# Router
router = APIRouter(prefix="/api/surveys", tags=["surveys"])

# In-memory storage (stubs)
_surveys: dict = {}


@router.get("", response_model=List[SurveyResponse])
async def list_surveys():
    """List all surveys"""
    return [
        SurveyResponse(
            id=survey_id,
            **survey
        )
        for survey_id, survey in _surveys.items()
    ]


@router.post("", response_model=SurveyResponse)
async def create_survey(request: SurveyRequest):
    """Create a new survey"""
    import uuid
    survey_id = str(uuid.uuid4())[:8]

    survey = {
        "id": survey_id,
        "name": request.name,
        "description": request.description,
        "level": request.level.value,
        "universe": request.universe,
        "neighbourhood": request.neighbourhood,
        "domain": request.domain,
        "status": SurveyStatus.IDLE.value,
        "progress": 0.0,
        "patterns_created": 0,
        "patterns_certified": 0,
        "patterns_flagged": 0,
        "patterns_rejected": 0,
        "patterns_pending": 0,
        "domains_created": 0,
        "neighbourhoods_created": 0,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "error_message": None,
    }

    _surveys[survey_id] = survey
    return SurveyResponse(**survey)


@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(survey_id: str):
    """Get survey details"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")
    return SurveyResponse(id=survey_id, **_surveys[survey_id])


@router.put("/{survey_id}", response_model=SurveyResponse)
async def update_survey(survey_id: str, request: SurveyRequest):
    """Update survey"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey = _surveys[survey_id]
    survey.update({
        "name": request.name,
        "description": request.description,
        "level": request.level.value,
        "universe": request.universe,
        "neighbourhood": request.neighbourhood,
        "domain": request.domain,
    })

    return SurveyResponse(id=survey_id, **survey)


@router.delete("/{survey_id}")
async def delete_survey(survey_id: str):
    """Delete survey"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")
    del _surveys[survey_id]
    return {"message": "Survey deleted"}


@router.post("/{survey_id}/start", response_model=SurveyResponse)
async def start_survey(survey_id: str):
    """Start a survey"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey = _surveys[survey_id]
    survey["status"] = SurveyStatus.RUNNING.value
    survey["started_at"] = datetime.utcnow().isoformat()

    return SurveyResponse(id=survey_id, **survey)


@router.post("/{survey_id}/stop", response_model=SurveyResponse)
async def stop_survey(survey_id: str):
    """Stop a survey"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey = _surveys[survey_id]
    survey["status"] = SurveyStatus.IDLE.value

    return SurveyResponse(id=survey_id, **survey)


@router.post("/{survey_id}/pause", response_model=SurveyResponse)
async def pause_survey(survey_id: str):
    """Pause a survey"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey = _surveys[survey_id]
    survey["status"] = SurveyStatus.PAUSED.value

    return SurveyResponse(id=survey_id, **survey)


@router.post("/{survey_id}/resume", response_model=SurveyResponse)
async def resume_survey(survey_id: str):
    """Resume a paused survey"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey = _surveys[survey_id]
    if survey["status"] != SurveyStatus.PAUSED.value:
        raise HTTPException(status_code=400, detail="Survey is not paused")

    survey["status"] = SurveyStatus.RUNNING.value

    return SurveyResponse(id=survey_id, **survey)


@router.get("/{survey_id}/metrics", response_model=SurveyMetrics)
async def get_survey_metrics(survey_id: str):
    """Get real-time survey metrics"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey = _surveys[survey_id]

    return SurveyMetrics(
        survey_id=survey_id,
        pulse="●●●●●" if survey["status"] == "running" else "○○○○○",
        status=survey["status"],
        progress=survey["progress"],
        throughput=3.2,  # stub
        certification={
            "certified": survey["patterns_certified"],
            "flagged": survey["patterns_flagged"],
            "rejected": survey["patterns_rejected"],
            "pending": survey["patterns_pending"],
        },
        judge_activity={
            "J1": 80,
            "J2": 82,
            "J3": 78,
            "J4": 85,
            "J5": 0,  # human
        },
        errors=2,
        focus=0.94,
    )


@router.get("/{survey_id}/patterns")
async def get_survey_patterns(survey_id: str):
    """Get patterns from survey"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")
    # STUB: Return empty list for now
    return {"patterns": []}


@router.get("/{survey_id}/report")
async def get_survey_report(survey_id: str):
    """Get survey report"""
    if survey_id not in _surveys:
        raise HTTPException(status_code=404, detail="Survey not found")
    # STUB: Return basic report
    survey = _surveys[survey_id]
    return {
        "survey_id": survey_id,
        "name": survey["name"],
        "summary": f"Survey completed with {survey['patterns_certified']} certified patterns",
    }


# Add stub surveys for demo
def init_stub_surveys():
    """Initialize stub surveys for demo"""
    import uuid

    _surveys["culinary_arts"] = {
        "id": "culinary_arts",
        "name": "Culinary Arts",
        "description": "Automatic recipe extraction and certification from 3 cooking domains",
        "level": "neighbourhood",
        "universe": "default",
        "neighbourhood": "parksville_bc",
        "domain": None,
        "status": "running",
        "progress": 0.85,
        "patterns_created": 47,
        "patterns_certified": 42,
        "patterns_flagged": 3,
        "patterns_rejected": 2,
        "patterns_pending": 5,
        "domains_created": 0,
        "neighbourhoods_created": 0,
        "created_at": "2026-01-12T10:00:00",
        "started_at": "2026-01-12T10:05:00",
        "completed_at": None,
        "error_message": None,
    }

    _surveys["python_basics"] = {
        "id": "python_basics",
        "name": "Python Basics",
        "description": "Python code patterns and best practices",
        "level": "domain",
        "universe": "default",
        "neighbourhood": "technical_skills",
        "domain": "python",
        "status": "idle",
        "progress": 0.0,
        "patterns_created": 0,
        "patterns_certified": 0,
        "patterns_flagged": 0,
        "patterns_rejected": 0,
        "patterns_pending": 0,
        "domains_created": 0,
        "neighbourhoods_created": 0,
        "created_at": "2026-01-12T09:00:00",
        "started_at": None,
        "completed_at": None,
        "error_message": None,
    }


# Initialize stubs on import
init_stub_surveys()
