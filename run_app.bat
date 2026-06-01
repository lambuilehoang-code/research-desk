@echo off
cd /d "%~dp0"

echo Installing packages...
.venv\Scripts\python -m pip install -q -r requirements.txt 2>nul

if not exist ".env" (
    if exist ".env.example" copy /Y ".env.example" ".env"
    echo Edit .env and add your OpenRouter key, or set it in the app Settings.
)

echo Starting desktop app...
.venv\Scripts\python app.py
pause
