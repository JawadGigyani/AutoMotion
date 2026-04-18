# =================================================================
# AutoMotion -- Start All Services
# Launches FastAPI backend, Remotion render server, and Next.js
# frontend in separate PowerShell windows.
#
# Usage (from repoReel/ directory):
#   .\start-all.ps1
# =================================================================

param(
    [switch]$NoBrowser
)

$Root = $PSScriptRoot

Write-Host ""
Write-Host "  AutoMotion -- Starting all services..." -ForegroundColor Cyan
Write-Host ""

# -- Verify directories exist --------------------------------------
$backendDir  = Join-Path $Root "backend"
$remotionDir = Join-Path $Root "remotion"
$frontendDir = Join-Path $Root "frontend"

foreach ($dir in @($backendDir, $remotionDir, $frontendDir)) {
    if (-not (Test-Path $dir)) {
        Write-Host "  [ERROR] Directory not found: $dir" -ForegroundColor Red
        exit 1
    }
}

# -- Verify venv ---------------------------------------------------
$venvActivate = Join-Path $backendDir "venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    Write-Host "  [ERROR] Python venv not found at backend\venv\" -ForegroundColor Red
    Write-Host "          Run: cd backend && python -m venv venv && venv\Scripts\pip install -r requirements.txt" -ForegroundColor DarkGray
    exit 1
}

# -- 1. Render Server (Node.js / Express) --------------------------
Write-Host "  [1/3] Starting Remotion render server on :3001 ..." -ForegroundColor Cyan
$renderCmd = "cd '$remotionDir'; `$host.UI.RawUI.WindowTitle = 'AutoMotion - Render Server 3001'; Write-Host '[Render Server] http://localhost:3001' -ForegroundColor Cyan; node render-server.mjs"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $renderCmd -WindowStyle Normal

Start-Sleep -Milliseconds 800

# -- 2. FastAPI Backend --------------------------------------------
Write-Host "  [2/3] Starting FastAPI backend on :8000 ..." -ForegroundColor Green
$backendCmd = "cd '$backendDir'; `$host.UI.RawUI.WindowTitle = 'AutoMotion - Backend 8000'; & '.\venv\Scripts\Activate.ps1'; Write-Host '[Backend] http://localhost:8000' -ForegroundColor Green; python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Start-Sleep -Milliseconds 800

# -- 3. Next.js Frontend -------------------------------------------
Write-Host "  [3/3] Starting Next.js frontend on :3000 ..." -ForegroundColor Magenta
$frontendCmd = "cd '$frontendDir'; `$host.UI.RawUI.WindowTitle = 'AutoMotion - Frontend 3000'; Write-Host '[Frontend] http://localhost:3000' -ForegroundColor Magenta; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

# -- Summary -------------------------------------------------------
Write-Host ""
Write-Host "  Services starting in separate windows:" -ForegroundColor White
Write-Host "    Render Server  ->  http://localhost:3001" -ForegroundColor DarkGray
Write-Host "    Backend API    ->  http://localhost:8000" -ForegroundColor DarkGray
Write-Host "    Frontend       ->  http://localhost:3000" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Allow ~10 seconds for all services to fully start." -ForegroundColor DarkGray
Write-Host "  The render server will pre-bundle Remotion on first launch (~5-10s)." -ForegroundColor DarkGray
Write-Host ""

# -- Auto-open browser ---------------------------------------------
if (-not $NoBrowser) {
    Write-Host "  Opening browser in 12 seconds... (Ctrl+C to cancel)" -ForegroundColor DarkGray
    Start-Sleep -Seconds 12
    Start-Process "http://localhost:3000"
}
