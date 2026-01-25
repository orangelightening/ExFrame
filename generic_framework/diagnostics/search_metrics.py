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
Search Metrics and Quality Analysis

Tracks search performance, quality metrics, and provides diagnostics
for understanding search behavior and identifying issues.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path


class SearchOutcome(Enum):
    """Categorization of search results."""
    SUCCESS_HIGH_CONFIDENCE = "success_high"
    SUCCESS_LOW_CONFIDENCE = "success_low"
    NO_RESULTS = "no_results"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class SearchTrace:
    """
    Detailed trace of a single search/query execution.

    Captures the full execution path for diagnostics and analysis.
    """
    query_id: str
    query: str
    domain_id: str
    timestamp: datetime

    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None

    # Search execution
    specialist_selected: Optional[str] = None
    specialist_scores: List[Dict[str, Any]] = field(default_factory=list)
    patterns_found: int = 0
    patterns_matched: List[Dict[str, Any]] = field(default_factory=list)
    patterns_used: int = 0

    # Results
    outcome: SearchOutcome = SearchOutcome.SUCCESS_HIGH_CONFIDENCE
    confidence: float = 0.0
    llm_used: bool = False
    error_message: Optional[str] = None

    # Steps for detailed analysis
    steps: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'query_id': self.query_id,
            'query': self.query,
            'domain_id': self.domain_id,
            'timestamp': self.timestamp.isoformat(),
            'duration_ms': self.duration_ms,
            'specialist_selected': self.specialist_selected,
            'specialist_scores': self.specialist_scores,
            'patterns_found': self.patterns_found,
            'patterns_matched': self.patterns_matched,
            'patterns_used': self.patterns_used,
            'outcome': self.outcome.value,
            'confidence': self.confidence,
            'llm_used': self.llm_used,
            'error_message': self.error_message,
            'steps': self.steps,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchTrace':
        """Create from dictionary."""
        return cls(
            query_id=data['query_id'],
            query=data['query'],
            domain_id=data['domain_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            start_time=datetime.fromisoformat(data['timestamp']),
            end_time=datetime.fromisoformat(data['timestamp']) + timedelta(milliseconds=data.get('duration_ms', 0)),
            duration_ms=data.get('duration_ms'),
            specialist_selected=data.get('specialist_selected'),
            specialist_scores=data.get('specialist_scores', []),
            patterns_found=data.get('patterns_found', 0),
            patterns_matched=data.get('patterns_matched', []),
            patterns_used=data.get('patterns_used', 0),
            outcome=SearchOutcome(data.get('outcome', SearchOutcome.SUCCESS_HIGH_CONFIDENCE.value)),
            confidence=data.get('confidence', 0.0),
            llm_used=data.get('llm_used', False),
            error_message=data.get('error_message'),
            steps=data.get('steps', []),
        )


@dataclass
class QualityMetrics:
    """Aggregate quality metrics for a time period."""
    total_searches: int = 0
    successful_searches: int = 0
    no_results_searches: int = 0
    error_searches: int = 0

    avg_confidence: float = 0.0
    avg_duration_ms: float = 0.0
    avg_patterns_found: float = 0.0
    avg_patterns_used: float = 0.0

    llm_fallback_rate: float = 0.0  # % of searches that used LLM

    # Percentiles
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0

    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_searches == 0:
            return 0.0
        return (self.successful_searches / self.total_searches) * 100

    def no_results_rate(self) -> float:
        """Calculate no-results rate."""
        if self.total_searches == 0:
            return 0.0
        return (self.no_results_searches / self.total_searches) * 100

    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.total_searches == 0:
            return 0.0
        return (self.error_searches / self.total_searches) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_searches': self.total_searches,
            'successful_searches': self.successful_searches,
            'no_results_searches': self.no_results_searches,
            'error_searches': self.error_searches,
            'success_rate': round(self.success_rate(), 2),
            'no_results_rate': round(self.no_results_rate(), 2),
            'error_rate': round(self.error_rate(), 2),
            'avg_confidence': round(self.avg_confidence, 3),
            'avg_duration_ms': round(self.avg_duration_ms, 2),
            'avg_patterns_found': round(self.avg_patterns_found, 2),
            'avg_patterns_used': round(self.avg_patterns_used, 2),
            'llm_fallback_rate': round(self.llm_fallback_rate, 2),
            'p50_duration_ms': round(self.p50_duration_ms, 2),
            'p95_duration_ms': round(self.p95_duration_ms, 2),
            'p99_duration_ms': round(self.p99_duration_ms, 2),
        }


class SearchMetrics:
    """
    Search metrics collector and analyzer.

    Tracks search execution, calculates quality metrics,
    and identifies search issues.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize search metrics.

        Args:
            storage_path: Path to store trace logs
        """
        self.storage_path = storage_path or Path.cwd() / "logs" / "search_metrics"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.traces: List[SearchTrace] = []
        self._load_traces()

    def _load_traces(self) -> None:
        """Load existing traces from storage."""
        trace_file = self.storage_path / "traces.jsonl"
        if trace_file.exists():
            with open(trace_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            trace = SearchTrace.from_dict(data)
                            self.traces.append(trace)
                        except Exception as e:
                            print(f"Warning: Failed to load trace: {e}")

    def record_search(self, trace: SearchTrace) -> None:
        """
        Record a search trace.

        Args:
            trace: Search trace to record
        """
        self.traces.append(trace)

        # Append to trace file
        trace_file = self.storage_path / "traces.jsonl"
        with open(trace_file, 'a') as f:
            f.write(json.dumps(trace.to_dict()) + '\n')

    def calculate_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        domain_id: Optional[str] = None
    ) -> QualityMetrics:
        """
        Calculate aggregate quality metrics.

        Args:
            start_time: Start of time window (default: 24 hours ago)
            end_time: End of time window (default: now)
            domain_id: Filter by domain

        Returns:
            QualityMetrics object with calculated metrics
        """
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(hours=24)

        # Filter traces
        filtered = [
            t for t in self.traces
            if start_time <= t.timestamp <= end_time
            and (domain_id is None or t.domain_id == domain_id)
        ]

        if not filtered:
            return QualityMetrics()

        # Calculate metrics
        metrics = QualityMetrics(total_searches=len(filtered))

        successful = [t for t in filtered if t.outcome == SearchOutcome.SUCCESS_HIGH_CONFIDENCE]
        no_results = [t for t in filtered if t.outcome == SearchOutcome.NO_RESULTS]
        errors = [t for t in filtered if t.outcome == SearchOutcome.ERROR]

        metrics.successful_searches = len(successful)
        metrics.no_results_searches = len(no_results)
        metrics.error_searches = len(errors)

        if successful:
            metrics.avg_confidence = sum(t.confidence for t in successful) / len(successful)
            metrics.avg_duration_ms = sum(t.duration_ms or 0 for t in successful) / len(successful)
            metrics.avg_patterns_found = sum(t.patterns_found for t in successful) / len(successful)
            metrics.avg_patterns_used = sum(t.patterns_used for t in successful) / len(successful)

        if filtered:
            llm_used_count = sum(1 for t in filtered if t.llm_used)
            metrics.llm_fallback_rate = (llm_used_count / len(filtered)) * 100

            # Calculate percentiles for duration
            durations = sorted([t.duration_ms or 0 for t in filtered if t.duration_ms])
            if durations:
                n = len(durations)
                metrics.p50_duration_ms = durations[int(n * 0.5)]
                metrics.p95_duration_ms = durations[int(n * 0.95)]
                metrics.p99_duration_ms = durations[int(n * 0.99)]

        return metrics

    def identify_low_confidence_searches(
        self,
        threshold: float = 0.5,
        limit: int = 50
    ) -> List[SearchTrace]:
        """
        Identify searches with low confidence scores.

        Args:
            threshold: Confidence threshold (default: 0.5)
            limit: Maximum results to return

        Returns:
            List of low-confidence search traces
        """
        low_conf = [
            t for t in self.traces
            if t.outcome == SearchOutcome.SUCCESS_LOW_CONFIDENCE
            or (t.confidence < threshold and t.outcome != SearchOutcome.ERROR)
        ]
        return sorted(low_conf, key=lambda x: x.confidence)[:limit]

    def identify_no_results_searches(
        self,
        limit: int = 50
    ) -> List[SearchTrace]:
        """
        Identify searches that returned no results.

        Args:
            limit: Maximum results to return

        Returns:
            List of no-results search traces
        """
        no_results = [
            t for t in self.traces
            if t.outcome == SearchOutcome.NO_RESULTS
        ]
        return no_results[:limit]

    def identify_slow_searches(
        self,
        threshold_ms: float = 5000.0,
        limit: int = 50
    ) -> List[SearchTrace]:
        """
        Identify searches that were slow.

        Args:
            threshold_ms: Duration threshold in milliseconds
            limit: Maximum results to return

        Returns:
            List of slow search traces
        """
        slow = [
            t for t in self.traces
            if t.duration_ms and t.duration_ms > threshold_ms
        ]
        return sorted(slow, key=lambda x: x.duration_ms or 0, reverse=True)[:limit]

    def get_pattern_usage_stats(
        self,
        pattern_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get pattern usage statistics.

        Args:
            pattern_id: Specific pattern to analyze, or None for all patterns

        Returns:
            Dictionary with usage statistics
        """
        pattern_counts: Dict[str, int] = {}
        pattern_avg_confidence: Dict[str, List[float]] = {}

        for trace in self.traces:
            for pattern in trace.patterns_matched:
                pid = pattern.get('id')
                if pid:
                    pattern_counts[pid] = pattern_counts.get(pid, 0) + 1
                    if pid not in pattern_avg_confidence:
                        pattern_avg_confidence[pid] = []
                    pattern_avg_confidence[pid].append(pattern.get('relevance', 0))

        # Calculate averages
        pattern_stats = {}
        for pid, count in pattern_counts.items():
            if pattern_id is None or pid == pattern_id:
                pattern_stats[pid] = {
                    'match_count': count,
                    'avg_confidence': sum(pattern_avg_confidence[pid]) / len(pattern_avg_confidence[pid]),
                }

        if pattern_id:
            return pattern_stats.get(pattern_id, {})

        # Sort by match count
        return dict(sorted(pattern_stats.items(), key=lambda x: x[1]['match_count'], reverse=True))

    def get_recent_traces(
        self,
        limit: int = 100,
        domain_id: Optional[str] = None
    ) -> List[SearchTrace]:
        """
        Get recent search traces.

        Args:
            limit: Maximum traces to return
            domain_id: Filter by domain

        Returns:
            List of recent traces
        """
        traces = self.traces
        if domain_id:
            traces = [t for t in traces if t.domain_id == domain_id]

        return sorted(traces, key=lambda x: x.timestamp, reverse=True)[:limit]
