/**
 * RepoReel — Remotion Render Server
 * Express server that bundles Remotion project once on startup,
 * then accepts render requests from the Python backend.
 *
 * Based on the proven pattern from Basic Project.
 */
import express from "express";
import cors from "cors";
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(cors());
app.use(express.json({ limit: "10mb" }));

// Serve audio files from the backend outputs directory
// so Chromium (used by Remotion renderer) can fetch them
app.use(
  "/static",
  express.static(path.resolve(__dirname, "..", "backend", "outputs"))
);

// ── Bundle management ──
let bundleLocation = null;

async function ensureBundle() {
  if (!bundleLocation) {
    console.log("📦 Bundling Remotion project...");
    const startTime = Date.now();
    bundleLocation = await bundle({
      entryPoint: path.resolve(__dirname, "src", "index.ts"),
      webpackOverride: (config) => config,
    });
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`✅ Bundle ready in ${elapsed}s`);
  }
  return bundleLocation;
}

// ── Health check ──
app.get("/health", (_req, res) => {
  res.json({ status: "ok", bundled: !!bundleLocation });
});

// ── Render endpoint ──
app.post("/render", async (req, res) => {
  const startTime = Date.now();
  console.log("\n🎬 Render request received");

  try {
    const { scenes, audioUrl, totalFrames, fps = 30, theme, outputPath } =
      req.body;

    if (!scenes || !totalFrames || !outputPath) {
      return res.status(400).json({
        error: "Missing required fields: scenes, totalFrames, outputPath",
      });
    }

    console.log(
      `   Scenes: ${scenes.length}, Frames: ${totalFrames}, FPS: ${fps}`
    );
    console.log(
      `   Theme: ${theme?.name || "default"}, Audio: ${audioUrl ? "yes" : "no"}`
    );

    const serveUrl = await ensureBundle();

    // Build the input props for the composition
    const inputProps = {
      scenes,
      audioUrl: audioUrl || "",
      totalFrames,
      fps,
      theme: theme || { id: "dark_cinematic" },
    };

    // Select composition (triggers calculateMetadata)
    const composition = await selectComposition({
      serveUrl,
      id: "RepoReel",
      inputProps,
      port: 3100,
    });

    console.log(
      `   Composition: ${composition.durationInFrames} frames @ ${composition.fps}fps`
    );

    // Render the video
    await renderMedia({
      composition,
      serveUrl,
      codec: "h264",
      outputLocation: outputPath,
      inputProps,
      concurrency: 2,
      port: 3100,
      onProgress: ({ progress }) => {
        const pct = Math.round(progress * 100);
        if (pct % 20 === 0) {
          console.log(`   Render progress: ${pct}%`);
        }
      },
    });

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`✅ Render complete in ${elapsed}s → ${outputPath}`);

    res.json({ success: true, path: outputPath });
  } catch (err) {
    console.error("❌ Render error:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ── Start server ──
const PORT = 3001;
app.listen(PORT, async () => {
  console.log(`\n🎬 RepoReel Render Server on http://localhost:${PORT}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Static: http://localhost:${PORT}/static/\n`);

  // Pre-bundle on startup for faster first render
  try {
    await ensureBundle();
  } catch (err) {
    console.error("⚠️  Initial bundle failed:", err.message);
    console.error("   Bundle will be attempted again on first render request.");
  }
});
