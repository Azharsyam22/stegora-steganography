"""
Stegora - Embed Page
Hide text or file inside cover image
"""
import streamlit as st
from stegora.ui.components import (
    page_title, section_header, muted_text,
    credentials_input, footer, status_badge
)


def show():
    """Embed page UI"""
    page_title(
        "Embed Message",
        "Hide text or file inside a cover image using LSB steganography"
    )
    
    # Step 1: Cover image
    section_header("1. Upload Cover Image")
    cover_file = st.file_uploader(
        "Choose PNG or BMP image",
        type=["png", "bmp"],
        key="embed_cover",
        help="Select a lossless image format for embedding"
    )
    
    if cover_file:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(cover_file, caption="Cover Image", use_container_width=True)
        
        with col2:
            st.success(f"Loaded: **{cover_file.name}**")
            st.info("Capacity calculation will be implemented in next task")
            muted_text("Image analysis requires stegora.image module")
    
    # Step 2: Payload
    section_header("2. Choose Payload")
    
    payload_type = st.radio(
        "Payload type",
        ["Text", "File"],
        horizontal=True,
        help="Select whether to hide text or a file"
    )
    
    payload_size = 0
    payload_text = None
    payload_file = None
    
    if payload_type == "Text":
        payload_text = st.text_area(
            "Enter secret message",
            placeholder="Your secret message here...",
            height=150,
            help="Text will be encrypted before embedding"
        )
        if payload_text:
            payload_size = len(payload_text.encode('utf-8'))
            muted_text(f"Text size: {payload_size} bytes")
    else:
        payload_file = st.file_uploader(
            "Choose file to hide",
            key="embed_payload_file",
            help="Small files work best (< 100 KB)"
        )
        if payload_file:
            payload_size = payload_file.size
            st.success(f"File: **{payload_file.name}** ({payload_size:,} bytes)")
    
    # Step 3: Credentials
    password, stego_key = credentials_input("embed")
    
    # Step 4: Embed
    section_header("4. Embed Message")
    
    # Show warnings if missing inputs
    warnings = []
    if not cover_file:
        warnings.append("Upload a cover image")
    if payload_type == "Text" and not payload_text:
        warnings.append("Enter text message")
    elif payload_type == "File" and not payload_file:
        warnings.append("Upload payload file")
    if not password:
        warnings.append("Enter password")
    if not stego_key:
        warnings.append("Enter stego-key")
    
    if warnings:
        st.warning(f"Required: {', '.join(warnings)}")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        embed_btn = st.button(
            "Embed Message",
            type="primary",
            use_container_width=True,
            disabled=bool(warnings)
        )
    
    if embed_btn:
        st.info("Embed functionality not yet implemented (requires T10-T14)")
        muted_text("Next tasks: Capacity calculator, Container, PRNG, AES-GCM, LSB embedding")
    
    footer()
