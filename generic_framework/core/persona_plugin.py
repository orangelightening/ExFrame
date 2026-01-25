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
Persona Plugin Interface

A persona plugin defines how an LLM should respond—its voice, tone, behaviors,
and resilience characteristics. Personas are plugins that can be dynamically
loaded, configured, and swapped.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PersonaConfig:
    """Configuration for a persona."""
    name: str
    description: str
    identity: Dict[str, Any]
    behaviors: List[str]
    example_phrases: List[str]
    config: Dict[str, Any]
    heartbeat: Dict[str, Any] = field(default_factory=dict)


class PersonaPlugin(ABC):
    """
    Abstract base class for persona plugins.

    A persona plugin defines:
    - Identity: Who the AI is pretending to be
    - Behaviors: How the AI should act
    - Examples: Sample responses that reinforce the persona
    - Heartbeat: How to recover when the AI drifts from persona

    Personas are loaded like any other plugin and can be configured per-domain.
    """

    # Subclasses must define these
    name: str = "Persona"
    """Human-readable name for this persona."""

    persona_id: str = "persona"
    """Unique identifier for this persona."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the persona plugin.

        Args:
            config: Optional configuration from domain.json
        """
        self.config = config or {}

    @abstractmethod
    def get_identity(self) -> Dict[str, Any]:
        """
        Get the persona's identity.

        Returns:
            Dict with keys:
                - role: str (e.g., "You are a helpful home improvement specialist")
                - expertise: List[str] (e.g., ["construction", "materials"])
                - tone: str (e.g., "practical and specific")
                - audience: str (e.g., "DIY enthusiasts")
        """
        pass

    @abstractmethod
    def get_behaviors(self) -> List[str]:
        """
        Get behavioral directives for the persona.

        These are instructions the LLM should follow when responding.

        Returns:
            List of behavioral directives (e.g., "Always mention specific measurements")
        """
        pass

    @abstractmethod
    def get_example_phrases(self) -> List[str]:
        """
        Get example phrases that reinforce the persona.

        These are included in the prompt to show the LLM the desired voice.

        Returns:
            List of example responses in this persona's voice
        """
        pass

    def get_config(self) -> Dict[str, Any]:
        """
        Get LLM configuration for this persona.

        Returns:
            Dict with keys:
                - temperature: float
                - max_tokens: int
                - preferred_format: str ("anthropic", "openai", "generic")
                - use_system_message: bool
        """
        return {
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 8192),
            "preferred_format": self.config.get("preferred_format", "anthropic"),
            "use_system_message": self.config.get("use_system_message", True)
        }

    def get_heartbeat_config(self) -> Dict[str, Any]:
        """
        Get heartbeat/resilience configuration for this persona.

        Returns:
            Dict with heartbeat settings (enabled, mode, triggers, recovery)
        """
        return self.config.get("heartbeat", {
            "enabled": False,
            "mode": "moderate",
            "triggers": {},
            "recovery": {"max_attempts": 2}
        })

    def build_system_prompt(self) -> str:
        """
        Build the system prompt for this persona.

        Combines identity, behaviors, and examples into a cohesive prompt.

        Returns:
            System prompt string
        """
        parts = []

        identity = self.get_identity()
        if identity.get("role"):
            parts.append(identity["role"])

        if identity.get("expertise"):
            parts.append(f"\nYour expertise includes: {', '.join(identity['expertise'])}.")

        if identity.get("tone"):
            parts.append(f"\nCommunication style: {identity['tone']}.")

        if identity.get("audience"):
            parts.append(f"\nYou are helping: {identity['audience']}.")

        behaviors = self.get_behaviors()
        if behaviors:
            parts.append("\n\nWhen responding:")
            for behavior in behaviors:
                parts.append(f"- {behavior}")

        examples = self.get_example_phrases()
        if examples:
            parts.append("\n\nExample responses that match your persona:")
            for i, example in enumerate(examples[:3], 1):
                parts.append(f"{i}. {example}")

        return "\n".join(parts) if parts else "You are a helpful assistant."

    def can_handle(self, domain_id: str, specialist_id: str) -> float:
        """
        Check if this persona can handle the given domain/specialist.

        Returns:
            Confidence score 0.0 to 1.0
        """
        # Default implementation - override in subclasses
        return 0.0

    async def on_query_start(self, query: str, context: Dict[str, Any]) -> None:
        """
        Called when a query starts being processed with this persona.

        Override for custom pre-query logic (logging, etc).
        """
        pass

    async def on_query_complete(
        self,
        query: str,
        response: str,
        context: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> None:
        """
        Called when a query completes.

        Override for custom post-query logic (analytics, etc).
        """
        pass


class PanelPersonaPlugin(PersonaPlugin):
    """
    A persona that represents a panel of experts.

    Instead of a single persona, this coordinates multiple expert personas
    working together (sequential, parallel, or debate modes).
    """

    def get_experts(self) -> List[str]:
        """
        Get the list of expert persona IDs for this panel.

        Returns:
            List of persona_id strings
        """
        return []

    def get_facilitator_id(self) -> str:
        """
        Get the facilitator persona ID that synthesizes expert input.

        Returns:
            Facilitator persona_id
        """
        raise NotImplementedError("Panel personas must define a facilitator")

    def get_panel_mode(self) -> str:
        """
        Get the panel interaction mode.

        Returns:
            One of: "sequential", "parallel", "debate"
        """
        return "sequential"

    def get_max_rounds(self) -> int:
        """
        Get maximum rounds for debate mode.

        Returns:
            Maximum number of debate rounds
        """
        return 2

    def get_consensus_threshold(self) -> float:
        """
        Get consensus threshold for stopping panel.

        Returns:
            Threshold 0.0 to 1.0
        """
        return 0.7

    # Note: Panel personas don't implement get_identity/get_behaviors directly
    # Those are delegated to the expert personas
    def get_identity(self) -> Dict[str, Any]:
        return {"role": f"You are a panel of experts: {', '.join(self.get_experts())}"}

    def get_behaviors(self) -> List[str]:
        return ["Collaborate to provide comprehensive responses"]

    def get_example_phrases(self) -> List[str]:
        return ["[Panel response synthesized from multiple expert perspectives]"]
