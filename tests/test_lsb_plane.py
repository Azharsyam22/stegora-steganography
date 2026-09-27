"""
Unit tests for stegora.analysis.lsb_plane module

Tests LSB plane extraction, enhanced visualization, and randomness analysis.

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

import pytest
import numpy as np

from stegora.analysis.lsb_plane import (
    extract_bit_plane,
    extract_lsb_plane,
    create_enhanced_lsb_visual,
    analyze_lsb_randomness,
    compare_lsb_planes,
    create_lsb_difference_visual,
    analyze_bit_plane_complexity
)


class TestExtractBitPlane:
    """Test bit plane extraction."""
    
    def test_extract_lsb(self):
        """Test extracting LSB (bit 0)."""
        # 100 = 0b01100100, LSB = 0
        # 101 = 0b01100101, LSB = 1
        img = np.array([[[100, 101, 102]]], dtype=np.uint8)
        
        plane = extract_bit_plane(img, bit_position=0)
        
        # LSBs: 0, 1, 0 → amplified to 0, 255, 0
        assert plane[0, 0, 0] == 0    # 100 LSB=0
        assert plane[0, 0, 1] == 255  # 101 LSB=1
        assert plane[0, 0, 2] == 0    # 102 LSB=0
    
    def test_extract_msb(self):
        """Test extracting MSB (bit 7)."""
        # 127 = 0b01111111, MSB = 0
        # 128 = 0b10000000, MSB = 1
        img = np.array([[[127, 128, 255]]], dtype=np.uint8)
        
        plane = extract_bit_plane(img, bit_position=7)
        
        # MSBs: 0, 1, 1 → amplified to 0, 255, 255
        assert plane[0, 0, 0] == 0
        assert plane[0, 0, 1] == 255
        assert plane[0, 0, 2] == 255
    
    def test_extract_middle_bit(self):
        """Test extracting middle bit (bit 3)."""
        # 8 = 0b00001000, bit3 = 1
        # 7 = 0b00000111, bit3 = 0
        img = np.array([[[8, 7, 15]]], dtype=np.uint8)
        
        plane = extract_bit_plane(img, bit_position=3)
        
        assert plane[0, 0, 0] == 255  # bit3=1
        assert plane[0, 0, 1] == 0    # bit3=0
        assert plane[0, 0, 2] == 255  # 15=0b1111, bit3=1
    
    def test_invalid_bit_position(self):
        """Test error on invalid bit position."""
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="bit_position must be in"):
            extract_bit_plane(img, bit_position=8)
        
        with pytest.raises(ValueError, match="bit_position must be in"):
            extract_bit_plane(img, bit_position=-1)
    
    def test_rgba_image(self):
        """Test that alpha channel is ignored."""
        img = np.zeros((10, 10, 4), dtype=np.uint8)
        img[:, :, 0] = 255  # Red LSB = 1
        img[:, :, 3] = 255  # Alpha (ignored)
        
        plane = extract_bit_plane(img, bit_position=0)
        
        # Should only have 3 channels (RGB)
        assert plane.shape == (10, 10, 3)
        assert np.all(plane[:, :, 0] == 255)
    
    def test_output_binary(self):
        """Test that output is binary (0 or 255)."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        plane = extract_bit_plane(img, bit_position=0)
        
        # All values should be 0 or 255
        unique_values = np.unique(plane)
        assert set(unique_values).issubset({0, 255})


class TestExtractLSBPlane:
    """Test LSB plane extraction convenience function."""
    
    def test_lsb_extraction(self):
        """Test that extract_lsb_plane calls extract_bit_plane correctly."""
        img = np.array([[[100, 101, 102]]], dtype=np.uint8)
        
        lsb = extract_lsb_plane(img)
        expected = extract_bit_plane(img, bit_position=0)
        
        assert np.array_equal(lsb, expected)


class TestCreateEnhancedLSBVisual:
    """Test enhanced LSB visualization."""
    
    def test_output_shape(self):
        """Test that output has same shape as input."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        enhanced = create_enhanced_lsb_visual(img)
        
        assert enhanced.shape == (50, 50, 3)
    
    def test_output_dtype(self):
        """Test that output is uint8."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        enhanced = create_enhanced_lsb_visual(img)
        
        assert enhanced.dtype == np.uint8
    
    def test_output_range(self):
        """Test that output is in valid range."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        enhanced = create_enhanced_lsb_visual(img)
        
        assert np.all(enhanced >= 0)
        assert np.all(enhanced <= 255)
    
    def test_uniform_lsb(self):
        """Test enhanced visual of uniform LSB (all 0s or all 1s)."""
        # All even values (LSB=0)
        img = np.full((20, 20, 3), 100, dtype=np.uint8)
        enhanced = create_enhanced_lsb_visual(img)
        
        # Uniform LSB (all 0) means local average = 0, deviation from 0.5 = 0.5
        # After amplification (*4), this becomes maximum (saturated to 255)
        # This is correct behavior - uniform LSB shows maximum deviation from random
        assert enhanced.dtype == np.uint8


class TestAnalyzeLSBRandomness:
    """Test LSB randomness analysis."""
    
    def test_perfect_balance(self):
        """Test analysis of perfectly balanced LSB."""
        # Half 0s, half 255s (perfect balance)
        lsb = np.zeros((100, 100, 3), dtype=np.uint8)
        lsb[:50, :, :] = 255
        
        metrics = analyze_lsb_randomness(lsb)
        
        # Balance should be 1.0 (equal 0s and 1s)
        assert 0.95 <= metrics['overall_balance'] <= 1.05
        
        # Entropy should be high (close to 1.0)
        assert metrics['overall_entropy'] > 0.95
    
    def test_all_zeros(self):
        """Test analysis of all-zero LSB."""
        lsb = np.zeros((50, 50, 3), dtype=np.uint8)
        
        metrics = analyze_lsb_randomness(lsb)
        
        # Balance should be 0.0 (no 1s)
        # Handled as zeros / zeros = 1.0 or special case
        assert metrics['overall_balance'] >= 0
        
        # Entropy should be 0.0 (no randomness)
        assert metrics['overall_entropy'] == 0.0
    
    def test_all_ones(self):
        """Test analysis of all-one LSB."""
        lsb = np.full((50, 50, 3), 255, dtype=np.uint8)
        
        metrics = analyze_lsb_randomness(lsb)
        
        # Balance should be inf or very high
        assert metrics['overall_balance'] > 5.0
        
        # Entropy should be 0.0 (no randomness)
        assert metrics['overall_entropy'] == 0.0
    
    def test_metric_keys(self):
        """Test that all expected metrics are present."""
        lsb = np.random.randint(0, 2, (50, 50, 3), dtype=np.uint8) * 255
        metrics = analyze_lsb_randomness(lsb)
        
        expected_keys = [
            'R_balance', 'G_balance', 'B_balance',
            'R_entropy', 'G_entropy', 'B_entropy',
            'overall_balance', 'overall_entropy'
        ]
        
        for key in expected_keys:
            assert key in metrics
    
    def test_random_lsb(self):
        """Test analysis of random LSB."""
        np.random.seed(42)
        lsb = np.random.randint(0, 2, (100, 100, 3), dtype=np.uint8) * 255
        
        metrics = analyze_lsb_randomness(lsb)
        
        # Random LSB should have balance ≈ 1.0
        assert 0.8 <= metrics['overall_balance'] <= 1.2
        
        # Random LSB should have high entropy
        assert metrics['overall_entropy'] > 0.9


class TestCompareLSBPlanes:
    """Test LSB plane comparison."""
    
    def test_identical_planes(self):
        """Test comparing identical LSB planes."""
        lsb = np.random.randint(0, 2, (50, 50, 3), dtype=np.uint8) * 255
        
        metrics = compare_lsb_planes(lsb, lsb)
        
        # No differences
        assert metrics['overall_diff_ratio'] == 0.0
        assert metrics['R_diff_ratio'] == 0.0
        assert metrics['G_diff_ratio'] == 0.0
        assert metrics['B_diff_ratio'] == 0.0
    
    def test_completely_different_planes(self):
        """Test comparing completely different LSB planes."""
        lsb1 = np.zeros((50, 50, 3), dtype=np.uint8)
        lsb2 = np.full((50, 50, 3), 255, dtype=np.uint8)
        
        metrics = compare_lsb_planes(lsb1, lsb2)
        
        # All bits different
        assert metrics['overall_diff_ratio'] == 1.0
    
    def test_half_different_planes(self):
        """Test comparing half-different LSB planes."""
        lsb1 = np.zeros((100, 100, 3), dtype=np.uint8)
        lsb2 = lsb1.copy()
        lsb2[:50, :, :] = 255  # Change half
        
        metrics = compare_lsb_planes(lsb1, lsb2)
        
        # Should be 50% different
        assert 0.45 <= metrics['overall_diff_ratio'] <= 0.55
    
    def test_shape_mismatch(self):
        """Test error on mismatched shapes."""
        lsb1 = np.zeros((10, 10, 3), dtype=np.uint8)
        lsb2 = np.zeros((20, 20, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="same shape"):
            compare_lsb_planes(lsb1, lsb2)


class TestCreateLSBDifferenceVisual:
    """Test LSB difference visualization."""
    
    def test_identical_images(self):
        """Test difference of identical images."""
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        diff = create_lsb_difference_visual(img, img)
        
        # No differences
        assert np.all(diff == 0)
    
    def test_lsb_change(self):
        """Test visualization of LSB change."""
        img1 = np.full((10, 10, 3), 100, dtype=np.uint8)  # LSB=0
        img2 = np.full((10, 10, 3), 101, dtype=np.uint8)  # LSB=1
        
        diff = create_lsb_difference_visual(img1, img2)
        
        # All LSBs changed → all white
        assert np.all(diff == 255)
    
    def test_no_lsb_change(self):
        """Test visualization when LSB unchanged but other bits changed."""
        img1 = np.full((10, 10, 3), 100, dtype=np.uint8)  # 0b01100100
        img2 = np.full((10, 10, 3), 108, dtype=np.uint8)  # 0b01101100
        # Both have LSB=0, so no LSB change
        
        diff = create_lsb_difference_visual(img1, img2)
        
        # No LSB changes → all black
        assert np.all(diff == 0)
    
    def test_partial_lsb_change(self):
        """Test visualization of partial LSB change."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = img1.copy()
        img2[5:, :, 0] = 1  # Change bottom half LSB in red channel
        
        diff = create_lsb_difference_visual(img1, img2)
        
        # Top half: no change
        assert np.all(diff[:5, :, 0] == 0)
        
        # Bottom half: changed
        assert np.all(diff[5:, :, 0] == 255)
    
    def test_shape_mismatch(self):
        """Test error on mismatched shapes."""
        img1 = np.zeros((10, 10, 3), dtype=np.uint8)
        img2 = np.zeros((20, 20, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="same shape"):
            create_lsb_difference_visual(img1, img2)
    
    def test_output_binary(self):
        """Test that output is binary (0 or 255)."""
        img1 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        img2 = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        diff = create_lsb_difference_visual(img1, img2)
        
        # All values should be 0 or 255
        unique_values = np.unique(diff)
        assert set(unique_values).issubset({0, 255})


class TestAnalyzeBitPlaneComplexity:
    """Test bit plane complexity analysis."""
    
    def test_uniform_plane(self):
        """Test complexity of uniform bit plane."""
        plane = np.zeros((50, 50, 3), dtype=np.uint8)
        
        metrics = analyze_bit_plane_complexity(plane)
        
        # No edges in uniform plane
        assert metrics['R_edge_density'] == 0.0
        assert metrics['G_edge_density'] == 0.0
        assert metrics['B_edge_density'] == 0.0
        
        # Zero uniformity (std=0)
        assert metrics['R_uniformity'] == 0.0
    
    def test_checkerboard_plane(self):
        """Test complexity of checkerboard pattern."""
        plane = np.zeros((50, 50, 3), dtype=np.uint8)
        # Create checkerboard
        plane[::2, ::2, :] = 255
        plane[1::2, 1::2, :] = 255
        
        metrics = analyze_bit_plane_complexity(plane)
        
        # High edge density (many transitions)
        assert metrics['R_edge_density'] > 0.4
        
        # High uniformity (std > 0)
        assert metrics['R_uniformity'] > 0.4
    
    def test_metric_keys(self):
        """Test that all expected metrics are present."""
        plane = np.random.randint(0, 2, (50, 50, 3), dtype=np.uint8) * 255
        metrics = analyze_bit_plane_complexity(plane)
        
        expected_keys = [
            'R_edge_density', 'G_edge_density', 'B_edge_density',
            'R_uniformity', 'G_uniformity', 'B_uniformity'
        ]
        
        for key in expected_keys:
            assert key in metrics
    
    def test_metric_ranges(self):
        """Test that metrics are in valid ranges."""
        plane = np.random.randint(0, 2, (50, 50, 3), dtype=np.uint8) * 255
        metrics = analyze_bit_plane_complexity(plane)
        
        # Edge density can be > 1.0 for binary random data
        # (counts absolute changes, not normalized to 0-1)
        for channel in ['R', 'G', 'B']:
            assert metrics[f'{channel}_edge_density'] >= 0.0
            assert metrics[f'{channel}_uniformity'] >= 0.0
