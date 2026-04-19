"""
AutoMotion — GitHub URL Parser & Validator
Extracts owner/repo from various GitHub URL formats and validates them.
"""
import re
from typing import Optional


# Patterns for GitHub URLs
GITHUB_PATTERNS = [
    # Full HTTPS URL: https://github.com/owner/repo or https://github.com/owner/repo.git
    re.compile(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"),
    # SSH URL: git@github.com:owner/repo.git
    re.compile(r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$"),
    # Shorthand: owner/repo
    re.compile(r"^([a-zA-Z0-9\-_.]+)/([a-zA-Z0-9\-_.]+)$"),
]

# Characters allowed in owner/repo names
VALID_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\-_.]+$")


def parse_github_url(url: str) -> Optional[tuple[str, str]]:
    """
    Parse a GitHub URL or shorthand into (owner, repo).

    Accepts:
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      - http://github.com/owner/repo
      - github.com/owner/repo
      - git@github.com:owner/repo.git
      - owner/repo

    Returns:
      (owner, repo) tuple on success, None on failure.
    """
    url = url.strip()

    if not url:
        return None

    # Handle bare "github.com/owner/repo" (no protocol)
    if url.startswith("github.com/"):
        url = "https://" + url

    for pattern in GITHUB_PATTERNS:
        match = pattern.match(url)
        if match:
            owner, repo = match.group(1), match.group(2)

            # Validate names
            if not VALID_NAME_PATTERN.match(owner) or not VALID_NAME_PATTERN.match(repo):
                return None

            # Reject suspicious patterns
            if owner.startswith(".") or repo.startswith("."):
                return None

            return owner, repo

    return None


def validate_github_url(url: str) -> tuple[bool, str, Optional[tuple[str, str]]]:
    """
    Validate a GitHub URL and return structured result.

    Returns:
      (is_valid, message, parsed)
      - is_valid: True if URL is valid
      - message: Human-readable status message
      - parsed: (owner, repo) tuple if valid, None otherwise
    """
    parsed = parse_github_url(url)

    if parsed is None:
        return False, "Invalid GitHub URL. Please use format: https://github.com/owner/repo", None

    owner, repo = parsed
    return True, f"Valid repository: {owner}/{repo}", (owner, repo)
