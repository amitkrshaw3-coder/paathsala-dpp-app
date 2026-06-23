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
    3. Since this is a JSON output, you must double-escape the backslashes for LaTeX commands so the
