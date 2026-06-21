import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. PAGE CONFIGURATION & AUTO-REFRESH
# ==========================================
st.set_page_config(page_title="PAATHSALA Chat", page_icon="💬", layout="centered")
# 👇 YEH RAHA WO CSS MAGIC JO GITHUB/MENU CHUPAYEGA 👇
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;} /* Top right ka menu chupayega */
footer {visibility: hidden;}    /* Niche ka 'Made with Streamlit' chupayega */
header {visibility: hidden;}    /* Upar ka header jisme GitHub icon hota hai wo chupayega */
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# 👆 ----------------------------------------------- 👆
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
        st.stop() 
except Exception as e:
    pass 

# ==========================================
# 5. UI HEADERS & USER INFO
# ==========================================
# 👇 Yeh naya button aapko wapas main.py par le jayega 👇
st.page_link("main.py", label="🏠 Main Menu me wapas jayein", use_container_width=False)

st.title("💬 PAATHSALA Live Discussion")
st.caption("🚀 Welcome to PAATHSALA Live Doubt Solving Room.")
st.write(f"👤 Connected as: **{current_user}**")

# ==========================================
# 6. DATABASE SE MESSAGES NIKALNA 📥
# (Chat pehle fetch karenge taaki Dropdown me list aake)
# ==========================================
try:
    response = supabase.table("chat_history").select("*").order("created_at").execute()
    chat_data = response.data
    # Chat me aaye sabhi unique emails ki ek list banayenge (Admin ko chhodkar)
    active_users = list(set([row['sender'] for row in chat_data if row['sender'] != "paathsala37@gmail.com"]))
except Exception as e:
    st.error("Database error aa raha hai.")
    chat_data = []
    active_users = []

# ==========================================
# 🌟 7. SMART SECRET ADMIN PANEL (NO TYPING!) 🌟
# ==========================================
if current_user == "paathsala37@gmail.com":
    with st.expander("🛠️ Admin Controls - Block / Unblock Users", expanded=False):
        tab1, tab2, tab3 = st.tabs(["🚫 Block", "✅ Unblock", "📋 Blocked List"])
        
        # Block tab me chat karne walo ki Dropdown
        with tab1:
            spammer_email = st.selectbox("Spammer ko select karein:", ["User chunein..."] + active_users, key="block_select")
            if st.button("🚫 Block User", key="block_btn"):
                if spammer_email != "User chunein...":
                    try:
                        supabase.table("blocked_users").insert({"email": spammer_email}).execute()
                        st.success(f"✅ {spammer_email} ko block kar diya gaya!")
                    except Exception as e:
                        st.error("Shayad user pehle se block hai.")
                else:
                    st.warning("Kripya dropdown se koi user chunein.")
                    
        # Unblock tab me Blocked walo ki Dropdown
        with tab2:
            try:
                blocked_res = supabase.table("blocked_users").select("email").execute()
                blocked_users_list = [row['email'] for row in blocked_res.data]
            except:
                blocked_users_list = []
                
            unblock_email = st.selectbox("Azaad karne ke liye select karein:", ["User chunein..."] + blocked_users_list, key="unblock_select")
            if st.button("✅ Unblock User", key="unblock_btn"):
                if unblock_email != "User chunein...":
                    try:
                        supabase.table("blocked_users").delete().eq("email", unblock_email).execute()
                        st.success(f"🎉 {unblock_email} ko unblock kar diya gaya!")
                    except Exception as e:
                        st.error("Unblock karne me error aayi.")
                else:
                    st.warning("Kripya dropdown se koi user chunein.")
                    
        with tab3:
            st.write("👇 **In users ko block kiya gaya hai:**")
            if len(blocked_users_list) > 0:
                for email in blocked_users_list:
                    st.error(f"- {email}")
            else:
                st.success("Abhi koi bhi user block nahi hai.")
st.divider()

# ==========================================
# 8. CHAT DIKHANE KA BOX (SMART MASKING) 🎭
# ==========================================
chat_container = st.container(height=450)

with chat_container:
    for row in chat_data:
        sender_email = row['sender']
        
        # 🔴 JADUI AANKHEIN (Smart Masking) 🔴
        if current_user == "paathsala37@gmail.com":
            display_name = sender_email # Admin ko pura naam dikhega
        else:
            display_name = sender_email[:4] + "***" # Bacchon ko aada dikhega
        
        if sender_email == current_user:
            st.markdown(f"🟢 **Aap**: {row['message']}")
        else:
            st.markdown(f"🔵 **{display_name}**: {row['message']}")

# ==========================================
# 9. MESSAGE TYPE KARNE KA BOX 📤
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
