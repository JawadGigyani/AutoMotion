"""
RepoReel — Agent #2: Script Writer + Scene Director (Merged)
Uses Qwen2.5-72B-Instruct to write the narration script AND
specify visual scenes in a single LLM call.
Also handles theme selection via the theme_service.
"""
import json
from typing import Any

from agents.state import PipelineState
from agents.prompts import SCRIPT_DIRECTOR_SYSTEM, SCRIPT_DIRECTOR_USER, get_fallback_script
from services.llm_service import call_llm_with_retry
from services.theme_service import select_theme


def _format_analysis(analysis: dict) -> str:
    """Format the analysis dict as readable text for the prompt."""
    parts = []
    parts.append(f"Purpose: {analysis.get('purpose', 'Unknown')}")
    parts.append(f"Architecture: {analysis.get('architecture', 'Unknown')}")
    parts.append(f"Target Audience: {analysis.get('target_audience', 'Developers')}")

    features = analysis.get("features", [])
    if features:
        parts.append("Key Features:")
        for f in features[:5]:
            parts.append(f"  - {f}")

    return "\n".join(parts)


def _format_code_highlights(analysis: dict) -> str:
    """Format code highlights for the prompt."""
    highlights = analysis.get("code_highlights", [])
    if not highlights:
        return "(no code highlights available)"

    parts = []
    for h in highlights[:3]:
        parts.append(
            f"File: {h.get('file', 'unknown')}\n"
            f"What it does: {h.get('explanation', '')}\n"
            f"Why interesting: {h.get('why_interesting', '')}"
        )

    return "\n\n".join(parts)


def _validate_scenes(script: dict) -> dict:
    """
    Validate and sanitize the script output.
    Ensures all required fields exist with sensible defaults.
    """
    valid_visual_types = {"title", "overview", "tech_stack", "code_highlight", "features", "stats", "closing"}
    valid_animations = {"fade_in", "slide_left", "slide_up", "typewriter", "code_reveal", "zoom_in", "count_up", "fade_out"}
    valid_backgrounds = {"gradient", "noise", "grid", "dots", "radial", "solid"}

    scenes = script.get("scenes", [])
    validated = []

    for i, scene in enumerate(scenes):
        validated_scene = {
            "narration": scene.get("narration", f"Scene {i + 1}"),
            "visual_type": scene.get("visual_type", "overview"),
            "content": scene.get("content", {}),
            "animation": scene.get("animation", "fade_in"),
            "background_variant": scene.get("background_variant", "gradient"),
        }

        # Clamp to valid values
        if validated_scene["visual_type"] not in valid_visual_types:
            validated_scene["visual_type"] = "overview"
        if validated_scene["animation"] not in valid_animations:
            validated_scene["animation"] = "fade_in"
        if validated_scene["background_variant"] not in valid_backgrounds:
            validated_scene["background_variant"] = "gradient"

        # Ensure narration is not empty
        if not validated_scene["narration"].strip():
            validated_scene["narration"] = f"Scene {i + 1} of the video."

        validated.append(validated_scene)

    # Ensure we have at least 3 scenes
    if len(validated) < 3:
        raise ValueError(f"Script has only {len(validated)} scenes, need at least 3")

    script["scenes"] = validated
    return script


async def write_script_and_scenes(state: PipelineState) -> dict[str, Any]:
    """
    LangGraph node: Write narration script + visual scene specs using Agent #2 (72B).
    Also performs theme selection based on the script's theme_hint.

    Reads: owner, repo, description, analysis, stars, forks, language, topics,
           license, languages, key_files
    Writes: script, theme
    """
    print("\n[STAGE 4] Writing script + directing scenes with 72B-Instruct...")

    owner = state["owner"]
    repo = state["repo"]
    analysis = state.get("analysis", {})

    # Build the prompt
    tech_stack = analysis.get("tech_stack", [])
    user_prompt = SCRIPT_DIRECTOR_USER.format(
        owner=owner,
        repo=repo,
        description=state.get("description", ""),
        analysis=_format_analysis(analysis),
        stars=state.get("stars", 0),
        forks=state.get("forks", 0),
        language=state.get("language", "Unknown"),
        license=state.get("license", "Unknown"),
        topics=", ".join(state.get("topics", [])) or "None",
        tech_stack=", ".join(tech_stack[:8]) if tech_stack else "Unknown",
        code_highlights=_format_code_highlights(analysis),
        key_file_names=", ".join(list(state.get("key_files", {}).keys())[:10]) or "None",
    )

    full_prompt = f"{SCRIPT_DIRECTOR_SYSTEM}\n\n{user_prompt}"

    try:
        script = await call_llm_with_retry(
            prompt=full_prompt,
            model_type="general",
            max_retries=2,
            expect_json=True,
        )

        # Validate scenes
        script = _validate_scenes(script)

        scene_count = len(script.get("scenes", []))
        total_words = sum(len(s["narration"].split()) for s in script["scenes"])
        print(f"  [SCRIPT] Generated {scene_count} scenes, {total_words} words total")

        for i, scene in enumerate(script["scenes"]):
            print(f"    Scene {i+1}: [{scene['visual_type']:15s}] {scene['narration'][:60]}...")

    except Exception as e:
        print(f"  [SCRIPT] All LLM attempts failed: {e}")
        print("  [SCRIPT] Using fallback template...")

        script = get_fallback_script(
            owner=owner,
            repo=repo,
            description=state.get("description", ""),
            language=state.get("language", ""),
            stars=state.get("stars", 0),
            forks=state.get("forks", 0),
            tech_stack=analysis.get("tech_stack", []),
        )

    # Select theme using weighted-random based on repo characteristics
    theme_hint = script.get("theme_hint", analysis.get("category_hint", ""))
    theme = select_theme(
        languages=state.get("languages", {}),
        primary_language=state.get("language", ""),
        theme_hint=theme_hint,
    )

    return {
        "script": script,
        "theme": theme,
        "current_step": "write_script",
        "progress": 50,
    }
