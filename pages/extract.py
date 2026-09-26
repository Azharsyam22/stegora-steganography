"""
Stegora - Extract Page
Extract hidden message from stego image
"""
import streamlit as st
from stegora.ui.components import (
    page_title, section_header, muted_text,
    credentials_input, footer
)


def show():
    """Extract page UI"""
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
    
    if stego_file:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(stego_file, caption="Stego Image", use_container_width=True)
        
        with col2:
            st.success(f"Loaded: **{stego_file.name}**")
            muted_text("Image ready for extraction")
    
    # Step 2: Credentials
    password, stego_key = credentials_input("extract")
    
    # Step 3: Extract
    section_header("3. Extract Message")
    
    # Show warnings if missing inputs
    warnings = []
    if not stego_file:
        warnings.append("Upload a stego image")
    if not password:
        warnings.append("Enter password")
    if not stego_key:
        warnings.append("Enter stego-key")
    
    if warnings:
        st.warning(f"Required: {', '.join(warnings)}")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        extract_btn = st.button(
            "Extract Message",
            type="primary",
            use_container_width=True,
            disabled=bool(warnings)
        )
    
    if extract_btn:
        st.info("Extract functionality not yet implemented (requires T11)")
        muted_text("Next task: LSB extraction module")
        
        # Show what will happen
        with st.expander("Extraction Process", expanded=True):
            st.markdown("""
            **Process Steps:**
            
            1. Load stego image
            2. Generate positions from stego-key
            3. Read LSB bits from positions
            4. Parse STGR container header
            5. Derive AES key from password
            6. Decrypt payload
            7. Return original message/file
            """)
    
    footer()
