
@echo off
cd /d "%~dp0"

echo Starting Computational Beam Analysis...
python main.py

if errorlevel 1 (
    echo.
    echo Application failed to start or exited with an error.
    pause
)
