#!/usr/bin/env python3
"""
DEVELOPMENT TEST SCRIPT - Formatter Plugin System

This is a development test script that runs against the internal source code
structure (generic_framework/).

IMPORTANT FOR USERS:
- Production deployment: Use Docker, no import setup needed
- Development: These tests use internal 'generic_framework' path
- This is NOT a pip-installable Python library

Verifies that all three default formatters (Markdown, JSON, Compact)
work correctly with sample data.
"""

import sys
from pathlib import Path

# Add framework to path for local development testing
# Note: Production deployment uses Docker where PYTHONPATH is set correctly
sys.path.insert(0, str(Path(__file__).parent / "generic_framework"))

from plugins.formatters.markdown_formatter import MarkdownFormatter, ConciseMarkdownFormatter
from plugins.formatters.json_formatter import JSONFormatter, CompactJSONFormatter
from plugins.formatters.compact_formatter import CompactFormatter, UltraCompactFormatter, TableFormatter


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
                "0xAA ^ 0xFF = 0x55 (invert all bits)",
                "flag ^ mask (toggle bits specified by mask)"
            ],
            "steps": [
                "Identify bits to toggle",
                "Create mask with 1s at target positions",
                "Apply XOR: result = value ^ mask"
            ],
            "conditions": {
                "when": "Need to toggle individual bits",
                "risk": "Low - well-defined operation"
            },
            "related_patterns": ["binary_002", "binary_003"]
        },
        {
            "pattern_id": "binary_002",
            "id": "binary_002",
            "name": "Bitwise Complement",
            "type": "technique",
            "pattern_type": "technique",
            "description": "Invert all bits using NOT operation",
            "problem": "Need to invert all bits in a value",
            "solution": "Use bitwise NOT (~) operator to flip all bits. Note: In two's complement, this is equivalent to -x - 1.",
            "tags": ["not", "complement", "invert"],
            "confidence": 0.85,
            "examples": [
                "~0x55 = 0xAA (in 8-bit)",
                "~0 = -1 (in two's complement)"
            ],
            "steps": [
                "Apply ~ operator to value",
                "Result is bitwise NOT of original"
            ],
            "conditions": {
                "when": "Need to invert all bits",
                "risk": "Low - but watch for sign extension"
            },
            "related_patterns": ["binary_001"]
        }
    ],
    "specialist_id": "bitwise_master",
    "confidence": 0.95
}


def test_formatter(formatter_class, name):
    """Test a single formatter."""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"{'='*80}\n")

    try:
        formatter = formatter_class()
        result = formatter.format(SAMPLE_RESPONSE)

        print(f"✓ Formatter: {formatter.name}")
        print(f"✓ MIME Type: {result.mime_type}")
        print(f"✓ Metadata: {result.metadata}")
        print(f"\n--- Output ---\n")
        print(result.content)
        print(f"\n--- End Output ---\n")

        # Validate
        assert len(result.content) > 0, "Content is empty!"
        assert result.mime_type, "No MIME type!"
        print(f"✓ Test PASSED\n")
        return True

    except Exception as e:
        print(f"✗ Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_format_support():
    """Test format support detection."""
    print(f"\n{'='*80}")
    print(f"Testing Format Support Detection")
    print(f"{'='*80}\n")

    formatters = [
        (MarkdownFormatter(), "markdown"),
        (JSONFormatter(), "json"),
        (CompactFormatter(), "compact"),
    ]

    for formatter, expected_format in formatters:
        supports = formatter.supports_format(expected_format)
        status = "✓" if supports else "✗"
        print(f"{status} {formatter.name} supports '{expected_format}': {supports}")

    print()


def test_multi_specialist_aggregation():
    """Test formatting of multi-specialist responses."""
    print(f"\n{'='*80}")
    print(f"Testing Multi-Specialist Aggregation Formatting")
    print(f"{'='*80}\n")

    # Sample multi-specialist response
    multi_response = {
        "query": "How do I optimize bit operations?",
        "patterns": [],
        "specialist_id": "multi_2",
        "confidence": 0.90,
        "aggregation_strategy": "merge_all",
        "specialist_count": 2,
        "responses": [
            {
                "specialist_id": "bitwise_master",
                "confidence": 0.95,
                "pattern_count": 3,
                "raw_answer": "See XOR and bit manipulation patterns"
            },
            {
                "specialist_id": "algorithm_explorer",
                "confidence": 0.85,
                "pattern_count": 2,
                "raw_answer": "See Brian Kernighan's algorithm"
            }
        ]
    }

    formatter = MarkdownFormatter()
    result = formatter.format(multi_response)

    print(f"✓ Aggregation Strategy: {multi_response['aggregation_strategy']}")
    print(f"✓ Specialist Count: {multi_response['specialist_count']}")
    print(f"\n--- Output ---\n")
    print(result.content[:500])  # Show first 500 chars
    print(f"\n--- End Output (truncated) ---\n")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print(" EEFrame Formatter Plugin System Tests")
    print("="*80)

    # Test each formatter
    tests = [
        (MarkdownFormatter, "MarkdownFormatter"),
        (ConciseMarkdownFormatter, "ConciseMarkdownFormatter"),
        (JSONFormatter, "JSONFormatter"),
        (CompactJSONFormatter, "CompactJSONFormatter"),
        (CompactFormatter, "CompactFormatter"),
        (UltraCompactFormatter, "UltraCompactFormatter"),
        (TableFormatter, "TableFormatter"),
    ]

    results = []
    for formatter_class, name in tests:
        passed = test_formatter(formatter_class, name)
        results.append((name, passed))

    # Test format support
    test_format_support()

    # Test multi-specialist
    test_multi_specialist_aggregation()

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
    sys.exit(main())
