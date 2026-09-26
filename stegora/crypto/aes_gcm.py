"""AES-256-GCM encryption and decryption for Stegora.

This module implements authenticated encryption using AES-256-GCM:
- AES-256 in Galois/Counter Mode (GCM)
- 12-byte random IV (nonce) per encryption
- Authentication tag for integrity verification
- Protects against tampering and wrong credentials

Author: Hana (247006111170)
Task: T14 - AES-256-GCM
"""

import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


# Project design constants (SECURITY.md)
IV_LENGTH = 12    # bytes (96 bits - recommended for GCM)
KEY_LENGTH = 32   # bytes (256 bits for AES-256)
TAG_LENGTH = 16   # bytes (128 bits - GCM authentication tag)


class EncryptionError(Exception):
    """Base exception for encryption errors."""
    pass


class DecryptionError(Exception):
    """Base exception for decryption errors."""
    pass


class AuthenticationError(DecryptionError):
    """Raised when authentication tag verification fails."""
    pass


def generate_iv() -> bytes:
    """Generate a cryptographically secure random IV (nonce) for AES-GCM.
    
    Returns:
        bytes: 12-byte random IV
    
    Note:
        IV must be unique for each encryption with the same key.
        Never reuse IV with the same key - this breaks GCM security!
    
    Example:
        >>> iv = generate_iv()
        >>> len(iv)
        12
    """
    return secrets.token_bytes(IV_LENGTH)


def encrypt(plaintext: bytes, key: bytes, associated_data: bytes = b"") -> tuple[bytes, bytes]:
    """Encrypt plaintext using AES-256-GCM.
    
    This function encrypts plaintext with AES-256 in GCM mode, providing both
    confidentiality and authenticity. A fresh random IV is generated for each
    encryption to ensure semantic security.
    
    Args:
        plaintext: Data to encrypt (bytes)
        key: 32-byte AES-256 key (from PBKDF2)
        associated_data: Optional additional authenticated data (AAD).
                        This data is authenticated but not encrypted.
                        Default: empty bytes.
    
    Returns:
        tuple: (ciphertext, iv) where:
            - ciphertext: Encrypted data with authentication tag appended (bytes)
            - iv: 12-byte IV used for this encryption (must be stored)
    
    Raises:
        EncryptionError: If encryption fails
        ValueError: If key length is not 32 bytes
    
    Security Properties:
        - Confidentiality: Plaintext is encrypted
        - Authenticity: Authentication tag prevents tampering
        - Semantic security: Random IV ensures same plaintext → different ciphertext
    
    Example:
        >>> from stegora.crypto import derive_key_with_new_salt
        >>> key, salt = derive_key_with_new_salt("password")
        >>> plaintext = b"secret message"
        >>> ciphertext, iv = encrypt(plaintext, key)
        >>> len(iv)
        12
        >>> len(ciphertext) > len(plaintext)
        True
    
    Note:
        The returned ciphertext includes the 16-byte authentication tag at the end.
        IV must be stored alongside ciphertext for decryption.
    """
    # Validate key length
    if len(key) != KEY_LENGTH:
        raise ValueError(f"Key must be {KEY_LENGTH} bytes for AES-256, got {len(key)}")
    
    # Generate fresh random IV
    iv = generate_iv()
    
    try:
        # Initialize AES-GCM cipher
        aesgcm = AESGCM(key)
        
        # Encrypt and authenticate
        # GCM automatically appends the authentication tag to ciphertext
        ciphertext = aesgcm.encrypt(iv, plaintext, associated_data)
        
        return ciphertext, iv
        
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {e}") from e


def decrypt(ciphertext: bytes, key: bytes, iv: bytes, associated_data: bytes = b"") -> bytes:
    """Decrypt ciphertext using AES-256-GCM.
    
    This function decrypts ciphertext encrypted with AES-256-GCM and verifies
    the authentication tag. If the tag verification fails (wrong key, tampered
    ciphertext, or wrong IV), an AuthenticationError is raised.
    
    Args:
        ciphertext: Encrypted data with authentication tag (bytes)
        key: 32-byte AES-256 key (same key used for encryption)
        iv: 12-byte IV used during encryption
        associated_data: Optional AAD (must match the AAD used in encryption)
    
    Returns:
        bytes: Decrypted plaintext
    
    Raises:
        AuthenticationError: If authentication tag verification fails
                           (wrong key, tampered data, or wrong IV)
        DecryptionError: If decryption fails for other reasons
        ValueError: If key or IV length is invalid
    
    Security Properties:
        - Authentication first: Tag is verified before decryption
        - Tamper detection: Any modification to ciphertext is detected
        - Key verification: Wrong key causes authentication failure
    
    Example:
        >>> from stegora.crypto import derive_key
        >>> # Encryption
        >>> key, salt = derive_key_with_new_salt("password")
        >>> ciphertext, iv = encrypt(b"secret", key)
        >>> 
        >>> # Decryption with correct key
        >>> plaintext = decrypt(ciphertext, key, iv)
        >>> plaintext
        b'secret'
        >>> 
        >>> # Decryption with wrong key (fails)
        >>> wrong_key, _ = derive_key_with_new_salt("wrong")
        >>> decrypt(ciphertext, wrong_key, iv)  # Raises AuthenticationError
    
    Note:
        GCM verifies the authentication tag before returning plaintext.
        If verification fails, no plaintext is returned - this prevents
        timing attacks and ensures security.
    """
    # Validate key length
    if len(key) != KEY_LENGTH:
        raise ValueError(f"Key must be {KEY_LENGTH} bytes for AES-256, got {len(key)}")
    
    # Validate IV length
    if len(iv) != IV_LENGTH:
        raise ValueError(f"IV must be {IV_LENGTH} bytes for GCM, got {len(iv)}")
    
    # Validate ciphertext has minimum length (must include tag)
    if len(ciphertext) < TAG_LENGTH:
        raise DecryptionError(
            f"Ciphertext too short (must be at least {TAG_LENGTH} bytes for tag)"
        )
    
    try:
        # Initialize AES-GCM cipher
        aesgcm = AESGCM(key)
        
        # Decrypt and verify authentication tag
        # GCM automatically verifies the tag before returning plaintext
        plaintext = aesgcm.decrypt(iv, ciphertext, associated_data)
        
        return plaintext
        
    except InvalidTag:
        # Authentication tag verification failed
        # This happens when:
        # - Wrong key is used
        # - Ciphertext has been tampered with
        # - Wrong IV is used
        # - Wrong associated_data is used
        raise AuthenticationError(
            "Authentication failed: wrong key, tampered ciphertext, or wrong IV"
        ) from None
        
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {e}") from e


def encrypt_text(plaintext: str, key: bytes, associated_data: bytes = b"") -> tuple[bytes, bytes]:
    """Encrypt text string using AES-256-GCM.
    
    Convenience function that handles UTF-8 encoding automatically.
    
    Args:
        plaintext: Text to encrypt (string)
        key: 32-byte AES-256 key
        associated_data: Optional AAD
    
    Returns:
        tuple: (ciphertext, iv)
    
    Example:
        >>> key, salt = derive_key_with_new_salt("password")
        >>> ciphertext, iv = encrypt_text("Hello World", key)
        >>> # Store ciphertext and iv for later decryption
    """
    plaintext_bytes = plaintext.encode('utf-8')
    return encrypt(plaintext_bytes, key, associated_data)


def decrypt_text(ciphertext: bytes, key: bytes, iv: bytes, associated_data: bytes = b"") -> str:
    """Decrypt ciphertext to text string using AES-256-GCM.
    
    Convenience function that handles UTF-8 decoding automatically.
    
    Args:
        ciphertext: Encrypted data with tag
        key: 32-byte AES-256 key
        iv: 12-byte IV
        associated_data: Optional AAD
    
    Returns:
        str: Decrypted text
    
    Raises:
        AuthenticationError: If authentication fails
        DecryptionError: If decryption fails
        UnicodeDecodeError: If plaintext is not valid UTF-8
    
    Example:
        >>> key, salt = derive_key_with_new_salt("password")
        >>> ciphertext, iv = encrypt_text("Hello", key)
        >>> plaintext = decrypt_text(ciphertext, key, iv)
        >>> plaintext
        'Hello'
    """
    plaintext_bytes = decrypt(ciphertext, key, iv, associated_data)
    return plaintext_bytes.decode('utf-8')


def validate_round_trip(plaintext: bytes, key: bytes) -> bool:
    """Validate that encryption and decryption are inverse operations (for testing).
    
    Args:
        plaintext: Test data
        key: Test key (32 bytes)
    
    Returns:
        bool: True if plaintext == decrypt(encrypt(plaintext))
    """
    ciphertext, iv = encrypt(plaintext, key)
    recovered = decrypt(ciphertext, key, iv)
    return plaintext == recovered
