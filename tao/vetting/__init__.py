"""
Tao Vetting Module

Manages candidate assessment, benchmarking, and report generation for hiring intelligence.
"""

from .models import Candidate, Assessment, Benchmark, Report
from .candidate_manager import CandidateManager
from .benchmark_engine import BenchmarkEngine
from .report_generator import ReportGenerator
from .api_router import router
from .database import init_database, create_tables, close_database

__all__ = [
    "Candidate",
    "Assessment",
    "Benchmark",
    "Report",
    "CandidateManager",
    "BenchmarkEngine",
    "ReportGenerator",
    "router",
    "init_database",
    "create_tables",
    "close_database",
]
