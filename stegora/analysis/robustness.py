"""
Stegora Robustness Testing Module

Provides JPEG robustness testing and security validation.
Tests steganography resilience against common attacks and transformations.

Academic Context:
- LSB steganography is fragile to lossy compression (JPEG)
- Security testing validates authentication and error handling
- Robustness metrics quantify data survival after attacks

Attack Types Tested:
1. JPEG compression (lossy)
2. Wrong credentials (password, stego-key)
3. Data tampering (bit flips, truncation)
4. Malformed headers

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

from typing import Dict, Tuple, Optional, List
import numpy as np
from PIL import Image
import io
import tempfile
import os


def test_jpeg_compression(
    image: np.ndarray,
    quality: int = 95
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Test image quality after JPEG compression.
    
    JPEG is lossy compression that modifies pixel values.
    LSB steganography is extremely fragile to JPEG compression.
    
    Args:
        image: Original image array (H, W, 3) uint8
        quality: JPEG quality (1-100, higher=better quality)
    
    Returns:
        Tuple of:
        - Compressed image array
        - Metrics dict with 'mse', 'psnr', 'survival_rate'
    
    Academic Note:
        - Quality 95+: minimal visible change, but LSB destroyed
        - Quality 75: JPEG default, significant LSB destruction
        - Quality 50-: visible artifacts, LSB completely lost
    """
    if image.ndim != 3 or image.shape[2] not in (3, 4):
        raise ValueError(f"Expected RGB/RGBA image, got shape {image.shape}")
    
    if not 1 <= quality <= 100:
        raise ValueError(f"Quality must be 1-100, got {quality}")
    
    # Convert to PIL Image
    pil_img = Image.fromarray(image[:, :, :3])  # RGB only for JPEG
    
    # Save to JPEG in memory
    buffer = io.BytesIO()
    pil_img.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    
    # Load back
    compressed_pil = Image.open(buffer)
    compressed = np.array(compressed_pil)
    
    # Calculate metrics
    from backend.image.metrics import calculate_mse, calculate_psnr
    
    mse = calculate_mse(image[:, :, :3], compressed)
    psnr = calculate_psnr(mse)  # Pass MSE as first arg (will be detected as float)
    
    # Calculate LSB survival rate
    # (percentage of LSBs that remained unchanged)
    lsb_original = (image[:, :, :3] & 1).flatten()
    lsb_compressed = (compressed & 1).flatten()
    lsb_matches = np.sum(lsb_original == lsb_compressed)
    survival_rate = lsb_matches / len(lsb_original)
    
    metrics = {
        'mse': float(mse),
        'psnr': float(psnr),
        'lsb_survival_rate': float(survival_rate)
    }
    
    return compressed, metrics


def test_jpeg_multiple_qualities(
    image: np.ndarray,
    qualities: Optional[List[int]] = None
) -> Dict[int, Dict[str, float]]:
    """
    Test JPEG compression at multiple quality levels.
    
    Args:
        image: Original image array (H, W, 3) uint8
        qualities: List of quality values to test (default: [95, 85, 75, 50])
    
    Returns:
        Dictionary mapping quality → metrics dict
    
    Example:
        >>> results = test_jpeg_multiple_qualities(image)
        >>> print(f"Q95 PSNR: {results[95]['psnr']:.2f} dB")
        >>> print(f"Q95 LSB survival: {results[95]['lsb_survival_rate']:.2%}")
    """
    if qualities is None:
        qualities = [95, 85, 75, 50]
    
    results = {}
    for quality in qualities:
        _, metrics = test_jpeg_compression(image, quality)
        results[quality] = metrics
    
    return results


def calculate_bit_error_rate(
    original: np.ndarray,
    modified: np.ndarray
) -> Dict[str, float]:
    """
    Calculate bit error rate between original and modified images.
    
    BER (Bit Error Rate) = number of different bits / total bits
    
    Args:
        original: Original image (H, W, 3) uint8
        modified: Modified image (H, W, 3) uint8
    
    Returns:
        Dictionary with bit error rates:
        {
            'ber_overall': float (0-1),
            'ber_lsb': float (0-1, LSB plane only),
            'ber_msb': float (0-1, MSB plane only),
            'pixels_changed': int,
            'pixels_total': int
        }
    
    Raises:
        ValueError: If images have different shapes
    """
    if original.shape != modified.shape:
        raise ValueError(
            f"Images must have same shape, got {original.shape} vs {modified.shape}"
        )
    
    # Flatten for bit-level comparison
    orig_flat = original.flatten()
    mod_flat = modified.flatten()
    
    # Overall BER (all 8 bits)
    total_bits = len(orig_flat) * 8
    bit_errors = 0
    for orig_byte, mod_byte in zip(orig_flat, mod_flat):
        xor = orig_byte ^ mod_byte
        bit_errors += bin(xor).count('1')
    
    ber_overall = bit_errors / total_bits
    
    # LSB BER (bit 0 only)
    lsb_orig = orig_flat & 1
    lsb_mod = mod_flat & 1
    lsb_errors = np.sum(lsb_orig != lsb_mod)
    ber_lsb = lsb_errors / len(orig_flat)
    
    # MSB BER (bit 7 only)
    msb_orig = (orig_flat >> 7) & 1
    msb_mod = (mod_flat >> 7) & 1
    msb_errors = np.sum(msb_orig != msb_mod)
    ber_msb = msb_errors / len(orig_flat)
    
    # Pixel-level changes
    pixels_changed = np.sum(orig_flat != mod_flat)
    pixels_total = len(orig_flat)
    
    return {
        'ber_overall': float(ber_overall),
        'ber_lsb': float(ber_lsb),
        'ber_msb': float(ber_msb),
        'pixels_changed': int(pixels_changed),
        'pixels_total': int(pixels_total),
        'pixel_change_rate': float(pixels_changed / pixels_total)
    }


def simulate_bit_flip_attack(
    data: bytes,
    flip_probability: float = 0.001
) -> bytes:
    """
    Simulate bit-flip attack on binary data.
    
    Random bit flips can occur due to:
    - Transmission errors
    - Storage corruption
    - Intentional tampering
    
    Args:
        data: Original data bytes
        flip_probability: Probability of each bit being flipped (0-1)
    
    Returns:
        Modified data with random bit flips
    
    Example:
        >>> tampered = simulate_bit_flip_attack(original, flip_probability=0.01)
        >>> # 1% of bits are randomly flipped
    """
    if not 0 <= flip_probability <= 1:
        raise ValueError(f"flip_probability must be 0-1, got {flip_probability}")
    
    data_array = np.frombuffer(data, dtype=np.uint8)
    modified = data_array.copy()
    
    # For each byte, flip random bits
    for i in range(len(modified)):
        for bit_pos in range(8):
            if np.random.random() < flip_probability:
                # Flip bit at position bit_pos
                modified[i] ^= (1 << bit_pos)
    
    return modified.tobytes()


def simulate_truncation_attack(
    data: bytes,
    truncate_ratio: float = 0.1
) -> bytes:
    """
    Simulate data truncation attack.
    
    Truncation removes data from the end, simulating:
    - Incomplete download
    - Storage limits
    - Intentional data deletion
    
    Args:
        data: Original data bytes
        truncate_ratio: Fraction of data to remove (0-1)
    
    Returns:
        Truncated data
    
    Example:
        >>> truncated = simulate_truncation_attack(data, truncate_ratio=0.2)
        >>> # Last 20% of data removed
    """
    if not 0 <= truncate_ratio <= 1:
        raise ValueError(f"truncate_ratio must be 0-1, got {truncate_ratio}")
    
    keep_length = int(len(data) * (1 - truncate_ratio))
    return data[:keep_length]


def create_malformed_header(
    valid_header: bytes,
    corruption_type: str = 'magic'
) -> bytes:
    """
    Create malformed header for testing error handling.
    
    Corruption types:
    - 'magic': corrupt magic bytes (STGR → XXXX)
    - 'version': corrupt version byte
    - 'length': corrupt payload length field
    
    Args:
        valid_header: Valid header bytes (at least 12 bytes)
        corruption_type: Type of corruption to apply
    
    Returns:
        Malformed header bytes
    
    Raises:
        ValueError: If corruption_type is invalid
    """
    if len(valid_header) < 12:
        raise ValueError(f"Header too short: {len(valid_header)} bytes")
    
    header = bytearray(valid_header)
    
    if corruption_type == 'magic':
        # Corrupt magic bytes (first 4 bytes)
        header[0:4] = b'XXXX'
    
    elif corruption_type == 'version':
        # Corrupt version byte (offset 4)
        header[4] = 99  # Invalid version
    
    elif corruption_type == 'length':
        # Corrupt payload length (offset 8-11, big-endian uint32)
        # Set impossibly large length
        header[8:12] = (0xFFFFFFFF).to_bytes(4, 'big')
    
    else:
        raise ValueError(
            f"Unknown corruption_type: {corruption_type}. "
            f"Valid: 'magic', 'version', 'length'"
        )
    
    return bytes(header)


def test_stego_resilience(
    stego_image: np.ndarray,
    attack_type: str = 'jpeg',
    **attack_params
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Test steganography resilience against various attacks.
    
    Supported attacks:
    - 'jpeg': JPEG compression (param: quality)
    - 'noise': Gaussian noise (param: sigma)
    - 'blur': Gaussian blur (param: sigma)
    
    Args:
        stego_image: Stego image array (H, W, 3) uint8
        attack_type: Type of attack to apply
        **attack_params: Attack-specific parameters
    
    Returns:
        Tuple of (attacked_image, metrics)
    
    Example:
        >>> attacked, metrics = test_stego_resilience(
        ...     stego, attack_type='jpeg', quality=75
        ... )
    """
    if attack_type == 'jpeg':
        quality = attack_params.get('quality', 75)
        return test_jpeg_compression(stego_image, quality)
    
    elif attack_type == 'noise':
        sigma = attack_params.get('sigma', 5.0)
        # Add Gaussian noise
        noise = np.random.normal(0, sigma, stego_image.shape)
        attacked = np.clip(stego_image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        
        from backend.image.metrics import calculate_mse, calculate_psnr
        mse = calculate_mse(stego_image, attacked)
        psnr = calculate_psnr(mse)
        ber = calculate_bit_error_rate(stego_image, attacked)
        
        metrics = {
            'mse': float(mse),
            'psnr': float(psnr),
            'lsb_survival_rate': 1.0 - ber['ber_lsb']
        }
        
        return attacked, metrics
    
    elif attack_type == 'blur':
        sigma = attack_params.get('sigma', 1.0)
        
        # Use PIL's Gaussian blur (no scipy needed)
        from PIL import ImageFilter
        pil_img = Image.fromarray(stego_image)
        blurred_pil = pil_img.filter(ImageFilter.GaussianBlur(radius=sigma))
        attacked = np.array(blurred_pil)
        
        from backend.image.metrics import calculate_mse, calculate_psnr
        mse = calculate_mse(stego_image, attacked)
        psnr = calculate_psnr(mse)
        ber = calculate_bit_error_rate(stego_image, attacked)
        
        metrics = {
            'mse': float(mse),
            'psnr': float(psnr),
            'lsb_survival_rate': 1.0 - ber['ber_lsb']
        }
        
        return attacked, metrics
    
    else:
        raise ValueError(
            f"Unknown attack_type: {attack_type}. "
            f"Valid: 'jpeg', 'noise', 'blur'"
        )


# Export public API
__all__ = [
    'test_jpeg_compression',
    'test_jpeg_multiple_qualities',
    'calculate_bit_error_rate',
    'simulate_bit_flip_attack',
    'simulate_truncation_attack',
    'create_malformed_header',
    'test_stego_resilience'
]
