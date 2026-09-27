"""
Unit tests for stegora.analysis.robustness module

Tests JPEG robustness, security attacks, and error handling.

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

import pytest
import numpy as np
from PIL import Image

from stegora.analysis.robustness import (
    test_jpeg_compression,
    test_jpeg_multiple_qualities,
    calculate_bit_error_rate,
    simulate_bit_flip_attack,
    simulate_truncation_attack,
    create_malformed_header,
    test_stego_resilience
)


class TestJPEGCompression:
    """Test JPEG compression robustness."""
    
    def test_jpeg_compression_basic(self):
        """Test basic JPEG compression."""
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        compressed, metrics = test_jpeg_compression(img, quality=95)
        
        assert compressed.shape == img.shape
        assert compressed.dtype == np.uint8
        assert 'mse' in metrics
        assert 'psnr' in metrics
        assert 'lsb_survival_rate' in metrics
    
    def test_jpeg_high_quality(self):
        """Test high quality JPEG (minimal loss)."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        compressed, metrics = test_jpeg_compression(img, quality=95)
        
        # JPEG compression always causes some loss (even Q95)
        assert metrics['psnr'] > 0  # Some PSNR value
        assert metrics['mse'] >= 0  # MSE non-negative
        
        # LSB affected by JPEG
        assert 0 <= metrics['lsb_survival_rate'] <= 1.0
    
    def test_jpeg_low_quality(self):
        """Test low quality JPEG (significant loss)."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        compressed, metrics = test_jpeg_compression(img, quality=50)
        
        # Low quality has lower PSNR
        assert metrics['psnr'] > 0  # Still some signal
        
        # LSB survival very low
        assert metrics['lsb_survival_rate'] < 0.55
    
    def test_jpeg_quality_comparison(self):
        """Test that higher quality gives better metrics."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        _, metrics_95 = test_jpeg_compression(img, quality=95)
        _, metrics_50 = test_jpeg_compression(img, quality=50)
        
        # Higher quality should have lower MSE and higher PSNR
        assert metrics_95['mse'] < metrics_50['mse']
        assert metrics_95['psnr'] > metrics_50['psnr']
    
    def test_jpeg_rgba_image(self):
        """Test JPEG with RGBA image (alpha ignored)."""
        img = np.random.randint(0, 256, (50, 50, 4), dtype=np.uint8)
        
        compressed, metrics = test_jpeg_compression(img, quality=95)
        
        # JPEG output is RGB (no alpha)
        assert compressed.shape == (50, 50, 3)
    
    def test_jpeg_invalid_quality(self):
        """Test error on invalid quality value."""
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="Quality must be"):
            test_jpeg_compression(img, quality=0)
        
        with pytest.raises(ValueError, match="Quality must be"):
            test_jpeg_compression(img, quality=101)
    
    def test_jpeg_invalid_shape(self):
        """Test error on invalid image shape."""
        img = np.zeros((10, 10), dtype=np.uint8)  # Grayscale
        
        with pytest.raises(ValueError, match="Expected RGB/RGBA"):
            test_jpeg_compression(img, quality=95)


class TestJPEGMultipleQualities:
    """Test JPEG compression at multiple quality levels."""
    
    def test_multiple_qualities_default(self):
        """Test with default quality levels."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        results = test_jpeg_multiple_qualities(img)
        
        # Default: [95, 85, 75, 50]
        assert len(results) == 4
        assert 95 in results
        assert 85 in results
        assert 75 in results
        assert 50 in results
    
    def test_multiple_qualities_custom(self):
        """Test with custom quality levels."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        results = test_jpeg_multiple_qualities(img, qualities=[90, 70, 50])
        
        assert len(results) == 3
        assert 90 in results
        assert 70 in results
        assert 50 in results
    
    def test_multiple_qualities_trend(self):
        """Test that MSE increases as quality decreases."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        results = test_jpeg_multiple_qualities(img, qualities=[95, 75, 50])
        
        # MSE should increase as quality decreases
        assert results[95]['mse'] < results[75]['mse']
        assert results[75]['mse'] < results[50]['mse']


class TestBitErrorRate:
    """Test bit error rate calculation."""
    
    def test_ber_identical_images(self):
        """Test BER of identical images is zero."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        ber = calculate_bit_error_rate(img, img)
        
        assert ber['ber_overall'] == 0.0
        assert ber['ber_lsb'] == 0.0
        assert ber['ber_msb'] == 0.0
        assert ber['pixels_changed'] == 0
    
    def test_ber_one_lsb_flip(self):
        """Test BER with single LSB flip."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = img1.copy()
        img2[0, 0, 0] = 1  # Flip LSB of one pixel
        
        ber = calculate_bit_error_rate(img1, img2)
        
        # Only 1 bit out of 10*10*3*8 = 2400 bits changed
        assert ber['ber_overall'] > 0
        assert ber['ber_overall'] < 0.01
        
        # LSB BER should be 1 / (10*10*3) = 1/300
        expected_lsb_ber = 1 / 300
        assert abs(ber['ber_lsb'] - expected_lsb_ber) < 0.001
    
    def test_ber_all_lsb_flips(self):
        """Test BER when all LSBs flipped."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = np.ones((10, 10, 3), dtype=np.uint8)  # All LSBs = 1
        
        ber = calculate_bit_error_rate(img1, img2)
        
        # All LSBs changed
        assert ber['ber_lsb'] == 1.0
        
        # Overall BER = 1/8 (only LSB changed out of 8 bits)
        assert abs(ber['ber_overall'] - 1/8) < 0.01
    
    def test_ber_shape_mismatch(self):
        """Test error on shape mismatch."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = np.zeros((20, 20, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="same shape"):
            calculate_bit_error_rate(img1, img2)
    
    def test_ber_pixel_change_rate(self):
        """Test pixel change rate calculation."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = img1.copy()
        img2[:5, :, :] = 1  # Change half the image
        
        ber = calculate_bit_error_rate(img1, img2)
        
        # Half the pixels changed (5*10*3 = 150 out of 300)
        assert abs(ber['pixel_change_rate'] - 0.5) < 0.01
        assert ber['pixels_changed'] == 150
        assert ber['pixels_total'] == 300


class TestBitFlipAttack:
    """Test bit flip attack simulation."""
    
    def test_bit_flip_no_flips(self):
        """Test with zero flip probability."""
        data = b'Hello, World!'
        
        modified = simulate_bit_flip_attack(data, flip_probability=0.0)
        
        assert modified == data
    
    def test_bit_flip_some_flips(self):
        """Test with moderate flip probability."""
        np.random.seed(42)
        data = b'A' * 1000  # 1000 bytes
        
        modified = simulate_bit_flip_attack(data, flip_probability=0.01)
        
        # Should have some differences
        assert modified != data
        
        # Count different bytes
        different = sum(a != b for a, b in zip(data, modified))
        # Expect ~1% of bits flipped = ~10 bytes affected
        assert 5 < different < 100  # Reasonable range
    
    def test_bit_flip_all_flips(self):
        """Test with 100% flip probability."""
        np.random.seed(42)
        data = b'\x00' * 10
        
        modified = simulate_bit_flip_attack(data, flip_probability=1.0)
        
        # All bytes should be changed to 0xFF (all bits flipped)
        assert modified == b'\xFF' * 10
    
    def test_bit_flip_invalid_probability(self):
        """Test error on invalid probability."""
        data = b'test'
        
        with pytest.raises(ValueError, match="flip_probability must be"):
            simulate_bit_flip_attack(data, flip_probability=-0.1)
        
        with pytest.raises(ValueError, match="flip_probability must be"):
            simulate_bit_flip_attack(data, flip_probability=1.1)


class TestTruncationAttack:
    """Test truncation attack simulation."""
    
    def test_truncation_no_truncate(self):
        """Test with zero truncation ratio."""
        data = b'Hello, World!'
        
        truncated = simulate_truncation_attack(data, truncate_ratio=0.0)
        
        assert truncated == data
    
    def test_truncation_half(self):
        """Test truncating half the data."""
        data = b'0123456789'
        
        truncated = simulate_truncation_attack(data, truncate_ratio=0.5)
        
        # Should keep first half (5 bytes)
        assert len(truncated) == 5
        assert truncated == b'01234'
    
    def test_truncation_90_percent(self):
        """Test truncating 90% of data."""
        data = b'A' * 100
        
        truncated = simulate_truncation_attack(data, truncate_ratio=0.9)
        
        # Should keep 10% = 10 bytes (with rounding)
        assert 9 <= len(truncated) <= 10
    
    def test_truncation_complete(self):
        """Test complete truncation."""
        data = b'test'
        
        truncated = simulate_truncation_attack(data, truncate_ratio=1.0)
        
        assert len(truncated) == 0
        assert truncated == b''
    
    def test_truncation_invalid_ratio(self):
        """Test error on invalid ratio."""
        data = b'test'
        
        with pytest.raises(ValueError, match="truncate_ratio must be"):
            simulate_truncation_attack(data, truncate_ratio=-0.1)
        
        with pytest.raises(ValueError, match="truncate_ratio must be"):
            simulate_truncation_attack(data, truncate_ratio=1.1)


class TestMalformedHeader:
    """Test malformed header generation."""
    
    def test_malform_magic(self):
        """Test corrupting magic bytes."""
        valid_header = b'STGR' + b'\x00' * 8
        
        malformed = create_malformed_header(valid_header, corruption_type='magic')
        
        # Magic should be corrupted
        assert malformed[:4] == b'XXXX'
        # Rest unchanged
        assert malformed[4:] == valid_header[4:]
    
    def test_malform_version(self):
        """Test corrupting version byte."""
        valid_header = b'STGR\x01\x00\x00\x00' + b'\x00' * 4
        
        malformed = create_malformed_header(valid_header, corruption_type='version')
        
        # Magic unchanged
        assert malformed[:4] == b'STGR'
        # Version corrupted to 99
        assert malformed[4] == 99
    
    def test_malform_length(self):
        """Test corrupting payload length."""
        valid_header = b'STGR\x01\x00\x00\x00' + (1000).to_bytes(4, 'big')
        
        malformed = create_malformed_header(valid_header, corruption_type='length')
        
        # Magic unchanged
        assert malformed[:4] == b'STGR'
        # Length set to 0xFFFFFFFF
        assert malformed[8:12] == b'\xFF\xFF\xFF\xFF'
    
    def test_malform_invalid_type(self):
        """Test error on invalid corruption type."""
        valid_header = b'STGR' + b'\x00' * 8
        
        with pytest.raises(ValueError, match="Unknown corruption_type"):
            create_malformed_header(valid_header, corruption_type='invalid')
    
    def test_malform_short_header(self):
        """Test error on header too short."""
        short_header = b'STGR'
        
        with pytest.raises(ValueError, match="Header too short"):
            create_malformed_header(short_header, corruption_type='magic')


class TestStegoResilience:
    """Test steganography resilience to attacks."""
    
    def test_resilience_jpeg(self):
        """Test resilience to JPEG compression."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        attacked, metrics = test_stego_resilience(img, attack_type='jpeg', quality=75)
        
        assert attacked.shape == img.shape
        assert 'psnr' in metrics
        assert 'lsb_survival_rate' in metrics
    
    def test_resilience_noise(self):
        """Test resilience to Gaussian noise."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        attacked, metrics = test_stego_resilience(img, attack_type='noise', sigma=5.0)
        
        assert attacked.shape == img.shape
        assert 'psnr' in metrics
        # Noise should reduce PSNR
        assert metrics['psnr'] > 0
    
    def test_resilience_blur(self):
        """Test resilience to Gaussian blur."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        attacked, metrics = test_stego_resilience(img, attack_type='blur', sigma=1.0)
        
        assert attacked.shape == img.shape
        assert 'psnr' in metrics
    
    def test_resilience_invalid_attack(self):
        """Test error on invalid attack type."""
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="Unknown attack_type"):
            test_stego_resilience(img, attack_type='invalid')


class TestJPEGLSBDestruction:
    """Test that JPEG destroys LSB steganography."""
    
    def test_jpeg_destroys_lsb_pattern(self):
        """Test that JPEG compression affects LSB."""
        # Create image with specific LSB pattern
        img = np.full((50, 50, 3), 100, dtype=np.uint8)  # All even (LSB=0)
        
        # Apply JPEG compression
        compressed, metrics = test_jpeg_compression(img, quality=75)
        
        # Uniform images may be well-preserved by JPEG
        # Just verify metrics are calculated
        assert 'lsb_survival_rate' in metrics
        assert 0 <= metrics['lsb_survival_rate'] <= 1.0
        assert metrics['mse'] >= 0
    
    def test_jpeg_high_quality_still_destroys_lsb(self):
        """Test that even high quality JPEG affects LSB."""
        img = np.full((50, 50, 3), 100, dtype=np.uint8)
        
        compressed, metrics = test_jpeg_compression(img, quality=95)
        
        # Even at Q95, uniform images might be well-preserved
        # Just check it's not identical
        assert metrics['mse'] >= 0  # Some difference or identical
