import json
import urllib.request
import streamlit as st

def generate_paathsala_dpp(subject, topic, target_class):
    prompt = f"""
    You are an expert exam paper setter. Create a Daily Practice Problem (DPP) for Class {target_class} on the Subject '{subject}' and Topic '{topic}'.
    
    CRITICAL MATH FORMATTING RULES:
    1. You MUST use LaTeX for ALL mathematical symbols, powers, fractions, and integrals.
    2. Enclose all math expressions in single dollar signs (e.g., $x^2$, $\\int x dx$).
    3. You must double-escape the backslashes for LaTeX commands so the JSON doesn't break (e.g., use \\\\int instead of \\int).
    
    Output ONLY valid JSON.
    {{
      "header": {{"class": "{target_class}", "subject": "{subject}", "topic": "{topic}"}},
      "section_a": [{{"q_no": 1, "question": "Evaluate $\\\\int x^2 dx$", "options": {{"a": "$x^3/3$", "b": "2", "c": "3", "d": "4"}}, "answer": "a"}}],
      "section_b": [{{"q_no": 11, "question": "Short answer", "key_point": "Brief answer"}}],
      "section_c": [{{"q_no": 16, "question": "Long answer", "key_point": "Detailed steps"}}]
    }}
    """
    
    # Direct API Endpoint (No Groq Package needed)
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Request setup
    data = json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "response_format": {"type": "json_object"}
    }).encode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        # Seedha server se connect karna
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            # Dictionary se extract karna (Yeh kabhi fail nahi hoga)
            raw_text = result["choices"]["message"]["content"]
            
            # JSON load karke wapas bhejna
            return json.loads(raw_text)
            
    except Exception as e:
        st.error(f"⚠️ Direct Connection Error: {e}")
        return None
