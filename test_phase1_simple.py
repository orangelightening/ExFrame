#!/usr/bin/env python3
"""
Simple Phase 1 test without pytest.

Verifies basic functionality of Persona + Override system.
"""

import sys
from pathlib import Path

# Add generic_framework to path
sys.path.insert(0, str(Path(__file__).parent / "generic_framework"))

from core.persona import Persona
from core.personas import get_persona, list_personas


def test_persona_creation():
    """Test creating personas"""
    print("Test 1: Creating personas...")

    poet = Persona(name="poet", data_source="void")
    assert poet.name == "poet"
    assert poet.data_source == "void"
    print("✓ Poet created")

    librarian = Persona(name="librarian", data_source="library")
    assert librarian.name == "librarian"
    assert librarian.data_source == "library"
    print("✓ Librarian created")

    researcher = Persona(name="researcher", data_source="internet")
    assert researcher.name == "researcher"
    assert researcher.data_source == "internet"
    print("✓ Researcher created")


def test_get_personas():
    """Test getting configured personas"""
    print("\nTest 2: Getting configured personas...")

    poet = get_persona("poet")
    assert poet.name == "poet"
    print("✓ Got poet")

    librarian = get_persona("librarian")
    assert librarian.name == "librarian"
    print("✓ Got librarian")

    researcher = get_persona("researcher")
    assert researcher.name == "researcher"
    print("✓ Got researcher")


def test_list_personas():
    """Test listing all personas"""
    print("\nTest 3: Listing personas...")

    personas = list_personas()
    assert len(personas) == 3
    assert "poet" in personas
    assert "librarian" in personas
    assert "researcher" in personas
    print(f"✓ Found {len(personas)} personas: {personas}")


async def test_pattern_override():
    """Test the core decision: patterns vs data source"""
    print("\nTest 4: Pattern override decision...")

    poet = get_persona("poet")

    # Test WITH patterns (should use override)
    patterns = [{"name": "Test", "solution": "Solution"}]
    response = await poet.respond("test query", override_patterns=patterns)

    assert response["source"] == "patterns_override"
    assert response["pattern_count"] == 1
    print("✓ With patterns: uses patterns_override")

    # Test WITHOUT patterns (should use data source)
    response = await poet.respond("test query")

    assert response["source"] == "void"
    assert response["pattern_count"] == 0
    print("✓ Without patterns: uses void data source")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Phase 1 Simple Tests")
    print("=" * 60)

    try:
        test_persona_creation()
        test_get_personas()
        test_list_personas()
        await test_pattern_override()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
