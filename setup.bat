@echo off
cd /d "%~dp0"

echo Research Desk - one-time setup
echo Run each step; wait until it finishes.
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment .venv ...
    py -m venv .venv
    if errorlevel 1 (
        echo Failed to create .venv. Try: py -3.12 -m venv .venv
        pause
        exit /b 1
    )
)

echo Installing Python packages ...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo pip install failed.
    pause
    exit /b 1
)

echo Installing Playwright browser ...
.venv\Scripts\python.exe -m playwright install
if errorlevel 1 (
    echo playwright install failed.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" copy /Y ".env.example" ".env"
    echo Created .env - open it in Notepad and add your OpenRouter key.
)

echo.
echo Setup done.
echo Next:
echo   1. Edit .env and add your OpenRouter key
echo   2. .venv\Scripts\python.exe -m notebooklm login
echo   3. Double-click run_app.bat or: .venv\Scripts\python.exe app.py
echo.
pause
