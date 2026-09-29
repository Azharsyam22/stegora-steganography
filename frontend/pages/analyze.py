"""
Stegora - Analyze Page
Steganalysis tools and metrics
"""
import streamlit as st
import numpy as np
from PIL import Image
import io

from frontend.ui.components import (
    page_title, section_header, muted_text, footer
)
from backend.image.io import validate_and_load_cover_image, ImageValidationError
from backend.image.metrics import calculate_mse, calculate_psnr, format_psnr, format_mse
from backend.pipeline import extract_pipeline, ExtractError
from frontend.ui.state import get_stored_credentials
from stegora.analysis.histogram import calculate_histogram_from_pil, compare_histograms
from stegora.analysis.lsb_plane import extract_lsb_plane, create_enhanced_lsb_visual
from stegora.analysis.robustness import test_jpeg_compression as jpeg_compression_test
import matplotlib.pyplot as plt


def show():
    """Analyze page UI with full functionality"""
    page_title(
        "Analisis Citra",
        "Metrik kualitas, histogram, dan visualisasi LSB untuk steganalisis"
    )
    
    # Step 1: Image uploads
    section_header("1. Unggah Citra")
    
    col1, col2 = st.columns(2)
    
    cover_valid = False
    stego_valid = False
    
    with col1:
        cover_file = st.file_uploader(
            "Citra penutup (asli)",
            type=["png", "bmp"],
            key="analyze_cover",
            help="Citra asli sebelum penyisipan (hanya PNG/BMP)."
        )
        if cover_file:
            try:
                cover_bytes = cover_file.read()
                cover_image, cover_metadata = validate_and_load_cover_image(cover_bytes)
                st.image(cover_image, caption="Citra Penutup", use_container_width=True)
                st.success(f"✓ {cover_file.name} ({cover_metadata['width']}×{cover_metadata['height']})")
                
                # Store in session with different key
                st.session_state['cover_img'] = cover_image
                st.session_state['cover_meta'] = cover_metadata
                cover_valid = True
            except ImageValidationError as e:
                st.error(f"**Kesalahan Validasi:** {str(e)}")
            except Exception as e:
                st.error(f"**Kesalahan:** {str(e)}")
    
    with col2:
        stego_file = st.file_uploader(
            "Citra stego (berisi pesan)",
            type=["png", "bmp"],
            key="analyze_stego",
            help="Citra setelah penyisipan (hanya PNG/BMP)."
        )
        if stego_file:
            try:
                stego_bytes = stego_file.read()
                stego_image, stego_metadata = validate_and_load_cover_image(stego_bytes)
                st.image(stego_image, caption="Citra Stego", use_container_width=True)
                st.success(f"✓ {stego_file.name} ({stego_metadata['width']}×{stego_metadata['height']})")
                
                # Store in session with different key
                st.session_state['stego_img'] = stego_image
                st.session_state['stego_meta'] = stego_metadata
                stego_valid = True
            except ImageValidationError as e:
                st.error(f"**Kesalahan Validasi:** {str(e)}")
            except Exception as e:
                st.error(f"**Kesalahan:** {str(e)}")
    
    # Step 2: Analysis options
    if cover_valid and stego_valid:
        # Check dimensions match
        if (cover_metadata['width'] != stego_metadata['width'] or 
            cover_metadata['height'] != stego_metadata['height']):
            st.error("**Error:** Images must have the same dimensions!")
            return
        
        section_header("2. Opsi Analisis")
        
        analysis_types = st.multiselect(
            "Pilih jenis analisis",
            [
                "MSE & PSNR",
                "Perbandingan Histogram",
                "Visualisasi LSB yang Ditingkatkan",
                "Uji Kerapuhan JPEG"
            ],
            default=["MSE & PSNR"],
            help="Pilih satu atau beberapa metode analisis."
        )
        
        if not analysis_types:
            st.warning("Pilih setidaknya satu jenis analisis.")
            return

        jpeg_test_selected = "Uji Kerapuhan JPEG" in analysis_types
        stored_password, stored_stego_key = get_stored_credentials()
        jpeg_quality = 90
        jpeg_password = ""
        jpeg_stego_key = ""

        if jpeg_test_selected:
            st.markdown("#### Uji Kerapuhan JPEG")
            st.caption(
                "Unggah citra penutup dan citra stego lama, lalu masukkan kredensial "
                "yang digunakan saat penyisipan. Citra stego akan disimpan ulang sebagai "
                "JPEG kualitas 90 dan diuji ekstraksinya. Embed ulang tidak diperlukan."
            )
            credential_col1, credential_col2 = st.columns(2)
            with credential_col1:
                jpeg_password = st.text_input(
                    "Kata sandi untuk uji JPEG",
                    type="password",
                    key="jpeg_test_password",
                    value=stored_password,
                )
            with credential_col2:
                jpeg_stego_key = st.text_input(
                    "Kunci stego untuk uji JPEG",
                    type="password",
                    key="jpeg_test_stego_key",
                    value=stored_stego_key,
                )
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            analyze_btn = st.button(
                "Analisis",
                type="primary",
                use_container_width=True
            )
        
        if analyze_btn:
            with st.spinner("Analyzing images..."):
                # Convert images to numpy arrays
                cover_array = np.array(st.session_state['cover_img'])
                stego_array = np.array(st.session_state['stego_img'])
                
                # Perform selected analyses
                section_header("3. Analysis Results")
                jpeg_test_skip_reason = None
                
                for analysis in analysis_types:
                    if analysis == "MSE & PSNR":
                        st.markdown("### Metrik Kualitas Citra")
                        
                        # Calculate MSE and PSNR
                        mse = calculate_mse(cover_array, stego_array)
                        psnr = calculate_psnr(cover_array, stego_array)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("MSE", format_mse(mse))
                        with col2:
                            st.metric("PSNR", format_psnr(psnr))
                        with col3:
                            if psnr == float('inf') or psnr >= 50:
                                quality = "Sangat baik"
                            elif psnr >= 30:
                                quality = "Baik"
                            else:
                                quality = "Cukup"
                            st.metric("Kualitas", quality)
                        
                        st.markdown("---")
                    
                    elif analysis == "Perbandingan Histogram":
                        st.markdown("### Perbandingan Histogram RGB")
                        
                        # Calculate histograms
                        cover_hist = calculate_histogram_from_pil(st.session_state['cover_img'])
                        stego_hist = calculate_histogram_from_pil(st.session_state['stego_img'])
                        
                        # Plot histograms
                        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
                        colors = ['red', 'green', 'blue']
                        channels = ['Merah', 'Hijau', 'Biru']
                        channel_keys = ['R', 'G', 'B']
                        
                        for i, (color, channel, key) in enumerate(zip(colors, channels, channel_keys)):
                            axes[i].plot(cover_hist[key], color=color, alpha=0.7, label='Cover', linewidth=1.5)
                            axes[i].plot(stego_hist[key], color=color, alpha=0.5, label='Stego', linestyle='--', linewidth=1.5)
                            axes[i].set_title(f'{channel} Channel')
                            axes[i].set_xlabel('Intensitas Piksel')
                            axes[i].set_ylabel('Frekuensi')
                            axes[i].legend(['Penutup', 'Stego'])
                            axes[i].grid(True, alpha=0.3)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close()
                        
                        # Comparison metrics
                        comparison = compare_histograms(cover_hist, stego_hist)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rata-rata Selisih", f"{comparison['overall_mad']:.2f}")
                        with col2:
                            st.metric("Chi-Square", f"{comparison['overall_chi2']:.2f}")
                        with col3:
                            st.metric("Selisih Maksimum", f"{comparison['overall_max']:.0f}")
                        
                        st.caption("**Interpretasi:** Korelasi yang lebih tinggi dan nilai chi-square yang lebih rendah menunjukkan histogram yang lebih mirip.")
                        st.markdown("---")
                    
                    elif analysis == "Visualisasi LSB yang Ditingkatkan":
                        st.markdown("### Visualisasi Bidang LSB yang Ditingkatkan")
                        
                        # Extract LSB planes
                        lsb_visual = create_enhanced_lsb_visual(stego_array)
                        
                        # Convert to PIL for display
                        lsb_image = Image.fromarray(lsb_visual)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(st.session_state['stego_img'], caption="Citra Stego Asli", use_container_width=True)
                        with col2:
                            st.image(lsb_image, caption="Bidang LSB (Ditingkatkan)", use_container_width=True)
                        
                        st.caption("**Visualisasi LSB:** Menampilkan bidang bit paling rendah. Pola derau acak dapat mengindikasikan steganografi.")
                        st.markdown("---")

                    elif analysis == "Uji Kerapuhan JPEG":
                        st.markdown("### Uji Kerapuhan JPEG")
                        if not jpeg_password or not jpeg_stego_key:
                            jpeg_test_skip_reason = (
                                "Masukkan kata sandi dan kunci stego yang digunakan "
                                "saat citra tersebut disisipkan."
                            )
                            continue

                        try:
                            original_payload, _ = extract_pipeline(
                                st.session_state['stego_img'],
                                jpeg_password,
                                jpeg_stego_key
                            )
                            st.success(
                                f"Pemeriksaan awal berhasil: {len(original_payload)} byte "
                                "berhasil dipulihkan dari citra stego asli."
                            )

                            jpeg_array, jpeg_metrics = jpeg_compression_test(
                                stego_array,
                                quality=jpeg_quality
                            )
                            jpeg_image = Image.fromarray(jpeg_array)

                            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                            with metrics_col1:
                                st.metric("Kualitas JPEG", jpeg_quality)
                            with metrics_col2:
                                st.metric("PSNR Citra", format_psnr(jpeg_metrics['psnr']))
                            with metrics_col3:
                                st.metric(
                                    "LSB yang bertahan",
                                    f"{jpeg_metrics['lsb_survival_rate'] * 100:.1f}%"
                                )

                            try:
                                jpeg_payload, _ = extract_pipeline(
                                    jpeg_image,
                                    jpeg_password,
                                    jpeg_stego_key
                                )
                                if jpeg_payload == original_payload:
                                    st.warning(
                                        "Ekstraksi masih berhasil pada kualitas JPEG ini. "
                                        "Coba kualitas lebih rendah untuk melihat dampak kerapuhan."
                                    )
                                else:
                                    st.success(
                                        "Uji kerapuhan berhasil: hasil ekstraksi berubah "
                                        "setelah citra stego disimpan ulang sebagai JPEG. "
                                        "Muatan data tidak lagi sama dengan pesan asli."
                                    )
                            except ExtractError:
                                st.success(
                                    "Uji kerapuhan berhasil: pesan tidak dapat diekstrak "
                                    "setelah citra stego disimpan ulang sebagai JPEG. "
                                    "Kompresi JPEG mengubah bit LSB yang menyimpan pesan. "
                                    "Pemeriksaan citra asli sebelumnya berhasil, jadi ini "
                                    "bukan karena kunci stego salah."
                                )

                            st.image(
                                jpeg_image,
                                caption="Citra stego setelah disimpan ulang sebagai JPEG",
                                use_container_width=True
                            )
                        except ExtractError:
                            jpeg_test_skip_reason = (
                                "Citra stego asli tidak berhasil diekstrak. Pastikan "
                                "berkas stego dan kredensial yang dimasukkan sesuai."
                            )
                        st.markdown("---")

                if jpeg_test_skip_reason:
                    st.warning(
                        "Analisis lain selesai, tetapi Uji Kerapuhan JPEG tidak "
                        f"dijalankan. {jpeg_test_skip_reason}"
                    )
                else:
                    st.success("✓ Analisis selesai!")
    
    else:
        st.info("Unggah citra penutup dan citra stego untuk memulai analisis.")
        muted_text("Kedua citra diperlukan untuk analisis perbandingan. Gunakan format PNG atau BMP.")
    
    footer()
