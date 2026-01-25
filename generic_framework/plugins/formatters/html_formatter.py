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
HTML Formatter Plugin

Formats specialist responses as HTML with CSS styling.
Ideal for web applications and rich display.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add framework to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.formatter_plugin import FormatterPlugin, FormattedResponse


class HTMLFormatter(FormatterPlugin):
    """
    Format specialist responses as styled HTML.

    Provides:
    - Full HTML document structure with CSS
    - Responsive design
    - Syntax highlighting for code
    - Collapsible sections
    - Print-friendly styles
    """

    name = "HTML Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.include_styles = self.config.get("include_styles", True)
        self.include_metadata = self.config.get("include_metadata", True)
        self.max_examples_per_pattern = self.config.get("max_examples_per_pattern", 3)

    def format(self, response_data: Dict[str, Any]) -> FormattedResponse:
        """Format response data as HTML."""
        if not self.validate_response_data(response_data):
            return FormattedResponse(
                content="<html><body><h1>Error</h1><p>Invalid response data</p></body></html>",
                mime_type="text/html"
            )

        query = response_data.get("query", "")
        patterns = response_data.get("patterns", [])
        specialist_id = response_data.get("specialist_id", "unknown")
        confidence = response_data.get("confidence", 0.0)

        # Build HTML
        html_parts = []

        # HTML header
        if self.include_styles:
            html_parts.append(self._get_html_header(query))
        else:
            html_parts.append("<html><head><title>Results</title></head><body>")

        # Query header
        html_parts.append(f'<div class="container">')
        html_parts.append(f'<h1 class="query-title">Results for: {self._escape(query)}</h1>')

        # Metadata
        if self.include_metadata:
            html_parts.append(f'''
            <div class="metadata">
                <span class="specialist">Specialist: {self._escape(specialist_id)}</span>
                <span class="confidence">Confidence: {confidence:.1%}</span>
                <span class="pattern-count">{len(patterns)} pattern(s) found</span>
            </div>
            ''')

        html_parts.append('</div>')

        # Patterns
        if patterns:
            for i, pattern in enumerate(patterns, 1):
                html_parts.append(self._format_pattern_html(pattern, i))
        else:
            html_parts.append('<div class="no-results">No patterns found.</div>')

        # Footer
        html_parts.append('</body></html>')

        content = "\n".join(html_parts)

        return FormattedResponse(
            content=content,
            mime_type="text/html",
            metadata={
                "pattern_count": len(patterns),
                "specialist": specialist_id,
                "styled": self.include_styles
            }
        )

    def _get_html_header(self, query: str) -> str:
        """Generate HTML header with CSS styles."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results for: {self._escape(query)[:50]}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .query-title {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 28px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        .metadata {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}

        .metadata span {{
            background: #ecf0f1;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }}

        .specialist {{ color: #8e44ad; }}
        .confidence {{ color: #27ae60; }}
        .pattern-count {{ color: #e74c3c; }}

        .pattern {{
            margin-bottom: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 6px;
        }}

        .pattern-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .pattern-name {{
            font-size: 22px;
            color: #2c3e50;
            font-weight: 600;
        }}

        .pattern-type {{
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 500;
        }}

        .pattern-section {{
            margin-bottom: 15px;
        }}

        .pattern-section h4 {{
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .pattern-section p, .pattern-section div {{
            color: #34495e;
            margin-left: 0;
        }}

        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}

        .tag {{
            background: #e8f4f8;
            color: #2980b9;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 13px;
        }}

        .examples {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }}

        .example {{
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}

        .example:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}

        .example-code {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 12px;
            border-radius: 4px;
            font-family: "Monaco", "Menlo", monospace;
            font-size: 13px;
            overflow-x: auto;
            margin-top: 5px;
        }}

        .enrichment {{
            background: #fff9e6;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
            border: 1px solid #ffeaa7;
        }}

        .enrichment h5 {{
            color: #d35400;
            margin-bottom: 10px;
            font-size: 14px;
        }}

        .quality-score {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
        }}

        .quality-A {{ background: #d4edda; color: #155724; }}
        .quality-B {{ background: #cce5ff; color: #004085; }}
        .quality-C {{ background: #fff3cd; color: #856404; }}
        .quality-D {{ background: #f8d7da; color: #721c24; }}
        .quality-F {{ background: #f5c6cb; color: #721c24; }}

        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #95a5a6;
            font-size: 18px;
        }}

        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
            .pattern {{ page-break-inside: avoid; }}
        }}

        @media (max-width: 768px) {{
            .metadata {{
                flex-direction: column;
                gap: 10px;
            }}
            .pattern-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
        }}
    </style>
</head>'''

    def _format_pattern_html(self, pattern: Dict, index: int) -> str:
        """Format a single pattern as HTML."""
        parts = []

        name = pattern.get("name", "Unknown Pattern")
        pattern_type = pattern.get("type") or pattern.get("pattern_type", "")
        description = pattern.get("description", "")
        problem = pattern.get("problem", "")
        solution = pattern.get("solution", "")
        tags = pattern.get("tags", [])
        examples = pattern.get("examples", [])[:self.max_examples_per_pattern]

        # Pattern container
        parts.append(f'<div class="pattern">')

        # Header
        parts.append(f'''
        <div class="pattern-header">
            <div class="pattern-name">{index}. {self._escape(name)}</div>
            <div class="pattern-type">{self._escape(pattern_type)}</div>
        </div>
        ''')

        # Description
        if description:
            parts.append(f'''
            <div class="pattern-section">
                <h4>Description</h4>
                <p>{self._escape(description)}</p>
            </div>
            ''')

        # Problem
        if problem:
            parts.append(f'''
            <div class="pattern-section">
                <h4>Problem</h4>
                <p>{self._escape(problem)}</p>
            </div>
            ''')

        # Solution
        if solution:
            parts.append(f'''
            <div class="pattern-section">
                <h4>Solution</h4>
                <p>{self._escape(solution)}</p>
            </div>
            ''')

        # Tags
        if tags:
            parts.append('<div class="pattern-section">')
            parts.append('<h4>Tags</h4>')
            parts.append('<div class="tags">')
            for tag in tags:
                parts.append(f'<span class="tag">{self._escape(tag)}</span>')
            parts.append('</div></div>')

        # Examples
        if examples:
            parts.append('<div class="pattern-section">')
            parts.append('<h4>Examples</h4>')
            parts.append('<div class="examples">')
            for example in examples:
                parts.append(self._format_example_html(example))
            parts.append('</div></div>')

        # Enrichment data (quality scores, usage stats, etc.)
        enrichment = self._format_enrichment_html(pattern)
        if enrichment:
            parts.append(f'<div class="enrichment">{enrichment}</div>')

        parts.append('</div>')

        return "\n".join(parts)

    def _format_example_html(self, example: Any) -> str:
        """Format an example as HTML."""
        if isinstance(example, dict):
            parts = ['<div class="example">']
            for key, value in example.items():
                if isinstance(value, (list, dict)):
                    value_str = str(value)
                else:
                    value_str = str(value)

                # Check if it looks like code
                if any(s in key.lower() for s in ["code", "input", "output", "result"]):
                    parts.append(f'<div><strong>{self._escape(key)}:</strong></div>')
                    parts.append(f'<div class="example-code">{self._escape(value_str)}</div>')
                else:
                    parts.append(f'<div><strong>{self._escape(key)}:</strong> {self._escape(value_str)}</div>')
            parts.append('</div>')
            return "\n".join(parts)
        else:
            return f'<div class="example">{self._escape(str(example))}</div>'

    def _format_enrichment_html(self, pattern: Dict) -> Optional[str]:
        """Format enrichment data as HTML."""
        parts = []

        # Quality score
        quality = pattern.get("quality_score")
        if quality:
            grade = quality.get("grade", "N/A")
            overall = quality.get("overall", 0)
            parts.append(f'<div class="quality-score quality-{grade}">Quality: {grade} ({overall:.0%})</div>')

        # Usage stats
        usage = pattern.get("usage_stats")
        if usage:
            uses = usage.get("total_uses", 0)
            success = usage.get("success_rate", 0)
            parts.append(f'<div>Used {uses} times, {success:.0%} success rate</div>')

        # Code examples
        code_examples = pattern.get("code_examples")
        if code_examples:
            parts.append('<h5>Code Examples</h5>')
            for lang, code_data in code_examples.items():
                parts.append(f'<div><strong>{lang}</strong></div>')
                if isinstance(code_data, dict) and "blocks" in code_data:
                    for block in code_data["blocks"][:1]:  # First block only
                        code = block.get("code", "")
                        parts.append(f'<div class="example-code">{self._escape(code)}</div>')

        # Related patterns
        related = pattern.get("related_patterns")
        if related:
            parts.append('<h5>Related Patterns</h5>')
            parts.append('<div class="tags">')
            for rel in related[:5]:
                name = rel.get("name", "Unknown")
                sim = rel.get("similarity", 0)
                parts.append(f'<span class="tag">{self._escape(name)} ({sim:.0%})</span>')
            parts.append('</div>')

        return "\n".join(parts) if parts else None

    def _escape(self, text: str) -> str:
        """Escape HTML special characters."""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))

    def get_supported_formats(self) -> List[str]:
        return ["html", "htm"]


class SimpleHTMLFormatter(HTMLFormatter):
    """
    Simplified HTML formatter without inline styles.

    Best for integration with existing CSS frameworks.
    """

    name = "Simple HTML Formatter"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        config["include_styles"] = False
        super().__init__(config)

    def _format_pattern_html(self, pattern: Dict, index: int) -> str:
        """Format pattern with semantic HTML only."""
        name = pattern.get("name", "Unknown Pattern")
        pattern_type = pattern.get("type") or pattern.get("pattern_type", "")
        description = pattern.get("description", "")
        solution = pattern.get("solution", "")

        parts = [f'<article class="pattern" data-type="{self._escape(pattern_type)}">']
        parts.append(f'<h2>{index}. {self._escape(name)}</h2>')
        parts.append(f'<span class="type">{self._escape(pattern_type)}</span>')

        if description:
            parts.append(f'<p class="description">{self._escape(description)}</p>')

        if solution:
            parts.append(f'<div class="solution">{self._escape(solution)}</div>')

        parts.append('</article>')
        return "\n".join(parts)

    def get_supported_formats(self) -> List[str]:
        return ["html-simple", "html-nostyle"]
