#!/usr/bin/env python3
"""
Pattern Analytics Tool

Analyzes patterns across all domains to provide insights:
- Pattern counts and distribution
- Usage statistics
- Quality indicators
- Duplicate detection
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

def load_domain_patterns(domain_path):
    """Load patterns from a domain directory."""
    patterns_file = domain_path / "patterns.json"
    if not patterns_file.exists():
        return []

    try:
        with open(patterns_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'patterns' in data:
                return data['patterns']
            elif isinstance(data, list):
                return data
            return []
    except Exception as e:
        print(f"  ⚠️  Error loading {patterns_file}: {e}", file=sys.stderr)
        return []


def analyze_pattern_quality(pattern):
    """Analyze pattern quality indicators."""
    quality_score = 0
    issues = []

    # Has description (optional but good)
    if pattern.get('description'):
        quality_score += 1
    else:
        issues.append("No description")

    # Has meaningful solution
    solution = pattern.get('solution', '')
    if len(solution) > 20:
        quality_score += 1
    else:
        issues.append("Short solution")

    # Has tags
    if pattern.get('tags') and len(pattern.get('tags', [])) > 0:
        quality_score += 1
    else:
        issues.append("No tags")

    # Has confidence score
    if pattern.get('confidence'):
        quality_score += 1

    # Has examples
    if pattern.get('examples'):
        quality_score += 1

    return quality_score, issues


def find_similar_patterns(patterns, similarity_threshold=0.8):
    """Find potentially duplicate patterns using simple text similarity.

    Returns both duplicate pairs and affected pattern IDs.
    """
    from difflib import SequenceMatcher

    duplicate_pairs = []
    affected_patterns = set()
    checked = set()

    for i, p1 in enumerate(patterns):
        for j, p2 in enumerate(patterns[i+1:], i+1):
            if (i, j) in checked:
                continue

            # Compare names and problems
            name_sim = SequenceMatcher(None,
                p1.get('name', '').lower(),
                p2.get('name', '').lower()
            ).ratio()

            problem_sim = SequenceMatcher(None,
                p1.get('problem', '').lower(),
                p2.get('problem', '').lower()
            ).ratio()

            # If either is very similar, flag as potential duplicate
            if name_sim > similarity_threshold or problem_sim > similarity_threshold:
                duplicate_pairs.append({
                    'pattern1': {'id': p1.get('id'), 'name': p1.get('name'), 'index': i},
                    'pattern2': {'id': p2.get('id'), 'name': p2.get('name'), 'index': j},
                    'name_similarity': name_sim,
                    'problem_similarity': problem_sim
                })
                affected_patterns.add(i)
                affected_patterns.add(j)
                checked.add((i, j))

    return duplicate_pairs, affected_patterns


def analyze_domains(universes_path):
    """Analyze all domains in the universes directory."""
    universes_path = Path(universes_path)

    print("=" * 70)
    print("ExFrame Pattern Analytics")
    print("=" * 70)
    print()

    all_patterns = []
    domain_stats = {}

    # Find all domains
    for universe_dir in universes_path.iterdir():
        if not universe_dir.is_dir():
            continue

        domains_dir = universe_dir / "domains"
        if not domains_dir.exists():
            continue

        print(f"📁 Universe: {universe_dir.name}")
        print()

        for domain_dir in domains_dir.iterdir():
            if not domain_dir.is_dir():
                continue

            domain_name = domain_dir.name
            patterns = load_domain_patterns(domain_dir)

            if not patterns:
                continue

            # Analyze domain
            pattern_types = Counter(p.get('pattern_type', 'unknown') for p in patterns)
            avg_quality, quality_dist = 0, defaultdict(int)

            for pattern in patterns:
                quality, _ = analyze_pattern_quality(pattern)
                quality_dist[quality] += 1
                avg_quality += quality

            avg_quality = avg_quality / len(patterns) if patterns else 0

            domain_stats[domain_name] = {
                'count': len(patterns),
                'pattern_types': dict(pattern_types),
                'avg_quality': avg_quality,
                'quality_distribution': dict(quality_dist),
                'patterns': patterns
            }

            all_patterns.extend([(domain_name, p) for p in patterns])

            # Print domain summary
            print(f"  📊 {domain_name}:")
            print(f"     Patterns: {len(patterns)}")
            print(f"     Types: {', '.join(f'{k}({v})' for k, v in pattern_types.most_common(3))}")
            print(f"     Avg Quality: {avg_quality:.1f}/5.0")
            print()

    print("=" * 70)
    print("Overall Statistics")
    print("=" * 70)
    print()
    print(f"Total patterns: {len(all_patterns)}")
    print(f"Total domains: {len(domain_stats)}")
    print()

    # Pattern type distribution
    all_types = Counter(p[1].get('pattern_type', 'unknown') for p in all_patterns)
    print("Pattern Types:")
    for ptype, count in all_types.most_common():
        print(f"  {ptype}: {count}")
    print()

    # Quality distribution
    print("Quality Distribution:")
    all_quality = defaultdict(int)
    for stats in domain_stats.values():
        for quality, count in stats['quality_distribution'].items():
            all_quality[quality] += count

    for quality in sorted(all_quality.keys(), reverse=True):
        count = all_quality[quality]
        bar = "█" * (count // 2) if count > 0 else ""
        print(f"  {quality}/5: {count:3d} {bar}")
    print()

    # Find duplicates
    print("=" * 70)
    print("Duplicate Detection")
    print("=" * 70)
    print()

    # Group by domain and check within domains
    total_affected = 0
    total_pairs = 0

    for domain_name, stats in domain_stats.items():
        duplicate_pairs, affected_patterns = find_similar_patterns(stats['patterns'], similarity_threshold=0.75)

        if duplicate_pairs:
            pattern_count = len(stats['patterns'])
            affected_count = len(affected_patterns)
            pair_count = len(duplicate_pairs)

            total_affected += affected_count
            total_pairs += pair_count

            print(f"⚠️  {domain_name}:")
            print(f"     Total patterns: {pattern_count}")
            print(f"     Patterns involved in duplicates: {affected_count} ({affected_count/pattern_count*100:.1f}%)")
            print(f"     Duplicate pairs found: {pair_count}")
            print()
            print(f"     Top duplicate pairs:")
            for dup in duplicate_pairs[:5]:  # Show top 5
                print(f"       • '{dup['pattern1']['name'][:50]}...' ≈ '{dup['pattern2']['name'][:50]}...'")
                print(f"         Similarity: name={dup['name_similarity']:.2f}, problem={dup['problem_similarity']:.2f}")
            if len(duplicate_pairs) > 5:
                print(f"       ... and {len(duplicate_pairs) - 5} more pairs")
            print()

    if total_pairs > 0:
        print(f"📊 Summary: {total_affected} patterns involved in {total_pairs} duplicate pairs")
        print()

    # Low quality patterns
    print("=" * 70)
    print("Low Quality Patterns (Quality < 2/5)")
    print("=" * 70)
    print()

    for domain_name, stats in domain_stats.items():
        low_quality = []
        for pattern in stats['patterns']:
            quality, issues = analyze_pattern_quality(pattern)
            if quality < 2:
                low_quality.append((pattern, quality, issues))

        if low_quality:
            print(f"⚠️  {domain_name} - {len(low_quality)} low quality patterns:")
            for pattern, quality, issues in low_quality[:3]:
                print(f"  • {pattern.get('name', 'Unnamed')} ({quality}/5)")
                print(f"    Issues: {', '.join(issues)}")
            if len(low_quality) > 3:
                print(f"  ... and {len(low_quality) - 3} more")
            print()

    print("=" * 70)
    print("✅ Analysis Complete")
    print("=" * 70)


if __name__ == "__main__":
    universes_path = Path("/app/universes") if Path("/app/universes").exists() else Path("./universes")

    if not universes_path.exists():
        print(f"❌ Error: {universes_path} not found", file=sys.stderr)
        sys.exit(1)

    analyze_domains(universes_path)
