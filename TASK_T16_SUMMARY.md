# Task T16 Summary: Histogram + Enhanced LSB Analysis

**Task ID:** T16  
**Owner:** Hana (247006111170)  
**Priority:** ANALYSIS  
**Status:** ✅ COMPLETE  
**Commit:** `feat: add histogram and lsb analysis`

---

## 📋 Scope

Implement histogram analysis and enhanced LSB plane visualization for steganalysis:

1. **RGB Histogram** - Calculate and compare pixel value distributions
2. **Enhanced LSB Plane** - Extract and visualize LSB bit planes
3. **Steganalysis Metrics** - Detect steganography artifacts

---

## 🎯 Implementation

### Files Created

#### Core Modules
1. **`stegora/analysis/histogram.py`** (361 lines)
   - `calculate_histogram()` - RGB histogram from image array
   - `calculate_histogram_from_pil()` - RGB histogram from PIL Image
   - `compare_histograms()` - MAD, max diff, chi-square metrics
   - `analyze_lsb_histogram_pairs()` - Even/odd LSB pair analysis
   - `calculate_histogram_difference_image()` - Pixel-wise diff visualization

2. **`stegora/analysis/lsb_plane.py`** (467 lines)
   - `extract_bit_plane()` - Extract specific bit plane (0-7)
   - `extract_lsb_plane()` - Extract LSB (bit 0) plane
   - `create_enhanced_lsb_visual()` - Enhanced LSB visualization
   - `analyze_lsb_randomness()` - Bit balance, entropy metrics
   - `compare_lsb_planes()` - Compare cover vs stego LSB
   - `create_lsb_difference_visual()` - Show which LSBs changed
   - `analyze_bit_plane_complexity()` - Edge density, uniformity

3. **`stegora/analysis/__init__.py`** (44 lines)
   - Exports all analysis functions

#### Unit Tests
4. **`tests/test_histogram.py`** (337 lines, 22 tests)
   - TestCalculateHistogram (8 tests)
   - TestCalculateHistogramFromPIL (3 tests)
   - TestCompareHistograms (3 tests)
   - TestAnalyzeLSBHistogramPairs (3 tests)
   - TestCalculateHistogramDifferenceImage (5 tests)

5. **`tests/test_lsb_plane.py`** (379 lines, 30 tests)
   - TestExtractBitPlane (6 tests)
   - TestExtractLSBPlane (1 test)
   - TestCreateEnhancedLSBVisual (4 tests)
   - TestAnalyzeLSBRandomness (5 tests)
   - TestCompareLSBPlanes (4 tests)
   - TestCreateLSBDifferenceVisual (6 tests)
   - TestAnalyzeBitPlaneComplexity (4 tests)

---

## 🔬 Technical Details

### Histogram Analysis

#### **Purpose**
Detect LSB embedding by comparing pixel value distributions between cover and stego images.

#### **Metrics**
1. **Mean Absolute Difference (MAD)**
   ```
   MAD = mean(|hist_cover - hist_stego|)
   Typical range: 0-100 for LSB changes
   ```

2. **Maximum Difference**
   ```
   Max = max(|hist_cover - hist_stego|)
   Shows worst-case bin change
   ```

3. **Chi-Square Distance**
   ```
   χ² = Σ (cover - stego)² / (cover + stego + ε)
   < 100 = very similar
   > 1000 = very different
   ```

4. **LSB Pair Analysis**
   ```
   Ratio = hist[2k] / hist[2k+1]  for k = 0..127
   Natural images: ratio ≈ 1.0
   Suspicious if ratio > 2.0 or < 0.5
   ```

#### **Academic Context**
- In natural images, adjacent pixel values (e.g., 100 vs 101) have similar frequencies
- LSB embedding disrupts this by preferentially modifying specific values
- Large histogram changes indicate potential steganography

---

### LSB Plane Visualization

#### **Purpose**
Extract and visualize specific bit planes to detect non-random patterns.

#### **Bit Plane Extraction**
```python
# Extract bit at position (0=LSB, 7=MSB)
bit = (pixel >> bit_position) & 1
plane = bit * 255  # Amplify to 0 or 255 for visibility
```

#### **Enhanced LSB Technique**
1. Extract LSB plane (bit 0)
2. Apply spatial averaging filter (3×3 kernel)
3. Calculate deviation from 0.5 (expected random value)
4. Amplify deviation (×4) for visibility

**Interpretation:**
- **Natural images:** LSB looks random/noisy (deviation ≈ 0)
- **Stego images:** LSB may show patterns (deviation > 0)

#### **Randomness Metrics**
1. **Bit Balance**
   ```
   Balance = count(1) / count(0)
   Random: balance ≈ 1.0
   Suspicious: balance >> 1.0 or << 1.0
   ```

2. **Entropy**
   ```
   H = -p·log₂(p) - (1-p)·log₂(1-p)
   Max = 1.0 (perfectly random)
   Low entropy suggests patterns
   ```

3. **Edge Density**
   ```
   Edges = count(horizontal transitions) + count(vertical transitions)
   Random: high edge density
   Uniform: low edge density
   ```

---

## 📊 Test Results

### Test Coverage
- **Total tests:** 52 (22 histogram + 30 LSB plane)
- **All tests:** ✅ PASSED
- **Project total:** 240 tests passing

### Key Test Cases

#### Histogram Tests
- ✅ Single color image histogram
- ✅ Gradient image histogram
- ✅ RGBA image (alpha ignored)
- ✅ Invalid input validation
- ✅ Identical histogram comparison (zero difference)
- ✅ Different histogram metrics
- ✅ LSB pair balance analysis
- ✅ Histogram difference visualization

#### LSB Plane Tests
- ✅ Extract LSB (bit 0) plane
- ✅ Extract MSB (bit 7) plane
- ✅ Extract middle bits (bit 3)
- ✅ Invalid bit position rejection
- ✅ Enhanced LSB visualization output
- ✅ Perfect balance randomness (entropy = 1.0)
- ✅ All-zero/all-one LSB detection
- ✅ LSB plane comparison (diff ratio)
- ✅ LSB difference visualization
- ✅ Bit plane complexity analysis

---

## 🔍 Steganalysis Workflow

### Cover vs Stego Analysis

```python
from stegora.analysis import (
    calculate_histogram,
    compare_histograms,
    extract_lsb_plane,
    create_enhanced_lsb_visual,
    analyze_lsb_randomness
)

# 1. Histogram Analysis
hist_cover = calculate_histogram(cover_image)
hist_stego = calculate_histogram(stego_image)
hist_metrics = compare_histograms(hist_cover, hist_stego)

# Interpret:
# - overall_mad < 10 → minimal change
# - overall_chi2 < 100 → very similar

# 2. LSB Plane Analysis
lsb_cover = extract_lsb_plane(cover_image)
lsb_stego = extract_lsb_plane(stego_image)

# 3. Enhanced LSB Visual
enhanced_cover = create_enhanced_lsb_visual(cover_image)
enhanced_stego = create_enhanced_lsb_visual(stego_image)

# Patterns in enhanced_stego suggest steganography

# 4. Randomness Analysis
randomness_cover = analyze_lsb_randomness(lsb_cover)
randomness_stego = analyze_lsb_randomness(lsb_stego)

# Interpret:
# - entropy close to 1.0 → random (good)
# - balance close to 1.0 → equal 0s/1s (good)
```

---

## 🎓 Educational Concepts

### What is a Histogram?
**Analogy:** Voting poll of pixel values
- How many pixels are black (0)?
- How many are white (255)?
- Shows distribution across 0-255

### What is LSB Plane?
**Analogy:** Extracting only the "last digit" of every number
- 100 → 0 (even)
- 101 → 1 (odd)
- Shows the "hidden layer" where stego data lives

### Why Enhanced LSB?
**Analogy:** Magnifying glass for patterns
- Random LSB looks like TV static (no patterns)
- Stego LSB might show structure (patterns visible)
- Amplifies subtle differences for human inspection

### Steganalysis Principle
**Detection Strategy:**
1. Natural images have statistical properties
2. LSB embedding disrupts these properties
3. Compare cover vs stego to detect disruption

**Limitations:**
- Cannot detect all steganography
- Requires cover image for comparison
- Small payloads are harder to detect

---

## ✅ Requirements Met

### From TESTING_SPEC.md
- ✅ Histogram comparison (mandatory)
- ✅ Enhanced LSB visual steganalysis (mandatory)
- ✅ No hard-coded metrics
- ✅ Real data only

### From ARCHITECTURE.md
- ✅ Core module (no Streamlit dependency)
- ✅ Proper module structure (`stegora/analysis/`)
- ✅ Clean public API (`__init__.py`)

### From AGENTS.md
- ✅ Comprehensive unit tests (52 tests)
- ✅ Educational documentation
- ✅ No fake/mock data

---

## 🚀 Next Steps

### T17: Security + JPEG Robustness Tests
- Wrong password/key tests
- JPEG re-save fragility tests
- Authentication failure tests

### T18: 5×3 Testing Matrix + XLSX
- 5 cover images × 3 payload sizes
- Record actual metrics (MSE, PSNR)
- Export to Excel

### Integration with Analysis Page
- Azhar will integrate histogram visualization
- Display LSB plane comparison
- Show enhanced LSB evidence

---

## 📈 Statistics

- **Lines of code:** 828 (histogram: 361, lsb_plane: 467)
- **Lines of tests:** 716 (histogram: 337, lsb_plane: 379)
- **Test coverage:** 52 tests, 100% passing
- **Functions:** 12 public API functions
- **Docstrings:** Full documentation with examples

---

## 🔐 Academic Integrity

**Author:** Hana (247006111170)  
**Course:** Information Security - Universitas Siliwangi  
**AI Assistance:** Used for implementation (will be disclosed in report)

**Learning Outcomes:**
- ✅ Understand histogram analysis for steganalysis
- ✅ Understand LSB plane extraction
- ✅ Understand enhanced LSB visualization technique
- ✅ Understand randomness metrics (entropy, bit balance)
- ✅ Apply steganalysis to detect steganography

---

**Status:** ✅ T16 COMPLETE - Ready for T17
