import streamlit as st
import csv
import random
import re
import base64  # NAYA: Photo ko text (code) me badalne ke liye

# Auto-Math-Fixer: ^2 ko power aur _2 ko base banayega
def format_math_symbols(text):
    text = re.sub(r'\^([0-9a-zA-Z]+)', r'<sup>\1</sup>', text)
    text = re.sub(r'_([0-9a-zA-Z]+)', r'<sub>\1</sub>', text)
    return text

# Photo ko Base64 me badalne ka jaadu
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return ""

st.set_page_config(page_title="PAATHSALA DPP Generator", page_icon="📚", layout="centered")

st.title("📚 PAATHSALA DPP Generator")
st.write("Apna Class, Subject aur Chapter chunein aur turant DPP banayein!")

# Database Load Karna
questions = []
try:
    with open('question_bank.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            questions.append(row)
except FileNotFoundError:
    st.error("❌ 'question_bank.csv' file nahi mili! Kripya ise same folder me rakhein.")

if questions:
    st.subheader("1. Paper Details Select Karein")
    
    all_classes = sorted(list(set(q['Class'].strip() for q in questions)))
    selected_class = st.selectbox("Select Class:", all_classes)

    all_subjects = sorted(list(set(q['Subject'].strip() for q in questions if q['Class'].strip() == selected_class)))
    selected_subject = st.selectbox("Select Subject:", all_subjects)

    all_chapters = sorted(list(set(q['Chapter'].strip() for q in questions if q['Class'].strip() == selected_class and q['Subject'].strip() == selected_subject)))
    selected_chapter = st.selectbox("Select Chapter:", all_chapters)

    st.subheader("2. Questions ki Sankhya (Number) Batayein")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        n_mcq = st.number_input("No. of MCQs:", min_value=0, value=10)
    with col2:
        n_short = st.number_input("No. of Short Qs:", min_value=0, value=5)
    with col3:
        n_long = st.number_input("No. of Long Qs:", min_value=0, value=2)

    st.markdown("---")
    if st.button("🚀 Generate My DPP", type="primary", use_container_width=True):
        
        chapter_pool = [q for q in questions if q['Class'].strip().lower() == selected_class.lower() and q['Subject'].strip().lower() == selected_subject.lower() and q['Chapter'].strip().lower() == selected_chapter.lower()]
        
        mcq_pool = [q for q in chapter_pool if q['Type'].strip().upper() == 'MCQ']
        short_pool = [q for q in chapter_pool if q['Type'].strip().upper() == 'SHORT ANSWER']
        long_pool = [q for q in chapter_pool if q['Type'].strip().upper() == 'LONG ANSWER']
        
        selected_mcqs = random.sample(mcq_pool, min(n_mcq, len(mcq_pool)))
        selected_shorts = random.sample(short_pool, min(n_short, len(short_pool)))
        selected_longs = random.sample(long_pool, min(n_long, len(long_pool)))
        
        mcq_html = ""
        ans_html_mcq = ""
        q_num = 1
        
        for q in selected_mcqs:
            formatted_q = format_math_symbols(q['Question'])
            formatted_ans = format_math_symbols(q['Answer'])
            if " a) " in formatted_q:
                formatted_q = formatted_q.replace(" a) ", "<div class='opt-row'><span class='opt-box'>a) ")
                formatted_q = formatted_q.replace(" b) ", "</span><span class='opt-box'>b) ")
                formatted_q = formatted_q.replace(" c) ", "</span></div><div class='opt-row'><span class='opt-box'>c) ")
                formatted_q = formatted_q.replace(" d) ", "</span><span class='opt-box'>d) ")
                formatted_q += "</span></div>"
            mcq_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{formatted_q}</div></div>\n'
            ans_html_mcq += f'<tr><td style="text-align: center;">{q_num}</td><td>{formatted_ans}</td></tr>\n'
            q_num += 1

        short_html = ""
        ans_html_short_long = ""
        for q in selected_shorts:
            formatted_q = format_math_symbols(q['Question'])
            formatted_ans = format_math_symbols(q['Answer'])
            short_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{formatted_q}</div></div>\n'
            ans_html_short_long += f'<tr><td style="text-align: center;">{q_num}</td><td>{formatted_ans}</td></tr>\n'
            q_num += 1

        long_html = ""
        for q in selected_longs:
            formatted_q = format_math_symbols(q['Question'])
            formatted_ans = format_math_symbols(q['Answer'])
            long_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{formatted_q}</div></div>\n'
            ans_html_short_long += f'<tr><td style="text-align: center;">{q_num}</td><td>{formatted_ans}</td></tr>\n'
            q_num += 1

        # Logo ko encode karke HTML ke liye taiyaar karna
        logo_base64 = get_image_base64("1000086036.png")
        logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="PAATHSALA Logo">' if logo_base64 else '<h2>PAATHSALA</h2>'

        # Pura HTML Template
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>PAATHSALA DPP - {selected_chapter}</title>
            <style>
                @page {{ size: A4; margin: 15mm 20mm; }}
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #111; }}
                .header-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
                .student-info {{ width: 50%; font-size: 11pt; vertical-align: top; }}
                .logo-cell {{ width: 50%; text-align: right; vertical-align: top; }}
                .logo-img {{ max-width: 200px; max-height: 120px; }}
                .title-section {{ text-align: center; margin: 20px 0 10px 0; }}
                .title-section h1 {{ font-size: 24pt; margin: 0; text-transform: uppercase; letter-spacing: 2px; }}
                .section-title {{ font-size: 12pt; font-weight: bold; background-color: #f4f4f4; padding: 6px 12px; border-left: 5px solid #fce803; margin: 15px 0 10px 0; }}
                .question {{ margin-bottom: 15px; font-size: 11pt; display: table; width: 100%; }}
                .q-num {{ display: table-cell; width: 30px; font-weight: bold; vertical-align: top; }}
                .q-text {{ display: table-cell; vertical-align: top; }}
                .opt-row {{ margin-top: 4px; display: block; }}
                .opt-box {{ display: inline-block; width: 48%; vertical-align: top; }}
                .answer-key-page {{ page-break-before: always; padding-top: 20px; }}
                .ans-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                .ans-table th, .ans-table td {{ border: 1px solid #ccc; padding: 8px; font-size: 10.5pt; text-align: left; }}
                .ans-table th {{ background-color: #fce803; font-weight: bold; text-align: center; }}
            </style>
        </head>
        <body>
            <table class="header-table">
                <tr>
                    <td class="student-info">
                        <div><strong>Name:</strong> ___________________________</div>
                        <div><strong>Date:</strong> ___________________________</div>
                        <div><strong>Class:</strong> {selected_class}</div>
                        <div><strong>Subject:</strong> {selected_subject}</div>
                    </td>
                    <td class="logo-cell">
                        {logo_img_tag}
                    </td>
                </tr>
            </table>

            <div class="title-section">
                <h1>{selected_chapter}</h1>
                <p><strong>Daily Practice Problem (DPP)</strong></p>
            </div>

            <div class="section-title">Section A: Multiple Choice Questions</div>
            {mcq_html}

            <div class="section-title">Section B: Short Answer Type Questions</div>
            {short_html}

            <div class="section-title">Section C: Long Answer Type Questions</div>
            {long_html}

            <div class="answer-key-page">
                <div class="title-section"><h2>ANSWER KEY</h2></div>
                <div class="section-title">Section A (MCQs)</div>
                <table class="ans-table">
                    <tr><th width="15%">Q.No.</th><th width="85%">Answer</th></tr>
                    {ans_html_mcq}
                </table>
                <div class="section-title">Section B & C (Subjective)</div>
                <table class="ans-table">
                    <tr><th width="15%">Q.No.</th><th width="85%">Key Points / Answers</th></tr>
                    {ans_html_short_long}
                </table>
            </div>
        </body>
        </html>
        """
        
        st.success(f"🎉 Yay! Aapka '{selected_chapter}' ka DPP ban gaya hai!")
        
        file_name = f"DPP_{selected_class.replace(' ', '')}_{selected_chapter.replace(' ', '')}.html"
        st.download_button(
            label="📥 Click Here to Download Your DPP",
            data=html_template,
            file_name=file_name,
            mime="text/html"
        )
