#!/usr/bin/env python3
"""
Test script for Wiseman with real LLM integration.

This test makes actual LLM API calls. Make sure your OPENAI_API_KEY
and OPENAI_BASE_URL environment variables are set.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generic_framework.core.wiseman import WiseMan, WiseManConfig
import json


def check_env_vars():
    """Check if required environment variables are set."""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    print("Environment Variables:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"  OPENAI_BASE_URL: {base_url or 'not set'}")
    print(f"  LLM_MODEL: {os.getenv('LLM_MODEL', 'glm-4.7')}")

    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set. Tests will fail.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    print()


def test_librarian_mode():
    """Test librarian mode with library search."""
    print("\n" + "="*60)
    print("TEST: Librarian Mode (library search + thinking)")
    print("="*60)

    config = WiseManConfig(
        use_library=True,
        use_void=False,
        use_internet=False,
        show_thinking=True,
        temperature=0.5
    )

    wiseman = WiseMan(config)
    print(f"Mode: {wiseman._get_mode_summary()}")

    # Mock context with patterns
    context = {
        "patterns": [
            {
                "name": "ExFrame Architecture",
                "solution": "ExFrame uses a universe-based architecture with plugin pipeline: Router → Specialist → Enricher → Formatter"
            },
            {
                "name": "Domain Types",
                "solution": "ExFrame supports 5 domain types: Type 1 (Pattern), Type 2 (API), Type 3 (Document), Type 4 (Web), Type 5 (Creative)"
            }
        ]
    }

    query = "What is ExFrame's architecture?"
    print(f"\nQuery: {query}")

    response = wiseman.respond(query, context)

    print(f"\n--- Response ---")
    print(f"Sources: {response.sources_used}")
    print(f"Answer Length: {len(response.answer)} chars")
    print(f"\n--- Full Response ---\n{response.answer}")

    if response.thinking:
        print(f"\n--- Thinking ---\n{response.thinking}")

    return response


def test_poet_mode():
    """Test poet mode (pure generation)."""
    print("\n" + "="*60)
    print("TEST: Poet Mode (pure generation, no sources)")
    print("="*60)

    config = WiseManConfig(
        use_void=True,
        use_library=False,
        use_internet=False,
        show_thinking=False,
        temperature=0.9
    )

    wiseman = WiseMan(config)
    print(f"Mode: {wiseman._get_mode_summary()}")

    query = "Write a haiku about software architecture"
    print(f"\nQuery: {query}")

    response = wiseman.respond(query)

    print(f"\n--- Response ---")
    print(f"Sources: {response.sources_used}")
    print(f"\n{response.answer}")

    return response


def test_hybrid_mode():
    """Test hybrid mode (library + internet)."""
    print("\n" + "="*60)
    print("TEST: Hybrid Mode (library + internet, thinking)")
    print("="*60)

    config = WiseManConfig(
        use_library=True,
        use_internet=True,
        use_void=False,
        show_thinking=True,
        temperature=0.6
    )

    wiseman = WiseMan(config)
    print(f"Mode: {wiseman._get_mode_summary()}")

    context = {
        "patterns": [
            {"name": "Test Pattern", "solution": "Test solution for hybrid mode"}
        ]
    }

    query = "What are the benefits of semantic search?"
    print(f"\nQuery: {query}")

    response = wiseman.respond(query, context)

    print(f"\n--- Response ---")
    print(f"Sources: {response.sources_used}")
    print(f"Answer Length: {len(response.answer)} chars")
    print(f"\n--- Full Response ---\n{response.answer}")

    return response


def main():
    """Run all tests."""
    print("="*60)
    print("Wiseman Real LLM Test")
    print("="*60)

    # Check environment
    check_env_vars()

    print("\n⚠️  This test makes REAL LLM API calls.")
    response = input("Press Enter to continue or Ctrl+C to cancel...")

    try:
        # Test 1: Librarian mode
        test_librarian_mode()

        # Test 2: Poet mode
        test_poet_mode()

        # Test 3: Hybrid mode
        test_hybrid_mode()

        print("\n" + "="*60)
        print("All tests complete!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
