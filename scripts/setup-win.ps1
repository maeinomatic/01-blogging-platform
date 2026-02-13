<#
PowerShell helper to set up the development environment on Windows.
Run as:  PowerShell -ExecutionPolicy RemoteSigned -File .\scripts\setup-win.ps1
#>

# Create venv if missing
if (-Not (Test-Path -Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
} else {
    Write-Host ".venv already exists"
}

# Install requirements using venv python
Write-Host "Installing Python dependencies into .venv..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Start Postgres in Docker Compose
Write-Host "Starting PostgreSQL (docker-compose)..."
docker-compose up -d db

# Wait for Postgres to become ready (pg_isready inside container)
Write-Host "Waiting for Postgres to become healthy..."
$maxAttempts = 20
$attempt = 0
while ($attempt -lt $maxAttempts) {
    $attempt++
    try {
        docker-compose exec -T db pg_isready -U $env:POSTGRES_USER | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Postgres is ready."
            break
        }
    } catch {
        # ignore
    }
    Start-Sleep -Seconds 2
}
if ($attempt -eq $maxAttempts) {
    Write-Warning "Postgres did not become ready within expected time. Check 'docker-compose logs db'."
}

# Run Alembic migrations
Write-Host "Applying database migrations (alembic upgrade head)..."
.\.venv\Scripts\python.exe -m alembic upgrade head

Write-Host "Setup complete. To activate the venv in this shell run:`n    . .\.venv\Scripts\Activate.ps1`" -ForegroundColor Green
Write-Host "Then start the backend with:`n    . .\scripts\run-backend-win.ps1`" -ForegroundColor Green
