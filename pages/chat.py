import time
import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="PAATHSALA Chat",
    page_icon="💬",
    layout="centered"
)

hide_style = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# Auto refresh every 3 sec
st_autorefresh(interval=3000, limit=None, key="chat_refresh")

# ======================================================
# LOGIN CHECK
# ======================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Session expired.")
    st.page_link("main.py", label="🏠 Login Again")
    st.stop()

current_user = st.session_state.get(
    "user_identifier",
    "Student"
)

# ======================================================
# SUPABASE CONNECTION
# ======================================================

# Replace these with your values for now
SUPABASE_URL = "https://rmdwvrjschmeztzrestm.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

# Future:
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ======================================================
# BAD WORD FILTER
# ======================================================
BAD_WORDS = [
    "idiot",
    "stupid",
    "abuse"
]

# ======================================================
# BLOCK CHECK
# ======================================================
try:
    blocked = (
        supabase
        .table("blocked_users")
        .select("*")
        .eq("email", current_user)
        .execute()
    )

    if len(blocked.data) > 0:
        st.error("🚫 Account Blocked")
        st.page_link("main.py", label="🏠 Main Menu")
        st.stop()

except:
    pass

# ======================================================
# HEADER
# ======================================================
st.page_link("main.py", label="🏠 Main Menu")

st.title("💬 PAATHSALA Live Discussion")
st.caption("Discuss doubts with other students")

# ======================================================
# LOAD CHAT
# ======================================================
try:
    response = (
        supabase
        .table("chat_history")
        .select("*")
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    chat_data = response.data[::-1]

    active_users = list(
        set(
            row["sender"]
            for row in chat_data
        )
    )

except:
    st.error("Database Error")
    chat_data = []
    active_users = []

st.info(f"👥 Active Users: {len(active_users)}")
st.write(f"👤 Logged in as: **{current_user}**")

# ======================================================
# ADMIN PANEL
# ======================================================
ADMIN_EMAIL = "paathsala37@gmail.com"

if current_user == ADMIN_EMAIL:

    with st.expander("🛠 Admin Controls"):

        tab1, tab2, tab3 = st.tabs(
            ["Block", "Unblock", "Blocked"]
        )

        with tab1:
            user = st.selectbox(
                "Select User",
                ["Select"] + active_users
            )

            if st.button("🚫 Block User"):
                if user != "Select":
                    try:
                        supabase.table(
                            "blocked_users"
                        ).insert(
                            {"email": user}
                        ).execute()

                        st.success("Blocked")

                    except:
                        st.warning("Already blocked")

        with tab2:

            try:
                blocked = (
                    supabase
                    .table("blocked_users")
                    .select("email")
                    .execute()
                )

                blocked_list = [
                    x["email"]
                    for x in blocked.data
                ]

            except:
                blocked_list = []

            selected = st.selectbox(
                "Select",
                ["Select"] + blocked_list
            )

            if st.button("✅ Unblock"):
                if selected != "Select":
                    supabase.table(
                        "blocked_users"
                    ).delete().eq(
                        "email",
                        selected
                    ).execute()

                    st.success("Unblocked")

        with tab3:

            if len(blocked_list) == 0:
                st.success("No blocked users")
            else:
                for x in blocked_list:
                    st.error(x)

st.divider()

# ======================================================
# SHOW CHAT
# ======================================================
chat_box = st.container(height=450)

with chat_box:

    for row in chat_data:

        sender = row["sender"]

        if current_user == ADMIN_EMAIL:
            display_name = sender
        else:
            display_name = sender[:4] + "***"

        if sender == current_user:
            st.markdown(
                f"🟢 **You:** {row['message']}"
            )
        else:
            st.markdown(
                f"🔵 **{display_name}:** "
                f"{row['message']}"
            )

# ======================================================
# MESSAGE COOLDOWN
# ======================================================
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

# ======================================================
# SEND MESSAGE
# ======================================================
prompt = st.chat_input(
    "Type your doubt..."
)

if prompt:

    prompt = prompt.strip()

    # Empty check
    if not prompt:
        st.warning("Empty message not allowed")
        st.stop()

    # Length check
    if len(prompt) > 500:
        st.warning(
            "Maximum 500 characters allowed"
        )
        st.stop()

    # Spam protection
    now = time.time()

    if (
        now -
        st.session_state.last_message_time
    ) < 5:

        st.warning(
            "Please wait 5 seconds"
        )
        st.stop()

    # Bad words filter
    lower_msg = prompt.lower()

    for word in BAD_WORDS:
        if word in lower_msg:
            st.warning(
                "Inappropriate language detected"
            )
            st.stop()

    st.session_state.last_message_time = now

    try:
        supabase.table(
            "chat_history"
        ).insert({
            "sender": current_user,
            "message": prompt
        }).execute()

        st.rerun()

    except:
        st.error("Message send failed")
