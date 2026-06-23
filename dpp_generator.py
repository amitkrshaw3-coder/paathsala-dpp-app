import json
import urllib.request
import urllib.error
import streamlit as st

def generate_paathsala_dpp(subject, topic, target_class):
    prompt = f"""
    You are an expert exam paper setter. Create a Daily Practice Problem (DPP) for Class {target_class} on the Subject '{subject}' and Topic '{topic}'.
    
    CRITICAL MATH FORMATTING RULES FOR PDF COMPATIBILITY:
    1. STRICTLY DO NOT USE LaTeX. The PDF generator cannot render backslashes or dollar signs.
    2. USE UNICODE MATH SYMBOLS DIRECTLY: 
       - For integration, use the Unicode symbol '∫' (e.g., ∫ x² dx).
       - For powers/exponents, use Unicode superscripts like '²' (square) and '³' (cube).
       - For fractions, use standard slash 'a/b' format.
       - For Greek letters, use standard Unicode symbols like 'θ', 'π', 'α', 'β'.
    3. Ensure NO LaTeX commands or dollar signs appear in the final output.
    
    Output ONLY valid JSON.
    {{
      "header": {{"class": "{target_class}", "subject": "{subject}", "topic": "{topic}"}},
      "section_a": [{{"q_no": 1, "question": "Evaluate ∫ x² dx", "options": {{"a": "x³ / 3", "b": "2x", "c": "3", "d": "4"}}, "answer": "a"}}],
      "section_b": [{{"q_no": 11, "question": "Short answer", "key_point": "Brief answer"}}],
      "section_c": [{{"q_no": 16, "question": "Long answer", "key_point": "Detailed steps"}}]
    }}
    """
    
    # FIX: Model ka sahi aur poora naam (-latest add kiya gaya hai)
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    
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
            
            # Gemini ke result se text nikalna
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
