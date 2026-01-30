#!/usr/bin/env python3
"""
Test script for Enrichment Plugin system.

Verifies that enrichment plugins work correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add framework to path for local development testing
# Note: Production deployment uses Docker where PYTHONPATH is set correctly
sys.path.insert(0, str(Path(__file__).parent / "generic_framework"))

from core.enrichment_plugin import EnrichmentContext, ChainedEnricher, ParallelEnricher
from plugins.enrichers.related_pattern_enricher import (
    RelatedPatternEnricher,
    PatternLinkEnricher,
    CategoryOverviewEnricher
)
from plugins.enrichers.example_expander_enricher import (
    ExampleExpanderEnricher,
    ExampleValidatorEnricher,
    ExampleSorterEnricher
)
from plugins.enrichers.code_generator_enricher import (
    CodeGeneratorEnricher,
    CodeSnippetEnricher
)
from plugins.enrichers.usage_stats_enricher import (
    UsageStatsEnricher,
    TrendingEnricher,
    FeedbackEnricher,
    QualityScoreEnricher
)


# Sample response data
SAMPLE_RESPONSE = {
    "query": "What is XOR?",
    "patterns": [
        {
            "pattern_id": "binary_001",
            "id": "binary_001",
            "name": "XOR Operation",
            "type": "technique",
            "pattern_type": "technique",
            "description": "Exclusive OR operation for bit manipulation",
            "problem": "Need to flip specific bits without affecting others",
            "solution": "Use XOR (^) operator to toggle bits. XOR with 1 flips a bit, XOR with 0 leaves it unchanged.",
            "tags": ["xor", "bitwise", "binary"],
            "confidence": 0.95,
            "examples": [
                {"input": "0xAA ^ 0xFF", "output": "0x55", "notes": "Invert all bits"},
                {"input": "flag ^ mask", "output": "toggled", "notes": "Toggle bits specified by mask"}
            ]
        },
        {
            "pattern_id": "binary_002",
            "id": "binary_002",
            "name": "Bitwise Complement",
            "type": "technique",
            "pattern_type": "technique",
            "description": "Invert all bits using NOT operation",
            "problem": "Need to invert all bits in a value",
            "solution": "Use bitwise NOT (~) operator to flip all bits.",
            "tags": ["not", "complement", "invert"],
            "confidence": 0.85,
            "examples": [
                {"input": "~0x55", "output": "0xAA", "notes": "Invert bits"}
            ]
        }
    ],
    "specialist_id": "bitwise_master",
    "confidence": 0.95
}


async def test_enricher(enricher_class, name: str):
    """Test a single enricher."""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"{'='*80}\n")

    try:
        enricher = enricher_class()

        # Create context
        context = EnrichmentContext(
            domain_id="binary_symmetry",
            specialist_id="bitwise_master",
            query=SAMPLE_RESPONSE["query"],
            knowledge_base=None,  # Mock KB
            metadata={}
        )

        # Enrich response
        result = await enricher.enrich(SAMPLE_RESPONSE.copy(), context)

        print(f"✓ Enricher: {enricher.name}")
        print(f"✓ Supports formats: {enricher.get_supported_formats()}")
        print(f"✓ Can run parallel: {enricher.can_run_parallel()}")
        print(f"\n--- Enrichment Results ---\n")

        # Show enriched patterns
        for i, pattern in enumerate(result.get("patterns", []), 1):
            print(f"Pattern {i}: {pattern.get('name')}")
            for key, value in pattern.items():
                if key not in ["name", "id", "pattern_id", "description", "solution"]:
                    if isinstance(value, (list, dict)):
                        value_str = str(value)[:100]
                    else:
                        value_str = str(value)
                    print(f"  + {key}: {value_str}")
            print()

        print("--- End Results ---\n")
        print(f"✓ Test PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_chained_enricher():
    """Test chained enricher."""
    print(f"\n{'='*80}")
    print(f"Testing: ChainedEnricher")
    print(f"{'='*80}\n")

    try:
        # Create chain
        chain = ChainedEnricher()
        chain.add_enricher(UsageStatsEnricher())
        chain.add_enricher(QualityScoreEnricher())

        context = EnrichmentContext(
            domain_id="binary_symmetry",
            specialist_id="bitwise_master",
            query=SAMPLE_RESPONSE["query"],
            knowledge_base=None
        )

        result = await chain.enrich(SAMPLE_RESPONSE.copy(), context)

        print(f"✓ Chained {len(chain.enrichers)} enrichers")

        # Check results
        for pattern in result.get("patterns", []):
            if "usage_stats" in pattern:
                print(f"  + Usage stats added to {pattern.get('name')}")
            if "quality_score" in pattern:
                print(f"  + Quality score added to {pattern.get('name')}")

        print(f"\n✓ Test PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print(" EEFrame Enrichment Plugin System Tests")
    print("="*80)

    # Test each enricher
    tests = [
        (RelatedPatternEnricher, "RelatedPatternEnricher"),
        (ExampleExpanderEnricher, "ExampleExpanderEnricher"),
        (CodeGeneratorEnricher, "CodeGeneratorEnricher"),
        (UsageStatsEnricher, "UsageStatsEnricher"),
        (QualityScoreEnricher, "QualityScoreEnricher"),
        (TrendingEnricher, "TrendingEnricher"),
    ]

    results = []
    for enricher_class, name in tests:
        passed = await test_enricher(enricher_class, name)
        results.append((name, passed))

    # Test chained enricher
    passed = await test_chained_enricher()
    results.append(("ChainedEnricher", passed))

    # Summary
    print("\n" + "="*80)
    print(" Test Summary")
    print("="*80)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
