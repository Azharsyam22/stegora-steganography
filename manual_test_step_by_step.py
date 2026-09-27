"""
Manual Test T10 - LSB Embedding Step by Step
Naufal (247006111158)

Test ini akan menjalankan 5 scenario berbeda untuk memverifikasi
implementasi LSB embedding bekerja dengan benar.
"""
from PIL import Image
import numpy as np
from backend.stego.lsb import embed_lsb
from backend.stego.positions import generate_positions
from backend.image.metrics import calculate_mse, calculate_psnr

print("=" * 70)
print("MANUAL TEST T10 - 1-BIT RGB LSB EMBEDDING")
print("=" * 70)
print()

# ============================================================================
# TEST 1: Basic RGB Embedding
# ============================================================================
print("TEST 1: Basic RGB Embedding")
print("-" * 70)
print("Tujuan: Memverifikasi embedding dasar berfungsi pada gambar RGB")
print()

try:
    # Buat cover image putih 100x100 pixels
    cover = Image.new('RGB', (100, 100), color='white')
    print(f"✅ Cover image dibuat: {cover.size}, mode={cover.mode}")
    
    # Payload test
    payload = b"Hello Stegora 2026!"
    print(f"✅ Payload: {len(payload)} bytes = {len(payload)*8} bits")
    print(f"   Content: {payload.decode('utf-8')}")
    
    # Generate posisi dari stego-key
    positions = generate_positions(100, 100, "test_key_123", len(payload) * 8)
    print(f"✅ Generated {len(positions)} positions dari stego-key")
    
    # Embed payload ke cover image
    stego = embed_lsb(cover, payload, positions)
    print(f"✅ Stego image dibuat: {stego.size}, mode={stego.mode}")
    
    # Calculate quality metrics
    mse = calculate_mse(cover, stego)
    psnr = calculate_psnr(cover, stego, mse=mse)
    print(f"✅ MSE: {mse:.6f} (harus > 0 untuk membuktikan ada perubahan)")
    print(f"✅ PSNR: {psnr:.2f} dB (harus > 45 dB untuk kualitas tinggi)")
    
    # Verifikasi perubahan hanya di LSB
    cover_arr = np.array(cover)
    stego_arr = np.array(stego)
    diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
    max_diff = diff.max()
    print(f"✅ Perubahan pixel maksimal: {max_diff} (harus ≤ 1 karena LSB only)")
    
    if mse > 0 and psnr > 45 and max_diff <= 1:
        print("✅ TEST 1 PASSED!")
    else:
        print("❌ TEST 1 FAILED!")
        
except Exception as e:
    print(f"❌ TEST 1 ERROR: {e}")

print()
print()

# ============================================================================
# TEST 2: Alpha Channel Preservation (RGBA)
# ============================================================================
print("TEST 2: Alpha Channel Preservation (RGBA)")
print("-" * 70)
print("Tujuan: Memverifikasi alpha channel tidak berubah sama sekali")
print()

try:
    # Buat RGBA image dengan transparansi
    cover_rgba = Image.new('RGBA', (100, 100), color=(255, 255, 255, 128))
    print(f"✅ Cover RGBA dibuat: {cover_rgba.size}, mode={cover_rgba.mode}")
    print(f"   Alpha value: 128 (50% transparansi)")
    
    # Payload
    payload2 = b"Test alpha preservation"
    print(f"✅ Payload: {len(payload2)} bytes")
    
    # Generate positions
    positions2 = generate_positions(100, 100, "alpha_key", len(payload2) * 8)
    
    # Embed
    stego_rgba = embed_lsb(cover_rgba, payload2, positions2)
    print(f"✅ Stego RGBA dibuat: {stego_rgba.size}, mode={stego_rgba.mode}")
    
    # Verify alpha tidak berubah SAMA SEKALI
    cover_alpha = np.array(cover_rgba)[:, :, 3]
    stego_alpha = np.array(stego_rgba)[:, :, 3]
    alpha_preserved = np.array_equal(cover_alpha, stego_alpha)
    
    print(f"✅ Alpha channel preserved: {alpha_preserved}")
    print(f"   Cover alpha sum: {cover_alpha.sum()}")
    print(f"   Stego alpha sum: {stego_alpha.sum()}")
    print(f"   Difference: {abs(cover_alpha.sum() - stego_alpha.sum())}")
    
    if alpha_preserved:
        print("✅ TEST 2 PASSED!")
    else:
        print("❌ TEST 2 FAILED! Alpha was modified!")
        
except Exception as e:
    print(f"❌ TEST 2 ERROR: {e}")

print()
print()

# ============================================================================
# TEST 3: Different Stego-Keys Produce Different Results
# ============================================================================
print("TEST 3: Different Stego-Keys")
print("-" * 70)
print("Tujuan: Stego-key berbeda harus menghasilkan stego image berbeda")
print()

try:
    payload3 = b"Same payload different keys"
    print(f"✅ Payload sama: {len(payload3)} bytes")
    
    # Generate positions dengan 2 key berbeda
    positions_a = generate_positions(100, 100, "key_A", len(payload3) * 8)
    positions_b = generate_positions(100, 100, "key_B", len(payload3) * 8)
    
    print(f"✅ Generated positions dengan key_A")
    print(f"✅ Generated positions dengan key_B")
    print(f"   First position key_A: {positions_a[0]}")
    print(f"   First position key_B: {positions_b[0]}")
    
    # Embed dengan kedua key
    cover3 = Image.new('RGB', (100, 100), color='blue')
    stego_a = embed_lsb(cover3, payload3, positions_a)
    stego_b = embed_lsb(cover3, payload3, positions_b)
    
    print(f"✅ Stego A dibuat dengan key_A")
    print(f"✅ Stego B dibuat dengan key_B")
    
    # Compare pixel arrays
    arr_a = np.array(stego_a)
    arr_b = np.array(stego_b)
    different = not np.array_equal(arr_a, arr_b)
    
    num_diff_pixels = np.count_nonzero(arr_a != arr_b)
    print(f"✅ Stego images berbeda: {different}")
    print(f"   Jumlah pixel berbeda: {num_diff_pixels}")
    
    if different and num_diff_pixels > 0:
        print("✅ TEST 3 PASSED!")
    else:
        print("❌ TEST 3 FAILED! Images should be different!")
        
except Exception as e:
    print(f"❌ TEST 3 ERROR: {e}")

print()
print()

# ============================================================================
# TEST 4: Large Payload
# ============================================================================
print("TEST 4: Large Payload (2KB)")
print("-" * 70)
print("Tujuan: Memverifikasi embedding payload besar berfungsi")
print()

try:
    # Large payload 2KB
    large_payload = b"X" * 2000
    print(f"✅ Large payload: {len(large_payload)} bytes = {len(large_payload)*8} bits")
    
    # Butuh gambar lebih besar untuk 2KB payload
    # 2000 bytes = 16000 bits
    # Butuh minimal 16000/3 = 5334 pixels
    # Gunakan 300x300 = 90000 pixels (aman)
    cover_large = Image.new('RGB', (300, 300), color='green')
    print(f"✅ Cover large: {cover_large.size} = {300*300} pixels")
    print(f"   Raw capacity: {(300*300*3)//8} bytes")
    
    positions_large = generate_positions(300, 300, "large_key", len(large_payload) * 8)
    stego_large = embed_lsb(cover_large, large_payload, positions_large)
    
    print(f"✅ Large payload embedded successfully")
    
    # Metrics
    mse_large = calculate_mse(cover_large, stego_large)
    psnr_large = calculate_psnr(cover_large, stego_large, mse=mse_large)
    print(f"✅ MSE: {mse_large:.6f}")
    print(f"✅ PSNR: {psnr_large:.2f} dB")
    
    if mse_large > 0 and psnr_large > 40:
        print("✅ TEST 4 PASSED!")
    else:
        print("❌ TEST 4 FAILED!")
        
except Exception as e:
    print(f"❌ TEST 4 ERROR: {e}")

print()
print()

# ============================================================================
# TEST 5: Validation - Reject Oversized Payload
# ============================================================================
print("TEST 5: Validation - Reject Oversized Payload")
print("-" * 70)
print("Tujuan: Memverifikasi sistem reject payload yang terlalu besar")
print()

try:
    # Small image dengan payload terlalu besar
    small_cover = Image.new('RGB', (50, 50), color='red')
    capacity = (50 * 50 * 3) // 8
    print(f"✅ Small cover: {small_cover.size}")
    print(f"   Raw capacity: {capacity} bytes")
    
    # Payload lebih besar dari capacity
    oversized_payload = b"X" * (capacity + 100)
    print(f"✅ Oversized payload: {len(oversized_payload)} bytes (melebihi capacity)")
    
    # Coba embed (harus error)
    positions_over = generate_positions(50, 50, "over_key", len(oversized_payload) * 8)
    
    try:
        stego_over = embed_lsb(small_cover, oversized_payload, positions_over)
        print("❌ TEST 5 FAILED! Should reject oversized payload!")
    except Exception as validation_error:
        print(f"✅ Validation error caught: {type(validation_error).__name__}")
        print(f"   Message: {str(validation_error)[:80]}...")
        print("✅ TEST 5 PASSED! Oversized payload correctly rejected")
        
except Exception as e:
    print(f"❌ TEST 5 ERROR: {e}")

print()
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY - MANUAL TESTS T10")
print("=" * 70)
print()
print("Hasil yang diharapkan:")
print("  ✅ TEST 1: Basic embedding works with real metrics")
print("  ✅ TEST 2: Alpha channel preserved 100%")
print("  ✅ TEST 3: Different keys produce different images")
print("  ✅ TEST 4: Large payloads work correctly")
print("  ✅ TEST 5: Oversized payloads rejected")
print()
print("Jika semua test PASSED, T10 implementation correct! ✅")
print("=" * 70)
