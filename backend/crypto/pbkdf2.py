"""PBKDF2-HMAC-SHA-256 key derivation for Stegora.

This module implements password-based key derivation following SECURITY.md:
- PBKDF2-HMAC-SHA-256
- 600,000 iterations (project design choice)
- 16-byte random salt
- 32-byte derived key (for AES-256)

Author: Hana (247006111170)
Task: T13 - PBKDF2 Key Derivation
"""

import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Project design constants (SECURITY.md)
PBKDF2_ITERATIONS = 600_000
SALT_LENGTH = 16  # bytes
KEY_LENGTH = 32   # bytes (256 bits for AES-256)


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt.
    
    Returns:
        bytes: 16-byte random salt
    
    Example:
        >>> salt = generate_salt()
        >>> len(salt)
        16
    """
    return secrets.token_bytes(SALT_LENGTH)


def derive_key(password: str | bytes, salt: bytes) -> bytes:
    """Derive a 32-byte AES-256 key from password and salt using PBKDF2-HMAC-SHA-256.
    
    This function implements the password derivation specified in SECURITY.md:
    - Algorithm: PBKDF2-HMAC-SHA-256
    - Iterations: 600,000
    - Output: 32 bytes (256 bits)
    
    Args:
        password: User password (string or bytes). If string, will be UTF-8 encoded.
        salt: 16-byte salt (should be generated with generate_salt())
    
    Returns:
        bytes: 32-byte derived key suitable for AES-256-GCM
    
    Raises:
        ValueError: If salt length is not 16 bytes
        TypeError: If password is neither str nor bytes
    
    Example:
        >>> salt = generate_salt()
        >>> key = derive_key("my_secure_password", salt)
        >>> len(key)
        32
    """
    # Validate salt length
    if len(salt) != SALT_LENGTH:
        raise ValueError(f"Salt must be {SALT_LENGTH} bytes, got {len(salt)}")
    
    # Convert password to bytes if needed
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    elif isinstance(password, bytes):
        password_bytes = password
    else:
        raise TypeError(f"Password must be str or bytes, got {type(password)}")
    
    # Initialize PBKDF2 with SHA-256
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    
    # Derive and return key
    key = kdf.derive(password_bytes)
    return key


def derive_key_with_new_salt(password: str | bytes) -> tuple[bytes, bytes]:
    """Derive key with a fresh random salt (convenience function for embedding).
    
    This is a helper function that generates a new salt and derives a key.
    Use this when encrypting/embedding. Store the returned salt with the ciphertext.
    
    Args:
        password: User password (string or bytes)
    
    Returns:
        tuple: (derived_key, salt) where both are bytes
            - derived_key: 32-byte AES-256 key
            - salt: 16-byte random salt (must be stored for decryption)
    
    Example:
        >>> key, salt = derive_key_with_new_salt("my_password")
        >>> len(key), len(salt)
        (32, 16)
        >>> # Store salt with ciphertext for later decryption
        >>> key2 = derive_key("my_password", salt)
        >>> key == key2
        True
    """
    salt = generate_salt()
    key = derive_key(password, salt)
    return key, salt


# Validation function for testing
def validate_determinism(password: str | bytes, salt: bytes) -> bool:
    """Validate that key derivation is deterministic (for testing).
    
    Args:
        password: Test password
        salt: Test salt
    
    Returns:
        bool: True if two derivations produce identical keys
    """
    key1 = derive_key(password, salt)
    key2 = derive_key(password, salt)
    return key1 == key2
