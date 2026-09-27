"""
Tests for steganography capacity calculations
"""
import pytest
from backend.stego.capacity import (
    calculate_raw_capacity,
    calculate_usable_capacity,
    check_payload_capacity,
    validate_payload_capacity,
    calculate_exact_container_overhead,
    format_bytes,
    PayloadCapacityExceededError,
    MINIMUM_CONTAINER_OVERHEAD
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

    def test_negative_dimensions_raise_error(self):
        """Negative dimensions should raise ValueError"""
        with pytest.raises(ValueError, match="Image dimensions must be non-negative"):
            calculate_raw_capacity(-10, 100)
            
        with pytest.raises(ValueError, match="Image dimensions must be non-negative"):
            calculate_raw_capacity(100, -5)

    def test_negative_payload_size_raises_error(self):
        """Negative payload size should raise ValueError"""
        with pytest.raises(ValueError, match="Payload size cannot be negative"):
            check_payload_capacity(100, 100, payload_size=-1)


class TestExactContainerOverhead:
    """Test calculation of exact container framing overhead"""
    
    def test_minimum_overhead(self):
        """Minimum overhead with no filename or MIME"""
        overhead = calculate_exact_container_overhead(filename="", mime_type="")
        # 12 (fixed) + 5 (meta lens) + 16 (salt) + 12 (iv) + 0 (fn) + 0 (mime) + 16 (tag) = 61
        assert overhead == 61
        assert overhead == MINIMUM_CONTAINER_OVERHEAD

    def test_overhead_with_filename_and_mime(self):
        """Overhead with custom filename and MIME type"""
        filename = "secret.txt"       # 10 bytes
        mime_type = "text/plain"      # 10 bytes
        overhead = calculate_exact_container_overhead(filename, mime_type)
        expected = 61 + len(filename.encode('utf-8')) + len(mime_type.encode('ascii'))
        assert overhead == expected
        assert overhead == 61 + 10 + 10  # 81 bytes


class TestValidatePayloadCapacityAndRejection:
    """Test strict validation and preflight rejection (enforcing Rule 8)"""
    
    def test_validate_payload_capacity_success(self):
        """Valid payload within capacity should return info without raising"""
        result = validate_payload_capacity(100, 100, payload_size=500)
        assert result['fits'] is True
        assert result['rejection_reason'] is None

    def test_validate_payload_capacity_raises_on_oversized(self):
        """Oversized payload must raise PayloadCapacityExceededError with diagnostics"""
        # 50x50 has 937 raw bytes, ~873 usable bytes. 2000 bytes payload will exceed it.
        with pytest.raises(PayloadCapacityExceededError) as exc_info:
            validate_payload_capacity(50, 50, payload_size=2000)
        
        err = exc_info.value
        assert err.payload_bytes == 2000
        assert err.required_bytes == 2000 + 16  # includes 16-byte tag
        assert err.available_bytes < err.required_bytes
        assert "exceeds" in str(err).lower()

    def test_one_byte_overflow_rejected(self):
        """Payload that exceeds usable capacity by exactly 1 byte must be rejected"""
        # 100x100: raw=3750, overhead=64 -> usable=3686
        # required = payload + 16
        # if payload = usable - 16 + 1 = 3671, required = 3687 > 3686
        usable = calculate_usable_capacity(100, 100, container_overhead=64)['usable_capacity_bytes']
        overflow_payload = usable - 16 + 1
        
        result = check_payload_capacity(100, 100, payload_size=overflow_payload, container_overhead=64)
        assert result['fits'] is False
        assert result['remaining_bytes'] == -1
        assert result['rejection_reason'] is not None
        assert "exceeds" in result['rejection_reason'].lower()

    def test_zero_capacity_utilization(self):
        """Zero usable capacity with non-zero required bytes should produce inf utilization"""
        result = check_payload_capacity(10, 10, payload_size=100, container_overhead=100)
        assert result['fits'] is False
        assert result['available_bytes'] == 0
        assert result['utilization_percent'] == float('inf')


class TestFormatBytesExtended:
    """Test extended formatting scenarios including negative bytes"""
    
    def test_format_negative_bytes(self):
        """Negative bytes should display with minus sign"""
        assert format_bytes(-50) == "-50 B"
        assert format_bytes(-2048) == "-2.0 KB"

    def test_format_gigabytes(self):
        """Gigabyte ranges should format properly"""
        gb_val = 2 * 1024 * 1024 * 1024
        assert format_bytes(gb_val) == "2.00 GB"

