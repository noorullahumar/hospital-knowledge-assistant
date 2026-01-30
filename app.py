import streamlit as st
import os
import time
import re
from database import * 
from ingest import process_pdf
from rag_pipeline import build_qa_chain, role_based_query
from style import apply_custom_css

# --- INITIALIZATION ---
# Initialize the SQLite database tables
init_db()

# Configure Streamlit page settings
st.set_page_config(page_title="Hospital AI Portal", page_icon="🏥", layout="wide")

# Apply custom CSS from style.py (handles colors, sidebar text contrast, and hero sections)
apply_custom_css()

# --- STATE MANAGEMENT ---
# These variables persist across user interactions (button clicks, inputs)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# --- HELPERS ---
def is_valid_email(email):
    """Regex helper to ensure registration emails are formatted correctly."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# --- UI PAGES ---

def landing_page():
    """Renders the initial welcome screen with feature cards."""
    st.markdown("""
        <div class='hero-section'>
            <h1>🏥 Hospital Intelligence Portal</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>
                Secure AI-powered knowledge retrieval for healthcare professionals and patients.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights using Streamlit info boxes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 🛡️ Secure\nRole-based access controls for data privacy.")
    with col2:
        st.info("### ⚡ Fast\nInstant answers from hospital policy PDFs.")
    with col3:
        st.info("### 📚 Verified\nEvery answer is backed by official documentation.")

    st.divider()
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button("🚀 Access Portal", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()

def auth_page():
    """Handles User Login and Registration logic."""
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
                            # Set session state variables upon successful auth
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.username = email
                            
                            # Load previous session history or start a fresh one
                            sessions = get_user_sessions(email)
                            st.session_state.current_session = sessions[0] if sessions else create_new_session(email)
                            
                            st.toast(f"Welcome back, {email}!", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials.")

        with tab_signup:
            new_email = st.text_input("Email", key="s_email")
            new_pwd = st.text_input("Password", type="password", key="s_pwd")
            new_role = st.selectbox("Role", ["Patient", "Staff", "Admin"])
            if st.button("Register Account", use_container_width=True):
                if not new_email or not new_pwd:
                    st.warning("⚠️ All fields are required.")
                elif not is_valid_email(new_email):
                    st.error("❌ Please enter a valid email address.")
                elif len(new_pwd) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    if add_user(new_email, new_pwd, new_role):
                        st.success("🎉 Account Created! Please switch to Login tab.")
                        st.toast("Registration Successful!")
                    else:
                        st.error("❌ User already exists.")
        
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()

def main_app():
    """The core Chat interface, Sidebar management, and Admin tools."""
    role = st.session_state.user_role
    user = st.session_state.username
    
    # --- SIDEBAR: Profile, History, and Admin ---
    with st.sidebar:
        st.markdown(f"### 👤 {user}")
        st.caption(f"Access Level: {role}")
        st.divider()
        
        # New Chat: Generates a unique ID and clears the current chat view
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            st.session_state.current_session = create_new_session(user)
            st.rerun()
        
        st.write("📂 **Recent Chats**")
        sessions = get_user_sessions(user)
        
        # Display list of past sessions with selection and deletion capability
        for s_id in sessions:
            cols = st.columns([0.8, 0.2])
            is_active = "▶️ " if s_id == st.session_state.current_session else "💬 "
            
            # Button to switch between chat threads
            if cols[0].button(f"{is_active}{s_id}", key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session = s_id
                st.rerun()
            
            # Individual session delete button
            if cols[1].button("🗑️", key=f"del_{s_id}", help="Delete this chat"):
                delete_session(s_id)
                if st.session_state.current_session == s_id:
                    remaining = get_user_sessions(user)
                    st.session_state.current_session = remaining[0] if remaining else create_new_session(user)
                st.rerun()

        # Global delete for user history
        if sessions:
            st.divider()
            if st.button("🧨 Clear All History", use_container_width=True):
                clear_chat_history(user)
                st.session_state.current_session = create_new_session(user)
                st.toast("All history cleared!")
                st.rerun()

        # Admin Only: PDF Upload and Ingestion logic
        if role == "Admin":
            st.divider()
            st.subheader("⚙️ Admin: Indexing")
            file = st.file_uploader("Upload Hospital PDF", type="pdf")
            if file and st.button("Index Knowledge"):
                with st.status("Processing PDF...") as status:
                    path = os.path.join("data", file.name)
                    if not os.path.exists("data"): os.makedirs("data")
                    with open(path, "wb") as f: f.write(file.getbuffer())
                    process_pdf(path) # Process PDF into JSON chunks
                    st.cache_resource.clear() # Clear AI model cache to recognize new data
                    status.update(label="Index Complete!", state="complete")
                st.toast("Knowledge Base Updated!")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "landing"
            st.session_state.current_session = None
            st.rerun()

    # --- MAIN CHAT INTERFACE ---
    st.title(f"🩺 Knowledge Assistant")
    st.caption(f"Active Session: {st.session_state.current_session}")
    
    # Initialize the AI Chain (Load documents -> Embeddings -> LLM)
    qa_chain = build_qa_chain()

    # Retrieve and display message history for the selected session
    history = get_chat_history(st.session_state.current_session)
    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input: Capture user question and generate AI response
    if query := st.chat_input("Ask a question about hospital records..."):
        with st.chat_message("user"):
            st.write(query)
        
        # Save user message to database immediately
        save_message(st.session_state.current_session, user, "user", query)
 
        with st.chat_message("assistant"):
            with st.spinner("Analyzing documents..."):
                # Execute AI query with role-based security prompts
                res = role_based_query(qa_chain, query, role)
                ans = res["result"]
                st.write(ans)
                # Save assistant response to database
                save_message(st.session_state.current_session, user, "assistant", ans)
                # Rerun to update the sidebar history list
                st.rerun()

# --- ROUTER ---
# Determines which page to show based on login status
if st.session_state.logged_in:
    main_app()
elif st.session_state.page == "auth":
    auth_page()
else:
    landing_page()