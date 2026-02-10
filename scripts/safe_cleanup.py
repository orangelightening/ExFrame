#!/usr/bin/env python3
"""
Remove only obviously garbage patterns (GitHub repos, blog posts, etc.)
Keep all AllRecipes recipe patterns.
"""
import json
from pathlib import Path

patterns_file = Path('universes/MINE/domains/cooking/patterns.json')
with open(patterns_file, 'r') as f:
    patterns = json.load(f)

print(f"Total patterns before cleanup: {len(patterns)}")

# Keep patterns that are NOT from these garbage sources
garbage_sources = [
    'github.com',
    'medium.com',
    'apify.com',
    'docs.recipe-scrapers.com',
    'scrapediary.com',
    'scrapingbee.com',
    'simplescraper.io',
    'spider.cloud',
    'fooddatascrape.com',
    'thunderbit.com',
    'testmuai.com',
    'codesandbox.io',
]

# Also remove by garbage pattern names
garbage_names = [
    'Cooking Troubleshooting Tip',
    'Recipe from Cooking',
    'Ingredient Substitution',
]

cleaned_patterns = []
removed_count = 0

for pattern in patterns:
    source = pattern.get('source', '')
    name = pattern.get('name', '')
    
    # Remove if source is garbage
    if any(garbage in source for garbage in garbage_sources):
        removed_count += 1
        print(f"Removing (garbage source): {name[:50]}")
        continue
    
    # Remove if name is garbage
    if name in garbage_names:
        removed_count += 1
        print(f"Removing (garbage name): {name[:50]}")
        continue
    
    # Keep everything else
    cleaned_patterns.append(pattern)

print(f"\nRemoved {removed_count} garbage patterns")
print(f"Total patterns after cleanup: {len(cleaned_patterns)}")

# Save
with open(patterns_file, 'w') as f:
    json.dump(cleaned_patterns, f, indent=2)

# Show breakdown
surveyor_patterns = [p for p in cleaned_patterns if p.get('origin') == 'surveyor']
print(f"\nSurveyor patterns: {len(surveyor_patterns)}")
