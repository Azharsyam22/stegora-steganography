"""
T12 Automatic Step-by-Step Test Runner with Explanations
Runs all 32 tests automatically with detailed explanations
"""
import subprocess
import sys
import time

# Test definitions (same as before but runs automatically)
TESTS = [
    # Category 1: TestTextRoundTrip
    {
        "name": "test_short_text_round_trip",
        "class": "TestTextRoundTrip",
        "number": 1,
        "category": "Text Payloads",
        "description": "Test round-trip dengan text pendek",
        "details": [
            "- Embed: 'Hello World!' (12 bytes)",
            "- Image: 100×100 RGB",
            "- Verify: Payload identik setelah extraction",
            "- Check: Metadata (filename, mime_type)"
        ]
    },
    {
        "name": "test_long_text_round_trip",
        "class": "TestTextRoundTrip",
        "number": 2,
        "category": "Text Payloads",
        "description": "Test round-trip dengan text panjang",
        "details": [
            "- Embed: 'Lorem ipsum...' × 50 = ~1400 bytes",
            "- Image: 300×300 RGB (cukup kapasitas)",
            "- Verify: Length dan content identik",
            "- Check: payload_size metadata match"
        ]
    },
    {
        "name": "test_unicode_text_round_trip",
        "class": "TestTextRoundTrip",
        "number": 3,
        "category": "Text Payloads",
        "description": "Test round-trip dengan Unicode (UTF-8)",
        "details": [
            "- Embed: Text multi-language (Chinese, Arabic, Latin)",
            "- Encoding: UTF-8",
            "- Verify: Unicode characters preserved",
            "- Check: Decode kembali tanpa error"
        ]
    },
    {
        "name": "test_special_characters_round_trip",
        "class": "TestTextRoundTrip",
        "number": 4,
        "category": "Text Payloads",
        "description": "Test round-trip dengan special characters",
        "details": [
            "- Embed: Symbols !@#$%^&*()",
            "- Include: Newline, tab, escape chars",
            "- Verify: Semua special chars preserved",
            "- Check: Tidak ada character corruption"
        ]
    },
    {
        "name": "test_empty_string_rejected",
        "class": "TestTextRoundTrip",
        "number": 5,
        "category": "Text Payloads",
        "description": "Test rejection untuk empty payload",
        "details": [
            "- Attempt: Embed empty string b''",
            "- Expected: EmbedError raised",
            "- Reason: Payload tidak boleh kosong",
            "- Security: Prevent information leak"
        ]
    },
    
    # Category 2: TestFileRoundTrip
    {
        "name": "test_binary_file_round_trip",
        "class": "TestFileRoundTrip",
        "number": 6,
        "category": "File Payloads",
        "description": "Test round-trip dengan binary file",
        "details": [
            "- Embed: Random binary data (256 bytes)",
            "- Type: Generic binary file",
            "- Verify: Byte-perfect reconstruction",
            "- Check: Tidak ada bit flip"
        ]
    },
    {
        "name": "test_json_file_round_trip",
        "class": "TestFileRoundTrip",
        "number": 7,
        "category": "File Payloads",
        "description": "Test round-trip dengan JSON file",
        "details": [
            "- Embed: JSON object as bytes",
            "- Content: Nested dict structure",
            "- Verify: JSON parseable after extraction",
            "- Check: Data structure intact"
        ]
    },
    {
        "name": "test_csv_file_round_trip",
        "class": "TestFileRoundTrip",
        "number": 8,
        "category": "File Payloads",
        "description": "Test round-trip dengan CSV file",
        "details": [
            "- Embed: CSV data (3 rows)",
            "- Format: name,age,city",
            "- Verify: CSV structure preserved",
            "- Check: Commas dan newlines intact"
        ]
    },
    {
        "name": "test_large_file_round_trip",
        "class": "TestFileRoundTrip",
        "number": 9,
        "category": "File Payloads",
        "description": "Test round-trip dengan large file (10KB)",
        "details": [
            "- Embed: 10KB random data",
            "- Image: 500×500 RGB (cukup kapasitas)",
            "- Verify: Complete data extraction",
            "- Check: Performance acceptable"
        ]
    },
    
    # Category 3: TestBoundaryCapacity
    {
        "name": "test_near_max_capacity",
        "class": "TestBoundaryCapacity",
        "number": 10,
        "category": "Capacity Boundaries",
        "description": "Test payload mendekati max capacity",
        "details": [
            "- Calculate: 95% of max capacity",
            "- Embed: Payload hampir penuh",
            "- Verify: Masih berhasil embed/extract",
            "- Check: capacity_utilization metadata"
        ]
    },
    {
        "name": "test_oversized_payload_rejected",
        "class": "TestBoundaryCapacity",
        "number": 11,
        "category": "Capacity Boundaries",
        "description": "Test rejection untuk oversized payload",
        "details": [
            "- Attempt: Embed data > image capacity",
            "- Expected: PayloadCapacityExceededError",
            "- Timing: Error before embedding starts",
            "- Security: Prevent data truncation"
        ]
    },
    {
        "name": "test_exact_capacity_boundary",
        "class": "TestBoundaryCapacity",
        "number": 12,
        "category": "Capacity Boundaries",
        "description": "Test payload tepat di boundary capacity",
        "details": [
            "- Calculate: Exact boundary size",
            "- Embed: Payload pas di limit",
            "- Verify: Edge case handled correctly",
            "- Check: No overflow"
        ]
    },
    {
        "name": "test_minimum_payload_size",
        "class": "TestBoundaryCapacity",
        "number": 13,
        "category": "Capacity Boundaries",
        "description": "Test minimum payload (1 byte)",
        "details": [
            "- Embed: Single byte b'X'",
            "- Verify: 1-byte payload works",
            "- Check: Container overhead OK",
            "- Edge case: Smallest valid payload"
        ]
    },
    
    # Category 4: TestWrongCredentials
    {
        "name": "test_wrong_password_fails",
        "class": "TestWrongCredentials",
        "number": 14,
        "category": "Authentication",
        "description": "Test wrong password menyebabkan auth failure",
        "details": [
            "- Embed: dengan password 'correct'",
            "- Extract: dengan password 'wrong'",
            "- Expected: ExtractError (authentication failed)",
            "- Reason: AES-GCM tag verification fails"
        ]
    },
    {
        "name": "test_wrong_stego_key_fails",
        "class": "TestWrongCredentials",
        "number": 15,
        "category": "Authentication",
        "description": "Test wrong stego-key menyebabkan extraction failure",
        "details": [
            "- Embed: dengan stego_key 'correct'",
            "- Extract: dengan stego_key 'wrong'",
            "- Result: Wrong LSB positions → garbage data",
            "- Expected: ExtractError (invalid magic bytes)"
        ]
    },
    {
        "name": "test_both_credentials_wrong_fails",
        "class": "TestWrongCredentials",
        "number": 16,
        "category": "Authentication",
        "description": "Test kedua credentials salah",
        "details": [
            "- Embed: password + stego_key correct",
            "- Extract: both wrong",
            "- Expected: ExtractError",
            "- Security: Double protection layer"
        ]
    },
    {
        "name": "test_case_sensitive_password",
        "class": "TestWrongCredentials",
        "number": 17,
        "category": "Authentication",
        "description": "Test password case-sensitive",
        "details": [
            "- Embed: password 'MyPassword123'",
            "- Extract: password 'mypassword123' (lowercase)",
            "- Expected: ExtractError",
            "- Verify: Case matters for security"
        ]
    },
    {
        "name": "test_case_sensitive_stego_key",
        "class": "TestWrongCredentials",
        "number": 18,
        "category": "Authentication",
        "description": "Test stego-key case-sensitive",
        "details": [
            "- Embed: stego_key 'MyStegoKey'",
            "- Extract: stego_key 'mystegokey' (lowercase)",
            "- Expected: ExtractError",
            "- Verify: Case matters for positions"
        ]
    },
    
    # Category 5: TestMalformedData
    {
        "name": "test_corrupted_magic_bytes",
        "class": "TestMalformedData",
        "number": 19,
        "category": "Error Detection",
        "description": "Test detection untuk magic bytes corruption",
        "details": [
            "- Embed: Normal data",
            "- Corrupt: Change magic bytes 'STEG' → 'XXXX'",
            "- Extract: Attempt extraction",
            "- Expected: ExtractError (invalid magic)"
        ]
    },
    {
        "name": "test_truncated_image",
        "class": "TestMalformedData",
        "number": 20,
        "category": "Error Detection",
        "description": "Test handling untuk truncated/incomplete data",
        "details": [
            "- Embed: Full payload",
            "- Truncate: Crop image to 50×50",
            "- Extract: Not enough data available",
            "- Expected: ExtractError"
        ]
    },
    {
        "name": "test_plain_image_without_data",
        "class": "TestMalformedData",
        "number": 21,
        "category": "Error Detection",
        "description": "Test extraction dari plain image (no data)",
        "details": [
            "- Input: Plain image (never embedded)",
            "- Extract: Attempt extraction",
            "- Result: Random LSBs → garbage",
            "- Expected: ExtractError (invalid container)"
        ]
    },
    {
        "name": "test_modified_stego_image",
        "class": "TestMalformedData",
        "number": 22,
        "category": "Error Detection",
        "description": "Test detection untuk modified stego image",
        "details": [
            "- Embed: Normal data",
            "- Modify: Flip LSBs di 100 pixels",
            "- Extract: Corrupted data",
            "- Expected: ExtractError (authentication/parsing fail)"
        ]
    },
    
    # Category 6: TestAlphaPreservation
    {
        "name": "test_rgba_alpha_unchanged_after_round_trip",
        "class": "TestAlphaPreservation",
        "number": 23,
        "category": "RGBA Support",
        "description": "Test alpha channel tetap 100% unchanged",
        "details": [
            "- Input: RGBA image (200×200)",
            "- Embed: Data ke RGB channels only",
            "- Verify: Alpha channel bit-identical",
            "- Check: np.array_equal() pada alpha"
        ]
    },
    {
        "name": "test_rgba_with_varying_transparency",
        "class": "TestAlphaPreservation",
        "number": 24,
        "category": "RGBA Support",
        "description": "Test RGBA dengan varying alpha values",
        "details": [
            "- Input: Alpha dari 0-255 (gradasi)",
            "- Embed: Data ke RGB",
            "- Verify: Semua alpha values preserved",
            "- Check: Transparency gradient intact"
        ]
    },
    {
        "name": "test_rgba_fully_transparent",
        "class": "TestAlphaPreservation",
        "number": 25,
        "category": "RGBA Support",
        "description": "Test RGBA dengan fully transparent regions",
        "details": [
            "- Input: Regions dengan alpha=0",
            "- Embed: Data (RGB modified)",
            "- Verify: Transparent regions stay alpha=0",
            "- Check: Transparency tidak hilang"
        ]
    },
    {
        "name": "test_rgba_fully_opaque",
        "class": "TestAlphaPreservation",
        "number": 26,
        "category": "RGBA Support",
        "description": "Test RGBA dengan fully opaque (alpha=255)",
        "details": [
            "- Input: All pixels alpha=255",
            "- Embed: Data ke RGB",
            "- Verify: Alpha tetap 255",
            "- Check: No alpha modification"
        ]
    },
    
    # Category 7: TestQualityMetrics
    {
        "name": "test_mse_positive_after_embedding",
        "class": "TestQualityMetrics",
        "number": 27,
        "category": "Image Quality",
        "description": "Test MSE positive (ada real modifications)",
        "details": [
            "- Calculate: MSE antara original & stego",
            "- Expected: MSE > 0 (LSBs modified)",
            "- Check: MSE not zero",
            "- Verify: Real embedding occurred"
        ]
    },
    {
        "name": "test_psnr_high_quality",
        "class": "TestQualityMetrics",
        "number": 28,
        "category": "Image Quality",
        "description": "Test PSNR indicates high quality (>40dB)",
        "details": [
            "- Calculate: PSNR dari MSE",
            "- Expected: PSNR > 40dB (1-bit LSB)",
            "- Typical: 48-52 dB untuk 1-bit",
            "- Verify: Imperceptible changes"
        ]
    },
    {
        "name": "test_metrics_consistency",
        "class": "TestQualityMetrics",
        "number": 29,
        "category": "Image Quality",
        "description": "Test metrics consistency untuk same image",
        "details": [
            "- Create: One stego image",
            "- Calculate: MSE dan PSNR 2x",
            "- Expected: Identical results",
            "- Verify: Metrics deterministic"
        ]
    },
    
    # Category 8: TestDeterminism
    {
        "name": "test_same_inputs_same_stego",
        "class": "TestDeterminism",
        "number": 30,
        "category": "Determinism",
        "description": "Test deterministic positioning via extraction",
        "details": [
            "- Embed: 2x dengan same parameters",
            "- Extract: Dari kedua stego images",
            "- Expected: Both extractions succeed",
            "- Verify: Positions deterministic (salt/IV random OK)"
        ]
    },
    {
        "name": "test_different_key_different_stego",
        "class": "TestDeterminism",
        "number": 31,
        "category": "Determinism",
        "description": "Test different stego-key → different positions",
        "details": [
            "- Embed: Same payload, 2 different keys",
            "- Compare: Stego images different",
            "- Verify: Keys affect LSB positions",
            "- Security: Key uniqueness important"
        ]
    },
    {
        "name": "test_extraction_deterministic",
        "class": "TestDeterminism",
        "number": 32,
        "category": "Determinism",
        "description": "Test extraction deterministic (consistent)",
        "details": [
            "- Extract: 3x dari same stego image",
            "- Expected: All 3 extractions identical",
            "- Verify: Extraction reproducible",
            "- Check: No randomness in extraction"
        ]
    },
]

def print_header():
    print("\n" + "="*80)
    print("T12 AUTOMATIC STEP-BY-STEP TEST RUNNER")
    print("32 Tests Total - Running Automatically with Explanations")
    print("="*80 + "\n")

def print_test_info(test):
    print(f"\n{'='*80}")
    print(f"TEST {test['number']}/32: {test['name']}")
    print(f"Category: {test['category']} | Class: {test['class']}")
    print(f"{'='*80}")
    print(f"\nDESKRIPSI: {test['description']}\n")
    for detail in test['details']:
        print(f"   {detail}")
    print()

def run_test(test):
    test_path = f"tests/test_core_roundtrip.py::{test['class']}::{test['name']}"
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-q", "--tb=no"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0 or "1 passed" in result.stdout:
        print(f"[PASSED]\n")
        return True
    else:
        print(f"[FAILED]")
        print(f"Output: {result.stdout}\n")
        return False

def main():
    print_header()
    
    passed = 0
    failed = 0
    start_time = time.time()
    
    for test in TESTS:
        print_test_info(test)
        
        if run_test(test):
            passed += 1
        else:
            failed += 1
    
    elapsed = time.time() - start_time
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"[PASSED]: {passed}/32")
    print(f"[FAILED]: {failed}/32")
    print(f"Success Rate: {passed/32*100:.1f}%")
    print(f"Total Time: {elapsed:.2f}s")
    print("="*80 + "\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
