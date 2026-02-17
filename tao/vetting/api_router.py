"""
BrainUse API Router - REST endpoints for hiring intelligence.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import logging

from .models import Candidate, Assessment, Report
from .candidate_manager import CandidateManager
from .benchmark_engine import BenchmarkEngine
from .report_generator import ReportGenerator

logger = logging.getLogger("tao.vetting.api")

router = APIRouter(prefix="/api/brainuse", tags=["brainuse"])

# Initialize components (in-memory for MVP)
candidate_manager = CandidateManager()
benchmark_engine = BenchmarkEngine()
report_generator = ReportGenerator(benchmark_engine)


# Request/Response models
class CreateCandidateRequest(BaseModel):
    name: str
    email: str
    role: str
    company: str
    assessment_domains: List[str] = ["python_assessment", "cloud_assessment", "leadership_assessment"]
    recruiter_notes: Optional[str] = None


class ConsentRequest(BaseModel):
    candidate_id: str
    consent_given: bool


@router.post("/candidates", response_model=Candidate)
async def create_candidate(request: CreateCandidateRequest):
    """
    Create new candidate for assessment.

    Args:
        request: Candidate details

    Returns:
        Created candidate object
    """
    try:
        candidate = candidate_manager.create_candidate(
            name=request.name,
            email=request.email,
            role=request.role,
            company=request.company,
            assessment_domains=request.assessment_domains,
            recruiter_notes=request.recruiter_notes
        )
        return candidate

    except Exception as e:
        logger.error(f"Error creating candidate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates", response_model=List[Candidate])
async def list_candidates(
    status: Optional[str] = Query(None, description="Filter by status"),
    company: Optional[str] = Query(None, description="Filter by company")
):
    """
    List candidates with optional filters.

    Args:
        status: Filter by status (pending|in_progress|completed|hired|rejected)
        company: Filter by company

    Returns:
        List of matching candidates
    """
    try:
        candidates = candidate_manager.list_candidates(status=status, company=company)
        return candidates

    except Exception as e:
        logger.error(f"Error listing candidates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: str):
    """
    Get candidate by ID.

    Args:
        candidate_id: Candidate UUID

    Returns:
        Candidate object
    """
    try:
        candidate = candidate_manager.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        return candidate

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/candidates/{candidate_id}", response_model=Candidate)
async def update_candidate(candidate_id: str, request: CreateCandidateRequest):
    """
    Update candidate information.

    Args:
        candidate_id: Candidate UUID
        request: Updated candidate data

    Returns:
        Updated candidate object
    """
    try:
        # Get existing candidate
        candidate = candidate_manager.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        # Update fields
        candidate.name = request.name
        candidate.email = request.email
        candidate.role = request.role
        candidate.company = request.company
        candidate.assessment_domains = request.assessment_domains
        if request.recruiter_notes is not None:
            candidate.recruiter_notes = request.recruiter_notes

        # Save updates
        success = candidate_manager.update_candidate(candidate)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update candidate")

        logger.info(f"Updated candidate {candidate_id}: {candidate.name}")
        return candidate

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating candidate {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """
    Delete candidate.

    Args:
        candidate_id: Candidate UUID

    Returns:
        Success message
    """
    try:
        from .database import get_db
        from .db_models import CandidateDB

        db = get_db()
        try:
            db_candidate = db.query(CandidateDB).filter(
                CandidateDB.candidate_id == candidate_id
            ).first()

            if not db_candidate:
                raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

            db.delete(db_candidate)
            db.commit()

            logger.info(f"Deleted candidate {candidate_id}")
            return {"status": "deleted", "candidate_id": candidate_id}

        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting candidate {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/candidates/{candidate_id}/consent")
async def record_consent(candidate_id: str, request: ConsentRequest):
    """
    Record candidate consent for assessment.

    GDPR/legal requirement: Must have explicit consent before starting assessment.

    Args:
        candidate_id: Candidate UUID
        request: Consent status

    Returns:
        Updated candidate
    """
    try:
        candidate = candidate_manager.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        from datetime import datetime
        candidate.consent_given = request.consent_given
        candidate.consent_timestamp = datetime.utcnow()

        success = candidate_manager.update_candidate(candidate)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update candidate consent")

        return {"status": "consent recorded", "candidate_id": candidate_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording consent for {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/candidates/{candidate_id}/start")
async def start_assessment(candidate_id: str):
    """
    Start assessment for candidate.

    Prerequisites:
    - Candidate must have given consent
    - Assessment domains must be configured

    Args:
        candidate_id: Candidate UUID

    Returns:
        Status and next steps
    """
    try:
        success = candidate_manager.start_assessment(candidate_id)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Cannot start assessment. Check consent and configuration."
            )

        candidate = candidate_manager.get_candidate(candidate_id)

        return {
            "status": "assessment started",
            "candidate_id": candidate_id,
            "assessment_domains": candidate.assessment_domains,
            "instructions": "Candidate should complete queries in each assessment domain over the next 10 days"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting assessment for {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/candidates/{candidate_id}/complete", response_model=Assessment)
async def complete_assessment(candidate_id: str):
    """
    Complete assessment and calculate metrics.

    This should be called after the 10-day assessment period.

    Args:
        candidate_id: Candidate UUID

    Returns:
        Assessment object with calculated metrics
    """
    try:
        assessment = candidate_manager.complete_assessment(candidate_id)

        # Calculate percentile
        candidate = candidate_manager.get_candidate(candidate_id)
        assessment.percentile = benchmark_engine.calculate_percentile(assessment, candidate.role)

        return assessment

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error completing assessment for {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates/{candidate_id}/report")
async def get_report(candidate_id: str):
    """
    Generate assessment report for candidate.

    Args:
        candidate_id: Candidate UUID

    Returns:
        Combined report with assessment metrics and recommendations
    """
    try:
        candidate = candidate_manager.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        if candidate.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Assessment not completed (status: {candidate.status})"
            )

        # Get or generate assessment
        # TODO: Store assessments and retrieve if already generated
        assessment = candidate_manager.complete_assessment(candidate_id)

        # Generate report
        report = report_generator.generate_report(candidate, assessment)

        # Return combined response with both report and assessment metrics
        return {
            # Report fields
            "report_id": report.report_id,
            "candidate_id": report.candidate_id,
            "assessment_id": report.assessment_id,
            "recommendation": report.recommendation,
            "confidence": report.confidence,
            "summary": report.summary,
            "strengths": report.strengths,
            "concerns": report.concerns,
            "learning_trajectory": report.learning_trajectory,
            "follow_up_questions": report.follow_up_questions,
            "vs_benchmark": report.vs_benchmark,
            "standout_metrics": report.standout_metrics,
            "generated_at": report.generated_at,

            # Assessment metrics (for charts and displays)
            "tao_index": assessment.tao_index,
            "percentile": assessment.percentile,
            "learning_velocity": assessment.learning_velocity,
            "avg_sophistication": assessment.avg_sophistication,
            "chain_depth": assessment.chain_depth,
            "concept_retention": assessment.concept_retention,
            "interest_ratio": assessment.interest_ratio,
            "domain_scores": assessment.domain_scores,
            "total_queries": assessment.total_queries,
            "total_sessions": assessment.total_sessions,
            "total_time_minutes": assessment.total_time_minutes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report for {candidate_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks", response_model=List[str])
async def list_benchmark_roles():
    """
    List available roles with benchmarks.

    Returns:
        List of role names
    """
    try:
        roles = benchmark_engine.list_roles()
        return roles

    except Exception as e:
        logger.error(f"Error listing benchmark roles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{role}")
async def get_benchmark(role: str):
    """
    Get benchmark data for a role.

    Args:
        role: Role name

    Returns:
        Benchmark object
    """
    try:
        benchmark = benchmark_engine.get_benchmark(role)

        if not benchmark:
            raise HTTPException(status_code=404, detail=f"No benchmark found for role '{role}'")

        return benchmark

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting benchmark for {role}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assessment-domains")
async def list_assessment_domains():
    """
    List available assessment domains.

    Returns:
        List of domain IDs with descriptions
    """
    try:
        domains = [
            {
                "id": "python_assessment",
                "name": "Python Programming",
                "description": "Core Python → Advanced patterns → Performance optimization"
            },
            {
                "id": "cloud_assessment",
                "name": "Cloud Infrastructure",
                "description": "AWS/GCP basics → Scalability → Advanced patterns"
            },
            {
                "id": "leadership_assessment",
                "name": "Technical Leadership",
                "description": "Team dynamics → Project management → Strategic thinking"
            },
            {
                "id": "database_assessment",
                "name": "Database Systems",
                "description": "SQL basics → Schema design → Distributed data"
            },
            {
                "id": "api_assessment",
                "name": "API Design",
                "description": "REST basics → Design principles → Distributed APIs"
            }
        ]

        return domains

    except Exception as e:
        logger.error(f"Error listing assessment domains: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "BrainUse Vetting System",
        "version": "1.0.0-mvp"
    }
