"""
Tao API Router - REST endpoints for knowledge analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from .models import (
    SessionSummary, SessionDetail, QueryChain, ChainEntry,
    RelatedQuery, ConceptStats, ConceptCooccurrence, ExplorationDepth
)
from tao.storage import load_history
from tao.analysis import sessions, chains, relations, concepts, depth, sophistication

logger = logging.getLogger("tao.api")

router = APIRouter(prefix="/api/tao", tags=["tao"])


@router.get("/sessions/{domain}", response_model=List[SessionDetail])
async def get_sessions(
    domain: str,
    gap_minutes: int = Query(30, description="Time gap to split sessions (minutes)"),
    min_queries: int = Query(1, description="Minimum queries per session to include")
):
    """
    Get exploration sessions for a domain.

    Sessions are groups of queries separated by time gaps.
    """
    try:
        history = load_history(domain)

        if not history:
            return []

        # Find sessions
        session_list = sessions.find_sessions(history, gap_minutes)

        # Filter by minimum queries
        if min_queries > 1:
            session_list = [s for s in session_list if len(s) >= min_queries]

        # Analyze each session
        results = []
        for i, session in enumerate(session_list):
            analysis = sessions.analyze_session(session)
            results.append(SessionDetail(
                session_id=i + 1,
                **analysis
            ))

        return results

    except Exception as e:
        logger.error(f"Error getting sessions for {domain}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{domain}/summary", response_model=SessionSummary)
async def get_session_summary(
    domain: str,
    gap_minutes: int = Query(30, description="Time gap to split sessions (minutes)")
):
    """Get summary statistics for all sessions."""
    try:
        history = load_history(domain)

        if not history:
            return SessionSummary(
                session_count=0,
                total_queries=0,
                avg_queries_per_session=0,
                largest_session=0,
                smallest_session=0
            )

        # Find sessions
        session_list = sessions.find_sessions(history, gap_minutes)

        # Get summary
        summary = sessions.get_session_summary(session_list)

        return SessionSummary(**summary)

    except Exception as e:
        logger.error(f"Error getting session summary for {domain}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chains/{domain}/{entry_id}", response_model=QueryChain)
async def get_query_chain(
    domain: str,
    entry_id: int,
    before: int = Query(3, description="Number of queries before target"),
    after: int = Query(3, description="Number of queries after target"),
    gap_minutes: int = Query(10, description="Max time gap for chain continuity")
):
    """
    Get query chain before and after a specific entry.

    Traces the path of exploration leading to and from a specific query.
    """
    try:
        history = load_history(domain)

        if not history:
            raise HTTPException(status_code=404, detail=f"No history found for domain {domain}")

        # Get chain
        target, before_chain, after_chain = chains.get_chain(
            history, entry_id, before, after, gap_minutes
        )

        if target is None:
            raise HTTPException(status_code=404, detail=f"Entry #{entry_id} not found")

        # Get summary
        summary = chains.get_chain_summary(target, before_chain, after_chain)

        return QueryChain(
            target=ChainEntry(**target),
            before=[ChainEntry(**entry) for entry in before_chain],
            after=[ChainEntry(**entry) for entry in after_chain],
            summary=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chain for {domain} entry {entry_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/related/{domain}/{entry_id}", response_model=List[RelatedQuery])
async def get_related_queries(
    domain: str,
    entry_id: int,
    strategy: str = Query("all", description="Strategy: temporal, pattern, keyword, or all"),
    limit: int = Query(5, description="Max results per strategy"),
    time_window: int = Query(60, description="Time window for temporal strategy (minutes)"),
    min_keywords: int = Query(2, description="Min shared keywords for keyword strategy")
):
    """
    Find queries related to a specific entry.

    Uses multiple strategies: temporal proximity, shared patterns, keyword overlap.
    """
    try:
        history = load_history(domain)

        if not history:
            raise HTTPException(status_code=404, detail=f"No history found for domain {domain}")

        # Validate strategy
        valid_strategies = {"temporal", "pattern", "keyword", "all"}
        if strategy not in valid_strategies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy '{strategy}'. Must be one of: {', '.join(valid_strategies)}"
            )

        # Find related queries
        related = relations.find_related(
            history, entry_id, strategy, limit, time_window, min_keywords
        )

        return [RelatedQuery(**r) for r in related]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding related queries for {domain} entry {entry_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/{domain}", response_model=List[ConceptStats])
async def get_concepts(
    domain: str,
    top_n: int = Query(10, description="Number of top concepts to return"),
    min_freq: int = Query(2, description="Minimum frequency to include")
):
    """
    Get top concepts (keywords) for a domain.

    Extracts and ranks concepts by frequency across all queries and responses.
    """
    try:
        history = load_history(domain)

        if not history:
            return []

        # Get top concepts
        top_concepts_list = concepts.get_top_concepts(history, top_n, min_freq)

        return [ConceptStats(**c) for c in top_concepts_list]

    except Exception as e:
        logger.error(f"Error getting concepts for {domain}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/{domain}/{concept}/cooccur", response_model=List[ConceptCooccurrence])
async def get_concept_cooccurrence(
    domain: str,
    concept: str,
    min_cooccurrence: int = Query(2, description="Minimum co-occurrence count")
):
    """
    Get concepts that co-occur with the specified concept.

    Finds other concepts that appear in the same queries/responses.
    """
    try:
        history = load_history(domain)

        if not history:
            return []

        # Find co-occurring concepts
        cooccur_list = concepts.find_cooccurring_concepts(
            history, concept.lower(), min_cooccurrence
        )

        return [ConceptCooccurrence(**c) for c in cooccur_list]

    except Exception as e:
        logger.error(f"Error getting concept cooccurrence for {domain}/{concept}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/depth/{domain}", response_model=List[ExplorationDepth])
async def get_exploration_depth(
    domain: str,
    min_depth: int = Query(2, description="Minimum queries to count as deep exploration"),
    time_gap: int = Query(10, description="Max time gap between queries (minutes)"),
    concept: Optional[str] = Query(None, description="Filter for specific concept")
):
    """
    Get deep explorations for a domain.

    A deep exploration is a sequence of related queries within a short time window.
    """
    try:
        history = load_history(domain)

        if not history:
            return []

        # Find deep explorations
        if concept:
            # Filter by concept
            explorations = depth.find_concept_depth(history, concept, time_gap)
        else:
            # All deep explorations
            explorations = depth.find_deep_explorations(history, min_depth, time_gap)

        return [ExplorationDepth(**e) for e in explorations]

    except Exception as e:
        logger.error(f"Error getting exploration depth for {domain}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{domain}")
async def get_full_history(
    domain: str,
    limit: Optional[int] = Query(None, description="Limit number of entries returned")
):
    """
    Get full query history for a domain.

    Returns complete query/response pairs with all metadata.
    """
    try:
        history = load_history(domain)

        if not history:
            return []

        # Apply limit if specified
        if limit and limit > 0:
            history = history[-limit:]  # Get most recent N entries

        return history

    except Exception as e:
        logger.error(f"Error getting history for {domain}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-velocity/{domain}")
async def get_learning_velocity(
    domain: str,
    min_questions: int = Query(5, description="Minimum questions required for calculation")
):
    """
    Calculate learning velocity for a domain.

    Measures how quickly a user progresses from novice (L1) to expert (L4) questions.

    Returns:
        - velocity: Levels per day (e.g., 0.41 = exceptional)
        - initial_level: Average level of first 3 questions
        - final_level: Average level of last 3 questions
        - days_elapsed: Time period covered
        - progression: Daily average levels
        - interpretation: Human-readable assessment
    """
    try:
        history = load_history(domain)

        if not history:
            raise HTTPException(status_code=404, detail=f"No history found for domain '{domain}'")

        # Calculate learning velocity
        result = sophistication.calculate_learning_velocity(history, domain, min_questions)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating learning velocity for {domain}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-question")
async def classify_question(
    question: str = Query(..., description="Question text to classify"),
    domain: Optional[str] = Query(None, description="Optional domain context")
):
    """
    Classify a single question's sophistication level.

    Returns:
        - level: 1-4 (Novice, Intermediate, Advanced, Expert)
        - confidence: 0.0-1.0
        - reasoning: Explanation of classification
        - label: Human-readable level name
    """
    try:
        classifier = sophistication.QuestionClassifier()
        result = classifier.classify_question(question, domain)
        return result

    except Exception as e:
        logger.error(f"Error classifying question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sophistication-distribution/{domain}")
async def get_sophistication_distribution(domain: str):
    """
    Get distribution of question sophistication levels for a domain.

    Returns count and percentage for each level (L1-L4).
    """
    try:
        history = load_history(domain)

        if not history:
            return {
                "total_classified": 0,
                "distribution": {}
            }

        # Count classified questions by level
        level_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        total_classified = 0

        for entry in history:
            if "metadata" in entry and "question_level" in entry["metadata"]:
                level = entry["metadata"]["question_level"]
                if level in level_counts:
                    level_counts[level] += 1
                    total_classified += 1

        # Calculate percentages
        distribution = {}
        for level in [1, 2, 3, 4]:
            count = level_counts[level]
            percentage = (count / total_classified * 100) if total_classified > 0 else 0
            distribution[f"L{level}"] = {
                "count": count,
                "percentage": round(percentage, 1),
                "label": sophistication.QuestionClassifier.LEVELS[level]["name"]
            }

        return {
            "total_questions": len(history),
            "total_classified": total_classified,
            "unclassified": len(history) - total_classified,
            "distribution": distribution
        }

    except Exception as e:
        logger.error(f"Error getting sophistication distribution for {domain}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
