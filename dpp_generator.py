import json
import streamlit as st
import google.generativeai as genai


# ---------------------------------------------------------
# PAATHSALA AI DPP GENERATOR
# Developed by Amit Kumar Shaw
# ---------------------------------------------------------

@st.cache_data(ttl=86400, show_spinner=False)
def generate_paathsala_dpp(subject, topic, target_class):

    prompt = f"""
You are an expert CBSE, JEE, NEET and competitive exam paper setter.

Create a Daily Practice Problem (DPP) for:

Class: {target_class}
Subject: {subject}
Topic: {topic}

IMPORTANT RULES:

1. Generate exactly:
   - 10 Multiple Choice Questions
   - 5 Short Answer Questions
   - 5 Long Answer Questions

2. Questions must be conceptually correct and suitable for Class {target_class}.

3. STRICTLY use ONLY ASCII characters.

4. Never use Unicode mathematical symbols.

5. For powers use:
   x^2, y^3

6. For fractions use:
   a/b

7. For integrals use:
   "Integral of x^2 dx"

8. For Greek symbols write:
   theta, alpha, beta, pi

9. Return ONLY JSON.

JSON FORMAT:

{{
  "header": {{
      "class": "{target_class}",
      "subject": "{subject}",
      "topic": "{topic}"
  }},

  "section_a": [
      {{
          "q_no": 1,
          "question": "",
          "options": {{
              "a": "",
              "b": "",
              "c": "",
              "d": ""
          }},
          "answer": ""
      }}
  ],

  "section_b": [
      {{
          "q_no": 11,
          "question": "",
          "key_point": ""
      }}
  ],

  "section_c": [
      {{
          "q_no": 16,
          "question": "",
          "key_point": ""
      }}
  ]
}}

Do not include markdown.
Do not include explanation.
Return ONLY JSON.
"""

    try:

        # Configure Gemini
        genai.configure(
            api_key=st.secrets["GEMINI_API_KEY"],
            transport="rest"
        )

        # Fast and free-tier friendly model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash"
        )

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json"
            }
        )

        if not response.text:
            st.error("⚠️ Empty response received from Gemini.")
            return None

        raw_text = response.text.strip()

        try:
            dpp_json = json.loads(raw_text)
            return dpp_json

        except json.JSONDecodeError:

            # Backup cleaner
            cleaned = (
                raw_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1

            if start != -1 and end != -1:
                cleaned = cleaned[start:end]

            return json.loads(cleaned)

    except json.JSONDecodeError:
        st.error("⚠️ AI returned invalid JSON.")
        return None

    except Exception as e:
        st.error(f"⚠️ Gemini API Error: {str(e)}")
        return None
