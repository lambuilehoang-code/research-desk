@echo off
cd /d "%~dp0"

echo 🔄 Installing packages if needed...
.venv\Scripts\python -m pip install -q -r requirements.txt 2>nul

if not exist ".env" (
    echo.
    echo ⚠️  First-time setup: copy .env.example to .env
    echo    Then paste your OpenRouter API key in .env ONE time only.
    echo.
    if exist ".env.example" copy /Y ".env.example" ".env"
    echo    Created .env from example — edit it and add your key, then run this again.
    pause
    exit /b 1
)

echo 🔐 Logging in to NotebookLM...
.venv\Scripts\python -m notebooklm login

echo 🚀 Starting Research Agent...
.venv\Scripts\python research_agent.py
pause
