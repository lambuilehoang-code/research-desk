@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Double-click setup.bat first, then run this again.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" copy /Y ".env.example" ".env"
    echo Edit .env and add your OpenRouter key, or set it in app Settings.
)

echo Starting Research Desk ...
.venv\Scripts\python.exe app.py
pause
