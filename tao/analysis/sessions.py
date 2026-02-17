"""
Session Analysis Module

Provides functions to detect and analyze exploration sessions from query history.
Sessions are groups of queries separated by time gaps.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any


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

    Args:
        history: Query history (list of dicts)
        gap_minutes: Max gap between queries in same session (default: 30)

    Returns:
        List of sessions (each session is list of entries)
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
    """
    Analyze a single session and return statistics.

    Args:
        session: List of query history entries in the session

    Returns:
        Dict with session statistics (query_count, duration, sources, etc.)
    """
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


def get_session_summary(sessions: List[List[Dict]]) -> Dict[str, Any]:
    """
    Get summary statistics for all sessions.

    Args:
        sessions: List of sessions

    Returns:
        Dict with aggregate statistics
    """
    if not sessions:
        return {
            'session_count': 0,
            'total_queries': 0
        }

    session_sizes = [len(s) for s in sessions]
    durations = []

    for session in sessions:
        if len(session) > 1:
            start = parse_timestamp(session[0]['timestamp'])
            end = parse_timestamp(session[-1]['timestamp'])
            durations.append((end - start).total_seconds() / 60)

    summary = {
        'session_count': len(sessions),
        'total_queries': sum(session_sizes),
        'avg_queries_per_session': round(sum(session_sizes) / len(session_sizes), 1),
        'largest_session': max(session_sizes),
        'smallest_session': min(session_sizes)
    }

    if durations:
        summary['avg_duration_minutes'] = round(sum(durations) / len(durations), 1)
        summary['longest_session_minutes'] = round(max(durations), 1)

    return summary
