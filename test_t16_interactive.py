"""
Interactive Testing for T16: Histogram + Enhanced LSB Analysis

Test histogram analysis and LSB plane visualization step-by-step.

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi

Usage:
    python test_t16_interactive.py
"""

import numpy as np
from PIL import Image
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from stegora.analysis.histogram import (
    calculate_histogram,
    calculate_histogram_from_pil,
    compare_histograms,
    analyze_lsb_histogram_pairs,
    calculate_histogram_difference_image
)

from stegora.analysis.lsb_plane import (
    extract_bit_plane,
    extract_lsb_plane,
    create_enhanced_lsb_visual,
    analyze_lsb_randomness,
    compare_lsb_planes,
    create_lsb_difference_visual,
    analyze_bit_plane_complexity
)


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title):
    """Print formatted subheader."""
    print(f"\n--- {title} ---")


def wait_for_enter():
    """Wait for user to press Enter."""
    input("\n[Press Enter to continue...]")


def test_1_config():
    """Test #1: Configuration Check."""
    print_header("Test #1: Configuration Check")
    
    print("""
📖 Apa itu Configuration?
   Sebelum test, kita perlu tahu parameter yang digunakan:
   - MAX_PIXEL_VALUE: Nilai maksimal pixel RGB (0-255)
   - Histogram bins: Jumlah bins untuk histogram (256)
   
🎯 Kenapa Penting?
   Histogram menghitung distribusi pixel dari 0 sampai 255
   
🔍 Yang Akan Dicek:
   1. Nilai maksimal pixel
   2. Jumlah bins histogram
   3. Range nilai yang valid
""")
    
    wait_for_enter()
    
    print_subheader("Configuration Values")
    print(f"MAX_PIXEL_VALUE: 255")
    print(f"HISTOGRAM_BINS: 256")
    print(f"BIT_PLANES: 0-7 (0=LSB, 7=MSB)")
    
    print("""
✅ Interpretation:
   - Pixels range: 0 (black) to 255 (white)
   - Histogram bins: 256 bins untuk nilai 0-255
   - Bit planes: 8 bits per pixel (0=LSB yang paling mudah diubah)
""")
    
    wait_for_enter()


def test_2_basic_histogram():
    """Test #2: Basic Histogram Calculation."""
    print_header("Test #2: Basic Histogram Calculation")
    
    print("""
📖 Apa itu Histogram?
   Histogram = grafik yang menunjukkan distribusi nilai pixel
   
   Analogi: Polling suara
   - Berapa orang pilih 0 (hitam)?
   - Berapa orang pilih 255 (putih)?
   - Berapa orang pilih nilai tengah?
   
🎯 Kenapa Penting?
   Histogram menunjukkan karakteristik gambar:
   - Gambar gelap: banyak pixel nilai rendah (0-100)
   - Gambar terang: banyak pixel nilai tinggi (150-255)
   - Gambar balanced: distribusi merata
   
🔍 Test Case:
   Create gambar solid merah (255, 0, 0)
   Semua pixel sama, jadi histogram punya 1 puncak
""")
    
    wait_for_enter()
    
    print_subheader("Creating Test Image")
    # Create 10x10 red image
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[:, :, 0] = 255  # Red channel = 255
    print(f"Image shape: {img.shape}")
    print(f"Image dtype: {img.dtype}")
    print(f"Total pixels: {img.shape[0] * img.shape[1]}")
    
    print_subheader("Calculating Histogram")
    hist = calculate_histogram(img)
    print(f"Histogram keys: {list(hist.keys())}")
    print(f"Histogram length per channel: {len(hist['R'])} bins")
    
    print_subheader("Red Channel Analysis")
    print(f"Pixels with value 255: {hist['R'][255]}")
    print(f"Pixels with value 0: {hist['R'][0]}")
    print(f"Total pixels in R histogram: {np.sum(hist['R'])}")
    
    print_subheader("Green Channel Analysis")
    print(f"Pixels with value 0: {hist['G'][0]}")
    print(f"Total pixels in G histogram: {np.sum(hist['G'])}")
    
    print_subheader("Blue Channel Analysis")
    print(f"Pixels with value 0: {hist['B'][0]}")
    print(f"Total pixels in B histogram: {np.sum(hist['B'])}")
    
    print("""
✅ Hasil:
   - Red: Semua 100 pixel punya nilai 255 (merah penuh)
   - Green: Semua 100 pixel punya nilai 0 (tidak ada hijau)
   - Blue: Semua 100 pixel punya nilai 0 (tidak ada biru)
   - Histogram menunjukkan distribusi yang sempurna!
""")
    
    wait_for_enter()


def test_3_gradient_histogram():
    """Test #3: Gradient Image Histogram."""
    print_header("Test #3: Gradient Image Histogram")
    
    print("""
📖 Apa itu Gradient Image?
   Gradient = gambar yang berubah bertahap dari hitam ke putih
   
   Contoh: 0, 1, 2, 3, ..., 253, 254, 255
   Setiap nilai muncul sekali
   
🎯 Kenapa Test Ini?
   Natural images biasanya punya distribusi yang spread out
   Test ini simulate natural image characteristics
   
🔍 Test Case:
   Create gradient 0-255 di red channel
   Histogram harus flat (setiap nilai muncul 1x)
""")
    
    wait_for_enter()
    
    print_subheader("Creating Gradient Image")
    # Create gradient: 0-255 in red channel
    img = np.zeros((256, 1, 3), dtype=np.uint8)
    img[:, 0, 0] = np.arange(256, dtype=np.uint8)
    print(f"Image shape: {img.shape}")
    print(f"Pixel values in red: 0 to 255")
    
    print_subheader("Calculating Histogram")
    hist = calculate_histogram(img)
    
    print_subheader("Red Channel Analysis")
    print(f"Each value count: {hist['R'][0]} (should be 1)")
    print(f"Min count: {np.min(hist['R'])}")
    print(f"Max count: {np.max(hist['R'])}")
    print(f"All values appear once: {np.all(hist['R'] == 1)}")
    
    print_subheader("Sample Distribution")
    for val in [0, 50, 100, 150, 200, 255]:
        print(f"  Value {val:3d}: {hist['R'][val]} pixel(s)")
    
    print("""
✅ Hasil:
   - Setiap nilai (0-255) muncul tepat 1 kali
   - Histogram flat = distribusi merata sempurna
   - Ini adalah edge case (jarang di natural image)
""")
    
    wait_for_enter()


def test_4_compare_histograms():
    """Test #4: Compare Histograms."""
    print_header("Test #4: Compare Histograms (Cover vs Stego)")
    
    print("""
📖 Apa itu Histogram Comparison?
   Compare distribusi pixel antara 2 gambar
   
   Metrics:
   1. MAD (Mean Absolute Difference)
      - Rata-rata perbedaan per bin
      - Low = mirip, High = beda
      
   2. Max Difference
      - Perbedaan terbesar di 1 bin
      - Menunjukkan worst case
      
   3. Chi-Square Distance
      - Ukuran statistik similarity
      - < 100 = very similar
      - > 1000 = very different
   
🎯 Kenapa Penting untuk Steganalysis?
   LSB embedding mengubah histogram sedikit
   Detect perubahan = detect steganography
   
🔍 Test Case:
   - Cover: All red = 100
   - Stego: Half red = 100, half red = 101 (LSB flip)
   - Histogram harus detect perbedaan ini
""")
    
    wait_for_enter()
    
    print_subheader("Creating Cover Image")
    cover = np.zeros((10, 10, 3), dtype=np.uint8)
    cover[:, :, 0] = 100  # All red = 100
    print(f"Cover: All pixels red=100")
    print(f"Binary: 100 = 0b{100:08b} (LSB=0)")
    
    print_subheader("Creating Stego Image (LSB Modified)")
    stego = cover.copy()
    stego[5:, :, 0] = 101  # Half pixels red=101
    print(f"Stego: Top half red=100, bottom half red=101")
    print(f"Binary: 101 = 0b{101:08b} (LSB=1)")
    print(f"Change: Only LSB flipped (100 → 101)")
    
    print_subheader("Calculating Histograms")
    hist_cover = calculate_histogram(cover)
    hist_stego = calculate_histogram(stego)
    
    print("Cover histogram (Red channel):")
    print(f"  Value 100: {hist_cover['R'][100]} pixels")
    print(f"  Value 101: {hist_cover['R'][101]} pixels")
    
    print("\nStego histogram (Red channel):")
    print(f"  Value 100: {hist_stego['R'][100]} pixels")
    print(f"  Value 101: {hist_stego['R'][101]} pixels")
    
    print_subheader("Comparing Histograms")
    metrics = compare_histograms(hist_cover, hist_stego)
    
    print("Per-Channel Metrics:")
    print(f"  R MAD: {metrics['R_mad']:.2f}")
    print(f"  R Max: {metrics['R_max']:.2f}")
    print(f"  R Chi2: {metrics['R_chi2']:.2f}")
    
    print("\nG and B channels (unchanged):")
    print(f"  G MAD: {metrics['G_mad']:.2f}")
    print(f"  B MAD: {metrics['B_mad']:.2f}")
    
    print("\nOverall Metrics:")
    print(f"  Overall MAD: {metrics['overall_mad']:.2f}")
    print(f"  Overall Max: {metrics['overall_max']:.2f}")
    print(f"  Overall Chi2: {metrics['overall_chi2']:.2f}")
    
    print("""
✅ Interpretation:
   - R channel detected change (MAD > 0)
   - G and B unchanged (MAD = 0)
   - Overall metrics show small change
   - This is typical LSB embedding signature!
""")
    
    wait_for_enter()


def test_5_lsb_histogram_pairs():
    """Test #5: LSB Histogram Pair Analysis."""
    print_header("Test #5: LSB Histogram Pair Analysis")
    
    print("""
📖 Apa itu LSB Pair Analysis?
   Analyze even/odd pairs dalam histogram
   
   Pairs: (0,1), (2,3), (4,5), ..., (254,255)
   
   Prinsip: Natural images punya balanced pairs
   - Pixel value 100 (even) dan 101 (odd) frekuensi mirip
   - Ratio ≈ 1.0 = natural
   - Ratio >> 1.0 atau << 1.0 = suspicious
   
🎯 Kenapa Penting?
   LSB embedding disrupts even/odd balance:
   - Flip LSB: even → odd atau odd → even
   - Creates imbalance yang bisa dideteksi
   
🔍 Test Case:
   Perfect balance: 50 pixels value 100, 50 pixels value 101
   Ratio should be 1.0
""")
    
    wait_for_enter()
    
    print_subheader("Creating Perfectly Balanced Image")
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:50, :, 0] = 100  # Even value
    img[50:, :, 0] = 101  # Odd value
    print(f"Top half: red=100 (even) → 5000 pixels")
    print(f"Bottom half: red=101 (odd) → 5000 pixels")
    print(f"Ratio: 5000/5000 = 1.0 (perfect balance)")
    
    print_subheader("Calculating Histogram")
    hist = calculate_histogram(img)
    
    print_subheader("Analyzing LSB Pairs")
    analysis = analyze_lsb_histogram_pairs(hist)
    
    print("Red Channel Analysis:")
    print(f"  Mean ratio: {analysis['R']['mean_ratio']:.3f}")
    print(f"  Max ratio: {analysis['R']['max_ratio']:.3f}")
    print(f"  Suspicious pairs: {analysis['R']['suspicious_pairs']}")
    
    print("\nGreen Channel Analysis:")
    print(f"  Mean ratio: {analysis['G']['mean_ratio']:.3f}")
    print(f"  Suspicious pairs: {analysis['G']['suspicious_pairs']}")
    
    print("""
✅ Interpretation:
   - Red channel: ratio ≈ 1.0 (balanced)
   - Few suspicious pairs (ratio natural)
   - This is characteristic of good steganography!
   
📚 Steganalysis Note:
   - Ratio close to 1.0 = hard to detect
   - Ratio far from 1.0 = easy to detect
   - LSB embedding should maintain balance
""")
    
    wait_for_enter()


def test_6_extract_lsb_plane():
    """Test #6: Extract LSB Plane."""
    print_header("Test #6: Extract LSB Plane")
    
    print("""
📖 Apa itu LSB Plane?
   Extract bit terakhir (LSB) dari setiap pixel
   
   Contoh:
   - 100 = 0b01100100 → LSB = 0
   - 101 = 0b01100101 → LSB = 1
   - 200 = 0b11001000 → LSB = 0
   
   Analogi: Ambil "digit terakhir" dari setiap angka
   
🎯 Kenapa Penting?
   LSB plane menunjukkan data yang di-embed:
   - Natural image: LSB looks random (noise)
   - Stego image: LSB might show patterns
   
🔍 Test Case:
   Create image dengan nilai known LSB
   Extract dan verify
""")
    
    wait_for_enter()
    
    print_subheader("Creating Test Image")
    img = np.array([
        [[100, 101, 102]],  # LSB: 0, 1, 0
        [[200, 201, 255]]   # LSB: 0, 1, 1
    ], dtype=np.uint8)
    
    print("Pixel values and their LSBs:")
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            r, g, b = img[i, j]
            print(f"  Pixel[{i},{j}]: R={r:3d} (LSB={r&1}), "
                  f"G={g:3d} (LSB={g&1}), "
                  f"B={b:3d} (LSB={b&1})")
    
    print_subheader("Extracting LSB Plane")
    lsb_plane = extract_lsb_plane(img)
    print(f"LSB plane shape: {lsb_plane.shape}")
    print(f"LSB plane dtype: {lsb_plane.dtype}")
    print(f"LSB plane values: 0 or 255 (amplified for visibility)")
    
    print_subheader("LSB Plane Values")
    for i in range(lsb_plane.shape[0]):
        for j in range(lsb_plane.shape[1]):
            r, g, b = lsb_plane[i, j]
            print(f"  LSB[{i},{j}]: R={r:3d}, G={g:3d}, B={b:3d}")
    
    print("""
✅ Verification:
   - 100 (even) → LSB=0 → plane=0
   - 101 (odd) → LSB=1 → plane=255
   - Values amplified (0→0, 1→255) untuk visibility
   
📊 In Real Images:
   - Natural: LSB plane looks like TV static (random)
   - Stego: LSB plane might show structure
""")
    
    wait_for_enter()


def test_7_lsb_randomness():
    """Test #7: LSB Randomness Analysis."""
    print_header("Test #7: LSB Randomness Analysis")
    
    print("""
📖 Apa itu LSB Randomness?
   Measure seberapa random LSB plane
   
   Metrics:
   1. Bit Balance = count(1) / count(0)
      - Random: ≈ 1.0 (equal 0s and 1s)
      - Suspicious: >> 1.0 atau << 1.0
      
   2. Entropy = -p·log₂(p) - (1-p)·log₂(1-p)
      - Random: ≈ 1.0 (maximum)
      - Pattern: < 0.8 (low entropy)
   
🎯 Kenapa Penting?
   Natural images: LSB should be random
   Encrypted stego: LSB should still be random (good crypto)
   Unencrypted stego: LSB shows patterns (detectable)
   
🔍 Test Cases:
   1. Perfect random (50% 0s, 50% 1s)
   2. All zeros (no randomness)
   3. All ones (no randomness)
""")
    
    wait_for_enter()
    
    # Test 1: Perfect balance
    print_subheader("Test Case 1: Perfect Balance")
    lsb_balanced = np.zeros((100, 100, 3), dtype=np.uint8)
    lsb_balanced[:50, :, :] = 255  # Half 1s
    # Half 0s (already 0)
    
    print("Creating LSB plane: 50% zeros, 50% ones")
    metrics = analyze_lsb_randomness(lsb_balanced)
    
    print("Red Channel:")
    print(f"  Balance: {metrics['R_balance']:.3f} (should be ≈1.0)")
    print(f"  Entropy: {metrics['R_entropy']:.3f} (should be ≈1.0)")
    
    print("\nOverall:")
    print(f"  Balance: {metrics['overall_balance']:.3f}")
    print(f"  Entropy: {metrics['overall_entropy']:.3f}")
    
    print("\n✅ Perfect random: balance=1.0, entropy≈1.0")
    
    wait_for_enter()
    
    # Test 2: All zeros
    print_subheader("Test Case 2: All Zeros (No Randomness)")
    lsb_zeros = np.zeros((50, 50, 3), dtype=np.uint8)
    
    print("Creating LSB plane: 100% zeros")
    metrics = analyze_lsb_randomness(lsb_zeros)
    
    print("Red Channel:")
    print(f"  Balance: {metrics['R_balance']:.3f}")
    print(f"  Entropy: {metrics['R_entropy']:.3f} (should be 0.0)")
    
    print("\n✅ No randomness: entropy=0.0")
    
    wait_for_enter()
    
    # Test 3: All ones
    print_subheader("Test Case 3: All Ones (No Randomness)")
    lsb_ones = np.full((50, 50, 3), 255, dtype=np.uint8)
    
    print("Creating LSB plane: 100% ones")
    metrics = analyze_lsb_randomness(lsb_ones)
    
    print("Red Channel:")
    print(f"  Balance: {metrics['R_balance']:.3f} (very high)")
    print(f"  Entropy: {metrics['R_entropy']:.3f} (should be 0.0)")
    
    print("""
✅ Summary:
   - Random data: balance≈1.0, entropy≈1.0
   - Uniform data: entropy=0.0
   - Stego with good crypto: should look random
   
📚 Steganalysis Rule:
   If LSB entropy << 1.0 → likely unencrypted stego (detectable)
   If LSB entropy ≈ 1.0 → either natural or encrypted stego (harder)
""")
    
    wait_for_enter()


def test_8_enhanced_lsb_visual():
    """Test #8: Enhanced LSB Visualization."""
    print_header("Test #8: Enhanced LSB Visualization")
    
    print("""
📖 Apa itu Enhanced LSB?
   Amplify patterns dalam LSB plane untuk human inspection
   
   Technique:
   1. Extract LSB plane
   2. Apply spatial averaging filter (3×3)
   3. Calculate deviation from 0.5 (expected random)
   4. Amplify deviation (×4) for visibility
   
   Analogi: Magnifying glass untuk pola tersembunyi
   
🎯 Kenapa Penting?
   Human eyes can spot patterns better than metrics
   Enhanced visualization makes patterns visible
   
🔍 Test Cases:
   1. Uniform LSB (all 0s) → maximum deviation
   2. Random LSB → near-zero deviation
""")
    
    wait_for_enter()
    
    # Test 1: Uniform LSB
    print_subheader("Test Case 1: Uniform LSB (All Zeros)")
    img_uniform = np.full((20, 20, 3), 100, dtype=np.uint8)  # All even (LSB=0)
    
    print("Image: All pixels even (LSB=0)")
    enhanced = create_enhanced_lsb_visual(img_uniform)
    
    print(f"Enhanced output shape: {enhanced.shape}")
    print(f"Enhanced output dtype: {enhanced.dtype}")
    print(f"Mean value: {np.mean(enhanced):.2f}")
    print(f"Min value: {np.min(enhanced)}")
    print(f"Max value: {np.max(enhanced)}")
    
    print("""
✅ Uniform LSB:
   - Local average = 0 (all zeros)
   - Deviation from 0.5 = 0.5 (maximum)
   - After amplification → bright (255)
   - Menunjukkan non-random pattern!
""")
    
    wait_for_enter()
    
    # Test 2: Random LSB
    print_subheader("Test Case 2: Random LSB")
    np.random.seed(42)
    # Create random even/odd values
    img_random = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
    
    print("Image: Random pixel values (random LSB)")
    enhanced = create_enhanced_lsb_visual(img_random)
    
    print(f"Mean value: {np.mean(enhanced):.2f}")
    print(f"Min value: {np.min(enhanced)}")
    print(f"Max value: {np.max(enhanced)}")
    
    print("""
✅ Random LSB:
   - Local average ≈ 0.5 (balanced 0s and 1s)
   - Deviation from 0.5 ≈ 0 (minimal)
   - After amplification → darker values
   - Menunjukkan random pattern (natural)
   
📚 Practical Use:
   Display enhanced LSB side-by-side:
   - Cover: should look noisy/random
   - Stego with pattern: shows structure
   - Visual inspection by human analyst
""")
    
    wait_for_enter()


def test_9_lsb_difference_visual():
    """Test #9: LSB Difference Visualization."""
    print_header("Test #9: LSB Difference Visualization")
    
    print("""
📖 Apa itu LSB Difference?
   Show which pixels had their LSB changed
   
   Process:
   1. Extract LSB plane from cover
   2. Extract LSB plane from stego
   3. Compare bit-by-bit
   4. White = LSB changed, Black = LSB unchanged
   
   Analogi: Highlighting changes dengan marker
   
🎯 Kenapa Penting?
   Visualize spatial distribution of embedded data:
   - Random PRNG: white pixels scattered randomly
   - Sequential: white pixels in order
   - Clustered: white pixels grouped
   
🔍 Test Case:
   - Cover: all even (LSB=0)
   - Stego: bottom half odd (LSB=1)
   - Difference should show bottom half white
""")
    
    wait_for_enter()
    
    print_subheader("Creating Cover Image")
    cover = np.full((10, 10, 3), 100, dtype=np.uint8)  # All even
    print("Cover: All pixels = 100 (LSB=0)")
    
    print_subheader("Creating Stego Image")
    stego = cover.copy()
    stego[5:, :, 0] = 101  # Bottom half odd in red channel
    print("Stego: Top half = 100 (LSB=0)")
    print("       Bottom half = 101 (LSB=1) in red channel")
    
    print_subheader("Creating LSB Difference Visualization")
    diff_visual = create_lsb_difference_visual(cover, stego)
    
    print(f"Difference shape: {diff_visual.shape}")
    print(f"Difference dtype: {diff_visual.dtype}")
    
    print_subheader("Analyzing Difference")
    print("\nRed channel (modified):")
    print(f"  Top half (unchanged): min={np.min(diff_visual[:5, :, 0])}, "
          f"max={np.max(diff_visual[:5, :, 0])}")
    print(f"  Bottom half (changed): min={np.min(diff_visual[5:, :, 0])}, "
          f"max={np.max(diff_visual[5:, :, 0])}")
    
    print("\nGreen channel (unchanged):")
    print(f"  All pixels: min={np.min(diff_visual[:, :, 1])}, "
          f"max={np.max(diff_visual[:, :, 1])}")
    
    print("""
✅ Verification:
   - Red top half: black (0) = no change
   - Red bottom half: white (255) = LSB changed
   - Green/Blue: all black = no change
   - Perfect visualization of embedding!
   
📊 Real Stego Analysis:
   With keyed PRNG:
   - White pixels scattered randomly
   - Distribution matches PRNG output
   - Can verify stego-key correctness
""")
    
    wait_for_enter()


def test_10_complete_analysis():
    """Test #10: Complete Steganalysis Workflow."""
    print_header("Test #10: Complete Steganalysis Workflow")
    
    print("""
📖 Complete Steganalysis Workflow
   Combine all techniques untuk comprehensive analysis
   
   Steps:
   1. Histogram comparison (statistical)
   2. LSB pair analysis (even/odd balance)
   3. LSB randomness analysis (entropy, balance)
   4. Enhanced LSB visual (pattern detection)
   5. LSB difference visual (spatial distribution)
   
🎯 Goal:
   Detect steganography dengan multiple evidence
   
🔍 Test Case:
   Simulate cover → stego embedding
   Run complete analysis pipeline
""")
    
    wait_for_enter()
    
    print_subheader("Step 1: Create Cover and Stego Images")
    # Create realistic cover (varied values)
    np.random.seed(42)
    cover = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    print(f"Cover: Random natural-like image (50×50)")
    
    # Create stego by flipping LSB in 30% of pixels
    stego = cover.copy()
    mask = np.random.random((50, 50, 3)) < 0.3  # 30% pixels
    stego[mask] = stego[mask] ^ 1  # XOR with 1 to flip LSB
    print(f"Stego: 30% pixels have LSB flipped")
    
    wait_for_enter()
    
    print_subheader("Step 2: Histogram Analysis")
    hist_cover = calculate_histogram(cover)
    hist_stego = calculate_histogram(stego)
    hist_metrics = compare_histograms(hist_cover, hist_stego)
    
    print(f"Overall MAD: {hist_metrics['overall_mad']:.2f}")
    print(f"Overall Chi2: {hist_metrics['overall_chi2']:.2f}")
    print("→ Small difference detected (LSB-level change)")
    
    wait_for_enter()
    
    print_subheader("Step 3: LSB Pair Analysis")
    pairs_cover = analyze_lsb_histogram_pairs(hist_cover)
    pairs_stego = analyze_lsb_histogram_pairs(hist_stego)
    
    print(f"Cover - R mean ratio: {pairs_cover['R']['mean_ratio']:.3f}")
    print(f"Stego - R mean ratio: {pairs_stego['R']['mean_ratio']:.3f}")
    print(f"Cover suspicious pairs: {pairs_cover['R']['suspicious_pairs']}")
    print(f"Stego suspicious pairs: {pairs_stego['R']['suspicious_pairs']}")
    
    wait_for_enter()
    
    print_subheader("Step 4: LSB Randomness Analysis")
    lsb_cover = extract_lsb_plane(cover)
    lsb_stego = extract_lsb_plane(stego)
    
    rand_cover = analyze_lsb_randomness(lsb_cover)
    rand_stego = analyze_lsb_randomness(lsb_stego)
    
    print(f"Cover entropy: {rand_cover['overall_entropy']:.3f}")
    print(f"Stego entropy: {rand_stego['overall_entropy']:.3f}")
    print(f"Cover balance: {rand_cover['overall_balance']:.3f}")
    print(f"Stego balance: {rand_stego['overall_balance']:.3f}")
    print("→ Both look random (good encryption simulation)")
    
    wait_for_enter()
    
    print_subheader("Step 5: LSB Plane Comparison")
    lsb_metrics = compare_lsb_planes(lsb_cover, lsb_stego)
    
    print(f"Overall diff ratio: {lsb_metrics['overall_diff_ratio']:.3f}")
    print(f"R diff ratio: {lsb_metrics['R_diff_ratio']:.3f}")
    print(f"Expected: ~0.3 (30% pixels modified)")
    print("→ Confirms 30% embedding rate")
    
    wait_for_enter()
    
    print_subheader("Analysis Summary")
    print("""
✅ Complete Steganalysis Results:

1. Histogram: Small changes detected (MAD > 0)
2. LSB Pairs: Maintained balance (ratio ≈ 1.0)
3. Randomness: Still random (entropy ≈ 1.0)
4. LSB Comparison: 30% bits changed

Conclusion:
- Steganography detected (30% capacity used)
- Good quality embedding (maintained randomness)
- With encryption, hard to detect without cover image
- With cover image, difference is measurable

📚 Real-World Application:
- Analyst compares suspicious image vs known cover
- Multiple metrics provide confidence
- Visual tools help human interpretation
- Automated tools flag suspicious images
""")
    
    wait_for_enter()


def main():
    """Main interactive test menu."""
    tests = [
        ("Configuration Check", test_1_config),
        ("Basic Histogram Calculation", test_2_basic_histogram),
        ("Gradient Image Histogram", test_3_gradient_histogram),
        ("Compare Histograms (Cover vs Stego)", test_4_compare_histograms),
        ("LSB Histogram Pair Analysis", test_5_lsb_histogram_pairs),
        ("Extract LSB Plane", test_6_extract_lsb_plane),
        ("LSB Randomness Analysis", test_7_lsb_randomness),
        ("Enhanced LSB Visualization", test_8_enhanced_lsb_visual),
        ("LSB Difference Visualization", test_9_lsb_difference_visual),
        ("Complete Steganalysis Workflow", test_10_complete_analysis),
    ]
    
    while True:
        print("\n" + "=" * 70)
        print("  T16 Interactive Testing: Histogram + Enhanced LSB Analysis")
        print("=" * 70)
        print("\nAvailable Tests:")
        for i, (name, _) in enumerate(tests, 1):
            print(f"  {i:2d}. {name}")
        print("   0. Exit")
        print("=" * 70)
        
        try:
            choice = input("\nSelect test number (0-10): ").strip()
            
            if choice == '0':
                print("\n✅ Testing complete! Good luck with your project, Hana!")
                break
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(tests):
                tests[choice_num - 1][1]()
            else:
                print(f"\n❌ Invalid choice. Please enter 0-{len(tests)}")
        
        except ValueError:
            print("\n❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n✅ Testing interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
