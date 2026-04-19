"use client";

import { Suspense, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
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

  // Called by ProgressTracker when the WS/poll signals completion
  const handleComplete = useCallback(
    async (relativeVideoUrl) => {
      const backendUrl =
        process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

      // relativeVideoUrl looks like "/outputs/{jobId}/video.mp4"
      const fullUrl = relativeVideoUrl
        ? `${backendUrl}${relativeVideoUrl}`
        : `${backendUrl}/outputs/${jobId}/video.mp4`;

      // Optionally fetch the result endpoint to get the theme name
      try {
        const res = await fetch(`${backendUrl}/api/result/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.theme) setTheme(data.theme);
          if (data.subtitle_url) setSubtitleUrl(`${backendUrl}${data.subtitle_url}`);
        }
      } catch {
        // theme is cosmetic — don't fail if fetch errors
      }

      setVideoUrl(fullUrl);
      setPageStatus("completed");
    },
    [jobId],
  );

  const handleError = useCallback((msg) => {
    setErrorMsg(msg || "An unknown error occurred during generation.");
    setPageStatus("failed");
  }, []);

  // ── No job ID ───────────────────────────────────────────────────────────
  if (!jobId) {
    return (
      <main className="gen-page">
        <nav className="nav animate-enter">
          <div className="container nav-inner">
            <Link href="/" className="gen-back-link">
              ← AutoMotion
            </Link>
            <div className="nav-logo">
              AutoMotion
            </div>
          </div>
        </nav>
        <div className="container gen-content">
          <div className="animate-enter" style={{ textAlign: "center", paddingTop: 48 }}>
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

  // ── Main page ────────────────────────────────────────────────────────────
  return (
    <main className="gen-page">
      {/* Nav */}
      <nav className="nav animate-enter">
        <div className="container nav-inner">
          <Link href="/" className="gen-back-link">
            ← AutoMotion
          </Link>
          <div className="nav-logo">
            AutoMotion
          </div>
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

        {/* Progress tracker — always rendered until done/failed so the
            WebSocket lifecycle runs to completion cleanly */}
        {pageStatus !== "failed" && (
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

        {/* Video player — shown once complete */}
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

        {/* Actions row — shown after any terminal state */}
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

// ── Page export with Suspense (required for useSearchParams) ─────────────
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
              <div className="nav-logo">
                AutoMotion
              </div>
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
