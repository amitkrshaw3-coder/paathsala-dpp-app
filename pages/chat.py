import streamlit as st
from datetime import datetime
# --- SECURITY LOCK ---
# Agar user ke paas login ka proof nahi hai, to usko wapas bhej do
# (Aap check kijiye ki aapne login ke liye konsa session_state variable use kiya hai, 
# main yahan 'logged_in' maan kar chal raha hu. Agar aapne kuch aur naam rakha hai jaise 'phone_verified', to wo likh dijiyega)

if "logged_in" not in st.session_state or st.session_state["logged_in"] == False:
    st.warning("⚠️ Access Denied! Kripya pehle PAATHSALA me login karein.")
    st.page_link("main.py", label="🏠 Wapas Login Page Par Jayein", icon="🔙")
    st.stop() # Ye line code ko yahi rok degi, niche ka chat box dikhega hi nahi!

# Page ki setting
st.set_page_config(page_title="Live Chat", page_icon="💬")

st.title("💬 PAATHSALA Live Discussion")
st.caption("Apne doubts yahan poochiye. Sabhi students aur admin yahan chat kar sakte hain.")

# Chat memory initialize karna
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# User ka naam (Agar login se naam nahi mila, toh 'Student' dikhega)
current_user = st.session_state.get("user_name", "Student") 

# Chat dikhane ka box
chat_container = st.container(height=450)

with chat_container:
    for msg in st.session_state.chat_messages:
        role = "user" if msg["sender"] == current_user else "assistant"
        with st.chat_message(role):
            st.markdown(f"**{msg['sender']}**: {msg['text']}")
            st.caption(f"{msg['time']}")

# Message type karne ka box
if prompt := st.chat_input("Apna doubt ya message yahan type karein..."):
    current_time = datetime.now().strftime("%I:%M %p")
    new_message = {
        "sender": current_user, 
        "text": prompt, 
        "time": current_time
    }
    
    st.session_state.chat_messages.append(new_message)
    st.rerun()
