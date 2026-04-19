# AutoMotion 🎬

**Turn any GitHub repository into a narrated 1080p explainer video.**

[![Devpost Project](https://img.shields.io/badge/Project-Devpost-blue?style=for-the-badge&logo=devpost)](https://orion-build-challenge.devpost.com/)
[![Watch the Demo on YouTube](https://img.shields.io/badge/YouTube-Watch_Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=Gm8zfuQ1-ro)

AutoMotion is an AI-powered platform that ingests public GitHub repositories, analyzes the architecture and source code using a multi-agent pipeline, and synthesizes a fully narrated, dynamically animated 1080p MP4 explainer video — synced to the millisecond. Paste a URL, get a video.

---

## 🌟 Overview

AutoMotion transforms code documentation by:

- **Deep Code Analysis** — Parses actual file trees, source code logic, and README content — not just metadata
- **Multi-Agent AI Pipeline** — Two specialized LLM agents (code analyst + script director) orchestrated by LangGraph
- **Studio-Grade Audio** — Per-scene ElevenLabs TTS with frame-perfect synchronization via ffprobe
- **Themed Visual Environments** — Five distinct visual themes (Dark Cinematic, Neon Cyberpunk, Minimal Light, Terminal Green, Ocean Depth) with unique layouts
- **Real-Time Progress** — WebSocket push connection streams step-by-step updates to the frontend
- **Programmatic Transitions** — Smooth cross-fades timed to audio durations using Remotion's TransitionSeries
- **Auto-Generated Subtitles** — WebVTT captions synced to narration, enabled by default in the player
- **Setup Instructions** — Automatically incorporates installation steps from project READMEs

---

## 🛠️ Tech Stack

### Frontend

| Technology | Version |
|------------|---------|
| **Next.js** (App Router) | `16.2.4` |
| **React** | `19.2.4` |

### Backend

| Technology | Version |
|------------|---------|
| **Python** | `3.10+` |
| **FastAPI** | `0.115.0` |
| **Uvicorn** | `0.30.0` |
| **LangChain** | `>=0.3.7` |
| **LangChain-OpenAI** | `>=0.2.5` |
| **LangGraph** | `>=0.2.28` |
| **ElevenLabs SDK** | `>=1.9.0` |
| **Pydantic** | `>=2.9.0` |
| **httpx** | `0.27.0` |

### Render Server

| Technology | Version |
|------------|---------|
| **Remotion** | `4.0.448` |
| **React** (Remotion runtime) | `18.3.1` |
| **Express** | `4.22.1` |
| **TypeScript** | `>=5.5.0` |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **FFmpeg / FFprobe** | Audio processing and duration detection |
| **Chromium** | Headless browser for Remotion rendering |
| **Docker** | Containerized deployment |
| **WebSockets** | Real-time progress streaming |

### AI Services

| Service | Role |
|---------|------|
| **Featherless.ai** | OpenAI-compatible LLM API (Qwen2.5-Coder-32B + Qwen2.5-72B) |
| **ElevenLabs** | Text-to-Speech synthesis and voice generation |
| **GitHub REST API** | Repository data, file trees, and source code |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) — [Download](https://nodejs.org/)
- **Python** (3.10 or higher) — [Download](https://www.python.org/downloads/)
- **FFmpeg** (must be on your system PATH) — [Download](https://ffmpeg.org/download.html)
- **Git** — [Download](https://git-scm.com/)

### Installing FFmpeg

#### Windows (Chocolatey)

```bash
choco install ffmpeg
```

#### macOS (Homebrew)

```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install ffmpeg
```

Verify installation:

```bash
ffmpeg -version
ffprobe -version
```

> **Note:** After installing FFmpeg, restart your terminal for PATH changes to take effect.

### API Keys

You will need API keys from the following services:

#### 1. Featherless.ai (LLM)

1. Go to [Featherless.ai](https://featherless.ai/)
2. Sign up and navigate to your API keys
3. Copy your API key

#### 2. ElevenLabs (Text-to-Speech)

1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up or log in
3. Navigate to [Developers → API Keys](https://elevenlabs.io/app/developers/api-keys)
4. Copy your API key

**Free Tier:** ElevenLabs offers a free tier with monthly character limits for TTS.

#### 3. GitHub Token (Optional)

A GitHub personal access token increases API rate limits from 60 to 5,000 requests/hour. Without it, public repos still work but you may hit rate limits during heavy use.

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Generate a new token (classic) with `public_repo` scope

---

## 🚀 Local Setup Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/JawadGigyani/AutoMotion.git
cd AutoMotion
```

### Step 2: Configure Environment Variables

Create `backend/.env`:

```env
# Required — Featherless.ai LLM
FEATHERLESS_API_KEY=your_featherless_api_key

# Required — ElevenLabs TTS
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Optional — Higher GitHub API rate limits
GITHUB_TOKEN=your_github_token

# Optional — Override defaults
# FEATHERLESS_BASE_URL=https://api.featherless.ai/v1
# FEATHERLESS_CODE_MODEL=Qwen/Qwen2.5-Coder-32B-Instruct
# FEATHERLESS_GENERAL_MODEL=Qwen/Qwen2.5-72B-Instruct
# REMOTION_RENDER_URL=http://localhost:3001
# BACKEND_URL=http://localhost:8000
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Step 3: Install Dependencies

#### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Frontend

```bash
cd frontend
npm install
```

#### Render Server

```bash
cd remotion
npm install
```

### Step 4: Start the Application

**Option A — Automated (Windows PowerShell):**

```powershell
.\start-all.ps1
```

This boots all three services in separate windows and opens the browser after 12 seconds.

**Option B — Manual (any OS):**

Open three terminal windows:

```bash
# Terminal 1: Remotion render server (port 3001)
cd remotion
node render-server.mjs

# Terminal 2: FastAPI backend (port 8000)
cd backend
source venv/bin/activate   # or venv\Scripts\Activate.ps1 on Windows
python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0

# Terminal 3: Next.js frontend (port 3000)
cd frontend
npm run dev
```

### Step 5: Open the Application

Navigate to **http://localhost:3000** in your browser.

1. Paste any public GitHub repository URL
2. Optionally select a theme and voice
3. Click **Generate** and watch real-time progress
4. Download or watch your 1080p video

---

## 🏗️ Architecture

AutoMotion is decoupled across three isolated services:

```
Browser (Next.js :3000)
    │
    ├── HTTP ──→ FastAPI Backend (:8000)
    │               ├── GitHub REST API
    │               ├── Featherless.ai LLM
    │               ├── ElevenLabs TTS
    │               └── HTTP ──→ Remotion Render Server (:3001)
    │                               └── Headless Chromium → H.264 MP4
    │
    └── WebSocket ──→ /ws/progress/{job_id} (real-time updates)
```

| Service | Directory | Port | Role |
|---------|-----------|------|------|
| **Frontend** | `/frontend` | 3000 | Next.js App Router UI with real-time progress tracking |
| **Backend** | `/backend` | 8000 | FastAPI server housing the LangGraph pipeline, AI agents, and TTS |
| **Render Server** | `/remotion` | 3001 | Express server running Remotion headless rendering |

---

## 🧠 Pipeline Execution

The backend uses a LangGraph deterministic graph to orchestrate seven stages:

```
START → parse_url → fetch_github_data → analyze_repo → write_script → generate_voice → calculate_frames → render_video → END
```

| # | Stage | What It Does |
|---|-------|-------------|
| 1 | **parse_url** | Validates and parses the GitHub URL, extracts owner and repo name |
| 2 | **fetch_github_data** | Calls GitHub REST API — retrieves metadata, README, languages, file tree, and key source files |
| 3 | **analyze_repo** | Agent #1 (Qwen2.5-Coder-32B) — deep code analysis: architecture patterns, features, tech stack, setup commands |
| 4 | **write_script** | Agent #2 (Qwen2.5-72B) — writes the narration script and scene specifications, selects visual theme, adapts tone to voice style |
| 5 | **generate_voice** | ElevenLabs TTS — generates per-scene audio clips, concatenates to a single `voice.mp3`, measures durations with ffprobe |
| 6 | **calculate_frames** | Converts audio durations to exact frame counts at 30 FPS, compensates for 12-frame transition overlaps |
| 7 | **render_video** | Sends scene data + audio to Remotion render server → produces `video.mp4` (1920×1080), `subtitles.vtt`, and `thumbnail.png` |

---

## 📁 Project Structure

```
AutoMotion/
├── frontend/                     # Next.js 16 App Router
│   ├── app/
│   │   ├── page.js               # Landing page with sample videos
│   │   ├── generate/page.js      # Video generation + progress tracking
│   │   └── globals.css           # Design system
│   ├── components/
│   │   ├── RepoInput.js          # URL input with theme/voice selectors
│   │   ├── ProgressTracker.js    # Real-time WebSocket progress UI
│   │   ├── VideoPlayer.js        # Video playback with captions
│   │   └── SampleVideos.js       # Landing page sample grid + modal
│   └── .env.local                # Frontend environment variables
│
├── backend/                      # FastAPI + LangGraph Pipeline
│   ├── main.py                   # App entry, CORS, static mounts
│   ├── config.py                 # Environment variable loader
│   ├── api/
│   │   ├── routes.py             # REST endpoints (generate, status, result, gallery)
│   │   └── websocket.py          # WebSocket progress streaming
│   ├── agents/
│   │   ├── pipeline.py           # LangGraph 7-stage orchestration
│   │   ├── state.py              # PipelineState TypedDict
│   │   ├── repo_analyzer.py      # Agent #1: code analysis
│   │   ├── script_director.py    # Agent #2: script + scene writing
│   │   └── prompts.py            # System prompts and instructions
│   ├── services/
│   │   ├── github_service.py     # GitHub REST API client
│   │   ├── llm_service.py        # Featherless.ai LLM client (LangChain)
│   │   ├── voice_service.py      # ElevenLabs TTS integration
│   │   └── theme_service.py      # Visual theme selection logic
│   ├── utils/
│   │   ├── url_parser.py         # GitHub URL validation
│   │   ├── file_utils.py         # Output directory management + cleanup
│   │   └── srt_generator.py      # WebVTT subtitle generation
│   ├── samples/                  # Pre-rendered sample videos
│   ├── outputs/                  # Generated job outputs (auto-cleaned)
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Backend environment variables
│
├── remotion/                     # Remotion 4 Render Server
│   ├── render-server.mjs         # Express server: /render, /thumbnail, /static
│   ├── src/
│   │   ├── index.ts              # Remotion composition registration
│   │   ├── RepoReelVideo.tsx     # Main composition orchestrating all scenes
│   │   ├── themes/index.ts       # 5 themes with colors + layout properties
│   │   └── scenes/
│   │       ├── TitleScene.tsx     # Repository title + tagline
│   │       ├── OverviewScene.tsx  # Project description
│   │       ├── TechStackScene.tsx # Language/framework breakdown
│   │       ├── CodeHighlightScene.tsx  # Key code patterns
│   │       ├── FeaturesScene.tsx  # Feature highlights
│   │       ├── SetupScene.tsx     # Installation commands (terminal style)
│   │       ├── StatsScene.tsx     # GitHub statistics
│   │       └── ClosingScene.tsx   # Call-to-action
│   └── package.json
│
├── Dockerfile                    # Combined Python + Node + FFmpeg + Chromium
├── startup.sh                    # Container entrypoint
├── start-all.ps1                 # Local Windows launcher (all 3 services)
└── README.md
```

---

## 🔧 Configuration Reference

### Backend Environment Variables (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEATHERLESS_API_KEY` | Yes | — | Featherless.ai API key for LLM access |
| `ELEVENLABS_API_KEY` | Yes | — | ElevenLabs API key for TTS |
| `GITHUB_TOKEN` | No | — | GitHub PAT for higher rate limits |
| `FEATHERLESS_BASE_URL` | No | `https://api.featherless.ai/v1` | LLM API base URL |
| `FEATHERLESS_CODE_MODEL` | No | `Qwen/Qwen2.5-Coder-32B-Instruct` | Model for code analysis |
| `FEATHERLESS_GENERAL_MODEL` | No | `Qwen/Qwen2.5-72B-Instruct` | Model for script writing |
| `FEATHERLESS_FALLBACK_MODEL` | No | `THUDM/glm-4-9b-chat` | Fallback model |
| `ELEVENLABS_VOICE_ID` | No | — | Default TTS voice (UI can override) |
| `ELEVENLABS_MODEL_ID` | No | `eleven_multilingual_v2` | ElevenLabs model |
| `REMOTION_RENDER_URL` | No | `http://localhost:3001` | Render server URL |
| `BACKEND_URL` | No | `http://localhost:8000` | Backend self-reference |

### Frontend Environment Variables (`frontend/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | Yes | `http://localhost:8000` | Backend API URL (browser-facing) |

---

## 🐳 Docker Deployment

The included Dockerfile builds a single container with Python 3.10, Node.js 18, FFmpeg, and Chromium:

```bash
docker build -t automotion .

docker run -p 8080:8080 \
  -e FEATHERLESS_API_KEY=your_key \
  -e ELEVENLABS_API_KEY=your_key \
  -e GITHUB_TOKEN=your_token \
  automotion
```

The container runs the Remotion render server in the background and the FastAPI backend on the foreground, both behind port `8080`.

---

## 🎬 How It Works

```
1. URL Parsing & Validation
   ↓
2. GitHub Data Fetching (README, file tree, source files)
   ↓
3. AI Code Analysis (Qwen2.5-Coder-32B via Featherless.ai)
   ↓
4. Script & Scene Direction (Qwen2.5-72B + voice style adaptation)
   ↓
5. Voice Synthesis (ElevenLabs per-scene TTS → concatenated MP3)
   ↓
6. Frame Calculation (ffprobe durations → 30 FPS frame counts)
   ↓
7. Video Rendering (Remotion headless → 1920×1080 H.264 + AAC)
```

### Output

Each generation produces:
- **video.mp4** — 1920×1080 H.264 + AAC, 90–120 seconds
- **subtitles.vtt** — WebVTT captions synced to narration
- **thumbnail.png** — Title scene still frame

Generated videos are automatically cleaned up after **45 minutes**. Sample videos are permanent.

---

## 👥 Team

**Muhammad Jawad** — AI Engineer

---

## 🤝 Developed For

**[Orion Build Hackathon 2026](https://orion-build-challenge.devpost.com/)**

---

## 📄 License

This project was created for the Orion Build Hackathon 2026.
