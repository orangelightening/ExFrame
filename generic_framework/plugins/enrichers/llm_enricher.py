"""
LLM Enricher Plugin

Uses Large Language Model to enhance responses.
Perfect for summarization, explanation generation, and handling low-confidence matches.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import logging

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.enrichment_plugin import EnrichmentPlugin, EnrichmentContext
from core.research import create_research_strategy, SearchResult

logger = logging.getLogger(__name__)


class LLMEnricher(EnrichmentPlugin):
    """
    Uses LLM to enhance pattern-based responses.

    Use cases:
    - Summarize multiple patterns into coherent answer
    - Generate natural language explanations
    - Fill gaps when pattern match is weak
    - Provide conversational responses

    Configuration:
        - api_key: str - OpenAI/Anthropic API key (or env var OPENAI_API_KEY)
        - base_url: str - API base URL (default: OpenAI)
        - model: str - Model to use (overrides LLM_MODEL env var)
        - min_confidence: float (default: 0.3) - Use LLM if pattern confidence below this
        - max_patterns: int (default: 10) - Max patterns to include in LLM context
        - mode: str (default: "enhance") - Mode: "enhance", "fallback", or "replace"

    Model Priority (first found wins):
        1. LLM_MODEL environment variable (global default for all domains)
        2. Domain config "model" field (per-domain override)
        3. Hardcoded default: glm-4.7
    """

    name = "LLM Enricher"

    # Mode descriptions
    MODE_ENHANCE = "enhance"  # Enhance existing patterns with LLM
    MODE_FALLBACK = "fallback"  # Only use LLM if no good patterns
    MODE_REPLACE = "replace"  # Use LLM for entire response

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.base_url = self.config.get("base_url") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        # Model priority: env var > domain config > hardcoded default
        self.model = (
            os.getenv("LLM_MODEL") or
            self.config.get("model") or
            "glm-4.7"
        )
        self.min_confidence = self.config.get("min_confidence", 0.3)
        self.max_patterns = self.config.get("max_patterns", 10)
        self.mode = self.config.get("mode", "enhance")
        # Temperature for LLM (default 0.7 for focused, consistent responses)
        self.temperature = self.config.get("temperature", 0.7)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Enrich response using LLM."""
        patterns = response_data.get("patterns", [])
        query = response_data.get("query", "")
        confidence = response_data.get("confidence", 0.0)

        # Decide whether to use LLM based on mode and confidence
        use_llm = self._should_use_llm(patterns, confidence)

        if not use_llm:
            # Skip LLM enrichment
            return response_data

        # Check if this is a creative query (write, create, make, generate)
        # For creative queries, use direct prompt without pattern context
        creative_keywords = ["write", "create", "make", "generate", "compose", "draft", "author"]
        is_creative_query = any(keyword in query.lower() for keyword in creative_keywords)

        # DEBUG: Log the decision
        print(f"  [LLMEnricher] Query: '{query[:50]}...', creative={is_creative_query}, patterns={len(patterns)}")

        # Generate LLM response
        if is_creative_query and patterns:
            print(f"  [LLMEnricher] Using direct prompt (creative query)")
            # Use direct prompt for creative requests - don't distract with patterns
            llm_response = await self._call_llm(self._build_direct_prompt(query, context))
        else:
            print(f"  [LLMEnricher] Using pattern-based enhancement")
            # Use pattern-based enhancement for informational queries
            llm_response = await self._generate_llm_response(
                response_data,
                context,
                patterns
            )

        # Merge based on mode
        # For creative queries, always use llm_response to replace pattern-based content entirely
        if is_creative_query or self.mode == self.MODE_REPLACE:
            # Replace entire response with LLM output
            response_data["llm_response"] = llm_response
            response_data["llm_used"] = True
        elif self.mode == self.MODE_FALLBACK:
            # LLM as fallback when patterns are weak
            if confidence < self.min_confidence or not patterns:
                response_data["llm_fallback"] = llm_response
                response_data["llm_used"] = True
        else:  # enhance (informational queries)
            # Add LLM enhancement to existing response
            response_data["llm_enhancement"] = llm_response
            response_data["llm_used"] = True

        return response_data

    def _should_use_llm(self, patterns: List, confidence: float) -> bool:
        """Decide whether to use LLM based on mode and confidence."""
        if self.mode == self.MODE_REPLACE:
            return True  # Always use LLM
        elif self.mode == self.MODE_FALLBACK:
            # Only use LLM if no patterns found (auto-fallback)
            # If patterns exist, confirmation will be handled in enrich() method
            result = not patterns
            return result
        else:  # enhance
            # Use LLM to enhance, but still use patterns
            return True

    async def _generate_llm_response(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext,
        patterns: List
    ) -> str:
        """Generate LLM response based on query and patterns."""
        query = response_data.get("query", "")
        specialist_id = response_data.get("specialist_id", "")

        # Build prompt based on mode and available patterns
        if patterns and self.mode != self.MODE_REPLACE:
            prompt = self._build_enhancement_prompt(query, patterns, specialist_id, context)
        else:
            prompt = self._build_direct_prompt(query, context)

        # Call LLM API
        try:
            response = await self._call_llm(prompt)
            return response
        except Exception as e:
            # Return error message if LLM fails
            return f"[LLM Error: {str(e)}]"

    def _clean_pattern_text(self, text: str) -> str:
        """Remove Source X references and other LLM artifacts from pattern text."""
        import re
        # Remove "Source X", "Source X:" references
        text = re.sub(r'\*\*Source \d+:\*\*', '', text)
        text = re.sub(r'\*\*Source \d+\*\*', '', text)
        text = re.sub(r'Source \d+:', '', text)
        text = re.sub(r'\(Source \d+\)', '', text)
        # Remove "According to Source X" phrases
        text = re.sub(r'According to \*\*Source \d+\*\*', 'According to', text)
        text = re.sub(r'According to Source \d+', 'According to', text)
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _build_enhancement_prompt(
        self,
        query: str,
        patterns: List,
        specialist_id: str,
        context: EnrichmentContext
    ) -> str:
        """Build prompt for LLM enhancement with pattern context."""
        domain_id = context.domain_id

        # Format patterns for prompt - clean up Source X references
        pattern_text = ""
        for i, pattern in enumerate(patterns[:self.max_patterns], 1):
            name = pattern.get("name", "Unknown")
            solution = pattern.get("solution", "")
            description = pattern.get("description", "")
            problem = pattern.get("problem", "")

            # Clean up Source X references from the content
            solution = self._clean_pattern_text(solution)
            description = self._clean_pattern_text(description)

            # Truncate solution if too long to avoid token limits
            if len(solution) > 1000:
                solution = solution[:1000] + "..."

            pattern_text += f"""
Pattern {i}: {name}
- Problem: {problem}
- Description: {description}
- Solution: {solution}
"""

        prompt = f"""You are a helpful AI assistant for the {domain_id} domain.

A user asked: "{query}"

We found {len(patterns)} relevant pattern(s) from our knowledge base:

{pattern_text}

Provide a comprehensive, helpful response:
1. Synthesize the key insights from these patterns
2. Keep it conversational and natural
3. Add relevant context and details when patterns are incomplete
4. Be thorough - don't cut short, provide complete information
5. Use markdown formatting for readability
6. **IMPORTANT**: Respond directly to the user's request. Do NOT include a "Patterns referenced" section or list patterns at the end - the user will see patterns separately if needed.

Provide your detailed response:"""

        return prompt

    def _build_direct_prompt(self, query: str, context: EnrichmentContext) -> str:
        """Build prompt for direct LLM response without pattern context."""
        # For creative queries, don't emphasize domain expertise - let the LLM be creative
        # Only mention domain if it provides useful context
        domain_id = context.domain_id

        prompt = f"""A user asked: "{query}"

Provide a creative, original response using markdown formatting:
- Be imaginative and original
- Follow the requested format or style precisely
- Don't reference other works or patterns unless explicitly asked
- Make it engaging and well-crafted

Your response:"""

        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM API."""
        if not self.api_key:
            return "[LLM not configured: No API key]"

        # Use httpx for async HTTP requests
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Determine if this is OpenAI or Anthropic-compatible API
        is_anthropic = "anthropic" in self.base_url.lower()

        if is_anthropic:
            # Anthropic/GLM API format (uses user role only)
            # For GLM models (glm-4.7, etc.), use model as-is
            model_name = self.model if self.model.startswith("glm-") else self.model.replace("gpt-", "claude-")
            payload = {
                "model": model_name,
                "max_tokens": 8192,  # Book chapter length responses
                "temperature": self.temperature,  # Control response randomness
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        else:
            # OpenAI API format
            payload = {
                "model": self.model,
                "max_tokens": 8192,  # Book chapter length responses
                "temperature": self.temperature,  # Control response randomness
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            }

        # Configure timeouts: 120s for read, 30s for connect, 30s for pool
        timeout = httpx.Timeout(
            timeout=120.0,      # Read timeout (increased from 60s)
            connect=30.0,     # Connection timeout
            pool=30.0          # Pool acquisition timeout
        )
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # Use correct endpoint based on API type
                if is_anthropic:
                    # Anthropic-compatible API uses /v1/messages endpoint
                    endpoint = f"{self.base_url.rstrip('/')}/v1/messages"
                else:
                    # OpenAI-compatible API uses /chat/completions endpoint
                    endpoint = f"{self.base_url.rstrip('/')}/chat/completions"

                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Debug: log raw response for troubleshooting
                print(f"  DEBUG: LLM API response keys: {list(data.keys())}")
                print(f"  DEBUG: LLM API response: {str(data)[:500]}")

                # Parse response based on API format
                # Try OpenAI format first (most common for proxy APIs)
                try:
                    # Handle Chinese API wrapper format (code, msg, success)
                    if "code" in data and "success" in data:
                        if data.get("success") or data.get("code") == 200 or data.get("code") == 0:
                            # Try to find actual content in nested data
                            if "data" in data:
                                inner_data = data["data"]
                                if isinstance(inner_data, dict):
                                    if "choices" in inner_data:
                                        return inner_data["choices"][0]["message"]["content"]
                                    elif "content" in inner_data:
                                        if isinstance(inner_data["content"], list):
                                            return inner_data["content"][0].get("text", inner_data["content"][0])
                                        return inner_data["content"]
                                    # Direct string in data field
                                    elif isinstance(inner_data, str):
                                        return inner_data
                                return str(inner_data)
                            elif "msg" in data and isinstance(data["msg"], str) and len(data["msg"]) > 20:
                                # Sometimes msg contains the actual response
                                return data["msg"]
                        return f"[LLM Error: API returned error - code: {data.get('code')}, msg: {data.get('msg')}]"

                    if "choices" in data:
                        return data["choices"][0]["message"]["content"]
                    elif "content" in data and isinstance(data["content"], list):
                        # Anthropic format or similar
                        return data["content"][0]["text"]
                    elif "content" in data and isinstance(data["content"], str):
                        # Direct content field
                        return data["content"]
                    else:
                        return f"[LLM Error: Unknown response format: {list(data.keys())}]"
                except (KeyError, IndexError, TypeError) as e:
                    return f"[LLM Error: Could not parse response - {str(e)}. Response keys: {list(data.keys())}]"
            except httpx.HTTPStatusError as e:
                # Try to get error details from response
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(error_data))
                except:
                    error_msg = e.response.text[:200] if e.response.text else "Unknown error"
                return f"[LLM HTTP Error: {e.response.status_code} - {error_msg}]"
            except httpx.RequestError as e:
                # Provide more detailed error information
                error_type = type(e).__name__
                error_details = str(e)
                if not error_details or error_details == str(type(e)):
                    error_details = "Connection failed - check API endpoint and network"
                return f"[LLM Request Error ({error_type}): {error_details}. API: {self.base_url}, Model: {self.model}]"
            except Exception as e:
                return f"[LLM Error: {str(e)}]"

    def get_supported_formats(self) -> List[str]:
        """Works with all formats - generates markdown text."""
        return []


class LLMFallbackEnricher(LLMEnricher):
    """
    LLM Enricher that only activates as a fallback.

    Only uses LLM when pattern confidence is below threshold.
    Useful for keeping fast pattern-based responses while having LLM safety net.

    Enhanced with Research Strategies:
    - Can search documents or internet for context before calling LLM
    - Configured via research_strategy in domain config

    Configuration:
        - mode: "fallback" (fixed)
        - research_strategy: Optional dict with 'type' and strategy-specific config
            Example:
            {
                'type': 'document',
                'documents': [
                    {'type': 'file', 'path': 'context.md'},
                    {'type': 'file', 'path': 'user-guide.md'}
                ],
                'base_path': '/path/to/project'
            }
            OR
            {
                'type': 'internet',
                'search_provider': 'auto'
            }
    """

    name = "LLM Fallback Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}

        # CONFIG OVERRIDE DETECTION: Log when hard-coded defaults override user config
        if "mode" in config and config["mode"] != "fallback":
            logger.warning(
                "[CONFIG] llm_enricher: hard-coded default 'mode=fallback' is overriding user config "
                f"'mode={config['mode']}'. User config value will be ignored."
            )
            print(
                f"  [CONFIG OVERRIDE WARNING] llm_enricher: hard-coded default 'mode=fallback' "
                f"is overriding user config 'mode={config['mode']}'"
            )

        config["mode"] = "fallback"
        super().__init__(config)

        # Require user confirmation before using LLM fallback (default: true)
        self.require_confirmation = config.get("require_confirmation", True)

        # Initialize research strategy if configured
        self.research_strategy = None
        research_config = config.get("research_strategy")

        if research_config:
            try:
                print(f"  [LLMFallbackEnricher] Initializing research strategy: {research_config.get('type')}")
                self.research_strategy = create_research_strategy(research_config)
            except Exception as e:
                print(f"  [LLMFallbackEnricher] Failed to initialize research strategy: {e}")

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Enrich using LLM with optional research strategy."""
        patterns = response_data.get("patterns", [])
        confidence = response_data.get("confidence", 0.0)

        # If user already confirmed LLM usage, execute directly
        if context.llm_confirmed:
            print(f"  [LLMFallbackEnricher] User confirmed LLM - executing directly")
            # Initialize research strategy if needed
            if self.research_strategy and not hasattr(self.research_strategy, '_initialized'):
                try:
                    await self.research_strategy.initialize()
                except Exception as e:
                    print(f"  [LLMFallbackEnricher] Failed to initialize research strategy: {e}")
                    self.research_strategy = None

            # Use research-enhanced prompt if strategy is available
            if self.research_strategy:
                llm_response = await self._generate_research_enhanced_response(
                    response_data,
                    context,
                    patterns
                )
            else:
                llm_response = await self._generate_llm_response(
                    response_data,
                    context,
                    patterns
                )

            response_data["llm_fallback"] = llm_response
            response_data["llm_used"] = True
            response_data["research_strategy_used"] = self.research_strategy is not None
            return response_data

        # Decide whether to use LLM based on mode and confidence
        use_llm = self._should_use_llm(patterns, confidence)

        # If patterns exist and confirmation is enabled, always offer choice
        # User sees results first, then decides whether to extend with LLM
        if self.require_confirmation and not context.llm_confirmed and patterns:
            # Return confirmation request with partial results
            print(f"  [LLMFallbackEnricher] Offering LLM extension choice (patterns: {len(patterns)})")
            response_data["requires_confirmation"] = True
            response_data["confirmation_message"] = "Would you like to extend your search beyond this local data?"
            response_data["partial_response"] = {
                "query": response_data.get("query"),
                "response": response_data.get("response") or response_data.get("raw_answer", "No detailed answer available."),
                "specialist": response_data.get("specialist_id"),
                "confidence": confidence,
                "patterns_used": patterns,
                "llm_used": False,
                "ai_generated": False
            }
            return response_data

        # No patterns found or confirmation disabled - auto-use LLM
        if not patterns:
            print(f"  [LLMFallbackEnricher] No patterns found - using LLM automatically")
            # Initialize research strategy if needed
            if self.research_strategy and not hasattr(self.research_strategy, '_initialized'):
                try:
                    await self.research_strategy.initialize()
                except Exception as e:
                    print(f"  [LLMFallbackEnricher] Failed to initialize research strategy: {e}")
                    self.research_strategy = None

            # Use research-enhanced prompt if strategy is available
            if self.research_strategy:
                llm_response = await self._generate_research_enhanced_response(
                    response_data,
                    context,
                    patterns
                )
            else:
                llm_response = await self._generate_llm_response(
                    response_data,
                    context,
                    patterns
                )

            response_data["llm_fallback"] = llm_response
            response_data["llm_used"] = True
            response_data["research_strategy_used"] = self.research_strategy is not None

        return response_data

    async def _generate_research_enhanced_response(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext,
        patterns: List
    ) -> str:
        """Generate LLM response with research context."""
        query = response_data.get("query", "")

        try:
            # Search for relevant context
            search_results = await self.research_strategy.search(query, limit=3)

            if search_results:
                # Build prompt with research context
                prompt = self._build_research_enhanced_prompt(
                    query,
                    search_results,
                    patterns,
                    context
                )
            else:
                # Fall back to standard prompt
                prompt = self._build_direct_prompt(query, context)

        except Exception as e:
            print(f"  [LLMFallbackEnricher] Research failed: {e}, using fallback")
            prompt = self._build_direct_prompt(query, context)

        # Call LLM
        return await self._call_llm(prompt)

    def _build_research_enhanced_prompt(
        self,
        query: str,
        search_results: List[SearchResult],
        patterns: List,
        context: EnrichmentContext
    ) -> str:
        """Build prompt with research context from documents or web search."""
        domain_id = context.domain_id

        # Format search results with meaningful source names
        research_context = ""
        for i, result in enumerate(search_results, 1):
            # Extract a meaningful source name from the file path
            source_name = result.source
            if '/' in source_name:
                source_name = source_name.split('/')[-1]  # Get filename
            # Remove file extension
            if '.' in source_name:
                source_name = source_name.rsplit('.', 1)[0]

            # Clean up the content to remove any Source X references
            content = self._clean_pattern_text(result.content[:500])

            research_context += f"""
From **{source_name}** (relevance: {result.relevance_score:.2f}):
{content}...
"""

        prompt = f"""You are a helpful AI assistant for the {domain_id} domain.

A user asked: "{query}"

We found the following relevant information from our documentation:

{research_context}

Use these search results to provide a clear, helpful answer:
1. Draw on the documentation results above
2. Add relevant context when needed
3. Cite documents using their actual names (e.g., "According to **README**..." or "As described in **user-guide**...")
4. NEVER use numbered references like "Source 1", "Source 2" - always use the document name
5. Use markdown formatting for readability

Provide your response:"""

        return prompt


class LLMSummarizerEnricher(LLMEnricher):
    """
    LLM Enricher that summarizes multiple patterns.

    When there are many patterns, uses LLM to create a coherent summary.
    """

    name = "LLM Summarizer Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}

        # CONFIG OVERRIDE DETECTION: Log when hard-coded defaults override user config
        if "mode" in config and config["mode"] != "enhance":
            logger.warning(
                "[CONFIG] llm_summarizer: hard-coded default 'mode=enhance' is overriding user config "
                f"'mode={config['mode']}'. User config value will be ignored."
            )
            print(
                f"  [CONFIG OVERRIDE WARNING] llm_summarizer: hard-coded default 'mode=enhance' "
                f"is overriding user config 'mode={config['mode']}'"
            )

        config["mode"] = "enhance"
        super().__init__(config)
        self.min_patterns_for_summary = self.config.get("min_patterns_for_summary", 3)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Only summarize if there are multiple patterns."""
        patterns = response_data.get("patterns", [])

        if len(patterns) < self.min_patterns_for_summary:
            # Not enough patterns to need summarization
            return response_data

        # Generate summary
        summary = await self._generate_summary(
            response_data.get("query", ""),
            patterns,
            context
        )

        response_data["llm_summary"] = summary
        response_data["llm_used"] = True

        return response_data

    async def _generate_summary(
        self,
        query: str,
        patterns: List,
        context: EnrichmentContext
    ) -> str:
        """Generate LLM summary of patterns."""
        domain_id = context.domain_id

        # Build patterns summary
        patterns_text = "\n\n".join([
            f"- {p.get('name', 'Unknown')}: {p.get('solution', p.get('description', ''))[:100]}"
            for p in patterns[:self.max_patterns]
        ])

        prompt = f"""Summarize these {len(patterns)} patterns for the query: "{query}"

Patterns:
{patterns_text}

Provide a concise 2-3 sentence summary that synthesizes the key insights."""

        try:
            return await self._call_llm(prompt)
        except Exception as e:
            return f"[Summary failed: {str(e)}]"


class LLMExplanationEnricher(LLMEnricher):
    """
    LLM Enricher that adds explanations to technical patterns.

    Great for code patterns, algorithms, and technical concepts.
    """

    name = "LLM Explanation Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.add_examples = self.config.get("add_examples", True)
        self.simplify_language = self.config.get("simplify_language", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Add LLM explanations to patterns."""
        patterns = response_data.get("patterns", [])

        if not patterns:
            return response_data

        # Add explanation to top pattern
        top_pattern = patterns[0]
        explanation = await self._generate_explanation(
            top_pattern,
            context
        )

        response_data["llm_explanation"] = explanation
        response_data["llm_used"] = True

        return response_data

    async def _generate_explanation(
        self,
        pattern: Dict,
        context: EnrichmentContext
    ) -> str:
        """Generate LLM explanation for a pattern."""
        name = pattern.get("name", "")
        solution = pattern.get("solution", "")
        problem = pattern.get("problem", "")

        instruction = "Explain this in simple terms for a beginner." if self.simplify_language else "Explain how this works."

        if self.add_examples:
            instruction += " Include a practical example."

        prompt = f"""{instruction}

Pattern: {name}
Problem: {problem}
Solution: {solution}

Your explanation:"""

        try:
            return await self._call_llm(prompt)
        except Exception as e:
            return f"[Explanation failed: {str(e)}]"
