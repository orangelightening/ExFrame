#!/usr/bin/env python3
"""
Related Query Finder - Find queries related to a specific entry

Finds related queries using multiple strategies:
- Temporal proximity (queries nearby in time)
- Shared patterns (queries using same domain patterns)
- Keyword overlap (queries with common terms)

Usage:
    python3 scripts/find_related.py <domain> --entry ID [options]

Examples:
    python3 scripts/find_related.py peter --entry 5
    python3 scripts/find_related.py peter --entry 5 --strategy temporal
    python3 scripts/find_related.py peter --entry 5 --limit 10

Options:
    --entry ID            Entry ID to find related queries for (required)
    --strategy STRATEGY   Strategy: temporal, pattern, keyword, all (default: all)
    --limit N             Max results per strategy (default: 5)
    --time-window MINS    Time window for temporal strategy (default: 60 minutes)
    --min-keywords N      Min shared keywords for keyword strategy (default: 2)
    --json                Output as JSON
"""

import gzip
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from collections import Counter
import re

def load_history(domain_name: str) -> List[Dict[str, Any]]:
    """Load query history for a domain."""
    history_file = Path(f"universes/MINE/domains/{domain_name}/query_history.json.gz")

    if not history_file.exists():
        print(f"❌ No query history found for domain '{domain_name}'")
        sys.exit(1)

    with gzip.open(history_file, 'rt', encoding='utf-8') as f:
        return json.load(f)


def parse_timestamp(iso_timestamp: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(iso_timestamp)


def format_timestamp(dt: datetime) -> str:
    """Format datetime to readable format."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def find_entry_by_id(history: List[Dict], entry_id: int) -> Optional[Dict]:
    """Find entry with given ID."""
    for entry in history:
        if entry.get('id') == entry_id:
            return entry
    return None


def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
    """Extract keywords from text (simple word-based)."""
    # Lowercase and split on non-word characters
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out short words and common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                  'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                  'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                  'what', 'when', 'where', 'who', 'why', 'how', 'which', 'if', 'my',
                  'your', 'his', 'her', 'its', 'our', 'their'}

    keywords = {w for w in words if len(w) >= min_length and w not in stop_words}
    return keywords


def find_temporal_related(
    target: Dict,
    history: List[Dict],
    time_window: int = 60,
    limit: int = 5
) -> List[Dict]:
    """
    Find queries temporally close to target.

    Args:
        target: Target entry
        history: Full history
        time_window: Time window in minutes
        limit: Max results

    Returns:
        List of related entries with similarity scores
    """
    target_time = parse_timestamp(target['timestamp'])
    window_delta = timedelta(minutes=time_window)

    related = []

    for entry in history:
        # Skip the target itself
        if entry.get('id') == target.get('id'):
            continue

        entry_time = parse_timestamp(entry['timestamp'])
        time_diff = abs((entry_time - target_time).total_seconds() / 60)  # minutes

        if time_diff <= time_window:
            # Score: closer = higher score (inverse of time diff)
            score = 1.0 - (time_diff / time_window)
            related.append({
                'entry': entry,
                'score': score,
                'reason': f'Within {time_diff:.1f} minutes',
                'strategy': 'temporal'
            })

    # Sort by score (closest first)
    related.sort(key=lambda x: x['score'], reverse=True)
    return related[:limit]


def find_pattern_related(
    target: Dict,
    history: List[Dict],
    limit: int = 5
) -> List[Dict]:
    """
    Find queries using same patterns.

    Args:
        target: Target entry
        history: Full history
        limit: Max results

    Returns:
        List of related entries with similarity scores
    """
    target_patterns = set(target.get('metadata', {}).get('patterns_used', []))

    if not target_patterns:
        return []

    related = []

    for entry in history:
        # Skip the target itself
        if entry.get('id') == target.get('id'):
            continue

        entry_patterns = set(entry.get('metadata', {}).get('patterns_used', []))

        if not entry_patterns:
            continue

        # Calculate Jaccard similarity
        intersection = target_patterns & entry_patterns
        union = target_patterns | entry_patterns

        if intersection:
            score = len(intersection) / len(union)
            shared = ', '.join(sorted(intersection))
            related.append({
                'entry': entry,
                'score': score,
                'reason': f'Shared patterns: {shared}',
                'strategy': 'pattern'
            })

    # Sort by score (most overlap first)
    related.sort(key=lambda x: x['score'], reverse=True)
    return related[:limit]


def find_keyword_related(
    target: Dict,
    history: List[Dict],
    min_keywords: int = 2,
    limit: int = 5
) -> List[Dict]:
    """
    Find queries with keyword overlap.

    Args:
        target: Target entry
        history: Full history
        min_keywords: Minimum shared keywords
        limit: Max results

    Returns:
        List of related entries with similarity scores
    """
    # Extract keywords from target query and response
    target_text = target['query'] + ' ' + target.get('response', '')
    target_keywords = extract_keywords(target_text)

    if not target_keywords:
        return []

    related = []

    for entry in history:
        # Skip the target itself
        if entry.get('id') == target.get('id'):
            continue

        # Extract keywords from entry
        entry_text = entry['query'] + ' ' + entry.get('response', '')
        entry_keywords = extract_keywords(entry_text)

        if not entry_keywords:
            continue

        # Calculate keyword overlap
        intersection = target_keywords & entry_keywords

        if len(intersection) >= min_keywords:
            # Score: Jaccard similarity
            union = target_keywords | entry_keywords
            score = len(intersection) / len(union)

            # Show top shared keywords
            top_shared = sorted(intersection, key=lambda k: len(k), reverse=True)[:5]
            shared_str = ', '.join(top_shared)

            related.append({
                'entry': entry,
                'score': score,
                'reason': f'{len(intersection)} shared keywords: {shared_str}',
                'strategy': 'keyword'
            })

    # Sort by score (most overlap first)
    related.sort(key=lambda x: x['score'], reverse=True)
    return related[:limit]


def print_related(target: Dict, related_groups: Dict[str, List[Dict]], domain: str):
    """Print related queries in readable format."""
    print(f"\n{'='*70}")
    print(f"Related Queries: {domain}")
    print(f"Target Entry: #{target.get('id')}")
    print(f"{'='*70}")

    # Print target
    print(f"\n{'█'*70}")
    print(f"TARGET QUERY")
    print(f"{'█'*70}")
    query = target.get('query', '')
    response = target.get('response', '')
    if len(response) > 100:
        response = response[:100] + '...'

    print(f"[{target.get('id')}] {format_timestamp(parse_timestamp(target['timestamp']))}")
    print(f"Query:    {query}")
    print(f"Response: {response}")

    # Print related by strategy
    for strategy, related_list in related_groups.items():
        if not related_list:
            continue

        print(f"\n{'─'*70}")
        print(f"RELATED BY {strategy.upper()} ({len(related_list)} results)")
        print(f"{'─'*70}")

        for i, item in enumerate(related_list, 1):
            entry = item['entry']
            score = item['score']
            reason = item['reason']

            query = entry.get('query', '')
            if len(query) > 60:
                query = query[:60] + '...'

            print(f"\n{i}. [{entry.get('id')}] {format_timestamp(parse_timestamp(entry['timestamp']))}")
            print(f"   Score:  {score:.3f}")
            print(f"   Reason: {reason}")
            print(f"   Query:  {query}")

    # Summary
    print(f"\n{'='*70}")
    total = sum(len(related_list) for related_list in related_groups.values())
    print(f"Total related queries found: {total}")
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    # Parse arguments
    if len(args) < 1:
        print("Error: domain name required")
        print(__doc__)
        sys.exit(1)

    domain_name = args[0]
    entry_id = None
    strategy = "all"
    limit = 5
    time_window = 60
    min_keywords = 2
    json_output = False

    i = 1
    while i < len(args):
        if args[i] == "--entry" and i + 1 < len(args):
            entry_id = int(args[i + 1])
            i += 2
        elif args[i] == "--strategy" and i + 1 < len(args):
            strategy = args[i + 1]
            i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "--time-window" and i + 1 < len(args):
            time_window = int(args[i + 1])
            i += 2
        elif args[i] == "--min-keywords" and i + 1 < len(args):
            min_keywords = int(args[i + 1])
            i += 2
        elif args[i] == "--json":
            json_output = True
            i += 1
        else:
            i += 1

    if entry_id is None:
        print("Error: --entry ID is required")
        print(__doc__)
        sys.exit(1)

    # Validate strategy
    valid_strategies = {"temporal", "pattern", "keyword", "all"}
    if strategy not in valid_strategies:
        print(f"Error: Invalid strategy '{strategy}'. Must be one of: {', '.join(valid_strategies)}")
        sys.exit(1)

    # Load history
    history = load_history(domain_name)

    if not history:
        print(f"No history entries found for {domain_name}")
        sys.exit(0)

    # Find target entry
    target_entry = find_entry_by_id(history, entry_id)
    if target_entry is None:
        print(f"❌ Entry #{entry_id} not found in {domain_name} history")
        sys.exit(1)

    # Find related queries by strategy
    related_groups = {}

    if strategy in ("temporal", "all"):
        related_groups["temporal"] = find_temporal_related(
            target_entry, history, time_window, limit
        )

    if strategy in ("pattern", "all"):
        related_groups["pattern"] = find_pattern_related(
            target_entry, history, limit
        )

    if strategy in ("keyword", "all"):
        related_groups["keyword"] = find_keyword_related(
            target_entry, history, min_keywords, limit
        )

    # JSON output
    if json_output:
        output = {
            'target': target_entry,
            'related': {
                strategy: [
                    {
                        'entry': item['entry'],
                        'score': item['score'],
                        'reason': item['reason']
                    }
                    for item in related_list
                ]
                for strategy, related_list in related_groups.items()
            }
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Print results
    print_related(target_entry, related_groups, domain_name)


if __name__ == "__main__":
    main()
