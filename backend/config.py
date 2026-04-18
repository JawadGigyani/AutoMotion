"""
AutoMotion Backend — Configuration
Loads environment variables and provides typed settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv(Path(__file__).parent / ".env")

# ── Paths ──
BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Featherless.ai (LLM) ──
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "")
FEATHERLESS_BASE_URL = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
FEATHERLESS_CODE_MODEL = os.getenv("FEATHERLESS_CODE_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")
FEATHERLESS_GENERAL_MODEL = os.getenv("FEATHERLESS_GENERAL_MODEL", "Qwen/Qwen2.5-72B-Instruct")
FEATHERLESS_FALLBACK_MODEL = os.getenv("FEATHERLESS_FALLBACK_MODEL", "THUDM/glm-4-9b-chat")

# ── ElevenLabs TTS ──
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

# ── GitHub ──
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# ── Services ──
REMOTION_RENDER_URL = os.getenv("REMOTION_RENDER_URL", "http://localhost:3001")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── Video ──
VIDEO_FPS = 30
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# ── Limits ──
MAX_README_CHARS = 5000
MAX_CODE_FILE_CHARS = 2000
MAX_KEY_FILES = 5
MAX_TREE_DEPTH = 2
MAX_CONCURRENT_JOBS = 3
