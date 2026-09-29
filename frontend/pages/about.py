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
        "Tentang Stegora",
        "Aplikasi steganografi dengan enkripsi AES-256-GCM"
    )
    
    # System Overview
    section_header("Gambaran Sistem")
    
    st.markdown("""
    **Stegora** adalah aplikasi steganografi berbasis web yang dirancang untuk 
    menyembunyikan pesan atau berkas di dalam citra PNG/BMP menggunakan teknik 
    **LSB RGB 1-bit** (bit paling rendah) dengan enkripsi **AES-256-GCM**.
    
    Sistem ini menggabungkan steganografi dan kriptografi untuk menyediakan 
    dua lapis keamanan: enkripsi muatan data (payload) dan pengacakan posisi penyisipan
    menggunakan PRNG deterministik.

    Halaman Sisipkan juga menyediakan riwayat hingga 10 hasil selama sesi aktif.
    Riwayat menyimpan metadata dan citra stego untuk diunduh kembali, tetapi tidak
    mencatat kata sandi, kunci stego, atau plaintext secara terpisah.
    """)
    
    # Technical Specifications
    section_header("Spesifikasi Teknis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Kriptografi**
        - Algoritma: AES-256-GCM
        - Derivasi Kunci: PBKDF2-HMAC-SHA-256
        - Iterasi: 600.000
        - Salt: 16 byte (acak untuk setiap enkripsi)
        - IV/Nonce: 12 byte (acak untuk setiap enkripsi)
        - Tag Autentikasi: 16 byte (otomatis)
        
        **Steganografi**
        - Metode: Penyisipan LSB RGB 1-bit
        - Kanal: RGB saja (alfa dipertahankan)
        - Pembangkitan Posisi: PRNG deterministik
        - Seed Posisi: SHA-256(kunci stego)
        - Format Kontainer: Biner STGR
        - Format yang Didukung: PNG, BMP
        """)
    
    with col2:
        st.markdown("""
        **Metrik Kualitas**
        - MSE: Rata-rata Kuadrat Galat
        - PSNR: Rasio Sinyal terhadap Derau Puncak
        - Target: PSNR ≥ 30 dB
        - LSB 1-bit umumnya: 50–60 dB
        
        **Alat Analisis**
        - Perbandingan Histogram RGB
        - Visualisasi Bidang LSB yang Ditingkatkan
        - Pengujian Kerapuhan JPEG
        - Jarak chi-square histogram
        """)
    
    # How It Works
    section_header("Cara Kerja")
    
    st.markdown("""
    ### Proses Penyisipan
    
     1. **Validasi Masukan**
         - Memvalidasi format citra penutup (PNG/BMP)
         - Menghitung kapasitas yang tersedia
        - Memeriksa batas ukuran muatan data
    
     2. **Persiapan Kriptografi**
         - Membuat salt acak (16 byte)
         - Menurunkan kunci enkripsi dengan PBKDF2 (600 ribu iterasi)
         - Membuat IV acak (12 byte)
        - Mengenkripsi muatan data dengan AES-256-GCM
    
     3. **Pembuatan Kontainer**
         - Membuat header STGR dengan byte penanda
         - Menambahkan metadata (salt, IV, nama berkas, jenis MIME)
        - Mengemas muatan data terenkripsi
    
     4. **Pembangkitan Posisi**
         - Meng-hash kunci stego dengan SHA-256
         - Memberi seed pada PRNG deterministik
         - Membuat posisi kanal RGB yang unik
    
     5. **Penyisipan LSB**
         - Mengubah kontainer menjadi aliran bit
         - Mengubah LSB pada kanal RGB yang dipilih
         - Mempertahankan kanal alfa sepenuhnya
    
     6. **Penilaian Kualitas**
         - Menghitung MSE antara citra penutup dan stego
         - Menghitung metrik kualitas PSNR
         - Menghasilkan citra stego
    
    ---
    
    ### Proses Ekstraksi
    
     1. **Pembangkitan Ulang Posisi**
         - Meng-hash kunci stego dengan SHA-256 seperti saat penyisipan
         - Menghasilkan kembali urutan posisi yang sama
    
     2. **Ekstraksi LSB**
         - Membaca LSB dari posisi yang ditentukan
         - Menyusun kembali aliran bit
         - Menguraikannya menjadi byte
    
     3. **Penguraian Kontainer**
         - Memvalidasi byte penanda STGR
         - Mengambil header dan metadata
        - Mendapatkan salt, IV, dan muatan data terenkripsi
    
     4. **Dekripsi**
         - Menurunkan kunci dari kata sandi dan salt hasil ekstraksi
         - Mendekripsi dengan AES-GCM menggunakan IV hasil ekstraksi
         - Memverifikasi tag autentikasi
    
     5. **Pemulihan Payload**
         - Mengembalikan teks atau berkas asli
         - Memulihkan data byte demi byte

    ### Uji Kerapuhan JPEG

    1. Unggah citra penutup dan citra stego yang sudah disimpan sebelumnya.
    2. Pilih **Uji Kerapuhan JPEG** pada halaman Analisis.
    3. Masukkan kata sandi dan kunci stego yang digunakan saat penyisipan.
    4. Aplikasi memastikan pesan dapat diekstrak dari citra stego asli.
    5. Aplikasi menyimpan ulang citra stego sebagai JPEG kualitas 90, lalu mencoba ekstraksi kembali.

    JPEG berhasil dibuat; kompresinya dapat mengubah bit LSB sehingga pesan tidak dapat dipulihkan.
    Kredensial dapat dimasukkan langsung pada halaman Analisis, jadi penyisipan ulang tidak diperlukan.
    """)
    
    # Security Features
    section_header("Fitur Keamanan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Keamanan Dua Lapis**
        
          1. **Kata Sandi (Lapisan Enkripsi)**
              - Mengenkripsi muatan data
              - Menggunakan AES-256-GCM
              - Menjaga kerahasiaan
              - Tag autentikasi mendeteksi perubahan data
        
          2. **Kunci Stego (Lapisan Posisi)**
              - Menentukan posisi penyisipan
              - Hasilnya deterministik, tetapi sulit ditebak
              - Tanpa kunci yang benar, data tampak acak
        """)
    
    with col2:
        st.markdown("""
        **Perlindungan dari**
        
        - Kata sandi salah: Autentikasi gagal
        - Kunci stego salah: Byte penanda tidak valid
        - Perubahan data: Diverifikasi oleh tag GCM
        - Brute force: PBKDF2 dengan 600 ribu iterasi
        - Analisis histogram: Perubahan distribusi RGB dapat dibandingkan
        - Deteksi visual: Perubahan dibuat nyaris tak terlihat
        """)
    
    # Use Cases
    section_header("Kegunaan")
    
    st.markdown("""
    **Pendidikan**
    - Mempelajari teknik steganografi
    - Memahami prinsip kriptografi
    - Mempelajari metode penyisipan LSB
    - Menganalisis teknik steganalisis
    
    **Riset dan Pengembangan**
    - Menguji algoritma steganografi
    - Mengevaluasi metrik kualitas
    - Membandingkan metode penyisipan
    - Mempelajari kompromi kapasitas dan kualitas
    
    **Privasi dan Keamanan**
    - Komunikasi tersembunyi
    - Penanda air digital
    - Perlindungan hak cipta
    - Penyembunyian data untuk riset
    
    **Catatan:** Proyek ini dibuat untuk keperluan pendidikan. Penggunaan untuk
    keamanan produksi memerlukan perlindungan tambahan dan audit profesional.
    """)
    
    # Technical Stack
    section_header("Teknologi yang Digunakan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Antarmuka**
        - Kerangka kerja: Streamlit
        - Bahasa pemrograman: Python 3.11
        - Komponen UI: Tema khusus
        - Navigasi: Aplikasi multi-halaman
        
        **Bagian Server (Backend)**
        - Kriptografi: pustaka cryptography
        - Pemrosesan citra: Pillow (PIL)
        - Komputasi numerik: NumPy
        - Pengujian: pytest
        """)
    
    with col2:
        st.markdown("""
        **Pustaka Keamanan**
        - AES-GCM: cryptography.hazmat
        - PBKDF2: cryptography.hazmat
        - Pengacakan: modul secrets
        - Hash: hashlib (SHA-256)
        
        **Alat Analisis**
        - Metrik: Implementasi khusus
        - Histogram: Pillow + NumPy
        - Bidang LSB: Operasi larik NumPy
        - Pengujian JPEG: Pillow dan pipeline ekstraksi
        """)
    
    # Project Team
    section_header("Tim Proyek")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Azhar**  
        247006111168
        
        **Tanggung Jawab:**
        - Desain UI/UX
        - Integrasi Streamlit
        - Koordinasi pipeline
        - Persiapan demo
        """)
    
    with col2:
        st.markdown("""
        **Naufal**  
        247006111158
        
        **Tanggung Jawab:**
        - Inti steganografi
        - Implementasi LSB
        - Format kontainer
        - Pembangkitan posisi
        """)
    
    with col3:
        st.markdown("""
        **Hana**  
        247006111170
        
        **Tanggung Jawab:**
        - Modul kriptografi
        - Metrik kualitas
        - Alat analisis
        - Matriks pengujian
        """)
    
    # Academic Information
    section_header("Informasi Akademik")
    
    st.markdown("""
    **Institusi:** Universitas Siliwangi  
    **Mata Kuliah:** Keamanan Informasi  
    **Jenis Proyek:** Tugas UTS  
    **Topik:** Aplikasi Steganografi (Topik B)
    
    **Penggunaan AI:** Proyek ini dikembangkan dengan bantuan AI untuk membuat kode,
    melakukan debugging, dan menyusun dokumentasi. Seluruh anggota tim memahami dan
    dapat menjelaskan kode serta algoritma yang diterapkan.
    """)

    st.markdown("""
    **Matriks pengujian otomatis:** 5 citra PNG × 3 ukuran muatan data (32 B, 512 B,
    dan 2 KB). Setiap kombinasi memeriksa ekstraksi byte-per-byte serta nilai MSE dan PSNR.
    Matriks ini dijalankan melalui pytest, bukan sebagai menu interaktif di halaman web.
    """)
    
    # Limitations & Disclaimers
    section_header("Batasan dan Penafian")
    
    st.markdown("""
    **Batasan yang Diketahui**
    - Hanya mendukung format tanpa kehilangan data (PNG/BMP)
    - Kompresi JPEG merusak data yang disisipkan
    - Muatan data berukuran besar dapat menurunkan kualitas citra
    - Keamanan kunci stego bergantung pada kerahasiaan kunci
    
    **Penafian**
    - Tidak ditujukan untuk penggunaan keamanan produksi tanpa audit
    - Proyek pendidikan untuk keperluan pembelajaran
    - Tidak ada jaminan atas keamanan atau integritas data
    - Pengguna bertanggung jawab atas penggunaan yang legal dan etis
    
    **Praktik Terbaik**
    - Gunakan kata sandi yang kuat dan unik
    - Jaga kerahasiaan kunci stego
    - Jangan mengubah citra stego
    - Uji pemulihan sebelum mengandalkan sistem
    """)
    
    # Version Information
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Versi:** 1.0.0")
    with col2:
        st.markdown("**Tahun Pembuatan:** 2026")
    with col3:
        st.markdown("**Lisensi:** Pendidikan")
    
    footer()
