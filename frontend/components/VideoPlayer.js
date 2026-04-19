'use client';

/**
 * AutoMotion — VideoPlayer Component
 * Displays the rendered video with download, subtitle, and GitHub link actions.
 */
export default function VideoPlayer({ videoUrl, subtitleUrl, repoUrl, theme }) {
  const handleDownload = async () => {
    try {
      // Fetch and create a blob URL so the download attribute works cross-origin
      const res = await fetch(videoUrl);
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = 'automotion.mp4';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 10_000);
    } catch {
      // Fallback: open in new tab
      window.open(videoUrl, '_blank');
    }
  };

  const handleDownloadSubtitles = async () => {
    if (!subtitleUrl) return;
    try {
      const res = await fetch(subtitleUrl);
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = 'automotion.srt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 10_000);
    } catch {
      window.open(subtitleUrl, '_blank');
    }
  };

  return (
    <div>
      {/* Success banner */}
      <div className="complete-banner">
        <span>✓</span>
        <span>Video ready</span>
        {theme && (
          <span style={{ marginLeft: 8, opacity: 0.6, fontSize: 12 }}>
            Theme: {theme}
          </span>
        )}
      </div>

      {/* Player */}
      <div className="video-card">
        <video
          className="video-element"
          controls
          autoPlay
          playsInline
          src={videoUrl}
          crossOrigin="anonymous"
          onError={(e) => {
            e.target.style.display = 'none';
            const msg = document.createElement('div');
            msg.style.cssText =
              'aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;color:#6b6b6b;font-size:14px;font-family:monospace;background:#e9ecef;border:1px solid #ddd;border-radius:8px;';
            msg.textContent = 'Video unavailable — check backend is running';
            e.target.parentNode.insertBefore(msg, e.target);
          }}
        >
          {subtitleUrl && (
            <track
              kind="captions"
              src={subtitleUrl}
              srcLang="en"
              label="English"
            />
          )}
        </video>

        {/* Actions */}
        <div className="video-actions">
          <button
            className="btn-primary"
            onClick={handleDownload}
            type="button"
          >
            ↓ Download MP4
          </button>

          {subtitleUrl && (
            <button
              className="btn-secondary"
              onClick={handleDownloadSubtitles}
              type="button"
            >
              ↓ Subtitles (.srt)
            </button>
          )}

          {repoUrl && (
            <a
              href={repoUrl.startsWith('http') ? repoUrl : `https://${repoUrl}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              View on GitHub ↗
            </a>
          )}

          {/* Share buttons */}
          <button
            className="btn-secondary share-btn"
            type="button"
            title="Share on X"
            onClick={() => {
              const repoName = repoUrl ? repoUrl.split('/').slice(-2).join('/') : 'a repo';
              const text = encodeURIComponent(
                `I just generated an AI video explainer for ${repoName} using AutoMotion! 🎬\n\nCheck it out:`
              );
              window.open(
                `https://twitter.com/intent/tweet?text=${text}`,
                '_blank',
                'width=600,height=400'
              );
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </button>
          <button
            className="btn-secondary share-btn"
            type="button"
            title="Share on LinkedIn"
            onClick={() => {
              const url = encodeURIComponent(window.location.href);
              window.open(
                `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
                '_blank',
                'width=600,height=400'
              );
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </button>

          <div className="video-meta">1920 × 1080 · H.264 + AAC</div>
        </div>
      </div>
    </div>
  );
}
