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
Document Store Plugin for ExFrame Domain Exception

This module provides an interface and implementation for searching external
document/knowledge stores as part of the exframe domain's two-stage
search process.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentStorePlugin(ABC):
    """Abstract base for document store plugins.
    
    This interface allows exframe domain to search external knowledge sources
    (vector databases, Elasticsearch, web search, or other ExFrame instances)
    before searching local patterns.
    """
    
    name: str = "DocumentStore"
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents in external store.
        
        Args:
            query: User's search query
            limit: Maximum number of results to return
            
        Returns:
            List of document results with metadata
        """
        pass
    
    @abstractmethod
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document details or None if not found
        """
        pass
    
    @abstractmethod
    async def add_document(self, document: Dict[str, Any]) -> str:
        """Add a document to the store.
        
        Args:
            document: Document to add
            
        Returns:
            Document ID
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check if the document store is healthy and accessible.
        
        Returns:
            Health status dictionary
        """
        pass


class ExFrameInstanceStore(DocumentStorePlugin):
    """Document store that connects to another ExFrame instance.
    
    This allows one ExFrame instance to search patterns in another instance,
    enabling the constellation vision where multiple instances share knowledge.
    """
    
    name: str = "ExFrameInstanceStore"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ExFrame instance document store.
        
        Args:
            config: Configuration dictionary with:
                - remote_url: URL of remote ExFrame instance
                - timeout: Request timeout in seconds
                - api_key: Optional API key for authentication
        """
        self.config = config
        self.remote_url = config.get("remote_url", "")
        self.timeout = config.get("timeout", 30)
        self.api_key = config.get("api_key", None)
        
        if not self.remote_url:
            logger.warning("[EXFRAME_DOC_STORE] No remote_url configured")
        
        logger.info(f"[EXFRAME_DOC_STORE] Initialized with remote_url={self.remote_url}")
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search patterns in remote ExFrame instance.
        
        Args:
            query: User's search query
            limit: Maximum number of results to return
            
        Returns:
            List of pattern results from remote instance
        """
        if not self.remote_url:
            logger.warning("[EXFRAME_DOC_STORE] Cannot search: no remote_url configured")
            return []
        
        try:
            import httpx
            import asyncio
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Search remote instance
                url = f"{self.remote_url.rstrip('/')}/api/query"
                payload = {
                    "query": query,
                    "domain": "exframe",  # Search exframe domain
                    "include_trace": False,
                    "format": "json"
                }
                
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                logger.info(f"[EXFRAME_DOC_STORE] Searching remote instance: {url} with query={query}")
                
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                patterns = result.get("patterns_used", [])
                
                # Transform to document format
                documents = []
                for pattern in patterns[:limit]:
                    documents.append({
                        "id": pattern.get("id", ""),
                        "title": pattern.get("name", "Unknown"),
                        "content": pattern.get("solution", ""),
                        "description": pattern.get("description", ""),
                        "source": "exframe_instance",
                        "metadata": {
                            "confidence": pattern.get("confidence", 0.0),
                            "domain": pattern.get("domain", "exframe"),
                            "pattern_type": pattern.get("pattern_type", "knowledge")
                        }
                    })
                
                logger.info(f"[EXFRAME_DOC_STORE] Found {len(documents)} documents in remote instance")
                return documents
                
        except httpx.TimeoutException as e:
            logger.error(f"[EXFRAME_DOC_STORE] Timeout searching remote instance: {e}")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"[EXFRAME_DOC_STORE] HTTP error searching remote instance: {e}")
            return []
        except Exception as e:
            logger.error(f"[EXFRAME_DOC_STORE] Error searching remote instance: {e}")
            return []
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document (pattern) from remote instance.
        
        Args:
            doc_id: Pattern ID
            
        Returns:
            Pattern details or None if not found
        """
        if not self.remote_url:
            logger.warning("[EXFRAME_DOC_STORE] Cannot get document: no remote_url configured")
            return None
        
        try:
            import httpx
            import asyncio
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get pattern from remote instance
                url = f"{self.remote_url.rstrip('/')}/api/domains/exframe/patterns/{doc_id}"
                
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                logger.info(f"[EXFRAME_DOC_STORE] Getting document from remote instance: {url}")
                
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                pattern = response.json()
                
                # Transform to document format
                document = {
                    "id": pattern.get("id", ""),
                    "title": pattern.get("name", "Unknown"),
                    "content": pattern.get("solution", ""),
                    "description": pattern.get("description", ""),
                    "source": "exframe_instance",
                    "metadata": {
                        "confidence": pattern.get("confidence", 0.0),
                        "domain": pattern.get("domain", "exframe"),
                        "pattern_type": pattern.get("pattern_type", "knowledge")
                    }
                }
                
                logger.info(f"[EXFRAME_DOC_STORE] Retrieved document: {doc_id}")
                return document
                
        except httpx.TimeoutException as e:
            logger.error(f"[EXFRAME_DOC_STORE] Timeout getting document: {e}")
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"[EXFRAME_DOC_STORE] Document not found: {doc_id}")
                return None
            logger.error(f"[EXFRAME_DOC_STORE] HTTP error getting document: {e}")
            return None
        except Exception as e:
            logger.error(f"[EXFRAME_DOC_STORE] Error getting document: {e}")
            return None
    
    async def add_document(self, document: Dict[str, Any]) -> str:
        """Add a document (pattern) to remote instance.
        
        Args:
            document: Document to add
            
        Returns:
            Document ID
        """
        if not self.remote_url:
            logger.warning("[EXFRAME_DOC_STORE] Cannot add document: no remote_url configured")
            raise Exception("No remote_url configured")
        
        try:
            import httpx
            import asyncio
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Add pattern to remote instance
                url = f"{self.remote_url.rstrip('/')}/api/patterns"
                
                # Transform document to pattern format
                pattern = {
                    "domain": "exframe",
                    "name": document.get("title", "Untitled"),
                    "problem": document.get("content", ""),
                    "solution": document.get("content", ""),
                    "description": document.get("description", ""),
                    "pattern_type": "knowledge",
                    "origin": "exframe_remote",
                    "llm_generated": False,
                    "confidence": 0.7,
                    "status": "validated",
                    "tags": ["exframe_remote"]
                }
                
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                logger.info(f"[EXFRAME_DOC_STORE] Adding document to remote instance: {url}")
                
                response = await client.post(url, json=pattern, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                pattern_id = result.get("pattern_id", "")
                
                logger.info(f"[EXFRAME_DOC_STORE] Added document: {pattern_id}")
                return pattern_id
                
        except httpx.TimeoutException as e:
            logger.error(f"[EXFRAME_DOC_STORE] Timeout adding document: {e}")
            raise Exception(f"Timeout adding document: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"[EXFRAME_DOC_STORE] HTTP error adding document: {e}")
            raise Exception(f"HTTP error adding document: {e}")
        except Exception as e:
            logger.error(f"[EXFRAME_DOC_STORE] Error adding document: {e}")
            raise Exception(f"Error adding document: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the remote ExFrame instance is healthy.
        
        Returns:
            Health status dictionary
        """
        if not self.remote_url:
            return {
                "status": "unhealthy",
                "error": "No remote_url configured"
            }
        
        try:
            import httpx
            import asyncio
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.remote_url.rstrip('/')}/health"
                
                logger.info(f"[EXFRAME_DOC_STORE] Checking health of remote instance: {url}")
                
                response = await client.get(url)
                response.raise_for_status()
                
                result = response.json()
                
                return {
                    "status": result.get("status", "unknown"),
                    "service": result.get("service", "ExFrame"),
                    "version": result.get("version", "unknown")
                }
                
        except httpx.TimeoutException as e:
            logger.error(f"[EXFRAME_DOC_STORE] Timeout checking health: {e}")
            return {
                "status": "unhealthy",
                "error": f"Timeout: {e}"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"[EXFRAME_DOC_STORE] HTTP error checking health: {e}")
            return {
                "status": "unhealthy",
                "error": f"HTTP error: {e}"
            }
        except Exception as e:
            logger.error(f"[EXFRAME_DOC_STORE] Error checking health: {e}")
            return {
                "status": "unhealthy",
                "error": f"Error: {e}"
            }
