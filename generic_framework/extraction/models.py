"""
Pattern Data Models

Defines the core data structures for representing expertise patterns
that can be extracted from any domain.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class PatternType(str, Enum):
    """Types of expertise patterns"""

    TROUBLESHOOTING = "troubleshooting"  # Diagnose and fix problems
    PROCEDURE = "procedure"  # Step-by-step process
    SUBSTITUTION = "substitution"  # Replace X with Y
    DECISION = "decision"  # Decision tree/branching
    DIAGNOSTIC = "diagnostic"  # Identify what's wrong
    PREPARATION = "preparation"  # Setup requirements
    OPTIMIZATION = "optimization"  # Improve performance
    PRINCIPLE = "principle"  # Fundamental rule/concept


class Pattern(BaseModel):
    """
    A reusable problem-solving pattern extracted from domain expertise.

    Cross-domain compatible - same structure works for OMV, Cooking,
    Python, DIY, First Aid, Gardening, etc.
    """

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str  # "omv", "cooking", "python", "diy", "first_aid", "gardening"
    name: str  # Short descriptive name
    pattern_type: PatternType

    # Core expertise
    description: str  # What this pattern does in 1-2 sentences
    problem: str  # What problem does this solve?
    solution: str  # How is it solved?
    steps: List[str] = []  # Procedural steps (if applicable)

    # Decision points (for branching patterns)
    conditions: Dict[str, str] = {}  # "if X then Y"

    # Relationships
    related_patterns: List[str] = []  # IDs of related patterns
    prerequisites: List[str] = []  # Must do these first
    alternatives: List[str] = []  # Other ways to solve this

    # Metadata
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)  # Reliability score
    sources: List[str] = []  # URLs, references
    tags: List[str] = []  # Free-form labels
    examples: List[str] = []  # Concrete examples

    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    times_accessed: int = 0
    user_rating: Optional[float] = None  # User feedback 0-1


class PatternMatch(BaseModel):
    """Result of pattern matching/similarity search"""

    pattern: Pattern
    similarity_score: float  # 0-1, how similar
    match_reason: str  # Why these matched


class PatternCluster(BaseModel):
    """A cluster of similar patterns across domains"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Abstract pattern name
    description: str  # What's the universal pattern?
    patterns: List[Pattern]  # Specific instances
    common_elements: List[str]  # What do they share?
    domain_specific: Dict[str, List[str]] = {}  # Domain-specific variations


class ExtractionResult(BaseModel):
    """Result of extracting patterns from a source"""

    source: str  # URL, file path, etc.
    domain: str
    patterns_found: int
    patterns: List[Pattern]
    confidence: float  # Overall confidence in extraction
    errors: List[str] = []


class CrossDomainMatch(BaseModel):
    """Patterns that match across different domains"""

    pattern1: Pattern  # From domain1
    pattern2: Pattern  # From domain2
    similarity: float  # 0-1
    shared_structure: List[str]  # What's similar?
    domain_variations: Dict[str, str] = {}  # How do they differ?


# Domain configuration
class DomainConfig(BaseModel):
    """Configuration for a domain"""

    name: str  # "cooking", "python", etc.
    display_name: str  # "Cooking Techniques"
    description: str
    sources: List[str] = []  # URLs to ingest
    patterns_count: int = 0
    last_updated: Optional[datetime] = None
    enabled: bool = True


# Existing OMV patterns can be migrated to this structure
def migrate_omv_pattern(omv_data: Dict[str, Any]) -> Pattern:
    """
    Convert existing OMV pattern to new Pattern structure.

    OMV patterns have: title, description, symptoms, causes, solutions, references
    """

    return Pattern(
        domain="omv",
        name=omv_data.get("title", "Unknown"),
        pattern_type=PatternType.TROUBLESHOOTING,
        description=omv_data.get("description", ""),
        problem=omv_data.get("symptoms", ""),
        solution=omv_data.get("solutions", ""),
        steps=omv_data.get("solutions", "").split("\n") if omv_data.get("solutions") else [],
        sources=omv_data.get("references", []),
        tags=["omv", "server", "administration"],
        confidence=0.8  # OMV patterns are manually curated
    )


if __name__ == "__main__":
    # Test creating a pattern
    pattern = Pattern(
        domain="cooking",
        name="Ingredient Substitution: Butter for Oil",
        pattern_type=PatternType.SUBSTITUTION,
        description="Replace butter with oil in baking recipes",
        problem="Recipe calls for butter but only have oil",
        solution="Use 3/4 cup of oil for every 1 cup of butter",
        steps=[
            "Measure the amount of butter needed",
            "Multiply by 0.75 to get oil amount",
            "Use oil in place of butter",
            "Note: texture may be slightly different"
        ],
        tags=["baking", "substitution", "ingredients"],
        confidence=0.9,
        examples=["Cookies: 1 cup butter → 3/4 cup oil"]
    )

    print("Pattern created:")
    print(pattern.model_dump_json(indent=2))
