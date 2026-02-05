"""
Phase 1 Engine - Persona + Override System

This is a simplified engine that coexists with the existing engine.
It provides the Phase 1 architecture (3 Personas + Pattern Override)
while keeping the old system intact for gradual migration.

Usage:
    from generic_framework.core.phase1_engine import Phase1Engine

    engine = Phase1Engine()
    response = await engine.process_query("How to cook rice", "cooking")
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from .query_processor import process_query
from .personas import get_persona, list_personas


logger = logging.getLogger("phase1_engine")


class Phase1Engine:
    """
    Phase 1 query processing engine.

    Simplified architecture:
    1. Load domain config → get persona
    2. Search for patterns
    3. If patterns found → use them (override)
    4. Else → use persona's data source

    That's it. No complex state machine, no multiple enrichers,
    just the core decision tree.
    """

    def __init__(self, enable_trace: bool = True):
        """
        Initialize Phase 1 engine.

        Args:
            enable_trace: Whether to log trace information
        """
        self.enable_trace = enable_trace

    async def process_query(
        self,
        query: str,
        domain_name: str,
        context: Optional[Dict] = None,
        search_patterns: Optional[bool] = None,
        show_thinking: bool = False
    ) -> Dict[str, Any]:
        """
        Process query using Phase 1 architecture.

        Args:
            query: User query
            domain_name: Domain name
            context: Optional context dict
            search_patterns: Optional flag to control pattern search
                           - True: Search for patterns
                           - False: Skip pattern search, use persona data source
                           - None: Use domain config default
            show_thinking: Whether to show step-by-step reasoning (default: False)

        Returns:
            Response dict with answer and metadata
        """
        start_time = datetime.utcnow()

        if self.enable_trace:
            logger.info(f"[Phase1] Processing query: {query} (domain: {domain_name})")

        try:
            # Use query processor (the core Phase 1 logic)
            response = await process_query(query, domain_name, context, search_patterns, show_thinking)

            # Add timing metadata
            end_time = datetime.utcnow()
            response['processing_time_ms'] = int(
                (end_time - start_time).total_seconds() * 1000
            )
            response['start_time'] = start_time.isoformat()
            response['end_time'] = end_time.isoformat()
            response['engine_version'] = 'phase1'

            if self.enable_trace:
                logger.info(
                    f"[Phase1] Complete: persona={response.get('persona')}, "
                    f"source={response.get('source')}, "
                    f"pattern_override={response.get('pattern_override_used')}"
                )

            return response

        except Exception as e:
            logger.error(f"[Phase1] Error processing query: {e}", exc_info=True)

            return {
                'error': True,
                'response': f"Error processing query: {str(e)}",
                'query': query,
                'domain': domain_name,
                'engine_version': 'phase1'
            }

    def get_available_personas(self) -> list:
        """Get list of available persona names"""
        return list_personas()

    def get_persona_info(self, persona_name: str) -> Dict[str, Any]:
        """
        Get information about a persona.

        Args:
            persona_name: Persona name (poet/librarian/researcher)

        Returns:
            Persona info dict
        """
        try:
            persona = get_persona(persona_name)
            return {
                'name': persona.name,
                'data_source': persona.data_source,
                'show_thinking': persona.show_thinking,
                'trace': persona.trace
            }
        except ValueError as e:
            return {
                'error': True,
                'message': str(e)
            }


# Singleton instance for convenience
_engine = None


def get_phase1_engine() -> Phase1Engine:
    """Get singleton Phase 1 engine instance"""
    global _engine
    if _engine is None:
        _engine = Phase1Engine()
    return _engine
