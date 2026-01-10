"""
Knowledge Base Plugin System

A knowledge base plugin manages pattern storage and retrieval.
This abstraction enables different backends (JSON, SQLite, Vector, Graph, Hybrid).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Pattern:
    """A pattern from the knowledge base."""
    pattern_id: str
    name: str
    type: str
    category: str
    problem: str
    solution: str
    examples: List[Any]
    tags: List[str]
    metadata: Dict[str, Any]
    relevance: float = 0.0


class KnowledgeBasePlugin(ABC):
    """
    A knowledge base plugin stores and retrieves patterns.

    This abstraction enables different storage backends while keeping
    the interface consistent for specialists.
    """

    # Subclasses should define these
    name: str = "KnowledgeBase"

    @abstractmethod
    async def load_patterns(self) -> None:
        """
        Load patterns from storage into memory.

        Called during domain initialization.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Search for patterns matching the query.

        Args:
            query: Search query text
            category: Optional category filter
            limit: Maximum results to return
            **filters: Additional backend-specific filters

        Returns:
            List of pattern dictionaries with at least:
                - pattern_id: str
                - name: str
                - type: str
                - category: str
                - solution: str
                - examples: List
        """
        pass

    @abstractmethod
    async def get_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific pattern by ID.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Pattern dict or None if not found
        """
        pass

    @abstractmethod
    def get_all_categories(self) -> List[str]:
        """
        Get all available categories.

        Returns:
            List of category names
        """
        pass

    @abstractmethod
    def get_pattern_count(self) -> int:
        """
        Get total number of patterns loaded.

        Returns:
            Pattern count
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Check knowledge base health.

        Returns:
            Health status dict with at least:
                - status: str ("healthy" | "degraded" | "unhealthy")
                - patterns_loaded: int
                - categories: List[str]
        """
        return {
            "status": "healthy",
            "patterns_loaded": self.get_pattern_count(),
            "categories": self.get_all_categories(),
            "backend": self.name
        }
