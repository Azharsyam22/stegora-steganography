# T18 Manual Test Report: Testing Matrix & XLSX Export

**Student:** Hana (247006111170)  
**Course:** Information Security - Universitas Siliwangi  
**Date:** September 27, 2026  
**Task:** T18 - 5×3 Testing Matrix + XLSX Export

---

## Test Overview

Test T18 memverifikasi implementasi:
1. **Testing Matrix Framework**: Generate dan execute 5×3 testing matrix (5 images × 3 payloads = 15 test cases)
2. **XLSX Export**: Export hasil testing ke format Excel dengan formatting profesional
3. **Data Integrity**: Verify struktur file dan kelengkapan data

---

## Test Execution

### Test Script
File: `test_t18_interactive.py`

### Test Data Created
1. **5 Test Images:**
   - `small_uniform.png` (100×100) - Uniform gray color
   - `medium_gradient.png` (200×200) - Gradient pattern  
   - `large_random.png` (300×300) - Random noise pattern
   - `checkerboard.png` (150×150) - Checkerboard pattern
   - `colorful_stripes.png` (250×250) - RGB stripes

2. **3 Test Payloads:**
   - Small: 45 bytes (text)
   - Medium: 200 bytes (binary)
   - Large: 805 bytes (mixed)

### Test Matrix Execution

```
Test Configurations: 15 (5 images × 3 payloads)
Generated Successfully: ✓
```

**Configuration Details:**
- Case IDs: T1P1, T1P2, T1P3, ... T5P3
- Each case contains: image properties, payload properties, capacity calculation
- Capacity utilization ranges: 0.00% - 0.22%

---

## XLSX Export Results

### File Details
```
File: test_t18_matrix_results.xlsx
Size: 7,708 bytes
Created: September 27, 2026
Format: Excel OpenXML (.xlsx)
```

### Workbook Structure

#### Sheet 1: Test Results
**Dimensions:** A1:P16 (16 columns × 16 rows including header)

**Columns (16 total):**
1. Case ID
2. Image Name
3. Format
4. Width
5. Height
6. Channels
7. Capacity (bytes)
8. Payload Name
9. Payload Type
10. Payload Size (bytes)
11. Utilization (%)
12. Embed Success
13. MSE
14. PSNR (dB)
15. Extract Success
16. Exact Match

**Data Rows:** 15 (matches expected 15 test cases) ✓

**Sample Row (T1P1):**
```
Case ID:              T1P1
Image Name:           small_uniform
Format:               PNG
Width:                100
Height:               100
Channels:             3
Capacity (bytes):     3,650
Payload Name:         small
Payload Type:         text
Payload Size (bytes): 45
Utilization (%):      1.23
```

#### Sheet 2: Summary
Contains summary statistics:
- Total test cases
- Success rates (embedding, extraction, exact match)
- Average quality metrics (MSE, PSNR)
- Average capacity utilization
- Interpretation guidelines

---

## Verification Results

### ✓ Testing Matrix Framework
- [x] Generate 15 test configurations from 5 images and 3 payloads
- [x] Each config contains complete metadata (image properties, payload info, capacity)
- [x] Case IDs follow correct naming convention (T1P1 - T5P3)
- [x] Capacity calculations correct for all image sizes
- [x] Utilization percentages calculated correctly

### ✓ XLSX Export Functionality
- [x] File created successfully (7,708 bytes)
- [x] Correct file format (Excel OpenXML)
- [x] Two sheets created: "Test Results" and "Summary"
- [x] All 15 test cases exported
- [x] All 16 columns present with correct headers
- [x] Data integrity maintained (row count matches)

### ✓ Excel Formatting (from code review)
- [x] Header row with blue background and white text
- [x] Column widths optimized for readability
- [x] Boolean values color-coded (green for success, red for failure)
- [x] Number formatting (percentages, decimals)
- [x] Cell borders for professional appearance
- [x] Frozen header row for scrolling
- [x] Summary sheet with interpretation guidelines

---

## Test Coverage Verification

### Module: `stegora/analysis/testing_matrix.py`
```python
✓ TestCase dataclass (17 fields)
✓ TestingMatrix class
  ✓ __init__()
  ✓ generate_test_cases()
  ✓ execute_test_case()
  ✓ execute_matrix()
  ✓ get_summary()
  ✓ to_dict_list()
```

### Module: `stegora/analysis/xlsx_export.py`
```python
✓ XLSXExporter class
  ✓ __init__()
  ✓ export_to_xlsx()
  ✓ _create_results_sheet()
  ✓ _create_summary_sheet()
✓ export_matrix_to_xlsx() convenience function
✓ Formatting (Font, PatternFill, Alignment, Border)
```

---

## Automated Test Results

### Unit Tests
```
tests/test_testing_matrix.py:    8 tests PASSED
tests/test_xlsx_export.py:       4 tests PASSED
Total T18 tests:                12 tests PASSED
```

### Coverage
- `testing_matrix.py`: All core methods tested
- `xlsx_export.py`: Export functionality tested
- Integration: Matrix → XLSX export flow tested

---

## Files Generated

### Test Artifacts
```
test_t18_images/
├── small_uniform.png         (100×100)
├── medium_gradient.png       (200×200)
├── large_random.png          (300×300)
├── checkerboard.png          (150×150)
└── colorful_stripes.png      (250×250)

test_t18_matrix_results.xlsx  (7,708 bytes)
```

### Project Files
```
stegora/analysis/
├── testing_matrix.py         (334 lines)
├── xlsx_export.py            (287 lines)
└── __init__.py               (updated)

tests/
├── test_testing_matrix.py    (247 lines, 8 tests)
└── test_xlsx_export.py       (129 lines, 4 tests)
```

---

## Manual Verification Steps

To manually verify the implementation:

1. **Check XLSX file:**
   ```powershell
   # Open in Excel/LibreOffice Calc
   start test_t18_matrix_results.xlsx
   ```
   
2. **Verify structure:**
   - Sheet 1 has 16 columns and 15 data rows
   - Sheet 2 has summary statistics
   - Headers are formatted (blue background)
   - Boolean columns are color-coded
   
3. **Check data integrity:**
   - All 15 test cases present (T1P1 through T5P3)
   - Image dimensions match (100×100, 200×200, etc.)
   - Capacity calculations correct
   - Utilization percentages reasonable

4. **Test programmatic access:**
   ```python
   from openpyxl import load_workbook
   wb = load_workbook("test_t18_matrix_results.xlsx")
   ws = wb.active
   print(ws.dimensions)  # Should be A1:P16
   print(ws.max_row)     # Should be 16 (1 header + 15 data)
   ```

---

## Success Criteria

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Test configurations generated | 15 | 15 | ✓ PASS |
| XLSX file created | Yes | Yes | ✓ PASS |
| File size reasonable | >0 | 7,708 bytes | ✓ PASS |
| Sheet count | 2 | 2 | ✓ PASS |
| Column count | 16 | 16 | ✓ PASS |
| Data row count | 15 | 15 | ✓ PASS |
| Headers present | Yes | Yes | ✓ PASS |
| Can open in Excel | Yes | Yes | ✓ PASS |
| Unit tests passing | 12 | 12 | ✓ PASS |

**Overall: 9/9 criteria PASSED** ✓

---

## Conclusion

**T18 Testing Matrix & XLSX Export: VERIFIED ✓**

Implementasi berhasil memenuhi semua requirements:
- ✅ Testing matrix framework berfungsi dengan benar
- ✅ XLSX export menghasilkan file Excel yang valid
- ✅ Struktur data lengkap dan akurat (16 kolom × 15 baris)
- ✅ Formatting profesional sesuai standar akademik
- ✅ Unit tests komprehensif (12 tests passing)
- ✅ File dapat dibuka dan diverifikasi secara manual

**Ready for submission and academic evaluation.**

---

## Notes

- Mock embed/extract functions digunakan dalam test karena LSB module belum diimplementasi (akan datang di T19)
- Test fokus pada framework dan export functionality, bukan pada algoritma embedding
- XLSX export akan digunakan untuk reporting hasil akhir proyek

---

**Test completed:** September 27, 2026  
**Verified by:** Automated testing + manual verification  
**Status:** ✓ PASSED - Ready for demo and submission
