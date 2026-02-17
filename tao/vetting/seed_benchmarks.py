#!/usr/bin/env python3
"""
Seed benchmark data for BrainUse hiring intelligence.

This script populates the benchmarks table with realistic percentile data
for common tech roles based on simulated candidate data.

Run once to initialize benchmarks:
    python -m tao.vetting.seed_benchmarks
"""

import logging
from uuid import uuid4
from datetime import datetime

from .database import init_database, get_db
from .db_models import BenchmarkDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Benchmark data based on simulated candidate assessments
# Format: (role, sample_size, percentiles_dict)
BENCHMARK_DATA = [
    {
        "role": "Senior Backend Engineer",
        "sample_size": 50,
        # Learning velocity (levels per day)
        "learning_velocity_p50": 0.25,
        "learning_velocity_p75": 0.35,
        "learning_velocity_p90": 0.45,
        # Sophistication (0-4.0 scale)
        "sophistication_p50": 2.2,
        "sophistication_p75": 2.7,
        "sophistication_p90": 3.2,
        # Chain depth (queries per chain)
        "chain_depth_p50": 3.0,
        "chain_depth_p75": 4.2,
        "chain_depth_p90": 5.5,
        # Tao Index (composite 0-10)
        "tao_index_p50": 5.5,
        "tao_index_p75": 7.0,
        "tao_index_p90": 8.5,
    },
    {
        "role": "Senior Frontend Engineer",
        "sample_size": 42,
        "learning_velocity_p50": 0.28,
        "learning_velocity_p75": 0.38,
        "learning_velocity_p90": 0.48,
        "sophistication_p50": 2.3,
        "sophistication_p75": 2.8,
        "sophistication_p90": 3.3,
        "chain_depth_p50": 3.2,
        "chain_depth_p75": 4.5,
        "chain_depth_p90": 5.8,
        "tao_index_p50": 5.8,
        "tao_index_p75": 7.2,
        "tao_index_p90": 8.8,
    },
    {
        "role": "Staff Engineer",
        "sample_size": 38,
        "learning_velocity_p50": 0.30,
        "learning_velocity_p75": 0.42,
        "learning_velocity_p90": 0.55,
        "sophistication_p50": 2.5,
        "sophistication_p75": 3.0,
        "sophistication_p90": 3.5,
        "chain_depth_p50": 3.5,
        "chain_depth_p75": 5.0,
        "chain_depth_p90": 6.5,
        "tao_index_p50": 6.2,
        "tao_index_p75": 7.8,
        "tao_index_p90": 9.2,
    },
    {
        "role": "Engineering Manager",
        "sample_size": 35,
        "learning_velocity_p50": 0.22,
        "learning_velocity_p75": 0.32,
        "learning_velocity_p90": 0.42,
        "sophistication_p50": 2.0,
        "sophistication_p75": 2.5,
        "sophistication_p90": 3.0,
        "chain_depth_p50": 2.8,
        "chain_depth_p75": 4.0,
        "chain_depth_p90": 5.2,
        "tao_index_p50": 5.0,
        "tao_index_p75": 6.5,
        "tao_index_p90": 8.0,
    },
    {
        "role": "Data Engineer",
        "sample_size": 45,
        "learning_velocity_p50": 0.26,
        "learning_velocity_p75": 0.36,
        "learning_velocity_p90": 0.46,
        "sophistication_p50": 2.3,
        "sophistication_p75": 2.9,
        "sophistication_p90": 3.4,
        "chain_depth_p50": 3.3,
        "chain_depth_p75": 4.6,
        "chain_depth_p90": 5.9,
        "tao_index_p50": 5.7,
        "tao_index_p75": 7.3,
        "tao_index_p90": 8.9,
    },
    {
        "role": "DevOps Engineer",
        "sample_size": 40,
        "learning_velocity_p50": 0.24,
        "learning_velocity_p75": 0.34,
        "learning_velocity_p90": 0.44,
        "sophistication_p50": 2.1,
        "sophistication_p75": 2.6,
        "sophistication_p90": 3.1,
        "chain_depth_p50": 3.0,
        "chain_depth_p75": 4.3,
        "chain_depth_p90": 5.6,
        "tao_index_p50": 5.4,
        "tao_index_p75": 6.9,
        "tao_index_p90": 8.4,
    },
    {
        "role": "Machine Learning Engineer",
        "sample_size": 33,
        "learning_velocity_p50": 0.32,
        "learning_velocity_p75": 0.44,
        "learning_velocity_p90": 0.58,
        "sophistication_p50": 2.6,
        "sophistication_p75": 3.2,
        "sophistication_p90": 3.8,
        "chain_depth_p50": 3.8,
        "chain_depth_p75": 5.3,
        "chain_depth_p90": 6.8,
        "tao_index_p50": 6.5,
        "tao_index_p75": 8.2,
        "tao_index_p90": 9.5,
    },
    {
        "role": "Product Manager",
        "sample_size": 30,
        "learning_velocity_p50": 0.20,
        "learning_velocity_p75": 0.30,
        "learning_velocity_p90": 0.40,
        "sophistication_p50": 1.9,
        "sophistication_p75": 2.4,
        "sophistication_p90": 2.9,
        "chain_depth_p50": 2.6,
        "chain_depth_p75": 3.8,
        "chain_depth_p90": 5.0,
        "tao_index_p50": 4.8,
        "tao_index_p75": 6.2,
        "tao_index_p90": 7.8,
    },
]


def seed_benchmarks():
    """Seed benchmark data into database."""

    # Initialize database
    init_database()

    db = get_db()
    try:
        # Check if benchmarks already exist
        existing_count = db.query(BenchmarkDB).count()
        if existing_count > 0:
            logger.info(f"Benchmarks already exist ({existing_count} roles). Skipping seed.")
            logger.info("To re-seed, delete existing benchmarks first:")
            logger.info("  docker compose exec -T postgres psql -U brainuse -d brainuse -c 'DELETE FROM benchmarks;'")
            return

        # Insert benchmark data
        for benchmark_data in BENCHMARK_DATA:
            benchmark = BenchmarkDB(
                benchmark_id=str(uuid4()),
                role=benchmark_data["role"],
                company=None,  # Generic benchmarks (not company-specific)
                sample_size=benchmark_data["sample_size"],
                learning_velocity_p50=benchmark_data["learning_velocity_p50"],
                learning_velocity_p75=benchmark_data["learning_velocity_p75"],
                learning_velocity_p90=benchmark_data["learning_velocity_p90"],
                sophistication_p50=benchmark_data["sophistication_p50"],
                sophistication_p75=benchmark_data["sophistication_p75"],
                sophistication_p90=benchmark_data["sophistication_p90"],
                chain_depth_p50=benchmark_data["chain_depth_p50"],
                chain_depth_p75=benchmark_data["chain_depth_p75"],
                chain_depth_p90=benchmark_data["chain_depth_p90"],
                tao_index_p50=benchmark_data["tao_index_p50"],
                tao_index_p75=benchmark_data["tao_index_p75"],
                tao_index_p90=benchmark_data["tao_index_p90"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(benchmark)
            logger.info(f"  ✓ Added benchmark: {benchmark_data['role']} (n={benchmark_data['sample_size']})")

        db.commit()
        logger.info(f"✓ Seeded {len(BENCHMARK_DATA)} benchmark roles")

    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error seeding benchmarks: {e}")
        raise
    finally:
        db.close()


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("BrainUse Benchmark Seeding")
    logger.info("=" * 60)

    seed_benchmarks()

    logger.info("=" * 60)
    logger.info("Benchmark seeding complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
