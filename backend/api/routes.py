"""
AutoMotion — API Routes
REST endpoints for video generation, status polling, and results.
"""

import asyncio
import time
import uuid
from typing import Optional

import httpx
from agents.pipeline import run_pipeline
from config import MAX_CONCURRENT_JOBS, REMOTION_RENDER_URL
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from utils.file_utils import cleanup_old_jobs

from api.websocket import send_progress_update

router = APIRouter()


# ── In-memory job store ──
# Each job also records its creation timestamp for TTL-based cleanup.
JOB_TTL_SECONDS = 45 * 60  # 45 minutes
CLEANUP_INTERVAL_SECONDS = 5 * 60  # Run cleanup every 5 minutes
jobs: dict[str, dict] = {}
_cleanup_task: asyncio.Task | None = None


async def _periodic_cleanup() -> None:
    """Background loop: purge expired jobs from memory and disk every 5 min."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
        try:
            now = time.time()
            expired_ids = [
                jid
                for jid, j in jobs.items()
                if now - j.get("created_at", now) > JOB_TTL_SECONDS
                and j.get("status") in ("completed", "failed")
            ]
            for jid in expired_ids:
                jobs.pop(jid, None)

            # Also clean up orphaned output directories on disk
            disk_cleaned = cleanup_old_jobs(max_age_seconds=JOB_TTL_SECONDS)

            if expired_ids or disk_cleaned:
                print(
                    f"[CLEANUP] Purged {len(expired_ids)} memory jobs, "
                    f"{disk_cleaned} disk directories"
                )
        except Exception as e:
            print(f"[CLEANUP] Error: {e}")


def start_cleanup_loop() -> None:
    """Start the periodic cleanup background task (call once at startup)."""
    global _cleanup_task
    if _cleanup_task is None:
        _cleanup_task = asyncio.create_task(_periodic_cleanup())
        print("[CLEANUP] Background cleanup started (TTL=45min, interval=5min)")


# ── Request / Response models ──


class GenerateRequest(BaseModel):
    repo_url: str
    theme_id: Optional[str] = None
    voice_id: Optional[str] = None


class GenerateResponse(BaseModel):
    job_id: str
    message: str


class StatusResponse(BaseModel):
    status: str
    step: Optional[str] = None
    progress: int = 0
    message: Optional[str] = None
    video_url: Optional[str] = None
    subtitle_url: Optional[str] = None
    error: Optional[str] = None


class ResultResponse(BaseModel):
    video_url: str
    repo_url: str
    theme: Optional[str] = None
    subtitle_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


# ── Background pipeline execution ──


async def _run_pipeline_task(
    job_id: str, repo_url: str, theme_id: str = None, voice_id: str = None, voice_style: str = None
):
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
            theme_id=theme_id,
            voice_id=voice_id,
            voice_style=voice_style,
        )

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["video_url"] = f"/outputs/{job_id}/video.mp4"
        jobs[job_id]["theme"] = result.get("theme", {}).get("name", "")

        # Subtitle URL (if SRT was generated)
        if result.get("subtitle_path"):
            jobs[job_id]["subtitle_url"] = f"/outputs/{job_id}/subtitles.vtt"

        # Thumbnail URL (if thumbnail was generated)
        if result.get("thumbnail_path"):
            jobs[job_id]["thumbnail_url"] = f"/outputs/{job_id}/thumbnail.png"

        await send_progress_update(
            job_id,
            {
                "step": "complete",
                "progress": 100,
                "message": "Video ready!",
                "status": "completed",
                "video_url": f"/outputs/{job_id}/video.mp4",
                "subtitle_url": jobs[job_id].get("subtitle_url"),
                "thumbnail_url": jobs[job_id].get("thumbnail_url"),
            },
        )

    except Exception as e:
        print(f"[ERROR] Pipeline failed for job {job_id[:8]}: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

        await send_progress_update(
            job_id,
            {
                "step": "error",
                "progress": 0,
                "message": str(e),
                "status": "failed",
            },
        )


# ── Endpoints ──


@router.post("/generate", response_model=GenerateResponse)
async def generate_video(request: GenerateRequest):
    """Start video generation. Returns a job ID for polling or WebSocket."""

    # ── Input validation ─────────────────────────────────────────────
    repo_url = (request.repo_url or "").strip()
    if not repo_url:
        raise HTTPException(status_code=400, detail="repo_url is required")

    # Basic sanity check — must look like a GitHub URL or owner/repo
    url_lower = repo_url.lower()
    is_github = (
        "github.com/" in url_lower or url_lower.count("/") == 1  # owner/repo shorthand
    )
    if not is_github:
        raise HTTPException(
            status_code=400,
            detail="Only public GitHub repository URLs are supported.",
        )

    # ── Rate limiting ────────────────────────────────────────────────
    active_jobs = sum(
        1 for j in jobs.values() if j.get("status") in ("pending", "processing")
    )
    if active_jobs >= MAX_CONCURRENT_JOBS:
        raise HTTPException(
            status_code=429,
            detail=f"Server is busy — {active_jobs} jobs are already running. "
            f"Please try again in a minute.",
        )

    # ── Create the job ───────────────────────────────────────────────
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "pending",
        "step": None,
        "progress": 0,
        "message": None,
        "video_url": None,
        "error": None,
        "repo_url": repo_url,
        "theme": None,
        "created_at": time.time(),
    }

    # Resolve voice style from selected voice ID
    voice_style = VOICE_STYLE_MAP.get(request.voice_id, None) if request.voice_id else None

    asyncio.create_task(
        _run_pipeline_task(
            job_id, repo_url,
            theme_id=request.theme_id,
            voice_id=request.voice_id,
            voice_style=voice_style,
        )
    )

    print(f"\n[NEW] Job created: {job_id[:8]}... ({repo_url})")

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
        subtitle_url=job.get("subtitle_url"),
        error=job.get("error"),
    )


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str):
    """Get the final result of a completed job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, detail=f"Job is not complete: {job['status']}"
        )

    return ResultResponse(
        video_url=job["video_url"],
        repo_url=job["repo_url"],
        theme=job.get("theme"),
        subtitle_url=job.get("subtitle_url"),
        thumbnail_url=job.get("thumbnail_url"),
    )


@router.get("/themes")
async def get_themes():
    """Return available video themes for the theme selector dropdown."""
    from services.theme_service import get_all_themes

    themes = get_all_themes()
    return [{"id": tid, "name": t["name"]} for tid, t in themes.items()]


# ── Curated voice list for the frontend selector ──
AVAILABLE_VOICES = [
    {"id": "CwhRBWXzGAHq8TQ4Fs17", "name": "Roger", "desc": "Male · American · Casual", "style": "casual"},
    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "desc": "Female · American · Professional", "style": "professional"},
    {"id": "IKne3meq5aSn9XLyUdCD", "name": "Charlie", "desc": "Male · Australian · Energetic", "style": "energetic"},
    {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "George", "desc": "Male · British · Storyteller", "style": "storytelling"},
    {"id": "FGY2WhTYpPnrIDTdsKH5", "name": "Laura", "desc": "Female · American · Enthusiastic", "style": "enthusiastic"},
]

VOICE_STYLE_MAP = {v["id"]: v["style"] for v in AVAILABLE_VOICES}


@router.get("/voices")
async def get_voices():
    """Return available voice options for the voice selector dropdown."""
    return AVAILABLE_VOICES


# ── Permanent sample entries ──
# Real renders stored in backend/samples/<Name>/ — never touched by cleanup.
SAMPLE_GALLERY = [
    {
        "job_id": "sample-storyweave",
        "repo_url": "https://github.com/JawadGigyani/StoryWeave",
        "theme": "Neon Cyberpunk",
        "video_url": "/samples/StoryWeave/video.mp4",
        "thumbnail_url": "/samples/StoryWeave/thumbnail.png",
        "subtitle_url": "/samples/StoryWeave/subtitles.vtt",
        "created_at": "2026-04-19T08:00:00Z",
        "is_sample": True,
    },
    {
        "job_id": "sample-flask",
        "repo_url": "https://github.com/pallets/flask",
        "theme": "Ocean Depth",
        "video_url": "/samples/Flask/video.mp4",
        "thumbnail_url": "/samples/Flask/thumbnail.png",
        "subtitle_url": "/samples/Flask/subtitles.vtt",
        "created_at": "2026-04-19T09:00:00Z",
        "is_sample": True,
    },
    {
        "job_id": "sample-langchain",
        "repo_url": "https://github.com/langchain-ai/langchain",
        "theme": "Dark Cinematic",
        "video_url": "/samples/LangChain/video.mp4",
        "thumbnail_url": "/samples/LangChain/thumbnail.png",
        "subtitle_url": "/samples/LangChain/subtitles.vtt",
        "created_at": "2026-04-19T10:00:00Z",
        "is_sample": True,
    },
]


@router.get("/gallery")
async def get_gallery():
    """Return permanent sample entries for the landing page."""
    return SAMPLE_GALLERY


@router.get("/render-health")
async def render_health():
    """Proxy health check to the internal Remotion render server."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{REMOTION_RENDER_URL}/health")
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Render server unreachable: {e}")
