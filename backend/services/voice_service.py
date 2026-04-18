"""
RepoReel — Voice Service
ElevenLabs TTS wrapper using the official Python SDK.

Two generation strategies:
  generate_per_scene_voiceovers()  — PRIMARY: one clip per scene, exact durations,
                                     then concatenated into a single voice.mp3.
                                     Gives perfect audio/video sync.
  generate_voiceover()             — FALLBACK: single-call full narration.

Also provides:
  get_audio_duration()             — ffprobe-based duration extraction
  _trim_leading_silence()          — ffmpeg silenceremove (in-place)
  _concat_audio_files()            — ffmpeg concat demuxer
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL_ID,
    ELEVENLABS_VOICE_ID,
)
from elevenlabs import ElevenLabs

# ── SDK Client (lazy init) ─────────────────────────────────────────────────

_client: ElevenLabs | None = None


def _get_client() -> ElevenLabs:
    """Get or create the ElevenLabs SDK client."""
    global _client
    if _client is None:
        if not ELEVENLABS_API_KEY:
            raise RuntimeError("ELEVENLABS_API_KEY is not set in .env")
        _client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    return _client


# ══════════════════════════════════════════════════════════════════════════════
# PRIMARY: Per-scene generation (exact sync)
# ══════════════════════════════════════════════════════════════════════════════


def generate_per_scene_voiceovers(
    scenes: list[dict],
    job_dir: Path | str,
) -> tuple[str, list[float]]:
    """
    Generate one MP3 clip per scene narration, trim leading silence from each,
    record the exact duration, then concatenate all clips into a single voice.mp3.

    This is the only reliable way to sync scene frame durations with the audio —
    word-count proportional distribution is not accurate because ElevenLabs speaks
    at a non-constant rate that varies with punctuation, phoneme complexity, and
    sentence rhythm.

    Args:
        scenes:   List of scene dicts, each must have a "narration" key.
        job_dir:  Directory where audio files will be written.

    Returns:
        (combined_audio_path, scene_durations)
        combined_audio_path  — absolute path to the stitched voice.mp3
        scene_durations      — per-scene durations in seconds (trimmed, exact)

    Raises:
        RuntimeError: If ElevenLabs keys are missing or ffmpeg concat fails.
    """
    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)

    if not ELEVENLABS_VOICE_ID:
        raise RuntimeError("ELEVENLABS_VOICE_ID is not set in .env")

    client = _get_client()

    total_chars = sum(len(s.get("narration", "")) for s in scenes)
    print(
        f"  [TTS] Generating {len(scenes)} per-scene clips "
        f"({total_chars} total chars)..."
    )

    scene_paths: list[str] = []
    scene_durations: list[float] = []

    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "").strip()
        if not narration:
            narration = f"Scene {i + 1}."

        scene_path = job_dir / f"scene_{i:02d}.mp3"

        # ── Generate TTS for this scene ──────────────────────────────────
        audio = client.text_to_speech.convert(
            text=narration,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id=ELEVENLABS_MODEL_ID,
            output_format="mp3_44100_128",
        )

        with open(scene_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        # ── Strip leading silence that ElevenLabs adds ───────────────────
        _trim_leading_silence(scene_path)

        # ── Record exact trimmed duration ────────────────────────────────
        duration = get_audio_duration(str(scene_path))
        scene_durations.append(duration)
        scene_paths.append(str(scene_path))

        preview = narration[:55] + ("..." if len(narration) > 55 else "")
        print(f'    [{i + 1:02d}/{len(scenes):02d}] {duration:.2f}s  — "{preview}"')

    # ── Concatenate all clips into a single voice.mp3 ─────────────────────
    combined_path = str(job_dir / "voice.mp3")
    _concat_audio_files(scene_paths, combined_path)

    total_duration = sum(scene_durations)
    print(f"  [TTS] ✓ All clips generated and stitched  | total: {total_duration:.2f}s")

    return combined_path, scene_durations


# ══════════════════════════════════════════════════════════════════════════════
# FALLBACK: Single-call generation (used if per-scene fails)
# ══════════════════════════════════════════════════════════════════════════════


def generate_voiceover(narration_text: str, output_path: str | Path) -> str:
    """
    Generate a voiceover MP3 from the full concatenated narration in one API call.
    Used as a fallback when per-scene generation is not possible.

    Args:
        narration_text: The full narration text to synthesise.
        output_path:    Where to save the MP3 file.

    Returns:
        Absolute path to the generated (and silence-trimmed) MP3.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not ELEVENLABS_VOICE_ID:
        raise RuntimeError("ELEVENLABS_VOICE_ID is not set in .env")

    client = _get_client()
    print(f"  [TTS] Generating single-call voiceover ({len(narration_text)} chars)...")

    audio = client.text_to_speech.convert(
        text=narration_text,
        voice_id=ELEVENLABS_VOICE_ID,
        model_id=ELEVENLABS_MODEL_ID,
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"  [TTS] ✓ Audio saved: {output_path} ({file_size_kb:.1f} KB)")

    _trim_leading_silence(output_path)
    return str(output_path.resolve())


# ══════════════════════════════════════════════════════════════════════════════
# AUDIO UTILITIES
# ══════════════════════════════════════════════════════════════════════════════


def get_audio_duration(audio_path: str | Path) -> float:
    """
    Get the precise duration of an audio file using ffprobe.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Duration in seconds (float).

    Raises:
        RuntimeError: If ffprobe is not found or fails.
    """
    audio_path = str(audio_path)

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-i",
                audio_path,
                "-show_entries",
                "format=duration",
                "-v",
                "quiet",
                "-of",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )

        probe_data = json.loads(result.stdout)
        duration = float(probe_data["format"]["duration"])
        print(f"  [AUDIO] Duration: {duration:.2f}s")
        return duration

    except FileNotFoundError:
        raise RuntimeError(
            "ffprobe not found. Install FFmpeg: https://ffmpeg.org/download.html"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed: {e.stderr}")
    except (json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"Failed to parse ffprobe output: {e}")


def _trim_leading_silence(
    audio_path: Path | str,
    threshold_db: float = -45.0,
) -> None:
    """
    Remove leading silence from an audio file **in place** using ffmpeg.

    ElevenLabs reliably adds 0.5–1.5 s of silence at the start of every
    generated MP3.  Without trimming, the video visuals play ahead of the
    narration for the first couple of seconds.

    Uses a conservative threshold so that intentionally soft openings
    (e.g. breathy voice acting) are not clipped.

    Silently no-ops if ffmpeg is unavailable or the operation fails — the
    pipeline will still work, just with the original audio.
    """
    audio_path = Path(audio_path)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp3", dir=audio_path.parent)
    os.close(tmp_fd)

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(audio_path),
                "-af",
                (
                    f"silenceremove="
                    f"start_periods=1:"
                    f"start_threshold={threshold_db}dB:"
                    f"start_duration=0.05"
                ),
                tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"  [AUDIO] Silence trim skipped (ffmpeg exit {result.returncode})")
            return

        trimmed_size = os.path.getsize(tmp_path)
        if trimmed_size < 1024:
            print("  [AUDIO] Silence trim skipped (output suspiciously small)")
            return

        original_size = os.path.getsize(audio_path)
        shutil.move(tmp_path, str(audio_path))
        saved_kb = (original_size - trimmed_size) / 1024
        if saved_kb > 0.5:
            print(f"  [AUDIO] Leading silence trimmed ({saved_kb:.1f} KB removed)")

    except FileNotFoundError:
        print("  [AUDIO] Silence trim skipped (ffmpeg not found in PATH)")
    except subprocess.TimeoutExpired:
        print("  [AUDIO] Silence trim skipped (ffmpeg timed out)")
    except Exception as e:
        print(f"  [AUDIO] Silence trim skipped ({e})")
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def _concat_audio_files(input_paths: list[str], output_path: str) -> None:
    """
    Concatenate multiple MP3 files into one using ffmpeg's concat demuxer.

    No re-encoding — copies streams directly, so it is fast and lossless.
    All inputs must share the same codec, sample rate, and channel layout
    (guaranteed here because every clip uses "mp3_44100_128").

    Args:
        input_paths: Ordered list of absolute paths to the clip MP3s.
        output_path: Destination path for the concatenated MP3.

    Raises:
        RuntimeError: If ffmpeg is not available or the concat fails.
    """
    if not input_paths:
        raise ValueError("No input paths provided to _concat_audio_files")

    # Single clip — just copy directly, no need to invoke ffmpeg
    if len(input_paths) == 1:
        shutil.copy2(input_paths[0], output_path)
        print(f"  [AUDIO] Single clip copied → {output_path}")
        return

    # Write the ffmpeg concat manifest.
    # ffmpeg requires forward slashes even on Windows.
    tmp_fd, list_path = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            for path in input_paths:
                posix_path = Path(path).as_posix()
                # FFmpeg concat requires single quotes explicitly
                f.write(f"file '{posix_path}'\n")

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_path,
                "-c",
                "copy",
                output_path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            # Include the last 600 chars of stderr for diagnosis
            stderr_tail = result.stderr[-600:] if result.stderr else "(no output)"
            raise RuntimeError(
                f"ffmpeg concat failed (exit {result.returncode}):\n{stderr_tail}"
            )

        out_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(
            f"  [AUDIO] Concatenated {len(input_paths)} clips "
            f"→ {output_path} ({out_mb:.2f} MB)"
        )

    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found in PATH. Install FFmpeg: https://ffmpeg.org/download.html"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("ffmpeg concat timed out after 120 s")
    finally:
        if os.path.exists(list_path):
            try:
                os.remove(list_path)
            except OSError:
                pass
