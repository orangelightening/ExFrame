#!/usr/bin/env python3
"""
Synthesize realistic test candidate data for BrainUse assessment.

This script generates query history that simulates a candidate exploring
assessment domains over a 10-day period with realistic learning patterns.

Usage:
    python scripts/synthesize_test_candidate.py --candidate-name "Test Engineer"
"""

import json
import gzip
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import argparse


# Question templates by sophistication level for each domain
CLOUD_QUESTIONS = {
    # Level 1: Fundamentals (0-1.5)
    1: [
        "What is the difference between EC2 and Lambda?",
        "How do I store files in AWS?",
        "What is a VPC?",
        "What's the difference between S3 and EBS?",
        "How does auto-scaling work in AWS?",
        "What is CloudFront used for?",
    ],
    # Level 2: Practical (1.5-2.5)
    2: [
        "When should I use RDS vs DynamoDB?",
        "How do I design a scalable web application architecture?",
        "What are best practices for IAM roles?",
        "How do I set up a load balancer for high availability?",
        "What's the difference between Application and Network Load Balancer?",
        "How do I implement blue-green deployments?",
    ],
    # Level 3: Advanced (2.5-3.5)
    3: [
        "How do I handle eventual consistency in a distributed system?",
        "What are trade-offs between multi-AZ and multi-region?",
        "How do I design for 99.99% availability?",
        "How do I optimize costs for a large-scale S3 deployment?",
        "What's the best approach to disaster recovery in AWS?",
        "How do I implement cross-region replication with low latency?",
    ],
    # Level 4: Expert (3.5-4.0)
    4: [
        "How does AWS handle network partition during a regional outage?",
        "What are consistency guarantees for cross-region DynamoDB replication?",
        "How do I design a globally distributed system with strong consistency?",
        "What are the CAP theorem implications for Aurora's architecture?",
        "How do I optimize S3 request rates above the partition limit?",
    ],
}

LEADERSHIP_QUESTIONS = {
    1: [
        "How do I run an effective 1-on-1?",
        "What's the difference between a tech lead and engineering manager?",
        "How do I give constructive feedback?",
        "How often should I meet with my team?",
        "What should I discuss in a 1-on-1?",
    ],
    2: [
        "How do I resolve conflict between two senior engineers?",
        "What's the best way to estimate project timelines?",
        "How do I keep a team motivated during a difficult project?",
        "How do I handle an underperforming team member?",
        "What's the right way to delegate tasks?",
    ],
    3: [
        "How do I build a strong engineering culture?",
        "When should I split a team into multiple teams?",
        "How do I balance tech debt with feature development?",
        "How do I scale my team from 5 to 20 engineers?",
        "What's the best organizational structure for a product team?",
    ],
    4: [
        "How do I align engineering strategy with business objectives when they conflict?",
        "What's the right organizational structure for transitioning from startup to scale-up?",
        "How do I drive technical change across a 500-person engineering org?",
        "How do I balance innovation with stability in a mature product?",
    ],
}

API_QUESTIONS = {
    1: [
        "What's the difference between GET and POST?",
        "How do I return an error from an API?",
        "What is REST?",
        "What HTTP status codes should I use?",
        "How do I authenticate API requests?",
    ],
    2: [
        "Should I use PUT or PATCH for updates?",
        "How do I version my API?",
        "What's the best way to handle pagination?",
        "How do I implement rate limiting?",
        "What's the difference between REST and GraphQL?",
    ],
    3: [
        "How do I maintain consistency across microservices?",
        "Should I use REST or GraphQL for microservices?",
        "How do I handle authentication in an API gateway?",
        "How do I design idempotent APIs?",
        "What's the best approach to API caching?",
    ],
    4: [
        "How do I design APIs for 10-year backward compatibility?",
        "What are trade-offs between REST, GraphQL, and gRPC at scale?",
        "How do I evolve an API used by thousands of clients?",
        "How do I implement distributed tracing across microservices?",
    ],
}

DOMAIN_QUESTIONS = {
    "cloud_assessment": CLOUD_QUESTIONS,
    "leadership_assessment": LEADERSHIP_QUESTIONS,
    "api_assessment": API_QUESTIONS,
}


def generate_query_history(
    domain: str,
    num_sessions: int = 8,
    days: int = 10,
    learning_velocity: float = 0.35,
) -> List[Dict[str, Any]]:
    """
    Generate realistic query history for a candidate.

    Args:
        domain: Domain ID (cloud_assessment, leadership_assessment, api_assessment)
        num_sessions: Number of exploration sessions
        days: Assessment period in days
        learning_velocity: Learning rate (0.2=slow, 0.4=fast)

    Returns:
        List of query/response entries with timestamps
    """

    history = []
    questions = DOMAIN_QUESTIONS[domain]

    # Start with lower sophistication, progress over time
    current_level = 1.0
    max_level = 4.0

    # Spread sessions over assessment period
    start_time = datetime.now() - timedelta(days=days)
    session_times = []

    for i in range(num_sessions):
        # Random session time during assessment period
        day_offset = random.uniform(0, days)
        # Most sessions during work hours (9am-6pm)
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)

        session_time = start_time + timedelta(
            days=day_offset,
            hours=hour - start_time.hour,
            minutes=minute - start_time.minute
        )
        session_times.append(session_time)

    session_times.sort()

    entry_id = 1
    for session_idx, session_time in enumerate(session_times):
        # Each session has 3-8 questions
        num_questions = random.randint(3, 8)

        # Progress sophistication level based on learning velocity
        if session_idx > 0:
            current_level = min(max_level, current_level + learning_velocity * random.uniform(0.8, 1.2))

        for q_idx in range(num_questions):
            # Determine sophistication level for this question
            level_int = min(4, max(1, int(current_level)))

            # Occasionally ask a question at current_level +/- 1 (exploration)
            if random.random() < 0.3:
                level_int = max(1, min(4, level_int + random.choice([-1, 0, 1])))

            # Pick a random question from this level
            question = random.choice(questions[level_int])

            # Calculate sophistication score (1.0-4.0 scale)
            sophistication = level_int + random.uniform(-0.3, 0.3)
            sophistication = max(1.0, min(4.0, sophistication))

            # Generate response
            response = f"[Synthesized response for: {question}]"

            # Time within session (questions spaced 1-5 minutes apart)
            if q_idx > 0:
                session_time += timedelta(minutes=random.randint(1, 5))

            entry = {
                "entry_id": entry_id,
                "timestamp": session_time.isoformat(),
                "query": question,
                "response": response,
                "source": "llm",
                "confidence": random.uniform(0.85, 0.95),
                "metadata": {
                    "sophistication": round(sophistication, 2),
                    "session_id": session_idx + 1,
                    "synthesized": True,
                },
            }

            history.append(entry)
            entry_id += 1

    return history


def save_query_history(domain: str, history: List[Dict[str, Any]], base_path: Path):
    """Save query history to compressed JSON file."""

    domain_path = base_path / domain
    domain_path.mkdir(parents=True, exist_ok=True)

    history_file = domain_path / "query_history.json.gz"

    with gzip.open(history_file, "wt", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"  ✓ Saved {len(history)} entries to {history_file}")


def synthesize_candidate(
    candidate_name: str,
    domains: List[str],
    base_path: Path,
    learning_profile: str = "average",
):
    """
    Synthesize a complete candidate with query history in all domains.

    Args:
        candidate_name: Candidate name (e.g., "Test Engineer")
        domains: List of domain IDs
        base_path: Base path for universe domains
        learning_profile: "slow", "average", or "fast"
    """

    # Learning velocity by profile
    profiles = {
        "slow": 0.20,
        "average": 0.35,
        "fast": 0.50,
    }
    learning_velocity = profiles[learning_profile]

    print(f"Synthesizing candidate: {candidate_name}")
    print(f"  Profile: {learning_profile} (velocity: {learning_velocity} levels/day)")
    print(f"  Domains: {', '.join(domains)}")
    print()

    for domain in domains:
        if domain not in DOMAIN_QUESTIONS:
            print(f"  ✗ Unknown domain: {domain}")
            continue

        # Generate history
        history = generate_query_history(
            domain=domain,
            num_sessions=random.randint(6, 10),
            days=10,
            learning_velocity=learning_velocity,
        )

        # Save to file
        save_query_history(domain, history, base_path)

    print()
    print(f"✓ Candidate synthesized: {candidate_name}")
    print(f"  Total queries: {sum(len(generate_query_history(d, 8, 10, learning_velocity)) for d in domains)}")
    print(f"  Assessment period: 10 days")
    print()
    print("Next steps:")
    print(f"  1. Create candidate in BrainUse dashboard")
    print(f"  2. Use name: {candidate_name}")
    print(f"  3. Select domains: {', '.join(domains)}")
    print(f"  4. Start assessment")
    print(f"  5. Complete assessment → view report")


def main():
    parser = argparse.ArgumentParser(description="Synthesize test candidate data")
    parser.add_argument(
        "--candidate-name",
        default="Test Engineer",
        help="Candidate name (default: Test Engineer)"
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        default=["cloud_assessment", "leadership_assessment", "api_assessment"],
        help="Assessment domains (default: cloud, leadership, api)"
    )
    parser.add_argument(
        "--profile",
        choices=["slow", "average", "fast"],
        default="average",
        help="Learning profile (default: average)"
    )
    parser.add_argument(
        "--universe-path",
        default="universes/MINE/domains",
        help="Path to universe domains (default: universes/MINE/domains)"
    )

    args = parser.parse_args()

    # Get base path
    script_dir = Path(__file__).parent.parent
    base_path = script_dir / args.universe_path

    # Synthesize candidate
    synthesize_candidate(
        candidate_name=args.candidate_name,
        domains=args.domains,
        base_path=base_path,
        learning_profile=args.profile,
    )


if __name__ == "__main__":
    main()
