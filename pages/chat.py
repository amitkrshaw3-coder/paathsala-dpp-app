import time
import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh

# ==========================================
# PAGE CONFIG
# ==========================================
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

# Auto refresh every 3 seconds
st_autorefresh(interval=3000, limit=None, key="chat_refresh")

# ==========================================
# LOGIN CHECK
# ==========================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Session Expired! Please login again.")
    st.page_link(
        "main.py",
        label="🏠 Login Again"
    )
    st.stop()

current_user = st.session_state.get(
    "user_identifier",
    "Student"
)

# ==========================================
# SUPABASE
# ==========================================
SUPABASE_URL = "https://rmdwvrjschmeztzrestm.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHd2cmpzY2htZXp0enJlc3RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNTI2NzcsImV4cCI6MjA5NzYyODY3N30.H9hvCcDe2EUqrkukbxQdKoMSt_VNryl4Hnn7t3XZm2o"

# Future:
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

ADMIN_EMAIL = "paathsala37@gmail.com"

# ==========================================
# BAD WORD FILTER
# ==========================================
BAD_WORDS = [
    "idiot",
    "stupid",
    "abuse"
]

# ==========================================
# BLOCK CHECK
# ==========================================
try:
    blocked = (
        supabase
        .table("blocked_users")
        .select("*")
        .eq("email", current_user)
        .execute()
    )

    if len(blocked.data) > 0:
        st.error("🚫 ACCOUNT BLOCKED")
        st.page_link(
            "main.py",
            label="🏠 Main Menu"
        )
        st.stop()

except Exception:
    pass

# ==========================================
# HEADER
# ==========================================
st.page_link(
    "main.py",
    label="🏠 Main Menu"
)

st.title("💬 PAATHSALA Live Discussion")
st.caption(
    "🚀 Welcome to PAATHSALA Live Doubt Solving Room"
)

st.write(
    f"👤 Connected as: **{current_user}**"
)

# ==========================================
# LOAD CHAT
# ==========================================
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

except Exception as e:

    st.error(f"Database Error: {e}")

    chat_data = []
    active_users = []

st.info(
    f"👥 Active Users: {len(active_users)}"
)

# ==========================================
# ADMIN PANEL
# ==========================================
if current_user == ADMIN_EMAIL:

    with st.expander(
        "🛠 Admin Controls",
        expanded=False
    ):

        tab1, tab2, tab3 = st.tabs(
            ["🚫 Block", "✅ Unblock", "📋 Blocked"]
        )

        with tab1:

            spammer = st.selectbox(
                "Select User",
                ["Select User"] + active_users
            )

            if st.button("🚫 Block User"):

                if spammer != "Select User":

                    try:
                        supabase.table(
                            "blocked_users"
                        ).insert(
                            {"email": spammer}
                        ).execute()

                        st.success(
                            f"{spammer} blocked"
                        )

                    except:
                        st.warning(
                            "Already blocked"
                        )

        with tab2:

            try:

                blocked = (
                    supabase
                    .table("blocked_users")
                    .select("email")
                    .execute()
                )

                blocked_list = [
                    row["email"]
                    for row in blocked.data
                ]

            except:
                blocked_list = []

            selected = st.selectbox(
                "Select User",
                ["Select User"] + blocked_list
            )

            if st.button("✅ Unblock User"):

                if selected != "Select User":

                    supabase.table(
                        "blocked_users"
                    ).delete().eq(
                        "email",
                        selected
                    ).execute()

                    st.success(
                        f"{selected} unblocked"
                    )

        with tab3:

            if len(blocked_list) == 0:
                st.success(
                    "No blocked users"
                )

            else:
                for user in blocked_list:
                    st.error(user)

st.divider()

# ==========================================
# ==========================================
# CHAT DISPLAY
# ==========================================

chat_html = """
<div id="chat-box" style="
height:450px;
overflow-y:auto;
border:1px solid #ddd;
padding:10px;
border-radius:10px;
background:white;
">
"""

for row in chat_data:

    sender = row["sender"]

    if current_user == ADMIN_EMAIL:
        display_name = sender
    else:
        display_name = sender[:4] + "***"

    message = row["message"]

    # Apna message
    if sender == current_user:

        chat_html += f"""
        <div style="text-align:right;margin:8px;">
            <div style="
                background:#DCF8C6;
                padding:10px;
                border-radius:12px;
                display:inline-block;
                max-width:80%;">
                <b>You</b><br>
                {message}
            </div>
        </div>
        """

    # Dusre users ka message
    else:

        chat_html += f"""
        <div style="margin:8px;">
            <div style="
                background:#F1F1F1;
                padding:10px;
                border-radius:12px;
                display:inline-block;
                max-width:80%;">
                <b>{display_name}</b><br>
                {message}
            </div>
        </div>
        """

chat_html += """
</div>

<script>
var objDiv = document.getElementById("chat-box");
objDiv.scrollTop = objDiv.scrollHeight;
</script>
"""

st.markdown(chat_html, unsafe_allow_html=True)

# ==========================================
# SPAM CONTROL
# ==========================================
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

# ==========================================
# SEND MESSAGE
# ==========================================
prompt = st.chat_input(
    "Type your doubt..."
)

if prompt:

    prompt = prompt.strip()

    # Empty message check
    if not prompt:
        st.warning(
            "Empty message not allowed"
        )
        st.stop()

    # Length check
    if len(prompt) > 500:
        st.warning(
            "Maximum 500 characters allowed"
        )
        st.stop()

    # Cooldown check
    current_time = time.time()

    if (
        current_time -
        st.session_state.last_message_time
    ) < 5:

        st.warning(
            "⚠️ Please wait 5 seconds before sending next message."
        )

        st.stop()

    # Bad words check
    lower_msg = prompt.lower()

    for word in BAD_WORDS:

        if word in lower_msg:

            st.warning(
                "⚠️ Inappropriate language detected."
            )

            st.stop()

    # Save message
    try:

        response = (
            supabase
            .table("chat_history")
            .insert({
                "sender": current_user,
                "message": prompt
            })
            .execute()
        )

        st.session_state.last_message_time = current_time

        if response.data:
            st.toast(
                "✅ Message Sent"
            )

    except Exception as e:

        st.error(
            f"Actual Error: {e}"
        )
