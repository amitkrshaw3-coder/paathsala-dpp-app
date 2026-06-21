import streamlit as st
from supabase import create_client, Client

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="PAATHSALA Chat", page_icon="💬", layout="centered")

# ==========================================
# 2. SECURITY LOCK (LOGIN CHECK) 🔒
# ==========================================
# Dhyan dein: Agar aapne main.py me login verify karne ke liye 'login_proof' ki jagah 
# koi aur variable use kiya hai (jaise 'logged_in' ya 'phone_verified'), to use niche badal lein.
if "login_proof" not in st.session_state or st.session_state["login_proof"] == False:
    st.warning("⚠️ Access Denied! Kripya pehle PAATHSALA app me login karein.")
    st.stop() # Bin login wale user ke liye code yahi ruk jayega

# ==========================================
# 3. SUPABASE CONNECTION CONFIGURATION ⚙️
# ==========================================
# 👇 YAHAN APNI SUPABASE DETAILS UPDATE KAREIN 👇

SUPABASE_URL = "https://rmdwvrjschmeztzrestm.supabase.co" # Apni Reference ID wali URL yahan dalein
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHd2cmpzY2htZXp0enJlc3RtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwNTI2NzcsImV4cCI6MjA5NzYyODY3N30.H9hvCcDe2EUqrkukbxQdKoMSt_VNryl4Hnn7t3XZm2o"          # Apni legacy anon key yahan paste karein

# 👆 --------------------------------------- 👆

# Supabase Client initialize karna
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 4. UI HEADERS & USER INFO
# ==========================================
st.title("💬 PAATHSALA Live Discussion")
st.caption("🚀 Welcome to PAATHSALA Live Doubt Solving Room. Aap yahan apne doubts discuss kar sakte hain.")

# User ka naam nikalna (Agar login system me kisi variable me naam save hai to wo utha lega, nahi to 'Student' dikhayega)
current_user = st.session_state.get("user_name", "Student")
st.write(f"👤 Connected as: **{current_user}**")
st.divider()

# ==========================================
# 5. CHAT DIKHANE KA BOX (READ FROM DATABASE) 📥
# ==========================================
try:
    # Supabase ki 'chat_history' table se saare messages time ke hisaab se laana
    response = supabase.table("chat_history").select("*").order("created_at").execute()
    chat_data = response.data
except Exception as e:
    st.error("Database se connect karne me dikkat aa rahi hai. Kripya URL aur Key check karein.")
    chat_data = []

# Ek fixed height wala container jisme saare messages scroll honge
chat_container = st.container(height=450)

with chat_container:
    for row in chat_data:
        # Agar message khud aapne bheja hai
        if row['sender'] == current_user:
            st.markdown(f"🟢 **Aap**: {row['message']}")
        # Agar kisi aur registered student ne bheja hai
        else:
            st.markdown(f"🔵 **{row['sender']}**: {row['message']}")

# ==========================================
# 6. MESSAGE TYPE KARNE KA BOX (WRITE TO DATABASE) 📤
# ==========================================
if prompt := st.chat_input("Apna doubt ya message yahan type karein..."):
    
    # Naye message ka format taiyar karna
    new_message_data = {
        "sender": current_user,
        "message": prompt
    }
    
    try:
        # Supabase me data insert karna
        supabase.table("chat_history").insert(new_message_data).execute()
        # Message save hote hi page ko refresh karna taaki screen par turant dikhe
        st.rerun()
    except Exception as e:
        st.error("Message send nahi ho paya. Kripya check karein ki Supabase me table ka naam 'chat_history' hi hai na.")
