"""
Tests for steganography capacity calculations
"""
import pytest
from backend.stego.capacity import (
    calculate_raw_capacity,
    calculate_usable_capacity,
    check_payload_capacity,
    format_bytes
)


class TestRawCapacity:
    """Test raw LSB capacity calculation"""
    
    def test_small_image_capacity(self):
        """100×100 RGB image should have correct raw capacity"""
        result = calculate_raw_capacity(100, 100)
        
        assert result['total_pixels'] == 10_000
        assert result['bits_per_pixel'] == 3  # RGB only
        assert result['total_bits'] == 30_000
        assert result['total_bytes'] == 3_750  # 30000 / 8
    
    def test_hd_image_capacity(self):
        """1920×1080 RGB image capacity"""
        result = calculate_raw_capacity(1920, 1080)
        
        assert result['total_pixels'] == 1920 * 1080
        assert result['bits_per_pixel'] == 3
        assert result['total_bits'] == 1920 * 1080 * 3
        assert result['total_bytes'] == (1920 * 1080 * 3) // 8
    
    def test_alpha_not_used(self):
        """Alpha channel should not be used (always 3 bits per pixel)"""
        result = calculate_raw_capacity(100, 100, use_alpha=True)
        
        # Even with use_alpha=True, should still be 3 bits per pixel
        # because we preserve alpha
        assert result['bits_per_pixel'] == 3
    
    def test_single_pixel(self):
        """Single pixel image"""
        result = calculate_raw_capacity(1, 1)
        
        assert result['total_pixels'] == 1
        assert result['total_bits'] == 3
        assert result['total_bytes'] == 0  # Floor division: 3 // 8 = 0


class TestUsableCapacity:
    """Test usable capacity after overhead"""
    
    def test_usable_capacity_with_default_overhead(self):
        """Usable capacity should account for 64-byte overhead"""
        result = calculate_usable_capacity(100, 100)
        
        raw_bytes = 3_750
        overhead = 64
        usable = raw_bytes - overhead
        
        assert result['raw_capacity_bytes'] == raw_bytes
        assert result['container_overhead_bytes'] == overhead
        assert result['usable_capacity_bytes'] == usable
        assert result['efficiency_percent'] == pytest.approx((usable / raw_bytes) * 100)
    
    def test_usable_capacity_custom_overhead(self):
        """Should allow custom overhead"""
        result = calculate_usable_capacity(200, 200, container_overhead=100)
        
        raw_bytes = (200 * 200 * 3) // 8
        overhead = 100
        usable = raw_bytes - overhead
        
        assert result['container_overhead_bytes'] == 100
        assert result['usable_capacity_bytes'] == usable
    
    def test_usable_capacity_small_image(self):
        """Small image with more overhead than capacity"""
        result = calculate_usable_capacity(10, 10, container_overhead=100)
        
        # Raw capacity: 10*10*3 / 8 = 37.5 = 37 bytes
        # Overhead: 100 bytes
        # Usable: max(0, 37 - 100) = 0
        
        assert result['usable_capacity_bytes'] == 0
        assert result['efficiency_percent'] == 0


class TestPayloadCapacityCheck:
    """Test payload fitting checks"""
    
    def test_payload_fits(self):
        """Small payload should fit in large image"""
        # 100×100 = 3750 bytes raw, ~3686 usable
        result = check_payload_capacity(100, 100, payload_size=1000)
        
        assert result['fits'] is True
        assert result['payload_bytes'] == 1000
        assert result['remaining_bytes'] > 0
        assert 0 < result['utilization_percent'] < 100
    
    def test_payload_too_large(self):
        """Large payload should not fit in small image"""
        # 50×50 = 937 bytes raw, ~873 usable
        result = check_payload_capacity(50, 50, payload_size=1000)
        
        assert result['fits'] is False
        assert result['payload_bytes'] == 1000
        assert result['remaining_bytes'] < 0
        assert result['utilization_percent'] > 100
    
    def test_payload_exact_fit(self):
        """Payload exactly at capacity"""
        # Calculate exact fit
        raw = (100 * 100 * 3) // 8  # 3750
        usable = raw - 64  # 3686
        payload = usable - 16  # Account for 16-byte encryption overhead
        
        result = check_payload_capacity(100, 100, payload_size=payload)
        
        assert result['fits'] is True
        assert result['utilization_percent'] == pytest.approx(100.0, abs=0.1)
        assert abs(result['remaining_bytes']) < 5
    
    def test_encryption_overhead_accounted(self):
        """Should account for 16-byte AES-GCM tag"""
        result = check_payload_capacity(100, 100, payload_size=1000)
        
        # Required should be payload + 16 bytes
        assert result['required_bytes'] == 1000 + 16


class TestByteFormatting:
    """Test human-readable byte formatting"""
    
    def test_format_bytes(self):
        """Should format bytes correctly"""
        assert format_bytes(100) == "100 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1536) == "1.5 KB"
        assert format_bytes(1024 * 1024) == "1.00 MB"
        assert format_bytes(2.5 * 1024 * 1024) == "2.50 MB"
    
    def test_format_zero_bytes(self):
        """Should handle zero bytes"""
        assert format_bytes(0) == "0 B"
    
    def test_format_large_bytes(self):
        """Should format large values"""
        assert format_bytes(10 * 1024 * 1024) == "10.00 MB"


class TestCapacityEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_dimension_image(self):
        """Zero dimension should result in zero capacity"""
        result = calculate_raw_capacity(0, 100)
        assert result['total_bytes'] == 0
        
        result = calculate_raw_capacity(100, 0)
        assert result['total_bytes'] == 0
    
    def test_very_large_image(self):
        """Should handle very large images"""
        # 4K image
        result = calculate_raw_capacity(3840, 2160)
        
        assert result['total_pixels'] == 3840 * 2160
        assert result['total_bytes'] == (3840 * 2160 * 3) // 8
        assert result['total_bytes'] > 1024 * 1024  # > 1 MB
