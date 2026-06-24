import time
import threading
import base64
from datetime import datetime, timedelta
import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
from ai_bot import ask_paathsala_ai

# ==========================================
# PAGE CONFIG & PREMIUM STYLING
# ==========================================
st.set_page_config(
    page_title="PAATHSALA Chat",
    page_icon="🎓",
    layout="centered"
)

# Premium CSS for Chat Bubbles, Hide Menus, and Native Scroll
custom_css = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
[data-testid="stVerticalBlock"] { overflow-y: auto; }

/* Custom Chat Bubbles */
.user-msg {
    background: linear-gradient(135deg, #0078D7, #00C6FF);
    padding: 12px 16px;
    border-radius: 18px 18px 2px 18px;
    color: white;
    margin-bottom: 5px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
    display: inline-block;
    max-width: 85%;
    float: right;
}
.assistant-msg {
    background: #2D2D2D;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 2px;
    color: white;
    margin-bottom: 5px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
    display: inline-block;
    max-width: 85%;
    float: left;
    border: 1px solid #444;
}
.clear-float { clear: both; }
.time-stamp {
    font-size: 10px;
    opacity: 0.7;
    margin-top: 5px;
    text-align: right;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Auto refresh every 3 seconds
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
<div style='text-align: center; padding: 15px; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; margin-bottom: 20px; color: white;'>
    <h2 style='margin:0; color: white;'>🎓 PAATHSALA LIVE ROOM</h2>
    <p style='margin:0; font-size: 14px;'>Learn • Discuss • Grow</p>
</div>
""", unsafe_allow_html=True)

st.write(f"👤 Connected as: **{current_user}**")
st.page_link("main.py", label="🏠 Go to Main Menu")

# ==========================================
# LOAD CHAT
# ==========================================
try:
    response = supabase.table("chat_history").select("*").order("created_at", desc=True).limit(100).execute()
    chat_data = response.data[::-1]
    active_users = list(set(row["sender"] for row in chat_data))
except Exception as e:
    chat_data = []
    active_users = []

st.info(f"👥 Active Users in Room: {len(active_users)}")

# ==========================================
# REPLY & STATE MANAGEMENT
# ==========================================
if "reply_to" not in st.session_state:
    st.session_state.reply_to = None
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

# ==========================================
# CHAT DISPLAY (PREMIUM UI)
# ==========================================
chat_container = st.container()

with chat_container:
    for row in chat_data:
        msg_id = row.get("id", 0)
        sender = row["sender"]
        message = row["message"]
        reply_text = row.get("reply_to")
        likes = row.get("likes", 0)
        
        # Timestamp parsing (UTC to IST Conversion)
        try:
            utc_dt = datetime.strptime(row['created_at'][:19], "%Y-%m-%dT%H:%M:%S")
            ist_dt = utc_dt + timedelta(hours=5, minutes=30)
            time_str = ist_dt.strftime("%I:%M %p")
        except:
            time_str = ""

        # Display Name masking
        if current_user == ADMIN_EMAIL or sender == "PAATHSALA AI 🤖":
            display_name = sender
        else:
            display_name = sender[:4] + "***"

        col_main, col_btn1, col_btn2 = st.columns([7, 1, 1])
        
        with col_main:
            # Format Reply Block
            reply_html = ""
            if reply_text:
                reply_html = f"""
                <div style="padding:6px; border-left:3px solid #ffcc00; background:rgba(255,255,255,0.1); border-radius:5px; font-size:12px; margin-bottom:5px; color:#ddd;">
                    ↪ <b>Reply:</b> {reply_text[:60]}...
                </div>
                """

            # RIGHT ALIGNED (User)
            if sender == current_user:
                st.markdown(f"""
                <div style="width: 100%;">
                    <div class="user-msg">
                        {reply_html}
                        <div style="font-size: 15px;">{message}</div>
                        <div class="time-stamp">{time_str}</div>
                    </div>
                    <div class="clear-float"></div>
                </div>
                """, unsafe_allow_html=True)
                
            # LEFT ALIGNED (Others & AI)
            else:
                st.markdown(f"""
                <div style="width: 100%;">
                    <div class="assistant-msg">
                        <div style="font-size: 11px; color: #00C6FF; margin-bottom: 3px;"><b>{display_name}</b></div>
                        {reply_html}
                        <div style="font-size: 15px;">{message}</div>
                        <div class="time-stamp">{time_str}</div>
                    </div>
                    <div class="clear-float"></div>
                </div>
                """, unsafe_allow_html=True)

        with col_btn1:
            if st.button("↩️", key=f"reply_btn_{msg_id}"):
                st.session_state.reply_to = {"sender": display_name, "message": message}
                st.rerun()
                
        with col_btn2:
            if st.button(f"❤️ {likes if likes > 0 else ''}", key=f"like_btn_{msg_id}"):
                try:
                    supabase.table("chat_history").update({"likes": likes + 1}).eq("id", msg_id).execute()
                    st.rerun()
                except:
                    pass

# ==========================================
# SEND MESSAGE & IMAGE UPLOAD UI
# ==========================================
st.divider()

if st.session_state.reply_to:
    st.info(f"↪ Replying to **{st.session_state.reply_to['sender']}**: {st.session_state.reply_to['message'][:50]}...")
    if st.button("❌ Cancel Reply"):
        st.session_state.reply_to = None
        st.rerun()

# Image Uploader (Collapsible to keep UI clean)
with st.expander("📎 Attach Image / Screenshot"):
    uploaded_image = st.file_uploader("Upload doubt image", type=['png', 'jpg', 'jpeg'])

prompt = st.chat_input("Type your doubt... (Use @ai for AI Tutor)")

# Trigger send if prompt has text OR an image is attached
if prompt or uploaded_image:
    
    final_message = prompt if prompt else "Attached an image."
    final_message = final_message.strip()

    # If image exists, convert to Base64 HTML and attach to message
    if uploaded_image:
        base64_img = base64.b64encode(uploaded_image.read()).decode()
        img_html = f'<br><img src="data:image/png;base64,{base64_img}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
        final_message += img_html

    # Validations
    if len(final_message) > 5000: # Increased limit for image HTML
        st.warning("Message too large.")
        st.stop()

    current_time = time.time()
    if (current_time - st.session_state.last_message_time) < 3:
        st.warning("⚠️ Please wait a few seconds before sending.")
        st.stop()

    for word in BAD_WORDS:
        if word in final_message.lower():
            st.warning("⚠️ Inappropriate language detected.")
            st.stop()

    # Format reply string
    db_reply_text = None
    if st.session_state.reply_to:
        db_reply_text = f"{st.session_state.reply_to['sender']}: {st.session_state.reply_to['message']}"

    try:
        # DB Insert
        db_response = supabase.table("chat_history").insert({
            "sender": current_user,
            "message": final_message,
            "reply_to": db_reply_text,
            "likes": 0
        }).execute()

        st.session_state.last_message_time = current_time
        st.session_state.reply_to = None

        # AI BOT THREADING
        if prompt and prompt.lower().startswith("@ai"):
            doubt = prompt[3:].strip()
            def ai_background_task(student_doubt, original_prompt, student_email):
                answer = ask_paathsala_ai(student_doubt)
                ai_reply_format = f"{student_email[:4]}***: {original_prompt}"
                supabase.table("chat_history").insert({
                    "sender": "PAATHSALA AI 🤖",
                    "message": answer,
                    "reply_to": ai_reply_format,
                    "likes": 0
                }).execute()

            bg_thread = threading.Thread(target=ai_background_task, args=(doubt, prompt, current_user))
            bg_thread.start()
            st.toast("🤖 AI is analyzing your doubt...")
            
        else:
            st.toast("✅ Message Sent")

        st.rerun()

    except Exception as e:
        st.error(f"Actual Error: {e}")
