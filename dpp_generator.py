import json
import streamlit as st
from google import genai

# Aapki wahi AQ wali key yahan daal di hai
MY_API_KEY = "AQ.Ab8RN6JuAh1uLkTtLpBYONwYTY0ctyts2M7OL3MucnsLke4nPA" 

def generate_paathsala_dpp(subject, topic, target_class):
    try:
        # Nayi library ka setup
        client = genai.Client(api_key=MY_API_KEY)
        
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
        
        # Exact wahi Interactions API jo AI Studio ne aapko dikhayi
        interaction = client.interactions.create(
            model="gemini-1.5-flash", # Naya fast model
            input=prompt
        )
        
        # Result ko nikal kar JSON mein convert karna
        raw_text = interaction.output_text
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"⚠️ System Error: {e}")
        return None
