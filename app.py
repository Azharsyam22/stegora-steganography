"""
Stegora - Steganography Application
Main entry point for Streamlit multipage app
"""
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Stegora | Aplikasi Steganografi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom theme
from frontend.ui.theme import apply_theme
apply_theme()

# Import pages
from frontend.pages import embed, extract, analyze, about

# Define pages
pages = [
    st.Page(embed.show, title="Sisipkan", url_path="embed"),
    st.Page(extract.show, title="Ekstrak", url_path="extract"),
    st.Page(analyze.show, title="Analisis", url_path="analyze"),
    st.Page(about.show, title="Tentang", url_path="about"),
]

# Navigation
pg = st.navigation(pages)

# Run selected page first
pg.run()

# Then add sidebar content (after pg.run())
st.sidebar.markdown("### STEGORA")
st.sidebar.caption("Perangkat Steganografi")

# Navigation Guide
st.sidebar.caption("**NAVIGASI**")
st.sidebar.markdown("""
**Sisipkan** — Sembunyikan pesan di dalam citra  
**Ekstrak** — Pulihkan pesan tersembunyi  
**Analisis** — Alat steganalisis  
**Tentang** — Informasi sistem
""")

st.sidebar.markdown("---")

# Team info
with st.sidebar.expander("TIM", expanded=False):
    st.markdown("""
    **Azhar** · 247006111168  
    UI/UX & Integrasi
    
    **Naufal** · 247006111158  
    Inti Steganografi
    
    **Hana** · 247006111170  
    Kriptografi & Analisis
    """)

# Technical Info
with st.sidebar.expander("TEKNOLOGI", expanded=False):
    st.markdown("""
    **Teknologi Keamanan**
    - Enkripsi AES-256-GCM
    - Derivasi kunci PBKDF2
    - Steganografi LSB
    
    **Platform**
    - Python 3.11
    - Kerangka kerja Streamlit
    - Pillow (Pemrosesan Citra)
    
    **Institusi**  
    Universitas Siliwangi  
    Keamanan Informasi
    """)
