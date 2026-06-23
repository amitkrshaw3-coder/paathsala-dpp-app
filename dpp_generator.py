import google.generativeai as genai
import json
import streamlit as st

# API key configure karein
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_paathsala_dpp(subject, topic, target_class):
    try:
        # 1. API se pucho aur SIRF 'Gemini' models filter karo jo text generate kar sakein
        valid_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower():
                valid_models.append(m.name)
        
        # Agar koi Gemini model nahi milta
        if not valid_models:
            st.error("⚠️ Error: Aapki API Key mein Gemini models active nahi hain. Nayi API key banayein.")
            return None
            
        # 2. Jo sabse pehla valid Gemini model mile (jaise models/gemini-1.5-flash), use chun lo
        chosen_model = valid_models 
        model = genai.GenerativeModel(chosen_model)
        
        # 3. AI ko instruction dena
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
        
        # 4. JSON generate karwana
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        # Koi aur error ho toh screen par dikhaye
        st.error(f"⚠️ Google AI Error: {e}")
        return None
