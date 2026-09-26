"""Unit tests for PBKDF2 key derivation.

Tests for T13 - PBKDF2 Key Derivation
Author: Hana (247006111170)
"""

import pytest
from backend.crypto.pbkdf2 import (
    derive_key,
    derive_key_with_new_salt,
    generate_salt,
    validate_determinism,
    PBKDF2_ITERATIONS,
    SALT_LENGTH,
    KEY_LENGTH,
)


class TestPBKDF2KeyDerivation:
    """Test suite for PBKDF2-HMAC-SHA-256 key derivation."""
    
    def test_generate_salt_length(self):
        """Test that generate_salt produces correct length."""
        salt = generate_salt()
        assert len(salt) == SALT_LENGTH
        assert len(salt) == 16
    
    def test_generate_salt_randomness(self):
        """Test that generate_salt produces different salts."""
        salt1 = generate_salt()
        salt2 = generate_salt()
        salt3 = generate_salt()
        
        # All salts should be different (extremely high probability)
        assert salt1 != salt2
        assert salt2 != salt3
        assert salt1 != salt3
    
    def test_derive_key_length(self):
        """Test that derive_key produces 32-byte key."""
        salt = generate_salt()
        key = derive_key("test_password", salt)
        
        assert len(key) == KEY_LENGTH
        assert len(key) == 32
    
    def test_derive_key_determinism(self):
        """Test that same password+salt produces same key (deterministic)."""
        password = "my_secure_password_123"
        salt = generate_salt()
        
        key1 = derive_key(password, salt)
        key2 = derive_key(password, salt)
        key3 = derive_key(password, salt)
        
        # Same inputs must produce identical keys
        assert key1 == key2
        assert key2 == key3
        assert key1 == key3
        
        # Also test with validation function
        assert validate_determinism(password, salt)
    
    def test_derive_key_different_password(self):
        """Test that different passwords produce different keys."""
        salt = generate_salt()
        
        key1 = derive_key("password1", salt)
        key2 = derive_key("password2", salt)
        key3 = derive_key("Password1", salt)  # case-sensitive
        
        # Different passwords must produce different keys
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3
    
    def test_derive_key_different_salt(self):
        """Test that different salts produce different keys."""
        password = "same_password"
        
        salt1 = generate_salt()
        salt2 = generate_salt()
        
        key1 = derive_key(password, salt1)
        key2 = derive_key(password, salt2)
        
        # Same password with different salts must produce different keys
        assert key1 != key2
    
    def test_derive_key_bytes_password(self):
        """Test that derive_key accepts bytes password."""
        salt = generate_salt()
        password_str = "test_password"
        password_bytes = password_str.encode('utf-8')
        
        key1 = derive_key(password_str, salt)
        key2 = derive_key(password_bytes, salt)
        
        # Both should produce same key
        assert key1 == key2
    
    def test_derive_key_invalid_salt_length(self):
        """Test that derive_key rejects invalid salt length."""
        with pytest.raises(ValueError, match="Salt must be 16 bytes"):
            derive_key("password", b"short")
        
        with pytest.raises(ValueError, match="Salt must be 16 bytes"):
            derive_key("password", b"toolongsalttoolongsalt")
    
    def test_derive_key_invalid_password_type(self):
        """Test that derive_key rejects invalid password type."""
        salt = generate_salt()
        
        with pytest.raises(TypeError, match="Password must be str or bytes"):
            derive_key(12345, salt)
        
        with pytest.raises(TypeError, match="Password must be str or bytes"):
            derive_key(None, salt)
    
    def test_derive_key_with_new_salt(self):
        """Test convenience function for generating salt and deriving key."""
        password = "test_password"
        
        key1, salt1 = derive_key_with_new_salt(password)
        key2, salt2 = derive_key_with_new_salt(password)
        
        # Check lengths
        assert len(key1) == KEY_LENGTH
        assert len(salt1) == SALT_LENGTH
        assert len(key2) == KEY_LENGTH
        assert len(salt2) == SALT_LENGTH
        
        # Salts should be different (fresh random)
        assert salt1 != salt2
        
        # Keys should be different (because salts are different)
        assert key1 != key2
        
        # But if we re-derive with same salt, should get same key
        key1_again = derive_key(password, salt1)
        assert key1 == key1_again
    
    def test_derive_key_empty_password(self):
        """Test that empty password is valid (though not recommended)."""
        salt = generate_salt()
        key = derive_key("", salt)
        
        assert len(key) == KEY_LENGTH
        assert isinstance(key, bytes)
    
    def test_derive_key_unicode_password(self):
        """Test that Unicode passwords work correctly."""
        salt = generate_salt()
        
        # Test with various Unicode characters
        passwords = [
            "パスワード",  # Japanese
            "пароль",      # Russian
            "密码",        # Chinese
            "🔒🔐🔑",      # Emoji
            "café_résumé", # Accented
        ]
        
        for password in passwords:
            key = derive_key(password, salt)
            assert len(key) == KEY_LENGTH
            
            # Verify determinism with Unicode
            key2 = derive_key(password, salt)
            assert key == key2
    
    def test_pbkdf2_parameters(self):
        """Test that PBKDF2 parameters match specification."""
        # Verify constants match SECURITY.md requirements
        assert PBKDF2_ITERATIONS == 600_000
        assert SALT_LENGTH == 16
        assert KEY_LENGTH == 32
    
    def test_derive_key_nonascii_bytes(self):
        """Test derive_key with non-ASCII bytes."""
        salt = generate_salt()
        password_bytes = b'\xff\xfe\xfd\xfc'
        
        key = derive_key(password_bytes, salt)
        assert len(key) == KEY_LENGTH
        
        # Verify determinism
        key2 = derive_key(password_bytes, salt)
        assert key == key2


class TestPBKDF2Integration:
    """Integration tests for PBKDF2 usage patterns."""
    
    def test_embed_extract_pattern(self):
        """Test typical embed/extract workflow pattern."""
        password = "user_password_123"
        
        # Embedding: generate fresh salt and derive key
        embed_key, salt = derive_key_with_new_salt(password)
        
        # Simulate storing salt (would be in STGR container)
        stored_salt = salt
        
        # Extraction: derive key from password and stored salt
        extract_key = derive_key(password, stored_salt)
        
        # Keys must match for successful decryption
        assert embed_key == extract_key
    
    def test_wrong_password_produces_different_key(self):
        """Test that wrong password at extraction produces different key."""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        # Embedding with correct password
        embed_key, salt = derive_key_with_new_salt(correct_password)
        
        # Extraction attempt with wrong password
        extract_key = derive_key(wrong_password, salt)
        
        # Keys must be different (decryption will fail)
        assert embed_key != extract_key
    
    def test_multiple_embeds_different_salts(self):
        """Test that multiple embeds with same password use different salts."""
        password = "same_password"
        
        # Multiple embedding operations
        key1, salt1 = derive_key_with_new_salt(password)
        key2, salt2 = derive_key_with_new_salt(password)
        key3, salt3 = derive_key_with_new_salt(password)
        
        # All salts must be different
        assert salt1 != salt2
        assert salt2 != salt3
        assert salt1 != salt3
        
        # All keys must be different (because salts differ)
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3
