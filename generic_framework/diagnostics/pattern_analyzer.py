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
Pattern Analyzer

Analyzes patterns for health issues including:
- Orphaned patterns (no references from domains)
- Duplicate patterns (similar content)
- Low-confidence patterns (rarely matched)
- Missing or invalid pattern fields
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
import json
from difflib import SequenceMatcher


@dataclass
class PatternIssue:
    """Represents a pattern health issue."""
    pattern_id: str
    issue_type: str  # 'orphaned', 'duplicate', 'low_confidence', 'missing_field', 'invalid_format'
    severity: str  # 'critical', 'warning', 'info'
    description: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pattern_id': self.pattern_id,
            'issue_type': self.issue_type,
            'severity': self.severity,
            'description': self.description,
            'details': self.details,
        }


@dataclass
class PatternHealthReport:
    """Overall pattern health report for a domain or universe."""
    domain_id: str
    total_patterns: int = 0
    healthy_patterns: int = 0
    issues_found: int = 0

    # Issue breakdown
    critical_issues: int = 0
    warning_issues: int = 0
    info_issues: int = 0

    # Specific issue counts
    orphaned_patterns: int = 0
    duplicate_patterns: int = 0
    low_confidence_patterns: int = 0
    missing_field_patterns: int = 0

    # Details
    issues: List[PatternIssue] = field(default_factory=list)

    # List of problematic pattern names (for UI display)
    problematic_patterns: List[str] = field(default_factory=list)

    # Map of pattern name to issue type (for detailed UI display)
    pattern_issues: Dict[str, str] = field(default_factory=dict)

    generated_at: datetime = field(default_factory=datetime.utcnow)

    def health_score(self) -> float:
        """Calculate health score (0-100)."""
        if self.total_patterns == 0:
            return 100.0
        healthy_ratio = self.healthy_patterns / self.total_patterns
        return round(healthy_ratio * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'domain_id': self.domain_id,
            'total_patterns': self.total_patterns,
            'healthy_patterns': self.healthy_patterns,
            'issues_found': self.issues_found,
            'health_score': self.health_score(),
            'critical_issues': self.critical_issues,
            'warning_issues': self.warning_issues,
            'info_issues': self.info_issues,
            'orphaned_patterns': self.orphaned_patterns,
            'duplicate_patterns': self.duplicate_patterns,
            'low_confidence_patterns': self.low_confidence_patterns,
            'missing_field_patterns': self.missing_field_patterns,
            'issues': [issue.to_dict() for issue in self.issues],
            'problematic_patterns': self.problematic_patterns,
            'pattern_issues': self.pattern_issues,
            'generated_at': self.generated_at.isoformat(),
        }


class PatternAnalyzer:
    """
    Analyzes patterns for health and quality issues.

    Detects orphaned, duplicate, low-confidence, and malformed patterns.
    """

    # Required fields for a valid pattern
    # Note: EEFrame patterns have structured fields like 'description', 'problem', 'solution'
    REQUIRED_FIELDS = {'id', 'name', 'pattern_type'}

    # Valid pattern types for EEFrame
    PATTERN_TYPES = {
        # Standard types
        'troubleshooting', 'procedure', 'substitution', 'decision',
        'diagnostic', 'preparation', 'optimization', 'principle',
        'solution', 'failure_mode', 'technique', 'concept',
        # EEFrame-specific types
        'getting_started', 'knowledge', 'how_to', 'concepts', 'features',
        # Binary symmetry domain types
        'symmetry', 'algorithm', 'metric', 'encoding', 'transformation',
        'property', 'relationship', 'duality', 'computation', 'extraction',
        'distribution', 'signed_arithmetic'
    }

    def __init__(self, pattern_storage_path: Path):
        """
        Initialize pattern analyzer.

        Args:
            pattern_storage_path: Base path for pattern storage
        """
        self.pattern_storage_path = pattern_storage_path

    def analyze_domain(self, domain_id: str) -> PatternHealthReport:
        """
        Analyze all patterns in a domain.

        Args:
            domain_id: Domain to analyze

        Returns:
            PatternHealthReport with findings
        """
        domain_path = self.pattern_storage_path / domain_id
        patterns_file = domain_path / "patterns.json"

        report = PatternHealthReport(domain_id=domain_id)

        if not patterns_file.exists():
            report.issues.append(PatternIssue(
                pattern_id='*',
                issue_type='missing_file',
                severity='critical',
                description=f'Patterns file not found: {patterns_file}',
            ))
            return report

        # Load patterns
        with open(patterns_file, 'r') as f:
            data = json.load(f)

        # Handle both list and dict formats
        if isinstance(data, list):
            patterns = data
        elif isinstance(data, dict):
            patterns = data.get('patterns', [])
        else:
            patterns = []

        report.total_patterns = len(patterns)

        # Track pattern IDs and content for duplicate detection
        pattern_ids: Set[str] = set()
        pattern_contents: Dict[str, str] = {}

        for pattern in patterns:
            pid = pattern.get('id')
            if not pid:
                continue

            pattern_ids.add(pid)

            # For EEFrame: combine description + problem + solution for duplicate detection
            description = pattern.get('description', '').strip()
            problem = pattern.get('problem', '').strip()
            solution = pattern.get('solution', '').strip()
            combined_content = f"{description} {problem} {solution}".strip()
            pattern_contents[pid] = combined_content

            # Check for missing required fields
            missing = self.REQUIRED_FIELDS - set(pattern.keys())
            if missing:
                report.missing_field_patterns += 1
                report.warning_issues += 1
                report.issues.append(PatternIssue(
                    pattern_id=pid,
                    issue_type='missing_field',
                    severity='warning',
                    description=f'Missing required fields: {", ".join(missing)}',
                    details={'missing_fields': list(missing)},
                ))

            # Check for invalid pattern type
            pattern_type = pattern.get('pattern_type')
            if pattern_type and pattern_type not in self.PATTERN_TYPES:
                report.warning_issues += 1
                report.issues.append(PatternIssue(
                    pattern_id=pid,
                    issue_type='invalid_pattern_type',
                    severity='warning',
                    description=f'Invalid pattern type: {pattern_type}',
                    details={'pattern_type': pattern_type},
                ))

            # Check for meaningful content in EEFrame fields
            # EEFrame patterns have structured fields: description, problem, solution
            if len(combined_content) < 30:
                report.warning_issues += 1
                report.issues.append(PatternIssue(
                    pattern_id=pid,
                    issue_type='empty_content',
                    severity='warning',
                    description='Pattern has insufficient content in description/problem/solution',
                    details={
                        'description_length': len(description),
                        'problem_length': len(problem),
                        'solution_length': len(solution)
                    },
                ))

        # Check for duplicates
        duplicates = self._find_duplicates(pattern_contents)
        for pid, duplicate_pids in duplicates.items():
            report.duplicate_patterns += len(duplicate_pids)
            report.warning_issues += len(duplicate_pids)
            report.issues.append(PatternIssue(
                pattern_id=pid,
                issue_type='duplicate',
                severity='warning',
                description=f'Pattern has {len(duplicate_pids)} duplicate(s)',
                details={'duplicates': duplicate_pids},
            ))

        # Skip orphaned pattern check - EEFrame stores all patterns in JSON only
        # No individual .md files expected

        # Calculate healthy patterns (avoid negative values) and build problematic pattern list
        report.issues_found = len(report.issues)
        # Count unique patterns with at least one critical or warning issue
        problematic_patterns = set()
        pattern_names = {}  # Map pattern_id to pattern name

        # First, build a map of pattern IDs to names
        for pattern in patterns:
            pid = pattern.get('id')
            if pid:
                pattern_names[pid] = pattern.get('name', pid)

        # Then track problematic patterns and add their names to the report
        for issue in report.issues:
            if issue.severity in ('critical', 'warning'):
                problematic_patterns.add(issue.pattern_id)

        # Add pattern names to the report for UI display
        for pid in problematic_patterns:
            name = pattern_names.get(pid, pid)
            report.problematic_patterns.append(name)

        # Map pattern names to their issue types for detailed UI
        for issue in report.issues:
            if issue.severity in ('critical', 'warning'):
                name = pattern_names.get(issue.pattern_id, issue.pattern_id)
                # Map issue_type to user-friendly label
                issue_labels = {
                    'invalid_pattern_type': 'Invalid Type',
                    'empty_content': 'Low Content',
                    'duplicate': 'Duplicate',
                    'missing_field': 'Missing Fields',
                    'orphaned': 'Orphaned',
                    'invalid_format': 'Invalid Format',
                }
                label = issue_labels.get(issue.issue_type, issue.issue_type.replace('_', ' ').title())
                # Only store the first issue for each pattern
                if name not in report.pattern_issues:
                    report.pattern_issues[name] = label

        report.healthy_patterns = max(0, report.total_patterns - len(problematic_patterns))

        return report

    def _find_duplicates(self, pattern_contents: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Find duplicate patterns based on content similarity.

        Args:
            pattern_contents: Map of pattern ID to content

        Returns:
            Dict mapping pattern IDs to list of duplicate IDs
        """
        duplicates = {}
        checked = set()

        pids = list(pattern_contents.keys())
        for i, pid1 in enumerate(pids):
            if pid1 in checked:
                continue

            content1 = pattern_contents[pid1].lower()
            duplicate_pids = []

            for pid2 in pids[i + 1:]:
                if pid2 in checked:
                    continue

                content2 = pattern_contents[pid2].lower()

                # Calculate similarity
                similarity = SequenceMatcher(None, content1, content2).ratio()

                # Consider duplicate if >90% similar
                if similarity > 0.9:
                    duplicate_pids.append(pid2)
                    checked.add(pid2)

            if duplicate_pids:
                duplicates[pid1] = duplicate_pids
                checked.add(pid1)

        return duplicates

    def analyze_universe(self, domain_ids: List[str]) -> Dict[str, PatternHealthReport]:
        """
        Analyze all domains in a universe.

        Args:
            domain_ids: List of domain IDs to analyze

        Returns:
            Dict mapping domain IDs to health reports
        """
        reports = {}
        for domain_id in domain_ids:
            reports[domain_id] = self.analyze_domain(domain_id)
        return reports

    def get_low_confidence_patterns(
        self,
        domain_id: str,
        threshold: float = 0.3,
        search_metrics: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get patterns that consistently have low match confidence.

        Args:
            domain_id: Domain to analyze
            threshold: Confidence threshold (default: 0.3)
            search_metrics: Optional SearchMetrics instance for usage data

        Returns:
            List of patterns with low confidence scores
        """
        low_confidence = []

        if search_metrics:
            # Use search metrics to find patterns with low avg confidence
            all_stats = search_metrics.get_pattern_usage_stats()

            for pid, stats in all_stats.items():
                if stats['avg_confidence'] < threshold:
                    low_confidence.append({
                        'pattern_id': pid,
                        'avg_confidence': stats['avg_confidence'],
                        'match_count': stats['match_count'],
                    })

        return low_confidence

    def validate_pattern(self, pattern: Dict[str, Any]) -> List[str]:
        """
        Validate a single pattern and return list of issues.

        Args:
            pattern: Pattern dictionary to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []

        # Check required fields
        missing = self.REQUIRED_FIELDS - set(pattern.keys())
        if missing:
            issues.append(f"Missing required fields: {', '.join(missing)}")

        # Validate pattern type
        pattern_type = pattern.get('pattern_type')
        if pattern_type and pattern_type not in self.PATTERN_TYPES:
            issues.append(f"Invalid pattern_type: {pattern_type}")

        # Validate content (EEFrame uses description/problem/solution fields)
        description = pattern.get('description', '').strip()
        problem = pattern.get('problem', '').strip()
        solution = pattern.get('solution', '').strip()
        combined_content = f"{description} {problem} {solution}".strip()
        if len(combined_content) < 30:
            issues.append("Combined content (description + problem + solution) is too short (min 30 chars)")

        # Validate ID format
        pid = pattern.get('id', '')
        if not re.match(r'^[a-z0-9_]+$', pid):
            issues.append(f"Invalid pattern ID format: {pid}")

        return issues
