@echo off
setlocal

echo ====================================================
echo Z-Image-Turbo API - Development Mode
echo ====================================================

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: uv is not installed
    echo Please install uv first:
    echo   pip install uv
    echo   or visit: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Install dependencies if .venv doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    uv venv  --python=3.12
    echo Installing dependencies...
    uv pip install -r requirements.txt

)

REM Activate virtual environment and run
echo Starting API server...
call .venv\Scripts\activate.bat
python main.py

pause
