"""
Generic Assistant Engine - Domain-agnostic query processing.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import json
import logging
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup query trace logging
TRACE_DIR = Path(__file__).parent.parent / "logs" / "traces"
TRACE_DIR.mkdir(parents=True, exist_ok=True)

trace_handler = logging.FileHandler(TRACE_DIR / "queries.log")
trace_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
trace_logger = logging.getLogger('query_trace')
trace_logger.addHandler(trace_handler)
trace_logger.setLevel(logging.INFO)

# Setup LLM usage logging for risk tracking
llm_handler = logging.FileHandler(TRACE_DIR / "llm_usage.log")
llm_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
llm_logger = logging.getLogger('llm_usage')
llm_logger.addHandler(llm_handler)
llm_logger.setLevel(logging.INFO)

# Setup general logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from core.domain import Domain
from core.knowledge_base import KnowledgeBaseConfig
from knowledge.json_kb import JSONKnowledgeBase


class GenericAssistantEngine:
    """
    Domain-agnostic assistant engine.

    Orchestrates query processing across specialists and knowledge base.
    Works with any domain that implements the Domain interface.
    """

    def __init__(
        self,
        domain: Domain,
        llm_client: Optional[Any] = None,
        enable_tracing: bool = True
    ):
        """
        Initialize the assistant engine.

        Args:
            domain: Domain instance (CookingDomain, PythonDomain, etc.)
            llm_client: Optional LLM client for advanced processing
            enable_tracing: Whether to collect detailed trace information
        """
        self.domain = domain
        self.llm_client = llm_client
        self.knowledge_base: Optional[JSONKnowledgeBase] = None
        self.query_history: List[Dict[str, Any]] = []
        self.enable_tracing = enable_tracing
        self.trace_log: List[Dict[str, Any]] = []

    async def initialize(self) -> None:
        """Initialize the engine and domain."""
        # Initialize domain
        await self.domain.initialize()

        # Initialize knowledge base
        kb_config = KnowledgeBaseConfig(
            storage_path=self.domain.config.pattern_storage_path,
            pattern_format=self.domain.config.pattern_format,
            pattern_schema=self.domain.config.pattern_schema
        )
        self.knowledge_base = JSONKnowledgeBase(kb_config)
        await self.knowledge_base.load_patterns()

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        include_trace: bool = False,
        llm_confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query.

        Args:
            query: User's question or request
            context: Optional additional context (may include llm_confirmed)
            include_trace: Whether to include detailed processing trace
            llm_confirmed: Whether user has confirmed LLM fallback usage

        Returns:
            Response dictionary with answer, sources, and metadata
        """
        # Extract llm_confirmed from context if provided there
        if context and isinstance(context, dict):
            llm_confirmed = context.get('llm_confirmed', llm_confirmed)

        # Check for direct prompt bypass (// prefix)
        # Trim whitespace first to handle " // query" cases
        direct_prompt = False
        actual_query = query
        trimmed_query = query.strip()
        if trimmed_query.startswith('//'):
            direct_prompt = True
            # Strip the // prefix and any following space from trimmed version
            actual_query = trimmed_query[2:].lstrip()
            logger.info(f"Direct prompt detected: '{actual_query}' (bypassing pattern search and specialist)")

        start_time = datetime.utcnow()
        trace = {
            'query': actual_query,
            'original_query': query,  # Keep original for reference
            'start_time': start_time.isoformat(),
            'steps': []
        } if self.enable_tracing else None

        # Handle direct prompt - skip to LLM directly
        if direct_prompt:
            return await self._process_direct_prompt(actual_query, query, start_time, trace)

        # Step 1: Select appropriate specialist
        step1_time = datetime.utcnow()
        specialist = self.domain.get_specialist_for_query(query)

        # Collect specialist scoring info
        specialist_scores = []
        for spec_id in self.domain.list_specialists():
            spec = self.domain.get_specialist(spec_id)
            if spec:
                score = spec.can_handle(query)
                specialist_scores.append({
                    'specialist': spec_id,
                    'name': spec.name,
                    'score': score
                })

        if trace:
            trace['steps'].append({
                'step': 1,
                'action': 'specialist_selection',
                'timestamp': step1_time.isoformat(),
                'selected': specialist.specialist_id if specialist else None,
                'all_scores': sorted(specialist_scores, key=lambda x: x['score'], reverse=True)
            })

        # Step 2: Search knowledge base for relevant patterns
        # Always do a full search - exact_only is too restrictive
        step2_time = datetime.utcnow()
        patterns = await self.knowledge_base.search(query, limit=10)

        if trace:
            trace['steps'].append({
                'step': 2,
                'action': 'knowledge_search',
                'timestamp': step2_time.isoformat(),
                'patterns_found': len(patterns),
                'patterns': [
                    {
                        'id': p.get('id'),
                        'name': p.get('name'),
                        'type': p.get('pattern_type'),
                        'relevance': p.get('_semantic_score', p.get('confidence', 0)),  # Use semantic score if available
                        'relevance_source': p.get('_relevance_source', 'unknown')
                    }
                    for p in patterns
                ]
            })

        # Step 3: Process query through specialist or general processing
        step3_time = datetime.utcnow()
        if specialist:
            # Pass pre-found patterns to specialist via context
            specialist_context = context or {}
            specialist_context['prematched_patterns'] = patterns
            response_data = await specialist.process_query(query, specialist_context)
            response = specialist.format_response(response_data)
            specialist_id = specialist.specialist_id
            processing_method = 'specialist'
        else:
            # General query processing
            response_data = await self._general_processing(query, patterns, context)
            response = self._format_general_response(response_data)
            specialist_id = None
            processing_method = 'general'

        if trace:
            trace['steps'].append({
                'step': 3,
                'action': 'response_generation',
                'timestamp': step3_time.isoformat(),
                'method': processing_method,
                'specialist': specialist_id,
                'patterns_used': len(response_data.get('patterns', patterns))
            })

        # Step 3.5: Apply enrichers (LLM fallback, quality scores, etc.)
        enrich_time = datetime.utcnow()

        # Calculate confidence BEFORE enrichers (needed for partial responses)
        confidence = self._calculate_confidence(patterns, specialist, query)

        # Prepare response data for enrichers
        enricher_input = {
            'query': query,
            'patterns': patterns,
            'response': response,
            'confidence': confidence,  # Include calculated confidence
            'specialist_id': specialist_id,
            'processing_method': processing_method
        }

        # Initialize enriched_data to avoid undefined variable
        enriched_data = {}

        # Call domain enrichers with EnrichmentContext
        try:
            # Import and create EnrichmentContext with llm_confirmed flag
            from core.enrichment_plugin import EnrichmentContext
            enrichment_context = EnrichmentContext(
                domain_id=self.domain.domain_id,
                specialist_id=specialist_id,
                query=query,
                knowledge_base=self.knowledge_base,
                llm_confirmed=llm_confirmed
            )
            enriched_data = await self.domain.enrich(enricher_input, enrichment_context)

            # Update response and result with enriched data
            if enriched_data.get('llm_used'):
                # LLM was used as fallback or enhancement
                if 'llm_fallback' in enriched_data:
                    # LLM fallback response
                    response = enriched_data['llm_fallback']
                    result_key = 'llm_fallback'
                elif 'llm_enhancement' in enriched_data:
                    # LLM enhancement to existing response
                    response = enriched_data.get('response', response)
                    if enriched_data.get('llm_enhancement'):
                        response += f"\n\n---\n\n{enriched_data['llm_enhancement']}"
                    result_key = 'llm_enhancement'
                elif 'llm_response' in enriched_data:
                    # LLM replaced response
                    response = enriched_data['llm_response']
                    result_key = 'llm_response'
                else:
                    pass  # llm_used=True but no response key found

                # Add LLM metadata to result
                enricher_input['llm_used'] = True
                if result_key:
                    enricher_input[result_key] = enriched_data.get(result_key)
            else:
                # No LLM used, but check if enricher modified response
                if 'response' in enriched_data:
                    response = enriched_data['response']

        except Exception as e:
            print(f"Warning: Enrichment failed: {e}")
            import traceback
            traceback.print_exc()
            # Continue without enrichment if it fails

        # Step 4: Record query for learning
        await self._record_query(query, response, specialist_id, patterns)

        end_time = datetime.utcnow()
        # Confidence was already calculated above (before enrichers)

        result = {
            'query': query,
            'response': response,
            'specialist': specialist_id,
            'patterns_used': [p.get('id', p.get('name', '')) for p in patterns],
            'confidence': confidence,
            'timestamp': end_time.isoformat(),
            'engine': 'GenericAssistantEngine',
            'domain': self.domain.domain_id,
            'processing_time_ms': int((end_time - start_time).total_seconds() * 1000)
        }

        # Add enriched data to result
        if enriched_data.get('llm_used'):
            result['llm_used'] = True
            for key in ['llm_fallback', 'llm_enhancement', 'llm_response']:
                if key in enriched_data:
                    result[key] = enriched_data[key]

        # Add confirmation data to result if user confirmation is required
        if enriched_data.get('requires_confirmation'):
            result['requires_confirmation'] = enriched_data['requires_confirmation']
            result['confirmation_message'] = enriched_data.get('confirmation_message')
            result['partial_response'] = enriched_data.get('partial_response')

            # Reduce confidence when confirmation is pending (user hasn't seen LLM yet)
            result['confidence'] = min(confidence * 0.7, 0.7)

        # Save LLM response as candidate pattern for future learning
        # This happens regardless of confirmation - whenever LLM is used, we create a pattern
        if enriched_data.get('llm_used'):
            # Extract LLM response text
            llm_response_text = None
            if 'llm_fallback' in enriched_data:
                llm_response_text = enriched_data['llm_fallback']
            elif 'llm_enhancement' in enriched_data:
                llm_response_text = enriched_data['llm_enhancement']
            elif 'llm_response' in enriched_data:
                llm_response_text = enriched_data['llm_response']

            if llm_response_text:
                # Check if research strategy was used (for auto-certification)
                research_strategy_used = enriched_data.get('research_strategy_used', False)

                # Log LLM usage for risk tracking
                llm_log_entry = {
                    'timestamp': end_time.isoformat(),
                    'domain': self.domain.domain_id,
                    'query': query,
                    'specialist': specialist_id,
                    'patterns_found': len(patterns),
                    'confidence': confidence,
                    'llm_used': True,
                    'llm_response_type': [k for k in ['llm_fallback', 'llm_enhancement', 'llm_response'] if k in enriched_data],
                    'processing_time_ms': result['processing_time_ms']
                }
                llm_logger.info(json.dumps(llm_log_entry))

                # NOTE: Auto-saving candidate patterns removed
                # Users now explicitly choose to accept patterns via "Accept as New Pattern" button
                # This puts human validation at the center of knowledge creation
                # Pattern creation happens through /api/patterns endpoint when user clicks accept

        # Add trace if requested
        if include_trace and trace:
            trace['end_time'] = end_time.isoformat()
            trace['total_time_ms'] = result['processing_time_ms']
            result['trace'] = trace
            self.trace_log.append(trace)

        # Log trace to file
        if trace and self.enable_tracing:
            trace['confidence'] = confidence
            trace['processing_method'] = processing_method
            trace_logger.info(json.dumps(trace))

        # Add AI-generated flag for risk tracking
        # Flag as AI-generated if LLM was used OR if any matched pattern is a candidate
        is_ai_generated = result.get('llm_used', False)
        if not is_ai_generated:
            # Check if any matched pattern is a candidate
            for pattern in patterns:
                if pattern.get('status') == 'candidate':
                    is_ai_generated = True
                    break
        result['ai_generated'] = is_ai_generated

        return result

    async def _general_processing(
        self,
        query: str,
        patterns: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process query without a specific specialist."""
        return {
            'query': query,
            'answer': self._synthesize_answer(query, patterns),
            'patterns': patterns,
            'suggestions': [p['name'] for p in patterns[:3]],
            'patterns_found': len(patterns)
        }

    @staticmethod
    def _clean_source_references(text: str) -> str:
        """Remove 'Source X' references from pattern text."""
        import re
        # Remove various Source X formats
        text = re.sub(r'\*\*Source \d+:\*\*', '', text)
        text = re.sub(r'\*\*Source \d+\*\*', '', text)
        text = re.sub(r'Source \d+:', '', text)
        text = re.sub(r'\(Source \d+\)', '', text)
        text = re.sub(r'According to \*\*Source \d+\*\*', 'According to', text)
        text = re.sub(r'According to Source \d+', 'According to', text)
        # Clean up extra whitespace and blank lines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def _synthesize_answer(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Synthesize answer from multiple patterns."""
        if not patterns:
            return ("I couldn't find specific information for your query. "
                   "Try rephrasing or being more specific.")

        # Use top pattern's solution
        top_pattern = patterns[0]

        if top_pattern.get('solution'):
            # Clean source references from the solution
            clean_solution = self._clean_source_references(top_pattern['solution'])
            answer = f"**{top_pattern['name']}**\n\n{clean_solution}"

            # Add steps if available
            if top_pattern.get('steps'):
                answer += "\n\n**Steps:**\n"
                for i, step in enumerate(top_pattern['steps'][:5], 1):
                    answer += f"{i}. {step}\n"

            # List all patterns used at the end
            if len(patterns) > 1:
                answer += f"\n\n---\n**Patterns referenced:**\n"
                for i, pattern in enumerate(patterns, 1):
                    answer += f"{i}. {pattern.get('name', 'Unknown')}\n"

            return answer

        return top_pattern.get('description', '')

    def _format_general_response(self, data: Dict[str, Any]) -> str:
        """Format general response for user."""
        return data.get('answer', '')

    def _calculate_confidence(
        self,
        patterns: List[Dict[str, Any]],
        specialist: Optional[Any],
        query: str = ""
    ) -> float:
        """
        Calculate overall confidence in the response.

        Confidence should reflect whether we actually have the answer,
        not just whether we found keyword matches.
        """
        if not patterns:
            return 0.0

        # Base confidence from pattern relevance scores
        pattern_confidence = sum(p.get('confidence', 0.5) for p in patterns) / len(patterns)

        # Check if query asks for specific factual information
        query_lower = query.lower()

        # Temperature queries
        temp_keywords = ['temperature', 'temp', 'degrees', '°f', '°c', 'fahrenheit', 'celsius', 'internal temp']
        # Time queries
        time_keywords = ['how long', 'time', 'minutes', 'hours', 'until', 'when']
        # Quantity/measurement queries
        quantity_keywords = ['how much', 'how many', 'amount', 'quantity', 'size', 'grams', 'ounces', 'cups', 'tablespoon']

        requires_specific = any(kw in query_lower for kw in temp_keywords + time_keywords + quantity_keywords)

        if requires_specific:
            # Check if patterns contain the specific information
            patterns_text = ' '.join(str(p.get('solution', '') + p.get('description', '')) for p in patterns)
            patterns_text_lower = patterns_text.lower()

            # For temperature queries, look for numbers with degree symbols or temp words
            if any(kw in query_lower for kw in temp_keywords):
                has_temp_info = any(
                    marker in patterns_text_lower
                    for marker in ['°', 'degree', 'fahrenheit', 'celsius', '165°', '170°', '175°', '180°', 'internal']
                )
                if not has_temp_info:
                    # Heavy penalty for missing temperature info
                    return max(pattern_confidence - 0.4, 0.1)

            # For time queries, look for time markers
            elif any(kw in query_lower for kw in time_keywords):
                has_time_info = any(
                    marker in patterns_text_lower
                    for marker in ['minutes', 'hours', 'until', 'when', 'until internal', 'about']
                )
                if not has_time_info:
                    return max(pattern_confidence - 0.3, 0.1)

            # For quantity queries, look for measurements
            elif any(kw in query_lower for kw in quantity_keywords):
                has_quantity = any(
                    marker in patterns_text_lower
                    for marker in ['cup', 'tablespoon', 'teaspoon', 'ounce', 'gram', 'pound', 'inch', '°']
                )
                if not has_quantity:
                    return max(pattern_confidence - 0.3, 0.1)

        # Moderate boost if specialist matched (reduced from 0.2 to 0.1)
        if specialist:
            return min(pattern_confidence + 0.1, 1.0)

        return pattern_confidence

    async def _record_query(
        self,
        query: str,
        response: str,
        specialist_id: Optional[str],
        patterns: List[Dict[str, Any]]
    ) -> None:
        """Record query for learning and analytics."""
        record = {
            'query': query,
            'response': response,
            'specialist': specialist_id,
            'patterns': [p.get('id', p.get('name', '')) for p in patterns],
            'timestamp': datetime.utcnow().isoformat()
        }
        self.query_history.append(record)

        # Update pattern access counts
        for pattern in patterns:
            pattern_id = pattern.get('id')
            if pattern_id:
                try:
                    await self.knowledge_base.record_feedback(
                        pattern_id,
                        {'accessed': True}
                    )
                except Exception:
                    pass  # Don't fail if recording fails

    async def _process_direct_prompt(
        self,
        actual_query: str,
        original_query: str,
        start_time: datetime,
        trace: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a direct prompt (// prefix) - bypass pattern search and specialist.

        Sends query directly to LLM without domain specialist persona wrapping.
        Uses the same API configuration as the LLM enricher.
        """
        import httpx
        import os

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        # Use same model priority as LLM enricher: LLM_MODEL env var > OPENAI_MODEL > default to glm-4.7
        model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or "glm-4.7"

        if not api_key:
            return {
                'query': actual_query,
                'original_query': original_query,
                'response': "[LLM not configured: No API key]",
                'specialist': None,
                'patterns_used': [],
                'confidence': 0.0,
                'timestamp': datetime.utcnow().isoformat(),
                'engine': 'GenericAssistantEngine',
                'domain': self.domain.domain_id,
                'processing_time_ms': 0,
                'direct_prompt': True,
                'llm_used': False,
                'error': True
            }

        # Record trace step for direct prompt
        if trace:
            trace['steps'].append({
                'step': 1,
                'action': 'direct_prompt_detected',
                'timestamp': datetime.utcnow().isoformat(),
                'bypassed': ['specialist_selection', 'pattern_search', 'domain_enrichment']
            })

        # Determine if this is OpenAI or Anthropic-compatible API
        is_anthropic = "anthropic" in base_url.lower()

        if is_anthropic:
            # Anthropic/GLM API format (uses user role only)
            model_name = model if model.startswith("glm-") else model.replace("gpt-", "claude-")
            payload = {
                "model": model_name,
                "max_tokens": 8192,
                "messages": [
                    {"role": "user", "content": actual_query}
                ]
            }
        else:
            # OpenAI API format
            payload = {
                "model": model,
                "max_tokens": 8192,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": actual_query}
                ]
            }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Use correct endpoint based on API type
        if is_anthropic:
            endpoint = f"{base_url.rstrip('/')}/v1/messages"
        else:
            endpoint = f"{base_url.rstrip('/')}/chat/completions"

        try:
            timeout = httpx.Timeout(60.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)

                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"Direct prompt LLM error: {error_text}")
                    return {
                        'query': actual_query,
                        'original_query': original_query,
                        'response': f"[LLM Error: {response.status_code} - {error_text}]",
                        'specialist': None,
                        'patterns_used': [],
                        'confidence': 0.0,
                        'timestamp': datetime.utcnow().isoformat(),
                        'engine': 'GenericAssistantEngine',
                        'domain': self.domain.domain_id,
                        'processing_time_ms': 0,
                        'direct_prompt': True,
                        'llm_used': True,
                        'error': True
                    }

                data = response.json()
                llm_response = data['content'][0]['text'] if is_anthropic else data['choices'][0]['message']['content']

                if trace:
                    trace['steps'].append({
                        'step': 2,
                        'action': 'llm_direct_call',
                        'timestamp': datetime.utcnow().isoformat(),
                        'model': model_name if is_anthropic else model,
                        'tokens_used': data.get('usage', {}).get('total_tokens', 0) if not is_anthropic else data.get('usage', {}).get('input_tokens', 0) + data.get('usage', {}).get('output_tokens', 0)
                    })

                end_time = datetime.utcnow()

                result = {
                    'query': actual_query,
                    'original_query': original_query,
                    'response': llm_response,
                    'specialist': None,
                    'patterns_used': [],
                    'confidence': 1.0,
                    'timestamp': end_time.isoformat(),
                    'engine': 'GenericAssistantEngine',
                    'domain': self.domain.domain_id,
                    'processing_time_ms': int((end_time - start_time).total_seconds() * 1000),
                    'direct_prompt': True,
                    'llm_used': True,
                    'llm_model': model_name if is_anthropic else model,
                    'processing_method': 'direct_prompt'
                }

                if trace:
                    result['trace'] = trace

                self.query_history.append({
                    'query': actual_query,
                    'original_query': original_query,
                    'response': llm_response,
                    'specialist': None,
                    'patterns': [],
                    'direct_prompt': True,
                    'timestamp': end_time.isoformat()
                })

                return result

        except httpx.RequestError as e:
            logger.error(f"Direct prompt request error: {e}")
            return {
                'query': actual_query,
                'original_query': original_query,
                'response': f"[Network Error: Unable to reach LLM - {str(e)}]",
                'specialist': None,
                'patterns_used': [],
                'confidence': 0.0,
                'timestamp': datetime.utcnow().isoformat(),
                'engine': 'GenericAssistantEngine',
                'domain': self.domain.domain_id,
                'processing_time_ms': 0,
                'direct_prompt': True,
                'llm_used': False,
                'error': True
            }
        except Exception as e:
            logger.error(f"Direct prompt unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'query': actual_query,
                'original_query': original_query,
                'response': f"[Error: {str(e)}]",
                'specialist': None,
                'patterns_used': [],
                'confidence': 0.0,
                'timestamp': datetime.utcnow().isoformat(),
                'engine': 'GenericAssistantEngine',
                'domain': self.domain.domain_id,
                'processing_time_ms': 0,
                'direct_prompt': True,
                'llm_used': False,
                'error': True
            }

    async def _polish_pattern(
        self,
        query: str,
        llm_response: str,
        domain_id: str
    ) -> Dict[str, Any]:
        """
        Polish a pattern using LLM to generate meaningful title and fill fields.

        Returns a dict with polished pattern fields:
        - name: Short, meaningful title (5-10 words)
        - problem: Clear problem statement
        - solution: Enhanced solution with details
        - description: Friendly, informative description
        - examples: Relevant examples
        - tags: Appropriate tags
        """
        import httpx

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "glm-4.7")

        if not api_key:
            # No API key - return basic polish
            return {
                "name": query[:50] + ("..." if len(query) > 50 else ""),
                "problem": query,
                "solution": llm_response,
                "description": f"Response to: {query}",
                "examples": [query],
                "tags": ["llm_generated"]
            }

        # Build polishing prompt - only for metadata, NOT rewriting the solution
        prompt = f"""Hey! You're helping organize knowledge for ExFrame (an awesome expertise framework)!

DOMAIN: {domain_id}

ORIGINAL QUERY: {query}

Great news - the AI has already provided a fantastic full answer! Your job is the fun part - creating a catchy title and helpful metadata so people can easily find this gem.

Return ONLY valid JSON:
{{
  "name": "A memorable, engaging title (5-10 words) that makes someone curious to learn more!",
  "problem": "What challenge does this solve? Describe it in a friendly, relatable way (1-2 sentences)",
  "description": "Get people excited about this! What's the context? Why is it useful? Be enthusiastic (2-3 sentences)",
  "examples": ["Give a concrete example of when someone would use this", "Add another practical scenario"],
  "tags": ["Pick 5 relevant tags that will help people discover this"]
}}

Style: Enthusiastic, friendly, like a knowledgeable friend sharing something cool. You love helping people learn!

Keep it concise but fun - the full detailed answer is stored separately.

Return ONLY the JSON, no other text:"""

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            is_anthropic = "anthropic" in base_url.lower()

            if is_anthropic:
                model_name = model if model.startswith("glm-") else model.replace("gpt-", "claude-")
                payload = {
                    "model": model_name,
                    "max_tokens": 512,  # Only metadata, not full solution
                    "messages": [{"role": "user", "content": prompt}]
                }
            else:
                payload = {
                    "model": model,
                    "max_tokens": 512,  # Only metadata, not full solution
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                }

            timeout = httpx.Timeout(30.0)  # Normal timeout for metadata generation
            async with httpx.AsyncClient(timeout=timeout) as client:
                endpoint = f"{base_url.rstrip('/')}/v1/messages" if is_anthropic else f"{base_url.rstrip('/')}/chat/completions"

                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                # Parse response
                content = ""
                if "choices" in data:
                    content = data["choices"][0]["message"]["content"]
                elif "content" in data and isinstance(data["content"], list):
                    content = data["content"][0].get("text", "")
                elif "content" in data and isinstance(data["content"], str):
                    content = data["content"]

                # Try to parse JSON from LLM response
                import re
                json_match = re.search(r'\{[^{}]*\{.*\}[^{}]*\}|\{[^{}]+\}', content, re.DOTALL)
                if json_match:
                    polished = json.loads(json_match.group(0))
                    print(f"  ✓ Pattern polished: {polished.get('name', 'Unknown')}")
                    return polished
                else:
                    print(f"  ⚠ Could not parse JSON from LLM polish, using basic")
                    raise ValueError("No JSON found")

        except Exception as e:
            print(f"  ⚠ LLM polishing failed: {e}, using basic fields")
            return {
                "name": query[:50] + ("..." if len(query) > 50 else ""),
                "problem": query,
                "solution": llm_response,
                "description": f"Response to: {query}",
                "examples": [query],
                "tags": ["llm_generated"]
            }

    async def _save_candidate_pattern(
        self,
        query: str,
        llm_response: str,
        specialist_id: Optional[str],
        patterns_found: int,
        confidence: float,
        research_strategy_used: bool = False
    ) -> Optional[str]:
        """
        Save LLM response as a pattern.

        If research_strategy_used is True (from trusted documentation),
        auto-certify at 80% confidence.
        Otherwise, save as candidate pattern for later review.
        """
        try:
            # Check if a pattern with this exact query already exists
            all_patterns = await self.knowledge_base.get_all_patterns()
            for existing_pattern in all_patterns:
                origin_query = existing_pattern.get("origin_query", "").lower().strip()
                if origin_query == query.lower().strip():
                    # Pattern exists with this query
                    if existing_pattern.get("status") == "certified":
                        # CERTIFIED patterns are sacred - don't overwrite them
                        print(f"  ✓ Certified pattern exists for query: {query[:40]}... - NOT overwriting with LLM response")
                        # Update usage count
                        try:
                            await self.knowledge_base.record_feedback(
                                existing_pattern["id"],
                                {"accessed": True}
                            )
                        except:
                            pass
                        return existing_pattern["id"]
                    elif existing_pattern.get("status") == "candidate":
                        # CANDIDATE patterns can be updated
                        print(f"  ℹ Candidate already exists for query: {query[:40]}... - Updating usage")
                        # Update usage count instead of creating duplicate
                        try:
                            await self.knowledge_base.record_feedback(
                                existing_pattern["id"],
                                {"accessed": True}
                            )
                        except:
                            pass
                        return existing_pattern["id"]

            # Check if LLM response indicates query is out of scope
            # Flag these patterns for human review instead of blocking creation
            out_of_scope_indicators = [
                "falls outside the scope",
                "outside the scope",
                "not covered",
                "does not contain relevant information",
                "beyond the scope",
                "not within the scope",
                "this domain does not cover",
                "this question is outside",
                "unable to answer",
                "cannot provide information",
                "not documented",
                # Added: Common LLM refusal patterns
                "i am unable to provide",
                "unable to provide",
                "cannot provide",
                "can only assist",
                "i can only assist",
                "unable to help with",
                "i'm unable to",
                "im unable to",
                "not able to provide",
                "only assist with",
                "is not within my expertise",
                "not something i can help with",
                "outside of my expertise",
                "beyond my expertise",
                "outside my expertise",
                "not designed to",
                "cannot assist with",
                "i cannot assist"
            ]

            llm_response_lower = llm_response.lower()
            is_out_of_scope = any(indicator in llm_response_lower for indicator in out_of_scope_indicators)

            # Generate pattern from LLM response
            now = datetime.utcnow()

            # Find the maximum existing pattern ID to generate a unique new ID
            # This is more robust than using len(all_patterns) which can cause duplicates
            max_id = 0
            for p in all_patterns:
                pid = p.get('id', '')
                # Extract the numeric part from IDs like "exframe_methods_018" or "exframe_methods_candidate_005"
                parts = pid.split('_')
                if len(parts) >= 2:
                    try:
                        num = int(parts[-1])
                        max_id = max(max_id, num)
                    except ValueError:
                        pass  # Skip if the last part isn't a number
            next_id = max_id + 1

            # Determine pattern status based on scope
            # ALL LLM-generated patterns are candidates requiring human verification
            if is_out_of_scope:
                # Out-of-scope queries get flagged for review
                pattern_id = f"{self.domain.domain_id}_flagged_{next_id:03d}"
                pattern_status = "flagged_for_review"
                pattern_confidence = 0.10  # Low confidence
                pattern_type = "how_to"  # Valid type even for flagged patterns
                pattern_tags = ["flagged_for_review", "out_of_scope", "llm_generated"]
                log_prefix = "⚠ Flagged pattern (out of scope)"
            else:
                # ALL LLM-generated patterns (including from docs) are candidates
                # They require human verification before becoming certified
                pattern_id = f"{self.domain.domain_id}_candidate_{next_id:03d}"
                pattern_status = "candidate"
                pattern_confidence = 0.50  # Candidate confidence
                pattern_type = "knowledge"
                # If research strategy was used, note it in tags for reference
                if research_strategy_used:
                    pattern_tags = ["candidate", "llm_generated", "documentation_derived"]
                else:
                    pattern_tags = ["candidate", "llm_generated"]
                log_prefix = "✓ Saved candidate pattern (requires human verification)"

            # Polish the pattern to generate meaningful title and fill fields (but keep full AI response)
            print(f"  → Polishing pattern for: {query[:40]}...")
            polished = await self._polish_pattern(query, llm_response, self.domain.domain_id)

            candidate_pattern = {
                "id": pattern_id,
                "name": polished.get("name", query[:50] + ("..." if len(query) > 50 else "")),
                "pattern_type": pattern_type,
                "description": polished.get("description", f"Auto-generated from query: {query}"),
                "problem": polished.get("problem", query),  # Polished problem statement
                "solution": llm_response,  # FULL original AI response - NOT the polished summary
                "steps": [],  # Could be parsed from response in future
                "conditions": {},
                "related_patterns": [],
                "prerequisites": [],
                "alternatives": [],
                "confidence": pattern_confidence,  # 0.50 for all candidates
                "sources": [],
                "tags": list(set(pattern_tags + polished.get("tags", []))),  # Merge tags
                "examples": polished.get("examples", [query]),  # Polished examples
                "domain": self.domain.domain_id,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "times_accessed": 0,
                "user_rating": None,

                # Status metadata - ALL candidates require human verification
                "status": pattern_status,
                "origin": "documentation_research" if research_strategy_used else "llm_fallback",
                "origin_query": query,  # Keep original query for matching
                "generated_at": now.isoformat(),
                "generated_by": os.getenv("LLM_MODEL", "glm-4.7"),
                "confidence_score": confidence,
                "reviewed_by": None,  # Candidate patterns are not reviewed
                "reviewed_at": None,  # Candidate patterns are not reviewed
                "review_notes": "Requires human verification before becoming certified",  # All candidates need verification
                "usage_count": 0,
                "user_feedback": []
            }

            # Save to knowledge base
            saved_id = await self.knowledge_base.add_pattern(candidate_pattern)

            print(f"  {log_prefix}: {saved_id} from query: {query[:40]}...")
            return saved_id

        except Exception as e:
            print(f"  Warning: Failed to save candidate pattern: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_domain_status(self) -> Dict[str, Any]:
        """Get status of the domain and engine."""
        return {
            'domain': self.domain.domain_id,
            'domain_name': self.domain.domain_name,
            'patterns_loaded': self.knowledge_base.get_pattern_count() if self.knowledge_base else 0,
            'specialists_available': self.domain.list_specialists(),
            'categories': self.knowledge_base.get_all_categories() if self.knowledge_base else [],
            'queries_processed': len(self.query_history),
        }

    async def reload(self) -> None:
        """Reload the domain configuration and knowledge base from disk.

        Called when domain.json is updated externally (e.g., via admin UI).
        Reloads:
        - Domain configuration from domain.json
        - Knowledge base patterns from patterns.json
        - Specialist definitions
        """
        logger.info(f"Reloading domain: {self.domain.domain_id}")

        # Reload domain configuration
        try:
            await self.domain.reload()
        except Exception as e:
            logger.warning(f"Failed to reload domain config: {e}")

        # Reload knowledge base patterns
        if self.knowledge_base:
            try:
                await self.knowledge_base.load_patterns()
                pattern_count = len(self.knowledge_base._patterns) if hasattr(self.knowledge_base, '_patterns') else 0
                logger.info(f"  Reloaded {pattern_count} patterns")
            except Exception as e:
                logger.warning(f"Failed to reload knowledge base: {e}")

        logger.info(f"Domain reload complete: {self.domain.domain_id}")

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query history."""
        return self.query_history[-limit:]

    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query traces from memory."""
        return self.trace_log[-limit:]

    @staticmethod
    def get_trace_from_log(limit: int = 50) -> List[Dict[str, Any]]:
        """Read recent traces from log file."""
        traces = []
        log_file = TRACE_DIR / "queries.log"

        if not log_file.exists():
            return []

        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-limit:]

            for line in lines:
                # Split timestamp from JSON
                try:
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        traces.append({
                            'logged_at': parts[0],
                            **json.loads(parts[1])
                        })
                except (json.JSONDecodeError, ValueError):
                    continue
        except Exception:
            pass

        return traces

    @staticmethod
    def get_trace_for_query(query_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific trace by query ID/timestamp."""
        traces = GenericAssistantEngine.get_trace_from_log(limit=1000)
        for trace in traces:
            if trace.get('start_time') == query_id or trace.get('query') == query_id:
                return trace
        return None
