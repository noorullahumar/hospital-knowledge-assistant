import streamlit as st
import os
import time
import re
from database import * 
from ingest import process_pdf
from rag_pipeline import build_qa_chain, role_based_query
from style import apply_custom_css
from dotenv import load_dotenv

load_dotenv()

# --- INITIALIZATION ---
init_db()

st.set_page_config(page_title="Hospital AI Portal", page_icon="🏥", layout="wide")
apply_custom_css()

# --- STATE MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# --- HELPERS ---
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# --- UI PAGES ---

def landing_page():
    st.markdown("""
        <div class='hero-section'>
            <h1>🏥 Hospital Intelligence Portal</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>
                Secure AI-powered knowledge retrieval for healthcare professionals and patients.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.info("### 🛡️ Secure\nRole-based access controls.")
    with col2: st.info("### ⚡ Fast\nInstant policy retrieval.")
    with col3: st.info("### 📚 Verified\nOfficial documentation only.")

    st.divider()
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button("🚀 Access Portal", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()

def auth_page():
    st.markdown("<h2 style='text-align: center;'>Portal Authentication</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    
    with col:
        tab_login, tab_signup = st.tabs(["Login", "Create Account"])
        
        with tab_login:
            email = st.text_input("Username/Email", key="l_email")
            pwd = st.text_input("Password", type="password", key="l_pwd")
            
            if st.button("Login", use_container_width=True):
                if not email or not pwd:
                    st.warning("⚠️ Please fill in all fields.")
                else:
                    with st.spinner("Authenticating..."):
                        role = verify_user(email, pwd)
                        if role:
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.username = email
                            
                            # Fetch or create session
                            sessions = get_user_sessions(email)
                            st.session_state.current_session = sessions[0] if sessions else create_new_session(email)
                            
                            st.toast(f"Welcome back, {email}!", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials.")

            with st.expander("Forgot Password?"):
                r_email = st.text_input("Registered Email", key="r_email")
                r_pwd = st.text_input("New Password", type="password", key="r_pwd")
                if st.button("Reset Password", use_container_width=True):
                    if r_email and r_pwd:
                        if len(r_pwd) < 6:
                            st.error("❌ Minimum 6 characters required.")
                        elif reset_user_password(r_email, r_pwd):
                            st.success("✅ Password updated!")
                        else:
                            st.error("❌ Email not found.")

        with tab_signup:
            new_email = st.text_input("Email", key="s_email")
            new_pwd = st.text_input("Password", type="password", key="s_pwd")
            new_role = st.selectbox("Request Role", ["Patient", "Staff"]) 
            
            if st.button("Register Account", use_container_width=True):
                if not new_email or not new_pwd:
                    st.warning("⚠️ All fields required.")
                elif not is_valid_email(new_email):
                    st.error("❌ Invalid email.")
                elif len(new_pwd) < 6:
                    st.error("❌ Password too short.")
                else:
                    # Pass new_email to add_user (matches user_email in database.py)
                    if add_user(new_email, new_pwd, new_role):
                        st.success("🎉 Created! Switch to Login tab.")
                    else:
                        st.error("❌ User already exists.")
        
        st.divider()
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()

# --- ADMIN SETUP TOOL ---
SETUP_KEY = os.getenv("ADMIN_SETUP_KEY")

def admin_setup_tool():
    if SETUP_KEY and st.query_params.get("setup") == SETUP_KEY:
        if not admin_exists():
            st.warning("🛠️ Admin Setup Mode Active")
            with st.expander("Create Initial Admin Account", expanded=True):
                adm_email = st.text_input("Admin Email")
                adm_pwd = st.text_input("Admin Password", type="password")
                if st.button("Generate System Admin"):
                    if adm_email and adm_pwd:
                        if add_user(adm_email, adm_pwd, "Admin"):
                            st.success("Admin created!")
                            st.query_params.clear()
                            st.rerun()
        else:
            st.query_params.clear()

admin_setup_tool()

def main_app():
    role = st.session_state.user_role
    user = st.session_state.username
    
    with st.sidebar:
        st.markdown(f"### 👤 {user}")
        st.caption(f"Access Level: {role}")
        st.divider()
        
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            st.session_state.current_session = create_new_session(user)
            st.rerun()
        
        st.write("📂 **Recent Chats**")
        sessions = get_user_sessions(user)
        
        for s_id in sessions:
            cols = st.columns([0.8, 0.2])
            is_active = "▶️ " if s_id == st.session_state.current_session else "💬 "
            if cols[0].button(f"{is_active}{s_id}", key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session = s_id
                st.rerun()
            
            if cols[1].button("🗑️", key=f"del_{s_id}"):
                delete_session(s_id)
                # Corrected logic to reset current session if deleted
                if st.session_state.current_session == s_id:
                    remaining = get_user_sessions(user)
                    st.session_state.current_session = remaining[0] if remaining else create_new_session(user)
                st.rerun()

        if sessions:
            st.divider()
            if st.button("🧨 Clear All History", use_container_width=True):
                clear_chat_history(user) # Corrected: matches user_email in database.py
                st.session_state.current_session = create_new_session(user)
                st.rerun()

        if role == "Admin":
            st.divider()
            st.subheader("⚙️ Admin: Indexing")
            file = st.file_uploader("Upload Hospital PDF", type="pdf")
            if file and st.button("Index Knowledge"):
                with st.status("Processing PDF...") as status:
                    path = os.path.join("data", file.name)
                    if not os.path.exists("data"): os.makedirs("data")
                    with open(path, "wb") as f: f.write(file.getbuffer())
                    process_pdf(path)
                    st.cache_resource.clear()
                    status.update(label="Index Complete!", state="complete")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "landing"
            st.rerun()

    # --- MAIN CHAT ---
    st.title(f"🩺 Knowledge Assistant")
    st.caption(f"Active Session: {st.session_state.current_session}")
    
    qa_chain = build_qa_chain()
    history = get_chat_history(st.session_state.current_session)
    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if query := st.chat_input("Ask a question..."):
        with st.chat_message("user"):
            st.write(query)
        save_message(st.session_state.current_session, user, "user", query)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing documents..."):
                res = role_based_query(qa_chain, query, role)
                ans = res["result"]
                st.write(ans)
                save_message(st.session_state.current_session, user, "assistant", ans)
                st.rerun()

if st.session_state.logged_in:
    main_app()
elif st.session_state.page == "auth":
    auth_page()
else:
    landing_page()