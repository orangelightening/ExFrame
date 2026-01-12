"""
Algorithm Explorer Plugin

Specialist for binary algorithms and computational techniques.
Implements the 3-method SpecialistPlugin interface.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.specialist_plugin import SpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase


class AlgorithmExplorerPlugin(SpecialistPlugin):
    """
    Binary algorithm specialist.

    NO inheritance. Just implements 3 methods.
    """

    name = "Algorithm Explorer"
    specialist_id = "algorithm_explorer"

    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict[str, Any] = None):
        """Initialize with knowledge base and optional config."""
        self.kb = knowledge_base
        self.config = config or {}

        self.keywords = self.config.get("keywords", [
            "algorithm", "optimize", "efficient", "fast", "swap",
            "divide", "modulus", "floor", "ceiling", "absolute",
            "minimum", "maximum", "compute", "calculate"
        ])

        self.categories = self.config.get("categories", [
            "algorithm", "technique", "transformation"
        ])

        self.threshold = self.config.get("threshold", 0.30)

    def can_handle(self, query: str) -> float:
        """Can I handle this query?"""
        query_lower = query.lower()
        score = 0.0

        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 0.2

        # Algorithm-specific boosts
        if "algorithm" in query_lower:
            score += 0.2
        if "efficient" in query_lower or "fast" in query_lower:
            score += 0.2
        if "without" in query_lower:
            score += 0.1  # "how to X without Y" pattern

        return min(score, 1.0)

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process the query."""
        # Use prematched patterns from engine if available (more efficient)
        if context and 'prematched_patterns' in context:
            all_patterns = context['prematched_patterns']
        else:
            # Fall back to category-based search (legacy behavior)
            all_patterns = []
            for category in self.categories:
                patterns = await self.kb.search(query, category=category, limit=5)
                all_patterns.extend(patterns)

        # Deduplicate
        seen = set()
        unique_patterns = []
        for pattern in all_patterns:
            pattern_id = pattern.get("pattern_id") or pattern.get("id")
            if pattern_id and pattern_id not in seen:
                seen.add(pattern_id)
                unique_patterns.append(pattern)

        return {
            "query": query,
            "specialist": "algorithm_explorer",
            "patterns_found": len(unique_patterns),
            "patterns": unique_patterns[:5],
            "answer": self._synthesize_answer(query, unique_patterns),
            "confidence": self.can_handle(query)
        }

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format the response for the user."""
        patterns = response_data.get("patterns", [])

        if not patterns:
            return f"[Algorithm Explorer] No patterns found for: {response_data.get('query', '')}"

        result = f"[Algorithm Explorer] Found {response_data.get('patterns_found', 0)} patterns:\n\n"

        for pattern in patterns[:3]:
            result += f"**{pattern.get('name', 'Unknown')}**\n"
            result += f"Type: {pattern.get('type', 'N/A')}\n\n"

            if "solution" in pattern:
                result += f"{pattern['solution']}\n\n"

            if "examples" in pattern and pattern["examples"]:
                result += "**Examples:**\n"
                for ex in pattern["examples"][:3]:
                    result += "   • "
                    if isinstance(ex, str):
                        result += ex
                    elif isinstance(ex, dict):
                        for key, value in ex.items():
                            if key != "notes":
                                result += f"{key}={value} "
                    result += "\n"
                result += "\n"

            if "mathematical_property" in pattern:
                result += f"**Mathematical Property:** {pattern['mathematical_property']}\n\n"

        return result

    def _synthesize_answer(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Synthesize an answer from the patterns."""
        if not patterns:
            return "No relevant patterns found."

        top_pattern = patterns[0]
        return f"See {top_pattern.get('name', 'pattern')}: {top_pattern.get('solution', '')[:100]}..."
