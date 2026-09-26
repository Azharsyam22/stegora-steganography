"""
Stegora Integration Pipeline
High-level pipeline functions with comprehensive error handling
"""
from typing import Dict, Tuple, Optional
from PIL import Image
import secrets

from backend.crypto.pbkdf2 import derive_key
from backend.crypto.aes_gcm import encrypt, decrypt
from backend.stego.container import (
    create_container, 
    parse_container, 
    ContainerError,
    calculate_container_size
)
from backend.stego.positions import generate_positions, PositionGeneratorError
from backend.stego.lsb import embed_lsb, extract_lsb, LSBError
from backend.stego.capacity import check_payload_capacity
from backend.image.metrics import calculate_mse, calculate_psnr


class PipelineError(Exception):
    """Base exception for pipeline operations"""
    pass


class EmbedError(PipelineError):
    """Raised when embedding fails"""
    pass


class ExtractError(PipelineError):
    """Raised when extraction fails"""
    pass


def embed_pipeline(
    cover_image: Image.Image,
    payload_bytes: bytes,
    password: str,
    stego_key: str,
    filename: str = "",
    mime_type: str = "application/octet-stream"
) -> Tuple[Image.Image, Dict]:
    """
    Complete embedding pipeline with error handling
    
    Args:
        cover_image: Cover image (PIL Image)
        payload_bytes: Raw payload bytes
        password: Encryption password
        stego_key: Position generation key
        filename: Optional filename
        mime_type: Optional MIME type
        
    Returns:
        Tuple of (stego_image, metadata_dict)
        
    Raises:
        EmbedError: If any step fails
    """
    try:
        # Validate inputs
        if not password:
            raise EmbedError("Password cannot be empty")
        if not stego_key:
            raise EmbedError("Stego-key cannot be empty")
        if not payload_bytes:
            raise EmbedError("Payload cannot be empty")
        
        width, height = cover_image.size
        
        # 1. Generate salt and IV
        salt = secrets.token_bytes(16)
        
        # 2. Derive encryption key
        try:
            encryption_key = derive_key(password, salt)
        except Exception as e:
            raise EmbedError(f"Key derivation failed: {str(e)}")
        
        # 3. Encrypt payload (generates IV internally)
        try:
            ciphertext, iv = encrypt(payload_bytes, encryption_key, b"")
        except Exception as e:
            raise EmbedError(f"Encryption failed: {str(e)}")
        
        # 4. Create container
        try:
            container = create_container(
                payload=ciphertext,
                salt=salt,
                iv=iv,
                filename=filename,
                mime_type=mime_type
            )
        except ContainerError as e:
            raise EmbedError(f"Container creation failed: {str(e)}")
        
        # 5. Check capacity
        capacity_check = check_payload_capacity(
            width=width,
            height=height,
            payload_size=len(payload_bytes),
            container_overhead=len(container) - len(ciphertext)
        )
        
        if not capacity_check['fits']:
            raise EmbedError(
                f"Payload too large: need {capacity_check['required_bytes']} bytes, "
                f"have {capacity_check['available_bytes']} bytes"
            )
        
        # 6. Generate positions
        num_bits = len(container) * 8
        try:
            positions = generate_positions(width, height, stego_key, num_bits)
        except PositionGeneratorError as e:
            raise EmbedError(f"Position generation failed: {str(e)}")
        
        # 7. Embed LSB
        try:
            stego_image = embed_lsb(cover_image, container, positions)
        except LSBError as e:
            raise EmbedError(f"LSB embedding failed: {str(e)}")
        
        # 8. Calculate metrics
        try:
            mse = calculate_mse(cover_image, stego_image)
            psnr = calculate_psnr(mse)
        except Exception as e:
            # Metrics failure is not critical
            mse = None
            psnr = None
        
        # Return result with metadata
        metadata = {
            'payload_size': len(payload_bytes),
            'encrypted_size': len(ciphertext),
            'container_size': len(container),
            'num_bits': num_bits,
            'capacity_utilization': capacity_check['utilization_percent'],
            'mse': mse,
            'psnr': psnr,
            'filename': filename,
            'mime_type': mime_type
        }
        
        return stego_image, metadata
        
    except EmbedError:
        raise
    except Exception as e:
        raise EmbedError(f"Unexpected error in embed pipeline: {str(e)}")


def extract_pipeline(
    stego_image: Image.Image,
    password: str,
    stego_key: str
) -> Tuple[bytes, Dict]:
    """
    Complete extraction pipeline with error handling
    
    Args:
        stego_image: Stego image (PIL Image)
        password: Decryption password
        stego_key: Position generation key
        
    Returns:
        Tuple of (plaintext_bytes, metadata_dict)
        
    Raises:
        ExtractError: If any step fails
    """
    try:
        # Validate inputs
        if not password:
            raise ExtractError("Password cannot be empty")
        if not stego_key:
            raise ExtractError("Stego-key cannot be empty")
        
        width, height = stego_image.size
        
        # 1. Read header to determine container size
        try:
            # Read fixed header (16 bytes)
            header_positions = generate_positions(width, height, stego_key, 16 * 8)
            header_bytes = extract_lsb(stego_image, header_positions, 16)
            
            # Parse magic and payload length
            import struct
            magic = header_bytes[0:4]
            payload_len = struct.unpack('>I', header_bytes[12:16])[0]
            
            if magic != b'STGR':
                raise ExtractError(
                    f"Invalid magic bytes: {magic}. "
                    "This may not be a Stegora image or wrong stego-key was used."
                )
            
        except PositionGeneratorError as e:
            raise ExtractError(f"Position generation failed: {str(e)}")
        except LSBError as e:
            raise ExtractError(f"LSB extraction failed: {str(e)}")
        
        # 2. Read metadata lengths (next 5 bytes)
        try:
            meta_positions = generate_positions(width, height, stego_key, 21 * 8)
            meta_bytes = extract_lsb(stego_image, meta_positions[16*8:], 5)
            
            import struct
            salt_len, iv_len, filename_len, mime_len = struct.unpack('>B B H B', meta_bytes)
            
        except Exception as e:
            raise ExtractError(f"Failed to read metadata lengths: {str(e)}")
        
        # 3. Calculate total container size
        total_size = 16 + 5 + salt_len + iv_len + filename_len + mime_len + payload_len
        
        # 4. Generate all positions and extract container
        try:
            all_positions = generate_positions(width, height, stego_key, total_size * 8)
            container_bytes = extract_lsb(stego_image, all_positions, total_size)
        except PositionGeneratorError as e:
            raise ExtractError(f"Position generation failed: {str(e)}")
        except LSBError as e:
            raise ExtractError(f"LSB extraction failed: {str(e)}")
        
        # 5. Parse container
        try:
            container_data = parse_container(container_bytes)
        except ContainerError as e:
            raise ExtractError(f"Container parsing failed: {str(e)}")
        
        # 6. Derive decryption key
        try:
            decryption_key = derive_key(password, container_data['salt'])
        except Exception as e:
            raise ExtractError(f"Key derivation failed: {str(e)}")
        
        # 7. Decrypt payload
        try:
            plaintext = decrypt(
                ciphertext=container_data['payload'],
                key=decryption_key,
                iv=container_data['iv'],
                associated_data=b""
            )
        except ValueError as e:
            raise ExtractError(
                f"Decryption failed: {str(e)}. "
                "This usually means wrong password or corrupted data."
            )
        except Exception as e:
            raise ExtractError(f"Decryption error: {str(e)}")
        
        # Return result with metadata
        metadata = {
            'plaintext_size': len(plaintext),
            'encrypted_size': len(container_data['payload']),
            'container_size': len(container_bytes),
            'filename': container_data['filename'],
            'mime_type': container_data['mime_type'],
            'magic_valid': True,
            'auth_valid': True,
            'integrity': 'OK'
        }
        
        return plaintext, metadata
        
    except ExtractError:
        raise
    except Exception as e:
        raise ExtractError(f"Unexpected error in extract pipeline: {str(e)}")


def validate_credentials(password: str, stego_key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate credentials before processing
    
    Args:
        password: Password to validate
        stego_key: Stego-key to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password should be at least 8 characters for security"
    
    if not stego_key:
        return False, "Stego-key is required"
    
    if len(stego_key) < 8:
        return False, "Stego-key should be at least 8 characters for security"
    
    return True, None
