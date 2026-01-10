"""
Compact Formatter Plugin

Formats specialist responses in a minimal, terminal-friendly format.
Ideal for CLI usage, quick scanning, and bandwidth-constrained environments.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.formatter_plugin import FormatterPlugin, FormattedResponse


class CompactFormatter(FormatterPlugin):
    """
    Format specialist responses in a compact, minimal format.

    Provides:
    - Minimal output for terminal/CLI usage
    - Truncated solutions (first N characters)
    - Limited pattern count (top 3 by default)
    - No markdown formatting
    - Plain text output
    """

    name = "Compact Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the compact formatter.

        Config options:
            - max_patterns: int (default: 3) - Maximum patterns to show
            - max_length: int (default: 100) - Truncate solutions to this length
            - show_specialist: bool (default: True) - Show specialist name
            - show_confidence: bool (default: False) - Show confidence score
            - show_type: bool (default: True) - Show pattern type
            - separator: str (default: "\n") - Line separator
        """
        super().__init__(config)
        self.max_patterns = self.config.get("max_patterns", 3)
        self.max_length = self.config.get("max_length", 100)
        self.show_specialist = self.config.get("show_specialist", True)
        self.show_confidence = self.config.get("show_confidence", False)
        self.show_type = self.config.get("show_type", True)
        self.separator = self.config.get("separator", "\n")

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format response data in compact format."""
        if not self.validate_response_data(response_data):
            return FormattedResponse(
                content="Error: Invalid response data",
                mime_type="text/plain"
            )

        query = response_data.get("query", "")
        patterns = response_data.get("patterns", [])
        specialist_id = response_data.get("specialist_id", "unknown")
        confidence = response_data.get("confidence", 0.0)

        lines = []

        # Query header
        lines.append(f"Query: {query}")

        # Optional specialist/confidence
        if self.show_specialist or self.show_confidence:
            parts = []
            if self.show_specialist:
                parts.append(f"Specialist: {specialist_id}")
            if self.show_confidence:
                parts.append(f"Confidence: {confidence:.0%}")
            if parts:
                lines.append(" | ".join(parts))

        # Separator
        lines.append("")

        # Patterns
        if patterns:
            # Limit patterns
            display_patterns = patterns[:self.max_patterns]

            for i, pattern in enumerate(display_patterns, 1):
                lines.extend(self._format_pattern_compact(pattern, i))

            # Truncation notice
            if len(patterns) > self.max_patterns:
                lines.append(f"... and {len(patterns) - self.max_patterns} more patterns")
        else:
            lines.append("No patterns found.")

        # Multi-specialist info
        aggregation = response_data.get("aggregation_strategy")
        if aggregation and aggregation != "single":
            responses = response_data.get("responses", [])
            lines.append("")
            lines.append(f"[{aggregation}] {len(responses)} specialist(s)")

        content = self.separator.join(lines)

        return FormattedResponse(
            content=content,
            mime_type="text/plain",
            metadata={
                "pattern_count": len(patterns),
                "displayed_count": min(len(patterns), self.max_patterns),
                "specialist": specialist_id,
                "truncated": len(patterns) > self.max_patterns
            }
        )

    def _format_pattern_compact(self, pattern: Dict, index: int) -> List[str]:
        """Format a single pattern compactly."""
        lines = []

        # Number + name
        name = pattern.get("name", "Unknown Pattern")
        pattern_type = pattern.get("type") or pattern.get("pattern_type", "")

        if self.show_type and pattern_type:
            lines.append(f"{index}. {name} ({pattern_type})")
        else:
            lines.append(f"{index}. {name}")

        # Truncated solution
        solution = pattern.get("solution", "")
        if solution:
            if len(solution) > self.max_length:
                solution = solution[:self.max_length] + "..."
            lines.append(f"   {solution}")

        return lines

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["compact", "terminal", "cli", "text"]


class UltraCompactFormatter(CompactFormatter):
    """
    Ultra-minimal formatter.

    Shows ONLY pattern names, one per line.
    Absolute minimum output.
    """

    name = "Ultra Compact Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        config["max_patterns"] = 10  # Show more patterns
        config["max_length"] = 0  # No solution text
        config["show_specialist"] = False
        config["show_confidence"] = False
        config["show_type"] = False
        super().__init__(config)

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format with just pattern names."""
        patterns = response_data.get("patterns", [])

        if not patterns:
            return FormattedResponse(
                content="No patterns found",
                mime_type="text/plain"
            )

        lines = []
        for pattern in patterns[:self.max_patterns]:
            name = pattern.get("name", "Unknown")
            lines.append(f"- {name}")

        if len(patterns) > self.max_patterns:
            lines.append(f"... and {len(patterns) - self.max_patterns} more")

        content = "\n".join(lines)

        return FormattedResponse(
            content=content,
            mime_type="text/plain",
            metadata={"pattern_count": len(patterns)}
        )

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["ultra-compact", "minimal", "names-only"]


class TableFormatter(CompactFormatter):
    """
    Tabular format for terminal display.

    Shows patterns in a simple table structure.
    """

    name = "Table Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        config["max_patterns"] = 10
        super().__init__(config)

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format as a simple table."""
        patterns = response_data.get("patterns", [])

        if not patterns:
            return FormattedResponse(
                content="No patterns found",
                mime_type="text/plain"
            )

        lines = []

        # Table header
        lines.append(f"{'#':<3} {'Name':<30} {'Type':<15} {'Solution':<40}")
        lines.append("-" * 90)

        # Table rows
        for i, pattern in enumerate(patterns[:self.max_patterns], 1):
            name = pattern.get("name", "Unknown")[:30]
            pattern_type = (pattern.get("type") or pattern.get("pattern_type", "N/A"))[:15]
            solution = pattern.get("solution", "")[:40]

            lines.append(f"{i:<3} {name:<30} {pattern_type:<15} {solution:<40}")

        if len(patterns) > self.max_patterns:
            lines.append(f"\n... and {len(patterns) - self.max_patterns} more patterns")

        content = "\n".join(lines)

        return FormattedResponse(
            content=content,
            mime_type="text/plain",
            metadata={"pattern_count": len(patterns)}
        )

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["table", "tabular"]
