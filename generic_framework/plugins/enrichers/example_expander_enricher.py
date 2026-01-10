"""
Example Expander Enricher Plugin

Expands examples within patterns.
Generates additional examples or clarifies existing ones.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.enrichment_plugin import EnrichmentPlugin, EnrichmentContext


class ExampleExpanderEnricher(EnrichmentPlugin):
    """
    Expands examples within patterns.

    Strategies:
    1. Generate variations of existing examples
    2. Add edge cases
    3. Add "what if" scenarios
    4. Clarify examples with explanations

    Configuration:
        - max_examples: int (default: 5) - Total examples after expansion
        - generate_variations: bool (default: true) - Generate example variations
        - add_edge_cases: bool (default: true) - Add edge case examples
        - add_explanations: bool (default: true) - Add explanations to examples
    """

    name = "Example Expander Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_examples = self.config.get("max_examples", 5)
        self.generate_variations = self.config.get("generate_variations", True)
        self.add_edge_cases = self.config.get("add_edge_cases", True)
        self.add_explanations = self.config.get("add_explanations", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Expand examples for each pattern."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()

            existing_examples = enriched.get("examples", [])
            if not existing_examples:
                enriched_patterns.append(enriched)
                continue

            # Expand examples
            expanded = await self._expand_examples(
                existing_examples,
                enriched,
                context
            )

            # Limit to max
            enriched["examples"] = expanded[:self.max_examples]
            enriched["example_count"] = len(expanded)
            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    async def _expand_examples(
        self,
        examples: List[Any],
        pattern: Dict[str, Any],
        context: EnrichmentContext
    ) -> List[Any]:
        """Expand the list of examples."""
        expanded = list(examples)  # Start with existing

        # Generate variations
        if self.generate_variations:
            variations = self._generate_variations(examples, pattern)
            expanded.extend(variations)

        # Add edge cases
        if self.add_edge_cases:
            edge_cases = self._generate_edge_cases(pattern)
            expanded.extend(edge_cases)

        # Add explanations
        if self.add_explanations:
            expanded = self._add_explanations(expanded, pattern)

        return expanded

    def _generate_variations(
        self,
        examples: List[Any],
        pattern: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate variations of existing examples."""
        variations = []

        for example in examples[:2]:  # Only vary first 2 examples
            if isinstance(example, dict):
                # Create a variation with modified values
                variation = example.copy()

                # Add "variation" note
                if "notes" in variation:
                    variation["notes"] = f"[Variation] {variation['notes']}"
                else:
                    variation["notes"] = "[Variation]"

                # Try to modify numeric values
                for key, value in variation.items():
                    if isinstance(value, (int, float)) and key not in ["id", "index"]:
                        # Perturb value slightly
                        if key.startswith("max") or key.startswith("limit"):
                            variation[key] = value * 2
                        elif key.startswith("min") or key.startswith("threshold"):
                            variation[key] = max(0, value // 2)
                        else:
                            variation[key] = value + 1

                variations.append(variation)

        return variations

    def _generate_edge_cases(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge case examples."""
        edge_cases = []

        pattern_type = pattern.get("type", "")
        pattern_name = pattern.get("name", "").lower()

        # Common edge cases based on pattern type
        edge_case = {
            "notes": "[Edge Case]"
        }

        if "xor" in pattern_name or "bitwise" in pattern_name:
            edge_case.update({
                "description": "Edge case: operating on zero or all-ones",
                "input": "0x00 or 0xFF",
                "behavior": "XOR with zero leaves value unchanged; XOR with all-ones inverts all bits"
            })
        elif "swap" in pattern_name:
            edge_case.update({
                "description": "Edge case: swapping identical values",
                "input": "a = b = 0x55",
                "behavior": "Result is both values become 0x00 (self-XOR = zero)"
            })
        elif "search" in pattern_name or "find" in pattern_name:
            edge_case.update({
                "description": "Edge case: empty or single-element collection",
                "input": "[] or [single_item]",
                "behavior": "Handle gracefully without errors"
            })
        elif "sort" in pattern_name or "order" in pattern_name:
            edge_case.update({
                "description": "Edge case: already sorted or reverse sorted",
                "input": "[1, 2, 3, 4, 5] or [5, 4, 3, 2, 1]",
                "behavior": "Algorithm should still complete correctly"
            })
        else:
            edge_case.update({
                "description": "Edge case: boundary conditions",
                "input": "Minimum/Maximum valid input",
                "behavior": "Verify behavior at limits"
            })

        edge_cases.append(edge_case)
        return edge_cases

    def _add_explanations(
        self,
        examples: List[Any],
        pattern: Dict[str, Any]
    ) -> List[Any]:
        """Add explanations to examples that don't have them."""
        explained = []

        for example in examples:
            if isinstance(example, dict):
                explained_example = example.copy()

                # Add explanation if missing and example has data
                if "explanation" not in explained_example and "notes" not in explained_example:
                    # Generate simple explanation
                    if example:
                        # Try to create a brief explanation from the example content
                        parts = []
                        for key, value in example.items():
                            if key not in ["id", "index", "notes"]:
                                parts.append(f"{key}={value}")

                        if parts:
                            explained_example["explanation"] = f"Example with: {', '.join(parts)}"

                explained.append(explained_example)
            else:
                explained.append(example)

        return explained


class ExampleValidatorEnricher(EnrichmentPlugin):
    """
    Validates and filters examples.

    Removes invalid or low-quality examples.
    """

    name = "Example Validator Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.min_quality = self.config.get("min_quality", 0.5)
        self.remove_duplicates = self.config.get("remove_duplicates", True)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Validate and filter examples."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()
            examples = enriched.get("examples", [])

            if examples:
                # Validate and filter
                filtered = self._validate_examples(examples)
                enriched["examples"] = filtered
                enriched["example_count"] = len(filtered)

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    def _validate_examples(self, examples: List[Any]) -> List[Any]:
        """Validate and filter examples."""
        valid = []
        seen = set()

        for example in examples:
            # Skip empty examples
            if not example:
                continue

            # Check for duplicates
            if self.remove_duplicates:
                example_str = str(example)
                if example_str in seen:
                    continue
                seen.add(example_str)

            # Quality check (simple heuristic)
            if isinstance(example, dict):
                # Count non-empty fields
                non_empty = sum(1 for v in example.values() if v)
                if non_empty >= 2:  # At least 2 non-empty fields
                    valid.append(example)
            else:
                valid.append(example)

        return valid


class ExampleSorterEnricher(EnrichmentPlugin):
    """
    Sorts examples by relevance or complexity.

    Configuration:
        - sort_by: str (default: "relevance") - Sort criterion
        - ascending: bool (default: false) - Sort order
    """

    name = "Example Sorter Enricher"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.sort_by = self.config.get("sort_by", "relevance")
        self.ascending = self.config.get("ascending", False)

    async def enrich(
        self,
        response_data: Dict[str, Any],
        context: EnrichmentContext
    ) -> Dict[str, Any]:
        """Sort examples for each pattern."""
        patterns = response_data.get("patterns", [])
        if not patterns:
            return response_data

        enriched_patterns = []
        for pattern in patterns:
            enriched = pattern.copy()
            examples = enriched.get("examples", [])

            if examples and len(examples) > 1:
                sorted_examples = self._sort_examples(examples)
                enriched["examples"] = sorted_examples

            enriched_patterns.append(enriched)

        response_data["patterns"] = enriched_patterns
        return response_data

    def _sort_examples(self, examples: List[Any]) -> List[Any]:
        """Sort examples based on configuration."""
        if self.sort_by == "complexity":
            # Sort by number of fields (more complex first)
            return sorted(
                examples,
                key=lambda e: len(e) if isinstance(e, dict) else 0,
                reverse=not self.ascending
            )
        elif self.sort_by == "relevance":
            # Move examples with "notes" or "explanation" to front
            return sorted(
                examples,
                key=lambda e: 0 if isinstance(e, dict) and ("notes" in e or "explanation" in e) else 1,
                reverse=not self.ascending
            )
        else:
            # Default: keep original order
            return examples
