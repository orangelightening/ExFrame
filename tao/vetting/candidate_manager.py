"""
Candidate management for BrainUse vetting system.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from .models import Candidate, Assessment
from .database import get_db
from .db_models import CandidateDB, AssessmentDB

logger = logging.getLogger("tao.vetting.candidate_manager")


class CandidateManager:
    """
    Manages candidate lifecycle from creation to assessment completion.

    Now uses PostgreSQL for persistence.
    """

    def __init__(self):
        """Initialize candidate manager with database connection."""
        logger.info("CandidateManager initialized with database persistence")

    def create_candidate(
        self,
        name: str,
        email: str,
        role: str,
        company: str,
        assessment_domains: List[str],
        recruiter_notes: Optional[str] = None
    ) -> Candidate:
        """
        Create new candidate and save to database.

        Args:
            name: Candidate name
            email: Contact email
            role: Target role
            company: Hiring company
            assessment_domains: List of domain IDs
            recruiter_notes: Optional notes from recruiter

        Returns:
            Candidate object
        """
        candidate_id = str(uuid4())

        # Create candidate model
        candidate = Candidate(
            candidate_id=candidate_id,
            name=name,
            email=email,
            role=role,
            company=company,
            assessment_domains=assessment_domains,
            recruiter_notes=recruiter_notes,
            status="pending"
        )

        # Save to database
        db = get_db()
        try:
            db_candidate = CandidateDB(
                candidate_id=candidate.candidate_id,
                name=candidate.name,
                email=candidate.email,
                role=candidate.role,
                company=candidate.company,
                status=candidate.status,
                consent_given=candidate.consent_given,
                consent_timestamp=candidate.consent_timestamp,
                assessment_domains=candidate.assessment_domains,
                assessment_start=candidate.assessment_start,
                assessment_end=candidate.assessment_end,
                recruiter_notes=candidate.recruiter_notes,
                resume_url=candidate.resume_url,
                created_at=candidate.created_at
            )

            db.add(db_candidate)
            db.commit()
            db.refresh(db_candidate)

            logger.info(f"Created candidate {candidate_id}: {name} for role {role}")

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating candidate: {e}")
            raise
        finally:
            db.close()

        return candidate

    def start_assessment(self, candidate_id: str) -> bool:
        """
        Start assessment for candidate.

        Args:
            candidate_id: Candidate UUID

        Returns:
            True if started successfully
        """
        db = get_db()
        try:
            db_candidate = db.query(CandidateDB).filter(
                CandidateDB.candidate_id == candidate_id
            ).first()

            if not db_candidate:
                logger.error(f"Candidate {candidate_id} not found")
                return False

            if not db_candidate.consent_given:
                logger.error(f"Cannot start assessment - consent not given for {candidate_id}")
                return False

            # Update status
            db_candidate.status = "in_progress"
            db_candidate.assessment_start = datetime.utcnow()
            db_candidate.updated_at = datetime.utcnow()

            db.commit()

            logger.info(f"Started assessment for candidate {candidate_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error starting assessment: {e}")
            raise
        finally:
            db.close()

    def complete_assessment(self, candidate_id: str) -> Assessment:
        """
        Complete assessment and calculate final metrics.

        Args:
            candidate_id: Candidate UUID

        Returns:
            Assessment object with calculated metrics
        """
        db = get_db()
        try:
            db_candidate = db.query(CandidateDB).filter(
                CandidateDB.candidate_id == candidate_id
            ).first()

            if not db_candidate:
                raise ValueError(f"Candidate {candidate_id} not found")

            # Update candidate status
            db_candidate.status = "completed"
            db_candidate.assessment_end = datetime.utcnow()
            db_candidate.updated_at = datetime.utcnow()

            # Calculate metrics from query history
            candidate = self._db_to_model(db_candidate)
            assessment = self._calculate_assessment_metrics(candidate)

            # Save assessment to database
            db_assessment = AssessmentDB(
                assessment_id=assessment.assessment_id,
                candidate_id=assessment.candidate_id,
                learning_velocity=assessment.learning_velocity,
                avg_sophistication=assessment.avg_sophistication,
                chain_depth=assessment.chain_depth,
                concept_retention=assessment.concept_retention,
                interest_ratio=assessment.interest_ratio,
                tao_index=assessment.tao_index,
                percentile=assessment.percentile,
                domain_scores=assessment.domain_scores,
                total_queries=assessment.total_queries,
                total_sessions=assessment.total_sessions,
                total_time_minutes=assessment.total_time_minutes,
                completed_at=assessment.completed_at
            )

            db.add(db_assessment)
            db.commit()

            logger.info(f"Completed assessment for {candidate_id}: Tao Index = {assessment.tao_index}")

            return assessment

        except Exception as e:
            db.rollback()
            logger.error(f"Error completing assessment: {e}")
            raise
        finally:
            db.close()

    def _calculate_assessment_metrics(self, candidate: Candidate) -> Assessment:
        """
        Calculate assessment metrics from candidate's query history.

        Uses Tao analysis modules.
        """
        from tao.storage import load_history
        from tao.analysis import sophistication, depth, concepts

        domain_scores = {}
        all_velocities = []
        all_sophistications = []
        all_chain_depths = []

        total_queries = 0
        total_sessions = 0
        total_time = 0.0

        # Calculate metrics for each domain
        for domain in candidate.assessment_domains:
            history = load_history(domain)
            if not history:
                logger.warning(f"No history found for domain {domain}")
                continue

            # Learning velocity
            velocity_result = sophistication.calculate_learning_velocity(
                history, domain, min_questions=3
            )

            if "error" not in velocity_result:
                velocity = velocity_result["velocity"]
                avg_soph = (velocity_result["initial_level"] + velocity_result["final_level"]) / 2
            else:
                velocity = 0.0
                avg_soph = 1.0

            # Chain depth
            deep_explorations = depth.find_deep_explorations(history, min_depth=2, time_gap=10)
            avg_chain_depth = sum(e["query_count"] for e in deep_explorations) / len(deep_explorations) if deep_explorations else 1.0

            # Concept retention (simplified)
            retention_score = 1.0

            # Store domain scores
            domain_scores[domain] = {
                "velocity": velocity,
                "sophistication": avg_soph,
                "chain_depth": avg_chain_depth,
                "retention": retention_score,
                "queries": len(history)
            }

            all_velocities.append(velocity)
            all_sophistications.append(avg_soph)
            all_chain_depths.append(avg_chain_depth)

            total_queries += len(history)

        # Calculate aggregate metrics
        learning_velocity = sum(all_velocities) / len(all_velocities) if all_velocities else 0.0
        avg_sophistication = sum(all_sophistications) / len(all_sophistications) if all_sophistications else 1.0
        chain_depth = sum(all_chain_depths) / len(all_chain_depths) if all_chain_depths else 1.0
        concept_retention = 1.0

        # Interest ratio (boring vs interesting domains)
        interesting_domains = [d for d in candidate.assessment_domains if "leadership" not in d]
        boring_domains = [d for d in candidate.assessment_domains if "leadership" in d]

        interesting_velocity = sum(
            domain_scores[d]["velocity"] for d in interesting_domains if d in domain_scores
        ) / len(interesting_domains) if interesting_domains else 0.0

        boring_velocity = sum(
            domain_scores[d]["velocity"] for d in boring_domains if d in domain_scores
        ) / len(boring_domains) if boring_domains else 0.0

        interest_ratio = boring_velocity / interesting_velocity if interesting_velocity > 0 else 0.0

        # Calculate Tao Index
        tao_index = (
            learning_velocity * 0.3 +
            avg_sophistication * 0.3 +
            chain_depth * 0.2 +
            concept_retention * 0.2
        )

        # Create assessment
        assessment = Assessment(
            assessment_id=str(uuid4()),
            candidate_id=candidate.candidate_id,
            learning_velocity=learning_velocity,
            avg_sophistication=avg_sophistication,
            chain_depth=chain_depth,
            concept_retention=concept_retention,
            interest_ratio=interest_ratio,
            tao_index=tao_index,
            percentile=0.0,  # Will be calculated by benchmark engine
            domain_scores=domain_scores,
            total_queries=total_queries,
            total_sessions=total_sessions,
            total_time_minutes=total_time
        )

        return assessment

    def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        """Get candidate by ID from database."""
        db = get_db()
        try:
            db_candidate = db.query(CandidateDB).filter(
                CandidateDB.candidate_id == candidate_id
            ).first()

            if not db_candidate:
                return None

            return self._db_to_model(db_candidate)

        finally:
            db.close()

    def list_candidates(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Candidate]:
        """
        List candidates with optional filters.

        Args:
            status: Filter by status
            company: Filter by company

        Returns:
            List of matching candidates
        """
        db = get_db()
        try:
            query = db.query(CandidateDB)

            # Apply filters
            if status:
                query = query.filter(CandidateDB.status == status)
            if company:
                query = query.filter(CandidateDB.company == company)

            # Order by created_at descending (newest first)
            query = query.order_by(CandidateDB.created_at.desc())

            db_candidates = query.all()

            return [self._db_to_model(db_c) for db_c in db_candidates]

        finally:
            db.close()

    def update_candidate(self, candidate: Candidate) -> bool:
        """Update candidate in database."""
        db = get_db()
        try:
            db_candidate = db.query(CandidateDB).filter(
                CandidateDB.candidate_id == candidate.candidate_id
            ).first()

            if not db_candidate:
                return False

            # Update fields
            db_candidate.name = candidate.name
            db_candidate.email = candidate.email
            db_candidate.role = candidate.role
            db_candidate.company = candidate.company
            db_candidate.status = candidate.status
            db_candidate.consent_given = candidate.consent_given
            db_candidate.consent_timestamp = candidate.consent_timestamp
            db_candidate.assessment_domains = candidate.assessment_domains
            db_candidate.assessment_start = candidate.assessment_start
            db_candidate.assessment_end = candidate.assessment_end
            db_candidate.recruiter_notes = candidate.recruiter_notes
            db_candidate.resume_url = candidate.resume_url
            db_candidate.updated_at = datetime.utcnow()

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating candidate: {e}")
            raise
        finally:
            db.close()

    def _db_to_model(self, db_candidate: CandidateDB) -> Candidate:
        """Convert database model to Pydantic model."""
        return Candidate(
            candidate_id=db_candidate.candidate_id,
            name=db_candidate.name,
            email=db_candidate.email,
            role=db_candidate.role,
            company=db_candidate.company,
            created_at=db_candidate.created_at,
            status=db_candidate.status,
            consent_given=db_candidate.consent_given,
            consent_timestamp=db_candidate.consent_timestamp,
            assessment_domains=db_candidate.assessment_domains,
            assessment_start=db_candidate.assessment_start,
            assessment_end=db_candidate.assessment_end,
            recruiter_notes=db_candidate.recruiter_notes,
            resume_url=db_candidate.resume_url
        )
