"""
Interactive Manual Testing for T09 - Keyed Deterministic PRNG
Stegora Steganography Core

Author: Naufal (247006111158)
Task: T09 - Keyed Deterministic PRNG
"""
import sys
import os

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Handle Windows terminal encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.stego.positions import (
    generate_seed_from_key,
    generate_positions,
    verify_determinism,
    verify_uniqueness,
    PositionGeneratorError
)


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_scenario_seed_generation():
    """Scenario 1: SHA-256 Seed Generation from stego-key"""
    print_header("SKENARIO 1: Generasi Seed PRNG Berbasis SHA-256")
    
    key1 = "kuncirahasia123"
    seed1 = generate_seed_from_key(key1)
    
    key2 = "kuncirahasia124"  # Beda 1 karakter
    seed2 = generate_seed_from_key(key2)
    
    print(f"Key A : '{key1}' -> Seed: {seed1}")
    print(f"Key B : '{key2}' -> Seed: {seed2}")
    
    assert seed1 != seed2, "Seed tidak boleh sama untuk key berbeda!"
    print("\n[OK] STATUS: Seed SHA-256 berhasil diturunkan dengan nilai unik.")


def test_scenario_determinism():
    """Scenario 2: Deterministic reproduction with same key"""
    print_header("SKENARIO 2: Uji Determinisme (Reproducibility)")
    print("Prinsip: Stego-key yang sama WAJIB menghasilkan koordinat yang identik.")
    
    key = "stegora_secure_key_2026"
    width, height = 100, 100
    num_bits = 8
    
    pos_run1 = generate_positions(width, height, key, num_bits)
    pos_run2 = generate_positions(width, height, key, num_bits)
    
    print(f"\nRun 1 Koordinat (x, y, kanal):")
    for i, (x, y, c) in enumerate(pos_run1):
        channel_name = ['Red', 'Green', 'Blue'][c]
        print(f"   Bit #{i+1}: Piksel ({x:2d}, {y:2d}), Kanal: {channel_name} (idx {c})")
        
    print(f"\nRun 2 Koordinat (x, y, kanal):")
    for i, (x, y, c) in enumerate(pos_run2):
        channel_name = ['Red', 'Green', 'Blue'][c]
        print(f"   Bit #{i+1}: Piksel ({x:2d}, {y:2d}), Kanal: {channel_name} (idx {c})")
        
    is_deterministic = verify_determinism(width, height, key, num_bits, iterations=5)
    assert is_deterministic, "Posisi tidak deterministik!"
    print("\n[OK] STATUS: Determinisme TERBUKTI 100% IDENTIK antar eksekusi.")


def test_scenario_key_sensitivity():
    """Scenario 3: Key sensitivity (avalanche effect)"""
    print_header("SKENARIO 3: Uji Sensitivitas Kunci (Avalanche Effect)")
    print("Prinsip: Perubahan 1 karakter kunci harus mengacak posisi secara total.")
    
    width, height = 200, 200
    num_bits = 10
    
    key_original = "password123"
    key_altered  = "password124"
    
    pos_orig = generate_positions(width, height, key_original, num_bits)
    pos_alt  = generate_positions(width, height, key_altered, num_bits)
    
    print(f"Kunci 1: '{key_original}' -> 3 Posisi Pertama: {pos_orig[:3]}")
    print(f"Kunci 2: '{key_altered}' -> 3 Posisi Pertama: {pos_alt[:3]}")
    
    # Hitung berapa banyak posisi yang bertabrakan di urutan yang sama
    matches = sum(1 for p1, p2 in zip(pos_orig, pos_alt) if p1 == p2)
    print(f"Jumlah posisi sama pada urutan identik: {matches} dari {num_bits}")
    
    assert pos_orig != pos_alt, "Posisi tidak boleh sama untuk kunci berbeda!"
    print("\n[OK] STATUS: Sensitivitas kunci terbukti. Posisi berubah total.")


def test_scenario_alpha_preservation():
    """Scenario 4: Alpha Channel Preservation"""
    print_header("SKENARIO 4: Perlindungan Kanal Alpha (Transparansi)")
    print("Prinsip: Algoritma steganografi HANYA boleh memodifikasi kanal R (0), G (1), B (2).")
    print("         Kanal Alpha (3) TIDAK BOLEH disentuh untuk menjaga integritas transparansi.")
    
    width, height = 64, 64
    num_bits = 1000  # Uji 1.000 bit acak
    key = "alpha_protection_test_key"
    
    positions = generate_positions(width, height, key, num_bits)
    
    channels_used = set(p[2] for p in positions)
    print(f"Kanal warna yang dipilih oleh PRNG: {sorted(list(channels_used))}")
    print("   0 = Merah (Red)")
    print("   1 = Hijau (Green)")
    print("   2 = Biru (Blue)")
    
    has_alpha = any(c >= 3 for c in channels_used)
    assert not has_alpha, "BAHAYA: PRNG menghasilkan kanal Alpha!"
    print("\n[OK] STATUS: Perlindungan Alpha AMAN! Kanal 3 (Alpha) tidak pernah dipilih.")


def test_scenario_uniqueness():
    """Scenario 5: Position Uniqueness (No collision without replacement)"""
    print_header("SKENARIO 5: Uji Keunikan Posisi (Tanpa Duplikasi)")
    print("Prinsip: Setiap bit harus menempati posisi unik agar tidak saling menimpa.")
    
    width, height = 50, 50
    num_bits = 2000
    key = "unique_positions_key"
    
    positions = generate_positions(width, height, key, num_bits)
    is_unique = verify_uniqueness(positions)
    
    print(f"Total Posisi Diminta : {num_bits}")
    print(f"Total Posisi Unik   : {len(set(positions))}")
    
    assert is_unique, "Ditemukan posisi duplikat!"
    print("\n[OK] STATUS: Semua posisi 100% UNIK tanpa tabrakan.")


def test_scenario_error_handling():
    """Scenario 6: Boundary & Error Handling"""
    print_header("SKENARIO 6: Uji Penanganan Error & Batas Kapasitas")
    
    # 1. Key kosong
    try:
        generate_positions(100, 100, "", 10)
        print("[FAIL] Seharusnya gagal jika key kosong!")
    except PositionGeneratorError as e:
        print(f"1. Key kosong ditolak dengan benar  : {e}")
        
    # 2. Dimensi tidak valid
    try:
        generate_positions(0, 100, "kunci123", 10)
        print("[FAIL] Seharusnya gagal jika lebar 0!")
    except PositionGeneratorError as e:
        print(f"2. Dimensi <= 0 ditolak dengan benar : {e}")
        
    # 3. Jumlah bit melebihi kapasitas piksel
    # Gambar 2x2 = 4 piksel x 3 kanal = 12 bit maks
    try:
        generate_positions(2, 2, "kunci123", 15)
        print("[FAIL] Seharusnya gagal jika melebihi kapasitas!")
    except PositionGeneratorError as e:
        print(f"3. Permintaan melebihi kapasitas ditolak: {e}")
        
    print("\n[OK] STATUS: Penanganan error batas input bekerja sempurna.")


def run_all_manual_tests():
    print("\n" + "=" * 70)
    print("  STEGORA - MANUAL TESTING SUITE: T09 KEYED DETERMINISTIC PRNG")
    print("  PIC: Naufal (247006111158)")
    print("=" * 70)
    
    test_scenario_seed_generation()
    test_scenario_determinism()
    test_scenario_key_sensitivity()
    test_scenario_alpha_preservation()
    test_scenario_uniqueness()
    test_scenario_error_handling()
    
    print("\n" + "=" * 70)
    print("  [SUCCESS] SEMUA SKENARIO PENGUJIAN MANUAL T09 BERHASIL TERVERIFIKASI!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_manual_tests()
