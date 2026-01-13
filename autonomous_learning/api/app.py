"""
Autonomous Learning API - Main Application

FastAPI application with stub endpoints for Surveyor UI.
This is a placeholder until Phases 2-5 are implemented.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .surveys import router as surveys_router
from .supervisor import router as supervisor_router
from .certification import router as certification_router
from .scraping import router as scraping_router

# Create FastAPI app
app = FastAPI(
    title="EEFrame Autonomous Learning API",
    description="Autonomous pattern scraping, certification, and storage",
    version="0.1.0-stub"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(surveys_router)
app.include_router(supervisor_router)
app.include_router(certification_router)
app.include_router(scraping_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "EEFrame Autonomous Learning API",
        "version": "0.1.0-stub",
        "status": "Phase 6 stubs - full implementation in progress",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "phase": "6 (stubs)",
        "components": {
            "supervisor": "stub",
            "certification": "stub",
            "scraping": "stub",
            "ingestion": "stub",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
