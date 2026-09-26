# Stegora — Security Requirements

## Cryptography
Use `cryptography` library:
- AES-256-GCM
- PBKDF2-HMAC-SHA-256

Do not implement AES manually.

## Password derivation
Project design:
- PBKDF2-HMAC-SHA-256
- 600,000 iterations
- 16-byte random salt
- 32-byte derived key

**Important:** 600,000 is a project design decision, not a lecturer-mandated number from the supplied brief.

## IV
Use a fresh 12-byte random IV for each AES-GCM encryption.

## Randomness
Use `secrets.token_bytes()` for salt and IV.
Do not use `random` or deterministic PRNG for security randomness.

## Separation of secrets
Password = encryption credential.
Stego-key = deterministic position credential.

Never hard-code either.

## Failure behavior
Wrong password/key, malformed header, truncation, and authentication failure should produce a clear safe error without exposing secret material.
