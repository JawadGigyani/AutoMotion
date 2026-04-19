"use client";

import { Suspense, useState, useCallback, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import ProgressTracker from "@/components/ProgressTracker";
import VideoPlayer from "@/components/VideoPlayer";

function GenerateContent() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get("job_id") || "";
  const repoUrl = searchParams.get("repo_url") || "";

  const [pageStatus, setPageStatus] = useState("in_progress");
  const [videoUrl, setVideoUrl] = useState("");
  const [subtitleUrl, setSubtitleUrl] = useState("");
  const [thumbnailUrl, setThumbnailUrl] = useState("");
  const [theme, setTheme] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [isAlreadyDone, setIsAlreadyDone] = useState(false);

  const videoUrlParam = searchParams.get("video_url");
  const themeParam = searchParams.get("theme");

  useEffect(() => {
    if (!videoUrlParam) return;
    setVideoUrl(decodeURIComponent(videoUrlParam));
    if (themeParam) setTheme(decodeURIComponent(themeParam));
    setIsAlreadyDone(true);
    setPageStatus("completed");
  }, [videoUrlParam, themeParam]);

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

          try {
            const res2 = await fetch(`${backendUrl}/api/result/${jobId}`);
            if (res2.ok && !cancelled) {
              const result = await res2.json();
              if (result.theme) setTheme(result.theme);
              if (result.subtitle_url)
                setSubtitleUrl(`${backendUrl}${result.subtitle_url}`);
              if (result.thumbnail_url)
                setThumbnailUrl(`${backendUrl}${result.thumbnail_url}`);
            }
          } catch {
            /* cosmetic */
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
      } catch {
        /* network error — fall through to WS/polling */
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  const handleComplete = useCallback(
    async (relativeVideoUrl) => {
      const backendUrl =
        process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

      const fullUrl = relativeVideoUrl
        ? `${backendUrl}${relativeVideoUrl}`
        : `${backendUrl}/outputs/${jobId}/video.mp4`;

      try {
        const res = await fetch(`${backendUrl}/api/result/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.theme) setTheme(data.theme);
          if (data.subtitle_url)
            setSubtitleUrl(`${backendUrl}${data.subtitle_url}`);
          if (data.thumbnail_url)
            setThumbnailUrl(`${backendUrl}${data.thumbnail_url}`);
        }
      } catch {
        /* cosmetic */
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

  if (!jobId && !videoUrlParam) {
    return (
      <main className="gen-page">
        <nav className="nav animate-enter">
          <div className="container nav-inner">
            <Link href="/" className="nav-logo">
              ← AutoMotion
            </Link>
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

  return (
    <main className="gen-page">
      <nav className="nav animate-enter">
        <div className="container nav-inner">
          <Link href="/" className="nav-logo">
            ← AutoMotion
          </Link>
        </div>
      </nav>

      <div className="container gen-content">
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

        {pageStatus !== "failed" && !isAlreadyDone && (
          <div className="animate-enter" style={{ animationDelay: "100ms" }}>
            <ProgressTracker
              jobId={jobId}
              onComplete={handleComplete}
              onError={handleError}
            />
          </div>
        )}

        {pageStatus === "failed" && (
          <div className="error-card animate-enter">
            <div className="error-title">✗ Generation failed</div>
            <div className="error-body">{errorMsg}</div>
          </div>
        )}

        {pageStatus === "completed" && videoUrl && (
          <div className="animate-enter">
            <VideoPlayer
              videoUrl={videoUrl}
              subtitleUrl={subtitleUrl}
              thumbnailUrl={thumbnailUrl}
              repoUrl={decodeURIComponent(repoUrl)}
              theme={theme}
            />
          </div>
        )}

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

export default function GeneratePage() {
  return (
    <Suspense
      fallback={
        <main className="gen-page">
          <nav className="nav animate-enter">
            <div className="container nav-inner">
              <Link href="/" className="nav-logo">
                ← AutoMotion
              </Link>
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
