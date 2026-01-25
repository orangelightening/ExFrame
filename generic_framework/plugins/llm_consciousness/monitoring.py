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
Monitoring Plugin

Specialist for monitoring systems and deployment architecture.
Implements the 3-method SpecialistPlugin interface.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.specialist_plugin import SpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase


class MonitoringPlugin(SpecialistPlugin):
    """
    Monitoring and architecture specialist.

    NO inheritance. Just implements 3 methods.
    """

    name = "Monitoring"
    specialist_id = "monitoring"

    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict[str, Any] = None):
        """Initialize with knowledge base and optional config."""
        self.kb = knowledge_base
        self.config = config or {}

        self.keywords = self.config.get("keywords", [
            "monitor", "watch", "detect", "alert", "system", "architecture",
            "deploy", "orchestrate", "multi-agent", "concurrent", "timeout", "isolate"
        ])

        self.categories = self.config.get("categories", [
            "monitoring", "architecture", "solution"
        ])

        self.threshold = self.config.get("threshold", 0.30)

    def can_handle(self, query: str) -> float:
        """Can I handle this query?"""
        query_lower = query.lower()
        score = 0.0

        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 0.15

        # Specific monitoring boosts
        if "monitor" in query_lower:
            score += 0.2
        if "architect" in query_lower:
            score += 0.2
        if "deploy" in query_lower:
            score += 0.15
        if "multi-agent" in query_lower or "concurrent" in query_lower:
            score += 0.2

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
            "specialist": "monitoring",
            "patterns_found": len(unique_patterns),
            "patterns": unique_patterns[:5],
            "answer": self._synthesize_answer(query, unique_patterns),
            "confidence": self.can_handle(query)
        }

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format the response for the user."""
        patterns = response_data.get("patterns", [])

        if not patterns:
            return f"[Monitoring] No patterns found for: {response_data.get('query', '')}"

        result = f"[Monitoring] Found {response_data.get('patterns_found', 0)} patterns:\n\n"

        for pattern in patterns[:3]:
            result += f"**{pattern.get('name', 'Unknown')}**\n"
            # Handle both 'type' and 'pattern_type' fields
            pattern_type = pattern.get('type') or pattern.get('pattern_type') or 'N/A'
            # Handle both 'category' and tags for category
            category = pattern.get('category') or (pattern.get('tags', ['N/A'])[0] if pattern.get('tags') else 'N/A')
            result += f"Type: {pattern_type} | Category: {category}\n\n"

            if "problem" in pattern:
                result += f"**Problem:** {pattern['problem']}\n\n"

            if "solution" in pattern:
                result += f"**Solution:** {pattern['solution']}\n\n"

            if "examples" in pattern and pattern["examples"]:
                result += "**Examples:**\n"
                for ex in pattern["examples"][:2]:
                    result += "   • "
                    if isinstance(ex, str):
                        result += ex
                    elif isinstance(ex, dict):
                        for key, value in ex.items():
                            if key != "notes":
                                result += f"{key}={value} "
                    result += "\n"
                result += "\n"

        return result

    def _synthesize_answer(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Synthesize an answer from the patterns."""
        if not patterns:
            return "No relevant patterns found."

        top_pattern = patterns[0]
        return f"See {top_pattern.get('name', 'pattern')}: {top_pattern.get('solution', '')[:100]}..."
