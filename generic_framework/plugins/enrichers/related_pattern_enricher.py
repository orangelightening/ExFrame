"""
Related Pattern Enricher Plugin

Finds and adds related patterns to the response.
Uses tag overlap, category similarity, and keyword matching.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import Counter

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.enrichment_plugin import EnrichmentPlugin, EnrichmentContext


class RelatedPatternEnricher(EnrichmentPlugin):
    """
    Finds related patterns for each pattern in the response.

    Enrichment strategy:
    1. Find patterns with overlapping tags
    2. Find patterns in same category
    3. Find patterns with similar names/descriptions
    4. Rank by similarity score
    5. Add top N related patterns to each pattern

    Configuration:
        - max_related: int (default: 3) - Maximum related patterns per pattern
        - min_similarity: float (default: 0.3) - Minimum similarity threshold
        - use_tags: bool (default: true) - Consider tag overlap
        - use_category: bool (default: true) - Consider category match
        - use_keywords: bool (default: true) - Consider keyword matching
    """

    name = "Related Pattern Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_related = self.config.get("max_related", 3)
        self.min_similarity = self.config.get("min_similarity", 0.3)
        self.use_tags = self.config.get("use_tags", True)
        self.use_category = self.config.get("use_category", True)
        self.use_keywords = self.config.get("use_keywords", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add related patterns to each pattern in response."""
        # Get knowledge base
        kb = context.knowledge_base
        if not kb:
            return response_data

        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        # Get all pattern IDs to avoid self-matches
        pattern_ids = set(p.get("id") or p.get("pattern_id", "") for p in patterns)

        # Enrich each pattern
        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()
            related = await self._find_related_patterns(
                pattern,
                kb,
                pattern_ids,
                context
            )
            if related:
                enriched["related_patterns"] = related
            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    async def _find_related_patterns(
        self,
        pattern: Dict[str, Any],
        kb: 'KnowledgeBase',
        exclude_ids: Set[str],
        context: EnrichmentContext
    ) -> List[Dict[str, Any]]:
        """Find related patterns for a single pattern."""
        pattern_id = pattern.get("id") or pattern.get("pattern_id", "")
        pattern_tags = set(pattern.get("tags", []))
        pattern_category = pattern.get("category") or pattern.get("type", "")
        pattern_name = pattern.get("name", "").lower()
        pattern_desc = pattern.get("description", "").lower()

        # Search for potentially related patterns
        # Use category to narrow search
        search_results = await kb.search(
            pattern_name.split()[0] if pattern_name else "",
            category=None,  # Search all categories
            limit=50
        )

        # Score candidates
        scored = []
        for candidate in search_results:
            cand_id = candidate.get("id") or candidate.get("pattern_id", "")

            # Skip self and already included patterns
            if cand_id == pattern_id or cand_id in exclude_ids:
                continue

            score = 0.0

            # Tag overlap
            if self.use_tags:
                cand_tags = set(candidate.get("tags", []))
                if pattern_tags and cand_tags:
                    overlap = len(pattern_tags & cand_tags)
                    score += (overlap / len(pattern_tags | cand_tags)) * 0.5

            # Category match
            if self.use_category:
                cand_category = candidate.get("category") or candidate.get("type", "")
                if pattern_category and cand_category == pattern_category:
                    score += 0.3

            # Keyword matching in name/description
            if self.use_keywords:
                cand_name = candidate.get("name", "").lower()
                cand_desc = candidate.get("description", "").lower()

                # Simple word overlap
                words = set(pattern_name.split() + pattern_desc.split())
                cand_words = set(cand_name.split() + cand_desc.split())
                if words and cand_words:
                    word_overlap = len(words & cand_words)
                    score += (word_overlap / len(words | cand_words)) * 0.2

            if score >= self.min_similarity:
                scored.append((score, candidate))

        # Sort by score and return top N
        scored.sort(key=lambda x: x[0], reverse=True)
        top_related = scored[:self.max_related]

        # Return minimal pattern info
        return [
            {
                "id": p.get("id") or p.get("pattern_id"),
                "name": p.get("name"),
                "type": p.get("type") or p.get("pattern_type"),
                "similarity": round(score, 2)
            }
            for score, p in top_related
        ]

    def get_supported_formats(self) -> List[str]:
        """Works with all formats."""
        return []


class PatternLinkEnricher(EnrichmentPlugin):
    """
    Adds bidirectional pattern links.

    If pattern A references pattern B, ensure B also references A.
    Useful for building pattern graphs.
    """

    name = "Pattern Link Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add back-references to patterns."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        # Build forward reference map
        forward_refs = {}
        for pattern in patterns:
            pattern_id = pattern.get("id") or pattern.get("pattern_id", "")
            related = pattern.get("related_patterns", [])
            forward_refs[pattern_id] = set(
                r.get("id") or r.get("pattern_id") for r in related if isinstance(r, dict)
            )

        # Add back-references
        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()
            pattern_id = enriched.get("id") or enriched.get("pattern_id", "")

            # Find patterns that reference this one
            back_refs = []
            for other_id, refs in forward_refs.items():
                if other_id != pattern_id and pattern_id in refs:
                    # Find the other pattern's name
                    other_pattern = next(
                        (p for p in patterns if (p.get("id") or p.get("pattern_id")) == other_id),
                        None
                    )
                    if other_pattern:
                        back_refs.append({
                            "id": other_id,
                            "name": other_pattern.get("name", ""),
                            "relation": "referenced_by"
                        })

            if back_refs:
                existing_related = enriched.get("related_patterns", [])
                if isinstance(existing_related, list):
                    enriched["related_patterns"] = existing_related + back_refs
                else:
                    enriched["related_patterns"] = back_refs

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data


class CategoryOverviewEnricher(EnrichmentPlugin):
    """
    Adds category-level overview for multi-pattern responses.

    Shows pattern distribution across categories.
    """

    name = "Category Overview Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.show_counts = self.config.get("show_counts", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add category distribution info."""
        patterns = response_data.get("patterns", [])
        if not patterns or len(patterns) < 2:
            return response_data

        # Count patterns per category
        category_counts = Counter()
        for pattern in patterns:
            category = pattern.get("category") or pattern.get("type", "uncategorized")
            category_counts[category] += 1

        # Add overview
        if self.show_counts:
            response_data["category_distribution"] = [
                {"category": cat, "count": count}
                for cat, count in category_counts.most_common()
            ]

        return response_data

    def get_supported_formats(self) -> List[str]:
        """Best for markdown formats."""
        return ["markdown", "md"]
