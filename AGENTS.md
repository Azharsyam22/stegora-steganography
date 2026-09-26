# AGENTS.md — Stegora AI Coding Rules

## Before coding
Read:
- PROJECT_CONTEXT.md
- PRD.md
- STEGO_SPEC.md
- ARCHITECTURE.md
- UI_UX_SPEC.md
- SECURITY.md
- TESTING_SPEC.md
- TASKS.md

## Non-negotiable
1. Do not fake features.
2. Do not hard-code metrics, ciphertext, capacity, extraction output, passwords, or keys.
3. Do not use a steganography library for mandatory LSB implementation.
4. Use Pillow for image I/O only.
5. Use `cryptography` for AES-GCM/PBKDF2.
6. Use `secrets` for salt/IV randomness.
7. Preserve alpha.
8. Reject oversized payloads before mutation.
9. Deterministic position generation must be reproducible for the same stego-key.
10. Core modules must not depend on Streamlit.
11. Run relevant tests after changes.
12. Do not introduce database/backend unless explicitly approved.
13. Do not add fake demo data.
14. Do not over-engineer UI.

## UI
Use native Streamlit first. Use theme configuration and small amounts of CSS for polish. Do not replace Streamlit with a giant custom HTML app.

## AI workflow
For each task:
1. inspect existing code,
2. explain plan,
3. implement smallest coherent change,
4. run tests,
5. report changed files,
6. report test result,
7. note remaining limitation.

## Academic integrity
AI assistance must be disclosed in the report appendix. Members must understand and be able to explain submitted code.
