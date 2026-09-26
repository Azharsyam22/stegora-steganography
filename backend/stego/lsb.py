"""
1-bit RGB LSB Steganography
Embed and extract data using least significant bit of RGB channels

TODO: This is a STUB for T10-T11 (Naufal)
Implementation needed for actual LSB embedding and extraction
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
    Embed container bytes into cover image using 1-bit RGB LSB
    
    Args:
        cover_image: PIL Image (RGB or RGBA)
        container_bytes: Complete STGR container to embed
        positions: List of (x, y, channel) positions from PRNG
        
    Returns:
        Stego image (PIL Image) with embedded data
        
    Raises:
        LSBError: If embedding fails
        
    TODO (T10 - Naufal): Implement actual LSB embedding
    - Convert image to numpy array for efficiency
    - Convert container bytes to bit array
    - For each bit, modify LSB at corresponding position
    - Preserve all other bits (use bitwise operations)
    - Preserve alpha channel completely
    - Return modified image
    
    Algorithm:
        for each bit in container:
            (x, y, channel) = positions[bit_index]
            pixel = image[y, x]
            old_value = pixel[channel]
            new_value = (old_value & 0xFE) | bit  # Clear LSB, set to bit
            pixel[channel] = new_value
    """
    # Validate inputs
    if cover_image.mode not in ('RGB', 'RGBA'):
        raise LSBError(f"Unsupported image mode: {cover_image.mode}")
    
    # Convert container to bits
    num_bits = len(container_bytes) * 8
    
    if len(positions) < num_bits:
        raise LSBError(
            f"Not enough positions: need {num_bits}, have {len(positions)}"
        )
    
    # STUB: Create a copy of the image without modification
    # TODO (T10): Implement actual LSB embedding here
    stego_image = cover_image.copy()
    
    # Convert to numpy array for manipulation
    pixels = np.array(stego_image)
    
    # Convert bytes to bit list
    bits = []
    for byte in container_bytes:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    
    # Embed each bit (STUB - not actually modifying LSBs yet)
    # TODO (T10): Uncomment and implement this loop
    """
    for bit_index, bit in enumerate(bits):
        x, y, channel = positions[bit_index]
        
        # Get current channel value
        old_value = pixels[y, x, channel]
        
        # Clear LSB and set to new bit
        new_value = (old_value & 0xFE) | bit
        
        # Update pixel
        pixels[y, x, channel] = new_value
    """
    
    # Convert back to PIL Image
    # TODO (T10): Use modified pixels array
    # stego_image = Image.fromarray(pixels, mode=cover_image.mode)
    
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
