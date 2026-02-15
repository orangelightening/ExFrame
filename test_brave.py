#!/usr/bin/env python3
"""
Test Brave Search API with multiple queries.
Run from container: docker exec eeframe-app python3 /app/test_brave.py
"""

import asyncio
import sys
sys.path.insert(0, '/app')

from integrations.brave_search import brave_search


async def test_multiple():
    """Test multiple queries and track usage."""
    queries = [
        ("What is CRISPR?", "single"),
        ("How does photosynthesis work?", "single"),
        ("Explain machine learning", "single"),
    ]

    total_tokens = 0
    total_cost = 0

    for i, (query, mode) in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(queries)}: {query}")
        print(f"{'='*70}")
        try:
            result = await brave_search(query, mode=mode)
            tokens = result['tokens']['total']
            cost = 0.004 + (tokens * 0.000005)

            total_tokens += tokens
            total_cost += cost

            print(f"✅ Answer preview: {result['answer'][:150]}...")
            print(f"📊 Tokens: {tokens:,}")
            print(f"⏱  Time: {result['time_ms']:.1f}ms")
            print(f"💰 Cost: ${cost:.4f}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"\n{'='*70}")
    print(f"📊 TOTAL USAGE")
    print(f"{'='*70}")
    print(f"Queries: {len(queries)}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Remaining free credit: ${5.00 - total_cost:.2f} ({int((5.00 - total_cost) / (total_cost / len(queries)))} more queries)")
    print(f"{'='*70}")
    print("\n✅ All tests complete! Check your Brave dashboard for detailed stats.")


if __name__ == "__main__":
    asyncio.run(test_multiple())
