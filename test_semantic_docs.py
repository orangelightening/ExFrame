#!/usr/bin/env python3
"""
Test semantic document search.

This script tests the DocumentVectorStore and semantic search functionality.
"""

import sys
import asyncio
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from generic_framework.core.document_embeddings import DocumentVectorStore


async def test_semantic_search():
    """Test semantic document search."""
    print("=" * 60)
    print("Testing Semantic Document Search (Phase 2)")
    print("=" * 60)

    # Test with exframe domain
    domain_name = "exframe"
    domain_path = Path("universes/MINE/domains/exframe")
    library_path = Path("/app/project")  # ExFrame project docs

    if not domain_path.exists():
        print(f"✗ Domain path not found: {domain_path}")
        return

    print(f"\nDomain: {domain_name}")
    print(f"Storage: {domain_path}")
    print(f"Library: {library_path}")

    # Create document store
    print("\n1. Creating DocumentVectorStore...")
    store = DocumentVectorStore(domain_name, domain_path)

    if not store.is_available:
        print("✗ sentence-transformers not available")
        print("Install with: pip install sentence-transformers")
        return

    print("✓ DocumentVectorStore created")

    # Load existing embeddings
    print("\n2. Loading existing embeddings...")
    loaded = store.load()
    if loaded:
        stats = store.get_stats()
        print(f"✓ Loaded {stats['total_documents']} document embeddings")
        print(f"  Model: {stats['model']}")
        print(f"  Last generated: {stats['last_generated']}")
    else:
        print("  No existing embeddings found")

    # Find documents
    print("\n3. Finding markdown files...")
    import glob
    md_files = glob.glob(str(library_path / "**/*.md"), recursive=True)
    print(f"✓ Found {len(md_files)} markdown files")

    # Show some examples
    if md_files:
        print("\n  Examples:")
        for file_path in md_files[:5]:
            print(f"    - {Path(file_path).name}")
        if len(md_files) > 5:
            print(f"    ... and {len(md_files) - 5} more")

    # Generate embeddings
    if not loaded or not md_files:
        print("\n4. Generating embeddings...")
        print("   (This may take a few seconds on first run)")
        generated = store.generate_embeddings(md_files[:10])  # Limit to 10 for testing
        print(f"✓ Generated {generated} new embeddings")
    else:
        print("\n4. Checking for stale embeddings...")
        stale = store.get_stale_documents(md_files[:10])
        if stale:
            print(f"  Found {len(stale)} stale embeddings")
            generated = store.generate_embeddings(stale)
            print(f"✓ Regenerated {generated} embeddings")
        else:
            print("✓ All embeddings current!")

    # Test search
    print("\n5. Testing semantic search...")
    test_queries = [
        "What is ExFrame?",
        "How do I create a domain?",
        "Plugin system architecture"
    ]

    for query in test_queries:
        print(f"\n  Query: \"{query}\"")
        results = store.search(query, top_k=3, min_similarity=0.2)

        if results:
            print(f"  Found {len(results)} relevant documents:")
            for doc_path, similarity in results:
                doc_name = Path(doc_path).name
                print(f"    - {doc_name}: {similarity:.3f}")
        else:
            print("    No relevant documents found")

    # Show stats
    print("\n6. Final statistics:")
    stats = store.get_stats()
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Model: {stats['model']}")
    print(f"  Embeddings file: {stats['embeddings_file']}")
    print(f"  File size: {Path(stats['embeddings_file']).stat().st_size if Path(stats['embeddings_file']).exists() else 0} bytes")

    print("\n" + "=" * 60)
    print("✓ Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_semantic_search())
