"""
Stegora - Extract Page
Extract hidden message from stego image
"""
import streamlit as st


def show():
    """Extract page UI"""
    st.title("📤 Extract Message")
    st.markdown("Extract hidden message from a stego image.")
    
    # Stego image upload
    st.subheader("1. Upload Stego Image")
    stego_file = st.file_uploader(
        "Choose PNG or BMP image with hidden message",
        type=["png", "bmp"],
        key="extract_stego"
    )
    
    if stego_file:
        st.success(f"✓ Loaded: {stego_file.name}")
        # TODO: Display image
    
    # Credentials
    st.subheader("2. Security Credentials")
    col1, col2 = st.columns(2)
    
    with col1:
        password = st.text_input(
            "Password (for decryption)",
            type="password",
            help="Same password used during embedding",
            key="extract_password"
        )
    
    with col2:
        stego_key = st.text_input(
            "Stego-key (for positions)",
            type="password",
            help="Same stego-key used during embedding",
            key="extract_stego_key"
        )
    
    # Extract button
    st.subheader("3. Extract")
    if st.button("🔓 Extract Message", type="primary", use_container_width=True):
        if not stego_file:
            st.error("❌ Please upload a stego image")
        elif not password or not stego_key:
            st.error("❌ Please provide both password and stego-key")
        else:
            st.warning("⚠️ Extract functionality not yet implemented")
            # TODO: Implement extract pipeline
    
    st.markdown("---")
    st.caption("Stegora - LSB Steganography with AES-256-GCM")
