import subprocess
import json
import os
import re
import sys
from pathlib import Path
from openai import OpenAI
from datetime import datetime, timedelta, timezone
import urllib.request
import urllib.error

DARK_STYLESHEET = """
QMainWindow { background-color: #1e1e1e; color: #ffffff; }
QTextEdit { background-color: #2d2d2d; color: #ffffff; border: 1px solid #444; }
QPushButton { background-color: #0d47a1; color: white; border: none; padding: 5px; }
QLineEdit { background-color: #2d2d2d; color: #ffffff; border: 1px solid #444; }
"""

LIGHT_STYLESHEET = """
QMainWindow { background-color: #ffffff; color: #000000; }
QTextEdit { background-color: #f5f5f5; color: #000000; border: 1px solid #ddd; }
QPushButton { background-color: #1976d2; color: white; border: none; padding: 5px; }
QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #ddd; }
"""

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# === PATHS & PYTHON (fix #1: same interpreter as venv / PyCharm) ===
PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"
CHAT_HISTORY_DIR = PROJECT_DIR / "chat_history"
CHAT_HISTORY_DIR.mkdir(exist_ok=True)
PYTHON = sys.executable

VIETNAM_TZ = timezone(timedelta(hours=7))
SESSION_API_CALLS = 0
LAST_CALL_TOKENS = None

# === CONFIG (fix #11: change model in one place) ===
LANGUAGE = "vi"  # "vi" or "en"
# Valid OpenRouter IDs (pick one):
#   openrouter/free                 — free, no wallet credits (recommended for free accounts)
#   anthropic/claude-haiku-4.5      — paid, needs credits in wallet
#   anthropic/claude-sonnet-4.6     — paid, best quality, uses more credits
DEFAULT_MODEL = "openrouter/free"

# === API KEY — paste once in .env file (fix #2) ===
ENV_FILE = PROJECT_DIR / ".env"
if load_dotenv:
    load_dotenv(ENV_FILE)

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "2500"))

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
if OPENROUTER_API_KEY.startswith('"') and OPENROUTER_API_KEY.endswith('"'):
    OPENROUTER_API_KEY = OPENROUTER_API_KEY[1:-1]
if OPENROUTER_API_KEY.startswith("'") and OPENROUTER_API_KEY.endswith("'"):
    OPENROUTER_API_KEY = OPENROUTER_API_KEY[1:-1]

# Optional: set CLAUDE_MODEL in .env to override default
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

client = None


def reload_config():
    """Reload .env and reset API client (after GUI saves settings)."""
    global OPENROUTER_API_KEY, CLAUDE_MODEL, MAX_TOKENS, LANGUAGE, client
    if load_dotenv:
        load_dotenv(ENV_FILE, override=True)
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
    CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "2500"))
    LANGUAGE = os.environ.get("LANGUAGE", LANGUAGE)
    client = None


def api_key_configured():
    return bool(OPENROUTER_API_KEY)


def get_client():
    global client
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OpenRouter API key not set. Add OPENROUTER_API_KEY to .env "
            "(free key from https://openrouter.ai/settings/keys)"
        )
    if client is None:
        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
    return client


def save_env_settings(api_key, model=None, max_tokens=None, language=None):
    """Save user settings to .env (one-time key paste from GUI)."""
    lines = []
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            key = line.split("=", 1)[0].strip() if "=" in line else ""
            if key in (
                "OPENROUTER_API_KEY",
                "CLAUDE_MODEL",
                "MAX_TOKENS",
                "LANGUAGE",
            ):
                continue
            if line.strip():
                lines.append(line)
    lines.append(f"OPENROUTER_API_KEY={api_key.strip()}")
    lines.append(f"CLAUDE_MODEL={(model or CLAUDE_MODEL).strip()}")
    lines.append(f"MAX_TOKENS={max_tokens or MAX_TOKENS}")
    if language:
        lines.append(f"LANGUAGE={language.strip()}")
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    reload_config()


def notebooklm_cmd(*args):
    """Build NotebookLM CLI command using the same Python as this script."""
    return [PYTHON, "-m", "notebooklm", *args]


def run_notebooklm(args, timeout=60):
    """Run a NotebookLM CLI command."""
    return subprocess.run(
        notebooklm_cmd(*args),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def fetch_notebooks():
    """List notebooks from NotebookLM. Returns list or None on error (fix #5, #6, #8)."""
    result = run_notebooklm(["list", "--json"], timeout=30)

    if result.returncode != 0:
        print(f"❌ Could not list notebooks: {result.stderr.strip() or 'unknown error'}")
        return None

    if not result.stdout.strip():
        print("❌ NotebookLM returned an empty response.")
        return None

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("❌ Invalid JSON from NotebookLM.")
        return None

    notebooks = data.get("notebooks", [])
    if not notebooks:
        print("❌ No notebooks found. Create one in NotebookLM first.")
        return None

    return notebooks


def fetch_sources(notebook_id):
    """List sources in a notebook via NotebookLM CLI. Returns list, [] if empty, None on error."""
    if not notebook_id:
        return []
    result = run_notebooklm(
        ["source", "list", "--json", "-n", notebook_id],
        timeout=60,
    )
    if result.returncode != 0:
        return None
    if not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return data.get("sources", [])


def count_citations(references, answer_text=""):
    """Count citations from structured refs or inline markers in NotebookLM answer text."""
    if references:
        return len(references)
    text = answer_text or ""
    match = re.search(r"(\d+)\s+sources?\s+referenced", text, re.I)
    if match:
        return int(match.group(1))
    nums = set(re.findall(r"\[(\d+)\]", text))
    return len(nums) if nums else 0


def count_citations_in_report(markdown_text: str) -> int:
    """Parse citation count from a saved analysis report."""
    match = re.search(r"(\d+)\s+sources?\s+referenced", markdown_text, re.I)
    if match:
        return int(match.group(1))
    if "## NotebookLM Research" in markdown_text:
        section = markdown_text.split("## NotebookLM Research", 1)[1]
        if "##" in section:
            section = section.split("##", 1)[0]
        return count_citations([], section)
    return 0


def list_report_files():
    """Return saved analysis reports newest first."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(
        REPORTS_DIR.glob("analysis_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def ensure_notebooklm_login():
    """Log in if needed, then return notebook list (fix #6, #9: one list call)."""
    print("🔐 Checking NotebookLM authentication...")
    notebooks = fetch_notebooks()

    if notebooks is not None:
        return notebooks

    print("⚠️  NotebookLM session expired or not logged in. Opening login...")
    subprocess.run(notebooklm_cmd("login"))

    print("🔄 Loading notebooks again...")
    return fetch_notebooks()


def select_notebook(notebooks):
    """Let user pick a notebook. Returns (id, title) or None."""
    print("\n📚 Your Notebooks:")
    for i, nb in enumerate(notebooks, 1):
        title = nb.get("title") or "(Untitled)"
        print(f"  {i}. {title} (ID: {nb['id'][:8]}...)")

    choice = input(f"\nSelect notebook number (1-{len(notebooks)}): ").strip()

    try:
        num = int(choice)
        if num < 1 or num > len(notebooks):
            print("❌ Invalid number.")
            return None
        nb = notebooks[num - 1]
        title = nb.get("title") or "(Untitled)"
        print(f"✅ Using: {title}\n")
        return nb["id"], title
    except ValueError:
        print("❌ Please enter a number.")
        return None


def query_notebooklm(question, notebook_id):
    """Query NotebookLM and return answer with citations."""
    try:
        result = run_notebooklm(
            ["ask", question, "--json", "-n", notebook_id],
            timeout=60,
        )

        if result.returncode != 0:
            print(f"❌ NotebookLM Error: {result.stderr}")
            return None

        if not result.stdout.strip():
            print("❌ NotebookLM returned an empty answer.")
            return None

        return json.loads(result.stdout)

    except subprocess.TimeoutExpired:
        print("❌ NotebookLM timeout (took too long)")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid response from NotebookLM")
        return None
    except Exception as e:
        print(f"❌ Error querying NotebookLM: {str(e)[:100]}")
        return None


def analyze_with_claude(notebook_answer):
    """Send NotebookLM output to Claude for deep analysis."""
    if not notebook_answer or not str(notebook_answer).strip():
        print("❌ NotebookLM had no answer text to analyze.")
        return None

    try:
        response = get_client().chat.completions.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            stream=True,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a senior research analyst specializing in investment and policy analysis.
        Respond in {LANGUAGE.upper()}.

        Write a LONG, detailed report (aim for 800–1200 words unless the source material is very short).
        Do not be brief. Expand on each point with explanation, context, and examples from the source.

        Your task:
        1. Deeply analyze all research provided from NotebookLM
        2. Identify key themes, patterns, and connections across sections
        3. Highlight critical insights with supporting detail
        4. Flag risks and opportunities with reasoning
        5. Provide actionable recommendations with clear next steps

        Use markdown headings (##, ###). Use bullet lists where helpful.
        Cite or reference specific ideas from the source when available.""",
                },
                {
                    "role": "user",
                    "content": f"""Based on this NotebookLM research, write a full in-depth analysis report:

        {notebook_answer}

        Structure your answer with these sections (write several paragraphs per section):

        ## Executive summary
        (1 full paragraph — not just 2 sentences)

        ## Key findings
        (At least 5 detailed findings, each with 2–3 sentences of explanation)

        ## Deep analysis
        (3–4 paragraphs connecting themes, data, and implications)

        ## Risks and challenges
        (At least 4 risks, each explained)

        ## Opportunities
        (At least 4 opportunities, each explained)

        ## Actionable recommendations
        (At least 5 recommendations with concrete steps)

        ## Conclusion
        (1–2 paragraphs)

        Be thorough and long. Do not shorten the answer.""",
                },
            ],
        )

        global SESSION_API_CALLS, LAST_CALL_TOKENS
        SESSION_API_CALLS += 1

        full_text = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_text += text
                yield text

        return full_text

    except Exception as e:
        err = str(e)
        if "402" in err or "credit" in err.lower() or "insufficient" in err.lower():
            print("❌ OpenRouter: payment required (402) — cannot run this model now.")
            print("   The meter bar is your KEY cap, not wallet balance.")
            print("   Options:")
            print("   1) In .env use a free model:")
            print("      CLAUDE_MODEL=openrouter/free")
            print("   2) Add credits: https://openrouter.ai/settings/credits")
            print("   3) Wait and try again after daily reset")
            print_credit_meter()
        elif "404" in err or "not a valid model" in err.lower() or "no endpoints" in err.lower():
            print(f"❌ Model not found on OpenRouter: {CLAUDE_MODEL}")
            print("   Claude has NO :free version. In .env use:")
            print("   CLAUDE_MODEL=openrouter/free")
            print("   Or a paid model if you added credits:")
            print("   CLAUDE_MODEL=anthropic/claude-haiku-4.5")
        else:
            print(f"❌ Claude Error: {err[:200]}")
        return None


def save_report(question, nb_output, claude_analysis):
    """Save results to markdown file (fix #7: path next to project, not hardcoded C:)."""
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = REPORTS_DIR / f"analysis_{timestamp}.md"

        content = f"""# Research Analysis Report
**Generated:** {datetime.now()}

## Question
{question}

## NotebookLM Research
{nb_output.get('answer', 'N/A')}

### Sources Cited
{len(nb_output.get('references', []))} sources referenced

## Claude's Deep Analysis
{claude_analysis}

---
*Generated by NotebookLM → Claude Orchestrator*
"""

        filename.write_text(content, encoding="utf-8")
        print(f"\n✅ Report saved: {filename}")
        return str(filename)

    except OSError as e:
        print(f"❌ Error saving report: {str(e)[:100]}")
        return None


def fetch_openrouter_status():
    """Fetch key usage/limits from OpenRouter."""
    url = "https://openrouter.ai/api/v1/key"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None

    return payload.get("data") or {}


def reset_countdown_vietnam():
    now = datetime.now(VIETNAM_TZ)
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    delta = next_midnight - now
    total_sec = int(delta.total_seconds())
    hours, rem = divmod(total_sec, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}", next_midnight.strftime("%Y-%m-%d %H:%M")


def credit_meter_bar(remaining, limit, width=20):
    """Bar for API key spending cap — NOT 'tokens left today'."""
    if limit is None or limit <= 0:
        return "[" + "█" * width + "] no cap set"
    if remaining is None:
        remaining = 0
    pct = max(0.0, min(1.0, float(remaining) / float(limit)))
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct * 100:.0f}% of key cap ({remaining:.2f} / {limit:.2f})"


def print_credit_meter():
    global LAST_CALL_TOKENS, SESSION_API_CALLS

    data = fetch_openrouter_status()
    countdown, reset_at = reset_countdown_vietnam()
    now_clock = datetime.now(VIETNAM_TZ).strftime("%H:%M:%S")
    using_free_variant = CLAUDE_MODEL.endswith(":free")

    print("\n" + "─" * 50)
    print(f"💳 OPENROUTER METER  ·  🕐 Vietnam {now_clock}")
    print("─" * 50)

    if not data:
        print("   ⚠️  Could not load balance (check internet / API key)")
    else:
        remaining = data.get("limit_remaining")
        limit = data.get("limit")
        daily = data.get("usage_daily", 0) or 0
        total_used = data.get("usage", 0) or 0
        free_tier = data.get("is_free_tier", False)
        tier = "free account (never bought credits)" if free_tier else "paid account"

        print(f"   🤖 Current model: {CLAUDE_MODEL}")
        if remaining is None:
            print("   Key spending cap: unlimited")
        else:
            print(f"   Key spending cap: {credit_meter_bar(remaining, limit)}")

        print(f"   Spent today (UTC): {daily:.4f} credits")
        print(f"   Spent all time:   {total_used:.4f} credits")
        print(f"   Account type:     {tier}")

        is_free_model = using_free_variant or CLAUDE_MODEL == "openrouter/free"
        if free_tier and not is_free_model:
            print("   ⚠️  Paid models need money in your OpenRouter wallet.")
            print("      The bar above is only the KEY limit, not wallet cash.")
            print("      Fix: in .env set CLAUDE_MODEL=openrouter/free")
        elif is_free_model:
            print("   ✅ Using a free model — no wallet credits needed.")
            print("      (Daily request limits still apply on OpenRouter.)")

    print(f"   ⏰ Daily UTC clock resets in: {countdown}  (midnight VN: {reset_at})")
    print(f"   📞 Claude calls this session: {SESSION_API_CALLS}")

    if LAST_CALL_TOKENS:
        t = LAST_CALL_TOKENS
        print(
            f"   🎯 Last call tokens: {t['total']} total "
            f"(in {t['prompt']} · out {t['completion']})"
        )
    print("─" * 50 + "\n")
def save_message(notebook_id, role, text):
    history_file = CHAT_HISTORY_DIR / f"{notebook_id}.json"
    data = []
    if history_file.exists():
        data = json.loads(history_file.read_text())
    data.append({"role": role, "text": text, "timestamp": datetime.now().isoformat()})
    history_file.write_text(json.dumps(data, indent=2))

def load_chat_history(notebook_id):
    history_file = CHAT_HISTORY_DIR / f"{notebook_id}.json"
    if history_file.exists():
        return json.loads(history_file.read_text())
    return []

def ask_question(notebook_id):
    """
    Ask a question and get analysis.
    Returns 'end', 'change', or None (fix #3).
    """
    print("╔════════════════════════════════════════╗")
    print("║  NotebookLM → Claude Research Agent    ║")
    print("╚════════════════════════════════════════╝\n")

    question = input("📝 What do you want to research? ").strip()

    if not question:
        print("❌ Question required")
        return None

    q_lower = question.lower()
    if q_lower == "end":
        return "end"
    if q_lower == "change notebook":
        return "change"
    if q_lower in ("balance", "credits", "meter"):
        print_credit_meter()
        return None

    print("\n📚 Querying NotebookLM...")
    nb_data = query_notebooklm(question, notebook_id)

    if not nb_data:
        print("❌ Failed to get NotebookLM response")
        return None

    answer = nb_data.get("answer") or ""
    print(f"✅ Got response ({len(answer)} chars)")

    if not answer.strip():
        print("❌ NotebookLM returned an empty answer.")
        return None

    print("\n🤖 Sending to Claude for analysis...")
    claude_analysis = analyze_with_claude(answer)

    if not claude_analysis:
        print("❌ Failed to get Claude response")
        return None

    print("✅ Claude analysis complete")

    print("\n" + "=" * 50)
    print("📊 CLAUDE'S ANALYSIS:")
    print("=" * 50)

    full_analysis = ""
    for chunk in claude_analysis:
        print(chunk, end="", flush=True)
        full_analysis += chunk
    claude_analysis = full_analysis

    save_report(question, nb_data, claude_analysis)
    CHAT_HISTORY_DIR = PROJECT_DIR / "chat_history"
    CHAT_HISTORY_DIR.mkdir(exist_ok=True)
    print_credit_meter()
    return None


def change_notebook():
    """Refresh notebook list and let user pick another (fix #8)."""
    notebooks = fetch_notebooks()
    if not notebooks:
        return None
    return select_notebook(notebooks)


def format_credit_meter():
    """Return credit meter text for GUI (no print)."""
    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print_credit_meter()
    return buffer.getvalue()


def run_research(question, notebook_id):
    """
    Full pipeline for GUI: NotebookLM → OpenRouter → save report.
    Returns dict with keys: ok, error, notebook_answer, analysis, report_path.
    """
    question = (question or "").strip()
    if not question:
        return {"ok": False, "error": "Question is empty."}
    if not api_key_configured():
        return {
            "ok": False,
            "error": "OpenRouter API key missing. Open Settings and paste your free key.",
        }

    nb_data = query_notebooklm(question, notebook_id)
    if not nb_data:
        return {"ok": False, "error": "NotebookLM failed. Try Login NotebookLM in the app."}

    answer = (nb_data.get("answer") or "").strip()
    if not answer:
        return {"ok": False, "error": "NotebookLM returned an empty answer."}

    analysis = ""
    for chunk in analyze_with_claude(answer):
        analysis += chunk

    if not analysis:
        return {
            "ok": False,
            "error": "AI analysis failed. Check model (use openrouter/free) or credits.",
            "notebook_answer": answer,
        }

    report_path = save_report(question, nb_data, analysis)
    return {
        "ok": True,
        "notebook_answer": answer,
        "analysis": analysis,
        "report_path": report_path,
    }


def list_all_conversations(notebook_id):
    """Get all conversation metadata for a notebook."""
    history_file = CHAT_HISTORY_DIR / f"{notebook_id}.json"
    if not history_file.exists():
        return []

    data = json.loads(history_file.read_text())
    if not data:
        return []

    # Group messages into conversations (user msg + assistant response = 1 conversation)
    conversations = []
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            user_msg = data[i]
            assistant_msg = data[i + 1]
            conversations.append({
                "index": i // 2,
                "question": user_msg["text"][:60] + "..." if len(user_msg["text"]) > 60 else user_msg["text"],
                "timestamp": user_msg["timestamp"],
                "msg_count": 2,
            })

    return sorted(conversations, key=lambda x: x["timestamp"], reverse=True)


def get_conversation_stats(notebook_id):
    """Get total messages and estimated cost for notebook."""
    data = load_chat_history(notebook_id)
    msg_count = len(data)
    # Rough estimate: ~0.01 per message (adjust based on your rate)
    estimated_cost = msg_count * 0.001
    return {"msg_count": msg_count, "cost": f"${estimated_cost:.3f}"}


def search_conversations(notebook_id, keyword):
    """Search past conversations by keyword."""
    conversations = list_all_conversations(notebook_id)
    return [c for c in conversations if keyword.lower() in c["question"].lower()]


def load_conversation_by_index(notebook_id, conv_index):
    """Load a specific conversation (user Q + assistant A) by index."""
    history_file = CHAT_HISTORY_DIR / f"{notebook_id}.json"
    if not history_file.exists():
        return None

    data = json.loads(history_file.read_text())
    start_idx = conv_index * 2
    if start_idx + 1 < len(data):
        return {
            "question": data[start_idx]["text"],
            "answer": data[start_idx + 1]["text"],
        }
    return None

if __name__ == "__main__":
    try:
        if not api_key_configured():
            print("❌ OPENROUTER_API_KEY is not set.")
            print("   One-time setup:")
            print("   1. Copy .env.example to .env")
            print("   2. Paste your OpenRouter key in .env (one time only)")
            print(f"   3. Save .env in: {PROJECT_DIR}")
            raise SystemExit(1)

        print(f"📂 Running: {Path(__file__).resolve()}")
        print(f"🤖 Claude model: {CLAUDE_MODEL}\n")

        notebooks = ensure_notebooklm_login()
        if not notebooks:
            raise SystemExit(1)

        picked = select_notebook(notebooks)
        if not picked:
            raise SystemExit(1)

        notebook_id, _notebook_title = picked

        print_credit_meter()
        print(
            "💡 Tips: 'end' = exit · 'change notebook' = switch · "
            "'balance' / 'meter' = show credits\n"
        )

        while True:
            result = ask_question(notebook_id)

            if result == "end":
                print("Goodbye! 👋")
                break

            if result == "change":
                new_pick = change_notebook()
                if new_pick:
                    notebook_id, _ = new_pick
                    print_credit_meter()
                continue

            print("\n" + "=" * 50)
            choice = input(
                "📝 Next: (question / change notebook / end / balance): "
            ).lower().strip()

            if choice == "end":
                print("Goodbye! 👋")
                break
            if choice in ("balance", "credits", "meter"):
                print_credit_meter()
                continue
            if choice == "change notebook":
                new_pick = change_notebook()
                if new_pick:
                    notebook_id, _ = new_pick
                    print_credit_meter()
                continue

    except KeyboardInterrupt:
        print("\n\nSession interrupted. Goodbye! 👋")
        raise SystemExit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)[:200]}")
        raise SystemExit(1)
