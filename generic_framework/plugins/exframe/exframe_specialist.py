"""
ExFrame Specialist Plugin for ExFrame Domain Exception

This specialist implements the two-stage search process:
1. Search document store (external knowledge)
2. Search local patterns
3. Combine results for reply formation
"""

from typing import List, Dict, Any, Optional
import logging

from core.specialist_plugin import SpecialistPlugin
from knowledge.document_store import DocumentStorePlugin, ExFrameInstanceStore

logger = logging.getLogger(__name__)


class ExFrameSpecialistPlugin(SpecialistPlugin):
    """Specialist for ExFrame domain with document store access.
    
    This specialist implements the two-stage search process:
    - Stage 1: Search document store (external knowledge)
    - Stage 2: Search local patterns
    - Combine results for reply formation
    """
    
    name: str = "ExFrame Knowledge Specialist"
    specialist_id: str = "exframe_specialist"
    
    def __init__(self, knowledge_base, config: Dict[str, Any]):
        """Initialize ExFrame specialist.
        
        Args:
            knowledge_base: Knowledge base instance for local pattern search
            config: Configuration dictionary with:
                - document_store_enabled: Enable document store search (default: True)
                - local_patterns_enabled: Enable local pattern search (default: True)
                - reply_capture_enabled: Enable reply capture (default: True)
                - session_tracking: Enable session tracking (default: True)
                - document_store_config: Configuration for document store
        """
        self.domain = knowledge_base  # Store knowledge base as domain for compatibility
        self.config = config
        self.document_store_enabled = config.get("document_store_enabled", True)
        self.local_patterns_enabled = config.get("local_patterns_enabled", True)
        self.reply_capture_enabled = config.get("reply_capture_enabled", True)
        self.session_tracking = config.get("session_tracking", True)
        
        # Initialize document store
        self.document_store: Optional[DocumentStorePlugin] = None
        doc_store_config = config.get("document_store_config", {})
        
        if self.document_store_enabled and doc_store_config:
            try:
                doc_store_type = doc_store_config.get("type", "exframe_instance")
                
                if doc_store_type == "exframe_instance":
                    self.document_store = ExFrameInstanceStore(doc_store_config)
                    logger.info("[EXFRAME_SPEC] Initialized ExFrameInstanceStore")
                # Add other store types here as needed
                # elif doc_store_type == "vector_store":
                #     self.document_store = VectorStoreDocumentStore(doc_store_config)
                # elif doc_store_type == "elasticsearch":
                #     self.document_store = ElasticsearchDocumentStore(doc_store_config)
                # elif doc_store_type == "web_search":
                #     self.document_store = WebSearchDocumentStore(doc_store_config)
                
            except Exception as e:
                logger.error(f"[EXFRAME_SPEC] Failed to initialize document store: {e}")
                self.document_store = None
        
        # Session tracking
        self.sessions: Dict[str, Dict] = {}
        
        logger.info(f"[EXFRAME_SPEC] Initialized with config: {config}")
    
    def can_handle(self, query: str) -> float:
        """Check if this specialist can handle the query.
        
        ExFrame specialist handles all queries to enable the two-stage
        search process.
        
        Args:
            query: User's query
            
        Returns:
            Confidence score (1.0 for all queries)
        """
        return 1.0
    
    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """Process query with two-stage search.
        
        ExFrame domain prioritizes FRESH document store searches over cached patterns.
        This ensures current documentation is always available, not stale cached patterns.
        
        Args:
            query: User's query
            context: Optional context dictionary with:
                - session_id: Session identifier for tracking
                - llm_confirmed: Whether LLM fallback is confirmed
            
        Returns:
            Dictionary with:
                - response: Formatted response text
                - patterns_used: List of local pattern IDs used (for reference only)
                - documents_used: List of document IDs from store (primary results)
                - document_results: Full document results (PRIMARY)
                - local_results: Full local pattern results (SECONDARY/REFERENCE)
                - session_id: Session identifier
                - confidence: Overall confidence score
        """
        session_id = None
        if context and isinstance(context, dict):
            session_id = context.get("session_id")
        
        # Stage 1: Search document store (PRIMARY - always fresh)
        document_results = []
        if self.document_store_enabled and self.document_store:
            try:
                document_results = await self.document_store.search(query, limit=5)
                logger.info(f"[EXFRAME_SPEC] Document store search returned {len(document_results)} results (PRIMARY)")
            except Exception as e:
                logger.error(f"[EXFRAME_SPEC] Document store search failed: {e}")

        # Stage 1.5: Search local documentation files (if document store returned nothing)
        # This is the "extended search" - searching local markdown files
        if not document_results:
            try:
                document_results = await self._search_local_docs(query, limit=5)
                logger.info(f"[EXFRAME_SPEC] Local doc search returned {len(document_results)} results (PRIMARY)")
            except Exception as e:
                logger.error(f"[EXFRAME_SPEC] Local doc search failed: {e}")
        
        # Stage 2: Search local patterns (ALWAYS run - merge with document results)
        local_results = []
        if self.local_patterns_enabled:
            try:
                kb = self.domain  # self.domain IS the knowledge_base (passed from generic_domain.py)
                local_results = await kb.search(query=query, limit=5)
                logger.info(f"[EXFRAME_SPEC] Local pattern search returned {len(local_results)} results (FALLBACK)")
            except Exception as e:
                logger.error(f"[EXFRAME_SPEC] Local pattern search failed: {e}")
        
        # Track session
        if session_id and self.session_tracking:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "query": query,
                    "created_at": self._get_timestamp(),
                    "document_results": [],
                    "local_results": [],
                    "replies": []
                }
            
            self.sessions[session_id]["document_results"] = document_results
            self.sessions[session_id]["local_results"] = local_results
        
        # Determine primary results (document store takes priority)
        primary_results = document_results if document_results else local_results
        
        # Calculate confidence
        # High confidence if document store has results (fresh data)
        # Lower confidence if falling back to local patterns (cached data)
        confidence = 0.5
        if document_results:
            confidence = 0.85  # Document store results are fresh and authoritative
        elif local_results:
            confidence = 0.6   # Local patterns are fallback only
        
        # Form response (prioritize document results)
        response_text = self._form_response(query, document_results, local_results)
        
        # Return combined results with document store as primary
        return {
            "response": response_text,
            "patterns_used": [r.get("id") for r in local_results],  # For reference
            "documents_used": [d.get("id") for d in document_results],  # PRIMARY
            "document_results": document_results,  # PRIMARY RESULTS
            "local_results": local_results,  # FALLBACK/REFERENCE
            "session_id": session_id,
            "confidence": confidence,
            "query": query,
            "search_strategy": "document_store_primary"  # Indicate strategy used
        }
    
    def _form_response(self, query: str, document_results: List, local_results: List) -> str:
        """Form response text from query and search results.

        Args:
            query: User's query
            document_results: Results from document store
            local_results: Results from local pattern search

        Returns:
            Formatted response string
        """
        if not document_results and not local_results:
            return f"I couldn't find any relevant information for '{query}'."

        # Format results
        output = []

        # Add document store results (primary)
        for i, result in enumerate(document_results):
            source = result.get("source", "Document Store")
            title = result.get("title", result.get("name", "Unknown"))
            output.append(f"{i+1}. {source}: {title}")

        # Add local pattern results (fallback)
        offset = len(document_results)
        for i, result in enumerate(local_results):
            source = "Local Patterns"
            name = result.get("name", "Unknown")
            output.append(f"{offset + i + 1}. {source}: {name}")

        response = "\n".join(output)

        # Add reply capture prompt if enabled
        if self.reply_capture_enabled:
            response += "\n\nWould you like me to elaborate on any of these?"

        return response

    async def _search_local_docs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search local documentation files for relevant content.

        This is the "extended search" that searches markdown files in the project.

        Args:
            query: User's search query
            limit: Maximum number of results to return

        Returns:
            List of document results with metadata
        """
        import os
        from pathlib import Path
        from typing import List

        # Documents to search (same as research_strategy)
        documents = [
            "README.md",
            "context.md",
            "claude-exframe.md",
            "ready-set.md",
            "LAUNCH_MANIFESTO.md",
            "LAUNCH_CHECKLIST.md",
            "OPEN_SOURCE_GUIDE.md",
            "GITHUB_LAUNCH_GUIDE.md",
            "INSTALL.md",
            "RELEASE_NOTES.md",
            "PLUGIN_ARCHITECTURE.md",
            "EXTENSION_POINTS.md",
            "rag-search-design.md",
            "query-rewrite.md"
        ]

        results = []
        base_path = Path("/app")

        for doc_name in documents:
            doc_path = base_path / doc_name
            if not doc_path.exists():
                continue

            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple keyword matching for now
                query_lower = query.lower()
                content_lower = content.lower()

                # Count keyword matches
                keywords = query_lower.split()
                match_count = sum(1 for kw in keywords if kw in content_lower)

                if match_count > 0:
                    # Extract a snippet around the first match
                    lines = content.split('\n')
                    snippet_lines = []
                    for i, line in enumerate(lines):
                        if any(kw in line.lower() for kw in keywords):
                            # Get context around the match
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            snippet_lines = lines[start:end]
                            break

                    snippet = '\n'.join(snippet_lines)[:300]

                    results.append({
                        "id": doc_name,
                        "title": doc_name,
                        "content": snippet,
                        "description": f"Matched {match_count} keywords in {doc_name}",
                        "source": "Local Documentation",
                        "metadata": {
                            "file": doc_name,
                            "match_count": match_count,
                            "confidence": min(match_count * 0.2, 1.0)
                        }
                    })
            except Exception as e:
                logger.warning(f"[EXFRAME_SPEC] Failed to read {doc_name}: {e}")

        # Sort by match count and return top results
        results.sort(key=lambda x: x["metadata"]["match_count"], reverse=True)
        return results[:limit]

    def format_response(self, response_data: Dict) -> str:
        """Format response for user.

        Args:
            response_data: Response data from process_query

        Returns:
            Formatted response string
        """
        query = response_data.get("query", "")
        document_results = response_data.get("document_results", [])
        local_results = response_data.get("local_results", [])
        
        if not document_results and not local_results:
            return f"I couldn't find any relevant information for '{query}'."
        
        # Format results
        output = []
        
        # Add document store results
        for i, result in enumerate(document_results):
            source = result.get("source", "Document Store")
            title = result.get("title", result.get("name", "Unknown"))
            output.append(f"{i+1}. {source}: {title}")
        
        # Add local pattern results
        offset = len(document_results)
        for i, result in enumerate(local_results):
            source = "Local Patterns"
            name = result.get("name", "Unknown")
            output.append(f"{offset + i + 1}. {source}: {name}")
        
        response = "\n".join(output)
        
        # Add reply capture prompt if enabled
        if self.reply_capture_enabled:
            response += "\n\nWould you like me to elaborate on any of these?"
        
        return response
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session dictionary or None
        """
        return self.sessions.get(session_id)
    
    def add_reply(self, session_id: str, reply: str, source: str = "manual") -> None:
        """Add a reply to a session.
        
        Args:
            session_id: Session identifier
            reply: Reply text
            source: Source of reply ("manual", "ai_generated")
        """
        if session_id in self.sessions and self.reply_capture_enabled:
            self.sessions[session_id]["replies"].append({
                "reply": reply,
                "source": source,
                "created_at": self._get_timestamp()
            })
            logger.info(f"[EXFRAME_SPEC] Added reply to session {session_id}")
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Remove sessions older than max_age_hours.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of sessions removed
        """
        from datetime import datetime, timedelta
        
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for session_id, session in self.sessions.items():
            if session["created_at"] < cutoff:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        logger.info(f"[EXFRAME_SPEC] Cleaned up {len(to_remove)} old sessions")
        return len(to_remove)
