"""
Keyed Deterministic Position Generator
Generate reproducible pixel/channel positions from stego-key

TODO: This is a STUB for T09 (Naufal)
Implementation needed for actual PRNG-based position generation
"""
from typing import List, Tuple
import hashlib
import random


class PositionGeneratorError(Exception):
    """Raised when position generation fails"""
    pass


def generate_seed_from_key(stego_key: str) -> int:
    """
    Generate deterministic seed from stego-key using SHA-256
    
    Args:
        stego_key: User-provided stego-key string
        
    Returns:
        Integer seed for PRNG
        
    TODO (T09 - Naufal): Verify this matches design spec
    """
    if not stego_key:
        raise PositionGeneratorError("Stego-key cannot be empty")
    
    # Hash the key with SHA-256
    key_bytes = stego_key.encode('utf-8')
    hash_digest = hashlib.sha256(key_bytes).digest()
    
    # Convert first 8 bytes to integer seed
    seed = int.from_bytes(hash_digest[:8], byteorder='big')
    
    return seed


def generate_positions(
    width: int,
    height: int,
    stego_key: str,
    num_bits: int
) -> List[Tuple[int, int, int]]:
    """
    Generate deterministic list of (x, y, channel) positions for embedding
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        stego_key: User-provided stego-key for seeding
        num_bits: Number of bit positions needed
        
    Returns:
        List of tuples (x, y, channel) where:
        - x: pixel x-coordinate (0 to width-1)
        - y: pixel y-coordinate (0 to height-1)
        - channel: RGB channel index (0=R, 1=G, 2=B)
        
    Raises:
        PositionGeneratorError: If not enough positions available
        
    TODO (T09 - Naufal): Implement actual deterministic PRNG algorithm
    - Generate seed from stego-key (SHA-256)
    - Initialize PRNG with seed
    - Generate unique positions without replacement
    - Ensure determinism (same key = same sequence)
    - Ensure different keys produce different sequences
    - Never use alpha channel (preserve alpha)
    """
    # Validate inputs
    if width <= 0 or height <= 0:
        raise PositionGeneratorError("Invalid image dimensions")
    
    if not stego_key:
        raise PositionGeneratorError("Stego-key is required")
    
    # Calculate maximum available positions (RGB only, 3 channels per pixel)
    max_positions = width * height * 3
    
    if num_bits > max_positions:
        raise PositionGeneratorError(
            f"Not enough positions: need {num_bits}, have {max_positions}"
        )
    
    # Generate seed
    seed = generate_seed_from_key(stego_key)
    
    # Initialize PRNG with seed for deterministic output
    rng = random.Random(seed)
    
    # Generate all possible positions
    all_positions = []
    for y in range(height):
        for x in range(width):
            for channel in range(3):  # RGB only, no alpha
                all_positions.append((x, y, channel))
    
    # Shuffle with seeded PRNG for determinism
    rng.shuffle(all_positions)
    
    # Return first num_bits positions
    return all_positions[:num_bits]


def verify_determinism(
    width: int,
    height: int,
    stego_key: str,
    num_bits: int,
    iterations: int = 10
) -> bool:
    """
    Verify that position generation is deterministic
    
    Args:
        width: Image width
        height: Image height
        stego_key: Stego-key
        num_bits: Number of positions
        iterations: Number of times to regenerate and compare
        
    Returns:
        True if all iterations produce identical sequences
        
    TODO (T09 - Naufal): Use this for testing determinism
    """
    first_run = generate_positions(width, height, stego_key, num_bits)
    
    for _ in range(iterations - 1):
        current_run = generate_positions(width, height, stego_key, num_bits)
        if current_run != first_run:
            return False
    
    return True


def verify_uniqueness(positions: List[Tuple[int, int, int]]) -> bool:
    """
    Verify that all positions in the list are unique
    
    Args:
        positions: List of (x, y, channel) tuples
        
    Returns:
        True if all positions are unique
    """
    return len(positions) == len(set(positions))
