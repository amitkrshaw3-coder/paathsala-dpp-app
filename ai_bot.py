import streamlit as st
import google.generativeai as genai

def ask_paathsala_ai(question):

    try:
        genai.configure(
            api_key=st.secrets["GEMINI_API_KEY"],
            transport="rest"
        )

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are PAATHSALA AI Tutor.

        Explain the student's doubt in simple language.

        Student question:
        {question}

        Give step-by-step explanation.
        """

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"⚠️ AI Error: {e}"
