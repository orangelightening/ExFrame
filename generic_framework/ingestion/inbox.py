"""
Pattern Inbox - Ingest recipes from AI-generated JSON files

Watches /development/eeframe/pattern-inbox/ for new JSON recipe files
and automatically extracts patterns from them.
"""

import json
import time
import glob
from pathlib import Path
from typing import List
from datetime import datetime

from generic_framework.extraction.extractor import PatternExtractor
from generic_framework.extraction.models import Pattern, PatternType


class PatternIngestionQueue:
    """
    Processes recipe JSON files from the AI-generated inbox.

    Monitors /development/eeframe/pattern-inbox/ for new JSON files
    and extracts patterns from them.
    """

    INBOX_PATH = Path("/home/peter/development/eeframe/pattern-inbox")
    PATTERNS_PATH = Path("/home/peter/development/eeframe/data/patterns")

    def __init__(self, domain: str = "cooking"):
        self.domain = domain
        self.processed_files = set()

    def scan_inbox(self) -> List[str]:
        """Scan inbox for new JSON files and return them."""
        if not self.INBOX_PATH.exists():
            return []

        json_files = list(self.INBOX_PATH.glob("recipe_*.json"))
        new_files = [f for f in json_files if str(f) not in self.processed_files]

        return new_files

    def process_file(self, file_path: Path) -> dict:
        """
        Process a single recipe JSON file and extract patterns.

        Args:
            file_path: Path to recipe JSON file

        Returns:
            Result dict with status and info
        """
        try:
            with open(file_path, 'r') as f:
                recipe = json.load(f)

            # Validate required fields
            if not recipe.get('title') or not recipe.get('steps'):
                return {
                    "file": str(file_path),
                    "status": "skipped",
                    "reason": "Missing required fields (title or steps)"
                }

            # Extract patterns from recipe
            extractor = PatternExtractor(domain=self.domain)
            recipe_text = self._recipe_to_text(recipe)

            extraction_result = extractor.extract_from_text(recipe_text)

            # Save patterns
            patterns_saved = self._save_patterns(
                extraction_result.patterns,
                source_url=recipe.get('url', file_path.name),
                rating=recipe.get('rating', 0)
            )

            # Mark as processed
            self.processed_files.add(str(file_path))

            return {
                "file": str(file_path),
                "status": "success",
                "recipe": recipe.get('title'),
                "patterns_extracted": len(extraction_result.patterns),
                "patterns_saved": patterns_saved
            }

        except json.JSONDecodeError as e:
            return {
                "file": str(file_path),
                "status": "error",
                "reason": f"Invalid JSON: {e}"
            }
        except Exception as e:
            return {
                "file": str(file_path),
                "status": "error",
                "reason": str(e)
            }

    def process_all(self) -> List[dict]:
        """Process all pending files in the inbox."""
        new_files = self.scan_inbox()

        if not new_files:
            return []

        results = []
        for file_path in new_files:
            result = self.process_file(file_path)
            results.append(result)

        return results

    def _recipe_to_text(self, recipe: dict) -> str:
        """Convert recipe dict to text for pattern extraction."""
        text = f"""Recipe: {recipe.get('title', '')}
Description: {recipe.get('description', '')}

Ingredients:
"""
        for ing in recipe.get('ingredients', []):
            if isinstance(ing, dict):
                amount = ing.get('amount', '')
                item = ing.get('item', '')
                notes = ing.get('notes', '')
                text += f"- {amount} {item}"
                if notes:
                    text += f" ({notes})"
                text += "\n"
            elif isinstance(ing, str):
                text += f"- {ing}\n"

        text += "\nSteps:\n"
        for i, step in enumerate(recipe.get('steps', [])):
            text += f"{i+1}. {step}\n"

        text += f"\nCategory: {recipe.get('category', '')}"
        text += f"\nTags: {', '.join(recipe.get('tags', []))}"

        return text

    def _save_patterns(self, patterns: list, source_url: str, rating: float = 0) -> int:
        """Save extracted patterns to the patterns file."""
        patterns_dir = self.PATTERNS_PATH / self.domain
        patterns_dir.mkdir(parents=True, exist_ok=True)

        pattern_file = patterns_dir / "patterns.json"

        # Load existing
        existing = []
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                existing = json.load(f)

        # Add new patterns
        for pattern in patterns:
            pattern_dict = pattern.model_dump(mode='json')
            pattern_dict["id"] = f"{self.domain}_{len(existing) + 1:03d}"
            pattern_dict["sources"] = [source_url]
            pattern_dict["rating"] = rating
            existing.append(pattern_dict)

        # Save
        with open(pattern_file, 'w') as f:
            json.dump(existing, f, indent=2)

        return len(patterns)


def ingest_from_inbox(domain: str = "cooking", force_reprocess: bool = False) -> dict:
    """
    Ingest all pending recipes from the inbox.

    Called by API to process AI-generated recipe files.

    Args:
        domain: The domain to categorize patterns under
        force_reprocess: If True, reprocess all files ignoring the processed cache
    """
    queue = PatternIngestionQueue(domain=domain)

    if force_reprocess:
        # Clear the processed files cache to force reprocessing
        queue.processed_files.clear()

    results = queue.process_all()

    return {
        "processed": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Test the inbox processor
    import sys

    domain = sys.argv[1] if len(sys.argv) > 1 else "cooking"

    print(f"Checking inbox for domain: {domain}")
    print("=" * 50)

    queue = PatternIngestionQueue(domain=domain)
    new_files = queue.scan_inbox()

    if not new_files:
        print("No new files to process")
    else:
        print(f"Found {len(new_files)} new files")
        print()

        for file_path in new_files:
            print(f"Processing: {file_path.name}")
            result = queue.process_file(file_path)
            print(f"  Status: {result['status']}")
            if result['status'] == 'success':
                print(f"  Recipe: {result['recipe']}")
                print(f"  Patterns extracted: {result['patterns_extracted']}")
                print(f"  Patterns saved: {result['patterns_saved']}")
            else:
                print(f"  Reason: {result.get('reason', 'Unknown')}")
            print()
