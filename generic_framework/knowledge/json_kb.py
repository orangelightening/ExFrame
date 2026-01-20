"""
JSON Knowledge Base - JSON file-based pattern storage.

Implements the KnowledgeBasePlugin interface for JSON file storage.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_base_plugin import KnowledgeBasePlugin
from core.knowledge_base import KnowledgeBaseConfig


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
        Search patterns by simple substring matching.

        Simple and reliable - just checks if query appears in pattern fields.
        """
        if not self._loaded:
            await self.load_patterns()

        query_lower = query.lower()

        # DEBUG: Log search start
        print(f"  [SEARCH] Query: '{query[:50]}...' (lowercased: '{query_lower[:50]}...')")
        print(f"  [SEARCH] Total patterns to check: {len(self._patterns)}")

        # Score each pattern by counting matching fields
        scored_patterns = []
        for pattern in self._patterns:
            # Filter by category if specified
            if category:
                pattern_cats = pattern.get('category', pattern.get('pattern_type', ''))
                pattern_tags = pattern.get('tags', [])
                if category != pattern_cats and category not in pattern_tags:
                    continue

            # Check for exact match first
            has_exact_match = False
            has_substring_match = False
            origin_query = pattern.get('origin_query', '').lower()

            # Full exact match (highest priority)
            if origin_query == query_lower:
                has_exact_match = True
            # Substring match in origin_query (e.g., "gallette" matches "What is a recipe for a gallette")
            elif query_lower in origin_query and len(query_lower) > 3:
                has_substring_match = True

            if not has_exact_match and not has_substring_match:
                examples = pattern.get('examples', [])
                if examples and query_lower in [str(ex).lower() for ex in examples]:
                    has_exact_match = True

            # If exact_only mode, skip patterns without exact match
            if exact_only and not has_exact_match:
                continue

            # Count how many fields contain the query (simple relevance)
            match_count = self._count_matching_fields(pattern, query_lower)

            # Exact matches get highest priority
            if has_exact_match:
                match_count += 100  # Bonus for exact match
            elif has_substring_match:
                match_count += 50  # Bonus for substring match in origin_query

            if match_count > 0:
                scored_patterns.append((pattern, match_count))
                # DEBUG: Log each match
                print(f"  [SEARCH] ✓ Match: '{pattern.get('name', '?')[:40]}...' (score: {match_count}, exact: {has_exact_match})")

        # DEBUG: Log results
        print(f"  [SEARCH] Found {len(scored_patterns)} matches")

        # Sort by match count descending
        scored_patterns.sort(key=lambda x: x[1], reverse=True)

        # Return top patterns
        return [p for p, _ in scored_patterns[:limit]]

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

    def _count_matching_fields(self, pattern: Dict[str, Any], query_lower: str) -> int:
        """
        Count how many query words match in pattern fields.

        Splits query into words and counts matches - works for long queries.
        """
        count = 0

        # Split query into words (simple tokenization)
        query_words = query_lower.split()
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
