"""
Unit tests for stegora.analysis.testing_matrix module

Tests 5×3 testing matrix generation and execution.

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

import pytest
import numpy as np

from stegora.analysis.testing_matrix import (
    TestCase,
    TestingMatrix,
    create_test_payloads,
    create_test_images
)


class TestTestCase:
    """Test TestCase dataclass."""
    
    def test_test_case_creation(self):
        """Test creating a test case."""
        tc = TestCase(
            case_id="T1P1",
            image_name="test.png",
            payload_name="small",
            image_format="PNG",
            image_width=100,
            image_height=100,
            image_channels=3,
            raw_capacity_bytes=3750,
            usable_capacity_bytes=3650,
            payload_type="text",
            payload_size_bytes=100,
            capacity_utilization=0.027,
            embedding_success=True,
            embedding_error=None,
            mse=0.5,
            psnr=51.13,
            extraction_success=True,
            extraction_error=None,
            exact_match=True,
            password="test123",
            stego_key="key456"
        )
        
        assert tc.case_id == "T1P1"
        assert tc.embedding_success is True
        assert tc.exact_match is True
    
    def test_to_dict(self):
        """Test converting test case to dictionary."""
        tc = TestCase(
            case_id="T1P1",
            image_name="test.png",
            payload_name="small",
            image_format="PNG",
            image_width=100,
            image_height=100,
            image_channels=3,
            raw_capacity_bytes=3750,
            usable_capacity_bytes=3650,
            payload_type="text",
            payload_size_bytes=100,
            capacity_utilization=0.027,
            embedding_success=True,
            embedding_error=None,
            mse=0.5,
            psnr=51.13,
            extraction_success=True,
            extraction_error=None,
            exact_match=True,
            password="test123",
            stego_key="key456"
        )
        
        d = tc.to_dict()
        
        assert isinstance(d, dict)
        assert d['case_id'] == "T1P1"
        assert d['embedding_success'] is True


class TestTestingMatrix:
    """Test TestingMatrix class."""
    
    def test_matrix_initialization(self):
        """Test initializing testing matrix."""
        matrix = TestingMatrix()
        
        assert matrix.test_cases == []
        assert matrix.results == []
    
    def test_generate_test_cases(self):
        """Test generating test case configurations."""
        matrix = TestingMatrix()
        
        # Create 2 images and 2 payloads = 4 test cases
        images = [
            ("img1.png", np.zeros((100, 100, 3), dtype=np.uint8)),
            ("img2.png", np.zeros((200, 200, 3), dtype=np.uint8))
        ]
        
        payloads = [
            ("small", b"test" * 25, "text"),  # 100 bytes
            ("medium", b"test" * 250, "text")  # 1000 bytes
        ]
        
        configs = matrix.generate_test_cases(images, payloads)
        
        assert len(configs) == 4  # 2×2 = 4
        assert configs[0]['case_id'] == "T1P1"
        assert configs[1]['case_id'] == "T1P2"
        assert configs[2]['case_id'] == "T2P1"
        assert configs[3]['case_id'] == "T2P2"
    
    def test_execute_test_case(self):
        """Test executing a single test case."""
        matrix = TestingMatrix()
        
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        payload = b"test data"
        
        config = {
            'case_id': 'T1P1',
            'image_name': 'test.png',
            'image_array': img,
            'payload_name': 'small',
            'payload_bytes': payload,
            'payload_type': 'text',
            'password': 'pass123',
            'stego_key': 'key456'
        }
        
        # Mock embed/extract functions
        def mock_embed(img, payload, password, stego_key):
            return img, {'mse': 0.5, 'psnr': 51.0}
        
        def mock_extract(stego, password, stego_key):
            return payload
        
        tc = matrix.execute_test_case(config, mock_embed, mock_extract)
        
        assert tc.case_id == 'T1P1'
        assert tc.embedding_success is True
        assert tc.extraction_success is True
        assert tc.exact_match is True
    
    def test_get_summary(self):
        """Test getting summary statistics."""
        matrix = TestingMatrix()
        
        # Create mock test cases
        matrix.test_cases = [
            TestCase(
                case_id=f"T{i}P1",
                image_name="test.png",
                payload_name="small",
                image_format="PNG",
                image_width=100,
                image_height=100,
                image_channels=3,
                raw_capacity_bytes=3750,
                usable_capacity_bytes=3650,
                payload_type="text",
                payload_size_bytes=100,
                capacity_utilization=0.027,
                embedding_success=True,
                embedding_error=None,
                mse=0.5,
                psnr=51.0,
                extraction_success=True,
                extraction_error=None,
                exact_match=True,
                password="test",
                stego_key="key"
            )
            for i in range(1, 6)
        ]
        
        summary = matrix.get_summary()
        
        assert summary['total_cases'] == 5
        assert summary['embedding_success_count'] == 5
        assert summary['embedding_success_rate'] == 1.0
        assert summary['exact_match_rate'] == 1.0
        assert summary['average_mse'] == 0.5
        assert summary['average_psnr'] == 51.0


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_create_test_payloads(self):
        """Test creating test payloads."""
        payloads = create_test_payloads()
        
        assert len(payloads) == 3  # small, medium, large
        
        # Check names
        names = [p[0] for p in payloads]
        assert "small_100B" in names
        assert "medium_1KB" in names
        assert "large_10KB" in names
        
        # Check sizes (approximate)
        small_size = len(payloads[0][1])
        medium_size = len(payloads[1][1])
        large_size = len(payloads[2][1])
        
        assert 90 <= small_size <= 110  # ~100 bytes
        assert 900 <= medium_size <= 1100  # ~1KB
        assert 9000 <= large_size <= 11000  # ~10KB
    
    def test_create_test_images(self):
        """Test creating test images."""
        images = create_test_images()
        
        assert len(images) == 5  # 5 different images
        
        # Check dimensions
        dims = [(img[1].shape[1], img[1].shape[0]) for img in images]
        
        assert (100, 100) in dims
        assert (300, 300) in dims
        assert (500, 500) in dims
        assert (800, 400) in dims
        assert (400, 800) in dims
