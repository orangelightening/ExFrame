#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Diagnostics API Routes

Provides endpoints for search quality analysis, pattern health,
and system diagnostics.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from diagnostics.search_metrics import SearchMetrics, SearchTrace, SearchOutcome
from diagnostics.pattern_analyzer import PatternAnalyzer, PatternHealthReport
from diagnostics.health_checker import HealthChecker, SystemHealthReport

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])

# Global instances (will be initialized at startup)
_search_metrics: Optional[SearchMetrics] = None
_pattern_analyzer: Optional[PatternAnalyzer] = None
_health_checker: Optional[HealthChecker] = None


def get_search_metrics() -> SearchMetrics:
    """Get or create SearchMetrics instance."""
    global _search_metrics
    if _search_metrics is None:
        _search_metrics = SearchMetrics()
    return _search_metrics


def get_pattern_analyzer() -> PatternAnalyzer:
    """Get or create PatternAnalyzer instance."""
    global _pattern_analyzer
    if _pattern_analyzer is None:
        import os
        # Use universe-based path structure
        universe_path = Path(os.getenv('UNIVERSE_PATH', '/app/universes/MINE/domains'))
        _pattern_analyzer = PatternAnalyzer(universe_path)
    return _pattern_analyzer


def get_health_checker() -> HealthChecker:
    """Get or create HealthChecker instance."""
    global _health_checker
    if _health_checker is None:
        import os
        # Use universe-based path structure
        universe_path = Path(os.getenv('UNIVERSE_PATH', '/app/universes/MINE/domains'))
        _health_checker = HealthChecker(universe_path, get_search_metrics())
    return _health_checker


@router.get("/health")
async def get_system_health(
    domain_ids: Optional[str] = Query(None, description="Comma-separated domain IDs to check")
) -> SystemHealthReport:
    """
    Get overall system health status.

    Runs checks on:
    - Pattern storage integrity
    - Knowledge base files
    - Search performance
    - Disk space
    - Pattern health
    """
    checker = get_health_checker()

    domains = domain_ids.split(',') if domain_ids else None

    report = checker.check_all(domain_ids=domains)
    return report


@router.get("/metrics")
async def get_search_metrics(
    hours: int = Query(24, description="Time window in hours"),
    domain_id: Optional[str] = Query(None, description="Filter by domain")
) -> Dict[str, Any]:
    """
    Get search quality metrics.

    Returns aggregate statistics including:
    - Success rate
    - Average confidence
    - Average duration
    - LLM fallback rate
    - Percentile latencies
    """
    metrics = get_search_metrics()

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    quality_metrics = metrics.calculate_metrics(
        start_time=start_time,
        end_time=end_time,
        domain_id=domain_id
    )

    return quality_metrics.to_dict()


@router.get("/traces")
async def get_search_traces(
    limit: int = Query(100, description="Maximum traces to return"),
    domain_id: Optional[str] = Query(None, description="Filter by domain")
) -> List[Dict[str, Any]]:
    """Get recent search traces."""
    metrics = get_search_metrics()

    traces = metrics.get_recent_traces(limit=limit, domain_id=domain_id)

    return [trace.to_dict() for trace in traces]


@router.get("/traces/low-confidence")
async def get_low_confidence_searches(
    threshold: float = Query(0.5, description="Confidence threshold"),
    limit: int = Query(50, description="Maximum results")
) -> List[Dict[str, Any]]:
    """Get searches with low confidence scores."""
    metrics = get_search_metrics()

    traces = metrics.identify_low_confidence_searches(
        threshold=threshold,
        limit=limit
    )

    return [trace.to_dict() for trace in traces]


@router.get("/traces/no-results")
async def get_no_results_searches(
    limit: int = Query(50, description="Maximum results")
) -> List[Dict[str, Any]]:
    """Get searches that returned no results."""
    metrics = get_search_metrics()

    traces = metrics.identify_no_results_searches(limit=limit)

    return [trace.to_dict() for trace in traces]


@router.get("/traces/slow")
async def get_slow_searches(
    threshold_ms: float = Query(5000.0, description="Duration threshold in milliseconds"),
    limit: int = Query(50, description="Maximum results")
) -> List[Dict[str, Any]]:
    """Get searches that were slow."""
    metrics = get_search_metrics()

    traces = metrics.identify_slow_searches(
        threshold_ms=threshold_ms,
        limit=limit
    )

    return [trace.to_dict() for trace in traces]


@router.get("/patterns/health/all")
async def get_all_pattern_health(
    domain_ids: Optional[str] = Query(None, description="Comma-separated domain IDs")
) -> Dict[str, Any]:
    """Get pattern health for all domains."""
    import os
    import logging
    logger = logging.getLogger(__name__)
    analyzer = get_pattern_analyzer()

    logger.info(f"Pattern analyzer path: {analyzer.pattern_storage_path}")

    domains = domain_ids.split(',') if domain_ids else None

    if domains:
        logger.info(f"Using provided domains: {domains}")
        reports = analyzer.analyze_universe(domains)
    else:
        # Get all domains from universe path
        universe_path = Path(os.getenv('UNIVERSE_PATH', '/app/universes/MINE/domains'))
        domains = [d.name for d in universe_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        logger.info(f"Auto-discovered domains: {domains}")
        reports = analyzer.analyze_universe(domains)

    logger.info(f"Generated reports for {len(reports)} domains: {list(reports.keys())}")

    result = {
        domain_id: report.to_dict()
        for domain_id, report in reports.items()
    }
    logger.info(f"Returning result with keys: {list(result.keys())}")
    return result


@router.get("/patterns/health")
async def get_pattern_health(
    domain_id: str = Query(..., description="Domain ID to analyze")
) -> PatternHealthReport:
    """
    Get pattern health report for a domain.

    Identifies:
    - Orphaned patterns
    - Duplicate patterns
    - Missing required fields
    - Empty or invalid content
    """
    analyzer = get_pattern_analyzer()

    report = analyzer.analyze_domain(domain_id)
    return report


@router.get("/patterns/usage")
async def get_pattern_usage(
    pattern_id: Optional[str] = Query(None, description="Specific pattern ID")
) -> Dict[str, Any]:
    """
    Get pattern usage statistics.

    Shows how often patterns are matched and their average confidence.
    """
    metrics = get_search_metrics()

    stats = metrics.get_pattern_usage_stats(pattern_id=pattern_id)

    return stats


@router.post("/traces")
async def record_search_trace(trace: Dict[str, Any]) -> Dict[str, Any]:
    """
    Record a search trace (internal use).

    Called by the assist engine to log search execution.
    """
    metrics = get_search_metrics()

    # Convert dict to SearchTrace
    search_trace = SearchTrace.from_dict(trace)

    metrics.record_search(search_trace)

    return {"status": "recorded", "query_id": trace.get("query_id")}


@router.get("/summary")
async def get_diagnostics_summary() -> Dict[str, Any]:
    """
    Get a comprehensive diagnostics summary.

    Combines health, metrics, and pattern analysis into one view.
    """
    # Get system health
    health = await get_system_health()

    # Get search metrics (last 24 hours)
    metrics_data = await get_search_metrics(hours=24)

    # Get pattern health for all domains
    pattern_health = await get_all_pattern_health()

    return {
        "health": health.to_dict(),
        "search_metrics": metrics_data,
        "pattern_health": pattern_health,
        "generated_at": datetime.utcnow().isoformat(),
    }
