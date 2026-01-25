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
Generic Domain - Fully configurable domain that loads from JSON.

No custom code required. Domains are defined entirely by configuration files.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
import sys
import logging

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.domain import Domain, DomainConfig, CollectorType
from core.specialist import Specialist
from core.knowledge_base import KnowledgeBase, KnowledgeBaseConfig
from core.knowledge_base_plugin import KnowledgeBasePlugin
from core.router_plugin import RouterPlugin, RouteResult
from core.formatter_plugin import FormatterPlugin, FormattedResponse
from core.enrichment_plugin import EnrichmentPlugin, EnrichmentContext
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
        self._config_path: Optional[Path] = None
        self._specialists: Dict[str, 'GenericSpecialist'] = {}
        self._router: Optional[RouterPlugin] = None
        self._formatter: Optional[FormatterPlugin] = None
        self._enrichers: List[EnrichmentPlugin] = []

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
        # Prevent duplicate initialization
        if self._initialized:
            return

        # Load domain configuration
        await self._load_domain_config()

        # Initialize knowledge base
        await self._initialize_knowledge_base()

        # Initialize specialists from config
        self._initialize_specialists()

        # Initialize router plugin
        await self._initialize_router()

        # Initialize formatter plugin
        self._initialize_formatter()

        # Initialize enrichment plugins
        self._initialize_enrichers()

        self._initialized = True

    async def _load_domain_config(self) -> None:
        """Load domain.json configuration file."""
        config_file = Path(self.config.pattern_storage_path) / "domain.json"

        # Store config path for later reload
        self._config_path = config_file

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
                    pattern_schema=self.config.pattern_schema,
                    similarity_threshold=kb_config_spec.get("similarity_threshold", 0.5)
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
            pattern_schema=self.config.pattern_schema,
            similarity_threshold=kb_config_spec.get("similarity_threshold", 0.5)
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

    async def _initialize_router(self) -> None:
        """
        Initialize router plugin from configuration.

        Loads router plugin from domain.json or uses default confidence-based router.
        """
        router_config = self._domain_config.get("router", {})

        if router_config:
            # Load custom router plugin
            router_module = router_config.get("module", "plugins.routers.confidence_router")
            router_class = router_config.get("class", "ConfidenceBasedRouter")

            try:
                # Dynamically import the router plugin
                module = importlib.import_module(router_module)
                router_plugin_class = getattr(module, router_class)

                # Instantiate router with config
                self._router = router_plugin_class(router_config.get("config", {}))
                print(f"  Router: {self._router.name} (plugin: {router_class})")
                return

            except (ImportError, AttributeError) as e:
                print(f"  Warning: Failed to load router plugin {router_class}: {e}")
                print(f"  Falling back to default confidence-based router")

        # Default: Use ConfidenceBasedRouter
        from plugins.routers.confidence_router import ConfidenceBasedRouter
        self._router = ConfidenceBasedRouter()
        print(f"  Router: {self._router.name} (default)")

    def _initialize_formatter(self) -> None:
        """
        Initialize formatter plugin from configuration.

        Loads formatter plugin from domain.json or uses default MarkdownFormatter.
        """
        formatter_config = self._domain_config.get("formatter", {})

        if formatter_config:
            # Load custom formatter plugin
            formatter_module = formatter_config.get("module", "plugins.formatters.markdown_formatter")
            formatter_class = formatter_config.get("class", "MarkdownFormatter")

            try:
                # Dynamically import the formatter plugin
                module = importlib.import_module(formatter_module)
                formatter_plugin_class = getattr(module, formatter_class)

                # Instantiate formatter with config
                self._formatter = formatter_plugin_class(formatter_config.get("config", {}))
                print(f"  Formatter: {self._formatter.name} (plugin: {formatter_class})")
                return

            except (ImportError, AttributeError) as e:
                print(f"  Warning: Failed to load formatter plugin {formatter_class}: {e}")
                print(f"  Falling back to default Markdown formatter")

        # Default: Use MarkdownFormatter
        from plugins.formatters.markdown_formatter import MarkdownFormatter
        self._formatter = MarkdownFormatter()
        print(f"  Formatter: {self._formatter.name} (default)")

    def _add_default_llm_fallback(self) -> None:
        """
        Add default LLM fallback enricher for all domains.

        This ensures every domain has LLM fallback capability when pattern matching fails.
        """
        try:
            from plugins.enrichers.llm_enricher import LLMFallbackEnricher

            # Default config for all domains
            default_config = {
                "mode": "fallback",
                "min_confidence": 0.30,
                "model": "glm-4.7",
                "max_patterns": 3
            }

            enricher = LLMFallbackEnricher(default_config)
            self._enrichers.append(enricher)
            print(f"  Enricher: {enricher.name} (default LLM fallback)")

        except ImportError as e:
            print(f"  Warning: Could not load default LLM fallback: {e}")

    def _initialize_enrichers(self) -> None:
        """
        Initialize enrichment plugins from configuration.

        Loads enrichment plugins from domain.json or uses defaults.
        Enrichers run in sequence between specialist and formatter.
        """
        enrichers_config = self._domain_config.get("enrichers", [])

        if not enrichers_config:
            # No enrichers configured - add default LLM fallback
            print(f"  No enrichers configured - adding default LLM fallback")
            self._add_default_llm_fallback()
            return

        # Load configured enrichers
        has_llm_fallback = False
        for idx, enricher_config in enumerate(enrichers_config):
            if not enricher_config.get("enabled", True):
                continue

            try:
                # Dynamically import the enricher plugin
                module_path = enricher_config["module"]
                class_name = enricher_config["class"]

                module = importlib.import_module(module_path)
                enricher_class = getattr(module, class_name)

                # Instantiate enricher with config
                enricher = enricher_class(enricher_config.get("config", {}))
                self._enrichers.append(enricher)

                # Check if this is an LLM enricher (any LLM-based enricher)
                if class_name in ('LLMFallbackEnricher', 'LLMEnricher', 'LLMSummarizerEnricher', 'LLMExplanationEnricher'):
                    has_llm_fallback = True

                print(f"  Enricher: {enricher.name} (plugin: {class_name})")

            except (ImportError, AttributeError) as e:
                print(f"  Warning: Failed to load enricher plugin {enricher_config.get('class')}: {e}")
            except Exception as e:
                print(f"  Warning: Unexpected error loading enricher {enricher_config.get('class')}: {e}")

        # ALWAYS add LLM fallback as the last enricher if not already present
        # This ensures all domains have LLM fallback when patterns are weak or missing
        # UNLESS the domain has explicitly disabled it by having a disabled LLM fallback in config
        has_llm_fallback_in_config = any(
            e.get('class') == 'LLMFallbackEnricher' for e in enrichers_config
        )
        if not has_llm_fallback and not has_llm_fallback_in_config:
            print(f"  No LLM fallback enricher found - adding default LLM fallback")
            self._add_default_llm_fallback()
        elif has_llm_fallback_in_config and not has_llm_fallback:
            print(f"  LLM fallback explicitly disabled in config - skipping default fallback")

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: Optional['EnrichmentContext'] = None
    ) -> Dict[str, Any]:
        """
        Apply all enrichers to the response data.

        Enrichers run in sequence, each can modify the response data.
        This is called after specialist processing but before formatting.

        Args:
            response_data: The response data to enrich
            context: Optional enrichment context with domain info

        Returns:
            Enriched response data
        """
        if not self._enrichers:
            # No enrichers configured
            return response_data

        # Create enrichment context if not provided
        if context is None:
            from core.enrichment_plugin import EnrichmentContext
            context = EnrichmentContext(
                domain_id=self.domain_id,
                specialist_id=response_data.get('specialist_id', ''),
                query=response_data.get('query', ''),
                knowledge_base=self._knowledge_base
            )

        # Apply each enricher in sequence
        for idx, enricher in enumerate(self._enrichers):
            try:
                response_data = await enricher.enrich(response_data, context)
            except Exception as e:
                print(f"  Warning: Enricher {enricher.name} failed: {e}")
                # Continue with other enrichers even if one fails

        return response_data

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

        Uses the router plugin to determine which specialist should handle the query.
        For backward compatibility, returns the first specialist from the route result.
        """
        if not self._specialists:
            return None

        # Use router if available
        if self._router:
            import asyncio
            try:
                # Try to get route result synchronously
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, we can't await - fall back to synchronous
                    return self._get_specialist_sync(query)
                else:
                    # Run the async route method
                    route_result = loop.run_until_complete(
                        self._router.route(query, self._specialists)
                    )
                    if route_result.specialist_ids:
                        return self._specialists.get(route_result.specialist_ids[0])
            except Exception:
                # Fall back to synchronous method
                pass

        # Fallback to synchronous method
        return self._get_specialist_sync(query)

    def _get_specialist_sync(self, query: str) -> Optional[Specialist]:
        """Synchronous fallback for specialist selection."""
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

    async def route_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> RouteResult:
        """
        Route a query using the router plugin.

        This is the preferred method for routing queries as it returns
        full routing information including strategy and reasoning.

        Args:
            query: The user's query
            context: Additional context for routing decisions

        Returns:
            RouteResult with specialist IDs and routing metadata
        """
        if not self._router:
            # Fallback to default router
            from plugins.routers.confidence_router import ConfidenceBasedRouter
            self._router = ConfidenceBasedRouter()

        return await self._router.route(query, self._specialists, context)

    def get_router(self) -> Optional[RouterPlugin]:
        """Get the router plugin instance."""
        return self._router

    def get_formatter(self) -> Optional[FormatterPlugin]:
        """Get the default formatter plugin instance."""
        return self._formatter

    def get_formatter_for_type(self, format_type: str) -> Optional[FormatterPlugin]:
        """
        Get a formatter for a specific format type.

        This allows runtime format overrides (e.g., API client requests JSON).

        Args:
            format_type: The format type (e.g., "json", "compact", "markdown")

        Returns:
            FormatterPlugin instance or None if format not supported
        """
        format_type = format_type.lower()

        # Check if current formatter supports this type
        if self._formatter and self._formatter.supports_format(format_type):
            return self._formatter

        # Otherwise, try to load the appropriate formatter
        formatter_map = {
            "json": ("plugins.formatters.json_formatter", "JSONFormatter"),
            "json-compact": ("plugins.formatters.json_formatter", "CompactJSONFormatter"),
            "compact": ("plugins.formatters.compact_formatter", "CompactFormatter"),
            "terminal": ("plugins.formatters.compact_formatter", "CompactFormatter"),
            "cli": ("plugins.formatters.compact_formatter", "CompactFormatter"),
            "ultra-compact": ("plugins.formatters.compact_formatter", "UltraCompactFormatter"),
            "minimal": ("plugins.formatters.compact_formatter", "UltraCompactFormatter"),
            "names-only": ("plugins.formatters.compact_formatter", "UltraCompactFormatter"),
            "markdown": ("plugins.formatters.markdown_formatter", "MarkdownFormatter"),
            "md": ("plugins.formatters.markdown_formatter", "MarkdownFormatter"),
            "table": ("plugins.formatters.compact_formatter", "TableFormatter"),
            "tabular": ("plugins.formatters.compact_formatter", "TableFormatter"),
            "html": ("plugins.formatters.html_formatter", "HTMLFormatter"),
            "htm": ("plugins.formatters.html_formatter", "HTMLFormatter"),
            "html-simple": ("plugins.formatters.html_formatter", "SimpleHTMLFormatter"),
            "slack": ("plugins.formatters.slack_formatter", "SlackFormatter"),
            "slack-blocks": ("plugins.formatters.slack_formatter", "SlackFormatter"),
            "slack-md": ("plugins.formatters.slack_formatter", "SlackMarkdownFormatter"),
            "slack-attachment": ("plugins.formatters.slack_formatter", "SlackAttachmentFormatter"),
        }

        if format_type in formatter_map:
            module_path, class_name = formatter_map[format_type]
            try:
                module = importlib.import_module(module_path)
                formatter_class = getattr(module, class_name)
                return formatter_class()
            except (ImportError, AttributeError):
                pass

        # Fallback to current formatter
        return self._formatter

    async def format_response(
        self,
        response_data: Dict[str, Any],
        format_type: Optional[str] = None
    ) -> FormattedResponse:
        """
        Format a response using the appropriate formatter.

        Enrichment pipeline: Specialist → [Enrichers] → Formatter

        Args:
            response_data: The response data from a specialist
            format_type: Optional format override (e.g., "json", "compact")

        Returns:
            FormattedResponse with formatted content
        """
        # Run enrichment plugins before formatting
        enriched_data = response_data
        if self._enrichers:
            # Create enrichment context
            context = EnrichmentContext(
                domain_id=self.domain_id,
                specialist_id=response_data.get("specialist_id", "unknown"),
                query=response_data.get("query", ""),
                knowledge_base=self._knowledge_base,
                metadata={"format_type": format_type or "default"}
            )

            # Run each enricher in sequence
            for enricher in self._enrichers:
                # Skip enricher if format not supported
                if enricher.supports_format(format_type or "markdown"):
                    enriched_data = await enricher.enrich(enriched_data, context)

        # Get formatter
        if format_type:
            formatter = self.get_formatter_for_type(format_type)
        else:
            formatter = self._formatter

        if not formatter:
            # Ultimate fallback
            from plugins.formatters.markdown_formatter import MarkdownFormatter
            formatter = MarkdownFormatter()

        # Format the enriched response
        return formatter.format(enriched_data)

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

    async def reload(self) -> None:
        """
        Reload domain configuration from the JSON file.

        Called when domain.json is updated externally.
        Reloads configuration and re-initializes specialists.
        """
        if not self._config_path or not self._config_path.exists():
            logger.warning(f"Cannot reload domain: config path not set or missing")
            return

        logger.info(f"Reloading domain config from: {self._config_path}")

        # Load the updated configuration
        try:
            with open(self._config_path, 'r') as f:
                self._domain_config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load domain config: {e}")
            return

        # Re-initialize specialists with new configuration
        old_specialists = self._specialists.copy()
        self._specialists.clear()

        # Load from plugins (same logic as _initialize_specialists)
        plugins_config = self._domain_config.get("plugins", [])
        if plugins_config:
            import importlib
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
                    logger.debug(f"  Reloaded specialist: {plugin_config['plugin_id']}")

                except (ImportError, AttributeError) as e:
                    logger.warning(f"  Failed to reload plugin {plugin_config.get('plugin_id')}: {e}")
        else:
            logger.warning(f"  No plugins configured in domain {self.domain_id}")

        logger.info(f"Domain reload complete: {self.domain_id}")

    async def cleanup(self) -> None:
        """Clean up domain resources."""
        self._specialists.clear()
        self._initialized = False

    @property
    def knowledge_base(self) -> Optional[KnowledgeBase]:
        """Get the knowledge base instance."""
        return self._knowledge_base
