import requests
import urllib.parse
import random
from datetime import datetime

# ==========================================
# CLOUD-SAFE & ACCURATE FREE AI ENGINE
# ==========================================
def ask_paathsala_ai(question):
    user_msg = question.strip()
    if not user_msg:
        return "⚠️ Kripya `@ai` ke baad apna sawal likhein."

    now_str = datetime.now().strftime("%d %B %Y")
    
    # Short & strict system prompt (No slashes '/', so URL never breaks)
    system_prompt = (
        f"You are PAATHSALA AI Tutor for Indian Competitive Exams (Date: {now_str}). "
        "Rules: 1. Give 100% accurate facts for RRB Group D, NTPC, SSC, UPSC, IBPS, CTET. "
        "2. RRB Group D (Level-1) eligibility is 10th pass or ITI, age 18-33 years, selection process is CBT, PET (Physical), Document Verification and Medical (NO interview or counselling). "
        "3. Never invent fake exam dates; say official dates are not announced yet if unknown. "
        "4. Reply in simple Hinglish using crisp bullet points under 150 words."
    )

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    # ----------------------------------------------------
    # ROUTE 1: Official /openai POST Endpoint (Multiple Models)
    # ----------------------------------------------------
    # Agar 'openai' 402 dega, toh 'qwen-coder' aur 'llama' Cloud IP par bina block huye chalenge
    models_to_try = ["openai", "qwen-coder", "llama", "mistral"]

    for model_name in models_to_try:
        try:
            res = requests.post(
                "https://text.pollinations.ai/openai",
                headers=headers,
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    "temperature": 0.1,
                    "seed": random.randint(1, 99999)
                },
                timeout=25
            )
            if res.status_code == 200:
                data = res.json()
                reply = data["choices"][0]["message"]["content"].strip()
                if reply and "Payment Required" not in reply:
                    return reply
        except Exception:
            continue

    # ----------------------------------------------------
    # ROUTE 2: Root POST Endpoint Backup
    # ----------------------------------------------------
    for model_name in ["qwen-coder", "llama", "mistral"]:
        try:
            res = requests.post(
                "https://text.pollinations.ai/",
                headers=headers,
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    "model": model_name,
                    "seed": random.randint(1, 99999)
                },
                timeout=25
            )
            if res.status_code == 200 and res.text.strip() and "Payment Required" not in res.text:
                return res.text.strip()
        except Exception:
            continue

    # ----------------------------------------------------
    # ROUTE 3: Clean GET Endpoint (Fixes HTTP 404 Not Found!)
    # ----------------------------------------------------
    try:
        # Path mein sirf chota question jayega, system prompt query parameter (?system=...) mein jayega!
        clean_q = urllib.parse.quote(user_msg.replace("/", " "))
        clean_sys = urllib.parse.quote(system_prompt)
        get_url = f"https://text.pollinations.ai/{clean_q}?system={clean_sys}&seed={random.randint(1,9999)}"

        res = requests.get(get_url, headers={"User-Agent": headers["User-Agent"]}, timeout=25)
        if res.status_code == 200 and res.text.strip() and "Payment Required" not in res.text:
            return res.text.strip()
        else:
            return f"⚠️ AI Notice: Server status {res.status_code}"
    except Exception as e:
        return f"⚠️ AI Notice: Connection issue ({str(e)})"
