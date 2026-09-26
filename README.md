# Stegora — LSB Steganography Application

Modern steganography application using LSB embedding with AES-256-GCM encryption.

## Team
- **Azhar** (247006111168) - UI/UX & Integration
- **Naufal** (247006111158) - Steganography Core
- **Hana** (247006111170) - Cryptography & Analysis

## Installation

### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux/Mac
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Run Tests
```bash
pytest
```

For verbose output:
```bash
pytest -v
```

## Project Structure
```
stegora/
├── app.py                 # Main Streamlit app
├── pages/                 # UI pages
│   ├── embed.py          # Embed message page
│   ├── extract.py        # Extract message page
│   └── analyze.py        # Analysis page
├── stegora/              # Core modules
│   ├── crypto/           # Cryptography (PBKDF2, AES-GCM)
│   ├── stego/            # Steganography core (LSB, container)
│   ├── image/            # Image I/O and metrics
│   ├── analysis/         # Analysis tools
│   └── ui/               # UI components
└── tests/                # Test suite
```

## Features
- **Embed**: Hide text or files in PNG/BMP images using LSB
- **Extract**: Recover hidden messages with correct credentials
- **Analyze**: PSNR, MSE, histogram, enhanced LSB steganalysis

## Documentation
- `PROJECT_CONTEXT.md` - Project overview and goals
- `STEGO_SPEC.md` - Technical steganography specification
- `ARCHITECTURE.md` - System architecture
- `SECURITY.md` - Security guidelines
- `TESTING_SPEC.md` - Testing requirements
- `UTS_COMPLIANCE.md` - UTS requirement mapping

## Academic Context
This project is developed for **Keamanan Informasi** course at Universitas Siliwangi, fulfilling UTS requirements for Topic B (Steganography Application).

## License
Academic project - Universitas Siliwangi 2026
