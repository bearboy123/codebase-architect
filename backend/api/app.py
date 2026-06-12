"""
FastAPI application and route definitions.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import tempfile
import shutil
from pathlib import Path
import uuid

from backend.config.settings import settings
from backend.config.semantic_kernel_config import get_kernel
from backend.analyzers.code_indexer import CodeIndexer
from backend.orchestrator.agent_orchestrator import AgentOrchestrator

# Initialize FastAPI app
app = FastAPI(
    title="Codebase Architect Agent",
    description="Multi-agent platform for codebase analysis",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (in production, use a database)
analysis_jobs: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class AnalysisRequest(BaseModel):
    """Request model for code analysis."""
    repo_url: Optional[str] = None
    repo_path: Optional[str] = None


class AnalysisStatus(BaseModel):
    """Status of an analysis job."""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    message: str


class AnalysisResponse(BaseModel):
    """Response with analysis results."""
    job_id: str
    status: str
    results: Optional[Dict[str, Any]] = None


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Codebase Architect Agent",
        "version": "0.1.0"
    }


@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks) -> AnalysisResponse:
    """
    Start a new codebase analysis job.
    
    Args:
        request: AnalysisRequest with repo_url or repo_path
        background_tasks: FastAPI background tasks for async execution
        
    Returns:
        AnalysisResponse with job ID
    """
    # Validate input
    if not request.repo_url and not request.repo_path:
        raise HTTPException(
            status_code=400,
            detail="Either repo_url or repo_path must be provided"
        )

    # Create job ID
    job_id = str(uuid.uuid4())

    # Initialize job
    analysis_jobs[job_id] = {
        'status': 'pending',
        'progress': 0,
        'repo_path': request.repo_path,
        'repo_url': request.repo_url,
        'results': None,
        'error': None
    }

    # Run analysis in background
    background_tasks.add_task(
        _run_analysis,
        job_id=job_id,
        repo_path=request.repo_path,
        repo_url=request.repo_url
    )

    return AnalysisResponse(
        job_id=job_id,
        status="pending",
        results=None
    )


@app.get("/api/analysis/{job_id}")
async def get_analysis_results(job_id: str) -> Dict[str, Any]:
    """
    Get analysis results for a job.
    
    Args:
        job_id: Job ID from start_analysis
        
    Returns:
        Analysis results
    """
    if job_id not in analysis_jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    job = analysis_jobs[job_id]

    response = {
        "job_id": job_id,
        "status": job['status'],
        "progress": job['progress'],
    }

    if job['status'] == 'completed':
        response['results'] = job['results']
    elif job['status'] == 'failed':
        response['error'] = job['error']

    return response


@app.get("/api/analysis/{job_id}/status")
async def get_analysis_status(job_id: str) -> AnalysisStatus:
    """
    Get status of an analysis job.
    
    Args:
        job_id: Job ID
        
    Returns:
        AnalysisStatus
    """
    if job_id not in analysis_jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    job = analysis_jobs[job_id]

    status_messages = {
        'pending': 'Analysis job is queued',
        'running': f'Analysis in progress... {job["progress"]}%',
        'completed': 'Analysis completed successfully',
        'failed': f'Analysis failed: {job.get("error", "Unknown error")}'
    }

    return AnalysisStatus(
        job_id=job_id,
        status=job['status'],
        progress=job['progress'],
        message=status_messages.get(job['status'], 'Unknown status')
    )


@app.post("/api/analyze/upload")
async def analyze_uploaded_repo(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
) -> AnalysisResponse:
    """
    Upload a zipped repository and analyze it.
    
    Args:
        file: Zipped repository file
        background_tasks: FastAPI background tasks
        
    Returns:
        AnalysisResponse with job ID
    """
    job_id = str(uuid.uuid4())

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Save uploaded file
        temp_file = Path(temp_dir) / file.filename
        with open(temp_file, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Initialize job
        analysis_jobs[job_id] = {
            'status': 'pending',
            'progress': 0,
            'repo_path': str(temp_dir),
            'repo_url': None,
            'results': None,
            'error': None,
            'temp_dir': temp_dir
        }

        # Run analysis
        background_tasks.add_task(
            _run_analysis,
            job_id=job_id,
            repo_path=str(temp_dir),
            repo_url=None
        )

        return AnalysisResponse(
            job_id=job_id,
            status="pending"
        )

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process uploaded file: {str(e)}"
        )


# Background task
async def _run_analysis(job_id: str, repo_path: Optional[str], repo_url: Optional[str]) -> None:
    """
    Run the actual analysis in background.
    
    Args:
        job_id: Job ID
        repo_path: Path to repository
        repo_url: URL of repository (clone it first)
    """
    try:
        job = analysis_jobs[job_id]
        job['status'] = 'running'
        job['progress'] = 10

        # If URL provided, clone the repo
        if repo_url and not repo_path:
            import subprocess
            temp_dir = tempfile.mkdtemp()
            try:
                subprocess.run(
                    ["git", "clone", repo_url, temp_dir],
                    check=True,
                    capture_output=True,
                    timeout=60
                )
                repo_path = temp_dir
                job['temp_dir'] = temp_dir
            except Exception as e:
                job['status'] = 'failed'
                job['error'] = f"Failed to clone repository: {str(e)}"
                return

        if not repo_path:
            job['status'] = 'failed'
            job['error'] = "No valid repository path"
            return

        job['progress'] = 30

        # Index the repository
        try:
            indexer = CodeIndexer(repo_path, max_file_size_mb=settings.max_file_size_mb)
            indexer.index()
        except Exception as e:
            job['status'] = 'failed'
            job['error'] = f"Failed to index repository: {str(e)}"
            return

        job['progress'] = 50

        # Create kernel and orchestrator
        kernel = get_kernel()
        orchestrator = AgentOrchestrator(kernel, indexer)

        job['progress'] = 60

        # Run analysis
        try:
            results = await orchestrator.analyze()
            job['results'] = results
            job['status'] = 'completed'
            job['progress'] = 100
        except Exception as e:
            job['status'] = 'failed'
            job['error'] = f"Analysis failed: {str(e)}"

    except Exception as e:
        job = analysis_jobs.get(job_id)
        if job:
            job['status'] = 'failed'
            job['error'] = f"Unexpected error: {str(e)}"

    finally:
        # Cleanup temporary directories
        job = analysis_jobs.get(job_id)
        if job and 'temp_dir' in job:
            try:
                shutil.rmtree(job['temp_dir'], ignore_errors=True)
            except Exception:
                pass


@app.get("/api/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """Get system metrics and statistics."""
    completed_jobs = sum(1 for j in analysis_jobs.values() if j['status'] == 'completed')
    failed_jobs = sum(1 for j in analysis_jobs.values() if j['status'] == 'failed')
    running_jobs = sum(1 for j in analysis_jobs.values() if j['status'] == 'running')

    return {
        'total_jobs': len(analysis_jobs),
        'completed': completed_jobs,
        'failed': failed_jobs,
        'running': running_jobs,
        'pending': len(analysis_jobs) - completed_jobs - failed_jobs - running_jobs
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("Starting Codebase Architect Agent...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down Codebase Architect Agent...")
    # Cleanup temporary directories
    for job in analysis_jobs.values():
        if 'temp_dir' in job:
            try:
                shutil.rmtree(job['temp_dir'], ignore_errors=True)
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        debug=settings.debug
    )
