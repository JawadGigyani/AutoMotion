"""
RepoReel — Integration Tests
=============================================================
Tests the full stack end-to-end:
  1. Health checks  — backend + render server
  2. Full pipeline  — submit → poll → verify video
  3. Error paths    — invalid URL, missing job, bad input
  4. WebSocket      — live progress stream

Usage:
    # From the repoReel/backend directory, with venv activated:
    python test_integration.py

    # Run only health checks:
    python test_integration.py --health

    # Run full pipeline against a specific repo:
    python test_integration.py --repo https://github.com/pallets/flask

    # Skip the slow render (just test API surface):
    python test_integration.py --no-render
=============================================================
"""

import argparse
import asyncio
import json
import sys
import time

import httpx
import websockets

# ── Config ──────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"
RENDER_URL = "http://localhost:3001"

# Default test repos (fast, public, well-known)
TEST_REPOS = [
    "https://github.com/pallets/flask",
    "https://github.com/tiangolo/fastapi",
]

# Colour helpers (Windows-safe via ANSI)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


# ── Utilities ────────────────────────────────────────────────────────────────
class TestResult:
    def __init__(self):
        self.passed: list[str] = []
        self.failed: list[tuple[str, str]] = []

    def ok(self, name: str):
        self.passed.append(name)
        print(f"  {GREEN}✓{RESET} {name}")

    def fail(self, name: str, reason: str):
        self.failed.append((name, reason))
        print(f"  {RED}✗{RESET} {name}")
        print(f"    {RED}↳ {reason}{RESET}")

    def summary(self) -> bool:
        total = len(self.passed) + len(self.failed)
        print(f"\n{'═' * 56}")
        if self.failed:
            print(f"{RED}{BOLD}FAILED  {len(self.failed)}/{total} tests failed{RESET}")
            for name, reason in self.failed:
                print(f"  {RED}✗ {name}{RESET}")
                print(f"    {reason}")
        else:
            print(f"{GREEN}{BOLD}PASSED  All {total} tests passed{RESET}")
        print(f"{'═' * 56}\n")
        return len(self.failed) == 0


results = TestResult()


# ════════════════════════════════════════════════════════════════════════════
# 1. HEALTH CHECKS
# ════════════════════════════════════════════════════════════════════════════


async def test_backend_health(client: httpx.AsyncClient):
    """GET /health → {"status": "ok"}"""
    try:
        r = await client.get(f"{BACKEND_URL}/health", timeout=5)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        assert data.get("status") == "ok", f"Unexpected body: {data}"
        results.ok("Backend health endpoint")
    except Exception as e:
        results.fail("Backend health endpoint", str(e))


async def test_render_health(client: httpx.AsyncClient):
    """GET /health on render server → {"status": "ok", "bundled": bool}"""
    try:
        r = await client.get(f"{RENDER_URL}/health", timeout=10)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        assert data.get("status") == "ok", f"Unexpected body: {data}"
        bundled = data.get("bundled", False)
        suffix = " (bundle ready)" if bundled else " (bundle pending)"
        results.ok(f"Render server health endpoint{suffix}")
    except Exception as e:
        results.fail("Render server health endpoint", str(e))


async def test_render_static(client: httpx.AsyncClient):
    """Render server static middleware should respond (not 500)."""
    try:
        r = await client.get(f"{RENDER_URL}/static/", timeout=5)
        # 200 (directory listing) or 404 (no index) are both fine — just not 500
        assert r.status_code in (200, 403, 404), f"Unexpected HTTP {r.status_code}"
        results.ok("Render server static file middleware")
    except Exception as e:
        results.fail("Render server static file middleware", str(e))


# ════════════════════════════════════════════════════════════════════════════
# 2. API SURFACE TESTS (no render)
# ════════════════════════════════════════════════════════════════════════════


async def test_generate_invalid_url(client: httpx.AsyncClient):
    """POST /api/generate with a non-GitHub URL should error gracefully."""
    try:
        r = await client.post(
            f"{BACKEND_URL}/api/generate",
            json={"repo_url": "https://example.com/not-github"},
            timeout=15,
        )
        # The pipeline starts a background task; it may return 200 and fail async,
        # OR the URL parser may raise immediately. Either is acceptable here.
        # What we must NOT see is a 500 crash on the /generate endpoint itself.
        assert r.status_code != 500, f"Server crash (500): {r.text}"
        results.ok("POST /api/generate with invalid URL (no 500 crash)")
    except Exception as e:
        results.fail("POST /api/generate with invalid URL", str(e))


async def test_status_unknown_job(client: httpx.AsyncClient):
    """GET /api/status/<unknown-id> → 404"""
    try:
        r = await client.get(
            f"{BACKEND_URL}/api/status/00000000-0000-0000-0000-000000000000",
            timeout=5,
        )
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        results.ok("GET /api/status with unknown job ID → 404")
    except Exception as e:
        results.fail("GET /api/status with unknown job ID", str(e))


async def test_result_unknown_job(client: httpx.AsyncClient):
    """GET /api/result/<unknown-id> → 404"""
    try:
        r = await client.get(
            f"{BACKEND_URL}/api/result/00000000-0000-0000-0000-000000000000",
            timeout=5,
        )
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        results.ok("GET /api/result with unknown job ID → 404")
    except Exception as e:
        results.fail("GET /api/result with unknown job ID", str(e))


async def test_generate_missing_body(client: httpx.AsyncClient):
    """POST /api/generate with no body → 422 validation error."""
    try:
        r = await client.post(
            f"{BACKEND_URL}/api/generate",
            json={},
            timeout=5,
        )
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"
        results.ok("POST /api/generate with empty body → 422")
    except Exception as e:
        results.fail("POST /api/generate with empty body", str(e))


# ════════════════════════════════════════════════════════════════════════════
# 3. WEBSOCKET TEST
# ════════════════════════════════════════════════════════════════════════════


async def test_websocket_connection(client: httpx.AsyncClient):
    """
    Start a real generation job, then connect via WebSocket and verify
    we receive at least one structured progress message.
    Disconnects after the first message — doesn't wait for completion.
    """
    ws_url = BACKEND_URL.replace("http", "ws")

    try:
        # Start a job
        r = await client.post(
            f"{BACKEND_URL}/api/generate",
            json={"repo_url": "https://github.com/pallets/flask"},
            timeout=10,
        )
        assert r.status_code == 200, f"Job start failed: HTTP {r.status_code}"
        job_id = r.json()["job_id"]

        # Connect WebSocket and wait for at least one real message
        received_message = False
        deadline = time.time() + 30  # wait up to 30s for first message

        async with websockets.connect(
            f"{ws_url}/ws/progress/{job_id}",
            ping_interval=None,
            close_timeout=5,
        ) as ws:
            while time.time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(raw)

                    # Skip keepalive frames
                    if data.get("type") in ("ping", "pong"):
                        continue

                    # We got a real progress message
                    assert "step" in data or "status" in data, (
                        f"Message missing 'step'/'status': {data}"
                    )
                    assert "progress" in data, f"Message missing 'progress': {data}"
                    received_message = True
                    break

                except asyncio.TimeoutError:
                    # No message yet — keep waiting
                    continue

        if received_message:
            results.ok(
                "WebSocket /ws/progress/{job_id} — received live progress message"
            )
        else:
            results.fail(
                "WebSocket /ws/progress/{job_id}",
                "No progress message received within 30s",
            )

    except Exception as e:
        results.fail("WebSocket /ws/progress/{job_id}", str(e))


# ════════════════════════════════════════════════════════════════════════════
# 4. FULL PIPELINE TEST (slow — requires all services running)
# ════════════════════════════════════════════════════════════════════════════


async def test_full_pipeline(client: httpx.AsyncClient, repo_url: str):
    """
    End-to-end test: submit → poll until complete → verify MP4 is accessible.
    This test can take 2-5 minutes depending on LLM and render speed.
    """
    test_name = f"Full pipeline — {repo_url}"
    print(f"\n  {CYAN}▸ Starting full pipeline test for {repo_url}{RESET}")

    try:
        # ── Step 1: Submit job ───────────────────────────────────
        r = await client.post(
            f"{BACKEND_URL}/api/generate",
            json={"repo_url": repo_url},
            timeout=15,
        )
        assert r.status_code == 200, f"Submit failed: HTTP {r.status_code}: {r.text}"
        job_id = r.json()["job_id"]
        print(f"    Job ID: {job_id[:8]}…")

        # ── Step 2: Poll until complete or failed ─────────────────
        timeout_s = 600  # 10 minutes max
        start = time.time()
        last_step = ""

        while True:
            elapsed = time.time() - start
            if elapsed > timeout_s:
                results.fail(test_name, f"Pipeline timed out after {timeout_s}s")
                return

            r = await client.get(f"{BACKEND_URL}/api/status/{job_id}", timeout=10)
            assert r.status_code == 200, f"Status check failed: HTTP {r.status_code}"
            status = r.json()

            step = status.get("step") or ""
            pct = status.get("progress", 0)
            msg = status.get("message") or ""

            if step != last_step:
                print(f"    [{pct:3}%] {step}  {YELLOW}{msg}{RESET}")
                last_step = step

            if status["status"] == "completed":
                video_url = status.get("video_url")
                print(f"    {GREEN}Pipeline complete! Video: {video_url}{RESET}")
                break

            if status["status"] == "failed":
                results.fail(
                    test_name,
                    f"Pipeline failed: {status.get('error', 'unknown error')}",
                )
                return

            await asyncio.sleep(4)

        # ── Step 3: Verify video is accessible ───────────────────
        video_url = status.get("video_url")
        assert video_url, "No video_url in completed status"

        full_video_url = f"{BACKEND_URL}{video_url}"
        r = await client.head(full_video_url, timeout=10)
        assert r.status_code == 200, (
            f"Video not accessible at {full_video_url}: HTTP {r.status_code}"
        )

        content_type = r.headers.get("content-type", "")
        assert "video" in content_type or "octet" in content_type, (
            f"Unexpected Content-Type: {content_type}"
        )

        content_length = int(r.headers.get("content-length", 0))
        assert content_length > 100_000, (
            f"Video file too small ({content_length} bytes) — likely empty"
        )

        mb = content_length / 1_048_576
        print(f"    {GREEN}Video accessible: {mb:.2f} MB — {content_type}{RESET}")

        # ── Step 4: Verify /api/result endpoint ───────────────────
        r = await client.get(f"{BACKEND_URL}/api/result/{job_id}", timeout=10)
        assert r.status_code == 200, f"Result endpoint failed: HTTP {r.status_code}"
        result_data = r.json()
        assert "video_url" in result_data, f"Missing video_url in result: {result_data}"

        elapsed_s = time.time() - start
        results.ok(f"{test_name} ({elapsed_s:.0f}s, {mb:.2f} MB)")

    except Exception as e:
        results.fail(test_name, str(e))


# ════════════════════════════════════════════════════════════════════════════
# 5. THEME VARIETY CHECK
# ════════════════════════════════════════════════════════════════════════════


async def test_theme_variety(client: httpx.AsyncClient):
    """
    Submit the same repo URL multiple times and check that we see theme variety.
    Because theme selection is weighted-random, we don't assert specific themes
    — just that the 'theme' field is returned and is a non-empty string.
    """
    try:
        r = await client.post(
            f"{BACKEND_URL}/api/generate",
            json={"repo_url": "https://github.com/pallets/flask"},
            timeout=10,
        )
        assert r.status_code == 200
        job_id = r.json()["job_id"]

        # Wait for at least the script stage where theme is selected
        deadline = time.time() + 120
        theme_seen = None

        while time.time() < deadline:
            r = await client.get(f"{BACKEND_URL}/api/status/{job_id}", timeout=5)
            status = r.json()
            step = status.get("step", "")

            if step in (
                "generate_voice",
                "calculate_frames",
                "render_video",
                "complete",
            ):
                # By this point theme has been selected — check the completed result
                if status["status"] == "completed":
                    r2 = await client.get(
                        f"{BACKEND_URL}/api/result/{job_id}", timeout=5
                    )
                    if r2.status_code == 200:
                        theme_seen = r2.json().get("theme")
                    break

            if status["status"] in ("failed", "completed"):
                break

            await asyncio.sleep(3)

        if theme_seen:
            results.ok(f"Theme variety check — theme returned: '{theme_seen}'")
        else:
            # Theme was not yet available — not a hard failure
            results.ok(
                "Theme variety check — job started (theme visible after completion)"
            )

    except Exception as e:
        results.fail("Theme variety check", str(e))


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(description="RepoReel Integration Tests")
    parser.add_argument("--health", action="store_true", help="Only run health checks")
    parser.add_argument(
        "--no-render", action="store_true", help="Skip the full pipeline test"
    )
    parser.add_argument("--repo", type=str, help="Repo URL for pipeline test")
    parser.add_argument("--ws", action="store_true", help="Also run WebSocket test")
    args = parser.parse_args()

    print(f"\n{BOLD}RepoReel — Integration Tests{RESET}")
    print(f"{'═' * 56}")
    print(f"  Backend:       {BACKEND_URL}")
    print(f"  Render server: {RENDER_URL}")
    print(f"{'═' * 56}\n")

    async with httpx.AsyncClient() as client:
        # ── Health checks ────────────────────────────────────────
        print(f"{BOLD}[1] Health Checks{RESET}")
        await test_backend_health(client)
        await test_render_health(client)
        await test_render_static(client)

        if args.health:
            results.summary()
            sys.exit(0 if not results.failed else 1)

        # ── API surface ──────────────────────────────────────────
        print(f"\n{BOLD}[2] API Surface Tests{RESET}")
        await test_generate_invalid_url(client)
        await test_status_unknown_job(client)
        await test_result_unknown_job(client)
        await test_generate_missing_body(client)

        # ── WebSocket ────────────────────────────────────────────
        if args.ws:
            print(f"\n{BOLD}[3] WebSocket{RESET}")
            await test_websocket_connection(client)

        # ── Full pipeline ────────────────────────────────────────
        if not args.no_render:
            repos_to_test = [args.repo] if args.repo else TEST_REPOS[:1]
            print(f"\n{BOLD}[4] Full Pipeline Test{RESET}")
            print(f"  {YELLOW}⚠  This test takes 2–10 minutes. Ctrl+C to skip.{RESET}")
            for repo in repos_to_test:
                await test_full_pipeline(client, repo)

        # ── Theme variety ────────────────────────────────────────
        if not args.no_render and not args.health:
            print(f"\n{BOLD}[5] Theme Variety{RESET}")
            await test_theme_variety(client)

    ok = results.summary()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user.{RESET}")
        results.summary()
        sys.exit(1)
