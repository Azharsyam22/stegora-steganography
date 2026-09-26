# T13: PBKDF2 Key Derivation Implementation

**Task:** T13 - PBKDF2 Key Derivation  
**PIC:** Hana (247006111170)  
**Status:** ✅ Completed  
**Commit:** `feat: implement pbkdf2 key derivation`

## Overview

Implemented PBKDF2-HMAC-SHA-256 password-based key derivation for secure encryption key generation in Stegora steganography application.

## Specifications

Following SECURITY.md requirements:

- **Algorithm:** PBKDF2-HMAC-SHA-256
- **Iterations:** 600,000 (project design choice for balance between security and performance)
- **Salt Length:** 16 bytes (128 bits)
- **Key Length:** 32 bytes (256 bits for AES-256-GCM)
- **Randomness Source:** `secrets.token_bytes()` for cryptographically secure random generation

## Implementation

### Module: `stegora/crypto/pbkdf2.py`

#### Functions

1. **`generate_salt() -> bytes`**
   - Generates cryptographically secure random 16-byte salt
   - Uses `secrets.token_bytes()` for security
   - Returns different salt on each call

2. **`derive_key(password: str | bytes, salt: bytes) -> bytes`**
   - Core key derivation function
   - Accepts password as string (UTF-8 encoded) or bytes
   - Requires exactly 16-byte salt
   - Returns 32-byte derived key
   - Deterministic: same inputs always produce same output
   - Validates input types and salt length

3. **`derive_key_with_new_salt(password: str | bytes) -> tuple[bytes, bytes]`**
   - Convenience function for embedding workflow
   - Generates fresh random salt automatically
   - Returns (key, salt) tuple
   - Salt must be stored with ciphertext for later decryption

4. **`validate_determinism(password: str | bytes, salt: bytes) -> bool`**
   - Testing helper to verify deterministic behavior
   - Returns True if two derivations produce identical keys

#### Constants

```python
PBKDF2_ITERATIONS = 600_000  # Project design choice
SALT_LENGTH = 16             # bytes
KEY_LENGTH = 32              # bytes (for AES-256)
```

## Usage Examples

### Embedding (Encryption)

```python
from stegora.crypto import derive_key_with_new_salt

# Generate fresh salt and derive key
password = "user_password"
key, salt = derive_key_with_new_salt(password)

# salt must be stored in STGR container for extraction
# key is used for AES-256-GCM encryption
```

### Extraction (Decryption)

```python
from stegora.crypto import derive_key

# Retrieve salt from STGR container
password = "user_password"
key = derive_key(password, stored_salt)

# key is used for AES-256-GCM decryption
```

## Security Properties

1. **Deterministic:** Same password + salt always produces same key
2. **Unique per operation:** Fresh random salt ensures different keys for different operations
3. **Password-independent timing:** PBKDF2 iteration count is constant
4. **Slow by design:** 600,000 iterations makes brute-force attacks computationally expensive
5. **Memory-efficient:** PBKDF2 has low memory requirements (unlike scrypt/Argon2)

## Testing

### Test Coverage: 17 Tests (100% passing)

**Unit Tests:**
- `test_generate_salt_length` - Verify 16-byte salt generation
- `test_generate_salt_randomness` - Ensure different salts on each call
- `test_derive_key_length` - Verify 32-byte key output
- `test_derive_key_determinism` - Same inputs → same key
- `test_derive_key_different_password` - Different passwords → different keys
- `test_derive_key_different_salt` - Different salts → different keys
- `test_derive_key_bytes_password` - Support both str and bytes
- `test_derive_key_invalid_salt_length` - Reject invalid salt lengths
- `test_derive_key_invalid_password_type` - Reject invalid password types
- `test_derive_key_with_new_salt` - Convenience function works correctly
- `test_derive_key_empty_password` - Handle edge case of empty password
- `test_derive_key_unicode_password` - Support Unicode passwords (Japanese, Russian, Emoji, etc.)
- `test_pbkdf2_parameters` - Verify constants match specification
- `test_derive_key_nonascii_bytes` - Handle non-ASCII byte sequences

**Integration Tests:**
- `test_embed_extract_pattern` - Verify round-trip workflow
- `test_wrong_password_produces_different_key` - Wrong password detection
- `test_multiple_embeds_different_salts` - Multiple operations use different salts

### Test Results

```
========================================= 70 passed in 7.98s =========================================
```

All tests passing, including:
- 17 PBKDF2 tests
- 53 existing project tests (no regression)

## Design Decisions

### Why 600,000 iterations?

- **OWASP Recommendation (2023):** Minimum 310,000 iterations for PBKDF2-SHA256
- **NIST SP 800-63B:** Recommends at least 10,000 iterations
- **Project Choice:** 600,000 provides good security margin while maintaining reasonable performance
- **Performance:** ~0.3-0.5 seconds per derivation on typical hardware (acceptable for user-facing operation)
- **Academic Context:** Demonstrates understanding of security/performance tradeoff

### Why 16-byte salt?

- **NIST Recommendation:** Minimum 16 bytes (128 bits)
- **Industry Standard:** 16 bytes is common in cryptographic libraries
- **Security:** 2^128 possible values makes collision practically impossible

### Why PBKDF2 vs Argon2/scrypt?

- **Assignment Requirement:** Brief explicitly mentions PBKDF2
- **Library Availability:** PBKDF2 is built into `cryptography` library
- **Compatibility:** PBKDF2 is widely supported and standardized (RFC 2898)
- **Simplicity:** Easier to explain and understand for academic project
- **Note:** Brief mentions PBKDF2, scrypt, or Argon2 as options; we chose PBKDF2

## Files Changed

```
Created:
- stegora/crypto/pbkdf2.py         (160 lines)
- tests/test_pbkdf2.py              (231 lines)

Modified:
- stegora/crypto/__init__.py        (exported functions)
```

## Integration Points

This module will be used by:
- **T14 (AES-256-GCM):** Password → derive_key() → AES key
- **Embed page:** User password input → key derivation
- **Extract page:** User password input → key derivation
- **STGR container:** Salt storage in metadata section

## Limitations & Future Work

1. **Not Post-Quantum:** PBKDF2 with SHA-256 is quantum-resistant for key derivation, but should be noted
2. **Fixed Iteration Count:** Could be configurable per security requirements
3. **No Pepper:** Could add server-side secret for additional security layer
4. **Memory-Hard Alternative:** For production, consider Argon2 (more memory-hard, better against GPU attacks)

## Compliance

✅ Follows AGENTS.md rules:
- No hard-coded keys or passwords
- Uses `secrets` for cryptographic randomness
- No mock/fake implementations
- Core module independent of Streamlit
- All tests passing

✅ Follows SECURITY.md:
- PBKDF2-HMAC-SHA-256
- 600,000 iterations
- 16-byte random salt
- 32-byte derived key
- Uses `cryptography` library

✅ Follows TESTING_SPEC.md:
- More than 5 unit tests (17 total)
- Real values, no invented metrics
- Round-trip testing

## References

- RFC 2898 - PKCS #5: Password-Based Cryptography Specification
- NIST SP 800-63B - Digital Identity Guidelines
- OWASP Password Storage Cheat Sheet
- Python `cryptography` library documentation

---

**Next Task:** T14 - AES-256-GCM encryption/decryption
