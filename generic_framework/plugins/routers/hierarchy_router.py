"""
Hierarchy Router Plugin

Routes queries through a hierarchy of specialists with fallback chains.
Useful for specialist → fallback → generalist patterns.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.router_plugin import RouterPlugin, RouteResult


class HierarchyRouter(RouterPlugin):
    """
    Routes queries through a hierarchy of specialists.

    This router implements fallback chains:
    1. Try the primary specialist
    2. If it fails or has low confidence, try fallback specialists
    3. Finally fall back to generalist if needed

    Configuration:
        hierarchies: Dict mapping specialist IDs to fallback chains
        threshold: Minimum confidence before triggering fallback
        max_chain_length: Maximum number of specialists in chain
    """

    name = "Hierarchy Router"
    router_id = "hierarchy"

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the hierarchy router.

        Args:
            config: Configuration dict with:
                - hierarchies: Dict of {specialist_id: [fallback1, fallback2, ...]}
                - threshold: Confidence threshold for fallback (default: 0.3)
                - max_chain_length: Max chain length (default: 3)
        """
        self.config = config or {}

        self.hierarchies = self.config.get("hierarchies", {})
        self.threshold = self.config.get("threshold", 0.3)
        self.max_chain_length = self.config.get("max_chain_length", 3)

    async def route(
        self,
        query: str,
        specialists: Dict[str, 'SpecialistPlugin'],
        context: Optional[Dict[str, Any]] = None
    ) -> RouteResult:
        """
        Route query through a hierarchy chain.

        Args:
            query: The user's query
            specialists: Available specialists
            context: Additional context

        Returns:
            RouteResult with fallback chain
        """
        # Score all specialists
        specialist_scores = {}
        for spec_id, specialist in specialists.items():
            score = specialist.can_handle(query)
            if score > 0:
                specialist_scores[spec_id] = score

        if not specialist_scores:
            return RouteResult(
                specialist_ids=[],
                strategy="fallback",
                confidence=0.0,
                reasoning="No specialists matched the query",
                metadata={}
            )

        # Find best primary specialist
        best_spec_id = max(specialist_scores, key=specialist_scores.get)
        best_score = specialist_scores[best_spec_id]

        # Build fallback chain
        chain = [best_spec_id]

        # If best specialist doesn't meet threshold, add fallbacks
        if best_score < self.threshold:
            # Get fallback chain for this specialist
            fallback_chain = self.hierarchies.get(best_spec_id, [])

            # Add fallback specialists that exist and have some confidence
            for fallback_id in fallback_chain:
                if len(chain) >= self.max_chain_length:
                    break
                if fallback_id in specialists and fallback_id not in chain:
                    chain.append(fallback_id)

        reasoning = f"Routing chain: {' → '.join(chain)}"
        if len(chain) > 1:
            reasoning += f" (best: '{best_spec_id}' at {best_score:.2f} < threshold {self.threshold:.2f})"

        return RouteResult(
            specialist_ids=chain,
            strategy="fallback",
            confidence=best_score,
            reasoning=reasoning,
            metadata={
                "primary_specialist": best_spec_id,
                "primary_score": best_score,
                "threshold": self.threshold,
                "all_scores": specialist_scores
            }
        )


class SpecialistWithFallbackRouter(HierarchyRouter):
    """
    Pre-configured hierarchy router for common specialist → fallback → generalist pattern.

    Configuration:
        specialist_order: Preferred order of specialists
        generalist_id: ID of generalist specialist
    """

    name = "Specialist with Fallback Router"
    router_id = "specialist_fallback"

    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}

        # Build hierarchies from specialist_order
        specialist_order = config.get("specialist_order", [])
        generalist_id = config.get("generalist_id", "generalist")

        # Each specialist falls back to the next, then generalist
        hierarchies = {}
        for i, spec_id in enumerate(specialist_order):
            fallback_chain = specialist_order[i+1:] + [generalist_id]
            hierarchies[spec_id] = fallback_chain

        # Generalist has no fallback
        hierarchies[generalist_id] = []

        config["hierarchies"] = hierarchies
        super().__init__(config)
