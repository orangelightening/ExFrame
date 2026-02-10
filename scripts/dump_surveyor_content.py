#!/usr/bin/env python3
"""
Dump surveyor scraped content to readable markdown files.
This bypasses the PatternExtractor and shows what was actually scraped.
"""
import json
from pathlib import Path
from datetime import datetime

def extract_domain(url):
    """Extract domain from URL"""
    from urllib.parse import urlparse
    return urlparse(url).netloc.replace('www.', '')

# Load patterns
patterns_file = Path('universes/MINE/domains/cooking/patterns.json')
with open(patterns_file, 'r') as f:
    patterns = json.load(f)

# Get surveyor patterns
surveyor_patterns = [p for p in patterns if p.get('origin') == 'surveyor']

# Group by source URL
by_source = {}
for p in surveyor_patterns:
    url = p.get('source', 'unknown')
    if url not in by_source:
        by_source[url] = {
            'name': p.get('name', 'Unnamed'),
            'domain': extract_domain(url),
            'patterns': []
        }
    by_source[url]['patterns'].append(p)

# Create output directory
output_dir = Path('/tmp/cooking_surveyor_dump')
output_dir.mkdir(exist_ok=True)

# Create index
index_md = []
index_md.append("# Cooking Surveyor - Scraped Content\n")
index_md.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
index_md.append(f"Total Sources: {len(by_source)}\n")
index_md.append(f"Total Patterns: {len(surveyor_patterns)}\n\n")
index_md.append("## Scraped Sources\n\n")

# Create per-source markdown files
for url, info in sorted(by_source.items()):
    domain = info['domain']
    safe_name = f"{domain}_{url.split('/')[-1][:30]}".replace('/', '_').replace('.', '_')
    safe_name = ''.join(c if c.isalnum() or c in '_-' else '_' for c in safe_name)
    
    # Create source file
    source_md = []
    source_md.append(f"# {info['name']}\n\n")
    source_md.append(f"**Source**: {url}\n\n")
    source_md.append(f"**Patterns Extracted**: {len(info['patterns'])}\n\n")
    source_md.append("---\n\n")
    
    for i, p in enumerate(info['patterns'], 1):
        source_md.append(f"## Pattern {i}\n\n")
        source_md.append(f"**Name**: {p.get('name', 'Unnamed')}\n\n")
        source_md.append(f"**Type**: {p.get('pattern_type', 'unknown')}\n\n")
        source_md.append(f"**Confidence**: {p.get('confidence', 0)}\n\n")
        
        if p.get('description'):
            source_md.append(f"**Description**:\n\n{p['description']}\n\n")
        
        if p.get('solution'):
            source_md.append(f"**Solution**:\n\n{p['solution']}\n\n")
        
        if p.get('steps'):
            source_md.append(f"**Steps**:\n\n")
            for step in p['steps']:
                source_md.append(f"- {step}\n")
            source_md.append("\n")
        
        if p.get('tags'):
            source_md.append(f"**Tags**: {', '.join(p['tags'])}\n\n")
        
        source_md.append("---\n\n")
    
    # Write source file
    source_file = output_dir / f"{safe_name}.md"
    with open(source_file, 'w') as f:
        f.write(''.join(source_md))
    
    # Add to index
    index_md.append(f"### {domain}\n\n")
    index_md.append(f"- [{info['name']}]({safe_name}.md) - {len(info['patterns'])} patterns\n")
    index_md.append(f"  - Source: {url}\n\n")

# Write index
with open(output_dir / 'index.md', 'w') as f:
    f.write(''.join(index_md))

print(f"✓ Dumped {len(by_source)} sources to {output_dir}/")
print(f"  - Total patterns: {len(surveyor_patterns)}")
print(f"  - Index: {output_dir}/index.md")
print(f"\nTo view:")
print(f"  cat {output_dir}/index.md")
