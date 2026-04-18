#!/bin/bash

# Start Remotion Render Server in the background on port 3001
echo "Starting Remotion Render Server..."
cd /app/remotion
node render-server.mjs &

# Move to backend
cd /app/backend

# The startup scripts ensures outputs directory exists
mkdir -p outputs

# Start FastAPI Backend in the foreground on the DO-provided port
echo "Starting FastAPI Backend on port ${PORT:-8080}..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
