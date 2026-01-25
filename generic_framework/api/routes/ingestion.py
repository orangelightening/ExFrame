#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Pattern ingestion routes for Generic Framework.

Provides endpoints for ingesting patterns from various sources:
- URLs (web scraping)
- Text (manual input)
- JSON (structured data)
- Batch (multiple files)

Migrated from Expertise Scanner.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import json
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class UrlIngestionRequest(BaseModel):
    """Request to ingest pattern from URL."""
    url: str
    domain: str
    extract_method: str = "llm"  # "llm" or "rule-based"


class TextIngestionRequest(BaseModel):
    """Request to ingest pattern from text."""
    text: str
    domain: str
    pattern_type: str = "procedure"


class JsonIngestionRequest(BaseModel):
    """Request to ingest pattern from JSON."""
    data: Dict[str, Any]
    domain: str


class BatchIngestionRequest(BaseModel):
    """Request for batch ingestion."""
    files: List[Dict[str, Any]]
    domain: str


class IngestionStatus(BaseModel):
    """Ingestion status response."""
    status: str  # "pending", "processing", "completed", "failed"
    total: int
    processed: int
    failed: int
    errors: List[str] = []


# Ingestion status tracking
ingestion_jobs: Dict[str, IngestionStatus] = {}


@router.post("/url", response_model=Dict[str, Any])
async def ingest_from_url(
    request: UrlIngestionRequest,
    background_tasks: BackgroundTasks,
):
    """Ingest pattern from URL."""
    try:
        # For now, return a placeholder
        # In full implementation, would scrape URL and extract pattern
        return {
            "status": "queued",
            "url": request.url,
            "domain": request.domain,
            "message": "URL ingestion queued for processing",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/text", response_model=Dict[str, Any])
async def ingest_from_text(request: TextIngestionRequest):
    """Ingest pattern from text."""
    try:
        # Parse text and create pattern
        # In full implementation, would use LLM to extract structure
        pattern_data = {
            "id": f"{request.domain}_{datetime.now().timestamp()}",
            "domain": request.domain,
            "name": "Ingested Pattern",
            "pattern_type": request.pattern_type,
            "description": request.text[:100],
            "problem": request.text,
            "solution": "See description",
            "confidence": 0.5,
            "tags": [request.domain],
        }
        
        # Save pattern
        patterns_dir = Path("data/patterns") / request.domain
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        pattern_file = patterns_dir / f"{pattern_data['id']}.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern_data, f, indent=2)
        
        return {
            "status": "created",
            "pattern_id": pattern_data["id"],
            "domain": request.domain,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/json", response_model=Dict[str, Any])
async def ingest_from_json(request: JsonIngestionRequest):
    """Ingest pattern from JSON."""
    try:
        # Validate and save pattern
        pattern_data = request.data
        
        # Ensure required fields
        if "id" not in pattern_data:
            pattern_data["id"] = f"{request.domain}_{datetime.now().timestamp()}"
        
        pattern_data["domain"] = request.domain
        
        # Save pattern
        patterns_dir = Path("data/patterns") / request.domain
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        pattern_file = patterns_dir / f"{pattern_data['id']}.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern_data, f, indent=2)
        
        return {
            "status": "created",
            "pattern_id": pattern_data["id"],
            "domain": request.domain,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=Dict[str, Any])
async def ingest_batch(
    request: BatchIngestionRequest,
    background_tasks: BackgroundTasks,
):
    """Ingest multiple patterns in batch."""
    try:
        job_id = f"batch_{datetime.now().timestamp()}"
        
        # Initialize job status
        ingestion_jobs[job_id] = IngestionStatus(
            status="processing",
            total=len(request.files),
            processed=0,
            failed=0,
        )
        
        # Process batch in background
        background_tasks.add_task(
            process_batch,
            job_id,
            request.files,
            request.domain,
        )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "total": len(request.files),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def process_batch(job_id: str, files: List[Dict[str, Any]], domain: str):
    """Process batch ingestion in background."""
    job = ingestion_jobs[job_id]
    patterns_dir = Path("data/patterns") / domain
    patterns_dir.mkdir(parents=True, exist_ok=True)
    
    for file_data in files:
        try:
            # Ensure required fields
            if "id" not in file_data:
                file_data["id"] = f"{domain}_{datetime.now().timestamp()}"
            
            file_data["domain"] = domain
            
            # Save pattern
            pattern_file = patterns_dir / f"{file_data['id']}.json"
            with open(pattern_file, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            job.processed += 1
        except Exception as e:
            job.failed += 1
            job.errors.append(str(e))
    
    job.status = "completed"


@router.get("/status/{job_id}", response_model=IngestionStatus)
async def get_ingestion_status(job_id: str):
    """Get status of an ingestion job."""
    if job_id not in ingestion_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return ingestion_jobs[job_id]


@router.get("/inbox", response_model=List[Dict[str, Any]])
async def list_inbox_files():
    """List files in AI inbox directory."""
    inbox_dir = Path("pattern-inbox")
    
    if not inbox_dir.exists():
        return []
    
    files = []
    for file_path in inbox_dir.glob("*.json"):
        try:
            with open(file_path) as f:
                data = json.load(f)
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "data": data,
            })
        except Exception:
            continue
    
    return files


@router.post("/inbox/process", response_model=Dict[str, Any])
async def process_inbox(
    domain: str,
    background_tasks: BackgroundTasks,
):
    """Process all files in AI inbox."""
    try:
        inbox_dir = Path("pattern-inbox")
        
        if not inbox_dir.exists():
            raise HTTPException(status_code=404, detail="Inbox directory not found")
        
        # Get all JSON files
        files = list(inbox_dir.glob("*.json"))
        
        if not files:
            return {
                "status": "completed",
                "processed": 0,
                "message": "No files in inbox",
            }
        
        # Process in background
        job_id = f"inbox_{datetime.now().timestamp()}"
        background_tasks.add_task(
            process_inbox_files,
            job_id,
            files,
            domain,
        )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "total": len(files),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def process_inbox_files(job_id: str, files: List[Path], domain: str):
    """Process inbox files in background."""
    job = IngestionStatus(
        status="processing",
        total=len(files),
        processed=0,
        failed=0,
    )
    ingestion_jobs[job_id] = job
    
    patterns_dir = Path("data/patterns") / domain
    patterns_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files:
        try:
            with open(file_path) as f:
                pattern_data = json.load(f)
            
            # Ensure required fields
            if "id" not in pattern_data:
                pattern_data["id"] = f"{domain}_{file_path.stem}"
            
            pattern_data["domain"] = domain
            
            # Save pattern
            pattern_file = patterns_dir / f"{pattern_data['id']}.json"
            with open(pattern_file, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            
            # Move processed file to archive
            archive_dir = Path("pattern-inbox/processed")
            archive_dir.mkdir(exist_ok=True)
            file_path.rename(archive_dir / file_path.name)
            
            job.processed += 1
        except Exception as e:
            job.failed += 1
            job.errors.append(str(e))
    
    job.status = "completed"
