# Research Desk
Desktop research app — **NotebookLM** + **OpenRouter** AI analysis.
**You do NOT need PyCharm.** Only Python and a web browser.
---
## What you need first
1. **Windows 10 or 11**
2. **Python 3.10+** — https://www.python.org/downloads/  
   - During install, check **“Add python.exe to PATH”**
3. **OpenRouter API key** (free works) — https://openrouter.ai/settings/keys  
4. **Google account** — for NotebookLM login
---
## Download
1. Open the GitHub repo → green **Code** → **Download ZIP**
2. Unzip to any folder (e.g. `C:\research-desk`)
3. Open that folder in **File Explorer**
4. Click the **address bar**, type `cmd`, press **Enter**
You should see something like: `C:\research-desk>`
---
## One-time setup (Windows)
Run **one line at a time** in cmd (not all on one line):
py -m venv .venv .venv\Scripts\activate.bat pip install -r requirements.txt playwright install copy .env.example .env

### Add your API key
1. Open `.env` in **Notepad** (same folder as `app.py`)
2. Replace `sk-or-v1-paste-your-key-here` with **your** OpenRouter key
3. Save the file
**Never share `.env` — it contains your secret key.**
### Log in to NotebookLM (once)
Still in cmd:
py -m notebooklm login

A browser opens — sign in with **your** Google account. When done, return to cmd.
---
## Run the app
**Option A — cmd**
cd C:\research-desk .venv\Scripts\activate.bat py app.py

(Use your actual folder path instead of `C:\research-desk`.)
**Option B — double-click**
After one-time setup above, double-click **`run_app.bat`**.
> Note: `run_app.bat` expects `.venv` to already exist. Run the setup steps first.
---
## First time inside the app
1. **Settings** (sidebar) → paste OpenRouter key if you didn’t add it to `.env`
2. **Login** (top bar) → complete NotebookLM in the browser
3. **Refresh** → open **Notebook** → pick a notebook
4. Type a question at the bottom → send
Reports save locally in the `reports/` folder (created automatically).
---
## Troubleshooting
| Problem | Fix |
|---------|-----|
| `'py' is not recognized` | Reinstall Python with **Add to PATH** checked |
| PowerShell blocks activate | Use **cmd** instead of PowerShell, or run `.venv\Scripts\activate.bat` |
| `'pip' is not recognized` | Run `.venv\Scripts\activate.bat` first, or use `.venv\Scripts\pip.exe install -r requirements.txt` |
| No notebooks listed | Click **Login**, finish in browser, then **Refresh** |
| API key error | Edit `.env` or use **Settings** in the app |
---
## Project layout
app.py — start the GUI research_agent.py — research backend UI/ — app screens Styles/ — theme requirements.txt — Python packages .env.example — template (copy to .env) run_app.bat — quick launcher (after setup) reports/ — saved reports (local, not in GitHub)

---
## Notes
- Default AI model: `openrouter/free` (no paid credits required)
- Each user needs **their own** OpenRouter key and NotebookLM login
- Do not commit or share `.env`
