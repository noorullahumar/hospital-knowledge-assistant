import streamlit as st

def apply_custom_css():
    """
    Injects custom CSS to override default Streamlit styling.
    Focuses on branding the portal with a medical 'Hospital' aesthetic
    and fixing visibility issues in the sidebar.
    """
    st.markdown("""
    <style>
    /* 1. Main Background: Sets a light, clean workspace background */
    .main { 
        background-color: #f8f9fa; 
    }
    
    /* 2. Hero Section: The blue gradient header on the landing page */
    .hero-section {
        padding: 60px 20px;
        background: linear-gradient(135deg, #0062ff 0%, #003399 100%);
        color: white;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    }

    /* 3. Sidebar Container: Forces a clean white background with a subtle border */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }

    /* 4. Sidebar Text: Fixes visibility by making text dark slate against the white background */
    [data-testid="stSidebar"] .stText, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #1e293b !important; 
    }

    /* 5. Captions: Muted text for secondary info like 'Access Level' */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #64748b !important;
    }

    /* 6. Sidebar Buttons: Styled to look professional and clickable */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: #f1f5f9;
        color: #1e293b !important;
        border: 1px solid #cbd5e1;
        width: 100%;
        transition: 0.3s;
    }
    
    /* Hover state for buttons to provide user feedback */
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #e2e8f0;
        border-color: #0062ff;
        color: #0062ff !important;
    }

    /* 7. Admin Tools visibility: Ensures file uploader and status text are readable */
    [data-testid="stSidebar"] [data-testid="stStatusWidget"] div,
    [data-testid="stSidebar"] [data-testid="stStatusWidget"] label,
    [data-testid="stSidebar"] .stFileUploader label,
    [data-testid="stSidebar"] .stFileUploader p {
        color: #1e293b !important; 
    }
    </style>
    """, unsafe_allow_html=True)