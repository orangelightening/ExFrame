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
ExFrame Specialist Plugin for ExFrame Domain Exception

This specialist implements the three-stage search process:
1. Research docs (local markdown files) - PRIMARY
2. Document store (external knowledge) - SECONDARY
3. Local patterns (cached data) - FALLBACK
"""

from typing import List, Dict, Any, Optional
import logging

from core.specialist_plugin import SpecialistPlugin
from knowledge.document_store import DocumentStorePlugin, ExFrameInstanceStore
from core.research import create_research_strategy

logger = logging.getLogger(__name__)


class ExFrameSpecialistPlugin(SpecialistPlugin):
    """Specialist for ExFrame domain with research strategy integration.

    This specialist implements the three-stage search process:
    - Stage 1: Research docs (local markdown files) - PRIMARY
    - Stage 2: Document store (external knowledge) - SECONDARY
    - Stage 3: Local patterns (cached data) - FALLBACK
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
                - research_strategy: Configuration for document research strategy
        """
        self.domain = knowledge_base  # Store knowledge base as domain for compatibility
        self.config = config
        self.document_store_enabled = config.get("document_store_enabled", True)
        self.local_patterns_enabled = config.get("local_patterns_enabled", True)
        self.reply_capture_enabled = config.get("reply_capture_enabled", True)
        self.session_tracking = config.get("session_tracking", True)

        # Scope boundary configuration
        self.scope_enabled = config.get("scope", {}).get("enabled", False)
        self.scope_min_confidence = config.get("scope", {}).get("min_confidence", 0.0)
        self.scope_in_list = config.get("scope", {}).get("in_scope", [])
        self.scope_out_list = config.get("scope", {}).get("out_of_scope", [])
        self.scope_response = config.get("scope", {}).get("out_of_scope_response",
            "This question is outside the documentation scope for this domain.")

        if self.scope_enabled:
            logger.info(f"[EXFRAME_SPEC] Scope boundaries enabled (min_confidence={self.scope_min_confidence})")

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

        # Initialize research strategy (PRIMARY document search)
        self.research_strategy = None
        research_config = config.get("research_strategy")

        if research_config:
            try:
                logger.info(f"[EXFRAME_SPEC] Initializing research strategy: {research_config.get('type')}")
                self.research_strategy = create_research_strategy(research_config)
            except Exception as e:
                logger.error(f"[EXFRAME_SPEC] Failed to initialize research strategy: {e}")
                self.research_strategy = None

        # Session tracking
        self.sessions: Dict[str, Dict] = {}

        logger.info(f"[EXFRAME_SPEC] Initialized with config: {config}")

    def _is_out_of_scope(self, query: str) -> tuple:
        """Check if query is outside the domain's scope boundaries.

        Args:
            query: User's query string

        Returns:
            Tuple of (is_out_of_scope, reason)
            - is_out_of_scope: True if query should be rejected
            - reason: String explaining why (or None if in scope)
        """
        if not self.scope_enabled:
            return False, None

        query_lower = query.lower()

        # Check explicit out_of_scope keywords
        for out_item in self.scope_out_list:
            # Check for multi-word phrases
            out_lower = out_item.lower()
            if out_lower in query_lower:
                logger.info(f"[EXFRAME_SPEC] Query rejected - out of scope: '{out_item}'")
                return True, f"Query contains out-of-scope topic: {out_item}"

        # Check for framework names that suggest out-of-scope questions
        out_of_scope_indicators = [
            "django", "flask ", "flask.", "rails", "laravel", "express.js",
            "react ", "react.", "vue", "angular", "svelte",
            "kubernetes", "k8s", "terraform", "ansible",
            "how do i in python", "python syntax", "python code for"
        ]

        for indicator in out_of_scope_indicators:
            if indicator in query_lower:
                # Only trigger if NOT also mentioning ExFrame/scope topics
                in_scope_check = any(item.lower() in query_lower for item in self.scope_in_list)
                if not in_scope_check:
                    logger.info(f"[EXFRAME_SPEC] Query rejected - detected out-of-scope indicator: '{indicator}'")
                    return True, f"Query appears to be about {indicator}, not ExFrame"

        return False, None

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
        """Process query with three-stage search.

        ExFrame domain prioritizes FRESH documentation searches over cached patterns.
        Search order: Research docs (local markdown) → Document store → Local patterns.

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

        # Check scope boundaries FIRST (before any searching)
        if self.scope_enabled:
            is_out_of_scope, reason = self._is_out_of_scope(query)
            if is_out_of_scope:
                logger.info(f"[EXFRAME_SPEC] Query rejected: {reason}")
                return {
                    "response": self.scope_response,
                    "patterns_used": [],
                    "documents_used": [],
                    "document_results": [],
                    "local_results": [],
                    "session_id": session_id,
                    "confidence": 0.0,
                    "query": query,
                    "out_of_scope": True,
                    "out_of_scope_reason": reason
                }

        # Stage 1: Research Strategy (PRIMARY - search local documentation files)
        research_results = []
        search_metadata = {}  # Track search metadata for citation prompt
        if self.research_strategy:
            try:
                # Initialize research strategy if needed
                if not hasattr(self.research_strategy, '_initialized') or not self.research_strategy._initialized:
                    await self.research_strategy.initialize()

                # Search using research strategy
                search_results = await self.research_strategy.search(query, limit=5)

                # Get search metadata for citation prompt
                if hasattr(self.research_strategy, 'get_search_metadata'):
                    search_metadata = self.research_strategy.get_search_metadata()

                # Convert SearchResult objects to document results format
                for result in search_results:
                    # SearchResult has: content, source (filename), relevance_score, metadata
                    research_results.append({
                        "id": result.source,  # Use source (filename) as ID
                        "title": result.source,  # Use source (filename) as title
                        "content": result.content,  # Full document content
                        "description": result.metadata.get("summary", f"Full document: {result.source}"),
                        "source": "Research Docs",
                        "metadata": {
                            "file": result.source,
                            "path": result.metadata.get("path", ""),
                            "relevance": result.relevance_score,
                            "total_files": result.metadata.get("total_files", 0)
                        }
                    })

                logger.info(f"[EXFRAME_SPEC] Research strategy search returned {len(research_results)} results (PRIMARY)")
            except Exception as e:
                logger.error(f"[EXFRAME_SPEC] Research strategy search failed: {e}")

        # Stage 2: Search document store (external knowledge)
        document_results = []
        if self.document_store_enabled and self.document_store:
            try:
                document_results = await self.document_store.search(query, limit=5)
                logger.info(f"[EXFRAME_SPEC] Document store search returned {len(document_results)} results (SECONDARY)")
            except Exception as e:
                logger.error(f"[EXFRAME_SPEC] Document store search failed: {e}")

        # Stage 3: Search local patterns (FALLBACK - only if no research/doc results)
        local_results = []
        if not research_results and not document_results:
            if self.local_patterns_enabled:
                try:
                    kb = self.domain  # self.domain IS the knowledge_base (passed from generic_domain.py)
                    local_results = await kb.search(query=query, limit=5)
                    logger.info(f"[EXFRAME_SPEC] Local pattern search returned {len(local_results)} results (FALLBACK)")
                except Exception as e:
                    logger.error(f"[EXFRAME_SPEC] Local pattern search failed: {e}")

        # Combine primary results (research + doc store)
        primary_results = research_results + document_results

        # Track session
        if session_id and self.session_tracking:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "query": query,
                    "created_at": self._get_timestamp(),
                    "research_results": [],
                    "document_results": [],
                    "local_results": [],
                    "replies": []
                }

            self.sessions[session_id]["research_results"] = research_results
            self.sessions[session_id]["document_results"] = document_results
            self.sessions[session_id]["local_results"] = local_results

        # Calculate confidence
        # High confidence if research/docs have results (fresh data)
        # Lower confidence if falling back to local patterns (cached data)
        confidence = 0.5
        if research_results:
            confidence = 0.90  # Research results are fresh and authoritative
        elif document_results:
            confidence = 0.85  # Document store results are fresh
        elif local_results:
            confidence = 0.60  # Local patterns are fallback only

        # Form response (prioritize research/doc results)
        # When we have research results, let LLM provide the main answer first
        # Store the file list separately to be appended at the end
        response_text = ""  # Empty response - LLM will provide the main answer

        # Format source list for display at the end
        source_list = self._form_source_list(primary_results, local_results) if primary_results or local_results else ""

        # Convert research_results to pattern format so they're passed to enricher
        research_patterns = []
        for r in research_results:
            research_patterns.append({
                "id": f"research_{r.get('id', '')}",  # Prefix to avoid KB lookup
                "name": r.get("title", r.get("id", "Unknown")),
                "description": r.get("description", ""),
                "solution": r.get("content", ""),
                "pattern_type": "knowledge",
                "confidence": r["metadata"].get("relevance", 0.8),
                "status": "certified",
                "tags": ["document_search", "research_docs"],
                "_source": "research_strategy"
            })

        # Return combined results with research/docs as primary
        # IMPORTANT: Include full pattern objects (not just IDs) so engine can pass them to enricher
        # Research patterns are synthetic (not from KB), so they must be passed as full objects
        all_patterns = research_patterns + local_results  # Full objects, not IDs

        return {
            "response": response_text,  # Empty - LLM provides main answer
            "patterns_used": all_patterns,  # Full pattern objects (engine handles both IDs and objects)
            "documents_used": [d.get("id") for d in primary_results],  # PRIMARY
            "research_results": research_results,  # PRIMARY RESULTS (for reference)
            "document_results": document_results,  # SECONDARY RESULTS
            "local_results": local_results,  # FALLBACK/REFERENCE
            "session_id": session_id,
            "confidence": confidence,
            "query": query,
            "search_strategy": "research_primary",  # Indicate strategy used
            "_source_list": source_list,  # File list to append after LLM response
            "search_metadata": search_metadata  # Total files searched, matches, for citation prompt
        }

    def _form_source_list(self, document_results: List, local_results: List) -> str:
        """Format source list for display at the end of response.

        Args:
            document_results: Results from research + document store
            local_results: Results from local pattern search

        Returns:
            Formatted source list string
        """
        if not document_results and not local_results:
            return ""

        # Format results
        output = []

        # Add document results (research + document store)
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

        return "\n".join(output)

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

        For Type 3 (Document Store) domains, always return empty string.
        This allows the LLM to generate the main response using the documents as context,
        without showing duplicate pattern lists.

        Args:
            response_data: Response data from process_query

        Returns:
            Formatted response string (always empty for Type 3)
        """
        # For Type 3 domains, always return empty string
        # The LLM enricher will provide the main response using document context
        # This prevents duplicate pattern lists from being shown
        return ""
    
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
