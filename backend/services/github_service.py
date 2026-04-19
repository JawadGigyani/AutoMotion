"""
AutoMotion — GitHub Service
Fetches repository data from the GitHub REST API:
metadata, README, file tree, and key source files.
"""
import base64
from typing import Any, Optional

import httpx

from config import (
    GITHUB_TOKEN,
    MAX_README_CHARS,
    MAX_CODE_FILE_CHARS,
    MAX_KEY_FILES,
)

# ── GitHub API base ──
GITHUB_API = "https://api.github.com"

# ── Key files to look for (in priority order) ──
KEY_FILE_NAMES = [
    # Package manifests
    "package.json", "requirements.txt", "setup.py", "pyproject.toml",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle",
    "Gemfile", "composer.json",
    # Entry points
    "main.py", "app.py", "index.js", "index.ts", "main.go",
    "main.rs", "App.tsx", "App.jsx", "server.py", "server.js",
    # Config
    "Dockerfile", "docker-compose.yml", ".env.example",
]


def _get_headers() -> dict[str, str]:
    """Build request headers with optional auth token."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AutoMotion/1.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


async def fetch_repo_metadata(owner: str, repo: str) -> dict[str, Any]:
    """
    Fetch repository metadata (description, stars, forks, language, topics).

    Returns a dict with:
      - name, full_name, description
      - stars, forks, watchers
      - language, topics
      - created_at, updated_at
      - is_fork, is_archived
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}",
            headers=_get_headers(),
        )
        response.raise_for_status()
        data = response.json()

    return {
        "name": data.get("name", ""),
        "full_name": data.get("full_name", ""),
        "description": data.get("description", "") or "",
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "watchers": data.get("subscribers_count", 0),
        "language": data.get("language", ""),
        "topics": data.get("topics", []),
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", ""),
        "is_fork": data.get("fork", False),
        "is_archived": data.get("archived", False),
        "default_branch": data.get("default_branch", "main"),
        "open_issues": data.get("open_issues_count", 0),
        "license": (data.get("license") or {}).get("spdx_id", ""),
    }


async def fetch_languages(owner: str, repo: str) -> dict[str, int]:
    """
    Fetch language breakdown (language → bytes).
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/languages",
            headers=_get_headers(),
        )
        response.raise_for_status()
        return response.json()


async def fetch_readme(owner: str, repo: str) -> str:
    """
    Fetch the README content as raw text.
    Tries the default endpoint, returns empty string on 404.
    Truncates to MAX_README_CHARS.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = _get_headers()
        headers["Accept"] = "application/vnd.github.raw"

        response = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/readme",
            headers=headers,
        )

        if response.status_code == 404:
            return ""

        response.raise_for_status()
        content = response.text

    # Truncate
    if len(content) > MAX_README_CHARS:
        content = content[:MAX_README_CHARS] + "\n\n[... truncated ...]"

    return content


async def fetch_file_tree(
    owner: str, repo: str, branch: str = "main"
) -> list[dict[str, str]]:
    """
    Fetch the repository file tree (recursive).
    Returns a list of {path, type, size} dicts.
    Filters to top 2 levels to avoid overwhelming the LLM.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}",
            params={"recursive": "1"},
            headers=_get_headers(),
        )

        # Try 'master' branch if 'main' fails
        if response.status_code == 404 and branch == "main":
            response = await client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/master",
                params={"recursive": "1"},
                headers=_get_headers(),
            )

        if response.status_code == 404:
            return []

        response.raise_for_status()
        data = response.json()

    tree = data.get("tree", [])

    # Filter to top 2 levels only
    filtered = []
    for item in tree:
        path = item.get("path", "")
        depth = path.count("/")
        if depth <= 1:  # 0 = root level, 1 = one level deep
            filtered.append({
                "path": path,
                "type": item.get("type", ""),
                "size": item.get("size", 0),
            })

    return filtered


async def fetch_file_content(owner: str, repo: str, path: str) -> Optional[str]:
    """
    Fetch the content of a single file from the repo.
    Returns the file content as a string, truncated to MAX_CODE_FILE_CHARS.
    Returns None if the file doesn't exist or is binary.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = _get_headers()
        headers["Accept"] = "application/vnd.github.raw"

        response = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=headers,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        # Check if response is text (not binary)
        content_type = response.headers.get("content-type", "")
        if "application/octet-stream" in content_type:
            return None

        content = response.text

    # Truncate
    if len(content) > MAX_CODE_FILE_CHARS:
        content = content[:MAX_CODE_FILE_CHARS] + "\n\n// ... truncated ..."

    return content


async def fetch_key_files(
    owner: str, repo: str, tree: list[dict[str, str]]
) -> dict[str, str]:
    """
    Intelligently select and fetch the most important source files.

    Strategy:
    1. Look for known key filenames in the tree
    2. Select up to MAX_KEY_FILES
    3. Fetch their contents

    Returns a dict of {filename: content}.
    """
    # Get all blob (file) paths from the tree
    file_paths = [item["path"] for item in tree if item["type"] == "blob"]

    # Find key files by matching against our priority list
    selected: list[str] = []

    # First pass: exact filename matches (priority list order)
    for key_name in KEY_FILE_NAMES:
        for file_path in file_paths:
            # Match both root-level and nested files
            if file_path.endswith(key_name) or file_path == key_name:
                if file_path not in selected:
                    selected.append(file_path)
                    break  # Only take the first match per key name

        if len(selected) >= MAX_KEY_FILES:
            break

    # Second pass: if we have fewer than MAX_KEY_FILES, look for main entry points
    # by file extension in common directories
    if len(selected) < MAX_KEY_FILES:
        entry_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs"}
        entry_dirs = {"src/", "lib/", "app/", "cmd/"}

        for file_path in file_paths:
            if len(selected) >= MAX_KEY_FILES:
                break
            if file_path in selected:
                continue

            # Check if it's in a source directory with a relevant extension
            ext = "." + file_path.rsplit(".", 1)[-1] if "." in file_path else ""
            in_src_dir = any(file_path.startswith(d) for d in entry_dirs)

            if ext in entry_extensions and in_src_dir:
                selected.append(file_path)

    # Fetch contents
    key_files: dict[str, str] = {}
    for file_path in selected:
        content = await fetch_file_content(owner, repo, file_path)
        if content is not None:
            key_files[file_path] = content

    return key_files


async def fetch_all_repo_data(owner: str, repo: str) -> dict[str, Any]:
    """
    Fetch all repository data in one call.

    Returns a comprehensive dict with:
      - metadata, languages, readme, tree, key_files
    """
    # Fetch metadata first to get the default branch
    metadata = await fetch_repo_metadata(owner, repo)
    default_branch = metadata.get("default_branch", "main")

    # Fetch everything else
    languages = await fetch_languages(owner, repo)
    readme = await fetch_readme(owner, repo)
    tree = await fetch_file_tree(owner, repo, branch=default_branch)
    key_files = await fetch_key_files(owner, repo, tree)

    return {
        "metadata": metadata,
        "languages": languages,
        "readme": readme,
        "tree": tree,
        "key_files": key_files,
    }
