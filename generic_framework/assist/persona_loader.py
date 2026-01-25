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
Persona Loader

Loads and manages persona plugins from domain configuration.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from core.persona_plugin import PersonaPlugin
from plugins.personas import PersonaRegistry


class PersonaLoader:
    """
    Loads persona plugins based on domain configuration.

    Personas can be specified in domain.json under the plugins section,
    and referenced by specialist_id in the specialists section.
    """

    def __init__(self, universe_path: Optional[Path] = None):
        """
        Initialize the persona loader.

        Args:
            universe_path: Path to the universe directory containing domains
        """
        self.universe_path = universe_path
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the persona registry by discovering all personas."""
        if not self._initialized:
            PersonaRegistry.initialize()
            self._initialized = True

    def load_persona_for_specialist(
        self,
        domain_id: str,
        specialist_id: str,
        domain_config: Dict[str, Any]
    ) -> Optional[PersonaPlugin]:
        """
        Load the appropriate persona for a given specialist.

        Args:
            domain_id: The domain identifier
            specialist_id: The specialist identifier
            domain_config: The full domain configuration dict

        Returns:
            PersonaPlugin instance or None if no persona configured
        """
        # Ensure registry is initialized
        self.initialize()

        # Find the specialist in the domain config
        specialists = domain_config.get("specialists", [])
        specialist = None
        for spec in specialists:
            if spec.get("specialist_id") == specialist_id:
                specialist = spec
                break

        if not specialist:
            return None

        # Check if specialist has a persona_plugin reference
        persona_id = specialist.get("persona_plugin")
        if not persona_id:
            return None

        # Check for persona-specific config in the specialist
        persona_config = specialist.get("persona_config", {})

        # Load persona from registry
        persona = PersonaRegistry.create_instance(persona_id, persona_config)

        if persona:
            print(f"[PersonaLoader] Loaded persona '{persona_id}' for specialist '{specialist_id}'")
        else:
            print(f"[PersonaLoader] Warning: Persona '{persona_id}' not found in registry")

        return persona

    def load_persona_by_id(
        self,
        persona_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[PersonaPlugin]:
        """
        Load a persona directly by ID.

        Args:
            persona_id: The persona identifier
            config: Optional configuration override

        Returns:
            PersonaPlugin instance or None if not found
        """
        self.initialize()
        return PersonaRegistry.create_instance(persona_id, config)

    def list_available_personas(self) -> List[str]:
        """
        List all available persona IDs.

        Returns:
            List of persona IDs
        """
        self.initialize()
        return PersonaRegistry.list_personas()

    def get_persona_info(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a persona without instantiating it.

        Args:
            persona_id: The persona identifier

        Returns:
            Dict with persona info or None if not found
        """
        self.initialize()
        persona_class = PersonaRegistry.get(persona_id)

        if not persona_class:
            return None

        # Create a temporary instance to get info
        temp_instance = persona_class()

        return {
            "persona_id": temp_instance.persona_id,
            "name": temp_instance.name,
            "identity": temp_instance.get_identity(),
            "behaviors": temp_instance.get_behaviors(),
            "config": temp_instance.get_config(),
            "heartbeat": temp_instance.get_heartbeat_config()
        }

    def register_specialist_persona(
        self,
        domain_id: str,
        specialist_id: str,
        persona: PersonaPlugin
    ) -> None:
        """
        Register a persona instance for a specialist.

        This is useful for dynamically created personas.

        Args:
            domain_id: The domain identifier
            specialist_id: The specialist identifier
            persona: The persona instance to register
        """
        # Store in a runtime registry (could be expanded to persist)
        if not hasattr(self, '_runtime_personas'):
            self._runtime_personas = {}

        key = f"{domain_id}:{specialist_id}"
        self._runtime_personas[key] = persona
        print(f"[PersonaLoader] Registered runtime persona for {key}")

    def get_specialist_persona(
        self,
        domain_id: str,
        specialist_id: str
    ) -> Optional[PersonaPlugin]:
        """
        Get a runtime-registered persona for a specialist.

        Args:
            domain_id: The domain identifier
            specialist_id: The specialist identifier

        Returns:
            PersonaPlugin instance or None
        """
        if not hasattr(self, '_runtime_personas'):
            return None

        key = f"{domain_id}:{specialist_id}"
        return self._runtime_personas.get(key)


# Singleton instance for easy access
_default_loader: Optional[PersonaLoader] = None


def get_default_loader(universe_path: Optional[Path] = None) -> PersonaLoader:
    """Get or create the default persona loader instance."""
    global _default_loader
    if _default_loader is None:
        _default_loader = PersonaLoader(universe_path)
    return _default_loader
