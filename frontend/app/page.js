import RepoInput from "@/components/RepoInput";

export default function Home() {
  return (
    <main>
      {/* ── Nav ── */}
      <nav className="nav">
        <div className="container nav-inner">
          <div className="nav-logo animate-enter" style={{ animationDelay: "0ms" }}>
            AutoMotion
          </div>
          <a href="/gallery" className="nav-link animate-enter" style={{ animationDelay: "50ms" }}>
            Gallery →
          </a>
        </div>
      </nav>

      <div className="container">
        {/* ── Hero ── */}
        <section className="hero animate-enter" style={{ animationDelay: "100ms" }}>
          <div className="hero-eyebrow">Automated Explainer Videos</div>

          <h1 className="hero-title">
            Transform any GitHub repository into an <em>automated video summary.</em>
          </h1>

          <p className="hero-subtitle">
            Provide a public GitHub URL. AutoMotion's logic-processing engine automatically digests the codebase, generates a structured technical script, synchronizes a voiceover, and renders a short 1080p video summary.
          </p>

          <RepoInput />
        </section>

        {/* ── How It Works ── */}
        <section className="section animate-enter" style={{ animationDelay: "200ms" }}>
          <div className="section-header">
            <span className="section-label">Pipeline Overview</span>
            <div className="section-rule" />
          </div>

          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">01</div>
              <div className="step-icon-wrap">
                <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
                </svg>
              </div>
              <div className="step-title">Input Source</div>
              <div className="step-desc">
                Submit any public GitHub repository URL. The system seamlessly pulls the latest source files—no authentication or complex integrations required.
              </div>
            </div>

            <div className="step-card">
              <div className="step-number">02</div>
              <div className="step-icon-wrap">
                <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <div className="step-title">Logic Extraction</div>
              <div className="step-desc">
                The core analysis engine maps the architecture, identifies the primary tech stack, and authors a timeline-accurate script with synchronized visual scenes.
              </div>
            </div>

            <div className="step-card">
              <div className="step-number">03</div>
              <div className="step-icon-wrap">
                <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="step-title">Render & Export</div>
              <div className="step-desc">
                A dynamically themed 1920×1080 export is compiled with perfectly timed voice audio. The resulting MP4 is optimized and ready for distribution.
              </div>
            </div>
          </div>
        </section>

        {/* ── Features ── */}
        <section className="section animate-enter" style={{ animationDelay: "300ms" }}>
          <div className="section-header">
            <span className="section-label">Technical Specifications</span>
            <div className="section-rule" />
          </div>

          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-dot" />
              <div className="feature-text">
                <h4>Comprehensive Code Parsing</h4>
                <p>
                  Going beyond superficial README scraping. AutoMotion evaluates real file hierarchies, source dependencies, and key application logic.
                </p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-dot" />
              <div className="feature-text">
                <h4>Adaptive Visual Environments</h4>
                <p>
                  The rendering engine automatically assigns visual themes based on framework domains (e.g., frontend frameworks trigger modern aesthetics, devops tools utilize terminal themes).
                </p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-dot" />
              <div className="feature-text">
                <h4>Dynamic Audio Synthesis</h4>
                <p>
                  Integrated TTS pipelines ensure voiceovers that are programmatically synced down to the millisecond with moving visual scenes.
                </p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-dot" />
              <div className="feature-text">
                <h4>High-Fidelity Output Format</h4>
                <p>
                  Exports as a standard 1920×1080 file, compatible across modern browsers, standard social media, or your internal chat networks.
                </p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-dot" />
              <div className="feature-text">
                <h4>Real-Time Progress WebSockets</h4>
                <p>
                  Never wait blindly. A low-latency WebSocket connection pushes telemetry data from the processing cluster directly to your active browser session.
                </p>
              </div>
            </div>

            <div className="feature-item">
              <div className="feature-dot" />
              <div className="feature-text">
                <h4>Programmatic Transitions</h4>
                <p>
                  Scenes are chained using smooth cross-fade techniques with algorithmic easing, ensuring pacing matches the spoken word frequency.
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* ── Footer ── */}
      <footer className="footer animate-enter" style={{ animationDelay: "400ms" }}>
        <div className="container footer-inner">
          <span className="footer-text">
            AutoMotion &copy; 2026
          </span>
          <span className="footer-stack">
            Developed for the Orion Build Hackathon
          </span>
        </div>
      </footer>
    </main>
  );
}
