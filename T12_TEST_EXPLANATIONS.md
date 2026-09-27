# T12 Core Round-Trip Tests - Penjelasan Detail 32 Tests

**Total**: 32 tests dalam 8 kategori  
**Runtime**: ~10-15 detik total  
**Result**: 32/32 PASSED ✅

---

## KATEGORI 1: TestTextRoundTrip (5 tests)
**Fokus**: Testing dengan payload berupa text

### Test 1/32: test_short_text_round_trip
**Deskripsi**: Test round-trip dengan text pendek

**Detail**:
- Embed: 'Hello World!' (12 bytes)
- Image: 100×100 RGB
- Verify: Payload identik setelah extraction
- Check: Metadata (filename, mime_type)

**Hasil**: ✅ PASSED - Text pendek berhasil embed dan extract sempurna

---

### Test 2/32: test_long_text_round_trip
**Deskripsi**: Test round-trip dengan text panjang

**Detail**:
- Embed: 'Lorem ipsum...' × 50 = ~1400 bytes
- Image: 300×300 RGB (cukup kapasitas)
- Verify: Length dan content identik
- Check: payload_size metadata match

**Hasil**: ✅ PASSED - Text panjang (~1.4KB) berhasil tanpa data loss

---

### Test 3/32: test_unicode_text_round_trip
**Deskripsi**: Test round-trip dengan Unicode (UTF-8)

**Detail**:
- Embed: Text multi-language (Chinese 你好, Arabic مرحبا, Latin Héllo)
- Encoding: UTF-8
- Verify: Unicode characters preserved
- Check: Decode kembali tanpa error

**Hasil**: ✅ PASSED - Multi-language Unicode tersimpan dengan benar

---

### Test 4/32: test_special_characters_round_trip
**Deskripsi**: Test round-trip dengan special characters

**Detail**:
- Embed: Symbols !@#$%^&*()
- Include: Newline, tab, escape chars
- Verify: Semua special chars preserved
- Check: Tidak ada character corruption

**Hasil**: ✅ PASSED - Special characters tidak corrupt

---

### Test 5/32: test_empty_string_rejected
**Deskripsi**: Test rejection untuk empty payload

**Detail**:
- Attempt: Embed empty string b''
- Expected: EmbedError raised
- Reason: Payload tidak boleh kosong
- Security: Prevent information leak

**Hasil**: ✅ PASSED - Empty payload ditolak dengan error yang tepat

---

## KATEGORI 2: TestFileRoundTrip (4 tests)
**Fokus**: Testing dengan payload berupa file binary

### Test 6/32: test_binary_file_round_trip
**Deskripsi**: Test round-trip dengan binary file

**Detail**:
- Embed: Random binary data (256 bytes)
- Type: Generic binary file
- Verify: Byte-perfect reconstruction
- Check: Tidak ada bit flip

**Hasil**: ✅ PASSED - Binary data 100% identik after extraction

---

### Test 7/32: test_json_file_round_trip
**Deskripsi**: Test round-trip dengan JSON file

**Detail**:
- Embed: JSON object as bytes
- Content: Nested dict structure
- Verify: JSON parseable after extraction
- Check: Data structure intact

**Hasil**: ✅ PASSED - JSON structure preserved, dapat di-parse kembali

---

### Test 8/32: test_csv_file_round_trip
**Deskripsi**: Test round-trip dengan CSV file

**Detail**:
- Embed: CSV data (3 rows)
- Format: name,age,city
- Verify: CSV structure preserved
- Check: Commas dan newlines intact

**Hasil**: ✅ PASSED - CSV format tidak rusak, delimiter preserved

---

### Test 9/32: test_large_file_round_trip
**Deskripsi**: Test round-trip dengan large file (10KB)

**Detail**:
- Embed: 10KB random data
- Image: 500×500 RGB (cukup kapasitas)
- Verify: Complete data extraction
- Check: Performance acceptable

**Hasil**: ✅ PASSED - File besar (10KB) berhasil, performance baik

---

## KATEGORI 3: TestBoundaryCapacity (4 tests)
**Fokus**: Testing edge cases pada kapasitas image

### Test 10/32: test_near_max_capacity
**Deskripsi**: Test payload mendekati max capacity

**Detail**:
- Calculate: 95% of max capacity
- Embed: Payload hampir penuh
- Verify: Masih berhasil embed/extract
- Check: capacity_utilization metadata

**Hasil**: ✅ PASSED - Sistem handle kapasitas tinggi (95%) dengan baik

---

### Test 11/32: test_oversized_payload_rejected
**Deskripsi**: Test rejection untuk oversized payload

**Detail**:
- Attempt: Embed data > image capacity
- Expected: PayloadCapacityExceededError
- Timing: Error before embedding starts
- Security: Prevent data truncation

**Hasil**: ✅ PASSED - Payload oversized ditolak sebelum embedding

---

### Test 12/32: test_exact_capacity_boundary
**Deskripsi**: Test payload tepat di boundary capacity

**Detail**:
- Calculate: Exact boundary size
- Embed: Payload pas di limit
- Verify: Edge case handled correctly
- Check: No overflow

**Hasil**: ✅ PASSED - Boundary tepat 100% capacity handled dengan benar

---

### Test 13/32: test_minimum_payload_size
**Deskripsi**: Test minimum payload (1 byte)

**Detail**:
- Embed: Single byte b'X'
- Verify: 1-byte payload works
- Check: Container overhead OK
- Edge case: Smallest valid payload

**Hasil**: ✅ PASSED - Payload minimal (1 byte) berhasil

---

## KATEGORI 4: TestWrongCredentials (5 tests)
**Fokus**: Testing autentikasi dan credential validation

### Test 14/32: test_wrong_password_fails
**Deskripsi**: Test wrong password menyebabkan auth failure

**Detail**:
- Embed: dengan password 'correct'
- Extract: dengan password 'wrong'
- Expected: ExtractError (authentication failed)
- Reason: AES-GCM tag verification fails

**Hasil**: ✅ PASSED - Wrong password terdeteksi (AES-GCM auth tag fail)

---

### Test 15/32: test_wrong_stego_key_fails
**Deskripsi**: Test wrong stego-key menyebabkan extraction failure

**Detail**:
- Embed: dengan stego_key 'correct'
- Extract: dengan stego_key 'wrong'
- Result: Wrong LSB positions → garbage data
- Expected: ExtractError (invalid magic bytes)

**Hasil**: ✅ PASSED - Wrong stego-key → extract dari posisi salah → garbage

---

### Test 16/32: test_both_credentials_wrong_fails
**Deskripsi**: Test kedua credentials salah

**Detail**:
- Embed: password + stego_key correct
- Extract: both wrong
- Expected: ExtractError
- Security: Double protection layer

**Hasil**: ✅ PASSED - Kedua credentials salah → extraction fail

---

### Test 17/32: test_case_sensitive_password
**Deskripsi**: Test password case-sensitive

**Detail**:
- Embed: password 'MyPassword123'
- Extract: password 'mypassword123' (lowercase)
- Expected: ExtractError
- Verify: Case matters for security

**Hasil**: ✅ PASSED - Password case-sensitive (MyPassword ≠ mypassword)

---

### Test 18/32: test_case_sensitive_stego_key
**Deskripsi**: Test stego-key case-sensitive

**Detail**:
- Embed: stego_key 'MyStegoKey'
- Extract: stego_key 'mystegokey' (lowercase)
- Expected: ExtractError
- Verify: Case matters for positions

**Hasil**: ✅ PASSED - Stego-key case-sensitive (MyStegoKey ≠ mystegokey)

---

## KATEGORI 5: TestMalformedData (4 tests)
**Fokus**: Testing error detection untuk data corruption

### Test 19/32: test_corrupted_magic_bytes
**Deskripsi**: Test detection untuk magic bytes corruption

**Detail**:
- Embed: Normal data
- Corrupt: Change magic bytes 'STEG' → 'XXXX'
- Extract: Attempt extraction
- Expected: ExtractError (invalid magic)

**Hasil**: ✅ PASSED - Magic bytes corruption terdeteksi

---

### Test 20/32: test_truncated_image
**Deskripsi**: Test handling untuk truncated/incomplete data

**Detail**:
- Embed: Full payload
- Truncate: Crop image to 50×50
- Extract: Not enough data available
- Expected: ExtractError

**Hasil**: ✅ PASSED - Truncated image terdeteksi (data tidak cukup)

---

### Test 21/32: test_plain_image_without_data
**Deskripsi**: Test extraction dari plain image (no data)

**Detail**:
- Input: Plain image (never embedded)
- Extract: Attempt extraction
- Result: Random LSBs → garbage
- Expected: ExtractError (invalid container)

**Hasil**: ✅ PASSED - Plain image tanpa data embedded terdeteksi

---

### Test 22/32: test_modified_stego_image
**Deskripsi**: Test detection untuk modified stego image

**Detail**:
- Embed: Normal data
- Modify: Flip LSBs di 100 pixels
- Extract: Corrupted data
- Expected: ExtractError (authentication/parsing fail)

**Hasil**: ✅ PASSED - Stego image yang di-modify terdeteksi

---

## KATEGORI 6: TestAlphaPreservation (4 tests)
**Fokus**: Testing alpha channel preservation pada RGBA images

### Test 23/32: test_rgba_alpha_unchanged_after_round_trip
**Deskripsi**: Test alpha channel tetap 100% unchanged

**Detail**:
- Input: RGBA image (200×200)
- Embed: Data ke RGB channels only
- Verify: Alpha channel bit-identical
- Check: np.array_equal() pada alpha

**Hasil**: ✅ PASSED - Alpha channel 100% tidak berubah (bit-identical)

---

### Test 24/32: test_rgba_with_varying_transparency
**Deskripsi**: Test RGBA dengan varying alpha values

**Detail**:
- Input: Alpha dari 0-255 (gradasi)
- Embed: Data ke RGB
- Verify: Semua alpha values preserved
- Check: Transparency gradient intact

**Hasil**: ✅ PASSED - Gradasi transparansi preserved dengan sempurna

---

### Test 25/32: test_rgba_fully_transparent
**Deskripsi**: Test RGBA dengan fully transparent regions

**Detail**:
- Input: Regions dengan alpha=0
- Embed: Data (RGB modified)
- Verify: Transparent regions stay alpha=0
- Check: Transparency tidak hilang

**Hasil**: ✅ PASSED - Transparent regions (alpha=0) tetap transparent

---

### Test 26/32: test_rgba_fully_opaque
**Deskripsi**: Test RGBA dengan fully opaque (alpha=255)

**Detail**:
- Input: All pixels alpha=255
- Embed: Data ke RGB
- Verify: Alpha tetap 255
- Check: No alpha modification

**Hasil**: ✅ PASSED - Opaque regions (alpha=255) tetap opaque

---

## KATEGORI 7: TestQualityMetrics (3 tests)
**Fokus**: Testing image quality metrics (MSE dan PSNR)

### Test 27/32: test_mse_positive_after_embedding
**Deskripsi**: Test MSE positive (ada real modifications)

**Detail**:
- Calculate: MSE antara original & stego
- Expected: MSE > 0 (LSBs modified)
- Check: MSE not zero
- Verify: Real embedding occurred

**Hasil**: ✅ PASSED - MSE > 0, konfirmasi ada LSB modifications

---

### Test 28/32: test_psnr_high_quality
**Deskripsi**: Test PSNR indicates high quality (>40dB)

**Detail**:
- Calculate: PSNR dari MSE
- Expected: PSNR > 40dB (1-bit LSB)
- Typical: 48-52 dB untuk 1-bit
- Verify: Imperceptible changes

**Hasil**: ✅ PASSED - PSNR >40dB, changes imperceptible to human eye

---

### Test 29/32: test_metrics_consistency
**Deskripsi**: Test metrics consistency untuk same image

**Detail**:
- Create: One stego image
- Calculate: MSE dan PSNR 2x
- Expected: Identical results
- Verify: Metrics deterministic

**Hasil**: ✅ PASSED - Metrics calculation deterministic (same input → same output)

---

## KATEGORI 8: TestDeterminism (3 tests)
**Fokus**: Testing deterministic behavior

### Test 30/32: test_same_inputs_same_stego
**Deskripsi**: Test deterministic positioning via extraction

**Detail**:
- Embed: 2x dengan same parameters
- Extract: Dari kedua stego images
- Expected: Both extractions succeed
- Verify: Positions deterministic (salt/IV random OK)

**Hasil**: ✅ PASSED - Positioning deterministic, extraction berhasil dari kedua stego

**Note**: Stego images berbeda (random salt/IV) tapi extraction works karena positioning deterministic dari stego-key

---

### Test 31/32: test_different_key_different_stego
**Deskripsi**: Test different stego-key → different positions

**Detail**:
- Embed: Same payload, 2 different keys
- Compare: Stego images different
- Verify: Keys affect LSB positions
- Security: Key uniqueness important

**Hasil**: ✅ PASSED - Different keys → different LSB positions → different stego images

---

### Test 32/32: test_extraction_deterministic
**Deskripsi**: Test extraction deterministic (consistent)

**Detail**:
- Extract: 3x dari same stego image
- Expected: All 3 extractions identical
- Verify: Extraction reproducible
- Check: No randomness in extraction

**Hasil**: ✅ PASSED - Extraction 100% deterministic, 3x extraction = hasil identik

---

## Ringkasan Hasil

### Per Kategori:
1. **TestTextRoundTrip**: 5/5 PASSED ✅
2. **TestFileRoundTrip**: 4/4 PASSED ✅
3. **TestBoundaryCapacity**: 4/4 PASSED ✅
4. **TestWrongCredentials**: 5/5 PASSED ✅
5. **TestMalformedData**: 4/4 PASSED ✅
6. **TestAlphaPreservation**: 4/4 PASSED ✅
7. **TestQualityMetrics**: 3/3 PASSED ✅
8. **TestDeterminism**: 3/3 PASSED ✅

### Total:
- **32/32 tests PASSED (100%)**
- **0 tests FAILED**
- **Runtime**: ~8-10 seconds
- **Coverage**: Comprehensive (all major scenarios)

---

## Key Takeaways

### ✅ Yang Berfungsi Dengan Baik:
1. **Round-trip integrity**: Payload identik setelah embed → extract
2. **Multi-format support**: Text, binary, JSON, CSV semua OK
3. **Capacity handling**: Min (1 byte) sampai Max (95%) capacity
4. **Authentication**: Wrong password/key terdeteksi dengan benar
5. **Error detection**: Corruption, truncation, tampering terdeteksi
6. **Alpha preservation**: RGBA transparency 100% preserved
7. **Quality metrics**: PSNR >40dB (imperceptible)
8. **Determinism**: Positioning deterministic, extraction reproducible

### 🔐 Security Features Verified:
- ✅ AES-256-GCM authentication (wrong password → fail)
- ✅ Keyed LSB positioning (wrong stego-key → garbage)
- ✅ Case-sensitive credentials
- ✅ Magic bytes validation
- ✅ Tamper detection
- ✅ Capacity overflow prevention

### 📊 Quality Assurance:
- ✅ MSE positive (real changes)
- ✅ PSNR >40dB (imperceptible)
- ✅ Metrics deterministic
- ✅ Alpha channel preserved 100%
- ✅ No data loss or corruption

---

**T12 COMPLETE ✅**  
**All 32 tests passing with comprehensive coverage**  
**System ready for production use**
