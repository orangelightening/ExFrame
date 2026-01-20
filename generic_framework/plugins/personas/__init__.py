"""
Persona Plugin Registry

Manages discovery, loading, and instantiation of persona plugins.
"""

from typing import Dict, List, Optional, Type
from pathlib import Path
from core.persona_plugin import PersonaPlugin, PanelPersonaPlugin


class PersonaRegistry:
    """Registry for persona plugins."""

    _personas: Dict[str, Type[PersonaPlugin]] = {}

    @classmethod
    def register(cls, persona_class: Type[PersonaPlugin]) -> Type[PersonaPlugin]:
        """
        Register a persona plugin class.

        Can be used as a decorator:
        ```
        @PersonaRegistry.register
        class MyPersona(PersonaPlugin):
            ...
        ```
        """
        cls._personas[persona_class.persona_id] = persona_class
        return persona_class

    @classmethod
    def unregister(cls, persona_id: str) -> None:
        """Unregister a persona by ID."""
        if persona_id in cls._personas:
            del cls._personas[persona_id]

    @classmethod
    def get(cls, persona_id: str) -> Optional[Type[PersonaPlugin]]:
        """Get a persona plugin class by ID."""
        return cls._personas.get(persona_id)

    @classmethod
    def list_personas(cls) -> List[str]:
        """List all registered persona IDs."""
        return list(cls._personas.keys())

    @classmethod
    def create_instance(
        cls,
        persona_id: str,
        config: Optional[Dict] = None
    ) -> Optional[PersonaPlugin]:
        """Create an instance of a persona plugin."""
        persona_class = cls.get(persona_id)
        if persona_class:
            return persona_class(config)
        return None

    @classmethod
    def discover_personas(cls, personas_path: Path) -> None:
        """
        Auto-discover persona plugins from a directory.

        Args:
            personas_path: Path to personas directory
        """
        import importlib
        import inspect

        for py_file in personas_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            # Import the module
            module_name = f"generic_framework.plugins.personas.{py_file.stem}"
            try:
                module = importlib.import_module(module_name)

                # Find all PersonaPlugin subclasses
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, PersonaPlugin) and
                        obj is not PersonaPlugin and
                        obj is not PanelPersonaPlugin):
                        cls.register(obj)
                        print(f"[PersonaRegistry] Registered persona: {obj.persona_id}")

            except Exception as e:
                print(f"[PersonaRegistry] Failed to load persona from {py_file}: {e}")

    @classmethod
    def initialize(cls) -> None:
        """Initialize the registry by discovering all built-in personas."""
        personas_path = Path(__file__).parent
        cls.discover_personas(personas_path)


# Export the registry and base classes
__all__ = [
    'PersonaRegistry',
    'PersonaPlugin',
    'PanelPersonaPlugin'
]
