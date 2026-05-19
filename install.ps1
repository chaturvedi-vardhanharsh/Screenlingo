# ScreenLingo — first-time setup for Windows
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "ScreenLingo setup" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot`n"

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python not found. Install from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Enable 'Add python.exe to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

$version = & python --version 2>&1
Write-Host "Found $version"

Set-Location $ProjectRoot

if (-not (Test-Path ".venv")) {
    Write-Host "`nCreating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing dependencies..."
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\pip.exe" install -r requirements.txt

Write-Host "`nSetup complete." -ForegroundColor Green
Write-Host "Run the app with:" -ForegroundColor Green
Write-Host "  .\run.bat" -ForegroundColor White
Write-Host "  — or —" -ForegroundColor DarkGray
Write-Host "  .\.venv\Scripts\python.exe main.py" -ForegroundColor White
