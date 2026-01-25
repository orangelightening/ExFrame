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
Hybrid Search - Combines keyword and semantic search with configurable weighting.

Provides a balanced search approach that leverages both:
1. Keyword matching (fast, precise)
2. Semantic similarity (understands meaning)
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from .embeddings import EmbeddingService, VectorStore


class HybridSearchConfig:
    """Configuration for hybrid search."""

    def __init__(
        self,
        semantic_weight: float = 0.5,
        keyword_weight: float = 0.5,
        min_semantic_score: float = 0.0,
        min_keyword_score: int = 0
    ):
        """
        Initialize hybrid search config.

        Args:
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword score (0-1)
            min_semantic_score: Minimum semantic score to include result
            min_keyword_score: Minimum keyword score to include result
        """
        # Normalize weights to sum to 1
        total = semantic_weight + keyword_weight
        if total > 0:
            self.semantic_weight = semantic_weight / total
            self.keyword_weight = keyword_weight / total
        else:
            self.semantic_weight = 0.5
            self.keyword_weight = 0.5

        self.min_semantic_score = min_semantic_score
        self.min_keyword_score = min_keyword_score

    def update_weights(self, semantic: float, keyword: float) -> None:
        """Update semantic and keyword weights."""
        total = semantic + keyword
        if total > 0:
            self.semantic_weight = semantic / total
            self.keyword_weight = keyword / total


class HybridSearchResult:
    """A search result with combined scores."""

    def __init__(
        self,
        pattern: Dict[str, Any],
        keyword_score: int,
        semantic_score: float,
        combined_score: float
    ):
        self.pattern = pattern
        self.keyword_score = keyword_score
        self.semantic_score = semantic_score
        self.combined_score = combined_score

    def __repr__(self) -> str:
        name = self.pattern.get('name', '?')[:30]
        return f"HybridSearchResult(name='{name}...', combined={self.combined_score:.3f}, kw={self.keyword_score}, sem={self.semantic_score:.3f})"


class HybridSearcher:
    """
    Hybrid search engine that combines keyword and semantic search.

    Scores are combined using weighted average:
    combined = (semantic_score * semantic_weight) + (normalized_keyword_score * keyword_weight)
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService],
        vector_store: VectorStore,
        config: Optional[HybridSearchConfig] = None
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.config = config or HybridSearchConfig()
        self._semantic_available = embedding_service is not None and embedding_service.is_loaded

    @property
    def semantic_available(self) -> bool:
        """Check if semantic search is available."""
        return self._semantic_available

    def set_config(self, config: HybridSearchConfig) -> None:
        """Update the search configuration."""
        self.config = config

    def adjust_weights(self, semantic: float, keyword: float) -> None:
        """Adjust semantic and keyword weights dynamically."""
        self.config.update_weights(semantic, keyword)
        print(f"[HYBRID] Updated weights: semantic={self.config.semantic_weight:.2f}, keyword={self.config.keyword_weight:.2f}")

    def search(
        self,
        query: str,
        patterns: List[Dict[str, Any]],
        keyword_scores: Dict[str, int],
        top_k: int = 10
    ) -> List[HybridSearchResult]:
        """
        Perform hybrid search combining keyword and semantic scores.

        Args:
            query: Search query text
            patterns: List of all patterns
            keyword_scores: Dict of pattern_id -> keyword score
            top_k: Number of results to return

        Returns:
            List of HybridSearchResult objects, sorted by combined score
        """
        # Build pattern lookup
        pattern_map = {p.get('id', p.get('pattern_id', p.get('name', ''))): p for p in patterns}

        # Get semantic scores if available
        semantic_scores: Dict[str, float] = {}
        if self.semantic_available and self.embedding_service:
            query_emb = self.embedding_service.encode(query)
            embeddings = self.vector_store.get_all()

            for pattern_id, pattern_emb in embeddings.items():
                if pattern_id in pattern_map:
                    semantic_scores[pattern_id] = self.embedding_service.cosine_similarity(
                        query_emb, pattern_emb
                    )

        # Calculate max keyword score for normalization
        max_keyword = max(keyword_scores.values()) if keyword_scores else 1
        if max_keyword == 0:
            max_keyword = 1

        # Combine scores
        results = []

        for pattern_id, pattern in pattern_map.items():
            # Get scores
            keyword_score = keyword_scores.get(pattern_id, 0)
            semantic_score = semantic_scores.get(pattern_id, 0.0)

            # Apply minimum thresholds
            if keyword_score < self.config.min_keyword_score:
                if semantic_score < self.config.min_semantic_score:
                    continue  # Below both thresholds, skip

            if semantic_score < self.config.min_semantic_score:
                if keyword_score < self.config.min_keyword_score:
                    continue  # Below both thresholds, skip

            # Normalize keyword score to 0-1 range
            normalized_keyword = keyword_score / max_keyword if max_keyword > 0 else 0

            # Combine with weights
            combined_score = (
                semantic_score * self.config.semantic_weight +
                normalized_keyword * self.config.keyword_weight
            )

            results.append(HybridSearchResult(
                pattern=pattern,
                keyword_score=keyword_score,
                semantic_score=semantic_score,
                combined_score=combined_score
            ))

        # Sort by combined score (descending)
        results.sort(key=lambda r: r.combined_score, reverse=True)

        # Log results - simplified for pure semantic search
        print(f"[SEMANTIC] Query: '{query[:50]}...'")
        if self.config.semantic_weight == 1.0:
            # Pure semantic search - cleaner output
            print(f"[SEMANTIC] Mode: PURE SEMANTIC (100% semantic similarity)")
            print(f"[SEMANTIC] Results: {len(results)} patterns matched")
            for i, r in enumerate(results[:5], 1):
                print(f"  {i}. {r.pattern.get('name', '?')[:35]}... (similarity={r.semantic_score:.4f})")
        else:
            # Hybrid mode - show both scores
            print(f"[SEMANTIC] Mode: HYBRID (semantic={self.config.semantic_weight:.0%}, keyword={self.config.keyword_weight:.0%})")
            print(f"[SEMANTIC] Results: {len(results)} patterns matched")
            for i, r in enumerate(results[:5], 1):
                print(f"  {i}. {r.pattern.get('name', '?')[:30]}... (combined={r.combined_score:.3f}, sem={r.semantic_score:.3f})")

        return results[:top_k]

    def search_exact(
        self,
        query: str,
        patterns: List[Dict[str, Any]],
        keyword_scores: Dict[str, int],
        exact_match_pattern_ids: List[str],
        top_k: int = 10
    ) -> List[HybridSearchResult]:
        """
        Search with exact matches prioritized.

        Exact matches always get top priority, then hybrid scoring applies
        to remaining results.

        Args:
            query: Search query text
            patterns: List of all patterns
            keyword_scores: Dict of pattern_id -> keyword score
            exact_match_pattern_ids: List of pattern IDs that are exact matches
            top_k: Number of results to return

        Returns:
            List of HybridSearchResult objects, sorted by combined score
        """
        exact_set = set(exact_match_pattern_ids)

        # Separate exact matches from others
        exact_results = []
        other_results = []

        for pattern_id, pattern in {p.get('id', p.get('pattern_id', p.get('name', ''))): p for p in patterns}.items():
            keyword_score = keyword_scores.get(pattern_id, 0)
            semantic_score = 0.0

            if self.semantic_available and pattern_id in self.vector_store.get_all():
                query_emb = self.embedding_service.encode(query)
                pattern_emb = self.vector_store.get(pattern_id)
                if pattern_emb is not None:
                    semantic_score = self.embedding_service.cosine_similarity(query_emb, pattern_emb)

            # Exact matches get maximum scores
            if pattern_id in exact_set:
                keyword_score += 100
                semantic_score = max(semantic_score, 1.0)
                exact_results.append(HybridSearchResult(
                    pattern=pattern,
                    keyword_score=keyword_score,
                    semantic_score=semantic_score,
                    combined_score=1.0  # Exact matches always first
                ))
            elif keyword_score > 0 or semantic_score > self.config.min_semantic_score:
                # Normalize and combine for non-exact matches
                max_keyword = max(keyword_scores.values()) if keyword_scores else 1
                if max_keyword == 0:
                    max_keyword = 1
                normalized_keyword = keyword_score / max_keyword
                combined_score = (
                    semantic_score * self.config.semantic_weight +
                    normalized_keyword * self.config.keyword_weight
                )
                other_results.append(HybridSearchResult(
                    pattern=pattern,
                    keyword_score=keyword_score,
                    semantic_score=semantic_score,
                    combined_score=combined_score
                ))

        # Sort non-exact results
        other_results.sort(key=lambda r: r.combined_score, reverse=True)

        # Combine: exact first, then others
        combined = exact_results + other_results

        print(f"[HYBRID] Query: '{query[:50]}...'")
        print(f"[HYBRID] Exact matches: {len(exact_results)}, Other matches: {len(other_results)}")
        for i, r in enumerate(combined[:5], 1):
            marker = "[EXACT]" if r in exact_results else ""
            print(f"  {i}. {r.pattern.get('name', '?')[:30]}... {marker}")

        return combined[:top_k]
