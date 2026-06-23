import json
import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_paathsala_dpp(subject, topic, target_class):
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
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.5,
        )
        
        choices = chat_completion.choices
        
        if isinstance(choices, list) and len(choices) > 0:
            first_choice = choices[0]
            
            if hasattr(first_choice, 'message'):
                raw_text = first_choice.message.content
            else:
                raw_text = first_choice['message']['content']
        else:
            st.error("⚠️ AI ne koi data nahi bheja.")
            return None

        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"⚠️ API Error: {e}")
        return None
