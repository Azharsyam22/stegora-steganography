"""
Generate test images untuk manual testing
Run: python generate_test_images.py
"""
from PIL import Image
import os

# Create test_images directory
os.makedirs('test_images', exist_ok=True)

print("Generating test images...")

# 1. Small PNG RGB (valid)
img1 = Image.new('RGB', (200, 200), color=(255, 100, 100))
img1.save('test_images/small_rgb.png')
print("✓ test_images/small_rgb.png (200×200 RGB)")

# 2. Medium PNG RGB (valid)
img2 = Image.new('RGB', (640, 480), color=(100, 150, 255))
img2.save('test_images/medium_rgb.png')
print("✓ test_images/medium_rgb.png (640×480 RGB)")

# 3. Large PNG RGB (valid)
img3 = Image.new('RGB', (1920, 1080), color=(150, 200, 100))
img3.save('test_images/large_rgb.png')
print("✓ test_images/large_rgb.png (1920×1080 RGB)")

# 4. PNG RGBA with alpha (valid)
img4 = Image.new('RGBA', (400, 300), color=(200, 100, 150, 128))
img4.save('test_images/rgba_alpha.png')
print("✓ test_images/rgba_alpha.png (400×300 RGBA)")

# 5. BMP RGB (valid)
img5 = Image.new('RGB', (500, 500), color=(255, 200, 50))
img5.save('test_images/valid_bmp.bmp')
print("✓ test_images/valid_bmp.bmp (500×500 RGB)")

# 6. JPEG (should be REJECTED)
img6 = Image.new('RGB', (300, 300), color=(100, 200, 255))
img6.save('test_images/invalid_jpeg.jpg', format='JPEG')
print("✓ test_images/invalid_jpeg.jpg (JPEG - should REJECT)")

# 7. Grayscale PNG (should be REJECTED)
img7 = Image.new('L', (250, 250), color=128)
img7.save('test_images/invalid_grayscale.png')
print("✓ test_images/invalid_grayscale.png (Grayscale - should REJECT)")

# 8. Very tiny PNG (low capacity)
img8 = Image.new('RGB', (50, 50), color=(255, 128, 0))
img8.save('test_images/tiny_rgb.png')
print("✓ test_images/tiny_rgb.png (50×50 RGB - low capacity)")

print("\n✅ Test images generated in 'test_images/' folder")
print("\nTest Matrix:")
print("=" * 60)
print("VALID IMAGES (should accept):")
print("  - small_rgb.png (200×200 RGB) → ~15 KB capacity")
print("  - medium_rgb.png (640×480 RGB) → ~113 KB capacity")
print("  - large_rgb.png (1920×1080 RGB) → ~777 KB capacity")
print("  - rgba_alpha.png (400×300 RGBA) → ~44 KB capacity")
print("  - valid_bmp.bmp (500×500 BMP RGB) → ~93 KB capacity")
print("  - tiny_rgb.png (50×50 RGB) → ~873 B capacity")
print("\nINVALID IMAGES (should reject):")
print("  - invalid_jpeg.jpg → Error: 'Unsupported format JPEG'")
print("  - invalid_grayscale.png → Error: 'Unsupported mode L'")
print("=" * 60)
