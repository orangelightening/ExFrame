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
Document Research Strategy

Searches through local documents using vector embeddings.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .base import ResearchStrategy, SearchResult


class DocumentResearchStrategy(ResearchStrategy):
    """
    Research strategy that searches through local documents.

    Two modes of operation:
    1. Full Context Mode (use_chunking: false): Load entire documents for LLM.
       Best for small document sets where full context matters (architecture docs, APIs).
    2. Chunked Mode (use_chunking: true): Split documents into chunks for search.
       Best for large document sets where targeted retrieval is needed.

    For EEFrame queries about features, architecture, and interfaces, use Full Context mode
    to preserve cross-section relationships and complete understanding.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.documents = config.get('documents', [])
        self.use_chunking = config.get('use_chunking', False)  # Default: full context
        self.chunk_size = config.get('chunk_size', 500)
        self.chunk_overlap = config.get('chunk_overlap', 100)
        self.base_path = config.get('base_path', os.getcwd())
        self.auto_discover = config.get('auto_discover', False)
        self.file_pattern = config.get('file_pattern', '**/*')  # Default to all files recursive
        # Default exclude patterns for common directories to ignore
        default_excludes = ['.env', '.git', '__pycache__', 'node_modules', '.pytest_cache',
                           'venv', '.venv', 'dist', 'build', '.eggs', '*.egg-info', '.tox']
        self.exclude_patterns = config.get('exclude_patterns', default_excludes)

        # Storage (will be initialized)
        self._chunks: List[Dict[str, Any]] = []
        self._full_documents: List[Dict[str, Any]] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize document index by loading documents."""
        if self._initialized:
            return

        # Auto-discover markdown files if enabled
        if self.auto_discover:
            await self._auto_discover_documents()
        elif not self.documents:
            # If no documents specified and auto_discover is off, enable it by default
            print(f"  [DocumentResearchStrategy] No documents specified, enabling auto-discovery")
            await self._auto_discover_documents()
            self._initialized = True
            return

        mode = "chunked" if self.use_chunking else "full context"
        print(f"  [DocumentResearchStrategy] Initializing with {len(self.documents)} documents ({mode} mode)")

        # Load and process each document
        for doc_config in self.documents:
            await self._load_document(doc_config)

        if self.use_chunking:
            print(f"  [DocumentResearchStrategy] Loaded {len(self._chunks)} chunks from {len(self.documents)} documents")
        else:
            print(f"  [DocumentResearchStrategy] Loaded {len(self._full_documents)} full documents")
        self._initialized = True

    async def _auto_discover_documents(self) -> None:
        """
        Auto-discover all files in the base_path recursively.

        Uses rglob for recursive discovery and filters out:
        - Directories (only includes files)
        - Paths matching exclude_patterns
        - Common ignore patterns (.git, __pycache__, node_modules, etc.)
        """
        base = Path(self.base_path)
        discovered_files = []

        # Use rglob for recursive discovery of all files
        for path in base.rglob("*"):
            # Skip directories (only process files)
            if path.is_dir():
                continue

            # Skip if path matches any exclude pattern
            if self._is_excluded(path, base):
                continue

            discovered_files.append(path)

        if not discovered_files:
            print(f"  [DocumentResearchStrategy] No files found in {base}")
            return

        print(f"  [DocumentResearchStrategy] Auto-discovered {len(discovered_files)} files")

        # Convert discovered files to document configs
        self.documents = []
        for file_path in discovered_files:
            # Get relative path from base_path
            rel_path = file_path.relative_to(base)
            self.documents.append({
                'type': 'file',
                'path': str(rel_path)
            })

        mode = "chunked" if self.use_chunking else "full context"
        print(f"  [DocumentResearchStrategy] Loading {len(self.documents)} auto-discovered documents ({mode} mode)")

        # Load and process each discovered document
        for doc_config in self.documents:
            await self._load_document(doc_config)

        if self.use_chunking:
            print(f"  [DocumentResearchStrategy] Loaded {len(self._chunks)} chunks from {len(self.documents)} documents")
        else:
            print(f"  [DocumentResearchStrategy] Loaded {len(self._full_documents)} full documents")
        self._initialized = True

    def _is_excluded(self, path: Path, base: Path) -> bool:
        """
        Check if a path should be excluded based on exclude_patterns.

        Args:
            path: The file path to check
            base: The base path for resolving relative paths

        Returns:
            True if the path should be excluded, False otherwise
        """
        rel_path = path.relative_to(base)
        parts = rel_path.parts

        for pattern in self.exclude_patterns:
            # Check if any part of the path matches the exclude pattern
            if pattern in parts:
                return True

            # Check for glob-style patterns in filename
            if '*' in pattern and path.match(pattern):
                return True

            # Check for exact match on directory name (e.g., ".git")
            if pattern in str(rel_path):
                # Ensure we're matching directory/segment names, not substrings
                for part in parts:
                    if part == pattern:
                        return True

        return False

    async def _load_document(self, doc_config: Dict[str, Any]) -> None:
        """Load a single document."""
        doc_type = doc_config.get('type', 'file')
        doc_path = doc_config.get('path', '')

        if doc_type == 'file':
            await self._load_local_file(doc_path)
        elif doc_type == 'url':
            # TODO: Implement URL loading
            print(f"  [DocumentResearchStrategy] URL loading not yet implemented: {doc_path}")
        elif doc_type == 'repo':
            # TODO: Implement Git repo loading
            print(f"  [DocumentResearchStrategy] Repo loading not yet implemented: {doc_path}")
        else:
            print(f"  [DocumentResearchStrategy] Unknown document type: {doc_type}")

    async def _load_local_file(self, file_path: str) -> None:
        """Load a local file (chunked or full based on mode)."""
        full_path = Path(self.base_path) / file_path

        if not full_path.exists():
            print(f"  [DocumentResearchStrategy] File not found: {full_path}")
            return

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.use_chunking:
                # Chunking mode: split into chunks for search
                chunks = self._chunk_text(content, str(full_path))
                self._chunks.extend(chunks)
                print(f"  [DocumentResearchStrategy] Loaded {len(chunks)} chunks from {file_path}")
            else:
                # Full context mode: store entire document
                self._full_documents.append({
                    'path': str(full_path),
                    'filename': file_path,
                    'content': content
                })
                print(f"  [DocumentResearchStrategy] Loaded full document: {file_path}")

        except Exception as e:
            print(f"  [DocumentResearchStrategy] Error loading {file_path}: {e}")

    def _chunk_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks for vector search.

        Args:
            text: The text to chunk
            source: Source file path

        Returns:
            List of chunk dictionaries
        """
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            chunks.append({
                'id': f"{source}_{chunk_id}",
                'text': chunk_text,
                'source': source,
                'chunk_id': chunk_id
            })

            start = end - self.chunk_overlap
            chunk_id += 1

        return chunks

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for relevant content in documents.

        In Full Context Mode: Returns all complete documents for the LLM to process.
        In Chunked Mode: Returns relevant chunks using keyword matching.

        Args:
            query: The search query
            limit: Maximum number of results (only applies to chunked mode)

        Returns:
            List of search results with metadata about search scope
        """
        if not self._initialized:
            await self.initialize()

        # Track search metadata for citation prompt
        self._search_metadata = {
            'total_files': len(self._full_documents) if not self.use_chunking else len(self._chunks),
            'query': query,
            'use_chunking': self.use_chunking
        }

        if not self.use_chunking:
            # Full Context Mode: Return all complete documents
            results = []
            for doc in self._full_documents:
                results.append(SearchResult(
                    content=doc['content'],
                    source=doc['filename'],
                    relevance_score=1.0,  # All docs are equally relevant in full context mode
                    metadata={
                        'path': doc['path'],
                        'full_document': True,
                        'total_files': len(self._full_documents)  # For citation prompt
                    }
                ))
            print(f"  [DocumentResearchStrategy] Returning {len(results)} full documents")
            self._search_metadata['matches'] = len(results)
            return results
        else:
            # Chunked Mode: Keyword search
            query_lower = query.lower()
            query_terms = query_lower.split()

            # Score each chunk based on keyword overlap
            scored_chunks = []
            for chunk in self._chunks:
                text_lower = chunk['text'].lower()

                # Simple scoring: count query term occurrences
                score = sum(1 for term in query_terms if term in text_lower)

                if score > 0:
                    scored_chunks.append((chunk, score))

            # Sort by score and take top results
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            top_chunks = scored_chunks[:limit]

            # Convert to SearchResult objects
            results = []
            for chunk, score in top_chunks:
                # Normalize score to 0-1 range
                max_possible_score = len(query_terms)
                normalized_score = min(score / max_possible_score, 1.0)

                results.append(SearchResult(
                    content=chunk['text'],
                    source=chunk['source'],
                    relevance_score=normalized_score,
                    metadata={
                        'chunk_id': chunk['chunk_id'],
                        'chunk_text': chunk['text'],
                        'full_document': False,
                        'total_files': len(self._chunks),  # For citation prompt
                        'total_chunks_searched': len(self._chunks)
                    }
                ))

            print(f"  [DocumentResearchStrategy] Found {len(results)} chunks for query: {query}")
            self._search_metadata['matches'] = len(results)
            self._search_metadata['total_chunks'] = len(self._chunks)
            return results

    def get_search_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the last search operation.

        Returns:
            Dictionary with search metadata (total files, matches, query)
        """
        return getattr(self, '_search_metadata', {
            'total_files': 0,
            'matches': 0,
            'query': ''
        })

    async def cleanup(self) -> None:
        """Clean up resources."""
        self._chunks.clear()
        self._full_documents.clear()
        self._initialized = False


class VectorDocumentResearchStrategy(DocumentResearchStrategy):
    """
    Enhanced document research strategy using vector embeddings.

    This version uses semantic search with embeddings for better results.
    Requires ChromaDB or similar vector database.

    TODO: Implement vector embedding and storage
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Vector DB client (ChromaDB, Weaviate, etc.)
        self._vector_db = None
        self._collection_name = config.get('collection_name', 'documents')

    async def initialize(self) -> None:
        """Initialize vector database and index documents."""
        # TODO: Set up ChromaDB or similar
        # await self._setup_vector_db()
        # await self._index_documents()

        # Fall back to parent implementation for now
        await super().initialize()

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Search using vector embeddings."""
        # TODO: Implement vector search
        # For now, fall back to keyword search
        return await super().search(query, limit)
