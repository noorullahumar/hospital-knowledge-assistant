import streamlit as st
import os
import time
import re
from database import * 
from ingest import process_pdf
from rag_pipeline import build_qa_chain, role_based_query
from style import apply_custom_css
from dotenv import load_dotenv
import random # Ensure this is at the top of your app.py
from mailer import send_otp_email # Ensure mailer.py exists with your SMTP logic

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

import time
import random
import streamlit as st
from mailer import send_otp_email

def auth_page():
    """Handles User Login, Registration, and Secure OTP Password Reset with Rate Limiting."""
    st.markdown("<h2 style='text-align: center;'>Portal Authentication</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    
    with col:
        tab_login, tab_signup = st.tabs(["Login", "Create Account"])
        
        # --- LOGIN TAB ---
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
                            
                            sessions = get_user_sessions(email)
                            st.session_state.current_session = sessions[0] if sessions else create_new_session(email)
                            
                            st.toast(f"Welcome back, {email}!", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials.")

            # --- SECURE OTP PASSWORD RESET WITH TIMER ---
            with st.expander("Forgot Password?"):
                # Initialize session states
                if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
                if "generated_otp" not in st.session_state: st.session_state.generated_otp = None
                if "reset_target_email" not in st.session_state: st.session_state.reset_target_email = None
                if "last_otp_time" not in st.session_state: st.session_state.last_otp_time = 0
                
                cooldown = 60  # Cooldown period in seconds

                # STEP 1: Request Email & Send OTP
                if not st.session_state.otp_sent:
                    st.caption("Step 1: Verify your registered email.")
                    email_to_verify = st.text_input("Enter Email", key="otp_email")
                    
                    elapsed = time.time() - st.session_state.last_otp_time
                    wait_time = int(cooldown - elapsed)

                    if wait_time > 0:
                        st.button(f"⏳ Resend Code in {wait_time}s", disabled=True, use_container_width=True)
                        time.sleep(1)
                        st.rerun()
                    else:
                        if st.button("Send Verification Code", use_container_width=True):
                            if user_exists(email_to_verify):
                                otp = random.randint(100000, 999999)
                                with st.spinner("Sending email..."):
                                    if send_otp_email(email_to_verify, otp):
                                        st.session_state.generated_otp = otp
                                        st.session_state.reset_target_email = email_to_verify
                                        st.session_state.otp_sent = True
                                        st.session_state.last_otp_time = time.time()
                                        st.success(f"📩 Code sent to {email_to_verify}!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to send email. Check .env settings.")
                            else:
                                st.error("❌ This email is not registered.")

                # STEP 2: Verify OTP & Update Password
                else:
                    st.caption(f"Step 2: Enter the code sent to {st.session_state.reset_target_email}")
                    user_otp = st.text_input("Enter 6-Digit Code", key="user_otp")
                    new_reset_pwd = st.text_input("New Password", type="password", key="new_reset_pwd")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("Verify & Reset", use_container_width=True):
                        if str(user_otp) == str(st.session_state.generated_otp):
                            if len(new_reset_pwd) >= 6:
                                if reset_user_password(st.session_state.reset_target_email, new_reset_pwd):
                                    st.success("✅ Password reset! Please login.")
                                    st.session_state.otp_sent = False 
                                    st.session_state.generated_otp = None
                                else:
                                    st.error("Database update failed.")
                            else:
                                st.error("Password must be at least 6 characters.")
                        else:
                            st.error("❌ Invalid verification code.")
                    
                    if c2.button("Cancel", use_container_width=True):
                        st.session_state.otp_sent = False
                        st.rerun()

                    # RESEND LOGIC INSIDE STEP 2
                    st.divider()
                    elapsed_step2 = time.time() - st.session_state.last_otp_time
                    wait_step2 = int(cooldown - elapsed_step2)

                    if wait_step2 > 0:
                        st.caption(f"Didn't get the code? You can resend in {wait_step2} seconds.")
                    else:
                        if st.button("📩 Resend Verification Code", key="resend_inner", use_container_width=True):
                            otp = random.randint(100000, 999999)
                            if send_otp_email(st.session_state.reset_target_email, otp):
                                st.session_state.generated_otp = otp
                                st.session_state.last_otp_time = time.time()
                                st.toast("New code sent!", icon="📧")
                                st.rerun()

        # --- SIGNUP TAB ---
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
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    if add_user(new_email, new_pwd, new_role):
                        st.success("🎉 Account Created! Please switch to Login tab.")
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