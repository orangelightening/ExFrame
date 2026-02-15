#!/usr/bin/env python3
"""
Query History Viewer - CLI tool to view compressed query/response history

Usage:
    python3 scripts/view_history.py <domain_name> [options]

Examples:
    python3 scripts/view_history.py peter
    python3 scripts/view_history.py peter --limit 10
    python3 scripts/view_history.py peter --min-confidence 0.5
    python3 scripts/view_history.py psycho --source brave-search

Options:
    --limit N             Show only last N entries
    --min-confidence X    Filter entries with confidence >= X
    --source SOURCE       Filter by source (simple_echo, pattern_match, brave-search, etc.)
    --stats-only          Show only summary statistics
    --json                Output as JSON instead of formatted text
"""

import gzip
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_history(domain_name: str) -> List[Dict[str, Any]]:
    """Load query history for a domain."""
    history_file = Path(f"universes/MINE/domains/{domain_name}/query_history.json.gz")

    if not history_file.exists():
        print(f"❌ No query history found for domain '{domain_name}'")
        print(f"   Expected: {history_file}")
        sys.exit(1)

    try:
        with gzip.open(history_file, 'rt', encoding='utf-8') as f:
            history = json.load(f)
        return history
    except Exception as e:
        print(f"❌ Error loading history: {e}")
        sys.exit(1)


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_timestamp


def truncate(text: str, max_length: int = 80) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def get_stats(history: List[Dict]) -> Dict[str, Any]:
    """Calculate summary statistics."""
    if not history:
        return {}

    confidences = [
        entry.get("metadata", {}).get("confidence", 0.0)
        for entry in history
        if entry.get("metadata", {}).get("confidence") is not None
    ]

    sources = {}
    for entry in history:
        source = entry.get("metadata", {}).get("source", "unknown")
        sources[source] = sources.get(source, 0) + 1

    timestamps = [entry.get("timestamp") for entry in history if entry.get("timestamp")]

    return {
        "total_entries": len(history),
        "date_range": {
            "first": format_timestamp(timestamps[0]) if timestamps else "N/A",
            "last": format_timestamp(timestamps[-1]) if timestamps else "N/A"
        },
        "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
        "sources": sources,
        "entries_with_patterns": sum(
            1 for entry in history
            if entry.get("metadata", {}).get("patterns_used")
        )
    }


def print_stats(stats: Dict[str, Any], domain_name: str):
    """Print summary statistics."""
    print(f"\n{'='*70}")
    print(f"Query History Summary: {domain_name}")
    print(f"{'='*70}")
    print(f"Total entries:     {stats['total_entries']}")
    print(f"Date range:        {stats['date_range']['first']} → {stats['date_range']['last']}")
    print(f"Avg confidence:    {stats['avg_confidence']:.3f}")
    print(f"With patterns:     {stats['entries_with_patterns']}")

    print(f"\nSources:")
    for source, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / stats['total_entries']) * 100
        print(f"  {source:20s} {count:4d} ({pct:5.1f}%)")
    print(f"{'='*70}\n")


def print_entry(entry: Dict[str, Any], index: int, verbose: bool = True):
    """Print a single query/response entry."""
    query = entry.get("query", "")
    response = entry.get("response", "")
    timestamp = entry.get("timestamp", "")
    metadata = entry.get("metadata", {})

    print(f"\n[{index}] {format_timestamp(timestamp)}")
    print(f"{'─'*70}")

    # Query
    if verbose or len(query) <= 80:
        print(f"Query:    {query}")
    else:
        print(f"Query:    {truncate(query, 80)}")

    # Response preview
    if verbose or len(response) <= 200:
        print(f"Response: {response}")
    else:
        lines = response.split('\n')
        preview = lines[0] if lines else response
        print(f"Response: {truncate(preview, 80)}")
        if len(lines) > 1 or len(response) > 80:
            print(f"          ... ({len(response)} chars total)")

    # Metadata
    source = metadata.get("source", "unknown")
    confidence = metadata.get("confidence")
    patterns = metadata.get("patterns_used", [])
    evoked = metadata.get("evoked_questions", [])

    print(f"\nSource:      {source}")
    if confidence is not None:
        print(f"Confidence:  {confidence:.3f}")

    if patterns:
        print(f"Patterns:    {len(patterns)} pattern(s) used")
        if verbose:
            for pattern_id in patterns[:5]:  # Show first 5
                print(f"             - {pattern_id}")
            if len(patterns) > 5:
                print(f"             ... and {len(patterns)-5} more")

    if evoked:
        print(f"Evoked Qs:   {len(evoked)} question(s)")
        if verbose:
            for i, q in enumerate(evoked[:3], 1):
                print(f"             {i}. {truncate(q, 60)}")


def filter_history(
    history: List[Dict],
    limit: Optional[int] = None,
    min_confidence: Optional[float] = None,
    source: Optional[str] = None
) -> List[Dict]:
    """Filter history entries based on criteria."""
    filtered = history

    # Filter by confidence
    if min_confidence is not None:
        filtered = [
            entry for entry in filtered
            if entry.get("metadata", {}).get("confidence", 0.0) >= min_confidence
        ]

    # Filter by source
    if source:
        filtered = [
            entry for entry in filtered
            if entry.get("metadata", {}).get("source", "").lower() == source.lower()
        ]

    # Apply limit (last N entries)
    if limit:
        filtered = filtered[-limit:]

    return filtered


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    # Parse arguments
    domain_name = args[0]
    limit = None
    min_confidence = None
    source = None
    stats_only = False
    json_output = False
    verbose = True

    i = 1
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "--min-confidence" and i + 1 < len(args):
            min_confidence = float(args[i + 1])
            i += 2
        elif args[i] == "--source" and i + 1 < len(args):
            source = args[i + 1]
            i += 2
        elif args[i] == "--stats-only":
            stats_only = True
            i += 1
        elif args[i] == "--json":
            json_output = True
            i += 1
        elif args[i] == "--brief":
            verbose = False
            i += 1
        else:
            i += 1

    # Load history
    history = load_history(domain_name)

    # Filter
    filtered = filter_history(history, limit, min_confidence, source)

    # JSON output
    if json_output:
        print(json.dumps(filtered, indent=2))
        sys.exit(0)

    # Calculate and print stats
    stats = get_stats(history)
    print_stats(stats, domain_name)

    if stats_only:
        sys.exit(0)

    # Print entries
    if filtered != history:
        print(f"Showing {len(filtered)} of {len(history)} entries (filtered)\n")

    for i, entry in enumerate(filtered, start=1):
        print_entry(entry, i, verbose=verbose)

    print(f"\n{'='*70}")
    print(f"End of history ({len(filtered)} entries shown)")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
