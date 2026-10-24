import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# ==========================================
# SMART MULTI-FALLBACK FREE AI CALL
# ==========================================
def call_ai_api(system_prompt, user_msg):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ]

    # Browser headers taaki Cloud IP block na ho
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://pollinations.ai",
        "Referer": "https://pollinations.ai/"
    }

    # Try multiple free models in order (Open-source models don't give 402 easily)
    models_to_try = ["mistral", "llama", "openai"]

    for model_name in models_to_try:
        try:
            url = "https://text.pollinations.ai/"
            payload = json.dumps({
                "messages": messages,
                "model": model_name,
                "seed": 42
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() == 200:
                    body = response.read().decode("utf-8").strip()
                    if body and "Payment Required" not in body:
                        return True, body
        except urllib.error.HTTPError as e:
            # Agar 402 ya 429 aaye toh rukna nahi hai, agla model try karna hai
            continue
        except Exception:
            continue

    # ==========================================
    # FINAL BACKUP: Direct GET Request Endpoint
    # ==========================================
    try:
        combined_prompt = f"{system_prompt}\n\nStudent Question: {user_msg}"
        encoded_prompt = urllib.parse.quote(combined_prompt)
        get_url = f"https://text.pollinations.ai/{encoded_prompt}"

        req = urllib.request.Request(
            get_url,
            headers={"User-Agent": headers["User-Agent"]},
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.getcode() == 200:
                body = response.read().decode("utf-8").strip()
                if body:
                    return True, body
    except Exception as e:
        return False, f"Server Busy ({str(e)})"

    return False, "Abhi free AI server busy hai, kripya 10 second baad dobara try karein."


# ==========================================
# MAIN FUNCTION FOR PAATHSALA CHAT.PY
# ==========================================
def ask_paathsala_ai(question):
    try:
        user_msg = question.strip()
        if not user_msg:
            return "⚠️ Kripya `@ai` ke baad apna sawal likhein."

        now_str = datetime.now().strftime("%d %B %Y")

        system_prompt = (
            f"You are PAATHSALA AI Tutor (Date: {now_str}). "
            "You help Indian students preparing for competitive exams like RRB Group D, NTPC, UPSC, SSC, IBPS, and CTET. "
            "Explain the student's doubt clearly, step-by-step in simple Hinglish."
        )

        ok, ai_reply = call_ai_api(system_prompt, user_msg)
        if not ok:
            return f"⚠️ AI Notice: {ai_reply}"

        return ai_reply

    except Exception as e:
        return f"⚠️ AI Error: {e}"
