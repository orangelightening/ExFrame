#!/usr/bin/env python3
"""
Regenerate document embeddings for exframe domain.
Run this whenever .md files are added/removed/modified in project root.
"""

import sys
sys.path.insert(0, '/app')

from pathlib import Path
from generic_framework.core.document_embeddings import DocumentVectorStore

# Domain configuration
domain_name = "exframe"
domain_path = Path("/app/universes/MINE/domains/exframe")
library_path = Path("/app/project")

# Find all .md files in project root
md_files = list(library_path.glob("*.md"))

print(f"Found {len(md_files)} markdown files in {library_path}")
print("Files:")
for f in sorted(md_files):
    print(f"  - {f.name}")

# Create document store
doc_store = DocumentVectorStore(domain_name, domain_path)

# Load existing embeddings (if any)
doc_store.load()

# Generate embeddings for all files (force=True to regenerate all)
print("\nGenerating embeddings...")
generated = doc_store.generate_embeddings([str(f) for f in md_files], force=True)

print(f"\n✅ Generated {generated} embeddings")
print(f"✅ Saved to {doc_store.embeddings_file}")

# Show stats
print(f"\n✅ Document index updated at {doc_store.embeddings_file}")
print(f"   Size: {doc_store.embeddings_file.stat().st_size / 1024:.1f} KB")
print(f"   Location: {doc_store.embeddings_file}")
