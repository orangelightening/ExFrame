"""
SQLAlchemy database models for BrainUse.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class CandidateDB(Base):
    """Candidate database model."""

    __tablename__ = "candidates"

    # Primary key
    candidate_id = Column(String(36), primary_key=True)

    # Basic info
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)

    # Status
    status = Column(String(50), nullable=False, default="pending")

    # Consent
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)

    # Assessment configuration
    assessment_domains = Column(JSON, nullable=False)  # List of domain IDs
    assessment_start = Column(DateTime, nullable=True)
    assessment_end = Column(DateTime, nullable=True)

    # Metadata
    recruiter_notes = Column(Text, nullable=True)
    resume_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = relationship("AssessmentDB", back_populates="candidate", cascade="all, delete-orphan")
    reports = relationship("ReportDB", back_populates="candidate", cascade="all, delete-orphan")


class AssessmentDB(Base):
    """Assessment database model."""

    __tablename__ = "assessments"

    # Primary key
    assessment_id = Column(String(36), primary_key=True)

    # Foreign key
    candidate_id = Column(String(36), ForeignKey("candidates.candidate_id"), nullable=False)

    # Core metrics
    learning_velocity = Column(Float, nullable=False)
    avg_sophistication = Column(Float, nullable=False)
    chain_depth = Column(Float, nullable=False)
    concept_retention = Column(Float, nullable=False)
    interest_ratio = Column(Float, nullable=False)

    # Tao Index (composite score)
    tao_index = Column(Float, nullable=False)
    percentile = Column(Float, nullable=False)

    # Domain-specific scores (JSON)
    domain_scores = Column(JSON, nullable=False)

    # Time metrics
    total_queries = Column(Integer, nullable=False)
    total_sessions = Column(Integer, nullable=False)
    total_time_minutes = Column(Float, nullable=False)

    # Timestamp
    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    candidate = relationship("CandidateDB", back_populates="assessments")
    reports = relationship("ReportDB", back_populates="assessment", cascade="all, delete-orphan")


class ReportDB(Base):
    """Report database model."""

    __tablename__ = "reports"

    # Primary key
    report_id = Column(String(36), primary_key=True)

    # Foreign keys
    candidate_id = Column(String(36), ForeignKey("candidates.candidate_id"), nullable=False)
    assessment_id = Column(String(36), ForeignKey("assessments.assessment_id"), nullable=False)

    # Summary
    recommendation = Column(String(50), nullable=False)  # hire|maybe|pass
    confidence = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)

    # Detailed sections (JSON arrays)
    strengths = Column(JSON, nullable=False)
    concerns = Column(JSON, nullable=False)
    follow_up_questions = Column(JSON, nullable=False)
    standout_metrics = Column(JSON, nullable=False)

    # Text sections
    learning_trajectory = Column(Text, nullable=False)
    vs_benchmark = Column(Text, nullable=False)

    # Timestamp
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # PDF path (if generated)
    pdf_path = Column(String(500), nullable=True)

    # Relationships
    candidate = relationship("CandidateDB", back_populates="reports")
    assessment = relationship("AssessmentDB", back_populates="reports")


class BenchmarkDB(Base):
    """Benchmark database model."""

    __tablename__ = "benchmarks"

    # Primary key
    benchmark_id = Column(String(36), primary_key=True)

    # Role info
    role = Column(String(255), nullable=False, unique=True)
    company = Column(String(255), nullable=True)  # Company-specific benchmark

    # Sample size
    sample_size = Column(Integer, nullable=False)

    # Learning velocity percentiles
    learning_velocity_p50 = Column(Float, nullable=False)
    learning_velocity_p75 = Column(Float, nullable=False)
    learning_velocity_p90 = Column(Float, nullable=False)

    # Sophistication percentiles
    sophistication_p50 = Column(Float, nullable=False)
    sophistication_p75 = Column(Float, nullable=False)
    sophistication_p90 = Column(Float, nullable=False)

    # Chain depth percentiles
    chain_depth_p50 = Column(Float, nullable=False)
    chain_depth_p75 = Column(Float, nullable=False)
    chain_depth_p90 = Column(Float, nullable=False)

    # Tao Index percentiles
    tao_index_p50 = Column(Float, nullable=False)
    tao_index_p75 = Column(Float, nullable=False)
    tao_index_p90 = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
