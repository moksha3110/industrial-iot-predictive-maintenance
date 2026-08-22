@echo off
setlocal
cd /d "%~dp0"
title Industrial IoT Predictive Maintenance

echo ============================================================
echo  Industrial IoT Predictive Maintenance - Setup and Run
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found.
  echo Install Python 3.11 or newer from https://www.python.org/downloads/
  echo During installation, select "Add Python to PATH".
  pause
  exit /b 1
)

python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 (
  echo ERROR: Python 3.11 or newer is required.
  python --version
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 goto :failed
) else (
  echo [1/4] Virtual environment already exists.
)

echo [2/4] Installing project dependencies...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :failed

if not exist ".env" copy /Y ".env.example" ".env" >nul

echo [3/4] Running automated tests...
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 goto :failed

echo [4/4] Starting application...
echo.
echo Dashboard: http://127.0.0.1:8000
echo Swagger:   http://127.0.0.1:8000/docs
echo Health:    http://127.0.0.1:8000/health
echo.
echo Keep this window open. Press Ctrl+C to stop the application.
echo ============================================================
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
exit /b %errorlevel%

:failed
echo.
echo SETUP FAILED. Read FRIEND_SETUP_GUIDE.md for troubleshooting.
pause
exit /b 1
