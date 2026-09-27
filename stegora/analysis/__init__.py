"""
Stegora Analysis Module

Provides histogram analysis, LSB plane visualization, and robustness testing.
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

from .robustness import (
    test_jpeg_compression,
    test_jpeg_multiple_qualities,
    calculate_bit_error_rate,
    simulate_bit_flip_attack,
    simulate_truncation_attack,
    create_malformed_header,
    test_stego_resilience
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
    'analyze_bit_plane_complexity',
    
    # Robustness testing
    'test_jpeg_compression',
    'test_jpeg_multiple_qualities',
    'calculate_bit_error_rate',
    'simulate_bit_flip_attack',
    'simulate_truncation_attack',
    'create_malformed_header',
    'test_stego_resilience'
]
