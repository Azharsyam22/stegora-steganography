"""
Stegora - Steganography Application
Main entry point for Streamlit multipage app
"""
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Stegora",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import pages
from pages import embed, extract, analyze

# Define pages
pages = [
    st.Page(embed.show, title="Embed", icon="📥", url_path="embed"),
    st.Page(extract.show, title="Extract", icon="📤", url_path="extract"),
    st.Page(analyze.show, title="Analyze", icon="📊", url_path="analyze"),
]

# Navigation
pg = st.navigation(pages)

# Header
st.sidebar.title("🔒 Stegora")
st.sidebar.markdown("**Steganography Application**")
st.sidebar.markdown("---")
st.sidebar.markdown("""
Modern LSB steganography with AES-256-GCM encryption.

**Team:**
- Azhar (247006111168)
- Naufal (247006111158)  
- Hana (247006111170)
""")

# Run selected page
pg.run()
