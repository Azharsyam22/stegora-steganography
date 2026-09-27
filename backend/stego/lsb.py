"""
1-bit RGB LSB Steganography
Embed and extract data using least significant bit of RGB channels

Author: Naufal (247006111158)
Task: T10 - 1-bit RGB LSB Embedding
"""
from typing import List, Tuple
from PIL import Image
import numpy as np


class LSBError(Exception):
    """Raised when LSB operations fail"""
    pass


def embed_lsb(
    cover_image: Image.Image,
    container_bytes: bytes,
    positions: List[Tuple[int, int, int]]
) -> Image.Image:
    """
    Embed container bytes into cover image using 1-bit RGB LSB.
    
    Args:
        cover_image: PIL Image (RGB or RGBA)
        container_bytes: Complete STGR container bytes to embed
        positions: List of (x, y, channel) positions from keyed PRNG
        
    Returns:
        Stego image (PIL Image) with embedded data
        
    Raises:
        LSBError: If image mode is unsupported, positions are insufficient,
                  coordinates are out of bounds, or channel is invalid.
    """
    if not isinstance(cover_image, Image.Image):
        raise LSBError("cover_image must be a PIL Image instance")
    
    if cover_image.mode not in ('RGB', 'RGBA'):
        raise LSBError(
            f"Unsupported image mode '{cover_image.mode}'. "
            "Only 'RGB' and 'RGBA' modes are supported for 1-bit RGB LSB."
        )
    
    if not isinstance(container_bytes, (bytes, bytearray)):
        raise LSBError("container_bytes must be bytes or bytearray")
        
    if len(container_bytes) == 0:
        raise LSBError("container_bytes cannot be empty")
        
    num_bits = len(container_bytes) * 8
    
    if len(positions) < num_bits:
        raise LSBError(
            f"Not enough positions: need {num_bits} bit positions, "
            f"but only {len(positions)} provided"
        )
    
    width, height = cover_image.size
    pos_subset = positions[:num_bits]
    
    # Extract coordinate arrays
    xs = np.fromiter((p[0] for p in pos_subset), dtype=np.intp, count=num_bits)
    ys = np.fromiter((p[1] for p in pos_subset), dtype=np.intp, count=num_bits)
    cs = np.fromiter((p[2] for p in pos_subset), dtype=np.intp, count=num_bits)
    
    # Validate coordinate boundaries and channel index
    if np.any(xs < 0) or np.any(xs >= width) or np.any(ys < 0) or np.any(ys >= height):
        raise LSBError(f"Position coordinates outside image dimensions ({width}x{height})")
    
    # Channel must be 0 (Red), 1 (Green), or 2 (Blue). Channel 3 (Alpha) is strictly forbidden.
    if np.any(cs < 0) or np.any(cs > 2):
        raise LSBError("Invalid channel index: only RGB channels (0, 1, 2) allowed; Alpha (3) is forbidden")
    
    # Convert container bytes to bit array (MSB first)
    bits = np.unpackbits(np.frombuffer(container_bytes, dtype=np.uint8))
    
    # Convert image to numpy array (copy to avoid mutating original image)
    pixels = np.array(cover_image, copy=True)
    
    # Save original alpha if RGBA to verify strict preservation
    if cover_image.mode == 'RGBA':
        original_alpha = pixels[:, :, 3].copy()
    
    # Embed 1-bit LSB: clear bit 0 and bitwise-OR with payload bit
    pixels[ys, xs, cs] = (pixels[ys, xs, cs] & 0xFE) | bits
    
    # Strict assertion: Alpha channel must remain 100% unchanged
    if cover_image.mode == 'RGBA':
        if not np.array_equal(original_alpha, pixels[:, :, 3]):
            raise LSBError("Alpha channel integrity check failed: alpha was modified during embedding")
    
    # Convert numpy array back to PIL Image
    stego_image = Image.fromarray(pixels)
    if cover_image.format:
        stego_image.format = cover_image.format
        
    return stego_image


def extract_lsb(
    stego_image: Image.Image,
    positions: List[Tuple[int, int, int]],
    num_bytes: int
) -> bytes:
    """
    Extract container bytes from stego image using 1-bit RGB LSB
    
    Args:
        stego_image: PIL Image with embedded data
        positions: List of (x, y, channel) positions (same as embedding)
        num_bytes: Number of bytes to extract
        
    Returns:
        Extracted container bytes
        
    Raises:
        LSBError: If extraction fails
        
    TODO (T11 - Naufal): Implement actual LSB extraction
    - Convert image to numpy array
    - For each position, read LSB
    - Collect bits into bytes
    - Return byte array
    
    Algorithm:
        bits = []
        for each position:
            (x, y, channel) = position
            value = image[y, x, channel]
            bit = value & 0x01  # Extract LSB
            bits.append(bit)
        
        Convert bits to bytes and return
    """
    # Validate inputs
    if stego_image.mode not in ('RGB', 'RGBA'):
        raise LSBError(f"Unsupported image mode: {stego_image.mode}")
    
    num_bits = num_bytes * 8
    
    if len(positions) < num_bits:
        raise LSBError(
            f"Not enough positions: need {num_bits}, have {len(positions)}"
        )
    
    # Convert to numpy array
    pixels = np.array(stego_image)
    
    # STUB: Return dummy bytes
    # TODO (T11): Implement actual LSB extraction
    bits = []
    
    """
    # TODO (T11): Uncomment and implement this loop
    for bit_index in range(num_bits):
        x, y, channel = positions[bit_index]
        
        # Read LSB
        value = pixels[y, x, channel]
        bit = value & 0x01
        
        bits.append(bit)
    """
    
    # STUB: Return zeros for now
    # TODO (T11): Convert bits to bytes
    """
    # Convert bits to bytes
    container_bytes = bytearray()
    for byte_index in range(num_bytes):
        byte_value = 0
        for bit_index in range(8):
            bit = bits[byte_index * 8 + bit_index]
            byte_value = (byte_value << 1) | bit
        container_bytes.append(byte_value)
    
    return bytes(container_bytes)
    """
    
    return bytes(num_bytes)  # STUB: return zeros


def verify_alpha_preservation(
    cover_image: Image.Image,
    stego_image: Image.Image
) -> bool:
    """
    Verify that alpha channel was not modified during embedding
    
    Args:
        cover_image: Original cover image
        stego_image: Stego image after embedding
        
    Returns:
        True if alpha channels are identical (or both images are RGB)
    """
    # If RGB mode, no alpha to preserve
    if cover_image.mode == 'RGB' and stego_image.mode == 'RGB':
        return True
    
    # If RGBA mode, compare alpha channels
    if cover_image.mode == 'RGBA' and stego_image.mode == 'RGBA':
        cover_alpha = np.array(cover_image)[:, :, 3]
        stego_alpha = np.array(stego_image)[:, :, 3]
        return np.array_equal(cover_alpha, stego_alpha)
    
    return False
