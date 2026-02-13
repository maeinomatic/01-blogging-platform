# Run FastAPI backend using the venv python
# Usage: PowerShell: . .\scripts\run-backend-win.ps1

Write-Host "Starting backend (uvicorn)..."
.\.venv\Scripts\python.exe -m uvicorn server.main:app --reload --host 0.0.0.0 --port 5000
