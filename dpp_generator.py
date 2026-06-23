import json
import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_paathsala_dpp(subject, topic, target_class):
    prompt = f"""
    You are an expert exam paper setter. Create a Daily Practice Problem (DPP) for Class {target_class} on the Subject '{subject}' and Topic '{topic}'.
    
    CRITICAL MATH FORMATTING RULES:
    1. You MUST use LaTeX for ALL mathematical symbols, powers, fractions, and integrals.
    2. Enclose all math expressions in single dollar signs (e.g., $x^2$, $\\int x dx$).
    3. Since this is a JSON output, you must double-escape the backslashes for LaTeX commands so the JSON doesn't break (e.g., use \\\\int instead of \\int).
    
    You MUST output strictly in the following JSON format. Do not add any extra text:
    {{
      "header": {{"class": "{target_class}", "subject": "{subject}", "topic": "{topic}"}},
      "section_a": [{{"q_no": 1, "question": "Evaluate $\\\\int x^2 dx$", "options": {{"a": "$x^3/3$", "b": "2", "c": "3", "d": "4"}}, "answer": "a"}}],
      "section_b": [{{"q_no": 11, "question": "Short answer", "key_point": "Brief answer"}}],
      "section_c": [{{"q_no": 16, "question": "Long answer", "key_point": "Detailed steps"}}]
    }}
    """
    
    try:
        # Groq API ko call karna
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            temperature=0.5,
        )
        
        # Standard tarike se text nikalna (List error fix)
        raw_text = chat_completion.choices.message.content
        
        # Smart Scanner: Jo sirf JSON wale hisse ko bahar nikalega
        clean_text = raw_text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json").split("```").strip()
        elif "```" in clean_text:
            clean_text = clean_text.split("```").split("```").strip()

        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"⚠️ API Error: {e}")
        return None
