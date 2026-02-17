"""
Concept Timeline Analysis Module

Extracts and tracks concepts (keywords) across query history to show
when concepts appeared, frequency, and co-occurrence patterns.
"""

from datetime import datetime
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
import re


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
        'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'them', 'us',
        'about', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'all', 'both', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
    }

    keywords = {w for w in words if len(w) >= min_length and w not in stop_words}
    return keywords


def build_concept_index(history: List[Dict]) -> Dict[str, List[Tuple[int, str]]]:
    """
    Build index of concepts to entries.

    Args:
        history: Query history

    Returns:
        Dict mapping concept -> [(entry_id, timestamp), ...]
    """
    concept_index = defaultdict(list)

    for entry in history:
        entry_id = entry.get('id')
        timestamp = entry['timestamp']

        # Extract keywords from query and response
        text = entry['query'] + ' ' + entry.get('response', '')
        keywords = extract_keywords(text)

        # Add to index
        for keyword in keywords:
            concept_index[keyword].append((entry_id, timestamp))

    return dict(concept_index)


def get_concept_stats(concept: str, occurrences: List[Tuple[int, str]]) -> Dict[str, Any]:
    """
    Get statistics for a specific concept.

    Args:
        concept: The concept keyword
        occurrences: List of (entry_id, timestamp) tuples

    Returns:
        Dict with concept statistics
    """
    if not occurrences:
        return {}

    # Sort by timestamp
    sorted_occ = sorted(occurrences, key=lambda x: x[1])

    return {
        'concept': concept,
        'frequency': len(occurrences),
        'first_seen': sorted_occ[0][1],
        'last_seen': sorted_occ[-1][1],
        'entry_ids': [occ[0] for occ in sorted_occ]
    }


def get_top_concepts(
    history: List[Dict],
    top_n: int = 10,
    min_freq: int = 2
) -> List[Dict[str, Any]]:
    """
    Get top N most frequent concepts.

    Args:
        history: Query history
        top_n: Number of top concepts to return
        min_freq: Minimum frequency to include

    Returns:
        List of concept statistics dicts
    """
    concept_index = build_concept_index(history)

    # Filter by minimum frequency
    filtered = {k: v for k, v in concept_index.items() if len(v) >= min_freq}

    # Sort by frequency
    sorted_concepts = sorted(filtered.items(), key=lambda x: len(x[1]), reverse=True)

    # Get top N
    top_concepts = sorted_concepts[:top_n]

    # Build results
    results = []
    for concept, occurrences in top_concepts:
        stats = get_concept_stats(concept, occurrences)
        results.append(stats)

    return results


def find_cooccurring_concepts(
    history: List[Dict],
    target_concept: str,
    min_cooccurrence: int = 2
) -> List[Dict[str, Any]]:
    """
    Find concepts that co-occur with target concept.

    Args:
        history: Query history
        target_concept: Target concept to find co-occurrences for
        min_cooccurrence: Minimum times concepts must co-occur

    Returns:
        List of co-occurring concepts with counts
    """
    concept_index = build_concept_index(history)

    # Get entries containing target concept
    if target_concept not in concept_index:
        return []

    target_entry_ids = set(occ[0] for occ in concept_index[target_concept])

    # Count co-occurrences
    cooccurrence_counts = defaultdict(int)

    for concept, occurrences in concept_index.items():
        if concept == target_concept:
            continue

        # Count how many times this concept appears in same entries as target
        concept_entry_ids = set(occ[0] for occ in occurrences)
        overlap = target_entry_ids & concept_entry_ids

        if len(overlap) >= min_cooccurrence:
            cooccurrence_counts[concept] = len(overlap)

    # Sort by co-occurrence count
    sorted_cooccur = sorted(cooccurrence_counts.items(), key=lambda x: x[1], reverse=True)

    return [
        {'concept': concept, 'cooccurrence_count': count}
        for concept, count in sorted_cooccur
    ]
