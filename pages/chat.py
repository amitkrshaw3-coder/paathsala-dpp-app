import time
import threading
import base64
from datetime import datetime, timedelta
import streamlit as st
from supabase import create_client, Client
from ai_bot import ask_paathsala_ai

# ==========================================
# PAGE CONFIG & CSS
# ==========================================
st.set_page_config(page_title="PAATHSALA Chat", page_icon="🎓", layout="centered")

custom_css = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 15px !important;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.12) !important;
    background-color: #fafbfc;
    padding: 10px;
    border: 1px solid #e0e0e0 !important;
}

.chat-row { display: flex; align-items: flex-start; margin-bottom: 15px; width: 100%; }
.chat-row.user { justify-content: flex-end; }
.chat-row.assistant { justify-content: flex-start; }

.user-msg {
    background: linear-gradient(135deg, #0078D7, #00C6FF);
    padding: 12px 16px;
    border-radius: 18px 18px 2px 18px;
    color: white;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
    max-width: 85%;
}
.assistant-msg {
    background: #ffffff;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 2px;
    color: #333;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
    max-width: 85%;
    border: 1px solid #eee;
}

.time-stamp { font-size: 10px; opacity: 0.7; margin-top: 5px; text-align: right; }
.user-time { color: #f0f0f0; }
.bot-time { color: #888; }
.sender-name { font-size: 12px; color: #0078D7; margin-bottom: 4px; font-weight: bold; }

/* Blinking Typing Animation */
.typing-text { font-size: 14px; color: #888; font-style: italic; animation: blink 1.5s infinite; }
@keyframes blink { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# SESSION & SUPABASE SETUP
# ==========================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Session Expired! Please login again.")
    st.page_link("main.py", label="🏠 Login Again")
    st.stop()

current_user = st.session_state.get("user_identifier", "Student")

SUPABASE_URL = "https://rmdwvrjschmeztzrestm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHd2cmpzY2htZXp0enJlc3RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNTI2NzcsImV4cCI6MjA5NzYyODY3N30.H9hvCcDe2EUqrkukbxQdKoMSt_VNryl4Hnn7t3XZm2o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
ADMIN_EMAIL = "paathsala37@gmail.com"
BAD_WORDS = ["idiot", "stupid", "abuse"]

def get_avatar_color(email):
    colors = ["#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93", "#e07a5f"]
    return colors[len(email) % len(colors)]

if "ai_is_typing" not in st.session_state:
    st.session_state.ai_is_typing = False

# ==========================================
# STATIC HEADER (Will NOT refresh)
# ==========================================
st.markdown("""
<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; margin-bottom: 15px; color: white;'>
    <h3 style='margin:0; color: white;'>🎓 PAATHSALA LIVE ROOM</h3>
    <p style='margin:0; font-size: 13px;'>Learn • Discuss • Grow</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1.write(f"🟢 **Online:** {current_user}")
col2.page_link("main.py", label="🏠 Go to Main Menu")

# ==========================================
# 🌟 MAGIC FRAGMENT: ONLY THIS BOX REFRESHES
# ==========================================
# Yeh function har 2.5 second mein sirf apne aap ko refresh karega, poore page ko nahi!
@st.fragment(run_every=2.5)
def render_chat_box():
    try:
        response = supabase.table("chat_history").select("*").order("created_at", desc=True).limit(100).execute()
        chat_data = response.data[::-1]
    except Exception:
        chat_data = []

    chat_container = st.container(height=500, border=True)
    
    with chat_container:
        for row in chat_data:
            sender = row["sender"]
            message = row["message"]
            
            try:
                utc_dt = datetime.strptime(row['created_at'][:19], "%Y-%m-%dT%H:%M:%S")
                ist_dt = utc_dt + timedelta(hours=5, minutes=30)
                time_str = ist_dt.strftime("%I:%M %p")
            except:
                time_str = ""

            display_name = "Admin 👑" if sender == ADMIN_EMAIL else ("PAATHSALA AI 🤖" if sender == "PAATHSALA AI 🤖" else sender[:5] + "***")
            avatar_letter = sender[0].upper() if sender != "PAATHSALA AI 🤖" else "🤖"
            bg_color = get_avatar_color(sender) if sender != "PAATHSALA AI 🤖" else "#333"
            avatar_html = f'<div style="width:32px; height:32px; border-radius:50%; background:{bg_color}; color:white; text-align:center; line-height:32px; font-size:14px; font-weight:bold; flex-shrink:0; border:2px solid #fff; margin: 0px 8px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);">{avatar_letter}</div>'

            if sender == current_user:
                st.markdown(
                    f'<div class="chat-row user">'
                    f'<div class="user-msg"><div style="font-size:14px;">{message}</div><div class="time-stamp user-time">{time_str}</div></div>'
                    f'{avatar_html}</div>', unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-row assistant">'
                    f'{avatar_html}'
                    f'<div class="assistant-msg"><div class="sender-name">{display_name}</div><div style="font-size:14px;">{message}</div><div class="time-stamp bot-time">{time_str}</div></div>'
                    f'</div>', unsafe_allow_html=True
                )
        
        # Agar AI soch raha hai, toh typing animation dikhao
        if st.session_state.ai_is_typing:
            st.markdown(
                f'<div class="chat-row assistant">'
                f'<div style="width:32px; height:32px; border-radius:50%; background:#333; color:white; text-align:center; line-height:32px; font-size:14px; font-weight:bold; flex-shrink:0; border:2px solid #fff; margin: 0px 8px;">🤖</div>'
                f'<div class="assistant-msg"><div class="sender-name">PAATHSALA AI 🤖</div><div class="typing-text">AI is thinking... ⏳</div></div>'
                f'</div>', unsafe_allow_html=True
            )

# Fragment ko yahan call kar diya (Ye background mein auto-refresh hota rahega)
render_chat_box()

# ==========================================
# MESSAGE INPUT (Static, Doesn't Glitch)
# ==========================================
st.write("") 

if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

with st.expander("📎 Attach Image / Screenshot"):
    uploaded_image = st.file_uploader("Upload doubt image", type=['png', 'jpg', 'jpeg'])

prompt = st.chat_input("Type your doubt... (Use @ai for AI Tutor)")

if prompt or uploaded_image:
    final_message = prompt if prompt else "Attached an image."
    final_message = final_message.strip()

    if uploaded_image:
        base64_img = base64.b64encode(uploaded_image.read()).decode()
        final_message += f'<br><img src="data:image/png;base64,{base64_img}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'

    if len(final_message) > 5000:
        st.warning("Message too large.")
        st.stop()

    current_time = time.time()
    if (current_time - st.session_state.last_message_time) < 2:
        st.warning("⚠️ Please wait before sending.")
        st.stop()

    # Database mein message insert karna
    supabase.table("chat_history").insert({
        "sender": current_user,
        "message": final_message
    }).execute()

    st.session_state.last_message_time = current_time

    # 🤖 AI LOGIC - Background Thread (App Hang Nahi Hogi)
    if prompt and prompt.lower().startswith("@ai"):
        doubt = prompt[3:].strip()
        st.session_state.ai_is_typing = True # Typing indicator ON
        
        def fetch_ai_answer(student_doubt, original_prompt, student_email):
            answer = ask_paathsala_ai(student_doubt)
            full_ai_message = f"**{student_email[:5]}*** asked:* {original_prompt}<br><br>{answer}"
            
            supabase.table("chat_history").insert({
                "sender": "PAATHSALA AI 🤖",
                "message": full_ai_message
            }).execute()
            
            st.session_state.ai_is_typing = False # Typing indicator OFF jab answer aa jaye

        # AI ko background mein bhej diya, main app free hai!
        threading.Thread(target=fetch_ai_answer, args=(doubt, prompt, current_user)).start()

    # User ke message bhejte hi sirf ek baar page instantly update hoga
    st.rerun()
