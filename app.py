# Streamlit library for building interactive web apps
import streamlit as st

# Import RAG pipeline functions
from rag_pipeline import build_qa_chain, role_based_query


# ================== PAGE CONFIG ==================
# Configure the Streamlit page (title, icon, layout)
st.set_page_config(
    page_title="Hospital Knowledge Assistant",
    page_icon="🩺",
    layout="wide"
)


# ================== STYLES ==================
# Custom CSS for chat bubbles and role badge
st.markdown("""
<style>
.chat-bubble-user {
    background-color: #e6f0ff;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    color: black;
}

.chat-bubble-assistant {
    background-color: #f4f6f8;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    color: black;
}

.role-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    background-color: #0d6efd;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# ================== LOAD QA ==================
# Cache the QA chain so it is built only once
@st.cache_resource
def load_qa():
    return build_qa_chain()

# Initialize the QA chain
qa_chain = load_qa()


# ================== SIDEBAR ==================
# Sidebar content (role selection + guidelines)
with st.sidebar:
    st.markdown("## 🏥 Hospital Assistant")
    st.caption("Secure • AI-Powered • Reliable")

    # Role selector (used for access control in RAG)
    role = st.radio(
        "👤 Select your role",
        ["Patient", "Hospital Staff"]
    )

    st.markdown("---")
    st.markdown("### ℹ️ Guidelines")
    st.markdown("""
    - Ask **clear medical or policy questions**
    - Not a replacement for a doctor
    - Data sourced from hospital documents
    """)


# ================== HEADER ==================
# Main page title with dynamic role badge
st.markdown(
    f"### 🩺 Hospital Knowledge Assistant "
    f"<span class='role-badge'>{role}</span>",
    unsafe_allow_html=True
)

st.caption("Ask questions about hospital policies, procedures, and services.")


# ================== CHAT STATE ==================
# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# ================== CHAT DISPLAY ==================
# Render all previous chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Display user messages
        with st.chat_message("user"):
            st.markdown(
                f"<div class='chat-bubble-user'>{msg['content']}</div>",
                unsafe_allow_html=True
            )
    else:
        # Display assistant messages
        with st.chat_message("assistant"):
            st.markdown(
                f"<div class='chat-bubble-assistant'>{msg['content']}</div>",
                unsafe_allow_html=True
            )

            # Show document sources if available
            if "sources" in msg:
                with st.expander("📚 Sources"):
                    for doc in msg["sources"]:
                        st.write(
                            f"📄 {doc.metadata.get('source')} — "
                            f"Page {doc.metadata.get('page', 'N/A')}"
                        )


# ================== CHAT INPUT ==================
# Input box for user questions
query = st.chat_input("Ask your hospital-related question...")


if query:
    # ---- USER MESSAGE ----
    # Save user message to session state
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(
            f"<div class='chat-bubble-user'>{query}</div>",
            unsafe_allow_html=True
        )

    # ---- ASSISTANT RESPONSE ----
    with st.chat_message("assistant"):
        # Show loading spinner while searching documents
        with st.spinner("🔍 Searching hospital knowledge..."):
            result = role_based_query(
                qa_chain,
                query,
                role=role
            )

        # Extract answer and source documents
        answer = result["result"]
        sources = result["source_documents"]

        # Display assistant answer
        st.markdown(
            f"<div class='chat-bubble-assistant'>{answer}</div>",
            unsafe_allow_html=True
        )

        # Display sources used in the response
        with st.expander("📚 Sources"):
            for doc in sources:
                st.write(
                    f"📄 {doc.metadata.get('source')} — "
                    f"Page {doc.metadata.get('page', 'N/A')}"
                )

    # ---- SAVE STATE ----
    # Save assistant response and sources
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
