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
Panel Manager

Coordinates multiple expert personas working together in different modes:
- Sequential: Each expert builds on previous responses
- Parallel: All experts respond independently, facilitator synthesizes
- Debate: Experts critique and respond to each other
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

from core.persona_plugin import PersonaPlugin, PanelPersonaPlugin
from assist.persona_loader import PersonaLoader

logger = logging.getLogger(__name__)


@dataclass
class ExpertContribution:
    """One expert's contribution to the panel."""
    expert_id: str
    expert_name: str
    response: str
    confidence: float
    round: int = 1
    critiques: List[str] = field(default_factory=list)
    build_on: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "expert_id": self.expert_id,
            "expert_name": self.expert_name,
            "response": self.response,
            "confidence": self.confidence,
            "round": self.round,
            "critiques": self.critiques,
            "build_on": self.build_on,
            "timestamp": self.timestamp
        }


@dataclass
class PanelResult:
    """Result from a panel consultation."""
    final_response: str
    contributions: List[ExpertContribution]
    consensus_level: float
    rounds: int
    panel_mode: str
    facilitator_id: str
    processing_time_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "final_response": self.final_response,
            "contributions": [c.to_dict() for c in self.contributions],
            "consensus_level": self.consensus_level,
            "rounds": self.rounds,
            "panel_mode": self.panel_mode,
            "facilitator_id": self.facilitator_id,
            "processing_time_ms": self.processing_time_ms,
            "expert_count": len(self.contributions)
        }


class PanelManager:
    """
    Manages expert panels for collaborative query resolution.

    Coordinates multiple expert personas to provide comprehensive responses.
    """

    def __init__(self, persona_loader: Optional[PersonaLoader] = None):
        """
        Initialize the panel manager.

        Args:
            persona_loader: Optional persona loader instance
        """
        self.persona_loader = persona_loader or PersonaLoader()

    async def process_with_panel(
        self,
        query: str,
        panel_persona: PanelPersonaPlugin,
        context: Optional[Dict[str, Any]] = None,
        llm_call_handler: Optional[callable] = None
    ) -> PanelResult:
        """
        Process query using expert panel.

        Args:
            query: The user's query
            panel_persona: The panel persona containing expert configuration
            context: Optional context for the query
            llm_call_handler: Optional async function to call LLM (signature: async call(prompt, persona) -> response)

        Returns:
            PanelResult with final response and all contributions
        """
        start_time = datetime.utcnow()

        mode = panel_persona.get_panel_mode()
        logger.info(f"[PanelManager] Processing query with panel mode: {mode}")

        if mode == "sequential":
            result = await self._sequential_panel(query, panel_persona, context, llm_call_handler)
        elif mode == "parallel":
            result = await self._parallel_panel(query, panel_persona, context, llm_call_handler)
        elif mode == "debate":
            result = await self._debate_panel(query, panel_persona, context, llm_call_handler)
        else:
            logger.warning(f"Unknown panel mode: {mode}, falling back to sequential")
            result = await self._sequential_panel(query, panel_persona, context, llm_call_handler)

        # Calculate processing time
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        result.processing_time_ms = processing_time

        return result

    async def _sequential_panel(
        self,
        query: str,
        panel_persona: PanelPersonaPlugin,
        context: Optional[Dict[str, Any]],
        llm_call_handler: Optional[callable]
    ) -> PanelResult:
        """
        Sequential mode: Each expert builds on previous responses.

        Expert 1 → Expert 2 (sees E1) → Expert 3 (sees E1, E2) → Facilitator
        """
        contributions = []
        expert_ids = panel_persona.get_experts()

        # Load all expert personas
        experts = []
        for expert_id in expert_ids:
            expert = self.persona_loader.load_persona_by_id(expert_id)
            if expert:
                experts.append((expert_id, expert))
            else:
                logger.warning(f"[PanelManager] Expert persona '{expert_id}' not found")

        if not experts:
            return self._empty_result("sequential", panel_persona)

        accumulated_context = context.copy() if context else {}

        # Each expert responds in sequence
        for i, (expert_id, expert) in enumerate(experts):
            # Build prompt with previous contributions
            prompt = self._build_sequential_prompt(
                query,
                expert,
                contributions,
                accumulated_context
            )

            # Get expert response
            response = await self._call_expert(expert, prompt, llm_call_handler)

            # Track contribution
            contribution = ExpertContribution(
                expert_id=expert_id,
                expert_name=expert.name,
                response=response["response"],
                confidence=response.get("confidence", 0.7),
                build_on=[c.expert_id for c in contributions]
            )
            contributions.append(contribution)

            # Accumulate context for next expert
            accumulated_context["previous_expert"] = contribution.to_dict()
            accumulated_context["expert_index"] = i + 1

        # Facilitator synthesizes
        final_response = await self._synthesize(
            query,
            contributions,
            panel_persona.get_facilitator_id(),
            context,
            llm_call_handler
        )

        return PanelResult(
            final_response=final_response,
            contributions=contributions,
            consensus_level=self._calculate_consensus(contributions),
            rounds=1,
            panel_mode="sequential",
            facilitator_id=panel_persona.get_facilitator_id()
        )

    async def _parallel_panel(
        self,
        query: str,
        panel_persona: PanelPersonaPlugin,
        context: Optional[Dict[str, Any]],
        llm_call_handler: Optional[callable]
    ) -> PanelResult:
        """
        Parallel mode: All experts respond independently.

        Expert 1 ──┐
        Expert 2 ──┼→ Facilitator synthesizes all
        Expert 3 ──┘
        """
        expert_ids = panel_persona.get_experts()

        # Load all expert personas
        expert_tasks = []
        for expert_id in expert_ids:
            expert = self.persona_loader.load_persona_by_id(expert_id)
            if expert:
                expert_tasks.append((expert_id, expert))
            else:
                logger.warning(f"[PanelManager] Expert persona '{expert_id}' not found")

        if not expert_tasks:
            return self._empty_result("parallel", panel_persona)

        # All experts respond in parallel
        tasks = []
        for expert_id, expert in expert_tasks:
            prompt = self._build_parallel_prompt(query, expert, context)
            task = self._call_expert(expert, prompt, llm_call_handler)
            tasks.append((expert_id, expert, task))

        # Wait for all responses
        contributions = []
        results = await asyncio.gather(*[t[2] for t in tasks], return_exceptions=True)

        for (expert_id, expert, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"[PanelManager] Expert {expert_id} failed: {result}")
                continue

            contribution = ExpertContribution(
                expert_id=expert_id,
                expert_name=expert.name,
                response=result["response"],
                confidence=result.get("confidence", 0.7)
            )
            contributions.append(contribution)

        # Facilitator synthesizes
        final_response = await self._synthesize(
            query,
            contributions,
            panel_persona.get_facilitator_id(),
            context,
            llm_call_handler
        )

        return PanelResult(
            final_response=final_response,
            contributions=contributions,
            consensus_level=self._calculate_consensus(contributions),
            rounds=1,
            panel_mode="parallel",
            facilitator_id=panel_persona.get_facilitator_id()
        )

    async def _debate_panel(
        self,
        query: str,
        panel_persona: PanelPersonaPlugin,
        context: Optional[Dict[str, Any]],
        llm_call_handler: Optional[callable]
    ) -> PanelResult:
        """
        Debate mode: Experts critique and respond to each other.

        Expert 1 → Expert 2 (critiques E1) → Expert 1 (rebuttal) → ...
        """
        contributions = []
        expert_ids = panel_persona.get_experts()
        max_rounds = panel_persona.get_max_rounds()

        # Load all expert personas
        experts = []
        for expert_id in expert_ids:
            expert = self.persona_loader.load_persona_by_id(expert_id)
            if expert:
                experts.append((expert_id, expert))
            else:
                logger.warning(f"[PanelManager] Expert persona '{expert_id}' not found")

        if not experts:
            return self._empty_result("debate", panel_persona)

        # Initial responses (round 1)
        accumulated_context = context.copy() if context else {}

        for round_num in range(1, max_rounds + 1):
            round_contributions = []

            for expert_id, expert in experts:
                # Build prompt with previous critiques/responses
                prompt = self._build_debate_prompt(
                    query,
                    expert,
                    contributions,
                    round_num,
                    accumulated_context
                )

                # Get expert response
                response = await self._call_expert(expert, prompt, llm_call_handler)

                # Track contribution
                contribution = ExpertContribution(
                    expert_id=expert_id,
                    expert_name=expert.name,
                    response=response["response"],
                    confidence=response.get("confidence", 0.7),
                    round=round_num
                )
                round_contributions.append(contribution)
                contributions.append(contribution)

            # Check for consensus
            consensus = self._calculate_consensus(round_contributions)
            threshold = panel_persona.get_consensus_threshold()

            if consensus >= threshold:
                logger.info(f"[PanelManager] Consensus reached at round {round_num}: {consensus}")
                break

            # Add round context for next iteration
            accumulated_context["last_round"] = [c.to_dict() for c in round_contributions]

        # Facilitator synthesizes final result
        final_response = await self._synthesize(
            query,
            contributions,
            panel_persona.get_facilitator_id(),
            context,
            llm_call_handler
        )

        return PanelResult(
            final_response=final_response,
            contributions=contributions,
            consensus_level=self._calculate_consensus(contributions),
            rounds=round_num,
            panel_mode="debate",
            facilitator_id=panel_persona.get_facilitator_id()
        )

    async def _call_expert(
        self,
        expert: PersonaPlugin,
        prompt: str,
        llm_call_handler: Optional[callable]
    ) -> Dict[str, Any]:
        """
        Call an expert persona to get a response.

        Args:
            expert: The expert persona
            prompt: The prompt to send
            llm_call_handler: Optional async LLM handler

        Returns:
            Dict with response and confidence
        """
        if llm_call_handler:
            # Use provided LLM handler
            try:
                result = await llm_call_handler(prompt, expert)
                return result
            except Exception as e:
                logger.error(f"[PanelManager] LLM call failed: {e}")
                return {
                    "response": f"[Error: {str(e)}]",
                    "confidence": 0.0
                }
        else:
            # Mock response for testing
            return {
                "response": f"[Mock response from {expert.name}]\nSystem prompt would be: {expert.build_system_prompt()[:100]}...",
                "confidence": 0.7
            }

    def _build_sequential_prompt(
        self,
        query: str,
        expert: PersonaPlugin,
        previous_contributions: List[ExpertContribution],
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for sequential expert."""
        parts = [f"Query: {query}\n"]

        if previous_contributions:
            parts.append("\nPrevious expert inputs:\n")
            for contrib in previous_contributions:
                parts.append(f"- {contrib.expert_name}: {contrib.response[:200]}...\n")

        parts.append(f"\nYour task: Provide your expert perspective on this query.")
        parts.append(f"\nBuild upon the previous inputs where relevant.")

        return "".join(parts)

    def _build_parallel_prompt(
        self,
        query: str,
        expert: PersonaPlugin,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for parallel expert."""
        return f"Query: {query}\n\nProvide your expert perspective independently of other experts."

    def _build_debate_prompt(
        self,
        query: str,
        expert: PersonaPlugin,
        previous_contributions: List[ExpertContribution],
        round_num: int,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for debate expert."""
        parts = [f"Query: {query}\n"]
        parts.append(f"Round: {round_num}\n")

        # Filter contributions for this round
        this_round = [c for c in previous_contributions if c.round == round_num - 1]

        if this_round or round_num > 1:
            parts.append("\nPrevious round responses:\n")
            for contrib in this_round:
                parts.append(f"- {contrib.expert_name}: {contrib.response[:200]}...\n")

        parts.append("\nYour task: Critique previous responses and provide your own perspective.")

        return "".join(parts)

    async def _synthesize(
        self,
        query: str,
        contributions: List[ExpertContribution],
        facilitator_id: str,
        context: Optional[Dict[str, Any]],
        llm_call_handler: Optional[callable]
    ) -> str:
        """
        Synthesize expert contributions using facilitator persona.

        Args:
            query: Original query
            contributions: All expert contributions
            facilitator_id: ID of facilitator persona
            context: Optional context
            llm_call_handler: Optional LLM handler

        Returns:
            Synthesized final response
        """
        facilitator = self.persona_loader.load_persona_by_id(facilitator_id)

        if not facilitator:
            logger.warning(f"[PanelManager] Facilitator '{facilitator_id}' not found, using simple synthesis")
            return self._simple_synthesis(contributions)

        # Build synthesis prompt
        prompt = self._build_synthesis_prompt(query, contributions, facilitator)

        # Get facilitator response
        if llm_call_handler:
            try:
                result = await llm_call_handler(prompt, facilitator)
                return result.get("response", self._simple_synthesis(contributions))
            except Exception as e:
                logger.error(f"[PanelManager] Facilitator synthesis failed: {e}")
                return self._simple_synthesis(contributions)
        else:
            # Mock synthesis for testing
            return self._simple_synthesis(contributions)

    def _build_synthesis_prompt(
        self,
        query: str,
        contributions: List[ExpertContribution],
        facilitator: PersonaPlugin
    ) -> str:
        """Build synthesis prompt for facilitator."""
        parts = [
            f"Original Query: {query}\n\n",
            "Expert Contributions:\n"
        ]

        for i, contrib in enumerate(contributions, 1):
            parts.append(f"\n{i}. {contrib.expert_name} (confidence: {contrib.confidence}):\n")
            parts.append(f"{contrib.response}\n")

        parts.append(f"\nYour task: Synthesize these expert perspectives into a comprehensive, unified response.")
        parts.append(f"\nIdentify areas of agreement and disagreement. Provide the best answer considering all inputs.")

        return "".join(parts)

    def _simple_synthesis(self, contributions: List[ExpertContribution]) -> str:
        """Simple synthesis without facilitator (fallback)."""
        if not contributions:
            return "[No expert contributions available]"

        parts = ["Synthesis of expert perspectives:\n\n"]

        for contrib in contributions:
            parts.append(f"**{contrib.expert_name}** (confidence: {contrib.confidence}):\n")
            parts.append(f"{contrib.response}\n\n")

        return "".join(parts)

    def _calculate_consensus(self, contributions: List[ExpertContribution]) -> float:
        """
        Calculate consensus level among contributions.

        Simple heuristic: average confidence normalized by agreement indicators.
        """
        if not contributions:
            return 0.0

        # Average confidence
        avg_confidence = sum(c.confidence for c in contributions) / len(contributions)

        # Check for agreement (simple: if all confidences are high)
        high_confidence_count = sum(1 for c in contributions if c.confidence > 0.7)
        agreement_bonus = high_confidence_count / len(contributions) if contributions else 0

        # Combined consensus score
        consensus = (avg_confidence * 0.7) + (agreement_bonus * 0.3)

        return round(consensus, 2)

    def _empty_result(self, mode: str, panel_persona: PanelPersonaPlugin) -> PanelResult:
        """Return empty result when no experts available."""
        return PanelResult(
            final_response="[Panel Error: No expert personas available]",
            contributions=[],
            consensus_level=0.0,
            rounds=0,
            panel_mode=mode,
            facilitator_id=panel_persona.get_facilitator_id()
        )
