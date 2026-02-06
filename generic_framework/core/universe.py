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
Universe - Runtime isolation boundary for ExFrame.

A Universe is a complete, self-contained configuration of domains, patterns,
search strategies, and plugins. Each universe can be loaded independently,
merged with another universe, or remain completely isolated.

Universe Identity: ASCII text identifier (e.g., "default", "testing", "staging")
"""

import asyncio
import yaml
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

from .domain import Domain, DomainConfig
from .generic_domain import GenericDomain
from .factory import DomainFactory
from assist.engine import GenericAssistantEngine


logger = logging.getLogger(__name__)


class UniverseMergeStrategy(Enum):
    """How to handle conflicts during universe merge."""
    SOURCE_WINS = "source_wins"      # Source overwrites target
    TARGET_WINS = "target_wins"      # Target keeps its values
    MERGE_PATTERNS = "merge"         # Combine pattern sets (deduplicated)
    FAIL_ON_CONFLICT = "fail"        # Error on conflict


class UniverseState(Enum):
    """Runtime state of a universe."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"


@dataclass
class DomainUniverseConfig:
    """Configuration for a domain within a universe."""
    domain_id: str
    enabled: bool = True
    priority: int = 0
    config_override: Optional[Dict[str, Any]] = None


@dataclass
class UniverseConfig:
    """Configuration for a universe."""
    # Identity
    universe_id: str
    name: str
    description: str = ""

    # Runtime behavior
    load_on_startup: bool = False
    is_default: bool = False

    # Universe-level defaults
    defaults: Dict[str, Any] = field(default_factory=dict)

    # Domain configurations
    domains: Dict[str, DomainUniverseConfig] = field(default_factory=dict)

    # Paths (relative to universe base)
    domains_path: str = "domains"
    plugins_path: str = "plugins"

    # Metadata
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "system"

    # Merge settings
    merge_strategy: UniverseMergeStrategy = UniverseMergeStrategy.MERGE_PATTERNS


@dataclass
class UniverseMeta:
    """Metadata about a universe."""
    universe_id: str
    name: str
    description: str
    state: UniverseState
    domain_count: int
    total_patterns: int
    version: str
    created_at: str
    loaded_at: Optional[str] = None
    checksum: Optional[str] = None


class UniverseDomainFactory(DomainFactory):
    """
    Universe-scoped domain factory.

    Unlike the global DomainFactory which uses classmethods and global state,
    this factory is instance-based and scoped to a specific universe.
    """

    def __init__(self, universe_id: str, universe_base_path: Path):
        """
        Initialize universe-scoped factory.

        Args:
            universe_id: The universe this factory belongs to
            universe_base_path: Base path for this universe's data
        """
        self.universe_id = universe_id
        self._domains: Dict[str, Type[Domain]] = {}
        self._config_base_path = universe_base_path / "domains"

    def set_config_path(self, base_path: str) -> None:
        """Set the base path for domain configuration files."""
        self._config_base_path = self._config_base_path.parent / base_path

    def create_domain(
        self,
        domain_id: str,
        domain_config: Optional[DomainConfig] = None,
        config_path: Optional[str] = None
    ) -> Domain:
        """
        Create a domain instance within this universe.

        Args:
            domain_id: Domain identifier
            domain_config: Optional pre-built DomainConfig
            config_path: Optional path to YAML config file

        Returns:
            Domain instance (GenericDomain by default)
        """
        # Use GenericDomain as the default
        domain_class = GenericDomain

        # Build config if not provided
        if domain_config is None:
            if config_path is None:
                config_path = self._config_base_path / domain_id / "domain.json"

            config_path = Path(config_path)
            if not config_path.exists():
                # Create minimal config for GenericDomain
                domain_config = DomainConfig(
                    domain_id=domain_id,
                    domain_name=f"Auto-loaded: {domain_id}",
                    version="1.0.0",
                    description=f"Dynamically loaded domain: {domain_id}",
                    pattern_storage_path=str(self._config_base_path / domain_id),
                    pattern_format="json",
                    pattern_schema={},
                    categories=[],
                    tags=[],
                    domain_type=None,
                    temperature=None
                )
            else:
                # Load from existing config
                import json
                with open(config_path, 'r') as f:
                    data = json.load(f)
                domain_config = DomainConfig(**data)

        return domain_class(domain_config)


class Universe:
    """
    A Universe is a complete, self-contained runtime environment.

    Each universe has:
    - Its own domain factory (scoped registration)
    - Its own set of domains and engines
    - Its own configuration
    - Isolated pattern storage
    - Optional universe-specific plugins
    """

    def __init__(self, config: UniverseConfig, base_path: Path):
        """
        Initialize a universe.

        Args:
            config: Universe configuration
            base_path: Base path for universe data
        """
        self.config = config
        self.base_path = base_path
        self.domains_path = base_path / config.domains_path
        self.plugins_path = base_path / config.plugins_path

        # Universe state
        self._state = UniverseState.UNLOADED
        self._loaded_at = None

        # Isolated components
        self.factory = UniverseDomainFactory(config.universe_id, base_path)
        self.domains: Dict[str, Domain] = {}
        self.engines: Dict[str, GenericAssistantEngine] = {}

        # Lock for thread safety
        self._lock = asyncio.Lock()

        logger.info(f"Universe '{config.universe_id}' initialized at {base_path}")

    @property
    def universe_id(self) -> str:
        """Get universe identifier."""
        return self.config.universe_id

    @property
    def state(self) -> UniverseState:
        """Get current universe state."""
        return self._state

    async def load(self) -> None:
        """
        Load the universe - discover and initialize all enabled domains.

        This is called on-demand or at startup if load_on_startup is True.
        """
        async with self._lock:
            if self._state != UniverseState.UNLOADED:
                logger.warning(f"Universe '{self.universe_id}' already loaded")
                return

            self._state = UniverseState.LOADING
            logger.info(f"Loading universe '{self.universe_id}'...")

            try:
                # Ensure domains directory exists
                self.domains_path.mkdir(parents=True, exist_ok=True)

                # Load domains based on configuration
                for domain_id, domain_config in self.config.domains.items():
                    if domain_config.enabled:
                        await self._load_domain(domain_id, domain_config)
                    else:
                        logger.debug(f"Skipping disabled domain: {domain_id}")

                # Auto-discover any domains not in config
                await self._auto_discover_domains()

                self._state = UniverseState.LOADED
                self._loaded_at = datetime.now().isoformat()
                logger.info(
                    f"Universe '{self.universe_id}' loaded: "
                    f"{len(self.domains)} domains, "
                    f"{sum(len(d.knowledge_base._patterns) if hasattr(d, 'knowledge_base') and d.knowledge_base else 0 for d in self.domains.values())} patterns"
                )

            except Exception as e:
                self._state = UniverseState.ERROR
                logger.error(f"Failed to load universe '{self.universe_id}': {e}")
                raise

    async def _load_domain(self, domain_id: str, domain_config: DomainUniverseConfig) -> None:
        """Load a single domain into the universe."""
        domain_path = self.domains_path / domain_id

        if not domain_path.exists():
            logger.warning(f"Domain path does not exist: {domain_path}")
            return

        try:
            # Create domain config with overrides
            base_config = DomainConfig(
                domain_id=domain_id,
                domain_name=f"{self.universe_id}:{domain_id}",
                version="1.0.0",
                description=f"Domain {domain_id} in universe {self.universe_id}",
                pattern_storage_path=str(domain_path),
                pattern_format="json",
                pattern_schema={},
                domain_type=None,
                temperature=None
            )

            # Apply universe-level overrides
            if domain_config.config_override:
                for key, value in domain_config.config_override.items():
                    setattr(base_config, key, value)

            # Create domain using universe factory
            domain = self.factory.create_domain(domain_id, base_config)
            await domain.initialize()

            # Create engine
            engine = GenericAssistantEngine(domain)
            await engine.initialize()

            # Store in universe
            self.domains[domain_id] = domain
            self.engines[domain_id] = engine

            pattern_count = len(domain.knowledge_base._patterns) if hasattr(domain, 'knowledge_base') and domain.knowledge_base else 0
            logger.info(f"  ✓ Loaded domain: {domain_id} ({pattern_count} patterns)")

        except Exception as e:
            logger.error(f"  ✗ Failed to load domain {domain_id}: {e}")

    async def _auto_discover_domains(self) -> None:
        """Auto-discover domains from filesystem that aren't in config."""
        for domain_dir in self.domains_path.iterdir():
            if not domain_dir.is_dir():
                continue

            domain_id = domain_dir.name

            # Skip if already loaded
            if domain_id in self.domains:
                continue

            # Check for patterns.json
            patterns_file = domain_dir / "patterns.json"
            if not patterns_file.exists():
                continue

            logger.info(f"Auto-discovering domain: {domain_id}")

            # Create minimal config
            domain_config = DomainUniverseConfig(
                domain_id=domain_id,
                enabled=True,
                priority=0
            )

            await self._load_domain(domain_id, domain_config)

    async def activate(self) -> None:
        """Mark universe as active for serving queries."""
        if self._state != UniverseState.LOADED:
            await self.load()
        self._state = UniverseState.ACTIVE
        logger.info(f"Universe '{self.universe_id}' is now ACTIVE")

    async def unload(self) -> None:
        """Unload universe and cleanup resources."""
        async with self._lock:
            logger.info(f"Unloading universe '{self.universe_id}'...")

            # Cleanup all engines and domains
            for engine in self.engines.values():
                try:
                    await engine.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up engine: {e}")

            for domain in self.domains.values():
                try:
                    await domain.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up domain: {e}")

            self.domains.clear()
            self.engines.clear()
            self._state = UniverseState.UNLOADED
            self._loaded_at = None

            logger.info(f"Universe '{self.universe_id}' unloaded")

    def get_domain(self, domain_id: str) -> Optional[Domain]:
        """Get a domain by ID."""
        return self.domains.get(domain_id)

    def get_engine(self, domain_id: str) -> Optional[GenericAssistantEngine]:
        """Get an engine by domain ID."""
        return self.engines.get(domain_id)

    def list_domains(self) -> List[str]:
        """List loaded domain IDs."""
        return list(self.domains.keys())

    def get_meta(self) -> UniverseMeta:
        """Get universe metadata."""
        total_patterns = sum(
            len(d.knowledge_base._patterns) if hasattr(d, 'knowledge_base') and d.knowledge_base else 0
            for d in self.domains.values()
        )

        return UniverseMeta(
            universe_id=self.config.universe_id,
            name=self.config.name,
            description=self.config.description,
            state=self._state,
            domain_count=len(self.domains),
            total_patterns=total_patterns,
            version=self.config.version,
            created_at=self.config.created_at,
            loaded_at=self._loaded_at,
            checksum=self._compute_checksum()
        )

    def _compute_checksum(self) -> str:
        """Compute checksum of universe configuration for identity verification."""
        # Create a deterministic hash of the config
        config_str = f"{self.config.universe_id}:{self.config.version}:{self.config.created_at}"
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    async def merge_domain(self, other_domain: Domain, strategy: UniverseMergeStrategy) -> None:
        """
        Merge a domain from another universe into this one.

        Args:
            other_domain: Domain to merge
            strategy: Merge strategy for handling conflicts
        """
        domain_id = other_domain.config.domain_id

        if domain_id in self.domains:
            if strategy == UniverseMergeStrategy.FAIL_ON_CONFLICT:
                raise ValueError(f"Domain '{domain_id}' already exists in universe")
            elif strategy == UniverseMergeStrategy.TARGET_WINS:
                logger.info(f"Skipping existing domain: {domain_id} (target wins)")
                return
            elif strategy == UniverseMergeStrategy.SOURCE_WINS:
                # Remove existing domain
                await self._remove_domain(domain_id)

        # Import domain patterns
        if hasattr(other_domain, 'knowledge_base') and other_domain.knowledge_base:
            target_path = self.domains_path / domain_id
            target_path.mkdir(parents=True, exist_ok=True)

            patterns_file = target_path / "patterns.json"
            existing_patterns = []

            if patterns_file.exists() and strategy == UniverseMergeStrategy.MERGE_PATTERNS:
                import json
                with open(patterns_file, 'r') as f:
                    existing_patterns = json.load(f)

            # Merge patterns (deduplicate by ID)
            new_patterns = other_domain.knowledge_base._patterns
            merged_patterns = {p['id']: p for p in existing_patterns}
            merged_patterns.update({p['id']: p for p in new_patterns})

            # Write merged patterns
            with open(patterns_file, 'w') as f:
                json.dump(list(merged_patterns.values()), f, indent=2)

            logger.info(f"Merged {len(new_patterns)} patterns into {domain_id}")

    async def _remove_domain(self, domain_id: str) -> None:
        """Remove a domain from the universe."""
        if domain_id in self.engines:
            await self.engines[domain_id].cleanup()
            del self.engines[domain_id]

        if domain_id in self.domains:
            await self.domains[domain_id].cleanup()
            del self.domains[domain_id]


class UniverseManager:
    """
    Manager for multiple universes.

    Handles loading, merging, and lifecycle management of universes.
    """

    def __init__(self, universes_base_path: Path, default_universe_id: str = "default"):
        """
        Initialize universe manager.

        Args:
            universes_base_path: Base directory containing all universes
            default_universe_id: ID of the default universe to load
        """
        self.universes_base_path = universes_base_path
        self.default_universe_id = default_universe_id
        self.universes: Dict[str, Universe] = {}
        self._lock = asyncio.Lock()

        logger.info(f"UniverseManager initialized with base: {universes_base_path}")

    async def load_universe(self, universe_id: str) -> Universe:
        """
        Load a universe by ID.

        Args:
            universe_id: Universe identifier

        Returns:
            Loaded universe instance
        """
        async with self._lock:
            if universe_id in self.universes:
                return self.universes[universe_id]

            universe_path = self.universes_base_path / universe_id
            config_file = universe_path / "universe.yaml"

            if not config_file.exists():
                raise ValueError(f"Universe config not found: {config_file}")

            # Load configuration
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)

            # Extract universe config data
            universe_data = config_data.get('universe', config_data)

            # Convert domains dict to DomainUniverseConfig objects
            domains_data = universe_data.get('domains', {})
            domains_configs = {}
            for domain_id, domain_dict in domains_data.items():
                if isinstance(domain_dict, dict):
                    domains_configs[domain_id] = DomainUniverseConfig(
                        domain_id=domain_id,
                        **domain_dict
                    )
                else:
                    domains_configs[domain_id] = domain_dict

            universe_data['domains'] = domains_configs

            # Handle merge_strategy enum
            if 'merge_strategy' in universe_data:
                strategy_value = universe_data['merge_strategy']
                if isinstance(strategy_value, str):
                    try:
                        universe_data['merge_strategy'] = UniverseMergeStrategy(strategy_value)
                    except ValueError:
                        universe_data['merge_strategy'] = UniverseMergeStrategy.MERGE_PATTERNS

            config = UniverseConfig(**universe_data)

            # Create universe
            universe = Universe(config, universe_path)
            await universe.load()

            self.universes[universe_id] = universe
            return universe

    async def get_universe(self, universe_id: str) -> Optional[Universe]:
        """Get a loaded universe by ID."""
        return self.universes.get(universe_id)

    async def load_default(self) -> Universe:
        """Load the default universe."""
        return await self.load_universe(self.default_universe_id)

    def list_universes(self) -> List[str]:
        """List available universe IDs."""
        if not self.universes_base_path.exists():
            return []

        return [
            d.name for d in self.universes_base_path.iterdir()
            if d.is_dir() and (d / "universe.yaml").exists()
        ]

    def list_loaded_universes(self) -> List[str]:
        """List currently loaded universe IDs."""
        return list(self.universes.keys())

    async def create_universe(
        self,
        universe_id: str,
        name: str,
        description: str = "",
        base_on: Optional[str] = None
    ) -> Universe:
        """
        Create a new universe.

        Args:
            universe_id: Unique identifier for the universe
            name: Human-readable name
            description: Optional description
            base_on: Optional universe ID to copy configuration from

        Returns:
            Newly created universe
        """
        universe_path = self.universes_base_path / universe_id

        if universe_path.exists():
            raise ValueError(f"Universe already exists: {universe_id}")

        # Create directory structure
        universe_path.mkdir(parents=True, exist_ok=True)
        (universe_path / "domains").mkdir(exist_ok=True)
        (universe_path / "plugins").mkdir(exist_ok=True)

        # Create configuration
        if base_on:
            # Copy from existing universe
            base_universe = await self.load_universe(base_on)
            config = base_universe.config
            config.universe_id = universe_id
            config.name = name
            config.description = description
            config.is_default = False
        else:
            config = UniverseConfig(
                universe_id=universe_id,
                name=name,
                description=description,
                version="1.0.0"
            )

        # Write config
        config_file = universe_path / "universe.yaml"
        # Convert config to dict, handling enums properly
        config_dict = {}
        for key, value in config.__dict__.items():
            if isinstance(value, UniverseMergeStrategy):
                config_dict[key] = value.value
            elif isinstance(value, dict):
                # Handle nested dicts (like domains)
                config_dict[key] = {
                    k: v.value if isinstance(v, UniverseMergeStrategy) else v
                    for k, v in value.items()
                }
            else:
                config_dict[key] = value

        with open(config_file, 'w') as f:
            yaml.dump({'universe': config_dict}, f, default_flow_style=False)

        logger.info(f"Created universe: {universe_id} at {universe_path}")

        # Load and return
        return await self.load_universe(universe_id)

    async def merge_universes(
        self,
        source_id: str,
        target_id: str,
        strategy: UniverseMergeStrategy = UniverseMergeStrategy.MERGE_PATTERNS
    ) -> Dict[str, Any]:
        """
        Merge source universe into target universe.

        Args:
            source_id: Source universe ID
            target_id: Target universe ID
            strategy: Merge strategy

        Returns:
            Merge result summary
        """
        source = await self.load_universe(source_id)
        target = await self.load_universe(target_id)

        merged_domains = 0
        skipped_domains = 0
        failed_domains = 0

        for domain_id, domain in source.domains.items():
            try:
                await target.merge_domain(domain, strategy)
                merged_domains += 1
            except ValueError as e:
                logger.warning(f"Failed to merge domain {domain_id}: {e}")
                failed_domains += 1
            except Exception as e:
                logger.error(f"Error merging domain {domain_id}: {e}")
                failed_domains += 1

        return {
            "source": source_id,
            "target": target_id,
            "strategy": strategy.value,
            "merged_domains": merged_domains,
            "skipped_domains": skipped_domains,
            "failed_domains": failed_domains
        }

    async def unload_all(self) -> None:
        """Unload all universes."""
        for universe in self.universes.values():
            await universe.unload()
        self.universes.clear()
