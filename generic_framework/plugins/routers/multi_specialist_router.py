"""
Multi-Specialist Router Plugin

Routes queries to multiple specialists in parallel or sequence.
Useful when queries span multiple domains or need multiple perspectives.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.router_plugin import RouterPlugin, RouteResult


class MultiSpecialistRouter(RouterPlugin):
    """
    Routes queries to multiple specialists.

    This router can:
    - Send query to multiple specialists in parallel (for comprehensive answers)
    - Route through specialists sequentially (for progressive refinement)
    - Select top N specialists by confidence

    Configuration:
        strategy: 'parallel' or 'sequential'
        min_specialists: Minimum number of specialists to select (default: 1)
        max_specialists: Maximum number of specialists to select (default: 3)
        threshold: Minimum confidence score to include a specialist (default: 0.2)
        require_threshold: Require at least one specialist to meet threshold (default: False)
    """

    name = "Multi-Specialist Router"
    router_id = "multi_specialist"

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the multi-specialist router.

        Args:
            config: Configuration dict
        """
        self.config = config or {}

        self.strategy = self.config.get("strategy", "parallel")
        self.min_specialists = self.config.get("min_specialists", 1)
        self.max_specialists = self.config.get("max_specialists", 3)
        self.threshold = self.config.get("threshold", 0.2)
        self.require_threshold = self.config.get("require_threshold", False)

    async def route(
        self,
        query: str,
        specialists: Dict[str, 'SpecialistPlugin'],
        context: Optional[Dict[str, Any]] = None
    ) -> RouteResult:
        """
        Route query to multiple specialists.

        Args:
            query: The user's query
            specialists: Available specialists
            context: Additional context

        Returns:
            RouteResult with multiple specialist IDs
        """
        # Score each specialist
        specialist_scores = []
        for spec_id, specialist in specialists.items():
            score = specialist.can_handle(query)
            if score >= self.threshold:
                specialist_scores.append((spec_id, score))

        # Sort by score descending
        specialist_scores.sort(key=lambda x: x[1], reverse=True)

        # Check if we have anyone meeting the threshold
        if self.require_threshold and not specialist_scores:
            return RouteResult(
                specialist_ids=[],
                strategy=self.strategy,
                confidence=0.0,
                reasoning=f"No specialists met threshold {self.threshold:.2f}",
                metadata={"threshold": self.threshold}
            )

        # Select top N specialists
        num_specialists = min(
            self.max_specialists,
            max(self.min_specialists, len(specialist_scores))
        )

        selected_specialists = specialist_scores[:num_specialists]
        specialist_ids = [spec_id for spec_id, _ in selected_specialists]
        scores = [score for _, score in selected_specialists]

        # Calculate average confidence
        avg_confidence = sum(scores) / len(scores) if scores else 0.0

        # Build reasoning
        specialist_desc = ", ".join([f"'{sid}' ({score:.2f})" for sid, score in selected_specialists])
        reasoning = f"Routing to {num_specialists} specialist(s): {specialist_desc}"

        return RouteResult(
            specialist_ids=specialist_ids,
            strategy=self.strategy,
            confidence=avg_confidence,
            reasoning=reasoning,
            metadata={
                "selected_specialists": dict(selected_specialists),
                "threshold": self.threshold,
                "min_specialists": self.min_specialists,
                "max_specialists": self.max_specialists
            }
        )


class ParallelRouter(MultiSpecialistRouter):
    """
    Routes to multiple specialists in parallel.

    All selected specialists process the query simultaneously,
    and their responses are aggregated.
    """

    name = "Parallel Router"
    router_id = "parallel"

    def __init__(self, config: Dict[str, Any] = None):
        # Default to parallel strategy
        config = config or {}
        config["strategy"] = "parallel"
        super().__init__(config)


class SequentialRouter(MultiSpecialistRouter):
    """
    Routes through specialists sequentially.

    Each specialist sees the previous specialist's response,
    enabling progressive refinement.
    """

    name = "Sequential Router"
    router_id = "sequential"

    def __init__(self, config: Dict[str, Any] = None):
        # Default to sequential strategy
        config = config or {}
        config["strategy"] = "sequential"
        super().__init__(config)
