"""
AutoMotion — Pipeline State
TypedDict shared across all LangGraph nodes.
"""

from typing import Any, Optional

from typing_extensions import TypedDict


class PipelineState(TypedDict, total=False):
    """
    Shared state passed through all LangGraph pipeline nodes.
    Each node reads what it needs and writes its outputs.
    """

    # ── Input (set at pipeline start) ──
    repo_url: str
    owner: str
    repo: str
    job_id: str
    theme_id: Optional[str]

    # ── GitHub Data (set by fetch_github_data node) ──
    readme: str
    description: str
    stars: int
    forks: int
    language: str
    topics: list[str]
    languages: dict[str, int]
    tree: list[dict[str, str]]
    key_files: dict[str, str]
    default_branch: str
    license: str
    open_issues: int

    # ── Agent #1 Output: Repo Analysis (set by analyze_repo node) ──
    analysis: dict[str, Any]

    # ── Agent #2 Output: Script + Scenes (set by write_script node) ──
    script: dict[str, Any]  # Contains theme_hint + scenes list
    theme: dict[str, Any]  # Selected theme definition

    # ── Voice (set by generate_voice node) ──
    audio_path: str
    audio_duration: float  # seconds
    scene_audio_durations: list[
        float
    ]  # per-scene durations in seconds (exact, from ffprobe)

    # ── Frames (set by calculate_frames node) ──
    total_frames: int
    fps: int
    scene_timing: list[dict[str, Any]]  # Scenes with start/durationInFrames

    # ── Video (set by render_video node) ──
    video_path: str

    # ── Tracking ──
    current_step: str
    progress: int  # 0-100
    error: Optional[str]
