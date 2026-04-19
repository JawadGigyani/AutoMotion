"""
AutoMotion — WebVTT Subtitle Generator
Generates .vtt subtitle files from scene narrations and audio durations.

WebVTT (Web Video Text Tracks) is the only subtitle format natively supported
by the HTML5 <track> element across all modern browsers (Chrome, Firefox, Safari).
SRT files are NOT reliably parsed by Safari and require a polyfill in Firefox.

Format difference from SRT:
  - File starts with "WEBVTT" header
  - Timestamps use "." for milliseconds instead of ","
  - Otherwise structurally identical
"""


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to WebVTT timestamp format: HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def generate_srt(
    scenes: list[dict],
    scene_durations: list[float],
    output_path: str,
) -> str:
    """
    Generate a WebVTT subtitle file from scene narrations and audio durations.

    Despite the function name kept as generate_srt for backwards compatibility,
    this now outputs a .vtt file. The caller (pipeline.py) should pass a path
    ending in .vtt.

    Args:
        scenes:          List of scene dicts, each with a "narration" key.
        scene_durations: List of per-scene audio durations in seconds (exact,
                         from ffprobe after silence trimming).
        output_path:     Where to write the file. Should end in .vtt.

    Returns:
        The output file path (same as output_path).
    """
    lines = ["WEBVTT", ""]  # WebVTT header + blank line

    current_time = 0.0
    cue_index = 1

    for scene, duration in zip(scenes, scene_durations):
        narration = scene.get("narration", "").strip()

        if not narration:
            current_time += duration
            continue

        start = current_time
        end = current_time + duration

        # Cue identifier (optional but helps debugging)
        lines.append(str(cue_index))
        # Timestamp line
        lines.append(f"{_format_timestamp(start)} --> {_format_timestamp(end)}")
        # Narration text
        lines.append(narration)
        # Blank line separator between cues
        lines.append("")

        current_time = end
        cue_index += 1

    vtt_content = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(vtt_content)

    print(f"  [VTT] Generated {cue_index - 1} subtitle cues → {output_path}")

    return output_path
