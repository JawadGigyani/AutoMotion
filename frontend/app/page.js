import RepoInput from "@/components/RepoInput";
import SampleVideos from "@/components/SampleVideos";

export default function Home() {
  return (
    <main>
      <nav className="nav">
        <div className="container nav-inner">
          <div
            className="nav-logo animate-enter"
            style={{ animationDelay: "0ms" }}
          >
            AutoMotion
          </div>
        </div>
      </nav>

      <div className="container">
        <section
          className="hero animate-enter"
          style={{ animationDelay: "100ms" }}
        >
          <div className="hero-eyebrow">Automated Explainer Videos</div>

          <h1 className="hero-title">
            Turn any GitHub repo into a{" "}
            <em>narrated video.</em>
          </h1>

          <p className="hero-subtitle">
            Paste a URL. Get a 1080p explainer video with AI narration
            in minutes.
          </p>

          <RepoInput />
        </section>

        <section
          className="section animate-enter"
          style={{ animationDelay: "200ms" }}
        >
          <div className="section-header">
            <span className="section-label">See It In Action</span>
            <div className="section-rule" />
          </div>

          <SampleVideos />
        </section>

        <section
          className="section animate-enter"
          style={{ animationDelay: "300ms" }}
        >
          <div className="section-header">
            <span className="section-label">How It Works</span>
            <div className="section-rule" />
          </div>

          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">01</div>
              <div className="step-icon-wrap">
                <svg
                  width="24"
                  height="24"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244"
                  />
                </svg>
              </div>
              <div className="step-title">Paste a URL</div>
              <div className="step-desc">
                Enter any public GitHub repository URL. No authentication
                needed.
              </div>
            </div>

            <div className="step-card">
              <div className="step-number">02</div>
              <div className="step-icon-wrap">
                <svg
                  width="24"
                  height="24"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                  />
                </svg>
              </div>
              <div className="step-title">AI Analyzes & Scripts</div>
              <div className="step-desc">
                AI agents read the codebase and write a narration script
                with visual scenes.
              </div>
            </div>

            <div className="step-card">
              <div className="step-number">03</div>
              <div className="step-icon-wrap">
                <svg
                  width="24"
                  height="24"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="step-title">Render & Export</div>
              <div className="step-desc">
                A 1080p video is rendered with synced voiceover and
                exported as MP4.
              </div>
            </div>
          </div>
        </section>
      </div>

      <footer
        className="footer animate-enter"
        style={{ animationDelay: "400ms" }}
      >
        <div className="container footer-inner">
          <span className="footer-text">AutoMotion &copy; 2026</span>
          <span className="footer-stack">
            Developed for the Orion Build Hackathon
          </span>
        </div>
      </footer>
    </main>
  );
}
