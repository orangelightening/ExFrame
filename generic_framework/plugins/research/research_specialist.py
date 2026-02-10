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
Research Specialist Plugin

Provides web search and research capabilities for domains.
Implements the 3-method SpecialistPlugin interface.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.specialist_plugin import SpecialistPlugin
from knowledge.json_kb import JSONKnowledgeBase
from core.research import create_research_strategy

logger = logging.getLogger(__name__)


class ResearchSpecialistPlugin(SpecialistPlugin):
    """
    A research specialist that performs web search and knowledge retrieval.

    Provides multi-stage search:
    1. Web search (if enabled) - for fresh, external information
    2. Local patterns - for cached domain knowledge

    NO inheritance. Just implements 3 methods.
    """

    name = "Research Specialist"
    specialist_id = "researcher"

    def __init__(self, knowledge_base: JSONKnowledgeBase, config: Dict[str, Any] = None):
        """Initialize with knowledge base and optional config."""
        self.kb = knowledge_base
        self.config = config or {}

        # Research configuration
        self.enable_web_search = self.config.get("enable_web_search", False)
        self.max_research_steps = self.config.get("max_research_steps", 10)
        self.research_timeout = self.config.get("research_timeout", 300)
        self.report_format = self.config.get("report_format", "structured")

        # Initialize research strategy if web search is enabled
        self.research_strategy = None
        if self.enable_web_search:
            try:
                research_config = {
                    "type": "internet",
                    "search_provider": self.config.get("search_provider", "auto"),
                    "max_results": self.config.get("max_results", 10),
                    "timeout": self.config.get("timeout", 10)
                }
                self.research_strategy = create_research_strategy(research_config)
                logger.info(f"[RESEARCH_SPEC] Initialized research strategy: {research_config['type']}")
            except Exception as e:
                logger.error(f"[RESEARCH_SPEC] Failed to initialize research strategy: {e}")
                self.research_strategy = None

        logger.info(f"[RESEARCH_SPEC] Initialized with web_search={self.enable_web_search}")

    def can_handle(self, query: str) -> float:
        """
        Can this specialist handle the query?

        Research specialist can handle any query - it's a generalist.
        Return: Confidence score 0.0 to 1.0
        """
        return 1.0  # Handle all queries

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process the query with research capabilities.

        Two-stage process:
        1. Initial query: Local pattern search only (fast)
        2. Extended search: Web search when user requests it

        Context can include:
        - "web_search_confirmed": True to perform web search
        - "llm_confirmed": True for LLM fallback

        Return: Dict with at least:
            - answer: str (the response text)
            - patterns: List[dict] (patterns used)
            - confidence: float (0.0 to 1.0)
            - can_extend_with_web_search: bool (flag for frontend)
        """
        # Check if this is an extended search request
        web_search_confirmed = context and context.get("web_search_confirmed", False)

        # Stage 1: Local pattern search (always done)
        local_patterns = await self.kb.search(query, limit=10)

        # Calculate base confidence from local results
        confidence = 0.3  # Base confidence
        if local_patterns:
            confidence += 0.4  # Boost for having local patterns
        confidence = min(confidence, 0.8)  # Max 0.8 without web search

        # Stage 2: Web search (perform if web_search_confirmed OR if enable_web_search is true in config)
        research_results = []
        if (web_search_confirmed or self.enable_web_search) and self.research_strategy:
            try:
                logger.info(f"[RESEARCH_SPEC] Performing web search for: {query}")
                await self.research_strategy.initialize()
                search_results = await self.research_strategy.search(query, limit=5)

                # Convert to standard format
                for result in search_results:
                    research_results.append({
                        "title": result.metadata.get("title", result.source),
                        "content": result.content,
                        "source": "web_search",
                        "url": result.source,
                        "relevance": result.relevance_score,
                        "metadata": result.metadata
                    })

                logger.info(f"[RESEARCH_SPEC] Found {len(research_results)} web search results")

                # Boost confidence for having web results
                if research_results:
                    confidence = min(confidence + 0.2, 1.0)

            except Exception as e:
                logger.error(f"[RESEARCH_SPEC] Web search failed: {e}")

        # Combine results
        all_results = []

        # Add local patterns first
        for pattern in local_patterns:
            pattern["source"] = "local"
            all_results.append(pattern)

        # Add web search results (if any)
        if research_results:
            for i, result in enumerate(research_results):
                all_results.append({
                    "pattern_id": f"web_{i}",
                    "name": result.get("title", "Web Search Result"),
                    "solution": result.get("content", ""),
                    "source": "web_search",
                    "relevance": result.get("relevance", 0.5),
                    "url": result.get("source", "")
                })

        # Synthesize answer
        answer = self._synthesize_answer(query, research_results, local_patterns)

        response = {
            "query": query,
            "specialist": "researcher",
            "patterns_found": len(all_results),
            "patterns_used": [p.get("id") or p.get("pattern_id") for p in all_results[:10]],  # Pattern IDs for engine
            "patterns": all_results[:10],  # Full pattern objects for enrichers
            "local_results": local_patterns,
            "answer": answer,
            "confidence": confidence,
            "web_search_enabled": self.enable_web_search
        }

        # Flag can_extend_with_web_search - now always False since we auto-search when enabled
        response["can_extend_with_web_search"] = False

        # Include research results if we did web search
        if research_results:
            response["research_results"] = research_results

        return response

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format the response for the user.

        Shows web search results if available, then local patterns.
        """
        research_results = response_data.get("research_results", [])
        local_patterns = response_data.get("local_results", [])

        # When LLM enricher is active, return empty so LLM response appears first
        # Results will still be available in response_data for the LLM to use
        return ""

    def _synthesize_answer(
        self,
        query: str,
        research_results: List[Dict],
        local_patterns: List[Dict]
    ) -> str:
        """Synthesize an answer from web search and local patterns."""
        parts = []

        if research_results:
            parts.append(f"## Web Search Results ({len(research_results)} results)")
            for i, result in enumerate(research_results[:3]):
                title = result.get("title", "Untitled")
                content = result.get("content", "")[:200]
                parts.append(f"{i+1}. **{title}**\n   {content}...")

        if local_patterns:
            parts.append(f"\n## Local Knowledge ({len(local_patterns)} patterns)")
            for pattern in local_patterns[:3]:
                name = pattern.get("name", "Unnamed")
                solution = pattern.get("solution", "")[:150]
                parts.append(f"- **{name}**: {solution}...")

        if not parts:
            return "No relevant information found in web search or local knowledge."

        return "\n".join(parts)
