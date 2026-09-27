# Stegora 🔒

**Stegora** adalah aplikasi steganografi berbasis web yang menggunakan metode **LSB (Least Significant Bit)** dengan enkripsi **AES-256-GCM** untuk menyembunyikan pesan rahasia di dalam gambar. Aplikasi ini dikembangkan sebagai proyek UTS mata kuliah Keamanan Informasi di Universitas Siliwangi.

---

## 📚 Fitur Utama

### 🔐 **Embed (Sembunyikan Pesan)**
Menyembunyikan teks atau file rahasia ke dalam gambar PNG/BMP menggunakan teknik LSB steganografi dengan enkripsi AES-256-GCM.

**Fitur Embed:**
- Upload gambar PNG/BMP sebagai wadah (container)
- Input pesan teks atau upload file untuk disembunyikan
- Password-based key derivation menggunakan PBKDF2 (100,000 iterasi)
- Enkripsi AES-256-GCM dengan authenticated encryption
- Posisi penyisipan bit deterministik berdasarkan stego-key
- Cek kapasitas otomatis sebelum embedding
- Perhitungan MSE dan PSNR untuk analisis kualitas
- Download stego-image hasil embedding

### 🔓 **Extract (Ekstrak Pesan)**
Mengekstrak pesan rahasia dari stego-image menggunakan password dan stego-key yang benar.

**Fitur Extract:**
- Upload stego-image yang sudah berisi pesan tersembunyi
- Input password dan stego-key untuk dekripsi
- Regenerasi posisi bit deterministik dari stego-key
- Validasi container magic bytes
- Dekripsi AES-256-GCM dengan verifikasi authentication tag
- Download pesan hasil ekstraksi (teks/file)
- Demo mode untuk wrong-key educational purpose

### 📊 **Analyze (Analisis Steganalisis)**
Melakukan analisis mendalam terhadap gambar untuk mendeteksi kemungkinan steganografi LSB.

**Fiset Analyze:**
- **Histogram RGB**: Visualisasi distribusi intensitas warna per channel
- **Enhanced LSB Visualization**: Tampilkan pola LSB plane dari setiap color channel
- **Image Quality Metrics**: Perhitungan MSE dan PSNR antara cover image dan stego-image
- **Statistical Analysis**: Deteksi anomali distribusi bit LSB
- **Export Analysis**: Download hasil analisis dalam format XLSX

---

## 🛠️ Instalasi & Penggunaan

### **Prasyarat**
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### **Instalasi (Windows)**
```powershell
# Clone repository
git clone https://github.com/yourusername/stegora-steganography.git
cd stegora-steganography

# Buat virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Instalasi (Linux/macOS)**
```bash
# Clone repository
git clone https://github.com/yourusername/stegora-steganography.git
cd stegora-steganography

# Buat virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Menjalankan Aplikasi**
```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

### **Menjalankan Unit Tests**
```bash
# Run semua test
pytest

# Run dengan output verbose
pytest -v

# Run test spesifik
pytest tests/test_pipeline.py -v
```

---

## 📂 Struktur Direktori

```
stegora-steganography/
├── app.py                          # Entry point aplikasi Streamlit
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
│
├── frontend/                       # UI Layer (Streamlit)
│   ├── pages/
│   │   ├── embed.py               # Halaman Embed
│   │   ├── extract.py             # Halaman Extract
│   │   ├── analyze.py             # Halaman Analyze
│   │   └── about.py               # Halaman About
│   └── ui/
│       ├── components.py          # Reusable UI components
│       ├── state.py               # Session state management
│       └── theme.py               # Color theme configuration
│
├── backend/                        # Business Logic Layer
│   ├── crypto/
│   │   ├── pbkdf2.py             # Key derivation (PBKDF2)
│   │   └── aes_gcm.py            # AES-256-GCM encryption/decryption
│   ├── stego/
│   │   ├── capacity.py           # Capacity calculation
│   │   ├── container.py          # Container format handler
│   │   ├── positions.py          # Deterministic PRNG positions
│   │   └── lsb.py                # LSB embed/extract core
│   ├── image/
│   │   ├── io.py                 # Image I/O operations
│   │   └── metrics.py            # MSE/PSNR calculation
│   └── pipeline.py                # High-level integration pipeline
│
├── stegora/                        # Analysis Tools
│   └── analysis/
│       ├── histogram.py           # RGB histogram visualization
│       ├── lsb_plane.py          # LSB plane extraction
│       ├── robustness.py         # Robustness testing
│       ├── testing_matrix.py     # Comprehensive test matrix
│       └── xlsx_export.py        # Export analysis to Excel
│
├── tests/                          # Test Suite (pytest)
│   ├── test_pipeline.py           # E2E pipeline tests
│   ├── test_crypto.py             # Cryptography tests
│   ├── test_stego.py              # Steganography tests
│   ├── test_analysis.py           # Analysis tools tests
│   └── ...
│
├── test_images/                    # Test data (PNG/BMP samples)
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                # Theme & server config
│
└── docs/                           # Documentation
    ├── ARCHITECTURE.md            # System architecture
    ├── STEGO_SPEC.md             # Steganography specification
    ├── SECURITY.md               # Security guidelines
    └── TESTING_SPEC.md           # Testing requirements
```

---

## 🔐 Keamanan & Spesifikasi Teknis

### **Enkripsi**
- **Algoritma**: AES-256-GCM (Galois/Counter Mode)
- **Key Derivation**: PBKDF2-HMAC-SHA256 dengan 100,000 iterasi
- **Salt**: 16 bytes random (disimpan dalam container)
- **Nonce/IV**: 12 bytes random per encryption
- **Authentication**: AEAD dengan 16-byte authentication tag

### **Steganografi**
- **Metode**: LSB (Least Significant Bit) embedding
- **Format Gambar**: PNG (lossless), BMP (lossless)
- **Channel Support**: RGB, RGBA (alpha channel preserved)
- **Posisi Embedding**: Deterministik berdasarkan PRNG dengan seed dari stego-key
- **Container Format**: Magic bytes + metadata + encrypted payload + checksum

### **Metrics**
- **MSE (Mean Squared Error)**: Rata-rata kuadrat selisih pixel
- **PSNR (Peak Signal-to-Noise Ratio)**: Kualitas gambar dalam dB
- **Capacity**: Maksimum payload = (width × height × channels) / 8 bytes

---

## 📖 Panduan Penggunaan

### **1. Embed Pesan**
1. Buka halaman **Embed**
2. Upload **cover image** (PNG/BMP)
3. Pilih mode pesan: **Text** atau **File**
4. Input **password** dan **stego-key** (min. 8 karakter)
5. Klik **Embed Message**
6. Download **stego-image** hasil embedding

### **2. Extract Pesan**
1. Buka halaman **Extract**
2. Upload **stego-image**
3. Input **password** dan **stego-key** yang sama saat embed
4. Klik **Extract Message**
5. Download pesan hasil ekstraksi

### **3. Analyze Image**
1. Buka halaman **Analyze**
2. Upload **cover image** dan **stego-image**
3. Pilih jenis analisis:
   - Histogram RGB
   - LSB Visualization
   - Image Quality Metrics
4. View hasil analisis atau export ke XLSX

---

## 👥 Tim Pengembang

| Nama | NIM | Role |
|------|-----|------|
| **Azhar** | 247006111168 | UI/UX Development & System Integration |
| **Naufal** | 247006111158 | Steganography Core & LSB Algorithm |
| **Hana** | 247006111170 | Cryptography & Analysis Tools |

---

## 🎓 Konteks Akademik

Proyek ini dikembangkan untuk memenuhi **Ujian Tengah Semester (UTS)** mata kuliah **Keamanan Informasi** di **Universitas Siliwangi** tahun 2026.

**Topik**: Steganografi LSB dengan Enkripsi AES-GCM  
**Dosen**: [Nama Dosen]  
**Semester**: [Semester/Tahun]

---

## 📄 Dokumentasi Teknis

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arsitektur sistem dan design patterns
- **[STEGO_SPEC.md](docs/STEGO_SPEC.md)** - Spesifikasi lengkap algoritma steganografi
- **[SECURITY.md](docs/SECURITY.md)** - Panduan keamanan dan threat model
- **[TESTING_SPEC.md](docs/TESTING_SPEC.md)** - Spesifikasi testing dan test coverage

---

## 🧪 Test Coverage

```
Test Suite: 347 tests
Coverage: 99.1%
E2E Pipeline Tests: 17/17 PASSED
```

**Test Categories:**
- ✅ Cryptography (PBKDF2, AES-GCM)
- ✅ Steganography (LSB embed/extract)
- ✅ Image Operations (I/O, metrics)
- ✅ Analysis Tools (histogram, LSB plane)
- ✅ E2E Pipeline (embed → extract round-trip)

---

## 📝 Lisensi

© 2026 Stegora Team - Universitas Siliwangi  
Academic Project - All Rights Reserved

---

## 📞 Kontak

Untuk pertanyaan atau feedback, silakan hubungi:
- **Email**: [your-email@example.com]
- **GitHub**: [github.com/yourusername]

---

**Built with ❤️ using Python, Streamlit, Pillow, and Cryptography**
