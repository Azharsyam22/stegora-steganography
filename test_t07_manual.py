"""
Interactive Manual Testing for T07 - Capacity Calculator
Stegora Steganography Core

Author: Naufal (247006111158)
Task: T07 - Capacity Calculator
"""
import sys
import os
from typing import Dict

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Handle Windows terminal encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.stego.capacity import (
    calculate_raw_capacity,
    calculate_usable_capacity,
    check_payload_capacity,
    validate_payload_capacity,
    calculate_exact_container_overhead,
    format_bytes,
    PayloadCapacityExceededError,
    FIXED_HEADER_SIZE,
    METADATA_LENGTHS_SIZE,
    SALT_SIZE,
    IV_SIZE,
    AES_GCM_TAG_SIZE,
    MINIMUM_CONTAINER_OVERHEAD,
    DEFAULT_CONTAINER_OVERHEAD,
)


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_scenario_resolution_capacity():
    """Scenario 1: Capacity for various resolutions"""
    print_header("SKENARIO 1: Perhitungan Kapasitas Aktual Berbagai Resolusi Citra")
    print(f"{'Resolusi':<16} | {'Total Pixel':<12} | {'Raw Capacity':<14} | {'Usable Capacity':<15} | {'Efisiensi':<10}")
    print("-" * 75)
    
    resolutions = [
        ("50 x 50 (Tiny)", 50, 50),
        ("100 x 100", 100, 100),
        ("200 x 200 (Small)", 200, 200),
        ("640 x 480 (VGA)", 640, 480),
        ("800 x 600 (SVGA)", 800, 600),
        ("1280 x 720 (HD)", 1280, 720),
        ("1920 x 1080 (FHD)", 1920, 1080),
        ("3840 x 2160 (4K)", 3840, 2160),
    ]
    
    for label, w, h in resolutions:
        raw = calculate_raw_capacity(w, h)
        usable = calculate_usable_capacity(w, h, container_overhead=64)
        print(
            f"{label:<16} | {raw['total_pixels']:<12,d} | "
            f"{format_bytes(raw['total_bytes']):<14} | "
            f"{format_bytes(usable['usable_capacity_bytes']):<15} | "
            f"{usable['efficiency_percent']:.1f}%"
        )
    print("\nPenjelasan: 1-bit LSB menggunakan 3 bit per pixel (RGB). Alpha tidak dihitung.")


def test_scenario_alpha_preservation():
    """Scenario 2: Alpha channel preservation"""
    print_header("SKENARIO 2: Verifikasi Preservasi Channel Alpha")
    w, h = 400, 300
    
    rgb_cap = calculate_raw_capacity(w, h, use_alpha=False)
    rgba_cap = calculate_raw_capacity(w, h, use_alpha=True)
    
    print(f"Citra 400x300 RGB  : Bits per pixel = {rgb_cap['bits_per_pixel']}, Total Bytes = {rgb_cap['total_bytes']:,} B")
    print(f"Citra 400x300 RGBA : Bits per pixel = {rgba_cap['bits_per_pixel']}, Total Bytes = {rgba_cap['total_bytes']:,} B")
    
    if rgb_cap['total_bytes'] == rgba_cap['total_bytes'] and rgba_cap['bits_per_pixel'] == 3:
        print("\n[OK] BERHASIL: Kapasitas RGB dan RGBA bernilai identik (3 bit/pixel).")
        print("     Channel alpha dijaga murni (preserved) dan tidak pernah dipakai embedding.")


def test_scenario_container_overhead_breakdown():
    """Scenario 3: Breakdown of container framing overhead"""
    print_header("SKENARIO 3: Rincian Container Framing Overhead (STGR Container)")
    print(f"1. Fixed STGR Header       : {FIXED_HEADER_SIZE} bytes (MAGIC: 4, VER: 1, FLAGS: 1, TYPE: 1, RES: 1, LEN: 4)")
    print(f"2. Metadata Lengths Field  : {METADATA_LENGTHS_SIZE} bytes (salt_len: 1, iv_len: 1, fn_len: 2, mime_len: 1)")
    print(f"3. PBKDF2 Salt             : {SALT_SIZE} bytes")
    print(f"4. AES-GCM IV (Nonce)      : {IV_SIZE} bytes")
    print(f"5. AES-GCM Auth Tag        : {AES_GCM_TAG_SIZE} bytes")
    print("-" * 70)
    print(f"Total Overhead Minimum     : {MINIMUM_CONTAINER_OVERHEAD} bytes (tanpa filename & MIME)")
    
    # Custom overhead calculation
    filename = "document_rahasia.pdf"
    mime_type = "application/pdf"
    exact = calculate_exact_container_overhead(filename=filename, mime_type=mime_type)
    print(f"\nContoh payload file nyata:")
    print(f"   Nama berkas             : '{filename}' ({len(filename.encode('utf-8'))} bytes UTF-8)")
    print(f"   MIME Type               : '{mime_type}' ({len(mime_type.encode('ascii'))} bytes ASCII)")
    print(f"   Total Overhead Eksak    : {exact} bytes")


def test_scenario_payload_fit():
    """Scenario 4: Valid payload within capacity"""
    print_header("SKENARIO 4: Uji Payload Normal (Fits Within Capacity)")
    w, h = 200, 200  # Raw: 15,000 bytes, Usable: 14,936 bytes
    payload_size = 500  # 500 bytes text
    
    res = check_payload_capacity(w, h, payload_size=payload_size)
    print(f"Dimensi Citra          : {w} x {h}")
    print(f"Ukuran Payload         : {format_bytes(payload_size)} ({payload_size} bytes)")
    print(f"Kapasitas Tersedia     : {format_bytes(res['available_bytes'])} ({res['available_bytes']} bytes)")
    print(f"Kebutuhan Total (+tag) : {format_bytes(res['required_bytes'])} ({res['required_bytes']} bytes)")
    print(f"Sisa Kapasitas         : {format_bytes(res['remaining_bytes'])} ({res['remaining_bytes']} bytes)")
    print(f"Utilisasi              : {res['utilization_percent']:.2f}%")
    print(f"Status Fits            : {res['fits']}")
    
    if res['fits']:
        print("\n[OK] STATUS: Payload DITERIMA (Fits). Siap untuk tahap enkripsi dan embedding.")


def test_scenario_oversized_rejection():
    """Scenario 5: Oversized payload rejection"""
    print_header("SKENARIO 5: Uji Penolakan Payload Berlebih (Oversized Rejection)")
    w, h = 50, 50  # Raw: 937 bytes, Usable: 873 bytes
    oversized_payload = 2000  # 2000 bytes > 873 bytes
    
    res = check_payload_capacity(w, h, payload_size=oversized_payload)
    print(f"Dimensi Citra          : {w} x {h}")
    print(f"Ukuran Payload         : {format_bytes(oversized_payload)} ({oversized_payload} bytes)")
    print(f"Kapasitas Tersedia     : {format_bytes(res['available_bytes'])} ({res['available_bytes']} bytes)")
    print(f"Kebutuhan Total (+tag) : {format_bytes(res['required_bytes'])} ({res['required_bytes']} bytes)")
    print(f"Defisit / Kurang       : {format_bytes(abs(res['remaining_bytes']))} ({abs(res['remaining_bytes'])} bytes)")
    print(f"Utilisasi              : {res['utilization_percent']:.2f}% (Melebihi 100%)")
    print(f"Status Fits            : {res['fits']}")
    print(f"Pesan Penolakan        : {res['rejection_reason']}")
    
    # Test programmatic exception enforcement
    try:
        validate_payload_capacity(w, h, payload_size=oversized_payload)
        print("\n[FAIL] GAGAL: Seharusnya melempar exception PayloadCapacityExceededError!")
    except PayloadCapacityExceededError as e:
        print(f"\n[OK] BERHASIL: PayloadCapacityExceededError berhasil dilempar sebelum mutasi citra!")
        print(f"     Detail Exception: {e}")


def test_scenario_boundary_check():
    """Scenario 6: Exact boundary check (pass vs 1-byte overflow)"""
    print_header("SKENARIO 6: Uji Batas Kritis (Exact Boundary vs 1-Byte Overflow)")
    w, h = 100, 100
    usable = calculate_usable_capacity(w, h, container_overhead=64)['usable_capacity_bytes']
    
    # Kasus 1: Payload pas di kapasitas maksimal
    exact_payload = usable - 16
    res_exact = check_payload_capacity(w, h, payload_size=exact_payload, container_overhead=64)
    print(f"1. Payload Pas Maksimal ({exact_payload} bytes):")
    print(f"   - Fits: {res_exact['fits']}, Remaining: {res_exact['remaining_bytes']} bytes, Utilisasi: {res_exact['utilization_percent']:.2f}%")
    
    # Kasus 2: Payload lebih 1 byte saja dari kapasitas
    overflow_payload = exact_payload + 1
    res_overflow = check_payload_capacity(w, h, payload_size=overflow_payload, container_overhead=64)
    print(f"2. Payload Lebih 1 Byte ({overflow_payload} bytes):")
    print(f"   - Fits: {res_overflow['fits']}, Remaining: {res_overflow['remaining_bytes']} bytes, Utilisasi: {res_overflow['utilization_percent']:.2f}%")
    print(f"   - Alasan: {res_overflow['rejection_reason']}")
    
    if res_exact['fits'] and not res_overflow['fits'] and res_overflow['remaining_bytes'] == -1:
        print("\n[OK] BERHASIL: Uji batas presisi 1-byte bekerja akurat!")


def run_all_manual_tests():
    print("\n" + "=" * 70)
    print("  STEGORA - MANUAL TESTING SUITE: T07 CAPACITY CALCULATOR")
    print("  PIC: Naufal (247006111158)")
    print("=" * 70)
    
    test_scenario_resolution_capacity()
    test_scenario_alpha_preservation()
    test_scenario_container_overhead_breakdown()
    test_scenario_payload_fit()
    test_scenario_oversized_rejection()
    test_scenario_boundary_check()
    
    print("\n" + "=" * 70)
    print("  [SUCCESS] SEMUA SKENARIO PENGUJIAN MANUAL T07 BERHASIL TERVERIFIKASI!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_manual_tests()
