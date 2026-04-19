"""
AutoMotion — Theme Service
Weighted-random selection of video themes based on repository characteristics.
Ensures visual variety across generations so judges see different templates.
"""
import random
from typing import Any


# ── Theme Definitions ──
THEMES = {
    "dark_cinematic": {
        "id": "dark_cinematic",
        "name": "Dark Cinematic",
        "colors": {
            "bgPrimary": "#0a0a0a",
            "bgSecondary": "#1a1a2e",
            "bgGradient": "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
            "accent": "#6c63ff",
            "accentSecondary": "#a78bfa",
            "text": "#f0f0f0",
            "textMuted": "#8b8b9e",
            "codeBg": "#1e1e2e",
            "codeText": "#cdd6f4",
            "cardBg": "#16162a",
        },
        "fonts": {
            "heading": "Inter",
            "body": "Inter",
            "code": "JetBrains Mono",
        },
    },
    "neon_cyberpunk": {
        "id": "neon_cyberpunk",
        "name": "Neon Cyberpunk",
        "colors": {
            "bgPrimary": "#0d0221",
            "bgSecondary": "#150530",
            "bgGradient": "linear-gradient(135deg, #0d0221 0%, #150530 50%, #0a0118 100%)",
            "accent": "#ff00ff",
            "accentSecondary": "#00ffff",
            "text": "#f0e6ff",
            "textMuted": "#9b72cf",
            "codeBg": "#1a0030",
            "codeText": "#e0d0ff",
            "cardBg": "#120428",
        },
        "fonts": {
            "heading": "Inter",
            "body": "Inter",
            "code": "JetBrains Mono",
        },
    },
    "minimal_light": {
        "id": "minimal_light",
        "name": "Minimal Light",
        "colors": {
            "bgPrimary": "#f8f9fa",
            "bgSecondary": "#e9ecef",
            "bgGradient": "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
            "accent": "#3b82f6",
            "accentSecondary": "#1d4ed8",
            "text": "#1a1a2e",
            "textMuted": "#6b7280",
            "codeBg": "#1e293b",
            "codeText": "#e2e8f0",
            "cardBg": "#ffffff",
        },
        "fonts": {
            "heading": "Inter",
            "body": "Inter",
            "code": "JetBrains Mono",
        },
    },
    "terminal_green": {
        "id": "terminal_green",
        "name": "Terminal Green",
        "colors": {
            "bgPrimary": "#0c0c0c",
            "bgSecondary": "#0a1a0a",
            "bgGradient": "linear-gradient(135deg, #0c0c0c 0%, #0a1a0a 100%)",
            "accent": "#00ff41",
            "accentSecondary": "#39ff14",
            "text": "#00ff41",
            "textMuted": "#007a1f",
            "codeBg": "#0a1a0a",
            "codeText": "#00ff41",
            "cardBg": "#0d1a0d",
        },
        "fonts": {
            "heading": "JetBrains Mono",
            "body": "JetBrains Mono",
            "code": "JetBrains Mono",
        },
    },
    "ocean_depth": {
        "id": "ocean_depth",
        "name": "Ocean Depth",
        "colors": {
            "bgPrimary": "#0a192f",
            "bgSecondary": "#112240",
            "bgGradient": "linear-gradient(135deg, #0a192f 0%, #112240 100%)",
            "accent": "#64ffda",
            "accentSecondary": "#7ee8fa",
            "text": "#ccd6f6",
            "textMuted": "#8892b0",
            "codeBg": "#0a192f",
            "codeText": "#a8b2d1",
            "cardBg": "#112240",
        },
        "fonts": {
            "heading": "Inter",
            "body": "Inter",
            "code": "JetBrains Mono",
        },
    },
}

# ── Language → Category Mapping ──
LANGUAGE_CATEGORIES: dict[str, str] = {
    # Frontend
    "JavaScript": "frontend",
    "TypeScript": "frontend",
    "Vue": "frontend",
    "CSS": "frontend",
    "HTML": "frontend",
    "Svelte": "frontend",
    "SCSS": "frontend",
    "Less": "frontend",
    # Backend
    "Go": "backend",
    "Rust": "backend",
    "C": "backend",
    "C++": "backend",
    "Elixir": "backend",
    "Erlang": "backend",
    # DevOps
    "Shell": "devops",
    "Dockerfile": "devops",
    "HCL": "devops",
    "Makefile": "devops",
    "PowerShell": "devops",
    "Nix": "devops",
    # Data Science
    "Jupyter Notebook": "datascience",
    "R": "datascience",
    # General
    "Python": "general",
    "Java": "general",
    "C#": "general",
    "Kotlin": "general",
    "Swift": "general",
    "Ruby": "general",
    "PHP": "general",
    "Dart": "general",
    "Lua": "general",
    "Scala": "general",
}

# ── Category → Theme Weights ──
# Higher weight = more likely to be selected for that category
THEME_WEIGHTS: dict[str, dict[str, int]] = {
    "frontend": {
        "dark_cinematic": 1,
        "neon_cyberpunk": 4,
        "minimal_light": 2,
        "terminal_green": 0,
        "ocean_depth": 1,
    },
    "backend": {
        "dark_cinematic": 4,
        "neon_cyberpunk": 1,
        "minimal_light": 1,
        "terminal_green": 2,
        "ocean_depth": 1,
    },
    "devops": {
        "dark_cinematic": 1,
        "neon_cyberpunk": 1,
        "minimal_light": 0,
        "terminal_green": 5,
        "ocean_depth": 1,
    },
    "datascience": {
        "dark_cinematic": 1,
        "neon_cyberpunk": 1,
        "minimal_light": 1,
        "terminal_green": 0,
        "ocean_depth": 5,
    },
    "general": {
        "dark_cinematic": 3,
        "neon_cyberpunk": 2,
        "minimal_light": 2,
        "terminal_green": 1,
        "ocean_depth": 2,
    },
}


def _detect_category(languages: dict[str, int], primary_language: str) -> str:
    """
    Detect the repo category from its languages.
    Uses the primary language first, then falls back to the most common category
    across all languages.
    """
    # Check primary language
    if primary_language and primary_language in LANGUAGE_CATEGORIES:
        return LANGUAGE_CATEGORIES[primary_language]

    # Count category votes from all languages
    category_votes: dict[str, int] = {}
    for lang, bytes_count in languages.items():
        category = LANGUAGE_CATEGORIES.get(lang, "general")
        category_votes[category] = category_votes.get(category, 0) + bytes_count

    if category_votes:
        return max(category_votes, key=category_votes.get)

    return "general"


def select_theme(
    languages: dict[str, int],
    primary_language: str = "",
    theme_hint: str = "",
) -> dict[str, Any]:
    """
    Select a theme using weighted-random selection based on repo characteristics.

    The selection is intentionally non-deterministic — the same repo may get
    a different theme on re-generation. Weights just bias toward aesthetically
    appropriate themes.

    Args:
        languages: Language breakdown dict (language → bytes)
        primary_language: The primary language of the repo
        theme_hint: Optional hint from the LLM (e.g., "frontend", "devops")

    Returns:
        A complete theme definition dict
    """
    # Determine category
    if theme_hint and theme_hint in THEME_WEIGHTS:
        category = theme_hint
    else:
        category = _detect_category(languages, primary_language)

    # Get weights for this category
    weights = THEME_WEIGHTS.get(category, THEME_WEIGHTS["general"])

    # Filter to themes with weight > 0
    eligible_themes = [tid for tid, w in weights.items() if w > 0]
    eligible_weights = [weights[tid] for tid in eligible_themes]

    if not eligible_themes:
        # Shouldn't happen, but fallback to dark_cinematic
        return THEMES["dark_cinematic"]

    # Weighted random selection
    selected_id = random.choices(eligible_themes, weights=eligible_weights, k=1)[0]

    print(f"  [THEME] Category: {category} → Selected: {THEMES[selected_id]['name']}")

    return THEMES[selected_id]


def get_all_themes() -> dict[str, dict[str, Any]]:
    """Return all available themes."""
    return THEMES


def get_theme_by_id(theme_id: str) -> dict[str, Any]:
    """Get a specific theme by ID. Falls back to dark_cinematic."""
    return THEMES.get(theme_id, THEMES["dark_cinematic"])
