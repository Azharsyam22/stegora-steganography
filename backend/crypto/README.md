# 🔐 Cryptography Modules

**Location:** `stegora/crypto/`  
**Purpose:** All cryptographic operations (PBKDF2, AES-256-GCM)  
**Owner:** Hana

---

## 📄 Modules

### **`pbkdf2.py`** - Key Derivation
**Purpose:** Derive AES key from user password using PBKDF2-HMAC-SHA-256

**Functions:**
```python
def derive_key(
    password: str,
    salt: bytes,
    iterations: int = 600000,
    key_length: int = 32
) -> bytes:
    """
    Derive encryption key from password
    
    Args:
        password: User password string
        salt: Random salt (16 bytes recommended)
        iterations: PBKDF2 iterations (600,000 default)
        key_length: Output key length in bytes (32 for AES-256)
        
    Returns:
        Derived key bytes (32 bytes)
    """
```

**Usage Example:**
```python
from stegora.crypto.pbkdf2 import derive_key
import secrets

# Generate random salt
salt = secrets.token_bytes(16)

# Derive key
password = "my_secure_password"
key = derive_key(password, salt)

# key is now 32 bytes, ready for AES-256
```

**Security:**
- ✅ Uses `cryptography` library (not custom crypto!)
- ✅ HMAC-SHA-256 (strong hash)
- ✅ 600,000 iterations (OWASP recommended for 2024)
- ✅ Random salt (must be stored with ciphertext)

**Status:** ✅ Implemented (T13)  
**Tests:** `tests/test_pbkdf2.py`

---

### **`aes_gcm.py`** - Encryption/Decryption
**Purpose:** Encrypt/decrypt payload using AES-256-GCM

**Functions:**
```python
def encrypt(
    plaintext: bytes,
    key: bytes,
    iv: bytes = None
) -> Tuple[bytes, bytes]:
    """
    Encrypt plaintext with AES-256-GCM
    
    Args:
        plaintext: Data to encrypt
        key: 32-byte encryption key (from PBKDF2)
        iv: 12-byte initialization vector (auto-generated if None)
        
    Returns:
        (ciphertext, authentication_tag)
    """

def decrypt(
    ciphertext: bytes,
    key: bytes,
    iv: bytes,
    tag: bytes
) -> bytes:
    """
    Decrypt ciphertext with AES-256-GCM
    
    Args:
        ciphertext: Encrypted data
        key: 32-byte encryption key (from PBKDF2)
        iv: 12-byte initialization vector (from encryption)
        tag: 16-byte authentication tag (from encryption)
        
    Returns:
        Decrypted plaintext
        
    Raises:
        ValueError: If authentication fails (wrong key/corrupted data)
    """
```

**Usage Example:**
```python
from stegora.crypto.aes_gcm import encrypt, decrypt
from stegora.crypto.pbkdf2 import derive_key
import secrets

# Prepare
password = "my_password"
salt = secrets.token_bytes(16)
key = derive_key(password, salt)

# Encrypt
plaintext = b"Secret message"
ciphertext, tag = encrypt(plaintext, key)

# Store: (salt, iv, ciphertext, tag) → Will be in STGR container

# Decrypt
recovered = decrypt(ciphertext, key, iv, tag)
assert recovered == plaintext  # ✅
```

**Security:**
- ✅ AES-256 (256-bit key = very strong)
- ✅ GCM mode (authenticated encryption)
- ✅ Authentication tag prevents tampering
- ✅ Random IV per encryption (12 bytes)
- ✅ Uses `cryptography` library

**Status:** ✅ Implemented (T14)  
**Tests:** `tests/test_aes_gcm.py`

---

## 🔄 Integration with Steganography

### **Embedding Flow:**
```python
# 1. User provides password
password = user_input

# 2. Generate random salt & IV
salt = secrets.token_bytes(16)

# 3. Derive key
key = derive_key(password, salt)

# 4. Encrypt payload
ciphertext, tag = encrypt(payload_bytes, key)

# 5. Build container with metadata
container = build_container({
    'salt': salt,
    'iv': iv,
    'ciphertext': ciphertext,
    'tag': tag,
    'filename': 'secret.txt',
    'mime': 'text/plain'
})

# 6. Embed container in LSB
stego_image = embed_lsb(cover, container, positions)
```

### **Extraction Flow:**
```python
# 1. Extract container from LSB
container_bytes = extract_lsb(stego_image, positions)

# 2. Parse container
metadata = parse_container(container_bytes)

# 3. User provides password
password = user_input

# 4. Derive key with stored salt
key = derive_key(password, metadata['salt'])

# 5. Decrypt with stored IV & tag
try:
    plaintext = decrypt(
        metadata['ciphertext'],
        key,
        metadata['iv'],
        metadata['tag']
    )
    # ✅ Success!
except ValueError:
    # ❌ Wrong password or corrupted data
    show_error("Decryption failed")
```

---

## 🧪 Testing

**Test Coverage:**
- ✅ PBKDF2 with known test vectors
- ✅ AES-GCM round-trip (encrypt → decrypt)
- ✅ Wrong password detection
- ✅ Authentication tag verification
- ✅ Different key lengths
- ✅ Edge cases (empty plaintext, large data)

**Run tests:**
```bash
pytest tests/test_pbkdf2.py -v
pytest tests/test_aes_gcm.py -v
```

---

## 📋 Security Checklist

- ✅ Use `cryptography` library (audited, battle-tested)
- ✅ Use `secrets` for random generation (not `random`)
- ✅ PBKDF2 with 600,000 iterations
- ✅ Random salt per encryption (16 bytes)
- ✅ Random IV per encryption (12 bytes)
- ✅ AES-256-GCM (authenticated encryption)
- ✅ Verify authentication tag on decrypt
- ✅ Safe error messages (no secret leakage)
- ✅ No hard-coded keys or passwords

---

## 🚫 Anti-Patterns (DON'T DO!)

❌ **Custom Crypto Implementation**
```python
# BAD: Custom AES implementation
def my_aes_encrypt(data, key):
    # Custom crypto is almost always broken!
```

✅ **Use Established Library**
```python
# GOOD: Use cryptography library
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
```

---

❌ **Weak KDF**
```python
# BAD: Simple hash
key = hashlib.sha256(password.encode()).digest()
```

✅ **Strong KDF**
```python
# GOOD: PBKDF2 with iterations
key = derive_key(password, salt, iterations=600000)
```

---

❌ **Reusing IV**
```python
# BAD: Same IV for multiple encryptions
iv = b'123456789012'  # Fixed IV!
ciphertext1, tag1 = encrypt(msg1, key, iv)
ciphertext2, tag2 = encrypt(msg2, key, iv)  # ❌ BROKEN!
```

✅ **Random IV**
```python
# GOOD: Generate fresh IV each time
ciphertext1, tag1 = encrypt(msg1, key)  # Random IV
ciphertext2, tag2 = encrypt(msg2, key)  # Different IV
```

---

## 📚 References

- **PBKDF2:** [RFC 8018](https://www.rfc-editor.org/rfc/rfc8018)
- **AES-GCM:** [NIST SP 800-38D](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)
- **Python cryptography:** [cryptography.io](https://cryptography.io/)
- **OWASP Password Storage:** [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Owner:** Hana  
**Status:** ✅ T13-T14 Complete  
**Next:** Integration in T05
