@echo off
echo Starting Backend Server with Uvicorn...
set PYTHONPATH=%CD%
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
if %ERRORLEVEL% NEQ 0 (
    echo Error starting server. Ensure uvicorn is installed and the virtual environment is active.
    pause
)
