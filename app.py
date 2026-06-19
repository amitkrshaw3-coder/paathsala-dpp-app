import streamlit as st
import csv
import random
import re
import urllib.request
import io

# Auto-Math-Fixer
def format_math_symbols(text):
    if not text: return ""
    text = re.sub(r'\^([0-9a-zA-Z]+)', r'<sup>\1</sup>', text)
    text = re.sub(r'_([0-9a-zA-Z]+)', r'<sub>\1</sub>', text)
    return text

st.set_page_config(page_title="PAATHSALA", page_icon="📚", layout="centered")

# --- 1. FULL BACKGROUND WATERMARK CODE (Opacity kam karke 0.05 kar di) ---
watermark_html = """
<div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; opacity: 0.05; pointer-events: none; background-image: url('https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png'); background-size: 250px; background-repeat: repeat;"></div>
"""
st.markdown(watermark_html, unsafe_allow_html=True)

# --- 2. ULTRA-PREMIUM UI CSS ---
custom_ui_css = """
<style>
/* Default Streamlit header hide karna */
header {visibility: hidden !important;}
[data-testid="stHeader"] {background-color: transparent !important;}

/* Deep Blue Top Patti */
.custom-top-bar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 60px; 
    background-color: #0b2265; 
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 99999;
    display: flex;
    justify-content: center;
}

/* Premium Rounded Logo */
.custom-logo {
    height: 90px; 
    background-color: white; 
    padding: 8px 20px; 
    border-bottom-left-radius: 25px; 
    border-bottom-right-radius: 25px; 
    box-shadow: 0px 5px 15px rgba(0,0,0,0.3); 
    margin-top: 0px; 
}

/* 🚀 NAYA: GLASSMORPHISM FLOATING PILL FOOTER 🚀 */
.custom-bottom-pill {
    position: fixed;
    bottom: 20px; /* Niche se thoda upar float karega */
    left: 50%;
    transform: translateX(-50%);
    background: rgba(11, 34, 101, 0.85); /* Transparent Dark Blue */
    backdrop-filter: blur(10px); /* Frosted Glass Effect */
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 8px 24px;
    border-radius: 50px; /* Pill Shape */
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2);
    z-index: 99999;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: popUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
}

.footer-text {
    color: #e2e8f0;
    font-size: 13px;
    letter-spacing: 0.5px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    display: flex;
    align-items: center;
    gap: 6px;
}

.footer-name {
    color: #ffffff;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* Pop Up Animation */
@keyframes popUp {
    0% { bottom: -20px; opacity: 0; transform: translateX(-50%) scale(0.9); }
    100% { bottom: 20px; opacity: 1; transform: translateX(-50%) scale(1); }
}

/* App ke main content ki spacing */
.main .block-container {
    padding-top: 110px !important;
    padding-bottom: 90px !important; 
}

/* FLOATING WHITE CARDS CSS */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border-radius: 16px !important;
    box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.05) !important;
    border: 1px solid #f1f5f9 !important;
    padding: 25px !important;
    margin-bottom: 25px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] p, 
div[data-testid="stVerticalBlockBorderWrapper"] label,
div[data-testid="stVerticalBlockBorderWrapper"] span {
    color: #0b2265 !important;
    font-weight: 600 !important;
}
</style>

<!-- Upar wala Logo HTML -->
<div class="custom-top-bar">
    <img class="custom-logo" src="https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png">
</div>

<!-- Niche wala Premium Glass Pill HTML -->
<div class="custom-bottom-pill">
    <div class="footer-text">
        Developed by <span class="footer-name">Amit Kumar Shaw</span>
    </div>
</div>
"""
st.markdown(custom_ui_css, unsafe_allow_html=True)
# -----------------------------------------------------------------

# Yahan 2 Tabs banaye gaye hain
tab1, tab2 = st.tabs(["📝 DPP Generator", "📞 Contact Us"])

# TAB 1: DPP Generator ka pura code
with tab1:
    st.write("Apna Class, Subject aur Chapter chunein aur turant DPP banayein!")
    
    # Google Sheets se data laana
    questions = []
    try:
        # 🔴 YAHAN APNA GOOGLE SHEET KA LINK PASTE KAREIN 🔴
        sheet_url = "https://docs.google.com/spreadsheets/d/1dc5ychco_3BXn_XcY0BGyxAlGDbczSuEel67VHYR-m4/edit?usp=sharing"
        
        # Link ko theek karne ka jaadu
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', str(sheet_url))
        if match:
            sheet_id = match.group(1)
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        else:
            csv_url = str(sheet_url)

        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        csv_data = response.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(csv_data))
        for row in reader:
            questions.append(row)
    except Exception as e:
        st.error(f"❌ Google Sheet se data laane mein error aaya! Details: {e}")

    if questions:
        
        # 📦 STEP 1 FLOATING CARD
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px;">
                <div style="background: linear-gradient(135deg, #0b2265, #2563eb); color: white; border-radius: 50%; width: 34px; height: 34px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 18px; margin-right: 12px; box-shadow: 0 4px 6px rgba(11, 34, 101, 0.2);">1</div>
                <div style="font-size: 20px; font-weight: 600; color: #0b2265; letter-spacing: 0.5px;">Paper Details Select Karein</div>
            </div>
            """, unsafe_allow_html=True)
            
            all_classes = sorted(list(set(q.get('Class', '').strip() for q in questions if q.get('Class'))))
            selected_class = st.selectbox("Select Class:", all_classes)

            all_subjects = sorted(list(set(q.get('Subject', '').strip() for q in questions if q.get('Subject') and q.get('Class', '').strip() == selected_class)))
            selected_subject = st.selectbox("Select Subject:", all_subjects)

            all_chapters = sorted(list(set(q.get('Chapter', '').strip() for q in questions if q.get('Chapter') and q.get('Class', '').strip() == selected_class and q.get('Subject', '').strip() == selected_subject)))
            selected_chapter = st.selectbox("Select Chapter:", all_chapters)

        # 📦 STEP 2 FLOATING CARD
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px;">
                <div style="background: linear-gradient(135deg, #0b2265, #2563eb); color: white; border-radius: 50%; width: 34px; height: 34px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 18px; margin-right: 12px; box-shadow: 0 4px 6px rgba(11, 34, 101, 0.2);">2</div>
                <div style="font-size: 20px; font-weight: 600; color: #0b2265; letter-spacing: 0.5px;">Questions ki Sankhya (Number) Batayein</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                n_mcq = st.number_input("No. of MCQs:", min_value=0, value=10)
            with col2:
                n_short = st.number_input("No. of Short Qs:", min_value=0, value=5)
            with col3:
                n_long = st.number_input("No. of Long Qs:", min_value=0, value=2)

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Generate My DPP", type="primary", use_container_width=True):
            
            chapter_pool = [q for q in questions if q.get('Class') and q.get('Subject') and q.get('Chapter') and q['Class'].strip().lower() == selected_class.lower() and q['Subject'].strip().lower() == selected_subject.lower() and q['Chapter'].strip().lower() == selected_chapter.lower()]
            
            mcq_pool = [q for q in chapter_pool if q.get('Type') and q['Type'].strip().upper() == 'MCQ']
            short_pool = [q for q in chapter_pool if q.get('Type') and q['Type'].strip().upper() == 'SHORT ANSWER']
            long_pool = [q for q in chapter_pool if q.get('Type') and q['Type'].strip().upper() == 'LONG ANSWER']
            
            selected_mcqs = random.sample(mcq_pool, min(n_mcq, len(mcq_pool)))
            selected_shorts = random.sample(short_pool, min(n_short, len(short_pool)))
            selected_longs = random.sample(long_pool, min(n_long, len(long_pool)))
            
            mcq_html = ""
            ans_html_mcq = ""
            q_num = 1
            
            for q in selected_mcqs:
                formatted_q = format_math_symbols(q.get('Question', ''))
                formatted_ans = format_math_symbols(q.get('Answer', ''))
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
                formatted_q = format_math_symbols(q.get('Question', ''))
                formatted_ans = format_math_symbols(q.get('Answer', ''))
                short_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{formatted_q}</div></div>\n'
                ans_html_short_long += f'<tr><td style="text-align: center;">{q_num}</td><td>{formatted_ans}</td></tr>\n'
                q_num += 1

            long_html = ""
            for q in selected_longs:
                formatted_q = format_math_symbols(q.get('Question', ''))
                formatted_ans = format_math_symbols(q.get('Answer', ''))
                long_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{formatted_q}</div></div>\n'
                ans_html_short_long += f'<tr><td style="text-align: center;">{q_num}</td><td>{formatted_ans}</td></tr>\n'
                q_num += 1

            logo_img_tag = '<img src="https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png" style="width: 150px; max-height: 80px;">' 

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

# TAB 2: Contact Us ka code
with tab2:
    st.header("📞 Contact Us")
    st.write("Agar aapko humari services pasand aayi ya aap humse judna chahte hain, toh niche di gayi details par sampark karein:")
    
    st.markdown("---")
    st.markdown("### 👤 **Name:** Amit Kumar Shaw")
    st.markdown("### 📞 **Phone:** [+91 8116230505](tel:+918116230505)")
    st.markdown("### 📧 **Email:** [amit.kr.shaw.3@gmail.com](mailto:amit.kr.shaw.3@gmail.com)")
    st.markdown("### 📍 **Location:** Raniganj, West Bengal, India")
    st.markdown("---")
    
    st.info("💡 **Tip:** Aap upar diye gaye Phone number ya Email par direct click karke bhi call ya mail kar sakte hain!")
