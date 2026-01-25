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
Research Strategy Base Interface

Provides abstract interface for different research strategies used by
LLM Fallback Enricher and Surveyor.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Result from a research strategy."""
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any]


class ResearchStrategy(ABC):
    """
    Abstract base class for research strategies.

    Research strategies are used to gather context information when
    patterns are not found or when additional context is needed.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the research strategy.

        Args:
            config: Strategy-specific configuration
        """
        self.config = config

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for relevant information based on the query.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            List of search results with content and metadata
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the research strategy.

        Called once when the strategy is first loaded.
        Use this to set up resources like database connections, indexes, etc.
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources used by the strategy.

        Called when the strategy is being unloaded.
        """
        pass

    def get_strategy_name(self) -> str:
        """Return the name of this strategy."""
        return self.__class__.__name__

    def get_strategy_type(self) -> str:
        """Return the type identifier for this strategy."""
        return self.__class__.__name__.replace('Strategy', '').lower()
