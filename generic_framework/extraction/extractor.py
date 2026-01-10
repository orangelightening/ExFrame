"""
Pattern Extractor - Core Extraction Engine

Uses LLM (GLM-4.7) to extract expertise patterns from domain text.
"""

import json
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Pattern, PatternType, ExtractionResult
from .prompts import get_prompt, PromptTemplate


class PatternExtractor:
    """
    Extract expertise patterns from text using LLM.

    Supports multiple extraction modes:
    - General: Extract all patterns from text
    - Q&A: Extract from question-answer pairs
    - Procedure: Extract from step-by-step guides
    - Substitution: Extract substitution rules
    - Troubleshooting: Extract diagnostic patterns
    """

    def __init__(self, domain: str, llm_client=None):
        """
        Initialize the extractor.

        Args:
            domain: The domain being analyzed (cooking, python, diy, etc.)
            llm_client: Optional LLM client for making API calls
        """
        self.domain = domain
        self.llm_client = llm_client

    def extract_from_text(self, text: str, pattern_type: Optional[str] = None) -> ExtractionResult:
        """
        Extract patterns from raw text.

        Args:
            text: The text to analyze
            pattern_type: Optional hint about what pattern type to look for

        Returns:
            ExtractionResult with found patterns
        """
        prompt = get_prompt(
            PromptTemplate.GENERAL_EXTRACTION,
            domain=self.domain,
            text=text[:5000]  # Limit text length
        )

        response = self._call_llm(prompt)
        patterns = self._parse_patterns(response, source="text_input")

        return ExtractionResult(
            source="text_input",
            domain=self.domain,
            patterns_found=len(patterns),
            patterns=patterns,
            confidence=self._calculate_overall_confidence(patterns)
        )

    def extract_from_qa(self, question: str, answers: List[str]) -> ExtractionResult:
        """
        Extract pattern from Q&A pair.

        Args:
            question: The question being asked
            answers: List of answers provided

        Returns:
            ExtractionResult with extracted pattern
        """
        answers_text = "\n\n".join([f"Answer {i+1}: {a}" for i, a in enumerate(answers)])

        prompt = get_prompt(
            PromptTemplate.QA_PATTERN,
            domain=self.domain,
            question=question,
            answers=answers_text
        )

        response = self._call_llm(prompt)
        patterns = self._parse_patterns(response, source="qa_pair")

        return ExtractionResult(
            source="qa_pair",
            domain=self.domain,
            patterns_found=len(patterns),
            patterns=patterns,
            confidence=self._calculate_overall_confidence(patterns)
        )

    def extract_from_procedure(self, procedure: str) -> ExtractionResult:
        """
        Extract pattern from step-by-step procedure.

        Args:
            procedure: The procedural text

        Returns:
            ExtractionResult with extracted pattern
        """
        prompt = get_prompt(
            PromptTemplate.PROCEDURE,
            domain=self.domain,
            procedure=procedure
        )

        response = self._call_llm(prompt)
        patterns = self._parse_patterns(response, source="procedure")

        return ExtractionResult(
            source="procedure",
            domain=self.domain,
            patterns_found=len(patterns),
            patterns=patterns,
            confidence=self._calculate_overall_confidence(patterns)
        )

    def extract_substitutions(self, text: str) -> ExtractionResult:
        """
        Extract substitution patterns from text.

        Args:
            text: Text containing substitution information

        Returns:
            ExtractionResult with substitution patterns
        """
        prompt = get_prompt(
            PromptTemplate.SUBSTITUTION,
            domain=self.domain,
            text=text
        )

        response = self._call_llm(prompt)
        patterns = self._parse_patterns(response, source="substitution")

        return ExtractionResult(
            source="substitution",
            domain=self.domain,
            patterns_found=len(patterns),
            patterns=patterns,
            confidence=self._calculate_overall_confidence(patterns)
        )

    def extract_troubleshooting(self, text: str) -> ExtractionResult:
        """
        Extract troubleshooting pattern from text.

        Args:
            text: Text containing troubleshooting information

        Returns:
            ExtractionResult with troubleshooting pattern
        """
        prompt = get_prompt(
            PromptTemplate.TROUBLESHOOTING,
            domain=self.domain,
            text=text
        )

        response = self._call_llm(prompt)
        patterns = self._parse_patterns(response, source="troubleshooting")

        return ExtractionResult(
            source="troubleshooting",
            domain=self.domain,
            patterns_found=len(patterns),
            patterns=patterns,
            confidence=self._calculate_overall_confidence(patterns)
        )

    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with the prompt.

        TODO: Integrate with actual GLM-4.7 API

        For now, uses rule-based extraction.
        """
        if self.llm_client:
            # Use actual LLM
            return self.llm_client.generate(prompt)
        else:
            # Use rule-based extraction for now
            return self._rule_based_extraction(prompt)

    def _mock_llm_response(self, prompt: str) -> str:
        """
        Mock LLM response for testing.

        Returns a sample JSON response.
        """
        # Return a mock pattern for testing
        mock_pattern = [{
            "name": "Sample Pattern from " + self.domain,
            "pattern_type": "procedure",
            "description": "A sample extracted pattern",
            "problem": "A sample problem",
            "solution": "A sample solution",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "conditions": {},
            "tags": ["sample", "mock", self.domain]
        }]
        return json.dumps(mock_pattern, indent=2)

    def _rule_based_extraction(self, prompt: str) -> str:
        """
        Rule-based pattern extraction for cooking domain.

        Extracts actual patterns from recipe text when no LLM is available.
        """
        # Extract the text content from the prompt
        text_match = re.search(r'TEXT TO ANALYZE:\s*(.+?)(?=---|$)', prompt, re.DOTALL | re.IGNORECASE)
        if not text_match:
            text_match = re.search(r'Content:\s*(.+?)(?:---|INSTRUCTIONS|$)', prompt, re.DOTALL | re.IGNORECASE)
        if not text_match:
            # Just take everything after the first line
            lines = prompt.split('\n')
            text = '\n'.join(lines[1:]) if len(lines) > 1 else prompt
        else:
            text = text_match.group(1)

        # Clean up the text
        text = re.sub(r'^.{0,100}?Content:\s*', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = text.strip()

        patterns = []

        if self.domain == "cooking":
            patterns.extend(self._extract_cooking_patterns(text))
        else:
            # Generic procedural extraction for other domains
            patterns.extend(self._extract_generic_patterns(text))

        return json.dumps(patterns, indent=2)

    def _extract_cooking_patterns(self, text: str) -> List[Dict]:
        """Extract cooking-specific patterns from text."""
        patterns = []
        text_lower = text.lower()

        # Extract ingredients and their quantities
        ingredients = re.findall(r'(?:\d+[\s¼½¾⅓⅔⅛⅐⅑⅒]?(?:cup|cups?|tablespoon|tbsp|teaspoon|tsp|oz|ounce|pound|lb|gram|g|kg|ml|liter|piece|slice|clove|bunch|head|can|jar)[s\s]+?[a-z\s]+?(?:,|\n|for|\.))', text, re.IGNORECASE)
        ingredients.extend(re.findall(r'(\d+\s*(?:cup|tablespoon|teaspoon|oz|pound|gram|ml|piece|slice|clove|bunch|head|can|jar)[s]+?\s+[a-z\s]+?)(?:,|\n|\.|\s+for)', text, re.IGNORECASE))

        # Look for preparation steps
        steps_matches = re.findall(r'(?:preheat|heat|mix|combine|whisk|stir|beat|fold|add|pour|place|arrange|bake|cook|boil|simmer|fry|sauté|roast|grill)[^.]+\.?', text, re.IGNORECASE)

        # Look for substitution hints
        substitutions = re.findall(r'(?:you can|substitute|replace|use|instead of|alternative)[^.]+?(?:instead of|for|with)[^.]+\.?', text, re.IGNORECASE)

        # Look for temperature/time info
        temps = re.findall(r'(\d+\s*(?:degrees?°?|°)[CF])\s*(?:for\s*)?(\d+\s*(?:minutes?|hours?))?', text, re.IGNORECASE)
        cooking_times = re.findall(r'(?:cook|bake|simmer|boil|roast|grill)[^.]+?(\d+\s*(?:minutes?|hours?))', text, re.IGNORECASE)

        # Create a main recipe procedure pattern
        if steps_matches or ingredients:
            pattern_name = self._extract_recipe_name(text)
            steps = [s.strip() for s in steps_matches[:8]]  # Limit to first 8 steps

            if not steps:
                # Try numbered steps
                numbered_steps = re.findall(r'^\d+\.\s*(.+?)(?:\n\d+\.|$)', text, re.MULTILINE)
                steps = numbered_steps[:8]

            patterns.append({
                "name": pattern_name,
                "pattern_type": "procedure",
                "description": f"A step-by-step {pattern_name.lower()}",
                "problem": f"How to make {pattern_name.lower()}",
                "solution": f"Follow these steps to create {pattern_name.lower()}",
                "steps": steps if steps else ["Prepare ingredients", "Mix according to recipe", "Cook/bake as directed"],
                "conditions": {},
                "tags": self._extract_cooking_tags(text)
            })

        # Extract substitution patterns
        for sub in substitutions:
            if len(sub) > 20 and any(word in sub.lower() for word in ['substitute', 'replace', 'instead', 'alternative']):
                patterns.append({
                    "name": f"Ingredient Substitution",
                    "pattern_type": "substitution",
                    "description": "Substitute one ingredient for another",
                    "problem": "Missing an ingredient or need alternative",
                    "solution": sub.strip(),
                    "steps": [],
                    "conditions": {},
                    "tags": ["substitution", "ingredients"]
                })

        # Extract troubleshooting patterns (tips for when things go wrong)
        troubleshooting = re.findall(r'(?:if|when|should)[^.]+?(?:too|not|don\'t|won\'t|over|under)[^.]+\.?', text, re.IGNORECASE)
        for tip in troubleshooting[:3]:
            if len(tip) > 30:
                patterns.append({
                    "name": "Cooking Troubleshooting Tip",
                    "pattern_type": "troubleshooting",
                    "description": "Handle common cooking issues",
                    "problem": "Something might go wrong during cooking",
                    "solution": tip.strip(),
                    "steps": [],
                    "conditions": {},
                    "tags": ["troubleshooting", "tips"]
                })

        # If no patterns found, create a generic one from the text
        if not patterns and len(text) > 100:
            sentences = re.split(r'[.!?]+', text)
            main_sentences = [s.strip() for s in sentences if len(s.strip()) > 30][:5]
            patterns.append({
                "name": self._extract_recipe_name(text),
                "pattern_type": "procedure",
                "description": "Cooking instructions extracted from recipe",
                "problem": "How to prepare this recipe",
                "solution": "Follow the recipe steps",
                "steps": main_sentences if main_sentences else ["Follow the recipe instructions"],
                "conditions": {},
                "tags": self._extract_cooking_tags(text)
            })

        return patterns[:5]  # Limit to 5 patterns

    def _extract_generic_patterns(self, text: str) -> List[Dict]:
        """Extract generic procedural patterns for non-cooking domains."""
        patterns = []

        # Extract numbered steps
        numbered_steps = re.findall(r'^\d+\.\s*(.+?)(?:\n\d+\.|$)', text, re.MULTILINE)

        if numbered_steps:
            patterns.append({
                "name": f"Procedure from {self.domain}",
                "pattern_type": "procedure",
                "description": "Step-by-step procedure",
                "problem": "How to complete this task",
                "solution": "Follow these steps",
                "steps": numbered_steps[:10],
                "conditions": {},
                "tags": [self.domain, "procedure"]
            })

        return patterns[:3]

    def _extract_recipe_name(self, text: str) -> str:
        """Extract a recipe name from the text."""
        # Look for "Recipe: Full Title" pattern at the start - highest priority
        recipe_title_match = re.search(r'^Recipe:\s*(.+?)(?:\n|Description:|$)', text, re.IGNORECASE)
        if recipe_title_match:
            return recipe_title_match.group(1).strip()

        # Look for title patterns
        title_match = re.search(r'(?:title|name|recipe for):\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()

        # Look for recipe patterns at the start - but be more specific
        # Match things like "Easy Chicken Recipe" or "Simple Lemon Herb Chicken Recipe"
        recipe_match = re.search(r'^(.{10,100}?recipe)', text, re.IGNORECASE)
        if recipe_match:
            return recipe_match.group(1).strip()

        # Extract from URL if present - this gives us the slug which is usually descriptive
        url_match = re.search(r'/recipe/(\d+/[^/\s]+)', text, re.IGNORECASE)
        if url_match:
            name = url_match.group(1).split('/')[-1].replace('-', ' ').replace('_', ' ')
            return ' '.join(word.capitalize() for word in name.split())

        # As a last resort, look for multi-word recipe names (not just single ingredients)
        # Only match if it's 3+ words, which suggests a full recipe title
        multiword_match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+){2,})', text)
        if multiword_match:
            return multiword_match.group(1).strip()

        return f"Recipe from {self.domain.capitalize()}"

    def _extract_cooking_tags(self, text: str) -> List[str]:
        """Extract relevant cooking tags from text."""
        tags = ["cooking", "recipe"]

        # Method tags
        methods = {
            'bake': 'baking', 'roast': 'roasting', 'grill': 'grilling',
            'fry': 'frying', 'sauté': 'sautéing', 'boil': 'boiling',
            'simmer': 'simmering', 'steam': 'steaming', 'microwave': 'microwave'
        }
        for method, tag in methods.items():
            if method in text.lower():
                tags.append(tag)

        # Ingredient tags
        ingredients = ['chicken', 'beef', 'pork', 'fish', 'vegetarian', 'vegan', 'dairy', 'gluten']
        for ing in ingredients:
            if ing in text.lower():
                tags.append(ing)

        # Meal type tags
        meals = ['breakfast', 'lunch', 'dinner', 'dessert', 'snack', 'appetizer']
        for meal in meals:
            if meal in text.lower():
                tags.append(meal)

        return tags[:5]  # Limit to 5 tags

    def _parse_patterns(self, response: str, source: str) -> List[Pattern]:
        """
        Parse LLM response into Pattern objects.

        Args:
            response: JSON string from LLM
            source: Source identifier for tracking

        Returns:
            List of Pattern objects
        """
        patterns = []

        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Try parsing the whole response as JSON
                data = json.loads(response)

            # Handle single pattern vs array
            if isinstance(data, dict):
                data = [data]

            for item in data:
                try:
                    pattern = self._create_pattern_from_dict(item, source)
                    patterns.append(pattern)
                except Exception as e:
                    print(f"Error creating pattern from {item}: {e}")

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Response was: {response[:500]}")

        return patterns

    def _create_pattern_from_dict(self, data: Dict[str, Any], source: str) -> Pattern:
        """
        Create a Pattern object from parsed LLM response.

        Args:
            data: Dictionary from LLM response
            source: Source identifier

        Returns:
            Pattern object
        """
        # Convert string pattern_type to enum
        pattern_type_str = data.get("pattern_type", "procedure").lower()
        try:
            pattern_type = PatternType(pattern_type_str)
        except ValueError:
            pattern_type = PatternType.PROCEDURE

        # Create the pattern
        return Pattern(
            domain=self.domain,
            name=data.get("name", "Unnamed Pattern"),
            pattern_type=pattern_type,
            description=data.get("description", ""),
            problem=data.get("problem", ""),
            solution=data.get("solution", ""),
            steps=data.get("steps", []),
            conditions=data.get("conditions", {}),
            tags=data.get("tags", []),
            sources=[source] if source else [],
            confidence=0.7  # Default confidence, will be refined
        )

    def _calculate_overall_confidence(self, patterns: List[Pattern]) -> float:
        """
        Calculate overall confidence for an extraction result.

        Args:
            patterns: List of extracted patterns

        Returns:
            Average confidence score
        """
        if not patterns:
            return 0.0

        return sum(p.confidence for p in patterns) / len(patterns)

    def score_pattern_confidence(self, pattern: Pattern) -> float:
        """
        Score a pattern's reliability using LLM.

        TODO: Implement with actual LLM call

        Args:
            pattern: Pattern to score

        Returns:
            Confidence score 0-1
        """
        # For now, use simple heuristics
        score = 0.5  # Base score

        # Increase if has description
        if pattern.description:
            score += 0.1

        # Increase if has steps
        if pattern.steps:
            score += 0.1

        # Increase if has tags
        if pattern.tags:
            score += 0.1

        # Increase if has sources
        if pattern.sources:
            score += 0.1

        # Decrease if fields are empty
        if not pattern.problem or not pattern.solution:
            score -= 0.2

        return max(0.0, min(1.0, score))


class MultiSourceExtractor:
    """
    Extract patterns from multiple sources and merge results.
    """

    def __init__(self, domain: str, llm_client=None):
        self.extractor = PatternExtractor(domain, llm_client)

    def extract_from_urls(self, urls: List[str]) -> ExtractionResult:
        """
        Extract patterns from multiple URLs.

        TODO: Implement URL scraping

        Args:
            urls: List of URLs to scrape

        Returns:
            Combined extraction result
        """
        all_patterns = []
        errors = []

        for url in urls:
            try:
                # TODO: Implement scraping
                # text = scrape_url(url)
                # result = self.extractor.extract_from_text(text)
                pass
            except Exception as e:
                errors.append(f"Error processing {url}: {e}")

        return ExtractionResult(
            source="multiple_urls",
            domain=self.extractor.domain,
            patterns_found=len(all_patterns),
            patterns=all_patterns,
            confidence=0.0,
            errors=errors
        )


if __name__ == "__main__":
    # Test the extractor
    extractor = PatternExtractor(domain="cooking")

    # Test text extraction
    sample_text = """
    To replace butter with oil in baking:
    Use 3/4 cup of oil for every 1 cup of butter.
    This works for cakes, muffins, and quick breads.
    The texture may be slightly more dense.
    """

    result = extractor.extract_from_text(sample_text)
    print(f"Extracted {result.patterns_found} patterns:")
    for pattern in result.patterns:
        print(f"  - {pattern.name}")
