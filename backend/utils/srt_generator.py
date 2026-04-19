"""
AutoMotion — SRT Subtitle Generator
Generates .srt subtitle files from scene narrations and audio durations.
"""


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(
    scenes: list[dict],
    scene_durations: list[float],
    output_path: str,
) -> str:
    """
    Generate an SRT subtitle file from scene narrations and audio durations.

    Args:
        scenes: List of scene dicts, each with a "narration" key
        scene_durations: List of per-scene audio durations in seconds
        output_path: Where to write the .srt file

    Returns:
        The output file path
    """
    lines = []
    current_time = 0.0

    for i, (scene, duration) in enumerate(zip(scenes, scene_durations)):
        narration = scene.get("narration", "").strip()
        if not narration:
            current_time += duration
            continue

        start = current_time
        end = current_time + duration

        # SRT block
        lines.append(str(i + 1))
        lines.append(f"{_format_timestamp(start)} --> {_format_timestamp(end)}")
        lines.append(narration)
        lines.append("")  # blank line separator

        current_time = end

    srt_content = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"  [SRT] Generated {len(scenes)} subtitle blocks → {output_path}")

    return output_path
