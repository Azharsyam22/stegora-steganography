# ⚙️ Backend - Core Modules

**Location:** `stegora/`  
**Purpose:** Backend logic untuk steganography, cryptography, image processing, dan analysis

**Rule:** Backend modules **NEVER** import Streamlit or UI components!

---

## 📂 Module Structure

```
stegora/
├── crypto/      # Cryptography (PBKDF2, AES-GCM)
├── stego/       # Steganography core (LSB, Container, PRNG)
├── image/       # Image I/O & metrics (Pillow wrapper, MSE/PSNR)
├── analysis/    # Steganalysis (Histogram, Enhanced LSB)
└── ui/          # UI components (Frontend, exception to backend rule)
```

---

## 🔐 `crypto/` - Cryptography

**Purpose:** All cryptographic operations

**Modules:**
- `pbkdf2.py` - PBKDF2-HMAC-SHA-256 key derivation ✅
- `aes_gcm.py` - AES-256-GCM encryption/decryption ✅

**Key Functions:**
```python
from stegora.crypto.pbkdf2 import derive_key
from stegora.crypto.aes_gcm import encrypt, decrypt

# Derive key from password
key = derive_key(password, salt, iterations=600000)

# Encrypt
ciphertext, tag = encrypt(plaintext, key, iv)

# Decrypt
plaintext = decrypt(ciphertext, key, iv, tag)
```

**Status:** ✅ Complete (T13-T14 by Hana)

---

## 🔀 `stego/` - Steganography Core

**Purpose:** LSB embedding, extraction, positioning, container format

**Modules:**
- `capacity.py` - Capacity calculation ✅
- `container.py` - STGR binary container ⏳
- `positions.py` - Keyed deterministic PRNG ⏳
- `lsb.py` - LSB embedding ⏳
- `extraction.py` - LSB extraction ⏳

**Key Functions:**
```python
from stegora.stego.capacity import calculate_raw_capacity, check_payload_capacity
from stegora.stego.container import build_container, parse_container
from stegora.stego.positions import generate_positions
from stegora.stego.lsb import embed_lsb
from stegora.stego.extraction import extract_lsb

# Calculate capacity
capacity = calculate_raw_capacity(width, height)

# Build container
container_bytes = build_container(payload, metadata)

# Generate positions
positions = generate_positions(stego_key, image_size, num_bits)

# Embed
stego_image = embed_lsb(cover_image, container_bytes, positions)

# Extract
recovered_bytes = extract_lsb(stego_image, positions, length)
```

**Status:** 🟡 Partial (T07 done, T08-T11 by Naufal)

---

## 🖼️ `image/` - Image Processing

**Purpose:** Image I/O, validation, quality metrics (Pillow wrapper only!)

**Modules:**
- `io.py` - Image loading, validation, metadata ✅
- `metrics.py` - MSE, PSNR calculations ✅

**Key Functions:**
```python
from stegora.image.io import validate_and_load_cover_image, save_image
from stegora.image.metrics import calculate_mse, calculate_psnr

# Load & validate
image, metadata = validate_and_load_cover_image(image_bytes)

# Calculate metrics
mse = calculate_mse(cover_image, stego_image)
psnr = calculate_psnr(cover_image, stego_image)

# Save
save_image(stego_image, "output.png", format="PNG")
```

**Status:** ✅ Complete (T03 by Azhar, T15 by Hana)

---

## 📊 `analysis/` - Steganalysis Tools

**Purpose:** Analysis dan visualization untuk steganalysis

**Modules:**
- `histogram.py` - RGB histogram comparison ⏳
- `lsb_plane.py` - Enhanced LSB visualization ⏳
- `mbits.py` - m-bit LSB analysis (enrichment) ⏳

**Key Functions:**
```python
from stegora.analysis.histogram import generate_histogram, compare_histograms
from stegora.analysis.lsb_plane import extract_lsb_plane
from stegora.analysis.mbits import analyze_mbits

# Generate histogram
hist = generate_histogram(image, channel='R')

# Compare
comparison = compare_histograms(cover, stego)

# Extract LSB plane
lsb_image = extract_lsb_plane(image, bit_position=1)

# Analyze m-bit trade-off
results = analyze_mbits(image, m_values=[1, 2, 3, 4])
```

**Status:** ⏳ Pending (T16-T19 by Hana)

---

## 🎨 `ui/` - UI Components

**Purpose:** Reusable UI components (Frontend exception!)

**Modules:**
- `theme.py` - Color palette & CSS
- `components.py` - Reusable UI elements

**Status:** ✅ Complete (T02 by Azhar)

**Note:** This is the ONLY module that imports Streamlit!

---

## 🧪 Testing

All backend modules have comprehensive unit tests in `tests/`:

```
tests/
├── test_capacity.py       # 16 tests ✅
├── test_image_io.py       # 15 tests ✅
├── test_pbkdf2.py         # Tests ✅
├── test_aes_gcm.py        # Tests ✅
├── test_metrics.py        # Tests ✅
└── test_*.py              # More tests ⏳
```

**Run tests:**
```bash
pytest
pytest -v                 # Verbose
pytest tests/test_capacity.py  # Specific module
```

---

## 📐 Design Principles

1. **No UI Dependencies:** Backend modules don't import Streamlit
2. **Pure Functions:** Input → Output, no hidden state
3. **Type Hints:** Use type annotations for clarity
4. **Docstrings:** Document all public functions
5. **Unit Tests:** Test coverage for all modules
6. **Error Handling:** Raise specific exceptions with clear messages

---

## 🔄 Module Dependencies

```
crypto/      → No internal dependencies (pure)
image/       → PIL only (no stegora deps)
stego/       → May use image.io for types
analysis/    → May use image.io and stego.*
ui/          → Uses Streamlit (exception)
```

**Rule:** Avoid circular dependencies!

---

## 👥 Team Responsibility

- **Azhar:** `ui/`, `image/io.py`, integration
- **Naufal:** `stego/` (except capacity)
- **Hana:** `crypto/`, `image/metrics.py`, `analysis/`

---

**Last Updated:** After T04  
**Next:** Complete T08-T11 (Naufal), T16-T18 (Hana)
