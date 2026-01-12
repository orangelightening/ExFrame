"""
Self-Test Runner

Automated testing for ExFrame search quality and system health.
Runs test queries, validates expected results, and detects regressions.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import asyncio

from .search_metrics import SearchMetrics, SearchTrace, SearchOutcome


@dataclass
class TestCase:
    """
    A single test case for query validation.

    Defines expected behavior for a given query.
    """
    name: str
    query: str
    domain_id: str

    # Expected results
    min_confidence: float = 0.5
    min_patterns_found: int = 1
    max_duration_ms: float = 5000.0
    should_succeed: bool = True

    # Expected patterns (optional)
    expected_pattern_ids: List[str] = field(default_factory=list)

    # Expected specialist (optional)
    expected_specialist: Optional[str] = None


@dataclass
class TestResult:
    """Result of running a single test case."""
    test_name: str
    passed: bool
    query: str
    domain_id: str

    # Actual results
    confidence: Optional[float] = None
    patterns_found: int = 0
    duration_ms: Optional[float] = None
    specialist: Optional[str] = None
    matched_pattern_ids: List[str] = field(default_factory=list)

    # Outcome
    failure_reason: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_name': self.test_name,
            'passed': self.passed,
            'query': self.query,
            'domain_id': self.domain_id,
            'confidence': self.confidence,
            'patterns_found': self.patterns_found,
            'duration_ms': self.duration_ms,
            'specialist': self.specialist,
            'matched_pattern_ids': self.matched_pattern_ids,
            'failure_reason': self.failure_reason,
            'warnings': self.warnings,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class TestSuiteResult:
    """Result of running a complete test suite."""
    suite_name: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0

    # Duration
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Results
    results: List[TestResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'suite_name': self.suite_name,
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'skipped_tests': self.skipped_tests,
            'success_rate': round(self.success_rate, 2),
            'duration_seconds': self.duration_seconds,
            'results': [r.to_dict() for r in self.results],
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
        }


class SelfTestRunner:
    """
    Self-test runner for ExFrame.

    Runs automated tests to validate:
    - Search quality (confidence, pattern matching)
    - Performance (latency)
    - Specialist selection
    - Regression detection
    """

    def __init__(
        self,
        api_base_url: str = "http://localhost:3000",
        search_metrics: Optional[SearchMetrics] = None
    ):
        """
        Initialize self-test runner.

        Args:
            api_base_url: Base URL for ExFrame API
            search_metrics: Optional SearchMetrics instance for recording test traces
        """
        self.api_base_url = api_base_url
        self.search_metrics = search_metrics

    async def run_test(self, test: TestCase) -> TestResult:
        """
        Run a single test case.

        Args:
            test: TestCase to run

        Returns:
            TestResult with outcome
        """
        import aiohttp

        # Prepare request
        payload = {
            "query": test.query,
            "domain": test.domain_id,
            "include_trace": True
        }

        start = datetime.utcnow()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/query",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as response:
                    end = datetime.utcnow()
                    data = await response.json()

                    # Extract metrics
                    duration_ms = (end - start).total_seconds() * 1000
                    confidence = data.get('confidence', 0.0)
                    specialist = data.get('specialist')
                    matched_patterns = data.get('matched_patterns', [])
                    pattern_ids = [p.get('id') for p in matched_patterns if p.get('id')]

                    # Build result
                    result = TestResult(
                        test_name=test.name,
                        passed=True,
                        query=test.query,
                        domain_id=test.domain_id,
                        confidence=confidence,
                        patterns_found=len(pattern_ids),
                        duration_ms=duration_ms,
                        specialist=specialist,
                        matched_pattern_ids=pattern_ids
                    )

                    # Validate expectations
                    failures = []
                    warnings = []

                    # Check if query succeeded
                    if test.should_succeed:
                        if not matched_patterns and not data.get('explanation'):
                            failures.append("No results returned")
                    else:
                        if matched_patterns or data.get('explanation'):
                            failures.append("Expected failure but got results")

                    # Check confidence threshold
                    if test.min_confidence > 0:
                        if confidence < test.min_confidence:
                            failures.append(f"Confidence {confidence:.2f} below threshold {test.min_confidence}")

                    # Check patterns found
                    if test.min_patterns_found > 0:
                        if len(pattern_ids) < test.min_patterns_found:
                            failures.append(f"Only {len(pattern_ids)} patterns found, expected at least {test.min_patterns_found}")

                    # Check performance
                    if duration_ms > test.max_duration_ms:
                        warnings.append(f"Slow response: {duration_ms:.0f}ms > {test.max_duration_ms}ms threshold")

                    # Check expected pattern IDs
                    if test.expected_pattern_ids:
                        missing = set(test.expected_pattern_ids) - set(pattern_ids)
                        if missing:
                            failures.append(f"Missing expected patterns: {missing}")

                    # Check expected specialist
                    if test.expected_specialist:
                        if specialist != test.expected_specialist:
                            warnings.append(f"Expected specialist '{test.expected_specialist}', got '{specialist}'")

                    # Set outcome
                    if failures:
                        result.passed = False
                        result.failure_reason = "; ".join(failures)

                    result.warnings = warnings

                    # Record trace in metrics if available
                    if self.search_metrics:
                        trace = SearchTrace(
                            query_id=f"test_{test.name}_{datetime.utcnow().timestamp()}",
                            query=test.query,
                            domain_id=test.domain_id,
                            timestamp=start,
                            start_time=start,
                            end_time=end,
                            duration_ms=duration_ms,
                            specialist_selected=specialist,
                            patterns_matched=[{'id': pid, 'relevance': confidence} for pid in pattern_ids],
                            patterns_used=len(pattern_ids),
                            outcome=SearchOutcome.SUCCESS_HIGH_CONFIDENCE if result.passed else SearchOutcome.SUCCESS_LOW_CONFIDENCE,
                            confidence=confidence,
                        )
                        self.search_metrics.record_search(trace)

                    return result

        except Exception as e:
            end = datetime.utcnow()
            duration_ms = (end - start).total_seconds() * 1000

            return TestResult(
                test_name=test.name,
                passed=False,
                query=test.query,
                domain_id=test.domain_id,
                duration_ms=duration_ms,
                failure_reason=f"Exception: {str(e)}"
            )

    async def run_test_suite(
        self,
        tests: List[TestCase],
        suite_name: str = "default"
    ) -> TestSuiteResult:
        """
        Run a complete test suite.

        Args:
            tests: List of TestCases to run
            suite_name: Name for the test suite

        Returns:
            TestSuiteResult with all outcomes
        """
        result = TestSuiteResult(suite_name=suite_name)
        result.total_tests = len(tests)

        print(f"\n{'='*60}")
        print(f"Running Test Suite: {suite_name}")
        print(f"{'='*60}")
        print(f"Tests: {len(tests)}")
        print(f"Started: {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        for i, test in enumerate(tests, 1):
            print(f"[{i}/{len(tests)}] {test.name}... ", end='', flush=True)

            test_result = await self.run_test(test)
            result.results.append(test_result)

            if test_result.passed:
                result.passed_tests += 1
                print(f"✅ PASS")
                if test_result.warnings:
                    for warning in test_result.warnings:
                        print(f"   ⚠️  {warning}")
            else:
                result.failed_tests += 1
                print(f"❌ FAIL")
                print(f"   Reason: {test_result.failure_reason}")

        result.end_time = datetime.utcnow()
        result.duration_seconds = (result.end_time - result.start_time).total_seconds()

        print()
        print(f"{'='*60}")
        print(f"Test Suite Complete: {suite_name}")
        print(f"{'='*60}")
        print(f"Passed: {result.passed_tests}/{result.total_tests} ({result.success_rate:.1f}%)")
        print(f"Failed: {result.failed_tests}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Ended: {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        return result

    def detect_regressions(
        self,
        current_result: TestSuiteResult,
        baseline_results: List[TestSuiteResult]
    ) -> List[Dict[str, Any]]:
        """
        Detect regressions by comparing current results with historical baselines.

        Args:
            current_result: Current test suite result
            baseline_results: List of historical results to compare against

        Returns:
            List of regression detections
        """
        regressions = []

        # Find baseline for same suite
        baseline = next(
            (r for r in baseline_results if r.suite_name == current_result.suite_name),
            None
        )

        if not baseline:
            return [{
                'type': 'no_baseline',
                'message': 'No baseline found for comparison',
                'severity': 'info'
            }]

        # Compare success rates
        if current_result.success_rate < baseline.success_rate:
            drop = baseline.success_rate - current_result.success_rate
            regressions.append({
                'type': 'success_rate_drop',
                'message': f"Success rate dropped by {drop:.1f}% (from {baseline.success_rate:.1f}% to {current_result.success_rate:.1f}%)",
                'severity': 'critical' if drop > 10 else 'warning',
                'baseline': baseline.success_rate,
                'current': current_result.success_rate
            })

        # Compare per-test results
        baseline_map = {r.test_name: r for r in baseline.results}
        for current_test in current_result.results:
            baseline_test = baseline_map.get(current_test.test_name)

            if baseline_test:
                # Test that passed before but now fails
                if baseline_test.passed and not current_test.passed:
                    regressions.append({
                        'type': 'test_failure',
                        'test_name': current_test.test_name,
                        'message': f"Test '{current_test.test_name}' now failing",
                        'severity': 'critical',
                        'baseline_result': baseline_test.to_dict(),
                        'current_result': current_test.to_dict()
                    })

                # Performance regression
                if (baseline_test.duration_ms and current_test.duration_ms and
                    current_test.duration_ms > baseline_test.duration_ms * 1.5):
                    regressions.append({
                        'type': 'performance_regression',
                        'test_name': current_test.test_name,
                        'message': f"Test '{current_test.test_name}' is {((current_test.duration_ms / baseline_test.duration_ms) - 1) * 100:.0f}% slower",
                        'severity': 'warning',
                        'baseline_duration_ms': baseline_test.duration_ms,
                        'current_duration_ms': current_test.duration_ms
                    })

                # Confidence drop
                if (baseline_test.confidence is not None and
                    current_test.confidence is not None and
                    current_test.confidence < baseline_test.confidence * 0.8):
                    regressions.append({
                        'type': 'confidence_drop',
                        'test_name': current_test.test_name,
                        'message': f"Confidence dropped from {baseline_test.confidence:.2f} to {current_test.confidence:.2f}",
                        'severity': 'warning',
                        'baseline_confidence': baseline_test.confidence,
                        'current_confidence': current_test.confidence
                    })

        return regressions

    def get_default_tests(self) -> List[TestCase]:
        """
        Get default test suite for common domains.

        Returns:
            List of default TestCases
        """
        return [
            # Binary Symmetry tests
            TestCase(
                name="binary_reverse_bits",
                query="How do I reverse the bits in a byte?",
                domain_id="binary_symmetry",
                min_confidence=0.6,
                min_patterns_found=1
            ),
            TestCase(
                name="binary_power_of_two",
                query="How can I detect if a number is a power of two?",
                domain_id="binary_symmetry",
                min_confidence=0.6,
                min_patterns_found=1
            ),

            # Cooking tests
            TestCase(
                name="cooking_chicken_temp",
                query="What's the internal temperature for cooked chicken?",
                domain_id="cooking",
                min_confidence=0.6,
                min_patterns_found=1
            ),
            TestCase(
                name="cooking_substitute",
                query="Can I substitute oil for butter in baking?",
                domain_id="cooking",
                min_confidence=0.5,
                min_patterns_found=1
            ),

            # LLM Consciousness tests
            TestCase(
                name="llm_hallucination",
                query="How do I detect when an LLM is hallucinating?",
                domain_id="llm_consciousness",
                min_confidence=0.5,
                min_patterns_found=1
            ),
            TestCase(
                name="llm_failure_modes",
                query="What are the common failure modes in autonomous agents?",
                domain_id="llm_consciousness",
                min_confidence=0.5,
                min_patterns_found=1
            ),

            # Python tests
            TestCase(
                name="python_list_comprehension",
                query="How do I create a list comprehension in Python?",
                domain_id="python",
                min_confidence=0.5,
                min_patterns_found=1
            ),
        ]

    async def run_self_tests(
        self,
        tests: Optional[List[TestCase]] = None,
        suite_name: str = "self_test"
    ) -> TestSuiteResult:
        """
        Run self-tests with optional regression detection.

        Args:
            tests: Optional list of tests (uses default if not provided)
            suite_name: Name for the test suite

        Returns:
            TestSuiteResult with all outcomes
        """
        if tests is None:
            tests = self.get_default_tests()

        # Run tests
        result = await self.run_test_suite(tests, suite_name)

        # Check for regressions against baseline
        if self.search_metrics:
            # Load historical baselines from file
            baseline_path = self.search_metrics.storage_path / "test_baselines.jsonl"
            baselines = []

            if baseline_path.exists():
                with open(baseline_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                # Reconstruct TestSuiteResult
                                baseline_result = TestSuiteResult(
                                    suite_name=data['suite_name'],
                                    total_tests=data['total_tests'],
                                    passed_tests=data['passed_tests'],
                                    failed_tests=data['failed_tests'],
                                    skipped_tests=data.get('skipped_tests', 0),
                                    results=[TestResult(**r) for r in data.get('results', [])],
                                    start_time=datetime.fromisoformat(data['start_time']),
                                    end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
                                )
                                baselines.append(baseline_result)
                            except Exception:
                                continue

            # Detect regressions
            if baselines:
                regressions = self.detect_regressions(result, baselines)

                if regressions:
                    print()
                    print("⚠️  REGRESSIONS DETECTED:")
                    for reg in regressions:
                        icon = "🔴" if reg['severity'] == 'critical' else "🟡"
                        print(f"   {icon} {reg['message']}")

        # Save this run as new baseline
        baseline_path = self.search_metrics.storage_path / "test_baselines.jsonl"
        with open(baseline_path, 'a') as f:
            f.write(json.dumps(result.to_dict()) + '\n')

        return result
