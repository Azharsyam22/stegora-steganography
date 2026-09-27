"""
Stegora Analysis Module

Provides histogram analysis and LSB plane visualization for steganalysis.
"""

from .histogram import (
    calculate_histogram,
    calculate_histogram_from_pil,
    compare_histograms,
    analyze_lsb_histogram_pairs,
    calculate_histogram_difference_image
)

from .lsb_plane import (
    extract_bit_plane,
    extract_lsb_plane,
    create_enhanced_lsb_visual,
    analyze_lsb_randomness,
    compare_lsb_planes,
    create_lsb_difference_visual,
    analyze_bit_plane_complexity
)

__all__ = [
    # Histogram analysis
    'calculate_histogram',
    'calculate_histogram_from_pil',
    'compare_histograms',
    'analyze_lsb_histogram_pairs',
    'calculate_histogram_difference_image',
    
    # LSB plane analysis
    'extract_bit_plane',
    'extract_lsb_plane',
    'create_enhanced_lsb_visual',
    'analyze_lsb_randomness',
    'compare_lsb_planes',
    'create_lsb_difference_visual',
    'analyze_bit_plane_complexity'
]
