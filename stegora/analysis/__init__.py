"""
Stegora Analysis Module

Provides histogram analysis, LSB plane visualization, robustness testing,
and testing matrix with XLSX export.
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

from .testing_matrix import (
    TestCase,
    TestingMatrix,
    create_test_payloads,
    create_test_images
)

from .xlsx_export import (
    XLSXExporter,
    export_matrix_to_xlsx,
    OPENPYXL_AVAILABLE
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
    'test_stego_resilience',
    
    # Testing matrix
    'TestCase',
    'TestingMatrix',
    'create_test_payloads',
    'create_test_images',
    
    # XLSX export
    'XLSXExporter',
    'export_matrix_to_xlsx',
    'OPENPYXL_AVAILABLE'
]
