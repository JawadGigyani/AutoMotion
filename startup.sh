#!/bin/bash

# Start Remotion Render Server in the background on port 3001
echo "[STARTUP] Starting Remotion Render Server..."
cd /app/remotion
node render-server.mjs &
REMOTION_PID=$!

# Wait for Remotion to be ready (health check loop)
echo "[STARTUP] Waiting for Remotion to bundle and become healthy..."
MAX_WAIT=120
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:3001/health > /dev/null 2>&1; then
        echo "[STARTUP] Remotion is healthy (waited ${WAITED}s)"
        break
    fi

    # Check if the process died
    if ! kill -0 $REMOTION_PID 2>/dev/null; then
        echo "[STARTUP] ERROR: Remotion process died unexpectedly"
        exit 1
    fi

    sleep 2
    WAITED=$((WAITED + 2))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "[STARTUP] WARNING: Remotion did not become healthy within ${MAX_WAIT}s, starting backend anyway"
fi

# Move to backend
cd /app/backend

# Ensure outputs directory exists
mkdir -p outputs

# Start FastAPI Backend in the foreground on the DO-provided port
echo "[STARTUP] Starting FastAPI Backend on port ${PORT:-8080}..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
