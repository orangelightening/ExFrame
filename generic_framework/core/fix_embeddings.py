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
Semantic Embedding Service

Provides text embedding generation and similarity computation
using SentenceTransformers for semantic search.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from functools import lru_cache

# Optional import - will fail gracefully if not installed
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingConfig:
    """Configuration for embedding service."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        embedding_dim: int = 384
    ):
        self.model_name = model_name
        self.embedding_dim = embedding_dim


class EmbeddingService:
    """
    Service for generating text embeddings and computing similarity.

    Uses SentenceTransformers for fast, local semantic embeddings.
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig()
        self._model = None
        self._loaded = False

    @property
    def is_available(self) -> bool:
        """Check if sentence-transformers is available."""
        return SENTENCE_TRANSFORMERS_AVAILABLE

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded and self._model is not None

    def load_model(self) -> None:
        """Load the sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it with: pip install sentence-transformers"
            )

        if self._loaded:
            return

        print(f"[EMBED] Loading model: {self.config.model_name}")
        self._model = SentenceTransformer(self.config.model_name)
        self._loaded = True
        print(f"[EMBED] Model loaded. Embedding dim: {self._model.get_sentence_embedding_dimension()}")

    def ensure_loaded(self) -> None:
        """Ensure model is loaded, loading if necessary."""
        if not self.is_loaded:
            self.load_model()

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a single text string to an embedding vector.

        Args:
            text: Input text to encode

        Returns:
            Embedding vector as numpy array
        """
        self.ensure_loaded()
        return self._model.encode(text, convert_to_numpy=True)

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts to embedding vectors.

        Args:
            texts: List of input texts

        Returns:
            Matrix of embedding vectors (n_texts, embedding_dim)
        """
        self.ensure_loaded()
        return self._model.encode(texts, convert_to_numpy=True)

    MAX_TOKENS = 256  # all-MiniLM-L6-v2 limit

    def encode_pattern(self, pattern: Dict[str, Any]) -> np.ndarray:
        """
        Encode a pattern dictionary to an embedding vector.

        Combines multiple fields for better semantic representation.
        Includes length protection to prevent truncation.

        Args:
            pattern: Pattern dictionary

        Returns:
            Embedding vector
        """
        # Build combined text from relevant fields (priority order)
        parts = []

        # High-priority fields (always include)
        name = pattern.get('name', '')
        if name:
            parts.append(f"Name: {name}")

        solution = pattern.get('solution', '')
        if solution:
            parts.append(f"Solution: {solution}")

        # Secondary fields (include if space permits)
        description = pattern.get('description', '')
        problem = pattern.get('problem', '')
        origin_query = pattern.get('origin_query', '')
        tags = pattern.get('tags', [])

        # Build text with length checking
        combined_text = "\n".join(parts)

        # Rough token count check (1 token ≈ 4 characters for English text)
        estimated_tokens = len(combined_text) // 4

        if estimated_tokens > self.MAX_TOKENS:
            # Need to truncate - use smarter strategy to preserve semantic diversity
            print(f"[EMBED] WARNING: Pattern {pattern.get('id')} may exceed token limit (est. {estimated_tokens} tokens)")

            # Smart truncation: prioritize name + solution, but also include description/problem if space permits
            # This helps maintain semantic diversity between patterns
            name_len = len(f"Name: {name}")
            solution_len = len(f"Solution: {solution}")
            header_len = name_len + solution_len + 2  # +2 for newlines

            # Calculate remaining space for secondary fields
            remaining_tokens = self.MAX_TOKENS - (header_len // 4)  # Convert chars to estimated tokens

            # Try to include description first (most important for semantics)
            if description and remaining_tokens > 20:
                desc_text = f"Description: {description[:200]}"  # Limit to ~50 tokens
                parts = [f"Name: {name}", f"Solution: {solution[:800]}", desc_text]  # Truncate solution to ~200 tokens to make room
                combined_text = "\n".join(parts)
                print(f"[EMBED] Truncated with description included")
            # If no space for description, try problem
            elif problem and remaining_tokens > 20:
                prob_text = f"Problem: {problem[:200]}"
                parts = [f"Name: {name}", f"Solution: {solution[:800]}", prob_text]
                combined_text = "\n".join(parts)
                print(f"[EMBED] Truncated with problem included")
            # Otherwise, just name + truncated solution
            else:
                truncated_parts = [f"Name: {name}", f"Solution: {solution[:1000]}"]  # Limit to ~250 tokens
                combined_text = "\n".join(truncated_parts)
                print(f"[EMBED] Truncated to name + solution only")
        else:
            # Add secondary fields if there's space
            if description:
                parts.append(f"Description: {description}")
            if problem:
                parts.append(f"Problem: {problem}")
            if origin_query:
                parts.append(f"Query: {origin_query}")
            if tags:
                parts.append(f"Tags: {', '.join(tags)}")

            combined_text = "\n".join(parts)

        return self.encode(combined_text)

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Similarity score between -1 and 1 (1 = identical)
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def compute_similarities(
        self,
        query_embedding: np.ndarray,
        pattern_embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Compute cosine similarity between query and all patterns.

        Args:
            query_embedding: Query vector
            pattern_embeddings: Dict of pattern_id -> embedding

        Returns:
            Dict of pattern_id -> similarity score
        """
        similarities = {}
        for pattern_id, pattern_emb in pattern_embeddings.items():
            similarities[pattern_id] = self.cosine_similarity(query_embedding, pattern_emb)
        return similarities

    def find_most_similar(
        self,
        query: str,
        pattern_embeddings: Dict[str, np.ndarray],
        pattern_data: Dict[str, Dict],
        top_k: int = 10,
        threshold: float = 0.0
    ) -> List[Tuple[Dict, float]]:
        """
        Find most similar patterns to a query.

        Args:
            query: Search query text
            pattern_embeddings: Dict of pattern_id -> embedding
            pattern_data: Dict of pattern_id -> pattern dict
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (pattern, similarity_score) tuples, sorted by similarity
        """
        # Encode query
        query_emb = self.encode(query)

        # Compute similarities
        similarities = self.compute_similarities(query_emb, pattern_embeddings)

        # Filter by threshold and sort
        results = []
        for pattern_id, score in similarities.items():
            if score >= threshold and pattern_id in pattern_data:
                results.append((pattern_data[pattern_id], score))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]


class VectorStore:
    """
    Simple vector store for pattern embeddings.

    Stores embeddings in memory with persistence to JSON.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.embeddings_file = storage_path / "embeddings.json"
        self._embeddings: Dict[str, List[float]] = {}
        self._numpy_embeddings: Dict[str, np.ndarray] = {}

    def load(self) -> None:
        """Load embeddings from disk."""
        if not self.embeddings_file.exists():
            print(f"[VECTOR] No existing embeddings file at {self.embeddings_file}")
            return

        with open(self.embeddings_file, 'r') as f:
            self._embeddings = json.load(f)

        # Convert to numpy for computation
        self._numpy_embeddings = {
            k: np.array(v) for k, v in self._embeddings.items()
        }

        print(f"[VECTOR] Loaded {len(self._embeddings)} embeddings")

    def save(self) -> None:
        """Save embeddings to disk."""
        self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.embeddings_file, 'w') as f:
            json.dump(self._embeddings, f)

        print(f"[VECTOR] Saved {len(self._embeddings)} embeddings to {self.embeddings_file}")

    def set(self, pattern_id: str, embedding: np.ndarray) -> None:
        """Store an embedding for a pattern."""
        self._embeddings[pattern_id] = embedding.tolist()
        self._numpy_embeddings[pattern_id] = embedding

    def get(self, pattern_id: str) -> Optional[np.ndarray]:
        """Get an embedding for a pattern."""
        return self._numpy_embeddings.get(pattern_id)

    def get_all(self) -> Dict[str, np.ndarray]:
        """Get all embeddings as numpy arrays."""
        return self._numpy_embeddings.copy()

    def has(self, pattern_id: str) -> bool:
        """Check if an embedding exists for a pattern."""
        return pattern_id in self._numpy_embeddings

    def remove(self, pattern_id: str) -> None:
        """Remove an embedding."""
        self._embeddings.pop(pattern_id, None)
        self._numpy_embeddings.pop(pattern_id, None)

    def clear(self) -> None:
        """Clear all embeddings."""
        self._embeddings.clear()
        self._numpy_embeddings.clear()

    def __len__(self) -> int:
        return len(self._embeddings)


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> Optional[EmbeddingService]:
    """Get or create the singleton embedding service."""
    global _embedding_service
    if _embedding_service is None:
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            _embedding_service = EmbeddingService()
        else:
            print("[EMBED] sentence-transformers not available, semantic search disabled")
    return _embedding_service
