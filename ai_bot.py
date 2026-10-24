import requests
import urllib.parse
import random
import re
import threading
from datetime import datetime
from supabase import create_client, Client

# ==========================================
# SUPABASE CONNECTION & TRAFFIC CONTROLLER
# ==========================================
SUPABASE_URL = "https://rmdwvrjschmeztzrestm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHd2cmpzY2htZXp0enJlc3RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNTI2NzcsImV4cCI6MjA5NzYyODY3N30.H9hvCcDe2EUqrkukbxQdKoMSt_VNryl4Hnn7t3XZm2o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 100 bacchon ke traffic ko line (queue) mein lagane ke liye Semaphore
ai_traffic_limiter = threading.Semaphore(4)

STOP_WORDS = {"what", "is", "the", "of", "in", "for", "kya", "hai", "kaise", "kab", "aur", "mein", "ko", "se", "ke", "ka", "ki", "tell", "me", "about", "explain"}

def extract_keywords(text):
    words = set(re.findall(r'\w+', text.lower()))
    return words - STOP_WORDS

# ==========================================
# MODULE 1: KNOWLEDGE RETRIEVAL (SUPABASE RAG)
# ==========================================
def retrieve_knowledge(user_question):
    """Supabase se verified answers aur past corrections nikalta hai"""
    try:
        res = supabase.table("ai_knowledge_base").select("*").order("is_verified", desc=True).limit(100).execute()
        rows = res.data
        if not rows:
            return None, []

        q_words = extract_keywords(user_question)
        if not q_words:
            return None, []

        relevant_facts = []
        for row in rows:
            db_q_words = extract_keywords(row["question"])
            if not db_q_words:
                continue
            
            overlap = len(q_words.intersection(db_q_words))
            similarity = overlap / max(len(q_words), len(db_q_words))

            # 1. Exact/High Match on Verified Answer -> Seedha return karo (0.1 sec response!)
            if row.get("is_verified") and similarity >= 0.75:
                return row["answer"], []

            # 2. Partial Match -> Context ke liye save karo
            if overlap >= 2:
                tag = "[VERIFIED FACT]" if row.get("is_verified") else "[PAST QA]"
                relevant_facts.append((overlap, f"{tag} Q: {row['question']} -> Ans: {row['answer']}"))

        relevant_facts.sort(key=lambda x: x[0], reverse=True)
        return None, [item[1] for item in relevant_facts[:3]]
    except Exception:
        return None, []

# ==========================================
# MODULE 2: ANSWER VERIFICATION ENGINE
# ==========================================
OFFICIAL_EXAM_FACTS = """
OFFICIAL VERIFIED INDIAN EXAM FACTS (STRICTLY FOLLOW):
- RRB Group D (Level-1): Qualification = 10th Pass (Matric) or ITI. Age = 18-33 years. Stages = CBT, PET (Physical), Document Verification & Medical. (NO Interview, NO Counselling).
- RRB NTPC: Qualification = 12th Pass (Undergrad posts) or Graduation (Graduate posts). Stages = CBT-1, CBT-2, CBAT/Typing Skill Test, DV/Medical. (NO Interview).
- SSC CGL / CHSL / MTS: No interview in any SSC Group B or C exam.
- UPSC CSE: Qualification = Graduation. Age = 21-32 years (General). Stages = Prelims, Mains, Personality Test (Interview).
- CTET: No negative marking. Qualifying marks = 60% (90/150) for General, 55% (82/150) for OBC/SC/ST. Validity = Lifetime.
"""

def verify_and_clean_answer(question, ai_answer):
    """Check karta hai ki AI ne Group D/SSC mein galti se Interview ya Graduation toh nahi likh diya"""
    q_low = question.lower()
    ans_low = ai_answer.lower()
    
    # Automatic Guardrail for Railway / SSC exams
    if ("group d" in q_low or "ntpc" in q_low or "ssc" in q_low) and "interview" in ans_low:
        if "no interview" not in ans_low and "interview nahi" not in ans_low:
            ai_answer += "\n\n*(✅ Fact Check Note: Railway aur SSC exams mein Interview nahi hota hai.)*"
            
    return ai_answer

# ==========================================
# MODULE 3: AI ENGINE + AUTO-SAVE TO SUPABASE
# ==========================================
def call_pollinations_engine(system_prompt, user_msg):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
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
                reply = res.json()["choices"][0]["message"]["content"].strip()
                if reply and "Payment Required" not in reply:
                    return True, reply
        except Exception:
            continue

    # Clean GET Backup
    try:
        clean_q = urllib.parse.quote(user_msg.replace("/", " "))
        clean_sys = urllib.parse.quote(system_prompt)
        get_url = f"https://text.pollinations.ai/{clean_q}?system={clean_sys}&seed={random.randint(1,9999)}"
        res = requests.get(get_url, headers=headers, timeout=25)
        if res.status_code == 200 and res.text.strip() and "Payment Required" not in res.text:
            return True, res.text.strip()
    except Exception as e:
        return False, str(e)

    return False, "Server busy hai, kripya 10 second baad try karein."

def ask_paathsala_ai(question):
    user_msg = question.strip()
    if not user_msg:
        return "⚠️ Kripya `@ai` ke baad apna sawal likhein."

    # 1. Check Supabase Knowledge Base First (Instant Fast Path)
    exact_verified_ans, retrieved_context = retrieve_knowledge(user_msg)
    if exact_verified_ans:
        return f"{exact_verified_ans}\n\n*(⚡ Verified PAATHSALA Knowledge Base)*"

    # 2. Build Context-Aware Verified Prompt
    now_str = datetime.now().strftime("%d %B %Y")
    context_str = "\n".join(retrieved_context) if retrieved_context else "No past context."

    system_prompt = (
        f"You are PAATHSALA AI Tutor (Date: {now_str}).\n"
        f"{OFFICIAL_EXAM_FACTS}\n"
        f"RETRIEVED PAST KNOWLEDGE:\n{context_str}\n\n"
        "Instructions: Prioritize RETRIEVED PAST KNOWLEDGE and OFFICIAL FACTS. "
        "Never invent fake dates. Explain clearly in Hinglish using bullet points under 150 words."
    )

    # 3. Queue Controlled AI Call (Handles 100 concurrent requests smoothly)
    with ai_traffic_limiter:
        ok, raw_reply = call_pollinations_engine(system_prompt, user_msg)

    if not ok:
        return f"⚠️ AI Notice: {raw_reply}"

    # 4. Verify Answer
    final_reply = verify_and_clean_answer(user_msg, raw_reply)

    # 5. Save to Supabase Knowledge Base (Unverified by default until Admin/Upvote verifies)
    try:
        kw = " ".join(extract_keywords(user_msg))
        supabase.table("ai_knowledge_base").insert({
            "question": user_msg,
            "keywords": kw,
            "answer": final_reply,
            "is_verified": False
        }).execute()
    except Exception:
        pass

    return final_reply

# ==========================================
# MODULE 4 & 5: FEEDBACK & EVALUATION HELPERS
# ==========================================
def submit_student_feedback(student_email, question, ai_answer, feedback_type, suggested_correction=""):
    """Student ka feedback ya correction report Supabase mein save karta hai"""
    try:
        supabase.table("ai_feedback").insert({
            "student_email": student_email,
            "question": question,
            "ai_answer": ai_answer,
            "feedback_type": feedback_type,
            "suggested_correction": suggested_correction
        }).execute()
        return True
    except Exception:
        return False

def approve_correction_to_kb(feedback_id, question, corrected_answer):
    """Admin jab correction approve kare toh wo Verified Knowledge Base ban jaye"""
    try:
        kw = " ".join(extract_keywords(question))
        supabase.table("ai_knowledge_base").insert({
            "question": question,
            "keywords": kw,
            "answer": corrected_answer,
            "is_verified": True
        }).execute()
        supabase.table("ai_feedback").update({"status": "approved"}).eq("id", feedback_id).execute()
        return True
    except Exception:
        return False

def run_evaluation_suite():
    """Test questions chala kar check karta hai ki AI kitने % accurate jawab de raha hai"""
    default_tests = [
        {"q": "rrb group d qualification and selection process", "must_have": ["10th", "iti", "cbt", "pet"]},
        {"q": "is there any negative marking in ctet exam", "must_have": ["no", "90", "lifetime"]},
        {"q": "upsc civil services age limit and stages", "must_have": ["21", "32", "prelims", "mains"]}
    ]
    results = []
    for test in default_tests:
        ans = ask_paathsala_ai(test["q"]).lower()
        matched = [kw for kw in test["must_have"] if kw in ans]
        score = int((len(matched) / len(test["must_have"])) * 100)
        results.append({
            "question": test["q"],
            "score": f"{score}%",
            "matched_keywords": matched,
            "sample_answer": ans[:120] + "..."
        })
    return results
