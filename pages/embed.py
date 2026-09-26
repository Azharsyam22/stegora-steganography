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
    check_payload_capacity,
    format_bytes
)


def show():
    """Embed page UI with complete workflow"""
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
    
    cover_valid = False
    payload_size = 0
    
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
            cover_valid = True
            
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
            cover_valid = False
        except Exception as e:
            st.error(f"**Unexpected Error:** {str(e)}")
            st.session_state.cover_image = None
            cover_valid = False
    
    # Step 2: Payload
    section_header("2. Choose Payload")
    
    payload_type = st.radio(
        "Payload type",
        ["Text", "File"],
        horizontal=True,
        help="Select whether to hide text or a file"
    )
    
    payload_text = None
    payload_file = None
    payload_fits = False
    
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
            if cover_valid and hasattr(st.session_state, 'cover_capacity'):
                capacity_check = check_payload_capacity(
                    st.session_state.cover_metadata['width'],
                    st.session_state.cover_metadata['height'],
                    payload_size,
                    container_overhead=64
                )
                
                if capacity_check['fits']:
                    st.success(f"✓ Payload fits ({capacity_check['utilization_percent']:.1f}% capacity utilization)")
                    payload_fits = True
                else:
                    st.error(f"⚠️ Payload too large! Required: {format_bytes(capacity_check['required_bytes'])}, Available: {format_bytes(capacity_check['available_bytes'])}")
                    payload_fits = False
    else:
        payload_file = st.file_uploader(
            "Choose file to hide",
            key="embed_payload_file",
            help="Small files work best"
        )
        if payload_file:
            payload_size = payload_file.size
            st.caption(f"File: **{payload_file.name}** — {format_bytes(payload_size)}")
            
            # Check capacity if cover loaded
            if cover_valid and hasattr(st.session_state, 'cover_capacity'):
                capacity_check = check_payload_capacity(
                    st.session_state.cover_metadata['width'],
                    st.session_state.cover_metadata['height'],
                    payload_size,
                    container_overhead=64
                )
                
                if capacity_check['fits']:
                    st.success(f"✓ File fits ({capacity_check['utilization_percent']:.1f}% capacity utilization)")
                    payload_fits = True
                else:
                    st.error(f"⚠️ File too large! Required: {format_bytes(capacity_check['required_bytes'])}, Available: {format_bytes(capacity_check['available_bytes'])}")
                    payload_fits = False
    
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
    
    # Validation
    can_embed = True
    warnings = []
    
    if not cover_valid:
        warnings.append("Upload a valid cover image")
        can_embed = False
    if payload_type == "Text" and not payload_text:
        warnings.append("Enter text message")
        can_embed = False
    elif payload_type == "File" and not payload_file:
        warnings.append("Upload payload file")
        can_embed = False
    if not password:
        warnings.append("Enter password")
        can_embed = False
    if not stego_key:
        warnings.append("Enter stego-key")
        can_embed = False
    if cover_valid and payload_size > 0 and not payload_fits:
        warnings.append("Payload too large for this image")
        can_embed = False
    
    if warnings:
        st.warning(f"⚠️ Required: {', '.join(warnings)}")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        embed_btn = st.button(
            "🔒 Embed Message",
            type="primary",
            use_container_width=True,
            disabled=not can_embed
        )
    
    # Process embedding (placeholder for now)
    if embed_btn and can_embed:
        with st.spinner("Embedding message..."):
            # This will be replaced with actual embedding in T05
            st.info("💡 Embed functionality not yet implemented (requires T07-T14)")
            muted_text("Next tasks: Container (T08), PRNG (T09), PBKDF2 (T13), AES-GCM (T14), LSB embedding (T10)")
            
            # Show what will happen
            with st.expander("📋 Embedding Process Preview", expanded=True):
                st.markdown("""
                **When implemented, the process will:**
                
                1. **Prepare payload**
                   - Text → UTF-8 bytes
                   - File → raw bytes
                
                2. **Encrypt payload**
                   - Derive key from password using PBKDF2 (600,000 iterations)
                   - Generate random salt (16 bytes)
                   - Generate random IV (12 bytes)
                   - Encrypt with AES-256-GCM
                
                3. **Build container**
                   - STGR header (magic, version, flags)
                   - Metadata (salt, IV, filename, MIME)
                   - Encrypted payload
                
                4. **Generate positions**
                   - SHA-256 hash of stego-key
                   - Deterministic PRNG sequence
                   - Unique RGB channel positions
                
                5. **Embed in LSB**
                   - For each bit in container
                   - Set LSB of selected RGB channel
                   - Preserve alpha channel
                
                6. **Output stego image**
                   - Same dimensions as cover
                   - Visually identical
                   - Contains hidden data
                """)
    
    # Step 5: Result (placeholder for now)
    if embed_btn and can_embed:
        section_header("5. Result")
        
        st.info("🎨 Result display will be implemented in T05 (Integration)")
        
        # Placeholder for result
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Cover Image**")
            if cover_valid:
                st.image(st.session_state.cover_image, use_container_width=True)
        
        with col2:
            st.markdown("**Stego Image**")
            st.markdown("*Stego image will appear here after embedding*")
            st.caption("Visually identical to cover, but contains hidden data")
        
        # Metrics placeholder
        st.markdown("**Quality Metrics**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("MSE", "—", help="Mean Squared Error")
        with col_b:
            st.metric("PSNR", "— dB", help="Peak Signal-to-Noise Ratio")
        with col_c:
            st.metric("Modified Pixels", "—", help="Pixels with LSB changed")
        
        # Download button (disabled for now)
        st.download_button(
            label="⬇️ Download Stego Image",
            data=b"",  # Will be actual image bytes in T05
            file_name="stego_image.png",
            mime="image/png",
            disabled=True,
            help="Available after embedding is implemented"
        )
    
    footer()
