"""
JSON Knowledge Base - JSON file-based pattern storage.

Implements the KnowledgeBasePlugin interface for JSON file storage.
Supports hybrid search combining keyword matching and semantic similarity.
"""

import json
import re
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_base_plugin import KnowledgeBasePlugin
from core.knowledge_base import KnowledgeBaseConfig
from core.embeddings import EmbeddingService, VectorStore, get_embedding_service
from core.hybrid_search import HybridSearcher, HybridSearchConfig


def weighted_random_select(scored_patterns: List[Tuple[Dict, int]], count: int = 10) -> List[Dict]:
    """
    Select patterns using weighted random selection based on relevance score.

    Weighting scale:
    - < 50: irrelevant (very low weight)
    - 60: relevant (low weight)
    - 80: truth (good weight)
    - 100: fact (highest weight)

    Args:
        scored_patterns: List of (pattern, score) tuples
        count: Number of patterns to select

    Returns:
        List of selected patterns
    """
    if not scored_patterns:
        return []

    # If we have fewer patterns than requested, return all
    if len(scored_patterns) <= count:
        return [p for p, _ in scored_patterns]

    # Calculate weights based on relevance score
    weights = []
    for _, score in scored_patterns:
        # Weighting scale from user:
        # < 50: irrelevant (very low)
        # 60: relevant (low)
        # 80: truth (good)
        # 100: fact (highest)
        if score < 50:
            weight = 1  # Very low weight for irrelevant
        elif score < 70:
            weight = 3  # Low weight for relevant
        elif score < 85:
            weight = 8  # Good weight for truth
        else:
            weight = 15  # Highest weight for fact

        weights.append(weight)

    # Weighted random selection
    selected_indices = random.choices(
        range(len(scored_patterns)),
        weights=weights,
        k=min(count, len(scored_patterns))
    )

    # Get unique selections (in case same index is picked multiple times)
    unique_indices = list(set(selected_indices))

    # If we didn't get enough unique patterns, fill the rest randomly
    while len(unique_indices) < min(count, len(scored_patterns)):
        remaining = [i for i in range(len(scored_patterns)) if i not in unique_indices]
        if remaining:
            unique_indices.append(random.choice(remaining))
        else:
            break

    # Return selected patterns
    return [scored_patterns[i][0] for i in unique_indices]


class JSONKnowledgeBase(KnowledgeBasePlugin):
    """
    JSON file-based knowledge base implementation.

    Stores patterns in a JSON file at the configured storage path.
    This is the default knowledge base plugin.
    """

    name = "JSON Knowledge Base"

    def __init__(self, config: KnowledgeBaseConfig):
        """Initialize with config."""
        self.config = config
        self.storage_file = Path(config.storage_path) / "patterns.json"
        self._ensure_storage_exists()
        self._patterns = []
        self._pattern_index = {}
        self._loaded = False

        # Hybrid search components
        storage_path = Path(config.storage_path)
        self.vector_store = VectorStore(storage_path)
        self.vector_store.load()

        # Initialize embedding service (may be None if not available)
        self.embedding_service = get_embedding_service()

        # Hybrid search configuration
        self.hybrid_config = HybridSearchConfig(
            semantic_weight=0.5,
            keyword_weight=0.5,
            min_semantic_score=0.0,  # Allow any semantic match to be considered
            min_keyword_score=0
        )

        # Hybrid searcher (created on first search if embeddings available)
        self._hybrid_searcher: Optional[HybridSearcher] = None

        # Feature flag: enable hybrid search
        self.use_hybrid_search = True

    def _get_hybrid_searcher(self) -> Optional[HybridSearcher]:
        """Get or create the hybrid searcher."""
        if not self.use_hybrid_search:
            return None

        if self._hybrid_searcher is None and self.embedding_service:
            # Auto-load model if embeddings exist and model isn't loaded yet
            if not self.embedding_service.is_loaded and len(self.vector_store) > 0:
                print("[KB] Loading embedding model (auto-loading due to existing embeddings)")
                try:
                    self.embedding_service.load_model()
                except Exception as e:
                    print(f"[KB] Failed to load embedding model: {e}")
                    return None

            if self.embedding_service.is_loaded:
                self._hybrid_searcher = HybridSearcher(
                    embedding_service=self.embedding_service,
                    vector_store=self.vector_store,
                    config=self.hybrid_config
                )
                print("[KB] Hybrid search enabled")
            else:
                print("[KB] Embedding service not loaded, using keyword-only search")

        return self._hybrid_searcher

    def set_hybrid_weights(self, semantic: float, keyword: float) -> None:
        """Adjust hybrid search weights dynamically."""
        self.hybrid_config.update_weights(semantic, keyword)
        if self._hybrid_searcher:
            self._hybrid_searcher.set_config(self.hybrid_config)
        print(f"[KB] Updated weights: semantic={self.hybrid_config.semantic_weight:.2f}, keyword={self.hybrid_config.keyword_weight:.2f}")

    async def generate_embeddings(self) -> Dict[str, str]:
        """
        Generate embeddings for all patterns that don't have them.

        Returns:
            Dict with status: {'generated': int, 'skipped': int, 'failed': int}
        """
        if not self.embedding_service or not self.embedding_service.is_available:
            return {'error': 'Embedding service not available'}

        # Ensure model is loaded
        self.embedding_service.load_model()

        if not self._loaded:
            await self.load_patterns()

        generated = 0
        skipped = 0
        failed = 0

        print(f"[KB] Generating embeddings for {len(self._patterns)} patterns...")

        for pattern in self._patterns:
            pattern_id = pattern.get('pattern_id') or pattern.get('id') or pattern.get('name', '')

            if not pattern_id:
                failed += 1
                continue

            # Skip if already has embedding
            if self.vector_store.has(pattern_id):
                skipped += 1
                continue

            try:
                embedding = self.embedding_service.encode_pattern(pattern)
                self.vector_store.set(pattern_id, embedding)
                generated += 1
            except Exception as e:
                print(f"[KB] Failed to generate embedding for {pattern_id}: {e}")
                failed += 1

        # Save to disk
        self.vector_store.save()

        result = {
            'generated': generated,
            'skipped': skipped,
            'failed': failed,
            'total': len(self._patterns)
        }

        print(f"[KB] Embedding generation complete: {result}")

        # Initialize hybrid searcher now that we have embeddings
        if generated > 0 or len(self.vector_store) > 0:
            self._get_hybrid_searcher()

        return result

    def get_embedding_status(self) -> Dict[str, Any]:
        """Get status of embeddings for patterns."""
        if not self._loaded:
            return {'error': 'Patterns not loaded'}

        total = len(self._patterns)
        embedded = len(self.vector_store)
        needs_embedding = total - embedded

        return {
            'total_patterns': total,
            'has_embeddings': embedded,
            'needs_embeddings': needs_embedding,
            'coverage_percent': round(embedded / total * 100, 1) if total > 0 else 0,
            'semantic_available': self.embedding_service is not None and self.embedding_service.is_available,
            'hybrid_enabled': self._hybrid_searcher is not None
        }

    def _ensure_storage_exists(self) -> None:
        """Ensure storage directory and file exist."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.storage_file.exists():
            # Create empty patterns file
            with open(self.storage_file, 'w') as f:
                json.dump([], f)

    async def load_patterns(self) -> None:
        """Load all patterns from JSON file."""
        try:
            with open(self.storage_file, 'r') as f:
                self._patterns = json.load(f)

            # Build index
            self._pattern_index = {}
            for p in self._patterns:
                # Use pattern_id if available, otherwise fallback to id or name
                key = p.get('pattern_id') or p.get('id') or p.get('name', '')
                if key:
                    self._pattern_index[key] = p

            self._loaded = True
        except FileNotFoundError:
            self._patterns = []
            self._pattern_index = {}
            self._loaded = True
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in patterns file: {e}")

    async def save_pattern(self, pattern: Dict[str, Any]) -> None:
        """Save a pattern to the JSON file."""
        self._patterns.append(pattern)
        # Use same key priority as load_patterns: pattern_id -> id -> name
        key = pattern.get('pattern_id') or pattern.get('id') or pattern.get('name', '')
        if key:
            self._pattern_index[key] = pattern
        await self._persist()

    async def _persist(self) -> None:
        """Persist patterns to file."""
        with open(self.storage_file, 'w') as f:
            json.dump(self._patterns, f, indent=2)

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        exact_only: bool = False,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Search patterns using hybrid semantic + keyword search.

        Falls back to keyword-only search if embeddings not available.
        """
        if not self._loaded:
            await self.load_patterns()

        query_lower = query.lower()

        # Extract content words from query (for better matching)
        # Strip punctuation from words
        import string
        content_words = [
            w.strip(string.punctuation)
            for w in query_lower.split()
            if w.strip(string.punctuation) not in self.STOP_WORDS
            and len(w.strip(string.punctuation)) > 2
        ]

        print(f"  [SEARCH] Query: '{query[:60]}...'")
        print(f"  [SEARCH] Content words: {content_words}")
        print(f"  [SEARCH] Total patterns to check: {len(self._patterns)}")

        # Check if hybrid search is available
        hybrid_searcher = self._get_hybrid_searcher()

        # Step 1: Filter by category and collect keyword scores
        filtered_patterns = []
        keyword_scores: Dict[str, int] = {}
        exact_match_ids = []

        for pattern in self._patterns:
            # Filter by category if specified
            if category:
                pattern_cats = pattern.get('category', pattern.get('pattern_type', ''))
                pattern_tags = pattern.get('tags', [])
                if category != pattern_cats and category not in pattern_tags:
                    continue

            pattern_id = pattern.get('pattern_id') or pattern.get('id') or pattern.get('name', '')
            if not pattern_id:
                continue

            # Check for exact match
            has_exact_match = False
            has_origin_word_match = False
            origin_query = pattern.get('origin_query', '').lower()

            if origin_query == query_lower:
                has_exact_match = True
            elif content_words:
                for word in content_words:
                    if word in origin_query:
                        has_origin_word_match = True
                        break

            if not has_exact_match:
                examples = pattern.get('examples', [])
                if examples and query_lower in [str(ex).lower() for ex in examples]:
                    has_exact_match = True

            if exact_only and not has_exact_match:
                continue

            # Calculate keyword score
            match_count = self._count_matching_fields(pattern, query_lower)

            if has_exact_match:
                match_count += 100
                exact_match_ids.append(pattern_id)
            elif has_origin_word_match:
                match_count += 30

            # Store keyword score for all patterns (0 if no matches)
            keyword_scores[pattern_id] = match_count

            # For keyword-only search: only include patterns with matches
            # For hybrid search: include all patterns (semantic can find relevance)
            if hybrid_searcher and self.hybrid_config.semantic_weight > 0:
                # Include all patterns for hybrid search
                filtered_patterns.append(pattern)
            else:
                # Only include patterns with keyword matches for keyword-only search
                base_score = match_count
                if has_origin_word_match:
                    base_score -= 30
                if has_exact_match:
                    base_score -= 100

                if match_count > 0 and (base_score > 0 or has_origin_word_match or has_exact_match):
                    filtered_patterns.append(pattern)

        # Step 2: Use hybrid search if available, otherwise keyword-only
        if hybrid_searcher and self.hybrid_config.semantic_weight > 0:
            print(f"  [SEARCH] Using hybrid search (semantic enabled)")
            results = hybrid_searcher.search(
                query=query,
                patterns=filtered_patterns,
                keyword_scores=keyword_scores,
                top_k=limit
            )
            return [r.pattern for r in results]
        else:
            print(f"  [SEARCH] Using keyword-only search")
            # Convert to tuples for weighted_random_select
            scored_patterns = [
                (p, keyword_scores.get(p.get('pattern_id') or p.get('id') or p.get('name', ''), 0))
                for p in filtered_patterns
            ]
            selected = weighted_random_select(scored_patterns, count=limit)
            return selected

    async def get_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific pattern by ID.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Pattern dict or None if not found
        """
        if not self._loaded:
            await self.load_patterns()

        # Try direct index lookup first
        if pattern_id in self._pattern_index:
            return self._pattern_index[pattern_id]

        # Fallback to linear search
        for pattern in self._patterns:
            if pattern.get('pattern_id') == pattern_id or pattern.get('id') == pattern_id:
                return pattern

        return None

    def get_all_categories(self) -> List[str]:
        """
        Get all available categories.

        Returns:
            List of category names
        """
        if not self._loaded:
            return []

        categories = set()
        for p in self._patterns:
            if 'category' in p:
                categories.add(p['category'])
            if 'pattern_type' in p:
                categories.add(p['pattern_type'])
            if 'tags' in p:
                categories.update(p['tags'])

        return sorted(list(categories))

    def get_pattern_count(self) -> int:
        """
        Get total number of patterns loaded.

        Returns:
            Pattern count
        """
        if not self._loaded:
            return 0
        return len(self._patterns)

    async def save_pattern(self, pattern: Dict[str, Any]) -> None:
        """Save a pattern to the JSON file."""
        self._patterns.append(pattern)
        key = pattern.get('pattern_id') or pattern.get('id') or pattern.get('name', '')
        if key:
            self._pattern_index[key] = pattern
        await self._persist()

    async def find_similar(
        self,
        query: str,
        threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find patterns similar to query.

        Returns list of (pattern, similarity_score) tuples.
        """
        if threshold is None:
            threshold = self.config.similarity_threshold

        results = await self.search(query, limit=self.config.max_results)
        scored = []

        for pattern in results:
            score = self._calculate_similarity(query, pattern)
            if score >= threshold:
                scored.append((pattern, score))

        # Sort by similarity score
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    async def add_pattern(self, pattern: Dict[str, Any]) -> str:
        """Add a new pattern, return pattern ID."""
        # Generate ID if not present
        if 'id' not in pattern:
            existing_count = len(self._patterns)
            domain = pattern.get('domain', 'unknown')
            pattern['id'] = f"{domain}_{existing_count + 1:03d}"

        # Add timestamps
        now = datetime.utcnow().isoformat()
        pattern['created_at'] = now
        pattern['updated_at'] = now

        await self.save_pattern(pattern)
        return pattern['id']

    async def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing pattern."""
        pattern = self._pattern_index.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern not found: {pattern_id}")

        # Update fields
        pattern.update(updates)
        pattern['updated_at'] = datetime.utcnow().isoformat()

        await self._persist()

    async def delete_pattern(self, pattern_id: str) -> None:
        """Delete a pattern."""
        pattern = self._pattern_index.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern not found: {pattern_id}")

        self._patterns.remove(pattern)
        del self._pattern_index[pattern_id]
        await self._persist()

    async def record_feedback(
        self,
        pattern_id: str,
        feedback: Dict[str, Any]
    ) -> None:
        """Record user feedback for learning."""
        pattern = self._pattern_index.get(pattern_id)
        if not pattern:
            return

        # Update confidence based on feedback
        if 'rating' in feedback:
            current_confidence = pattern.get('confidence', 0.5)
            rating = feedback['rating'] / 5.0  # Normalize to 0-1
            # Blend current confidence with new rating
            new_confidence = (current_confidence * self.config.feedback_decay + rating * (1 - self.config.feedback_decay))
            pattern['confidence'] = round(new_confidence, 2)

        # Update access count
        if 'times_accessed' in pattern:
            pattern['times_accessed'] = pattern.get('times_accessed', 0) + 1
        else:
            pattern['times_accessed'] = 1

        await self._persist()

    def get_patterns_by_category(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all patterns, optionally filtered by category."""
        if not self._loaded:
            # Return empty if not loaded (sync method)
            return []

        if category:
            return [
                p for p in self._patterns
                if p.get('pattern_type') == category or
                category in p.get('tags', [])
            ]
        else:
            # Return all patterns
            return self._patterns

    async def get_all_patterns(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all patterns (async wrapper for API compatibility).

        Args:
            limit: Maximum patterns to return

        Returns:
            List of pattern dictionaries
        """
        if not self._loaded:
            await self.load_patterns()

        return self._patterns[:limit]

    def get_all_categories(self) -> List[str]:
        """Get all categories."""
        if not self._loaded:
            return []

        categories = set()
        for p in self._patterns:
            if 'pattern_type' in p:
                categories.add(p['pattern_type'])
            if 'tags' in p:
                categories.update(p['tags'])

        return sorted(list(categories))

    def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by its ID."""
        if not self._loaded:
            return None

        for pattern in self._patterns:
            if pattern.get('id') == pattern_id:
                return pattern

        return None

    # Common stop words that shouldn't influence matching
    STOP_WORDS = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'what',
        'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
        'there', 'here', 'this', 'that', 'these', 'those', 'for', 'of', 'with',
        'by', 'from', 'in', 'on', 'at', 'to', 'into', 'onto', 'upon', 'about',
        'between', 'among', 'through', 'during', 'before', 'after', 'above',
        'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further',
        'then', 'once', 'and', 'or', 'but', 'if', 'because', 'as', 'until',
        'while', 'though', 'although', 'i', 'you', 'your', 'my', 'me', 'make',
        'get', 'give', 'know', 'take', 'see', 'come', 'think', 'look', 'want',
        'tell', 'ask', 'work', 'seem', 'feel', 'try', 'leave', 'call', 'keep',
        'let', 'begin', 'help', 'show', 'hear', 'play', 'run', 'move', 'live',
        'believe', 'hold', 'bring', 'write', 'stand', 'set', 'learn', 'change',
        'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak',
        'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer',
        'remember', 'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die',
        'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'remain',
        'type', 'types', 'like', 'just', 'some', 'more', 'much', 'many', 'such'
    }

    def _count_matching_fields(self, pattern: Dict[str, Any], query_lower: str) -> int:
        """
        Count how many content words match in pattern fields.

        Filters out stop words and counts meaningful content matches.
        """
        count = 0

        # Split query into words and filter out stop words
        query_words = [w for w in query_lower.split() if w not in self.STOP_WORDS and len(w) > 2]
        if not query_words:
            return 0

        # Check all searchable fields
        fields_to_check = [
            pattern.get('name', ''),
            pattern.get('description', ''),
            pattern.get('problem', ''),
            pattern.get('solution', ''),
            pattern.get('origin_query', ''),
            ' '.join(pattern.get('tags', [])),
            ' '.join(str(ex) for ex in pattern.get('examples', []))
        ]

        # For each field, check if ANY query word matches
        for field_value in fields_to_check:
            if not field_value:
                continue
            field_lower = field_value.lower()
            for word in query_words:
                if word in field_lower:
                    count += 1
                    break  # Count each field once, even if multiple words match

        return count

    def _calculate_similarity(self, query: str, pattern: Dict[str, Any]) -> float:
        """Calculate similarity score (0-1) - simplified version."""
        query_lower = query.lower()
        match_count = self._count_matching_fields(pattern, query_lower)
        # Normalize: 6 fields max, so return match_count / 6
        return min(match_count / 6.0, 1.0)
