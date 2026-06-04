# Research Desk — Session Handoff Summary

**Project:** `C:\AIResearch` / GitHub: `https://github.com/lambuilehoang-code/research-desk.git`  
**App:** PyQt6 desktop GUI wrapping `research_agent.py` (NotebookLM + OpenRouter)  
**Last focus:** GitHub publish, friend setup, NotebookLM timeout debugging  

---

## 1. Project status

| Track | Status |
|-------|--------|
| **Track A (v1 GUI)** | Complete — chat, sources, analysis, settings, search, reports |
| **GitHub prep** | `.gitignore`, `README.md`, `setup.bat`, `run_app.bat` — done locally; push as needed |
| **Track v2** | Not started — rich analysis, 4-column notebook, source hub v2, polish |
| **Code fixes (v1.1)** | Applied locally: subprocess UTF-8, startup notebook load try/except, README, setup.bat |

---

## 2. Track v2 (future)

1. **Rich Analysis** — parse `reports/*.md`, insight cards, charts, entity map  
2. **Notebook 4-column** — outline \| editor \| AI copilot  
3. **Source Hub v2** — add/delete sources, full-text preview via NotebookLM CLI  
4. **Polish** — SVG icons, dark mode, real source snippets  

---

## 3. GitHub — friends download without PyCharm

**Friends need:** Python 3.10–3.12, OpenRouter key, Google account. **Not** PyCharm or Git.

**Download:** GitHub → Code → Download ZIP → unzip to folder with `app.py`.

**Setup (one command per line):**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
.venv\Scripts\playwright.exe install
copy .env.example .env
```

Or double-click **`setup.bat`**.

**Run:**

```powershell
.venv\Scripts\python.exe -m notebooklm login
.venv\Scripts\python.exe app.py
```

Or **`run_app.bat`** after setup.

**Never commit:** `.env`, `.venv`, `reports/`, `chat_history/`

---

## 4. Setup mistakes (teach friends)

| Mistake | Result |
|---------|--------|
| All setup commands on **one line** | `venv: error: unrecognized arguments` |
| `py app.py` before pip / without `.venv` | `No module named 'PyQt6'` |
| PowerShell `activate` blocked | Use `.venv\Scripts\pip.exe` and `.venv\Scripts\python.exe` |
| **Python 3.14** | Subprocess bugs, instability — use **3.12** |
| Nested ZIP path `research-desk-master\...` | Normal — open folder that contains `app.py` |

---

## 5. Code fixes applied (v1.1)

### `research_agent.py` — `run_notebooklm`

- Explicit command list, `encoding="utf-8"`, `errors="replace"`, `cwd=PROJECT_DIR`
- Fixes Windows Unicode and Python 3.14 subprocess issues

### `UI/main_window.py`

- `try/except` around startup `load_notebooks()` so app opens even if list fails

### `setup.bat` / `run_app.bat`

- `setup.bat` — one-time venv + pip + playwright  
- `run_app.bat` — requires `.venv`, uses `.venv\Scripts\python.exe`

### `README.md`

- Separate setup commands, Python 3.10–3.12 warning, troubleshooting, antivirus section, known bugs

### `UI/report_picker_dialog.py` + `theme.qss`

- `reportPickerDialog` styling (Browse reports dark background fix)

---

## 6. Bugs discovered on friend's laptop

### A. README one-line commands

- Old README pasted all commands on one line → venv errors  
- **Fix:** README + `setup.bat` with one command per line  

### B. Python 3.14.5

- `TypeError: 'NoneType' object is not iterable` on startup (subprocess)  
- **Fix:** Recreate `.venv` with `py -3.12 -m venv .venv`  

### C. PyQt6 pip — Permission denied (`d3dcompiler_47.dll`)

- Locked `.venv` (app/PyCharm/Python still running) or OneDrive/sync  
- **Fix:** Close all Python, delete `.venv`, move project to `C:\research-desk`, `pip install --no-cache-dir`, restart PC if needed  

### D. Antivirus

- Caused NotebookLM timeouts / TransportServerError when enabled  
- **Fix:** Remove or allowlist project folder + `C:\Users\<user>\.notebooklm\`  
- Documented in README  

### E. NotebookLM: login OK, ask fails

- `Authentication saved to: ...storage_state.json` ✅  
- `❌ NotebookLM timeout (took too long)` on **ask** (not list)  

**Ruled out:**

- 46 notebooks — `list` finishes in under 5 seconds  
- Wrong internet (same Wi‑Fi, CLI works)  
- List broken — CLI list works  

**Still possible when CLI ask works but app fails:**

- Different question (long vs short)  
- Same title, **different notebook UUID** (status bar shows title only)  
- App hides real error — UI shows `"NotebookLM failed"`; read PowerShell when running `python.exe app.py`  
- Stale NotebookLM conversation — try `notebooklm clear`  
- **60s app timeout** on heavy ask — CLI may finish in 30s but app kills at 60s  
- Old code on machine without v1.1 fixes  

**Exact message `NotebookLM timeout`:** only from `query_notebooklm` → `subprocess.TimeoutExpired` (60s), not from `list` (30s).

### F. Browse reports dialog

- Black background, white list — missing `reportPickerDialog` in QSS  
- **Fix:** objectName + theme block  

### G. `load_notebooks` after Refresh

- Sets `notebook_id = None`; `setCurrentRow(0)` may not fire signal if row already 0  
- **Fix (recommended):** explicitly set `notebook_id` after load  

---

## 7. Testing tutorial (short)

**Layers:**

1. Setup — venv, pip, imports  
2. CLI — `login`, `list`, `list --json`, `ask --json -n ID`  
3. Subprocess — `test_ask.py` mimics `query_notebooklm`  
4. App — `python.exe app.py` from PowerShell, watch terminal  

**Decision:**

| CLI ask | test_ask.py | App ask | Conclusion |
|---------|-------------|---------|------------|
| Pass | Pass | Fail | GUI / worker / wrong notebook / old code |
| Pass | Fail | — | Subprocess path issue |
| Fail | — | — | NotebookLM / network / notebook |

---

## 8. If Python 3.14.5

```powershell
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
.venv\Scripts\playwright.exe install
.venv\Scripts\python.exe --version   # must show 3.12.x
```

---

## 9. NotebookLM timeout — what to do next

1. `notebooklm list --json` → copy notebook **id**  
2. CLI: `ask "What is this notebook about?" --json -n ID`  
3. Run `test_ask.py` (subprocess, 60s timeout, same as app)  
4. Run app from PowerShell, same short question, read terminal  
5. `notebooklm clear` → retry  
6. **Code fixes:** raise ask timeout to 120s, show stderr in UI, show notebook id on status bar  

### `test_ask.py` template

```python
import subprocess, sys, json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
QUESTION = "What is this notebook about?"
NOTEBOOK_ID = "PASTE_UUID_HERE"

cmd = [str(sys.executable), "-m", "notebooklm", "ask", QUESTION, "--json", "-n", NOTEBOOK_ID]
r = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=60,
    cwd=str(PROJECT_DIR),
)
print("returncode:", r.returncode)
print("stderr:", (r.stderr or "")[:1200])
print("stdout:", (r.stdout or "")[:400])
if r.returncode == 0 and r.stdout.strip():
    try:
        json.loads(r.stdout)
        print("JSON: OK")
    except json.JSONDecodeError as e:
        print("JSON: FAIL", e)
```

---

## 10. Recommended code changes (pending)

- [ ] Push latest README + fixes to GitHub  
- [ ] `query_notebooklm` timeout 60 → 120  
- [ ] Pass stderr to UI instead of generic `"NotebookLM failed"`  
- [ ] Set `notebook_id` after `load_notebooks()` / show UUID in status bar  
- [ ] `setup.bat` use `py -3.12` explicitly  
- [ ] Optional: `notebooklm use <id>` on notebook select  

---

## 11. File map

```text
AIResearch/
  app.py, research_agent.py
  UI/          — main_window, panels, workers, dialogs
  Styles/      — theme.qss
  setup.bat, run_app.bat
  .env.example, requirements.txt
  README.md, .gitignore, SESSION_HANDOFF.md
  reports/, chat_history/   — local only, gitignored
```

---

## 12. One-line status

**v1 works on dev machine.** Friends need Python **3.12**, one-line-at-a-time setup, `.venv\Scripts\python.exe`. Main remaining issue: **NotebookLM ask timeout in app while CLI ask works** — debug with PowerShell + `test_ask.py`, then raise timeout and improve error messages in code.

---

## 13. Reference links

- Repo: https://github.com/lambuilehoang-code/research-desk.git  
- OpenRouter keys: https://openrouter.ai/settings/keys  
- Python 3.12: https://www.python.org/downloads/  
- NotebookLM: https://notebooklm.google.com  
