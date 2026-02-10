#!/usr/bin/env python3
"""Dump AllRecipes survey results to readable markdown"""
import json
from pathlib import Path
from datetime import datetime

with open('universes/MINE/domains/cooking/patterns.json', 'r') as f:
    patterns = json.load(f)

# Get recent surveyor recipes (last 50)
surveyor_patterns = [p for p in patterns if p.get('origin') == 'surveyor']
recent_recipes = sorted(surveyor_patterns, key=lambda p: p.get('created_at', ''))[-50:]

# Create markdown
md = []
md.append("# AllRecipes - Survey Results\n")
md.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
md.append(f"Total Recipes: {len(recent_recipes)}\n\n")
md.append("---\n\n")

for i, recipe in enumerate(recent_recipes, 1):
    md.append(f"## {i}. {recipe['name']}\n\n")
    md.append(f"**Source**: [View on AllRecipes]({recipe['source']})\n\n")
    
    if recipe.get('description'):
        # Ingredients are in description
        desc = recipe['description']
        if 'Ingredients' in desc:
            md.append(f"{desc}\n\n")
        else:
            md.append(f"{desc}\n\n")
    
    if recipe.get('steps'):
        md.append(f"**Steps**:\n\n")
        for step in recipe['steps']:
            md.append(f"{step}\n")
        md.append("\n")
    
    md.append("---\n\n")

# Write to file
output_file = Path('/tmp/allrecipes_survey_results.md')
output_file.write_text(''.join(md))

print(f"✓ Dumped {len(recent_recipes)} recipes to {output_file}")
print(f"\nTo view: cat {output_file}")
