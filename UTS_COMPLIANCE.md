# Stegora — UTS Compliance Map

## Mandatory Topic B
| Requirement | Planned implementation | Evidence |
|---|---|---|
| PNG/BMP text/small file | Pillow + Streamlit upload | Demo |
| 1-bit LSB | Self-written RGB LSB | Code + test |
| Header length | STGR PAYLOAD_LEN | Container test |
| PRNG + stego-key | SHA-256 seed + deterministic positions | Determinism test |
| Encryption | AES-256-GCM | Crypto test |
| Capacity | Actual preflight | Demo + test |
| Side-by-side | Cover/stego result UI | Demo |
| MSE/PSNR | Actual RGB metrics | 5×3 |
| Histogram | Actual RGB histogram | Analysis |
| JPEG re-save | Actual experiment | Test results |
| Enhanced LSB | Actual LSB plane | Analysis |
| Correct/wrong key | Both cases | Live demo |
| m-bit enrichment | 1/2/3/4-bit comparison | Analysis |
| Unit tests | ≥5 | pytest report |
| README | install/run/usage/team | GitHub |
| No secrets | no hard-coded credentials | repo review |
| AI disclosure | appendix | report |

## Note
The UTS brief requires a relevant lecturer publication among the report references. Add this to the report bibliography before submission.
