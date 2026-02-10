#!/usr/bin/env python3
"""
Test script for WiseMan prototype.

Run this to verify Wiseman class works with different configurations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generic_framework.core.wiseman import WiseMan, WiseManConfig, WiseManResponse
import json


def load_templates():
    """Load configuration templates."""
    config_path = Path(__file__).parent / "generic_framework/config/wiseman_templates.json"
    with open(config_path) as f:
        data = json.load(f)
    return data["templates"]


def test_mode(mode_name: str, config: WiseManConfig):
    """Test a specific mode."""
    print(f"\n{'='*60}")
    print(f"Testing Mode: {mode_name.upper()}")
    print(f"{'='*60}")

    # Create Wiseman instance
    wiseman = WiseMan(config)

    # Show mode summary
    print(f"\nMode: {wiseman._get_mode_summary()}")

    # Process a test query
    query = "What is the meaning of life?"
    print(f"\nQuery: {query}")

    # Mock context with patterns (for library mode)
    context = {
        "patterns": [
            {"name": "Life Pattern", "solution": "Life is what you make it."},
            {"name": "Purpose Pattern", "solution": "Find your own purpose."},
        ]
    } if config.use_library else None

    response = wiseman.respond(query, context)

    # Show response
    print(f"\n--- Response ---")
    print(f"Answer: {response.answer}")
    print(f"Sources: {response.sources_used}")
    if response.thinking:
        print(f"Thinking: {response.thinking}")

    # Show trace if available
    if response.metadata.get("trace"):
        print(f"\n--- Execution Trace ---")
        for entry in response.metadata["trace"]:
            print(f"  {entry['step']}: {entry['data']}")


def main():
    """Run all tests."""
    print("WiseMan Prototype Test")
    print("="*60)

    # Load templates
    templates = load_templates()

    # Test each mode
    for mode_name, config_dict in templates.items():
        # Skip debug mode for now (too verbose)
        if mode_name == "debug":
            continue

        config = WiseManConfig.from_dict(config_dict)
        test_mode(mode_name, config)

    print(f"\n{'='*60}")
    print("All tests complete!")
    print("="*60)


if __name__ == "__main__":
    main()
