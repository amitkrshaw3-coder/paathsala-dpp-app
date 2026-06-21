import streamlit as st
from supabase import create_client, Client

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="PAATHSALA Chat", page_icon="💬", layout="centered")

# ==========================================
# 2. SECURITY LOCK (LOGIN CHECK) 🔒
# ==========================================
# CHOR MIL GAYA! Yahan 'logged_in' set kar diya hai
if "logged_in" not in st.session_state or st.session_state["logged_in"] == False:
    st.warning("⚠️ Access Denied! Kripya pehle PAATHSALA app me login karein.")
    st.stop() 

# ==========================================
# 3. SUPABASE CONNECTION CONFIGURATION ⚙️
# ==========================================
# 👇 YAHAN APNI SUPABASE DETAILS WAPAS DAAL DIJIYE 👇

SUPABASE_URL = "https://https://rmdwvrjschmeztzrestm.supabase.co" # Apni URL dalein
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHd2cmpzY2htZXp0enJlc3RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNTI2NzcsImV4cCI6MjA5NzYyODY3N30.H9hvCcDe2EUqrkukbxQdKoMSt_VNryl4Hnn7t3XZm2o"          # Apni API key dalein

# 👆 --------------------------------------- 👆

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 4. UI HEADERS & USER INFO
# ==========================================
st.title("💬 PAATHSALA Live Discussion")
st.caption("🚀 Welcome to PAATHSALA Live Doubt Solving Room. Aap yahan apne doubts discuss kar sakte hain.")

# YAHAN BHI CHANGE KIYA HAI: Sender ka email dikhane ke liye 'user_identifier'
current_user = st.session_state.get("user_identifier", "Student")
st.write(f"👤 Connected as: **{current_user}**")
st.divider()

# ==========================================
# 5. CHAT DIKHANE KA BOX (READ FROM DATABASE) 📥
# ==========================================
try:
    response = supabase.table("chat_history").select("*").order("created_at").execute()
    chat_data = response.data
except Exception as e:
    st.error("Database se connect karne me dikkat aa rahi hai. Kripya URL aur Key check karein.")
    chat_data = []

chat_container = st.container(height=450)

with chat_container:
    for row in chat_data:
        if row['sender'] == current_user:
            st.markdown(f"🟢 **Aap**: {row['message']}")
        else:
            st.markdown(f"🔵 **{row['sender']}**: {row['message']}")

# ==========================================
# 6. MESSAGE TYPE KARNE KA BOX (WRITE TO DATABASE) 📤
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
        st.error("Message send nahi ho paya. Kripya check karein ki Supabase me table ka naam 'chat_history' hi hai na.")
