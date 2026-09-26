"""
Stegora UI Theme
Premium design system
"""
import streamlit as st

# Color palette
COLORS = {
    "background": "#F7F8F6",
    "surface": "#FFFFFF",
    "text": "#26343B",
    "muted": "#6C777C",
    "accent": "#718E88",
    "accent_soft": "#E5EEEC",
    "border": "#D9E0DE",
    "success": "#4A9B7F",
    "warning": "#D4A574",
    "error": "#C7726B",
}

# Custom CSS
CUSTOM_CSS = """
<style>
.main { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
.stegora-card {
    background: #FFFFFF; border: 1px solid #D9E0DE; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); transition: all 0.3s ease;
}
.stegora-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); }
.stegora-section {
    color: #26343B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;
    margin-top: 2rem; margin-bottom: 1rem; border-bottom: 2px solid #D9E0DE; padding-bottom: 0.5rem;
}
.stegora-muted { color: #6C777C; font-size: 0.875rem; line-height: 1.6; }
.stegora-metric {
    background: linear-gradient(135deg, #F7F8F6 0%, #FFFFFF 100%); border: 1px solid #D9E0DE; border-radius: 8px;
    padding: 1.25rem; text-align: center; transition: all 0.3s ease;
}
.stegora-metric:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06); }
.stegora-metric-label { color: #6C777C; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; font-weight: 600; }
.stegora-metric-value { color: #26343B; font-size: 1.75rem; font-weight: 700; }
[data-testid="stFileUploader"] {
    border: 2px dashed #D9E0DE; border-radius: 10px; padding: 2rem;
    background: linear-gradient(135deg, #FAFBFA 0%, #FFFFFF 100%); transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: #718E88; background: #F7F8F6; transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(113, 142, 136, 0.1);
}
.stButton button {
    border-radius: 8px; font-weight: 600; letter-spacing: 0.02em; transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.stButton button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(113, 142, 136, 0.25); }
input, textarea, select { transition: all 0.3s ease; border-radius: 6px !important; }
input:focus, textarea:focus, select:focus {
    border-color: #718E88 !important; box-shadow: 0 0 0 3px rgba(113, 142, 136, 0.1) !important;
}
[data-testid="stSidebar"] { background: #FAFBFA; border-right: 1px solid #E5E7E6; }
.stAlert { border-radius: 8px; border-left-width: 4px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); }
img { border-radius: 8px; transition: all 0.3s ease; }
img:hover { transform: scale(1.02); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
html { scroll-behavior: smooth; }
footer { visibility: hidden; }
h1, h2, h3, h4, h5, h6 { font-weight: 700; letter-spacing: -0.02em; }
</style>
"""

def apply_theme():
    """Apply custom theme CSS"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_color(name: str) -> str:
    """Get color from palette"""
    return COLORS.get(name, "#000000")
