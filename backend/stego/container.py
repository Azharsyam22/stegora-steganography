"""
STGR Binary Container
Encode/decode payload into framed binary container with header and metadata

TODO: This is a STUB for T08 (Naufal)
Implementation needed for actual container serialization
"""
from typing import Dict, Tuple, Optional
import struct


class ContainerError(Exception):
    """Raised when container operations fail"""
    pass


# Container constants
MAGIC = b'STGR'
VERSION = 1
CONTAINER_OVERHEAD = 64  # Estimated overhead in bytes


def create_container(
    payload: bytes,
    salt: bytes,
    iv: bytes,
    filename: str = "",
    mime_type: str = "application/octet-stream"
) -> bytes:
    """
    Create STGR binary container with header and metadata
    
    Container format:
    - MAGIC: 4 bytes 'STGR'
    - VERSION: 1 byte
    - FLAGS: 1 byte
    - PAYLOAD_TYPE: 1 byte
    - RESERVED: 1 byte
    - PAYLOAD_LEN: 4 bytes (big-endian)
    - SALT_LEN: 1 byte
    - IV_LEN: 1 byte
    - FILENAME_LEN: 2 bytes (big-endian)
    - MIME_LEN: 1 byte
    - SALT: variable
    - IV: variable
    - FILENAME: variable (UTF-8)
    - MIME: variable (ASCII)
    - PAYLOAD: variable (encrypted data)
    
    Args:
        payload: Encrypted payload bytes (AES-GCM ciphertext + tag)
        salt: PBKDF2 salt
        iv: AES-GCM initialization vector
        filename: Optional original filename
        mime_type: Optional MIME type
        
    Returns:
        Complete framed container bytes
        
    Raises:
        ContainerError: If container creation fails
        
    TODO (T08 - Naufal): Implement actual container serialization
    - Pack header with struct
    - Pack metadata lengths
    - Concatenate all parts
    - Validate total size
    """
    try:
        # Encode strings
        filename_bytes = filename.encode('utf-8')
        mime_bytes = mime_type.encode('ascii')
        
        # Validate lengths
        if len(salt) > 255:
            raise ContainerError("Salt too long (max 255 bytes)")
        if len(iv) > 255:
            raise ContainerError("IV too long (max 255 bytes)")
        if len(filename_bytes) > 65535:
            raise ContainerError("Filename too long (max 65535 bytes)")
        if len(mime_bytes) > 255:
            raise ContainerError("MIME type too long (max 255 bytes)")
        
        # Build header (16 bytes fixed)
        header = struct.pack(
            '>4s B B B B I',
            MAGIC,              # 4 bytes: magic
            VERSION,            # 1 byte: version
            0,                  # 1 byte: flags
            0,                  # 1 byte: payload type
            0,                  # 1 byte: reserved
            len(payload)        # 4 bytes: payload length
        )
        
        # Build metadata lengths (5 bytes)
        meta_lengths = struct.pack(
            '>B B H B',
            len(salt),          # 1 byte: salt length
            len(iv),            # 1 byte: iv length
            len(filename_bytes),# 2 bytes: filename length
            len(mime_bytes)     # 1 byte: mime length
        )
        
        # Concatenate all parts
        container = (
            header +
            meta_lengths +
            salt +
            iv +
            filename_bytes +
            mime_bytes +
            payload
        )
        
        return container
        
    except Exception as e:
        raise ContainerError(f"Failed to create container: {str(e)}")


def parse_container(container: bytes) -> Dict[str, any]:
    """
    Parse STGR container and extract all components
    
    Args:
        container: Complete container bytes
        
    Returns:
        Dictionary containing:
        - magic: Magic bytes
        - version: Version number
        - flags: Flag bits
        - payload_type: Payload type code
        - salt: PBKDF2 salt
        - iv: AES-GCM IV
        - filename: Original filename
        - mime_type: MIME type
        - payload: Encrypted payload
        
    Raises:
        ContainerError: If parsing fails or validation fails
        
    TODO (T08 - Naufal): Implement actual container parsing
    - Validate minimum size
    - Unpack header
    - Validate magic and version
    - Unpack metadata
    - Extract all fields
    - Validate consistency
    """
    try:
        # Minimum container size: 16 (header) + 5 (meta lengths)
        if len(container) < 21:
            raise ContainerError("Container too short")
        
        # Parse header (16 bytes)
        magic, version, flags, payload_type, reserved, payload_len = struct.unpack(
            '>4s B B B B I',
            container[0:16]
        )
        
        # Validate magic
        if magic != MAGIC:
            raise ContainerError(f"Invalid magic: expected {MAGIC}, got {magic}")
        
        # Validate version
        if version != VERSION:
            raise ContainerError(f"Unsupported version: {version}")
        
        # Parse metadata lengths (5 bytes)
        salt_len, iv_len, filename_len, mime_len = struct.unpack(
            '>B B H B',
            container[16:21]
        )
        
        # Calculate offsets
        offset = 21
        salt_offset = offset
        iv_offset = salt_offset + salt_len
        filename_offset = iv_offset + iv_len
        mime_offset = filename_offset + filename_len
        payload_offset = mime_offset + mime_len
        
        # Validate total length
        expected_len = payload_offset + payload_len
        if len(container) < expected_len:
            raise ContainerError(f"Container truncated: expected {expected_len}, got {len(container)}")
        
        # Extract components
        salt = container[salt_offset:iv_offset]
        iv = container[iv_offset:filename_offset]
        filename_bytes = container[filename_offset:mime_offset]
        mime_bytes = container[mime_offset:payload_offset]
        payload = container[payload_offset:payload_offset + payload_len]
        
        # Decode strings
        filename = filename_bytes.decode('utf-8')
        mime_type = mime_bytes.decode('ascii')
        
        return {
            'magic': magic,
            'version': version,
            'flags': flags,
            'payload_type': payload_type,
            'salt': salt,
            'iv': iv,
            'filename': filename,
            'mime_type': mime_type,
            'payload': payload
        }
        
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
    Calculate total container size for given payload
    
    Args:
        payload_size: Encrypted payload size in bytes
        salt_len: Salt length (default 16)
        iv_len: IV length (default 12)
        filename_len: Filename length in bytes (default 0)
        mime_len: MIME type length (default 24 for "application/octet-stream")
        
    Returns:
        Total container size in bytes
    """
    header_size = 16  # Fixed header
    meta_lengths_size = 5  # Metadata length fields
    
    return (
        header_size +
        meta_lengths_size +
        salt_len +
        iv_len +
        filename_len +
        mime_len +
        payload_size
    )
