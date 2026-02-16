#!/usr/bin/env python3
"""
Exploration Depth Analyzer - Measure how deeply topics were explored

Analyzes query patterns to identify deep explorations vs shallow touches.
A deep exploration is a sequence of related queries within a short time window.

Usage:
    python3 scripts/analyze_depth.py <domain> [options]

Examples:
    python3 scripts/analyze_depth.py peter
    python3 scripts/analyze_depth.py peter --concept "embedding"
    python3 scripts/analyze_depth.py peter --min-depth 3
    python3 scripts/analyze_depth.py peter --time-gap 15

Options:
    --concept TERM        Analyze depth for specific concept
    --min-depth N         Only show explorations with N+ queries (default: 2)
    --time-gap MINS       Max gap between queries in exploration (default: 10)
    --show-shallow        Also show shallow (single query) topics
    --json                Output as JSON
"""

import gzip
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Set
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


def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
    """Extract keywords from text."""
    words = re.findall(r'\b\w+\b', text.lower())

    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'when', 'where', 'who', 'why', 'how', 'which', 'if', 'my',
        'your', 'his', 'her', 'its', 'our', 'their'
    }

    keywords = {w for w in words if len(w) >= min_length and w not in stop_words}
    return keywords


def find_exploration_chains(history: List[Dict], time_gap_minutes: int = 10) -> List[List[Dict]]:
    """
    Find chains of queries that form explorations.

    An exploration is a sequence of queries close together in time.
    """
    if not history:
        return []

    chains = []
    current_chain = [history[0]]

    for i in range(1, len(history)):
        prev_time = parse_timestamp(history[i-1]['timestamp'])
        curr_time = parse_timestamp(history[i]['timestamp'])

        gap = (curr_time - prev_time).total_seconds() / 60  # minutes

        if gap <= time_gap_minutes:
            current_chain.append(history[i])
        else:
            chains.append(current_chain)
            current_chain = [history[i]]

    chains.append(current_chain)
    return chains


def analyze_chain_topics(chain: List[Dict]) -> Dict[str, int]:
    """
    Analyze topics (keywords) in a chain.

    Returns:
        Dict mapping keyword -> frequency in chain
    """
    topic_counts = {}

    for entry in chain:
        text = entry['query'] + ' ' + entry.get('response', '')
        keywords = extract_keywords(text)

        for keyword in keywords:
            topic_counts[keyword] = topic_counts.get(keyword, 0) + 1

    return topic_counts


def identify_deep_explorations(
    chains: List[List[Dict]],
    min_depth: int = 2
) -> List[Dict[str, Any]]:
    """
    Identify deep explorations (chains with depth >= min_depth).

    Returns:
        List of exploration dicts with metadata
    """
    explorations = []

    for chain in chains:
        if len(chain) < min_depth:
            continue

        # Analyze topics in chain
        topics = analyze_chain_topics(chain)

        # Find dominant topic (most frequent keyword)
        if not topics:
            dominant_topic = "unknown"
        else:
            dominant_topic = max(topics.items(), key=lambda x: x[1])[0]

        start_time = parse_timestamp(chain[0]['timestamp'])
        end_time = parse_timestamp(chain[-1]['timestamp'])
        duration = (end_time - start_time).total_seconds() / 60

        explorations.append({
            'chain': chain,
            'depth': len(chain),
            'dominant_topic': dominant_topic,
            'topics': topics,
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': round(duration, 1)
        })

    # Sort by depth (deepest first)
    explorations.sort(key=lambda x: x['depth'], reverse=True)
    return explorations


def filter_by_concept(
    explorations: List[Dict[str, Any]],
    concept: str
) -> List[Dict[str, Any]]:
    """Filter explorations by concept."""
    filtered = []

    for exploration in explorations:
        if concept in exploration['topics']:
            filtered.append(exploration)

    return filtered


def print_explorations(explorations: List[Dict[str, Any]], domain: str, min_depth: int):
    """Print exploration analysis."""
    print(f"\n{'='*70}")
    print(f"Exploration Depth Analysis: {domain}")
    print(f"Minimum depth: {min_depth} queries")
    print(f"{'='*70}")

    if not explorations:
        print("\nNo deep explorations found.")
        print(f"Try lowering --min-depth or increasing --time-gap")
        print(f"{'='*70}\n")
        return

    print(f"\nFound {len(explorations)} deep explorations")
    print(f"{'='*70}\n")

    for i, exploration in enumerate(explorations, 1):
        chain = exploration['chain']
        depth = exploration['depth']
        dominant_topic = exploration['dominant_topic']
        topics = exploration['topics']
        start_time = exploration['start_time']
        end_time = exploration['end_time']
        duration = exploration['duration_minutes']

        print(f"{'─'*70}")
        print(f"Exploration {i}: {dominant_topic.upper()}")
        print(f"{'─'*70}")
        print(f"Depth:     {depth} queries")
        print(f"Duration:  {duration} minutes")
        print(f"Started:   {format_timestamp(start_time)}")
        print(f"Ended:     {format_timestamp(end_time)}")

        # Show top topics
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"\nTop topics:")
        for topic, count in top_topics:
            print(f"  {topic:20s} {count} times")

        # Show queries
        print(f"\nQueries in exploration:")
        for j, entry in enumerate(chain, 1):
            query = entry.get('query', '')
            if len(query) > 55:
                query = query[:55] + '...'

            print(f"  {j}. [{entry.get('id')}] {query}")

        print()

    # Summary statistics
    print(f"{'='*70}")
    print(f"Summary:")
    total_depth = sum(e['depth'] for e in explorations)
    avg_depth = total_depth / len(explorations)
    max_depth = max(e['depth'] for e in explorations)
    avg_duration = sum(e['duration_minutes'] for e in explorations) / len(explorations)

    print(f"  Total explorations:  {len(explorations)}")
    print(f"  Average depth:       {avg_depth:.1f} queries")
    print(f"  Maximum depth:       {max_depth} queries")
    print(f"  Average duration:    {avg_duration:.1f} minutes")
    print(f"{'='*70}\n")


def print_concept_depth(
    explorations: List[Dict[str, Any]],
    concept: str,
    domain: str
):
    """Print depth analysis for specific concept."""
    if not explorations:
        print(f"\n❌ No explorations found for concept '{concept}'")
        return

    print(f"\n{'='*70}")
    print(f"Concept Depth Analysis: {domain}")
    print(f"Concept: {concept.upper()}")
    print(f"{'='*70}")

    total_occurrences = sum(e['topics'][concept] for e in explorations)
    total_depth = sum(e['depth'] for e in explorations)

    print(f"\nExplorations mentioning '{concept}': {len(explorations)}")
    print(f"Total occurrences: {total_occurrences}")
    print(f"Total queries in these explorations: {total_depth}")
    print(f"{'='*70}\n")

    for i, exploration in enumerate(explorations, 1):
        chain = exploration['chain']
        depth = exploration['depth']
        concept_count = exploration['topics'][concept]
        start_time = exploration['start_time']
        duration = exploration['duration_minutes']

        print(f"{'─'*70}")
        print(f"Exploration {i}")
        print(f"{'─'*70}")
        print(f"Depth:           {depth} queries")
        print(f"'{concept}' appears:  {concept_count} times")
        print(f"Duration:        {duration} minutes")
        print(f"Started:         {format_timestamp(start_time)}")

        print(f"\nQueries:")
        for j, entry in enumerate(chain, 1):
            query = entry.get('query', '')
            if len(query) > 55:
                query = query[:55] + '...'

            # Mark if this query contains the concept
            text = entry['query'] + ' ' + entry.get('response', '')
            has_concept = concept in extract_keywords(text)
            marker = "◆" if has_concept else " "

            print(f"  {marker} {j}. [{entry.get('id')}] {query}")

        print()

    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    # Parse arguments
    domain_name = args[0]
    concept = None
    min_depth = 2
    time_gap = 10
    show_shallow = False
    json_output = False

    i = 1
    while i < len(args):
        if args[i] == "--concept" and i + 1 < len(args):
            concept = args[i + 1].lower()
            i += 2
        elif args[i] == "--min-depth" and i + 1 < len(args):
            min_depth = int(args[i + 1])
            i += 2
        elif args[i] == "--time-gap" and i + 1 < len(args):
            time_gap = int(args[i + 1])
            i += 2
        elif args[i] == "--show-shallow":
            show_shallow = True
            min_depth = 1
            i += 1
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

    # Find exploration chains
    chains = find_exploration_chains(history, time_gap)

    # Identify deep explorations
    explorations = identify_deep_explorations(chains, min_depth)

    # Filter by concept if specified
    if concept:
        explorations = filter_by_concept(explorations, concept)

    # JSON output
    if json_output:
        output = {
            'total_explorations': len(explorations),
            'explorations': [
                {
                    'depth': e['depth'],
                    'dominant_topic': e['dominant_topic'],
                    'topics': e['topics'],
                    'start_time': e['start_time'].isoformat(),
                    'end_time': e['end_time'].isoformat(),
                    'duration_minutes': e['duration_minutes'],
                    'entry_ids': [entry.get('id') for entry in e['chain']]
                }
                for e in explorations
            ]
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Print results
    if concept:
        print_concept_depth(explorations, concept, domain_name)
    else:
        print_explorations(explorations, domain, min_depth)


if __name__ == "__main__":
    main()
