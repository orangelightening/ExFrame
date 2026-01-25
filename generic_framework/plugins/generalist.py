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
Generalist Plugin

A simple, configurable specialist plugin for general-purpose domains.
Can be used for any domain that needs a single specialist.
Implements the 3-method SpecialistPlugin interface.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.specialist_plugin import SpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase


class GeneralistPlugin(SpecialistPlugin):
    """
    A generalist specialist that can be configured for any domain.

    NO inheritance. Just implements 3 methods.
    """

    name = "Generalist"
    specialist_id = "generalist"

    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict[str, Any] = None):
        """Initialize with knowledge base and optional config."""
        self.kb = knowledge_base
        self.config = config or {}

        # Override name from config if provided
        if config and config.get("name"):
            self.name = config["name"]

        self.keywords = self.config.get("keywords", [
            "how", "what", "why", "explain", "make", "do", "create"
        ])

        self.categories = self.config.get("categories", [])

        self.threshold = self.config.get("threshold", 0.25)

    def can_handle(self, query: str) -> float:
        """Can I handle this query?"""
        query_lower = query.lower()
        score = 0.0

        # Score keyword matches
        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 0.15

        # Question words boost
        if any(word in query_lower for word in ["how", "what", "why", "explain", "tell"]):
            score += 0.1

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
            # Search across all configured categories (or all if none specified)
            if self.categories:
                all_patterns = []
                for category in self.categories:
                    patterns = await self.kb.search(query, category=category, limit=5)
                    all_patterns.extend(patterns)
            else:
                # Search all patterns if no categories specified
                all_patterns = await self.kb.search(query, limit=10)

        # Deduplicate
        seen = set()
        unique_patterns = []
        for pattern in all_patterns:
            pid = pattern.get("pattern_id") or pattern.get("id")
            if pid not in seen:
                seen.add(pid)
                unique_patterns.append(pattern)

        return {
            "query": query,
            "specialist": "generalist",
            "patterns_found": len(unique_patterns),
            "patterns": unique_patterns[:5],
            "answer": self._synthesize_answer(query, unique_patterns),
            "confidence": self.can_handle(query)
        }

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format the response for the user."""
        patterns = response_data.get("patterns", [])

        if not patterns:
            return f"[{self.name}] No patterns found for: {response_data.get('query', '')}"

        # When LLM enricher is active, return empty so LLM response appears first
        # Pattern details will still be available in the response_data for the LLM to use
        return ""

    def _synthesize_answer(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Synthesize an answer from the patterns."""
        if not patterns:
            return "No relevant patterns found."

        top_pattern = patterns[0]
        solution = top_pattern.get('solution', '') or top_pattern.get('description', '')
        return f"See {top_pattern.get('name', 'pattern')}: {solution[:100]}..."
