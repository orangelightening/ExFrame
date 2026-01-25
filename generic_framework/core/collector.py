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
Collector Interface - Abstract base class for data collectors.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .domain import CollectorType


@dataclass
class CollectorConfig:
    """Configuration for a data collector."""
    collector_type: CollectorType
    name: str
    description: str = ""

    # Connection settings
    endpoint: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    headers: Dict[str, str] = field(default_factory=dict)

    # Domain-specific configuration
    scraping_rules: Dict[str, Any] = field(default_factory=dict)
    api_paths: Dict[str, str] = field(default_factory=dict)
    file_patterns: List[str] = field(default_factory=list)


class Collector(ABC):
    """
    Abstract base class for data collectors.

    A Collector gathers data from external sources (websites, APIs, files, etc.)
    for pattern extraction and knowledge building.
    """

    def __init__(self, config: CollectorConfig):
        self.config = config
        self._initialized = False

    @property
    @abstractmethod
    def collector_type(self) -> CollectorType:
        """Type of this collector."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the collector."""
        pass

    @abstractmethod
    async def collect(self, source: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Collect data from a source.

        Args:
            source: URL, file path, API endpoint, etc.
            params: Optional parameters for collection

        Returns:
            Dict containing collected data.
        """
        pass

    @abstractmethod
    async def collect_batch(self, sources: List[str]) -> List[Dict[str, Any]]:
        """
        Collect data from multiple sources.

        Args:
            sources: List of URLs, file paths, etc.

        Returns:
            List of collected data dicts.
        """
        pass

    @abstractmethod
    async def is_available(self, source: str) -> bool:
        """Check if source is available."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources."""
        pass

    def is_initialized(self) -> bool:
        """Check if collector has been initialized."""
        return self._initialized
