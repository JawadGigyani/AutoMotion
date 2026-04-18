"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RepoInput() {
  const [url, setUrl] = useState("");
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
      const res = await fetch(`${backendUrl}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: normalizedUrl }),
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

        {error && <div className="input-error">{error}</div>}
      </form>
    </div>
  );
}
