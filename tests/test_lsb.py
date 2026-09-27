"""
Unit Tests for T10 - 1-bit RGB LSB Embedding
Stegora Steganography Core

Author: Naufal (247006111158)
Task: T10 - 1-bit RGB LSB Embedding
"""
import pytest
import numpy as np
from PIL import Image

from backend.stego.lsb import (
    embed_lsb,
    verify_alpha_preservation,
    LSBError
)
from backend.stego.positions import generate_positions
from backend.image.metrics import calculate_mse, calculate_psnr


@pytest.fixture
def sample_rgb_image():
    """Create a sample 50x50 RGB image with gradient pattern"""
    arr = np.zeros((50, 50, 3), dtype=np.uint8)
    for y in range(50):
        for x in range(50):
            arr[y, x] = [x * 4, y * 4, (x + y) * 2]
    return Image.fromarray(arr)


@pytest.fixture
def sample_rgba_image():
    """Create a sample 50x50 RGBA image with variable transparency"""
    arr = np.zeros((50, 50, 4), dtype=np.uint8)
    for y in range(50):
        for x in range(50):
            arr[y, x] = [x * 4, y * 4, (x + y) * 2, 128 + (x % 128)]
    return Image.fromarray(arr)


class TestLSBEmbedding:
    """Test suite for 1-bit RGB LSB embedding"""

    def test_embed_lsb_rgb_success(self, sample_rgb_image):
        """Test successful embedding in an RGB image"""
        payload = b"Hello Stegora 2026!"
        num_bits = len(payload) * 8
        positions = generate_positions(50, 50, "test_stego_key", num_bits)

        stego = embed_lsb(sample_rgb_image, payload, positions)

        assert isinstance(stego, Image.Image)
        assert stego.size == sample_rgb_image.size
        assert stego.mode == 'RGB'

        # Verify bit-level accuracy at embedded positions
        stego_arr = np.array(stego)
        expected_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        for i, (x, y, c) in enumerate(positions[:num_bits]):
            actual_bit = stego_arr[y, x, c] & 1
            assert actual_bit == expected_bits[i], f"Bit mismatch at index {i} pos ({x}, {y}, {c})"

    def test_embed_lsb_only_modifies_least_significant_bit(self, sample_rgb_image):
        """Test that only bit 0 (LSB) is altered; upper 7 bits remain identical"""
        payload = b"Exact LSB Bit Preservation Test"
        num_bits = len(payload) * 8
        positions = generate_positions(50, 50, "key_bits_test", num_bits)

        stego = embed_lsb(sample_rgb_image, payload, positions)

        cover_arr = np.array(sample_rgb_image)
        stego_arr = np.array(stego)

        # Difference in pixel values must be at most 1 (0 or 1)
        diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
        assert np.max(diff) <= 1, "Pixel altered by more than 1 (upper bits corrupted)!"

        # For positions that were NOT in the embedding list, diff must be strictly 0
        embedded_mask = np.zeros(cover_arr.shape, dtype=bool)
        for x, y, c in positions[:num_bits]:
            embedded_mask[y, x, c] = True

        assert np.all(cover_arr[~embedded_mask] == stego_arr[~embedded_mask]), \
            "Unindexed pixels were modified!"

    def test_embed_lsb_preserves_alpha_strictly(self, sample_rgba_image):
        """Test that RGBA alpha channel (channel 3) is 100% preserved"""
        payload = b"Alpha Channel Preservation Test Payload"
        num_bits = len(payload) * 8
        positions = generate_positions(50, 50, "alpha_test_key", num_bits)

        stego = embed_lsb(sample_rgba_image, payload, positions)

        assert stego.mode == 'RGBA'
        assert verify_alpha_preservation(sample_rgba_image, stego) is True

        cover_alpha = np.array(sample_rgba_image)[:, :, 3]
        stego_alpha = np.array(stego)[:, :, 3]
        assert np.array_equal(cover_alpha, stego_alpha), "Alpha channel was altered!"

    def test_embed_lsb_different_stego_keys_produce_different_images(self, sample_rgb_image):
        """Test that different stego keys embed into different pixel coordinates"""
        payload = b"Identical payload for different keys"
        num_bits = len(payload) * 8

        pos1 = generate_positions(50, 50, "first_unique_key_111", num_bits)
        pos2 = generate_positions(50, 50, "second_unique_key_222", num_bits)

        stego1 = embed_lsb(sample_rgb_image, payload, pos1)
        stego2 = embed_lsb(sample_rgb_image, payload, pos2)

        arr1 = np.array(stego1)
        arr2 = np.array(stego2)
        assert not np.array_equal(arr1, arr2), \
            "Stego images with different keys must have different modified pixels!"

    def test_embed_lsb_metrics_reflect_real_modifications(self, sample_rgb_image):
        """Test that real LSB embedding produces non-zero MSE and realistic PSNR"""
        payload = b"Real MSE/PSNR calculation verification payload"
        num_bits = len(payload) * 8
        positions = generate_positions(50, 50, "metrics_key", num_bits)

        stego = embed_lsb(sample_rgb_image, payload, positions)

        mse = calculate_mse(sample_rgb_image, stego)
        psnr = calculate_psnr(sample_rgb_image, stego, mse=mse)

        # MSE must be strictly positive (real modifications)
        assert mse > 0, "MSE should be positive after real LSB embedding"
        # PSNR for 1-bit LSB should typically be > 50 dB (very high quality)
        assert psnr > 45.0, f"PSNR should be high (>45 dB), got {psnr:.2f}"
        assert psnr < float('inf'), "PSNR should be finite"


class TestLSBValidationAndErrors:
    """Test suite for error conditions and input validation in embed_lsb"""

    def test_reject_invalid_image_type(self):
        """Non-PIL Image should raise LSBError"""
        with pytest.raises(LSBError, match="must be a PIL Image"):
            embed_lsb("not_an_image", b"payload", [(0, 0, 0)] * 56)

    def test_reject_unsupported_mode(self):
        """Grayscale (L) or CMYK images should raise LSBError"""
        gray_img = Image.new('L', (20, 20), color=128)
        positions = [(0, 0, 0)] * 8
        with pytest.raises(LSBError, match="Unsupported image mode"):
            embed_lsb(gray_img, b"X", positions)

    def test_reject_empty_payload(self, sample_rgb_image):
        """Empty container bytes should raise LSBError"""
        positions = [(0, 0, 0)] * 8
        with pytest.raises(LSBError, match="cannot be empty"):
            embed_lsb(sample_rgb_image, b"", positions)

    def test_reject_insufficient_positions(self, sample_rgb_image):
        """Fewer positions than payload bits should raise LSBError"""
        payload = b"Test"  # 32 bits
        positions = [(0, 0, 0)] * 10  # Only 10 positions
        with pytest.raises(LSBError, match="Not enough positions"):
            embed_lsb(sample_rgb_image, payload, positions)

    def test_reject_out_of_bounds_coordinates(self, sample_rgb_image):
        """Coordinates outside image bounds should raise LSBError"""
        payload = b"X"  # 8 bits
        # x=100 is out of bounds for 50x50 image
        positions = [(100, 0, 0)] + [(0, 0, 0)] * 7
        with pytest.raises(LSBError, match="outside image dimensions"):
            embed_lsb(sample_rgb_image, payload, positions)

    def test_reject_alpha_channel_index(self, sample_rgba_image):
        """Channel index 3 (Alpha) in positions must be rejected"""
        payload = b"X"  # 8 bits
        # channel=3 (Alpha) is forbidden
        positions = [(0, 0, 3)] + [(0, 0, 0)] * 7
        with pytest.raises(LSBError, match="only RGB channels .* allowed"):
            embed_lsb(sample_rgba_image, payload, positions)
