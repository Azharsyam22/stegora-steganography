"""
Manual Test T11 - LSB Extraction Step by Step
Naufal (247006111158)

Test ini memverifikasi:
1. Basic extraction works
2. Round-trip (embed → extract) identical
3. Wrong key produces garbage (safe failure)
4. Bit-level accuracy
5. Integration with pipeline
"""
from PIL import Image
import numpy as np
from backend.stego.lsb import embed_lsb, extract_lsb
from backend.stego.positions import generate_positions
from backend.image.metrics import calculate_mse, calculate_psnr
from backend.pipeline import embed_pipeline, extract_pipeline

print("=" * 70)
print("MANUAL TEST T11 - 1-BIT RGB LSB EXTRACTION")
print("=" * 70)
print()

# ============================================================================
# TEST 1: Basic Extraction (RGB)
# ============================================================================
print("TEST 1: Basic Extraction (RGB)")
print("-" * 70)
print("Tujuan: Verify basic extraction berfungsi pada RGB image")
print()

try:
    # Create cover image
    cover = Image.new('RGB', (100, 100), color='white')
    print(f"✅ Cover created: {cover.size}, mode={cover.mode}")
    
    # Payload
    payload_original = b"Hello T11 Extraction Test!"
    print(f"✅ Original payload: {len(payload_original)} bytes")
    print(f"   Content: {payload_original.decode('utf-8')}")
    
    # Generate positions
    num_bits = len(payload_original) * 8
    positions = generate_positions(100, 100, "test_key_extraction", num_bits)
    print(f"✅ Generated {len(positions)} positions")
    
    # EMBED first
    stego = embed_lsb(cover, payload_original, positions)
    print(f"✅ Embedded into stego image")
    
    # EXTRACT (T11)
    payload_extracted = extract_lsb(stego, positions, len(payload_original))
    print(f"✅ Extracted: {len(payload_extracted)} bytes")
    print(f"   Content: {payload_extracted.decode('utf-8')}")
    
    # VERIFY identical
    if payload_extracted == payload_original:
        print("✅ VERIFICATION: Extracted payload IDENTICAL to original")
        print("✅ TEST 1 PASSED!")
    else:
        print("❌ TEST 1 FAILED! Payloads don't match")
        print(f"   Expected: {payload_original}")
        print(f"   Got:      {payload_extracted}")
        
except Exception as e:
    print(f"❌ TEST 1 ERROR: {e}")

print()
print()

# ============================================================================
# TEST 2: Round-Trip with Various Payloads
# ============================================================================
print("TEST 2: Round-Trip with Various Payloads")
print("-" * 70)
print("Tujuan: Test berbagai jenis payload (text, binary, unicode)")
print()

test_payloads = [
    (b"Short", "Short text"),
    (b"A" * 100, "Repeated character (100 bytes)"),
    (b"Unicode: \xc3\xa9\xc3\xa7\xc3\xb1", "Unicode characters"),
    (b"\x00\x01\x02\xff\xfe\xfd", "Binary data with extremes"),
    (bytes(range(50)), "Sequential bytes 0-49"),
]

cover = Image.new('RGB', (150, 150), color='blue')
all_passed = True

for idx, (payload, description) in enumerate(test_payloads):
    try:
        print(f"Test 2.{idx+1}: {description}")
        
        # Generate unique positions for each test
        key = f"round_trip_key_{idx}"
        positions = generate_positions(150, 150, key, len(payload) * 8)
        
        # Embed
        stego = embed_lsb(cover, payload, positions)
        
        # Extract
        extracted = extract_lsb(stego, positions, len(payload))
        
        # Verify
        if extracted == payload:
            print(f"  ✅ PASSED: {len(payload)} bytes extracted correctly")
        else:
            print(f"  ❌ FAILED: Mismatch!")
            all_passed = False
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        all_passed = False

print()
if all_passed:
    print("✅ TEST 2 PASSED! All payloads round-trip correctly")
else:
    print("❌ TEST 2 FAILED! Some payloads didn't match")

print()
print()

# ============================================================================
# TEST 3: Wrong Stego-Key Produces Garbage
# ============================================================================
print("TEST 3: Wrong Stego-Key Behavior")
print("-" * 70)
print("Tujuan: Verify wrong key produces different (garbage) data")
print()

try:
    cover = Image.new('RGB', (100, 100), color='green')
    payload_secret = b"Secret message with correct key"
    
    # Embed with correct key
    correct_key = "correct_key_ABC"
    positions_correct = generate_positions(100, 100, correct_key, len(payload_secret) * 8)
    stego = embed_lsb(cover, payload_secret, positions_correct)
    print(f"✅ Embedded with correct key: '{correct_key}'")
    
    # Extract with CORRECT key
    extracted_correct = extract_lsb(stego, positions_correct, len(payload_secret))
    print(f"✅ Extracted with correct key: {extracted_correct.decode('utf-8', errors='replace')[:30]}")
    
    # Extract with WRONG key
    wrong_key = "wrong_key_XYZ"
    positions_wrong = generate_positions(100, 100, wrong_key, len(payload_secret) * 8)
    extracted_wrong = extract_lsb(stego, positions_wrong, len(payload_secret))
    print(f"✅ Extracted with wrong key: {extracted_wrong[:30]} (binary)")
    
    # Verify behavior
    if extracted_correct == payload_secret:
        print("  ✅ Correct key: Extracted MATCHES original")
    else:
        print("  ❌ Correct key: Should match but doesn't!")
        
    if extracted_wrong != payload_secret:
        print("  ✅ Wrong key: Extracted DIFFERS from original (garbage)")
        
        # Calculate bit error rate
        bit_errors = 0
        for i in range(len(payload_secret)):
            xor = payload_secret[i] ^ extracted_wrong[i]
            bit_errors += bin(xor).count('1')
        bit_error_rate = bit_errors / (len(payload_secret) * 8)
        print(f"  ✅ Bit error rate: {bit_error_rate:.1%} (should be ~50% for random)")
        
        if bit_error_rate > 0.3:
            print("✅ TEST 3 PASSED! Wrong key produces garbage data safely")
        else:
            print("⚠️  TEST 3 WARNING: Bit error rate unexpectedly low")
    else:
        print("  ❌ Wrong key: Should produce garbage but got original!")
        print("❌ TEST 3 FAILED!")
        
except Exception as e:
    print(f"❌ TEST 3 ERROR: {e}")

print()
print()

# ============================================================================
# TEST 4: Bit-Level Accuracy
# ============================================================================
print("TEST 4: Bit-Level Accuracy")
print("-" * 70)
print("Tujuan: Verify setiap bit extracted dengan akurat")
print()

try:
    cover = Image.new('RGB', (100, 100), color='red')
    
    # Known bit patterns
    test_bytes = bytes([
        0b10101010,  # Alternating bits
        0b11110000,  # Half on, half off
        0b00001111,  # Opposite of above
        0b11111111,  # All ones
        0b00000000,  # All zeros
    ])
    
    print(f"Test bytes (binary):")
    for i, byte in enumerate(test_bytes):
        print(f"  Byte {i}: {byte:08b} (0x{byte:02x})")
    
    # Embed and extract
    positions = generate_positions(100, 100, "bit_accuracy_key", len(test_bytes) * 8)
    stego = embed_lsb(cover, test_bytes, positions)
    extracted = extract_lsb(stego, positions, len(test_bytes))
    
    print()
    print("Extracted bytes (binary):")
    for i, byte in enumerate(extracted):
        print(f"  Byte {i}: {byte:08b} (0x{byte:02x})")
    
    # Bit-by-bit comparison
    print()
    all_bits_match = True
    for i in range(len(test_bytes)):
        if test_bytes[i] != extracted[i]:
            print(f"  ❌ Byte {i} mismatch: {test_bytes[i]:08b} != {extracted[i]:08b}")
            all_bits_match = False
    
    if all_bits_match:
        print("✅ All bits match perfectly!")
        print("✅ TEST 4 PASSED! Bit-level accuracy verified")
    else:
        print("❌ TEST 4 FAILED! Bit mismatches detected")
        
except Exception as e:
    print(f"❌ TEST 4 ERROR: {e}")

print()
print()

# ============================================================================
# TEST 5: Pipeline Integration (End-to-End)
# ============================================================================
print("TEST 5: Pipeline Integration (End-to-End)")
print("-" * 70)
print("Tujuan: Verify full pipeline (encrypt → embed → extract → decrypt)")
print()

try:
    cover_pipeline = Image.new('RGB', (200, 200), color='white')
    
    # Test data
    payload_text = b"Full pipeline test with encryption!"
    password = "testpassword123"
    stego_key = "teststegokey456"
    
    print(f"✅ Payload: {payload_text.decode('utf-8')}")
    print(f"✅ Password: {password}")
    print(f"✅ Stego-key: {stego_key}")
    print()
    
    # EMBED via pipeline
    print("EMBED PHASE:")
    stego_image, embed_meta = embed_pipeline(
        cover_image=cover_pipeline,
        payload_bytes=payload_text,
        password=password,
        stego_key=stego_key,
        filename="test.txt",
        mime_type="text/plain"
    )
    
    print(f"  ✅ Stego created: {stego_image.size}")
    print(f"  ✅ Payload size: {embed_meta['payload_size']} bytes")
    print(f"  ✅ Container size: {embed_meta['container_size']} bytes")
    print(f"  ✅ MSE: {embed_meta.get('mse', 'N/A')}")
    print(f"  ✅ PSNR: {embed_meta.get('psnr', 'N/A')} dB")
    print()
    
    # EXTRACT via pipeline
    print("EXTRACT PHASE:")
    extracted_payload, extract_meta = extract_pipeline(
        stego_image=stego_image,
        password=password,
        stego_key=stego_key
    )
    
    print(f"  ✅ Extracted: {extracted_payload.decode('utf-8')}")
    print(f"  ✅ Plaintext size: {extract_meta['plaintext_size']} bytes")
    print(f"  ✅ Filename: {extract_meta['filename']}")
    print(f"  ✅ MIME type: {extract_meta['mime_type']}")
    print(f"  ✅ Magic valid: {extract_meta['magic_valid']}")
    print(f"  ✅ Auth valid: {extract_meta['auth_valid']}")
    print()
    
    # VERIFY
    if extracted_payload == payload_text:
        print("✅ VERIFICATION: Extracted payload IDENTICAL to original")
        print("✅ TEST 5 PASSED! Full pipeline working end-to-end")
    else:
        print("❌ TEST 5 FAILED! Pipeline round-trip failed")
        print(f"   Expected: {payload_text}")
        print(f"   Got:      {extracted_payload}")
        
except Exception as e:
    print(f"❌ TEST 5 ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print()

# ============================================================================
# TEST 6: RGBA Alpha Preservation
# ============================================================================
print("TEST 6: RGBA Alpha Preservation")
print("-" * 70)
print("Tujuan: Verify alpha channel tidak digunakan untuk extraction")
print()

try:
    # RGBA image with specific alpha
    cover_rgba = Image.new('RGBA', (100, 100), color=(255, 255, 255, 128))
    alpha_original = np.array(cover_rgba)[:, :, 3].copy()
    
    print(f"✅ RGBA cover created with alpha=128")
    
    # Embed and extract
    payload_alpha = b"RGBA extraction test"
    positions_rgba = generate_positions(100, 100, "rgba_key", len(payload_alpha) * 8)
    
    stego_rgba = embed_lsb(cover_rgba, payload_alpha, positions_rgba)
    extracted_alpha = extract_lsb(stego_rgba, positions_rgba, len(payload_alpha))
    
    # Check alpha unchanged
    alpha_after = np.array(stego_rgba)[:, :, 3]
    alpha_preserved = np.array_equal(alpha_original, alpha_after)
    
    print(f"✅ Alpha preserved: {alpha_preserved}")
    print(f"✅ Payload extracted: {extracted_alpha.decode('utf-8')}")
    
    if alpha_preserved and extracted_alpha == payload_alpha:
        print("✅ TEST 6 PASSED! RGBA works with alpha preserved")
    else:
        if not alpha_preserved:
            print("❌ Alpha was modified!")
        if extracted_alpha != payload_alpha:
            print("❌ Payload doesn't match!")
        print("❌ TEST 6 FAILED!")
        
except Exception as e:
    print(f"❌ TEST 6 ERROR: {e}")

print()
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("SUMMARY - MANUAL TESTS T11")
print("=" * 70)
print()
print("Tests yang dijalankan:")
print("  ✅ TEST 1: Basic extraction (RGB)")
print("  ✅ TEST 2: Round-trip various payloads")
print("  ✅ TEST 3: Wrong key behavior")
print("  ✅ TEST 4: Bit-level accuracy")
print("  ✅ TEST 5: Pipeline integration")
print("  ✅ TEST 6: RGBA alpha preservation")
print()
print("Jika semua test PASSED:")
print("  → T11 implementation CORRECT! ✅")
print("  → Round-trip embed → extract WORKING! ✅")
print("  → Wrong key fails SAFELY! ✅")
print("  → Ready for UTS demo! 🚀")
print()
print("=" * 70)
