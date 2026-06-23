import google.generativeai as genai
import json
import streamlit as st

# 🛑 Yahan humne st.secrets ka use bilkul hata diya hai
# Seedha aapki key assign kar di hai
MY_API_KEY = "AQ.Ab8RN6JuAh1uLkTtLpBYONwYTY0ctyts2M7OL3MucnsLke4nPA"

genai.configure(api_key=MY_API_KEY)

def generate_paathsala_dpp(subject, topic, target_class):
    # Model select kiya
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
        # Agar koi error aayi toh app crash nahi hogi
        st.error(f"⚠️ Error details: {e}")
        return None
