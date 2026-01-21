"""
Pattern management routes for Generic Framework.

Provides CRUD operations for patterns across all domains.
Migrated from Expertise Scanner.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import json
from pathlib import Path

router = APIRouter(prefix="/patterns", tags=["patterns"])


class PatternCreate(BaseModel):
    """Pattern creation model."""
    domain: str
    name: str
    pattern_type: str
    description: str
    problem: str
    solution: str
    category: Optional[str] = None
    symptoms: List[str] = []
    triggers: List[str] = []
    diagnostics: List[Dict[str, Any]] = []
    solutions: List[Dict[str, Any]] = []
    related_patterns: List[str] = []
    prerequisites: List[str] = []
    alternatives: List[str] = []
    confidence: float = 0.5
    sources: List[str] = []
    tags: List[str] = []
    examples: List[str] = []
    code: Optional[str] = None  # Executable code associated with this pattern


class PatternUpdate(BaseModel):
    """Pattern update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    confidence: Optional[float] = None
    tags: Optional[List[str]] = None


class PatternResponse(BaseModel):
    """Pattern response model."""
    id: str
    domain: str
    name: str
    pattern_type: str
    description: str
    problem: str
    solution: str
    category: Optional[str]
    confidence: float
    tags: List[str]


# Pattern storage path
PATTERNS_DIR = Path("data/patterns")


def get_pattern_path(domain: str, pattern_id: str) -> Path:
    """Get path to pattern file."""
    return PATTERNS_DIR / domain / f"{pattern_id}.json"


def load_pattern(domain: str, pattern_id: str) -> Dict[str, Any]:
    """Load a pattern from disk."""
    path = get_pattern_path(domain, pattern_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")
    
    with open(path) as f:
        return json.load(f)


def save_pattern(domain: str, pattern_id: str, data: Dict[str, Any]) -> None:
    """Save a pattern to disk."""
    path = get_pattern_path(domain, pattern_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


@router.get("/", response_model=List[PatternResponse])
async def list_patterns(
    domain: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List all patterns, optionally filtered by domain and category."""
    patterns = []
    
    # Get all domains if not specified
    domains = [domain] if domain else list(PATTERNS_DIR.glob("*/"))
    
    for domain_dir in domains:
        if isinstance(domain_dir, str):
            domain_dir = PATTERNS_DIR / domain_dir
        
        if not domain_dir.is_dir():
            continue
        
        # Load all patterns in domain
        for pattern_file in domain_dir.glob("*.json"):
            try:
                with open(pattern_file) as f:
                    pattern = json.load(f)
                
                # Filter by category if specified
                if category and pattern.get("category") != category:
                    continue
                
                patterns.append(PatternResponse(**pattern))
            except Exception:
                continue
    
    # Apply pagination
    return patterns[offset:offset + limit]


@router.get("/search", response_model=List[PatternResponse])
async def search_patterns(
    q: str = Query(..., min_length=1),
    domain: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    """Search patterns by keywords."""
    results = []
    query_lower = q.lower()
    
    # Get all domains if not specified
    domains = [domain] if domain else list(PATTERNS_DIR.glob("*/"))
    
    for domain_dir in domains:
        if isinstance(domain_dir, str):
            domain_dir = PATTERNS_DIR / domain_dir
        
        if not domain_dir.is_dir():
            continue
        
        # Search in all patterns
        for pattern_file in domain_dir.glob("*.json"):
            try:
                with open(pattern_file) as f:
                    pattern = json.load(f)
                
                # Search in name, description, problem, solution, tags
                search_text = " ".join([
                    pattern.get("name", ""),
                    pattern.get("description", ""),
                    pattern.get("problem", ""),
                    pattern.get("solution", ""),
                    " ".join(pattern.get("tags", [])),
                    " ".join(pattern.get("triggers", [])),
                ]).lower()
                
                if query_lower in search_text:
                    results.append(PatternResponse(**pattern))
                    if len(results) >= limit:
                        return results
            except Exception:
                continue
    
    return results


@router.get("/{pattern_id}", response_model=Dict[str, Any])
async def get_pattern(
    pattern_id: str,
    domain: Optional[str] = Query(None),
):
    """Get a specific pattern."""
    # If domain not specified, search all domains
    if domain:
        return load_pattern(domain, pattern_id)
    
    # Search all domains
    for domain_dir in PATTERNS_DIR.glob("*/"):
        if domain_dir.is_dir():
            path = domain_dir / f"{pattern_id}.json"
            if path.exists():
                with open(path) as f:
                    return json.load(f)
    
    raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")


@router.post("/", response_model=Dict[str, Any])
async def create_pattern(pattern: PatternCreate):
    """Create a new pattern."""
    # Generate pattern ID
    domain_dir = PATTERNS_DIR / pattern.domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next ID
    existing = list(domain_dir.glob("*.json"))
    next_num = len(existing) + 1
    pattern_id = f"{pattern.domain}_{next_num:03d}"
    
    # Create pattern data
    pattern_data = {
        "id": pattern_id,
        **pattern.dict(),
    }
    
    # Save pattern
    save_pattern(pattern.domain, pattern_id, pattern_data)
    
    return pattern_data


@router.put("/{pattern_id}", response_model=Dict[str, Any])
async def update_pattern(
    pattern_id: str,
    update: PatternUpdate,
    domain: Optional[str] = Query(None),
):
    """Update a pattern."""
    # Load existing pattern
    if domain:
        pattern_data = load_pattern(domain, pattern_id)
    else:
        # Search all domains
        pattern_data = None
        for domain_dir in PATTERNS_DIR.glob("*/"):
            if domain_dir.is_dir():
                path = domain_dir / f"{pattern_id}.json"
                if path.exists():
                    with open(path) as f:
                        pattern_data = json.load(f)
                    domain = domain_dir.name
                    break
        
        if not pattern_data:
            raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")
    
    # Update fields
    for field, value in update.dict(exclude_unset=True).items():
        pattern_data[field] = value
    
    # Save updated pattern
    save_pattern(domain, pattern_id, pattern_data)
    
    return pattern_data


@router.delete("/{pattern_id}")
async def delete_pattern(
    pattern_id: str,
    domain: Optional[str] = Query(None),
):
    """Delete a pattern."""
    # Find and delete pattern
    if domain:
        path = get_pattern_path(domain, pattern_id)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")
        path.unlink()
    else:
        # Search all domains
        found = False
        for domain_dir in PATTERNS_DIR.glob("*/"):
            if domain_dir.is_dir():
                path = domain_dir / f"{pattern_id}.json"
                if path.exists():
                    path.unlink()
                    found = True
                    break
        
        if not found:
            raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")
    
    return {"status": "deleted", "pattern_id": pattern_id}
