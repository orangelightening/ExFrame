"""
Report generator for BrainUse vetting system.

Generates comprehensive assessment reports with recommendations.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from uuid import uuid4

from .models import Report, Candidate, Assessment, Benchmark
from .benchmark_engine import BenchmarkEngine

logger = logging.getLogger("tao.vetting.report_generator")


class ReportGenerator:
    """
    Generates assessment reports for candidates.

    Responsibilities:
    - Analyze assessment metrics
    - Generate recommendations (hire/maybe/pass)
    - Identify strengths and concerns
    - Generate interview follow-up questions
    - Export to PDF (future)
    """

    def __init__(self, benchmark_engine: BenchmarkEngine):
        """
        Initialize report generator.

        Args:
            benchmark_engine: BenchmarkEngine instance for comparisons
        """
        self.benchmark_engine = benchmark_engine
        logger.info("ReportGenerator initialized")

    def generate_report(
        self,
        candidate: Candidate,
        assessment: Assessment
    ) -> Report:
        """
        Generate comprehensive assessment report.

        Args:
            candidate: Candidate object
            assessment: Assessment object with calculated metrics

        Returns:
            Report object with recommendations
        """
        # Calculate percentile vs benchmark
        percentile = self.benchmark_engine.calculate_percentile(assessment, candidate.role)
        assessment.percentile = percentile

        # Get benchmark comparisons
        comparisons = self.benchmark_engine.compare_to_benchmark(assessment, candidate.role)

        # Generate recommendation
        recommendation, confidence = self._generate_recommendation(assessment, percentile)

        # Identify strengths and concerns
        strengths = self._identify_strengths(assessment, comparisons)
        concerns = self._identify_concerns(assessment, comparisons)

        # Generate summary
        summary = self._generate_summary(candidate, assessment, percentile, recommendation)

        # Generate learning trajectory description
        trajectory = self._describe_learning_trajectory(assessment)

        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(candidate, assessment)

        # Identify standout metrics
        standout = self._identify_standout_metrics(assessment, comparisons)

        # Create report
        report = Report(
            report_id=str(uuid4()),
            candidate_id=candidate.candidate_id,
            assessment_id=assessment.assessment_id,
            recommendation=recommendation,
            confidence=confidence,
            summary=summary,
            strengths=strengths,
            concerns=concerns,
            learning_trajectory=trajectory,
            follow_up_questions=follow_up_questions,
            vs_benchmark=comparisons.get("overall", "No benchmark available"),
            standout_metrics=standout
        )

        logger.info(f"Generated report {report.report_id} for {candidate.name}: {recommendation}")
        return report

    def _generate_recommendation(
        self,
        assessment: Assessment,
        percentile: float
    ) -> Tuple[str, float]:
        """
        Generate hire recommendation.

        Decision logic:
        - hire: Percentile >= 75 AND velocity >= 0.30 AND interest_ratio >= 0.60
        - pass: Percentile < 50 OR velocity < 0.20 OR interest_ratio < 0.40
        - maybe: Everything else

        Args:
            assessment: Assessment object
            percentile: Percentile vs benchmark

        Returns:
            Tuple of (recommendation, confidence)
        """
        velocity = assessment.learning_velocity
        interest_ratio = assessment.interest_ratio
        tao_index = assessment.tao_index

        # Strong hire signals
        if percentile >= 90 and velocity >= 0.40 and interest_ratio >= 0.70:
            return "hire", 0.95

        if percentile >= 75 and velocity >= 0.30 and interest_ratio >= 0.60:
            return "hire", 0.85

        # Clear pass signals
        if percentile < 30 or velocity < 0.15 or interest_ratio < 0.30:
            return "pass", 0.90

        if percentile < 50 and velocity < 0.20:
            return "pass", 0.75

        # Maybe (needs interview to decide)
        if percentile >= 60:
            return "maybe", 0.60
        else:
            return "maybe", 0.55

    def _identify_strengths(
        self,
        assessment: Assessment,
        comparisons: Dict[str, str]
    ) -> List[str]:
        """Identify candidate strengths."""
        strengths = []

        # Learning velocity
        if assessment.learning_velocity >= 0.40:
            strengths.append(f"Exceptional learning velocity ({assessment.learning_velocity:.2f} levels/day, Top 3%)")
        elif assessment.learning_velocity >= 0.30:
            strengths.append(f"Strong learning velocity ({assessment.learning_velocity:.2f} levels/day)")

        # Question sophistication
        if assessment.avg_sophistication >= 3.0:
            strengths.append(f"Advanced question sophistication (avg {assessment.avg_sophistication:.1f}/4.0)")
        elif assessment.avg_sophistication >= 2.5:
            strengths.append(f"Strong question sophistication (avg {assessment.avg_sophistication:.1f}/4.0)")

        # Persistence (chain depth)
        if assessment.chain_depth >= 4.5:
            strengths.append(f"Exceptional persistence in exploration (avg {assessment.chain_depth:.1f} queries per chain)")
        elif assessment.chain_depth >= 3.5:
            strengths.append(f"Strong persistence in exploration (avg {assessment.chain_depth:.1f} queries per chain)")

        # Discipline (interest ratio)
        if assessment.interest_ratio >= 0.70:
            strengths.append(f"Excellent discipline in low-interest domains (interest ratio {assessment.interest_ratio:.2f})")
        elif assessment.interest_ratio >= 0.60:
            strengths.append(f"Good discipline in low-interest domains (interest ratio {assessment.interest_ratio:.2f})")

        # Retention
        if assessment.concept_retention <= 0.80:
            strengths.append(f"Strong concept retention (retention score {assessment.concept_retention:.2f})")

        # Domain-specific strengths
        for domain, scores in assessment.domain_scores.items():
            if scores["velocity"] >= 0.45:
                domain_name = domain.replace("_assessment", "").replace("_", " ").title()
                strengths.append(f"Exceptionally fast learning in {domain_name} domain")

        return strengths[:5]  # Top 5 strengths

    def _identify_concerns(
        self,
        assessment: Assessment,
        comparisons: Dict[str, str]
    ) -> List[str]:
        """Identify potential concerns."""
        concerns = []

        # Learning velocity
        if assessment.learning_velocity < 0.20:
            concerns.append(f"Below-average learning velocity ({assessment.learning_velocity:.2f} levels/day)")

        # Question sophistication
        if assessment.avg_sophistication < 2.0:
            concerns.append(f"Limited question sophistication (avg {assessment.avg_sophistication:.1f}/4.0)")

        # Persistence
        if assessment.chain_depth < 2.5:
            concerns.append(f"Low exploration persistence (avg {assessment.chain_depth:.1f} queries per chain)")

        # Discipline
        if assessment.interest_ratio < 0.50:
            concerns.append(f"Struggled with low-interest domains (interest ratio {assessment.interest_ratio:.2f})")

        # Retention
        if assessment.concept_retention > 1.20:
            concerns.append(f"May need refreshers on complex topics (retention score {assessment.concept_retention:.2f})")

        # Total queries (engagement)
        if assessment.total_queries < 30:
            concerns.append(f"Limited engagement in assessment ({assessment.total_queries} queries)")

        # Domain-specific concerns
        for domain, scores in assessment.domain_scores.items():
            if scores["velocity"] < 0.15:
                domain_name = domain.replace("_assessment", "").replace("_", " ").title()
                concerns.append(f"Slow learning in {domain_name} domain")

        return concerns[:4]  # Top 4 concerns

    def _generate_summary(
        self,
        candidate: Candidate,
        assessment: Assessment,
        percentile: float,
        recommendation: str
    ) -> str:
        """Generate 2-3 sentence summary."""
        # Headline based on recommendation
        if recommendation == "hire":
            headline = f"{int(percentile)}th percentile performer with strong learning velocity"
        elif recommendation == "pass":
            headline = f"Below benchmark performance in key learning metrics"
        else:
            headline = f"Mixed performance with some strong indicators"

        # Key metric
        if assessment.learning_velocity >= 0.35:
            metric_note = f"Rapidly progressed from foundational to expert-level questions ({assessment.learning_velocity:.2f} levels/day)"
        elif assessment.interest_ratio >= 0.70:
            metric_note = f"Demonstrated strong discipline across high and low-interest domains (ratio {assessment.interest_ratio:.2f})"
        elif assessment.chain_depth >= 4.0:
            metric_note = f"Deep exploration chains show strong persistence (avg {assessment.chain_depth:.1f} queries)"
        else:
            metric_note = f"Learning velocity of {assessment.learning_velocity:.2f} levels/day"

        # Overall assessment
        if recommendation == "hire":
            overall = "Strong candidate for role"
        elif recommendation == "pass":
            overall = "Consider other candidates"
        else:
            overall = "Recommend in-depth interview to assess fit"

        return f"{headline}. {metric_note}. {overall}."

    def _describe_learning_trajectory(self, assessment: Assessment) -> str:
        """Describe learning curve across assessment."""
        velocity = assessment.learning_velocity
        sophistication = assessment.avg_sophistication

        if velocity >= 0.40:
            pace = "exceptionally rapid"
        elif velocity >= 0.30:
            pace = "rapid"
        elif velocity >= 0.20:
            pace = "steady"
        else:
            pace = "slow"

        if sophistication >= 3.0:
            level = "advanced to expert"
        elif sophistication >= 2.5:
            level = "intermediate to advanced"
        elif sophistication >= 2.0:
            level = "intermediate"
        else:
            level = "foundational to intermediate"

        trajectory = f"Demonstrated {pace} progression through {level} level questions over {assessment.total_queries} queries across {assessment.total_sessions} sessions"

        # Add domain variation if significant
        velocities = [scores["velocity"] for scores in assessment.domain_scores.values()]
        if len(velocities) >= 2:
            max_vel = max(velocities)
            min_vel = min(velocities)
            if max_vel > min_vel * 1.5:
                trajectory += ". Faster learning in areas of high interest, but maintained discipline in all domains"

        return trajectory + "."

    def _generate_follow_up_questions(
        self,
        candidate: Candidate,
        assessment: Assessment
    ) -> List[str]:
        """Generate interview questions based on assessment."""
        questions = []

        # Based on domains assessed
        for domain, scores in assessment.domain_scores.items():
            domain_name = domain.replace("_assessment", "").replace("_", " ")

            if scores["sophistication"] >= 3.0:
                # They reached advanced topics - go deeper
                if "python" in domain:
                    questions.append("Explore GIL implications in recent projects")
                elif "cloud" in domain:
                    questions.append("Discuss distributed systems challenges in production")
                elif "database" in domain:
                    questions.append("Deep dive on consistency trade-offs in past systems")
                elif "api" in domain:
                    questions.append("Explore API design decisions in previous work")

            elif scores["velocity"] < 0.20:
                # Struggled in this domain - verify understanding
                questions.append(f"Verify foundational understanding of {domain_name} concepts")

        # Based on interest ratio
        if assessment.interest_ratio < 0.60:
            questions.append("Assess motivation and self-discipline in less interesting work")

        # Based on chain depth
        if assessment.chain_depth >= 4.5:
            questions.append("Discuss problem-solving approach and persistence through challenges")

        return questions[:5]  # Top 5 questions

    def _identify_standout_metrics(
        self,
        assessment: Assessment,
        comparisons: Dict[str, str]
    ) -> List[str]:
        """Identify metrics where candidate significantly outperforms benchmark."""
        standout = []

        # Check each metric against comparisons
        for metric, comparison in comparisons.items():
            if "Exceptional" in comparison or "Top 10%" in comparison:
                if metric == "velocity":
                    standout.append(f"Learning Velocity: {assessment.learning_velocity:.2f} levels/day (Top 10%)")
                elif metric == "sophistication":
                    standout.append(f"Question Sophistication: {assessment.avg_sophistication:.1f}/4.0 (Top 10%)")
                elif metric == "persistence":
                    standout.append(f"Exploration Depth: {assessment.chain_depth:.1f} queries/chain (Top 10%)")

        # Interest ratio if exceptional
        if assessment.interest_ratio >= 0.75:
            standout.append(f"Interest Ratio: {assessment.interest_ratio:.2f} (exceptional discipline)")

        return standout

    def export_to_pdf(self, report: Report, output_path: str) -> bool:
        """
        Export report to PDF.

        Args:
            report: Report object
            output_path: Path to save PDF

        Returns:
            True if successful

        Note: PDF generation not yet implemented
        """
        # TODO: Implement PDF generation
        # - Use ReportLab or WeasyPrint
        # - Format with company branding
        # - Include charts/visualizations
        logger.warning("PDF export not yet implemented")
        return False
