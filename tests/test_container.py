"""
Tests for STGR Binary Container (T08 - Naufal)
Verifies container serialization, parsing, header framing, and error handling.
"""
import pytest
import os
import secrets

from backend.stego.container import (
    create_container,
    parse_container,
    parse_header,
    parse_metadata_lengths,
    calculate_container_size,
    ContainerError,
    MAGIC,
    VERSION,
    HEADER_SIZE,
    META_LENGTHS_SIZE,
    MIN_CONTAINER_SIZE,
)


class TestContainerRoundTrip:
    """Test serialization and deserialization round trip"""
    
    def test_text_payload_round_trip(self):
        """Standard text payload with filename and MIME type"""
        payload = b"Sample AES-GCM ciphertext with authentication tag 12345678"
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(12)
        filename = "pesan.txt"
        mime_type = "text/plain"
        
        container = create_container(
            payload=payload,
            salt=salt,
            iv=iv,
            filename=filename,
            mime_type=mime_type,
            flags=0,
            payload_type=0
        )
        
        parsed = parse_container(container)
        
        assert parsed['magic'] == MAGIC
        assert parsed['version'] == VERSION
        assert parsed['flags'] == 0
        assert parsed['payload_type'] == 0
        assert parsed['salt'] == salt
        assert parsed['iv'] == iv
        assert parsed['filename'] == filename
        assert parsed['mime_type'] == mime_type
        assert parsed['payload'] == payload
        assert parsed['payload_len'] == len(payload)

    def test_binary_file_payload_round_trip(self):
        """Binary file payload with arbitrary bytes"""
        payload = os.urandom(1024)
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(12)
        filename = "dokumen.pdf"
        mime_type = "application/pdf"
        
        container = create_container(
            payload=payload,
            salt=salt,
            iv=iv,
            filename=filename,
            mime_type=mime_type,
            flags=1,
            payload_type=1
        )
        
        parsed = parse_container(container)
        
        assert parsed['payload'] == payload
        assert parsed['salt'] == salt
        assert parsed['iv'] == iv
        assert parsed['filename'] == filename
        assert parsed['mime_type'] == mime_type
        assert parsed['flags'] == 1
        assert parsed['payload_type'] == 1

    def test_empty_optional_metadata(self):
        """Container with empty filename and empty MIME type"""
        payload = b"encrypted_bytes"
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(12)
        
        container = create_container(
            payload=payload,
            salt=salt,
            iv=iv,
            filename="",
            mime_type=""
        )
        
        parsed = parse_container(container)
        assert parsed['filename'] == ""
        assert parsed['mime_type'] == ""
        assert parsed['payload'] == payload

    def test_unicode_filename_round_trip(self):
        """Container with UTF-8 non-ASCII filename"""
        payload = b"secret_data"
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(12)
        filename = "laporan_rahasia_🔒.docx"
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        container = create_container(
            payload=payload,
            salt=salt,
            iv=iv,
            filename=filename,
            mime_type=mime_type
        )
        
        parsed = parse_container(container)
        assert parsed['filename'] == filename
        assert parsed['payload'] == payload


class TestHeaderAndMetadataParsing:
    """Test separate header and metadata lengths parsing"""
    
    def test_parse_header_valid(self):
        """Parse valid 12-byte header"""
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(12)
        container = create_container(
            payload=b"test_payload_123",
            salt=salt,
            iv=iv,
            flags=3,
            payload_type=1
        )
        
        header = parse_header(container[:HEADER_SIZE])
        assert header['magic'] == b'STGR'
        assert header['version'] == 1
        assert header['flags'] == 3
        assert header['payload_type'] == 1
        assert header['reserved'] == 0
        assert header['payload_len'] == len(b"test_payload_123")

    def test_parse_header_invalid_magic(self):
        """Header with invalid magic must raise ContainerError"""
        bad_header = b'XXXX' + b'\x01\x00\x00\x00\x00\x00\x00\x05'
        with pytest.raises(ContainerError, match="Invalid magic bytes"):
            parse_header(bad_header)

    def test_parse_header_unsupported_version(self):
        """Header with unsupported version must raise ContainerError"""
        bad_version_header = b'STGR' + b'\x02\x00\x00\x00\x00\x00\x00\x05'
        with pytest.raises(ContainerError, match="Unsupported container version"):
            parse_header(bad_version_header)

    def test_parse_header_too_short(self):
        """Header with fewer than 12 bytes must raise ContainerError"""
        with pytest.raises(ContainerError, match="Header too short"):
            parse_header(b'STGR\x01\x00')

    def test_parse_metadata_lengths_valid(self):
        """Parse valid 5-byte metadata lengths field"""
        # salt_len=16 (0x10), iv_len=12 (0x0C), fn_len=10 (0x000A), mime_len=20 (0x14)
        meta_bytes = bytes([16, 12, 0, 10, 20])
        salt_len, iv_len, fn_len, mime_len = parse_metadata_lengths(meta_bytes)
        assert salt_len == 16
        assert iv_len == 12
        assert fn_len == 10
        assert mime_len == 20

    def test_parse_metadata_lengths_too_short(self):
        """Metadata lengths field shorter than 5 bytes must raise ContainerError"""
        with pytest.raises(ContainerError, match="Metadata lengths field too short"):
            parse_metadata_lengths(b'\x10\x0c\x00')


class TestContainerValidationAndErrors:
    """Test edge cases, corruption, and input validation"""
    
    def test_container_too_short(self):
        """Container shorter than 17 bytes must raise ContainerError"""
        with pytest.raises(ContainerError, match="Container too short"):
            parse_container(b'STGR1234')

    def test_container_truncated_payload(self):
        """Container truncated in payload section must raise ContainerError"""
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(12)
        container = create_container(
            payload=b"1234567890" * 10,  # 100 bytes
            salt=salt,
            iv=iv
        )
        
        # Chop off last 20 bytes
        truncated = container[:-20]
        with pytest.raises(ContainerError, match="Container truncated"):
            parse_container(truncated)

    def test_salt_too_long(self):
        """Salt longer than 255 bytes must raise ContainerError"""
        with pytest.raises(ContainerError, match="Salt too long"):
            create_container(
                payload=b"data",
                salt=b"x" * 256,
                iv=secrets.token_bytes(12)
            )

    def test_iv_too_long(self):
        """IV longer than 255 bytes must raise ContainerError"""
        with pytest.raises(ContainerError, match="IV too long"):
            create_container(
                payload=b"data",
                salt=secrets.token_bytes(16),
                iv=b"y" * 256
            )

    def test_invalid_type_inputs(self):
        """Non-bytes inputs for payload or salt must raise ContainerError"""
        with pytest.raises(ContainerError, match="Payload must be bytes"):
            create_container(
                payload="not_bytes",  # type: ignore
                salt=secrets.token_bytes(16),
                iv=secrets.token_bytes(12)
            )


class TestContainerSizeCalculation:
    """Test calculate_container_size against actual created containers"""
    
    def test_size_matches_actual_container(self):
        """Calculated size must match len(create_container) exactly"""
        payload = b"secret ciphertext"
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(12)
        filename = "note.txt"
        mime_type = "text/plain"
        
        container = create_container(
            payload=payload,
            salt=salt,
            iv=iv,
            filename=filename,
            mime_type=mime_type
        )
        
        calculated_size = calculate_container_size(
            payload_size=len(payload),
            salt_len=len(salt),
            iv_len=len(iv),
            filename_len=len(filename.encode('utf-8')),
            mime_len=len(mime_type.encode('ascii'))
        )
        
        assert len(container) == calculated_size
        assert len(container) == 12 + 5 + 16 + 12 + len(filename) + len(mime_type) + len(payload)
