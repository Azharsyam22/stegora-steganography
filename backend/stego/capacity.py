"""
Steganography Capacity Calculator
Calculate available capacity for LSB embedding, container framing overhead,
and reject oversized payloads before image mutation.

Author: Naufal (247006111158)
Task: T07 - Capacity Calculator
"""
from typing import Dict, Optional, Union


# Project design constants (STEGO_SPEC.md & SECURITY.md)
BITS_PER_CHANNEL = 1
CHANNELS_PER_PIXEL = 3  # RGB only, alpha channel is strictly preserved
AES_GCM_TAG_SIZE = 16   # 128-bit authentication tag (bytes)
FIXED_HEADER_SIZE = 12  # STGR (4) + ver (1) + flags (1) + type (1) + res (1) + payload_len (4)
METADATA_LENGTHS_SIZE = 5  # salt_len (1) + iv_len (1) + filename_len (2) + mime_len (1)
SALT_SIZE = 16          # PBKDF2 salt length (bytes)
IV_SIZE = 12            # AES-GCM IV length (bytes)
DEFAULT_MIME_SIZE = 24  # len("application/octet-stream")

# Minimum framing overhead without filename or MIME (12 + 5 + 16 + 12 = 45 bytes)
# Plus 16 bytes authentication tag = 61 bytes total minimum overhead
MINIMUM_CONTAINER_OVERHEAD = FIXED_HEADER_SIZE + METADATA_LENGTHS_SIZE + SALT_SIZE + IV_SIZE + AES_GCM_TAG_SIZE
DEFAULT_CONTAINER_OVERHEAD = 64  # Standard default estimated overhead


class CapacityError(Exception):
    """Base exception for capacity errors."""
    pass


class PayloadCapacityExceededError(CapacityError):
    """Raised when payload exceeds available image steganography capacity."""
    def __init__(
        self,
        required_bytes: int,
        available_bytes: int,
        payload_bytes: int,
        message: str = ""
    ):
        self.required_bytes = required_bytes
        self.available_bytes = available_bytes
        self.payload_bytes = payload_bytes
        if not message:
            message = (
                f"Payload exceeds capacity: requires {required_bytes} bytes "
                f"(plaintext: {payload_bytes} bytes), but only {available_bytes} bytes available."
            )
        super().__init__(message)


def calculate_exact_container_overhead(
    filename: str = "",
    mime_type: str = "application/octet-stream",
    salt_len: int = SALT_SIZE,
    iv_len: int = IV_SIZE,
    tag_len: int = AES_GCM_TAG_SIZE
) -> int:
    """
    Calculate the exact container framing overhead in bytes including metadata and auth tag.
    
    Overhead breakdown:
    - Fixed STGR header: 12 bytes
    - Metadata length fields: 5 bytes
    - Salt: 16 bytes
    - IV: 12 bytes
    - Filename bytes: len(filename.encode('utf-8'))
    - MIME type bytes: len(mime_type.encode('ascii'))
    - AES-GCM authentication tag: 16 bytes
    
    Args:
        filename: Optional payload filename
        mime_type: Optional payload MIME type
        salt_len: Length of cryptographic salt (default: 16)
        iv_len: Length of initialization vector (default: 12)
        tag_len: Length of AES-GCM authentication tag (default: 16)
        
    Returns:
        Exact overhead in bytes
    """
    fn_bytes_len = len(filename.encode('utf-8')) if filename else 0
    mime_bytes_len = len(mime_type.encode('ascii')) if mime_type else 0
    return (
        FIXED_HEADER_SIZE +
        METADATA_LENGTHS_SIZE +
        salt_len +
        iv_len +
        fn_bytes_len +
        mime_bytes_len +
        tag_len
    )


def calculate_raw_capacity(width: int, height: int, use_alpha: bool = False) -> Dict[str, int]:
    """
    Calculate raw LSB capacity for RGB(A) image.
    
    For 1-bit RGB LSB:
    - 3 bits per pixel (R, G, B channels)
    - Alpha channel is strictly preserved (never used for embedding)
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        use_alpha: Whether to use alpha channel (always ignored to preserve alpha)
        
    Returns:
        Dictionary containing:
        - total_pixels: Total pixel count
        - bits_per_pixel: Usable bits per pixel (always 3 for RGB)
        - total_bits: Total bits available
        - total_bytes: Total bytes available (floor division: total_bits // 8)
        
    Raises:
        ValueError: If width or height is negative
    """
    if width < 0 or height < 0:
        raise ValueError(f"Image dimensions must be non-negative: width={width}, height={height}")
        
    total_pixels = width * height
    bits_per_pixel = CHANNELS_PER_PIXEL * BITS_PER_CHANNEL  # Always 3
    total_bits = total_pixels * bits_per_pixel
    total_bytes = total_bits // 8
    
    return {
        'total_pixels': total_pixels,
        'bits_per_pixel': bits_per_pixel,
        'total_bits': total_bits,
        'total_bytes': total_bytes,
    }


def calculate_usable_capacity(
    width: int, 
    height: int, 
    container_overhead: int = DEFAULT_CONTAINER_OVERHEAD
) -> Dict[str, Union[int, float]]:
    """
    Calculate usable capacity after accounting for container overhead.
    
    Container overhead includes:
    - Fixed header (12 bytes)
    - Metadata lengths (5 bytes)
    - Salt (16 bytes)
    - IV (12 bytes)
    - Filename and MIME
    - Authentication tag (16 bytes)
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        container_overhead: Estimated/exact overhead in bytes (default: 64)
        
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
    efficiency = (usable_bytes / raw_bytes * 100.0) if raw_bytes > 0 else 0.0
    
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
    container_overhead: int = DEFAULT_CONTAINER_OVERHEAD,
    encryption_overhead: int = AES_GCM_TAG_SIZE
) -> Dict[str, any]:
    """
    Check if payload fits within image capacity and generate rejection diagnostics.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        payload_size: Plaintext payload size in bytes
        container_overhead: Container framing overhead in bytes (default: 64)
        encryption_overhead: GCM authentication tag size in bytes (default: 16)
        
    Returns:
        Dictionary containing:
        - fits: Boolean indicating if payload fits
        - payload_bytes: Plaintext payload size
        - required_bytes: Total required bytes (payload + encryption overhead)
        - available_bytes: Available usable capacity for encrypted payload
        - raw_capacity_bytes: Total raw capacity of the image
        - container_overhead_bytes: Overhead allocated for container framing
        - utilization_percent: Percentage of usable capacity required
        - remaining_bytes: Remaining capacity (negative if oversized)
        - rejection_reason: Optional human-readable rejection explanation
        
    Raises:
        ValueError: If payload_size is negative
    """
    if payload_size < 0:
        raise ValueError(f"Payload size cannot be negative: {payload_size}")
        
    capacity_info = calculate_usable_capacity(width, height, container_overhead)
    available = int(capacity_info['usable_capacity_bytes'])
    raw_bytes = int(capacity_info['raw_capacity_bytes'])
    
    required = payload_size + encryption_overhead
    fits = (required <= available) and (raw_bytes >= container_overhead + required)
    
    if available > 0:
        utilization = (required / available) * 100.0
    elif required == 0 and available == 0:
        utilization = 0.0
    else:
        utilization = float('inf') if required > 0 else 0.0
        
    remaining = available - required
    
    rejection_reason = None
    if not fits:
        rejection_reason = (
            f"Payload of {format_bytes(payload_size)} (requires {format_bytes(required)} "
            f"with crypto/container overhead) exceeds available capacity of {format_bytes(available)} "
            f"(short by {format_bytes(abs(remaining))})."
        )
    
    return {
        'fits': fits,
        'payload_bytes': payload_size,
        'required_bytes': required,
        'available_bytes': available,
        'raw_capacity_bytes': raw_bytes,
        'container_overhead_bytes': container_overhead,
        'utilization_percent': utilization,
        'remaining_bytes': remaining,
        'rejection_reason': rejection_reason,
    }


def validate_payload_capacity(
    width: int,
    height: int,
    payload_size: int,
    container_overhead: int = DEFAULT_CONTAINER_OVERHEAD,
    encryption_overhead: int = AES_GCM_TAG_SIZE
) -> Dict[str, any]:
    """
    Validate that payload fits within capacity. Raises PayloadCapacityExceededError
    if the payload exceeds capacity (enforcing preflight rejection before mutation).
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        payload_size: Plaintext payload size in bytes
        container_overhead: Container framing overhead in bytes
        encryption_overhead: Authentication tag size in bytes
        
    Returns:
        The capacity check dictionary if valid.
        
    Raises:
        PayloadCapacityExceededError: If payload exceeds capacity.
    """
    result = check_payload_capacity(
        width=width,
        height=height,
        payload_size=payload_size,
        container_overhead=container_overhead,
        encryption_overhead=encryption_overhead
    )
    if not result['fits']:
        raise PayloadCapacityExceededError(
            required_bytes=result['required_bytes'],
            available_bytes=result['available_bytes'],
            payload_bytes=payload_size,
            message=result['rejection_reason']
        )
    return result


def format_bytes(num_bytes: Union[int, float]) -> str:
    """
    Format bytes as human-readable string (B, KB, MB, GB).
    
    Args:
        num_bytes: Number of bytes (can be negative or float)
        
    Returns:
        Formatted string (e.g., "100 B", "1.5 KB", "2.30 MB", "-50 B")
    """
    abs_bytes = abs(num_bytes)
    sign = "-" if num_bytes < 0 else ""
    
    if abs_bytes < 1024:
        return f"{sign}{int(abs_bytes)} B"
    elif abs_bytes < 1024 * 1024:
        return f"{sign}{abs_bytes / 1024:.1f} KB"
    elif abs_bytes < 1024 * 1024 * 1024:
        return f"{sign}{abs_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{sign}{abs_bytes / (1024 * 1024 * 1024):.2f} GB"
