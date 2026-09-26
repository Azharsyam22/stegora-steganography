"""
Stegora - Embed Page
Hide text or file inside cover image using LSB steganography
"""
import streamlit as st
import secrets
import io
from PIL import Image

from frontend.ui.components import (
    page_title, section_header, muted_text, footer
)
from backend.image.io import validate_and_load_cover_image, ImageValidationError, save_image
from backend.image.metrics import calculate_mse, calculate_psnr
from backend.stego.capacity import (
    calculate_raw_capacity, 
    calculate_usable_capacity,
    check_payload_capacity,
    format_bytes
)
from backend.crypto.pbkdf2 import derive_key
from backend.crypto.aes_gcm import encrypt
from backend.stego.container import create_container, calculate_container_size
from backend.stego.positions import generate_positions
from backend.stego.lsb import embed_lsb


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
    
    # Process embedding
    if embed_btn and can_embed:
        try:
            with st.spinner("Embedding message..."):
                # 1. Prepare payload
                if payload_type == "Text":
                    payload_bytes = payload_text.encode('utf-8')
                    filename = "message.txt"
                    mime_type = "text/plain"
                else:
                    payload_bytes = payload_file.read()
                    filename = payload_file.name
                    mime_type = payload_file.type or "application/octet-stream"
                
                # 2. Encrypt payload
                # Generate random salt and IV
                salt = secrets.token_bytes(16)
                
                # Derive encryption key from password
                encryption_key = derive_key(password, salt)
                
                # Encrypt with AES-256-GCM (generates IV internally)
                ciphertext, iv = encrypt(payload_bytes, encryption_key, b"")
                
                # 3. Build container
                container = create_container(
                    payload=ciphertext,
                    salt=salt,
                    iv=iv,
                    filename=filename,
                    mime_type=mime_type
                )
                
                # 4. Generate positions
                num_bits = len(container) * 8
                positions = generate_positions(
                    width=st.session_state.cover_metadata['width'],
                    height=st.session_state.cover_metadata['height'],
                    stego_key=stego_key,
                    num_bits=num_bits
                )
                
                # 5. Embed in LSB
                stego_image = embed_lsb(
                    cover_image=st.session_state.cover_image,
                    container_bytes=container,
                    positions=positions
                )
                
                # Store result in session state
                st.session_state.stego_image = stego_image
                st.session_state.embed_metadata = {
                    'payload_size': len(payload_bytes),
                    'container_size': len(container),
                    'filename': filename,
                    'mime_type': mime_type,
                    'num_positions': len(positions)
                }
                
                st.success("✓ Message embedded successfully!")
                
                # Show embedding statistics
                with st.expander("📊 Embedding Statistics", expanded=False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Payload Size", format_bytes(len(payload_bytes)))
                        st.metric("Encrypted Size", format_bytes(len(ciphertext)))
                    with col_b:
                        st.metric("Container Size", format_bytes(len(container)))
                        st.metric("Bits Embedded", f"{num_bits:,}")
                
        except Exception as e:
            st.error(f"**Embedding Failed:** {str(e)}")
            st.session_state.stego_image = None
    
    # Step 5: Result
    if hasattr(st.session_state, 'stego_image') and st.session_state.stego_image is not None:
        section_header("5. Result")
        
        # Display comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Cover Image**")
            st.image(st.session_state.cover_image, use_container_width=True)
            st.caption("Original image")
        
        with col2:
            st.markdown("**Stego Image**")
            st.image(st.session_state.stego_image, use_container_width=True)
            st.caption("Image with hidden data")
        
        # Calculate and display metrics
        st.markdown("**Quality Metrics**")
        
        try:
            mse = calculate_mse(
                st.session_state.cover_image,
                st.session_state.stego_image
            )
            psnr = calculate_psnr(mse)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("MSE", f"{mse:.6f}", help="Mean Squared Error (lower is better)")
            with col_b:
                st.metric("PSNR", f"{psnr:.2f} dB", help="Peak Signal-to-Noise Ratio (higher is better)")
            with col_c:
                utilization = (st.session_state.embed_metadata['container_size'] * 8 / 
                              (st.session_state.cover_metadata['width'] * 
                               st.session_state.cover_metadata['height'] * 3)) * 100
                st.metric("Capacity Used", f"{utilization:.2f}%", help="Percentage of available capacity used")
            
            # Quality interpretation
            if psnr >= 40:
                quality_text = "🟢 **Excellent** - Changes imperceptible"
            elif psnr >= 30:
                quality_text = "🟡 **Good** - Acceptable quality"
            else:
                quality_text = "🔴 **Fair** - Visible artifacts possible"
            
            st.info(quality_text)
            
        except Exception as e:
            st.warning(f"Could not calculate metrics: {str(e)}")
        
        # Download stego image
        try:
            # Convert PIL Image to bytes for download
            img_bytes = io.BytesIO()
            st.session_state.stego_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            st.download_button(
                label="⬇️ Download Stego Image",
                data=img_bytes,
                file_name="stego_image.png",
                mime="image/png",
                help="Download the image with hidden data"
            )
            
            st.caption("⚠️ **Important:** Keep your password and stego-key safe. You'll need both to extract the hidden message.")
            
        except Exception as e:
            st.error(f"Could not prepare download: {str(e)}")
    
    footer()
