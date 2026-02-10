#!/usr/bin/env python3
"""
Test the search_patterns flag - THE SWITCH

This demonstrates Phase 1's core feature:
- search_patterns=True → search for patterns, use if found
- search_patterns=False → skip pattern search, use persona data source
"""

import asyncio
import sys


async def test_with_patterns_flag():
    """Test WITH search_patterns=True"""
    print("\n" + "="*60)
    print("TEST 1: search_patterns=True (SEARCH FOR PATTERNS)")
    print("="*60)

    from core.query_processor import process_query

    response = await process_query(
        query="How to cook rice",
        domain_name="cooking",
        search_patterns=True  # ← THE SWITCH: Search patterns
    )

    print(f"✓ Response received")
    print(f"  Domain: {response['domain']}")
    print(f"  Persona: {response['persona_type']}")
    print(f"  Source: {response['source']}")
    print(f"  Search patterns enabled: {response['search_patterns_enabled']}")
    print(f"  Pattern override used: {response['pattern_override_used']}")

    if response['pattern_override_used']:
        print(f"  ✓ Patterns found and used!")
    else:
        print(f"  ℹ No patterns found, used persona data source")

    assert response['search_patterns_enabled'] is True
    print("\n✅ search_patterns=True test PASSED")


async def test_without_patterns_flag():
    """Test WITH search_patterns=False"""
    print("\n" + "="*60)
    print("TEST 2: search_patterns=False (SKIP PATTERN SEARCH)")
    print("="*60)

    from core.query_processor import process_query

    response = await process_query(
        query="How to cook rice",
        domain_name="cooking",
        search_patterns=False  # ← THE SWITCH: Skip patterns
    )

    print(f"✓ Response received")
    print(f"  Domain: {response['domain']}")
    print(f"  Persona: {response['persona_type']}")
    print(f"  Source: {response['source']}")
    print(f"  Search patterns enabled: {response['search_patterns_enabled']}")
    print(f"  Pattern override used: {response['pattern_override_used']}")

    if response['pattern_override_used']:
        print(f"  ⚠ Patterns were used (shouldn't happen!)")
    else:
        print(f"  ✓ Patterns skipped, used persona data source directly!")

    assert response['search_patterns_enabled'] is False
    assert response['pattern_override_used'] is False
    print("\n✅ search_patterns=False test PASSED")


async def test_context_flag():
    """Test with flag in context dict"""
    print("\n" + "="*60)
    print("TEST 3: search_patterns in context dict")
    print("="*60)

    from core.query_processor import process_query

    # Via context dict
    response = await process_query(
        query="How to cook rice",
        domain_name="cooking",
        context={"search_patterns": False}  # ← THE SWITCH: In context
    )

    print(f"✓ Response received")
    print(f"  Search patterns enabled: {response['search_patterns_enabled']}")
    print(f"  Pattern override used: {response['pattern_override_used']}")

    assert response['search_patterns_enabled'] is False
    assert response['pattern_override_used'] is False
    print("\n✅ Context flag test PASSED")


async def test_default_behavior():
    """Test default (no flag) - uses domain config"""
    print("\n" + "="*60)
    print("TEST 4: No flag (uses domain config default)")
    print("="*60)

    from core.query_processor import process_query

    response = await process_query(
        query="How to cook rice",
        domain_name="cooking"
        # No search_patterns flag → uses domain config
    )

    print(f"✓ Response received")
    print(f"  Search patterns enabled: {response['search_patterns_enabled']}")
    print(f"  (from domain config: enable_pattern_override)")

    print("\n✅ Default behavior test PASSED")


async def main():
    """Run all tests"""
    print("="*60)
    print("Search Patterns Flag Tests")
    print("="*60)
    print("\nThe search_patterns flag controls THE CORE DECISION:")
    print("- True: Search for patterns in domain")
    print("- False: Skip pattern search, use persona data source")
    print("- None/omitted: Use domain config default")

    try:
        await test_with_patterns_flag()
        await test_without_patterns_flag()
        await test_context_flag()
        await test_default_behavior()

        print("\n" + "="*60)
        print("✅ ALL FLAG TESTS PASSED")
        print("="*60)
        print("\nThe search_patterns flag is working correctly!")
        print("You can now control pattern search on/off per query.")
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
