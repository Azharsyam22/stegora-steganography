"""
Stegora Histogram Analysis Module

Provides RGB histogram calculation and comparison for steganalysis.
Used to detect LSB embedding artifacts by comparing cover vs stego histograms.

Academic Context:
- Histogram shows pixel value distribution (0-255)
- LSB embedding can create subtle histogram changes
- Even bits (LSB=0) and odd bits (LSB=1) should have similar distribution
- Large differences may indicate steganography

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

from typing import Dict, Tuple, Optional
import numpy as np
from PIL import Image


def calculate_histogram(image: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Calculate RGB histogram for an image.
    
    Args:
        image: NumPy array of shape (H, W, 3) or (H, W, 4) with dtype uint8
               Supports RGB and RGBA images
    
    Returns:
        Dictionary with keys 'R', 'G', 'B' containing histogram arrays
        Each histogram is array of 256 values (counts for pixel values 0-255)
    
    Example:
        >>> img = np.array([[[100, 150, 200]]], dtype=np.uint8)
        >>> hist = calculate_histogram(img)
        >>> hist['R'][100]  # Count of pixels with R=100
        1
    
    Raises:
        ValueError: If image is not 3 or 4 channels
        ValueError: If image dtype is not uint8
    """
    if image.ndim != 3:
        raise ValueError(f"Expected 3D image array, got {image.ndim}D")
    
    height, width, channels = image.shape
    
    if channels not in (3, 4):
        raise ValueError(f"Expected RGB or RGBA image (3 or 4 channels), got {channels}")
    
    if image.dtype != np.uint8:
        raise ValueError(f"Expected uint8 image, got {image.dtype}")
    
    # Calculate histogram for each RGB channel
    # bins=256 covers full range 0-255
    # range=(0, 256) ensures bins are [0,1), [1,2), ..., [255,256)
    hist_r, _ = np.histogram(image[:, :, 0], bins=256, range=(0, 256))
    hist_g, _ = np.histogram(image[:, :, 1], bins=256, range=(0, 256))
    hist_b, _ = np.histogram(image[:, :, 2], bins=256, range=(0, 256))
    
    return {
        'R': hist_r,
        'G': hist_g,
        'B': hist_b
    }


def calculate_histogram_from_pil(image: Image.Image) -> Dict[str, np.ndarray]:
    """
    Calculate RGB histogram from PIL Image.
    
    Convenience wrapper for calculate_histogram that accepts PIL Image.
    
    Args:
        image: PIL Image in RGB or RGBA mode
    
    Returns:
        Dictionary with keys 'R', 'G', 'B' containing histogram arrays
    
    Raises:
        ValueError: If image is not RGB or RGBA mode
    """
    if image.mode not in ('RGB', 'RGBA'):
        raise ValueError(f"Expected RGB or RGBA image, got mode {image.mode}")
    
    img_array = np.array(image)
    return calculate_histogram(img_array)


def compare_histograms(
    cover_hist: Dict[str, np.ndarray],
    stego_hist: Dict[str, np.ndarray]
) -> Dict[str, float]:
    """
    Compare two histograms and calculate difference metrics.
    
    Uses multiple metrics to quantify histogram similarity:
    1. Mean Absolute Difference (MAD): Average absolute difference per bin
    2. Maximum Difference: Largest difference in any bin
    3. Chi-Square Distance: Statistical measure of distribution similarity
    
    Args:
        cover_hist: Histogram dict with 'R', 'G', 'B' keys
        stego_hist: Histogram dict with 'R', 'G', 'B' keys
    
    Returns:
        Dictionary with per-channel and overall metrics:
        {
            'R_mad': float,
            'G_mad': float,
            'B_mad': float,
            'R_max': float,
            'G_max': float,
            'B_max': float,
            'R_chi2': float,
            'G_chi2': float,
            'B_chi2': float,
            'overall_mad': float,
            'overall_max': float,
            'overall_chi2': float
        }
    
    Interpretation:
        - Lower values = more similar histograms
        - MAD: typical range 0-100 for LSB changes
        - Chi-square: < 100 very similar, > 1000 very different
    """
    metrics = {}
    
    channels = ['R', 'G', 'B']
    all_mad = []
    all_max = []
    all_chi2 = []
    
    for channel in channels:
        cover = cover_hist[channel].astype(np.float64)
        stego = stego_hist[channel].astype(np.float64)
        
        # Mean Absolute Difference
        diff = np.abs(cover - stego)
        mad = np.mean(diff)
        metrics[f'{channel}_mad'] = float(mad)
        all_mad.append(mad)
        
        # Maximum Difference
        max_diff = np.max(diff)
        metrics[f'{channel}_max'] = float(max_diff)
        all_max.append(max_diff)
        
        # Chi-Square Distance
        # Add small epsilon to avoid division by zero
        epsilon = 1e-10
        chi2 = np.sum((cover - stego) ** 2 / (cover + stego + epsilon))
        metrics[f'{channel}_chi2'] = float(chi2)
        all_chi2.append(chi2)
    
    # Overall metrics (average across channels)
    metrics['overall_mad'] = float(np.mean(all_mad))
    metrics['overall_max'] = float(np.max(all_max))
    metrics['overall_chi2'] = float(np.mean(all_chi2))
    
    return metrics


def analyze_lsb_histogram_pairs(histogram: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
    """
    Analyze even/odd LSB pairs in histogram for steganalysis.
    
    In natural images, pixel values differing by 1 (e.g., 100 vs 101)
    should have similar frequencies. LSB embedding disrupts this.
    
    This function checks the ratio of even/odd pairs:
    - Pair (2k, 2k+1) should have similar counts
    - Large imbalance suggests LSB modification
    
    Args:
        histogram: Histogram dict with 'R', 'G', 'B' keys
    
    Returns:
        Dictionary with per-channel analysis:
        {
            'R': {
                'mean_ratio': float,  # Average even/odd ratio
                'max_ratio': float,   # Maximum ratio (worst case)
                'suspicious_pairs': int  # Count of pairs with ratio > 2.0
            },
            'G': {...},
            'B': {...}
        }
    
    Interpretation:
        - mean_ratio close to 1.0 = natural distribution
        - mean_ratio >> 1.0 or << 1.0 = potential LSB embedding
        - suspicious_pairs > 10% of total pairs = likely stego
    """
    analysis = {}
    
    for channel in ['R', 'G', 'B']:
        hist = histogram[channel].astype(np.float64)
        
        ratios = []
        suspicious_count = 0
        
        # Analyze pairs (0,1), (2,3), (4,5), ..., (254,255)
        for i in range(0, 256, 2):
            even_count = hist[i]
            odd_count = hist[i + 1]
            
            # Skip empty pairs
            if even_count == 0 and odd_count == 0:
                continue
            
            # Calculate ratio (avoid division by zero)
            if odd_count == 0:
                ratio = even_count if even_count > 0 else 1.0
            else:
                ratio = even_count / odd_count
            
            ratios.append(ratio)
            
            # Suspicious if ratio > 2.0 or < 0.5 (one value 2x the other)
            if ratio > 2.0 or ratio < 0.5:
                suspicious_count += 1
        
        # Calculate statistics
        mean_ratio = float(np.mean(ratios)) if ratios else 1.0
        max_ratio = float(np.max(ratios)) if ratios else 1.0
        
        analysis[channel] = {
            'mean_ratio': mean_ratio,
            'max_ratio': max_ratio,
            'suspicious_pairs': suspicious_count
        }
    
    return analysis


def calculate_histogram_difference_image(
    cover: np.ndarray,
    stego: np.ndarray
) -> np.ndarray:
    """
    Calculate pixel-wise absolute difference between cover and stego images.
    
    Useful for visualizing which pixels changed during embedding.
    
    Args:
        cover: Cover image array (H, W, 3) uint8
        stego: Stego image array (H, W, 3) uint8
    
    Returns:
        Difference image (H, W, 3) uint8
        Brighter pixels = larger changes
    
    Raises:
        ValueError: If images have different shapes
    """
    if cover.shape != stego.shape:
        raise ValueError(
            f"Cover and stego must have same shape, "
            f"got {cover.shape} vs {stego.shape}"
        )
    
    # Calculate absolute difference
    diff = np.abs(cover.astype(np.int16) - stego.astype(np.int16))
    
    # Scale up differences for visibility (multiply by 128)
    # LSB changes (±1) become visible (128)
    diff_scaled = np.clip(diff * 128, 0, 255).astype(np.uint8)
    
    return diff_scaled


# Export public API
__all__ = [
    'calculate_histogram',
    'calculate_histogram_from_pil',
    'compare_histograms',
    'analyze_lsb_histogram_pairs',
    'calculate_histogram_difference_image'
]
