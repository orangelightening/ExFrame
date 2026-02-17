"""
Query Chain Analysis Module

Provides functions to trace exploration chains before and after specific queries.
Chains help understand how questions evolved over time.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


def parse_timestamp(iso_timestamp: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(iso_timestamp)


def time_gap_minutes(entry1: Dict, entry2: Dict) -> float:
    """Calculate time gap between two entries in minutes."""
    t1 = parse_timestamp(entry1['timestamp'])
    t2 = parse_timestamp(entry2['timestamp'])
    return abs((t2 - t1).total_seconds() / 60)


def find_entry_index(history: List[Dict], entry_id: int) -> Optional[int]:
    """
    Find index of entry with given ID.

    Args:
        history: Query history
        entry_id: Entry ID to find

    Returns:
        Index of entry or None if not found
    """
    for i, entry in enumerate(history):
        if entry.get('id') == entry_id:
            return i
    return None


def get_chain_before(history: List[Dict], start_idx: int, count: int, max_gap: int) -> List[Dict]:
    """
    Get chain of queries before the start index.

    Args:
        history: Query history
        start_idx: Starting index
        count: Maximum number of queries to retrieve
        max_gap: Maximum time gap in minutes to continue chain

    Returns:
        List of entries in the chain before target
    """
    chain = []
    idx = start_idx - 1

    while idx >= 0 and len(chain) < count:
        # Check time gap
        if chain:  # Check gap from most recent in chain
            gap = time_gap_minutes(history[idx], chain[0])
            if gap > max_gap:
                break

        chain.insert(0, history[idx])
        idx -= 1

    return chain


def get_chain_after(history: List[Dict], start_idx: int, count: int, max_gap: int) -> List[Dict]:
    """
    Get chain of queries after the start index.

    Args:
        history: Query history
        start_idx: Starting index
        count: Maximum number of queries to retrieve
        max_gap: Maximum time gap in minutes to continue chain

    Returns:
        List of entries in the chain after target
    """
    chain = []
    idx = start_idx + 1

    while idx < len(history) and len(chain) < count:
        # Check time gap
        if chain:  # Check gap from most recent in chain
            gap = time_gap_minutes(chain[-1], history[idx])
            if gap > max_gap:
                break

        chain.append(history[idx])
        idx += 1

    return chain


def get_chain(
    history: List[Dict],
    entry_id: int,
    before: int = 3,
    after: int = 3,
    gap_minutes: int = 10
) -> Tuple[Optional[Dict], List[Dict], List[Dict]]:
    """
    Get complete query chain around a target entry.

    Args:
        history: Query history
        entry_id: Target entry ID
        before: Number of queries to retrieve before target
        after: Number of queries to retrieve after target
        gap_minutes: Maximum time gap in minutes for chain continuity

    Returns:
        Tuple of (target_entry, before_chain, after_chain)
        Returns (None, [], []) if entry not found
    """
    target_idx = find_entry_index(history, entry_id)

    if target_idx is None:
        return None, [], []

    target_entry = history[target_idx]
    before_chain = get_chain_before(history, target_idx, before, gap_minutes)
    after_chain = get_chain_after(history, target_idx, after, gap_minutes)

    return target_entry, before_chain, after_chain


def get_chain_summary(target: Dict, before: List[Dict], after: List[Dict]) -> Dict[str, Any]:
    """
    Get summary statistics for a chain.

    Args:
        target: Target entry
        before: Entries before target
        after: Entries after target

    Returns:
        Dict with chain statistics
    """
    total_length = len(before) + 1 + len(after)

    summary = {
        'target_id': target.get('id'),
        'chain_length': total_length,
        'before_count': len(before),
        'after_count': len(after)
    }

    if before and after:
        start_time = parse_timestamp(before[0]['timestamp'])
        end_time = parse_timestamp(after[-1]['timestamp'])
        duration = (end_time - start_time).total_seconds() / 60
        summary['duration_minutes'] = round(duration, 1)

    return summary
