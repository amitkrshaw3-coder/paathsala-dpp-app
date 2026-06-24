import time
import threading
import base64
from datetime import datetime, timedelta
import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
from ai_bot import ask_paathsala_ai

# ==========================================
# PAGE CONFIG & ULTRA-CLEAN STYLING
# ==========================================
st.set_page_config(page_title="PAATHSALA Chat", page_icon="🎓", layout="centered")

custom_css = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
[data-testid="stVerticalBlock"] { overflow-y: auto; }

/* 🌟 MAGIC FIX: Make Streamlit Buttons look like plain icons (No ugly borders) */
[data-testid="stButton"] button {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0px !important;
    font-size: 18px !important;
    transition: all 0.2s ease-in-out;
}
[data-testid="stButton"] button:hover {
    transform: scale(1.2);
}

/* Custom Chat Bubbles */
.chat-row { display: flex; align-items: flex-start; margin-bottom: 12px; width: 100%; }
.chat-row.user { justify-content: flex-end; }
.chat-row.assistant { justify-content: flex-start; }

.user-msg {
    background: linear-gradient(135deg, #0078D7, #00C6FF);
    padding: 10px 14px;
    border-radius: 18px 18px 2px 18px;
    color: white;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
    max-width: 85%;
}
.assistant-msg {
    background: #2D2D2D;
    padding: 10px 14px;
    border-radius: 18px 18px 18px 2px;
    color: white;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
    max-width: 85%;
    border: 1px solid #444;
}

.time-stamp { font-size: 10px; opacity: 0.7; margin-top: 5px; text-align: right; }
.sender-name { font-size: 11px; color: #00C6FF; margin-bottom: 3px; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st_autorefresh(interval=3000, limit=None, key="chat_refresh")

# ==========================================
# LOGIN & SUPABASE SETUP
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

try:
    blocked = supabase.table("blocked_users").select("*").eq("email", current_user).execute()
    if len(blocked.data) > 0:
        st.error("🚫 ACCOUNT BLOCKED")
        st.stop()
except Exception:
    pass

# ==========================================
# PREMIUM HEADER
# ==========================================
st.markdown("""
<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; margin-bottom: 15px; color: white;'>
    <h3 style='margin:0; color: white;'>🎓 PAATHSALA LIVE ROOM</h3>
    <p style='margin:0; font-size: 13px;'>Learn • Discuss • Grow</p>
</div>
""", unsafe_allow_html=True)

st.write(f"🟢 **Online:** {current_user}")
st.page_link("main.py", label="🏠 Go to Main Menu")

# ==========================================
# LOAD CHAT
# ==========================================
try:
    response = supabase.table("chat_history").select("*").order("created_at", desc=True).limit(100).execute()
    chat_data = response.data[::-1]
    active_users = list(set(row["sender"] for row in chat_data[:20])) 
except Exception as e:
    chat_data = []
    active_users = []

# Unread Messages Counter
if "total_msgs" not in st.session_state:
    st.session_state.total_msgs = len(chat_data)
if len(chat_data) > st.session_state.total_msgs:
    new_msgs = len(chat_data) - st.session_state.total_msgs
    st.toast(f"📬 {new_msgs} New Message(s)!")
    st.session_state.total_msgs = len(chat_data)

st.info(f"👥 Active Users in Room: {len(active_users)}")

# ==========================================
# REPLY & STATE MANAGEMENT
# ==========================================
if "reply_to" not in st.session_state:
    st.session_state.reply_to = None
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

def get_avatar_color(email):
    colors = ["#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93", "#e07a5f"]
    return colors[len(email) % len(colors)]

# ==========================================
# CHAT DISPLAY (MINIMAL UI)
# ==========================================
chat_container = st.container()

with chat_container:
    for row in chat_data:
        msg_id = row.get("id", 0)
        sender = row["sender"]
        message = row["message"]
        reply_text = row.get("reply_to")
        
        # Timestamp parsing
        try:
            utc_dt = datetime.strptime(row['created_at'][:19], "%Y-%m-%dT%H:%M:%S")
            ist_dt = utc_dt + timedelta(hours=5, minutes=30)
            time_str = ist_dt.strftime("%I:%M %p")
        except:
            time_str = ""

        # Badges
        badge = " 🟢" if sender in active_users else ""
        if sender == ADMIN_EMAIL:
            display_name = "Admin 👑" + badge
        elif sender == "PAATHSALA AI 🤖":
            display_name = "PAATHSALA AI 🤖"
        else:
            display_name = sender[:5] + "***" + badge

        # Avatar
        avatar_letter = sender[0].upper() if sender != "PAATHSALA AI 🤖" else "🤖"
        bg_color = get_avatar_color(sender) if sender != "PAATHSALA AI 🤖" else "#333"
        avatar_html = f'<div style="width:32px; height:32px; border-radius:50%; background:{bg_color}; color:white; text-align:center; line-height:32px; font-size:14px; font-weight:bold; flex-shrink:0; border:2px solid #fff; margin: 0px 8px;">{avatar_letter}</div>'

        # Reply Box Format
        reply_html = ""
        if reply_text:
            reply_html = f'<div style="padding:6px; border-left:3px solid #ffcc00; background:rgba(255,255,255,0.1); border-radius:5px; font-size:12px; margin-bottom:5px; color:#ddd;">↪ <b>Reply:</b> {reply_text[:50]}...</div>'

        # Layout: 90% Message, 10% Action Button
        col_main, col_btn = st.columns([9, 1])
        
        with col_main:
            if sender == current_user:
                st.markdown(
                    f'<div class="chat-row user">'
                    f'<div class="user-msg">{reply_html}<div style="font-size:14px;">{message}</div><div class="time-stamp">{time_str}</div></div>'
                    f'{avatar_html}'
                    f'</div>', unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-row assistant">'
                    f'{avatar_html}'
                    f'<div class="assistant-msg"><div class="sender-name">{display_name}</div>{reply_html}<div style="font-size:14px;">{message}</div><div class="time-stamp">{time_str}</div></div>'
                    f'</div>', unsafe_allow_html=True
                )

        # 🌟 Minimal Reply Icon Button
        with col_btn:
            st.write("") # Adjust alignment slightly
            if st.button("↩️", key=f"r_{msg_id}"):
                clean_name = display_name.replace(" 🟢","").replace(" 👑","").replace(" ***","")
                st.session_state.reply_to = {"sender": clean_name, "message": message}
                st.rerun()

# ==========================================
# SEND MESSAGE & UI
# ==========================================
st.divider()

if st.session_state.reply_to:
    st.info(f"↪ Replying to **{st.session_state.reply_to['sender']}**: {st.session_state.reply_to['message'][:40]}...")
    if st.button("❌ Cancel Reply"):
        st.session_state.reply_to = None
        st.rerun()

with st.expander("📎 Attach Image / Screenshot"):
    uploaded_image = st.file_uploader("Upload doubt image", type=['png', 'jpg', 'jpeg'])

prompt = st.chat_input("Type your doubt... (Use @ai for AI Tutor)")

if prompt or uploaded_image:
    final_message = prompt if prompt else "Attached an image."
    final_message = final_message.strip()

    if uploaded_image:
        base64_img = base64.b64encode(uploaded_image.read()).decode()
        img_html = f'<br><img src="data:image/png;base64,{base64_img}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
        final_message += img_html

    if len(final_message) > 5000:
        st.warning("Message too large.")
        st.stop()

    current_time = time.time()
    if (current_time - st.session_state.last_message_time) < 3:
        st.warning("⚠️ Please wait before sending.")
        st.stop()

    for word in BAD_WORDS:
        if word in final_message.lower():
            st.warning("⚠️ Inappropriate language detected.")
            st.stop()

    db_reply_text = f"{st.session_state.reply_to['sender']}: {st.session_state.reply_to['message']}" if st.session_state.reply_to else None

    try:
        supabase.table("chat_history").insert({
            "sender": current_user,
            "message": final_message,
            "reply_to": db_reply_text
        }).execute()

        st.session_state.last_message_time = current_time
        st.session_state.reply_to = None
        st.session_state.total_msgs += 1 

        if prompt and prompt.lower().startswith("@ai"):
            doubt = prompt[3:].strip()
            def ai_background_task(student_doubt, original_prompt, student_email):
                answer = ask_paathsala_ai(student_doubt)
                ai_reply_format = f"{student_email[:5]}***: {original_prompt}"
                supabase.table("chat_history").insert({
                    "sender": "PAATHSALA AI 🤖",
                    "message": answer,
                    "reply_to": ai_reply_format
                }).execute()

            bg_thread = threading.Thread(target=ai_background_task, args=(doubt, prompt, current_user))
            bg_thread.start()
            st.toast("🤖 AI is analyzing your doubt...")
            
        else:
            st.toast("✅ Message Sent")

        st.rerun()

    except Exception as e:
        st.error(f"Actual Error: {e}")
