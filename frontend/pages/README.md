# 🎨 Frontend - Streamlit Pages

**Location:** `pages/`  
**Purpose:** User-facing interface untuk semua fitur Stegora

---

## 📄 Files

### **`embed.py`** - Embed Workflow
**Purpose:** UI untuk menyembunyikan pesan dalam gambar

**Features:**
- Step 1: Upload & validate cover image
- Step 2: Input payload (text/file) dengan capacity checking
- Step 3: Security credentials (password + stego-key)
- Step 4: Embed action dengan validation
- Step 5: Result display (cover vs stego, metrics, download)

**Dependencies:**
- `stegora.ui.components` - UI components
- `stegora.image.io` - Image validation
- `stegora.stego.capacity` - Capacity calculator
- `stegora.crypto.*` - Encryption (when integrated)
- `stegora.stego.*` - LSB embedding (when integrated)

**Status:** ✅ UI Complete, ⏳ Waiting backend integration (T05)

---

### **`extract.py`** - Extract Workflow
**Purpose:** UI untuk mengekstrak pesan tersembunyi dari stego image

**Features:**
- Step 1: Upload & validate stego image
- Step 2: Input credentials (same as embedding)
- Step 3: Extract action dengan validation
- Step 4: Result display (recovered text/file, verification)

**Dependencies:**
- `stegora.ui.components` - UI components
- `stegora.image.io` - Image validation
- `stegora.stego.*` - LSB extraction (when integrated)
- `stegora.crypto.*` - Decryption (when integrated)

**Status:** ✅ UI Complete, ⏳ Waiting backend integration (T05)

---

### **`analyze.py`** - Analysis Tools
**Purpose:** UI untuk steganalysis dan quality metrics

**Features:**
- Upload cover & stego images
- Select analysis types (MSE/PSNR, Histogram, Enhanced LSB, m-bit)
- Display comparison results
- Visual steganalysis tools

**Dependencies:**
- `stegora.ui.components` - UI components
- `stegora.image.metrics` - MSE/PSNR (when integrated)
- `stegora.analysis.*` - Analysis tools (when integrated)

**Status:** ✅ Basic UI, ⏳ Waiting analysis modules (T16-T18)

---

## 🔄 Adding New Page

1. Create `pages/newpage.py`:
```python
import streamlit as st
from stegora.ui.components import page_title, section_header, footer

def show():
    page_title("New Feature", "Description")
    
    section_header("1. First Section")
    # Your UI code here
    
    footer()
```

2. Add to `app.py` navigation:
```python
from pages import embed, extract, analyze, newpage

pages = [
    st.Page(embed.show, title="Embed", url_path="embed"),
    st.Page(extract.show, title="Extract", url_path="extract"),
    st.Page(analyze.show, title="Analyze", url_path="analyze"),
    st.Page(newpage.show, title="New Feature", url_path="newfeature"),
]
```

---

## 📐 Design Guidelines

Follow `UI_UX_SPEC.md` for:
- Soft neutral palette with muted teal accent
- No fake metrics or decorative charts
- Clear error messages
- One action at a time
- Minimal navigation

---

## 🧪 Testing

Pages are tested in `tests/test_embed_extract_pages.py`:
- Page structure validation
- Import checks
- Integration readiness
- No hardcoded data verification

---

**Owner:** Azhar (UI/UX)  
**Status:** T04 Complete  
**Next:** T05 Integration with backend
