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
Health Checker

Provides system-wide health checks and diagnostics.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from .search_metrics import SearchMetrics, QualityMetrics
from .pattern_analyzer import PatternAnalyzer, PatternHealthReport


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    name: str
    status: str  # 'healthy', 'warning', 'critical', 'unknown'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'status': self.status,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class SystemHealthReport:
    """Overall system health report."""
    overall_status: str  # 'healthy', 'warning', 'critical'
    checks: List[HealthCheckResult] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_status': self.overall_status,
            'checks': [check.to_dict() for check in self.checks],
            'generated_at': self.generated_at.isoformat(),
        }


class HealthChecker:
    """
    System health checker.

    Runs diagnostic checks on:
    - Knowledge base connectivity
    - Pattern storage integrity
    - Search performance
    - LLM availability (if configured)
    - Disk space
    - Memory usage
    """

    def __init__(
        self,
        pattern_storage_path: Path,
        search_metrics: Optional[SearchMetrics] = None,
    ):
        """
        Initialize health checker.

        Args:
            pattern_storage_path: Base path for pattern storage
            search_metrics: Optional SearchMetrics instance
        """
        self.pattern_storage_path = pattern_storage_path
        self.search_metrics = search_metrics or SearchMetrics()
        self.pattern_analyzer = PatternAnalyzer(pattern_storage_path)

    def check_all(self, domain_ids: Optional[List[str]] = None) -> SystemHealthReport:
        """
        Run all health checks.

        Args:
            domain_ids: List of domain IDs to check (default: all)

        Returns:
            SystemHealthReport with all check results
        """
        report = SystemHealthReport(overall_status='healthy')

        # Get domain IDs if not provided
        if domain_ids is None:
            domain_ids = self._get_domain_ids()

        # Run health checks
        report.checks.append(self._check_pattern_storage(domain_ids))
        report.checks.append(self._check_knowledge_base(domain_ids))
        report.checks.append(self._check_search_performance())
        report.checks.append(self._check_disk_space())
        report.checks.append(self._check_pattern_health(domain_ids))

        # Calculate overall status
        critical = any(c.status == 'critical' for c in report.checks)
        warning = any(c.status == 'warning' for c in report.checks)

        if critical:
            report.overall_status = 'critical'
        elif warning:
            report.overall_status = 'warning'

        return report

    def _get_domain_ids(self) -> List[str]:
        """Get list of all domain IDs."""
        if not self.pattern_storage_path.exists():
            return []

        return [
            d.name for d in self.pattern_storage_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]

    def _check_pattern_storage(self, domain_ids: List[str]) -> HealthCheckResult:
        """Check pattern storage integrity."""
        missing_count = 0
        total_count = 0

        for domain_id in domain_ids:
            domain_path = self.pattern_storage_path / domain_id
            patterns_file = domain_path / "patterns.json"

            total_count += 1

            if not patterns_file.exists():
                missing_count += 1
                continue

            # Try to load and parse
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    # Accept both list format and dict with 'patterns' key
                    if isinstance(data, list):
                        # List format is valid
                        pass
                    elif isinstance(data, dict) and 'patterns' in data:
                        # Dict with 'patterns' key is valid
                        pass
                    else:
                        # Invalid format
                        missing_count += 1
            except Exception as e:
                missing_count += 1

        if missing_count == 0:
            return HealthCheckResult(
                name='pattern_storage',
                status='healthy',
                message=f'All {total_count} domains have valid pattern files',
                details={'domains_checked': total_count},
            )
        elif missing_count < total_count:
            return HealthCheckResult(
                name='pattern_storage',
                status='warning',
                message=f'{missing_count} of {total_count} domains have pattern file issues',
                details={
                    'domains_checked': total_count,
                    'domains_with_issues': missing_count,
                },
            )
        else:
            return HealthCheckResult(
                name='pattern_storage',
                status='critical',
                message='No valid pattern files found',
                details={'domains_checked': total_count},
            )

    def _check_knowledge_base(self, domain_ids: List[str]) -> HealthCheckResult:
        """Check knowledge base integrity (JSON or SQLite)."""
        issues = []
        has_kb_count = 0

        for domain_id in domain_ids:
            domain_path = self.pattern_storage_path / domain_id

            # Check for JSON knowledge base (patterns.json)
            json_kb = domain_path / "patterns.json"
            # Check for SQLite knowledge base
            sqlite_kb = domain_path / "knowledge_base.db"

            if json_kb.exists():
                # Validate JSON KB
                try:
                    with open(json_kb, 'r') as f:
                        data = json.load(f)
                        # Accept both list format and dict with 'patterns' key
                        if isinstance(data, list) and len(data) > 0:
                            has_kb_count += 1
                        elif isinstance(data, dict) and 'patterns' in data and len(data['patterns']) > 0:
                            has_kb_count += 1
                        else:
                            issues.append(f'{domain_id}: JSON KB is empty')
                except Exception as e:
                    issues.append(f'{domain_id}: JSON KB error - {str(e)}')
            elif sqlite_kb.exists():
                # Validate SQLite KB
                size_kb = sqlite_kb.stat().st_size / 1024
                if size_kb < 1:
                    issues.append(f'{domain_id}: SQLite KB file too small ({size_kb:.1f} KB)')
                else:
                    has_kb_count += 1
            else:
                issues.append(f'{domain_id}: No knowledge base file found (patterns.json or knowledge_base.db)')

        if not issues:
            return HealthCheckResult(
                name='knowledge_base',
                status='healthy',
                message=f'Knowledge base present for all {len(domain_ids)} domains',
                details={'domains_checked': len(domain_ids)},
            )
        elif has_kb_count > 0:
            return HealthCheckResult(
                name='knowledge_base',
                status='warning',
                message=f'{len(issues)} domains have KB issues, {has_kb_count} OK',
                details={'issues': issues, 'domains_ok': has_kb_count},
            )
        else:
            return HealthCheckResult(
                name='knowledge_base',
                status='critical',
                message='No valid knowledge base files found',
                details={'issues': issues},
            )

    def _check_search_performance(self) -> HealthCheckResult:
        """Check search performance metrics."""
        metrics = self.search_metrics.calculate_metrics()

        if metrics.total_searches == 0:
            return HealthCheckResult(
                name='search_performance',
                status='unknown',
                message='No search metrics available yet',
                details={'message': 'System needs to process queries first'},
            )

        issues = []

        # Check success rate
        success_rate = metrics.success_rate()
        if success_rate < 70:
            issues.append(f'Low success rate: {success_rate:.1f}%')
            status = 'critical'
        elif success_rate < 90:
            issues.append(f'Moderate success rate: {success_rate:.1f}%')
            status = 'warning'
        else:
            status = 'healthy'

        # Check error rate
        error_rate = metrics.error_rate()
        if error_rate > 5:
            issues.append(f'High error rate: {error_rate:.1f}%')
            status = 'critical'

        # Check latency
        if metrics.p95_duration_ms > 10000:
            issues.append(f'High P95 latency: {metrics.p95_duration_ms:.0f}ms')
            if status != 'critical':
                status = 'warning'

        if status == 'healthy':
            message = f'Search performance good (success: {success_rate:.1f}%, P95: {metrics.p95_duration_ms:.0f}ms)'
        else:
            message = f'Search performance issues: {"; ".join(issues)}'

        return HealthCheckResult(
            name='search_performance',
            status=status,
            message=message,
            details={
                'success_rate': success_rate,
                'error_rate': error_rate,
                'no_results_rate': metrics.no_results_rate(),
                'p95_latency_ms': metrics.p95_duration_ms,
            },
        )

    def _check_disk_space(self) -> HealthCheckResult:
        """Check available disk space."""
        import shutil

        try:
            total, used, free = shutil.disk_usage(self.pattern_storage_path)

            free_gb = free / (1024**3)
            used_percent = (used / total) * 100

            if used_percent > 90:
                return HealthCheckResult(
                    name='disk_space',
                    status='critical',
                    message=f'Critically low disk space: {free_gb:.1f}GB free ({used_percent:.1f}% used)',
                    details={
                        'free_gb': round(free_gb, 2),
                        'used_percent': round(used_percent, 2),
                    },
                )
            elif used_percent > 80:
                return HealthCheckResult(
                    name='disk_space',
                    status='warning',
                    message=f'Low disk space: {free_gb:.1f}GB free ({used_percent:.1f}% used)',
                    details={
                        'free_gb': round(free_gb, 2),
                        'used_percent': round(used_percent, 2),
                    },
                )
            else:
                return HealthCheckResult(
                    name='disk_space',
                    status='healthy',
                    message=f'Disk space OK: {free_gb:.1f}GB free ({used_percent:.1f}% used)',
                    details={
                        'free_gb': round(free_gb, 2),
                        'used_percent': round(used_percent, 2),
                    },
                )
        except Exception as e:
            return HealthCheckResult(
                name='disk_space',
                status='unknown',
                message=f'Could not check disk space: {str(e)}',
            )

    def _check_pattern_health(self, domain_ids: List[str]) -> HealthCheckResult:
        """Check overall pattern health."""
        if not domain_ids:
            return HealthCheckResult(
                name='pattern_health',
                status='unknown',
                message='No domains to check',
            )

        reports = self.pattern_analyzer.analyze_universe(domain_ids)

        total_patterns = sum(r.total_patterns for r in reports.values())
        total_issues = sum(r.issues_found for r in reports.values())
        avg_health_score = sum(r.health_score() for r in reports.values()) / len(reports)

        if avg_health_score >= 90:
            status = 'healthy'
        elif avg_health_score >= 70:
            status = 'warning'
        else:
            status = 'critical'

        return HealthCheckResult(
            name='pattern_health',
            status=status,
            message=f'Pattern health: {avg_health_score:.1f}% ({total_issues} issues across {total_patterns} patterns)',
            details={
                'total_patterns': total_patterns,
                'total_issues': total_issues,
                'avg_health_score': round(avg_health_score, 2),
                'domains_checked': len(domain_ids),
            },
        )
