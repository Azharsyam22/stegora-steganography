"""
Stegora Steganography Core Module
"""

from backend.stego.capacity import (
    calculate_raw_capacity,
    calculate_usable_capacity,
    check_payload_capacity,
    format_bytes
)

from backend.stego.container import (
    create_container,
    parse_container,
    calculate_container_size,
    ContainerError
)

from backend.stego.positions import (
    generate_positions,
    generate_seed_from_key,
    verify_determinism,
    verify_uniqueness,
    PositionGeneratorError
)

from backend.stego.lsb import (
    embed_lsb,
    extract_lsb,
    verify_alpha_preservation,
    LSBError
)

__all__ = [
    # Capacity
    'calculate_raw_capacity',
    'calculate_usable_capacity',
    'check_payload_capacity',
    'format_bytes',
    
    # Container
    'create_container',
    'parse_container',
    'calculate_container_size',
    'ContainerError',
    
    # Positions
    'generate_positions',
    'generate_seed_from_key',
    'verify_determinism',
    'verify_uniqueness',
    'PositionGeneratorError',
    
    # LSB
    'embed_lsb',
    'extract_lsb',
    'verify_alpha_preservation',
    'LSBError',
]
