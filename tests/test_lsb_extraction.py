"""
Unit Tests for T11 - 1-bit RGB LSB Extraction
Stegora Steganography Core

Author: Naufal (247006111158)
Task: T11 - 1-bit RGB LSB Extraction
"""
import pytest
import numpy as np
from PIL import Image

from backend.stego.lsb import (
    embed_lsb,
    extract_lsb,
    LSBError
)
from backend.stego.positions import generate_positions
from backend.image.metrics import calculate_mse, calculate_psnr


@pytest.fixture
def sample_rgb_image():
    """Create a sample 100x100 RGB image with gradient pattern"""
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    for y in range(100):
        for x in range(100):
            arr[y, x] = [x * 2, y * 2, (x + y)]
    return Image.fromarray(arr)


@pytest.fixture
def sample_rgba_image():
    """Create a sample 100x100 RGBA image"""
    arr = np.zeros((100, 100, 4), dtype=np.uint8)
    for y in range(100):
        for x in range(100):
            arr[y, x] = [x * 2, y * 2, (x + y), 200]
    return Image.fromarray(arr)


class TestLSBExtraction:
    """Test suite for 1-bit RGB LSB extraction"""

    def test_extract_lsb_rgb_success(self, sample_rgb_image):
        """Test successful extraction from RGB image"""
        payload = b"Hello World!"
        num_bits = len(payload) * 8
        positions = generate_positions(100, 100, "extract_key", num_bits)

        # Embed first
        stego = embed_lsb(sample_rgb_image, payload, positions)
        
        # Extract
        extracted = extract_lsb(stego, positions, len(payload))

        assert isinstance(extracted, bytes)
        assert len(extracted) == len(payload)
        assert extracted == payload

    def test_extract_lsb_rgba_success(self, sample_rgba_image):
        """Test successful extraction from RGBA image"""
        payload = b"RGBA extraction test"
        num_bits = len(payload) * 8
        positions = generate_positions(100, 100, "rgba_extract", num_bits)

        # Embed and extract
        stego = embed_lsb(sample_rgba_image, payload, positions)
        extracted = extract_lsb(stego, positions, len(payload))

        assert extracted == payload

    def test_round_trip_various_payloads(self, sample_rgb_image):
        """Test round-trip (embed → extract) with various payloads"""
        test_cases = [
            b"Short",
            b"A" * 100,
            b"Unicode test: \xc2\xa9 \xe2\x9c\x93",
            b"\x00\x01\x02\xff\xfe\xfd",  # Binary data
            b"The quick brown fox jumps over the lazy dog",
        ]
        
        for idx, payload in enumerate(test_cases):
            key = f"test_key_{idx}"
            num_bits = len(payload) * 8
            positions = generate_positions(100, 100, key, num_bits)
            
            stego = embed_lsb(sample_rgb_image, payload, positions)
            extracted = extract_lsb(stego, positions, len(payload))
            
            assert extracted == payload, f"Round-trip failed for test case {idx}"

    def test_round_trip_large_payload(self, sample_rgb_image):
        """Test round-trip with large payload"""
        # 1KB payload
        payload = b"X" * 1000
        num_bits = len(payload) * 8
        
        # Need larger image for 1KB
        large_image = Image.new('RGB', (300, 300), color='blue')
        positions = generate_positions(300, 300, "large_key", num_bits)
        
        stego = embed_lsb(large_image, payload, positions)
        extracted = extract_lsb(stego, positions, len(payload))
        
        assert extracted == payload
        assert len(extracted) == 1000

    def test_extract_with_wrong_stego_key_produces_garbage(self, sample_rgb_image):
        """Test that wrong stego-key produces incorrect extraction"""
        payload = b"Secret message"
        num_bits = len(payload) * 8
        
        # Embed with key A
        positions_a = generate_positions(100, 100, "correct_key_A", num_bits)
        stego = embed_lsb(sample_rgb_image, payload, positions_a)
        
        # Extract with key B (wrong key)
        positions_b = generate_positions(100, 100, "wrong_key_B", num_bits)
        extracted_wrong = extract_lsb(stego, positions_b, len(payload))
        
        # Should NOT match original payload
        assert extracted_wrong != payload, "Wrong key should not extract correct data"
        assert len(extracted_wrong) == len(payload), "Length should still match"

    def test_extract_preserves_image_unchanged(self, sample_rgb_image):
        """Test that extraction does not modify the stego image"""
        payload = b"Extract without modify"
        num_bits = len(payload) * 8
        positions = generate_positions(100, 100, "preserve_key", num_bits)
        
        stego = embed_lsb(sample_rgb_image, payload, positions)
        stego_before = np.array(stego).copy()
        
        # Extract
        extracted = extract_lsb(stego, positions, len(payload))
        stego_after = np.array(stego)
        
        # Stego image should be unchanged
        assert np.array_equal(stego_before, stego_after)
        assert extracted == payload

    def test_extract_bit_accuracy(self, sample_rgb_image):
        """Test bit-level accuracy of extraction"""
        # Use known bit patterns
        payload = bytes([0b10101010, 0b11110000, 0b00001111])
        num_bits = len(payload) * 8
        positions = generate_positions(100, 100, "bit_test", num_bits)
        
        stego = embed_lsb(sample_rgb_image, payload, positions)
        extracted = extract_lsb(stego, positions, len(payload))
        
        # Check bit-by-bit
        for i in range(len(payload)):
            assert extracted[i] == payload[i], \
                f"Byte {i}: expected {payload[i]:08b}, got {extracted[i]:08b}"


class TestLSBExtractionValidation:
    """Test suite for extraction validation and error handling"""

    def test_reject_invalid_image_type(self):
        """Non-PIL Image should raise LSBError"""
        with pytest.raises(LSBError, match="must be a PIL Image"):
            extract_lsb("not_an_image", [(0, 0, 0)] * 8, 1)

    def test_reject_unsupported_mode(self):
        """Grayscale images should raise LSBError"""
        gray_img = Image.new('L', (50, 50), color=128)
        positions = [(0, 0, 0)] * 8
        with pytest.raises(LSBError, match="Unsupported image mode"):
            extract_lsb(gray_img, positions, 1)

    def test_reject_zero_num_bytes(self, sample_rgb_image):
        """Zero or negative num_bytes should raise LSBError"""
        positions = [(0, 0, 0)] * 8
        with pytest.raises(LSBError, match="must be positive"):
            extract_lsb(sample_rgb_image, positions, 0)

    def test_reject_negative_num_bytes(self, sample_rgb_image):
        """Negative num_bytes should raise LSBError"""
        positions = [(0, 0, 0)] * 8
        with pytest.raises(LSBError, match="must be positive"):
            extract_lsb(sample_rgb_image, positions, -5)

    def test_reject_insufficient_positions(self, sample_rgb_image):
        """Fewer positions than needed should raise LSBError"""
        # Need 8 positions for 1 byte, provide only 5
        positions = [(0, 0, 0)] * 5
        with pytest.raises(LSBError, match="Not enough positions"):
            extract_lsb(sample_rgb_image, positions, 1)

    def test_reject_out_of_bounds_coordinates(self, sample_rgb_image):
        """Coordinates outside image bounds should raise LSBError"""
        # x=200 is out of bounds for 100x100 image
        positions = [(200, 0, 0)] + [(0, 0, 0)] * 7
        with pytest.raises(LSBError, match="outside image dimensions"):
            extract_lsb(sample_rgb_image, positions, 1)

    def test_reject_alpha_channel_index(self, sample_rgba_image):
        """Channel index 3 (Alpha) must be rejected"""
        # channel=3 (Alpha) is forbidden
        positions = [(0, 0, 3)] + [(0, 0, 0)] * 7
        with pytest.raises(LSBError, match="Only RGB channels"):
            extract_lsb(sample_rgba_image, positions, 1)


class TestRoundTripIntegration:
    """Integration tests for complete embed-extract cycle"""

    def test_round_trip_maintains_quality_metrics(self, sample_rgb_image):
        """Test that round-trip maintains expected quality metrics"""
        payload = b"Quality metrics test payload"
        num_bits = len(payload) * 8
        positions = generate_positions(100, 100, "quality_key", num_bits)
        
        # Embed
        stego = embed_lsb(sample_rgb_image, payload, positions)
        
        # Check quality
        mse = calculate_mse(sample_rgb_image, stego)
        psnr = calculate_psnr(sample_rgb_image, stego, mse=mse)
        
        assert mse > 0, "MSE should be positive (real modifications)"
        assert psnr > 45.0, f"PSNR should be high (>45 dB), got {psnr:.2f}"
        
        # Extract and verify
        extracted = extract_lsb(stego, positions, len(payload))
        assert extracted == payload

    def test_round_trip_multiple_payloads_same_image(self):
        """Test embedding and extracting different payloads from same cover"""
        cover = Image.new('RGB', (200, 200), color='white')
        
        test_payloads = [
            (b"First payload", "key1"),
            (b"Second different payload", "key2"),
            (b"Third unique data", "key3"),
        ]
        
        for payload, key in test_payloads:
            num_bits = len(payload) * 8
            positions = generate_positions(200, 200, key, num_bits)
            
            stego = embed_lsb(cover, payload, positions)
            extracted = extract_lsb(stego, positions, len(payload))
            
            assert extracted == payload, f"Failed for key {key}"

    def test_round_trip_preserves_binary_data(self):
        """Test that binary data (not text) is preserved exactly"""
        # Binary data with all possible byte values
        payload = bytes(range(256))
        
        cover = Image.new('RGB', (300, 300), color='green')
        num_bits = len(payload) * 8
        positions = generate_positions(300, 300, "binary_key", num_bits)
        
        stego = embed_lsb(cover, payload, positions)
        extracted = extract_lsb(stego, positions, len(payload))
        
        assert extracted == payload
        # Verify every byte
        for i in range(256):
            assert extracted[i] == i

    def test_deterministic_extraction_same_key(self, sample_rgb_image):
        """Test that same key always produces same extraction"""
        payload = b"Deterministic test"
        num_bits = len(payload) * 8
        key = "deterministic_key_123"
        
        # Embed once
        positions = generate_positions(100, 100, key, num_bits)
        stego = embed_lsb(sample_rgb_image, payload, positions)
        
        # Extract multiple times with same key
        positions1 = generate_positions(100, 100, key, num_bits)
        extracted1 = extract_lsb(stego, positions1, len(payload))
        
        positions2 = generate_positions(100, 100, key, num_bits)
        extracted2 = extract_lsb(stego, positions2, len(payload))
        
        assert extracted1 == extracted2 == payload


class TestWrongKeyFailure:
    """Test suite for wrong key failure scenarios"""

    def test_wrong_key_produces_different_data(self, sample_rgb_image):
        """Test that wrong key extracts garbage data"""
        payload = b"Correct data with correct key"
        num_bits = len(payload) * 8
        
        correct_key = "correct_key_ABC"
        wrong_key = "wrong_key_XYZ"
        
        # Embed with correct key
        positions_correct = generate_positions(100, 100, correct_key, num_bits)
        stego = embed_lsb(sample_rgb_image, payload, positions_correct)
        
        # Extract with correct key (should work)
        extracted_correct = extract_lsb(stego, positions_correct, len(payload))
        assert extracted_correct == payload
        
        # Extract with wrong key (should get garbage)
        positions_wrong = generate_positions(100, 100, wrong_key, num_bits)
        extracted_wrong = extract_lsb(stego, positions_wrong, len(payload))
        
        assert extracted_wrong != payload
        assert len(extracted_wrong) == len(payload)

    def test_wrong_key_high_bit_error_rate(self, sample_rgb_image):
        """Test that wrong key produces high bit error rate"""
        payload = b"Test bit error rate"
        num_bits = len(payload) * 8
        
        # Embed with key A
        positions_a = generate_positions(100, 100, "keyA", num_bits)
        stego = embed_lsb(sample_rgb_image, payload, positions_a)
        
        # Extract with key B
        positions_b = generate_positions(100, 100, "keyB", num_bits)
        extracted_wrong = extract_lsb(stego, positions_b, len(payload))
        
        # Count bit errors
        bit_errors = 0
        for i in range(len(payload)):
            xor = payload[i] ^ extracted_wrong[i]
            bit_errors += bin(xor).count('1')
        
        bit_error_rate = bit_errors / (len(payload) * 8)
        
        # With wrong key, expect ~50% bit error rate (random-like)
        assert bit_error_rate > 0.3, f"Bit error rate too low: {bit_error_rate:.2%}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
