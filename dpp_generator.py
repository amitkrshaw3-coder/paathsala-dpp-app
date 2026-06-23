import json
import requests
import streamlit as st

# Aapki key yahan daal di gayi hai
MY_API_KEY = "API KEY"

def generate_paathsala_dpp(subject, topic, target_class):
    # Seedha Google ke server ka direct link (Bina kisi library ke)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={MY_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
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

    # Data pack karke bhejna
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        # Direct server par hit
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        # Agar Google ne koi naya bahana banaya, toh wo screen par dikhega
        if 'error' in response_json:
            st.error(f"Google Server Reply: {response_json['error']['message']}")
            return None
            
        # Sahi data aane par extract karna
        raw_text = response_json['candidates']['content']['parts']['text']
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"System Error: {e}")
        return None
