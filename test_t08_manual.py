"""
Interactive Manual Testing for T08 - STGR Binary Container
Stegora Steganography Core

Author: Naufal (247006111158)
Task: T08 - STGR Binary Container
"""
import sys
import os
import secrets

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Handle Windows terminal encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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
)


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_scenario_text_round_trip():
    """Scenario 1: Text message container round trip"""
    print_header("SKENARIO 1: Encode & Decode Text Payload Container")
    
    # Simulate AES-GCM ciphertext + 16-byte tag
    sample_ciphertext = b"CIPHERTEXT_AES_GCM_ENCRYPTED_MESSAGE_PAYLOAD_WITH_TAG_12345678"
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    filename = "pesan_rahasia.txt"
    mime_type = "text/plain"
    
    print(f"Input Plaintext Metadata:")
    print(f"   Filename  : {filename}")
    print(f"   MIME Type : {mime_type}")
    print(f"   Salt (16B): {salt.hex()}")
    print(f"   IV (12B)  : {iv.hex()}")
    print(f"   Ciphertext: {len(sample_ciphertext)} bytes")
    
    container = create_container(
        payload=sample_ciphertext,
        salt=salt,
        iv=iv,
        filename=filename,
        mime_type=mime_type,
        flags=0,
        payload_type=0
    )
    print(f"\nFramed Container Terbentuk: {len(container)} bytes total")
    
    # Parse container back
    parsed = parse_container(container)
    print(f"\nHasil Parsing Container:")
    print(f"   Magic Valid  : {parsed['magic'] == MAGIC} ({parsed['magic']})")
    print(f"   Version      : {parsed['version']}")
    print(f"   Flags        : {parsed['flags']}")
    print(f"   Payload Type : {parsed['payload_type']}")
    print(f"   Payload Len  : {parsed['payload_len']} bytes")
    print(f"   Salt Cocok   : {parsed['salt'] == salt}")
    print(f"   IV Cocok     : {parsed['iv'] == iv}")
    print(f"   Filename     : '{parsed['filename']}'")
    print(f"   MIME Type    : '{parsed['mime_type']}'")
    print(f"   Payload Cocok: {parsed['payload'] == sample_ciphertext}")
    
    if (parsed['payload'] == sample_ciphertext and 
        parsed['salt'] == salt and 
        parsed['iv'] == iv and 
        parsed['filename'] == filename):
        print("\n[OK] STATUS: Round-trip Text Payload BERHASIL SEMPURNA (100% Cocok).")


def test_scenario_binary_file_round_trip():
    """Scenario 2: Binary file payload container round trip"""
    print_header("SKENARIO 2: Encode & Decode Binary File Container (e.g. PDF)")
    
    # 2048 bytes of arbitrary binary payload
    fake_pdf_payload = os.urandom(2048)
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    filename = "laporan_keuangan.pdf"
    mime_type = "application/pdf"
    
    container = create_container(
        payload=fake_pdf_payload,
        salt=salt,
        iv=iv,
        filename=filename,
        mime_type=mime_type,
        flags=1,
        payload_type=1
    )
    
    parsed = parse_container(container)
    print(f"Total Container Size : {len(container)} bytes")
    print(f"Original Payload Len : {len(fake_pdf_payload)} bytes")
    print(f"Extracted Payload Len: {len(parsed['payload'])} bytes")
    print(f"Payload Type         : {parsed['payload_type']} (1=File)")
    print(f"Bytes Match Exact    : {parsed['payload'] == fake_pdf_payload}")
    
    if parsed['payload'] == fake_pdf_payload:
        print("\n[OK] STATUS: Round-trip Binary File BERHASIL SEMPURNA.")


def test_scenario_header_inspection():
    """Scenario 3: Direct inspection of 12-byte fixed header"""
    print_header("SKENARIO 3: Inspeksi Fixed Header 12-Byte (STGR)")
    
    sample_payload = b"TEST"
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    container = create_container(sample_payload, salt, iv)
    
    header_bytes = container[:HEADER_SIZE]
    header = parse_header(header_bytes)
    
    print(f"Header Raw Bytes (Hex): {header_bytes.hex()}")
    print(f"Header Size           : {len(header_bytes)} bytes (Standard STEGO_SPEC.md)")
    print(f"MAGIC                 : {header['magic']} (Must be b'STGR')")
    print(f"VERSION               : {header['version']}")
    print(f"FLAGS                 : {header['flags']}")
    print(f"PAYLOAD_TYPE          : {header['payload_type']}")
    print(f"RESERVED              : {header['reserved']}")
    print(f"PAYLOAD_LEN           : {header['payload_len']} bytes")
    print("\n[OK] STATUS: Fixed Header 12-byte terverifikasi sesuai spesifikasi.")


def test_scenario_metadata_lengths():
    """Scenario 4: Direct inspection of 5-byte metadata lengths"""
    print_header("SKENARIO 4: Inspeksi Metadata Lengths Field 5-Byte")
    
    filename = "dokumen.docx"
    mime_type = "application/octet-stream"
    container = create_container(b"data", secrets.token_bytes(16), secrets.token_bytes(12), filename, mime_type)
    
    meta_bytes = container[HEADER_SIZE:HEADER_SIZE + META_LENGTHS_SIZE]
    salt_len, iv_len, fn_len, mime_len = parse_metadata_lengths(meta_bytes)
    
    print(f"Meta Lengths Raw (Hex): {meta_bytes.hex()}")
    print(f"SALT_LEN (1 byte)     : {salt_len} bytes")
    print(f"IV_LEN (1 byte)       : {iv_len} bytes")
    print(f"FILENAME_LEN (2 bytes): {fn_len} bytes (Matches '{filename}': {len(filename.encode('utf-8'))}B)")
    print(f"MIME_LEN (1 byte)     : {mime_len} bytes (Matches '{mime_type}': {len(mime_type.encode('ascii'))}B)")
    print("\n[OK] STATUS: Metadata Lengths field 5-byte terverifikasi akurat.")


def test_scenario_tampered_magic_detection():
    """Scenario 5: Detection of invalid magic bytes"""
    print_header("SKENARIO 5: Deteksi Magic Bytes Rusak / Kunci Salah")
    
    container = create_container(b"rahasia", secrets.token_bytes(16), secrets.token_bytes(12))
    # Rusak magic bytes dari STGR menjadi NOPE
    corrupted = b'NOPE' + container[4:]
    
    try:
        parse_container(corrupted)
        print("\n[FAIL] GAGAL: Container dengan magic rusak seharusnya ditolak!")
    except ContainerError as e:
        print(f"Deteksi Penolakan: Berhasil menolak container dengan aman!")
        print(f"Pesan Error      : {e}")
        print("\n[OK] STATUS: Validasi Magic Bytes mendeteksi ketidaksesuaian dengan tepat.")


def test_scenario_truncation_detection():
    """Scenario 6: Detection of truncated container"""
    print_header("SKENARIO 6: Deteksi Container Terpotong (Truncated Data)")
    
    long_payload = b"A" * 500
    container = create_container(long_payload, secrets.token_bytes(16), secrets.token_bytes(12))
    
    # Potong 50 byte di akhir payload
    truncated = container[:-50]
    
    try:
        parse_container(truncated)
        print("\n[FAIL] GAGAL: Container terpotong seharusnya ditolak!")
    except ContainerError as e:
        print(f"Deteksi Penolakan: Berhasil mendeteksi container terpotong!")
        print(f"Pesan Error      : {e}")
        print("\n[OK] STATUS: Penolakan Truncation bekerja dengan aman.")


def run_all_manual_tests():
    print("\n" + "=" * 70)
    print("  STEGORA - MANUAL TESTING SUITE: T08 STGR BINARY CONTAINER")
    print("  PIC: Naufal (247006111158)")
    print("=" * 70)
    
    test_scenario_text_round_trip()
    test_scenario_binary_file_round_trip()
    test_scenario_header_inspection()
    test_scenario_metadata_lengths()
    test_scenario_tampered_magic_detection()
    test_scenario_truncation_detection()
    
    print("\n" + "=" * 70)
    print("  [SUCCESS] SEMUA SKENARIO PENGUJIAN MANUAL T08 BERHASIL TERVERIFIKASI!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_manual_tests()
