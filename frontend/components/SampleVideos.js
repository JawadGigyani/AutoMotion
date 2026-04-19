"use client";

import { useEffect, useState, useCallback } from "react";

const THEME_COLORS = {
  "Dark Cinematic": "#6c63ff",
  "Neon Cyberpunk": "#ff00ff",
  "Minimal Light": "#3b82f6",
  "Terminal Green": "#00ff41",
  "Ocean Depth": "#64ffda",
};

function extractRepoName(url) {
  if (!url) return "Unknown";
  const cleaned = url
    .replace(/\/$/, "")
    .replace(/^https?:\/\/(www\.)?github\.com\//, "");
  return cleaned.split("/").slice(0, 2).join("/") || url;
}

export default function SampleVideos() {
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeVideo, setActiveVideo] = useState(null);

  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  useEffect(() => {
    async function fetchSamples() {
      try {
        const res = await fetch(`${backendUrl}/api/gallery`);
        if (res.ok) {
          const data = await res.json();
          setSamples(data);
        }
      } catch {
        /* backend offline */
      } finally {
        setLoading(false);
      }
    }
    fetchSamples();
  }, [backendUrl]);

  const closeModal = useCallback(() => setActiveVideo(null), []);

  useEffect(() => {
    if (!activeVideo) return;
    function onKey(e) {
      if (e.key === "Escape") closeModal();
    }
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
    };
  }, [activeVideo, closeModal]);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "40px 0", color: "var(--text-dim)" }}>
        <div className="spinner" style={{ width: 20, height: 20, margin: "0 auto 12px" }} />
        Loading samples…
      </div>
    );
  }

  if (samples.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px 0", color: "var(--text-dim)", fontSize: 14 }}>
        Sample videos unavailable — start the backend to see demos.
      </div>
    );
  }

  function resolveUrl(path) {
    if (!path) return null;
    return path.startsWith("http") ? path : `${backendUrl}${path}`;
  }

  return (
    <>
      <div className="samples-grid">
        {samples.map((entry) => {
          const repoName = extractRepoName(entry.repo_url);
          const themeColor = THEME_COLORS[entry.theme] || "#888";
          const thumbSrc = resolveUrl(entry.thumbnail_url);

          return (
            <div key={entry.job_id} className="sample-card">
              <div
                className="sample-thumb"
                style={{
                  background: thumbSrc
                    ? "#000"
                    : `linear-gradient(135deg, ${themeColor}22 0%, ${themeColor}08 100%)`,
                }}
              >
                {thumbSrc ? (
                  <img
                    src={thumbSrc}
                    alt={`${repoName} preview`}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    onError={(e) => { e.target.style.display = "none"; }}
                  />
                ) : (
                  <div style={{ fontSize: 36, opacity: 0.3 }}>▶</div>
                )}
              </div>

              <div className="sample-meta">
                <div className="sample-repo" title={entry.repo_url}>
                  {repoName}
                </div>
                <span
                  className="sample-theme"
                  style={{ borderColor: themeColor, color: themeColor }}
                >
                  {entry.theme || "Auto"}
                </span>
              </div>

              <div className="sample-action">
                <button
                  type="button"
                  className="btn-primary sample-btn"
                  onClick={() => setActiveVideo(entry)}
                >
                  Watch
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {activeVideo && (
        <div className="video-modal-overlay" onClick={closeModal}>
          <div className="video-modal" onClick={(e) => e.stopPropagation()}>

            <div className="video-modal-body">
              <button
                type="button"
                className="video-modal-close"
                onClick={closeModal}
                aria-label="Close"
              >
                ✕
              </button>
              <video
                className="video-modal-player"
                controls
                autoPlay
                playsInline
                crossOrigin="anonymous"
              >
                <source src={resolveUrl(activeVideo.video_url)} type="video/mp4" />
                {activeVideo.subtitle_url && (
                  <track
                    kind="captions"
                    src={resolveUrl(activeVideo.subtitle_url)}
                    srcLang="en"
                    label="English"
                    default
                  />
                )}
              </video>
            </div>

            <div className="video-modal-info">
              <div className="video-modal-repo">
                {extractRepoName(activeVideo.repo_url)}
              </div>
              <div className="video-modal-actions">
                {activeVideo.repo_url && (
                  <a
                    href={activeVideo.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary"
                  >
                    View on GitHub ↗
                  </a>
                )}
              </div>
            </div>

          </div>
        </div>
      )}
    </>
  );
}
