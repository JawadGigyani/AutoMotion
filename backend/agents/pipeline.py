"""
AutoMotion — LangGraph Pipeline
Orchestrates the 7-stage video generation pipeline as a deterministic
sequential graph: parse → fetch → analyze → script → voice → frames → render.
"""

import asyncio
import math
from typing import Any, Callable, Optional

import httpx
from config import REMOTION_RENDER_URL, VIDEO_FPS
from langgraph.graph import END, START, StateGraph
from services.github_service import fetch_all_repo_data
from services.theme_service import select_theme
from services.voice_service import (
    generate_per_scene_voiceovers,
    generate_voiceover,
    get_audio_duration,
)
from utils.file_utils import get_job_dir
from utils.url_parser import parse_github_url

from agents.repo_analyzer import analyze_repo
from agents.script_director import write_script_and_scenes
from agents.state import PipelineState

# ═══════════════════════════════════════════════════════════════
# PIPELINE NODE FUNCTIONS
# Each node reads from state, does work, returns updates.
# ═══════════════════════════════════════════════════════════════

# ── Global progress callback registry ──
_progress_callbacks: dict[str, Callable] = {}


def register_progress_callback(job_id: str, callback: Callable) -> None:
    """Register a callback for real-time progress updates."""
    _progress_callbacks[job_id] = callback


def unregister_progress_callback(job_id: str) -> None:
    """Remove a progress callback."""
    _progress_callbacks.pop(job_id, None)


async def _report_progress(job_id: str, step: str, progress: int, message: str) -> None:
    """Send progress update via registered callback."""
    callback = _progress_callbacks.get(job_id)
    if callback:
        try:
            await callback(
                {
                    "step": step,
                    "progress": progress,
                    "message": message,
                    "status": "in_progress",
                }
            )
        except Exception:
            pass  # Don't let progress reporting crash the pipeline


# ── Node 1: Parse URL ──
async def parse_url(state: PipelineState) -> dict[str, Any]:
    """Validate and parse the GitHub URL."""
    print("\n[STAGE 1] Parsing URL...")
    job_id = state.get("job_id", "")

    await _report_progress(job_id, "parse_url", 5, "Parsing GitHub URL...")

    repo_url = state.get("repo_url", "")
    parsed = parse_github_url(repo_url)

    if parsed is None:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")

    owner, repo = parsed
    print(f"  [URL] Parsed: {owner}/{repo}")

    return {
        "owner": owner,
        "repo": repo,
        "current_step": "parse_url",
        "progress": 10,
    }


# ── Node 2: Fetch GitHub Data ──
async def fetch_github_data(state: PipelineState) -> dict[str, Any]:
    """Fetch all repository data from GitHub API."""
    print("\n[STAGE 2] Fetching GitHub data...")
    job_id = state.get("job_id", "")

    await _report_progress(
        job_id, "fetch_github_data", 15, "Fetching repository data from GitHub..."
    )

    owner = state["owner"]
    repo = state["repo"]

    repo_data = await fetch_all_repo_data(owner, repo)

    metadata = repo_data["metadata"]
    print(f"  [GITHUB] {metadata['full_name']}: {metadata['stars']} stars")
    print(f"  [GITHUB] Languages: {list(repo_data['languages'].keys())[:5]}")
    print(f"  [GITHUB] Key files: {list(repo_data['key_files'].keys())[:5]}")
    print(f"  [GITHUB] Tree items: {len(repo_data['tree'])}")
    print(f"  [GITHUB] README: {len(repo_data['readme'])} chars")

    return {
        "readme": repo_data["readme"],
        "description": metadata["description"],
        "stars": metadata["stars"],
        "forks": metadata["forks"],
        "language": metadata["language"],
        "topics": metadata["topics"],
        "languages": repo_data["languages"],
        "tree": repo_data["tree"],
        "key_files": repo_data["key_files"],
        "default_branch": metadata["default_branch"],
        "license": metadata["license"],
        "open_issues": metadata["open_issues"],
        "current_step": "fetch_github_data",
        "progress": 25,
    }


# ── Node 3: Analyze Repo (Agent #1) ──
# Defined in agents/repo_analyzer.py → analyze_repo()
# Wrapped here to add progress reporting
async def analyze_repo_node(state: PipelineState) -> dict[str, Any]:
    """Wrapper for Agent #1 with progress reporting."""
    job_id = state.get("job_id", "")
    await _report_progress(
        job_id, "analyze_repo", 30, "AI is analyzing the codebase..."
    )

    result = await analyze_repo(state)

    await _report_progress(job_id, "analyze_repo", 40, "Code analysis complete!")
    return result


# ── Node 4: Write Script + Direct Scenes (Agent #2, merged) ──
# Defined in agents/script_director.py → write_script_and_scenes()
async def write_script_node(state: PipelineState) -> dict[str, Any]:
    """Wrapper for Agent #2 with progress reporting."""
    job_id = state.get("job_id", "")
    await _report_progress(
        job_id, "write_script", 45, "AI is writing the narration script..."
    )

    result = await write_script_and_scenes(state)

    await _report_progress(job_id, "write_script", 55, "Script and scenes ready!")
    return result


# ── Node 5: Generate Voice ──
async def generate_voice(state: PipelineState) -> dict[str, Any]:
    """Generate per-scene TTS audio clips and concatenate into a single track.

    Uses generate_per_scene_voiceovers() so every scene's clip has a
    precisely-measured duration (via ffprobe after silence trimming).
    Those durations are stored in state["scene_audio_durations"] and used
    by calculate_frames to set exact durationInFrames per scene — the only
    reliable way to keep visuals and narration in sync.
    """
    print("\n[STAGE 5] Generating voiceover (per-scene)...")
    job_id = state.get("job_id", "")

    await _report_progress(
        job_id, "generate_voice", 58, "Generating voiceover with ElevenLabs..."
    )

    script = state.get("script", {})
    scenes = script.get("scenes", [])

    if not scenes:
        raise ValueError("No scenes found to generate voice from")

    job_dir = get_job_dir(job_id)

    try:
        # ── Primary: per-scene clips → exact durations ──────────────────
        audio_path, scene_audio_durations = generate_per_scene_voiceovers(
            scenes, job_dir
        )
        audio_duration = sum(scene_audio_durations)

        await _report_progress(
            job_id,
            "generate_voice",
            68,
            f"Voice ready — {len(scenes)} clips, {audio_duration:.1f}s total",
        )

        return {
            "audio_path": audio_path,
            "audio_duration": audio_duration,
            "scene_audio_durations": scene_audio_durations,
            "current_step": "generate_voice",
            "progress": 70,
        }

    except Exception as e:
        # ── Fallback: single combined call (no per-scene durations) ─────
        print(
            f"  [VOICE] Per-scene generation failed ({e}), falling back to single call..."
        )

        narration_parts = [s["narration"] for s in scenes if s.get("narration")]
        full_narration = ". ".join(narration_parts)

        if not full_narration.strip():
            raise ValueError("No narration text to generate voice from")

        audio_path_str = str(job_dir / "voice.mp3")
        audio_path_str = generate_voiceover(full_narration, audio_path_str)
        audio_duration = get_audio_duration(audio_path_str)

        await _report_progress(
            job_id,
            "generate_voice",
            68,
            f"Voice generated (fallback mode) — {audio_duration:.1f}s",
        )

        return {
            "audio_path": audio_path_str,
            "audio_duration": audio_duration,
            "scene_audio_durations": [],  # empty → calculate_frames uses word-count fallback
            "current_step": "generate_voice",
            "progress": 70,
        }


# ── Node 6: Calculate Frames + Scene Timing ──

# Must match transitionDuration in remotion/src/RepoReelVideo.tsx
REMOTION_TRANSITION_FRAMES = 12


async def calculate_frames(state: PipelineState) -> dict[str, Any]:
    """Set exact durationInFrames per scene, compensating for TransitionSeries overlap.

    Strategy A — Per-scene audio durations (primary, used when available)
    ─────────────────────────────────────────────────────────────────────
    When generate_voice succeeds with per-scene clips, each scene's exact
    spoken duration in seconds is known.  We convert that to frames and add
    REMOTION_TRANSITION_FRAMES to every scene except the last, so that after
    TransitionSeries subtracts those frames for crossfades the remaining
    content plays for exactly the correct number of audio frames:

        TransitionSeries duration
          = Σ(scene_frames) − (N−1) × TRANSITION
          = Σ(audio_frames_i + TRANSITION) − TRANSITION_for_last − (N−1)×TRANSITION
          = Σ(audio_frames_i)
          ≈ total_audio_frames  ✓

    Strategy B — Word-count proportional fallback
    ─────────────────────────────────────────────
    Used when scene_audio_durations is absent (single-call fallback path).
    Distributes (audio_frames + overlap_budget) proportionally across scenes.
    Less accurate but acceptable when per-scene data is unavailable.
    """
    print("\n[STAGE 6] Calculating frame timing...")
    job_id = state.get("job_id", "")

    await _report_progress(
        job_id, "calculate_frames", 72, "Calculating scene timing..."
    )

    audio_duration = state["audio_duration"]
    fps = VIDEO_FPS
    audio_frames = math.ceil(audio_duration * fps)

    script = state.get("script", {})
    scenes = script.get("scenes", [])
    scene_audio_durations: list[float] = state.get("scene_audio_durations", [])

    n_transitions = max(0, len(scenes) - 1)
    timed_scenes = []
    current_frame = 0

    # ── Strategy A: per-scene exact durations ────────────────────────────
    if scene_audio_durations and len(scene_audio_durations) == len(scenes):
        print(
            f"  [FRAMES] Strategy A — exact per-scene durations "
            f"({len(scenes)} scenes, {audio_duration:.2f}s total)"
        )

        for i, (scene, scene_dur) in enumerate(zip(scenes, scene_audio_durations)):
            scene_audio_frames = round(scene_dur * fps)

            # Add transition padding to every scene except the last so that
            # TransitionSeries subtracts it back out and the visual duration
            # matches the spoken duration exactly.
            if i < len(scenes) - 1:
                duration_frames = scene_audio_frames + REMOTION_TRANSITION_FRAMES
            else:
                duration_frames = scene_audio_frames

            duration_frames = max(30, duration_frames)  # enforce ≥ 1 s minimum

            timed_scene = {
                **scene,
                "start": current_frame,
                "durationInFrames": duration_frames,
            }
            timed_scenes.append(timed_scene)

            print(
                f"    Scene {i + 1:02d} [{scene.get('visual_type', '?'):15s}]: "
                f"{scene_dur:.2f}s audio → {duration_frames} frames"
                + (" (+transition pad)" if i < len(scenes) - 1 else " (last)")
            )

            current_frame += duration_frames

    # ── Strategy B: word-count proportional fallback ──────────────────────
    else:
        transition_padding = n_transitions * REMOTION_TRANSITION_FRAMES
        distribution_frames = audio_frames + transition_padding

        print(
            f"  [FRAMES] Strategy B — word-count proportional fallback "
            f"({audio_frames} audio frames + {transition_padding} transition padding "
            f"= {distribution_frames} to distribute)"
        )

        word_counts = [len(scene.get("narration", "").split()) for scene in scenes]
        total_words = sum(word_counts) or 1
        frames_remaining = distribution_frames

        for i, scene in enumerate(scenes):
            if i == len(scenes) - 1:
                duration_frames = frames_remaining
            else:
                proportion = word_counts[i] / total_words
                duration_frames = max(30, round(distribution_frames * proportion))
                duration_frames = min(duration_frames, frames_remaining)

            timed_scene = {
                **scene,
                "start": current_frame,
                "durationInFrames": duration_frames,
            }
            timed_scenes.append(timed_scene)

            print(
                f"    Scene {i + 1:02d} [{scene.get('visual_type', '?'):15s}]: "
                f"{duration_frames} frames (word-count proportional)"
            )

            current_frame += duration_frames
            frames_remaining -= duration_frames

    await _report_progress(job_id, "calculate_frames", 75, "Scene timing calculated!")

    return {
        "total_frames": audio_frames,  # composition duration = exact audio duration
        "fps": fps,
        "scene_timing": timed_scenes,
        "current_step": "calculate_frames",
        "progress": 75,
    }


# ── Node 7: Render Video ──
async def render_video(state: PipelineState) -> dict[str, Any]:
    """Send scene data to the Remotion render server."""
    print("\n[STAGE 7] Rendering video with Remotion...")
    job_id = state.get("job_id", "")

    await _report_progress(
        job_id, "render_video", 78, "Rendering video (this may take a minute)..."
    )

    scene_timing = state["scene_timing"]
    total_frames = state["total_frames"]
    fps = state["fps"]
    theme = state.get("theme", {})

    # Audio URL the Remotion Chromium renderer can fetch from the render server
    audio_url = f"{REMOTION_RENDER_URL}/static/{job_id}/voice.mp3"

    # Output path for the rendered video
    job_dir = get_job_dir(job_id)
    output_path = str((job_dir / "video.mp4").resolve())

    payload = {
        "scenes": scene_timing,
        "audioUrl": audio_url,
        "totalFrames": total_frames,
        "fps": fps,
        "theme": theme,
        "outputPath": output_path,
    }

    print(f"  [RENDER] Sending to {REMOTION_RENDER_URL}/render...")
    print(
        f"  [RENDER] Scenes: {len(scene_timing)}, Frames: {total_frames}, Theme: {theme.get('name', '?')}"
    )
    print(f"  [RENDER] Output: {output_path}")

    # Call the render server (this blocks until render is complete)
    async with httpx.AsyncClient(timeout=600.0) as client:
        response = await client.post(f"{REMOTION_RENDER_URL}/render", json=payload)
        response.raise_for_status()
        result = response.json()

    if not result.get("success"):
        raise RuntimeError(f"Render failed: {result.get('error', 'Unknown error')}")

    print(f"  [RENDER] Video rendered successfully!")

    await _report_progress(job_id, "render_video", 100, "Video ready!")

    return {
        "video_path": output_path,
        "current_step": "render_video",
        "progress": 100,
    }


# ═══════════════════════════════════════════════════════════════
# GRAPH CONSTRUCTION
# ═══════════════════════════════════════════════════════════════


def build_pipeline() -> StateGraph:
    """
    Build the LangGraph pipeline.

    Graph: START → parse_url → fetch_github_data → analyze_repo →
           write_script → generate_voice → calculate_frames → render_video → END
    """
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("parse_url", parse_url)
    graph.add_node("fetch_github_data", fetch_github_data)
    graph.add_node("analyze_repo", analyze_repo_node)
    graph.add_node("write_script", write_script_node)
    graph.add_node("generate_voice", generate_voice)
    graph.add_node("calculate_frames", calculate_frames)
    graph.add_node("render_video", render_video)

    # Wire edges (strictly sequential)
    graph.add_edge(START, "parse_url")
    graph.add_edge("parse_url", "fetch_github_data")
    graph.add_edge("fetch_github_data", "analyze_repo")
    graph.add_edge("analyze_repo", "write_script")
    graph.add_edge("write_script", "generate_voice")
    graph.add_edge("generate_voice", "calculate_frames")
    graph.add_edge("calculate_frames", "render_video")
    graph.add_edge("render_video", END)

    return graph


# Compiled pipeline (singleton)
_compiled_pipeline = None


def get_pipeline():
    """Get or create the compiled pipeline."""
    global _compiled_pipeline
    if _compiled_pipeline is None:
        graph = build_pipeline()
        _compiled_pipeline = graph.compile()
    return _compiled_pipeline


async def run_pipeline(
    job_id: str,
    repo_url: str,
    progress_callback: Optional[Callable] = None,
) -> dict[str, Any]:
    """
    Run the full video generation pipeline.

    Args:
        job_id: Unique job identifier
        repo_url: GitHub repository URL
        progress_callback: Optional async callback for progress updates

    Returns:
        Final pipeline state dict

    Raises:
        Exception: If the pipeline fails at any stage
    """
    # Register progress callback
    if progress_callback:
        register_progress_callback(job_id, progress_callback)

    try:
        pipeline = get_pipeline()

        initial_state: PipelineState = {
            "repo_url": repo_url,
            "job_id": job_id,
            "current_step": "starting",
            "progress": 0,
        }

        print("=" * 60)
        print(f"AutoMotion Pipeline — Job {job_id[:8]}...")
        print(f"Repository: {repo_url}")
        print("=" * 60 + "\n")

        # Run the pipeline
        final_state = await pipeline.ainvoke(initial_state)

        print(f"\n{'=' * 60}")
        print(f"Pipeline complete! Video: {final_state.get('video_path', 'N/A')}")
        print(f"{'=' * 60}")

        return dict(final_state)

    finally:
        unregister_progress_callback(job_id)
