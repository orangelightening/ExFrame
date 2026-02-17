#!/usr/bin/env python3
"""
Query Chain Tracer - Show exploration chains before and after a query

Traces the path of exploration leading to and from a specific query,
helping understand how questions evolved over time.

Usage:
    python -m tao.cli.trace_chain <domain> --entry ID [options]
    python3 scripts/trace_chain.py <domain> --entry ID [options]  # Legacy

Examples:
    python -m tao.cli.trace_chain peter --entry 5
    python -m tao.cli.trace_chain peter --entry 5 --before 3 --after 5
    python -m tao.cli.trace_chain psycho --entry 2 --gap 10

Options:
    --entry ID            Entry ID to trace from (required)
    --before N            Show N queries before (default: 3)
    --after N             Show N queries after (default: 3)
    --gap MINUTES         Max time gap for chain (default: 10 minutes)
    --json                Output as JSON
"""

import json
import sys
from typing import Dict, List
from tao.storage import load_history
from tao.analysis.chains import get_chain, parse_timestamp


def format_timestamp(dt) -> str:
    """Format datetime to readable format."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def print_entry(entry: Dict, label: str = ""):
    """Print a single entry."""
    query = entry.get('query', '')
    response = entry.get('response', '')
    timestamp = entry.get('timestamp', '')
    metadata = entry.get('metadata', {})

    # Truncate long text
    if len(response) > 150:
        response = response[:150] + '...'

    print(f"\n{label}[{entry.get('id')}] {format_timestamp(parse_timestamp(timestamp))}")
    print(f"{'─'*70}")
    print(f"Query:      {query}")
    print(f"Response:   {response}")
    print(f"Source:     {metadata.get('source', 'unknown')}")
    confidence = metadata.get('confidence')
    if confidence is not None:
        print(f"Confidence: {confidence:.3f}")


def print_chain(target: Dict, before: List[Dict], after: List[Dict], domain: str, max_gap: int):
    """Print the complete chain."""
    print(f"\n{'='*70}")
    print(f"Query Chain: {domain}")
    print(f"Tracing from entry #{target.get('id')}")
    print(f"Max time gap: {max_gap} minutes")
    print(f"{'='*70}")

    # Before chain
    if before:
        print(f"\n{'▼'*70}")
        print(f"BEFORE ({len(before)} queries leading up to this)")
        print(f"{'▼'*70}")
        for entry in before:
            print_entry(entry, "  ↓ ")

    # Target entry
    print(f"\n{'█'*70}")
    print(f"TARGET ENTRY")
    print(f"{'█'*70}")
    print_entry(target, "  ➤ ")

    # After chain
    if after:
        print(f"\n{'▲'*70}")
        print(f"AFTER ({len(after)} queries following from this)")
        print(f"{'▲'*70}")
        for entry in after:
            print_entry(entry, "  ↑ ")

    # Summary
    print(f"\n{'='*70}")
    total_chain = len(before) + 1 + len(after)
    print(f"Chain length: {total_chain} queries")
    if before and after:
        start_time = parse_timestamp(before[0]['timestamp'])
        end_time = parse_timestamp(after[-1]['timestamp'])
        duration = (end_time - start_time).total_seconds() / 60
        print(f"Chain duration: {duration:.1f} minutes")
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
    before_count = 3
    after_count = 3
    max_gap_minutes = 10
    json_output = False

    i = 1
    while i < len(args):
        if args[i] == "--entry" and i + 1 < len(args):
            entry_id = int(args[i + 1])
            i += 2
        elif args[i] == "--before" and i + 1 < len(args):
            before_count = int(args[i + 1])
            i += 2
        elif args[i] == "--after" and i + 1 < len(args):
            after_count = int(args[i + 1])
            i += 2
        elif args[i] == "--gap" and i + 1 < len(args):
            max_gap_minutes = int(args[i + 1])
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

    # Load history
    history = load_history(domain_name)

    if not history:
        print(f"❌ No query history found for domain '{domain_name}'")
        sys.exit(1)

    # Get chain
    target_entry, before_chain, after_chain = get_chain(
        history, entry_id, before_count, after_count, max_gap_minutes
    )

    if target_entry is None:
        print(f"❌ Entry #{entry_id} not found in {domain_name} history")
        sys.exit(1)

    # JSON output
    if json_output:
        output = {
            'target': target_entry,
            'before': before_chain,
            'after': after_chain
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Print chain
    print_chain(target_entry, before_chain, after_chain, domain_name, max_gap_minutes)


if __name__ == "__main__":
    main()
