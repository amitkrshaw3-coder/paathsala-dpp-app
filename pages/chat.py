import base64
import html
import re
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
from supabase import create_client, Client
from ai_bot import ask_paathsala_ai, submit_student_feedback, run_evaluation_suite

st.set_page_config(page_title="PAATHSALA Chat", page_icon="馃帗", layout="centered")

st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
[data-testid="stSkeleton"] {display:none !important;}
.chat-row {display:flex; align-items:flex-start; margin-bottom:15px; width:100%;}
.chat-row.user {justify-content:flex-end;}
.chat-row.assistant {justify-content:flex-start;}
.user-msg {background:linear-gradient(135deg,#0078D7,#00C6FF);padding:12px 16px;border-radius:18px 18px 2px 18px;color:white;box-shadow:0 3px 10px rgba(0,0,0,.1);max-width:85%;overflow-wrap:anywhere;}
.assistant-msg {background:#fff;padding:12px 16px;border-radius:18px 18px 18px 2px;color:#333;box-shadow:0 3px 10px rgba(0,0,0,.08);max-width:85%;border:1px solid #eee;overflow-wrap:anywhere;}
.time-stamp {font-size:10px;opacity:.75;margin-top:5px;text-align:right;}
.user-time {color:#f0f0f0;} .bot-time {color:#888;}
.sender-name {font-size:12px;color:#0078D7;margin-bottom:4px;font-weight:bold;}
.avatar {width:32px;height:32px;border-radius:50%;color:white;text-align:center;line-height:32px;font-size:14px;font-weight:bold;flex-shrink:0;margin:0 8px;box-shadow:0 2px 5px rgba(0,0,0,.1);}
.typing-text {font-size:14px;color:#888;font-style:italic;}
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("logged_in", False):
    st.warning("鈿狅笍 Session expired. Please log in again.")
    st.page_link("main.py", label="馃彔 Login Again")
    st.stop()

current_user = str(st.session_state.get("user_identifier", "Student"))
ADMIN_EMAIL = "paathsala37@gmail.com"
AI_SENDER = "PAATHSALA AI 馃"
BAD_WORDS = {"idiot", "stupid", "abuse"}

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    st.error("Supabase secrets are missing in Streamlit configuration.")
    st.stop()

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Could not initialize Supabase. Check the project URL and key.")
    st.stop()


def get_avatar_color(identifier):
    colors = ["#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93", "#e07a5f"]
    return colors[len(identifier) % len(colors)]


def safe_message_html(message):
    """
    Escape untrusted HTML. Preserve only our own base64 image tags created by this app.
    All other HTML tags/attributes are escaped.
    """
    text = str(message or "")
    pattern = re.compile(
        r'<img\s+src="data:image/(?:png|jpeg);base64,([A-Za-z0-9+/=]+)"\s+style="max-width:\s*100%;\s*border-radius:\s*8px;\s*margin-top:\s*5px;"\s*>',
        re.IGNORECASE
    )
    parts = []
    last = 0
    for match in pattern.finditer(text):
        parts.append(html.escape(text[last:match.start()]).replace("\n", "<br>"))
        parts.append(
            '<img src="data:image/png;base64,' + match.group(1) +
            '" style="max-width:100%;border-radius:8px;margin-top:5px;">'
        )
        last = match.end()
    parts.append(html.escape(text[last:]).replace("\n", "<br>"))
    return "".join(parts)


def get_time_label(created_at):
    try:
        value = str(created_at).replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone(timedelta(hours=5, minutes=30))).strftime("%I:%M %p")
    except Exception:
        return ""


# Block check: fail closed if the database check errors.
try:
    block_result = (
        supabase.table("blocked_users")
        .select("email")
        .eq("email", current_user)
        .limit(1)
        .execute()
    )
except Exception:
    st.error("Could not verify account status. Please refresh or contact admin.")
    st.stop()

if block_result.data:
    st.error("馃毇 ACCOUNT BLOCKED BY ADMIN")
    st.stop()

st.markdown("""
<div style="text-align:center;padding:15px;background:linear-gradient(90deg,#1e3c72 0%,#2a5298 100%);border-radius:10px;margin-bottom:15px;color:white;">
<h3 style="margin:0;color:white;">馃帗 PAATHSALA LIVE ROOM</h3>
<p style="margin:0;font-size:13px;">Learn 鈥� Discuss 鈥� Grow</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1.write(f"馃煝 **Online:** {html.escape(current_user)}")
col2.page_link("main.py", label="馃彔 Go to Main Menu")

# Admin UI is only a UI check, not a substitute for Supabase RLS policies.
if current_user.lower() == ADMIN_EMAIL.lower():
    try:
        admin_resp = supabase.table("chat_history").select("sender").limit(500).execute()
        active_users = sorted({
            str(row.get("sender", ""))
            for row in (admin_resp.data or [])
            if row.get("sender") not in (ADMIN_EMAIL, AI_SENDER, "")
        })
    except Exception:
        active_users = []

    with st.expander("馃洜 Admin Controls (Block, Clear & AI Eval)", expanded=False):
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["馃毇 Block", "鉁� Unblock", "馃搵 Blocked", "馃棏锔� Clear Chat", "馃 AI Eval"])

        with tab1:
            selected_user = st.selectbox("Select user to block", ["Select User"] + active_users)
            if st.button("馃毇 Block User", use_container_width=True):
                if selected_user != "Select User":
                    try:
                        existing = supabase.table("blocked_users").select("email").eq("email", selected_user).execute()
                        if existing.data:
                            st.info("User is already blocked.")
                        else:
                            supabase.table("blocked_users").insert({"email": selected_user}).execute()
                            st.success(f"{selected_user} has been blocked.")
                            st.rerun()
                    except Exception:
                        st.error("Could not block this user. Check database policies.")

        with tab2:
            try:
                blocked_rows = supabase.table("blocked_users").select("email").execute().data or []
                blocked_list = sorted({str(row["email"]) for row in blocked_rows if row.get("email")})
            except Exception:
                blocked_list = []
            selected_unblock = st.selectbox("Select user to unblock", ["Select User"] + blocked_list)
            if st.button("鉁� Unblock User", use_container_width=True):
                if selected_unblock != "Select User":
                    try:
                        supabase.table("blocked_users").delete().eq("email", selected_unblock).execute()
                        st.success(f"{selected_unblock} unblocked.")
                        st.rerun()
                    except Exception:
                        st.error("Could not unblock this user. Check database policies.")

        with tab3:
            if not blocked_list:
                st.success("No users blocked.")
            else:
                for blocked_email in blocked_list:
                    st.write(f"馃毇 {html.escape(blocked_email)}")

        with tab4:
            st.warning("This permanently deletes all chat messages.")
            confirm_clear = st.checkbox("I understand and want to clear the entire chat.")
            if st.button("馃棏锔� Clear All Chat History", type="primary", use_container_width=True, disabled=not confirm_clear):
                try:
                    supabase.table("chat_history").delete().neq("sender", "DummyClearAllData123").execute()
                    st.success("Chat history cleared.")
                    st.rerun()
                except Exception:
                    st.error("Could not clear chat history. Check database policies.")

        with tab5:
            st.write("### 馃И AI Benchmark & Evaluation")
            if st.button("馃殌 Run AI Accuracy Benchmark", use_container_width=True):
                with st.spinner("Testing AI responses..."):
                    for result in run_evaluation_suite():
                        st.info(
                            f"**Q:** {result['question']}\n\n"
                            f"**Score:** {result['score']} | **Matched:** {', '.join(result['matched_keywords']) or 'None'}\n\n"
                            f"**Sample:** {result['sample_answer']}"
                        )

st.divider()

@st.fragment(run_every=4)
def render_chat_box():
    try:
        response = (
            supabase.table("chat_history")
            .select("sender,message,created_at")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
        chat_data = list(reversed(response.data or []))
    except Exception:
        chat_data = []
        st.warning("Chat history could not be loaded right now.")

    with st.container(height=450, border=True):
        if not chat_data:
            st.info("No messages yet. Be the first to start the discussion! 馃殌")

        for row in chat_data:
            sender = str(row.get("sender") or "Unknown")
            message = safe_message_html(row.get("message", ""))
            time_label = get_time_label(row.get("created_at", ""))

            display_name = "Admin 馃憫" if sender.lower() == ADMIN_EMAIL.lower() else (
                AI_SENDER if sender == AI_SENDER else sender[:5] + "***"
            )
            avatar_letter = "馃" if sender == AI_SENDER else html.escape(sender[:1].upper() or "?")
            avatar_color = get_avatar_color(sender) if sender != AI_SENDER else "#333"
            avatar = (
                f'<div class="avatar" style="background:{avatar_color};">'
                f'{avatar_letter}</div>'
            )

            if sender == current_user:
                st.markdown(
                    f'<div class="chat-row user"><div class="user-msg">'
                    f'<div style="font-size:14px;">{message}</div>'
                    f'<div class="time-stamp user-time">{time_label}</div>'
                    f'</div>{avatar}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-row assistant">{avatar}<div class="assistant-msg">'
                    f'<div class="sender-name">{html.escape(display_name)}</div>'
                    f'<div style="font-size:14px;">{message}</div>'
                    f'<div class="time-stamp bot-time">{time_label}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

render_chat_box()

st.write("")
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0.0
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = "uploader_1"

send_triggered = False
final_message_html = ""
raw_user_prompt = ""

with st.expander("馃搸 Attach Image / Screenshot"):
    uploaded_image = st.file_uploader(
        "Upload doubt image (PNG/JPG, max 3 MB)",
        type=["png", "jpg", "jpeg"],
        key=st.session_state.uploader_key
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Image preview", width=200)
        img_caption = st.text_input("Add a message with image (Use @ai for AI help):")
        if st.button("馃摛 Send Image", type="primary", use_container_width=True):
            image_bytes = uploaded_image.getvalue()
            if len(image_bytes) > 3 * 1024 * 1024:
                st.error("Image is too large. Please upload an image under 3 MB.")
            else:
                mime = uploaded_image.type if uploaded_image.type in ("image/png", "image/jpeg") else "image/png"
                base64_img = base64.b64encode(image_bytes).decode("ascii")
                img_html = (
                    f'<br><img src="data:{mime};base64,{base64_img}" '
                    'style="max-width:100%;border-radius:8px;margin-top:5px;">'
                )
                raw_user_prompt = img_caption.strip() if img_caption else "Attached an image."
                final_message_html = raw_user_prompt + img_html
                send_triggered = True

with st.expander("馃毄 Report AI Error / Give Feedback"):
    feedback_question = st.text_input("Poochha gaya sawal:", key="fb_question_input")
    feedback_correction = st.text_area("Sahi jawab kya hona chahiye tha?:", key="fb_correction_input")
    fb_col1, fb_col2 = st.columns(2)
    if fb_col1.button("馃憤 Helpful Answer", use_container_width=True):
        if feedback_question.strip():
            success = submit_student_feedback(current_user, feedback_question.strip(), "", "helpful")
            st.success("Feedback recorded.") if success else st.error("Feedback save nahi ho paya.")
        else:
            st.warning("Pehle sawal likhein.")
    if fb_col2.button("Report Incorrect AI", use_container_width=True):
        if feedback_question.strip():
            success = submit_student_feedback(
                current_user, feedback_question.strip(), "", "report_error", feedback_correction.strip()
            )
            st.success("Report submitted to Admin.") if success else st.error("Report save nahi ho payi.")
        else:
            st.warning("Pehle sawal likhein.")

chat_prompt = st.chat_input("Type your doubt... (Use @ai for AI Tutor)")
if chat_prompt:
    raw_user_prompt = chat_prompt.strip()
    final_message_html = raw_user_prompt
    send_triggered = True

if send_triggered:
    # Keep message sizes bounded before touching the database.
    if len(final_message_html.encode("utf-8")) > 4 * 1024 * 1024:
        st.error("Message is too large. Please use a smaller image or shorter text.")
        st.stop()

    now = time.time()
    if now - st.session_state.last_message_time < 2:
        st.warning("Please wait a moment before sending another message.")
        st.stop()

    lowered = raw_user_prompt.lower()
    if any(word in lowered.split() for word in BAD_WORDS):
        st.warning("鈿狅笍 Inappropriate language detected.")
        st.stop()

    try:
        supabase.table("chat_history").insert({
            "sender": current_user,
            "message": final_message_html
        }).execute()
    except Exception:
        st.error("Message could not be saved. Check Supabase connectivity and RLS policies.")
        st.stop()

    st.session_state.last_message_time = now

    # Run AI synchronously for reliable Streamlit state and visible error handling.
    # The semaphore inside ai_bot.py limits concurrent requests in this process.
    if raw_user_prompt.lower().startswith("@ai"):
        doubt = raw_user_prompt[3:].strip()
        with st.spinner("PAATHSALA AI is thinking..."):
            answer = ask_paathsala_ai(doubt)
        safe_question = html.escape(raw_user_prompt)
        safe_answer = html.escape(answer).replace("\n", "<br>")
        ai_message = f"<b>{safe_question}</b><br><br>{safe_answer}"
        try:
            supabase.table("chat_history").insert({
                "sender": AI_SENDER,
                "message": ai_message
            }).execute()
        except Exception:
            st.error("AI answered, but its reply could not be saved to chat history.")
    st.rerun()