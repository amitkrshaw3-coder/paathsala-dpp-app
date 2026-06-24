import google.generativeai as genai
import streamlit as st

# Gemini Configure

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

def ask_paathsala_ai(question):

    try:

        prompt = f"""
        You are PAATHSALA AI.

        Answer student doubts clearly and simply.

        Student Question:
        {question}
        """

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        return f"❌ AI Error: {e}"
