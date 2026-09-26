"""
Stegora - Analyze Page
Steganalysis tools and metrics
"""
import streamlit as st
from stegora.ui.components import (
    page_title, section_header, muted_text, footer
)


def show():
    """Analyze page UI"""
    page_title(
        "Analyze Images",
        "Steganalysis tools: metrics, histogram, enhanced LSB"
    )
    
    # Step 1: Image uploads
    section_header("1. Upload Images")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cover_file = st.file_uploader(
            "Cover image (original)",
            type=["png", "bmp"],
            key="analyze_cover",
            help="Original image before embedding"
        )
        if cover_file:
            st.image(cover_file, caption="Cover", use_container_width=True)
            st.success(f"{cover_file.name}")
    
    with col2:
        stego_file = st.file_uploader(
            "Stego image (with message)",
            type=["png", "bmp"],
            key="analyze_stego",
            help="Image after embedding"
        )
        if stego_file:
            st.image(stego_file, caption="Stego", use_container_width=True)
            st.success(f"{stego_file.name}")
    
    # Step 2: Analysis options
    if cover_file and stego_file:
        section_header("2. Analysis Options")
        
        analysis_types = st.multiselect(
            "Select analysis types",
            [
                "MSE & PSNR",
                "Histogram Comparison",
                "Enhanced LSB",
                "m-bit LSB Comparison"
            ],
            default=["MSE & PSNR"],
            help="Choose one or more analysis methods"
        )
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            analyze_btn = st.button(
                "Analyze",
                type="primary",
                use_container_width=True
            )
        
        if analyze_btn:
            st.info("Analysis functionality not yet implemented (requires T15-T18)")
            muted_text("Next tasks: MSE/PSNR, Histogram, Enhanced LSB, m-bit analysis")
            
            # Show what will be implemented
            with st.expander("Planned Analysis", expanded=True):
                for analysis in analysis_types:
                    if analysis == "MSE & PSNR":
                        st.markdown("**MSE & PSNR:**")
                        st.markdown("- Mean Squared Error between images")
                        st.markdown("- Peak Signal-to-Noise Ratio (minimum 30 dB)")
                        st.markdown("- Quality assessment")
                    elif analysis == "Histogram Comparison":
                        st.markdown("**Histogram Comparison:**")
                        st.markdown("- RGB channel histograms")
                        st.markdown("- Side-by-side comparison")
                        st.markdown("- Visual distribution analysis")
                    elif analysis == "Enhanced LSB":
                        st.markdown("**Enhanced LSB:**")
                        st.markdown("- Extract and visualize LSB plane")
                        st.markdown("- Visual steganalysis")
                        st.markdown("- Detect patterns")
                    elif analysis == "m-bit LSB Comparison":
                        st.markdown("**m-bit LSB Comparison:**")
                        st.markdown("- Compare 1-bit, 2-bit, 3-bit, 4-bit LSB")
                        st.markdown("- Capacity vs PSNR trade-off")
                        st.markdown("- Enrichment feature")
    else:
        st.info("Upload both cover and stego images to start analysis")
        muted_text("You need both images to perform comparative analysis")
    
    footer()
