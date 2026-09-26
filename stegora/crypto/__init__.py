"""Cryptography modules: PBKDF2, AES-GCM"""

from .pbkdf2 import (
    derive_key,
    derive_key_with_new_salt,
    generate_salt,
    validate_determinism,
    PBKDF2_ITERATIONS,
    SALT_LENGTH,
    KEY_LENGTH,
)

from .aes_gcm import (
    encrypt,
    decrypt,
    encrypt_text,
    decrypt_text,
    generate_iv,
    validate_round_trip,
    IV_LENGTH,
    TAG_LENGTH,
    EncryptionError,
    DecryptionError,
    AuthenticationError,
)

__all__ = [
    # PBKDF2
    'derive_key',
    'derive_key_with_new_salt',
    'generate_salt',
    'validate_determinism',
    'PBKDF2_ITERATIONS',
    'SALT_LENGTH',
    'KEY_LENGTH',
    # AES-GCM
    'encrypt',
    'decrypt',
    'encrypt_text',
    'decrypt_text',
    'generate_iv',
    'validate_round_trip',
    'IV_LENGTH',
    'TAG_LENGTH',
    'EncryptionError',
    'DecryptionError',
    'AuthenticationError',
]
