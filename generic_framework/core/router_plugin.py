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
Router Plugin System

A router plugin determines which specialist(s) should handle a query.
This enables different routing strategies beyond simple confidence scoring.

Router plugins can implement:
- Single-specialist routing (current behavior)
- Multi-specialist routing (parallel, sequential)
- Hierarchy routing (specialist → fallback → generalist)
- Category-based routing
- Custom routing logic
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class RouteResult:
    """
    Result of routing a query.

    Attributes:
        specialist_ids: List of specialist IDs to handle the query
        strategy: How to route ('single', 'parallel', 'sequential', 'fallback')
        confidence: Overall confidence score for this routing decision
        reasoning: Human-readable explanation of routing decision
        metadata: Additional routing information
    """
    specialist_ids: List[str]
    strategy: str = "single"
    confidence: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RouterPlugin(ABC):
    """
    A router plugin determines which specialist(s) should handle a query.

    The router is called for every query and decides:
    - Which specialist(s) should process the query
    - In what order (parallel, sequential, fallback)
    - How confident we are in this routing decision

    This enables complex routing strategies beyond simple confidence scoring.
    """

    name: str = "Router"

    @abstractmethod
    async def route(
        self,
        query: str,
        specialists: Dict[str, 'SpecialistPlugin'],
        context: Optional[Dict[str, Any]] = None
    ) -> RouteResult:
        """
        Determine which specialist(s) should handle the query.

        Args:
            query: The user's query
            specialists: Available specialists (id -> SpecialistPlugin)
            context: Additional context (domain info, query history, etc.)

        Returns:
            RouteResult with specialist IDs and routing strategy
        """
        pass

    async def validate_routing(
        self,
        result: RouteResult,
        available_specialists: Dict[str, 'SpecialistPlugin']
    ) -> bool:
        """
        Validate that the routing result is valid.

        Args:
            result: The routing result to validate
            available_specialists: Available specialists

        Returns:
            True if routing is valid, False otherwise
        """
        # Check that all specialist IDs exist
        for spec_id in result.specialist_ids:
            if spec_id not in available_specialists:
                return False

        # Check that strategy is valid
        valid_strategies = {'single', 'parallel', 'sequential', 'fallback'}
        if result.strategy not in valid_strategies:
            return False

        # Check confidence is in valid range
        if not 0.0 <= result.confidence <= 1.0:
            return False

        return True
