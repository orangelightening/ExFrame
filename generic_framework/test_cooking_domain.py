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
Test script for the Generic Framework with Cooking Domain.

Tests the core abstractions and cooking domain implementation.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.factory import DomainFactory
from core.domain import DomainConfig
from domains.cooking import CookingDomain
from assist.engine import GenericAssistantEngine


async def test_cooking_domain():
    """Test the cooking domain implementation."""

    print("=" * 60)
    print("Testing Generic Framework - Cooking Domain")
    print("=" * 60)

    # 1. Register domain
    print("\n[1] Registering Cooking Domain...")
    DomainFactory.register_domain(CookingDomain)
    print(f"    Available domains: {DomainFactory.list_domains()}")

    # 2. Create domain instance
    print("\n[2] Creating Cooking Domain instance...")
    config = DomainConfig(
        domain_id="cooking",
        domain_name="Cooking & Recipes",
        version="1.0.0",
        description="Culinary knowledge and recipes",
        pattern_storage_path="/home/peter/development/eeframe/data/patterns/cooking",
        pattern_format="json",
        categories=["technique", "recipe", "cooking_method", "ingredient_substitution"],
        tags=["baking", "chicken", "quick", "healthy"]
    )
    cooking_domain = CookingDomain(config)
    print(f"    Domain ID: {cooking_domain.domain_id}")
    print(f"    Domain Name: {cooking_domain.domain_name}")

    # 3. Initialize domain
    print("\n[3] Initializing domain...")
    await cooking_domain.initialize()
    print(f"    Specialists available: {cooking_domain.list_specialists()}")

    # 4. Health check
    print("\n[4] Health check...")
    health = await cooking_domain.health_check()
    print(f"    Status: {health['status']}")
    print(f"    Patterns loaded: {health['patterns_loaded']}")
    print(f"    Specialists: {health['specialists_available']}")
    print(f"    Categories: {health['categories']}")

    # 5. Create assistant engine
    print("\n[5] Creating Assistant Engine...")
    engine = GenericAssistantEngine(cooking_domain)
    await engine.initialize()
    print(f"    Engine ready")

    # 6. Test queries
    print("\n[6] Testing queries...")

    test_queries = [
        "How do I cook chicken breast?",
        "My cake is too dense, what did I do wrong?",
        "Can I substitute oil for butter?",
        "I need a quick dinner tonight",
        "How long should I bake chicken?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n    Query {i}: {query}")
        print("    " + "-" * 50)
        result = await engine.process_query(query)

        print(f"    Specialist: {result['specialist'] or 'General'}")
        print(f"    Patterns used: {len(result['patterns_used'])}")
        print(f"    Confidence: {result['confidence']:.2f}")

        # Show first part of response
        response_lines = result['response'].split('\n')
        if len(response_lines) > 5:
            preview = '\n    '.join(response_lines[:5])
            print(f"    Response preview:\n    {preview}...")
        else:
            print(f"    Response:\n{result['response']}")

    # 7. Domain status
    print("\n[7] Final domain status...")
    status = await engine.get_domain_status()
    print(f"    Queries processed: {status['queries_processed']}")
    print(f"    Patterns in KB: {status['patterns_loaded']}")

    # 8. Cleanup
    print("\n[8] Cleanup...")
    await cooking_domain.cleanup()
    print("    Done")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_cooking_domain())
