"""
Stegora - Embed Page
Hide text or file inside cover image using LSB steganography
"""
import streamlit as st
from stegora.ui.components import (
    page_title, section_header, muted_text, footer
)
from stegora.image.io import validate_and_load_cover_image, ImageValidationError
from stegora.stego.capacity import (
    calculate_raw_capacity, 
    calculate_usable_capacity,
    format_bytes
)


def show():
    """Embed page UI with image upload and validation"""
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
        try:
            # Read file bytes
            cover_bytes = cover_file.read()
            
            # Validate and load image
            image, metadata = validate_and_load_cover_image(cover_bytes)
            
            # Calculate capacity
            raw_capacity = calculate_raw_capacity(
                metadata['width'], 
                metadata['height']
            )
            usable_capacity = calculate_usable_capacity(
                metadata['width'], 
                metadata['height'],
                container_overhead=64
            )
            
            # Store in session state
            st.session_state.cover_image = image
            st.session_state.cover_metadata = metadata
            st.session_state.cover_capacity = usable_capacity
            
            # Display image and metadata
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(image, caption="Cover Image", use_container_width=True)
            
            with col2:
                st.success(f"✓ Loaded: **{cover_file.name}**")
                
                # Image info
                st.markdown("**Image Information**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Format", metadata['format'])
                    st.metric("Mode", metadata['mode'])
                with col_b:
                    st.metric("Width", f"{metadata['width']} px")
                    st.metric("Height", f"{metadata['height']} px")
                
                if metadata['has_alpha']:
                    st.caption("⚠️ Alpha channel will be preserved (not used for embedding)")
                
                # Capacity info
                st.markdown("**Steganography Capacity**")
                col_c, col_d = st.columns(2)
                with col_c:
                    st.metric("Total Pixels", f"{metadata['total_pixels']:,}")
                    st.metric("Raw Capacity", format_bytes(raw_capacity['total_bytes']))
                with col_d:
                    st.metric("Usable Capacity", format_bytes(usable_capacity['usable_capacity_bytes']))
                    st.metric("Efficiency", f"{usable_capacity['efficiency_percent']:.1f}%")
                
                muted_text(f"Using 1-bit RGB LSB: 3 bits per pixel")
            
        except ImageValidationError as e:
            st.error(f"**Validation Error:** {str(e)}")
            st.session_state.cover_image = None
            return
        except Exception as e:
            st.error(f"**Unexpected Error:** {str(e)}")
            st.session_state.cover_image = None
            return
    
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
            help="Text will be encrypted before embedding",
            key="secret_text"
        )
        if payload_text:
            payload_size = len(payload_text.encode('utf-8'))
            st.caption(f"Message size: **{format_bytes(payload_size)}**")
            
            # Check capacity if cover loaded
            if hasattr(st.session_state, 'cover_capacity') and st.session_state.cover_capacity:
                available = st.session_state.cover_capacity['usable_capacity_bytes']
                required = payload_size + 16  # +16 for AES-GCM tag
                
                if required > available:
                    st.error(f"⚠️ Payload too large! Required: {format_bytes(required)}, Available: {format_bytes(available)}")
                else:
                    utilization = (required / available * 100) if available > 0 else 0
                    st.success(f"✓ Payload fits ({utilization:.1f}% capacity utilization)")
    else:
        payload_file = st.file_uploader(
            "Choose file to hide",
            key="embed_payload_file",
            help="Small files work best (< 100 KB)"
        )
        if payload_file:
            payload_size = payload_file.size
            st.caption(f"File: **{payload_file.name}** — {format_bytes(payload_size)}")
            
            # Check capacity if cover loaded
            if hasattr(st.session_state, 'cover_capacity') and st.session_state.cover_capacity:
                available = st.session_state.cover_capacity['usable_capacity_bytes']
                required = payload_size + 16  # +16 for AES-GCM tag
                
                if required > available:
                    st.error(f"⚠️ File too large! Required: {format_bytes(required)}, Available: {format_bytes(available)}")
                else:
                    utilization = (required / available * 100) if available > 0 else 0
                    st.success(f"✓ File fits ({utilization:.1f}% capacity utilization)")
    
    # Step 3: Credentials
    section_header("3. Security Credentials")
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input(
            "Password",
            type="password",
            key="embed_password",
            help="AES-256-GCM encryption password"
        )
    with col2:
        stego_key = st.text_input(
            "Stego-key",
            type="password",
            key="embed_stego_key",
            help="Deterministic position seed"
        )
    
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
        st.info("Embed functionality not yet implemented (requires T07-T14)")
        muted_text("Next tasks: Container, PRNG, PBKDF2, AES-GCM, LSB embedding")
    
    footer()
