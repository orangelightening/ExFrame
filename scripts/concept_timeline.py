#!/usr/bin/env python3
"""
Concept Timeline - Track concepts across query history

Extracts keywords from queries/responses and shows when concepts appeared,
how often they were explored, and which concepts co-occur.

Usage:
    python3 scripts/concept_timeline.py <domain> [options]

Examples:
    python3 scripts/concept_timeline.py peter
    python3 scripts/concept_timeline.py peter --concept "patterns"
    python3 scripts/concept_timeline.py peter --top 20
    python3 scripts/concept_timeline.py peter --cooccurrence --concept "embedding"

Options:
    --concept TERM        Show timeline for specific concept
    --top N               Show top N most frequent concepts (default: 10)
    --min-freq N          Only show concepts appearing N+ times (default: 2)
    --cooccurrence        Show co-occurring concepts
    --date-from DATE      Filter from date (YYYY-MM-DD)
    --date-to DATE        Filter to date (YYYY-MM-DD)
    --json                Output as JSON
"""

import gzip
import json
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from collections import Counter, defaultdict
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


def format_date(dt: datetime) -> str:
    """Format datetime to date only."""
    return dt.strftime("%Y-%m-%d")


def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
    """Extract keywords from text."""
    # Lowercase and split on non-word characters
    words = re.findall(r'\b\w+\b', text.lower())

    # Stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'when', 'where', 'who', 'why', 'how', 'which', 'if', 'my',
        'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us',
        'about', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'all', 'both', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
    }

    keywords = {w for w in words if len(w) >= min_length and w not in stop_words}
    return keywords


def build_concept_index(history: List[Dict]) -> Dict[str, List[Tuple[int, datetime]]]:
    """
    Build index of concepts to entries.

    Returns:
        Dict mapping concept -> [(entry_id, timestamp), ...]
    """
    concept_index = defaultdict(list)

    for entry in history:
        entry_id = entry.get('id')
        timestamp = parse_timestamp(entry['timestamp'])

        # Extract keywords from query and response
        text = entry['query'] + ' ' + entry.get('response', '')
        keywords = extract_keywords(text)

        for keyword in keywords:
            concept_index[keyword].append((entry_id, timestamp))

    return dict(concept_index)


def build_cooccurrence(history: List[Dict]) -> Dict[str, Counter]:
    """
    Build co-occurrence matrix for concepts.

    Returns:
        Dict mapping concept -> Counter of co-occurring concepts
    """
    cooccurrence = defaultdict(Counter)

    for entry in history:
        text = entry['query'] + ' ' + entry.get('response', '')
        keywords = extract_keywords(text)

        # For each pair of keywords in the same entry, count co-occurrence
        keyword_list = list(keywords)
        for i, k1 in enumerate(keyword_list):
            for k2 in keyword_list[i+1:]:
                cooccurrence[k1][k2] += 1
                cooccurrence[k2][k1] += 1

    return dict(cooccurrence)


def filter_by_date(
    history: List[Dict],
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[Dict]:
    """Filter history by date range."""
    if not date_from and not date_to:
        return history

    filtered = []

    for entry in history:
        entry_date = parse_timestamp(entry['timestamp']).date()

        if date_from:
            from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            if entry_date < from_date:
                continue

        if date_to:
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            if entry_date > to_date:
                continue

        filtered.append(entry)

    return filtered


def print_top_concepts(
    concept_index: Dict[str, List[Tuple[int, datetime]]],
    top_n: int,
    min_freq: int,
    domain: str
):
    """Print top N most frequent concepts."""
    # Filter by minimum frequency
    concepts = {
        concept: occurrences
        for concept, occurrences in concept_index.items()
        if len(occurrences) >= min_freq
    }

    if not concepts:
        print(f"No concepts found with min frequency {min_freq}")
        return

    # Sort by frequency
    sorted_concepts = sorted(concepts.items(), key=lambda x: len(x[1]), reverse=True)
    top_concepts = sorted_concepts[:top_n]

    print(f"\n{'='*70}")
    print(f"Top Concepts: {domain}")
    print(f"Showing top {len(top_concepts)} concepts (min frequency: {min_freq})")
    print(f"{'='*70}")

    for i, (concept, occurrences) in enumerate(top_concepts, 1):
        first_seen = min(occurrences, key=lambda x: x[1])[1]
        last_seen = max(occurrences, key=lambda x: x[1])[1]

        print(f"\n{i}. {concept.upper()}")
        print(f"   Frequency:  {len(occurrences)} times")
        print(f"   First seen: {format_timestamp(first_seen)}")
        print(f"   Last seen:  {format_timestamp(last_seen)}")

        # Show entry IDs
        entry_ids = [entry_id for entry_id, _ in occurrences]
        if len(entry_ids) <= 10:
            print(f"   Entries:    {', '.join(f'#{id}' for id in entry_ids)}")
        else:
            print(f"   Entries:    {', '.join(f'#{id}' for id in entry_ids[:10])}... (+{len(entry_ids)-10} more)")

    print(f"\n{'='*70}\n")


def print_concept_timeline(
    concept: str,
    concept_index: Dict[str, List[Tuple[int, datetime]]],
    history: List[Dict],
    domain: str
):
    """Print timeline for specific concept."""
    if concept not in concept_index:
        print(f"❌ Concept '{concept}' not found in {domain} history")
        return

    occurrences = concept_index[concept]

    print(f"\n{'='*70}")
    print(f"Concept Timeline: {domain}")
    print(f"Concept: {concept.upper()}")
    print(f"{'='*70}")
    print(f"Total occurrences: {len(occurrences)}")

    # Sort by timestamp
    occurrences_sorted = sorted(occurrences, key=lambda x: x[1])

    first_seen = occurrences_sorted[0][1]
    last_seen = occurrences_sorted[-1][1]
    span_days = (last_seen - first_seen).days

    print(f"First seen: {format_timestamp(first_seen)}")
    print(f"Last seen:  {format_timestamp(last_seen)}")
    print(f"Time span:  {span_days} days")
    print(f"{'='*70}\n")

    # Show each occurrence
    for entry_id, timestamp in occurrences_sorted:
        # Find the entry
        entry = next((e for e in history if e.get('id') == entry_id), None)
        if not entry:
            continue

        query = entry.get('query', '')
        if len(query) > 60:
            query = query[:60] + '...'

        print(f"[{entry_id}] {format_timestamp(timestamp)}")
        print(f"    {query}")
        print()

    print(f"{'='*70}\n")


def print_cooccurrence(
    concept: str,
    cooccurrence: Dict[str, Counter],
    top_n: int,
    domain: str
):
    """Print concepts that co-occur with given concept."""
    if concept not in cooccurrence:
        print(f"❌ Concept '{concept}' not found in {domain} history")
        return

    related = cooccurrence[concept]

    if not related:
        print(f"No co-occurring concepts found for '{concept}'")
        return

    # Sort by frequency
    top_related = related.most_common(top_n)

    print(f"\n{'='*70}")
    print(f"Co-occurring Concepts: {domain}")
    print(f"Base concept: {concept.upper()}")
    print(f"{'='*70}")
    print(f"Showing top {len(top_related)} co-occurring concepts")
    print(f"{'='*70}\n")

    for i, (related_concept, count) in enumerate(top_related, 1):
        print(f"{i}. {related_concept:20s} {count:3d} co-occurrences")

    print(f"\n{'='*70}\n")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    # Parse arguments
    domain_name = args[0]
    concept = None
    top_n = 10
    min_freq = 2
    show_cooccurrence = False
    date_from = None
    date_to = None
    json_output = False

    i = 1
    while i < len(args):
        if args[i] == "--concept" and i + 1 < len(args):
            concept = args[i + 1].lower()
            i += 2
        elif args[i] == "--top" and i + 1 < len(args):
            top_n = int(args[i + 1])
            i += 2
        elif args[i] == "--min-freq" and i + 1 < len(args):
            min_freq = int(args[i + 1])
            i += 2
        elif args[i] == "--cooccurrence":
            show_cooccurrence = True
            i += 1
        elif args[i] == "--date-from" and i + 1 < len(args):
            date_from = args[i + 1]
            i += 2
        elif args[i] == "--date-to" and i + 1 < len(args):
            date_to = args[i + 1]
            i += 2
        elif args[i] == "--json":
            json_output = True
            i += 1
        else:
            i += 1

    # Load history
    history = load_history(domain_name)

    if not history:
        print(f"No history entries found for {domain_name}")
        sys.exit(0)

    # Filter by date if specified
    history = filter_by_date(history, date_from, date_to)

    if not history:
        print(f"No history entries in specified date range")
        sys.exit(0)

    # Build indexes
    concept_index = build_concept_index(history)

    # JSON output
    if json_output:
        output = {
            'total_concepts': len(concept_index),
            'concepts': {
                concept: {
                    'frequency': len(occurrences),
                    'entries': [entry_id for entry_id, _ in occurrences]
                }
                for concept, occurrences in concept_index.items()
            }
        }
        if concept:
            output['selected_concept'] = concept
            if concept in concept_index:
                output['selected_concept_data'] = {
                    'frequency': len(concept_index[concept]),
                    'entries': [entry_id for entry_id, _ in concept_index[concept]]
                }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Show specific concept timeline
    if concept:
        print_concept_timeline(concept, concept_index, history, domain_name)

        if show_cooccurrence:
            cooccurrence = build_cooccurrence(history)
            print_cooccurrence(concept, cooccurrence, top_n, domain_name)
    else:
        # Show top concepts
        print_top_concepts(concept_index, top_n, min_freq, domain_name)


if __name__ == "__main__":
    main()
