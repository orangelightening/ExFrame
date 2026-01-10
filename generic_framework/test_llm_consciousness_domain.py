"""
Test script for llm_consciousness domain integration
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.domain import DomainConfig
from domains.llm_consciousness import LlConsciousnessDomain
from assist.engine import GenericAssistantEngine


async def test_llm_consciousness_domain():
    """Test the llm_consciousness domain."""
    print("=" * 60)
    print("Testing LLM Consciousness Domain")
    print("=" * 60)

    # Create domain config
    config = DomainConfig(
        domain_id="llm_consciousness",
        domain_name="LLM Consciousness & Failure Modes",
        version="1.0.0",
        description="Patterns of LLM consciousness lapses, failure modes in autonomous operation, and mitigation strategies",
        pattern_storage_path="/home/peter/development/eeframe/data/patterns/llm_consciousness",
        pattern_format="json",
        categories=["failure_mode", "solution", "monitoring", "architecture", "detection", "recovery", "prevention"],
        tags=["hallucination", "tool_failure", "loops", "amnesia", "confidence", "quality_drift", "monitoring", "orchestration", "llm", "autonomous_agents"]
    )

    # Create and initialize domain
    print("\n1. Creating domain...")
    domain = LlConsciousnessDomain(config)

    print("2. Initializing domain...")
    await domain.initialize()

    # Check health
    print("3. Checking domain health...")
    health = await domain.health_check()
    print(f"   Domain: {health['domain']}")
    print(f"   Status: {health['status']}")
    print(f"   Patterns loaded: {health['patterns_loaded']}")
    print(f"   Specialists available: {health['specialists_available']}")
    print(f"   Categories: {health['categories']}")

    # List specialists
    print("\n4. Available specialists:")
    for spec_id in domain.list_specialists():
        specialist = domain.get_specialist(spec_id)
        print(f"   - {specialist.name}: {specialist.config.description}")

    # Create engine and test queries
    print("\n5. Creating assistant engine...")
    engine = GenericAssistantEngine(domain)
    await engine.initialize()

    # Test queries
    test_queries = [
        "How do I detect when an LLM is hallucinating?",
        "What are the common failure modes in autonomous agents?",
        "How can I monitor for quality drift in LLM responses?",
        "What should I do when an agent gets stuck in a loop?"
    ]

    print("\n6. Testing queries:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        result = await engine.process_query(query, include_trace=True)

        specialist = domain.get_specialist_for_query(query)
        specialist_name = specialist.name if specialist else "None"

        print(f"   Response: {result['response'][:100]}...")
        print(f"   Specialist: {specialist_name}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Patterns used: {len(result['patterns_used'])}")

    # Cleanup
    print("\n7. Cleaning up...")
    await domain.cleanup()

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_llm_consciousness_domain())
