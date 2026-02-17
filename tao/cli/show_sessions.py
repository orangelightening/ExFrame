#!/usr/bin/env python3
"""
Session Analyzer - Group queries into exploration sessions

Sessions are groups of queries separated by time gaps. This helps identify
distinct periods of exploration and understand usage patterns.

Usage:
    python -m tao.cli.show_sessions <domain> [options]
    python3 scripts/show_sessions.py <domain> [options]  # Legacy

Examples:
    python -m tao.cli.show_sessions peter
    python -m tao.cli.show_sessions peter --gap 30
    python -m tao.cli.show_sessions psycho --min-queries 2

Options:
    --gap MINUTES         Time gap to split sessions (default: 30 minutes)
    --min-queries N       Only show sessions with at least N queries
    --stats-only          Show only session statistics
    --json                Output as JSON
"""

import json
import sys
from typing import List, Dict
from tao.storage import load_history
from tao.analysis.sessions import find_sessions, analyze_session, get_session_summary


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
    summary = get_session_summary(sessions)

    print(f"\n{'='*70}")
    print(f"Session Statistics: {domain}")
    print(f"{'='*70}")
    print(f"Total sessions:      {summary['session_count']}")
    print(f"Total queries:       {summary['total_queries']}")

    if summary['session_count'] > 0:
        print(f"Avg queries/session: {summary['avg_queries_per_session']}")
        print(f"Largest session:     {summary['largest_session']} queries")
        print(f"Smallest session:    {summary['smallest_session']} queries")

        if 'avg_duration_minutes' in summary:
            print(f"Avg duration:        {summary['avg_duration_minutes']} minutes")
            print(f"Longest session:     {summary['longest_session_minutes']} minutes")

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
        print(f"❌ No query history found for domain '{domain_name}'")
        sys.exit(1)

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
