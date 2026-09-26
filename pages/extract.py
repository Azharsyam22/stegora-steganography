"""
Stegora - Extract Page
Extract hidden message from stego image
"""
import streamlit as st
from stegora.ui.components import (
    page_title, section_header, muted_text, footer
)
from stegora.image.io import validate_and_load_cover_image, ImageValidationError
from stegora.stego.capacity import format_bytes


def show():
    """Extract page UI with complete workflow"""
    page_title(
        "Extract Message",
        "Extract hidden message from a stego image"
    )
    
    # Step 1: Stego image
    section_header("1. Upload Stego Image")
    stego_file = st.file_uploader(
        "Choose PNG or BMP image with hidden message",
        type=["png", "bmp"],
        key="extract_stego",
        help="Select the image containing the hidden message"
    )
    
    stego_valid = False
    
    if stego_file:
        try:
            # Read and validate
            stego_bytes = stego_file.read()
            image, metadata = validate_and_load_cover_image(stego_bytes)
            
            # Store in session state
            st.session_state.stego_image = image
            st.session_state.stego_metadata = metadata
            stego_valid = True
            
            # Display
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(image, caption="Stego Image", use_container_width=True)
            
            with col2:
                st.success(f"✓ Loaded: **{stego_file.name}**")
                
                # Image info
                st.markdown("**Image Information**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Format", metadata['format'])
                    st.metric("Mode", metadata['mode'])
                with col_b:
                    st.metric("Width", f"{metadata['width']} px")
                    st.metric("Height", f"{metadata['height']} px")
                
                muted_text("Image ready for extraction")
                
        except ImageValidationError as e:
            st.error(f"**Validation Error:** {str(e)}")
            stego_valid = False
        except Exception as e:
            st.error(f"**Unexpected Error:** {str(e)}")
            stego_valid = False
    
    # Step 2: Credentials
    section_header("2. Security Credentials")
    
    st.markdown("Enter the same credentials used during embedding:")
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input(
            "Password",
            type="password",
            key="extract_password",
            help="Same password used for encryption"
        )
    with col2:
        stego_key = st.text_input(
            "Stego-key",
            type="password",
            key="extract_stego_key",
            help="Same stego-key used for positioning"
        )
    
    # Step 3: Extract
    section_header("3. Extract Message")
    
    # Validation
    can_extract = True
    warnings = []
    
    if not stego_valid:
        warnings.append("Upload a valid stego image")
        can_extract = False
    if not password:
        warnings.append("Enter password")
        can_extract = False
    if not stego_key:
        warnings.append("Enter stego-key")
        can_extract = False
    
    if warnings:
        st.warning(f"⚠️ Required: {', '.join(warnings)}")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        extract_btn = st.button(
            "🔓 Extract Message",
            type="primary",
            use_container_width=True,
            disabled=not can_extract
        )
    
    # Process extraction (placeholder for now)
    if extract_btn and can_extract:
        with st.spinner("Extracting message..."):
            # This will be replaced with actual extraction in T05
            st.info("💡 Extract functionality not yet implemented (requires T11)")
            muted_text("Next tasks: LSB extraction (T11), Container parsing (T08), PBKDF2 (T13), AES-GCM (T14)")
            
            # Show what will happen
            with st.expander("📋 Extraction Process Preview", expanded=True):
                st.markdown("""
                **When implemented, the process will:**
                
                1. **Generate positions**
                   - SHA-256 hash of stego-key
                   - Reproduce same PRNG sequence used in embedding
                   - Same RGB channel positions
                
                2. **Read LSB bits**
                   - Extract bits from determined positions
                   - Reconstruct byte stream
                
                3. **Parse container**
                   - Read STGR magic bytes (validate)
                   - Read header (version, flags, payload length)
                   - Extract metadata (salt, IV, filename, MIME)
                   - Extract encrypted payload
                
                4. **Decrypt payload**
                   - Derive key from password using PBKDF2
                   - Use stored salt from container
                   - Decrypt with AES-256-GCM using stored IV
                   - Verify authentication tag
                
                5. **Return result**
                   - Text message → display as string
                   - File → provide download
                
                **Error Handling:**
                - Wrong password → Decryption fails (authentication error)
                - Wrong stego-key → Wrong positions, garbled data
                - Corrupted image → Magic bytes mismatch
                - Truncated data → Length validation fails
                """)
    
    # Step 4: Result (placeholder for now)
    if extract_btn and can_extract:
        section_header("4. Extracted Content")
        
        st.info("📄 Extraction result will be displayed here after implementation")
        
        # Placeholder tabs for different result types
        tab1, tab2 = st.tabs(["📝 Text Message", "📎 File"])
        
        with tab1:
            st.markdown("**Recovered Text:**")
            st.text_area(
                "Message content",
                value="",
                height=200,
                disabled=True,
                placeholder="Extracted text will appear here...",
                label_visibility="collapsed"
            )
            
            # Copy button (disabled for now)
            st.button(
                "📋 Copy to Clipboard",
                disabled=True,
                help="Available after extraction is implemented"
            )
        
        with tab2:
            st.markdown("**Recovered File:**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Filename", "—")
                st.metric("MIME Type", "—")
            with col_b:
                st.metric("File Size", "—")
                st.metric("Status", "—")
            
            # Download button (disabled for now)
            st.download_button(
                label="⬇️ Download Recovered File",
                data=b"",  # Will be actual file bytes in T05
                file_name="recovered_file.bin",
                disabled=True,
                help="Available after extraction is implemented"
            )
        
        # Verification status
        st.markdown("**Verification**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Magic Bytes", "—", help="STGR header validation")
        with col2:
            st.metric("Auth Tag", "—", help="AES-GCM authentication")
        with col3:
            st.metric("Integrity", "—", help="Overall data integrity")
    
    # Help section
    with st.expander("ℹ️ Extraction Tips", expanded=False):
        st.markdown("""
        **For successful extraction:**
        
        1. **Use the correct stego image**
           - Must be the exact output from embedding
           - Do not re-save or modify the image
           - JPEG conversion will destroy hidden data
        
        2. **Use the exact same credentials**
           - Password must match exactly (case-sensitive)
           - Stego-key must match exactly
           - Wrong credentials = wrong/garbled output
        
        3. **Avoid image modification**
           - Do not crop, resize, or rotate
           - Do not apply filters or adjustments
           - Do not convert format (PNG ↔ BMP is safe if lossless)
        
        4. **Expected outcomes**
           - ✅ Correct credentials → Original message recovered
           - ❌ Wrong password → Authentication failure
           - ❌ Wrong stego-key → Garbled data or parse error
           - ❌ Modified image → Corrupted/partial data
        """)
    
    footer()
