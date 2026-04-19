"""
AutoMotion — Agent #1: Repository Analyzer
Uses Qwen2.5-Coder-32B-Instruct to analyze the codebase and produce
structured JSON covering purpose, tech stack, features, architecture,
and code highlights.
"""
import json
from typing import Any

from agents.state import PipelineState
from agents.prompts import REPO_ANALYST_SYSTEM, REPO_ANALYST_USER, get_fallback_analysis
from services.llm_service import call_llm_with_retry


def _format_tree(tree: list[dict[str, str]]) -> str:
    """Format file tree for the prompt."""
    if not tree:
        return "(empty)"

    lines = []
    for item in tree[:50]:  # Limit to 50 items
        prefix = "📁 " if item["type"] == "tree" else "📄 "
        size = f" ({item['size']} bytes)" if item.get("size") else ""
        lines.append(f"{prefix}{item['path']}{size}")

    return "\n".join(lines)


def _format_key_files(key_files: dict[str, str]) -> str:
    """Format key file contents for the prompt."""
    if not key_files:
        return "(no key files found)"

    parts = []
    for path, content in key_files.items():
        parts.append(f"### {path}\n```\n{content}\n```")

    return "\n\n".join(parts)


def _format_languages(languages: dict[str, int]) -> str:
    """Format language breakdown as readable text."""
    if not languages:
        return "(unknown)"

    total = sum(languages.values())
    lines = []
    for lang, bytes_count in sorted(languages.items(), key=lambda x: -x[1]):
        pct = (bytes_count / total * 100) if total > 0 else 0
        lines.append(f"- {lang}: {pct:.1f}%")

    return "\n".join(lines[:10])  # Top 10


async def analyze_repo(state: PipelineState) -> dict[str, Any]:
    """
    LangGraph node: Analyze the repository using Agent #1 (Coder-32B).

    Reads: owner, repo, readme, description, stars, forks, languages, tree,
           key_files, topics, license, open_issues
    Writes: analysis
    """
    print("\n[STAGE 3] Analyzing repository with Coder-32B...")

    owner = state["owner"]
    repo = state["repo"]

    # Build the prompt
    user_prompt = REPO_ANALYST_USER.format(
        owner=owner,
        repo=repo,
        description=state.get("description", ""),
        readme=state.get("readme", "(no README)"),
        languages=_format_languages(state.get("languages", {})),
        stars=state.get("stars", 0),
        forks=state.get("forks", 0),
        open_issues=state.get("open_issues", 0),
        license=state.get("license", "Unknown"),
        topics=", ".join(state.get("topics", [])) or "None",
        tree=_format_tree(state.get("tree", [])),
        key_files=_format_key_files(state.get("key_files", {})),
    )

    full_prompt = f"{REPO_ANALYST_SYSTEM}\n\n{user_prompt}"

    try:
        analysis = await call_llm_with_retry(
            prompt=full_prompt,
            model_type="code",
            max_retries=2,
            expect_json=True,
        )

        # Validate required fields
        required = ["purpose", "tech_stack", "features"]
        for field in required:
            if field not in analysis:
                raise ValueError(f"Missing required field: {field}")

        print(f"  [ANALYSIS] Purpose: {analysis.get('purpose', '')[:100]}...")
        print(f"  [ANALYSIS] Tech stack: {', '.join(analysis.get('tech_stack', [])[:5])}")
        print(f"  [ANALYSIS] Features: {len(analysis.get('features', []))} found")
        print(f"  [ANALYSIS] Code highlights: {len(analysis.get('code_highlights', []))} found")

        return {
            "analysis": analysis,
            "current_step": "analyze_repo",
            "progress": 35,
        }

    except Exception as e:
        print(f"  [ANALYSIS] All LLM attempts failed: {e}")
        print("  [ANALYSIS] Using fallback template...")

        fallback = get_fallback_analysis(
            owner=owner,
            repo=repo,
            description=state.get("description", ""),
            language=state.get("language", ""),
            stars=state.get("stars", 0),
            topics=state.get("topics", []),
        )

        return {
            "analysis": fallback,
            "current_step": "analyze_repo",
            "progress": 35,
        }
