"""
Stegora - Analyze Page
Steganalysis tools and metrics
"""
import streamlit as st


def show():
    """Analyze page UI"""
    st.title("📊 Analyze")
    st.markdown("Steganalysis tools: metrics, histogram, enhanced LSB.")
    
    # Image uploads
    st.subheader("1. Upload Images")
    col1, col2 = st.columns(2)
    
    with col1:
        cover_file = st.file_uploader(
            "Cover image",
            type=["png", "bmp"],
            key="analyze_cover"
        )
        if cover_file:
            st.success(f"✓ Cover: {cover_file.name}")
    
    with col2:
        stego_file = st.file_uploader(
            "Stego image",
            type=["png", "bmp"],
            key="analyze_stego"
        )
        if stego_file:
            st.success(f"✓ Stego: {stego_file.name}")
    
    # Analysis options
    if cover_file and stego_file:
        st.subheader("2. Analysis Options")
        
        analysis_type = st.multiselect(
            "Select analysis types",
            ["MSE & PSNR", "Histogram Comparison", "Enhanced LSB", "m-bit LSB Comparison"],
            default=["MSE & PSNR"]
        )
        
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            st.warning("⚠️ Analysis functionality not yet implemented")
            # TODO: Implement analysis tools
    else:
        st.info("Upload both cover and stego images to start analysis")
    
    st.markdown("---")
    st.caption("Stegora - LSB Steganography with AES-256-GCM")
