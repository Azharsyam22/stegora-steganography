"""Unit tests for AES-256-GCM encryption and decryption.

Tests for T14 - AES-256-GCM
Author: Hana (247006111170)
"""

import pytest
from stegora.crypto import (
    encrypt,
    decrypt,
    encrypt_text,
    decrypt_text,
    generate_iv,
    validate_round_trip,
    derive_key_with_new_salt,
    IV_LENGTH,
    TAG_LENGTH,
    KEY_LENGTH,
    EncryptionError,
    DecryptionError,
    AuthenticationError,
)


class TestIVGeneration:
    """Test suite for IV generation."""
    
    def test_generate_iv_length(self):
        """Test that generate_iv produces correct length."""
        iv = generate_iv()
        assert len(iv) == IV_LENGTH
        assert len(iv) == 12
    
    def test_generate_iv_randomness(self):
        """Test that generate_iv produces different IVs."""
        iv1 = generate_iv()
        iv2 = generate_iv()
        iv3 = generate_iv()
        
        # All IVs should be different (extremely high probability)
        assert iv1 != iv2
        assert iv2 != iv3
        assert iv1 != iv3
    
    def test_generate_iv_type(self):
        """Test that generate_iv returns bytes."""
        iv = generate_iv()
        assert isinstance(iv, bytes)


class TestEncryption:
    """Test suite for encryption."""
    
    def test_encrypt_basic(self):
        """Test basic encryption works."""
        key, _ = derive_key_with_new_salt("test_password")
        plaintext = b"Hello, World!"
        
        ciphertext, iv = encrypt(plaintext, key)
        
        assert isinstance(ciphertext, bytes)
        assert isinstance(iv, bytes)
        assert len(iv) == IV_LENGTH
        assert len(ciphertext) > len(plaintext)  # Ciphertext includes tag
    
    def test_encrypt_includes_tag(self):
        """Test that ciphertext includes authentication tag."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"test"
        
        ciphertext, iv = encrypt(plaintext, key)
        
        # Ciphertext = encrypted_data + tag (16 bytes)
        # So ciphertext should be at least len(plaintext) + TAG_LENGTH
        assert len(ciphertext) >= len(plaintext) + TAG_LENGTH
    
    def test_encrypt_different_ciphertext_same_plaintext(self):
        """Test that same plaintext produces different ciphertext (semantic security)."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"same plaintext"
        
        ciphertext1, iv1 = encrypt(plaintext, key)
        ciphertext2, iv2 = encrypt(plaintext, key)
        ciphertext3, iv3 = encrypt(plaintext, key)
        
        # Different IVs ensure different ciphertexts
        assert iv1 != iv2 != iv3
        assert ciphertext1 != ciphertext2 != ciphertext3
    
    def test_encrypt_empty_plaintext(self):
        """Test encrypting empty data."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b""
        
        ciphertext, iv = encrypt(plaintext, key)
        
        # Even empty plaintext has authentication tag
        assert len(ciphertext) == TAG_LENGTH
        assert len(iv) == IV_LENGTH
    
    def test_encrypt_large_plaintext(self):
        """Test encrypting large data."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"A" * 10000  # 10KB
        
        ciphertext, iv = encrypt(plaintext, key)
        
        assert len(ciphertext) >= len(plaintext) + TAG_LENGTH
        assert len(iv) == IV_LENGTH
    
    def test_encrypt_binary_data(self):
        """Test encrypting binary data (not just text)."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = bytes(range(256))  # All possible byte values
        
        ciphertext, iv = encrypt(plaintext, key)
        
        assert len(ciphertext) >= len(plaintext) + TAG_LENGTH
        assert len(iv) == IV_LENGTH
    
    def test_encrypt_invalid_key_length(self):
        """Test that encrypt rejects invalid key length."""
        short_key = b"short"
        long_key = b"a" * 64
        plaintext = b"test"
        
        with pytest.raises(ValueError, match="Key must be 32 bytes"):
            encrypt(plaintext, short_key)
        
        with pytest.raises(ValueError, match="Key must be 32 bytes"):
            encrypt(plaintext, long_key)
    
    def test_encrypt_with_aad(self):
        """Test encryption with additional authenticated data."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"secret message"
        aad = b"metadata: user=hana, timestamp=123456"
        
        ciphertext, iv = encrypt(plaintext, key, aad)
        
        assert len(ciphertext) >= len(plaintext) + TAG_LENGTH
        # AAD is authenticated but not included in ciphertext
        assert len(ciphertext) < len(plaintext) + len(aad)


class TestDecryption:
    """Test suite for decryption."""
    
    def test_decrypt_basic(self):
        """Test basic decryption works."""
        key, _ = derive_key_with_new_salt("test_password")
        plaintext = b"Hello, World!"
        
        ciphertext, iv = encrypt(plaintext, key)
        recovered = decrypt(ciphertext, key, iv)
        
        assert recovered == plaintext
    
    def test_decrypt_empty_plaintext(self):
        """Test decrypting empty data."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b""
        
        ciphertext, iv = encrypt(plaintext, key)
        recovered = decrypt(ciphertext, key, iv)
        
        assert recovered == plaintext
        assert recovered == b""
    
    def test_decrypt_large_plaintext(self):
        """Test decrypting large data."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"B" * 10000  # 10KB
        
        ciphertext, iv = encrypt(plaintext, key)
        recovered = decrypt(ciphertext, key, iv)
        
        assert recovered == plaintext
    
    def test_decrypt_binary_data(self):
        """Test decrypting binary data."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = bytes(range(256))
        
        ciphertext, iv = encrypt(plaintext, key)
        recovered = decrypt(ciphertext, key, iv)
        
        assert recovered == plaintext
    
    def test_decrypt_with_aad(self):
        """Test decryption with AAD."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"secret"
        aad = b"metadata"
        
        ciphertext, iv = encrypt(plaintext, key, aad)
        recovered = decrypt(ciphertext, key, iv, aad)
        
        assert recovered == plaintext
    
    def test_decrypt_wrong_key_fails(self):
        """Test that wrong key causes authentication failure."""
        key1, _ = derive_key_with_new_salt("correct_password")
        key2, _ = derive_key_with_new_salt("wrong_password")
        plaintext = b"secret message"
        
        ciphertext, iv = encrypt(plaintext, key1)
        
        # Decryption with wrong key must fail
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            decrypt(ciphertext, key2, iv)
    
    def test_decrypt_tampered_ciphertext_fails(self):
        """Test that tampered ciphertext is detected."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"original message"
        
        ciphertext, iv = encrypt(plaintext, key)
        
        # Tamper with ciphertext (flip one bit)
        tampered = bytearray(ciphertext)
        tampered[0] ^= 1  # Flip first bit
        tampered_ciphertext = bytes(tampered)
        
        # Decryption must fail (authentication error)
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            decrypt(tampered_ciphertext, key, iv)
    
    def test_decrypt_wrong_iv_fails(self):
        """Test that wrong IV causes authentication failure."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"message"
        
        ciphertext, correct_iv = encrypt(plaintext, key)
        wrong_iv = generate_iv()  # Different IV
        
        # Decryption with wrong IV must fail
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            decrypt(ciphertext, key, wrong_iv)
    
    def test_decrypt_wrong_aad_fails(self):
        """Test that wrong AAD causes authentication failure."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"message"
        correct_aad = b"metadata1"
        wrong_aad = b"metadata2"
        
        ciphertext, iv = encrypt(plaintext, key, correct_aad)
        
        # Decryption with wrong AAD must fail
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            decrypt(ciphertext, key, iv, wrong_aad)
    
    def test_decrypt_truncated_ciphertext_fails(self):
        """Test that truncated ciphertext is rejected."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"long message here"
        
        ciphertext, iv = encrypt(plaintext, key)
        
        # Truncate ciphertext (remove some bytes)
        truncated = ciphertext[:5]
        
        # Decryption must fail
        with pytest.raises((AuthenticationError, DecryptionError)):
            decrypt(truncated, key, iv)
    
    def test_decrypt_too_short_ciphertext(self):
        """Test that ciphertext shorter than tag length is rejected."""
        key, _ = derive_key_with_new_salt("password")
        iv = generate_iv()
        short_ciphertext = b"short"  # Less than 16 bytes (TAG_LENGTH)
        
        with pytest.raises(DecryptionError, match="too short"):
            decrypt(short_ciphertext, key, iv)
    
    def test_decrypt_invalid_key_length(self):
        """Test that decrypt rejects invalid key length."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"test"
        ciphertext, iv = encrypt(plaintext, key)
        
        short_key = b"short"
        with pytest.raises(ValueError, match="Key must be 32 bytes"):
            decrypt(ciphertext, short_key, iv)
    
    def test_decrypt_invalid_iv_length(self):
        """Test that decrypt rejects invalid IV length."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"test"
        ciphertext, _ = encrypt(plaintext, key)
        
        short_iv = b"short"
        with pytest.raises(ValueError, match="IV must be 12 bytes"):
            decrypt(ciphertext, key, short_iv)


class TestRoundTrip:
    """Test suite for encryption/decryption round trips."""
    
    def test_round_trip_basic(self):
        """Test basic round trip."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"test message"
        
        ciphertext, iv = encrypt(plaintext, key)
        recovered = decrypt(ciphertext, key, iv)
        
        assert plaintext == recovered
    
    def test_round_trip_multiple_messages(self):
        """Test multiple round trips with same key."""
        key, _ = derive_key_with_new_salt("password")
        
        messages = [
            b"message 1",
            b"message 2",
            b"message 3",
            b"a" * 1000,  # longer message
            b"",  # empty
        ]
        
        for plaintext in messages:
            ciphertext, iv = encrypt(plaintext, key)
            recovered = decrypt(ciphertext, key, iv)
            assert plaintext == recovered
    
    def test_round_trip_unicode_text(self):
        """Test round trip with Unicode text."""
        key, _ = derive_key_with_new_salt("password")
        
        texts = [
            "Hello World",
            "パスワード",  # Japanese
            "пароль",      # Russian
            "密码",        # Chinese
            "🔒secure🔑",  # Emoji
        ]
        
        for text in texts:
            ciphertext, iv = encrypt_text(text, key)
            recovered = decrypt_text(ciphertext, key, iv)
            assert text == recovered
    
    def test_validate_round_trip_function(self):
        """Test the validate_round_trip helper function."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"test data"
        
        assert validate_round_trip(plaintext, key) is True
    
    def test_round_trip_different_keys_fail(self):
        """Test that different keys break round trip."""
        key1, _ = derive_key_with_new_salt("password1")
        key2, _ = derive_key_with_new_salt("password2")
        plaintext = b"secret"
        
        ciphertext, iv = encrypt(plaintext, key1)
        
        # Cannot decrypt with different key
        with pytest.raises(AuthenticationError):
            decrypt(ciphertext, key2, iv)


class TestTextConvenience:
    """Test suite for text encryption convenience functions."""
    
    def test_encrypt_text_basic(self):
        """Test text encryption convenience function."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = "Hello, World!"
        
        ciphertext, iv = encrypt_text(plaintext, key)
        
        assert isinstance(ciphertext, bytes)
        assert isinstance(iv, bytes)
        assert len(iv) == IV_LENGTH
    
    def test_decrypt_text_basic(self):
        """Test text decryption convenience function."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = "Hello, World!"
        
        ciphertext, iv = encrypt_text(plaintext, key)
        recovered = decrypt_text(ciphertext, key, iv)
        
        assert recovered == plaintext
        assert isinstance(recovered, str)
    
    def test_text_round_trip_unicode(self):
        """Test text round trip with Unicode."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = "Héllø Wörld 🌍"
        
        ciphertext, iv = encrypt_text(plaintext, key)
        recovered = decrypt_text(ciphertext, key, iv)
        
        assert recovered == plaintext
    
    def test_text_round_trip_empty(self):
        """Test text round trip with empty string."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = ""
        
        ciphertext, iv = encrypt_text(plaintext, key)
        recovered = decrypt_text(ciphertext, key, iv)
        
        assert recovered == plaintext
        assert recovered == ""


class TestSecurityProperties:
    """Test suite for security properties."""
    
    def test_semantic_security(self):
        """Test semantic security: same plaintext → different ciphertexts."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"same plaintext"
        
        # Encrypt same plaintext multiple times
        results = [encrypt(plaintext, key) for _ in range(10)]
        ciphertexts = [c for c, iv in results]
        ivs = [iv for c, iv in results]
        
        # All IVs should be unique
        assert len(set(ivs)) == 10
        
        # All ciphertexts should be unique
        assert len(set(ciphertexts)) == 10
        
        # But all should decrypt to same plaintext
        for ciphertext, iv in results:
            assert decrypt(ciphertext, key, iv) == plaintext
    
    def test_avalanche_effect(self):
        """Test avalanche effect: small plaintext change → large ciphertext change."""
        key, _ = derive_key_with_new_salt("password")
        iv = generate_iv()  # Use same IV to isolate plaintext effect
        
        plaintext1 = b"test message 1"
        plaintext2 = b"test message 2"  # Only one char different
        
        # Use internal AESGCM to control IV
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(key)
        
        ciphertext1 = aesgcm.encrypt(iv, plaintext1, b"")
        ciphertext2 = aesgcm.encrypt(iv, plaintext2, b"")
        
        # Ciphertexts should be very different
        assert ciphertext1 != ciphertext2
        
        # Count differing bytes
        min_len = min(len(ciphertext1), len(ciphertext2))
        diff_count = sum(c1 != c2 for c1, c2 in zip(ciphertext1[:min_len], ciphertext2[:min_len]))
        
        # At least 50% of bytes should differ (avalanche effect)
        assert diff_count / min_len > 0.5
    
    def test_iv_uniqueness_critical(self):
        """Test that IV reuse with same key is detectable (security test)."""
        key, _ = derive_key_with_new_salt("password")
        
        plaintext1 = b"message one"
        plaintext2 = b"message two"
        
        # Encrypt with fresh IVs (correct usage)
        ct1, iv1 = encrypt(plaintext1, key)
        ct2, iv2 = encrypt(plaintext2, key)
        
        # IVs must be different
        assert iv1 != iv2
        
        # Both should decrypt correctly
        assert decrypt(ct1, key, iv1) == plaintext1
        assert decrypt(ct2, key, iv2) == plaintext2
    
    def test_authentication_prevents_silent_corruption(self):
        """Test that corruption is detected, not silently accepted."""
        key, _ = derive_key_with_new_salt("password")
        plaintext = b"important data"
        
        ciphertext, iv = encrypt(plaintext, key)
        
        # Corrupt various positions
        for position in [0, len(ciphertext)//2, -1]:
            corrupted = bytearray(ciphertext)
            corrupted[position] ^= 0xFF  # Flip all bits at position
            
            # Must raise AuthenticationError, not return corrupted plaintext
            with pytest.raises(AuthenticationError):
                decrypt(bytes(corrupted), key, iv)


class TestConstants:
    """Test suite for module constants."""
    
    def test_constants_match_specification(self):
        """Test that constants match SECURITY.md."""
        assert IV_LENGTH == 12  # GCM recommendation
        assert KEY_LENGTH == 32  # AES-256
        assert TAG_LENGTH == 16  # GCM standard
