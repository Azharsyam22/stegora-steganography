"""
Stegora - Steganography Application
Main entry point for Streamlit multipage app
"""
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Stegora | Professional Steganography",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom theme
from frontend.ui.theme import apply_theme
apply_theme()

# Import pages
from frontend.pages import embed, extract, analyze

# Define pages
pages = [
    st.Page(embed.show, title="Embed", url_path="embed"),
    st.Page(extract.show, title="Extract", url_path="extract"),
    st.Page(analyze.show, title="Analyze", url_path="analyze"),
]

# Navigation
pg = st.navigation(pages)

# Run selected page first
pg.run()

# Then add sidebar content (after pg.run())
st.sidebar.markdown("### STEGORA")
st.sidebar.caption("Professional Steganography Suite")

# Navigation Guide
st.sidebar.caption("**NAVIGATION**")
st.sidebar.markdown("""
**Embed** — Hide messages in images  
**Extract** — Recover hidden messages  
**Analyze** — Steganalysis tools
""")

st.sidebar.markdown("---")

# Team info
with st.sidebar.expander("TEAM", expanded=False):
    st.markdown("""
    **Azhar** · 247006111168  
    UI/UX & Integration
    
    **Naufal** · 247006111158  
    Steganography Core
    
    **Hana** · 247006111170  
    Cryptography & Analysis
    """)

# Technical Info
with st.sidebar.expander("TECHNOLOGY", expanded=False):
    st.markdown("""
    **Security Stack**
    - AES-256-GCM Encryption
    - PBKDF2 Key Derivation
    - LSB Steganography
    
    **Platform**
    - Python 3.11
    - Streamlit Framework
    - Pillow (Image Processing)
    
    **Institution**  
    Universitas Siliwangi  
    Keamanan Informasi
    """)
