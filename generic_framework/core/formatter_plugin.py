"""
Formatter Plugin System

A formatter plugin converts specialist response data into formatted output.
This enables multiple output formats (Markdown, JSON, HTML, etc.) from the same data.

Formatter plugins can implement:
- Markdown formatting (default, human-readable)
- JSON formatting (API-friendly)
- Compact formatting (terminal/CLI)
- HTML formatting (web display)
- Custom formatting (Slack, voice, rich terminal, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FormattedResponse:
    """
    Container for formatted response with metadata.

    Attributes:
        content: The formatted content as a string
        mime_type: MIME type of the content (e.g., "text/markdown", "application/json")
        metadata: Formatter-specific metadata (e.g., pattern counts, truncation info)
        encoding: Character encoding (default: "utf-8")
    """
    content: str
    mime_type: str = "text/plain"
    metadata: Dict[str, Any] = field(default_factory=dict)
    encoding: str = "utf-8"


class FormatterPlugin(ABC):
    """
    A formatter plugin converts specialist response data into formatted output.

    The formatter receives response_data from a specialist (or aggregated from
    multiple specialists) and returns formatted content.

    This separation allows:
    - Specialists to focus on logic, not formatting
    - Multiple output formats from the same data
    - Consistent formatting across domains
    """

    name: str = "Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the formatter.

        Args:
            config: Optional configuration dict with formatter-specific settings
        """
        self.config = config or {}

    @abstractmethod
    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """
        Format specialist response data into final output.

        Args:
            response_data: Dict containing at least:
                - query: str - The original query
                - patterns: List[Dict] - Found patterns
                - specialist_id: str - Which specialist handled it
                - confidence: float - Confidence score
                - aggregation_strategy: str (optional) - For multi-specialist results
                - responses: List[Dict] (optional) - Individual specialist responses

        Returns:
            FormattedResponse with formatted content and metadata
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Return list of output format names this formatter supports.

        Examples:
            ["markdown", "md"]
            ["json"]
            ["compact", "terminal", "cli"]
        """
        pass

    def validate_response_data(self, response_data: Dict[str, Any]) -> bool:
        """
        Validate that response_data has required fields.

        Default implementation checks for required fields.
        Override for custom validation.

        Args:
            response_data: The response data to validate

        Returns:
            True if valid, False otherwise
        """
        required = ["query", "patterns", "specialist_id"]
        return all(key in response_data for key in required)

    def get_content_type(self) -> str:
        """
        Get the HTTP Content-Type header for this formatter.

        Returns:
            Content-Type string (e.g., "text/markdown; charset=utf-8")
        """
        mime = self.format({"query": "", "patterns": [], "specialist_id": ""}).mime_type
        encoding = self.format({"query": "", "patterns": [], "specialist_id": ""}).encoding
        return f"{mime}; charset={encoding}"

    def supports_format(self, format_name: str) -> bool:
        """
        Check if this formatter supports the given format name.

        Args:
            format_name: The format to check (e.g., "markdown", "json")

        Returns:
            True if supported, False otherwise
        """
        return format_name.lower() in [f.lower() for f in self.get_supported_formats()]


class ChainedFormatter(FormatterPlugin):
    """
    Compose multiple formatters in sequence.

    Each formatter receives the output of the previous formatter.
    Useful for post-processing (e.g., syntax highlighting, caching).
    """

    name = "Chained Formatter"

    def __init__(self, formatters: List[FormatterPlugin], config: Optional[Dict[str, Any]] = None):
        """
        Initialize with a list of formatters to chain.

        Args:
            formatters: List of formatters to apply in order
            config: Optional config (passed to first formatter)
        """
        super().__init__(config)
        self.formatters = formatters

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Apply formatters in sequence."""
        current_data = response_data

        for formatter in self.formatters:
            result = formatter.format(current_data)

            # Pass result as input to next formatter
            current_data = {
                "query": current_data.get("query", ""),
                "patterns": current_data.get("patterns", []),
                "specialist_id": current_data.get("specialist_id", ""),
                "formatted_content": result.content,
                "metadata": result.metadata
            }

        return result

    def get_supported_formats(self) -> List[str]:
        """Return combined formats from all formatters."""
        formats = []
        for formatter in self.formatters:
            formats.extend(formatter.get_supported_formats())
        return list(set(formats))
