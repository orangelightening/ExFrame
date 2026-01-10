"""
Markdown Formatter Plugin

Formats specialist responses as Markdown (default human-readable format).
Migrates existing formatting logic from specialists into a reusable plugin.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.formatter_plugin import FormatterPlugin, FormattedResponse


class MarkdownFormatter(FormatterPlugin):
    """
    Format specialist responses as Markdown.

    This is the default formatter, providing human-readable output with:
    - Headers for structure
    - Bold for emphasis
    - Code blocks for examples
    - Lists for patterns and steps
    """

    name = "Markdown Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Markdown formatter.

        Config options:
            - include_metadata: bool (default: True) - Include specialist and confidence info
            - max_examples_per_pattern: int (default: 3) - Limit examples per pattern
            - include_tags: bool (default: True) - Show pattern tags
            - code_block_language: str (default: None) - Language for code blocks
            - show_pattern_id: bool (default: False) - Show pattern IDs
        """
        super().__init__(config)
        self.include_metadata = self.config.get("include_metadata", True)
        self.max_examples = self.config.get("max_examples_per_pattern", 3)
        self.include_tags = self.config.get("include_tags", True)
        self.code_lang = self.config.get("code_block_language")
        self.show_pattern_id = self.config.get("show_pattern_id", False)

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format response data as Markdown."""
        if not self.validate_response_data(response_data):
            return FormattedResponse(
                content="# Error\n\nInvalid response data",
                mime_type="text/markdown"
            )

        query = response_data.get("query", "")
        patterns = response_data.get("patterns", [])
        specialist_id = response_data.get("specialist_id", "unknown")
        confidence = response_data.get("confidence", 0.0)

        # Check for multi-specialist aggregation
        aggregation_strategy = response_data.get("aggregation_strategy")
        individual_responses = response_data.get("responses", [])

        lines = []

        # Header
        lines.append(f"## Results for: {query}\n")

        # Metadata section
        if self.include_metadata:
            lines.append(f"**Specialist:** {specialist_id}")
            lines.append(f"**Confidence:** {confidence:.1%}")
            if aggregation_strategy:
                lines.append(f"**Aggregation:** {aggregation_strategy}")
                if aggregation_strategy == "side_by_side":
                    lines.append(f"**Specialists:** {len(individual_responses)}")
            lines.append("")

        # Multi-specialist handling
        if aggregation_strategy == "side_by_side" and individual_responses:
            return self._format_side_by_side(response_data, lines)

        # Pattern results
        if patterns:
            lines.append(f"**Found {len(patterns)} relevant pattern(s):**\n")

            for i, pattern in enumerate(patterns[:5], 1):  # Limit to 5 patterns
                lines.extend(self._format_pattern(pattern, i))

            if len(patterns) > 5:
                lines.append(f"\n*... and {len(patterns) - 5} more patterns*")
        else:
            lines.append("**No patterns found.**")

        # Individual responses (for non-side-by-side multi-specialist)
        if aggregation_strategy and aggregation_strategy != "side_by_side" and individual_responses:
            lines.append("\n---\n")
            lines.append("### Individual Specialist Responses\n")
            for resp in individual_responses:
                lines.append(f"**{resp['specialist_id']}** (confidence: {resp['confidence']:.1%})")
                lines.append(f"- {resp['pattern_count']} patterns")
                lines.append("")

        content = "\n".join(lines)

        return FormattedResponse(
            content=content,
            mime_type="text/markdown",
            metadata={
                "pattern_count": len(patterns),
                "specialist": specialist_id,
                "confidence": confidence,
                "aggregation": aggregation_strategy,
                "truncated": len(patterns) > 5
            }
        )

    def _format_pattern(self, pattern: Dict, index: int) -> List[str]:
        """Format a single pattern as Markdown."""
        lines = []

        # Pattern header
        name = pattern.get("name", "Unknown Pattern")
        pattern_type = pattern.get("type") or pattern.get("pattern_type", "N/A")

        if self.show_pattern_id:
            pid = pattern.get("pattern_id") or pattern.get("id", "")
            lines.append(f"### {index}. {name} (`{pid}`)")
        else:
            lines.append(f"### {index}. {name}")

        lines.append(f"**Type:** {pattern_type}")

        # Tags
        if self.include_tags:
            tags = pattern.get("tags", [])
            if tags:
                tags_str = " | ".join(tags[:5])
                lines.append(f"**Tags:** {tags_str}")

        lines.append("")

        # Problem
        if "problem" in pattern:
            lines.append(f"**Problem:** {pattern['problem']}")
            lines.append("")

        # Solution
        if "solution" in pattern:
            lines.append(f"**Solution:** {pattern['solution']}")
            lines.append("")

        # Steps
        if "steps" in pattern and pattern["steps"]:
            lines.append("**Steps:**")
            for step in pattern["steps"][:5]:
                lines.append(f"{step}. {step}")
            lines.append("")

        # Examples
        if "examples" in pattern and pattern["examples"]:
            lines.append("**Examples:**")
            for ex in pattern["examples"][:self.max_examples]:
                lines.append(f"- {self._format_example(ex)}")
            lines.append("")

        # Conditions
        if "conditions" in pattern and pattern["conditions"]:
            lines.append("**When to use:**")
            lines.append(f"- {pattern['conditions'].get('when', 'N/A')}")
            lines.append(f"- **Risk:** {pattern['conditions'].get('risk', 'N/A')}")
            lines.append("")

        # Related patterns
        if "related_patterns" in pattern and pattern["related_patterns"]:
            related = ", ".join(pattern["related_patterns"][:3])
            lines.append(f"**Related:** {related}")
            lines.append("")

        return lines

    def _format_example(self, example: Any) -> str:
        """Format a single example."""
        if isinstance(example, str):
            return example
        elif isinstance(example, dict):
            # Format key-value pairs
            parts = []
            for key, value in example.items():
                if key != "notes":
                    parts.append(f"{key}={value}")
            return " ".join(parts)
        else:
            return str(example)

    def _format_side_by_side(self, response_data: Dict[str, Any], header_lines: List[str]) -> FormattedResponse:
        """Format multi-specialist side-by-side responses."""
        individual_responses = response_data.get("responses", [])
        lines = header_lines.copy()

        for resp in individual_responses:
            specialist_id = resp.get("specialist_id", "unknown")
            confidence = resp.get("confidence", 0.0)
            pattern_count = resp.get("pattern_count", 0)

            lines.append(f"### {specialist_id}")
            lines.append(f"**Confidence:** {confidence:.1%} | **Patterns:** {pattern_count}")
            lines.append("")

            # Note: In side_by_side, we'd need the full patterns for each specialist
            # For now, just show summary
            raw_answer = resp.get("raw_answer", "")
            if raw_answer:
                lines.append(f"{raw_answer}")
                lines.append("")

        content = "\n".join(lines)

        return FormattedResponse(
            content=content,
            mime_type="text/markdown",
            metadata={
                "specialist_count": len(individual_responses),
                "aggregation": "side_by_side"
            }
        )

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["markdown", "md"]


class ConciseMarkdownFormatter(MarkdownFormatter):
    """
    A more compact version of MarkdownFormatter.

    Less verbose, suitable for quick scanning.
    """

    name = "Concise Markdown Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Override defaults for concise output
        config = config or {}
        config.setdefault("include_metadata", False)
        config.setdefault("max_examples_per_pattern", 1)
        config.setdefault("include_tags", False)
        super().__init__(config)

    def _format_pattern(self, pattern: Dict, index: int) -> List[str]:
        """Format pattern more concisely."""
        lines = []

        name = pattern.get("name", "Unknown Pattern")
        lines.append(f"### {index}. {name}")

        # Just solution, no problem/steps
        if "solution" in pattern:
            # Truncate long solutions
            solution = pattern["solution"]
            if len(solution) > 200:
                solution = solution[:200] + "..."
            lines.append(f"{solution}")

        lines.append("")
        return lines

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["markdown-concise", "md-concise", "concise"]
