#!/usr/bin/env python3
"""
State Machine Test Suite

Tests that queries follow the expected state machine flow as defined in
statemachine-design.md. Produces a report card showing pass/fail for each test.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TestCase:
    """A single test case."""
    name: str
    query: str
    domain: str
    verbose: bool = True
    expected_min_states: int = None
    expected_max_states: int = None
    required_states: List[str] = field(default_factory=list)
    forbidden_states: List[str] = field(default_factory=list)
    expected_flow_pattern: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Result of a single test case."""
    test_name: str
    passed: bool
    actual_state_count: int
    expected_state_count: Optional[int]
    actual_states: List[str]
    violations: List[str] = field(default_factory=list)
    duration_ms: int = 0
    state_machine_log: Dict[str, Any] = None


@dataclass
class TestReport:
    """Overall test report."""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    results: List[TestResult] = field(default_factory=list)

    def print_report(self):
        """Print a human-readable report card."""
        print("\n" + "=" * 80)
        print(f"STATE MACHINE TEST REPORT CARD")
        print(f"Timestamp: {self.timestamp}")
        print("=" * 80)
        print(f"\nTotal Tests: {self.total_tests}")
        print(f"Passed: {self.passed} ✓")
        print(f"Failed: {self.failed} ✗")
        print(f"Score: {(self.passed / self.total_tests * 100):.1f}%")

        print("\n" + "-" * 80)
        print("DETAILED RESULTS:")
        print("-" * 80)

        for result in self.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"\n{status} | {result.test_name}")
            print(f"  States: {result.actual_state_count} (expected: {result.expected_state_count or 'N/A'})")
            print(f"  Duration: {result.duration_ms}ms")

            if result.violations:
                print("  Violations:")
                for violation in result.violations:
                    print(f"    - {violation}")

            print(f"  State flow:")
            for i, state in enumerate(result.actual_states, 1):
                print(f"    {i:2d}. {state}")

        print("\n" + "=" * 80)


class StateMachineTester:
    """Test runner for state machine validation."""

    def __init__(self, api_url: str = "http://localhost:3000"):
        self.api_url = api_url
        self.test_cases = self._define_test_cases()

    def _define_test_cases(self) -> List[TestCase]:
        """Define test cases based on statemachine-design.md."""

        return [
            # Test 1: Simple single-specialist query (exframe)
            # Based on actual implementation: ~15 states including self-transitions
            TestCase(
                name="Simple ExFrame Query",
                query="What is ExFrame?",
                domain="exframe",
                expected_min_states=12,
                expected_max_states=20,  # Allow for self-transitions
                required_states=[
                    "QUERY_RECEIVED",
                    "ROUTING_SELECTION",
                    "SEARCHING",
                    "SINGLE_SPECIALIST_PROCESSING",
                    "CONTEXT_READY",
                    "OUT_OF_SCOPE_CHECK",
                    "ENRICHMENT_PIPELINE",
                    "ENRICHMENT_COMPLETE",
                    "RESPONSE_CONSTRUCTION",
                    "COMPLETE",
                    "RESPONSE_RETURNED"
                ],
                forbidden_states=[
                    "ERROR",
                    "MULTI_SPECIALIST_PROCESSING",
                    "AWAITING_CONFIRMATION"
                ]
            ),

            # Test 2: Query with LLM usage (should hit LLM states)
            TestCase(
                name="Query with LLM Enhancement",
                query="Tell me a creative story about ExFrame",
                domain="llm_consciousness",  # This domain uses LLM
                expected_min_states=12,
                required_states=[
                    "QUERY_RECEIVED",
                    "ROUTING_SELECTION",
                    "ENRICHMENT_PIPELINE",
                    "LLM_PROCESSING"
                ]
            ),

            # Test 3: Direct prompt (// prefix)
            TestCase(
                name="Direct Prompt (// prefix)",
                query="// Ignore patterns and tell me about AI",
                domain="exframe",
                expected_min_states=3,
                expected_max_states=6,
                required_states=[
                    "QUERY_RECEIVED",
                    "DIRECT_PROMPT_CHECK",
                    "DIRECT_LLM"
                ],
                forbidden_states=[
                    "ROUTING_SELECTION",
                    "SEARCHING"
                ]
            ),

            # Test 4: Low confidence query (might trigger confirmation)
            TestCase(
                name="Low Confidence Query",
                query="asdfghjkl",
                domain="exframe",
                # Should still complete, maybe with low confidence
                required_states=[
                    "QUERY_RECEIVED",
                    "RESPONSE_RETURNED"
                ]
            ),
        ]

    async def run_query(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a single query and return the response."""
        import httpx

        payload = {
            "query": test_case.query,
            "domain": test_case.domain,
            "verbose": test_case.verbose
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.api_url}/api/query",
                json=payload
            )
            response.raise_for_status()
            return response.json()

    def validate_test_case(self, test_case: TestCase, result: Dict[str, Any]) -> TestResult:
        """Validate a test case against its expected outcomes."""

        state_machine = result.get("state_machine", {})
        events = state_machine.get("events", [])
        summary = state_machine.get("summary", {})

        # Extract state sequence
        actual_states = [e["to_state"] for e in events]
        actual_count = len(actual_states)

        violations = []
        passed = True

        # Check state count bounds
        if test_case.expected_min_states and actual_count < test_case.expected_min_states:
            violations.append(f"Too few states: {actual_count} < {test_case.expected_min_states}")
            passed = False

        if test_case.expected_max_states and actual_count > test_case.expected_max_states:
            violations.append(f"Too many states: {actual_count} > {test_case.expected_max_states}")
            passed = False

        # Check required states are present
        for required in test_case.required_states:
            if required not in actual_states:
                violations.append(f"Missing required state: {required}")
                passed = False

        # Check forbidden states are NOT present
        for forbidden in test_case.forbidden_states:
            if forbidden in actual_states:
                violations.append(f"Forbidden state present: {forbidden}")
                passed = False

        # Note: Self-transitions (e.g., ROUTING_SELECTION → ROUTING_SELECTION)
        # are VALID - they represent events/milestones within a state.
        # We track them but note them for design review if excessive.
        self_transitions = []
        for i, event in enumerate(events):
            if event["from_state"] == event["to_state"]:
                self_transitions.append(f"{event['from_state']} → {event['to_state']} ({event['trigger']})")

        # Self-transitions are NOT violations - they're valid events.
        # Just note them for reference.
        if self_transitions:
            violations.append(f"Self-transitions (valid events): {len(self_transitions)}")
            for st in self_transitions[:3]:  # Show first 3
                violations.append(f"  - {st}")
            if len(self_transitions) > 3:
                violations.append(f"  - ... and {len(self_transitions) - 3} more")
            # Note: this doesn't fail the test, just informational

        # Check for errors
        if summary.get("has_error"):
            violations.append("Query entered ERROR state")
            passed = False

        # Determine expected count (use min if max not specified)
        expected_count = test_case.expected_max_states or test_case.expected_min_states

        return TestResult(
            test_name=test_case.name,
            passed=passed,
            actual_state_count=actual_count,
            expected_state_count=expected_count,
            actual_states=actual_states,
            violations=violations,
            duration_ms=summary.get("total_duration_ms", 0),
            state_machine_log=state_machine
        )

    async def run_all_tests(self) -> TestReport:
        """Run all test cases and generate a report."""

        print("Running State Machine Test Suite...")
        print(f"API URL: {self.api_url}")
        print(f"Test cases: {len(self.test_cases)}")

        results = []
        passed = 0
        failed = 0

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{len(self.test_cases)}] Running: {test_case.name}...")
            print(f"  Query: '{test_case.query}'")
            print(f"  Domain: {test_case.domain}")

            try:
                result = await self.run_query(test_case)
                test_result = self.validate_test_case(test_case, result)
                results.append(test_result)

                if test_result.passed:
                    passed += 1
                    print(f"  Result: PASS ({test_result.actual_state_count} states)")
                else:
                    failed += 1
                    print(f"  Result: FAIL")
                    for violation in test_result.violations:
                        print(f"    - {violation}")

            except Exception as e:
                failed += 1
                print(f"  Result: ERROR - {e}")
                results.append(TestResult(
                    test_name=test_case.name,
                    passed=False,
                    actual_state_count=0,
                    expected_state_count=None,
                    actual_states=[],
                    violations=[f"Test execution error: {e}"]
                ))

        now = datetime.now(timezone.utc)
        report = TestReport(
            timestamp=now.isoformat().replace('+00:00', 'Z'),
            total_tests=len(self.test_cases),
            passed=passed,
            failed=failed,
            results=results
        )

        # Save report to file
        report_path = Path("/app/logs/test_reports") / f"statemachine_test_{now.strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report_data = {
            "timestamp": report.timestamp,
            "total_tests": report.total_tests,
            "passed": report.passed,
            "failed": report.failed,
            "score": report.passed / report.total_tests if report.total_tests > 0 else 0,
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "actual_state_count": r.actual_state_count,
                    "expected_state_count": r.expected_state_count,
                    "violations": r.violations,
                    "actual_states": r.actual_states,
                    "duration_ms": r.duration_ms
                }
                for r in results
            ]
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\nReport saved to: {report_path}")

        return report


async def main():
    """Main entry point."""

    import argparse

    parser = argparse.ArgumentParser(description="State Machine Test Suite")
    parser.add_argument("--api-url", default="http://localhost:3000", help="API base URL")
    parser.add_argument("--output", choices=["console", "json", "both"], default="both", help="Output format")

    args = parser.parse_args()

    tester = StateMachineTester(api_url=args.api_url)
    report = await tester.run_all_tests()

    if args.output in ["console", "both"]:
        report.print_report()

    # Exit with error code if any tests failed
    sys.exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
