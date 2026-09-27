"""
STGR Binary Container
Encode/decode payload into framed binary container with fixed header and metadata.

Author: Naufal (247006111158)
Task: T08 - STGR Binary Container
"""
from typing import Dict, Tuple, Optional
import struct


class ContainerError(Exception):
    """Raised when container operations fail (parsing, serialization, validation)."""
    pass


# Container specification constants (STEGO_SPEC.md)
MAGIC = b'STGR'
VERSION = 1

# Header formats:
# Fixed Header (12 bytes):
# - MAGIC: 4 bytes 'STGR'
# - VERSION: 1 byte uint8
# - FLAGS: 1 byte uint8
# - PAYLOAD_TYPE: 1 byte uint8 (0=text, 1=file)
# - RESERVED: 1 byte uint8
# - PAYLOAD_LEN: 4 bytes big-endian uint32
HEADER_FORMAT = '>4s B B B B I'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 12 bytes

# Metadata Lengths Format (5 bytes):
# - SALT_LEN: 1 byte uint8
# - IV_LEN: 1 byte uint8
# - FILENAME_LEN: 2 bytes big-endian uint16
# - MIME_LEN: 1 byte uint8
META_LENGTHS_FORMAT = '>B B H B'
META_LENGTHS_SIZE = struct.calcsize(META_LENGTHS_FORMAT)  # 5 bytes

MIN_CONTAINER_SIZE = HEADER_SIZE + META_LENGTHS_SIZE  # 17 bytes
CONTAINER_OVERHEAD = 64  # Estimated baseline overhead


def parse_header(header_bytes: bytes) -> Dict[str, any]:
    """
    Parse and validate fixed 12-byte STGR header.
    
    Args:
        header_bytes: Raw bytes containing at least 12 bytes
        
    Returns:
        Dictionary containing magic, version, flags, payload_type, reserved, payload_len
        
    Raises:
        ContainerError: If header is too short, magic is invalid, or version is unsupported
    """
    if len(header_bytes) < HEADER_SIZE:
        raise ContainerError(
            f"Header too short: expected at least {HEADER_SIZE} bytes, got {len(header_bytes)}"
        )
    
    magic, version, flags, payload_type, reserved, payload_len = struct.unpack(
        HEADER_FORMAT,
        header_bytes[:HEADER_SIZE]
    )
    
    if magic != MAGIC:
        raise ContainerError(
            f"Invalid magic bytes: {magic}. Expected {MAGIC}. "
            "This may not be a Stegora image or the wrong stego-key was used."
        )
    
    if version != VERSION:
        raise ContainerError(
            f"Unsupported container version: {version}. Expected version {VERSION}."
        )
    
    return {
        'magic': magic,
        'version': version,
        'flags': flags,
        'payload_type': payload_type,
        'reserved': reserved,
        'payload_len': payload_len,
    }


def parse_metadata_lengths(meta_bytes: bytes) -> Tuple[int, int, int, int]:
    """
    Parse 5-byte metadata lengths field.
    
    Args:
        meta_bytes: Raw bytes containing at least 5 bytes
        
    Returns:
        Tuple of (salt_len, iv_len, filename_len, mime_len)
        
    Raises:
        ContainerError: If metadata lengths field is too short
    """
    if len(meta_bytes) < META_LENGTHS_SIZE:
        raise ContainerError(
            f"Metadata lengths field too short: expected at least {META_LENGTHS_SIZE} bytes, got {len(meta_bytes)}"
        )
    
    salt_len, iv_len, filename_len, mime_len = struct.unpack(
        META_LENGTHS_FORMAT,
        meta_bytes[:META_LENGTHS_SIZE]
    )
    return salt_len, iv_len, filename_len, mime_len


def create_container(
    payload: bytes,
    salt: bytes,
    iv: bytes,
    filename: str = "",
    mime_type: str = "application/octet-stream",
    flags: int = 0,
    payload_type: int = 0
) -> bytes:
    """
    Create STGR binary container with fixed header, metadata lengths, metadata, and payload.
    
    Container layout:
    - Fixed Header (12 bytes):
        - MAGIC: 4 bytes ('STGR')
        - VERSION: 1 byte
        - FLAGS: 1 byte
        - PAYLOAD_TYPE: 1 byte
        - RESERVED: 1 byte
        - PAYLOAD_LEN: 4 bytes (big-endian uint32)
    - Metadata Lengths (5 bytes):
        - SALT_LEN: 1 byte
        - IV_LEN: 1 byte
        - FILENAME_LEN: 2 bytes (big-endian uint16)
        - MIME_LEN: 1 byte
    - Variable Data:
        - SALT: salt_len bytes
        - IV: iv_len bytes
        - FILENAME: filename_len bytes (UTF-8)
        - MIME: mime_len bytes (ASCII)
        - PAYLOAD: payload_len bytes (AES-GCM ciphertext + tag)
        
    Args:
        payload: Encrypted payload bytes (AES-GCM ciphertext + tag)
        salt: PBKDF2 salt (bytes)
        iv: AES-GCM initialization vector (bytes)
        filename: Optional original filename (string)
        mime_type: Optional MIME type (string)
        flags: Optional container flags bitfield (default 0)
        payload_type: Payload type code (0=text, 1=file, default 0)
        
    Returns:
        Complete framed container bytes
        
    Raises:
        ContainerError: If container creation or input validation fails
    """
    try:
        if not isinstance(payload, (bytes, bytearray)):
            raise ContainerError(f"Payload must be bytes, got {type(payload)}")
        if not isinstance(salt, (bytes, bytearray)):
            raise ContainerError(f"Salt must be bytes, got {type(salt)}")
        if not isinstance(iv, (bytes, bytearray)):
            raise ContainerError(f"IV must be bytes, got {type(iv)}")
        
        # Encode strings
        try:
            filename_bytes = filename.encode('utf-8') if filename else b""
        except UnicodeEncodeError as e:
            raise ContainerError(f"Invalid filename encoding (must be UTF-8): {e}")
        
        try:
            mime_bytes = mime_type.encode('ascii') if mime_type else b""
        except UnicodeEncodeError as e:
            raise ContainerError(f"Invalid MIME type encoding (must be ASCII): {e}")
        
        # Validate lengths against maximum field limits
        if len(salt) > 255:
            raise ContainerError(f"Salt too long: max 255 bytes, got {len(salt)}")
        if len(iv) > 255:
            raise ContainerError(f"IV too long: max 255 bytes, got {len(iv)}")
        if len(filename_bytes) > 65535:
            raise ContainerError(f"Filename too long: max 65535 bytes, got {len(filename_bytes)}")
        if len(mime_bytes) > 255:
            raise ContainerError(f"MIME type too long: max 255 bytes, got {len(mime_bytes)}")
        if len(payload) > 0xFFFFFFFF:
            raise ContainerError(f"Payload too large: max 4GB, got {len(payload)}")
        
        # 1. Build fixed header (12 bytes)
        header = struct.pack(
            HEADER_FORMAT,
            MAGIC,
            VERSION,
            flags & 0xFF,
            payload_type & 0xFF,
            0,  # reserved
            len(payload)
        )
        
        # 2. Build metadata lengths (5 bytes)
        meta_lengths = struct.pack(
            META_LENGTHS_FORMAT,
            len(salt),
            len(iv),
            len(filename_bytes),
            len(mime_bytes)
        )
        
        # 3. Concatenate all parts
        container = (
            header +
            meta_lengths +
            bytes(salt) +
            bytes(iv) +
            filename_bytes +
            mime_bytes +
            bytes(payload)
        )
        
        return container
        
    except ContainerError:
        raise
    except Exception as e:
        raise ContainerError(f"Failed to create container: {str(e)}")


def parse_container(container: bytes) -> Dict[str, any]:
    """
    Parse STGR container and extract all header, metadata, and payload components.
    
    Args:
        container: Complete container bytes
        
    Returns:
        Dictionary containing:
        - magic: bytes (b'STGR')
        - version: int
        - flags: int
        - payload_type: int
        - reserved: int
        - payload_len: int
        - salt: bytes
        - iv: bytes
        - filename: str
        - mime_type: str
        - payload: bytes
        
    Raises:
        ContainerError: If container is truncated, malformed, or has invalid magic/version
    """
    try:
        if not isinstance(container, (bytes, bytearray)):
            raise ContainerError(f"Container must be bytes, got {type(container)}")
        
        # Minimum container size: 12 (header) + 5 (meta lengths) = 17 bytes
        if len(container) < MIN_CONTAINER_SIZE:
            raise ContainerError(
                f"Container too short: expected at least {MIN_CONTAINER_SIZE} bytes, got {len(container)}"
            )
        
        # 1. Parse fixed header (12 bytes)
        header_info = parse_header(container[:HEADER_SIZE])
        payload_len = header_info['payload_len']
        
        # 2. Parse metadata lengths (5 bytes)
        salt_len, iv_len, filename_len, mime_len = parse_metadata_lengths(
            container[HEADER_SIZE:HEADER_SIZE + META_LENGTHS_SIZE]
        )
        
        # 3. Calculate component offsets
        offset = HEADER_SIZE + META_LENGTHS_SIZE  # 17
        salt_offset = offset
        iv_offset = salt_offset + salt_len
        filename_offset = iv_offset + iv_len
        mime_offset = filename_offset + filename_len
        payload_offset = mime_offset + mime_len
        expected_total_len = payload_offset + payload_len
        
        # 4. Validate total length
        if len(container) < expected_total_len:
            raise ContainerError(
                f"Container truncated: expected at least {expected_total_len} bytes, got {len(container)}"
            )
        
        # 5. Extract components
        salt = container[salt_offset:iv_offset]
        iv = container[iv_offset:filename_offset]
        filename_bytes = container[filename_offset:mime_offset]
        mime_bytes = container[mime_offset:payload_offset]
        payload = container[payload_offset:payload_offset + payload_len]
        
        # 6. Decode strings
        try:
            filename = filename_bytes.decode('utf-8')
        except UnicodeDecodeError:
            filename = filename_bytes.decode('utf-8', errors='replace')
        
        try:
            mime_type = mime_bytes.decode('ascii')
        except UnicodeDecodeError:
            mime_type = mime_bytes.decode('ascii', errors='replace')
        
        return {
            'magic': header_info['magic'],
            'version': header_info['version'],
            'flags': header_info['flags'],
            'payload_type': header_info['payload_type'],
            'reserved': header_info['reserved'],
            'payload_len': payload_len,
            'salt': bytes(salt),
            'iv': bytes(iv),
            'filename': filename,
            'mime_type': mime_type,
            'payload': bytes(payload)
        }
        
    except ContainerError:
        raise
    except Exception as e:
        raise ContainerError(f"Failed to parse container: {str(e)}")


def calculate_container_size(
    payload_size: int,
    salt_len: int = 16,
    iv_len: int = 12,
    filename_len: int = 0,
    mime_len: int = 24
) -> int:
    """
    Calculate total container size for given payload and metadata lengths.
    
    Args:
        payload_size: Encrypted payload size in bytes
        salt_len: Salt length (default 16)
        iv_len: IV length (default 12)
        filename_len: Filename length in bytes (default 0)
        mime_len: MIME type length (default 24 for "application/octet-stream")
        
    Returns:
        Total container size in bytes
    """
    return (
        HEADER_SIZE +
        META_LENGTHS_SIZE +
        salt_len +
        iv_len +
        filename_len +
        mime_len +
        payload_size
    )

