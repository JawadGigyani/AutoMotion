"use client";

import { Suspense, useState, useCallback, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import ProgressTracker from "@/components/ProgressTracker";
import VideoPlayer from "@/components/VideoPlayer";

// ── Inner component (needs useSearchParams inside Suspense) ──────────────
function GenerateContent() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get("job_id") || "";
  const repoUrl = searchParams.get("repo_url") || "";

  const [pageStatus, setPageStatus] = useState("in_progress"); // in_progress | completed | failed
  const [videoUrl, setVideoUrl] = useState("");
  const [subtitleUrl, setSubtitleUrl] = useState("");
  const [theme, setTheme] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  // When true the job was already done before we connected — skip the tracker
  const [isAlreadyDone, setIsAlreadyDone] = useState(false);

  // ── Immediate status check on mount ─────────────────────────────────────
  // When a user navigates here from the gallery ("Watch"), the job may already
  // be completed.  Without this check they'd stare at "Connecting…" for ~120 s
  // while the WebSocket times out before polling kicks in.
  useEffect(() => {
    if (!jobId) return;

    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

    let cancelled = false;

    (async () => {
      try {
        const res = await fetch(`${backendUrl}/api/status/${jobId}`);
        if (!res.ok || cancelled) return;
        const data = await res.json();

        if (data.status === "completed" && data.video_url) {
          const fullUrl = `${backendUrl}${data.video_url}`;

          // Also grab subtitle and theme from the result endpoint
          try {
            const res2 = await fetch(`${backendUrl}/api/result/${jobId}`);
            if (res2.ok && !cancelled) {
              const result = await res2.json();
              if (result.theme) setTheme(result.theme);
              if (result.subtitle_url)
                setSubtitleUrl(`${backendUrl}${result.subtitle_url}`);
            }
          } catch {
            /* cosmetic — ignore */
          }

          if (!cancelled) {
            setVideoUrl(fullUrl);
            setIsAlreadyDone(true);
            setPageStatus("completed");
          }
        } else if (data.status === "failed" && !cancelled) {
          setErrorMsg(data.error || "Generation failed");
          setIsAlreadyDone(true);
          setPageStatus("failed");
        }
        // If status is "pending" or "processing", fall through to normal WS flow
      } catch {
        /* network error — fall through to normal WS/polling flow */
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  // ── Called by ProgressTracker when the WS/poll signals completion ────────
  const handleComplete = useCallback(
    async (relativeVideoUrl) => {
      const backendUrl =
        process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

      const fullUrl = relativeVideoUrl
        ? `${backendUrl}${relativeVideoUrl}`
        : `${backendUrl}/outputs/${jobId}/video.mp4`;

      let themeName = "";
      let subtitleRel = "";

      try {
        const res = await fetch(`${backendUrl}/api/result/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.theme) {
            themeName = data.theme;
            setTheme(data.theme);
          }
          if (data.subtitle_url) {
            subtitleRel = data.subtitle_url;
            setSubtitleUrl(`${backendUrl}${data.subtitle_url}`);
          }
        }
      } catch {
        /* cosmetic */
      }

      setVideoUrl(fullUrl);
      setPageStatus("completed");

      // Persist to sessionStorage for the gallery page
      try {
        const existing = JSON.parse(
          sessionStorage.getItem("automotion_gallery") || "[]",
        );
        if (!existing.find((e) => e.job_id === jobId)) {
          existing.unshift({
            job_id: jobId,
            repo_url: decodeURIComponent(repoUrl),
            theme: themeName,
            video_url: relativeVideoUrl || `/outputs/${jobId}/video.mp4`,
            subtitle_url: subtitleRel || null,
            created_at: new Date().toISOString(),
            is_sample: false,
          });
          sessionStorage.setItem(
            "automotion_gallery",
            JSON.stringify(existing.slice(0, 20)),
          );
        }
      } catch {
        /* sessionStorage unavailable */
      }
    },
    [jobId, repoUrl],
  );

  const handleError = useCallback((msg) => {
    setErrorMsg(msg || "An unknown error occurred during generation.");
    setPageStatus("failed");
  }, []);

  // ── No job ID ─────────────────────────────────────────────────────────────
  if (!jobId) {
    return (
      <main className="gen-page">
        <nav className="nav animate-enter">
          <div className="container nav-inner">
            <Link href="/" className="gen-back-link">
              ← AutoMotion
            </Link>
            <div className="nav-logo">AutoMotion</div>
            <a href="/gallery" className="nav-link">
              Gallery →
            </a>
          </div>
        </nav>
        <div className="container gen-content">
          <div
            className="animate-enter"
            style={{ textAlign: "center", paddingTop: 48 }}
          >
            <p style={{ color: "var(--text-muted)", marginBottom: 24 }}>
              No job ID found. Please start a new generation.
            </p>
            <Link href="/" className="btn-primary">
              ← Back to Home
            </Link>
          </div>
        </div>
      </main>
    );
  }

  // ── Main page ─────────────────────────────────────────────────────────────
  return (
    <main className="gen-page">
      {/* Nav */}
      <nav className="nav animate-enter">
        <div className="container nav-inner">
          <Link href="/" className="gen-back-link">
            ← AutoMotion
          </Link>
          <div className="nav-logo">AutoMotion</div>
          <a href="/gallery" className="nav-link">
            Gallery →
          </a>
        </div>
      </nav>

      <div className="container gen-content">
        {/* Heading */}
        <div className="gen-heading animate-enter">
          <h1 className="gen-title">
            {pageStatus === "completed"
              ? "Your video is ready"
              : pageStatus === "failed"
                ? "Generation failed"
                : "Processing Repository…"}
          </h1>
          {repoUrl && (
            <div className="gen-repo-url">{decodeURIComponent(repoUrl)}</div>
          )}
        </div>

        {/* Progress tracker — hidden if job was already done when we arrived */}
        {pageStatus !== "failed" && !isAlreadyDone && (
          <div className="animate-enter" style={{ animationDelay: "100ms" }}>
            <ProgressTracker
              jobId={jobId}
              onComplete={handleComplete}
              onError={handleError}
            />
          </div>
        )}

        {/* Error card */}
        {pageStatus === "failed" && (
          <div className="error-card animate-enter">
            <div className="error-title">✗ Generation failed</div>
            <div className="error-body">{errorMsg}</div>
          </div>
        )}

        {/* Video player */}
        {pageStatus === "completed" && videoUrl && (
          <div className="animate-enter">
            <VideoPlayer
              videoUrl={videoUrl}
              subtitleUrl={subtitleUrl}
              repoUrl={decodeURIComponent(repoUrl)}
              theme={theme}
            />
          </div>
        )}

        {/* Action buttons */}
        {(pageStatus === "completed" || pageStatus === "failed") && (
          <div className="action-row animate-enter" style={{ marginTop: 16 }}>
            <Link href="/" className="btn-primary">
              Generate Another →
            </Link>
            {pageStatus === "failed" && (
              <button
                className="btn-secondary"
                type="button"
                onClick={() => window.location.reload()}
              >
                Retry
              </button>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

// ── Page export wrapped in Suspense (required for useSearchParams) ─────────
export default function GeneratePage() {
  return (
    <Suspense
      fallback={
        <main className="gen-page">
          <nav className="nav animate-enter">
            <div className="container nav-inner">
              <Link href="/" className="gen-back-link">
                ← AutoMotion
              </Link>
              <div className="nav-logo">AutoMotion</div>
            </div>
          </nav>
          <div className="container gen-content">
            <div
              className="animate-enter"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                color: "var(--text-muted)",
              }}
            >
              <span className="spinner" />
              <span style={{ fontSize: 14, fontFamily: "var(--font-mono)" }}>
                Initializing connection…
              </span>
            </div>
          </div>
        </main>
      }
    >
      <GenerateContent />
    </Suspense>
  );
}
