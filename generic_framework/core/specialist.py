"""
Specialist Interface - Abstract base class for domain specialists.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class SpecialistConfig:
    """Configuration for a domain specialist."""
    specialist_id: str
    name: str
    description: str = ""

    # Expertise areas
    expertise_keywords: List[str] = field(default_factory=list)
    expertise_categories: List[str] = field(default_factory=list)

    # Knowledge base
    knowledge_categories: List[str] = field(default_factory=list)
    pattern_filters: Dict[str, Any] = field(default_factory=dict)

    # Response preferences
    response_format: str = "structured"  # "structured", "narrative", "concise"
    include_examples: bool = True
    confidence_threshold: float = 0.6


class Specialist(ABC):
    """
    Abstract base class for domain specialists.

    A Specialist is an expert in a specific area within a domain
    (e.g., Baking Specialist within the Cooking domain).
    """

    def __init__(self, config: SpecialistConfig, knowledge_base: 'KnowledgeBase'):
        self.config = config
        self.knowledge_base = knowledge_base

    @property
    @abstractmethod
    def specialist_id(self) -> str:
        """Unique identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """
        Return confidence score for handling this query (0-1).

        Higher score indicates better fit for this specialist.
        """
        pass

    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query within this specialist's domain.

        Args:
            query: User's question
            context: Optional additional context (system state, etc.)

        Returns:
            Dict with answer and metadata.
        """
        pass

    @abstractmethod
    def get_relevant_patterns(self, query: str) -> List[Any]:
        """
        Get relevant knowledge patterns for a query.

        Returns list of patterns from knowledge base.
        """
        pass

    @abstractmethod
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format response for user consumption."""
        pass

    def matches_keywords(self, query: str) -> bool:
        """Quick check if query matches any expertise keywords."""
        query_lower = query.lower()
        return any(keyword.lower() in query_lower for keyword in self.config.expertise_keywords)
