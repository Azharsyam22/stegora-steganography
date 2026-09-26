"""
Stegora UI Components
Reusable UI elements for consistent design
"""
import streamlit as st
from typing import Optional


def section_header(text: str):
    """Display section header"""
    st.markdown(f'<div class="stegora-section">{text}</div>', unsafe_allow_html=True)


def card(content_func, **kwargs):
    """Wrap content in card-like container"""
    st.markdown('<div class="stegora-card">', unsafe_allow_html=True)
    content_func(**kwargs)
    st.markdown('</div>', unsafe_allow_html=True)


def metric_display(label: str, value: str, unit: str = ""):
    """Display metric in styled format"""
    full_value = f"{value} {unit}".strip()
    html = f"""
    <div class="stegora-metric">
        <div class="stegora-metric-label">{label}</div>
        <div class="stegora-metric-value">{full_value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def status_badge(text: str, status: str = "success"):
    """Display status badge
    
    Args:
        text: Badge text
        status: One of 'success', 'warning', 'error'
    """
    html = f'<span class="stegora-badge stegora-badge-{status}">{text}</span>'
    st.markdown(html, unsafe_allow_html=True)


def muted_text(text: str):
    """Display muted helper text"""
    st.markdown(f'<p class="stegora-muted">{text}</p>', unsafe_allow_html=True)


def page_title(title: str, description: str):
    """Display consistent page header without emoji"""
    st.title(title)
    muted_text(description)
    st.markdown("---")


def image_info_card(filename: str, format_type: str, dimensions: tuple, 
                    channels: int, capacity: Optional[int] = None):
    """Display image information card
    
    Args:
        filename: Image filename
        format_type: Image format (PNG, BMP, etc)
        dimensions: (width, height) tuple
        channels: Number of color channels
        capacity: Optional capacity in bytes
    """
    width, height = dimensions
    
    st.markdown('<div class="stegora-card">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_display("Format", format_type)
    
    with col2:
        metric_display("Dimensions", f"{width}×{height}", "px")
    
    with col3:
        metric_display("Channels", str(channels))
    
    with col4:
        if capacity is not None:
            if capacity >= 1024:
                cap_str = f"{capacity / 1024:.1f}"
                unit = "KB"
            else:
                cap_str = str(capacity)
                unit = "bytes"
            metric_display("Capacity", cap_str, unit)
        else:
            metric_display("Capacity", "—")
    
    st.markdown('</div>', unsafe_allow_html=True)


def credentials_input(key_prefix: str = ""):
    """Standard credentials input section
    
    Args:
        key_prefix: Prefix for input keys to avoid collision
    
    Returns:
        tuple: (password, stego_key)
    """
    section_header("Security Credentials")
    
    col1, col2 = st.columns(2)
    
    with col1:
        password = st.text_input(
            "Password",
            type="password",
            help="Used for AES-256-GCM encryption/decryption",
            key=f"{key_prefix}_password"
        )
    
    with col2:
        stego_key = st.text_input(
            "Stego-key",
            type="password",
            help="Determines pixel positions for embedding",
            key=f"{key_prefix}_stego_key"
        )
    
    return password, stego_key


def footer():
    """Display consistent footer"""
    st.markdown("---")
    st.caption("STEGORA · Professional Steganography Suite · LSB with AES-256-GCM")


def show_progress(message: str = "Processing..."):
    """Show premium progress indicator"""
    html = f"""
    <div style="text-align: center; margin: 2rem 0;">
        <div class="stegora-spinner"></div>
        <p class="stegora-muted" style="margin-top: 1rem;">{message}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def show_progress_bar(percent: int = 0, message: str = ""):
    """Show progress bar with percentage
    
    Args:
        percent: Progress percentage (0-100)
        message: Optional message to display
    """
    html = f"""
    <div class="stegora-progress">
        <div style="width: {percent}%; height: 100%; background: linear-gradient(90deg, #718E88 0%, #5FB98F 100%); transition: width 0.3s ease;"></div>
    </div>
    """
    if message:
        html += f'<p class="stegora-muted" style="text-align: center; margin-top: 0.5rem;">{message}</p>'
    st.markdown(html, unsafe_allow_html=True)



def info_card(label: str, value: str):
    """
    Display info as label-value pair
    
    Args:
        label: Label text
        value: Value text
    """
    st.markdown(f"**{label}:** {value}")


def error_message(title: str, message: str):
    """
    Display formatted error message
    
    Args:
        title: Error title
        message: Error description
    """
    st.error(f"**{title}**")
    st.markdown(message)


def success_message(message: str):
    """
    Display success message
    
    Args:
        message: Success text
    """
    st.success(f"✓ {message}")


def warning_list(items: list):
    """
    Display warning with list of items
    
    Args:
        items: List of warning strings
    """
    if items:
        st.warning(f"⚠️ Required: {', '.join(items)}")


def result_placeholder(title: str, description: str):
    """
    Display placeholder for future results
    
    Args:
        title: Result section title
        description: Description of what will appear
    """
    st.markdown(f"**{title}**")
    st.caption(description)
    st.markdown("*Result will appear here after implementation*")
