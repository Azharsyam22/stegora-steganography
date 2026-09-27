"""
Stegora LSB Plane Analysis Module

Provides LSB bit-plane extraction and enhanced visualization for steganalysis.
Implements "Enhanced LSB" technique to detect steganography.

Academic Context:
- Bit-plane: isolate specific bit position across all pixels
- LSB plane (bit 0) should look random/noise-like in natural images
- Patterns in LSB plane suggest steganography
- Enhanced visualization amplifies LSB patterns for human inspection

Steganalysis Techniques:
1. LSB Plane Extraction: Extract bit 0, 1, 2, etc. from each pixel
2. Enhanced LSB: Amplify LSB differences to make patterns visible
3. Visual Inspection: Human can spot non-random patterns

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

from typing import Tuple, Dict, Optional
import numpy as np
from PIL import Image


def extract_bit_plane(image: np.ndarray, bit_position: int = 0) -> np.ndarray:
    """
    Extract specific bit plane from image.
    
    Bit planes:
    - bit_position=0: LSB (least significant bit)
    - bit_position=1: second-least significant bit
    - bit_position=7: MSB (most significant bit)
    
    Args:
        image: Image array (H, W, 3) or (H, W, 4) uint8
        bit_position: Bit position to extract (0=LSB, 7=MSB)
    
    Returns:
        Bit plane array (H, W, 3) uint8
        Values are 0 or 255 (binary amplified for visibility)
    
    Example:
        >>> img = np.array([[[100, 150, 200]]], dtype=np.uint8)
        >>> # 100 = 0b01100100, LSB=0
        >>> # 150 = 0b10010110, LSB=0
        >>> # 200 = 0b11001000, LSB=0
        >>> plane = extract_bit_plane(img, bit_position=0)
        >>> plane[0, 0]  # All zeros
        array([0, 0, 0], dtype=uint8)
    
    Raises:
        ValueError: If bit_position not in range [0, 7]
    """
    if not 0 <= bit_position <= 7:
        raise ValueError(f"bit_position must be in [0, 7], got {bit_position}")
    
    if image.ndim != 3:
        raise ValueError(f"Expected 3D image array, got {image.ndim}D")
    
    # Extract RGB channels only (ignore alpha if present)
    rgb = image[:, :, :3]
    
    # Extract bit at position using bitwise AND
    # (pixel >> bit_position) & 1 gives 0 or 1
    bit = (rgb >> bit_position) & 1
    
    # Amplify to 0 or 255 for visibility
    plane = (bit * 255).astype(np.uint8)
    
    return plane


def extract_lsb_plane(image: np.ndarray) -> np.ndarray:
    """
    Extract LSB (Least Significant Bit) plane from image.
    
    Convenience wrapper for extract_bit_plane(image, bit_position=0).
    
    Args:
        image: Image array (H, W, 3) or (H, W, 4) uint8
    
    Returns:
        LSB plane (H, W, 3) uint8 with values 0 or 255
    """
    return extract_bit_plane(image, bit_position=0)


def create_enhanced_lsb_visual(image: np.ndarray) -> np.ndarray:
    """
    Create enhanced LSB visualization for steganalysis.
    
    Enhanced LSB technique:
    1. Extract LSB plane (bit 0)
    2. Apply spatial filtering to amplify patterns
    3. Adjust contrast to make subtle patterns visible
    
    In natural images, LSB plane looks random/noisy.
    In stego images, LSB plane may show patterns or structure.
    
    Args:
        image: Image array (H, W, 3) or (H, W, 4) uint8
    
    Returns:
        Enhanced visualization (H, W, 3) uint8
        Patterns in output suggest steganography
    """
    # Extract LSB plane
    lsb = extract_lsb_plane(image)
    
    # Convert to binary (0 or 1)
    lsb_binary = (lsb // 255).astype(np.float32)
    
    # Apply simple averaging filter to detect local patterns
    # If LSB is truly random, averaging nearby pixels → ~0.5
    # If LSB has patterns, averaging shows structure
    kernel_size = 3
    
    # Pad image for filtering
    padded = np.pad(
        lsb_binary,
        ((kernel_size // 2, kernel_size // 2),
         (kernel_size // 2, kernel_size // 2),
         (0, 0)),
        mode='edge'
    )
    
    # Calculate local average for each pixel
    height, width, channels = lsb_binary.shape
    averaged = np.zeros_like(lsb_binary)
    
    for i in range(height):
        for j in range(width):
            # Extract local window
            window = padded[i:i+kernel_size, j:j+kernel_size, :]
            # Calculate mean
            averaged[i, j, :] = np.mean(window, axis=(0, 1))
    
    # Calculate deviation from expected random value (0.5)
    # In random LSB: deviation ≈ 0
    # In patterned LSB: deviation > 0
    deviation = np.abs(averaged - 0.5)
    
    # Amplify deviation for visibility (scale by 4)
    enhanced = np.clip(deviation * 4.0, 0, 1)
    
    # Convert to uint8 for display
    enhanced_uint8 = (enhanced * 255).astype(np.uint8)
    
    return enhanced_uint8


def analyze_lsb_randomness(lsb_plane: np.ndarray) -> Dict[str, float]:
    """
    Analyze randomness of LSB plane.
    
    Metrics:
    1. Bit balance: ratio of 1s to 0s (should be ≈ 1.0 for random)
    2. Run length: average consecutive same-bit count (lower = more random)
    3. Entropy: information entropy (higher = more random, max = 1.0)
    
    Args:
        lsb_plane: LSB plane array (H, W, 3) uint8 with values 0 or 255
    
    Returns:
        Dictionary with randomness metrics per channel:
        {
            'R_balance': float (0.9-1.1 = good, far from 1.0 = suspicious),
            'G_balance': float,
            'B_balance': float,
            'R_entropy': float (0.9-1.0 = random, < 0.8 = suspicious),
            'G_entropy': float,
            'B_entropy': float,
            'overall_balance': float,
            'overall_entropy': float
        }
    """
    metrics = {}
    
    # Convert to binary (0 or 1)
    lsb_binary = (lsb_plane // 255).astype(np.uint8)
    
    all_balance = []
    all_entropy = []
    
    for i, channel in enumerate(['R', 'G', 'B']):
        channel_data = lsb_binary[:, :, i].flatten()
        
        # Bit balance: ratio of 1s to 0s
        ones = np.sum(channel_data == 1)
        zeros = np.sum(channel_data == 0)
        
        if zeros > 0:
            balance = ones / zeros
        else:
            balance = float('inf') if ones > 0 else 1.0
        
        metrics[f'{channel}_balance'] = float(balance)
        all_balance.append(balance if balance != float('inf') else 10.0)
        
        # Entropy calculation
        # For binary: entropy = -p*log2(p) - (1-p)*log2(1-p)
        # Max entropy = 1.0 when p = 0.5 (perfectly random)
        total = len(channel_data)
        p_one = ones / total if total > 0 else 0.5
        p_zero = zeros / total if total > 0 else 0.5
        
        # Avoid log(0)
        if p_one == 0 or p_one == 1:
            entropy = 0.0
        else:
            entropy = -(p_one * np.log2(p_one) + p_zero * np.log2(p_zero))
        
        metrics[f'{channel}_entropy'] = float(entropy)
        all_entropy.append(entropy)
    
    # Overall metrics
    metrics['overall_balance'] = float(np.mean(all_balance))
    metrics['overall_entropy'] = float(np.mean(all_entropy))
    
    return metrics


def compare_lsb_planes(
    cover_lsb: np.ndarray,
    stego_lsb: np.ndarray
) -> Dict[str, float]:
    """
    Compare LSB planes of cover and stego images.
    
    Metrics:
    1. Difference ratio: percentage of bits that changed
    2. Spatial correlation: how spatially correlated are changes
    
    Args:
        cover_lsb: Cover LSB plane (H, W, 3) uint8
        stego_lsb: Stego LSB plane (H, W, 3) uint8
    
    Returns:
        Dictionary with comparison metrics:
        {
            'R_diff_ratio': float (0-1, higher = more changes),
            'G_diff_ratio': float,
            'B_diff_ratio': float,
            'overall_diff_ratio': float
        }
    
    Raises:
        ValueError: If LSB planes have different shapes
    """
    if cover_lsb.shape != stego_lsb.shape:
        raise ValueError(
            f"Cover and stego LSB planes must have same shape, "
            f"got {cover_lsb.shape} vs {stego_lsb.shape}"
        )
    
    metrics = {}
    
    # Convert to binary
    cover_bin = (cover_lsb // 255).astype(np.uint8)
    stego_bin = (stego_lsb // 255).astype(np.uint8)
    
    all_diff_ratios = []
    
    for i, channel in enumerate(['R', 'G', 'B']):
        cover_ch = cover_bin[:, :, i].flatten()
        stego_ch = stego_bin[:, :, i].flatten()
        
        # Count different bits
        differences = np.sum(cover_ch != stego_ch)
        total = len(cover_ch)
        
        diff_ratio = differences / total if total > 0 else 0.0
        
        metrics[f'{channel}_diff_ratio'] = float(diff_ratio)
        all_diff_ratios.append(diff_ratio)
    
    metrics['overall_diff_ratio'] = float(np.mean(all_diff_ratios))
    
    return metrics


def create_lsb_difference_visual(
    cover: np.ndarray,
    stego: np.ndarray
) -> np.ndarray:
    """
    Create visualization showing which LSB bits changed.
    
    Useful for visualizing the spatial distribution of embedded data.
    
    Args:
        cover: Cover image (H, W, 3) uint8
        stego: Stego image (H, W, 3) uint8
    
    Returns:
        Difference visualization (H, W, 3) uint8
        White pixels = LSB changed, Black pixels = LSB unchanged
    
    Raises:
        ValueError: If images have different shapes
    """
    if cover.shape != stego.shape:
        raise ValueError(
            f"Cover and stego must have same shape, "
            f"got {cover.shape} vs {stego.shape}"
        )
    
    # Extract LSB planes
    cover_lsb = extract_lsb_plane(cover)
    stego_lsb = extract_lsb_plane(stego)
    
    # Find differences
    diff = (cover_lsb != stego_lsb).astype(np.uint8) * 255
    
    return diff


def analyze_bit_plane_complexity(bit_plane: np.ndarray) -> Dict[str, float]:
    """
    Analyze visual complexity of a bit plane.
    
    Complexity metrics:
    1. Edge density: count of horizontal/vertical transitions
    2. Uniformity: standard deviation (lower = more uniform = suspicious)
    
    Args:
        bit_plane: Bit plane array (H, W, 3) uint8
    
    Returns:
        Dictionary with complexity metrics per channel:
        {
            'R_edge_density': float,
            'G_edge_density': float,
            'B_edge_density': float,
            'R_uniformity': float,
            'G_uniformity': float,
            'B_uniformity': float
        }
    """
    metrics = {}
    
    # Convert to binary
    binary = (bit_plane // 255).astype(np.uint8)
    
    for i, channel in enumerate(['R', 'G', 'B']):
        ch = binary[:, :, i]
        
        # Edge density: count horizontal + vertical transitions
        h_edges = np.sum(np.abs(np.diff(ch, axis=1)))
        v_edges = np.sum(np.abs(np.diff(ch, axis=0)))
        total_possible = ch.shape[0] * (ch.shape[1] - 1) + ch.shape[1] * (ch.shape[0] - 1)
        
        edge_density = (h_edges + v_edges) / total_possible if total_possible > 0 else 0.0
        
        # Uniformity: standard deviation
        uniformity = float(np.std(ch))
        
        metrics[f'{channel}_edge_density'] = float(edge_density)
        metrics[f'{channel}_uniformity'] = float(uniformity)
    
    return metrics


# Export public API
__all__ = [
    'extract_bit_plane',
    'extract_lsb_plane',
    'create_enhanced_lsb_visual',
    'analyze_lsb_randomness',
    'compare_lsb_planes',
    'create_lsb_difference_visual',
    'analyze_bit_plane_complexity'
]
