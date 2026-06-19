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

# --- WATERMARK BACKGROUND KA CODE ---
watermark_css = """
<style>
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url("https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png");
    background-size: 50%; /* Logo kitna bada dikhega (50% matlab half screen) */
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    opacity: 0.10; /* OPACITY LEVEL: 0.10 matlab sirf 10% dikhega (ekdum halka) */
    z-index: -1;
}
</style>
"""
st.markdown(watermark_css, unsafe_allow_html=True)
# ------------------------------------

# Upar wala main logo (Agar aapko ye interface ke top par bhi chahiye toh)
st.image("https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png", width=200)

# Yahan 2 Tabs banaye gaye hain
tab1, tab2 = st.tabs(["📝 DPP Generator", "📞 Contact Us"])

# TAB 1: DPP Generator ka pura code
with tab1:
    st.write("Apna Class, Subject aur Chapter chunein aur turant DPP banayein!")
    
    # Google Sheets se data laana (Ultra-Smart Method)
    questions = []
    try:
        # 🔴 YAHAN APNA GOOGLE SHEET KA LINK PASTE KAREIN 🔴
        sheet_url = "https://docs.google.com/spreadsheets/d/1dc5ychco_3BXn_XcY0BGyxAlGDbczSuEel67VHYR-m4/edit?usp=sharing"
        
        # Link ko theek karne ka jaadu (Regex)
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
        st.subheader("1. Paper Details Select Karein")
        
        all_classes = sorted(list(set(q.get('Class', '').strip() for q in questions if q.get('Class'))))
        selected_class = st.selectbox("Select Class:", all_classes)

        all_subjects = sorted(list(set(q.get('Subject', '').strip() for q in questions if q.get('Subject') and q.get('Class', '').strip() == selected_class)))
        selected_subject = st.selectbox("Select Subject:", all_subjects)

        all_chapters = sorted(list(set(q.get('Chapter', '').strip() for q in questions if q.get('Chapter') and q.get('Class', '').strip() == selected_class and q.get('Subject', '').strip() == selected_subject)))
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
                    .title-section h1 {{ font-size: 24pt; margin: 0; text-transform: uppercase; letter-
