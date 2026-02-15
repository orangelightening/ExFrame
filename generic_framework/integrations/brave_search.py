"""
Brave Search API Integration

Provides AI-grounded web search using Brave Answers API.
OpenAI SDK compatible for easy integration.

See: BRAVE_SEARCH_INTEGRATION.md for full documentation
"""

import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger("brave_search")


class BraveSearch:
    """
    Brave Search API client using OpenAI SDK.

    Supports two modes:
    - single: Fast single-search (~3s)
    - research: Deep multi-source research (~8s)
    """

    def __init__(self, api_key: Optional[str] = None, mode: str = "single"):
        """
        Initialize Brave Search client.

        Args:
            api_key: Brave API key (defaults to BRAVE_API_KEY env var)
            mode: 'single' for fast, 'research' for deep
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        self.mode = mode or os.getenv("BRAVE_SEARCH_MODE", "single")

        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not set in environment or constructor")

        self.client = OpenAI(
            base_url="https://api.search.brave.com/res/v1",
            api_key=self.api_key,
        )

        logger.info(f"Brave Search initialized (mode: {self.mode})")

    async def search(
        self,
        query: str,
        mode: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a search query.

        Args:
            query: Search query
            mode: Override default mode ('single' or 'research')
            stream: Enable streaming responses

        Returns:
            dict with:
                - answer: AI-grounded answer with citations
                - source: "brave-answers"
                - mode: Search mode used
                - tokens: Token usage info
                - time_ms: Response time in milliseconds
        """
        import time

        search_mode = mode or self.mode
        start_time = time.time()

        try:
            # Build request
            extra_body = {}
            if search_mode == "research":
                extra_body["enable_research"] = True

            logger.info(f"Brave search: query='{query[:50]}...', mode={search_mode}, stream={stream}")

            # Execute search - query passed as-is, user controls prompt
            response = self.client.chat.completions.create(
                model="brave",
                messages=[{"role": "user", "content": query}],
                stream=stream,
                **({"extra_body": extra_body} if extra_body else {})
            )

            elapsed_ms = (time.time() - start_time) * 1000

            if stream:
                # Return streaming generator
                return self._handle_stream(response, search_mode, start_time)
            else:
                # Return complete response
                answer = response.choices[0].message.content
                usage = response.usage

                logger.info(
                    f"Brave search complete: mode={search_mode}, "
                    f"tokens={usage.total_tokens}, time={elapsed_ms:.1f}ms"
                )

                return {
                    "answer": answer,
                    "source": "brave-answers",
                    "mode": search_mode,
                    "tokens": {
                        "prompt": usage.prompt_tokens,
                        "completion": usage.completion_tokens,
                        "total": usage.total_tokens
                    },
                    "time_ms": elapsed_ms,
                    "confidence": 0.9  # High confidence for cited search results
                }

        except Exception as e:
            logger.error(f"Brave search failed: {e}", exc_info=True)
            raise

    def _handle_stream(self, stream, mode: str, start_time: float):
        """Handle streaming response."""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield {
                    "chunk": chunk.choices[0].delta.content,
                    "mode": mode,
                    "source": "brave-answers"
                }

    def is_available(self) -> bool:
        """Check if Brave Search is configured and available."""
        return bool(self.api_key)


def create_brave_client(mode: str = "single") -> Optional[BraveSearch]:
    """
    Factory function to create Brave Search client.

    Returns None if BRAVE_API_KEY not configured.
    """
    try:
        return BraveSearch(mode=mode)
    except ValueError:
        logger.warning("Brave Search not configured (BRAVE_API_KEY missing)")
        return None


# Convenience function for quick searches
async def brave_search(query: str, mode: str = "single") -> Dict[str, Any]:
    """
    Execute a quick Brave search.

    Args:
        query: Search query
        mode: 'single' (fast) or 'research' (deep)

    Returns:
        Search results dict

    Raises:
        ValueError: If BRAVE_API_KEY not configured
    """
    client = BraveSearch(mode=mode)
    return await client.search(query)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        # Test single-search mode
        result = await brave_search("What is quantum computing?", mode="single")
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Tokens: {result['tokens']['total']}")
        print(f"Time: {result['time_ms']:.1f}ms")

    asyncio.run(test())
