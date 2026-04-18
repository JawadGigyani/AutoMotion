'use client';

/**
 * RepoReel — VideoPlayer Component
 * Displays the rendered video with download and GitHub link actions.
 */
export default function VideoPlayer({ videoUrl, repoUrl, theme }) {
  const handleDownload = async () => {
    try {
      // Fetch and create a blob URL so the download attribute works cross-origin
      const res = await fetch(videoUrl);
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = 'reporeel.mp4';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 10_000);
    } catch {
      // Fallback: open in new tab
      window.open(videoUrl, '_blank');
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
          onError={(e) => {
            // If the video fails to load, show a helpful message
            e.target.style.display = 'none';
            const msg = document.createElement('div');
            msg.style.cssText =
              'aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;color:#6b6b6b;font-size:14px;font-family:monospace;background:#0d0d0d;';
            msg.textContent = 'Video unavailable — check backend is running';
            e.target.parentNode.insertBefore(msg, e.target);
          }}
        />

        {/* Actions */}
        <div className="video-actions">
          <button
            className="btn-primary"
            onClick={handleDownload}
            type="button"
          >
            ↓ Download MP4
          </button>

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

          <div className="video-meta">1920 × 1080 · H.264 + AAC</div>
        </div>
      </div>
    </div>
  );
}
