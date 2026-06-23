import json
import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_paathsala_dpp(subject, topic, target_class):
    prompt = f"""
    You are an expert exam paper setter. Create a Daily Practice Problem (DPP) for Class {target_class} on the Subject '{subject}' and Topic '{topic}'.
    
    CRITICAL MATH FORMATTING RULES:
    1. You MUST use LaTeX for ALL mathematical symbols, powers, fractions, and integrals.
    2. Enclose all math expressions in single dollar signs (e.g., $x^2$, $\\int x dx$).
    3. Since this is a JSON output, you must double-escape the backslashes for LaTeX commands so the JSON doesn't break (e.g., use \\\\int instead of \\int).
    
    You MUST output strictly in the following JSON format. Do not add any extra text:
    {{
      "header": {{"class": "{target_class}", "subject": "{subject}", "topic": "{topic}"}},
      "section_a": [{{"q_no": 1, "question": "Evaluate $\\\\int x^2 dx$", "options": {{"a": "$x^3/3$", "b": "2", "c": "3", "d": "4"}}, "answer": "a"}}],
      "section_b": [{{"q_no": 11, "question": "Short answer", "key_point": "Brief answer"}}],
      "section_c": [{{"q_no": 16, "question": "Long answer", "key_point": "Detailed steps"}}]
    }}
    """
    
    try:
        # API Request
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            temperature=0.5,
        )
        
        raw_text = None
        
        # 🔍 STEP 1: Standard SDK method se try karein
        try:
            raw_text = chat_completion.choices.message.content
        except:
            pass
            
        # 🔍 STEP 2: Agar Dictionary format hai, toh usse try karein
        if not raw_text:
            try:
                raw_text = chat_completion['choices']['message']['content']
            except:
                pass
        
        # 🔍 STEP 3: Deep Recursive Scanner (Agar sab fail ho jaye, toh yeh data dhoondhega)
        if not raw_text:
            def deep_scanner(obj):
                if isinstance(obj, dict):
                    if 'content' in obj and isinstance(obj['content'], str) and '{' in obj['content']:
                        return obj['content']
                    for v in obj.values():
                        res = deep_scanner(v)
                        if res: return res
                elif isinstance(obj, list):
                    for item in obj:
                        res = deep_scanner(item)
                        if res: return res
                elif hasattr(obj, '__dict__') or dir(obj):
                    try:
                        if hasattr(obj, 'content') and isinstance(obj.content, str) and '{' in obj.content:
                            return obj.content
                    except: pass
                    try:
                        for attr in dir(obj):
                            if not attr.startswith('_'):
                                val = getattr(obj, attr)
                                if not callable(val):
                                    res = deep_scanner(val)
                                    if res: return res
                    except: pass
                return None
                
            raw_text = deep_scanner(chat_completion)

        if not raw_text:
            st.error("⚠️ AI Response structure completely unrecognized.")
            return None

        # JSON Cleaning
        clean_text = raw_text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json").split("```").strip()
        elif "```" in clean_text:
            clean_text = clean_text.split("```").split("```").strip()

        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"⚠️ API Error: {e}")
        return None
