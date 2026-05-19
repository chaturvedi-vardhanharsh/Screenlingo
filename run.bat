@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ScreenLingo: first-time setup...
  python -m venv .venv
  if errorlevel 1 (
    echo ERROR: Python not found. Install from https://www.python.org/downloads/
    pause
    exit /b 1
  )
  .venv\Scripts\python.exe -m pip install --upgrade pip
  .venv\Scripts\pip install -r requirements.txt
  if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
  )
  echo Setup complete.
)
.venv\Scripts\python.exe main.py
if errorlevel 1 pause
