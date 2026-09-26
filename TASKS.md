# Stegora — Task Map

| ID | PIC | Task | Priority | Commit |
|---|---|---|---|---|
| T01 | Azhar | Project scaffold Python + Streamlit | CORE | `feat: initialize stegora streamlit project` |
| T02 | Azhar | UI/UX shell modern | CORE | `feat: build modern streamlit ui shell` |
| T03 | Azhar | Upload & validation PNG/BMP | CORE | `feat: add image upload and validation` |
| T04 | Azhar | Embed/Extract workspace | CORE | `feat: build embed extract workspace` |
| T05 | Azhar | Integrasi pipeline + result | CORE | `feat: integrate stego pipeline and results` |
| T06 | Azhar | E2E demo & stability | CORE | `fix: complete demo flow and error handling` |
| T07 | Naufal | Capacity calculator | CORE | `feat: add stego capacity calculator` |
| T08 | Naufal | STGR binary container | CORE | `feat: implement stego binary container` |
| T09 | Naufal | Keyed deterministic PRNG | CORE | `feat: add keyed pixel position prng` |
| T10 | Naufal | 1-bit RGB LSB embedding | CORE | `feat: implement rgb lsb embedding` |
| T11 | Naufal | 1-bit RGB LSB extraction | CORE | `feat: implement rgb lsb extraction` |
| T12 | Naufal | Core round-trip tests | CORE | `test: add stego round trip tests` |
| T13 | Hana | PBKDF2 key derivation | CORE | `feat: implement pbkdf2 key derivation` |
| T14 | Hana | AES-256-GCM | CORE | `feat: add aes gcm encryption` |
| T15 | Hana | MSE & PSNR | CORE | `feat: implement mse psnr metrics` |
| T16 | Hana | Histogram + enhanced LSB | ANALYSIS | `feat: add histogram and lsb analysis` |
| T17 | Hana | Security + JPEG robustness | ANALYSIS | `test: add security and jpeg robustness tests` |
| T18 | Hana | 5×3 testing matrix + XLSX | ANALYSIS | `test: complete image payload test matrix` |
| T19 | Naufal + Hana | m-bit LSB enrichment | ENRICHMENT | `feat: add m-bit lsb analysis` |
| T20 | Semua | Final review + submission | UTS | `docs: finalize project documentation` |

## Development order
T01–T03 → T07–T14 → T10–T12 → T04–T06 → T15–T18 → T19 → T20.

Do not wait until the end to discover that the core cannot round-trip.
