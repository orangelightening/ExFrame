"""
Pydantic models for Tao API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SessionSummary(BaseModel):
    """Summary statistics for all sessions."""
    session_count: int
    total_queries: int
    avg_queries_per_session: float
    largest_session: int
    smallest_session: int
    avg_duration_minutes: Optional[float] = None
    longest_session_minutes: Optional[float] = None


class SessionDetail(BaseModel):
    """Detailed information about a single session."""
    session_id: int
    query_count: int
    start_time: str
    end_time: str
    duration_minutes: float
    sources: Dict[str, int]
    avg_confidence: float
    queries: List[str]


class ChainEntry(BaseModel):
    """Single entry in a query chain."""
    id: int
    timestamp: str
    query: str
    response: str
    metadata: Dict[str, Any] = {}


class QueryChain(BaseModel):
    """Complete query chain with target and surrounding context."""
    target: ChainEntry
    before: List[ChainEntry]
    after: List[ChainEntry]
    summary: Dict[str, Any]


class RelatedQuery(BaseModel):
    """Related query result."""
    entry_id: int
    query: str
    score: float
    reason: str
    strategy: str


class ConceptStats(BaseModel):
    """Statistics for a concept keyword."""
    concept: str
    frequency: int
    first_seen: str
    last_seen: str
    entry_ids: List[int]


class ConceptCooccurrence(BaseModel):
    """Co-occurring concept."""
    concept: str
    cooccurrence_count: int


class ExplorationDepth(BaseModel):
    """Deep exploration analysis."""
    query_count: int
    start_time: str
    end_time: str
    duration_minutes: float
    unique_concepts: int
    top_concepts: List[str]
    sources: List[str]
    queries: List[str]
    focused_on: Optional[str] = None
