#!/usr/bin/env python3
"""
Session Analyzer - Group queries into exploration sessions

Sessions are groups of queries separated by time gaps. This helps identify
distinct periods of exploration and understand usage patterns.

Usage:
    python3 scripts/show_sessions.py <domain> [options]

Examples:
    python3 scripts/show_sessions.py peter
    python3 scripts/show_sessions.py peter --gap 30
    python3 scripts/show_sessions.py psycho --min-queries 2

Options:
    --gap MINUTES         Time gap to split sessions (default: 30 minutes)
    --min-queries N       Only show sessions with at least N queries
    --stats-only          Show only session statistics
    --json                Output as JSON
"""

import gzip
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


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


def find_sessions(history: List[Dict], gap_minutes: int = 30) -> List[List[Dict]]:
    """
    Group queries into sessions based on time gaps.

    A new session starts when there's a gap > gap_minutes between queries.
    """
    if not history:
        return []

    sessions = []
    current_session = [history[0]]

    for i in range(1, len(history)):
        prev_time = parse_timestamp(history[i-1]['timestamp'])
        curr_time = parse_timestamp(history[i]['timestamp'])

        gap = (curr_time - prev_time).total_seconds() / 60  # minutes

        if gap <= gap_minutes:
            # Continue current session
            current_session.append(history[i])
        else:
            # Start new session
            sessions.append(current_session)
            current_session = [history[i]]

    # Add final session
    if current_session:
        sessions.append(current_session)

    return sessions


def analyze_session(session: List[Dict]) -> Dict[str, Any]:
    """Analyze a single session."""
    if not session:
        return {}

    start_time = parse_timestamp(session[0]['timestamp'])
    end_time = parse_timestamp(session[-1]['timestamp'])
    duration = (end_time - start_time).total_seconds() / 60  # minutes

    # Count sources
    sources = {}
    for entry in session:
        source = entry.get('metadata', {}).get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1

    # Calculate average confidence
    confidences = [
        entry.get('metadata', {}).get('confidence', 0.0)
        for entry in session
        if entry.get('metadata', {}).get('confidence') is not None
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return {
        'query_count': len(session),
        'start_time': format_timestamp(start_time),
        'end_time': format_timestamp(end_time),
        'duration_minutes': round(duration, 1),
        'sources': sources,
        'avg_confidence': round(avg_confidence, 3),
        'queries': [e['query'][:60] + '...' if len(e['query']) > 60 else e['query']
                   for e in session]
    }


def print_sessions(sessions: List[List[Dict]], domain: str, gap_minutes: int):
    """Print sessions in readable format."""
    print(f"\n{'='*70}")
    print(f"Query Sessions: {domain}")
    print(f"Session gap threshold: {gap_minutes} minutes")
    print(f"{'='*70}")
    print(f"Total sessions: {len(sessions)}")
    print(f"Total queries:  {sum(len(s) for s in sessions)}")
    print(f"{'='*70}\n")

    for i, session in enumerate(sessions, 1):
        stats = analyze_session(session)

        print(f"\n{'─'*70}")
        print(f"Session {i}")
        print(f"{'─'*70}")
        print(f"Time:       {stats['start_time']} → {stats['end_time']}")
        print(f"Duration:   {stats['duration_minutes']} minutes")
        print(f"Queries:    {stats['query_count']}")
        print(f"Confidence: {stats['avg_confidence']:.3f}")

        print(f"\nSources:")
        for source, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {source:20s} {count:3d}")

        print(f"\nQueries:")
        for j, query in enumerate(stats['queries'], 1):
            print(f"  {j}. {query}")


def print_stats_only(sessions: List[List[Dict]], domain: str):
    """Print only session statistics."""
    print(f"\n{'='*70}")
    print(f"Session Statistics: {domain}")
    print(f"{'='*70}")
    print(f"Total sessions:     {len(sessions)}")
    print(f"Total queries:      {sum(len(s) for s in sessions)}")

    if sessions:
        session_sizes = [len(s) for s in sessions]
        durations = []

        for session in sessions:
            if len(session) > 1:
                start = parse_timestamp(session[0]['timestamp'])
                end = parse_timestamp(session[-1]['timestamp'])
                durations.append((end - start).total_seconds() / 60)

        print(f"Avg queries/session: {sum(session_sizes) / len(session_sizes):.1f}")
        print(f"Largest session:     {max(session_sizes)} queries")
        print(f"Smallest session:    {min(session_sizes)} queries")

        if durations:
            print(f"Avg duration:        {sum(durations) / len(durations):.1f} minutes")
            print(f"Longest session:     {max(durations):.1f} minutes")

    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    # Parse arguments
    domain_name = args[0]
    gap_minutes = 30
    min_queries = 1
    stats_only = False
    json_output = False

    i = 1
    while i < len(args):
        if args[i] == "--gap" and i + 1 < len(args):
            gap_minutes = int(args[i + 1])
            i += 2
        elif args[i] == "--min-queries" and i + 1 < len(args):
            min_queries = int(args[i + 1])
            i += 2
        elif args[i] == "--stats-only":
            stats_only = True
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

    # Find sessions
    sessions = find_sessions(history, gap_minutes)

    # Filter by minimum queries
    if min_queries > 1:
        sessions = [s for s in sessions if len(s) >= min_queries]

    # JSON output
    if json_output:
        output = [analyze_session(s) for s in sessions]
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Print results
    if stats_only:
        print_stats_only(sessions, domain_name)
    else:
        print_sessions(sessions, domain_name, gap_minutes)


if __name__ == "__main__":
    main()
