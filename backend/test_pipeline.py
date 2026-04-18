"""
RepoReel — Phase 2 Pipeline Tests
Tests pipeline compilation and runs stages 1-4 against a real repo.
Stages 5-7 (voice, frames, render) are skipped as they need ElevenLabs + Remotion.

Run with: python test_pipeline.py
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


async def test_pipeline_compilation():
    """Test that the pipeline graph compiles without errors."""
    print("\n-- Testing pipeline compilation --")

    from agents.pipeline import build_pipeline, get_pipeline

    graph = build_pipeline()
    compiled = graph.compile()

    print(f"  Graph nodes: {list(compiled.get_graph().nodes.keys())}")
    print("  [OK] Pipeline compiles successfully")


async def test_stages_1_2(owner: str = "pallets", repo: str = "flask"):
    """Test Stage 1 (URL parse) and Stage 2 (GitHub fetch)."""
    print(f"\n-- Testing Stages 1-2: Parse URL + Fetch GitHub ({owner}/{repo}) --")

    from agents.pipeline import parse_url, fetch_github_data, PipelineState

    # Stage 1: Parse URL
    state: PipelineState = {
        "repo_url": f"https://github.com/{owner}/{repo}",
        "job_id": "test-pipeline",
    }

    result = await parse_url(state)
    assert result["owner"] == owner, f"Expected owner={owner}, got {result['owner']}"
    assert result["repo"] == repo, f"Expected repo={repo}, got {result['repo']}"
    print(f"  [OK] Stage 1: Parsed {owner}/{repo}")

    # Stage 2: Fetch GitHub data
    state.update(result)
    result = await fetch_github_data(state)

    assert "readme" in result, "Missing readme"
    assert "description" in result, "Missing description"
    assert result["stars"] > 0, "Stars should be > 0"
    assert len(result["languages"]) > 0, "Should have languages"

    print(f"  [OK] Stage 2: Fetched data - {result['stars']} stars, "
          f"{len(result['languages'])} langs, {len(result.get('tree', []))} tree items")

    return state


async def test_stages_3_4(owner: str = "pallets", repo: str = "flask"):
    """Test Stage 3 (repo analysis) and Stage 4 (script + scenes)."""
    print(f"\n-- Testing Stages 3-4: Analyze Repo + Write Script ({owner}/{repo}) --")

    from agents.pipeline import (
        parse_url, fetch_github_data, analyze_repo_node,
        write_script_node, PipelineState,
    )

    # Run stages 1-2 first
    state: PipelineState = {
        "repo_url": f"https://github.com/{owner}/{repo}",
        "job_id": "test-pipeline",
    }
    state.update(await parse_url(state))
    state.update(await fetch_github_data(state))

    # Stage 3: Analyze repo
    print("\n  Running Agent #1 (Repo Analyst)...")
    result = await analyze_repo_node(state)
    state.update(result)

    analysis = result.get("analysis", {})
    assert "purpose" in analysis, "Missing purpose"
    assert "tech_stack" in analysis, "Missing tech_stack"
    assert "features" in analysis, "Missing features"

    print(f"  [OK] Stage 3: Analysis complete")
    print(f"    Purpose: {analysis['purpose'][:100]}...")
    print(f"    Tech stack: {analysis['tech_stack'][:5]}")
    print(f"    Features: {len(analysis['features'])} found")

    # Stage 4: Write script + scenes
    print("\n  Running Agent #2 (Script + Scene Director)...")
    result = await write_script_node(state)
    state.update(result)

    script = result.get("script", {})
    theme = result.get("theme", {})
    scenes = script.get("scenes", [])

    assert len(scenes) >= 3, f"Need >= 3 scenes, got {len(scenes)}"
    assert "id" in theme, "Theme should have an ID"

    print(f"  [OK] Stage 4: Script complete")
    print(f"    Scenes: {len(scenes)}")
    print(f"    Theme: {theme.get('name', '?')} ({theme.get('id', '?')})")
    print(f"    Theme hint: {script.get('theme_hint', '?')}")

    # Print full scene breakdown
    print(f"\n  Scene Breakdown:")
    for i, scene in enumerate(scenes):
        print(f"    {i+1}. [{scene['visual_type']:15s}] {scene['narration'][:70]}...")

    # Save the script for inspection
    output_path = os.path.join(os.path.dirname(__file__), "outputs", "test-pipeline")
    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, "script.json"), "w") as f:
        json.dump({"script": script, "theme": theme, "analysis": analysis}, f, indent=2)
    print(f"\n  [SAVED] Full output → {output_path}/script.json")


async def main():
    print("=" * 60)
    print("RepoReel - Phase 2 Pipeline Tests")
    print("=" * 60)

    await test_pipeline_compilation()
    await test_stages_1_2()
    await test_stages_3_4()

    print("\n" + "=" * 60)
    print("All Phase 2 tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
