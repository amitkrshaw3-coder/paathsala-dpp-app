import json
import urllib.request
import urllib.error
import urllib.parse
import random
from datetime import datetime

# ==========================================
# HIGH-ACCURACY FREE AI CALL (NO HALLUCINATION)
# ==========================================
def call_ai_api(system_prompt, user_msg):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg}
    ]

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    # 🌟 SIRF SMART MODELS: 'mistral' hata diya kyunki wo Indian exams me galat info deta hai
    # 'searchgpt' aur 'openai' (GPT-4o-mini) ko Indian exams ka accurate data pata hota hai
    accurate_models = ["openai", "searchgpt", "openai-large"]

    for model_name in accurate_models:
        try:
            url = "https://text.pollinations.ai/"
            payload = json.dumps({
                "messages": messages,
                "model": model_name,
                "temperature": 0.1,  # Strict factual mode (Tukka maarna band)
                "seed": random.randint(1, 99999)
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=40) as response:
                if response.getcode() == 200:
                    body = response.read().decode("utf-8").strip()
                    if body and "Payment Required" not in body:
                        return True, body
        except Exception:
            continue

    # ==========================================
    # BACKUP: Direct GET with OpenAI Model
    # ==========================================
    try:
        combined_prompt = f"{system_prompt}\n\nQuestion: {user_msg}"
        encoded_prompt = urllib.parse.quote(combined_prompt)
        # Yahan bhi model=openai rakha hai taaki accuracy kharab na ho
        get_url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&seed={random.randint(1,9999)}"

        req = urllib.request.Request(
            get_url,
            headers={"User-Agent": headers["User-Agent"]},
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=40) as response:
            if response.getcode() == 200:
                body = response.read().decode("utf-8").strip()
                if body and "Payment Required" not in body:
                    return True, body
    except Exception as e:
        return False, f"Server busy ({str(e)})"

    return False, "Abhi AI server busy hai, kripya 10 second baad dobara puchein."


# ==========================================
# MAIN FUNCTION FOR PAATHSALA CHAT.PY
# ==========================================
def ask_paathsala_ai(question):
    try:
        user_msg = question.strip()
        if not user_msg:
            return "⚠️ Kripya `@ai` ke baad apna sawal likhein."

        now_str = datetime.now().strftime("%d %B %Y")

        # 🌟 STRICT INDIAN EXAM PROMPT: Galat dates ya fake pattern banane se rokne ke liye
        system_prompt = (
            f"You are PAATHSALA AI Tutor, an expert on Indian Competitive Exams (Current Date: {now_str}). "
            "Follow these strict rules:\n"
            "1. Give 100% factual, official information about Indian exams (RRB Group D/NTPC, SSC, UPSC, IBPS, CTET).\n"
            "2. NEVER invent fake exam dates, fake counselling rounds, or fake interview stages.\n"
            "3. Remember: RRB Group D (Level-1) requires 10th pass/ITI, age 18-33 years, and selection is via CBT, PET (Physical), and DV/Medical (NO interview).\n"
            "4. If official dates for a year are not announced, clearly say 'Official dates abhi announce nahi hui hain'.\n"
            "5. Reply in clear, concise Hinglish using bullet points (under 150 words)."
        )

        ok, ai_reply = call_ai_api(system_prompt, user_msg)
        if not ok:
            return f"⚠️ AI Notice: {ai_reply}"

        return ai_reply

    except Exception as e:
        return f"⚠️ AI Error: {e}"
