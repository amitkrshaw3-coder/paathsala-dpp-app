import json
import streamlit as st
import google.generativeai as genai

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
    
    try:
        # Google SDK Setup
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # 🚀 FIX: Aapke screenshot mein mojood naya model use kar rahe hain
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        # Request generation
        response = model.generate_content(prompt)
        raw_text = response.text
        
        # JSON Cleaner
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            clean_text = clean_text[start_idx:end_idx]
            
        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"⚠️ Gemini SDK Error: {e}")
        return None
