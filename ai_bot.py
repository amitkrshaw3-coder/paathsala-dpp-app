import json
import sqlite3
import urllib.request
import urllib.error
import re
import os
from datetime import datetime

# ==========================================
# 1. PERMANENT SQLITE MEMORY SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
DB_FILE = os.path.join(BASE_DIR, "bot_brain.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT DEFAULT 'general',
                    fact TEXT UNIQUE,
                    source TEXT DEFAULT 'user',
                    created_at TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_query TEXT,
                    wrong_reply TEXT,
                    correct_reply TEXT,
                    created_at TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. SMART MEMORY & CORRECTION SEARCH
# ==========================================
def get_relevant_context(user_text):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute("SELECT id, category, fact FROM memories ORDER BY id DESC")
        all_memories = c.fetchall()
        
        c.execute("SELECT user_query, correct_reply FROM corrections ORDER BY id DESC")
        all_corrections = c.fetchall()
        conn.close()

        words = set(re.findall(r'\w+', user_text.lower()))
        
        scored_memories = []
        for mid, cat, fact in all_memories:
            fact_words = set(re.findall(r'\w+', fact.lower()))
            overlap = len(words.intersection(fact_words))
            if overlap > 0 or cat in ['rule', 'profile']:
                scored_memories.append((overlap, f"[{cat.upper()}] {fact}"))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        selected_memories = [m[1] for m in scored_memories[:8]]

        relevant_corrections = []
        for uq, cr in all_corrections:
            uq_words = set(re.findall(r'\w+', uq.lower()))
            if len(words.intersection(uq_words)) > 0:
                relevant_corrections.append(f"Q: '{uq}' -> Sahi Jawab: '{cr}'")

        return selected_memories, relevant_corrections[:4]
    except Exception:
        return [], []

def save_learned_fact(fact):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO memories (category, fact, created_at) VALUES (?, ?, ?)",
            ("auto_learned", fact, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

# ==========================================
# 3. FREE POLLINATIONS AI API CALL
# ==========================================
def call_ai_api(messages):
    url = "https://text.pollinations.ai/"
    payload = json.dumps({
        "messages": messages,
        "model": "openai"
    }).encode("utf-8")

    req = urllib.request.Request(
        url, 
        data=payload, 
        headers={
            "Content-Type": "application/json",
            "User-Agent": "PaathsalaAIBot/2.0"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8").strip()
            if status_code != 200:
                return False, f"API HTTP Error: Status {status_code}"
            if not body:
                return False, "API ne khali response bheja."
            return True, body
    except urllib.error.HTTPError as e:
        return False, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Network Error: Internet check karein ({e.reason})"
    except Exception as e:
        return False, f"System Error: {str(e)}"

# ==========================================
# 4. MAIN FUNCTION FOR PAATHSALA CHAT.PY
# ==========================================
def ask_paathsala_ai(question):
    try:
        user_msg = question.strip()
        if not user_msg:
            return "⚠️ Kripya `@ai` ke baad apna sawal likhein."

        relevant_mems, relevant_corrs = get_relevant_context(user_msg)
        now_str = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

        sys_parts = [
            f"Tumhara naam PAATHSALA AI Tutor hai. Current Date/Time: {now_str}.",
            "Tum competitive exams (UPSC, RRB, IBPS, SSC, CTET) ki taiyari karne wale students ke doubts solve karte ho.",
            "Student ke doubt ko simple, clear aur step-by-step Hinglish ya English mein samjhao.",
            "Agar student koi zaroori exam rule ya fact bataye, toh reply ke bilkul end mein [LEARN: fact] likho."
        ]
        
        if relevant_mems:
            sys_parts.append("\n[RELEVANT PERMANENT MEMORIES]:\n" + "\n".join(relevant_mems))
        if relevant_corrs:
            sys_parts.append("\n[PAST MISTAKES TO AVOID / LEARNED ANSWERS]:\n" + "\n".join(relevant_corrs))

        api_messages = [
            {"role": "system", "content": "\n".join(sys_parts)},
            {"role": "user", "content": user_msg}
        ]

        ok, ai_reply = call_ai_api(api_messages)
        if not ok:
            return f"⚠️ AI Error: {ai_reply}"

        # Agar AI ne kuch naya seekha hai ([LEARN: ...]), toh use SQLite mein save kar lo aur text se hata do
        learn_regex = re.compile(r'\[LEARN:\s*(.*?)\]', re.IGNORECASE)
        suggested = [m.strip() for m in learn_regex.findall(ai_reply) if m.strip()]
        for fact in suggested:
            save_learned_fact(fact)

        clean_reply = learn_regex.sub("", ai_reply).strip()
        return clean_reply

    except Exception as e:
        return f"⚠️ AI Error: {e}"
