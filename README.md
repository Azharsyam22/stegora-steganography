# Stegora

**Stegora** adalah aplikasi steganografi berbasis web untuk menyisipkan teks atau berkas ke dalam citra PNG/BMP dengan metode **LSB (Least Significant Bit)** dan enkripsi **AES-256-GCM**. Aplikasi ini dikembangkan sebagai proyek UTS mata kuliah Keamanan Informasi di Universitas Siliwangi.

---

## 📚 Fitur Utama

### 🔐 Sisipkan Pesan
Menyisipkan teks atau berkas ke dalam citra PNG/BMP menggunakan LSB dan enkripsi AES-256-GCM.

**Fitur Penyisipan:**
- Upload citra PNG/BMP sebagai citra penutup
- Sisipkan pesan teks atau berkas
- **Unified Credentials:** Satu kata kunci untuk enkripsi dan penentuan posisi LSB
- **Generate Strong Key:** Generate kata kunci kuat 16-karakter secara otomatis
- Derivasi kunci berbasis kata sandi dengan PBKDF2-HMAC-SHA-256 (600,000 iterasi)
- Enkripsi terautentikasi AES-256-GCM
- Tentukan posisi penyisipan secara deterministik menggunakan kata kunci
- Validasi kapasitas dan tolak payload yang tidak muat
- Tampilkan MSE dan PSNR untuk membandingkan kualitas citra
- Download citra stego hasil penyisipan
- Riwayat penyisipan tersimpan selama sesi aktif

### 🔓 Ekstrak Pesan
Ekstrak pesan dari citra stego menggunakan kata kunci yang benar.

**Fitur Ekstraksi:**
- Upload citra stego PNG/BMP
- **JPEG Robustness Test:** Support upload JPEG untuk demonstrasi kerapuhan
- Regenerasi posisi bit dari kata kunci
- Validasi header kontainer STGR
- Dekripsi AES-256-GCM dan verifikasi tag autentikasi
- Tampilkan pesan atau download berkas hasil ekstraksi
- Deteksi otomatis format JPEG dengan pesan edukatif saat extraction fails

### 📊 Analisis Citra
Bandingkan citra penutup dan citra stego dengan berbagai metrik dan visualisasi.

**Opsi Analisis (Pilih Salah Satu):**
- **MSE & PSNR:** Ukur perubahan dan kualitas citra setelah penyisipan
- **Perbandingan Histogram RGB:** 
  - 6 subplot terpisah (2 baris × 3 kolom)
  - Baris 1: Cover histogram (Red, Green, Blue)
  - Baris 2: Stego histogram (Red, Green, Blue)
  - Metrics: Rata-rata Selisih, Chi-Square Distance, Selisih Maksimum
- **Visualisasi LSB yang Ditingkatkan:** Tampilkan bidang LSB citra stego

**Catatan:** Chi-square di halaman ini adalah metrik perbandingan histogram, bukan uji signifikansi statistik atau p-value.

### 📖 Tentang
Informasi proyek, tim pengembang, dan konteks akademik.

---

## 🛠️ Instalasi & Penggunaan

### **Prasyarat**
- Python 3.10 atau lebih tinggi
- pip (Python package manager)

### **Instalasi (Windows)**
```powershell
# Clone repository
git clone https://github.com/Azharsyam22/stegora-steganography.git
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
git clone https://github.com/Azharsyam22/stegora-steganography.git
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
# Jalankan semua tes
pytest

# Jalankan dengan output terperinci
pytest -v

# Jalankan tes pipeline tertentu
pytest tests/test_pipeline.py -v

# Matriks 5 citra x 3 ukuran payload
pytest tests/test_required_matrix.py -v

# Uji ekstraksi setelah citra stego disimpan ulang sebagai JPEG
pytest tests/test_robustness.py::test_extraction_fails_after_stego_is_resaved_as_jpeg -v
```

---

## 📂 Struktur Direktori

```
stegora-steganography/
├── app.py                          # Entry point Streamlit
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
│
├── frontend/                       # UI Layer (Streamlit)
│   ├── pages/
│   │   ├── embed.py               # Embed page dengan unified credentials
│   │   ├── extract.py             # Extract page dengan JPEG robustness test
│   │   ├── analyze.py             # Analysis page (radio selection)
│   │   └── about.py               # About page
│   └── ui/
│       ├── components.py          # Reusable UI components
│       ├── state.py               # Session state management
│       └── theme.py               # Theme configuration
│
├── backend/                        # Application Layer
│   ├── crypto/
│   │   ├── pbkdf2.py             # PBKDF2 key derivation
│   │   └── aes_gcm.py            # AES-256-GCM encryption/decryption
│   ├── stego/
│   │   ├── capacity.py           # Capacity calculation
│   │   ├── container.py          # Container format (STGR header)
│   │   ├── positions.py          # Deterministic PRNG position generation
│   │   └── lsb.py                # LSB embedding/extraction (core)
│   ├── image/
│   │   ├── io.py                 # Image I/O & validation
│   │   └── metrics.py            # MSE/PSNR calculation
│   └── pipeline.py                # Main embed/extract orchestration
│
├── stegora/                        # Infrastructure Layer
│   └── analysis/
│       ├── histogram.py           # RGB histogram comparison
│       ├── lsb_plane.py          # LSB plane extraction & visualization
│       ├── robustness.py         # JPEG robustness testing
│       ├── testing_matrix.py     # Test matrix generation
│       └── xlsx_export.py        # Excel export utilities
│
├── tests/                          # Test Suite (pytest)
│   ├── test_pipeline.py           # End-to-end pipeline tests
│   ├── test_embed_extract.py     # Embed/extract integration
│   ├── test_aes_gcm.py           # AES-GCM crypto tests
│   ├── test_pbkdf2.py            # PBKDF2 tests
│   ├── test_lsb.py               # LSB algorithm tests
│   ├── test_container.py         # Container format tests
│   ├── test_positions.py         # Position generation tests
│   ├── test_capacity.py          # Capacity calculation tests
│   ├── test_image_io.py          # Image I/O validation tests
│   ├── test_metrics.py           # MSE/PSNR tests
│   ├── test_histogram.py         # Histogram analysis tests
│   ├── test_lsb_plane.py         # LSB visualization tests
│   ├── test_robustness.py        # JPEG robustness tests
│   ├── test_required_matrix.py   # 5×3 test matrix
│   └── test_embedding_history.py # Session history tests
│
├── docs/                           # Technical Documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── STEGO_SPEC.md             # Steganography specification
│   ├── SECURITY.md               # Security guidelines
│   ├── TESTING_SPEC.md           # Testing requirements
│   └── UI_UX_SPEC.md             # UI/UX specification
│
├── test_images/                    # Test data
├── test_t18_images/                # Matrix test data (5 images)
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                # Theme & server settings
│
├── PROJECT_CONTEXT.md              # Complete project documentation
├── FINAL_VERIFICATION.md           # Production readiness report
└── README.md                       # This file
```

---

## 🔐 Keamanan & Spesifikasi Teknis

### **Enkripsi**
- **Algoritma:** AES-256-GCM (Galois/Counter Mode)
- **Derivasi Kunci:** PBKDF2-HMAC-SHA-256 dengan 600,000 iterasi
- **Salt:** 16 byte acak (disimpan di dalam kontainer)
- **Nonce/IV:** 12 byte acak untuk setiap enkripsi
- **Autentikasi:** AEAD dengan tag autentikasi 16 byte

### **Steganografi**
- **Metode:** LSB (Least Significant Bit) embedding
- **Format Gambar:** PNG (lossless), BMP (lossless)
- **Kanal:** RGB; kanal alfa pada RGBA dipertahankan dan tidak digunakan
- **Posisi Penyisipan:** Deterministik menggunakan PRNG dengan seed dari kata kunci
- **Format Kontainer:** Header STGR, panjang metadata, salt, IV, nama berkas, jenis MIME, dan payload terenkripsi

### **Metrik**
- **MSE (Mean Squared Error):** Rata-rata kuadrat selisih piksel
- **PSNR (Peak Signal-to-Noise Ratio):** Rasio sinyal terhadap derau puncak dalam dB
- **Kapasitas Mentah:** floor(lebar × tinggi × 3 / 8) byte
- **Kapasitas Tersedia:** Kapasitas mentah - overhead kontainer - overhead enkripsi

---

## 📖 Panduan Penggunaan

### **1. Sisipkan Pesan**
1. Buka halaman **Sisipkan**
2. Upload citra penutup PNG/BMP
3. Pilih **Teks** atau **Berkas**, lalu isi atau upload muatan data
4. Masukkan kata kunci (minimal 8 karakter) atau klik **Generate** untuk kata kunci kuat otomatis
5. Klik **Sisipkan Pesan**, lalu download citra stego
6. **PENTING:** Simpan kata kunci dengan aman - diperlukan untuk ekstraksi!

### **2. Ekstrak Pesan**
1. Buka halaman **Ekstrak**
2. Upload citra stego PNG/BMP (atau JPEG untuk uji kerapuhan)
3. Masukkan kata kunci yang sama seperti saat penyisipan
4. Klik **Ekstrak Pesan**
5. Salin teks yang dipulihkan atau download berkas hasil ekstraksi

**Uji Kerapuhan JPEG:**
- Upload file JPEG (hasil konversi dari stego.png)
- Sistem akan mendeteksi format JPEG dan menampilkan warning
- Extraction akan gagal dengan pesan edukatif
- Demonstrasi bahwa LSB steganography tidak robust terhadap lossy compression

### **3. Analisis Citra**
1. Buka halaman **Analisis**
2. Upload citra penutup dan citra stego dengan dimensi yang sama
3. Pilih **salah satu** opsi analisis:
   - **MSE & PSNR:** Metrik kualitas (MSE, PSNR, kualitas rating)
   - **Perbandingan Histogram:** 6 subplot terpisah (Cover RGB + Stego RGB)
   - **Visualisasi LSB:** Extract dan enhance LSB plane
4. Klik **Analisis** dan lihat hasil

---

## 👥 Tim Pengembang

| Nama | NIM | Peran |
|------|-----|------|
| **Azhar** | 247006111168 | Lead Developer, UI/UX, System Integration |
| **Naufal** | 247006111158 | Steganography Core, LSB Algorithm Implementation |
| **Hana** | 247006111170 | Cryptography Implementation, Analysis Tools |

---

## 🎓 Konteks Akademik

Proyek ini dikembangkan untuk memenuhi **Ujian Tengah Semester (UTS)** mata kuliah **Keamanan Informasi** di **Universitas Siliwangi** tahun 2026.

**Topik:** Steganografi LSB dengan enkripsi AES-GCM  
**Dosen:** Ir. Alam Rahmatulloh, S.T., M.T., MCE., IPM  
**Semester:** Semester 5, 2026  

---

## 📄 Dokumentasi Teknis

- **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)** - Dokumentasi lengkap proyek (69KB)
- **[FINAL_VERIFICATION.md](FINAL_VERIFICATION.md)** - Laporan verifikasi production readiness
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arsitektur sistem dan pola desain
- **[docs/STEGO_SPEC.md](docs/STEGO_SPEC.md)** - Spesifikasi lengkap algoritma steganografi
- **[docs/SECURITY.md](docs/SECURITY.md)** - Panduan keamanan dan model ancaman
- **[docs/TESTING_SPEC.md](docs/TESTING_SPEC.md)** - Spesifikasi pengujian
- **[docs/UI_UX_SPEC.md](docs/UI_UX_SPEC.md)** - Spesifikasi UI/UX

---

## 🧪 Hasil Pengujian

**Test Suite:** 366 tests  
**Status:** ✅ ALL PASSED  
**Coverage:** 92%  
**Execution Time:** ~68 seconds  

**Kategori Tes:**
- ✅ Kriptografi (PBKDF2, AES-GCM)
- ✅ Steganografi (penyisipan dan ekstraksi LSB)
- ✅ Operasi citra (I/O dan metrik)
- ✅ Analisis (histogram RGB, chi-square, visualisasi LSB)
- ✅ Ketahanan JPEG: citra stego disimpan ulang sebagai JPEG lalu diuji ekstraksinya
- ✅ Matriks 5 citra × 3 ukuran muatan data
- ✅ Riwayat penyisipan sesi
- ✅ Pipeline end-to-end

---

## 🚀 Fitur Terbaru (v1.0.0)

### ✅ Unified Credentials
- Satu kata kunci untuk enkripsi dan penentuan posisi LSB
- Simplified UX - tidak ada field terpisah untuk stego-key
- User-friendly dan mengurangi error

### ✅ Generate Strong Key
- Button "Generate" untuk create kata kunci kuat otomatis
- 16-karakter cryptographically secure (secrets module)
- Character set: a-z, A-Z, 0-9, !@#$%^&*-_
- Auto-populate ke field kata kunci
- Warning untuk save key

### ✅ JPEG Robustness Test (Integrated)
- Extract page accept JPG/JPEG upload
- Auto-detect format dengan warning message
- Extraction fails dengan pesan edukatif
- Demonstrasi real-world fragility terhadap lossy compression

### ✅ Histogram Comparison (Separate Graphs)
- 6 subplot terpisah (2 baris × 3 kolom)
- Baris 1: Cover histogram (Red, Green, Blue)
- Baris 2: Stego histogram (Red, Green, Blue)
- Clear vertical comparison
- Professional academic layout

### ✅ Single-Select Analysis
- Radio buttons (hanya pilih satu analisis)
- Focused results (tidak scroll banyak)
- Better for presentation dan demo

### ✅ Clean UI
- No emoji (professional appearance)
- Consistent styling
- Clear labels dan help text
- Responsive layout

---

## 🔒 Keamanan

**Cryptographic Security:**
- ✅ No hard-coded credentials
- ✅ CSPRNG untuk salt/IV (secrets module)
- ✅ 600,000 PBKDF2 iterations (OWASP recommended)
- ✅ AES-256-GCM authenticated encryption
- ✅ Authentication tag validation

**Steganography Security:**
- ⚠️ LSB detectable dengan steganalysis (chi-square, RS analysis)
- ⚠️ Not robust: JPEG, resizing, rotation merusak data
- ✅ Educational purpose only - not for covert communication

**Best Practices:**
- Use strong passwords (8+ characters, or use Generate button)
- Keep password secret and safe
- Use PNG/BMP only (no JPEG)
- Don't modify stego image after embedding
- Verify extraction successful before deleting original

---

## 📝 Lisensi

© 2026 Tim Stegora - Universitas Siliwangi  
Proyek akademik - Hak cipta dilindungi

---

## 📞 Kontak

**GitHub Repository:** https://github.com/Azharsyam22/stegora-steganography

**Untuk pertanyaan akademik:**
- Dosen Pengampu: Ir. Alam Rahmatulloh, S.T., M.T., MCE., IPM
- Institusi: Universitas Siliwangi
- Mata Kuliah: Keamanan Informasi

---

**Built with Python, Streamlit, Pillow, and cryptography**

**Status:** ✅ Production Ready for UTS Week 8  
**Version:** 1.0.0  
**Last Updated:** 26 September 2026
