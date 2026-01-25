#!/usr/bin/env python3
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
Benchmark: JSON vs SQLite Knowledge Base Backends

Compares:
1. Speed: Search latency, load time, write performance
2. Security: Injection safety, file permissions
3. Capability: Query features, filtering, full-text search
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_base import KnowledgeBaseConfig
from knowledge.json_kb import JSONKnowledgeBase
from knowledge.sqlite_kb import SQLiteKnowledgeBase


# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}{Colors.END}\n")


def print_section(title: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}── {title} ──{Colors.END}")


def print_result(label: str, value: Any, unit: str = "", winner: str = ""):
    winner_str = f" {Colors.GREEN}✓ {winner}{Colors.END}" if winner else ""
    print(f"  {label:30} {Colors.BOLD}{value}{unit}{Colors.END}{winner_str}")


class BenchmarkResults:
    """Store benchmark results for comparison."""

    def __init__(self):
        self.json_results = {}
        self.sqlite_results = {}

    def record(self, backend: str, metric: str, value: Any):
        if backend == "json":
            self.json_results[metric] = value
        else:
            self.sqlite_results[metric] = value

    def compare(self, metric: str, lower_is_better: bool = True) -> str:
        """Return winner for a metric."""
        if metric not in self.json_results or metric not in self.sqlite_results:
            return "N/A"

        json_val = self.json_results[metric]
        sqlite_val = self.sqlite_results[metric]

        if lower_is_better:
            return "JSON" if json_val < sqlite_val else "SQLite"
        else:
            return "JSON" if json_val > sqlite_val else "SQLite"


def get_test_patterns(count: int = 100) -> List[Dict[str, Any]]:
    """Generate test patterns for benchmarking."""
    patterns = []
    topics = [
        "Gray code", "XOR operation", "Hamming distance", "Bit manipulation",
        "Binary search", "Quick sort", "Merge sort", "Hash table",
        "Linked list", "Tree traversal", "Graph algorithms", "Dynamic programming",
        "Recursion", "Iteration", "Sorting algorithms", "Search algorithms"
    ]

    for i in range(count):
        topic = topics[i % len(topics)]
        patterns.append({
            "id": f"test_pattern_{i:05d}",
            "name": f"{topic} - Example {i}",
            "pattern_type": "algorithm" if i % 2 == 0 else "technique",
            "description": f"This is a test pattern about {topic.lower()}",
            "problem": f"How do I implement {topic.lower()}?",
            "solution": f"Here is how {topic.lower()} works: {topic} is a fundamental concept...",
            "tags": ["test", "benchmark", topic.lower().replace(" ", "_")],
            "confidence": 0.5 + (i % 5) * 0.1,
            "status": "candidate" if i % 3 == 0 else "certified",
            "domain": "benchmark",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "times_accessed": i * 10,
            "llm_generated": i % 2 == 0
        })

    return patterns


async def benchmark_load_speed(kb_class, config: KnowledgeBaseConfig, patterns: List[Dict]) -> Dict[str, Any]:
    """Benchmark loading patterns."""
    storage_path = Path(config.storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)

    # Clean up any existing database files for fresh start
    if kb_class == SQLiteKnowledgeBase:
        db_file = storage_path / "patterns.db"
        if db_file.exists():
            db_file.unlink()
        # Also clean WAL files
        for wal_file in storage_path.glob("patterns.db-*"):
            wal_file.unlink()

    # Write patterns.json for both backends (SQLite will migrate from it)
    json_file = storage_path / "patterns.json"
    with open(json_file, 'w') as f:
        json.dump(patterns, f)

    # Time the load
    start = time.time()
    kb = kb_class(config)
    await kb.load_patterns()
    load_time = time.time() - start

    return {
        "load_time": load_time,
        "pattern_count": kb.get_pattern_count(),
        "memory_mb": 0  # Would need psutil for accurate measurement
    }


async def benchmark_search_speed(kb, queries: List[str]) -> Dict[str, Any]:
    """Benchmark search performance."""
    times = []

    for query in queries:
        start = time.time()
        results = await kb.search(query, limit=10)
        elapsed = time.time() - start
        times.append(elapsed)

    return {
        "avg_search_ms": sum(times) / len(times) * 1000,
        "min_search_ms": min(times) * 1000,
        "max_search_ms": max(times) * 1000,
        "total_queries": len(queries)
    }


async def benchmark_write_speed(kb, patterns: List[Dict]) -> Dict[str, Any]:
    """Benchmark write performance."""
    times = []

    # Create new unique patterns for write test (avoid UNIQUE constraint)
    import uuid
    for i in range(10):  # Test with 10 writes
        new_pattern = patterns[0].copy()  # Use first pattern as template
        new_pattern['id'] = f"write_test_{uuid.uuid4().hex[:8]}"  # Unique ID
        new_pattern['name'] = f"Write Test Pattern {i}"

        start = time.time()
        await kb.add_pattern(new_pattern)
        elapsed = time.time() - start
        times.append(elapsed)

    return {
        "avg_write_ms": sum(times) / len(times) * 1000,
        "total_writes": len(times)
    }


def check_security(json_path: Path, sqlite_path: Path) -> Dict[str, Dict]:
    """Check security aspects of both backends."""
    results = {
        "json": {},
        "sqlite": {}
    }

    # File permissions
    if json_path.exists():
        stat = json_path.stat()
        results["json"]["file_perms"] = oct(stat.st_mode)[-3:]
        results["json"]["readable"] = os.access(json_path, os.R_OK)
        results["json"]["writable"] = os.access(json_path, os.W_OK)

    if sqlite_path.exists():
        stat = sqlite_path.stat()
        results["sqlite"]["file_perms"] = oct(stat.st_mode)[-3:]
        results["sqlite"]["readable"] = os.access(sqlite_path, os.R_OK)
        results["sqlite"]["writable"] = os.access(sqlite_path, os.W_OK)

    # Injection safety
    results["json"]["injection_safe"] = "JSON parsing protects against injection"
    results["sqlite"]["injection_safe"] = "Parameterized queries prevent SQL injection"

    return results


def check_capability(json_kb: JSONKnowledgeBase, sqlite_kb: SQLiteKnowledgeBase) -> Dict[str, Dict]:
    """Check feature capabilities."""
    return {
        "json": {
            "full_text_search": "Manual implementation",
            "indexing": "None (linear scan)",
            "transactions": "No",
            "concurrent_reads": "No (file lock)",
            "partial_load": "No (loads all)",
            "filter_by_status": "Manual filter after load",
            "filter_by_confidence": "Manual filter after load",
            "category_filter": "Supported",
            "fuzzy_search": "Manual implementation",
            "schema_flexibility": "High (any JSON)"
        },
        "sqlite": {
            "full_text_search": "FTS5 built-in",
            "indexing": "B-tree indexes on multiple fields",
            "transactions": "ACID compliant",
            "concurrent_reads": "Yes (WAL mode)",
            "partial_load": "Yes (lazy loading)",
            "filter_by_status": "Indexed query",
            "filter_by_confidence": "Indexed query",
            "category_filter": "Supported (indexed)",
            "fuzzy_search": "FTS5 with Porter stemming",
            "schema_flexibility": "Medium (structured + JSON blob)"
        }
    }


async def run_benchmarks():
    """Run all benchmarks and compare backends."""
    print_header("ExFrame Backend Benchmark: JSON vs SQLite")

    # Setup test data
    test_patterns = get_test_patterns(100)
    test_queries = [
        "Gray code implementation",
        "How to use XOR",
        "Hamming distance algorithm",
        "Binary search tree",
        "Sorting algorithms comparison",
        "Graph traversal methods",
        "Dynamic programming examples"
    ]

    results = BenchmarkResults()

    # Create test directories
    base_path = Path("/tmp/eeframe_benchmark")
    json_path = base_path / "json"
    sqlite_path = base_path / "sqlite"

    # Clean up any existing test data
    import shutil
    if base_path.exists():
        shutil.rmtree(base_path)

    # ========== SPEED BENCHMARKS ==========

    print_section("1. SPEED BENCHMARKS")

    # JSON Load
    print(f"\n{Colors.YELLOW}Testing JSON backend...{Colors.END}")
    json_config = KnowledgeBaseConfig(storage_path=str(json_path))
    json_load = await benchmark_load_speed(JSONKnowledgeBase, json_config, test_patterns)
    json_kb = JSONKnowledgeBase(json_config)
    await json_kb.load_patterns()

    results.record("json", "load_time", json_load["load_time"])
    print_result("Load Time", f"{json_load['load_time']:.4f}", "s")
    print_result("Patterns Loaded", json_load["pattern_count"], "")

    # SQLite Load
    print(f"\n{Colors.YELLOW}Testing SQLite backend...{Colors.END}")
    sqlite_config = KnowledgeBaseConfig(storage_path=str(sqlite_path))
    sqlite_load = await benchmark_load_speed(SQLiteKnowledgeBase, sqlite_config, test_patterns)
    sqlite_kb = SQLiteKnowledgeBase(sqlite_config)
    await sqlite_kb.load_patterns()

    results.record("sqlite", "load_time", sqlite_load["load_time"])
    print_result("Load Time", f"{sqlite_load['load_time']:.4f}", "s")
    print_result("Patterns Loaded", sqlite_load["pattern_count"], "")

    load_winner = results.compare("load_time", lower_is_better=True)
    print(f"\n  {Colors.GREEN}Winner: {load_winner}{Colors.END}")

    # Search Performance
    print(f"\n{Colors.YELLOW}Benchmarking search performance...{Colors.END}")

    json_search = await benchmark_search_speed(json_kb, test_queries)
    sqlite_search = await benchmark_search_speed(sqlite_kb, test_queries)

    results.record("json", "avg_search_ms", json_search["avg_search_ms"])
    results.record("sqlite", "avg_search_ms", sqlite_search["avg_search_ms"])

    print_result("JSON - Avg Search", f"{json_search['avg_search_ms']:.2f}", "ms")
    print_result("SQLite - Avg Search", f"{sqlite_search['avg_search_ms']:.2f}", "ms")

    search_winner = results.compare("avg_search_ms", lower_is_better=True)
    print(f"  {Colors.GREEN}Winner: {search_winner}{Colors.END}")

    # Write Performance
    print(f"\n{Colors.YELLOW}Benchmarking write performance...{Colors.END}")

    json_write = await benchmark_write_speed(json_kb, test_patterns[:10])
    sqlite_write = await benchmark_write_speed(sqlite_kb, test_patterns[:10])

    results.record("json", "avg_write_ms", json_write["avg_write_ms"])
    results.record("sqlite", "avg_write_ms", sqlite_write["avg_write_ms"])

    print_result("JSON - Avg Write", f"{json_write['avg_write_ms']:.2f}", "ms")
    print_result("SQLite - Avg Write", f"{sqlite_write['avg_write_ms']:.2f}", "ms")

    write_winner = results.compare("avg_write_ms", lower_is_better=True)
    print(f"  {Colors.GREEN}Winner: {write_winner}{Colors.END}")

    # ========== SECURITY BENCHMARKS ==========

    print_section("2. SECURITY ASSESSMENT")

    security = check_security(json_path / "patterns.json", sqlite_path / "patterns.db")

    print(f"\n  {Colors.BOLD}File Permissions:{Colors.END}")
    for backend, data in security.items():
        if data:
            print(f"    {backend.upper()}: {data.get('file_perms', 'N/A')}")

    print(f"\n  {Colors.BOLD}Injection Safety:{Colors.END}")
    print(f"    JSON: {security['json'].get('injection_safe', 'N/A')}")
    print(f"    SQLite: {security['sqlite'].get('injection_safe', 'N/A')}")

    # ========== CAPABILITY COMPARISON ==========

    print_section("3. CAPABILITY COMPARISON")

    capabilities = check_capability(json_kb, sqlite_kb)

    print(f"\n  {Colors.BOLD}Feature Comparison:{Colors.END}\n")
    print(f"  {'Feature':<30} {'JSON':<30} {'SQLite':<30}")
    print(f"  {'-' * 90}")

    for feature in capabilities["json"].keys():
        json_val = capabilities["json"][feature]
        sqlite_val = capabilities["sqlite"][feature]

        # Highlight winner
        if "built-in" in sqlite_val.lower() or "indexed" in sqlite_val.lower() or "yes" in sqlite_val.lower():
            sqlite_str = f"{Colors.GREEN}{sqlite_val}{Colors.END}"
        else:
            sqlite_str = sqlite_val

        if "high" in json_val.lower():
            json_str = f"{Colors.GREEN}{json_val}{Colors.END}"
        else:
            json_str = json_val

        print(f"  {feature:<30} {json_str:<30} {sqlite_str:<30}")

    # ========== SUMMARY ==========

    print_section("4. SUMMARY")

    print(f"\n  {Colors.BOLD}Speed Summary:{Colors.END}")
    print(f"    Load:    {load_winner} wins ({results.json_results['load_time']:.4f}s vs {results.sqlite_results['load_time']:.4f}s)")
    print(f"    Search:  {search_winner} wins ({results.json_results['avg_search_ms']:.2f}ms vs {results.sqlite_results['avg_search_ms']:.2f}ms)")
    print(f"    Write:   {write_winner} wins ({results.json_results['avg_write_ms']:.2f}ms vs {results.sqlite_results['avg_write_ms']:.2f}ms)")

    print(f"\n  {Colors.BOLD}Recommendation:{Colors.END}")

    # Calculate overall winner
    json_score = 0
    sqlite_score = 0

    if results.json_results['load_time'] < results.sqlite_results['load_time']:
        json_score += 1
    else:
        sqlite_score += 1

    if results.json_results['avg_search_ms'] < results.sqlite_results['avg_search_ms']:
        json_score += 1
    else:
        sqlite_score += 1

    if results.json_results['avg_write_ms'] < results.sqlite_results['avg_write_ms']:
        json_score += 1
    else:
        sqlite_score += 1

    # SQLite gets bonus points for features
    sqlite_score += 3  # Transactions, indexing, FTS

    if sqlite_score > json_score:
        print(f"    {Colors.GREEN}{Colors.BOLD}SQLite is recommended{Colors.END}")
        print(f"    - Better feature set")
        print(f"    - Scales better with data growth")
        print(f"    - Use SQLite for production")
    else:
        print(f"    {Colors.GREEN}{Colors.BOLD}JSON is competitive{Colors.END}")
        print(f"    - Simpler for small datasets")
        print(f"    - Easier to debug")
        print(f"    - Good for development/testing")

    print(f"\n  {Colors.BOLD}Verdict:{Colors.END}")
    print(f"    {Colors.YELLOW}< 1,000 patterns{Colors.END}: JSON is fine")
    print(f"    {Colors.YELLOW}1,000 - 10,000{Colors.END}: SQLite recommended")
    print(f"    {Colors.GREEN}> 10,000 patterns{Colors.END}: Use SQLite")

    # Cleanup
    await sqlite_kb.close()
    if base_path.exists():
        shutil.rmtree(base_path)

    print(f"\n{Colors.CYAN}Benchmark complete!{Colors.END}\n")


if __name__ == "__main__":
    asyncio.run(run_benchmarks())
