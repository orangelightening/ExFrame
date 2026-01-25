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
Slack Formatter Plugin

Formats specialist responses as Slack blocks API format.
Ideal for Slack app integration and bot responses.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.formatter_plugin import FormatterPlugin, FormattedResponse


class SlackFormatter(FormatterPlugin):
    """
    Format specialist responses as Slack blocks.

    Provides:
    - Slack Block Kit formatting
    - Interactive elements (buttons, links)
    - Rich text formatting
    - Proper escaping for Slack
    - Section and divider blocks
    """

    name = "Slack Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_patterns = self.config.get("max_patterns", 5)
        self.include_dividers = self.config.get("include_dividers", True)
        self.use_fields = self.config.get("use_fields", True)

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format response data as Slack blocks."""
        if not self.validate_response_data(response_data):
            return FormattedResponse(
                content=self._error_blocks("Invalid response data"),
                mime_type="application/json"
            )

        query = response_data.get("query", "")
        patterns = response_data.get("patterns", [])
        specialist_id = response_data.get("specialist_id", "unknown")
        confidence = response_data.get("confidence", 0.0)

        # Build blocks
        blocks = []

        # Header block
        blocks.append(self._header_block(query, specialist_id, confidence))

        # Divider
        if self.include_dividers:
            blocks.append({"type": "divider"})

        # Patterns
        display_patterns = patterns[:self.max_patterns]

        for i, pattern in enumerate(display_patterns, 1):
            blocks.extend(self._pattern_blocks(pattern, i))

            # Divider between patterns
            if self.include_dividers and i < len(display_patterns):
                blocks.append({"type": "divider"})

        # Truncation notice
        if len(patterns) > self.max_patterns:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"... and {len(patterns) - self.max_patterns} more patterns"
                    }
                ]
            })

        # Create Slack message payload
        payload = {
            "blocks": blocks
        }

        import json
        content = json.dumps(payload, indent=2)

        return FormattedResponse(
            content=content,
            mime_type="application/json",
            metadata={
                "pattern_count": len(patterns),
                "displayed_count": len(display_patterns),
                "block_count": len(blocks),
                "truncated": len(patterns) > self.max_patterns
            }
        )

    def _header_block(self, query: str, specialist: str, confidence: float) -> Dict:
        """Create header block."""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Results for: {self._escape(query)}*\n"
                        f"_Specialist: {self._escape(specialist)} | "
                        f"Confidence: {confidence:.0%}_"
            }
        }

    def _pattern_blocks(self, pattern: Dict, index: int) -> List[Dict]:
        """Create blocks for a single pattern."""
        blocks = []

        name = pattern.get("name", "Unknown Pattern")
        pattern_type = pattern.get("type") or pattern.get("pattern_type", "")
        description = pattern.get("description", "")
        solution = pattern.get("solution", "")
        tags = pattern.get("tags", [])
        examples = pattern.get("examples", [])[:2]

        # Pattern name and type
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{index}. {self._escape(name)}*\n"
                        f"`{self._escape(pattern_type)}`"
            }
        })

        # Description
        if description:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description*\n{self._escape(description)}"
                }
            })

        # Solution (use fields for compact display)
        if solution:
            if self.use_fields:
                blocks.append({
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Solution*\n{self._truncate(self._escape(solution), 200)}"
                        }
                    ]
                })
            else:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Solution*\n{self._escape(solution)}"
                    }
                })

        # Tags (use fields for compact display)
        if tags:
            tags_text = " | ".join(f"`{tag}`" for tag in tags[:5])
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": tags_text
                    }
                ]
            })

        # Examples
        if examples:
            example_texts = []
            for example in examples:
                if isinstance(example, dict):
                    ex_text = " • ".join(
                        f"{k}: {v}" for k, v in list(example.items())[:3]
                    )
                    example_texts.append(f"• {ex_text}")
                else:
                    example_texts.append(f"• {example}")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Examples*\n" + "\n".join(example_texts[:2])
                }
            })

        return blocks

    def _error_blocks(self, message: str) -> str:
        """Create error blocks."""
        import json
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"Error: {message}",
                        "emoji": True
                    }
                }
            ]
        }
        return json.dumps(payload, indent=2)

    def _escape(self, text: str) -> str:
        """Escape special characters for Slack."""
        # Slack mrkdwn needs less escaping than regular markdown
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def get_supported_formats(self) -> List[str]:
        return ["slack", "slack-blocks"]


class SlackMarkdownFormatter(SlackFormatter):
    """
    Slack formatter using simpler markdown format.

    Uses Slack's markdown syntax instead of Block Kit.
    Best for simple messages and webhooks.
    """

    name = "Slack Markdown Formatter"

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format as simple Slack markdown."""
        if not self.validate_response_data(response_data):
            return FormattedResponse(
                content="Error: Invalid response data",
                mime_type="text/plain"
            )

        query = response_data.get("query", "")
        patterns = response_data.get("patterns", [])
        specialist_id = response_data.get("specialist_id", "unknown")
        confidence = response_data.get("confidence", 0.0)

        # Build markdown text
        lines = []

        # Header
        lines.append(f"*Results for: {self._escape(query)}*")
        lines.append(f"_Specialist: {specialist_id} | Confidence: {confidence:.0%}_")
        lines.append("")

        # Patterns
        for i, pattern in enumerate(patterns[:self.max_patterns], 1):
            lines.extend(self._pattern_markdown(pattern, i))

        # Truncation notice
        if len(patterns) > self.max_patterns:
            lines.append(f"\n... and {len(patterns) - self.max_patterns} more patterns")

        content = "\n".join(lines)

        return FormattedResponse(
            content=content,
            mime_type="text/plain",
            metadata={
                "pattern_count": len(patterns),
                "slack_markdown": True
            }
        )

    def _pattern_markdown(self, pattern: Dict, index: int) -> List[str]:
        """Format pattern as Slack markdown."""
        lines = []

        name = pattern.get("name", "Unknown Pattern")
        pattern_type = pattern.get("type") or pattern.get("pattern_type", "")
        description = pattern.get("description", "")
        solution = pattern.get("solution", "")
        tags = pattern.get("tags", [])

        # Name and type
        lines.append(f"*{index}. {name}* `{pattern_type}`")
        lines.append("")

        # Description
        if description:
            lines.append(f"{description}")
            lines.append("")

        # Solution
        if solution:
            # Use code block for solution
            lines.append(f"```")
            lines.append(f"{solution}")
            lines.append(f"```")
            lines.append("")

        # Tags
        if tags:
            tags_str = " | ".join(f"`{tag}`" for tag in tags[:5])
            lines.append(tags_str)
            lines.append("")

        return lines


class SlackAttachmentFormatter(SlackFormatter):
    """
    Legacy Slack attachment format.

    Uses the older attachment format for compatibility
    with legacy Slack integrations.
    """

    name = "Slack Attachment Formatter"

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format as Slack attachments."""
        if not self.validate_response_data(response_data):
            return FormattedResponse(
                content=self._error_attachment("Invalid response data"),
                mime_type="application/json"
            )

        query = response_data.get("query", "")
        patterns = response_data.get("patterns", [])
        specialist_id = response_data.get("specialist_id", "unknown")
        confidence = response_data.get("confidence", 0.0)

        # Build attachments
        attachments = []

        # Summary attachment
        attachments.append({
            "color": "#36a64f",
            "title": f"Results for: {query[:100]}",
            "fields": [
                {
                    "title": "Specialist",
                    "value": specialist_id,
                    "short": True
                },
                {
                    "title": "Confidence",
                    "value": f"{confidence:.0%}",
                    "short": True
                },
                {
                    "title": "Patterns Found",
                    "value": str(len(patterns)),
                    "short": True
                }
            ]
        })

        # Pattern attachments
        for i, pattern in enumerate(patterns[:self.max_patterns], 1):
            attachments.append(self._pattern_attachment(pattern, i))

        # Truncation notice
        if len(patterns) > self.max_patterns:
            attachments.append({
                "text": f"... and {len(patterns) - self.max_patterns} more patterns",
                "color": "#808080"
            })

        payload = {
            "attachments": attachments
        }

        import json
        content = json.dumps(payload, indent=2)

        return FormattedResponse(
            content=content,
            mime_type="application/json",
            metadata={
                "pattern_count": len(patterns),
                "attachment_count": len(attachments)
            }
        )

    def _pattern_attachment(self, pattern: Dict, index: int) -> Dict:
        """Create attachment for a pattern."""
        name = pattern.get("name", "Unknown Pattern")
        pattern_type = pattern.get("type") or pattern.get("pattern_type", "")
        description = pattern.get("description", "")
        solution = pattern.get("solution", "")
        tags = pattern.get("tags", [])

        # Color by pattern type
        color_map = {
            "algorithm": "#36a64f",
            "technique": "#0072bb",
            "pattern": "#e96600",
            "property": "#8c8c8c",
        }
        color = color_map.get(pattern_type.lower(), "#808080")

        attachment = {
            "color": color,
            "title": f"{index}. {name}",
            "fields": [
                {
                    "title": "Type",
                    "value": pattern_type,
                    "short": True
                }
            ]
        }

        # Add description as pretext
        if description:
            attachment["pretext"] = description[:200]

        # Add solution as text
        if solution:
            attachment["text"] = f"*Solution:*\n```{solution[:300]}```"

        # Add tags
        if tags:
            attachment["fields"].append({
                "title": "Tags",
                "value": ", ".join(tags[:5]),
                "short": False
            })

        return attachment

    def _error_attachment(self, message: str) -> str:
        """Create error attachment."""
        import json
        payload = {
            "attachments": [
                {
                    "color": "#ff0000",
                    "title": "Error",
                    "text": message
                }
            ]
        }
        return json.dumps(payload, indent=2)
