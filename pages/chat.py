import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. PAGE CONFIGURATION & AUTO-REFRESH
# ==========================================
st.set_page_config(page_title="PAATHSALA Chat", page_icon="💬", layout="centered")

# Har 3 second me naye messages check karne ke liye
st_autorefresh(interval=3000, limit=None, key="chat_autorefresh")

# ==========================================
# 2. SECURITY LOCK (LOGIN CHECK) 🔒
# ==========================================
if "logged_in" not in st.session_state or st.session_state["logged_in"] == False:
    st.warning("⚠️ Access Denied! Kripya pehle PAATHSALA app me login karein.")
    st.stop() 

# ==========================================
# 3. SUPABASE CONNECTION CONFIGURATION ⚙️
# ==========================================
# 👇 Yahan Apni URL aur Key wapas daaliye 👇
SUPABASE_URL = "https://rmdwvrjschmeztzrestm.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHd2cmpzY2htZXp0enJlc3RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNTI2NzcsImV4cCI6MjA5NzYyODY3N30.H9hvCcDe2EUqrkukbxQdKoMSt_VNryl4Hnn7t3XZm2o"          
# 👆 --------------------------------------- 👆

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
current_user = st.session_state.get("user_identifier", "Student")

# ==========================================
# 4. 🔴 BOUNCER (BLOCK CHECK) 🔴
# ==========================================
try:
    block_check = supabase.table("blocked_users").select("*").eq("email", current_user).execute()
    if len(block_check.data) > 0:
        st.error("🚫 ACCOUNT BLOCKED!")
        st.error("Aapko chat room me spam karne ya rules todne ke karan block kar diya gaya hai.")
        st.stop() # Blocked user ke liye code yahi ruk jayega
except Exception as e:
    pass # Agar connection error ho to app crash na ho

# ==========================================
# 5. UI HEADERS & USER INFO
# ==========================================
st.title("💬 PAATHSALA Live Discussion")
st.caption("🚀 Welcome to PAATHSALA Live Doubt Solving Room.")
st.write(f"👤 Connected as: **{current_user}**")

# ==========================================
# 🌟 6. SECRET ADMIN PANEL (SIRF AAPKE LIYE) 🌟
# ==========================================
if current_user == "paathsala37@gmail.com":
    with st.expander("🛠️ Admin Controls - Block / Unblock Users", expanded=False):
        tab1, tab2, tab3 = st.tabs(["🚫 Block", "✅ Unblock", "📋 Blocked List"])
        
        with tab1:
            spammer_email = st.text_input("Spammer ka Email ID likhein:", key="block_input")
            if st.button("🚫 Block User", key="block_btn"):
                if spammer_email:
                    try:
                        supabase.table("blocked_users").insert({"email": spammer_email}).execute()
                        st.success(f"✅ {spammer_email} ko block kar diya gaya hai!")
                    except Exception as e:
                        st.error("Error! Shayad user pehle se block hai.")
                else:
                    st.warning("Kripya pehle email ID type karein.")
                    
        with tab2:
            unblock_email = st.text_input("User ka Email ID likhein jise azaad karna hai:", key="unblock_input")
            if st.button("✅ Unblock User", key="unblock_btn"):
                if unblock_email:
                    try:
                        supabase.table("blocked_users").delete().eq("email", unblock_email).execute()
                        st.success(f"🎉 {unblock_email} ko unblock kar diya gaya hai!")
                    except Exception as e:
                        st.error("Unblock karne me error aayi.")
                else:
                    st.warning("Kripya pehle email ID type karein.")
                    
        with tab3:
            st.write("👇 **In users ko chat se block kiya gaya hai:**")
            try:
                blocked_list = supabase.table("blocked_users").select("email").execute()
                if len(blocked_list.data) > 0:
                    for row in blocked_list.data:
                        st.error(f"- {row['email']}")
                else:
                    st.success("Abhi koi bhi user block nahi hai.")
            except Exception as e:
                st.write("List load nahi ho payi.")
st.divider()

# ==========================================
# 7. CHAT DIKHANE KA BOX (READ FROM DATABASE) 📥
# ==========================================
try:
    response = supabase.table("chat_history").select("*").order("created_at").execute()
    chat_data = response.data
except Exception as e:
    st.error(f"Database se connect karne me dikkat aa rahi hai. Error: {e}")
    chat_data = []

chat_container = st.container(height=450)

with chat_container:
    for row in chat_data:
        sender_email = row['sender']
        # Bank-level security: Sirf pehle 4 letter aur uske baad ***
        display_name = sender_email[:4] + "***"
        
        if sender_email == current_user:
            st.markdown(f"🟢 **Aap**: {row['message']}")
        else:
            st.markdown(f"🔵 **{display_name}**: {row['message']}")

# ==========================================
# 8. MESSAGE TYPE KARNE KA BOX (WRITE TO DATABASE) 📤
# ==========================================
if prompt := st.chat_input("Apna doubt ya message yahan type karein..."):
    new_message_data = {
        "sender": current_user,
        "message": prompt
    }
    try:
        supabase.table("chat_history").insert(new_message_data).execute()
        st.rerun()
    except Exception as e:
        st.error("Message send nahi ho paya. Kripya URL/Key check karein.")
