#!/usr/bin/env python3
"""
Test Phase 1 inside Docker container with real LLM.
"""

import asyncio
import sys


async def test_poet_void():
    """Test poet with void data source (pure generation)"""
    print("\n" + "="*60)
    print("TEST 1: Poet (void - pure generation)")
    print("="*60)

    from core.personas import get_persona

    poet = get_persona("poet")
    print(f"✓ Got poet: data_source={poet.data_source}")

    # Test with pure generation (no patterns)
    response = await poet.respond("Write a short haiku about coding")

    print(f"✓ Response received")
    print(f"  Source: {response['source']}")
    print(f"  Persona: {response['persona']}")
    print(f"  Answer length: {len(response['answer'])} chars")
    print(f"\nAnswer:\n{response['answer']}\n")

    assert response['source'] == 'void'
    assert response['persona'] == 'poet'
    print("✅ Poet test PASSED")


async def test_pattern_override():
    """Test pattern override with poet"""
    print("\n" + "="*60)
    print("TEST 2: Pattern Override")
    print("="*60)

    from core.personas import get_persona

    poet = get_persona("poet")

    # Test with patterns (should override void)
    patterns = [
        {
            "name": "Haiku Structure",
            "solution": "A haiku has 3 lines: 5 syllables, 7 syllables, 5 syllables. It should capture a moment in nature or emotion."
        }
    ]

    response = await poet.respond(
        "Write a haiku about coding",
        override_patterns=patterns
    )

    print(f"✓ Response received")
    print(f"  Source: {response['source']}")
    print(f"  Pattern count: {response['pattern_count']}")
    print(f"  Answer length: {len(response['answer'])} chars")
    print(f"\nAnswer:\n{response['answer']}\n")

    assert response['source'] == 'patterns_override'
    assert response['pattern_count'] == 1
    print("✅ Pattern override test PASSED")


async def test_query_processor():
    """Test full query processor with domain"""
    print("\n" + "="*60)
    print("TEST 3: Query Processor")
    print("="*60)

    from core.query_processor import process_query

    # Test with a domain that has patterns
    response = await process_query(
        "How to cook rice",
        "cooking"
    )

    print(f"✓ Response received")
    print(f"  Domain: {response['domain']}")
    print(f"  Persona: {response['persona_type']}")
    print(f"  Source: {response['source']}")
    print(f"  Pattern override used: {response['pattern_override_used']}")
    print(f"  Answer length: {len(response['answer'])} chars")
    print(f"\nAnswer preview:\n{response['answer'][:200]}...\n")

    assert response['domain'] == 'cooking'
    assert response['persona_type'] == 'researcher'
    print("✅ Query processor test PASSED")


async def main():
    """Run all tests"""
    print("="*60)
    print("Phase 1 Integration Tests (Docker Container)")
    print("="*60)

    try:
        await test_poet_void()
        await test_pattern_override()
        await test_query_processor()

        print("\n" + "="*60)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("="*60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
