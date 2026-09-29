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
from frontend.ui.state import (
    init_session_state, save_extract_result, save_extract_error
)
from backend.image.io import validate_and_load_cover_image, ImageValidationError
from backend.stego.capacity import format_bytes
from backend.stego.positions import generate_positions
from backend.stego.lsb import extract_lsb
from backend.stego.container import (
    parse_container, 
    parse_header, 
    parse_metadata_lengths, 
    ContainerError,
    HEADER_SIZE,
    META_LENGTHS_SIZE
)
from backend.crypto.pbkdf2 import derive_key
from backend.crypto.aes_gcm import decrypt


def show():
    """Extract page UI with complete workflow"""
    page_title(
        "Ekstrak Pesan",
        "Ambil kembali pesan tersembunyi dari citra stego"
    )
    
    # Step 1: Stego image
    section_header("1. Unggah Citra Stego")
    stego_file = st.file_uploader(
        "Pilih citra (PNG, BMP, JPG)",
        type=["png", "bmp", "jpg", "jpeg"],
        key="extract_stego",
        help="Pilih citra yang berisi pesan tersembunyi. PNG/BMP untuk ekstraksi normal. JPG/JPEG untuk uji kerapuhan (akan gagal karena lossy compression)."
    )
    
    stego_valid = False
    
    if stego_file:
        try:
            # Read and validate
            stego_bytes = stego_file.read()
            image, metadata = validate_and_load_cover_image(stego_bytes)
            
            # Detect if JPEG for warning
            is_jpeg = metadata['format'].upper() in ['JPEG', 'JPG']
            
            # Store in session state
            st.session_state.stego_image = image
            st.session_state.stego_metadata = metadata
            st.session_state.is_jpeg_stego = is_jpeg
            stego_valid = True
            
            # Display
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(image, caption="Citra Stego", use_container_width=True)
            
            with col2:
                if is_jpeg:
                    st.warning(f"**Format JPEG Terdeteksi:** {stego_file.name}")
                    st.error(
                        "**Uji Kerapuhan JPEG:** Citra ini dalam format JPEG (lossy compression). "
                        "Kompresi JPEG mengubah pixel values dan merusak bit LSB yang menyimpan data steganografi. "
                        "Ekstraksi kemungkinan besar akan **GAGAL**. Ini adalah uji kerapuhan untuk mendemonstrasikan "
                        "bahwa steganografi LSB tidak robust terhadap lossy compression."
                    )
                else:
                    st.success(f"Berhasil dimuat: **{stego_file.name}**")
                
                # Image info
                st.markdown("**Informasi Citra**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Format", metadata['format'])
                    st.metric("Mode", metadata['mode'])
                with col_b:
                    st.metric("Lebar", f"{metadata['width']} px")
                    st.metric("Tinggi", f"{metadata['height']} px")
                
                if not is_jpeg:
                    muted_text("Citra siap diekstrak")
                else:
                    st.caption("Ekstraksi dari JPEG untuk demo kerapuhan")
                
        except ImageValidationError as e:
            st.error(f"**Kesalahan Validasi:** {str(e)}")
            stego_valid = False
        except Exception as e:
            st.error(f"**Kesalahan Tidak Terduga:** {str(e)}")
            stego_valid = False
    
    # Step 2: Credentials
    section_header("2. Kredensial Keamanan")
    
    st.markdown("Masukkan **kata kunci** yang sama dengan saat penyisipan:")
    
    password = st.text_input(
        "Kata Kunci / Password",
        type="password",
        key="extract_password",
        value="",
        help="Gunakan kata kunci yang sama persis dengan saat penyisipan. Case-sensitive!",
        placeholder="Masukkan kata kunci..."
    )
    
    # Use same password for stego_key (unified credential)
    stego_key = password
    
    # Step 3: Extract
    section_header("3. Ekstrak Pesan")
    
    # Validation
    can_extract = True
    warnings = []
    
    if not stego_valid:
        warnings.append("Unggah citra stego yang valid")
        can_extract = False
    if not password:
        warnings.append("Masukkan kata kunci")
        can_extract = False
    
    if warnings:
        st.warning(f"Perlu dilengkapi: {', '.join(warnings)}")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        extract_btn = st.button(
            "Ekstrak Pesan",
            type="primary",
            use_container_width=True,
            disabled=not can_extract
        )
    
    # Process extraction
    if extract_btn and can_extract:
        try:
            with st.spinner("Pesan sedang diekstrak..."):
                # 1. Generate positions (must match embedding)
                # First, we need to read the header to know how many bytes to extract
                # Read fixed header size first (12 bytes)
                header_positions = generate_positions(
                    width=st.session_state.stego_metadata['width'],
                    height=st.session_state.stego_metadata['height'],
                    stego_key=stego_key,
                    num_bits=HEADER_SIZE * 8  # 12 bytes for fixed header
                )
                
                header_bytes = extract_lsb(
                    stego_image=st.session_state.stego_image,
                    positions=header_positions,
                    num_bytes=HEADER_SIZE
                )
                
                # Parse header to get payload length
                header_data = parse_header(header_bytes)
                payload_len = header_data['payload_len']
                
                # Read metadata lengths (next 5 bytes)
                meta_positions = generate_positions(
                    width=st.session_state.stego_metadata['width'],
                    height=st.session_state.stego_metadata['height'],
                    stego_key=stego_key,
                    num_bits=(HEADER_SIZE + META_LENGTHS_SIZE) * 8
                )
                
                meta_bytes = extract_lsb(
                    stego_image=st.session_state.stego_image,
                    positions=meta_positions[HEADER_SIZE * 8:],  # Skip header
                    num_bytes=META_LENGTHS_SIZE
                )
                
                salt_len, iv_len, filename_len, mime_len = parse_metadata_lengths(meta_bytes)
                
                # Calculate total container size
                total_size = HEADER_SIZE + META_LENGTHS_SIZE + salt_len + iv_len + filename_len + mime_len + payload_len
                
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
                
                st.success("Pesan berhasil diekstrak dan didekripsi!")
                
                # Show extraction statistics
                with st.expander("Statistik Ekstraksi", expanded=False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Ukuran Kontainer", format_bytes(len(container_bytes)))
                        st.metric("Ukuran Terenkripsi", format_bytes(len(container_data['payload'])))
                    with col_b:
                        st.metric("Ukuran Terdekripsi", format_bytes(len(plaintext)))
                        st.metric("Bit Diekstrak", f"{len(container_bytes) * 8:,}")
                
        except ContainerError as e:
            st.error(f"**Kesalahan Kontainer:** {str(e)}")
            
            # Check if JPEG for specific message
            if hasattr(st.session_state, 'is_jpeg_stego') and st.session_state.is_jpeg_stego:
                st.info(
                    "**Uji Kerapuhan JPEG Berhasil:** "
                    "Ekstraksi gagal karena citra stego disimpan dalam format JPEG (lossy compression). "
                    "Kompresi JPEG mengubah bit LSB yang menyimpan data steganografi, sehingga header magic number "
                    "dan struktur kontainer rusak. Ini membuktikan bahwa steganografi LSB **tidak robust** "
                    "terhadap kompresi lossy.\n\n"
                    "**Kesimpulan:** Format lossless (PNG, BMP) wajib untuk komunikasi steganografi."
                )
            else:
                st.caption("Biasanya kunci stego salah atau citra rusak.")
            
            st.session_state.extracted_data = None
            
        except ValueError as e:
            st.error(f"**Kesalahan Dekripsi:** {str(e)}")
            
            # Check if JPEG for specific message
            if hasattr(st.session_state, 'is_jpeg_stego') and st.session_state.is_jpeg_stego:
                st.info(
                    "**Uji Kerapuhan JPEG Berhasil:** "
                    "Dekripsi gagal karena data yang diekstrak dari JPEG corrupt. "
                    "Kompresi JPEG merusak bit LSB, sehingga payload terenkripsi tidak dapat didekripsi "
                    "meskipun password benar. Authentication tag AES-GCM mendeteksi perubahan data.\n\n"
                    "**Kesimpulan:** Steganografi LSB tidak dapat digunakan dengan format JPEG."
                )
            else:
                st.caption("Biasanya kata sandi salah atau data rusak.")
            
            st.session_state.extracted_data = None
            
        except Exception as e:
            st.error(f"**Ekstraksi Gagal:** {str(e)}")
            st.session_state.extracted_data = None
    
    # Step 4: Result
    if hasattr(st.session_state, 'extracted_data') and st.session_state.extracted_data is not None:
        section_header("4. Konten Hasil Ekstraksi")
        
        extracted = st.session_state.extracted_data
        
        # Determine if text or binary
        is_text = extracted['mime_type'].startswith('text/')
        
        if is_text:
            # Display as text
            try:
                text_content = extracted['plaintext'].decode('utf-8')
                
                st.markdown("**Pesan Teks yang Dipulihkan:**")
                st.text_area(
                    "Isi pesan",
                    value=text_content,
                    height=200,
                    label_visibility="collapsed"
                )
                
                # Metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Nama berkas", extracted['filename'])
                    st.metric("Jenis", extracted['mime_type'])
                with col2:
                    st.metric("Ukuran", format_bytes(extracted['payload_size']))
                    st.metric("Jumlah karakter", len(text_content))
                
            except UnicodeDecodeError:
                st.warning("Teks tidak dapat dibaca. Konten akan diperlakukan sebagai berkas biner.")
                is_text = False
        
        if not is_text:
            # Display file info and download
            st.markdown("**Berkas yang Dipulihkan:**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Nama berkas", extracted['filename'])
                st.metric("Jenis MIME", extracted['mime_type'])
            with col2:
                st.metric("Ukuran Berkas", format_bytes(extracted['payload_size']))
                st.metric("Status", "Siap")
            
            # Download button
            st.download_button(
                label="Unduh Berkas Hasil Ekstraksi",
                data=extracted['plaintext'],
                file_name=extracted['filename'] or "recovered_file.bin",
                mime=extracted['mime_type'],
                help="Unduh berkas yang telah diekstrak."
            )
        
        # Verification status
        st.markdown("**Status Verifikasi**")
        col1, col2, col3 = st.columns(3)
        with col1:
            status = "Valid" if extracted['magic_valid'] else "Invalid"
            st.metric("Byte Penanda", status, help="Validasi header STGR.")
        with col2:
            status = "Valid" if extracted['auth_valid'] else "Invalid"
            st.metric("Tag Autentikasi", status, help="Autentikasi AES-GCM berhasil.")
        with col3:
            st.metric("Integritas", extracted['integrity'], help="Integritas data secara keseluruhan.")
        
        st.success("Ekstraksi berhasil! Semua verifikasi lolos.")
    
    # Help section
    with st.expander("Tips Ekstraksi", expanded=False):
        st.markdown("""
        **Agar ekstraksi berhasil:**
        
          1. **Gunakan citra stego yang benar**
              - Gunakan berkas hasil penyisipan yang asli
              - Jangan simpan ulang atau mengubah citra
              - Konversi JPEG akan merusak data tersembunyi
        
          2. **Gunakan kredensial yang sama persis**
              - Kata sandi peka terhadap huruf besar dan kecil
              - Kunci stego harus sama persis
              - Kredensial salah akan menghasilkan data keliru atau rusak
        
          3. **Hindari mengubah citra**
              - Jangan memotong, mengubah ukuran, atau memutar citra
              - Jangan menerapkan filter atau penyesuaian
              - Jangan mengubah format (PNG ↔ BMP aman jika lossless)
        
          4. **Hasil yang diharapkan**
              - [X] Kata sandi salah → Autentikasi gagal
              - [X] Kunci stego salah → Data rusak atau kesalahan pembacaan
              - [X] Citra diubah → Data rusak atau tidak lengkap
        """)
    
    footer()
