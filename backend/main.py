"""
AutoMotion — FastAPI Application
Main entry point for the backend server.
"""
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import OUTPUTS_DIR, BACKEND_URL
from api.routes import router, start_cleanup_loop
from api.websocket import ws_router


# ── App lifespan ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n[START] AutoMotion Backend")
    print(f"   Outputs: {OUTPUTS_DIR.resolve()}")
    print(f"   Backend: {BACKEND_URL}")
    start_cleanup_loop()
    yield
    print("\n[STOP] Shutting down...")


app = FastAPI(
    title="AutoMotion",
    description="Turn any GitHub repo into a narrated explainer video",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files: serve generated videos ──
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

# ── Register routes ──
app.include_router(router, prefix="/api")
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "automotion-backend"}


@app.get("/")
async def root():
    return {"status": "ok", "service": "automotion-backend"}
