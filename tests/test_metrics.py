"""Unit tests for MSE and PSNR metrics.

Tests for T15 - MSE & PSNR Metrics
Author: Hana (247006111170)
"""

import pytest
import numpy as np
from PIL import Image
from stegora.image import (
    calculate_mse,
    calculate_psnr,
    calculate_metrics,
    format_psnr,
    format_mse,
    is_acceptable_quality,
    calculate_per_channel_mse,
    MetricsError,
    MAX_PIXEL_VALUE,
    PSNR_THRESHOLD_CONTEXT,
)


class TestMSECalculation:
    """Test suite for MSE calculation."""
    
    def test_mse_identical_images(self):
        """Test that identical images have MSE = 0."""
        # Create identical images
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        mse = calculate_mse(img, img)
        
        assert mse == 0.0
    
    def test_mse_different_images(self):
        """Test that different images have MSE > 0."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8)
        
        mse = calculate_mse(img1, img2)
        
        assert mse > 0.0
        # MSE should be 1.0 (difference of 1 pixel value squared)
        assert mse == 1.0
    
    def test_mse_maximum_difference(self):
        """Test MSE with maximum pixel difference."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)  # All 0
        img2 = np.full((100, 100, 3), 255, dtype=np.uint8)  # All 255
        
        mse = calculate_mse(img1, img2)
        
        # MSE should be 255^2 = 65025
        expected_mse = 255 ** 2
        assert mse == expected_mse
    
    def test_mse_small_difference(self):
        """Test MSE with small pixel difference."""
        img1 = np.full((100, 100, 3), 100, dtype=np.uint8)
        img2 = np.full((100, 100, 3), 101, dtype=np.uint8)
        
        mse = calculate_mse(img1, img2)
        
        # Difference is 1, so MSE = 1^2 = 1.0
        assert mse == 1.0
    
    def test_mse_with_pil_images(self):
        """Test MSE with PIL Image objects."""
        # Create PIL images
        img1 = Image.new('RGB', (50, 50), color=(0, 0, 0))
        img2 = Image.new('RGB', (50, 50), color=(10, 10, 10))
        
        mse = calculate_mse(img1, img2)
        
        # Difference is 10 per channel, MSE = 10^2 = 100
        assert mse == 100.0
    
    def test_mse_rgba_images(self):
        """Test MSE with RGBA images (with alpha channel)."""
        img1 = np.zeros((50, 50, 4), dtype=np.uint8)
        img2 = np.ones((50, 50, 4), dtype=np.uint8)
        
        mse = calculate_mse(img1, img2)
        
        # Difference is 1, MSE = 1.0
        assert mse == 1.0
    
    def test_mse_dimension_mismatch(self):
        """Test that dimension mismatch raises error."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((50, 50, 3), dtype=np.uint8)
        
        with pytest.raises(MetricsError, match="dimensions must match"):
            calculate_mse(img1, img2)
    
    def test_mse_invalid_input_type(self):
        """Test that invalid input types raise error."""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="must be PIL Image or numpy array"):
            calculate_mse(img, "invalid")
        
        with pytest.raises(ValueError, match="must be PIL Image or numpy array"):
            calculate_mse("invalid", img)
    
    def test_mse_fractional_result(self):
        """Test MSE with mixed pixel values."""
        img1 = np.array([[[0, 0, 0], [255, 255, 255]]], dtype=np.uint8)
        img2 = np.array([[[1, 1, 1], [254, 254, 254]]], dtype=np.uint8)
        
        mse = calculate_mse(img1, img2)
        
        # First pixel: diff=1, squared=1
        # Second pixel: diff=1, squared=1
        # Average: (1+1) / 2 pixels / 3 channels = 1.0
        assert mse == 1.0


class TestPSNRCalculation:
    """Test suite for PSNR calculation."""
    
    def test_psnr_identical_images(self):
        """Test that identical images have PSNR = infinity."""
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        psnr = calculate_psnr(img, img)
        
        assert psnr == float('inf')
    
    def test_psnr_with_known_mse(self):
        """Test PSNR calculation with known MSE value."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8)
        
        # MSE = 1.0
        psnr = calculate_psnr(img1, img2)
        
        # PSNR = 10 * log10(255^2 / 1.0) = 10 * log10(65025) ≈ 48.13 dB
        expected_psnr = 10 * np.log10(255 ** 2 / 1.0)
        assert abs(psnr - expected_psnr) < 0.01
    
    def test_psnr_with_precalculated_mse(self):
        """Test PSNR with pre-calculated MSE."""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        mse = 100.0
        
        psnr = calculate_psnr(img, img, mse=mse)
        
        # PSNR = 10 * log10(255^2 / 100)
        expected_psnr = 10 * np.log10(255 ** 2 / 100.0)
        assert abs(psnr - expected_psnr) < 0.01
    
    def test_psnr_zero_mse(self):
        """Test PSNR with MSE = 0 returns infinity."""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        psnr = calculate_psnr(img, img, mse=0.0)
        
        assert psnr == float('inf')
    
    def test_psnr_high_quality(self):
        """Test PSNR for high quality (small MSE)."""
        img1 = np.full((100, 100, 3), 128, dtype=np.uint8)
        img2 = np.full((100, 100, 3), 129, dtype=np.uint8)
        
        psnr = calculate_psnr(img1, img2)
        
        # MSE = 1, PSNR should be ~48 dB (high quality)
        assert psnr > 40.0
    
    def test_psnr_low_quality(self):
        """Test PSNR for low quality (large MSE)."""
        img1 = np.full((100, 100, 3), 0, dtype=np.uint8)
        img2 = np.full((100, 100, 3), 100, dtype=np.uint8)
        
        psnr = calculate_psnr(img1, img2)
        
        # MSE = 10000, PSNR should be ~18 dB (low quality)
        assert psnr < 20.0
    
    def test_psnr_threshold_context(self):
        """Test PSNR around 30 dB threshold."""
        # Create image with MSE that gives ~30 dB PSNR
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Calculate MSE needed for 30 dB PSNR
        # 30 = 10 * log10(255^2 / MSE)
        # MSE = 255^2 / 10^3 ≈ 65.025
        target_mse = 65.025
        
        psnr = calculate_psnr(img1, img1, mse=target_mse)
        
        # PSNR should be approximately 30 dB
        assert abs(psnr - 30.0) < 0.01


class TestMetricsCalculation:
    """Test suite for combined metrics calculation."""
    
    def test_calculate_metrics_identical(self):
        """Test metrics for identical images."""
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        metrics = calculate_metrics(img, img)
        
        assert metrics['mse'] == 0.0
        assert metrics['psnr'] == float('inf')
        assert metrics['psnr_db'] == float('inf')
        assert 'Identical' in metrics['quality_assessment']
    
    def test_calculate_metrics_excellent(self):
        """Test metrics for excellent quality (PSNR >= 50 dB)."""
        # Create images with very small difference for PSNR > 50 dB
        img1 = np.full((100, 100, 3), 128, dtype=np.uint8)
        img2 = img1.copy()
        # Change only a few pixels by 1 to get PSNR > 50
        img2[0, 0, 0] = 129
        img2[0, 1, 0] = 129
        
        metrics = calculate_metrics(img1, img2)
        
        assert metrics['mse'] < 1.0  # Very small MSE
        assert metrics['psnr'] >= 50.0
        assert 'Excellent' in metrics['quality_assessment']
    
    def test_calculate_metrics_acceptable(self):
        """Test metrics for acceptable quality (30-40 dB)."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        # Create image with MSE for ~35 dB PSNR
        diff = int(np.sqrt(255**2 / 10**3.5))  # ~32
        img2 = np.full((100, 100, 3), diff, dtype=np.uint8)
        
        metrics = calculate_metrics(img1, img2)
        
        assert 30.0 <= metrics['psnr'] < 40.0
        assert 'Acceptable' in metrics['quality_assessment'] or 'good' in metrics['quality_assessment'].lower()
    
    def test_calculate_metrics_poor(self):
        """Test metrics for poor quality (PSNR < 20 dB)."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.full((100, 100, 3), 200, dtype=np.uint8)
        
        metrics = calculate_metrics(img1, img2)
        
        assert metrics['psnr'] < 20.0
        assert 'Poor' in metrics['quality_assessment']
    
    def test_calculate_metrics_keys(self):
        """Test that all expected keys are present."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8)
        
        metrics = calculate_metrics(img1, img2)
        
        assert 'mse' in metrics
        assert 'psnr' in metrics
        assert 'psnr_db' in metrics
        assert 'quality_assessment' in metrics


class TestFormattingFunctions:
    """Test suite for formatting functions."""
    
    def test_format_psnr_finite(self):
        """Test PSNR formatting for finite values."""
        formatted = format_psnr(42.5678)
        assert formatted == "42.57 dB"
    
    def test_format_psnr_infinite(self):
        """Test PSNR formatting for infinite value."""
        formatted = format_psnr(float('inf'))
        assert "∞" in formatted
        assert "identical" in formatted.lower()
    
    def test_format_mse_nonzero(self):
        """Test MSE formatting for non-zero values."""
        formatted = format_mse(1.2345)
        assert formatted == "1.2345"
    
    def test_format_mse_zero(self):
        """Test MSE formatting for zero."""
        formatted = format_mse(0.0)
        assert "0.0000" in formatted
        assert "identical" in formatted.lower()


class TestQualityAssessment:
    """Test suite for quality assessment functions."""
    
    def test_is_acceptable_quality_above_threshold(self):
        """Test quality check above threshold."""
        assert is_acceptable_quality(40.0) is True
        assert is_acceptable_quality(30.0) is True
        assert is_acceptable_quality(30.1) is True
    
    def test_is_acceptable_quality_below_threshold(self):
        """Test quality check below threshold."""
        assert is_acceptable_quality(29.9) is False
        assert is_acceptable_quality(20.0) is False
    
    def test_is_acceptable_quality_infinite(self):
        """Test quality check for infinite PSNR."""
        assert is_acceptable_quality(float('inf')) is True
    
    def test_is_acceptable_quality_custom_threshold(self):
        """Test quality check with custom threshold."""
        assert is_acceptable_quality(35.0, threshold=40.0) is False
        assert is_acceptable_quality(45.0, threshold=40.0) is True


class TestPerChannelMSE:
    """Test suite for per-channel MSE calculation."""
    
    def test_per_channel_mse_rgb(self):
        """Test per-channel MSE for RGB image."""
        # Create image with different changes in each channel
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.array([[[1, 2, 3]]], dtype=np.uint8)
        img2 = np.tile(img2, (100, 100, 1))
        
        metrics = calculate_per_channel_mse(img1, img2)
        
        assert 'r' in metrics
        assert 'g' in metrics
        assert 'b' in metrics
        assert 'overall' in metrics
        
        # Red channel: diff = 1, MSE = 1
        assert metrics['r'] == 1.0
        # Green channel: diff = 2, MSE = 4
        assert metrics['g'] == 4.0
        # Blue channel: diff = 3, MSE = 9
        assert metrics['b'] == 9.0
        # Overall: (1 + 4 + 9) / 3 ≈ 4.67
        assert abs(metrics['overall'] - 4.666667) < 0.01
    
    def test_per_channel_mse_rgba(self):
        """Test per-channel MSE for RGBA image."""
        img1 = np.zeros((100, 100, 4), dtype=np.uint8)
        img2 = np.ones((100, 100, 4), dtype=np.uint8)
        
        metrics = calculate_per_channel_mse(img1, img2)
        
        assert 'r' in metrics
        assert 'g' in metrics
        assert 'b' in metrics
        assert 'a' in metrics
        assert 'overall' in metrics
        
        # All channels have diff = 1, MSE = 1
        assert metrics['r'] == 1.0
        assert metrics['g'] == 1.0
        assert metrics['b'] == 1.0
        assert metrics['a'] == 1.0
        assert metrics['overall'] == 1.0
    
    def test_per_channel_mse_no_channels(self):
        """Test that grayscale images raise error."""
        img1 = np.zeros((100, 100), dtype=np.uint8)
        img2 = np.zeros((100, 100), dtype=np.uint8)
        
        with pytest.raises(MetricsError, match="must have color channels"):
            calculate_per_channel_mse(img1, img2)


class TestConstants:
    """Test suite for module constants."""
    
    def test_max_pixel_value(self):
        """Test that MAX_PIXEL_VALUE is correct."""
        assert MAX_PIXEL_VALUE == 255
    
    def test_psnr_threshold_context(self):
        """Test that PSNR threshold is documented value."""
        assert PSNR_THRESHOLD_CONTEXT == 30.0


class TestRealWorldScenarios:
    """Test suite for realistic steganography scenarios."""
    
    def test_1bit_lsb_typical_psnr(self):
        """Test typical PSNR for 1-bit LSB embedding."""
        # Simulate 1-bit LSB change in half the pixels
        img1 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img2 = img1.copy()
        
        # Flip LSB in 50% of pixels
        mask = np.random.rand(100, 100, 3) < 0.5
        img2[mask] ^= 1  # XOR with 1 flips LSB
        
        metrics = calculate_metrics(img1, img2)
        
        # 1-bit LSB should give very high PSNR (typically > 50 dB)
        assert metrics['psnr'] > 40.0
    
    def test_small_payload_high_psnr(self):
        """Test that small payload gives high PSNR."""
        # Create large image with minimal changes
        img1 = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
        img2 = img1.copy()
        
        # Change only 100 pixels by 1 bit
        for i in range(100):
            x, y = np.random.randint(0, 500), np.random.randint(0, 500)
            c = np.random.randint(0, 3)
            img2[x, y, c] ^= 1
        
        psnr = calculate_psnr(img1, img2)
        
        # Should have very high PSNR
        assert psnr > 45.0
    
    def test_full_capacity_acceptable_psnr(self):
        """Test PSNR at full capacity (all pixels modified)."""
        img1 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img2 = img1.copy()
        
        # Flip LSB in all pixels
        img2 ^= 1
        
        psnr = calculate_psnr(img1, img2)
        
        # Even with all pixels changed, 1-bit LSB should give PSNR > 30 dB
        assert psnr > 30.0
