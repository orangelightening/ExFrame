"""
Benchmark engine for BrainUse vetting system.

Manages role-based benchmarks and percentile calculations.
"""

import logging
from typing import Dict, List, Optional
import numpy as np

from .models import Benchmark, Assessment

logger = logging.getLogger("tao.vetting.benchmark_engine")


class BenchmarkEngine:
    """
    Manages benchmarking data for candidate comparison.

    Responsibilities:
    - Store and retrieve role-based benchmarks
    - Calculate percentiles for candidates
    - Update benchmarks as more data is collected
    - Generate comparative insights
    """

    def __init__(self, db_connection=None):
        """
        Initialize benchmark engine.

        Args:
            db_connection: Database connection (PostgreSQL)
                          If None, uses built-in default benchmarks
        """
        self.db = db_connection
        self._default_benchmarks = self._load_default_benchmarks()
        logger.info("BenchmarkEngine initialized")

    def _load_default_benchmarks(self) -> Dict[str, Benchmark]:
        """
        Load default benchmarks for common roles.

        These are based on industry data and will be refined as we collect real data.

        Returns:
            Dict mapping role to Benchmark object
        """
        benchmarks = {
            "Senior Backend Engineer": Benchmark(
                benchmark_id="bench-senior-backend",
                role="Senior Backend Engineer",
                sample_size=100,  # Assumed from industry data
                learning_velocity_p50=0.28,
                learning_velocity_p75=0.35,
                learning_velocity_p90=0.42,
                sophistication_p50=2.4,
                sophistication_p75=2.8,
                sophistication_p90=3.2,
                chain_depth_p50=3.0,
                chain_depth_p75=3.8,
                chain_depth_p90=4.5,
                tao_index_p50=6.2,
                tao_index_p75=7.5,
                tao_index_p90=8.3
            ),
            "Junior Backend Engineer": Benchmark(
                benchmark_id="bench-junior-backend",
                role="Junior Backend Engineer",
                sample_size=80,
                learning_velocity_p50=0.22,
                learning_velocity_p75=0.28,
                learning_velocity_p90=0.35,
                sophistication_p50=1.8,
                sophistication_p75=2.2,
                sophistication_p90=2.6,
                chain_depth_p50=2.2,
                chain_depth_p75=2.8,
                chain_depth_p90=3.4,
                tao_index_p50=5.0,
                tao_index_p75=6.2,
                tao_index_p90=7.0
            ),
            "Staff Engineer": Benchmark(
                benchmark_id="bench-staff",
                role="Staff Engineer",
                sample_size=50,
                learning_velocity_p50=0.32,
                learning_velocity_p75=0.40,
                learning_velocity_p90=0.50,
                sophistication_p50=2.8,
                sophistication_p75=3.2,
                sophistication_p90=3.6,
                chain_depth_p50=3.5,
                chain_depth_p75=4.5,
                chain_depth_p90=5.5,
                tao_index_p50=7.0,
                tao_index_p75=8.2,
                tao_index_p90=9.1
            ),
            "Engineering Manager": Benchmark(
                benchmark_id="bench-em",
                role="Engineering Manager",
                sample_size=60,
                learning_velocity_p50=0.25,
                learning_velocity_p75=0.32,
                learning_velocity_p90=0.40,
                sophistication_p50=2.3,
                sophistication_p75=2.7,
                sophistication_p90=3.1,
                chain_depth_p50=2.8,
                chain_depth_p75=3.5,
                chain_depth_p90=4.2,
                tao_index_p50=5.8,
                tao_index_p75=7.0,
                tao_index_p90=7.8
            )
        }

        return benchmarks

    def get_benchmark(self, role: str, company: Optional[str] = None) -> Optional[Benchmark]:
        """
        Get benchmark for a role.

        Args:
            role: Role title
            company: Optional company-specific benchmark

        Returns:
            Benchmark object or None if not found
        """
        # Try to load from database first
        try:
            from .database import get_db
            from .db_models import BenchmarkDB

            db = get_db()
            try:
                # Check for company-specific benchmark first
                if company:
                    db_benchmark = db.query(BenchmarkDB).filter(
                        BenchmarkDB.role == role,
                        BenchmarkDB.company == company
                    ).first()

                    if db_benchmark:
                        return self._db_to_model(db_benchmark)

                # Fall back to generic benchmark for role
                db_benchmark = db.query(BenchmarkDB).filter(
                    BenchmarkDB.role == role,
                    BenchmarkDB.company == None
                ).first()

                if db_benchmark:
                    return self._db_to_model(db_benchmark)

            finally:
                db.close()

        except Exception as e:
            logger.warning(f"Could not load benchmark from database: {e}")

        # Fall back to default benchmarks
        return self._default_benchmarks.get(role)

    def calculate_percentile(self, assessment: Assessment, role: str) -> float:
        """
        Calculate candidate's percentile vs role benchmark.

        Args:
            assessment: Candidate assessment
            role: Target role

        Returns:
            Percentile (0-100)
        """
        benchmark = self.get_benchmark(role)
        if not benchmark:
            logger.warning(f"No benchmark found for role {role}")
            return 50.0  # Default to median

        # Calculate percentile based on Tao Index
        tao_index = assessment.tao_index

        # Interpolate between percentile markers
        if tao_index <= benchmark.tao_index_p50:
            # Below median
            percentile = 50.0 * (tao_index / benchmark.tao_index_p50)
        elif tao_index <= benchmark.tao_index_p75:
            # Between p50 and p75
            percentile = 50.0 + 25.0 * (
                (tao_index - benchmark.tao_index_p50) /
                (benchmark.tao_index_p75 - benchmark.tao_index_p50)
            )
        elif tao_index <= benchmark.tao_index_p90:
            # Between p75 and p90
            percentile = 75.0 + 15.0 * (
                (tao_index - benchmark.tao_index_p75) /
                (benchmark.tao_index_p90 - benchmark.tao_index_p75)
            )
        else:
            # Above p90
            percentile = 90.0 + 10.0 * min(
                (tao_index - benchmark.tao_index_p90) /
                (benchmark.tao_index_p90 * 0.1),
                1.0
            )

        return min(percentile, 99.9)

    def compare_to_benchmark(self, assessment: Assessment, role: str) -> Dict[str, str]:
        """
        Generate human-readable comparison to benchmark.

        Args:
            assessment: Candidate assessment
            role: Target role

        Returns:
            Dict with comparison insights for each metric
        """
        benchmark = self.get_benchmark(role)
        if not benchmark:
            return {"overall": "No benchmark available for comparison"}

        comparisons = {}

        # Learning velocity
        if assessment.learning_velocity >= benchmark.learning_velocity_p90:
            comparisons["velocity"] = "Exceptional (Top 10%)"
        elif assessment.learning_velocity >= benchmark.learning_velocity_p75:
            comparisons["velocity"] = "Strong (Top 25%)"
        elif assessment.learning_velocity >= benchmark.learning_velocity_p50:
            comparisons["velocity"] = "Above average"
        else:
            comparisons["velocity"] = "Below average"

        # Sophistication
        if assessment.avg_sophistication >= benchmark.sophistication_p90:
            comparisons["sophistication"] = "Exceptional (Top 10%)"
        elif assessment.avg_sophistication >= benchmark.sophistication_p75:
            comparisons["sophistication"] = "Strong (Top 25%)"
        elif assessment.avg_sophistication >= benchmark.sophistication_p50:
            comparisons["sophistication"] = "Above average"
        else:
            comparisons["sophistication"] = "Below average"

        # Chain depth
        if assessment.chain_depth >= benchmark.chain_depth_p90:
            comparisons["persistence"] = "Exceptional (Top 10%)"
        elif assessment.chain_depth >= benchmark.chain_depth_p75:
            comparisons["persistence"] = "Strong (Top 25%)"
        elif assessment.chain_depth >= benchmark.chain_depth_p50:
            comparisons["persistence"] = "Above average"
        else:
            comparisons["persistence"] = "Below average"

        # Overall Tao Index
        percentile = self.calculate_percentile(assessment, role)
        if percentile >= 90:
            comparisons["overall"] = f"Exceptional ({int(percentile)}th percentile)"
        elif percentile >= 75:
            comparisons["overall"] = f"Strong ({int(percentile)}th percentile)"
        elif percentile >= 50:
            comparisons["overall"] = f"Above average ({int(percentile)}th percentile)"
        else:
            comparisons["overall"] = f"Below average ({int(percentile)}th percentile)"

        return comparisons

    def update_benchmark(self, role: str, new_assessment: Assessment):
        """
        Update benchmark with new assessment data.

        As we collect more candidate data, benchmarks become more accurate.

        Args:
            role: Role to update
            new_assessment: New assessment to incorporate
        """
        # TODO: Implement rolling benchmark updates
        # - Store all assessment data points
        # - Recalculate percentiles periodically
        # - Track sample size growth
        logger.info(f"Benchmark update for {role} (not yet implemented)")
        pass

    def _db_to_model(self, db_benchmark) -> Benchmark:
        """Convert database benchmark to Pydantic model."""
        return Benchmark(
            benchmark_id=db_benchmark.benchmark_id,
            role=db_benchmark.role,
            company=db_benchmark.company,
            sample_size=db_benchmark.sample_size,
            learning_velocity_p50=db_benchmark.learning_velocity_p50,
            learning_velocity_p75=db_benchmark.learning_velocity_p75,
            learning_velocity_p90=db_benchmark.learning_velocity_p90,
            sophistication_p50=db_benchmark.sophistication_p50,
            sophistication_p75=db_benchmark.sophistication_p75,
            sophistication_p90=db_benchmark.sophistication_p90,
            chain_depth_p50=db_benchmark.chain_depth_p50,
            chain_depth_p75=db_benchmark.chain_depth_p75,
            chain_depth_p90=db_benchmark.chain_depth_p90,
            tao_index_p50=db_benchmark.tao_index_p50,
            tao_index_p75=db_benchmark.tao_index_p75,
            tao_index_p90=db_benchmark.tao_index_p90,
            created_at=db_benchmark.created_at,
            updated_at=db_benchmark.updated_at
        )

    def list_roles(self) -> List[str]:
        """Get list of available roles with benchmarks."""
        roles = set(self._default_benchmarks.keys())

        # Add roles from database
        try:
            from .database import get_db
            from .db_models import BenchmarkDB

            db = get_db()
            try:
                db_benchmarks = db.query(BenchmarkDB).all()
                for db_bench in db_benchmarks:
                    roles.add(db_bench.role)
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Could not load roles from database: {e}")

        return sorted(list(roles))
