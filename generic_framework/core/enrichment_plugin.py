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
Enrichment Plugin Interface

Enrichment plugins transform specialist response data BEFORE formatting.
They sit in the pipeline: Specialist → [Enrichers] → Formatter

Use cases:
- Add related patterns
- Expand examples
- Generate code from patterns
- Add usage statistics
- Enhance with external data
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class EnrichmentContext:
    """
    Context information for enrichment plugins.

    Provides access to domain resources and metadata.
    """
    domain_id: str
    specialist_id: str
    query: str
    knowledge_base: Optional['KnowledgeBase'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    llm_confirmed: bool = False  # User has confirmed LLM fallback usage


class EnrichmentPlugin(ABC):
    """
    Abstract base class for enrichment plugins.

    Enrichment plugins modify/add data to the response BEFORE formatting.
    They can:
    - Add new fields to patterns
    - Enrich existing data (e.g., expand examples)
    - Add metadata (usage stats, related patterns)
    - Generate derived content (code, summaries)
    """

    name: str = "EnrichmentPlugin"
    """
    Human-readable name for this enricher.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enrichment plugin.

        Args:
            config: Optional configuration dictionary from domain.json
        """
        self.config = config or {}

    @abstractmethod
    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """
        Enrich the response data.

        This method receives the specialist's response and can:
        - Add new fields to patterns
        - Enrich existing data
        - Add metadata
        - Generate derived content

        Args:
            response_data: The response data from the specialist
            context: Enrichment context with domain/KB access

        Returns:
            Enriched response data (may be modified or new dict)
        """
        pass

    def get_supported_formats(self) -> List[str]:
        """
        Return list of format types this enricher supports.

        Some enrichers may only work with specific output formats.
        Return empty list to apply to all formats.

        Returns:
            List of format identifiers (e.g., ["markdown", "json"])
        """
        return []

    def supports_format(self, format_type: str) -> bool:
        """
        Check if this enricher supports a specific format.

        Args:
            format_type: The format type to check

        Returns:
            True if enricher should be applied for this format
        """
        supported = self.get_supported_formats()
        return not supported or format_type in supported

    def can_run_parallel(self) -> bool:
        """
        Whether this enricher can run in parallel with other enrichers.

        If True, this enricher doesn't depend on output from other enrichers.
        If False, it should run sequentially after dependent enrichers.

        Returns:
            True if parallel execution is safe
        """
        return True


class ChainedEnricher(EnrichmentPlugin):
    """
    Runs multiple enrichers in sequence.

    Output of one enricher becomes input to the next.
    """

    name = "ChainedEnricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.enrichers: List[EnrichmentPlugin] = []

    def add_enricher(self, enricher: EnrichmentPlugin) -> 'ChainedEnricher':
        """
        Add an enricher to the chain.

        Args:
            enricher: The enricher to add

        Returns:
            Self for method chaining
        """
        self.enrichers.append(enricher)
        return self

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Run all enrichers in sequence."""
        data = response_data
        for enricher in self.enrichers:
            # Skip enricher if format not supported
            if not enricher.supports_format(self.config.get("target_format", "")):
                continue
            data = await enricher.enrich(data, context)
        return data

    def can_run_parallel(self) -> bool:
        """Chain is sequential."""
        return False


class ParallelEnricher(EnrichmentPlugin):
    """
    Runs multiple enrichers in parallel and merges results.

    All enrichers receive the same input and their outputs are merged.
    """

    name = "ParallelEnricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.enrichers: List[EnrichmentPlugin] = []
        self.merge_strategy = self.config.get("merge_strategy", "merge_all")

    def add_enricher(self, enricher: EnrichmentPlugin) -> 'ParallelEnricher':
        """Add an enricher to the parallel set."""
        self.enrichers.append(enricher)
        return self

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Run all enrichers in parallel and merge."""
        import asyncio

        # Filter by format support
        eligible_enrichers = [
            e for e in self.enrichers
            if e.supports_format(self.config.get("target_format", ""))
        ]

        # Run all enrichers in parallel
        tasks = [
            e.enrich(response_data.copy(), context)
            for e in eligible_enrichers
            if e.can_run_parallel()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results
        merged = response_data.copy()
        for result in results:
            if isinstance(result, Exception):
                continue
            if isinstance(result, dict):
                merged.update(result)

        return merged

    def can_run_parallel(self) -> bool:
        """ParallelEnricher itself runs parallel enrichers."""
        return True
