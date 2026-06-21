import streamlit as st
import csv
import random
import re
import urllib.request
import urllib.parse
import io
import streamlit.components.v1 as components 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Yeh Brahmastra CSS har tarah ke Streamlit branding ko block karega
hide_all_streamlit_branding = """
<style>
/* 1. Normal Footer hide karne ke liye */
footer {visibility: hidden !important;}

/* 2. Top Header aur Menu hide karne ke liye */
header {visibility: hidden !important;}
#MainMenu {visibility: hidden !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

/* 3. Floating "Hosted with Streamlit" badge hide karne ke liye (LINK BLOCKER) */
a[href*="streamlit.io"] {display: none !important;}
a[href*="streamlit.app"] {display: none !important;}

/* 4. Kisi bhi 'viewerBadge' class ko force hide karne ke liye */
div[class*="viewerBadge"] {display: none !important;}
</style>
"""
st.markdown(hide_all_streamlit_branding, unsafe_allow_html=True)
st.page_link("pages/chat.py", label="💬 Live Chat Room", icon="💬")

# =========================================================================
# 🛑 APNE LINKS YAHAN DAALEIN 🛑
# =========================================================================

if 'dynamic_sheet_url' not in st.session_state: 
    st.session_state.dynamic_sheet_url = "https://docs.google.com/spreadsheets/d/1dc5ychco_3BXn_XcY0BGyxAlGDbczSuEel67VHYR-m4/edit?usp=sharing"

if 'users_sheet_url' not in st.session_state: 
    st.session_state.users_sheet_url = "https://docs.google.com/spreadsheets/d/1mlHR5Bq0RcOqTAOaePSiLiakSasKeF9JgOrL_7nmUFI/edit?usp=sharing"

if 'apps_script_url' not in st.session_state: 
    st.session_state.apps_script_url = "https://script.google.com/macros/s/AKfycbwToIrpZtr924Drx55s432gaQwrfMxwZ8auzsyVnusLxVgkyT7t8MUFtkjfWoj0Xt1T/exec"

# =========================================================================

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'otp_sent' not in st.session_state: st.session_state.otp_sent = False
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = None
if 'user_identifier' not in st.session_state: st.session_state.user_identifier = ""
if 'live_allowed_users' not in st.session_state: st.session_state.live_allowed_users = []

def get_live_users(sheet_url):
    try:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', str(sheet_url))
        if match:
            csv_url = f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv"
            req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            data = response.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(data))
            return [row['Email'].strip().lower() for row in reader if row.get('Email')]
        return []
    except:
        return []

def format_math_symbols(text):
    if not text: return ""
    if '$' in text: return text  
    text = re.sub(r'\^([0-9a-zA-Z]+)', r'<sup>\1</sup>', text)
    text = re.sub(r'_([0-9a-zA-Z]+)', r'<sub>\1</sub>', text)
    return text

def send_real_otp_email(receiver_email, otp_code):
    try:
        sender_email = st.secrets["SENDER_EMAIL"]
        app_password = st.secrets["APP_PASSWORD"]
        
        msg = MIMEMultipart()
        msg['From'] = f"PAATHSALA <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = "🔒 PAATHSALA - Your Login OTP"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 500px; margin: auto; border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px;">
                    <h2 style="color: #0b2265; text-align: center;">Welcome to PAATHSALA</h2>
                    <p>Hello,</p>
                    <p>Your One-Time Password (OTP) to securely login to your account is:</p>
                    <h1 style="text-align: center; color: #2563eb; letter-spacing: 5px; font-size: 36px; background: #f4f7f6; padding: 10px; border-radius: 8px;">{otp_code}</h1>
                    <p style="color: #888; font-size: 12px; text-align: center;">Please do not share this code with anyone.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"⚠️ Email server error: Secrets check karein. Error: {e}")
        return False

st.set_page_config(page_title="PAATHSALA", page_icon="📚", layout="centered")

custom_ui_css = """
<style>
header {visibility: hidden !important;} [data-testid="stHeader"] {background-color: transparent !important;}
[data-testid="stAppViewContainer"]::after { content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-image: url('https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png'); background-size: 250px; background-repeat: repeat; opacity: 0.05; pointer-events: none; z-index: -1 !important; }
.custom-top-bar { position: fixed; top: 0; left: 0; width: 100vw; height: 60px; background-color: #0b2265; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2); z-index: 99999; display: flex; justify-content: center; }
.custom-logo { height: 90px; background-color: white; padding: 8px 20px; border-bottom-left-radius: 25px; border-bottom-right-radius: 25px; box-shadow: 0px 5px 15px rgba(0,0,0,0.3); margin-top: 0px; }
.custom-bottom-pill { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(11, 34, 101, 0.95) !important; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.15); padding: 8px 24px; border-radius: 50px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3); z-index: 99999; display: flex; justify-content: center; align-items: center; }
.footer-text { color: #e2e8f0 !important; font-size: 13px !important; font-family: sans-serif; display: flex; align-items: center; gap: 6px; margin: 0 !important; }
.footer-name { color: #ffffff !important; font-weight: 700 !important; }
.main .block-container { padding-top: 110px !important; padding-bottom: 90px !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #ffffff !important; border-radius: 16px !important; box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.05) !important; border: 1px solid #f1f5f9 !important; padding: 25px !important; margin-bottom: 25px !important; position: relative; z-index: 10; }
div[data-testid="stVerticalBlockBorderWrapper"] p, div[data-testid="stVerticalBlockBorderWrapper"] label, div[data-testid="stVerticalBlockBorderWrapper"] span { color: #0b2265 !important; font-weight: 600 !important; }
</style>
<div class="custom-top-bar"><img class="custom-logo" src="https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png"></div>
<div class="custom-bottom-pill"><div class="footer-text">Developed by <span class="footer-name">Amit Kumar Shaw</span></div></div>
"""
st.markdown(custom_ui_css, unsafe_allow_html=True)

st.session_state.live_allowed_users = get_live_users(st.session_state.users_sheet_url)
admin_email = st.secrets.get("ADMIN_EMAIL", "admin@gmail.com").strip().lower()

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<h2 style='text-align:center; color:#0b2265;'>🔒 Registered User Login</h2>", unsafe_allow_html=True)
        if not st.session_state.otp_sent:
            with st.form("email_form"):
                user_input = st.text_input("Enter Registered Email ID:", placeholder="student@gmail.com", key="login_email_widget")
                submit_email = st.form_submit_button("🚀 Request Login OTP")
                if submit_email:
                    cleaned_email = user_input.strip().lower()
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", cleaned_email):
                        st.warning("⚠️ Kripya sahi Email daalein!")
                    elif cleaned_email not in st.session_state.live_allowed_users and cleaned_email != admin_email:
                        st.error("❌ Aap is app par registered nahi hain! Kripya access paane ke liye Admin se sampark karein.")
                    else:
                        with st.spinner("📧 Security OTP bheja ja raha hai..."):
                            st.session_state.generated_otp = str(random.randint(1000, 9999))
                            if send_real_otp_email(cleaned_email, st.session_state.generated_otp):
                                st.session_state.user_identifier = cleaned_email
                                st.session_state.otp_sent = True
                                st.rerun()
        else:
            st.info(f"📩 OTP sent successfully to **{st.session_state.user_identifier}**")
            with st.form("otp_form"):
                entered_otp = st.text_input("Enter 4-Digit OTP:", max_chars=4, key="login_otp_widget")
                col1, col2 = st.columns(2)
                with col1: verify_btn = st.form_submit_button("✅ Verify & Login")
                with col2: resend_btn = st.form_submit_button("🔄 Cancel / Change Email")
                if verify_btn:
                    if entered_otp == st.session_state.generated_otp:
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("❌ Galat OTP!")
                if resend_btn:
                    st.session_state.otp_sent = False
                    st.session_state.generated_otp = None
                    st.rerun()
else:
    is_admin = (st.session_state.user_identifier == admin_email)
    role_icon = "👑 Admin Dashboard" if is_admin else "🎓 Student Portal"
    
    st.markdown(f"""
    <div style="background-color: #f8fafc; padding: 10px 20px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 5px solid #2563eb; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{role_icon}</div>
            <div style="font-size: 16px; color: #0b2265; font-weight: 800;">👤 {st.session_state.user_identifier}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔒 Secure Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.session_state.generated_otp = None
        st.session_state.user_identifier = "" 
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)

    if is_admin:
        tab1, tab2, tab3 = st.tabs(["📝 DPP Generator", "📞 Contact Us", "👑 Admin Panel"])
    else:
        tab1, tab2 = st.tabs(["📝 DPP Generator", "📞 Contact Us"])

    with tab1:
        st.write("Apna Class, Subject aur Chapter chunein aur turant DPP banayein!")
        questions = []
        try:
            sheet_url = st.session_state.dynamic_sheet_url
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', str(sheet_url))
            if match:
                csv_url = f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv"
                req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = urllib.request.urlopen(req)
                csv_data = response.read().decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(csv_data))
                for row in reader: questions.append(row)
        except: pass 

        if questions:
            with st.container(border=True):
                all_classes = sorted(list(set(q.get('Class', '').strip() for q in questions if q.get('Class'))))
                selected_class = st.selectbox("Select Class:", all_classes)
                all_subjects = sorted(list(set(q.get('Subject', '').strip() for q in questions if q.get('Subject') and q.get('Class', '').strip() == selected_class)))
                selected_subject = st.selectbox("Select Subject:", all_subjects)
                all_chapters = sorted(list(set(q.get('Chapter', '').strip() for q in questions if q.get('Chapter') and q.get('Class', '').strip() == selected_class and q.get('Subject', '').strip() == selected_subject)))
                selected_chapter = st.selectbox("Select Chapter:", all_chapters)

            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                with col1: n_mcq = st.number_input("No. of MCQs:", min_value=0, value=10)
                with col2: n_short = st.number_input("No. of Short Qs:", min_value=0, value=5)
                with col3: n_long = st.number_input("No. of Long Qs:", min_value=0, value=2)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Generate Print-Ready PDF", type="primary", use_container_width=True):
                with st.spinner("Apka shandar DPP ready ho raha hai..."):
                    chapter_pool = [q for q in questions if q.get('Class') and q.get('Subject') and q.get('Chapter') and q['Class'].strip().lower() == selected_class.lower() and q['Subject'].strip().lower() == selected_subject.lower() and q['Chapter'].strip().lower() == selected_chapter.lower()]
                    mcq_pool = [q for q in chapter_pool if q.get('Type') and q['Type'].strip().upper() == 'MCQ']
                    short_pool = [q for q in chapter_pool if q.get('Type') and q['Type'].strip().upper() == 'SHORT ANSWER']
                    long_pool = [q for q in chapter_pool if q.get('Type') and q['Type'].strip().upper() == 'LONG ANSWER']
                    
                    selected_mcqs = random.sample(mcq_pool, min(n_mcq, len(mcq_pool)))
                    selected_shorts = random.sample(short_pool, min(n_short, len(short_pool)))
                    selected_longs = random.sample(long_pool, min(n_long, len(long_pool)))
                    
                    mcq_html, ans_html_mcq, q_num = "", "", 1
                    for q in selected_mcqs:
                        formatted_q = format_math_symbols(q.get('Question', ''))
                        formatted_ans = format_math_symbols(q.get('Answer', ''))
                        if " a) " in formatted_q:
                            formatted_q = formatted_q.replace(" a) ", "<div class='opt-row'><span class='opt-box'>a) ").replace(" b) ", "</span><span class='opt-box'>b) ").replace(" c) ", "</span></div><div class='opt-row'><span class='opt-box'>c) ").replace(" d) ", "</span><span class='opt-box'>d) ") + "</span></div>"
                        mcq_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{formatted_q}</div></div>\n'
                        ans_html_mcq += f'<tr><td style="text-align: center;">{q_num}</td><td>{formatted_ans}</td></tr>\n'
                        q_num += 1

                    short_html, ans_html_short_long = "", ""
                    for q in selected_shorts:
                        short_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{format_math_symbols(q.get("Question", ""))}</div></div>\n'
                        ans_html_short_long += f'<tr><td style="text-align: center;">{q_num}</td><td>{format_math_symbols(q.get("Answer", ""))}</td></tr>\n'
                        q_num += 1

                    long_html = ""
                    for q in selected_longs:
                        long_html += f'<div class="question"><div class="q-num">{q_num}.</div><div class="q-text">{format_math_symbols(q.get("Question", ""))}</div></div>\n'
                        ans_html_short_long += f'<tr><td style="text-align: center;">{q_num}</td><td>{format_math_symbols(q.get("Answer", ""))}</td></tr>\n'
                        q_num += 1

                    logo_img_tag = '<img src="https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png" style="width: 150px; max-height: 80px;">' 
                    clean_filename = f"DPP_{selected_class.replace(' ', '')}_{selected_chapter.replace(' ', '')}.pdf"

                    html_template = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
                        <script>window.MathJax = {{ tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }}, svg: {{ fontCache: 'global' }} }};</script>
                        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #111; padding: 10px; }}
                            #pdf-content {{ position: relative; padding: 20px; background-color: white; z-index: 1; }}
                            #pdf-content::before {{ content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('https://raw.githubusercontent.com/amitkrshaw3-coder/paathsala-dpp-app/main/1000086036.png'); background-size: 350px; background-repeat: repeat; opacity: 0.08; z-index: -1; pointer-events: none; }}
                            .header-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
                            .student-info {{ width: 50%; font-size: 11pt; vertical-align: top; }}
                            .logo-cell {{ width: 50%; text-align: right; vertical-align: top; }}
                            .title-section {{ text-align: center; margin: 20px 0 10px 0; }}
                            .title-section h1 {{ font-size: 24pt; margin: 0; text-transform: uppercase; letter-spacing: 2px; color: #0b2265; }}
                            .section-title {{ font-size: 12pt; font-weight: bold; background-color: #f4f4f4; padding: 6px 12px; border-left: 5px solid #fce803; margin: 15px 0 10px 0; border-radius: 4px; }}
                            .question {{ margin-bottom: 15px; font-size: 11pt; display: table; width: 100%; }}
                            .q-num {{ display: table-cell; width: 30px; font-weight: bold; vertical-align: top; }}
                            .q-text {{ display: table-cell; vertical-align: top; }}
                            .opt-row {{ margin-top: 4px; display: block; }}
                            .opt-box {{ display: inline-block; width: 48%; vertical-align: top; }}
                            .ans-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                            .ans-table th, .ans-table td {{ border: 1px solid #ccc; padding: 8px; font-size: 10.5pt; text-align: left; }}
                            .ans-table th {{ background-color: #fce803; font-weight: bold; text-align: center; }}
                            .download-btn-container {{ text-align: center; margin-bottom: 30px; margin-top: 10px; }}
                            .download-btn {{ background: linear-gradient(135deg, #0b2265, #2563eb); color: white; padding: 14px 28px; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 8px 15px rgba(37, 99, 235, 0.3); transition: transform 0.2s; }}
                            .download-btn:hover {{ transform: translateY(-2px); }}
                        </style>
                    </head>
                    <body>
                        <div class="download-btn-container"><button class="download-btn" onclick="downloadPDF()">📥 Click Here to Save as Perfect PDF</button></div>
                        <div id="pdf-content">
                            <table class="header-table">
                                <tr>
                                    <td class="student-info">
                                        <div><strong>Name:</strong> ___________________________</div>
                                        <div><strong>Date:</strong> ___________________________</div>
                                        <div><strong>Class:</strong> {selected_class}</div>
                                        <div><strong>Subject:</strong> {selected_subject}</div>
                                    </td>
                                    <td class="logo-cell">{logo_img_tag}</td>
                                </tr>
                            </table>
                            <div class="title-section"><h1>{selected_chapter}</h1><p><strong>Daily Practice Problem (DPP)</strong></p></div>
                            <div class="section-title">Section A: Multiple Choice Questions</div>{mcq_html}
                            <div class="section-title">Section B: Short Answer Type Questions</div>{short_html}
                            <div class="section-title">Section C: Long Answer Type Questions</div>{long_html}
                            <div style="page-break-before: always; padding-top: 20px;">
                                <div class="title-section"><h2>ANSWER KEY</h2></div>
                                <div class="section-title">Section A (MCQs)</div><table class="ans-table"><tr><th width="15%">Q.No.</th><th width="85%">Answer</th></tr>{ans_html_mcq}</table>
                                <div class="section-title">Section B & C (Subjective)</div><table class="ans-table"><tr><th width="15%">Q.No.</th><th width="85%">Key Points / Answers</th></tr>{ans_html_short_long}</table>
                            </div>
                        </div>
                        <script>
                            function downloadPDF() {{
                                MathJax.typesetPromise().then(() => {{
                                    const element = document.getElementById('pdf-content');
                                    document.querySelector('.download-btn-container').style.display = 'none';
                                    var opt = {{ margin: 10, filename: '{clean_filename}', image: {{ type: 'jpeg', quality: 1.0 }}, html2canvas: {{ scale: 2, useCORS: true }}, jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }} }};
                                    html2pdf().set(opt).from(element).save().then(function() {{ document.querySelector('.download-btn-container').style.display = 'block'; }});
                                }});
                            }}
                        </script>
                    </body>
                    </html>
                    """
                    components.html(html_template, height=800, scrolling=True)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; margin-bottom: 25px;">
                <h2 style="color: #0b2265; margin: 0; font-size: 26px; font-weight: 800;">Amit Kumar Shaw</h2>
                <p style="color: #64748b; margin: 5px 0 0 0; font-size: 15px; font-weight: 500;">Developer & Creator</p>
            </div>
            <hr>
            <p style="text-align: center;"><strong>📞 Phone / WhatsApp:</strong> +91 8116230505</p>
            <p style="text-align: center;"><strong>📧 Email:</strong> amit.kr.shaw.3@gmail.com</p>
            """, unsafe_allow_html=True)

    if is_admin:
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("### 👥 Manage Registered Users")
                st.write("Yahan se naye users add ya delete karein.")
                
                col_add, col_del = st.columns(2)
                
                with col_add:
                    st.markdown("##### ➕ Add Student")
                    new_user_email = st.text_input("Enter Email:", placeholder="rahul@gmail.com", key="add_user").strip().lower()
                    if st.button("➕ Add", type="primary", use_container_width=True):
                        if new_user_email:
                            try:
                                safe_email = urllib.parse.quote(new_user_email)
                                urllib.request.urlopen(f"{st.session_state.apps_script_url}?action=add&email={safe_email}") 
                                st.success(f"Added `{new_user_email}`")
                                st.rerun()
                            except Exception as e:
                                st.error("Link check karein.")
                
                with col_del:
                    st.markdown("##### 🗑️ Remove Student")
                    if st.session_state.live_allowed_users:
                        user_to_delete = st.selectbox("Select Email:", st.session_state.live_allowed_users)
                        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                            try:
                                safe_email_del = urllib.parse.quote(user_to_delete)
                                urllib.request.urlopen(f"{st.session_state.apps_script_url}?action=delete&email={safe_email_del}")
                                st.success("Removed successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error("Link check karein.")
                    else:
                        st.info("No active users.")

            with st.container(border=True):
                st.markdown("### ⚙️ System Configuration")
                new_dpp_url = st.text_input("📚 DPP Questions Sheet Link:", value=st.session_state.dynamic_sheet_url)
                new_users_url = st.text_input("👥 Users Database Sheet Link:", value=st.session_state.users_sheet_url)
                new_api_url = st.text_input("🔗 API Script Web App Link:", value=st.session_state.apps_script_url)
                
                if st.button("💾 Save Settings", type="primary"):
                    st.session_state.dynamic_sheet_url = new_dpp_url
                    st.session_state.users_sheet_url = new_users_url
                    st.session_state.apps_script_url = new_api_url
                    st.success("🎉 Settings saved!")
                    st.rerun()
