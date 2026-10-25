import json
import streamlit as st


# =========================================================
# PAATHSALA AI DPP GENERATOR
# Developed by Amit Kumar Shaw
# =========================================================


def parse_dpp_json(raw_text):
    """Safely parse JSON returned by the AI."""

    if not raw_text or not raw_text.strip():
        return None

    cleaned = raw_text.strip()

    # Remove accidental Markdown fences.
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```", "").strip()

    # Extract the JSON object if extra text is present.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end < start:
        return None

    try:
        return json.loads(cleaned[start:end + 1])
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def validate_dpp(data):
    """Check the basic DPP structure before returning it."""

    if not isinstance(data, dict):
        return False

    section_a = data.get("section_a")
    section_b = data.get("section_b")
    section_c = data.get("section_c")

    if not isinstance(section_a, list):
        return False

    if not isinstance(section_b, list):
        return False

    if not isinstance(section_c, list):
        return False

    if len(section_a) != 10:
        return False

    if len(section_b) != 5:
        return False

    if len(section_c) != 5:
        return False

    return True


@st.cache_data(ttl=86400, show_spinner=False)
def generate_paathsala_dpp(subject, topic, target_class):

    try:
        # Import inside the function so an SDK import error
        # can be handled without breaking other app pages.
        import google.generativeai as genai

        # Read the API key safely.
        api_key = st.secrets.get("GEMINI_API_KEY", "")

        if not api_key:
            st.error(
                "Gemini API key is missing. "
                "Add GEMINI_API_KEY to Streamlit Secrets."
            )
            return None

        prompt = f"""
You are an expert CBSE, JEE, NEET and competitive exam paper setter.

Create a Daily Practice Problem (DPP).

Class: {target_class}
Subject: {subject}
Topic: {topic}

STRICT REQUIREMENTS:

1. Generate exactly 10 Multiple Choice Questions.
2. Generate exactly 5 Short Answer Questions.
3. Generate exactly 5 Long Answer Questions.
4. Questions must be conceptually correct and suitable for the given class.
5. Use ASCII characters only in generated question content.
6. Do not use Unicode mathematical symbols.
7. Write powers as x^2 or y^3.
8. Write fractions as a/b.
9. Write integrals as "Integral of x^2 dx".
10. Write Greek symbols as theta, alpha, beta or pi.
11. MCQs must have four options: a, b, c and d.
12. Each MCQ answer must identify the correct option.
13. Short and long questions must include a concise key_point.
14. Do not repeat questions.
15. Return valid JSON only. Do not include Markdown or explanations.

Use exactly this JSON structure:

{{
  "header": {{
    "class": "{target_class}",
    "subject": "{subject}",
    "topic": "{topic}"
  }},
  "section_a": [
    {{
      "q_no": 1,
      "question": "Question text",
      "options": {{
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D"
      }},
      "answer": "a"
    }}
  ],
  "section_b": [
    {{
      "q_no": 11,
      "question": "Question text",
      "key_point": "Expected answer"
    }}
  ],
  "section_c": [
    {{
      "q_no": 16,
      "question": "Question text",
      "key_point": "Expected answer"
    }}
  ]
}}

The arrays above show example objects only.
Generate exactly 10 objects in section_a,
5 objects in section_b, and 5 objects in section_c.

Return ONLY valid JSON.
"""

        genai.configure(
            api_key=api_key,
            transport="rest"
        )

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash"
        )

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.5,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
        )

        raw_text = getattr(response, "text", None)

        if not raw_text:
            st.error(
                "AI returned an empty response. Please try again."
            )
            return None

        dpp_json = parse_dpp_json(raw_text)

        if dpp_json is None:
            st.error(
                "AI returned invalid JSON. Please generate the DPP again."
            )
            return None

        if not validate_dpp(dpp_json):
            st.error(
                "The generated DPP has an incorrect question count "
                "or JSON structure. Please try again."
            )
            return None

        return dpp_json

    except Exception as e:
        # Handle API, configuration, network and SDK errors.
        st.error(
            "DPP generation failed. Please try again later. "
            f"Error: {str(e)[:300]}"
        )
        return None