"""
AutoMotion — WebSocket Progress Hub
Real-time progress updates pushed to connected frontend clients.
"""
import json
import asyncio
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()

# ── Connected clients per job ──
_connections: dict[str, list[WebSocket]] = {}


async def send_progress_update(job_id: str, data: dict) -> None:
    """
    Send a progress update to all WebSocket clients watching a specific job.
    Safe to call even if no clients are connected.
    """
    clients = _connections.get(job_id, [])
    if not clients:
        return

    message = json.dumps(data)
    disconnected = []

    for ws in clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)

    # Clean up disconnected clients
    for ws in disconnected:
        clients.remove(ws)


@ws_router.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates.

    The frontend connects after receiving a job_id from POST /api/generate.
    Progress messages are pushed as JSON: {step, progress, message, status}
    """
    await websocket.accept()

    # Register this connection
    if job_id not in _connections:
        _connections[job_id] = []
    _connections[job_id].append(websocket)

    print(f"  [WS] Client connected for job {job_id[:8]}...")

    try:
        # Keep the connection alive until the client disconnects
        # We send progress updates via send_progress_update()
        while True:
            # Wait for any client message (keepalive/ping)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=120)
                # Client can send "ping" to keep alive
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # Send a keepalive ping
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    finally:
        # Unregister
        if job_id in _connections:
            if websocket in _connections[job_id]:
                _connections[job_id].remove(websocket)
            if not _connections[job_id]:
                del _connections[job_id]

        print(f"  [WS] Client disconnected for job {job_id[:8]}...")
