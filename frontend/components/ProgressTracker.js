"use client";

import { useEffect, useState, useRef } from "react";

const STEPS = [
  {
    key: "parse_url",
    label: "Parsing GitHub URL",
    hint: "Validating repository format",
  },
  {
    key: "fetch_github_data",
    label: "Fetching repository data",
    hint: "Reading README, tree & source files",
  },
  {
    key: "analyze_repo",
    label: "Analyzing codebase",
    hint: "Agent #1 — Qwen2.5-Coder-32B",
  },
  {
    key: "write_script",
    label: "Writing narration script",
    hint: "Agent #2 — Qwen2.5-72B",
  },
  {
    key: "generate_voice",
    label: "Generating voiceover",
    hint: "ElevenLabs TTS",
  },
  {
    key: "calculate_frames",
    label: "Calculating scene timing",
    hint: "Proportional frame distribution",
  },
  {
    key: "render_video",
    label: "Rendering video",
    hint: "Remotion — 1920×1080 H.264",
  },
];

export default function ProgressTracker({ jobId, onComplete, onError }) {
  const [currentStep, setCurrentStep] = useState("");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("Connecting to server...");
  const [wsStatus, setWsStatus] = useState("connecting"); // connecting | connected | polling | done | error

  // Stable refs so the effect closure doesn't go stale
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);
  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  useEffect(() => {
    if (!jobId) return;

    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    const wsBase = backendUrl.replace(/^http/, "ws");

    let done = false;
    let ws = null;
    let pingTimer = null;
    let pollTimer = null;

    // ── Shared data handler ──────────────────────────────────────
    function handleData(data) {
      if (done) return;

      // Ignore keepalive frames
      if (data.type === "ping" || data.type === "pong") return;

      setCurrentStep(data.step || "");
      setProgress(data.progress || 0);
      setMessage(data.message || "");

      if (data.status === "completed") {
        done = true;
        setProgress(100);
        setWsStatus("done");
        cleanup();
        onCompleteRef.current && onCompleteRef.current(data.video_url);
      } else if (data.status === "failed") {
        done = true;
        setWsStatus("error");
        cleanup();
        onErrorRef.current &&
          onErrorRef.current(data.message || "Generation failed");
      }
    }

    // ── Polling fallback ─────────────────────────────────────────
    function startPolling() {
      if (pollTimer || done) return;
      setWsStatus("polling");
      setMessage("Polling for updates...");

      pollTimer = setInterval(async () => {
        if (done) {
          clearInterval(pollTimer);
          return;
        }
        try {
          const res = await fetch(`${backendUrl}/api/status/${jobId}`);
          if (!res.ok) return;
          const data = await res.json();
          handleData(data);
        } catch {
          // network hiccup — keep polling
        }
      }, 2500);
    }

    // ── Cleanup ──────────────────────────────────────────────────
    function cleanup() {
      clearInterval(pingTimer);
      clearInterval(pollTimer);
      if (ws) {
        try {
          ws.close();
        } catch {
          /* ignore */
        }
      }
    }

    // ── WebSocket ────────────────────────────────────────────────
    try {
      ws = new WebSocket(`${wsBase}/ws/progress/${jobId}`);

      ws.onopen = () => {
        if (done) {
          ws.close();
          return;
        }
        setWsStatus("connected");
        setMessage("Connected — pipeline starting...");

        // Send a keepalive ping every 25 s to prevent proxy timeouts
        pingTimer = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
          }
        }, 25_000);
      };

      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          // Echo pong back for server-side keepalive
          if (data.type === "ping") {
            if (ws.readyState === WebSocket.OPEN)
              ws.send(JSON.stringify({ type: "pong" }));
            return;
          }
          handleData(data);
        } catch {
          // malformed frame — ignore
        }
      };

      ws.onerror = () => {
        // onerror is always followed by onclose — start polling there
      };

      ws.onclose = () => {
        clearInterval(pingTimer);
        if (!done) startPolling();
      };
    } catch {
      // WebSocket constructor failed (e.g. unsupported env)
      startPolling();
    }

    return () => {
      done = true;
      cleanup();
    };
  }, [jobId]); // intentionally only jobId — callbacks go through refs

  // ── Helpers ─────────────────────────────────────────────────────
  function stepStatus(stepKey) {
    if (wsStatus === "done") return "done";
    const currentIdx = STEPS.findIndex((s) => s.key === currentStep);
    const thisIdx = STEPS.findIndex((s) => s.key === stepKey);
    if (thisIdx < 0) return "pending";
    if (currentIdx < 0) return "pending";
    if (thisIdx < currentIdx) return "done";
    if (thisIdx === currentIdx) return "active";
    return "pending";
  }

  function statusText() {
    if (wsStatus === "done") return "✓ Complete";
    if (wsStatus === "error") return "✗ Failed";
    if (wsStatus === "polling") return `Polling… ${progress}%`;
    if (wsStatus === "connecting") return "Connecting…";
    return `${progress}%`;
  }

  return (
    <div className="tracker-card">
      {/* Progress bar */}
      <div className="progress-bar-wrap">
        <div
          className="progress-bar-fill"
          style={{ width: `${progress}%` }}
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
          role="progressbar"
        />
      </div>

      {/* Step list */}
      <div className="tracker-steps">
        {STEPS.map((step, i) => {
          const status = stepStatus(step.key);
          return (
            <div key={step.key} className="tracker-step">
              {/* Icon */}
              <div
                className={`step-icon${status === "done" ? " done" : status === "active" ? " active" : ""}`}
              >
                {status === "done" ? "✓" : String(i + 1).padStart(2, "0")}
              </div>

              {/* Labels */}
              <div className="step-info">
                <div
                  className={`step-label${status === "done" ? " done" : status === "active" ? " active" : ""}`}
                >
                  {step.label}
                </div>
                {status === "active" && (
                  <div className="step-sublabel">{message || step.hint}</div>
                )}
                {status !== "active" && (
                  <div className="step-sublabel" style={{ opacity: 0.5 }}>
                    {step.hint}
                  </div>
                )}
              </div>

              {/* Done checkmark on right */}
              {status === "done" && <div className="step-check">done</div>}

              {/* Spinner for active */}
              {status === "active" && (
                <div className="spinner" aria-label="In progress" />
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="tracker-footer">
        <span className="tracker-status-text">
          {wsStatus === "polling"
            ? "⚡ Polling mode"
            : wsStatus === "connected"
              ? "⚡ Live"
              : ""}
          {wsStatus === "connecting" ? "Connecting…" : ""}
        </span>
        <span className="tracker-pct">{statusText()}</span>
      </div>
    </div>
  );
}
