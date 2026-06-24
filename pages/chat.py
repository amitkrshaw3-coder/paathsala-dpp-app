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

/* Ghost Refresh Magic */
[data-testid="stFragment"], 
div[data-testid="stVerticalBlockBorderWrapper"], 
[data-testid="stVerticalBlock"],
.st-emotion-cache-1kyxreq,
.st-emotion-cache-1wmy9hl {
    opacity: 1 !important;
    transition: none !important;
    filter: none !important;
    animation: none !important;
}

[data-testid="stSkeleton"] { display: none !important; }

/* Floating Box Setup */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 15px !important;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.12) !important;
    background-color: #ffffff !important; 
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
    overflow-wrap: break-word;
}
.assistant-msg {
    background: #ffffff;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 2px;
    color: #333;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
    max-width: 85%;
    border: 1px solid #eee;
    overflow-wrap: break-word;
}

.time-stamp { font-size: 10px; opacity: 0.7; margin-top: 5px; text-align: right; }
.user-time { color: #f0f0f0; }
.bot-time { color: #888; }
.sender-name { font-size: 12px; color: #0078D7; margin-bottom: 4px; font-weight: bold; }
.typing-text { font-size: 14px; color: #888; font-style: italic; }
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

# BLOCK CHECK
try:
    blocked = supabase.table("blocked_users").select("*").eq("email", current_user).execute()
    if len(blocked.data) > 0:
        st.error("🚫 ACCOUNT BLOCKED BY ADMIN")
        st.stop()
except Exception:
    pass

# ==========================================
# STATIC HEADER
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
# 🛠️ ADMIN CONTROLS PANEL
# ==========================================
if current_user == ADMIN_EMAIL:
    # Fetch active users for the dropdown
    try:
        admin_resp = supabase.table("chat_history").select("sender").limit(200).execute()
        active_users_list = list(set([row["sender"] for row in admin_resp.data if row["sender"] not in [ADMIN_EMAIL, "PAATHSALA AI 🤖"]]))
    except:
        active_users_list = []

    with st.expander("🛠 Admin Controls (Block & Clear Data)", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs(["🚫 Block", "✅ Unblock", "📋 Blocked List", "🗑️ Clear Chat"])

        with tab1:
            spammer = st.selectbox("Select User to Block", ["Select User"] + active_users_list)
            if st.button("🚫 Block User", use_container_width=True):
                if spammer != "Select User":
                    try:
                        supabase.table("blocked_users").insert({"email": spammer}).execute()
                        st.success(f"{spammer} has been blocked.")
                    except:
                        st.warning("User is already blocked.")

        with tab2:
            try:
                blocked_res = supabase.table("blocked_users").select("email").execute()
                blocked_list = [row["email"] for row in blocked_res.data]
            except:
                blocked_list = []
            
            selected_unblock = st.selectbox("Select User to Unblock", ["Select User"] + blocked_list)
            if st.button("✅ Unblock User", use_container_width=True):
                if selected_unblock != "Select User":
                    supabase.table("blocked_users").delete().eq("email", selected_unblock).execute()
                    st.success(f"{selected_unblock} unblocked successfully.")

        with tab3:
            if not blocked_list:
                st.success("No users are currently blocked.")
            else:
                for u in blocked_list:
                    st.error(f"🚫 {u}")
        
        with tab4:
            st.warning("⚠️ Warning: This will permanently delete ALL messages from the database.")
            if st.button("🗑️ Clear All Chat History", type="primary", use_container_width=True):
                try:
                    # Deletes all rows where sender is not some dummy text (Clears entire table)
                    supabase.table("chat_history").delete().neq("sender", "DummyClearAllData123").execute()
                    st.success("✅ Entire Chat History Cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing chat: {e}")

st.divider()

# ==========================================
# 🌟 INVISIBLE AUTO-REFRESH CHAT DISPLAY 
# ==========================================
@st.fragment(run_every=2)
def render_chat_box():
    try:
        response = supabase.table("chat_history").select("*").order("created_at", desc=True).limit(100).execute()
        chat_data = response.data[::-1]
    except Exception:
        chat_data = []

    chat_container = st.container(height=450, border=True)
    
    with chat_container:
        if not chat_data:
            st.info("No messages yet. Be the first to start the discussion! 🚀")
            
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
        
        # AI Typing Indicator
        if st.session_state.ai_is_typing:
            st.markdown(
                f'<div class="chat-row assistant">'
                f'<div style="width:32px; height:32px; border-radius:50%; background:#333; color:white; text-align:center; line-height:32px; font-size:14px; font-weight:bold; flex-shrink:0; border:2px solid #fff; margin: 0px 8px;">🤖</div>'
                f'<div class="assistant-msg"><div class="sender-name">PAATHSALA AI 🤖</div><div class="typing-text">AI is thinking... ⏳</div></div>'
                f'</div>', unsafe_allow_html=True
            )

render_chat_box()

# ==========================================
# INPUT LOGIC (Text vs Image)
# ==========================================
st.write("") 

if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = "uploader_1"

send_triggered = False
final_message_html = ""
raw_user_prompt = ""

# 1. 📎 IMAGE UPLOAD SECTION
with st.expander("📎 Attach Image / Screenshot"):
    uploaded_image = st.file_uploader("Upload doubt image", type=['png', 'jpg', 'jpeg'], key=st.session_state.uploader_key)
    
    if uploaded_image:
        st.image(uploaded_image, caption="Image Preview", width=200)
        img_caption = st.text_input("Add a message with image (Use @ai for AI help):")
        
        if st.button("📤 Send Image", type="primary", use_container_width=True):
            base64_img = base64.b64encode(uploaded_image.read()).decode()
            img_html = f'<br><img src="data:image/png;base64,{base64_img}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
            
            raw_user_prompt = img_caption.strip() if img_caption else "Attached an image."
            final_message_html = raw_user_prompt + img_html
            send_triggered = True
            
            st.session_state.uploader_key = f"uploader_{int(time.time())}"

# 2. 💬 NORMAL TEXT CHAT SECTION
chat_prompt = st.chat_input("Type your doubt... (Use @ai for AI Tutor)")

if chat_prompt:
    raw_user_prompt = chat_prompt.strip()
    final_message_html = raw_user_prompt
    send_triggered = True

# ==========================================
# COMMON SEND LOGIC 
# ==========================================
if send_triggered:
    if len(final_message_html) > 5000000:
        st.warning("⚠️ Image file is too large! Please upload under 3MB.")
        st.stop()

    current_time = time.time()
    if (current_time - st.session_state.last_message_time) < 2:
        st.warning("⚠️ Please wait before sending.")
        st.stop()

    for word in BAD_WORDS:
        if word in final_message_html.lower():
            st.warning("⚠️ Inappropriate language detected.")
            st.stop()

    # DB Insert
    supabase.table("chat_history").insert({
        "sender": current_user,
        "message": final_message_html
    }).execute()

    st.session_state.last_message_time = current_time

    # 🤖 AI LOGIC
    if raw_user_prompt.lower().startswith("@ai"):
        doubt = raw_user_prompt[3:].strip()
        st.session_state.ai_is_typing = True 
        
        def fetch_ai_answer(student_doubt, original_prompt, student_email):
            try:
                answer = ask_paathsala_ai(student_doubt)
                full_ai_message = f"**{student_email[:5]}*** asked:* {original_prompt}<br><br>{answer}"
                
                supabase.table("chat_history").insert({
                    "sender": "PAATHSALA AI 🤖",
                    "message": full_ai_message
                }).execute()
            except Exception:
                pass
            finally:
                st.session_state.ai_is_typing = False 
        
        threading.Thread(target=fetch_ai_answer, args=(doubt, raw_user_prompt, current_user)).start()

    st.rerun()
