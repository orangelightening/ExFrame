"""
Exploration Depth Analysis Module

Analyzes query patterns to identify deep explorations vs shallow touches.
A deep exploration is a sequence of related queries within a short time window.
"""

from datetime import datetime
from typing import List, Dict, Any, Set
import re


def parse_timestamp(iso_timestamp: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(iso_timestamp)


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

    Args:
        history: Query history
        time_gap_minutes: Max gap between queries in same exploration

    Returns:
        List of exploration chains (each chain is list of entries)
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


def analyze_exploration(chain: List[Dict]) -> Dict[str, Any]:
    """
    Analyze a single exploration chain.

    Args:
        chain: List of entries in the chain

    Returns:
        Dict with exploration statistics
    """
    if not chain:
        return {}

    # Extract all keywords from chain
    all_keywords = set()
    for entry in chain:
        text = entry['query'] + ' ' + entry.get('response', '')
        keywords = extract_keywords(text)
        all_keywords.update(keywords)

    # Calculate duration
    start_time = parse_timestamp(chain[0]['timestamp'])
    end_time = parse_timestamp(chain[-1]['timestamp'])
    duration = (end_time - start_time).total_seconds() / 60

    # Get sources
    sources = set()
    for entry in chain:
        source = entry.get('metadata', {}).get('source', 'unknown')
        sources.add(source)

    return {
        'query_count': len(chain),
        'start_time': chain[0]['timestamp'],
        'end_time': chain[-1]['timestamp'],
        'duration_minutes': round(duration, 1),
        'unique_concepts': len(all_keywords),
        'top_concepts': sorted(all_keywords)[:10],  # Top 10 alphabetically
        'sources': list(sources),
        'queries': [e['query'][:60] + '...' if len(e['query']) > 60 else e['query']
                   for e in chain]
    }


def find_deep_explorations(
    history: List[Dict],
    min_depth: int = 2,
    time_gap: int = 10
) -> List[Dict[str, Any]]:
    """
    Find deep explorations (multiple related queries).

    Args:
        history: Query history
        min_depth: Minimum queries to count as deep exploration
        time_gap: Max time gap between queries in minutes

    Returns:
        List of deep exploration analyses
    """
    chains = find_exploration_chains(history, time_gap)

    # Filter by minimum depth
    deep_chains = [chain for chain in chains if len(chain) >= min_depth]

    # Analyze each deep chain
    analyses = []
    for chain in deep_chains:
        analysis = analyze_exploration(chain)
        analyses.append(analysis)

    # Sort by query count (deepest first)
    analyses.sort(key=lambda x: x['query_count'], reverse=True)

    return analyses


def find_concept_depth(
    history: List[Dict],
    concept: str,
    time_gap: int = 10
) -> List[Dict[str, Any]]:
    """
    Find explorations focused on a specific concept.

    Args:
        history: Query history
        concept: Concept keyword to search for
        time_gap: Max time gap between queries in minutes

    Returns:
        List of explorations containing the concept
    """
    # Find all exploration chains
    chains = find_exploration_chains(history, time_gap)

    # Filter chains containing the concept
    concept_lower = concept.lower()
    matching_chains = []

    for chain in chains:
        # Check if concept appears in any query/response in this chain
        for entry in chain:
            text = (entry['query'] + ' ' + entry.get('response', '')).lower()
            if concept_lower in text:
                matching_chains.append(chain)
                break  # Found in this chain, move to next

    # Analyze matching chains
    analyses = []
    for chain in matching_chains:
        analysis = analyze_exploration(chain)
        analysis['focused_on'] = concept
        analyses.append(analysis)

    # Sort by query count
    analyses.sort(key=lambda x: x['query_count'], reverse=True)

    return analyses
