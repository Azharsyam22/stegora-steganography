# Stegora — UTS Demo & Q&A Cheat Sheet

## One-sentence description
“Stegora adalah web app berbasis Python dan Streamlit untuk menyisipkan payload yang sudah dienkripsi ke PNG/BMP menggunakan 1-bit RGB LSB dengan posisi yang ditentukan oleh stego-key.”

## 20-second system story
Cover → capacity → payload → PBKDF2/AES-GCM → STGR container → keyed positions → RGB LSB → stego → MSE/PSNR → extract.

## 7-minute demo
1. Open app.
2. Upload PNG/BMP.
3. Show dimensions + capacity.
4. Enter text/file + password + stego-key.
5. Embed.
6. Show cover vs stego.
7. Show actual MSE/PSNR.
8. Extract with correct credentials.
9. Show recovered payload.
10. Repeat with wrong stego-key and show safe failure.
11. Briefly show Analyze page.

## Member focus
Azhar: Streamlit/UI/integration/demo.
Naufal: capacity/container/PRNG/LSB/extraction.
Hana: PBKDF2/AES-GCM/metrics/histogram/JPEG/testing.

## Q&A rule
Everyone must understand the whole system story. Each PIC must master implementation details of their own modules. Never invent a result.
