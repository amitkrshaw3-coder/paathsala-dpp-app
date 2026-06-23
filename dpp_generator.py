import google.generativeai as genai
import json
import streamlit as st

# API key configure karein
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_paathsala_dpp(subject, topic, target_class):
    # Google ke naye format ke hisaab se 'models/' lagana zaroori hai
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
        # Ab app crash nahi hogi, seedha screen par bata degi ki dikkat kahan hai
        st.error(f"⚠️ Google AI Error: {e}")
        return None
