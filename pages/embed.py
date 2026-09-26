"""
Stegora - Embed Page
Hide text or file inside cover image
"""
import streamlit as st


def show():
    """Embed page UI"""
    st.title("📥 Embed Message")
    st.markdown("Hide text or file inside a cover image using LSB steganography.")
    
    # Cover image upload
    st.subheader("1. Upload Cover Image")
    cover_file = st.file_uploader(
        "Choose PNG or BMP image",
        type=["png", "bmp"],
        key="embed_cover"
    )
    
    if cover_file:
        st.success(f"✓ Loaded: {cover_file.name}")
        # TODO: Display image and calculate capacity
        st.info("⚠️ Capacity calculation not yet implemented")
    
    # Payload input
    st.subheader("2. Choose Payload")
    payload_type = st.radio(
        "Payload type",
        ["Text", "File"],
        horizontal=True
    )
    
    if payload_type == "Text":
        payload_text = st.text_area(
            "Enter secret message",
            placeholder="Your secret message here...",
            height=150
        )
    else:
        payload_file = st.file_uploader(
            "Choose file to hide",
            key="embed_payload_file"
        )
    
    # Credentials
    st.subheader("3. Security Credentials")
    col1, col2 = st.columns(2)
    
    with col1:
        password = st.text_input(
            "Password (for encryption)",
            type="password",
            help="Used to encrypt the payload with AES-256-GCM"
        )
    
    with col2:
        stego_key = st.text_input(
            "Stego-key (for positions)",
            type="password",
            help="Determines pixel positions for embedding"
        )
    
    # Embed button
    st.subheader("4. Embed")
    if st.button("🔒 Embed Message", type="primary", use_container_width=True):
        if not cover_file:
            st.error("❌ Please upload a cover image")
        elif not password or not stego_key:
            st.error("❌ Please provide both password and stego-key")
        else:
            st.warning("⚠️ Embed functionality not yet implemented")
            # TODO: Implement embed pipeline
    
    st.markdown("---")
    st.caption("Stegora - LSB Steganography with AES-256-GCM")
