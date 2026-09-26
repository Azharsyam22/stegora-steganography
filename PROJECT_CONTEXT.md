# Stegora — Project Context
## Final stack
**Python + Streamlit** web application.

Team:
- Azhar — 247006111168 — UI/UX Streamlit & Integration
- Naufal — 247006111158 — Steganography Core
- Hana — 247006111170 — Cryptography, Analysis & Testing

## Academic basis
This project follows the supplied UTS brief, Topic B — Aplikasi Steganografi.

Mandatory functional scope:
1. Hide text/small file in PNG/BMP and extract intact.
2. Mandatory 1-bit RGB LSB insertion/extraction.
3. Header marking message/payload length.
4. Pixel positions randomized/determined using a PRNG seeded from the stego-key.
5. Encrypt the message before embedding; minimum XOR is allowed by the brief, AES is recommended. Stegora uses AES-256-GCM.
6. Capacity calculation and rejection of oversized payloads.
7. Side-by-side cover/stego display.
8. MSE/PSNR analysis.
9. Histogram comparison.
10. JPEG re-save fragility test.
11. Enhanced LSB visual steganalysis.
12. UTS demo: encrypted insert, cover/stego + PSNR, correct-key extraction, wrong-key failure.

Enrichment:
- WAV/video if desired, but not required for this implementation.
- m-bit LSB capacity/PSNR trade-off.
- chi-square if time permits. Do not replace mandatory features with enrichment.

## Product goal
Stegora should look like a modern, calm, technical security utility—not a generic AI dashboard. It should be easy to demonstrate and easy for all members to explain.

## Why Streamlit
Streamlit is selected to keep one Python stack for UI, image processing, cryptography, steganography core, analysis, and tests. Current Streamlit supports multipage apps with `st.Page`/`st.navigation`, theming, and custom components, so the UI can be substantially polished while keeping the codebase approachable.

## Core system story
```text
Cover PNG/BMP
  -> capacity preflight
  -> payload bytes
  -> PBKDF2-HMAC-SHA-256
  -> AES-256-GCM
  -> STGR binary container
  -> stego-key -> SHA-256 seed -> deterministic position generator
  -> 1-bit RGB LSB embedding
  -> stego PNG
  -> MSE/PSNR + histogram + enhanced LSB
  -> extraction with correct key
  -> wrong-key failure
```

## Scope boundary
- No database required.
- No remote API required.
- No secret keys/passwords hard-coded.
- Do not claim production-grade security.
- Do not claim PSNR proves security.
- Do not claim JPEG results are universal beyond the tested encoder/quality.
