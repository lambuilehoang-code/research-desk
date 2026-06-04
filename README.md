# Research Desk

Desktop research app — **NotebookLM** + **OpenRouter** AI analysis.

**You do NOT need PyCharm.** Only Python and a web browser.

---

## What you need first

1. **Windows 10 or 11**
2. **Python 3.10, 3.11, or 3.12** — https://www.python.org/downloads/  
   - During install, check **“Add python.exe to PATH”**
   - **Avoid Python 3.14** for now (known subprocess issues with this app)
3. **OpenRouter API key** (free works) — https://openrouter.ai/settings/keys
4. **Google account** — for NotebookLM login

---

## Download

1. Open the GitHub repo → green **Code** → **Download ZIP**
2. Unzip to any folder (e.g. `C:\research-desk`)
3. Open the folder that contains **`app.py`** (GitHub ZIP may nest folders like `research-desk-master\research-desk-master` — that is normal)

---

## One-time setup (Windows)

Open **cmd** or **PowerShell** in the folder with `app.py`.

**Run each command separately.** Press Enter after each line. Do **not** paste all lines as one line.

```
py -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
.venv\Scripts\playwright.exe install
copy .env.example .env
```

Or double-click **`setup.bat`** (same steps).

### Add your API key

1. Open `.env` in **Notepad**
2. Replace `sk-or-v1-paste-your-key-here` with **your** OpenRouter key
3. Save

**Never share `.env` — it contains your secret key.**

### Log in to NotebookLM (once)

```
.venv\Scripts\python.exe -m notebooklm login
```

Sign in with **your** Google account in the browser.

Test (optional but recommended):

```
.venv\Scripts\python.exe -m notebooklm list
```

---

## Run the app

```
.venv\Scripts\python.exe app.py
```

Or double-click **`run_app.bat`** (after setup).

**Do not use** `py app.py` — that skips the virtual environment and causes missing-module errors.

---

## First time inside the app

1. **Settings** → OpenRouter key (if not in `.env`)
2. **Login** → NotebookLM in the browser
3. **Refresh** → **Notebook** → pick a notebook
4. Ask a question

Reports save locally in `reports/` (not uploaded to GitHub).

---

## Troubleshooting

### Common setup mistakes

| Mistake | What happens | Fix |
|---------|--------------|-----|
| Pasting all setup commands on **one line** | `venv: error: unrecognized arguments` | Run **one command per line** (see setup above) |
| Running `py app.py` before setup | `No module named 'PyQt6'` or `No module named 'notebooklm'` | Run `setup.bat` or pip install first; use `.venv\Scripts\python.exe app.py` |
| Using system Python instead of `.venv` | Missing modules even after install | Always use `.venv\Scripts\python.exe` and `.venv\Scripts\pip.exe` |
| Wrong folder after ZIP download | `app.py` not found | Open the nested folder until you see `app.py` next to `requirements.txt` |
| Using `git clone` without Git installed | `'git' is not recognized` | Use **Download ZIP** instead — Git is optional |

### App errors

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: 'NoneType' object is not iterable` on startup | Python **3.14** + Windows subprocess bug when loading notebooks | Use **Python 3.12** (`py -3.12 -m venv .venv`). Re-download latest ZIP |
| App opens then closes immediately | NotebookLM not logged in or subprocess failed | Click **Login** → browser → **Refresh**. Run `.venv\Scripts\python.exe -m notebooklm list` first |
| `UnicodeDecodeError: 'charmap' codec can't decode` | Windows encoding vs NotebookLM UTF-8 output | Fixed in latest code — re-download ZIP |
| PowerShell: `Activate.ps1 cannot be loaded` | PowerShell script policy | Skip activate — use `.venv\Scripts\pip.exe` and `.venv\Scripts\python.exe` directly |
| `Could not load notebooks` in status bar | Normal on first launch before login | **Login** → NotebookLM in browser → **Refresh** |
| No notebooks listed after login | Session expired or wrong Google account | Run `.venv\Scripts\python.exe -m notebooklm login` again, then **Refresh** |
| API key error | Missing or invalid OpenRouter key | Edit `.env` or **Settings** in the app |
| Answers in English when you asked in Vietnamese | NotebookLM follows **source language** | Normal. Set **LANGUAGE=vi** in Settings for Claude's deep analysis |
| `TransportServerError`, `chat.ask retry timed out after 30.0s`, `NotebookLM timeout` | **Antivirus or firewall** slowing/blocking Chromium, Python, or Google | See **Antivirus & firewall** below |

### Antivirus & firewall

Research Desk uses **Python**, **Chromium (Playwright)**, and **saved Google login files**. Many antivirus apps treat that as suspicious and **slow or block** it — even when login looks OK, **asking a question** can still time out.

**Typical symptoms when antivirus is the cause:**

- Login works (`Already logged in`) but questions fail
- `TransportServerError` or `chat.ask retry timed out after 30.0s`
- `NotebookLM timeout (took too long)`
- First run very slow; `pip install` or `playwright install` hangs

**Fix (recommended): allowlist these paths**

Replace `YourName` with the Windows username and adjust the project path if different:

| What to allow | Path |
|---------------|------|
| Project folder | `C:\research-desk\` (or wherever you unzipped the app) |
| Virtual environment | `...\research-desk-master\.venv\` |
| NotebookLM login data | `C:\Users\YourName\.notebooklm\` |
| Python in venv | `...\research-desk-master\.venv\Scripts\python.exe` |

In your antivirus app, look for **Exclusions**, **Allowlist**, or **Trusted applications** and add the items above.

**Also check:**

1. Test https://notebooklm.google.com in Chrome on the **same PC and Wi‑Fi** — if the website is slow, fix network first
2. Turn **VPN off** temporarily
3. Allow **Python** and **Chromium** through **Windows Firewall** when prompted
4. After changing antivirus settings, run login again:
   ```
   .venv\Scripts\python.exe -m notebooklm login
   ```
5. Try a **short** question first (large notebooks take longer)

**Quick test:** If the app fails with antivirus **on** but works with real-time protection **off** (briefly, for testing only), the cause is confirmed — use allowlist instead of leaving protection off.

### Verify NotebookLM before opening the app

```
.venv\Scripts\python.exe -m notebooklm list
```

- **Works** → use **Login** + **Refresh** in the app
- **Fails** → run `.venv\Scripts\python.exe -m notebooklm login` and try again

### Fresh reinstall (last resort)

In PowerShell (project folder):

```
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
.venv\Scripts\playwright.exe install
copy .env.example .env
```

Edit `.env`, login to NotebookLM, then run the app.

---

## Known bugs fixed (v1.1)

1. **Startup crash on Windows (Python 3.14)** — `TypeError` when loading notebooks. Fixed in `research_agent.py`; app no longer crashes if notebooks fail on startup.
2. **Unicode errors on Windows** — Fixed with `encoding="utf-8"` in subprocess calls.
3. **README one-line command confusion** — Setup commands must be run separately; use `setup.bat` or follow steps above.
4. **`run_app.bat` using wrong Python** — Now uses `.venv\Scripts\python.exe` and checks `.venv` exists.
5. **Browse reports dialog dark background** — Report picker styling fixed in theme.

**Recommended:** Python **3.10–3.12**. Use **3.12** if problems persist.

---

## Project layout

```
app.py              — start the GUI
research_agent.py   — research backend
UI/                 — app screens
Styles/             — theme
requirements.txt    — Python packages
.env.example        — template (copy to .env)
setup.bat           — one-time setup
run_app.bat         — launch app (after setup)
reports/            — saved reports (local only)
```

---

## Notes

- Default AI model: `openrouter/free`
- Each user needs **their own** OpenRouter key and NotebookLM login
- Do not commit or share `.env`
