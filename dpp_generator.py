import google.generativeai as genai
import json
import streamlit as st

# API key configure karein
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_paathsala_dpp(subject, topic, target_class):
    try:
        # 1. API se pucho ki kaun se models available hain (Ab naam guess nahi karna padega)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            st.error("⚠️ Error: Aapki API Key mein koi bhi text model available nahi hai. Kripya nayi API key banayein.")
            return None
            
        # 2. Jo bhi best model mile, usko automatically chun lo
        chosen_model = available_models # Default pehla model
        for m in available_models:
            if '1.5-flash' in m:
                chosen_model = m
                break
            elif 'pro' in m:
                chosen_model = m
                
        # 3. Model ko setup karo
        model = genai.GenerativeModel(chosen_model)
        
        # 4. Prompt banayein
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
        
        # 5. AI se response lo aur JSON me convert karo
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        # Koi bhi error aayegi toh app crash nahi hogi
        st.error(f"⚠️ Google AI Error: {e}")
        return None
