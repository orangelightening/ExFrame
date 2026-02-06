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
Domain Interface - Abstract base class for all domain implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum


class CollectorType(Enum):
    """Types of data collectors."""
    WEB_SCRAPER = "web_scraper"
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    PROMETHEUS = "prometheus"
    LOKI = "loki"
    SSH = "ssh"
    RPC = "rpc"
    CUSTOM = "custom"


@dataclass
class DomainConfig:
    """Configuration for a specific domain."""
    domain_id: str
    domain_name: str
    version: str
    description: str

    # Domain type (1-5)
    domain_type: Optional[str] = None

    # LLM temperature
    temperature: Optional[float] = None

    # Data sources
    data_sources: List[str] = field(default_factory=list)
    default_collector_type: CollectorType = CollectorType.FILE_SYSTEM

    # Taxonomy
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Knowledge base settings
    pattern_storage_path: str = ""
    pattern_format: str = "json"  # 'yaml' or 'json'
    pattern_schema: Dict[str, Any] = field(default_factory=dict)

    # Feature flags
    enabled_features: List[str] = field(default_factory=list)

    # Domain-specific settings
    domain_settings: Dict[str, Any] = field(default_factory=dict)


class Domain(ABC):
    """
    Abstract base class for all domain implementations.

    A Domain represents a specific area of expertise (e.g., Cooking, Python, DIY)
    with its own data collectors, specialists, and knowledge base.
    """

    def __init__(self, config: DomainConfig):
        self.config = config
        self._collectors: Dict[str, 'Collector'] = {}
        self._specialists: Dict[str, 'Specialist'] = {}
        self._initialized = False

    @property
    @abstractmethod
    def domain_id(self) -> str:
        """Unique identifier for this domain."""
        pass

    @property
    @abstractmethod
    def domain_name(self) -> str:
        """Human-readable name."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize domain-specific resources."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of domain services.

        Returns:
            Dict with health status information.
        """
        pass

    @abstractmethod
    def get_collector(self, collector_type: str) -> Optional['Collector']:
        """Get a collector instance by type."""
        pass

    @abstractmethod
    def get_specialist(self, specialist_id: str) -> Optional['Specialist']:
        """Get a specialist instance by ID."""
        pass

    @abstractmethod
    def get_specialist_for_query(self, query: str) -> Optional['Specialist']:
        """
        Select appropriate specialist based on query keywords.

        Returns the specialist with highest confidence score for handling this query.
        """
        pass

    @abstractmethod
    def list_specialists(self) -> List[str]:
        """List available specialist IDs."""
        pass

    @abstractmethod
    def list_collectors(self) -> List[str]:
        """List available collector types."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up domain resources."""
        pass

    def is_initialized(self) -> bool:
        """Check if domain has been initialized."""
        return self._initialized
