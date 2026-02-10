#!/usr/bin/env python3
"""
Remove low-quality patterns from the DuckDuckGo + PatternExtractor survey.
Keep only high-quality AllRecipes surveyor patterns.
"""
import json
from pathlib import Path
from datetime import datetime

# Load patterns
patterns_file = Path('universes/MINE/domains/cooking/patterns.json')
with open(patterns_file, 'r') as f:
    patterns = json.load(f)

print(f"Total patterns before cleanup: {len(patterns)}")

# Keep patterns that are:
# 1. Not from surveyor (manual/original patterns)
# 2. From surveyor BUT have structured ingredient lists (good quality)
cleaned_patterns = []
removed_count = 0

for pattern in patterns:
    # Keep non-surveyor patterns
    if pattern.get('origin') != 'surveyor':
        cleaned_patterns.append(pattern)
        continue
    
    # For surveyor patterns, check quality
    # Good patterns have detailed descriptions with ingredients
    description = pattern.get('description', '')
    
    # Bad pattern indicators from old DuckDuckGo survey:
    bad_indicators = [
        'Cooking instructions extracted from recipe',  # Generic fallback
        'A step-by-step',  # Generic prefix
        len(description) < 50,  # Too short
        pattern.get('name', '') in ['Cooking Troubleshooting Tip', 'Recipe from Cooking']
    ]
    
    # Good pattern indicators from AllRecipes:
    good_indicators = [
        '**Ingredients**' in description,  # Has structured ingredients
        'allrecipes.com/recipe/' in pattern.get('source', ''),  # From AllRecipes
        len(pattern.get('steps', [])) > 0,  # Has steps
    ]
    
    # Remove bad patterns
    if any(bad_indicators):
        removed_count += 1
        print(f"Removing: {pattern.get('name', 'Unknown')[:50]}")
        continue
    
    # Keep good patterns
    if any(good_indicators):
        cleaned_patterns.append(pattern)
    else:
        # Borderline case - check if it has actual content
        if len(description) > 100:
            cleaned_patterns.append(pattern)
        else:
            removed_count += 1
            print(f"Removing (low quality): {pattern.get('name', 'Unknown')[:50]}")

print(f"\nRemoved {removed_count} low-quality patterns")
print(f"Total patterns after cleanup: {len(cleaned_patterns)}")

# Backup original file
backup_file = patterns_file.with_suffix('.json.backup')
with open(backup_file, 'w') as f:
    json.dump(patterns, f, indent=2)
print(f"\n✓ Backed up original to: {backup_file}")

# Save cleaned patterns
with open(patterns_file, 'w') as f:
    json.dump(cleaned_patterns, f, indent=2)

print(f"✓ Saved cleaned patterns to: {patterns_file}")

# Show breakdown
surveyor_patterns = [p for p in cleaned_patterns if p.get('origin') == 'surveyor']
manual_patterns = [p for p in cleaned_patterns if p.get('origin') != 'surveyor']

print(f"\nFinal breakdown:")
print(f"  Surveyor patterns: {len(surveyor_patterns)}")
print(f"  Manual patterns: {len(manual_patterns)}")
