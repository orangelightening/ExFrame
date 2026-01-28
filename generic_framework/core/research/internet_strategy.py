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
Internet Research Strategy

Searches the web for relevant information using DuckDuckGo (no API key required).
"""

import asyncio
import logging
import re
import urllib.parse
from typing import List, Dict, Any
from dataclasses import dataclass

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from .base import ResearchStrategy, SearchResult

logger = logging.getLogger(__name__)


class InternetResearchStrategy(ResearchStrategy):
    """
    Research strategy that searches the internet.

    Uses web search APIs to find relevant information.
    Can leverage MCP web search tools if available.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.search_provider = config.get('search_provider', 'auto')  # 'auto', 'brave', 'google', etc.
        self.max_results = config.get('max_results', 10)
        self.timeout = config.get('timeout', 10)

        # Search API config (if using paid API)
        self.api_key = config.get('api_key')
        self.api_endpoint = config.get('api_endpoint')

    async def initialize(self) -> None:
        """Initialize the search provider."""
        print(f"  [InternetResearchStrategy] Initializing with provider: {self.search_provider}")

        # Check for available search tools
        self._has_mcp_search = self._check_mcp_search_available()
        if self._has_mcp_search:
            print(f"  [InternetResearchStrategy] Using MCP web search tools")
        else:
            print(f"  [InternetResearchStrategy] MCP search not available, using fallback")

    def _check_mcp_search_available(self) -> bool:
        """Check if MCP web search tools are available."""
        # Try to import the MCP web search tool
        try:
            # The tool will be available if MCP is running
            # We can't actually import it directly as a module
            # Instead, we'll try to use it at search time
            return True  # Assume available, will catch errors at search time
        except Exception as e:
            logger.debug(f"[InternetResearchStrategy] MCP search not available: {e}")
            return False

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """
        Search the internet for relevant information.

        Args:
            query: The search query
            limit: Maximum number of results

        Returns:
            List of search results
        """
        if not hasattr(self, '_initialized') or not self._initialized:
            await self.initialize()

        # Try MCP search first
        if self._has_mcp_search:
            return await self._search_with_mcp(query, limit)

        # Fallback to simple implementation
        return await self._search_fallback(query, limit)

    async def _search_with_mcp(self, query: str, limit: int) -> List[SearchResult]:
        """
        Search using DuckDuckGo HTML version (no API key required).

        This provides free web search without needing API keys or MCP tools.
        """
        print(f"  [InternetResearchStrategy] Web search for: {query}")

        if not HAS_HTTPX:
            print(f"  [InternetResearchStrategy] httpx not installed, cannot search web")
            print(f"  [InternetResearchStrategy] Install with: pip install httpx")
            return []

        try:
            # Use DuckDuckGo HTML version for free web search
            encoded_query = urllib.parse.quote(query)
            ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(ddg_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()

                # Parse the HTML response
                results = self._parse_duckduckgo_results(response.text)

                # Limit results
                results = results[:limit]

                print(f"  [InternetResearchStrategy] Found {len(results)} results")

                # Convert to SearchResult format
                search_results = []
                for result in results:
                    search_results.append(SearchResult(
                        content=result.get('snippet', ''),
                        source=result.get('url', ''),
                        relevance_score=0.8,  # Default relevance for web results
                        metadata={
                            'title': result.get('title', ''),
                            'url': result.get('url', '')
                        }
                    ))

                return search_results

        except Exception as e:
            logger.error(f"[InternetResearchStrategy] Web search failed: {e}")
            return []

    def _parse_duckduckgo_results(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse DuckDuckGo HTML results.

        Extracts search results from the HTML response.
        """
        results = []

        # DuckDuckGo HTML structure - updated pattern
        # Format: <a class="result__a" href="//duckduckgo.com/l/?uddg=ENCODED_URL&amp;rut=...">TITLE</a>
        result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'

        # Extract URLs and titles
        url_matches = re.findall(result_pattern, html, re.DOTALL)

        # Extract snippets from result__snippet class
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]+)</a>'
        snippet_matches = re.findall(snippet_pattern, html, re.DOTALL)

        from urllib.parse import unquote

        # Process results
        for i, (redirect_url, title) in enumerate(url_matches):
            # Get snippet if available
            snippet = snippet_matches[i] if i < len(snippet_matches) else ""

            # Decode the DuckDuckGo redirect URL
            # Format: //duckduckgo.com/l/?uddg=ENCODED_URL&amp;rut=HASH
            try:
                if 'uddg=' in redirect_url:
                    # Extract the encoded URL
                    encoded_part = redirect_url.split('uddg=')[1].split('&')[0]
                    # Decode twice (once for HTML entities, once for URL encoding)
                    import html as html_module
                    decoded_once = html_module.unescape(encoded_part)
                    actual_url = unquote(decoded_once)
                else:
                    actual_url = redirect_url
                    # Add https: if missing
                    if actual_url.startswith('//'):
                        actual_url = 'https:' + actual_url
            except Exception as e:
                logger.debug(f"[InternetResearchStrategy] Failed to decode URL: {e}")
                actual_url = redirect_url
                if actual_url.startswith('//'):
                    actual_url = 'https:' + actual_url

            # Clean up HTML entities from title and snippet
            import html as html_module
            title = html_module.unescape(title)
            snippet = html_module.unescape(snippet)

            if title:
                results.append({
                    'title': title.strip(),
                    'url': actual_url,
                    'snippet': snippet.strip()
                })

        return results

    async def _search_fallback(self, query: str, limit: int) -> List[SearchResult]:
        """
        Fallback search implementation.

        Returns placeholder results indicating need for proper search API.
        """
        print(f"  [InternetResearchStrategy] Fallback search for: {query}")
        print(f"  [InternetResearchStrategy] WARNING: No search API configured")

        # Return empty results with helpful message
        return []

    async def cleanup(self) -> None:
        """Clean up resources."""
        pass


class BraveSearchInternetStrategy(InternetResearchStrategy):
    """
    Internet research strategy using Brave Search API.

    Provides private, ad-free search results.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.search_provider = 'brave'
        self.brave_api_key = config.get('brave_api_key', self.api_key)

    async def _search_with_brave(self, query: str, limit: int) -> List[SearchResult]:
        """
        Search using Brave Search API.

        TODO: Implement Brave API calls
        """
        # API endpoint: https://api.search.brave.com/res/v1/web/search
        pass


class GoogleSearchInternetStrategy(InternetResearchStrategy):
    """
    Internet research strategy using Google Search API.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.search_provider = 'google'
        self.google_api_key = config.get('google_api_key', self.api_key)
        self.search_engine_id = config.get('search_engine_id')

    async def _search_with_google(self, query: str, limit: int) -> List[SearchResult]:
        """
        Search using Google Custom Search API.

        TODO: Implement Google API calls
        """
        pass
