import json
import urllib.request
import urllib.error
import streamlit as st

def generate_paathsala_dpp(subject, topic, target_class):
    prompt = f"""
    You are an expert exam paper setter. Create a Daily Practice Problem (DPP) for Class {target_class} on the Subject '{subject}' and Topic '{topic}'.
    
    CRITICAL MATH FORMATTING RULES FOR PDF COMPATIBILITY:
    1. STRICTLY USE ONLY BASIC ASCII KEYBOARD CHARACTERS. 
    2. DO NOT use any special Unicode math symbols (like integration signs, superscript squares, etc.). The system will CRASH if you use them.
    3. For integrals, write "Integral of" (e.g., "Integral of x^2 dx").
    4. For powers/exponents, use the caret symbol '^' (e.g., x^2, y^3).
    5. For fractions, use standard slash 'a/b' format.
    6. For Greek letters, spell them out completely in English (e.g., "theta", "pi", "alpha").
    
    Output ONLY valid JSON.
    {{
      "header": {{"class": "{target_class}", "subject": "{subject}", "topic": "{topic}"}},
      "section_a": [{{"q_no": 1, "question": "Evaluate the Integral of x^2 dx", "options": {{"a": "x^3 / 3", "b": "2x", "c": "3", "d": "4"}}, "answer": "a"}}],
      "section_b": [{{"q_no": 11, "question": "Short answer", "key_point": "Brief answer"}}],
      "section_c": [{{"q_no": 16, "question": "Long answer", "key_point": "Detailed steps"}}]
    }}
    """
    
    # URL SE '-latest' HATA DIYA GAYA HAI
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.5,
            "responseMimeType": "application/json"
        }
    }).encode("utf-8")
    
    headers = {
        "x-goog-api-key": st.secrets["GEMINI_API_KEY"],
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_text = response.read().decode("utf-8")
            result = json.loads(response_text)
            
            raw_text = result["candidates"]["content"]["parts"]["text"]
            
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
                
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        st.error(f"⚠️ Gemini Server Error ({e.code}): {error_msg}")
        return None
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return None
