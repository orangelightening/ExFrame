"""
Confidence-Based Router Plugin

Routes queries to the specialist with the highest confidence score.
This is the default routing behavior.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.router_plugin import RouterPlugin, RouteResult


class ConfidenceBasedRouter(RouterPlugin):
    """
    Routes queries to the specialist with the highest confidence score.

    This is the classic routing strategy:
    1. Query each specialist's can_handle() method
    2. Select the specialist with the highest score
    3. If no specialist meets the threshold, use generalist

    Configuration:
        threshold: Minimum confidence score to select a specialist (default: 0.3)
        fallback_to_generalist: If True, use generalist when no specialist meets threshold (default: True)
        generalist_id: ID of the generalist specialist (default: "generalist")
    """

    name = "Confidence-Based Router"
    router_id = "confidence_based"

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the confidence-based router.

        Args:
            config: Configuration dict with optional keys:
                - threshold: Minimum confidence score (default: 0.3)
                - fallback_to_generalist: Whether to use generalist (default: True)
                - generalist_id: ID of generalist specialist (default: "generalist")
        """
        self.config = config or {}

        self.threshold = self.config.get("threshold", 0.30)
        self.fallback_to_generalist = self.config.get("fallback_to_generalist", True)
        self.generalist_id = self.config.get("generalist_id", "generalist")

    async def route(
        self,
        query: str,
        specialists: Dict[str, 'SpecialistPlugin'],
        context: Optional[Dict[str, Any]] = None
    ) -> RouteResult:
        """
        Route query to specialist with highest confidence score.

        Args:
            query: The user's query
            specialists: Available specialists
            context: Additional context (unused in basic implementation)

        Returns:
            RouteResult with single best specialist
        """
        # Score each specialist
        specialist_scores = []
        for spec_id, specialist in specialists.items():
            score = specialist.can_handle(query)
            if score > 0:
                specialist_scores.append((spec_id, score))

        # Sort by score descending
        specialist_scores.sort(key=lambda x: x[1], reverse=True)

        # Select best specialist
        if specialist_scores:
            best_spec_id, best_score = specialist_scores[0]

            if best_score >= self.threshold:
                # Specialist meets threshold
                return RouteResult(
                    specialist_ids=[best_spec_id],
                    strategy="single",
                    confidence=best_score,
                    reasoning=f"Selected '{best_spec_id}' with confidence {best_score:.2f}",
                    metadata={
                        "all_scores": dict(specialist_scores),
                        "threshold": self.threshold
                    }
                )
            elif self.fallback_to_generalist and self.generalist_id in specialists:
                # No specialist meets threshold, use generalist
                return RouteResult(
                    specialist_ids=[self.generalist_id],
                    strategy="single",
                    confidence=best_score,
                    reasoning=f"No specialist met threshold {self.threshold:.2f}, using '{self.generalist_id}'",
                    metadata={
                        "all_scores": dict(specialist_scores),
                        "threshold": self.threshold,
                        "fallback": True
                    }
                )

        # No specialists available or no matches
        return RouteResult(
            specialist_ids=[],
            strategy="single",
            confidence=0.0,
            reasoning="No specialists available or no matches found",
            metadata={}
        )
