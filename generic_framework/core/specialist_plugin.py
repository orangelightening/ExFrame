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
Specialist Plugin System

A specialist plugin is a module that answers questions in its domain.
The interface is intentionally simple: 3 methods.

No base class inheritance required. Just implement these 3 methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class SpecialistPlugin(ABC):
    """
    A specialist is a plugin that answers questions in its domain.

    Interface: 3 methods. That's all.
    """

    # Subclasses should define a name attribute
    name: str = "Specialist"

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """
        Can this specialist handle the query?

        Return: Confidence score 0.0 to 1.0
        """
        pass

    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process the query and return response data.

        Return: Dict with at least:
            - answer: str (the response text)
            - patterns: List[dict] (patterns used)
            - confidence: float (0.0 to 1.0)
        """
        pass

    @abstractmethod
    def format_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format the response for user consumption.

        Return: String to display to user
        """
        pass
