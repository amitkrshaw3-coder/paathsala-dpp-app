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

# =========================================================================
# DUMMY LINKS (APP CHALNE KE BAAD ADMIN PANEL SE CHANGE KAREIN)
# =========================================================================

if 'dynamic_sheet_url' not in st.session_state: 
    st.session_state.dynamic_sheet_url = "https://docs.google.com/spreadsheets/d/dummy_link"

if 'users_sheet_url' not in st.session_state: 
    st.session_state.users_sheet_url = "https://docs.google.com/spreadsheets/d/dummy_link"

if 'apps_script_url' not in st.session_state: 
    st.session_state.apps_script_url = "https://script.google.com/macros/s/dummy_link/exec"

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
                            if send_real_otp_email(cleaned_email, st.session_state.
