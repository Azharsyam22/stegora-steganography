"""
Stegora - About Page
System information and technical specifications
"""
import streamlit as st
from frontend.ui.components import (
    page_title, section_header, muted_text, footer
)


def show():
    """About page with system information"""
    page_title(
        "About Stegora",
        "Professional steganography suite with AES-256-GCM encryption"
    )
    
    # System Overview
    section_header("System Overview")
    
    st.markdown("""
    **Stegora** adalah aplikasi steganografi berbasis web yang dirancang untuk 
    menyembunyikan pesan atau file di dalam gambar PNG/BMP menggunakan teknik 
    **1-bit RGB LSB** (Least Significant Bit) dengan enkripsi **AES-256-GCM**.
    
    Sistem ini menggabungkan steganografi dan kriptografi untuk menyediakan 
    dua lapis keamanan: enkripsi payload dan randomisasi posisi embedding 
    menggunakan deterministic PRNG.
    """)
    
    # Technical Specifications
    section_header("Technical Specifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Cryptography**
        - Algorithm: AES-256-GCM
        - Key Derivation: PBKDF2-HMAC-SHA-256
        - Iterations: 600,000
        - Salt: 16 bytes (random per encryption)
        - IV/Nonce: 12 bytes (random per encryption)
        - Authentication Tag: 16 bytes (automatic)
        
        **Steganography**
        - Method: 1-bit RGB LSB embedding
        - Channels: RGB only (alpha preserved)
        - Position Generation: Deterministic PRNG
        - Position Seed: SHA-256(stego-key)
        - Container Format: STGR binary format
        - Supported Formats: PNG, BMP
        """)
    
    with col2:
        st.markdown("""
        **Quality Metrics**
        - MSE: Mean Squared Error
        - PSNR: Peak Signal-to-Noise Ratio
        - Target: PSNR ≥ 30 dB
        - Typical 1-bit LSB: 50-60 dB
        
        **Analysis Tools**
        - RGB Histogram Comparison
        - Enhanced LSB Plane Visualization
        - JPEG Robustness Testing
        - m-bit LSB Comparison
        - 5x3 Testing Matrix
        - XLSX Export
        """)
    
    # How It Works
    section_header("How It Works")
    
    st.markdown("""
    ### Embedding Process
    
    1. **Input Validation**
       - Validate cover image format (PNG/BMP)
       - Calculate available capacity
       - Check payload size constraints
    
    2. **Cryptographic Preparation**
       - Generate random salt (16 bytes)
       - Derive encryption key using PBKDF2 (600k iterations)
       - Generate random IV (12 bytes)
       - Encrypt payload with AES-256-GCM
    
    3. **Container Creation**
       - Build STGR header with magic bytes
       - Add metadata (salt, IV, filename, MIME type)
       - Package encrypted payload
    
    4. **Position Generation**
       - Hash stego-key with SHA-256
       - Seed deterministic PRNG
       - Generate unique RGB channel positions
    
    5. **LSB Embedding**
       - Convert container to bit stream
       - Modify LSB of selected RGB channels
       - Preserve alpha channel completely
    
    6. **Quality Assessment**
       - Calculate MSE between cover and stego
       - Calculate PSNR quality metric
       - Output stego image
    
    ---
    
    ### Extraction Process
    
    1. **Position Regeneration**
       - Hash stego-key with SHA-256 (same as embedding)
       - Regenerate same position sequence
    
    2. **LSB Extraction**
       - Read LSB from determined positions
       - Reconstruct bit stream
       - Parse as bytes
    
    3. **Container Parsing**
       - Validate STGR magic bytes
       - Extract header and metadata
       - Retrieve salt, IV, and encrypted payload
    
    4. **Decryption**
       - Derive key from password + extracted salt
       - Decrypt with AES-GCM using extracted IV
       - Verify authentication tag
    
    5. **Payload Recovery**
       - Return original text or file
       - Byte-perfect reconstruction
    """)
    
    # Security Features
    section_header("Security Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Two-Layer Security**
        
        1. **Password (Encryption Layer)**
           - Encrypts the actual payload
           - Uses AES-256-GCM (industry standard)
           - Provides confidentiality
           - Authentication tag prevents tampering
        
        2. **Stego-Key (Positioning Layer)**
           - Determines embedding positions
           - Deterministic but unpredictable
           - Without correct key, data appears random
           - Security through obscurity
        """)
    
    with col2:
        st.markdown("""
        **Protection Against**
        
        - Wrong Password: Authentication failure
        - Wrong Stego-Key: Invalid magic bytes
        - Data Tampering: GCM tag verification
        - Brute Force: PBKDF2 with 600k iterations
        - Statistical Analysis: Random positioning
        - Visual Detection: Imperceptible changes
        """)
    
    # Use Cases
    section_header("Use Cases")
    
    st.markdown("""
    **Educational Applications**
    - Learn steganography techniques
    - Understand cryptographic principles
    - Study LSB embedding methods
    - Analyze steganalysis techniques
    
    **Research & Development**
    - Test steganography algorithms
    - Evaluate quality metrics
    - Compare embedding methods
    - Study capacity vs quality trade-offs
    
    **Privacy & Security**
    - Covert communication
    - Digital watermarking
    - Copyright protection
    - Data hiding for research
    
    **Note:** This is an educational project. For production security applications,
    additional security measures and professional audit are recommended.
    """)
    
    # Technical Stack
    section_header("Technical Stack")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Frontend**
        - Framework: Streamlit
        - Language: Python 3.11
        - UI Components: Custom theme
        - Navigation: Multipage app
        
        **Backend**
        - Cryptography: cryptography library
        - Image Processing: Pillow (PIL)
        - Numerics: NumPy
        - Testing: pytest
        """)
    
    with col2:
        st.markdown("""
        **Security Libraries**
        - AES-GCM: cryptography.hazmat
        - PBKDF2: cryptography.hazmat
        - Random: secrets module
        - Hashing: hashlib (SHA-256)
        
        **Analysis Tools**
        - Metrics: Custom implementation
        - Histogram: Pillow + NumPy
        - LSB Plane: NumPy array operations
        - XLSX Export: openpyxl
        """)
    
    # Project Team
    section_header("Project Team")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Azhar**  
        247006111168
        
        **Responsibilities:**
        - UI/UX Design
        - Streamlit Integration
        - Pipeline Coordination
        - Demo Preparation
        """)
    
    with col2:
        st.markdown("""
        **Naufal**  
        247006111158
        
        **Responsibilities:**
        - Steganography Core
        - LSB Implementation
        - Container Format
        - Position Generator
        """)
    
    with col3:
        st.markdown("""
        **Hana**  
        247006111170
        
        **Responsibilities:**
        - Cryptography Module
        - Quality Metrics
        - Analysis Tools
        - Testing Matrix
        """)
    
    # Academic Information
    section_header("Academic Information")
    
    st.markdown("""
    **Institution:** Universitas Siliwangi  
    **Course:** Keamanan Informasi  
    **Project Type:** UTS Assignment  
    **Topic:** Aplikasi Steganografi (Topic B)
    
    **AI Disclosure:** This project was developed with AI assistance for code 
    generation, debugging, and documentation. All team members understand and 
    can explain the implemented code and algorithms.
    """)
    
    # Limitations & Disclaimers
    section_header("Limitations & Disclaimers")
    
    st.markdown("""
    **Known Limitations**
    - Only supports lossless formats (PNG/BMP)
    - JPEG compression destroys embedded data
    - Large payloads may reduce image quality
    - Stego-key security relies on obscurity
    
    **Disclaimers**
    - Not intended for production security use without audit
    - Educational project for learning purposes
    - No warranty for data security or integrity
    - Users responsible for legal and ethical use
    
    **Best Practices**
    - Use strong, unique passwords
    - Keep stego-key confidential
    - Don't modify stego images
    - Test recovery before relying on system
    """)
    
    # Version Information
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Version:** 1.0.0")
    with col2:
        st.markdown("**Build Date:** 2026")
    with col3:
        st.markdown("**License:** Educational")
    
    footer()
