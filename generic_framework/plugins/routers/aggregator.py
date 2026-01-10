"""
Response Aggregation for Multi-Specialist Routing

Handles merging results from multiple specialists based on routing strategy.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SpecialistResponse:
    """Response from a single specialist."""
    specialist_id: str
    confidence: float
    patterns: List[Dict[str, Any]]
    raw_answer: str
    metadata: Dict[str, Any]


class ResponseAggregator:
    """
    Aggregates responses from multiple specialists.

    Strategies:
    - merge_all: Combine all patterns, re-rank by combined score
    - first_wins: Use first specialist's response, show others in metadata
    - side_by_side: Show each specialist's response separately
    - best_pattern: Select best pattern across all specialists
    """

    async def aggregate(
        self,
        responses: List[SpecialistResponse],
        strategy: str = "merge_all",
        query: str = ""
    ) -> Dict[str, Any]:
        """
        Aggregate multiple specialist responses.

        Args:
            responses: List of SpecialistResponse objects
            strategy: Aggregation strategy
            query: Original query (for context)

        Returns:
            Aggregated response_data dict suitable for formatting
        """
        if not responses:
            return {
                "query": query,
                "patterns": [],
                "specialist_id": "none",
                "confidence": 0.0,
                "aggregation_strategy": strategy,
                "responses": []
            }

        if len(responses) == 1:
            # Single response, return as-is
            return {
                "query": query,
                "patterns": responses[0].patterns,
                "specialist_id": responses[0].specialist_id,
                "confidence": responses[0].confidence,
                "raw_answer": responses[0].raw_answer,
                "aggregation_strategy": "single",
                "responses": [self._response_to_dict(responses[0])]
            }

        # Multiple responses - apply aggregation strategy
        if strategy == "first_wins":
            return self._first_wins(responses, query)
        elif strategy == "side_by_side":
            return self._side_by_side(responses, query)
        elif strategy == "best_pattern":
            return self._best_pattern(responses, query)
        else:  # merge_all (default)
            return self._merge_all(responses, query)

    def _merge_all(self, responses: List[SpecialistResponse], query: str) -> Dict[str, Any]:
        """Merge all patterns, re-rank by combined relevance score."""
        # Collect all patterns with their source specialist
        all_patterns = []
        for resp in responses:
            for pattern in resp.patterns:
                # Add source specialist info
                pattern_enhanced = pattern.copy()
                pattern_enhanced["_source_specialist"] = resp.specialist_id
                pattern_enhanced["_source_confidence"] = resp.confidence

                # Calculate combined score (pattern confidence * specialist confidence)
                pattern_confidence = pattern.get("confidence", 0.5)
                combined_score = pattern_confidence * resp.confidence
                pattern_enhanced["_combined_score"] = combined_score

                all_patterns.append(pattern_enhanced)

        # Sort by combined score
        all_patterns.sort(key=lambda p: p.get("_combined_score", 0.0), reverse=True)

        # Remove duplicates (same pattern_id)
        seen = set()
        unique_patterns = []
        for p in all_patterns:
            pid = p.get("pattern_id") or p.get("id")
            if pid and pid not in seen:
                seen.add(pid)
                unique_patterns.append(p)

        return {
            "query": query,
            "patterns": unique_patterns,
            "specialist_id": f"multi_{len(responses)}",
            "confidence": max(r.confidence for r in responses),
            "aggregation_strategy": "merge_all",
            "responses": [self._response_to_dict(r) for r in responses],
            "pattern_count": len(unique_patterns),
            "specialist_count": len(responses)
        }

    def _first_wins(self, responses: List[SpecialistResponse], query: str) -> Dict[str, Any]:
        """Use first specialist's response, include others in metadata."""
        first = responses[0]

        return {
            "query": query,
            "patterns": first.patterns,
            "specialist_id": first.specialist_id,
            "confidence": first.confidence,
            "raw_answer": first.raw_answer,
            "aggregation_strategy": "first_wins",
            "responses": [self._response_to_dict(r) for r in responses],
            "alternative_responses": [self._response_to_dict(r) for r in responses[1:]]
        }

    def _side_by_side(self, responses: List[SpecialistResponse], query: str) -> Dict[str, Any]:
        """Show each specialist's response separately."""
        return {
            "query": query,
            "patterns": [],  # Empty, patterns are in individual responses
            "specialist_id": f"multi_{len(responses)}",
            "confidence": max(r.confidence for r in responses),
            "aggregation_strategy": "side_by_side",
            "responses": [self._response_to_dict(r) for r in responses],
            "specialist_count": len(responses)
        }

    def _best_pattern(self, responses: List[SpecialistResponse], query: str) -> Dict[str, Any]:
        """Select the single best pattern across all specialists."""
        # Find best pattern
        best_pattern = None
        best_score = 0.0
        best_specialist = None

        for resp in responses:
            for pattern in resp.patterns:
                pattern_confidence = pattern.get("confidence", 0.5)
                combined_score = pattern_confidence * resp.confidence

                if combined_score > best_score:
                    best_score = combined_score
                    best_pattern = pattern
                    best_specialist = resp.specialist_id

        if best_pattern:
            return {
                "query": query,
                "patterns": [best_pattern],
                "specialist_id": best_specialist,
                "confidence": best_score,
                "aggregation_strategy": "best_pattern",
                "responses": [self._response_to_dict(r) for r in responses]
            }

        # Fallback to merge_all if no patterns found
        return self._merge_all(responses, query)

    def _response_to_dict(self, response: SpecialistResponse) -> Dict[str, Any]:
        """Convert SpecialistResponse to dict."""
        return {
            "specialist_id": response.specialist_id,
            "confidence": response.confidence,
            "pattern_count": len(response.patterns),
            "raw_answer": response.raw_answer,
            "metadata": response.metadata
        }
