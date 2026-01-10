"""
Generic Domain - Fully configurable domain that loads from JSON.

No custom code required. Domains are defined entirely by configuration files.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.domain import Domain, DomainConfig, CollectorType
from core.specialist import Specialist
from core.knowledge_base import KnowledgeBase, KnowledgeBaseConfig
from core.knowledge_base_plugin import KnowledgeBasePlugin
from knowledge.json_kb import JSONKnowledgeBase
import importlib


class GenericDomain(Domain):
    """
    Universal domain that loads configuration from JSON.

    Eliminates the need to write custom domain classes.
    Domains are now data-driven, not code-driven.
    """

    def __init__(self, config: DomainConfig):
        super().__init__(config)
        self._domain_config: Optional[Dict[str, Any]] = None
        self._knowledge_base: Optional[KnowledgeBase] = None
        self._specialists: Dict[str, 'GenericSpecialist'] = {}

    @property
    def domain_id(self) -> str:
        """Get domain ID from config or fallback to DomainConfig."""
        if self._domain_config:
            return self._domain_config.get("domain_id", self.config.domain_id)
        return self.config.domain_id

    @property
    def domain_name(self) -> str:
        """Get domain name from config."""
        if self._domain_config:
            return self._domain_config.get("domain_name", "Unknown Domain")
        return self.config.domain_name or "Unknown Domain"

    async def initialize(self) -> None:
        """
        Initialize domain by loading configuration from JSON.

        This replaces all the custom initialization code
        that used to be in every domain class.
        """
        # Load domain configuration
        await self._load_domain_config()

        # Initialize knowledge base
        await self._initialize_knowledge_base()

        # Initialize specialists from config
        self._initialize_specialists()

        self._initialized = True

    async def _load_domain_config(self) -> None:
        """Load domain.json configuration file."""
        config_file = Path(self.config.pattern_storage_path) / "domain.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self._domain_config = json.load(f)
            except json.JSONDecodeError as e:
                # If config is invalid, create default
                print(f"Warning: Invalid domain.json: {e}")
                self._domain_config = self._create_default_config()
        else:
            # No config file exists, create default
            self._domain_config = self._create_default_config()
            await self._save_domain_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default domain configuration."""
        return {
            "domain_id": self.config.domain_id,
            "domain_name": self.config.domain_name or self.config.domain_id.title(),
            "description": self.config.description or "",
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "specialists": [
                {
                    "specialist_id": "generalist",
                    "name": "General Specialist",
                    "description": f"General expert for {self.config.domain_id}",
                    "expertise_keywords": self.config.tags or [],
                    "expertise_categories": self.config.categories or [],
                    "confidence_threshold": 0.6,
                    "response_template": "structured"
                }
            ],
            "categories": self.config.categories or [],
            "tags": self.config.tags or [],
            "ui_config": {
                "placeholder_text": f"Ask about {self.config.domain_name.lower()}...",
                "example_queries": [],
                "icon": "📚",
                "color": "#2196F3"
            },
            "links": {
                "related_domains": [],
                "imports_patterns_from": [],
                "suggest_on_confidence_below": 0.3
            }
        }

    async def _save_domain_config(self) -> None:
        """Save domain configuration to file."""
        config_file = Path(self.config.pattern_storage_path) / "domain.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w') as f:
            json.dump(self._domain_config, f, indent=2)

    async def _initialize_knowledge_base(self) -> None:
        """
        Initialize knowledge base from configuration.

        Supports loading knowledge base plugins dynamically from domain.json.
        Falls back to JSONKnowledgeBase if no plugin specified.
        """
        # Check if domain config specifies a knowledge base plugin
        kb_config_spec = self._domain_config.get("knowledge_base", {})

        if kb_config_spec:
            # Load custom knowledge base plugin
            kb_module = kb_config_spec.get("module", "knowledge.json_kb")
            kb_class = kb_config_spec.get("class", "JSONKnowledgeBase")

            try:
                # Dynamically import the knowledge base plugin
                module = importlib.import_module(kb_module)
                kb_plugin_class = getattr(module, kb_class)

                # Create knowledge base config
                kb_config = KnowledgeBaseConfig(
                    storage_path=self.config.pattern_storage_path,
                    pattern_format=self.config.pattern_format,
                    pattern_schema=self.config.pattern_schema
                )

                # Instantiate plugin with additional config if provided
                kb_plugin = kb_plugin_class(kb_config)
                await kb_plugin.load_patterns()

                self._knowledge_base = kb_plugin
                print(f"  Knowledge Base: {kb_plugin.name} (plugin: {kb_class})")
                return

            except (ImportError, AttributeError) as e:
                print(f"  Warning: Failed to load KB plugin {kb_class}: {e}")
                print(f"  Falling back to JSONKnowledgeBase")

        # Default: Use JSONKnowledgeBase
        kb_config = KnowledgeBaseConfig(
            storage_path=self.config.pattern_storage_path,
            pattern_format=self.config.pattern_format,
            pattern_schema=self.config.pattern_schema
        )
        self._knowledge_base = JSONKnowledgeBase(kb_config)
        await self._knowledge_base.load_patterns()
        print(f"  Knowledge Base: {self._knowledge_base.name} (default)")

    def _initialize_specialists(self) -> None:
        """Initialize specialists from plugin configuration."""
        import importlib

        # Prefer plugins if available, otherwise fall back to old specialists config
        plugins_config = self._domain_config.get("plugins", [])
        specialists_config = self._domain_config.get("specialists", [])

        if plugins_config:
            # Load from plugins
            for plugin_config in plugins_config:
                if not plugin_config.get("enabled", True):
                    continue

                try:
                    # Dynamically import the plugin module
                    module_path = plugin_config["module"]
                    class_name = plugin_config["class"]

                    module = importlib.import_module(module_path)
                    plugin_class = getattr(module, class_name)

                    # Instantiate plugin with knowledge base and config
                    plugin = plugin_class(self._knowledge_base, plugin_config.get("config", {}))

                    # Store using plugin_id as specialist_id
                    self._specialists[plugin_config["plugin_id"]] = plugin

                except (ImportError, AttributeError) as e:
                    print(f"Warning: Failed to load plugin {plugin_config.get('plugin_id')}: {e}")

        elif specialists_config:
            # No GenericSpecialist fallback - plugins are required
            print(f"Warning: Domain {self.domain_id} has specialists config but no plugins. Plugins are now required.")
            print("Please configure plugins in domain.json")

    async def health_check(self) -> Dict[str, Any]:
        """Check health of domain services."""
        return {
            "domain": self.domain_id,
            "domain_name": self.domain_name,
            "status": "healthy",
            "patterns_loaded": self._knowledge_base.get_pattern_count() if self._knowledge_base else 0,
            "specialists_available": len(self._specialists),
            "categories": self._knowledge_base.get_all_categories() if self._knowledge_base else [],
            "config_file": str(Path(self.config.pattern_storage_path) / "domain.json"),
            "last_updated": self._domain_config.get("updated_at") if self._domain_config else None
        }

    def get_collector(self, collector_type: str) -> Optional['Collector']:
        """Get a collector instance by type."""
        # Generic domains don't use collectors
        return None

    def get_specialist(self, specialist_id: str) -> Optional[Specialist]:
        """Get a specialist instance by ID."""
        return self._specialists.get(specialist_id)

    def get_specialist_for_query(self, query: str) -> Optional[Specialist]:
        """
        Select the best specialist for a query.

        Uses confidence scoring to pick the specialist most capable
        of handling the query.
        """
        if not self._specialists:
            return None

        best_specialist = None
        best_score = 0.0

        for specialist_id, specialist in self._specialists.items():
            score = specialist.can_handle(query)

            # Get threshold - plugins have .threshold, GenericSpecialist has .config.confidence_threshold
            if hasattr(specialist, 'threshold'):
                threshold = specialist.threshold
            elif hasattr(specialist, 'config') and hasattr(specialist.config, 'confidence_threshold'):
                threshold = specialist.config.confidence_threshold
            else:
                threshold = 0.3  # Default threshold

            if score >= threshold and score > best_score:
                best_score = score
                best_specialist = specialist

        return best_specialist

    def list_specialists(self) -> List[str]:
        """List all specialist IDs."""
        return list(self._specialists.keys())

    def list_collectors(self) -> List[str]:
        """List available collector types."""
        return []  # Generic domains don't use collectors

    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration for this domain."""
        if self._domain_config:
            return self._domain_config.get("ui_config", {})
        return {
            "placeholder_text": f"Ask about {self.domain_name.lower()}...",
            "example_queries": [],
            "icon": "📚",
            "color": "#2196F3"
        }

    def get_linked_domains(self) -> List[str]:
        """Get list of linked domain IDs."""
        if self._domain_config and "links" in self._domain_config:
            return self._domain_config["links"].get("related_domains", [])
        return []

    async def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update domain configuration.

        Allows dynamic modification of domain settings.
        """
        if self._domain_config:
            self._domain_config.update(updates)
            self._domain_config["updated_at"] = datetime.utcnow().isoformat()
            await self._save_domain_config()

            # Reinitialize specialists if they were updated
            if "specialists" in updates:
                self._initialize_specialists()

    async def add_specialist(self, specialist_config: Dict[str, Any]) -> None:
        """Add a new specialist to the domain."""
        if not self._domain_config:
            self._domain_config = self._create_default_config()

        if "specialists" not in self._domain_config:
            self._domain_config["specialists"] = []

        self._domain_config["specialists"].append(specialist_config)
        await self._save_domain_config()
        self._initialize_specialists()

    async def cleanup(self) -> None:
        """Clean up domain resources."""
        self._specialists.clear()
        self._initialized = False

    @property
    def knowledge_base(self) -> Optional[KnowledgeBase]:
        """Get the knowledge base instance."""
        return self._knowledge_base
