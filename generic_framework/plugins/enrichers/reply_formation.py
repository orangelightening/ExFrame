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
Reply Formation Enricher for ExFrame Domain Exception

This enricher combines results from document store and local patterns
into a coherent reply for the user.
"""

from typing import List, Dict, Any, Optional
import logging

from core.enrichment_plugin import EnrichmentPlugin

logger = logging.getLogger(__name__)


class ReplyFormationEnricher(EnrichmentPlugin):
    """Enricher for forming replies from multiple sources.
    
    This enricher combines document store and local pattern results
    into a coherent reply based on configurable strategy.
    """
    
    name: str = "ReplyFormationEnricher"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize reply formation enricher.

        Args:
            config: Configuration dictionary with:
                - combine_strategy: How to combine results ("merge", "document_first", "local_first")
                - max_results: Maximum number of results to include
                - show_results: Whether to show pattern hits in response (default: true)
                - show_sources: Whether to show sources in pattern hits (default: true)
        """
        self.config = config
        self.combine_strategy = config.get("combine_strategy", "merge")
        self.max_results = config.get("max_results", 10)
        self.show_results = config.get("show_results", True)
        self.show_sources = config.get("show_sources", True)
        
        logger.info(f"[REPLY_FORM] Initialized with strategy={self.combine_strategy}, max_results={self.max_results}")
    
    async def enrich(self, response_data: Dict, context: Optional[Dict] = None) -> Dict:
        """Form reply from document store and local patterns.

        Args:
            response_data: Response data from specialist
            context: Optional context dictionary

        Returns:
            Enriched response data with combined results and reply
        """
        # Get all result types (research results from docs, document store, local patterns)
        research_results = response_data.get("research_results", [])
        document_results = response_data.get("document_results", [])
        local_results = response_data.get("local_results", [])

        # Research + document store results are the primary sources
        primary_results = research_results + document_results

        if not primary_results and not local_results:
            # No results from any source
            return response_data

        # Check if this is a Type 4 (Analytical Engine) domain
        # Type 4 domains prioritize web search over local patterns
        domain_type = getattr(context, 'domain_type', None) if context else None
        is_type4 = domain_type == "4"

        # For Type 4 domains: only include local patterns if NO web search results exist
        # Type 4 is designed to use web search as primary, local patterns as fallback only
        if is_type4:
            if primary_results:
                # Have web search results - use ONLY those, skip local patterns
                combined = primary_results[:self.max_results]
                logger.info(f"[REPLY_FORM] Type 4: Using web search only ({len(combined)} results, skipping {len(local_results)} local)")
            else:
                # No web search - fall back to local patterns
                combined = local_results[:self.max_results]
                logger.info(f"[REPLY_FORM] Type 4: No web search, using {len(combined)} local patterns as fallback")
        else:
            # Non-Type 4 domains: use configured strategy
            if self.combine_strategy == "merge":
                combined = self._merge_results(primary_results, local_results)
            elif self.combine_strategy == "document_first":
                combined = self._document_first_strategy(primary_results, local_results)
            elif self.combine_strategy == "local_first":
                combined = self._local_first_strategy(primary_results, local_results)
            else:
                # Default to merge
                combined = self._merge_results(primary_results, local_results)

        response_data["combined_results"] = combined
        response_data["reply"] = self._form_reply(combined)

        # Replace patterns with combined results so LLM uses correct context
        # This prevents duplicate pattern lists in the response
        response_data["patterns"] = combined

        logger.info(f"[REPLY_FORM] Formed reply from {len(combined)} results (research: {len(research_results)}, doc: {len(document_results)}, local: {len(local_results)})")

        return response_data
    
    def _merge_results(self, document_results: List[Dict], local_results: List[Dict]) -> List[Dict]:
        """Merge results by interleaving document store and local patterns.
        
        Args:
            document_results: Results from document store
            local_results: Results from local patterns
            
        Returns:
            Combined list of results
        """
        combined = []
        max_len = max(len(document_results), len(local_results))
        
        for i in range(min(max_len, self.max_results)):
            if i < len(document_results):
                combined.append(document_results[i])
            if i < len(local_results):
                combined.append(local_results[i])
        
        return combined
    
    def _document_first_strategy(self, document_results: List[Dict], local_results: List[Dict]) -> List[Dict]:
        """Prioritize document store results, then local patterns.
        
        Args:
            document_results: Results from document store
            local_results: Results from local patterns
            
        Returns:
            Combined list of results
        """
        combined = document_results + local_results
        return combined[:self.max_results]
    
    def _local_first_strategy(self, document_results: List[Dict], local_results: List[Dict]) -> List[Dict]:
        """Prioritize local patterns, then document store results.
        
        Args:
            document_results: Results from document store
            local_results: Results from local patterns
            
        Returns:
            Combined list of results
        """
        combined = local_results + document_results
        return combined[:self.max_results]
    
    def _form_reply(self, results: List[Dict]) -> str:
        """Form a coherent reply from results.

        Args:
            results: List of combined results

        Returns:
            Formatted reply string
        """
        if not results:
            return "I couldn't find any relevant information."

        # Simple reply formation
        reply_parts = []

        for i, result in enumerate(results[:5]):
            source = result.get("source", "local")
            title = result.get("title", result.get("name", "Unknown"))
            url = result.get("url", "")

            # Format source label
            if source == "web_search":
                source_label = "Web"
            elif source == "exframe_instance" or "source" in result:
                source_label = "Doc"
            else:
                source_label = "Local"

            if url:
                reply_parts.append(f"{i+1}. [{source_label}] {title}\n   {url}")
            else:
                reply_parts.append(f"{i+1}. [{source_label}] {title}")

        reply = "\n".join(reply_parts)
        reply += "\n\nWould you like me to elaborate on any of these?"

        return reply
    
    def format_response(self, response_data: Dict, format_type: str = "markdown") -> str:
        """Format response for user.
        
        Args:
            response_data: Response data with combined results
            format_type: Output format type
            
        Returns:
            Formatted response string
        """
        combined_results = response_data.get("combined_results", [])
        reply = response_data.get("reply", "")
        
        if format_type == "markdown":
            return self._format_markdown(combined_results, reply)
        elif format_type == "json":
            return self._format_json(combined_results, reply)
        elif format_type == "compact":
            return self._format_compact(combined_results, reply)
        else:
            # Default to markdown
            return self._format_markdown(combined_results, reply)
    
    def _format_markdown(self, results: List[Dict], reply: str) -> str:
        """Format results as Markdown.

        Args:
            results: List of combined results
            reply: Formatted reply text

        Returns:
            Markdown formatted string
        """
        # If show_results is False, only return the AI reply
        if not self.show_results:
            return reply

        if not results:
            return reply

        output = []
        for result in results[:5]:
            source = result.get("source", "local")
            title = result.get("title", result.get("name", "Unknown"))
            content = result.get("content", result.get("solution", ""))
            url = result.get("url", "")

            # Format source label
            if source == "web_search":
                source_label = "🌐 Web Search"
            elif source == "exframe_instance" or "source" in result:
                source_label = "📄 Document Store"
            else:
                source_label = "📚 Local Pattern"

            output.append(f"### {source_label}: {title}")

            # Show URL for web search results if enabled
            if source == "web_search" and url and self.show_sources:
                output.append(f"**Source:** {url}")

            output.append(f"{content}")
            output.append("")

        output.append("---")
        output.append(reply)

        return "\n".join(output)
    
    def _format_json(self, results: List[Dict], reply: str) -> str:
        """Format results as JSON.
        
        Args:
            results: List of combined results
            reply: Formatted reply text
            
        Returns:
            JSON formatted string
        """
        import json
        
        return json.dumps({
            "results": results,
            "reply": reply
        }, indent=2)
    
    def _format_compact(self, results: List[Dict], reply: str) -> str:
        """Format results as compact text.

        Args:
            results: List of combined results
            reply: Formatted reply text

        Returns:
            Compact formatted string
        """
        if not results:
            return reply

        output = []
        for i, result in enumerate(results):
            source = result.get("source", "local")
            title = result.get("title", result.get("name", "Unknown")[:30])
            url = result.get("url", "")

            # Format source label
            if source == "web_search":
                source_label = "WEB"
            elif source == "exframe_instance" or "source" in result:
                source_label = "DOC"
            else:
                source_label = "LOC"

            if url:
                output.append(f"{i+1}. [{source_label}] {title}\n    {url}")
            else:
                output.append(f"{i+1}. [{source_label}] {title}")

        output.append(f"\n{reply}")

        return "\n".join(output)
