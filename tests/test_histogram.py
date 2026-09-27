"""
Unit tests for stegora.analysis.histogram module

Tests histogram calculation, comparison, and LSB pair analysis.

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

import pytest
import numpy as np
from PIL import Image

from stegora.analysis.histogram import (
    calculate_histogram,
    calculate_histogram_from_pil,
    compare_histograms,
    analyze_lsb_histogram_pairs,
    calculate_histogram_difference_image
)


class TestCalculateHistogram:
    """Test histogram calculation from NumPy arrays."""
    
    def test_single_color_image(self):
        """Test histogram of solid color image."""
        # 10x10 red image (255, 0, 0)
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        img[:, :, 0] = 255  # Red channel = 255
        
        hist = calculate_histogram(img)
        
        assert 'R' in hist
        assert 'G' in hist
        assert 'B' in hist
        
        # Red channel: all 100 pixels have value 255
        assert hist['R'][255] == 100
        assert np.sum(hist['R']) == 100
        
        # Green channel: all pixels have value 0
        assert hist['G'][0] == 100
        
        # Blue channel: all pixels have value 0
        assert hist['B'][0] == 100
    
    def test_gradient_image(self):
        """Test histogram of gradient image."""
        # Create gradient: 0-255 in red channel
        img = np.zeros((256, 1, 3), dtype=np.uint8)
        img[:, 0, 0] = np.arange(256, dtype=np.uint8)
        
        hist = calculate_histogram(img)
        
        # Each value 0-255 appears exactly once
        assert np.all(hist['R'] == 1)
        assert np.sum(hist['R']) == 256
    
    def test_rgba_image(self):
        """Test histogram of RGBA image (alpha ignored)."""
        img = np.zeros((10, 10, 4), dtype=np.uint8)
        img[:, :, 0] = 100  # Red
        img[:, :, 3] = 255  # Alpha (should be ignored)
        
        hist = calculate_histogram(img)
        
        # Should only have R, G, B keys
        assert set(hist.keys()) == {'R', 'G', 'B'}
        assert hist['R'][100] == 100
    
    def test_invalid_dimensions(self):
        """Test error on invalid image dimensions."""
        # 2D image (grayscale)
        img = np.zeros((10, 10), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="Expected 3D image"):
            calculate_histogram(img)
    
    def test_invalid_channels(self):
        """Test error on invalid number of channels."""
        # 2-channel image
        img = np.zeros((10, 10, 2), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="Expected RGB or RGBA"):
            calculate_histogram(img)
    
    def test_invalid_dtype(self):
        """Test error on non-uint8 dtype."""
        img = np.zeros((10, 10, 3), dtype=np.float32)
        
        with pytest.raises(ValueError, match="Expected uint8"):
            calculate_histogram(img)
    
    def test_histogram_length(self):
        """Test that histogram has 256 bins."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        hist = calculate_histogram(img)
        
        assert len(hist['R']) == 256
        assert len(hist['G']) == 256
        assert len(hist['B']) == 256
    
    def test_histogram_sum(self):
        """Test that histogram sum equals total pixels."""
        width, height = 73, 42
        img = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        hist = calculate_histogram(img)
        
        total_pixels = width * height
        assert np.sum(hist['R']) == total_pixels
        assert np.sum(hist['G']) == total_pixels
        assert np.sum(hist['B']) == total_pixels


class TestCalculateHistogramFromPIL:
    """Test histogram calculation from PIL Images."""
    
    def test_rgb_image(self):
        """Test histogram from RGB PIL image."""
        img = Image.new('RGB', (10, 10), color=(100, 150, 200))
        hist = calculate_histogram_from_pil(img)
        
        assert hist['R'][100] == 100
        assert hist['G'][150] == 100
        assert hist['B'][200] == 100
    
    def test_rgba_image(self):
        """Test histogram from RGBA PIL image."""
        img = Image.new('RGBA', (10, 10), color=(50, 100, 150, 255))
        hist = calculate_histogram_from_pil(img)
        
        assert hist['R'][50] == 100
        assert hist['G'][100] == 100
        assert hist['B'][150] == 100
    
    def test_invalid_mode(self):
        """Test error on non-RGB/RGBA mode."""
        img = Image.new('L', (10, 10), color=128)  # Grayscale
        
        with pytest.raises(ValueError, match="Expected RGB or RGBA"):
            calculate_histogram_from_pil(img)


class TestCompareHistograms:
    """Test histogram comparison metrics."""
    
    def test_identical_histograms(self):
        """Test comparing identical histograms."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        hist1 = calculate_histogram(img)
        hist2 = calculate_histogram(img)
        
        metrics = compare_histograms(hist1, hist2)
        
        # Identical histograms should have zero difference
        assert metrics['overall_mad'] == 0.0
        assert metrics['overall_max'] == 0.0
        assert metrics['overall_chi2'] == 0.0
        
        for channel in ['R', 'G', 'B']:
            assert metrics[f'{channel}_mad'] == 0.0
            assert metrics[f'{channel}_max'] == 0.0
            assert metrics[f'{channel}_chi2'] == 0.0
    
    def test_different_histograms(self):
        """Test comparing different histograms."""
        # Cover: all red=100
        cover = np.zeros((10, 10, 3), dtype=np.uint8)
        cover[:, :, 0] = 100
        
        # Stego: half red=100, half red=101 (LSB flip)
        stego = cover.copy()
        stego[5:, :, 0] = 101
        
        hist_cover = calculate_histogram(cover)
        hist_stego = calculate_histogram(stego)
        
        metrics = compare_histograms(hist_cover, hist_stego)
        
        # Should detect differences
        assert metrics['R_mad'] > 0
        assert metrics['R_max'] > 0
        assert metrics['overall_mad'] > 0
    
    def test_metric_ranges(self):
        """Test that metrics are in expected ranges."""
        img1 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        img2 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        hist1 = calculate_histogram(img1)
        hist2 = calculate_histogram(img2)
        
        metrics = compare_histograms(hist1, hist2)
        
        # All metrics should be non-negative
        for key, value in metrics.items():
            assert value >= 0, f"{key} should be non-negative"
        
        # MAD should be reasonable (< 1000 for 50x50 image)
        assert metrics['overall_mad'] < 1000


class TestAnalyzeLSBHistogramPairs:
    """Test LSB even/odd pair analysis."""
    
    def test_perfect_balance(self):
        """Test analysis of perfectly balanced LSB pairs."""
        # Create histogram with equal even/odd pairs
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        # Half pixels = 100 (even), half = 101 (odd)
        img[:50, :, 0] = 100
        img[50:, :, 0] = 101
        
        hist = calculate_histogram(img)
        analysis = analyze_lsb_histogram_pairs(hist)
        
        # Mean ratio should be close to 1.0
        assert 'R' in analysis
        assert 0.95 <= analysis['R']['mean_ratio'] <= 1.05
        
        # Should have few suspicious pairs
        assert analysis['R']['suspicious_pairs'] < 5
    
    def test_imbalanced_pairs(self):
        """Test analysis of imbalanced LSB pairs."""
        # Create histogram with imbalanced pairs
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        # Many even values, few odd values
        img[:90, :, 0] = 100  # Even
        img[90:, :, 0] = 101  # Odd
        
        hist = calculate_histogram(img)
        analysis = analyze_lsb_histogram_pairs(hist)
        
        # Ratio should be far from 1.0
        assert analysis['R']['mean_ratio'] > 2.0 or analysis['R']['mean_ratio'] < 0.5
        
        # Should have suspicious pairs
        assert analysis['R']['suspicious_pairs'] > 0
    
    def test_all_channels(self):
        """Test that analysis covers all RGB channels."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        hist = calculate_histogram(img)
        analysis = analyze_lsb_histogram_pairs(hist)
        
        assert 'R' in analysis
        assert 'G' in analysis
        assert 'B' in analysis
        
        for channel in ['R', 'G', 'B']:
            assert 'mean_ratio' in analysis[channel]
            assert 'max_ratio' in analysis[channel]
            assert 'suspicious_pairs' in analysis[channel]


class TestCalculateHistogramDifferenceImage:
    """Test histogram difference image generation."""
    
    def test_identical_images(self):
        """Test difference of identical images is zero."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        diff = calculate_histogram_difference_image(img, img)
        
        # All differences should be zero
        assert np.all(diff == 0)
    
    def test_one_pixel_difference(self):
        """Test difference with one pixel changed."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = img1.copy()
        img2[5, 5, 0] = 1  # Change one pixel by 1
        
        diff = calculate_histogram_difference_image(img1, img2)
        
        # Most pixels should be zero
        assert np.sum(diff == 0) > 90 * 3  # At least 90 out of 100 pixels
        
        # Changed pixel should be non-zero (scaled)
        assert diff[5, 5, 0] > 0
    
    def test_lsb_change_visibility(self):
        """Test that LSB changes are amplified."""
        img1 = np.full((10, 10, 3), 100, dtype=np.uint8)
        img2 = np.full((10, 10, 3), 101, dtype=np.uint8)  # All LSB flipped
        
        diff = calculate_histogram_difference_image(img1, img2)
        
        # LSB change (±1) should be amplified to 128
        assert np.all(diff == 128)
    
    def test_shape_mismatch(self):
        """Test error on mismatched image shapes."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = np.zeros((20, 20, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="same shape"):
            calculate_histogram_difference_image(img1, img2)
    
    def test_output_range(self):
        """Test that output is in valid uint8 range."""
        img1 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        img2 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        diff = calculate_histogram_difference_image(img1, img2)
        
        assert diff.dtype == np.uint8
        assert np.all(diff >= 0)
        assert np.all(diff <= 255)
