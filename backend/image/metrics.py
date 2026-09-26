"""Image quality metrics: MSE and PSNR for steganography evaluation.

This module implements Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR)
metrics to measure the visual difference between cover and stego images.

PSNR threshold context (from course material):
- PSNR >= 30 dB: Generally acceptable quality for steganography
- Higher PSNR = Less perceptible difference
- Lower PSNR = More visible artifacts

Note: 30 dB is a guideline from academic literature, not a hard requirement.
Actual acceptable PSNR depends on application and image content.

Author: Hana (247006111170)
Task: T15 - MSE & PSNR Metrics
"""

import numpy as np
from PIL import Image
from typing import Union, Tuple


# Constants
MAX_PIXEL_VALUE = 255  # For 8-bit images
PSNR_THRESHOLD_CONTEXT = 30.0  # dB - Course material guideline (not hard requirement)


class MetricsError(Exception):
    """Base exception for metrics calculation errors."""
    pass


def calculate_mse(cover: Union[Image.Image, np.ndarray], 
                  stego: Union[Image.Image, np.ndarray]) -> float:
    """Calculate Mean Squared Error between cover and stego images.
    
    MSE measures the average squared difference between corresponding pixels.
    Lower MSE = more similar images.
    MSE = 0 means images are identical.
    
    Formula:
        MSE = (1 / N) * Σ(cover[i] - stego[i])²
        where N = total number of pixels × channels
    
    Args:
        cover: Cover image (PIL Image or numpy array)
        stego: Stego image (PIL Image or numpy array)
    
    Returns:
        float: MSE value (0.0 to 65025.0 for 8-bit images)
            - 0.0 = identical images
            - Higher values = more difference
    
    Raises:
        MetricsError: If images have different dimensions
        ValueError: If input types are invalid
    
    Example:
        >>> from PIL import Image
        >>> cover = Image.open("cover.png")
        >>> stego = Image.open("stego.png")
        >>> mse = calculate_mse(cover, stego)
        >>> print(f"MSE: {mse:.2f}")
    """
    # Convert to numpy arrays if needed
    if isinstance(cover, Image.Image):
        cover_arr = np.array(cover)
    elif isinstance(cover, np.ndarray):
        cover_arr = cover
    else:
        raise ValueError(f"Cover must be PIL Image or numpy array, got {type(cover)}")
    
    if isinstance(stego, Image.Image):
        stego_arr = np.array(stego)
    elif isinstance(stego, np.ndarray):
        stego_arr = stego
    else:
        raise ValueError(f"Stego must be PIL Image or numpy array, got {type(stego)}")
    
    # Validate dimensions
    if cover_arr.shape != stego_arr.shape:
        raise MetricsError(
            f"Image dimensions must match: cover {cover_arr.shape} vs stego {stego_arr.shape}"
        )
    
    # Calculate MSE
    # Convert to float to avoid integer overflow
    cover_float = cover_arr.astype(np.float64)
    stego_float = stego_arr.astype(np.float64)
    
    # Squared difference
    squared_diff = (cover_float - stego_float) ** 2
    
    # Mean of all squared differences
    mse = np.mean(squared_diff)
    
    return float(mse)


def calculate_psnr(cover: Union[Image.Image, np.ndarray], 
                   stego: Union[Image.Image, np.ndarray],
                   mse: float = None) -> float:
    """Calculate Peak Signal-to-Noise Ratio between cover and stego images.
    
    PSNR measures image quality in decibels (dB).
    Higher PSNR = better quality (less perceptible difference).
    
    Formula:
        PSNR = 10 * log₁₀(MAX² / MSE)
        where MAX = 255 for 8-bit images
    
    Special case:
        If MSE = 0 (identical images), PSNR = infinity (represented as float('inf'))
    
    Course material context:
        - PSNR ≥ 30 dB: Generally considered acceptable
        - PSNR ≥ 40 dB: Very good quality
        - PSNR ≥ 50 dB: Excellent quality
        - PSNR = ∞: Identical images
    
    Args:
        cover: Cover image (PIL Image or numpy array)
        stego: Stego image (PIL Image or numpy array)
        mse: Pre-calculated MSE (optional). If None, will calculate MSE first.
    
    Returns:
        float: PSNR in decibels (dB)
            - float('inf') if images are identical (MSE = 0)
            - Typically ranges from 20 dB to 50 dB for steganography
            - Higher is better
    
    Raises:
        MetricsError: If images have different dimensions or MSE calculation fails
    
    Example:
        >>> cover = Image.open("cover.png")
        >>> stego = Image.open("stego.png")
        >>> psnr = calculate_psnr(cover, stego)
        >>> print(f"PSNR: {psnr:.2f} dB")
        >>> if psnr >= 30:
        >>>     print("Quality is acceptable (≥30 dB)")
    """
    # Calculate MSE if not provided
    if mse is None:
        mse = calculate_mse(cover, stego)
    
    # Handle special case: identical images (MSE = 0)
    if mse == 0.0:
        return float('inf')
    
    # Calculate PSNR using formula: PSNR = 10 * log10(MAX^2 / MSE)
    max_squared = MAX_PIXEL_VALUE ** 2
    psnr = 10.0 * np.log10(max_squared / mse)
    
    return float(psnr)


def calculate_metrics(cover: Union[Image.Image, np.ndarray], 
                      stego: Union[Image.Image, np.ndarray]) -> dict:
    """Calculate both MSE and PSNR metrics together (efficient).
    
    This function calculates MSE once and derives PSNR from it,
    avoiding redundant computation.
    
    Args:
        cover: Cover image
        stego: Stego image
    
    Returns:
        dict: Metrics dictionary with keys:
            - 'mse': float - Mean Squared Error
            - 'psnr': float - Peak Signal-to-Noise Ratio (dB)
            - 'psnr_db': float - Same as 'psnr' (for clarity)
            - 'quality_assessment': str - Human-readable quality assessment
    
    Example:
        >>> metrics = calculate_metrics(cover, stego)
        >>> print(f"MSE: {metrics['mse']:.4f}")
        >>> print(f"PSNR: {metrics['psnr']:.2f} dB")
        >>> print(f"Quality: {metrics['quality_assessment']}")
    """
    # Calculate MSE
    mse = calculate_mse(cover, stego)
    
    # Calculate PSNR using the MSE
    psnr = calculate_psnr(cover, stego, mse=mse)
    
    # Quality assessment based on PSNR
    if psnr == float('inf'):
        quality = "Identical (perfect)"
    elif psnr >= 50:
        quality = "Excellent (≥50 dB)"
    elif psnr >= 40:
        quality = "Very good (≥40 dB)"
    elif psnr >= PSNR_THRESHOLD_CONTEXT:
        quality = f"Acceptable (≥{PSNR_THRESHOLD_CONTEXT} dB)"
    elif psnr >= 20:
        quality = f"Below threshold (<{PSNR_THRESHOLD_CONTEXT} dB)"
    else:
        quality = "Poor (<20 dB)"
    
    return {
        'mse': mse,
        'psnr': psnr,
        'psnr_db': psnr,  # Alias for clarity
        'quality_assessment': quality,
    }


def format_psnr(psnr: float) -> str:
    """Format PSNR value for display.
    
    Args:
        psnr: PSNR value in dB
    
    Returns:
        str: Formatted PSNR string
            - "∞ dB" for infinite PSNR (identical images)
            - "XX.XX dB" for finite PSNR values
    
    Example:
        >>> format_psnr(42.5)
        '42.50 dB'
        >>> format_psnr(float('inf'))
        '∞ dB (identical)'
    """
    if psnr == float('inf'):
        return "∞ dB (identical)"
    else:
        return f"{psnr:.2f} dB"


def format_mse(mse: float) -> str:
    """Format MSE value for display.
    
    Args:
        mse: MSE value
    
    Returns:
        str: Formatted MSE string
    
    Example:
        >>> format_mse(0.5432)
        '0.5432'
        >>> format_mse(0.0)
        '0.0000 (identical)'
    """
    if mse == 0.0:
        return "0.0000 (identical)"
    else:
        return f"{mse:.4f}"


def is_acceptable_quality(psnr: float, threshold: float = PSNR_THRESHOLD_CONTEXT) -> bool:
    """Check if PSNR meets acceptable quality threshold.
    
    Args:
        psnr: PSNR value in dB
        threshold: Quality threshold in dB (default: 30 dB from course material)
    
    Returns:
        bool: True if PSNR >= threshold or PSNR is infinite
    
    Note:
        The default threshold (30 dB) is a guideline from academic literature,
        not a hard requirement. Actual acceptable quality depends on:
        - Application requirements
        - Image content
        - User perception
    
    Example:
        >>> psnr = calculate_psnr(cover, stego)
        >>> if is_acceptable_quality(psnr):
        >>>     print("Quality is acceptable for steganography")
    """
    if psnr == float('inf'):
        return True
    return psnr >= threshold


def calculate_per_channel_mse(cover: Union[Image.Image, np.ndarray],
                               stego: Union[Image.Image, np.ndarray]) -> dict:
    """Calculate MSE for each color channel separately.
    
    This provides more detailed analysis of where differences occur.
    Useful for debugging and understanding embedding impact.
    
    Args:
        cover: Cover image (must be RGB or RGBA)
        stego: Stego image (must be RGB or RGBA)
    
    Returns:
        dict: MSE per channel:
            - 'r': float - Red channel MSE
            - 'g': float - Green channel MSE
            - 'b': float - Blue channel MSE
            - 'a': float - Alpha channel MSE (if present)
            - 'overall': float - Overall MSE (same as calculate_mse)
    
    Raises:
        MetricsError: If images don't have channel dimension
    
    Example:
        >>> metrics = calculate_per_channel_mse(cover, stego)
        >>> print(f"Red MSE: {metrics['r']:.4f}")
        >>> print(f"Green MSE: {metrics['g']:.4f}")
        >>> print(f"Blue MSE: {metrics['b']:.4f}")
    """
    # Convert to numpy arrays
    if isinstance(cover, Image.Image):
        cover_arr = np.array(cover)
    else:
        cover_arr = cover
    
    if isinstance(stego, Image.Image):
        stego_arr = np.array(stego)
    else:
        stego_arr = stego
    
    # Validate dimensions
    if cover_arr.shape != stego_arr.shape:
        raise MetricsError(
            f"Image dimensions must match: cover {cover_arr.shape} vs stego {stego_arr.shape}"
        )
    
    # Check if image has channels
    if len(cover_arr.shape) < 3:
        raise MetricsError("Images must have color channels (RGB or RGBA)")
    
    num_channels = cover_arr.shape[2]
    
    # Calculate MSE per channel
    result = {}
    channel_names = ['r', 'g', 'b', 'a']
    
    cover_float = cover_arr.astype(np.float64)
    stego_float = stego_arr.astype(np.float64)
    
    for i in range(num_channels):
        channel_name = channel_names[i]
        squared_diff = (cover_float[:, :, i] - stego_float[:, :, i]) ** 2
        mse = np.mean(squared_diff)
        result[channel_name] = float(mse)
    
    # Overall MSE
    result['overall'] = calculate_mse(cover_arr, stego_arr)
    
    return result


# Export threshold for reference
__all__ = [
    'calculate_mse',
    'calculate_psnr',
    'calculate_metrics',
    'format_psnr',
    'format_mse',
    'is_acceptable_quality',
    'calculate_per_channel_mse',
    'MetricsError',
    'MAX_PIXEL_VALUE',
    'PSNR_THRESHOLD_CONTEXT',
]
