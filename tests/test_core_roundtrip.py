"""
Unit Tests for T12 - Core Round-Trip Tests
Stegora Steganography Core

Comprehensive round-trip testing for embed → extract cycle.
Tests cover: text/file payloads, boundary capacity, wrong credentials,
malformed headers, alpha preservation, and integration scenarios.

Author: Naufal (247006111158)
Task: T12 - Core Round-Trip Tests
"""
import pytest
import numpy as np
from PIL import Image
import io
import secrets

from backend.stego.lsb import embed_lsb, extract_lsb, LSBError
from backend.stego.positions import generate_positions
from backend.stego.capacity import (
    calculate_raw_capacity,
    check_payload_capacity,
    PayloadCapacityExceededError
)
from backend.stego.container import create_container, parse_container, ContainerError
from backend.crypto.pbkdf2 import derive_key
from backend.crypto.aes_gcm import encrypt, decrypt
from backend.pipeline import embed_pipeline, extract_pipeline, EmbedError, ExtractError
from backend.image.metrics import calculate_mse, calculate_psnr


@pytest.fixture
def small_rgb_image():
    """100×100 RGB image for small payloads"""
    return Image.new('RGB', (100, 100), color='white')


@pytest.fixture
def medium_rgb_image():
    """300×300 RGB image for medium payloads"""
    arr = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.fixture
def large_rgb_image():
    """500×500 RGB image for large payloads"""
    arr = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.fixture
def rgba_image():
    """200×200 RGBA image with transparency"""
    arr = np.random.randint(0, 256, (200, 200, 4), dtype=np.uint8)
    return Image.fromarray(arr)


class TestTextRoundTrip:
    """Test suite for text payload round-trip"""

    def test_short_text_round_trip(self, small_rgb_image):
        """Test round-trip with short text message"""
        payload = b"Hello World!"
        password = "password123"
        stego_key = "stegokey123"
        
        # Full pipeline
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key,
            filename="test.txt", mime_type="text/plain"
        )
        
        extracted, meta = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert meta['filename'] == "test.txt"
        assert meta['mime_type'] == "text/plain"

    def test_long_text_round_trip(self, medium_rgb_image):
        """Test round-trip with long text (1000+ characters)"""
        payload = b"Lorem ipsum dolor sit amet. " * 50  # ~1400 bytes
        password = "longtext_pass"
        stego_key = "longtext_key"
        
        stego, embed_meta = embed_pipeline(
            medium_rgb_image, payload, password, stego_key
        )
        
        extracted, extract_meta = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert len(extracted) == len(payload)
        assert embed_meta['payload_size'] == extract_meta['plaintext_size']

    def test_unicode_text_round_trip(self, small_rgb_image):
        """Test round-trip with Unicode characters"""
        payload = "Héllo Wørld! 你好世界 مرحبا العالم".encode('utf-8')
        password = "unicode_pass"
        stego_key = "unicode_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert extracted.decode('utf-8') == payload.decode('utf-8')

    def test_special_characters_round_trip(self, small_rgb_image):
        """Test round-trip with special characters and symbols"""
        payload = b"Special: !@#$%^&*()_+-=[]{}|;':\",./<>?`~\n\t\r"
        password = "special_pass"
        stego_key = "special_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload

    def test_empty_string_rejected(self, small_rgb_image):
        """Test that empty payload is rejected"""
        with pytest.raises(EmbedError, match="cannot be empty"):
            embed_pipeline(
                small_rgb_image, b"", "pass", "key"
            )


class TestFileRoundTrip:
    """Test suite for file payload round-trip"""

    def test_binary_file_round_trip(self, medium_rgb_image):
        """Test round-trip with binary file data"""
        # Simulate binary file (all byte values 0-255)
        payload = bytes(range(256))
        password = "binary_pass"
        stego_key = "binary_key"
        
        stego, embed_meta = embed_pipeline(
            medium_rgb_image, payload, password, stego_key,
            filename="data.bin", mime_type="application/octet-stream"
        )
        
        extracted, extract_meta = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert extract_meta['filename'] == "data.bin"
        assert extract_meta['mime_type'] == "application/octet-stream"
        
        # Verify every byte
        for i in range(256):
            assert extracted[i] == i

    def test_json_file_round_trip(self, small_rgb_image):
        """Test round-trip with JSON file"""
        payload = b'{"name":"test","value":123,"nested":{"key":"val"}}'
        password = "json_pass"
        stego_key = "json_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key,
            filename="data.json", mime_type="application/json"
        )
        
        extracted, meta = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert meta['filename'] == "data.json"
        assert meta['mime_type'] == "application/json"

    def test_csv_file_round_trip(self, small_rgb_image):
        """Test round-trip with CSV file"""
        payload = b"name,age,city\nAlice,30,NYC\nBob,25,LA\n"
        password = "csv_pass"
        stego_key = "csv_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key,
            filename="data.csv", mime_type="text/csv"
        )
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload

    def test_large_file_round_trip(self, large_rgb_image):
        """Test round-trip with large file (10KB)"""
        payload = b"X" * 10240  # 10KB
        password = "large_pass"
        stego_key = "large_key"
        
        stego, embed_meta = embed_pipeline(
            large_rgb_image, payload, password, stego_key,
            filename="large.dat"
        )
        
        extracted, extract_meta = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert len(extracted) == 10240
        assert embed_meta['payload_size'] == 10240


class TestBoundaryCapacity:
    """Test suite for boundary capacity scenarios"""

    def test_near_max_capacity(self, medium_rgb_image):
        """Test payload near maximum capacity"""
        # Calculate capacity
        capacity = calculate_raw_capacity(300, 300)
        usable = capacity['total_bytes'] - 150  # Leave room for container overhead
        
        payload = b"X" * usable
        password = "capacity_pass"
        stego_key = "capacity_key"
        
        stego, embed_meta = embed_pipeline(
            medium_rgb_image, payload, password, stego_key
        )
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert embed_meta['capacity_utilization'] > 90.0  # Should be high utilization

    def test_oversized_payload_rejected(self, small_rgb_image):
        """Test that oversized payload is rejected before embedding"""
        # Small image: 100×100 = 30,000 bits = 3,750 bytes raw
        # With overhead, usable is ~3,600 bytes
        oversized_payload = b"X" * 5000  # Too large
        
        with pytest.raises(EmbedError, match="too large"):
            embed_pipeline(
                small_rgb_image, oversized_payload, "pass", "key"
            )

    def test_exact_capacity_boundary(self, small_rgb_image):
        """Test payload at exact capacity boundary"""
        # Calculate exact usable capacity
        width, height = 100, 100
        raw_capacity = (width * height * 3) // 8  # 3750 bytes
        
        # Account for container overhead (header + metadata + salt + IV)
        # Approximate: 12 (header) + 5 (meta lengths) + 16 (salt) + 12 (IV) + 
        #              16 (GCM tag) + filenames ~100 bytes overhead
        safe_payload_size = raw_capacity - 150
        
        payload = b"B" * safe_payload_size
        password = "boundary_pass"
        stego_key = "boundary_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload

    def test_minimum_payload_size(self, small_rgb_image):
        """Test with minimum payload (1 byte)"""
        payload = b"X"
        password = "min_pass"
        stego_key = "min_key"
        
        stego, embed_meta = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        
        assert extracted == payload
        assert embed_meta['capacity_utilization'] < 5.0  # Very low utilization


class TestWrongCredentials:
    """Test suite for wrong credential scenarios"""

    def test_wrong_password_fails(self, small_rgb_image):
        """Test that wrong password causes authentication failure"""
        payload = b"Secret message"
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        stego_key = "test_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, correct_password, stego_key
        )
        
        with pytest.raises(ExtractError, match="Decryption error|Authentication failed"):
            extract_pipeline(stego, wrong_password, stego_key)

    def test_wrong_stego_key_fails(self, small_rgb_image):
        """Test that wrong stego-key causes extraction failure"""
        payload = b"Secret message"
        password = "test_password"
        correct_key = "correct_stego_key"
        wrong_key = "wrong_stego_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, correct_key
        )
        
        # Wrong stego-key reads from wrong positions → garbage data
        with pytest.raises(ExtractError, match="Invalid magic|Container parsing|Decryption|Authentication"):
            extract_pipeline(stego, password, wrong_key)

    def test_both_credentials_wrong_fails(self, small_rgb_image):
        """Test that both wrong credentials fail"""
        payload = b"Secret message"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, "correct_pass", "correct_key"
        )
        
        with pytest.raises(ExtractError):
            extract_pipeline(stego, "wrong_pass", "wrong_key")

    def test_case_sensitive_password(self, small_rgb_image):
        """Test that password is case-sensitive"""
        payload = b"Case sensitive test"
        password = "MyPassword123"
        stego_key = "test_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        # Try with different case
        with pytest.raises(ExtractError):
            extract_pipeline(stego, "mypassword123", stego_key)

    def test_case_sensitive_stego_key(self, small_rgb_image):
        """Test that stego-key is case-sensitive"""
        payload = b"Case sensitive key test"
        password = "test_pass"
        stego_key = "MyStegoKey"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        # Try with different case
        with pytest.raises(ExtractError):
            extract_pipeline(stego, password, "mystegokey")


class TestMalformedData:
    """Test suite for malformed data scenarios"""

    def test_corrupted_magic_bytes(self, small_rgb_image):
        """Test that corrupted magic bytes are detected"""
        payload = b"Test message"
        password = "test_pass"
        stego_key = "test_key"
        
        # Embed normally
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        # Corrupt the stego image by modifying some pixels drastically
        stego_arr = np.array(stego)
        stego_arr[0:10, 0:10, :] = 0  # Corrupt top-left corner
        stego_corrupted = Image.fromarray(stego_arr)
        
        # Extraction should fail
        with pytest.raises(ExtractError):
            extract_pipeline(stego_corrupted, password, stego_key)

    def test_truncated_image(self, small_rgb_image):
        """Test handling of truncated/incomplete data"""
        payload = b"Test message for truncation"
        password = "test_pass"
        stego_key = "test_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        # Create truncated image (crop)
        stego_truncated = stego.crop((0, 0, 50, 50))  # Half size
        
        # Should fail due to insufficient data
        with pytest.raises((ExtractError, LSBError)):
            extract_pipeline(stego_truncated, password, stego_key)

    def test_plain_image_without_data(self, small_rgb_image):
        """Test extraction from plain image (no embedded data)"""
        password = "test_pass"
        stego_key = "test_key"
        
        # Try to extract from plain image (no data embedded)
        with pytest.raises(ExtractError, match="Invalid magic bytes"):
            extract_pipeline(small_rgb_image, password, stego_key)

    def test_modified_stego_image(self, small_rgb_image):
        """Test detection of modified stego image"""
        payload = b"Original message"
        password = "test_pass"
        stego_key = "test_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        # Modify LSB positions that likely contain data
        # With 100x100 RGB image, first few positions contain header/payload
        stego_arr = np.array(stego)
        # Flip multiple LSBs in first 100 pixels (high probability of hitting data)
        for i in range(100):
            y = i // 100
            x = i % 100
            for c in range(3):
                stego_arr[y, x, c] ^= 1  # Flip LSB
        stego_modified = Image.fromarray(stego_arr)
        
        # Corrupted LSBs should cause extraction/decryption failure
        with pytest.raises(ExtractError):
            extract_pipeline(stego_modified, password, stego_key)


class TestAlphaPreservation:
    """Test suite for alpha channel preservation in RGBA images"""

    def test_rgba_alpha_unchanged_after_round_trip(self, rgba_image):
        """Test that alpha channel remains 100% unchanged"""
        payload = b"RGBA test message"
        password = "rgba_pass"
        stego_key = "rgba_key"
        
        # Save original alpha
        original_alpha = np.array(rgba_image)[:, :, 3].copy()
        
        # Full round-trip
        stego, _ = embed_pipeline(
            rgba_image, payload, password, stego_key
        )
        
        # Check alpha unchanged
        stego_alpha = np.array(stego)[:, :, 3]
        assert np.array_equal(original_alpha, stego_alpha), "Alpha was modified!"
        
        # Extract should work
        extracted, _ = extract_pipeline(stego, password, stego_key)
        assert extracted == payload

    def test_rgba_with_varying_transparency(self):
        """Test RGBA with varying alpha values"""
        # Create image with gradient transparency
        arr = np.zeros((100, 100, 4), dtype=np.uint8)
        for y in range(100):
            for x in range(100):
                arr[y, x] = [x*2, y*2, 128, int(x * 2.55)]  # Alpha varies 0-255
        
        rgba_gradient = Image.fromarray(arr)
        original_alpha = arr[:, :, 3].copy()
        
        payload = b"Gradient alpha test"
        password = "gradient_pass"
        stego_key = "gradient_key"
        
        stego, _ = embed_pipeline(
            rgba_gradient, payload, password, stego_key
        )
        
        stego_alpha = np.array(stego)[:, :, 3]
        assert np.array_equal(original_alpha, stego_alpha)
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        assert extracted == payload

    def test_rgba_fully_transparent(self):
        """Test RGBA with fully transparent regions"""
        arr = np.zeros((100, 100, 4), dtype=np.uint8)
        arr[:, :, 3] = 0  # Fully transparent
        rgba_transparent = Image.fromarray(arr)
        
        payload = b"Transparent test"
        password = "trans_pass"
        stego_key = "trans_key"
        
        stego, _ = embed_pipeline(
            rgba_transparent, payload, password, stego_key
        )
        
        # Alpha should still be 0
        stego_alpha = np.array(stego)[:, :, 3]
        assert np.all(stego_alpha == 0)
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        assert extracted == payload

    def test_rgba_fully_opaque(self):
        """Test RGBA with fully opaque (alpha=255)"""
        arr = np.ones((100, 100, 4), dtype=np.uint8) * 128
        arr[:, :, 3] = 255  # Fully opaque
        rgba_opaque = Image.fromarray(arr)
        
        payload = b"Opaque test"
        password = "opaque_pass"
        stego_key = "opaque_key"
        
        stego, _ = embed_pipeline(
            rgba_opaque, payload, password, stego_key
        )
        
        # Alpha should still be 255
        stego_alpha = np.array(stego)[:, :, 3]
        assert np.all(stego_alpha == 255)
        
        extracted, _ = extract_pipeline(stego, password, stego_key)
        assert extracted == payload


class TestQualityMetrics:
    """Test suite for quality metrics in round-trip"""

    def test_mse_positive_after_embedding(self, small_rgb_image):
        """Test that MSE is positive (real modifications)"""
        payload = b"Test for MSE"
        password = "mse_pass"
        stego_key = "mse_key"
        
        stego, meta = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        assert meta['mse'] > 0, "MSE should be positive"
        assert meta['mse'] < 2.0, "MSE should be small for LSB"

    def test_psnr_high_quality(self, small_rgb_image):
        """Test that PSNR indicates high quality (>40dB)"""
        payload = b"Test for PSNR"
        password = "psnr_pass"
        stego_key = "psnr_key"
        
        stego, meta = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        assert meta['psnr'] > 40.0, "PSNR should be >40dB for 1-bit LSB"
        assert meta['psnr'] < float('inf'), "PSNR should be finite"

    def test_metrics_consistency(self, medium_rgb_image):
        """Test that metrics are consistent for same stego image"""
        payload = b"Consistency test"
        password = "consistent_pass"
        stego_key = "consistent_key"
        
        # Create one stego image
        stego, meta1 = embed_pipeline(
            medium_rgb_image, payload, password, stego_key
        )
        
        # Calculate metrics twice on same stego image
        mse1 = calculate_mse(medium_rgb_image, stego)
        psnr1 = calculate_psnr(medium_rgb_image, stego)
        
        mse2 = calculate_mse(medium_rgb_image, stego)
        psnr2 = calculate_psnr(medium_rgb_image, stego)
        
        # Metrics should be identical for same image pair
        assert mse1 == mse2
        assert psnr1 == psnr2
        assert mse1 == meta1['mse']
        assert psnr1 == meta1['psnr']


class TestDeterminism:
    """Test suite for deterministic behavior"""

    def test_same_inputs_same_stego(self, small_rgb_image):
        """Test that deterministic positioning produces extractable data"""
        payload = b"Deterministic test"
        password = "det_pass"
        stego_key = "det_key"
        
        # Embed twice with same parameters
        stego1, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        stego2, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        # Extraction should work on both (positions are deterministic)
        extracted1, _ = extract_pipeline(stego1, password, stego_key)
        extracted2, _ = extract_pipeline(stego2, password, stego_key)
        
        # Extracted payloads should be identical to original
        assert extracted1 == payload
        assert extracted2 == payload
        # Note: Stego images will differ due to random salt/IV in encryption

    def test_different_key_different_stego(self, small_rgb_image):
        """Test that different stego-key produces different image"""
        payload = b"Different key test"
        password = "same_pass"
        
        stego1, _ = embed_pipeline(
            small_rgb_image, payload, password, "key1"
        )
        
        stego2, _ = embed_pipeline(
            small_rgb_image, payload, password, "key2"
        )
        
        # Images should be different
        arr1 = np.array(stego1)
        arr2 = np.array(stego2)
        assert not np.array_equal(arr1, arr2)

    def test_extraction_deterministic(self, small_rgb_image):
        """Test that extraction is deterministic"""
        payload = b"Extract deterministic"
        password = "det_pass"
        stego_key = "det_key"
        
        stego, _ = embed_pipeline(
            small_rgb_image, payload, password, stego_key
        )
        
        # Extract multiple times
        extracted1, _ = extract_pipeline(stego, password, stego_key)
        extracted2, _ = extract_pipeline(stego, password, stego_key)
        extracted3, _ = extract_pipeline(stego, password, stego_key)
        
        # All should be identical
        assert extracted1 == extracted2 == extracted3 == payload


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
