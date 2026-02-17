"""
Query Relations Analysis Module

Provides functions to find related queries using multiple strategies:
- Temporal proximity (queries nearby in time)
- Shared patterns (queries using same domain patterns)
- Keyword overlap (queries with common terms)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
import re


def parse_timestamp(iso_timestamp: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(iso_timestamp)


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
                'entry_id': entry.get('id'),
                'query': entry.get('query'),
                'score': round(score, 3),
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
                'entry_id': entry.get('id'),
                'query': entry.get('query'),
                'score': round(score, 3),
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
                'entry_id': entry.get('id'),
                'query': entry.get('query'),
                'score': round(score, 3),
                'reason': f'{len(intersection)} shared keywords: {shared_str}',
                'strategy': 'keyword'
            })

    # Sort by score (most overlap first)
    related.sort(key=lambda x: x['score'], reverse=True)
    return related[:limit]


def find_related(
    history: List[Dict],
    entry_id: int,
    strategy: str = "all",
    limit: int = 5,
    time_window: int = 60,
    min_keywords: int = 2
) -> List[Dict]:
    """
    Find related queries using specified strategy.

    Args:
        history: Query history
        entry_id: Target entry ID
        strategy: "temporal", "pattern", "keyword", or "all"
        limit: Max results per strategy
        time_window: Time window for temporal strategy (minutes)
        min_keywords: Min shared keywords for keyword strategy

    Returns:
        List of related entries with scores and reasons
    """
    target_entry = find_entry_by_id(history, entry_id)
    if target_entry is None:
        return []

    all_related = []

    if strategy in ("temporal", "all"):
        temporal = find_temporal_related(target_entry, history, time_window, limit)
        all_related.extend(temporal)

    if strategy in ("pattern", "all"):
        pattern = find_pattern_related(target_entry, history, limit)
        all_related.extend(pattern)

    if strategy in ("keyword", "all"):
        keyword = find_keyword_related(target_entry, history, min_keywords, limit)
        all_related.extend(keyword)

    # Remove duplicates (same entry found by multiple strategies)
    seen = set()
    unique_related = []
    for item in all_related:
        if item['entry_id'] not in seen:
            seen.add(item['entry_id'])
            unique_related.append(item)

    return unique_related
