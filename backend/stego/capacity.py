"""
Steganography Capacity Calculator
Calculate available capacity for LSB embedding
"""
from typing import Dict
from PIL import Image


def calculate_raw_capacity(width: int, height: int, use_alpha: bool = False) -> Dict[str, int]:
    """
    Calculate raw LSB capacity for RGB(A) image
    
    For 1-bit RGB LSB:
    - 3 bits per pixel (R, G, B channels)
    - Alpha channel is preserved (not used for embedding)
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        use_alpha: Whether to use alpha channel (always False for this implementation)
        
    Returns:
        Dictionary containing:
        - total_pixels: Total pixel count
        - bits_per_pixel: Usable bits per pixel (always 3 for RGB)
        - total_bits: Total bits available
        - total_bytes: Total bytes available (floor division)
    """
    total_pixels = width * height
    bits_per_pixel = 3  # RGB only, alpha preserved
    total_bits = total_pixels * bits_per_pixel
    total_bytes = total_bits // 8
    
    return {
        'total_pixels': total_pixels,
        'bits_per_pixel': bits_per_pixel,
        'total_bits': total_bits,
        'total_bytes': total_bytes,
    }


def calculate_usable_capacity(width: int, height: int, container_overhead: int = 64) -> Dict[str, int]:
    """
    Calculate usable capacity after accounting for container overhead
    
    Container overhead includes:
    - Fixed header (12 bytes minimum)
    - Metadata (salt, IV, filename, MIME)
    - Authentication tag
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        container_overhead: Estimated overhead in bytes (default: 64)
        
    Returns:
        Dictionary containing:
        - raw_capacity_bytes: Raw capacity before overhead
        - container_overhead_bytes: Overhead bytes
        - usable_capacity_bytes: Net capacity for payload
        - efficiency_percent: Percentage of raw capacity usable
    """
    raw_capacity = calculate_raw_capacity(width, height)
    raw_bytes = raw_capacity['total_bytes']
    usable_bytes = max(0, raw_bytes - container_overhead)
    efficiency = (usable_bytes / raw_bytes * 100) if raw_bytes > 0 else 0
    
    return {
        'raw_capacity_bytes': raw_bytes,
        'container_overhead_bytes': container_overhead,
        'usable_capacity_bytes': usable_bytes,
        'efficiency_percent': efficiency,
    }


def check_payload_capacity(
    width: int, 
    height: int, 
    payload_size: int,
    container_overhead: int = 64
) -> Dict[str, any]:
    """
    Check if payload fits within image capacity
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        payload_size: Payload size in bytes (before encryption)
        container_overhead: Container overhead in bytes
        
    Returns:
        Dictionary containing:
        - fits: Boolean indicating if payload fits
        - payload_bytes: Payload size
        - required_bytes: Total required bytes (payload + overhead)
        - available_bytes: Available capacity
        - utilization_percent: Percentage of capacity used
        - remaining_bytes: Remaining capacity (negative if oversized)
    """
    capacity_info = calculate_usable_capacity(width, height, container_overhead)
    available = capacity_info['usable_capacity_bytes']
    
    # Payload will be encrypted, adding ~16 bytes for GCM tag
    encryption_overhead = 16
    required = payload_size + encryption_overhead
    
    fits = required <= available
    utilization = (required / available * 100) if available > 0 else 0
    remaining = available - required
    
    return {
        'fits': fits,
        'payload_bytes': payload_size,
        'required_bytes': required,
        'available_bytes': available,
        'utilization_percent': utilization,
        'remaining_bytes': remaining,
    }


def format_bytes(num_bytes: int) -> str:
    """
    Format bytes as human-readable string
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    else:
        return f"{num_bytes / (1024 * 1024):.2f} MB"
