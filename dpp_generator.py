import json
import urllib.request
import urllib.error
import streamlit as st

def generate_paathsala_dpp(subject, topic, target_class):
    prompt = f"""
    You are an expert exam paper setter. Create a Daily Practice Problem (DPP) for Class {target_class} on the Subject '{subject}' and Topic '{topic}'.
    
    CRITICAL MATH FORMATTING RULES FOR PDF COMPATIBILITY (PREVENT LATIN-1 ERROR):
    1. STRICTLY USE ONLY BASIC ASCII KEYBOARD CHARACTERS. 
    2. DO NOT use any special Unicode math symbols (like ∫, ², ³, θ, π). The system will CRASH if you use them.
    3. For integrals, write the word "Integral of" or "INT()". (e.g., "Integral of x^2 dx").
    4. For powers/exponents, use the caret symbol '^' (e.g., x^2, y^3).
    5. For fractions, use standard slash 'a/b' format.
    6. For Greek letters, spell them out completely in English letters (e.g., "theta", "pi", "alpha").
    
    Output ONLY valid JSON.
    {{
      "header": {{"class": "{target_class}", "subject": "{subject}", "topic": "{topic}"}},
      "section_a": [{{"q_no": 1, "question": "Evaluate the Integral of x^2 dx", "options": {{"a": "x^3 / 3", "b": "2x", "c": "3", "d": "4"}}, "answer": "a"}}],
      "section_b": [{{"q_no": 11, "question": "Short answer", "key_point": "Brief answer"}}],
      "section_c": [{{"q_no": 16, "question": "Long answer", "key_point": "Detailed steps"}}]
    }}
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = json.dumps({
        # AI ka Sabse Smart aur Bada model
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "response_format": {"type": "json_object"}
    }).encode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_text = response.read().decode("utf-8")
            result = json.loads(response_text)
            
            # The Ghost Scanner
            def dhoondho_dpp(obj):
                if isinstance(obj, dict):
                    if 'content' in obj and isinstance(obj['content'], str) and '"header"' in obj['content']:
                        return obj['content']
                    for key, value in obj.items():
                        res = dhoondho_dpp(value)
                        if res: return res
                elif isinstance(obj, list):
                    for item in obj:
                        res = dhoondho_dpp(item)
                        if res: return res
                return None
                
            raw_text = dhoondho_dpp(result)
            
            if raw_text:
                clean_text = raw_text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)
            else:
                st.error("⚠️ Scanner ko AI ke data mein DPP nahi mila.")
                return None
                
    except Exception as e:
        st.error(f"⚠️ Ultimate Error: {e}")
        return None
