# 📁 Stegora Project Structure

Struktur project yang terorganisir dengan pemisahan jelas antara Frontend (UI) dan Backend (Core Logic).

---

## 📂 Root Directory

```
stegora-steganography/
├── 🎨 FRONTEND (UI Layer)
│   ├── app.py                    # Main entry point Streamlit
│   ├── pages/                    # Streamlit pages (Embed/Extract/Analyze)
│   └── stegora/ui/              # UI components & theme
│
├── ⚙️ BACKEND (Core Logic)
│   └── stegora/
│       ├── crypto/              # Cryptography modules (PBKDF2, AES-GCM)
│       ├── stego/               # Steganography core (LSB, Container, PRNG)
│       ├── image/               # Image I/O & metrics (Pillow wrapper, MSE/PSNR)
│       └── analysis/            # Steganalysis tools (Histogram, Enhanced LSB)
│
├── 🧪 TESTING
│   └── tests/                   # Unit tests & integration tests
│
├── 📖 DOCUMENTATION
│   ├── docs/                    # Additional documentation
│   ├── *.md                     # Project specs & guides
│   └── PROJECT_STRUCTURE.md     # This file
│
└── 🛠️ CONFIG & UTILS
    ├── .streamlit/              # Streamlit config
    ├── test_images/             # Sample images for testing
    ├── requirements.txt         # Python dependencies
    └── pytest.ini               # Test configuration
```

---

## 🎨 FRONTEND Structure

### **`app.py`** - Main Application Entry Point
```python
# Purpose: Streamlit app initialization
# - Configure page settings
# - Apply theme
# - Setup navigation
# - Run selected page
```

### **`pages/`** - Streamlit Pages (User Interface)
```
pages/
├── __init__.py
├── embed.py        # Embed workflow UI (5 steps)
├── extract.py      # Extract workflow UI (4 steps)
└── analyze.py      # Analysis tools UI
```

**Purpose:** User-facing interface untuk setiap fitur
**Dependencies:** Menggunakan `stegora.ui` untuk components, `stegora.image`, `stegora.stego` untuk logic

### **`stegora/ui/`** - UI Components & Theme
```
stegora/ui/
├── __init__.py
├── theme.py        # Color palette & CSS
└── components.py   # Reusable UI components
```

**Purpose:** Reusable UI elements yang dipakai di semua pages
**Contains:**
- `page_title()`, `section_header()`, `muted_text()`
- `card()`, `metric_display()`, `status_badge()`
- `show_progress()`, `show_progress_bar()`

---

## ⚙️ BACKEND Structure

### **`stegora/crypto/`** - Cryptography Modules
```
stegora/crypto/
├── __init__.py
├── pbkdf2.py       # PBKDF2-HMAC-SHA-256 key derivation
└── aes_gcm.py      # AES-256-GCM encryption/decryption
```

**Purpose:** Handle all cryptography operations
**Key Functions:**
- `derive_key(password, salt, iterations)` → 32-byte key
- `encrypt(plaintext, key, iv)` → (ciphertext, tag)
- `decrypt(ciphertext, key, iv, tag)` → plaintext

**Status:**
- ✅ T13 PBKDF2 - **IMPLEMENTED**
- ✅ T14 AES-GCM - **IMPLEMENTED**

---

### **`stegora/stego/`** - Steganography Core
```
stegora/stego/
├── __init__.py
├── capacity.py     # Capacity calculation (W×H×3/8)
├── container.py    # STGR binary container format
├── positions.py    # Keyed deterministic PRNG
├── lsb.py          # LSB embedding operations
└── extraction.py   # LSB extraction operations
```

**Purpose:** Core steganography logic (LSB, positioning, container)

**Key Functions:**
- `calculate_raw_capacity(width, height)` → capacity_dict ✅
- `build_container(payload, metadata)` → bytes ⏳
- `parse_container(data)` → (payload, metadata) ⏳
- `generate_positions(stego_key, image_size, num_bits)` → positions ⏳
- `embed_lsb(image, container_bits, positions)` → stego_image ⏳
- `extract_lsb(stego_image, positions, length)` → container_bits ⏳

**Status:**
- ✅ T07 Capacity - **IMPLEMENTED**
- ⏳ T08 Container - **TO DO (Naufal)**
- ⏳ T09 PRNG - **TO DO (Naufal)**
- ⏳ T10 LSB Embed - **TO DO (Naufal)**
- ⏳ T11 LSB Extract - **TO DO (Naufal)**

---

### **`stegora/image/`** - Image Processing & Metrics
```
stegora/image/
├── __init__.py
├── io.py           # Image I/O, validation (Pillow wrapper)
└── metrics.py      # MSE, PSNR calculations
```

**Purpose:** Image operations & quality metrics (Pillow for I/O only)

**Key Functions:**
- `validate_and_load_cover_image(bytes)` → (image, metadata) ✅
- `validate_image_format(image)` → None or raise ✅
- `get_image_metadata(image)` → metadata_dict ✅
- `calculate_mse(cover, stego)` → float ✅
- `calculate_psnr(cover, stego)` → float ✅

**Status:**
- ✅ T03 Image I/O - **IMPLEMENTED**
- ✅ T15 MSE/PSNR - **IMPLEMENTED**

---

### **`stegora/analysis/`** - Steganalysis Tools
```
stegora/analysis/
├── __init__.py
├── histogram.py    # RGB histogram comparison
├── lsb_plane.py    # Enhanced LSB visualization
└── mbits.py        # m-bit LSB analysis (enrichment)
```

**Purpose:** Analysis & visualization tools untuk steganalysis

**Key Functions:**
- `generate_histogram(image, channel)` → histogram_data ⏳
- `compare_histograms(cover, stego)` → comparison_plot ⏳
- `extract_lsb_plane(image, bit_position)` → lsb_image ⏳
- `analyze_mbits(image, m)` → capacity_psnr_tradeoff ⏳

**Status:**
- ⏳ T16 Histogram/LSB - **TO DO (Hana)**
- ⏳ T19 m-bit - **TO DO (Naufal+Hana)**

---

## 🧪 TESTING Structure

```
tests/
├── __init__.py
├── test_capacity.py              # Capacity calculator tests (16 tests)
├── test_image_io.py              # Image validation tests (15 tests)
├── test_pbkdf2.py                # PBKDF2 tests
├── test_aes_gcm.py               # AES-GCM tests
├── test_metrics.py               # MSE/PSNR tests
├── test_ui_components.py         # UI component tests (9 tests)
└── test_embed_extract_pages.py   # Page structure tests (9 tests)
```

**Total:** 53 tests passing

**Coverage:**
- ✅ Image validation (format, mode)
- ✅ Capacity calculations
- ✅ PBKDF2 key derivation
- ✅ AES-GCM encryption/decryption
- ✅ MSE/PSNR metrics
- ✅ UI components
- ✅ Page structure
- ⏳ LSB embedding (wait T10)
- ⏳ LSB extraction (wait T11)
- ⏳ Container format (wait T08)

---

## 📖 DOCUMENTATION

```
Root level documentation:
├── README.md               # Project overview & quick start
├── PROJECT_STRUCTURE.md    # This file (structure guide)
├── ARCHITECTURE.md         # System architecture & design
├── TASKS.md               # Task breakdown & assignments
├── UTS_COMPLIANCE.md      # Compliance with UTS requirements
├── STEGO_SPEC.md          # Steganography technical spec
├── SECURITY.md            # Security requirements
├── TESTING_SPEC.md        # Testing specifications
├── UI_UX_SPEC.md          # UI/UX design guidelines
└── AGENTS.md              # AI coding rules

Additional docs:
└── docs/                  # Extended documentation (if needed)
```

---

## 🛠️ UTILITIES & CONFIG

```
Configuration:
├── .streamlit/config.toml  # Streamlit theme config
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Python dependencies
└── .gitignore             # Git ignore rules

Helper scripts:
├── run.bat                # Quick run script (Windows)
├── test.bat               # Quick test script (Windows)
└── generate_test_images.py # Generate sample images

Test data:
└── test_images/           # Sample PNG/BMP images
    ├── small_rgb.png
    ├── medium_rgb.png
    ├── large_rgb.png
    ├── rgba_alpha.png
    ├── valid_bmp.bmp
    └── tiny_rgb.png
```

---

## 🔄 Data Flow

### **Embed Flow:**
```
User (Frontend)
    ↓
pages/embed.py (UI)
    ↓
stegora/image/io.py (validate image)
    ↓
stegora/stego/capacity.py (check capacity)
    ↓
stegora/crypto/pbkdf2.py (derive key)
    ↓
stegora/crypto/aes_gcm.py (encrypt)
    ↓
stegora/stego/container.py (build STGR)
    ↓
stegora/stego/positions.py (generate positions)
    ↓
stegora/stego/lsb.py (embed in LSB)
    ↓
stegora/image/io.py (save stego image)
    ↓
stegora/image/metrics.py (calculate PSNR)
    ↓
pages/embed.py (display result)
    ↓
User (Download stego image)
```

### **Extract Flow:**
```
User (Frontend)
    ↓
pages/extract.py (UI)
    ↓
stegora/image/io.py (load stego image)
    ↓
stegora/stego/positions.py (generate same positions)
    ↓
stegora/stego/extraction.py (extract LSB)
    ↓
stegora/stego/container.py (parse STGR)
    ↓
stegora/crypto/pbkdf2.py (derive key)
    ↓
stegora/crypto/aes_gcm.py (decrypt)
    ↓
pages/extract.py (display message)
    ↓
User (View/download recovered data)
```

---

## 📋 Module Dependencies

### **Frontend depends on Backend:**
```
pages/embed.py
    → stegora.ui.components
    → stegora.image.io
    → stegora.stego.capacity
    → stegora.crypto.*
    → stegora.stego.*

pages/extract.py
    → stegora.ui.components
    → stegora.image.io
    → stegora.stego.*
    → stegora.crypto.*

pages/analyze.py
    → stegora.ui.components
    → stegora.image.metrics
    → stegora.analysis.*
```

### **Backend modules are independent:**
```
stegora/crypto/*    → Pure cryptography (no other stegora deps)
stegora/image/*     → PIL only (no other stegora deps)
stegora/stego/*     → May use image.io for types
stegora/analysis/*  → May use image.io and stego.*
```

**Rule:** Backend modules NEVER import Streamlit or UI components!

---

## 🎯 Quick Reference

### **I want to...**

**Add a new UI page:**
→ Create `pages/mypage.py`
→ Add to `app.py` navigation

**Modify UI components:**
→ Edit `stegora/ui/components.py`

**Change theme/colors:**
→ Edit `stegora/ui/theme.py`

**Add cryptography:**
→ Add to `stegora/crypto/`

**Add steganography logic:**
→ Add to `stegora/stego/`

**Add image processing:**
→ Add to `stegora/image/`

**Add analysis tool:**
→ Add to `stegora/analysis/`

**Add tests:**
→ Create `tests/test_*.py`

**Run application:**
→ `streamlit run app.py`

**Run tests:**
→ `pytest` or `pytest -v`

---

## 📊 Implementation Status

```
Frontend (UI):           ✅ 100% Complete (T01-T04)
Backend - Crypto:        ✅ 100% Complete (T13-T14)
Backend - Image:         ✅ 100% Complete (T03, T15)
Backend - Stego Core:    🟡 33% Complete (T07 done, T08-T11 pending)
Backend - Analysis:      ⏳ 0% Pending (T16-T18)
Testing:                 ✅ 53 tests passing
Integration:             ⏳ Pending (T05)
```

---

## 👥 Team Responsibility

**Azhar (UI/UX & Integration):**
- ✅ `app.py`
- ✅ `pages/*`
- ✅ `stegora/ui/*`
- ⏳ Integration (T05)

**Naufal (Steganography Core):**
- ✅ `stegora/stego/capacity.py`
- ⏳ `stegora/stego/container.py`
- ⏳ `stegora/stego/positions.py`
- ⏳ `stegora/stego/lsb.py`
- ⏳ `stegora/stego/extraction.py`

**Hana (Crypto & Analysis):**
- ✅ `stegora/crypto/*`
- ✅ `stegora/image/metrics.py`
- ⏳ `stegora/analysis/*`

---

**Last Updated:** After Task T04  
**Version:** 1.0  
**Maintained by:** Team Stegora
