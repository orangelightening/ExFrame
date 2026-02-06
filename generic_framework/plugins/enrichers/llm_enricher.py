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
        creative_keywords = ["write", "create", "make", "generate", "compose", "draft", "author", "poem", "haiku", "sonnet", "verse"]
        # Also check for patterns like "a poem about", "write me a poem", etc.
        query_lower = query.lower()
        is_creative_query = (
            any(keyword in query_lower for keyword in creative_keywords) or
            "poem about" in query_lower or
            "haiku about" in query_lower or
            "sonnet about" in query_lower or
            "verse about" in query_lower or
            "write me" in query_lower
        )

        # DEBUG: Log the decision
        print(f"  [LLMEnricher] Query: '{query[:50]}...', creative={is_creative_query}, patterns={len(patterns)}")

        # Generate LLM response
        if is_creative_query and patterns:
            print(f"  [LLMEnricher] Using direct prompt (creative query)")
            # Use direct prompt for creative requests - don't distract with patterns
            show_thinking = getattr(context, 'show_thinking', False)
            llm_response = await self._call_llm(self._build_direct_prompt(query, context), show_thinking)
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
            # Use LLM to enhance, but NOT if there are no patterns to work with
            # This prevents hallucination when no relevant content exists
            return bool(patterns)  # Only use LLM if we have patterns to enhance

    async def _generate_llm_response(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext,
        patterns: List
    ) -> str:
        """Generate LLM response based on query and patterns."""
        query = response_data.get("query", "")
        specialist_id = response_data.get("specialist_id", "")

        # Attach response_data to context for access in prompt builders
        # This allows prompt builders to access search_metadata
        context.response_data = response_data

        # Check if this is a Type 3 (document store) domain
        # Type 3 domains use exframe_specialist and have specific search metadata
        # We check domain type from context, not from response_data keys (which can be added by any enricher)
        domain_type = getattr(context, 'domain_type', None)
        is_type3_domain = (
            specialist_id == "exframe_specialist" or
            domain_type == "3" or
            response_data.get("search_strategy") == "research_primary"
        )

        # Check if we have web search results (research_results from Type 4 web search)
        research_results = response_data.get("research_results", [])
        # Differentiate Type 4 web search from Type 3 document search
        # Type 4 web search has results with "web_search" source or URLs
        # Type 3 document search has "Research Docs" source and no URLs
        has_web_search = (
            len(research_results) > 0 and
            not is_type3_domain and  # Not Type 3
            (response_data.get("search_strategy") != "research_primary") and
            (research_results[0].get("source") == "web_search" or research_results[0].get("url") if research_results else False)
        )

        # Check if this is Type 4 (Analytical Engine) with no web search and low-relevance local patterns
        # In this case, don't hallucinate - ask user to enable web search
        is_type4_domain = domain_type == "4"
        if is_type4_domain and not has_web_search and patterns:
            # Check relevance of local patterns
            max_relevance = max((p.get('confidence', p.get('relevance', p.get('_semantic_score', 0))) for p in patterns[:20]), default=0)

            # Check if patterns are from keyword search (low quality) vs semantic search
            has_keyword_only = any(p.get('_relevance_source') == 'keyword' for p in patterns[:10])

            # If relevance is low OR patterns are keyword-only matches, don't hallucinate
            if max_relevance < 0.5 or (has_keyword_only and max_relevance < 0.8):
                print(f"  [LLMEnricher] Type 4: Low relevance local patterns (max_relevance={max_relevance:.2f}, keyword_only={has_keyword_only})")
                # Build a prompt that tells LLM to request web search instead of hallucinating
                prompt = self._build_web_search_request_prompt(query, patterns, context, max_relevance, has_keyword_only)
                show_thinking = getattr(context, 'show_thinking', False)
                response = await self._call_llm(prompt, show_thinking)
                plugin_prefix = "\n\n---\n\n*Generated by LLMEnricher*"
                if not response.endswith(plugin_prefix):
                    response = response + plugin_prefix
                return response

        # Build prompt based on mode and available patterns
        if has_web_search:
            # Use web search results as context
            print(f"  [LLMEnricher] Using web search results ({len(research_results)} results)")
            prompt = self._build_web_search_prompt(query, research_results, patterns, context)
        elif is_type3_domain and patterns:
            # Use document-context prompt for Type 3 document search results
            print(f"  [LLMEnricher] Using Type 3 document context prompt ({len(patterns)} documents)")

            # PRE-LLM RELEVANCE CHECK: Don't answer if no relevant documents found
            max_relevance = max((p.get('confidence', p.get('relevance', 0)) for p in patterns[:20]), default=0)

            # Check total_files from search metadata to understand search scope
            search_metadata = response_data.get('search_metadata', {})
            total_files = search_metadata.get('total_files', 0)
            matches = search_metadata.get('matches', len(patterns))

            # If relevance is very low AND we searched many files with few matches, reject
            if max_relevance < 0.3 and total_files > 10 and matches < 3:
                no_info_msg = f"I don't have information about '{query}' in the ExFrame documentation. I searched through {total_files} files but found no relevant content. I can only answer questions about ExFrame's architecture, configuration, plugin system, and usage."
                print(f"  [LLMEnricher] No relevant docs found (max_relevance={max_relevance:.2f}, files={total_files}, matches={matches})")
                return no_info_msg

            prompt = self._build_document_context_prompt(query, patterns, context)
        elif patterns and self.mode != self.MODE_REPLACE:
            # Use pattern-based enhancement for local patterns
            prompt = self._build_enhancement_prompt(query, patterns, specialist_id, context)
        else:
            # No patterns available - for Type 3, this means document search found nothing
            if is_type3_domain:
                no_info_msg = f"I don't have information about '{query}' in the ExFrame documentation. I can only answer questions about ExFrame's architecture, configuration, plugin system, and usage."
                print(f"  [LLMEnricher] No patterns found for Type 3 query")
                return no_info_msg
            # Use direct prompt when no patterns or in replace mode
            prompt = self._build_direct_prompt(query, context)

        # Call LLM API
        try:
            show_thinking = getattr(context, 'show_thinking', False)
            response = await self._call_llm(prompt, show_thinking)

            # Add plugin identifier to response
            # This helps users identify which plugin generated the output
            plugin_prefix = "\n\n---\n\n*Generated by LLMEnricher*"
            if not response.endswith(plugin_prefix):
                response = response + plugin_prefix

            # Post-response analysis: Detect contradictions for Type 3 domains
            if is_type3_domain and patterns:
                await self._detect_and_log_contradictions(query, patterns, context)

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
        show_thinking = getattr(context, 'show_thinking', False)

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

        # Build reasoning section if show_thinking is enabled
        if show_thinking:
            reasoning_section = """
**IMPORTANT - Show your reasoning process:**

Please show your step-by-step reasoning before giving the final answer:
1. First, explain what patterns are relevant and why
2. Walk through how the pattern information addresses the question
3. Show your analysis and synthesis of the information
4. Then provide your final, comprehensive answer

Your response structure:
- **Reasoning:** [Your step-by-step analysis of what the patterns say and how it answers the question]
- **Answer:** [Your final answer]

"""
        else:
            reasoning_section = ""

        prompt = f"""You are a helpful AI assistant for the {domain_id} domain.

A user asked: "{query}"

We found {len(patterns)} relevant pattern(s) from our knowledge base:

{pattern_text}
{reasoning_section}Format your answer to:
- Synthesize key insights from these patterns
- Keep it conversational and natural
- Add relevant context and details when patterns are incomplete
- Be thorough - provide complete information
- Use markdown formatting for readability
- Respond directly to the user's request (do not list patterns at the end)

Your response:"""

        return prompt

    def _build_direct_prompt(self, query: str, context: EnrichmentContext) -> str:
        """Build prompt for direct LLM response without pattern context."""
        # For creative queries, don't emphasize domain expertise - let the LLM be creative
        # Only mention domain if it provides useful context
        domain_id = context.domain_id
        show_thinking = getattr(context, 'show_thinking', False)

        # Build reasoning section if show_thinking is enabled
        if show_thinking:
            reasoning_section = """
**IMPORTANT - Show your reasoning process:**

Please show your step-by-step reasoning before giving your final response:
1. First, explain your understanding of what's being asked
2. Walk through your thought process and approach
3. Show your analysis or planning
4. Then provide your final, creative response

Your response structure:
- **Reasoning:** [Your step-by-step thought process]
- **Response:** [Your final creative output]

"""
        else:
            reasoning_section = ""

        prompt = f"""A user asked: "{query}"
{reasoning_section}Format your response to:
- Be imaginative and original
- Follow the requested format or style precisely
- Don't reference other works or patterns unless explicitly asked
- Make it engaging and well-crafted
- Use markdown formatting for readability

Your response:"""

        return prompt

    def _build_document_context_prompt(
        self,
        query: str,
        patterns: List,
        context: EnrichmentContext
    ) -> str:
        """Build prompt with document context for Type 3 (Document Store) domains.

        Unlike the enhancement prompt, this doesn't ask the LLM to list patterns.
        The LLM should use the documents as context to answer naturally.

        Includes citation requirements for Type 3 (Document Store Search) domains.
        """
        domain_id = context.domain_id
        show_thinking = getattr(context, 'show_thinking', False)

        # Get search metadata if available (passed from specialist via engine)
        response_data = getattr(context, 'response_data', {})
        search_metadata = response_data.get('search_metadata', {})

        # Extract search scope for citation context
        total_files = search_metadata.get('total_files', 0)
        matches = search_metadata.get('matches', len(patterns))
        files_checked = f"{total_files} files" if total_files > 0 else "project files"

        # Format documents as context (not as patterns to be listed)
        # Use the document content directly to provide context
        context_text = ""
        for i, doc in enumerate(patterns[:self.max_patterns], 1):
            # For document results, use the content field
            content = doc.get("content", doc.get("solution", ""))
            title = doc.get("title", doc.get("name", "Document"))

            # Clean up any existing source references
            content = self._clean_pattern_text(content)

            # Truncate if too long
            if len(content) > 1500:
                content = content[:1500] + "..."

            context_text += f"""
--- Document {i}: {title} ---
{content}
---
"""

        # Build citation requirements for Type 3 domains
        citation_requirements = """
**IMPORTANT CITATION REQUIREMENTS:**
- When answering questions about this codebase, ALWAYS cite specific files when making factual claims
- Use the format: "According to [filename]: [fact]"
- For code behavior: reference the actual file/function names
- If information spans multiple files, cite all relevant sources
- If uncertain about information, acknowledge which files you checked and what you couldn't find
"""

        # Add scope boundaries for Type 3 domains (especially ExFrame)
        scope_boundaries = """
**SCOPE BOUNDARIES:**
You are an ExFrame expert. Answer ONLY questions about:
- ExFrame architecture and design
- Plugin system (Router, Specialist, Enricher, Formatter)
- Domain types 1-5 and their configurations
- Configuration and setup
- API endpoints and usage
- Universe and domain management
- Pattern-based knowledge
- Semantic search
- Self-healing features
- Citation requirements
- Docker deployment

**OUT OF SCOPE** (do not answer these):
- General Python questions (syntax, language features)
- Other frameworks (Django, Flask, FastAPI internals)
- Infrastructure best practices (Docker, Kubernetes, networking)
- Business logic for specific domains (cooking, DIY, gardening)
- General software development questions
- AI/ML theory unrelated to ExFrame

If a question is clearly outside ExFrame's scope, respond: "This question is outside ExFrame's documentation scope. I can only answer questions about ExFrame's architecture, configuration, plugin system, and usage."
"""

        # Add search context if available
        search_context = f"\n**Search Context:** I searched through {files_checked} and found {matches} relevant document(s)." if total_files > 0 else ""

        # Build reasoning section if show_thinking is enabled
        if show_thinking:
            reasoning_section = """
**IMPORTANT - Show your reasoning process:**

Please show your step-by-step reasoning before giving the final answer:
1. First, explain what you're looking for and what information you found in the documents
2. Walk through how the document content addresses the question
3. Show your analysis of the information
4. Then provide your final, comprehensive answer

Your response structure:
- **Reasoning:** [Your step-by-step analysis of what the documents say and how it answers the question]
- **Answer:** [Your final answer with proper citations]

"""
        else:
            reasoning_section = ""

        prompt = f"""You are a helpful AI assistant with access to documentation.

A user asked: "{query}"
{search_context}

{scope_boundaries}

Here are the relevant documents from our knowledge base:

{context_text}

{citation_requirements}
{reasoning_section}Format your answer to include:
- Specific details drawn from the document content
- Citations using the format: "According to [filename]: [fact]"
- Markdown formatting for readability (headers, bullet points, etc.)
- Do NOT include a "Sources" or "References" section at the end

Your response:"""

        return prompt

    def _build_web_search_prompt(
        self,
        query: str,
        research_results: List[Dict],
        local_patterns: List,
        context: EnrichmentContext
    ) -> str:
        """Build prompt with web search results context.

        Web search results provide fresh, external information that should
        be used as the primary source for answering.
        """
        domain_id = context.domain_id
        show_thinking = getattr(context, 'show_thinking', False)

        # Format web search results as context
        web_context = ""
        for i, result in enumerate(research_results[:10], 1):
            title = result.get("title", "Untitled")
            content = result.get("content", "")
            url = result.get("source", "")

            # Clean up content
            content = self._clean_pattern_text(content)

            # Truncate if too long
            if len(content) > 800:
                content = content[:800] + "..."

            web_context += f"""
--- Web Result {i}: {title} ---
{content}
Source: {url}
---
"""

        # Add note about local patterns if they exist
        local_note = ""
        if local_patterns:
            local_note = f"""

Note: We also have {len(local_patterns)} local patterns that may provide additional context, but prioritize the web search results above as they contain fresher, more specific information for this query.
"""

        # Build reasoning section if show_thinking is enabled
        if show_thinking:
            reasoning_section = """
**IMPORTANT - Show your reasoning process:**

Please show your step-by-step reasoning before giving your final answer:
1. First, explain what you found in the web search results
2. Walk through how the search results address the question
3. Show your analysis and synthesis of the information
4. Then provide your final, comprehensive answer

Your response structure:
- **Reasoning:** [Your step-by-step analysis of what the web results say and how it answers the question]
- **Answer:** [Your final answer with source URLs]

"""
        else:
            reasoning_section = ""

        prompt = f"""You are a helpful AI assistant with access to web search results.

A user asked: "{query}"

Here are the relevant web search results:

{web_context}{local_note}
{reasoning_section}Format your answer to:
- Draw primarily from the web search results (they are fresh and specific to this query)
- Organize the information in a natural, conversational way
- Include specific details, URLs, and information from the web results
- If multiple results are relevant, synthesize them into a coherent answer
- Use markdown formatting for readability (headers, bullet points, links)
- When mentioning information, cite the source URLs

Your response:"""

        return prompt

    def _build_web_search_request_prompt(
        self,
        query: str,
        local_patterns: List,
        context: EnrichmentContext,
        max_relevance: float,
        has_keyword_only: bool
    ) -> str:
        """Build prompt that requests web search instead of hallucinating.

        For Type 4 domains when local patterns are irrelevant, tell LLM to request web search.

        Args:
            query: User's question
            local_patterns: Local patterns that were found (but irrelevant)
            context: Enrichment context
            max_relevance: Highest relevance score among patterns
            has_keyword_only: Whether patterns are from keyword-only search

        Returns:
            Prompt that tells LLM to request web search
        """
        domain_id = context.domain_id
        show_thinking = getattr(context, 'show_thinking', False)

        # Explain why local patterns aren't sufficient
        reason = ""
        if has_keyword_only:
            reason = f"I found {len(local_patterns)} local patterns matching keywords, but they don't seem directly relevant to your specific question about '{query[:50]}...'. The patterns appear to be general matches rather than specific answers."
        else:
            reason = f"I found {len(local_patterns)} local patterns, but their relevance score is low ({max_relevance:.1%}), suggesting they don't directly answer your question."

        # Build reasoning section if show_thinking is enabled
        if show_thinking:
            reasoning_section = """
**IMPORTANT - Show your reasoning process:**

Please show your step-by-step reasoning:
1. First, explain what local information was found
2. Explain why the local patterns aren't sufficient to answer this specific question
3. Recommend using web search to get a proper answer
4. Then provide your response

Your response structure:
- **Reasoning:** [Your analysis of the local patterns and why web search is needed]
- **Response:** [Your request for the user to enable web search]

"""
        else:
            reasoning_section = ""

        prompt = f"""You are a helpful AI assistant for the {domain_id} domain with access to a knowledge base of patterns and web search.

A user asked: "{query}"

{reason}

You DO NOT have access to web search right now - it must be manually enabled by the user.

**IMPORTANT:** Do NOT hallucinate, make up, or guess an answer. If you don't have specific, relevant information from the local patterns, tell the user you need them to enable web search.

{reasoning_section}Format your response to:
- Acknowledge what the user is asking for
- Explain that the local patterns don't contain the specific information they need
- Ask them to click "Extended Search (Internet)" to search the web for a proper answer
- Be helpful but honest about not having the information locally
- Do NOT provide a recipe, instructions, or specific information unless it's directly from the local patterns

Your response:"""

        return prompt

    async def _call_llm(self, prompt: str, show_thinking: bool = False) -> str:
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

        # Debug: Log temperature being used
        print(f"  [LLMEnricher] Using model={self.model}, temperature={self.temperature}")

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
            # OpenAI API format - conditional system message
            system_message = "You are a helpful assistant."
            if show_thinking:
                system_message += " Always show your step-by-step reasoning before providing your final answer."
            payload = {
                "model": self.model,
                "max_tokens": 8192,  # Book chapter length responses
                "temperature": self.temperature,  # Control response randomness
                "messages": [
                    {"role": "system", "content": system_message},
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

    async def _detect_and_log_contradictions(
        self,
        query: str,
        patterns: List,
        context: EnrichmentContext
    ) -> None:
        """Analyze documents for contradictions and log findings.

        This runs as a post-response analysis for Type 3 domains to identify:
        - Direct contradictions between documents
        - Ambiguous or conflicting information
        - Outdated content that conflicts with other docs

        Results are logged with severity levels:
        - high: flag_for_immediate_review - Could cause incorrect answers
        - medium: schedule_cleanup - Creates ambiguity but answers still valid
        - low: log_only - Minor inconsistency in terminology
        """
        import json
        from pathlib import Path
        from datetime import datetime

        # Skip if no patterns to analyze
        if not patterns:
            return

        # First, extract annotation context from the documentation
        # Annotations provide historical context, known issues, and superseded systems
        # Look for: <!-- HISTORICAL NOTE -->, <!-- SUPERSEDED -->, <!-- CONTRADICTION -->
        # IMPORTANT: Search ALL documents for annotation markers
        annotation_context = ""
        for doc in patterns:
            title = doc.get("title", doc.get("name", ""))
            content = doc.get("content", doc.get("solution", ""))

            # Look for annotation markers or historical context
            if any(marker in content for marker in [
                "<!-- HISTORICAL NOTE",
                "<!-- SUPERSEDED",
                "Historical Nomenclature",
                "EEFrame → ExFrame",
                "nomenclature"
            ]):
                # Extract a substantial excerpt (up to 2000 chars to include full context)
                annotation_context = content[:2000]
                annotation_context = f"\n*** ANNOTATION CONTEXT (from {title}) ***\n{annotation_context}\n***\n"
                print(f"  [LLMEnricher] Found annotation context in: {title}")
                break

        # Build contradiction detection prompt
        # Limit to top 20 documents to avoid token limits
        docs_to_analyze = patterns[:20]

        doc_summary = ""
        for i, doc in enumerate(docs_to_analyze, 1):
            title = doc.get("title", doc.get("name", "Unknown"))
            content = doc.get("content", doc.get("solution", ""))[:500]  # First 500 chars
            doc_summary += f"\n--- Document {i}: {title} ---\n{content}...\n"

        contradiction_prompt = f"""You are a documentation quality analyst. Analyze these documents for contradictions, ambiguities, or inconsistencies.

{annotation_context}

Query: "{query}"

Documents:
{doc_summary}

*** IMPORTANT INSTRUCTIONS: If there is an annotation context section above, read it carefully: ***

1. HISTORICAL NAMES (EEFrame, omv-copilot, eeframe-app, eeframe-*) are INTENTIONAL and should NOT be flagged.

2. Service/container names (e.g., 'eeframe-app' in docker-compose.yml) are INTERNAL infrastructure plumbing for:
   - Docker volumes and data preservation
   - Git history continuity
   - Deployment stability
   These DO NOT affect end users and should NOT be compared to package names.

3. Package names (e.g., 'exframe' in pyproject.toml) are for USER-FACING installs (pip install).
   This is the correct public name and should NOT be changed to match internal service names.

4. DO NOT flag differences between internal infrastructure names (service names, container names, volume names) and public-facing names (package name, documentation) as contradictions.

5. Only flag issues that represent ACTUAL conflicts or unclear documentation that would confuse users.

Identify and categorize any issues found. Respond ONLY in valid JSON format with this structure:
{{
  "contradictions_found": true,
  "issues": [
    {{
      "type": "direct_contradiction|ambiguity|outdated_info|terminology_mismatch",
      "severity": "high|medium|low",
      "action": "flag_for_immediate_review|schedule_cleanup|log_only",
      "impact": "Brief description of impact",
      "files": ["file1.md", "file2.md"],
      "description": "Clear explanation of the contradiction",
      "suggestion": "How to fix it (optional)"
    }}
  ]
}}

Severity guidelines:
- high: Direct contradictions that could cause incorrect answers - action: flag_for_immediate_review
- medium: Ambiguous information where answers are still valid but unclear - action: schedule_cleanup
- low: Minor terminology inconsistencies that don't affect accuracy - action: log_only

If no contradictions found, respond with:
{{"contradictions_found": false, "issues": []}}

Your JSON response:"""

        try:
            # Call LLM for contradiction analysis
            analysis = await self._call_llm(contradiction_prompt)

            # Parse JSON response
            try:
                # Extract JSON from response (handle potential markdown code blocks)
                import re
                json_match = re.search(r'\{[\s\S]*\}', analysis)
                if json_match:
                    analysis_json = json.loads(json_match.group())
                else:
                    analysis_json = json.loads(analysis)

                # Only log if contradictions were found
                if not analysis_json.get("contradictions_found", False):
                    return

                issues = analysis_json.get("issues", [])
                if not issues:
                    return

                # Log the contradictions
                await self._log_contradictions(query, issues, context)

                # Log summary to console
                severity_counts = {"high": 0, "medium": 0, "low": 0}
                for issue in issues:
                    sev = issue.get("severity", "low")
                    if sev in severity_counts:
                        severity_counts[sev] += 1

                total = sum(severity_counts.values())
                print(f"  [ContradictionDetector] Found {total} issue(s): high={severity_counts['high']}, medium={severity_counts['medium']}, low={severity_counts['low']}")

            except json.JSONDecodeError as e:
                # Failed to parse JSON - log the raw response for debugging
                print(f"  [ContradictionDetector] Failed to parse analysis JSON: {e}")
                print(f"  [ContradictionDetector] Raw response: {analysis[:500]}")

        except Exception as e:
            # Don't fail the main response if contradiction detection fails
            print(f"  [ContradictionDetector] Analysis failed: {e}")

    async def _log_contradictions(
        self,
        query: str,
        issues: List[Dict[str, Any]],
        context: EnrichmentContext
    ) -> None:
        """Log contradictions to both plain text and JSON files."""
        import json
        from pathlib import Path
        from datetime import datetime

        # Create logs directory
        logs_dir = Path(__file__).parent.parent.parent / "logs" / "contradictions"
        logs_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().isoformat() + "Z"
        domain_id = context.domain_id

        # Prepare log entry
        log_entry = {
            "timestamp": timestamp,
            "domain": domain_id,
            "query": query,
            "issues": issues,
            "summary": {
                "total_issues": len(issues),
                "by_severity": {
                    "high": sum(1 for i in issues if i.get("severity") == "high"),
                    "medium": sum(1 for i in issues if i.get("severity") == "medium"),
                    "low": sum(1 for i in issues if i.get("severity") == "low")
                }
            }
        }

        # Write to JSON log (structured for analysis)
        json_log_path = logs_dir / "contradictions.json"
        try:
            # Read existing log or create new list
            if json_log_path.exists():
                with open(json_log_path, 'r') as f:
                    log_history = json.load(f)
            else:
                log_history = []

            # Append new entry (keep last 1000 entries)
            log_history.append(log_entry)
            if len(log_history) > 1000:
                log_history = log_history[-1000:]

            with open(json_log_path, 'w') as f:
                json.dump(log_history, f, indent=2)

        except Exception as e:
            print(f"  [ContradictionDetector] Failed to write JSON log: {e}")

        # Write to plain text log (human-readable)
        text_log_path = logs_dir / "contradictions.log"
        try:
            with open(text_log_path, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"DOMAIN: {domain_id}\n")
                f.write(f"QUERY: {query}\n")
                f.write(f"FOUND: {len(issues)} issue(s)\n")
                f.write(f"{'='*80}\n")

                for i, issue in enumerate(issues, 1):
                    severity = issue.get("severity", "unknown").upper()
                    action = issue.get("action", "unknown")
                    impact = issue.get("impact", "")
                    files = issue.get("files", [])
                    description = issue.get("description", "")

                    f.write(f"\n[Issue {i}] - Severity: {severity}\n")
                    f.write(f"  Action: {action}\n")
                    f.write(f"  Impact: {impact}\n")
                    f.write(f"  Files: {', '.join(files)}\n")
                    f.write(f"  Description: {description}\n")

                    if issue.get("suggestion"):
                        f.write(f"  Suggestion: {issue['suggestion']}\n")

        except Exception as e:
            print(f"  [ContradictionDetector] Failed to write text log: {e}")

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
        show_thinking = getattr(context, 'show_thinking', False)
        return await self._call_llm(prompt, show_thinking)

    def _build_research_enhanced_prompt(
        self,
        query: str,
        search_results: List[SearchResult],
        patterns: List,
        context: EnrichmentContext
    ) -> str:
        """Build prompt with research context from documents or web search."""
        domain_id = context.domain_id
        show_thinking = getattr(context, 'show_thinking', False)

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

        # Build reasoning section if show_thinking is enabled
        if show_thinking:
            reasoning_section = """
**IMPORTANT - Show your reasoning process:**

Please show your step-by-step reasoning before giving your final answer:
1. First, explain what you found in the documentation
2. Walk through how the documentation addresses the question
3. Show your analysis and synthesis of the information
4. Then provide your final, comprehensive answer

Your response structure:
- **Reasoning:** [Your step-by-step analysis of what the documents say and how it answers the question]
- **Answer:** [Your final answer with document citations]

"""
        else:
            reasoning_section = ""

        prompt = f"""You are a helpful AI assistant for the {domain_id} domain.

A user asked: "{query}"

We found the following relevant information from our documentation:

{research_context}
{reasoning_section}Format your answer to:
- Draw on the documentation results above
- Add relevant context when needed
- Cite documents using their actual names (e.g., "According to **README**..." or "As described in **user-guide**...")
- NEVER use numbered references like "Source 1", "Source 2" - always use the document name
- Use markdown formatting for readability

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
