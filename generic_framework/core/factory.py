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
Domain Factory - Factory pattern for creating domain instances.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Type, Optional

from .domain import Domain, DomainConfig


class DomainFactory:
    """
    Factory for creating domain instances.

    Domains register themselves, then can be instantiated by domain_id.
    Configuration is loaded from YAML files in config/domains/.
    """

    _domains: Dict[str, Type[Domain]] = {}
    _config_base_path: str = "config/domains"

    @classmethod
    def register_domain(cls, domain_class: Type[Domain]) -> None:
        """
        Register a domain implementation class.

        The domain_id is extracted from the class name.
        Example: CookingDomain -> 'cooking'
        """
        # Extract domain_id from class name
        class_name = domain_class.__name__
        if class_name.endswith('Domain'):
            domain_id = class_name[:-6].lower()
        else:
            domain_id = class_name.lower()

        cls._domains[domain_id] = domain_class

    @classmethod
    def set_config_path(cls, base_path: str) -> None:
        """Set the base path for domain configuration files."""
        cls._config_base_path = base_path

    @classmethod
    def load_config(cls, config_path: str) -> DomainConfig:
        """
        Load domain configuration from YAML file.

        Args:
            config_path: Path to YAML config file

        Returns:
            DomainConfig instance
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)

        if 'domain' not in data:
            raise ValueError(f"Invalid config file: missing 'domain' section in {config_path}")

        return DomainConfig(**data['domain'])

    @classmethod
    def create_domain(
        cls,
        domain_id: str,
        config_path: Optional[str] = None
    ) -> Domain:
        """
        Create a domain instance.

        Args:
            domain_id: Domain identifier (e.g., 'cooking', 'python')
            config_path: Optional path to config file. If not provided,
                        uses default: {config_base_path}/{domain_id}.yaml

        Returns:
            Domain instance

        Raises:
            ValueError: If domain_id is not registered
        """
        if domain_id not in cls._domains:
            available = ', '.join(cls.list_domains())
            raise ValueError(
                f"Unknown domain: '{domain_id}'. Available: {available}"
            )

        domain_class = cls._domains[domain_id]

        # Load config
        if config_path is None:
            config_path = f"{cls._config_base_path}/{domain_id}.yaml"

        config = cls.load_config(config_path)

        return domain_class(config)

    @classmethod
    def list_domains(cls) -> List[str]:
        """List available domain types."""
        return list(cls._domains.keys())

    @classmethod
    def is_registered(cls, domain_id: str) -> bool:
        """Check if a domain is registered."""
        return domain_id in cls._domains

    @classmethod
    def get_domain_class(cls, domain_id: str) -> Optional[Type[Domain]]:
        """Get the domain class for a domain_id without instantiating."""
        return cls._domains.get(domain_id)
