# Stegora 🔒

**Stegora** adalah aplikasi steganografi berbasis web untuk menyisipkan teks atau berkas ke dalam citra PNG/BMP dengan metode **LSB (Least Significant Bit)** dan enkripsi **AES-256-GCM**. Aplikasi ini dikembangkan sebagai proyek UTS mata kuliah Keamanan Informasi di Universitas Siliwangi.

---

## 📚 Fitur Utama

### 🔐 **Sisipkan Pesan**
Menyisipkan teks atau berkas ke dalam citra PNG/BMP menggunakan LSB dan enkripsi AES-256-GCM.

**Fitur Penyisipan:**
- Unggah citra PNG/BMP sebagai citra penutup
- Sisipkan pesan teks atau berkas
- Derivasi kunci berbasis kata sandi dengan PBKDF2-HMAC-SHA-256 (600.000 iterasi)
- Enkripsi terautentikasi AES-256-GCM
- Tentukan posisi penyisipan secara deterministik menggunakan kunci stego
- Periksa kapasitas dan tolak payload yang tidak muat
- Tampilkan MSE dan PSNR untuk membandingkan kualitas citra
- Unduh citra stego hasil penyisipan
- Simpan hingga 10 riwayat penyisipan selama sesi. Riwayat tidak mencatat kata sandi, kunci stego, atau plaintext; citra stego yang disimpan untuk diunduh tetap berisi payload terenkripsi.

### 🔓 **Ekstrak Pesan**
Mengekstrak pesan dari citra stego menggunakan kata sandi dan kunci stego yang benar.

**Fitur Ekstraksi:**
- Unggah citra stego PNG/BMP
- Regenerasi posisi bit dari kunci stego
- Validasi header kontainer STGR
- Dekripsi AES-256-GCM dan verifikasi tag autentikasi
- Tampilkan pesan atau unduh berkas hasil ekstraksi

### 📊 **Analisis Citra**
Membandingkan citra penutup dan citra stego serta menguji dampak penyimpanan ulang JPEG.

**Pilihan analisis:**
- **MSE & PSNR**: Ukur perubahan dan kualitas citra setelah penyisipan
- **Perbandingan Histogram**: Bandingkan distribusi RGB; tampilkan rata-rata selisih, selisih maksimum, dan jarak chi-square histogram
- **Visualisasi LSB yang Ditingkatkan**: Tampilkan bidang LSB citra stego
- **Uji Kerapuhan JPEG**: Simpan ulang citra stego sebagai JPEG kualitas 90, lalu coba ekstraksi dengan kredensial dari sesi Embed yang sama

Jarak chi-square di halaman ini adalah metrik perbandingan histogram, bukan uji signifikansi statistik atau p-value.

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
├── app.py                          # Titik masuk aplikasi Streamlit
├── requirements.txt                # Dependensi Python
├── pytest.ini                      # Konfigurasi pytest
│
├── frontend/                       # Lapisan antarmuka (Streamlit)
│   ├── pages/
│   │   ├── embed.py               # Halaman penyisipan dan riwayat
│   │   ├── extract.py             # Halaman ekstraksi
│   │   ├── analyze.py             # Analisis kualitas, histogram, LSB, JPEG
│   │   └── about.py               # Informasi aplikasi
│   └── ui/
│       ├── components.py          # Komponen antarmuka yang dapat digunakan ulang
│       ├── state.py               # Pengelolaan status sesi dan riwayat
│       └── theme.py               # Konfigurasi tema
│
├── backend/                        # Lapisan logika aplikasi
│   ├── crypto/
│   │   ├── pbkdf2.py             # Derivasi kunci (PBKDF2)
│   │   └── aes_gcm.py            # Enkripsi/dekripsi AES-256-GCM
│   ├── stego/
│   │   ├── capacity.py           # Perhitungan kapasitas
│   │   ├── container.py          # Penanganan format kontainer
│   │   ├── positions.py          # Posisi PRNG deterministik
│   │   └── lsb.py                # Inti penyisipan/ekstraksi LSB
│   ├── image/
│   │   ├── io.py                 # Operasi masukan/keluaran citra
│   │   └── metrics.py            # Perhitungan MSE/PSNR
│   └── pipeline.py                # Integrasi alur utama
│
├── stegora/                        # Perangkat analisis
│   └── analysis/
│       ├── histogram.py           # Visualisasi histogram RGB
│       ├── lsb_plane.py          # Ekstraksi bidang LSB
│       ├── robustness.py         # Pengujian ketahanan
│       ├── testing_matrix.py     # Matriks pengujian
│       └── xlsx_export.py        # Utilitas ekspor hasil ke Excel
│
├── tests/                          # Kumpulan tes (pytest)
│   ├── test_pipeline.py           # Tes pipeline end-to-end
│   ├── test_required_matrix.py    # Matriks 5 citra × 3 ukuran muatan data
│   ├── test_robustness.py         # Ketahanan JPEG dan serangan
│   ├── test_embedding_history.py  # Pengujian riwayat penyisipan
│   └── ...
│
├── test_images/                    # Data uji (contoh PNG/BMP)
├── test_t18_images/                # Lima citra untuk matriks pengujian 5×3
├── .streamlit/                     # Konfigurasi Streamlit
│   └── config.toml                # Konfigurasi tema dan server
│
└── docs/                           # Dokumentasi
    ├── ARCHITECTURE.md            # System architecture
    ├── STEGO_SPEC.md             # Steganography specification
    ├── SECURITY.md               # Security guidelines
    └── TESTING_SPEC.md           # Testing requirements
```

---

## 🔐 Keamanan & Spesifikasi Teknis

### **Enkripsi**
- **Algoritma**: AES-256-GCM (Galois/Counter Mode)
- **Derivasi Kunci**: PBKDF2-HMAC-SHA-256 dengan 600.000 iterasi
- **Salt**: 16 byte acak (disimpan di dalam kontainer)
- **Nonce/IV**: 12 byte acak untuk setiap enkripsi
- **Autentikasi**: AEAD dengan tag autentikasi 16 byte

### **Steganografi**
- **Metode**: LSB (Least Significant Bit) embedding
- **Format Gambar**: PNG (lossless), BMP (lossless)
- **Kanal**: RGB; kanal alfa pada RGBA dipertahankan dan tidak digunakan
- **Posisi Penyisipan**: Deterministik menggunakan PRNG dengan seed dari kunci stego
- **Format Kontainer**: Header STGR, panjang metadata, salt, IV, nama berkas, jenis MIME, dan payload terenkripsi

### **Metrik**
- **MSE (Mean Squared Error)**: Rata-rata kuadrat selisih piksel
- **PSNR (Peak Signal-to-Noise Ratio)**: Rasio sinyal terhadap derau puncak dalam dB
- **Kapasitas Mentah**: floor(lebar × tinggi × 3 / 8) byte; kapasitas payload berkurang setelah overhead kontainer dan enkripsi

---

## 📖 Panduan Penggunaan

### **1. Sisipkan Pesan**
1. Buka halaman **Sisipkan**
2. Unggah citra penutup PNG/BMP
3. Pilih **Teks** atau **Berkas**, lalu isi atau unggah muatan data
4. Masukkan kata sandi dan kunci stego (disarankan minimal 8 karakter)
5. Klik **Sisipkan Pesan**, lalu unduh citra stego
6. Riwayat tersedia selama sesi browser aktif. Riwayat menyimpan metadata dan citra stego untuk diunduh kembali, tetapi tidak mencatat kata sandi, kunci stego, atau plaintext secara terpisah

### **2. Ekstrak Pesan**
1. Buka halaman **Ekstrak**
2. Unggah citra stego PNG/BMP
3. Masukkan kata sandi dan kunci stego yang sama seperti saat penyisipan
4. Klik **Ekstrak Pesan**
5. Salin teks yang dipulihkan atau unduh berkas hasil ekstraksi

### **3. Analisis Citra**
1. Buka halaman **Analisis**
2. Unggah citra penutup dan citra stego dengan dimensi yang sama
3. Pilih satu atau beberapa opsi: MSE & PSNR, Perbandingan Histogram, Visualisasi LSB yang Ditingkatkan, atau Uji Kerapuhan JPEG
4. Untuk Uji Kerapuhan JPEG, lakukan penyisipan terlebih dahulu dan jalankan analisis pada sesi browser yang sama agar kredensial tersedia
5. Klik **Analisis** dan baca hasil aktual yang ditampilkan

---

## 👥 Tim Pengembang

| Nama | NIM | Peran |
|------|-----|------|
| **Azhar** | 247006111168 | UI/UX dan integrasi sistem |
| **Naufal** | 247006111158 | Inti steganografi dan algoritma LSB |
| **Hana** | 247006111170 | Kriptografi dan perangkat analisis |

---

## 🎓 Konteks Akademik

Proyek ini dikembangkan untuk memenuhi **Ujian Tengah Semester (UTS)** mata kuliah **Keamanan Informasi** di **Universitas Siliwangi** tahun 2026.

**Topik**: Steganografi LSB dengan enkripsi AES-GCM
**Dosen**: Ir. Alam Rahmatulloh, S.T., M.T., MCE., IPM
**Semester**: Semester 5, 2026

---
## 📄 Dokumentasi Teknis

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arsitektur sistem dan pola desain
- **[STEGO_SPEC.md](docs/STEGO_SPEC.md)** - Spesifikasi lengkap algoritma steganografi
- **[SECURITY.md](docs/SECURITY.md)** - Panduan keamanan dan model ancaman
- **[TESTING_SPEC.md](docs/TESTING_SPEC.md)** - Spesifikasi pengujian

---

## 🧪 Hasil Pengujian

Hasil pengujian terakhir: **369 tes lulus**. Cakupan kode tidak dicantumkan karena belum diukur pada pengujian terakhir.

**Kategori Tes:**
- ✅ Kriptografi (PBKDF2, AES-GCM)
- ✅ Steganografi (penyisipan dan ekstraksi LSB)
- ✅ Operasi citra (I/O dan metrik)
- ✅ Analisis (histogram RGB, jarak chi-square, visualisasi LSB)
- ✅ Ketahanan JPEG: citra stego disimpan ulang sebagai JPEG lalu diuji ekstraksinya
- ✅ Matriks 5 citra × 3 ukuran muatan data: pemeriksaan MSE, PSNR, ekstraksi, dan kecocokan data
- ✅ Riwayat penyisipan sesi: pembatasan jumlah, privasi kredensial, dan unduhan ulang
- ✅ Pipeline end-to-end: penyisipan → ekstraksi

---

## 📝 Lisensi

© 2026 Tim Stegora - Universitas Siliwangi
Proyek akademik - Hak cipta dilindungi

---

**Dibangun dengan Python, Streamlit, Pillow, dan cryptography**
