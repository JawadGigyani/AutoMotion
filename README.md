# AutoMotion 🎬

**Transform any GitHub repository into an automated video summary.**

[![Watch the Demo on YouTube](https://img.shields.io/badge/YouTube-Watch_Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/5tpIs1Sgbh4)

## Overview

AutoMotion is a sophisticated logic-processing engine built for the **Orion Build Hackathon**. It ingests public GitHub repositories, analyzes the architecture and key logic using a multi-agent AI pipeline, and automatically synthesizes a fully narrated, dynamically animated 1080p MP4 explainer video synced perfectly to the millisecond.

## 🚀 Features

- **Deep Code Analysis**: Parses actual file trees and source code logic, pulling way more than just standard `README.md` metadata.
- **Adaptive Visual Environments**: Automatically selects visual aesthetics (e.g., Terminal Green, Dark Neon, Ocean Depth) based on the repository's primary technical domain.
- **Studio-Grade Audio**: Integrated text-to-speech with frame-perfect video synchronization.
- **Real-Time Progress WebSockets**: A low-latency push connection streams terminal-level updates directly to your frontend dashboard.
- **Programmatic Transitions**: Smooth cross-fades and slide algorithms timed exactly to spoken word lengths.

## 🏗️ Architecture

AutoMotion is resiliently decoupled across three isolated services:
1. **Frontend (`/frontend`)**: A pure React + Next.js (App Router) interface styled with a sleek matte-grey CSS framework.
2. **Backend (`/backend`)**: A FastAPI application housing a LangGraph deterministic pipeline. Interacts with Featherless AI models for analysis and ElevenLabs for voice synthesis.
3. **Render Server (`/remotion`)**: An Express cluster running [Remotion](https://www.remotion.dev/) that horizontally headless-compiles raw React frames into standard H.264 video.

## 🛠 Prerequisites

- Node.js (v18+)
- Python (3.10+)
- **FFmpeg** (Must be installed and added to your system PATH)
- Featherless AI API Key
- ElevenLabs API Key

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/automotion.git
   cd automotion
   ```

2. **Configure Environment Variables**
   
   Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

   Create `backend/.env`:
   ```env
   FEATHERLESS_API_KEY=your_featherless_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ```

3. **Install Dependencies**
   ```powershell
   # 1. Backend environment
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   
   # 2. Frontend
   cd ../frontend
   npm install
   
   # 3. Render Server
   cd ../remotion
   npm install
   ```

4. **Run the Application**
   For Windows environments, launch the system locally via the provided automation script:
   ```powershell
   .\start-all.ps1
   ```
   This will simultaneously boot the Remotion server (Port `3001`), the FastAPI backend (Port `8000`), and the Next.js frontend (Port `3000`).

## 🧠 The Pipeline Execution Logic

Behind the scenes, AutoMotion utilizes a heavy deterministic graph model:
1. `parse_repo_node`: Traverses GitHub via the REST API to retrieve the global file tree and target language statistics.
2. `fetch_files_node`: Concurrently downloads critical application entry points (e.g., `main.py`, `App.tsx`, `docker-compose.yml`).
3. `repo_analyst`: Extracts architecture patterns, edge-cases, and clever internal code implementations.
4. `script_director`: Authors a 7-scene screenplay dictating exact background variants, CSS animations, and verbatim voice text.
5. `voiceover_node`: Generates perfectly spliced `.mp3` sub-clips per scene using ElevenLabs.
6. `scene_timing_node`: Computes strict frame durations (30 FPS) based on word-count distributions and audio buffer lengths.
7. `render_video_node`: Triggers the Remotion render cluster and caches the final `video.mp4` to the output buffer.

## 🤝 Developed For
**Orion Build Hackathon 2026**
