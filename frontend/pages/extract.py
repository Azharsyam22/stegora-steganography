"""
Stegora - Extract Page
Extract hidden message from stego image
"""
import streamlit as st
import io
import struct

from frontend.ui.components import (
    page_title, section_header, muted_text, footer
)
from backend.image.io import validate_and_load_cover_image, ImageValidationError
from backend.stego.capacity import format_bytes
from backend.stego.positions import generate_positions
from backend.stego.lsb import extract_lsb
from backend.stego.container import parse_container, ContainerError
from backend.crypto.pbkdf2 import derive_key
from backend.crypto.aes_gcm import decrypt


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
    
    # Process extraction
    if extract_btn and can_extract:
        try:
            with st.spinner("Extracting message..."):
                # 1. Generate positions (must match embedding)
                # First, we need to read the header to know how many bytes to extract
                # Read fixed header size first (16 bytes)
                header_positions = generate_positions(
                    width=st.session_state.stego_metadata['width'],
                    height=st.session_state.stego_metadata['height'],
                    stego_key=stego_key,
                    num_bits=16 * 8  # 16 bytes for fixed header
                )
                
                header_bytes = extract_lsb(
                    stego_image=st.session_state.stego_image,
                    positions=header_positions,
                    num_bytes=16
                )
                
                # Parse header to get payload length
                magic, version, flags, payload_type, reserved, payload_len = struct.unpack(
                    '>4s B B B B I',
                    header_bytes
                )
                
                # Validate magic
                if magic != b'STGR':
                    raise ContainerError(f"Invalid magic bytes: {magic}. This may not be a Stegora image or wrong stego-key was used.")
                
                # Read metadata lengths (next 5 bytes)
                meta_positions = generate_positions(
                    width=st.session_state.stego_metadata['width'],
                    height=st.session_state.stego_metadata['height'],
                    stego_key=stego_key,
                    num_bits=(16 + 5) * 8
                )
                
                meta_bytes = extract_lsb(
                    stego_image=st.session_state.stego_image,
                    positions=meta_positions[16*8:],  # Skip header
                    num_bytes=5
                )
                
                salt_len, iv_len, filename_len, mime_len = struct.unpack('>B B H B', meta_bytes)
                
                # Calculate total container size
                total_size = 16 + 5 + salt_len + iv_len + filename_len + mime_len + payload_len
                
                # 2. Generate all positions needed
                all_positions = generate_positions(
                    width=st.session_state.stego_metadata['width'],
                    height=st.session_state.stego_metadata['height'],
                    stego_key=stego_key,
                    num_bits=total_size * 8
                )
                
                # 3. Extract complete container
                container_bytes = extract_lsb(
                    stego_image=st.session_state.stego_image,
                    positions=all_positions,
                    num_bytes=total_size
                )
                
                # 4. Parse container
                container_data = parse_container(container_bytes)
                
                # 5. Decrypt payload
                # Derive key from password and stored salt
                decryption_key = derive_key(password, container_data['salt'])
                
                # Decrypt with stored IV
                plaintext = decrypt(
                    ciphertext=container_data['payload'],
                    key=decryption_key,
                    iv=container_data['iv'],
                    associated_data=b""
                )
                
                # Store result in session state
                st.session_state.extracted_data = {
                    'plaintext': plaintext,
                    'filename': container_data['filename'],
                    'mime_type': container_data['mime_type'],
                    'container_size': len(container_bytes),
                    'payload_size': len(plaintext),
                    'magic_valid': True,
                    'auth_valid': True,
                    'integrity': 'OK'
                }
                
                st.success("✓ Message extracted and decrypted successfully!")
                
                # Show extraction statistics
                with st.expander("📊 Extraction Statistics", expanded=False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Container Size", format_bytes(len(container_bytes)))
                        st.metric("Encrypted Size", format_bytes(len(container_data['payload'])))
                    with col_b:
                        st.metric("Decrypted Size", format_bytes(len(plaintext)))
                        st.metric("Bits Extracted", f"{len(container_bytes) * 8:,}")
                
        except ContainerError as e:
            st.error(f"**Container Error:** {str(e)}")
            st.caption("This usually means wrong stego-key or corrupted image.")
            st.session_state.extracted_data = None
            
        except ValueError as e:
            st.error(f"**Decryption Error:** {str(e)}")
            st.caption("This usually means wrong password or corrupted data.")
            st.session_state.extracted_data = None
            
        except Exception as e:
            st.error(f"**Extraction Failed:** {str(e)}")
            st.session_state.extracted_data = None
    
    # Step 4: Result
    if hasattr(st.session_state, 'extracted_data') and st.session_state.extracted_data is not None:
        section_header("4. Extracted Content")
        
        extracted = st.session_state.extracted_data
        
        # Determine if text or binary
        is_text = extracted['mime_type'].startswith('text/')
        
        if is_text:
            # Display as text
            try:
                text_content = extracted['plaintext'].decode('utf-8')
                
                st.markdown("**Recovered Text Message:**")
                st.text_area(
                    "Message content",
                    value=text_content,
                    height=200,
                    label_visibility="collapsed"
                )
                
                # Metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Filename", extracted['filename'])
                    st.metric("Type", extracted['mime_type'])
                with col2:
                    st.metric("Size", format_bytes(extracted['payload_size']))
                    st.metric("Characters", len(text_content))
                
            except UnicodeDecodeError:
                st.warning("Could not decode as text. Treating as binary file.")
                is_text = False
        
        if not is_text:
            # Display file info and download
            st.markdown("**Recovered File:**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Filename", extracted['filename'])
                st.metric("MIME Type", extracted['mime_type'])
            with col2:
                st.metric("File Size", format_bytes(extracted['payload_size']))
                st.metric("Status", "✓ Ready")
            
            # Download button
            st.download_button(
                label="⬇️ Download Recovered File",
                data=extracted['plaintext'],
                file_name=extracted['filename'] or "recovered_file.bin",
                mime=extracted['mime_type'],
                help="Download the extracted file"
            )
        
        # Verification status
        st.markdown("**Verification Status**")
        col1, col2, col3 = st.columns(3)
        with col1:
            status = "✓ Valid" if extracted['magic_valid'] else "✗ Invalid"
            st.metric("Magic Bytes", status, help="STGR header validation")
        with col2:
            status = "✓ Valid" if extracted['auth_valid'] else "✗ Invalid"
            st.metric("Auth Tag", status, help="AES-GCM authentication passed")
        with col3:
            st.metric("Integrity", extracted['integrity'], help="Overall data integrity")
        
        st.success("🎉 Extraction completed successfully! All verifications passed.")
    
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
