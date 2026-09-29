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
from stegora.analysis.histogram import calculate_histogram_from_pil, compare_histograms
from stegora.analysis.lsb_plane import extract_lsb_plane, create_enhanced_lsb_visual
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
                st.success(f"{cover_file.name} ({cover_metadata['width']}×{cover_metadata['height']})")
                
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
                st.success(f"{stego_file.name} ({stego_metadata['width']}×{stego_metadata['height']})")
                
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
        
        analysis_type = st.radio(
            "Pilih jenis analisis (hanya satu)",
            [
                "MSE & PSNR",
                "Perbandingan Histogram",
                "Visualisasi LSB yang Ditingkatkan"
            ],
            index=0,
            help="Pilih salah satu metode analisis untuk ditampilkan."
        )
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            analyze_btn = st.button(
                "Analisis",
                type="primary",
                use_container_width=True
            )
        
        if analyze_btn:
            with st.spinner("Melakukan analisis..."):
                # Convert images to numpy arrays
                cover_array = np.array(st.session_state['cover_img'])
                stego_array = np.array(st.session_state['stego_img'])
                
                # Perform selected analysis
                section_header("3. Hasil Analisis")
                
                if analysis_type == "MSE & PSNR":
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
                
                elif analysis_type == "Perbandingan Histogram":
                    st.markdown("### Perbandingan Histogram RGB")
                    
                    # Calculate histograms
                    cover_hist = calculate_histogram_from_pil(st.session_state['cover_img'])
                    stego_hist = calculate_histogram_from_pil(st.session_state['stego_img'])
                    
                    # Plot histograms - 2 rows (Cover & Stego), 3 columns (R, G, B)
                    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
                    colors = ['red', 'green', 'blue']
                    channels = ['Merah', 'Hijau', 'Biru']
                    channel_keys = ['R', 'G', 'B']
                    
                    # Row 1: Cover histograms
                    for i, (color, channel, key) in enumerate(zip(colors, channels, channel_keys)):
                        axes[0, i].plot(cover_hist[key], color=color, alpha=0.8, linewidth=2.0)
                        axes[0, i].set_title(f'Cover - {channel} Channel', fontsize=11, fontweight='bold')
                        axes[0, i].set_xlabel('Intensitas Piksel (0-255)', fontsize=9)
                        axes[0, i].set_ylabel('Frekuensi', fontsize=9)
                        axes[0, i].grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
                    
                    # Row 2: Stego histograms
                    for i, (color, channel, key) in enumerate(zip(colors, channels, channel_keys)):
                        axes[1, i].plot(stego_hist[key], color=color, alpha=0.8, linewidth=2.0)
                        axes[1, i].set_title(f'Stego - {channel} Channel', fontsize=11, fontweight='bold')
                        axes[1, i].set_xlabel('Intensitas Piksel (0-255)', fontsize=9)
                        axes[1, i].set_ylabel('Frekuensi', fontsize=9)
                        axes[1, i].grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
                    
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
                
                elif analysis_type == "Visualisasi LSB yang Ditingkatkan":
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
                
                st.success("Analisis selesai!")
    
    else:
        st.info("Unggah citra penutup dan citra stego untuk memulai analisis.")
        muted_text("Kedua citra diperlukan untuk analisis perbandingan. Gunakan format PNG atau BMP.")
    
    footer()
