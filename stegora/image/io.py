"""
Image I/O and Validation
Use Pillow for loading and format validation only
"""
from pathlib import Path
from typing import Dict, Tuple, Optional
from PIL import Image
import io


class ImageValidationError(Exception):
    """Raised when image validation fails"""
    pass


def validate_image_format(image: Image.Image) -> None:
    """
    Validate that image format is PNG or BMP
    
    Args:
        image: PIL Image object
        
    Raises:
        ImageValidationError: If format is not supported
    """
    if image.format not in ('PNG', 'BMP'):
        raise ImageValidationError(
            f"Unsupported format '{image.format}'. Only PNG and BMP are supported."
        )


def validate_image_mode(image: Image.Image) -> None:
    """
    Validate that image has RGB or RGBA mode
    
    Args:
        image: PIL Image object
        
    Raises:
        ImageValidationError: If mode is not supported
    """
    if image.mode not in ('RGB', 'RGBA'):
        raise ImageValidationError(
            f"Unsupported mode '{image.mode}'. Only RGB and RGBA modes are supported."
        )


def load_image(file_path_or_bytes) -> Image.Image:
    """
    Load image from file path or bytes using Pillow
    
    Args:
        file_path_or_bytes: File path string/Path or bytes-like object
        
    Returns:
        PIL Image object
        
    Raises:
        ImageValidationError: If image cannot be loaded
    """
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            image = Image.open(file_path_or_bytes)
        else:
            # Bytes-like object (e.g., from Streamlit uploader)
            image = Image.open(io.BytesIO(file_path_or_bytes))
        
        return image
    except Exception as e:
        raise ImageValidationError(f"Failed to load image: {str(e)}")


def get_image_metadata(image: Image.Image) -> Dict[str, any]:
    """
    Extract image metadata
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary containing:
        - format: Image format (PNG, BMP)
        - mode: Color mode (RGB, RGBA)
        - width: Image width in pixels
        - height: Image height in pixels
        - channels: Number of color channels (3 for RGB, 4 for RGBA)
        - has_alpha: Boolean indicating if alpha channel exists
        - total_pixels: Total pixel count
    """
    width, height = image.size
    has_alpha = image.mode == 'RGBA'
    channels = 4 if has_alpha else 3
    
    return {
        'format': image.format or 'Unknown',
        'mode': image.mode,
        'width': width,
        'height': height,
        'channels': channels,
        'has_alpha': has_alpha,
        'total_pixels': width * height,
    }


def validate_and_load_cover_image(file_path_or_bytes) -> Tuple[Image.Image, Dict[str, any]]:
    """
    Complete validation pipeline for cover image
    
    Args:
        file_path_or_bytes: File path or bytes from uploader
        
    Returns:
        Tuple of (PIL Image, metadata dict)
        
    Raises:
        ImageValidationError: If validation fails at any step
    """
    # Load image
    image = load_image(file_path_or_bytes)
    
    # Validate format
    validate_image_format(image)
    
    # Validate mode
    validate_image_mode(image)
    
    # Extract metadata
    metadata = get_image_metadata(image)
    
    return image, metadata


def save_image(image: Image.Image, output_path: str, format: str = None) -> None:
    """
    Save image using Pillow
    
    Args:
        image: PIL Image object
        output_path: Output file path
        format: Optional format override (PNG, BMP)
    """
    if format is None:
        format = image.format or 'PNG'
    
    image.save(output_path, format=format)
