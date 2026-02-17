"""
Data models for BrainUse vetting system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Candidate(BaseModel):
    """Candidate undergoing assessment."""

    candidate_id: str = Field(..., description="Unique identifier (UUID)")
    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Contact email")
    role: str = Field(..., description="Target role (e.g., 'Senior Backend Engineer')")
    company: str = Field(..., description="Hiring company")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending", description="pending|in_progress|completed|hired|rejected")

    # Consent and legal
    consent_given: bool = Field(default=False)
    consent_timestamp: Optional[datetime] = None

    # Assessment configuration
    assessment_domains: List[str] = Field(
        default=["python_assessment", "cloud_assessment", "leadership_assessment"],
        description="Domains to assess"
    )
    assessment_start: Optional[datetime] = None
    assessment_end: Optional[datetime] = None

    # Metadata
    recruiter_notes: Optional[str] = None
    resume_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "candidate_id": "c7f1a2b3-4d5e-6f7g-8h9i-0j1k2l3m4n5o",
                "name": "Jane Doe",
                "email": "jane@example.com",
                "role": "Senior Backend Engineer",
                "company": "TechCorp",
                "status": "in_progress",
                "assessment_domains": ["python_assessment", "cloud_assessment", "database_assessment"]
            }
        }


class Assessment(BaseModel):
    """Assessment results for a candidate."""

    assessment_id: str = Field(..., description="Unique identifier")
    candidate_id: str = Field(..., description="Foreign key to candidate")

    # Core metrics (from Tao analysis)
    learning_velocity: float = Field(..., description="Levels per day")
    avg_sophistication: float = Field(..., description="Average question level 1-4")
    chain_depth: float = Field(..., description="Average queries per exploration chain")
    concept_retention: float = Field(..., description="1.0 = perfect, >1.0 = needed more queries")
    interest_ratio: float = Field(..., description="Interesting domain velocity / Boring domain velocity")

    # Tao Index (composite score)
    tao_index: float = Field(..., description="Composite score 0-10")
    percentile: float = Field(..., description="Percentile vs benchmark 0-100")

    # Domain-specific scores
    domain_scores: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-domain metrics"
    )

    # Time metrics
    total_queries: int = Field(..., description="Total questions asked")
    total_sessions: int = Field(..., description="Number of sessions")
    total_time_minutes: float = Field(..., description="Total time spent")

    # Timestamps
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
                "candidate_id": "c7f1a2b3-4d5e-6f7g-8h9i-0j1k2l3m4n5o",
                "learning_velocity": 0.42,
                "avg_sophistication": 2.8,
                "chain_depth": 4.2,
                "concept_retention": 0.85,
                "interest_ratio": 0.72,
                "tao_index": 7.8,
                "percentile": 91.0,
                "total_queries": 47,
                "total_sessions": 8,
                "total_time_minutes": 320
            }
        }


class Benchmark(BaseModel):
    """Benchmark data for a specific role and company."""

    benchmark_id: str = Field(..., description="Unique identifier")
    role: str = Field(..., description="Role category")
    company: Optional[str] = Field(None, description="Company-specific benchmark")

    # Sample size
    sample_size: int = Field(..., description="Number of candidates in benchmark")

    # Metric distributions (percentiles)
    learning_velocity_p50: float
    learning_velocity_p75: float
    learning_velocity_p90: float

    sophistication_p50: float
    sophistication_p75: float
    sophistication_p90: float

    chain_depth_p50: float
    chain_depth_p75: float
    chain_depth_p90: float

    tao_index_p50: float
    tao_index_p75: float
    tao_index_p90: float

    # Updated timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "benchmark_id": "bench-001",
                "role": "Senior Backend Engineer",
                "company": None,
                "sample_size": 150,
                "learning_velocity_p50": 0.28,
                "learning_velocity_p75": 0.35,
                "learning_velocity_p90": 0.42,
                "tao_index_p50": 6.2,
                "tao_index_p75": 7.5,
                "tao_index_p90": 8.3
            }
        }


class Report(BaseModel):
    """Generated assessment report."""

    report_id: str = Field(..., description="Unique identifier")
    candidate_id: str = Field(..., description="Foreign key to candidate")
    assessment_id: str = Field(..., description="Foreign key to assessment")

    # Summary
    recommendation: str = Field(..., description="hire|maybe|pass")
    confidence: float = Field(..., description="0.0-1.0")
    summary: str = Field(..., description="2-3 sentence summary")

    # Detailed sections
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    learning_trajectory: str = Field(..., description="Description of learning curve")

    # Interview recommendations
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested interview questions based on assessment"
    )

    # Comparisons
    vs_benchmark: str = Field(..., description="How candidate compares to role benchmark")
    standout_metrics: List[str] = Field(
        default_factory=list,
        description="Metrics where candidate excels"
    )

    # Generated timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # PDF export path (if generated)
    pdf_path: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "rep-001",
                "candidate_id": "c7f1a2b3-4d5e-6f7g-8h9i-0j1k2l3m4n5o",
                "assessment_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
                "recommendation": "hire",
                "confidence": 0.92,
                "summary": "Exceptional learning velocity (91st percentile). Rapidly progressed from foundational to expert-level questions. Strong discipline in low-interest domains.",
                "strengths": [
                    "Top 3% learning velocity (0.42 levels/day)",
                    "Maintained focus in leadership domain despite low interest",
                    "Deep exploration chains (avg 4.2 queries)"
                ],
                "concerns": [
                    "Slightly lower retention score (0.85) - may need refreshers on complex topics"
                ],
                "follow_up_questions": [
                    "Explore GIL implications in recent projects",
                    "Discuss distributed consensus challenges"
                ]
            }
        }
