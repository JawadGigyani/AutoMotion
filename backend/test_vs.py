import asyncio
from pathlib import Path
from services.voice_service import generate_per_scene_voiceovers
import traceback

scenes = [{"narration": "Test scene 1"}, {"narration": "Test scene 2"}]
job_dir = Path("outputs/test-job-dir")
try:
    generate_per_scene_voiceovers(scenes, job_dir=job_dir)
    print("SUCCESS")
except Exception as e:
    print("FAILED:")
    traceback.print_exc()
