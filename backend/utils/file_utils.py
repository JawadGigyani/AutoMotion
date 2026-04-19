"""
AutoMotion — File Utilities
Temp directory management and cleanup.
"""
import shutil
import time
from pathlib import Path

from config import OUTPUTS_DIR


def get_job_dir(job_id: str) -> Path:
    """Get or create the output directory for a specific job."""
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def cleanup_job(job_id: str) -> None:
    """Remove all files for a specific job."""
    job_dir = OUTPUTS_DIR / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)


def cleanup_old_jobs(max_age_seconds: int = 3600) -> int:
    """
    Remove job directories older than max_age_seconds.
    Returns the number of directories cleaned up.
    """
    cleaned = 0
    now = time.time()

    if not OUTPUTS_DIR.exists():
        return 0

    for job_dir in OUTPUTS_DIR.iterdir():
        if not job_dir.is_dir():
            continue

        # Check directory modification time
        try:
            dir_age = now - job_dir.stat().st_mtime
            if dir_age > max_age_seconds:
                shutil.rmtree(job_dir, ignore_errors=True)
                cleaned += 1
        except OSError:
            continue

    return cleaned
