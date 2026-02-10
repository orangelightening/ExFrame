"""
Persona - Simple LLM responder with data source and pattern override.

A persona is a configured LLM responder that either:
1. Uses patterns if provided (override)
2. Uses its configured data source (void/library/internet)

That's the entire decision tree. No more conditionals.
"""

from typing import Optional, Dict, List, Any
import logging


class Persona:
    """
    A persona is a configured LLM responder with a data source.

    Core behavior:
    - If patterns provided → use patterns (override)
    - Else → use configured data source

    Three personas:
    - Poet: void (pure generation)
    - Librarian: library (document search)
    - Researcher: internet (web search)
    """

    def __init__(
        self,
        name: str,
        data_source: str,
        show_thinking: bool = False,
        trace: bool = False
    ):
        """
        Initialize persona.

        Args:
            name: Persona name (poet/librarian/researcher)
            data_source: Data source type (void/library/internet)
            show_thinking: Whether to request LLM reasoning
            trace: Whether to log trace information
        """
        if data_source not in ["void", "library", "internet"]:
            raise ValueError(f"Invalid data source: {data_source}")

        self.name = name
        self.data_source = data_source
        self.show_thinking = show_thinking
        self.trace = trace
        self.logger = logging.getLogger(f"persona.{name}")

    async def respond(
        self,
        query: str,
        override_patterns: Optional[List[Dict]] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Respond to query using persona's data source.

        THE CORE DECISION: If patterns provided, use them.
        Otherwise, use persona's configured data source.

        Args:
            query: User query
            override_patterns: Optional patterns to override data source
            context: Optional context dict (for enrichment settings, etc.)

        Returns:
            Response dict with answer and metadata
        """
        if self.trace:
            self.logger.info(f"[{self.name}] Processing query: {query}")

        # THE ONE DECISION
        if override_patterns:
            if self.trace:
                self.logger.info(
                    f"[{self.name}] Using pattern override ({len(override_patterns)} patterns)"
                )
            content = self._format_patterns(override_patterns)
            source = "patterns_override"
        else:
            if self.trace:
                self.logger.info(f"[{self.name}] Using data source: {self.data_source}")
            content = self._get_data_source_content(query, context)
            source = self.data_source

        # Determine show_thinking: context value overrides persona default
        context = context or {}
        show_thinking = context.get("show_thinking", self.show_thinking)

        # Check for conversation memory prefix (previous conversations)
        memory_prefix = context.get("memory_prefix", "")
        if memory_prefix:
            if self.trace:
                self.logger.info(f"[{self.name}] Using conversation memory prefix ({len(memory_prefix)} chars)")
            # Prepend memory content to whatever content we have
            if content:
                content = memory_prefix + content
            else:
                content = memory_prefix

        # Build prompt
        prompt = self._build_prompt(query, content, show_thinking)

        # Call LLM (async)
        answer = await self._call_llm(prompt, context)

        return {
            "answer": answer,
            "source": source,
            "persona": self.name,
            "query": query,
            "show_thinking": show_thinking,
            "pattern_count": len(override_patterns) if override_patterns else 0
        }

    def _get_data_source_content(self, query: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Get content from persona's configured data source.

        Args:
            query: User query
            context: Optional context dict (may contain library_documents)

        Returns:
            Content string or None (for void)
        """
        context = context or {}
        if self.data_source == "void":
            # Pure generation - no context needed
            return None

        elif self.data_source == "library":
            # Search local document library
            # Check if documents were loaded by query_processor
            library_docs = context.get("library_documents")
            if library_docs:
                self.logger.info(f"Using {len(library_docs)} library documents")
                # Format documents for LLM
                doc_content = "\n\n".join([
                    f"**Document: {doc['name']}**\n{doc['content']}"
                    for doc in library_docs
                ])
                return f"Library documents:\n\n{doc_content}"

            self.logger.info("Library search - no documents loaded, using LLM knowledge")
            return "Using library of knowledge (documents not available)"

        elif self.data_source == "internet":
            # Search the web - use LLM knowledge for now
            # Web search integration will be added in future updates
            try:
                self.logger.info("Web search requested - using LLM knowledge with research capabilities")
                # Return None to let LLM use its training data with research approach
                return None
            except Exception as e:
                self.logger.error(f"Internet search failed: {e}")
                return None

        else:
            raise ValueError(f"Unknown data source: {self.data_source}")

    def _format_patterns(self, patterns: List[Dict]) -> str:
        """
        Format patterns into context string.

        Args:
            patterns: List of pattern dicts

        Returns:
            Formatted context string
        """
        if not patterns:
            return ""

        formatted = []
        for i, p in enumerate(patterns, 1):
            # Extract key fields
            name = p.get('name', 'Untitled')
            solution = p.get('solution', '')
            problem = p.get('problem', '')
            description = p.get('description', '')

            # Build pattern text
            pattern_text = f"[Pattern {i}] {name}\n"
            if problem:
                pattern_text += f"Problem: {problem}\n"
            if description:
                pattern_text += f"Description: {description}\n"
            if solution:
                pattern_text += f"Solution:\n{solution}\n"

            formatted.append(pattern_text)

        return "\n".join(formatted)

    def _format_library_results(self, results: List[Dict]) -> Optional[str]:
        """Format library search results"""
        if not results:
            return None

        formatted = []
        for i, r in enumerate(results, 1):
            # Handle both pattern format and document format
            if 'name' in r:
                # Pattern format
                title = r.get('name', 'Untitled')
                content = r.get('solution', r.get('description', ''))
            else:
                # Document format
                title = r.get('title', 'Untitled')
                content = r.get('content', '')

            formatted.append(f"[Document {i}] {title}\n{content}\n")

        return "\n".join(formatted)

    def _format_web_results(self, results: List[Dict]) -> Optional[str]:
        """Format web search results"""
        if not results:
            return None

        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get('title', 'Untitled')
            url = r.get('url', '')
            snippet = r.get('snippet', r.get('content', ''))

            formatted.append(f"[Source {i}] {title}\n{url}\n{snippet}\n")

        return "\n".join(formatted)

    def _build_prompt(self, query: str, content: Optional[str], show_thinking: bool = False) -> str:
        """
        Build LLM prompt.

        Args:
            query: User query
            content: Context content or None
            show_thinking: Whether to request reasoning explanation

        Returns:
            Complete prompt for LLM
        """
        parts = []

        # Add content if available
        if content:
            parts.append(f"Context:\n{content}\n")

        # For internet data source or // queries, explicitly tell GLM to search
        if self.data_source == "internet" or "//" in query:
            parts.append("IMPORTANT: You have access to web search. Use your browser tool to search for current information online.")

        # Add query
        parts.append(f"Query: {query}")

        # Add thinking instruction if needed
        if show_thinking:
            parts.append(
                "\nBefore answering, briefly explain your reasoning process."
            )

        return "\n".join(parts)

    async def _call_llm(self, prompt: str, context: Dict) -> str:
        """
        Call LLM with prompt.

        Args:
            prompt: Complete prompt
            context: Context dict with settings

        Returns:
            LLM response
        """
        import os
        import httpx

        # Get API credentials from environment
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        # Use AllTools variant for web search capability
        model = os.getenv("LLM_MODEL", "glm-4.7")  # Standard model

        if not api_key:
            self.logger.warning("LLM not configured: No API key")
            return "[LLM not configured: No API key. Set OPENAI_API_KEY environment variable.]"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Determine if this is Anthropic-compatible API (like DeepSeek)
        is_anthropic = "anthropic" in base_url.lower()

        # Get temperature from context or use default
        temperature = context.get('temperature', 0.7)

        if self.trace:
            self.logger.info(f"Calling LLM: model={model}, temp={temperature}")

        # Build payload based on API type
        if is_anthropic:
            # Anthropic/DeepSeek format - user role only
            payload = {
                "model": model,
                "max_tokens": 8192,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            # Note: For Anthropic-compatible endpoints, GLM web search tools aren't supported
            # Use OpenAI-compatible endpoint (/api/coding/paas/v4) for web search
            if model.startswith("glm-") and "//" in prompt:
                self.logger.info(f"GLM model detected on Anthropic endpoint - web search not available, switching to OpenAI endpoint for // queries")

            endpoint = f"{base_url.rstrip('/')}/v1/messages"
        else:
            # OpenAI format - system + user messages
            system_message = "You are a helpful assistant."
            if self.show_thinking:
                system_message += " Always show your step-by-step reasoning before providing your final answer."

            payload = {
                "model": model,
                "max_tokens": 8192,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "stream": False  # We don't use streaming currently
            }

            # Enable GLM web search for // prefix (single-turn embedded format)
            if model.startswith("glm-") and "//" in prompt:
                # Only enable tools for queries that actually need web search
                query_lower = prompt.lower()
                needs_web_search = any(word in query_lower for word in [
                    "weather", "news", "current", "latest", "price", "stock",
                    "temperature", "forecast", "today", "now", "recent", "breaking"
                ])

                if needs_web_search:
                    self.logger.info(f"GLM model (OpenAI format) - enabling web_search via function calling")
                    payload["tools"] = [{
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "Search the web for current information including weather, news, prices, etc.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The search query to execute"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }]
                    payload["tool_choice"] = "auto"  # Let GLM decide when to use tools
                else:
                    self.logger.info(f"GLM model (OpenAI format) - simple query, no web search needed")

            endpoint = f"{base_url.rstrip('/')}/chat/completions"

        # Call LLM API
        timeout = httpx.Timeout(timeout=180.0, connect=60.0, pool=60.0)  # Increased timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Check for tool calls (GLM web_search)
                if "content" in data and isinstance(data["content"], list):
                    for block in data["content"]:
                        if block.get("type") == "tool_calls":
                            # GLM wants to use tools - send back confirmation to execute
                            tool_id = block.get("id", "")
                            self.logger.info(f"GLM requested tool call: {block.get('name', 'unknown')}")

                            # Extract tool calls from the block
                            tool_calls_block = block
                            break
                    else:
                        # No tool calls, return text content
                        return data["content"][0]["text"]

                # Parse response based on API format
                # Handle multiple response formats
                if "code" in data and "success" in data:
                    # Chinese API wrapper format
                    if data.get("success") or data.get("code") == 200 or data.get("code") == 0:
                        if "data" in data:
                            inner_data = data["data"]
                            if isinstance(inner_data, dict):
                                if "choices" in inner_data:
                                    return inner_data["choices"][0]["message"]["content"]
                                elif "content" in inner_data:
                                    if isinstance(inner_data["content"], list):
                                        return inner_data["content"][0].get("text", inner_data["content"][0])
                                    return inner_data["content"]
                                elif isinstance(inner_data, str):
                                    return inner_data
                            return str(inner_data)
                    return f"[LLM Error: API returned error - code: {data.get('code')}, msg: {data.get('msg')}]"

                # Standard OpenAI format
                if "choices" in data:
                    message = data["choices"][0]["message"]
                    # Check for tool_calls in OpenAI format
                    if "tool_calls" in message and message["tool_calls"]:
                        self.logger.info(f"GLM returned {len(message['tool_calls'])} tool_calls - implementing multi-turn")
                        # Extract tool call details
                        tool_call = message["tool_calls"][0]
                        function_name = tool_call["function"]["name"]
                        function_args = tool_call["function"]["arguments"]

                        self.logger.info(f"Tool call: {function_name}({function_args})")

                        # For web_search, we need to execute the search ourselves
                        # Z.AI coding plan doesn't include server-side search execution
                        if function_name == "web_search":
                            self.logger.info("Processing web_search tool call - executing DuckDuckGo search")

                            # Parse the function args as JSON to get the query
                            import json
                            try:
                                args_dict = json.loads(function_args)
                                search_query = args_dict.get("query", function_args)
                            except:
                                search_query = function_args

                            self.logger.info(f"Search query: {search_query}")

                            # Execute actual web search using DuckDuckGo
                            try:
                                from .research.internet_strategy import InternetResearchStrategy

                                # Create search strategy instance
                                search_strategy = InternetResearchStrategy({})
                                await search_strategy.initialize()

                                # Execute search
                                search_results = await search_strategy.search(search_query, limit=5)

                                if search_results:
                                    # Format results for GLM
                                    formatted_results = []
                                    for i, result in enumerate(search_results, 1):
                                        title = result.metadata.get('title', 'Untitled')
                                        url = result.metadata.get('url', '')
                                        snippet = result.content
                                        formatted_results.append(
                                            f"[Result {i}] {title}\nURL: {url}\n{snippet}\n"
                                        )

                                    search_content = "\n".join(formatted_results)
                                    self.logger.info(f"Found {len(search_results)} search results")
                                else:
                                    search_content = f"No search results found for query: {search_query}"
                                    self.logger.warning("No search results returned")

                            except Exception as e:
                                self.logger.error(f"Web search execution failed: {e}", exc_info=True)
                                search_content = f"Search failed: {str(e)}"

                            # Build the multi-turn request
                            messages_with_tool = payload["messages"].copy()
                            messages_with_tool.append({
                                "role": "assistant",
                                "content": message.get("content", ""),
                                "tool_calls": message["tool_calls"]
                            })

                            # Send back search results in tool response
                            tool_response = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": search_content  # Actual search results
                            }
                            self.logger.info(f"Tool response length: {len(search_content)} chars")
                            messages_with_tool.append(tool_response)

                            # Make second request to get actual search results
                            self.logger.info("Sending second request with tool confirmation")
                            payload["messages"] = messages_with_tool
                            # Remove tools from second request
                            if "tools" in payload:
                                del payload["tools"]
                            if "tool_choice" in payload:
                                del payload["tool_choice"]

                            response2 = await client.post(endpoint, headers=headers, json=payload)
                            response2.raise_for_status()
                            data2 = response2.json()

                            if "choices" in data2:
                                msg2 = data2["choices"][0]["message"]
                                if "tool_calls" in msg2 and msg2["tool_calls"]:
                                    self.logger.warning(f"Second response still has tool_calls - may need another round")
                                return msg2["content"]
                            else:
                                self.logger.error(f"Second response format unexpected: {list(data2.keys())}")
                                return message.get("content", "[Tool call executed but response format unknown]")

                        return message.get("content", "[GLM requested unknown tool]")
                    return message["content"]

                # Anthropic format
                elif "content" in data and isinstance(data["content"], list):
                    return data["content"][0]["text"]

                # Direct content field
                elif "content" in data and isinstance(data["content"], str):
                    return data["content"]

                else:
                    return f"[LLM Error: Unknown response format: {list(data.keys())}]"

            except httpx.HTTPStatusError as e:
                self.logger.error(f"LLM HTTP error: {e.response.status_code} - {e.response.text}")
                return f"[LLM Error: HTTP {e.response.status_code}]"

            except Exception as e:
                self.logger.error(f"LLM call failed: {e}", exc_info=True)
                return f"[LLM Error: {str(e)}]"
