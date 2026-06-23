import google.generativeai as genai
import json
import streamlit as st

# 1. API Key Fixer: Agar Streamlit ne galti se list bana di hai, toh pehli key utha lo
raw_key = st.secrets["AQ.Ab8RN6JuAh1uLkTtLpBYONwYTY0ctyts2M7OL3MucnsLke4nPA"]
safe_key = raw_key if isinstance(raw_key, list) else str(raw_key).strip()

genai.configure(api_key=safe_key)

def generate_paathsala_dpp(subject, topic, target_class):
    # 2. Sabse Fast aur Standard Model 
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert exam paper setter. Create a Daily Practice Problem (DPP) for Class {target_class} on the Subject '{subject}' and Topic '{topic}'.
    You MUST output strictly in the following JSON format. Do not add any extra text:
    {{
      "header": {{"class": "{target_class}", "subject": "{subject}", "topic": "{topic}"}},
      "section_a": [{{"q_no": 1, "question": "Question text", "options": {{"a": "1", "b": "2", "c": "3", "d": "4"}}, "answer": "a"}}],
      "section_b": [{{"q_no": 11, "question": "Short answer", "key_point": "Brief answer"}}],
      "section_c": [{{"q_no": 16, "question": "Long answer", "key_point": "Detailed steps"}}]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        # 3. BACKUP PLAN: Agar 'flash' model API key ke karan fail hua, toh 'pro' try karega
        try:
            backup_model = genai.GenerativeModel('gemini-pro')
            response = backup_model.generate_content(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as backup_e:
            st.error(f"⚠️ API Error: {backup_e}. Kripya Streamlit Secrets mein check karein ki API key sahi hai.")
            return None
