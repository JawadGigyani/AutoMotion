"""
AutoMotion — API Routes
REST endpoints for video generation, status polling, and results.
"""
import uuid
import asyncio
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from agents.pipeline import run_pipeline
from api.websocket import send_progress_update

router = APIRouter()


# ── In-memory job store ──
jobs: dict[str, dict] = {}


# ── Request / Response models ──

class GenerateRequest(BaseModel):
    repo_url: str


class GenerateResponse(BaseModel):
    job_id: str
    message: str


class StatusResponse(BaseModel):
    status: str
    step: Optional[str] = None
    progress: int = 0
    message: Optional[str] = None
    video_url: Optional[str] = None
    error: Optional[str] = None


class ResultResponse(BaseModel):
    video_url: str
    repo_url: str
    theme: Optional[str] = None


# ── Background pipeline execution ──

async def _run_pipeline_task(job_id: str, repo_url: str):
    """Run the LangGraph pipeline in the background with progress tracking."""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["step"] = "starting"

        # Progress callback for WebSocket updates
        async def on_progress(data: dict):
            jobs[job_id]["step"] = data.get("step", "")
            jobs[job_id]["progress"] = data.get("progress", 0)
            jobs[job_id]["message"] = data.get("message", "")
            # Also push via WebSocket
            await send_progress_update(job_id, data)

        result = await run_pipeline(
            job_id=job_id,
            repo_url=repo_url,
            progress_callback=on_progress,
        )

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["video_url"] = f"/outputs/{job_id}/video.mp4"
        jobs[job_id]["theme"] = result.get("theme", {}).get("name", "")

        # Send final WebSocket update
        await send_progress_update(job_id, {
            "step": "complete",
            "progress": 100,
            "message": "Video ready!",
            "status": "completed",
            "video_url": f"/outputs/{job_id}/video.mp4",
        })

    except Exception as e:
        print(f"[ERROR] Pipeline failed for job {job_id[:8]}: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

        await send_progress_update(job_id, {
            "step": "error",
            "progress": 0,
            "message": str(e),
            "status": "failed",
        })


# ── Endpoints ──

@router.post("/generate", response_model=GenerateResponse)
async def generate_video(request: GenerateRequest):
    """Start video generation. Returns a job ID for polling or WebSocket."""
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "pending",
        "step": None,
        "progress": 0,
        "message": None,
        "video_url": None,
        "error": None,
        "repo_url": request.repo_url,
        "theme": None,
    }

    # Run pipeline in background
    asyncio.create_task(_run_pipeline_task(job_id, request.repo_url))

    print(f"\n[NEW] Job created: {job_id[:8]}... ({request.repo_url})")

    return GenerateResponse(
        job_id=job_id,
        message="Video generation started",
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Poll for job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return StatusResponse(
        status=job["status"],
        step=job.get("step"),
        progress=job.get("progress", 0),
        message=job.get("message"),
        video_url=job.get("video_url"),
        error=job.get("error"),
    )


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str):
    """Get the final result of a completed job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job is not complete: {job['status']}")

    return ResultResponse(
        video_url=job["video_url"],
        repo_url=job["repo_url"],
        theme=job.get("theme"),
    )
