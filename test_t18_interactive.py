"""
Interactive Test Script for T18: Testing Matrix & XLSX Export
Tests 5×3 matrix execution and XLSX export functionality
"""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from stegora.analysis.testing_matrix import TestingMatrix, TestCase
from stegora.analysis.xlsx_export import XLSXExporter


def create_test_images():
    """Create 5 test images with different characteristics"""
    print("\n" + "="*60)
    print("CREATING TEST IMAGES")
    print("="*60)
    
    test_dir = Path("test_t18_images")
    test_dir.mkdir(exist_ok=True)
    
    images = []
    
    # 1. Small uniform image (100x100)
    print("\n1. Creating small uniform image (100x100)...")
    img1 = Image.new('RGB', (100, 100), color=(128, 128, 128))
    path1 = test_dir / "small_uniform.png"
    img1.save(path1)
    images.append(path1)
    print(f"   ✓ Saved: {path1}")
    print(f"   Size: {img1.size}, Capacity: ~{100*100*3} bytes")
    
    # 2. Medium gradient image (200x200)
    print("\n2. Creating medium gradient image (200x200)...")
    arr2 = np.zeros((200, 200, 3), dtype=np.uint8)
    for i in range(200):
        arr2[i, :] = [int(i * 255/200), int(i * 255/200), int(i * 255/200)]
    img2 = Image.fromarray(arr2)
    path2 = test_dir / "medium_gradient.png"
    img2.save(path2)
    images.append(path2)
    print(f"   ✓ Saved: {path2}")
    print(f"   Size: {img2.size}, Capacity: ~{200*200*3} bytes")
    
    # 3. Large random pattern (300x300)
    print("\n3. Creating large random pattern (300x300)...")
    arr3 = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
    img3 = Image.fromarray(arr3)
    path3 = test_dir / "large_random.png"
    img3.save(path3)
    images.append(path3)
    print(f"   ✓ Saved: {path3}")
    print(f"   Size: {img3.size}, Capacity: ~{300*300*3} bytes")
    
    # 4. Checkerboard pattern (150x150)
    print("\n4. Creating checkerboard pattern (150x150)...")
    arr4 = np.zeros((150, 150, 3), dtype=np.uint8)
    for i in range(150):
        for j in range(150):
            if (i // 10 + j // 10) % 2 == 0:
                arr4[i, j] = [255, 255, 255]
    img4 = Image.fromarray(arr4)
    path4 = test_dir / "checkerboard.png"
    img4.save(path4)
    images.append(path4)
    print(f"   ✓ Saved: {path4}")
    print(f"   Size: {img4.size}, Capacity: ~{150*150*3} bytes")
    
    # 5. Colorful stripes (250x250)
    print("\n5. Creating colorful stripes (250x250)...")
    arr5 = np.zeros((250, 250, 3), dtype=np.uint8)
    for i in range(250):
        if i < 83:
            arr5[i, :] = [255, 0, 0]  # Red
        elif i < 166:
            arr5[i, :] = [0, 255, 0]  # Green
        else:
            arr5[i, :] = [0, 0, 255]  # Blue
    img5 = Image.fromarray(arr5)
    path5 = test_dir / "colorful_stripes.png"
    img5.save(path5)
    images.append(path5)
    print(f"   ✓ Saved: {path5}")
    print(f"   Size: {img5.size}, Capacity: ~{250*250*3} bytes")
    
    return images


def create_test_payloads():
    """Create 3 test payloads with different sizes"""
    print("\n" + "="*60)
    print("CREATING TEST PAYLOADS")
    print("="*60)
    
    # 1. Small payload (50 bytes)
    payload1 = b"Small test payload for steganography testing!"
    print(f"\n1. Small payload: {len(payload1)} bytes")
    print(f"   Content: {payload1.decode('utf-8', errors='replace')}")
    
    # 2. Medium payload (200 bytes)
    payload2 = b"M" * 200
    print(f"\n2. Medium payload: {len(payload2)} bytes")
    print(f"   Content: {'M' * 50}... (repeated)")
    
    # 3. Large payload (1000 bytes)
    payload3 = b"Large payload with mixed content: " + bytes(range(256)) * 3 + b"END"
    print(f"\n3. Large payload: {len(payload3)} bytes")
    print(f"   Content: Mixed binary data")
    
    return [payload1, payload2, payload3]


def test_testing_matrix():
    """Test the 5×3 testing matrix execution"""
    print("\n" + "="*60)
    print("TESTING MATRIX EXECUTION")
    print("="*60)
    
    # Create test data
    image_paths = create_test_images()
    payloads = create_test_payloads()
    
    # Load images as numpy arrays
    print("\n" + "-"*60)
    print("Loading images as numpy arrays...")
    print("-"*60)
    
    cover_images = []
    for path in image_paths:
        img = Image.open(path)
        img_array = np.array(img)
        name = path.stem
        cover_images.append((name, img_array))
        print(f"  ✓ Loaded {name}: {img_array.shape}")
    
    # Prepare payload tuples (name, bytes, type)
    payload_tuples = [
        ("small", payloads[0], "text"),
        ("medium", payloads[1], "binary"),
        ("large", payloads[2], "mixed")
    ]
    
    print("\n" + "-"*60)
    print("Executing 5×3 Testing Matrix (5 images × 3 payloads = 15 tests)")
    print("-"*60)
    
    # Initialize testing matrix
    matrix = TestingMatrix()
    
    # Generate test configurations
    print("\nGenerating test configurations...")
    test_configs = matrix.generate_test_cases(
        cover_images=cover_images,
        payloads=payload_tuples
    )
    print(f"  ✓ Generated {len(test_configs)} test configurations")
    
    # Create mock embed/extract functions for testing framework
    def mock_embed(cover, payload, password, stego_key):
        """Mock embed function for testing framework"""
        # Simulate successful embedding
        stego = cover.copy()
        # Add minimal LSB changes
        if stego.size > 0:
            stego.flat[0] = (stego.flat[0] & 0xFE) | 1
        return stego
    
    def mock_extract(stego, password, stego_key, payload_size):
        """Mock extract function for testing framework"""
        # For this test, return the expected payload based on size
        # Find matching payload
        for _, payload_bytes, _ in payload_tuples:
            if len(payload_bytes) == payload_size:
                return payload_bytes
        return b"mock_extracted_data"
    
    # Execute matrix
    print("\nRunning tests...")
    results = matrix.execute_matrix(
        test_configs=test_configs,
        embed_fn=mock_embed,
        extract_fn=mock_extract
    )
    
    print(f"\n✓ Completed {len(results)} test cases")
    
    # Display summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r.embedding_success and r.extraction_success]
    failed = [r for r in results if not (r.embedding_success and r.extraction_success)]
    
    print(f"\n✓ Successful: {len(successful)}/{len(results)}")
    print(f"✗ Failed: {len(failed)}/{len(results)}")
    
    # Display detailed results
    print("\n" + "-"*60)
    print("DETAILED RESULTS")
    print("-"*60)
    
    for i, result in enumerate(results, 1):
        print(f"\nTest {i}: {result.case_id} - {result.image_name} × {result.payload_name}")
        print(f"  Status: {'✓ SUCCESS' if result.embedding_success else '✗ FAILED'}")
        print(f"  Image: {result.image_width}×{result.image_height}×{result.image_channels}")
        print(f"  Capacity: {result.usable_capacity_bytes:,} bytes")
        print(f"  Payload: {result.payload_size_bytes:,} bytes ({result.payload_type})")
        print(f"  Utilization: {result.capacity_utilization:.2f}%")
        
        if result.embedding_success:
            print(f"  MSE: {result.mse:.6f}")
            print(f"  PSNR: {result.psnr:.2f} dB")
            print(f"  Extraction: {'✓ Match' if result.exact_match else '✗ Mismatch'}")
        else:
            print(f"  Error: {result.embedding_error or result.extraction_error}")
    
    return results


def test_xlsx_export(results):
    """Test XLSX export functionality"""
    print("\n" + "="*60)
    print("TESTING XLSX EXPORT")
    print("="*60)
    
    output_path = Path("test_t18_matrix_results.xlsx")
    
    print(f"\nExporting results to: {output_path}")
    
    # Convert TestCase objects to dictionaries
    test_cases_dict = [r.to_dict() for r in results]
    
    # Generate summary statistics
    matrix = TestingMatrix()
    matrix.test_cases = results
    summary = matrix.get_summary()
    
    # Create exporter and export
    exporter = XLSXExporter()
    exporter.export_to_xlsx(test_cases_dict, summary, str(output_path))
    
    print(f"✓ Export completed!")
    
    # Verify file
    if output_path.exists():
        file_size = output_path.stat().st_size
        print(f"\n✓ File created successfully")
        print(f"  Path: {output_path.absolute()}")
        print(f"  Size: {file_size:,} bytes")
        print(f"\nYou can open this file in Excel/LibreOffice to view formatted results")
        return True
    else:
        print(f"\n✗ File was not created")
        return False


def verify_xlsx_structure(results):
    """Verify the structure of exported XLSX"""
    print("\n" + "="*60)
    print("VERIFYING XLSX STRUCTURE")
    print("="*60)
    
    try:
        from openpyxl import load_workbook
        
        wb = load_workbook("test_t18_matrix_results.xlsx")
        ws = wb.active
        
        print(f"\n✓ Workbook loaded successfully")
        print(f"  Active sheet: {ws.title}")
        print(f"  Dimensions: {ws.dimensions}")
        
        # Check headers
        headers = [cell.value for cell in ws[1]]
        print(f"\n✓ Headers ({len(headers)} columns):")
        for i, header in enumerate(headers, 1):
            print(f"  {i}. {header}")
        
        # Check data rows
        data_rows = ws.max_row - 1  # Exclude header
        print(f"\n✓ Data rows: {data_rows}")
        print(f"  Expected: {len(results)}")
        
        if data_rows == len(results):
            print(f"  ✓ Row count matches!")
        else:
            print(f"  ✗ Row count mismatch!")
        
        # Sample first data row
        if ws.max_row > 1:
            print(f"\n✓ Sample data (Row 2):")
            for i, cell in enumerate(ws[2], 1):
                if headers[i-1]:
                    print(f"  {headers[i-1]}: {cell.value}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error verifying XLSX: {e}")
        return False


def main():
    """Main test execution"""
    print("="*60)
    print("T18 INTERACTIVE TEST: Testing Matrix & XLSX Export")
    print("="*60)
    print("\nThis script will test:")
    print("1. Creating 5 test images with different characteristics")
    print("2. Creating 3 test payloads with different sizes")
    print("3. Executing 5×3 testing matrix (15 test cases)")
    print("4. Exporting results to XLSX with formatting")
    print("5. Verifying XLSX structure and content")
    
    print("\nStarting tests automatically...")
    
    try:
        # Test 1: Execute testing matrix
        results = test_testing_matrix()
        
        # Test 2: Export to XLSX
        export_success = test_xlsx_export(results)
        
        # Test 3: Verify XLSX structure
        if export_success:
            verify_xlsx_structure(results)
        
        # Final summary
        print("\n" + "="*60)
        print("FINAL SUMMARY")
        print("="*60)
        
        successful_tests = sum(1 for r in results if r.embedding_success and r.extraction_success)
        print(f"\n✓ Testing Matrix: {successful_tests}/{len(results)} tests passed")
        print(f"✓ XLSX Export: {'Success' if export_success else 'Failed'}")
        
        if successful_tests == len(results) and export_success:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print("\n⚠️  Some tests had issues")
        
        print("\n" + "="*60)
        print("Test files created:")
        print("  - test_t18_images/ (5 test images)")
        print("  - test_t18_matrix_results.xlsx (Excel export)")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
