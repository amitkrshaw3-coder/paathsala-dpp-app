import json
import urllib.request
import urllib.error
import urllib.parse
import random
from datetime import datetime

# ==========================================
# FAST & TIMEOUT-PROOF FREE AI CALL
# ==========================================
def call_ai_api(system_prompt, user_msg):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ]

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    # Fast models first
    models_to_try = ["openai-fast", "mistral", "llama", "openai"]

    for model_name in models_to_try:
        try:
            url = "https://text.pollinations.ai/"
            payload = json.dumps({
                "messages": messages,
                "model": model_name,
                "seed": random.randint(1, 99999)
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            # 🌟 FIX 1: Timeout badha kar 45 seconds kar diya hai
            with urllib.request.urlopen(req, timeout=45) as response:
                if response.getcode() == 200:
                    body = response.read().decode("utf-8").strip()
                    if body and "Payment Required" not in body:
                        return True, body
        except urllib.error.HTTPError:
            continue
        except Exception:
            continue

    # ==========================================
    # BACKUP: Direct GET Endpoint (45s timeout)
    # ==========================================
    try:
        combined_prompt = f"{system_prompt}\n\nQuestion: {user_msg}"
        encoded_prompt = urllib.parse.quote(combined_prompt)
        get_url = f"https://text.pollinations.ai/{encoded_prompt}?model=mistral"

        req = urllib.request.Request(
            get_url,
            headers={"User-Agent": headers["User-Agent"]},
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=45) as response:
            if response.getcode() == 200:
                body = response.read().decode("utf-8").strip()
                if body:
                    return True, body
    except Exception as e:
        return False, f"Server Timeout ({str(e)})"

    return False, "Server abhi busy hai, kripya dobara try karein."


# ==========================================
# MAIN FUNCTION FOR PAATHSALA CHAT.PY
# ==========================================
def ask_paathsala_ai(question):
    try:
        user_msg = question.strip()
        if not user_msg:
            return "⚠️ Kripya `@ai` ke baad apna sawal likhein."

        now_str = datetime.now().strftime("%d %B %Y")

        # 🌟 FIX 2: AI ko crisp aur point-to-point bolne ki instruction (taaki 4-5 sec mein reply aaye)
        system_prompt = (
            f"You are PAATHSALA AI Tutor (Date: {now_str}). "
            "Help Indian students with RRB Group D, NTPC, UPSC, SSC, IBPS, and CTET doubts. "
            "IMPORTANT: Keep your answer concise, crisp, and under 150 words using bullet points in simple Hinglish so it loads quickly."
        )

        ok, ai_reply = call_ai_api(system_prompt, user_msg)
        if not ok:
            return f"⚠️ AI Error: {ai_reply}"

        return ai_reply

    except Exception as e:
        return f"⚠️ AI Error: {e}"
