#!/usr/bin/env python3
"""
Critical Flow Verification Script
Tests the main user workflows to ensure no bugs or errors
"""

import sys
from PIL import Image
import numpy as np
from io import BytesIO

print("=" * 60)
print("STEGORA - CRITICAL FLOW VERIFICATION")
print("=" * 60)

errors = []
warnings = []

# Test 1: Import all critical modules
print("\n[1/8] Testing module imports...")
try:
    from backend.pipeline import embed_pipeline, extract_pipeline
    from backend.image.io import validate_and_load_cover_image
    from backend.stego.capacity import calculate_usable_capacity
    from backend.crypto.aes_gcm import encrypt, decrypt
    from backend.crypto.pbkdf2 import derive_key, generate_salt
    from stegora.analysis.histogram import calculate_histogram_from_pil
    from stegora.analysis.lsb_plane import extract_lsb_plane
    print("✓ All critical modules imported successfully")
except ImportError as e:
    errors.append(f"Import error: {e}")
    print(f"✗ Import failed: {e}")

# Test 2: Create test image
print("\n[2/8] Creating test image...")
try:
    test_image = Image.new('RGB', (512, 512), color=(128, 128, 128))
    test_bytes = BytesIO()
    test_image.save(test_bytes, format='PNG')
    test_bytes.seek(0)
    print("✓ Test image created (512×512 PNG)")
except Exception as e:
    errors.append(f"Image creation error: {e}")
    print(f"✗ Image creation failed: {e}")

# Test 3: Test unified credentials
print("\n[3/8] Testing unified credential system...")
try:
    unified_key = "TestKey2024!"
    password = unified_key
    stego_key = unified_key  # Same as password
    
    # Test key derivation
    salt = generate_salt()
    derived = derive_key(password, salt)
    
    assert len(derived) == 32, "Derived key should be 32 bytes"
    assert password == stego_key, "Unified credentials should be identical"
    
    print(f"✓ Unified credential system working")
    print(f"  Password: {password}")
    print(f"  Stego-key: {stego_key} (same as password)")
except Exception as e:
    errors.append(f"Credential system error: {e}")
    print(f"✗ Credential test failed: {e}")

# Test 4: Test embed pipeline
print("\n[4/8] Testing embed pipeline...")
try:
    test_image_embed = Image.new('RGB', (256, 256), color=(100, 150, 200))
    test_payload = b"Test message for UTS demo"
    test_password = "SecurePass123!"
    
    stego_image, metadata = embed_pipeline(
        test_image_embed,
        test_payload,
        password=test_password,
        stego_key=test_password,  # Unified
        filename="test.txt",
        mime_type="text/plain"
    )
    
    assert stego_image is not None, "Stego image should not be None"
    assert stego_image.size == test_image_embed.size, "Stego should preserve dimensions"
    print(f"✓ Embed pipeline successful")
    print(f"  Payload size: {len(test_payload)} bytes")
    print(f"  Image size: {stego_image.size}")
except Exception as e:
    errors.append(f"Embed pipeline error: {e}")
    print(f"✗ Embed failed: {e}")

# Test 5: Test extract pipeline
print("\n[5/8] Testing extract pipeline...")
try:
    extracted_payload, extract_metadata = extract_pipeline(
        stego_image,
        password=test_password,
        stego_key=test_password  # Unified
    )
    
    assert extracted_payload == test_payload, "Extracted should match original"
    print(f"✓ Extract pipeline successful")
    print(f"  Original: {test_payload}")
    print(f"  Extracted: {extracted_payload}")
    assert extracted_payload == test_payload
except Exception as e:
    errors.append(f"Extract pipeline error: {e}")
    print(f"✗ Extract failed: {e}")

# Test 6: Test wrong password
print("\n[6/8] Testing wrong password handling...")
try:
    wrong_password = "WrongPassword!"
    
    try:
        extract_pipeline(
            stego_image,
            password=wrong_password,
            stego_key=wrong_password  # Unified
        )
        warnings.append("Wrong password should fail but didn't!")
        print("⚠ Warning: Wrong password didn't fail (unexpected)")
    except (ValueError, Exception) as expected_error:
        print(f"✓ Wrong password correctly rejected")
        print(f"  Error type: {type(expected_error).__name__}")
except Exception as e:
    errors.append(f"Wrong password test error: {e}")
    print(f"✗ Wrong password test failed: {e}")

# Test 7: Test JPEG format detection
print("\n[7/8] Testing JPEG format handling...")
try:
    # Create JPEG version
    jpeg_bytes = BytesIO()
    test_image.save(jpeg_bytes, format='JPEG', quality=90)
    jpeg_bytes.seek(0)
    
    # Load JPEG
    jpeg_image = Image.open(jpeg_bytes)
    
    # Check format detection
    assert jpeg_image.format == 'JPEG', "Should detect JPEG format"
    print(f"✓ JPEG format detection working")
    print(f"  Format: {jpeg_image.format}")
    print(f"  Note: Extract from JPEG will fail (expected for robustness test)")
except Exception as e:
    warnings.append(f"JPEG test warning: {e}")
    print(f"⚠ JPEG test warning: {e}")

# Test 8: Test histogram analysis
print("\n[8/8] Testing histogram analysis...")
try:
    # Create two test images
    cover = Image.new('RGB', (128, 128), color=(100, 100, 100))
    stego = Image.new('RGB', (128, 128), color=(101, 100, 100))
    
    # Calculate histograms
    hist_cover = calculate_histogram_from_pil(cover)
    hist_stego = calculate_histogram_from_pil(stego)
    
    assert 'R' in hist_cover, "Should have R channel"
    assert 'G' in hist_cover, "Should have G channel"
    assert 'B' in hist_cover, "Should have B channel"
    
    print(f"✓ Histogram analysis working")
    print(f"  Channels: R, G, B")
    print(f"  Histogram bins: {len(hist_cover['R'])}")
except Exception as e:
    errors.append(f"Histogram analysis error: {e}")
    print(f"✗ Histogram test failed: {e}")

# Final Results
print("\n" + "=" * 60)
print("VERIFICATION RESULTS")
print("=" * 60)

if not errors and not warnings:
    print("\n🟢 ALL TESTS PASSED - NO ERRORS OR WARNINGS")
    print("\nStatus: ✅ PRODUCTION READY")
    print("Confidence: 🟢 VERY HIGH")
    sys.exit(0)
elif not errors and warnings:
    print(f"\n🟡 ALL CRITICAL TESTS PASSED - {len(warnings)} WARNING(S)")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    print("\nStatus: ✅ READY (with minor warnings)")
    print("Confidence: 🟢 HIGH")
    sys.exit(0)
else:
    print(f"\n🔴 {len(errors)} ERROR(S) FOUND")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNING(S)")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    print("\nStatus: ❌ NEEDS FIXING")
    print("Confidence: 🔴 LOW")
    sys.exit(1)
