import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh  # Nayi library auto-refresh ke liye

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="PAATHSALA Chat", page_icon="💬", layout="centered")

# ==========================================
# 2. AUTO-REFRESHER (Magic Trick) 🪄
# ==========================================
# Yeh line har 3000 milliseconds (3 seconds) me page ko chupchap refresh karegi
# Jisse kisi aur ka message aate hi turant screen par dikh jayega!
st_autorefresh(interval=3000, limit=None, key="chat_autorefresh")

# ==========================================
# 3. SECURITY LOCK (LOGIN CHECK) 🔒
# ==========================================
if "logged_in" not in st.session_state or st.session_state["logged_in"] == False:
    st.warning("⚠️ Access Denied! Kripya pehle PAATHSALA app me login karein.")
    st.stop() 

# ==========================================
# 4. SUPABASE CONNECTION CONFIGURATION ⚙️
# ==========================================
# 👇 Apni URL aur Key yahan daaliye 👇
SUPABASE_URL = "https://rmdwvrjschmeztzrestm.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHd2cmpzY2htZXp0enJlc3RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNTI2NzcsImV4cCI6MjA5NzYyODY3N30.H9hvCcDe2EUqrkukbxQdKoMSt_VNryl4Hnn7t3XZm2oE"          
# 👆 --------------------------------------- 👆

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 5. UI HEADERS & USER INFO
# ==========================================
st.title("💬 PAATHSALA Live Discussion")
st.caption("🚀 Welcome to PAATHSALA Live Doubt Solving Room.")

current_user = st.session_state.get("user_identifier", "Student")

# Yahan aapko khudka naam dikhega
st.write(f"👤 Connected as: **{current_user}**")
st.divider()

# ==========================================
# 6. CHAT DIKHANE KA BOX (READ FROM DATABASE) 📥
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
        
        # TRICK 1: Email ke shuruati 4 letters lo aur aage '***' laga do (Bank Level Security)
        # Jaise 'paathsala37@gmail.com' ban jayega 'paat***'
        display_name = sender_email[:4] + "***"
        
        if sender_email == current_user:
            st.markdown(f"🟢 **Aap**: {row['message']}")
        else:
            st.markdown(f"🔵 **{display_name}**: {row['message']}")

# ==========================================
# 7. MESSAGE TYPE KARNE KA BOX (WRITE TO DATABASE) 📤
# ==========================================
if prompt := st.chat_input("Apna doubt ya message yahan type karein..."):
    
    new_message_data = {
        "sender": current_user,
        "message": prompt
    }
    
    try:
        supabase.table("chat_history").insert(new_message_data).execute()
        # Message bhejne ke turant baad refresh
        st.rerun()
    except Exception as e:
        st.error("Message send nahi ho paya. Kripya URL/Key check karein.")
