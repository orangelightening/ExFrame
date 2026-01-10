"""
JSON Formatter Plugin

Formats specialist responses as structured JSON.
Ideal for API clients and programmatic consumption.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.formatter_plugin import FormatterPlugin, FormattedResponse


class JSONFormatter(FormatterPlugin):
    """
    Format specialist responses as JSON.

    Provides clean, structured output suitable for:
    - API responses
    - Programmatic processing
    - Data export
    - Integration with other systems
    """

    name = "JSON Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the JSON formatter.

        Config options:
            - indent: int (default: 2) - JSON indentation (0 for compact)
            - sort_keys: bool (default: False) - Sort object keys alphabetically
            - include_raw_answer: bool (default: True) - Include specialist's raw answer
            - include_metadata: bool (default: True) - Include metadata section
            - pattern_fields: List[str] (default: None) - Specific fields to include (None = all)
        """
        super().__init__(config)
        self.indent = self.config.get("indent", 2)
        self.sort_keys = self.config.get("sort_keys", False)
        self.include_raw_answer = self.config.get("include_raw_answer", True)
        self.include_metadata = self.config.get("include_metadata", True)
        self.pattern_fields = self.config.get("pattern_fields")

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format response data as JSON."""
        if not self.validate_response_data(response_data):
            error_response = {
                "error": "Invalid response data",
                "missing_fields": self._get_missing_fields(response_data)
            }
            return FormattedResponse(
                content=json.dumps(error_response, indent=self.indent),
                mime_type="application/json"
            )

        # Build structured response
        structured = {
            "query": response_data.get("query", ""),
            "specialist": response_data.get("specialist_id", "unknown"),
            "confidence": response_data.get("confidence", 0.0),
            "patterns": self._format_patterns(response_data.get("patterns", [])),
            "pattern_count": len(response_data.get("patterns", []))
        }

        # Add raw answer if available
        if self.include_raw_answer and "raw_answer" in response_data:
            structured["raw_answer"] = response_data["raw_answer"]

        # Add aggregation info for multi-specialist
        aggregation = response_data.get("aggregation_strategy")
        if aggregation:
            structured["aggregation"] = {
                "strategy": aggregation,
                "specialist_count": response_data.get("specialist_count", 1)
            }

        # Add individual responses for multi-specialist
        if "responses" in response_data:
            structured["specialist_responses"] = response_data["responses"]

        # Add metadata
        if self.include_metadata:
            structured["metadata"] = self._extract_metadata(response_data)

        # Serialize
        content = json.dumps(structured, indent=self.indent, sort_keys=self.sort_keys)

        return FormattedResponse(
            content=content,
            mime_type="application/json",
            metadata={
                "pattern_count": structured["pattern_count"],
                "specialist": structured["specialist"],
                "confidence": structured["confidence"],
                "indent": self.indent
            }
        )

    def _format_patterns(self, patterns: List[Dict]) -> List[Dict]:
        """Format patterns for JSON output."""
        formatted = []

        for pattern in patterns:
            # Extract fields
            pattern_dict = {
                "id": pattern.get("pattern_id") or pattern.get("id", ""),
                "name": pattern.get("name", ""),
                "type": pattern.get("type") or pattern.get("pattern_type", ""),
                "description": pattern.get("description", ""),
            }

            # Add category/tags
            if "category" in pattern:
                pattern_dict["category"] = pattern["category"]
            if "tags" in pattern:
                pattern_dict["tags"] = pattern["tags"]

            # Add problem/solution
            if "problem" in pattern:
                pattern_dict["problem"] = pattern["problem"]
            if "solution" in pattern:
                pattern_dict["solution"] = pattern["solution"]

            # Add steps
            if "steps" in pattern:
                pattern_dict["steps"] = pattern["steps"]

            # Add examples
            if "examples" in pattern:
                pattern_dict["examples"] = pattern["examples"]

            # Add conditions
            if "conditions" in pattern:
                pattern_dict["conditions"] = pattern["conditions"]

            # Add related patterns
            if "related_patterns" in pattern:
                pattern_dict["related_patterns"] = pattern["related_patterns"]

            # Add confidence
            if "confidence" in pattern:
                pattern_dict["confidence"] = pattern["confidence"]

            # Add internal fields (for merge_all)
            if "_source_specialist" in pattern:
                pattern_dict["source_specialist"] = pattern["_source_specialist"]
            if "_combined_score" in pattern:
                pattern_dict["combined_score"] = pattern["_combined_score"]

            # Filter to specific fields if requested
            if self.pattern_fields:
                pattern_dict = {
                    k: v for k, v in pattern_dict.items()
                    if k in self.pattern_fields
                }

            formatted.append(pattern_dict)

        return formatted

    def _extract_metadata(self, response_data: Dict) -> Dict[str, Any]:
        """Extract metadata from response data."""
        metadata = {
            "formatter": "json",
            "formatter_version": "1.0.0"
        }

        # Add timing if available
        if "timing" in response_data:
            metadata["timing_ms"] = response_data["timing"]

        # Add domain if available
        if "domain_id" in response_data:
            metadata["domain"] = response_data["domain_id"]

        # Add timestamp
        from datetime import datetime
        metadata["formatted_at"] = datetime.utcnow().isoformat()

        return metadata

    def _get_missing_fields(self, response_data: Dict) -> List[str]:
        """Get list of missing required fields."""
        required = ["query", "patterns", "specialist_id"]
        return [field for field in required if field not in response_data]

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["json"]


class CompactJSONFormatter(JSONFormatter):
    """
    Compact JSON formatter with no indentation.

    Useful for:
    - Minimized API responses
    - Logging
    - Network transmission
    """

    name = "Compact JSON Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        config["indent"] = 0  # No indentation
        config["include_metadata"] = False  # Skip metadata
        config["include_raw_answer"] = False  # Skip raw answer
        super().__init__(config)

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["json-compact", "json-min"]


class PrettyJSONFormatter(JSONFormatter):
    """
    Pretty-printed JSON with extra formatting.

    Useful for:
    - Human-readable API responses
    - Debugging
    - Documentation
    """

    name = "Pretty JSON Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        config.setdefault("indent", 4)  # More indentation
        config.setdefault("sort_keys", True)  # Alphabetical keys
        config.setdefault("include_metadata", True)
        config.setdefault("include_raw_answer", True)
        super().__init__(config)

    def get_supported_formats(self) -> List[str]:
        """Return supported format names."""
        return ["json-pretty", "json-formatted"]
