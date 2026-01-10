"""
Knowledge Base Interface - Abstract base class for knowledge storage.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class KnowledgeBaseConfig:
    """Configuration for knowledge base storage."""
    storage_path: str
    pattern_format: str = "json"  # 'yaml' or 'json'
    pattern_schema: Dict[str, Any] = field(default_factory=dict)

    # Search settings
    search_algorithm: str = "keyword"  # "keyword", "semantic", "hybrid"
    similarity_threshold: float = 0.5
    max_results: int = 10

    # Learning settings
    enable_learning: bool = True
    feedback_decay: float = 0.95


class KnowledgeBase(ABC):
    """
    Abstract base class for knowledge base storage.

    A KnowledgeBase stores and retrieves expertise patterns
    that can be matched against user queries.
    """

    def __init__(self, config: KnowledgeBaseConfig):
        self.config = config
        self._patterns: List[Dict[str, Any]] = []
        self._pattern_index: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    @abstractmethod
    async def load_patterns(self) -> List[Dict[str, Any]]:
        """
        Load all patterns from storage.

        Returns:
            List of all patterns.
        """
        pass

    @abstractmethod
    async def save_pattern(self, pattern: Dict[str, Any]) -> None:
        """Save a pattern to storage."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search patterns by query text.

        Args:
            query: Search query
            category: Optional category filter
            limit: Max results

        Returns:
            List of matching patterns.
        """
        pass

    @abstractmethod
    async def find_similar(
        self,
        query: str,
        threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find patterns similar to query.

        Returns list of (pattern, similarity_score) tuples.
        """
        pass

    @abstractmethod
    async def add_pattern(self, pattern: Dict[str, Any]) -> str:
        """
        Add a new pattern.

        Returns:
            Pattern ID.
        """
        pass

    @abstractmethod
    async def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing pattern."""
        pass

    @abstractmethod
    async def delete_pattern(self, pattern_id: str) -> None:
        """Delete a pattern."""
        pass

    @abstractmethod
    async def record_feedback(
        self,
        pattern_id: str,
        feedback: Dict[str, Any]
    ) -> None:
        """Record user feedback for learning."""
        pass

    @abstractmethod
    def get_patterns_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all patterns in a category."""
        pass

    @abstractmethod
    def get_all_categories(self) -> List[str]:
        """Get all categories."""
        pass

    def is_loaded(self) -> bool:
        """Check if patterns have been loaded."""
        return self._loaded

    def get_pattern_count(self) -> int:
        """Get total number of patterns."""
        return len(self._patterns)

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by ID."""
        return self._pattern_index.get(pattern_id)
