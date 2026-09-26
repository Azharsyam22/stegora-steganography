"""
Tests for image I/O and validation
"""
import pytest
from PIL import Image
import io
from stegora.image.io import (
    validate_image_format,
    validate_image_mode,
    load_image,
    get_image_metadata,
    validate_and_load_cover_image,
    ImageValidationError
)


def create_test_image(width=100, height=100, mode='RGB', format='PNG'):
    """Helper to create test image in memory"""
    img = Image.new(mode, (width, height), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    # Set format attribute
    img.format = format
    return img, buffer.getvalue()


class TestImageValidation:
    """Test image format and mode validation"""
    
    def test_validate_png_format(self):
        """PNG format should be valid"""
        img, _ = create_test_image(format='PNG')
        validate_image_format(img)  # Should not raise
    
    def test_validate_bmp_format(self):
        """BMP format should be valid"""
        img, _ = create_test_image(format='BMP')
        validate_image_format(img)  # Should not raise
    
    def test_reject_unsupported_format(self):
        """JPEG and other formats should be rejected"""
        img = Image.new('RGB', (100, 100))
        img.format = 'JPEG'
        
        with pytest.raises(ImageValidationError) as exc_info:
            validate_image_format(img)
        
        assert 'Unsupported format' in str(exc_info.value)
        assert 'JPEG' in str(exc_info.value)
    
    def test_validate_rgb_mode(self):
        """RGB mode should be valid"""
        img, _ = create_test_image(mode='RGB')
        validate_image_mode(img)  # Should not raise
    
    def test_validate_rgba_mode(self):
        """RGBA mode should be valid"""
        img, _ = create_test_image(mode='RGBA')
        validate_image_mode(img)  # Should not raise
    
    def test_reject_grayscale_mode(self):
        """Grayscale mode should be rejected"""
        img = Image.new('L', (100, 100))
        
        with pytest.raises(ImageValidationError) as exc_info:
            validate_image_mode(img)
        
        assert 'Unsupported mode' in str(exc_info.value)
        assert 'L' in str(exc_info.value)
    
    def test_reject_palette_mode(self):
        """Palette mode should be rejected"""
        img = Image.new('P', (100, 100))
        
        with pytest.raises(ImageValidationError) as exc_info:
            validate_image_mode(img)
        
        assert 'Unsupported mode' in str(exc_info.value)


class TestImageLoading:
    """Test image loading from bytes"""
    
    def test_load_image_from_bytes(self):
        """Should load image from bytes"""
        _, img_bytes = create_test_image(width=200, height=150)
        
        img = load_image(img_bytes)
        
        assert img.size == (200, 150)
        assert img.mode == 'RGB'
    
    def test_load_image_invalid_bytes(self):
        """Should raise error for invalid image bytes"""
        invalid_bytes = b'not an image'
        
        with pytest.raises(ImageValidationError) as exc_info:
            load_image(invalid_bytes)
        
        assert 'Failed to load image' in str(exc_info.value)


class TestImageMetadata:
    """Test metadata extraction"""
    
    def test_metadata_rgb_image(self):
        """Should extract correct metadata for RGB image"""
        img, _ = create_test_image(width=640, height=480, mode='RGB', format='PNG')
        
        metadata = get_image_metadata(img)
        
        assert metadata['format'] == 'PNG'
        assert metadata['mode'] == 'RGB'
        assert metadata['width'] == 640
        assert metadata['height'] == 480
        assert metadata['channels'] == 3
        assert metadata['has_alpha'] is False
        assert metadata['total_pixels'] == 640 * 480
    
    def test_metadata_rgba_image(self):
        """Should extract correct metadata for RGBA image"""
        img, _ = create_test_image(width=800, height=600, mode='RGBA', format='PNG')
        
        metadata = get_image_metadata(img)
        
        assert metadata['mode'] == 'RGBA'
        assert metadata['channels'] == 4
        assert metadata['has_alpha'] is True
        assert metadata['total_pixels'] == 800 * 600


class TestCompleteValidation:
    """Test complete validation pipeline"""
    
    def test_validate_and_load_valid_png(self):
        """Should validate and load valid PNG"""
        _, img_bytes = create_test_image(width=300, height=200, mode='RGB', format='PNG')
        
        img, metadata = validate_and_load_cover_image(img_bytes)
        
        assert img.size == (300, 200)
        assert metadata['format'] == 'PNG'
        assert metadata['mode'] == 'RGB'
        assert metadata['width'] == 300
        assert metadata['height'] == 200
    
    def test_validate_and_load_valid_bmp(self):
        """Should validate and load valid BMP"""
        _, img_bytes = create_test_image(width=400, height=300, mode='RGB', format='BMP')
        
        img, metadata = validate_and_load_cover_image(img_bytes)
        
        assert img.size == (400, 300)
        assert metadata['format'] == 'BMP'
    
    def test_validate_and_load_rgba_png(self):
        """Should validate and load RGBA PNG"""
        _, img_bytes = create_test_image(width=256, height=256, mode='RGBA', format='PNG')
        
        img, metadata = validate_and_load_cover_image(img_bytes)
        
        assert metadata['mode'] == 'RGBA'
        assert metadata['has_alpha'] is True
    
    def test_reject_invalid_format_in_pipeline(self):
        """Should reject invalid format in complete pipeline"""
        # Create JPEG
        img = Image.new('RGB', (100, 100))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        with pytest.raises(ImageValidationError):
            validate_and_load_cover_image(buffer.getvalue())
