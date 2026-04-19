"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const THEMES = [
  { id: "auto", name: "Auto (recommended)" },
  { id: "dark_cinematic", name: "Dark Cinematic" },
  { id: "neon_cyberpunk", name: "Neon Cyberpunk" },
  { id: "minimal_light", name: "Minimal Light" },
  { id: "terminal_green", name: "Terminal Green" },
  { id: "ocean_depth", name: "Ocean Depth" },
];

const VOICES = [
  { id: "auto", name: "Default" },
  { id: "CwhRBWXzGAHq8TQ4Fs17", name: "Roger — Casual" },
  { id: "EXAVITQu4vr4xnSDxMaL", name: "Sarah — Professional" },
  { id: "IKne3meq5aSn9XLyUdCD", name: "Charlie — Energetic" },
  { id: "JBFqnCBsd6RMkjVDRZzb", name: "George — Storyteller" },
  { id: "FGY2WhTYpPnrIDTdsKH5", name: "Laura — Enthusiastic" },
];

export default function RepoInput() {
  const [url, setUrl] = useState("");
  const [themeId, setThemeId] = useState("auto");
  const [voiceId, setVoiceId] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const isValidGithubUrl = (value) => {
    const trimmed = value.trim();
    // Accept full URLs or owner/repo shorthand
    return (
      /^https?:\/\/(www\.)?github\.com\/[\w.-]+\/[\w.-]+(\/.*)?$/.test(
        trimmed,
      ) ||
      /^github\.com\/[\w.-]+\/[\w.-]+(\/.*)?$/.test(trimmed) ||
      /^[\w.-]+\/[\w.-]+$/.test(trimmed)
    );
  };

  const normalizeUrl = (value) => {
    const trimmed = value.trim();
    if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
      return trimmed;
    }
    if (trimmed.startsWith("github.com/")) {
      return `https://${trimmed}`;
    }
    // owner/repo shorthand
    return `https://github.com/${trimmed}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmed = url.trim();
    if (!trimmed) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    if (!isValidGithubUrl(trimmed)) {
      setError(
        "Please enter a valid GitHub repository URL (e.g. github.com/owner/repo).",
      );
      return;
    }

    setError("");
    setLoading(true);

    const normalizedUrl = normalizeUrl(trimmed);
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

    try {
      const body = { repo_url: normalizedUrl };
      if (themeId && themeId !== "auto") {
        body.theme_id = themeId;
      }
      if (voiceId && voiceId !== "auto") {
        body.voice_id = voiceId;
      }

      const res = await fetch(`${backendUrl}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        let msg = `Server error (${res.status})`;
        try {
          const errData = await res.json();
          msg = errData.detail || errData.message || msg;
        } catch (_) {}
        throw new Error(msg);
      }

      const data = await res.json();
      const jobId = data.job_id;

      if (!jobId) {
        throw new Error("No job ID returned from server.");
      }

      router.push(
        `/generate?job_id=${encodeURIComponent(jobId)}&repo_url=${encodeURIComponent(normalizedUrl)}`,
      );
    } catch (err) {
      setError(
        err.message ||
          "Could not reach the backend. Make sure the server is running on port 8000.",
      );
      setLoading(false);
    }
  };

  return (
    <div className="repo-input-form">
      <form onSubmit={handleSubmit}>
        <div className="input-row">
          <input
            className="url-input"
            type="text"
            placeholder="https://github.com/owner/repo"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (error) setError("");
            }}
            disabled={loading}
            autoFocus
            autoComplete="off"
            spellCheck={false}
            aria-label="GitHub repository URL"
          />
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner" />
                Starting…
              </>
            ) : (
              <>Generate →</>
            )}
          </button>
        </div>

        {/* Theme & Voice selectors */}
        <div className="options-row">
          <div className="option-group">
            <label className="option-label" htmlFor="theme-select">Theme</label>
            <select
              id="theme-select"
              className="option-select"
              value={themeId}
              onChange={(e) => setThemeId(e.target.value)}
              disabled={loading}
            >
              {THEMES.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div className="option-group">
            <label className="option-label" htmlFor="voice-select">Voice</label>
            <select
              id="voice-select"
              className="option-select"
              value={voiceId}
              onChange={(e) => setVoiceId(e.target.value)}
              disabled={loading}
            >
              {VOICES.map((v) => (
                <option key={v.id} value={v.id}>{v.name}</option>
              ))}
            </select>
          </div>
        </div>

        {error && <div className="input-error">{error}</div>}
      </form>
    </div>
  );
}
