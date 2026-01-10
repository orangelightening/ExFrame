"""
AI-Powered Scraper - Uses LLM to extract structured data from web pages

Instead of rule-based scraping, use an LLM to:
1. Parse recipe pages into structured JSON
2. Extract patterns from the clean data

This produces consistent, validated output.
"""

import json
import re
from typing import Dict, List, Optional
from extraction.prompts import get_prompt, PromptTemplate


class AIPoweredExtractor:
    """
    Uses LLM to extract structured recipe data and patterns.

    The LLM acts as an intelligent scraper that:
    - Parses unstructured HTML/text into structured recipe data
    - Extracts meaningful patterns from that data
    - Validates output against templates
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def scrape_recipe_with_llm(self, html_content: str, url: str) -> Dict:
        """
        Use LLM to parse recipe HTML into structured data.

        Args:
            html_content: Raw HTML from recipe page
            url: Source URL

        Returns:
            Structured recipe dict with clean, validated fields
        """
        prompt = self._build_recipe_scraping_prompt(html_content, url)

        response = self._call_llm(prompt)
        return self._parse_structured_response(response)

    def extract_patterns_from_recipe(self, recipe_data: Dict) -> List[Dict]:
        """
        Extract patterns from clean structured recipe data.

        Args:
            recipe_data: Structured recipe from LLM scraper

        Returns:
            List of pattern dictionaries
        """
        prompt = self._build_pattern_extraction_prompt(recipe_data)

        response = self._call_llm(prompt)
        return self._parse_pattern_response(response)

    def _build_recipe_scraping_prompt(self, html_content: str, url: str) -> str:
        """Build prompt to extract structured recipe data from HTML."""

        # Clean HTML - remove scripts, styles, etc.
        clean_html = self._clean_html(html_content)

        prompt = f"""You are an expert web scraper. Extract structured recipe data from the following HTML.

SOURCE URL: {url}

HTML CONTENT:
{clean_html[:10000]}

Extract the following fields as JSON:
{{
  "title": "recipe name",
  "description": "brief description",
  "ingredients": [
    {{"amount": "1 cup", "item": "flour", "notes": ""}},
    {{"amount": "2 tsp", "item": "salt", "notes": ""}}
  ],
  "steps": [
    "Preheat oven to 350°F",
    "Mix ingredients together"
  ],
  "prep_time": "30 minutes",
  "cook_time": "1 hour",
  "total_time": "1 hour 30 minutes",
  "servings": "8",
  "category": "dinner",
  "tags": ["easy", "comfort-food"]
}}

Return ONLY valid JSON. If a field is missing, use empty string or empty array.
"""
        return prompt

    def _build_pattern_extraction_prompt(self, recipe_data: Dict) -> str:
        """Build prompt to extract patterns from structured recipe."""

        recipe_text = f"""Recipe: {recipe_data.get('title', '')}
Description: {recipe_data.get('description', '')}

Ingredients:
{chr(10).join(f'- {ing.get("amount", "")} {ing.get("item", "")}' for ing in recipe_data.get('ingredients', []))}

Steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(recipe_data.get('steps', [])))}
"""

        prompt = f"""You are an expert at analyzing cooking expertise. Extract reusable patterns from this recipe:

{recipe_text}

Look for patterns like:
- **Procedures**: Step-by-step techniques that could apply to other dishes
- **Substitutions**: Ingredient swaps mentioned or implied
- **Principles**: Fundamental cooking rules demonstrated
- **Troubleshooting**: Tips for when things go wrong

Return as a JSON array of patterns:
[
  {{
    "name": "Descriptive pattern name",
    "pattern_type": "procedure|substitution|principle|troubleshooting",
    "description": "What this pattern does in 1-2 sentences",
    "problem": "What problem does this solve?",
    "solution": "How is it solved?",
    "steps": ["step 1", "step 2"],
    "tags": ["tag1", "tag2"]
  }}
]

Return ONLY valid JSON array. If no clear patterns found, return empty array [].
"""
        return prompt

    def _clean_html(self, html: str) -> str:
        """Remove noise from HTML."""
        # Remove script tags, style tags, comments
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

        # Remove excessive whitespace
        html = re.sub(r'\s+', ' ', html)

        return html.strip()

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the prompt."""
        if self.llm_client:
            return self.llm_client.generate(prompt)
        else:
            # Mock response for now - TODO: integrate actual LLM
            return self._mock_llm_response(prompt)

    def _mock_llm_response(self, prompt: str) -> str:
        """Mock response for testing."""
        # Return empty array to indicate no LLM available
        return "[]"

    def _parse_structured_response(self, response: str) -> Dict:
        """Parse LLM response into structured dict."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
            return {}
        except:
            return {}

    def _parse_pattern_response(self, response: str) -> List[Dict]:
        """Parse LLM pattern response."""
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data if isinstance(data, list) else [data]
            return []
        except:
            return []


# Template-based extraction prompts

COOKING_EXTRACTION_TEMPLATE = """
You are analyzing a cooking recipe to extract reusable expertise patterns.

RECIPE:
{recipe_content}

Extract patterns following these templates:

**Procedure Pattern:**
- Used when: Step-by-step cooking process
- Extract: The core technique that applies to multiple dishes
- Example: "Cream Sauce Base" from mac & cheese → applies to any creamy sauce

**Substitution Pattern:**
- Used when: Alternative ingredients mentioned
- Extract: What can replace what and in what ratio
- Example: "Butter → Oil (3:4 ratio)" for baking

**Temperature/Time Pattern:**
- Used when: Specific cooking conditions
- Extract: Temperature + time combinations
- Example: "350°F for 30-45 minutes" for casseroles

**Equipment Pattern:**
- Used when: Specific tools required
- Extract: Tool + purpose + alternatives
- Example: "9x13 baking dish" for casseroles

Return JSON array of patterns found.
"""

def get_ai_extraction_prompt(domain: str, content: str) -> str:
    """Get domain-specific AI extraction prompt."""

    templates = {
        'cooking': COOKING_EXTRACTION_TEMPLATE,
        'python': """
You are analyzing Python code to extract reusable patterns.

Focus on:
- Code patterns (idioms, design patterns)
- Error handling approaches
- Performance optimizations
- Library usage patterns

Return JSON array of patterns.
""",
        'diy': """
You are analyzing DIY instructions to extract reusable patterns.

Focus on:
- Tool usage patterns
- Material substitutions
- Safety procedures
- Step-by-step techniques

Return JSON array of patterns.
""",
    }

    template = templates.get(domain, templates['cooking'])
    return template.format(recipe_content=content)
