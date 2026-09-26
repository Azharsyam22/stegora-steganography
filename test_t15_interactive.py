"""Interactive manual testing for T15 - MSE & PSNR Metrics

Run this script to test image quality metrics with visual examples.
Author: Hana (247006111170)
"""

import sys
import numpy as np
from PIL import Image
from stegora.image import (
    calculate_mse,
    calculate_psnr,
    calculate_metrics,
    format_psnr,
    format_mse,
    is_acceptable_quality,
    calculate_per_channel_mse,
    PSNR_THRESHOLD_CONTEXT,
)


def print_separator():
    print("\n" + "="*70 + "\n")


def print_metrics(metrics, label=""):
    """Print metrics in a nice formatted way."""
    if label:
        print(f"{label}:")
    print(f"  MSE: {format_mse(metrics['mse'])}")
    print(f"  PSNR: {format_psnr(metrics['psnr'])}")
    print(f"  Quality: {metrics['quality_assessment']}")


def save_test_image(img_array, filename):
    """Save numpy array as image file."""
    img = Image.fromarray(img_array.astype(np.uint8))
    img.save(filename)
    print(f"  Saved: {filename}")


def menu():
    """Show interactive menu."""
    print("\n" + "█"*70)
    print("█  T15 - MSE & PSNR Interactive Testing                             █")
    print("█  Author: Hana (247006111170)                                      █")
    print("█"*70)
    print("\nPilih test yang ingin dijalankan:\n")
    print("  1. Identical Images (MSE=0, PSNR=∞)")
    print("  2. Small Difference (1-bit LSB)")
    print("  3. Medium Difference")
    print("  4. Large Difference")
    print("  5. Maximum Difference (Black vs White)")
    print("  6. Compare Different Modifications")
    print("  7. Per-Channel Analysis")
    print("  8. PSNR Threshold Test (30 dB)")
    print("  9. View Configuration")
    print("  0. Exit")
    print("\n" + "-"*70)


def test_1_identical():
    """Test 1: Identical images."""
    print_separator()
    print("TEST 1: Identical Images")
    print_separator()
    
    print("\n📚 KONSEP:")
    print("Ketika cover dan stego image IDENTIK (tidak ada perubahan):")
    print("  - MSE = 0 (no difference)")
    print("  - PSNR = ∞ (perfect quality)")
    
    print("\n" + "-"*70)
    print("CREATING TEST IMAGES...")
    print("-"*70)
    
    # Create a random image
    np.random.seed(42)
    cover = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    stego = cover.copy()  # Identical copy
    
    print(f"Cover image: 200×200 RGB")
    print(f"Stego image: 200×200 RGB (identical copy)")
    
    print("\n" + "-"*70)
    print("CALCULATING METRICS...")
    print("-"*70)
    
    metrics = calculate_metrics(cover, stego)
    print_metrics(metrics)
    
    print("\n💡 PENJELASAN:")
    print(f"  MSE = {metrics['mse']:.10f}")
    print("  → Tidak ada perbedaan pixel sama sekali")
    print(f"  PSNR = {metrics['psnr']}")
    print("  → Infinity karena MSE = 0 (perfect quality)")
    print("  → Dalam Python, infinity direpresentasikan sebagai float('inf')")
    
    print("\n✅ EXPECTED BEHAVIOR:")
    print("  Identical images should have:")
    print("  - MSE = 0.0")
    print("  - PSNR = infinity (∞)")
    print("  - Quality = 'Identical'")
    
    if metrics['mse'] == 0.0 and metrics['psnr'] == float('inf'):
        print("\n🎉 TEST PASSED!")
    else:
        print("\n❌ TEST FAILED!")
    
    input("\nPress Enter to continue...")


def test_2_small_difference():
    """Test 2: Small difference (1-bit LSB)."""
    print_separator()
    print("TEST 2: Small Difference (1-bit LSB)")
    print_separator()
    
    print("\n📚 KONSEP:")
    print("1-bit LSB steganography mengubah bit terakhir (Least Significant Bit):")
    print("  Contoh: 128 (binary: 10000000) → 129 (binary: 10000001)")
    print("  Perubahan sangat kecil, tidak terlihat mata manusia")
    print("  Expected: PSNR sangat tinggi (>50 dB)")
    
    print("\n" + "-"*70)
    print("SIMULATING 1-BIT LSB EMBEDDING...")
    print("-"*70)
    
    # Create cover image
    np.random.seed(42)
    cover = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    stego = cover.copy()
    
    # Flip LSB in 50% of pixels (simulate embedding)
    mask = np.random.rand(200, 200, 3) < 0.5
    num_changed = np.sum(mask)
    stego[mask] ^= 1  # XOR with 1 flips LSB
    
    print(f"Cover image: 200×200 RGB = {200*200*3:,} pixels")
    print(f"Modified pixels: {num_changed:,} ({num_changed/(200*200*3)*100:.1f}%)")
    print(f"Change amount: ±1 (LSB flip)")
    
    print("\n" + "-"*70)
    print("CALCULATING METRICS...")
    print("-"*70)
    
    metrics = calculate_metrics(cover, stego)
    print_metrics(metrics)
    
    print("\n💡 PENJELASAN:")
    print(f"  MSE = {metrics['mse']:.4f}")
    print("  → Sangat kecil karena perubahan hanya ±1")
    print(f"  PSNR = {metrics['psnr']:.2f} dB")
    print("  → Sangat tinggi! 1-bit LSB gives excellent quality")
    
    print("\n📊 INTERPRETASI:")
    if metrics['psnr'] >= 50:
        print("  ✅ PSNR ≥ 50 dB = Excellent quality")
        print("  ✅ Perubahan tidak terlihat mata manusia")
        print("  ✅ Aman untuk steganography")
    elif metrics['psnr'] >= 40:
        print("  ✅ PSNR ≥ 40 dB = Very good quality")
    
    print(f"\n📌 THRESHOLD CHECK:")
    print(f"  Course guideline: {PSNR_THRESHOLD_CONTEXT} dB minimum")
    if is_acceptable_quality(metrics['psnr']):
        print(f"  ✅ {metrics['psnr']:.2f} dB ≥ {PSNR_THRESHOLD_CONTEXT} dB → ACCEPTABLE")
    else:
        print(f"  ❌ {metrics['psnr']:.2f} dB < {PSNR_THRESHOLD_CONTEXT} dB → BELOW THRESHOLD")
    
    input("\nPress Enter to continue...")


def test_3_medium_difference():
    """Test 3: Medium difference."""
    print_separator()
    print("TEST 3: Medium Difference")
    print_separator()
    
    print("\n📚 KONSEP:")
    print("Perubahan sedang pada pixel values:")
    print("  Expected: PSNR moderate (30-40 dB)")
    print("  Might be visible on close inspection")
    
    print("\n" + "-"*70)
    print("CREATING IMAGES WITH MEDIUM DIFFERENCE...")
    print("-"*70)
    
    # Create images with medium difference
    cover = np.full((200, 200, 3), 128, dtype=np.uint8)
    stego = np.full((200, 200, 3), 136, dtype=np.uint8)  # +8 difference
    
    print(f"Cover image: All pixels = 128")
    print(f"Stego image: All pixels = 136")
    print(f"Difference: +8 per pixel")
    
    print("\n" + "-"*70)
    print("CALCULATING METRICS...")
    print("-"*70)
    
    metrics = calculate_metrics(cover, stego)
    print_metrics(metrics)
    
    print("\n💡 PENJELASAN:")
    print(f"  MSE = {metrics['mse']:.4f}")
    print(f"  → (136-128)² = 8² = 64")
    print(f"  PSNR = {metrics['psnr']:.2f} dB")
    
    print("\n📊 INTERPRETASI:")
    if metrics['psnr'] >= 40:
        print("  ✅ Very good quality")
    elif metrics['psnr'] >= 30:
        print("  ✅ Acceptable quality")
    else:
        print("  ⚠️  Below recommended threshold")
    
    input("\nPress Enter to continue...")


def test_4_large_difference():
    """Test 4: Large difference."""
    print_separator()
    print("TEST 4: Large Difference")
    print_separator()
    
    print("\n📚 KONSEP:")
    print("Perubahan besar pada pixel values:")
    print("  Expected: PSNR low (<30 dB)")
    print("  Clearly visible difference")
    
    print("\n" + "-"*70)
    print("CREATING IMAGES WITH LARGE DIFFERENCE...")
    print("-"*70)
    
    # Create images with large difference
    cover = np.full((200, 200, 3), 100, dtype=np.uint8)
    stego = np.full((200, 200, 3), 200, dtype=np.uint8)  # +100 difference
    
    print(f"Cover image: All pixels = 100")
    print(f"Stego image: All pixels = 200")
    print(f"Difference: +100 per pixel")
    
    print("\n" + "-"*70)
    print("CALCULATING METRICS...")
    print("-"*70)
    
    metrics = calculate_metrics(cover, stego)
    print_metrics(metrics)
    
    print("\n💡 PENJELASAN:")
    print(f"  MSE = {metrics['mse']:.4f}")
    print(f"  → (200-100)² = 100² = 10,000")
    print(f"  PSNR = {metrics['psnr']:.2f} dB")
    print("  → Low PSNR means poor quality (visible difference)")
    
    print("\n⚠️  INTERPRETASI:")
    print("  ❌ PSNR < 30 dB = Below threshold")
    print("  ❌ Difference is clearly visible")
    print("  ❌ NOT suitable for steganography")
    
    input("\nPress Enter to continue...")


def test_5_maximum_difference():
    """Test 5: Maximum difference."""
    print_separator()
    print("TEST 5: Maximum Difference (Black vs White)")
    print_separator()
    
    print("\n📚 KONSEP:")
    print("Maximum possible difference: 0 vs 255")
    print("  MSE = 255² = 65,025")
    print("  PSNR = minimum possible (~8 dB)")
    
    print("\n" + "-"*70)
    print("CREATING BLACK AND WHITE IMAGES...")
    print("-"*70)
    
    # Create black and white images
    cover = np.zeros((200, 200, 3), dtype=np.uint8)  # Black
    stego = np.full((200, 200, 3), 255, dtype=np.uint8)  # White
    
    print(f"Cover image: All pixels = 0 (black)")
    print(f"Stego image: All pixels = 255 (white)")
    print(f"Difference: +255 per pixel (maximum)")
    
    print("\n" + "-"*70)
    print("CALCULATING METRICS...")
    print("-"*70)
    
    metrics = calculate_metrics(cover, stego)
    print_metrics(metrics)
    
    print("\n💡 PENJELASAN:")
    print(f"  MSE = {metrics['mse']:.4f}")
    print(f"  → (255-0)² = 255² = 65,025 (MAXIMUM)")
    print(f"  PSNR = {metrics['psnr']:.2f} dB")
    print("  → Minimum possible PSNR")
    print("  → Completely different images!")
    
    print("\n📐 FORMULA VERIFICATION:")
    print(f"  PSNR = 10 × log₁₀(255² / {metrics['mse']:.1f})")
    print(f"       = 10 × log₁₀({255**2} / {metrics['mse']:.1f})")
    print(f"       = 10 × log₁₀({255**2 / metrics['mse']:.6f})")
    print(f"       = 10 × {np.log10(255**2 / metrics['mse']):.6f}")
    print(f"       = {metrics['psnr']:.2f} dB")
    
    input("\nPress Enter to continue...")


def test_6_compare_modifications():
    """Test 6: Compare different modifications."""
    print_separator()
    print("TEST 6: Compare Different Modifications")
    print_separator()
    
    print("\n📚 KONSEP:")
    print("Membandingkan berbagai tingkat modifikasi:")
    print("  1-bit change vs 2-bit change vs 4-bit change")
    
    print("\n" + "-"*70)
    print("CREATING BASE IMAGE...")
    print("-"*70)
    
    np.random.seed(42)
    cover = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    
    scenarios = [
        ("1-bit LSB", 1),
        ("2-bit LSB", 3),
        ("4-bit LSB", 15),
    ]
    
    print(f"Cover image: 200×200 RGB random image")
    print(f"\nTesting {len(scenarios)} scenarios:")
    
    results = []
    for i, (name, xor_mask) in enumerate(scenarios, 1):
        print(f"\n{'-'*70}")
        print(f"Scenario {i}: {name}")
        print(f"{'-'*70}")
        
        # Create stego with different bit modifications
        stego = cover.copy()
        mask = np.random.rand(200, 200, 3) < 0.5
        stego[mask] ^= xor_mask
        
        num_changed = np.sum(mask)
        
        print(f"Modification: XOR with {xor_mask:08b}")
        print(f"Pixels modified: {num_changed:,} ({num_changed/(200*200*3)*100:.1f}%)")
        
        metrics = calculate_metrics(cover, stego)
        results.append((name, metrics))
        
        print(f"\nResults:")
        print_metrics(metrics, "  ")
    
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    
    print(f"\n{'Scenario':<20} {'MSE':<12} {'PSNR':<12} {'Quality'}")
    print("-"*70)
    for name, metrics in results:
        mse_str = f"{metrics['mse']:.4f}"
        psnr_str = format_psnr(metrics['psnr'])
        print(f"{name:<20} {mse_str:<12} {psnr_str:<12} {metrics['quality_assessment']}")
    
    print("\n💡 OBSERVATION:")
    print("  More bits changed → Higher MSE → Lower PSNR")
    print("  1-bit LSB is best for steganography (highest PSNR)")
    
    input("\nPress Enter to continue...")


def test_7_per_channel():
    """Test 7: Per-channel analysis."""
    print_separator()
    print("TEST 7: Per-Channel MSE Analysis")
    print_separator()
    
    print("\n📚 KONSEP:")
    print("Analisis MSE untuk setiap color channel (R, G, B) secara terpisah")
    print("  Useful untuk debug: channel mana yang paling terpengaruh?")
    
    print("\n" + "-"*70)
    print("CREATING IMAGES WITH CHANNEL-SPECIFIC CHANGES...")
    print("-"*70)
    
    # Create image with different changes per channel
    cover = np.full((200, 200, 3), 128, dtype=np.uint8)
    stego = cover.copy()
    
    # Modify each channel differently
    stego[:, :, 0] += 1  # Red: +1
    stego[:, :, 1] += 2  # Green: +2
    stego[:, :, 2] += 3  # Blue: +3
    
    print(f"Cover: All channels = 128")
    print(f"Stego modifications:")
    print(f"  Red (R):   128 → 129 (+1)")
    print(f"  Green (G): 128 → 130 (+2)")
    print(f"  Blue (B):  128 → 131 (+3)")
    
    print("\n" + "-"*70)
    print("CALCULATING PER-CHANNEL MSE...")
    print("-"*70)
    
    per_channel = calculate_per_channel_mse(cover, stego)
    
    print(f"\nResults:")
    print(f"  Red channel MSE:   {per_channel['r']:.4f} (diff=1, squared=1)")
    print(f"  Green channel MSE: {per_channel['g']:.4f} (diff=2, squared=4)")
    print(f"  Blue channel MSE:  {per_channel['b']:.4f} (diff=3, squared=9)")
    print(f"  Overall MSE:       {per_channel['overall']:.4f} (average: (1+4+9)/3)")
    
    print("\n💡 PENJELASAN:")
    print("  MSE_red = (129-128)² = 1² = 1.0")
    print("  MSE_green = (130-128)² = 2² = 4.0")
    print("  MSE_blue = (131-128)² = 3² = 9.0")
    print(f"  MSE_overall = (1 + 4 + 9) / 3 = {per_channel['overall']:.4f}")
    
    print("\n📊 INTERPRETASI:")
    print("  Blue channel has highest MSE (most affected)")
    print("  Red channel has lowest MSE (least affected)")
    print("  Useful for optimizing embedding strategy!")
    
    # Also show PSNR
    overall_psnr = calculate_psnr(cover, stego)
    print(f"\n  Overall PSNR: {format_psnr(overall_psnr)}")
    
    input("\nPress Enter to continue...")


def test_8_threshold():
    """Test 8: PSNR threshold test."""
    print_separator()
    print("TEST 8: PSNR Threshold Test (30 dB)")
    print_separator()
    
    print("\n📚 KONSEP:")
    print(f"Course guideline: PSNR ≥ {PSNR_THRESHOLD_CONTEXT} dB is acceptable")
    print("  Note: Ini adalah GUIDELINE, bukan hard requirement")
    print("  Actual acceptable PSNR depends on application")
    
    print("\n" + "-"*70)
    print("TESTING IMAGES AROUND 30 dB THRESHOLD...")
    print("-"*70)
    
    # Calculate MSE needed for different PSNR values
    # PSNR = 10 * log10(255^2 / MSE)
    # MSE = 255^2 / 10^(PSNR/10)
    
    test_psnrs = [25, 28, 30, 32, 35, 40]
    
    cover = np.zeros((200, 200, 3), dtype=np.uint8)
    
    print(f"\n{'Target PSNR':<15} {'Calculated MSE':<15} {'Actual PSNR':<15} {'Acceptable?'}")
    print("-"*70)
    
    for target_psnr in test_psnrs:
        # Calculate MSE for target PSNR
        target_mse = 255**2 / (10 ** (target_psnr / 10))
        
        # Calculate actual PSNR (should match target)
        actual_psnr = calculate_psnr(cover, cover, mse=target_mse)
        
        # Check if acceptable
        acceptable = "✅ YES" if is_acceptable_quality(actual_psnr) else "❌ NO"
        
        print(f"{target_psnr} dB{'':<9} {target_mse:<15.4f} {actual_psnr:.2f} dB{'':<8} {acceptable}")
    
    print("\n💡 INTERPRETATION:")
    print(f"  PSNR ≥ {PSNR_THRESHOLD_CONTEXT} dB → Acceptable quality")
    print(f"  PSNR < {PSNR_THRESHOLD_CONTEXT} dB → Below threshold")
    print("\n  Higher PSNR = Better quality")
    print("  Lower PSNR = More visible artifacts")
    
    print("\n📌 IMPORTANT NOTE:")
    print(f"  {PSNR_THRESHOLD_CONTEXT} dB is from academic literature (course material)")
    print("  It's a GUIDELINE, not absolute requirement")
    print("  Some applications may accept lower PSNR")
    print("  Some applications may require higher PSNR")
    
    input("\nPress Enter to continue...")


def test_9_config():
    """Test 9: Show configuration."""
    print_separator()
    print("CONFIGURATION")
    print_separator()
    
    print("\nT15 - MSE & PSNR Metrics Configuration:")
    
    print("\n" + "-"*70)
    print("MSE (Mean Squared Error)")
    print("-"*70)
    print("  Formula: MSE = (1/N) × Σ(cover[i] - stego[i])²")
    print("  Range: 0.0 to 65,025.0 (for 8-bit images)")
    print("  Interpretation:")
    print("    - 0.0 = Identical images")
    print("    - Lower = Better (less difference)")
    print("    - 65,025 = Maximum difference (0 vs 255)")
    
    print("\n" + "-"*70)
    print("PSNR (Peak Signal-to-Noise Ratio)")
    print("-"*70)
    print("  Formula: PSNR = 10 × log₁₀(MAX² / MSE)")
    print("           where MAX = 255 for 8-bit images")
    print("  Unit: Decibels (dB)")
    print("  Range: ~10 dB to ∞")
    print("  Interpretation:")
    print("    - ∞ = Identical images (MSE=0)")
    print("    - ≥50 dB = Excellent quality")
    print("    - ≥40 dB = Very good quality")
    print(f"    - ≥{PSNR_THRESHOLD_CONTEXT} dB = Acceptable (course guideline)")
    print(f"    - <{PSNR_THRESHOLD_CONTEXT} dB = Below threshold")
    print("    - <20 dB = Poor quality")
    
    print("\n" + "-"*70)
    print("THRESHOLD CONTEXT")
    print("-"*70)
    print(f"  Default threshold: {PSNR_THRESHOLD_CONTEXT} dB")
    print("  Source: Course material / Academic literature")
    print("  Status: GUIDELINE (not hard requirement)")
    print("  Note: Actual acceptable PSNR varies by:")
    print("    - Application requirements")
    print("    - Image content type")
    print("    - User perception tolerance")
    
    print("\n" + "-"*70)
    print("SPECIAL CASES")
    print("-"*70)
    print("  MSE = 0:")
    print("    → Images are identical")
    print("    → PSNR = infinity (∞)")
    print("    → Represented as float('inf') in Python")
    
    print("\n" + "-"*70)
    print("TYPICAL VALUES FOR STEGANOGRAPHY")
    print("-"*70)
    print("  1-bit LSB (full capacity):")
    print("    MSE: ~0.33")
    print("    PSNR: ~52-53 dB (Excellent)")
    print("  ")
    print("  1-bit LSB (50% capacity):")
    print("    MSE: ~0.17")
    print("    PSNR: ~55-56 dB (Excellent)")
    print("  ")
    print("  2-bit LSB:")
    print("    MSE: ~1-2")
    print("    PSNR: ~45-48 dB (Very good)")
    
    input("\nPress Enter to continue...")


def main():
    """Main interactive loop."""
    while True:
        menu()
        choice = input("Pilih menu (0-9): ").strip()
        
        if choice == '0':
            print("\n✨ Terima kasih sudah testing T15!")
            print("💪 MSE & PSNR metrics ready for steganography evaluation!\n")
            break
        elif choice == '1':
            test_1_identical()
        elif choice == '2':
            test_2_small_difference()
        elif choice == '3':
            test_3_medium_difference()
        elif choice == '4':
            test_4_large_difference()
        elif choice == '5':
            test_5_maximum_difference()
        elif choice == '6':
            test_6_compare_modifications()
        elif choice == '7':
            test_7_per_channel()
        elif choice == '8':
            test_8_threshold()
        elif choice == '9':
            test_9_config()
        else:
            print("\n❌ Pilihan tidak valid. Silakan pilih 0-9.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing dibatalkan. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
