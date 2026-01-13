"""
Generic Assistant Engine - Domain-agnostic query processing.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import json
import logging
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
        include_trace: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query.

        Args:
            query: User's question or request
            context: Optional additional context
            include_trace: Whether to include detailed processing trace

        Returns:
            Response dictionary with answer, sources, and metadata
        """
        start_time = datetime.utcnow()
        trace = {
            'query': query,
            'start_time': start_time.isoformat(),
            'steps': []
        } if self.enable_tracing else None

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
        step2_time = datetime.utcnow()
        patterns = await self.knowledge_base.search(query, limit=5)

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
                        'relevance': p.get('confidence', 0)
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
        # Prepare response data for enrichers
        enricher_input = {
            'query': query,
            'patterns': patterns,
            'response': response,
            'confidence': 0.0,  # Will be calculated later
            'specialist_id': specialist_id,
            'processing_method': processing_method
        }

        # Initialize enriched_data to avoid undefined variable
        enriched_data = {}

        # Call domain enrichers
        try:
            enriched_data = await self.domain.enrich(enricher_input)

            print(f"  DEBUG: After enrichment - llm_used: {enriched_data.get('llm_used')}, keys: {list(enriched_data.keys())}")

            # Update response and result with enriched data
            if enriched_data.get('llm_used'):
                print(f"  DEBUG: LLM was used, checking response key...")
                # LLM was used as fallback or enhancement
                if 'llm_fallback' in enriched_data:
                    # LLM fallback response
                    print(f"  DEBUG: Using llm_fallback as response")
                    response = enriched_data['llm_fallback']
                    result_key = 'llm_fallback'
                elif 'llm_enhancement' in enriched_data:
                    # LLM enhancement to existing response
                    print(f"  DEBUG: Using llm_enhancement")
                    response = enriched_data.get('response', response)
                    if enriched_data.get('llm_enhancement'):
                        response += f"\n\n---\n\n{enriched_data['llm_enhancement']}"
                    result_key = 'llm_enhancement'
                elif 'llm_response' in enriched_data:
                    # LLM replaced response
                    print(f"  DEBUG: Using llm_response as response")
                    response = enriched_data['llm_response']
                    result_key = 'llm_response'
                else:
                    print(f"  DEBUG: llm_used=True but no response key found!")

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
        confidence = self._calculate_confidence(patterns, specialist, query)

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

            # Reduce confidence when LLM is used - AI-generated content is less reliable
            # Set to max 0.7 (70%) to indicate uncertainty and risk
            result['confidence'] = min(confidence * 0.7, 0.7)
            print(f"  DEBUG: Reduced confidence from {confidence:.2f} to {result['confidence']:.2f} due to LLM usage")

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

            # Save LLM response as candidate pattern for future learning
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

                await self._save_candidate_pattern(
                    query=query,
                    llm_response=llm_response_text,
                    specialist_id=specialist_id,
                    patterns_found=len(patterns),
                    confidence=result['confidence'],  # Use reduced confidence
                    research_strategy_used=research_strategy_used
                )

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

    def _synthesize_answer(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """Synthesize answer from multiple patterns."""
        if not patterns:
            return ("I couldn't find specific information for your query. "
                   "Try rephrasing or being more specific.")

        # Use top pattern's solution
        top_pattern = patterns[0]

        if top_pattern.get('solution'):
            answer = f"**{top_pattern['name']}**\n\n{top_pattern['solution']}"

            # Add steps if available
            if top_pattern.get('steps'):
                answer += "\n\n**Steps:**\n"
                for i, step in enumerate(top_pattern['steps'][:5], 1):
                    answer += f"{i}. {step}\n"

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
            # Don't create patterns for out-of-scope queries
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
                "cannot provide information"
            ]

            llm_response_lower = llm_response.lower()
            is_out_of_scope = any(indicator in llm_response_lower for indicator in out_of_scope_indicators)

            if is_out_of_scope:
                print(f"  ✗ Skipping pattern creation - query is out of scope: {query[:40]}...")
                return None

            # Generate pattern from LLM response
            now = datetime.utcnow()

            # Extract a name from the query (first ~50 chars)
            name = query[:50] + ("..." if len(query) > 50 else "")

            # Count existing patterns to generate ID
            existing_count = len(all_patterns)

            # Auto-certify if from trusted documentation research
            if research_strategy_used:
                # Documentation patterns get auto-certified at 80%
                pattern_id = f"{self.domain.domain_id}_{existing_count + 1:03d}"
                pattern_status = "certified"
                pattern_confidence = 0.80
                pattern_type = "knowledge"
                pattern_tags = ["auto_certified", "documentation_derived"]
                log_prefix = "✓ Auto-certified pattern"
            else:
                # Regular LLM responses are candidates
                pattern_id = f"{self.domain.domain_id}_candidate_{existing_count + 1:03d}"
                pattern_status = "candidate"
                pattern_confidence = 0.50
                pattern_type = "candidate"
                pattern_tags = ["candidate", "llm_generated"]
                log_prefix = "✓ Saved candidate pattern"

            candidate_pattern = {
                "id": pattern_id,
                "name": name,
                "pattern_type": pattern_type,
                "description": f"Auto-generated from query: {query}",
                "problem": query,  # The query that triggered the LLM
                "solution": llm_response,  # The LLM's response
                "steps": [],  # Could be parsed from response in future
                "conditions": {},
                "related_patterns": [],
                "prerequisites": [],
                "alternatives": [],
                "confidence": pattern_confidence,  # 0.80 for docs, 0.50 for candidates
                "sources": [],
                "tags": pattern_tags,
                "examples": [query],  # Sample question from the query
                "domain": self.domain.domain_id,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "times_accessed": 0,
                "user_rating": None,

                # Status metadata
                "status": pattern_status,
                "origin": "documentation_research" if research_strategy_used else "llm_fallback",
                "origin_query": query,
                "generated_at": now.isoformat(),
                "generated_by": "glm-4.7",  # Could be made configurable
                "confidence_score": confidence,
                "reviewed_by": None if not research_strategy_used else "system",
                "reviewed_at": None if not research_strategy_used else now.isoformat(),
                "review_notes": None if not research_strategy_used else "Auto-certified from trusted documentation",
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
