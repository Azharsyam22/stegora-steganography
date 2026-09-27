"""
Stegora Testing Matrix Module

Implements 5×3 testing matrix for comprehensive steganography evaluation.
Tests 5 different cover images with 3 different payload sizes.

Academic Context:
- Systematic testing validates algorithm across various scenarios
- Matrix approach ensures comprehensive coverage
- Real metrics demonstrate actual performance

Testing Matrix:
- 5 cover images (different sizes, content types)
- 3 payload sizes (small, medium, large)
- Total: 15 test cases

Metrics Recorded:
- Image properties (format, dimensions, capacity)
- Payload properties (type, size, utilization)
- Quality metrics (MSE, PSNR)
- Extraction results (success, exact match)

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from PIL import Image
import io
from pathlib import Path
from dataclasses import dataclass, asdict
import json


@dataclass
class TestCase:
    """Single test case in the testing matrix."""
    
    # Test identifiers
    case_id: str
    image_name: str
    payload_name: str
    
    # Image properties
    image_format: str
    image_width: int
    image_height: int
    image_channels: int
    
    # Capacity
    raw_capacity_bytes: int
    usable_capacity_bytes: int
    
    # Payload properties
    payload_type: str
    payload_size_bytes: int
    capacity_utilization: float
    
    # Embedding results
    embedding_success: bool
    embedding_error: Optional[str]
    
    # Quality metrics
    mse: Optional[float]
    psnr: Optional[float]
    
    # Extraction results
    extraction_success: bool
    extraction_error: Optional[str]
    exact_match: bool
    
    # Additional metadata
    password: str
    stego_key: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class TestingMatrix:
    """
    Testing matrix generator and executor.
    
    Manages 5×3 testing matrix:
    - 5 different cover images
    - 3 different payload sizes
    - Total 15 test cases
    """
    
    def __init__(self):
        """Initialize testing matrix."""
        self.test_cases: List[TestCase] = []
        self.results: List[Dict] = []
    
    def generate_test_cases(
        self,
        cover_images: List[Tuple[str, np.ndarray]],
        payloads: List[Tuple[str, bytes, str]],
        password: str = "test_password_123",
        stego_key: str = "test_stego_key_456"
    ) -> List[Dict]:
        """
        Generate test case configurations.
        
        Args:
            cover_images: List of (name, image_array) tuples
            payloads: List of (name, payload_bytes, type) tuples
            password: Password for encryption
            stego_key: Stego key for position generation
        
        Returns:
            List of test case configurations
        """
        test_configs = []
        
        for img_idx, (img_name, img_array) in enumerate(cover_images, 1):
            for payload_idx, (payload_name, payload_bytes, payload_type) in enumerate(payloads, 1):
                case_id = f"T{img_idx}P{payload_idx}"
                
                config = {
                    'case_id': case_id,
                    'image_name': img_name,
                    'image_array': img_array,
                    'payload_name': payload_name,
                    'payload_bytes': payload_bytes,
                    'payload_type': payload_type,
                    'password': password,
                    'stego_key': stego_key
                }
                
                test_configs.append(config)
        
        return test_configs
    
    def execute_test_case(
        self,
        config: Dict,
        embed_fn,
        extract_fn
    ) -> TestCase:
        """
        Execute a single test case.
        
        Args:
            config: Test case configuration
            embed_fn: Embedding function (cover, payload, password, stego_key) -> (stego, metrics)
            extract_fn: Extraction function (stego, password, stego_key) -> payload
        
        Returns:
            TestCase with results
        """
        case_id = config['case_id']
        img_name = config['image_name']
        img_array = config['image_array']
        payload_name = config['payload_name']
        payload_bytes = config['payload_bytes']
        payload_type = config['payload_type']
        password = config['password']
        stego_key = config['stego_key']
        
        # Image properties
        height, width = img_array.shape[:2]
        channels = img_array.shape[2] if img_array.ndim == 3 else 1
        
        # Detect format from image name
        img_format = Path(img_name).suffix.upper().replace('.', '') or 'PNG'
        
        # Calculate capacity (simplified - actual calculation should use capacity module)
        raw_bits = width * height * min(channels, 3)  # RGB only
        raw_capacity_bytes = raw_bits // 8
        
        # Estimate overhead (simplified)
        overhead_bytes = 100  # Approximate header + crypto overhead
        usable_capacity_bytes = raw_capacity_bytes - overhead_bytes
        
        payload_size = len(payload_bytes)
        capacity_utilization = payload_size / usable_capacity_bytes if usable_capacity_bytes > 0 else 0.0
        
        # Initialize test case
        test_case = TestCase(
            case_id=case_id,
            image_name=img_name,
            payload_name=payload_name,
            image_format=img_format,
            image_width=width,
            image_height=height,
            image_channels=channels,
            raw_capacity_bytes=raw_capacity_bytes,
            usable_capacity_bytes=usable_capacity_bytes,
            payload_type=payload_type,
            payload_size_bytes=payload_size,
            capacity_utilization=capacity_utilization,
            embedding_success=False,
            embedding_error=None,
            mse=None,
            psnr=None,
            extraction_success=False,
            extraction_error=None,
            exact_match=False,
            password=password,
            stego_key=stego_key
        )
        
        # Try embedding
        try:
            stego_array, metrics = embed_fn(
                img_array,
                payload_bytes,
                password,
                stego_key
            )
            
            test_case.embedding_success = True
            test_case.mse = metrics.get('mse')
            test_case.psnr = metrics.get('psnr')
            
            # Try extraction
            try:
                extracted_bytes = extract_fn(
                    stego_array,
                    password,
                    stego_key
                )
                
                test_case.extraction_success = True
                test_case.exact_match = (extracted_bytes == payload_bytes)
                
            except Exception as e:
                test_case.extraction_success = False
                test_case.extraction_error = str(e)
                test_case.exact_match = False
        
        except Exception as e:
            test_case.embedding_success = False
            test_case.embedding_error = str(e)
        
        return test_case
    
    def execute_matrix(
        self,
        test_configs: List[Dict],
        embed_fn,
        extract_fn
    ) -> List[TestCase]:
        """
        Execute all test cases in matrix.
        
        Args:
            test_configs: List of test configurations
            embed_fn: Embedding function
            extract_fn: Extraction function
        
        Returns:
            List of TestCase results
        """
        results = []
        
        for config in test_configs:
            test_case = self.execute_test_case(config, embed_fn, extract_fn)
            results.append(test_case)
        
        self.test_cases = results
        return results
    
    def get_summary(self) -> Dict:
        """
        Get summary statistics of matrix results.
        
        Returns:
            Dictionary with summary metrics
        """
        if not self.test_cases:
            return {}
        
        total = len(self.test_cases)
        embed_success = sum(1 for tc in self.test_cases if tc.embedding_success)
        extract_success = sum(1 for tc in self.test_cases if tc.extraction_success)
        exact_match = sum(1 for tc in self.test_cases if tc.exact_match)
        
        # Calculate average metrics
        valid_mse = [tc.mse for tc in self.test_cases if tc.mse is not None]
        valid_psnr = [tc.psnr for tc in self.test_cases if tc.psnr is not None]
        
        avg_mse = sum(valid_mse) / len(valid_mse) if valid_mse else None
        avg_psnr = sum(valid_psnr) / len(valid_psnr) if valid_psnr else None
        
        # Utilization stats
        utilizations = [tc.capacity_utilization for tc in self.test_cases]
        avg_utilization = sum(utilizations) / len(utilizations) if utilizations else 0.0
        
        return {
            'total_cases': total,
            'embedding_success_count': embed_success,
            'embedding_success_rate': embed_success / total if total > 0 else 0.0,
            'extraction_success_count': extract_success,
            'extraction_success_rate': extract_success / total if total > 0 else 0.0,
            'exact_match_count': exact_match,
            'exact_match_rate': exact_match / total if total > 0 else 0.0,
            'average_mse': avg_mse,
            'average_psnr': avg_psnr,
            'average_utilization': avg_utilization
        }
    
    def to_dict_list(self) -> List[Dict]:
        """Convert all test cases to list of dictionaries."""
        return [tc.to_dict() for tc in self.test_cases]


def create_test_payloads() -> List[Tuple[str, bytes, str]]:
    """
    Create standard test payloads (small, medium, large).
    
    Returns:
        List of (name, bytes, type) tuples
    """
    payloads = []
    
    # Small payload: 100 bytes
    small_text = "Small test payload. " * 5  # ~100 bytes
    payloads.append(("small_100B", small_text.encode('utf-8'), "text"))
    
    # Medium payload: 1KB
    medium_text = "Medium test payload with more content. " * 25  # ~1KB
    payloads.append(("medium_1KB", medium_text.encode('utf-8'), "text"))
    
    # Large payload: 10KB
    large_text = "Large test payload with substantial data. " * 230  # ~10KB
    payloads.append(("large_10KB", large_text.encode('utf-8'), "text"))
    
    return payloads


def create_test_images() -> List[Tuple[str, np.ndarray]]:
    """
    Create standard test cover images.
    
    Returns:
        List of (name, image_array) tuples
    """
    images = []
    
    # Image 1: Small 100×100
    img1 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    images.append(("test_100x100.png", img1))
    
    # Image 2: Medium 300×300
    img2 = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
    images.append(("test_300x300.png", img2))
    
    # Image 3: Large 500×500
    img3 = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
    images.append(("test_500x500.png", img3))
    
    # Image 4: Wide 800×400
    img4 = np.random.randint(0, 256, (400, 800, 3), dtype=np.uint8)
    images.append(("test_800x400.png", img4))
    
    # Image 5: Tall 400×800
    img5 = np.random.randint(0, 256, (800, 400, 3), dtype=np.uint8)
    images.append(("test_400x800.png", img5))
    
    return images


# Export public API
__all__ = [
    'TestCase',
    'TestingMatrix',
    'create_test_payloads',
    'create_test_images'
]
