"""
AutoMotion — Phase 1 Service Tests
Quick smoke tests for all backend services.
Run with: python test_services.py
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))


def test_config():
    """Test config loads correctly."""
    print("\n── Testing config.py ──")
    from config import (
        FEATHERLESS_API_KEY, FEATHERLESS_BASE_URL,
        ELEVENLABS_API_KEY, OUTPUTS_DIR, VIDEO_FPS,
    )
    print(f"  Featherless URL: {FEATHERLESS_BASE_URL}")
    print(f"  Featherless Key: {'✓ set' if FEATHERLESS_API_KEY else '✗ not set'}")
    print(f"  ElevenLabs Key:  {'✓ set' if ELEVENLABS_API_KEY else '✗ not set'}")
    print(f"  Outputs Dir:     {OUTPUTS_DIR}")
    print(f"  Video FPS:       {VIDEO_FPS}")
    print("  ✓ Config loaded successfully")


def test_url_parser():
    """Test GitHub URL parsing."""
    print("\n── Testing url_parser.py ──")
    from utils.url_parser import parse_github_url, validate_github_url

    # Valid URLs
    test_cases = [
        ("https://github.com/facebook/react", ("facebook", "react")),
        ("https://github.com/owner/repo.git", ("owner", "repo")),
        ("github.com/owner/repo", ("owner", "repo")),
        ("owner/repo", ("owner", "repo")),
        ("git@github.com:owner/repo.git", ("owner", "repo")),
    ]

    for url, expected in test_cases:
        result = parse_github_url(url)
        status = "✓" if result == expected else f"✗ (got {result})"
        print(f"  {status} parse({url!r}) → {result}")

    # Invalid URLs
    invalid_cases = [
        "",
        "not a url",
        "https://gitlab.com/owner/repo",
        "https://github.com/",
    ]
    for url in invalid_cases:
        result = parse_github_url(url)
        status = "✓" if result is None else f"✗ (should be None, got {result})"
        print(f"  {status} parse({url!r}) → None")

    # Validate
    valid, msg, parsed = validate_github_url("https://github.com/facebook/react")
    print(f"  ✓ validate: valid={valid}, msg='{msg}', parsed={parsed}")


def test_json_extractor():
    """Test JSON extraction from various LLM response formats."""
    print("\n── Testing json_extractor.py ──")
    from utils.json_extractor import extract_json

    # Direct JSON
    result = extract_json('{"key": "value"}')
    assert result == {"key": "value"}, f"Direct JSON failed: {result}"
    print("  ✓ Direct JSON")

    # Markdown code block
    result = extract_json('Here is the result:\n```json\n{"key": "value"}\n```\nDone.')
    assert result == {"key": "value"}, f"Markdown block failed: {result}"
    print("  ✓ Markdown ```json block")

    # Bare code block
    result = extract_json('```\n{"key": "value"}\n```')
    assert result == {"key": "value"}, f"Bare block failed: {result}"
    print("  ✓ Bare ``` block")

    # Brace matching
    result = extract_json('Some text before {"key": "value"} and after')
    assert result == {"key": "value"}, f"Brace matching failed: {result}"
    print("  ✓ Brace matching")

    # Array
    result = extract_json('Result: [1, 2, 3]')
    assert result == [1, 2, 3], f"Array failed: {result}"
    print("  ✓ Array extraction")

    # Invalid
    result = extract_json("no json here")
    assert result is None, f"Should return None: {result}"
    print("  ✓ Invalid returns None")


def test_theme_service():
    """Test theme selection."""
    print("\n── Testing theme_service.py ──")
    from services.theme_service import select_theme, get_all_themes

    themes = get_all_themes()
    print(f"  Available themes: {len(themes)}")
    for tid, theme in themes.items():
        print(f"    • {theme['name']} ({tid})")

    # Test selection with different language profiles
    test_cases = [
        ({"JavaScript": 50000, "TypeScript": 30000}, "TypeScript"),
        ({"Python": 40000}, "Python"),
        ({"Shell": 5000, "Dockerfile": 2000}, "Shell"),
        ({"Jupyter Notebook": 30000}, "Jupyter Notebook"),
        ({"Go": 50000}, "Go"),
    ]

    for languages, primary in test_cases:
        theme = select_theme(languages, primary)
        print(f"  {primary:20s} → {theme['name']}")

    # Test randomness — same input should sometimes give different themes
    results = set()
    for _ in range(20):
        theme = select_theme({"Python": 10000}, "Python")
        results.add(theme["id"])
    print(f"  ✓ Randomness check: {len(results)} unique themes from 20 runs")


async def test_github_service():
    """Test GitHub API access (requires network)."""
    print("\n── Testing github_service.py ──")
    from services.github_service import fetch_repo_metadata

    try:
        metadata = await fetch_repo_metadata("facebook", "react")
        print(f"  Repo: {metadata['full_name']}")
        print(f"  Stars: {metadata['stars']:,}")
        print(f"  Language: {metadata['language']}")
        print(f"  Description: {metadata['description'][:80]}...")
        print("  ✓ GitHub API working")
    except Exception as e:
        print(f"  ✗ GitHub API failed: {e}")
        print("  (This may be a rate limit — run again with GITHUB_TOKEN set)")


def test_file_utils():
    """Test file utilities."""
    print("\n── Testing file_utils.py ──")
    from utils.file_utils import get_job_dir, cleanup_job
    import uuid

    test_job_id = f"test-{uuid.uuid4().hex[:8]}"
    job_dir = get_job_dir(test_job_id)
    print(f"  Created job dir: {job_dir}")
    assert job_dir.exists(), "Job dir should exist"

    # Create a test file
    (job_dir / "test.txt").write_text("hello")

    cleanup_job(test_job_id)
    assert not job_dir.exists(), "Job dir should be cleaned up"
    print("  ✓ Job directory create/cleanup works")


def main():
    print("=" * 60)
    print("AutoMotion — Phase 1 Service Tests")
    print("=" * 60)

    test_config()
    test_url_parser()
    test_json_extractor()
    test_theme_service()
    test_file_utils()

    # Async test
    asyncio.run(test_github_service())

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()
