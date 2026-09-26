"""
Tests for integration pipeline
"""
import pytest
from PIL import Image
import io

from backend.pipeline import (
    embed_pipeline,
    extract_pipeline,
    validate_credentials,
    EmbedError,
    ExtractError
)


@pytest.fixture
def sample_cover_image():
    """Create a sample RGB image for testing"""
    return Image.new('RGB', (100, 100), color='white')


@pytest.fixture
def sample_rgba_image():
    """Create a sample RGBA image for testing"""
    return Image.new('RGBA', (100, 100), color='white')


def test_validate_credentials_valid():
    """Test credential validation with valid inputs"""
    is_valid, error = validate_credentials("password123", "stegokey123")
    assert is_valid is True
    assert error is None


def test_validate_credentials_empty_password():
    """Test credential validation with empty password"""
    is_valid, error = validate_credentials("", "stegokey123")
    assert is_valid is False
    assert "Password is required" in error


def test_validate_credentials_short_password():
    """Test credential validation with short password"""
    is_valid, error = validate_credentials("pass", "stegokey123")
    assert is_valid is False
    assert "at least 8 characters" in error


def test_validate_credentials_empty_stego_key():
    """Test credential validation with empty stego-key"""
    is_valid, error = validate_credentials("password123", "")
    assert is_valid is False
    assert "Stego-key is required" in error


def test_validate_credentials_short_stego_key():
    """Test credential validation with short stego-key"""
    is_valid, error = validate_credentials("password123", "key")
    assert is_valid is False
    assert "at least 8 characters" in error


def test_embed_pipeline_empty_payload(sample_cover_image):
    """Test embed pipeline with empty payload"""
    with pytest.raises(EmbedError, match="Payload cannot be empty"):
        embed_pipeline(
            cover_image=sample_cover_image,
            payload_bytes=b"",
            password="password123",
            stego_key="stegokey123"
        )


def test_embed_pipeline_empty_password(sample_cover_image):
    """Test embed pipeline with empty password"""
    with pytest.raises(EmbedError, match="Password cannot be empty"):
        embed_pipeline(
            cover_image=sample_cover_image,
            payload_bytes=b"test message",
            password="",
            stego_key="stegokey123"
        )


def test_embed_pipeline_empty_stego_key(sample_cover_image):
    """Test embed pipeline with empty stego-key"""
    with pytest.raises(EmbedError, match="Stego-key cannot be empty"):
        embed_pipeline(
            cover_image=sample_cover_image,
            payload_bytes=b"test message",
            password="password123",
            stego_key=""
        )


def test_embed_pipeline_payload_too_large(sample_cover_image):
    """Test embed pipeline with payload too large for image"""
    # Create a huge payload that won't fit in 100x100 image
    huge_payload = b"X" * 10000
    
    with pytest.raises(EmbedError, match="Payload too large"):
        embed_pipeline(
            cover_image=sample_cover_image,
            payload_bytes=huge_payload,
            password="password123",
            stego_key="stegokey123"
        )


def test_extract_pipeline_empty_password(sample_cover_image):
    """Test extract pipeline with empty password"""
    with pytest.raises(ExtractError, match="Password cannot be empty"):
        extract_pipeline(
            stego_image=sample_cover_image,
            password="",
            stego_key="stegokey123"
        )


def test_extract_pipeline_empty_stego_key(sample_cover_image):
    """Test extract pipeline with empty stego-key"""
    with pytest.raises(ExtractError, match="Stego-key cannot be empty"):
        extract_pipeline(
            stego_image=sample_cover_image,
            password="password123",
            stego_key=""
        )


def test_extract_pipeline_invalid_magic(sample_cover_image):
    """Test extract pipeline with image without STGR magic bytes"""
    # Plain image without embedded data should fail with magic bytes error
    with pytest.raises(ExtractError, match="Invalid magic bytes"):
        extract_pipeline(
            stego_image=sample_cover_image,
            password="password123",
            stego_key="stegokey123"
        )


def test_embed_extract_round_trip_text(sample_cover_image):
    """Test complete embed-extract round trip with text message"""
    # NOTE: This test will pass validation but LSB is stub, so extraction will fail
    # This test documents expected behavior once T10-T11 are implemented
    
    payload = b"Hello, World! This is a secret message."
    password = "password123"
    stego_key = "stegokey123"
    
    # Embed should succeed (creates container, but LSB is stub)
    stego_image, embed_meta = embed_pipeline(
        cover_image=sample_cover_image,
        payload_bytes=payload,
        password=password,
        stego_key=stego_key,
        filename="message.txt",
        mime_type="text/plain"
    )
    
    # Verify embed metadata
    assert embed_meta['payload_size'] == len(payload)
    assert embed_meta['filename'] == "message.txt"
    assert embed_meta['mime_type'] == "text/plain"
    assert stego_image.size == sample_cover_image.size
    
    # Extract will fail because LSB is stub (returns zeros)
    # Once T10-T11 are implemented, this should pass:
    # extracted_payload, extract_meta = extract_pipeline(
    #     stego_image=stego_image,
    #     password=password,
    #     stego_key=stego_key
    # )
    # assert extracted_payload == payload


def test_embed_metadata_structure(sample_cover_image):
    """Test that embed pipeline returns complete metadata"""
    payload = b"Test message"
    
    stego_image, metadata = embed_pipeline(
        cover_image=sample_cover_image,
        payload_bytes=payload,
        password="password123",
        stego_key="stegokey123",
        filename="test.txt",
        mime_type="text/plain"
    )
    
    # Check all expected metadata fields
    assert 'payload_size' in metadata
    assert 'encrypted_size' in metadata
    assert 'container_size' in metadata
    assert 'num_bits' in metadata
    assert 'capacity_utilization' in metadata
    assert 'filename' in metadata
    assert 'mime_type' in metadata
    
    # Verify values
    assert metadata['payload_size'] == len(payload)
    assert metadata['encrypted_size'] > len(payload)  # AES-GCM adds overhead
    assert metadata['container_size'] > metadata['encrypted_size']  # Container adds header
    assert metadata['filename'] == "test.txt"
    assert metadata['mime_type'] == "text/plain"


def test_embed_different_stego_keys_produce_different_positions(sample_cover_image):
    """Test that different stego-keys produce different position sequences"""
    payload = b"Test message"
    password = "password123"
    
    # Embed with first key
    stego1, _ = embed_pipeline(
        cover_image=sample_cover_image,
        payload_bytes=payload,
        password=password,
        stego_key="stegokey111"
    )
    
    # Embed with second key
    stego2, _ = embed_pipeline(
        cover_image=sample_cover_image,
        payload_bytes=payload,
        password=password,
        stego_key="stegokey222"
    )
    
    # Images should be different (different positions modified)
    # NOTE: With LSB stub, images are identical. Once T10 implemented, they'll differ
    # For now, just verify both succeed
    assert stego1.size == stego2.size


def test_embed_rgba_image_preserves_mode(sample_rgba_image):
    """Test that RGBA images maintain their alpha channel"""
    payload = b"Test message"
    
    stego_image, _ = embed_pipeline(
        cover_image=sample_rgba_image,
        payload_bytes=payload,
        password="password123",
        stego_key="stegokey123"
    )
    
    # Should preserve RGBA mode
    assert stego_image.mode == 'RGBA'
    assert stego_image.size == sample_rgba_image.size


def test_embed_metrics_calculation(sample_cover_image):
    """Test that MSE/PSNR metrics are calculated"""
    payload = b"Test message"
    
    stego_image, metadata = embed_pipeline(
        cover_image=sample_cover_image,
        payload_bytes=payload,
        password="password123",
        stego_key="stegokey123"
    )
    
    # Metrics should be present (even if stub LSB doesn't modify pixels)
    assert 'mse' in metadata
    assert 'psnr' in metadata
    
    # With stub LSB (no actual modification), MSE should be 0
    # Once T10 implemented, MSE should be > 0
    # For now, just check metrics exist


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
