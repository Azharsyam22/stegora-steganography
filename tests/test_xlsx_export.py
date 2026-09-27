"""
Unit tests for stegora.analysis.xlsx_export module

Tests XLSX export functionality.

Author: Hana (247006111170)
Course: Information Security - Universitas Siliwangi
"""

import pytest
from pathlib import Path
import tempfile

from stegora.analysis.xlsx_export import (
    XLSXExporter,
    export_matrix_to_xlsx,
    OPENPYXL_AVAILABLE
)


@pytest.mark.skipif(not OPENPYXL_AVAILABLE, reason="openpyxl not installed")
class TestXLSXExporter:
    """Test XLSX exporter."""
    
    def test_exporter_initialization(self):
        """Test initializing exporter."""
        exporter = XLSXExporter()
        assert exporter.workbook is None
    
    def test_export_to_xlsx(self, tmp_path):
        """Test exporting to XLSX file."""
        # Create mock data
        test_cases = [
            {
                'case_id': 'T1P1',
                'image_name': 'test.png',
                'image_format': 'PNG',
                'image_width': 100,
                'image_height': 100,
                'image_channels': 3,
                'usable_capacity_bytes': 3650,
                'payload_name': 'small',
                'payload_type': 'text',
                'payload_size_bytes': 100,
                'capacity_utilization': 0.027,
                'embedding_success': True,
                'mse': 0.5,
                'psnr': 51.0,
                'extraction_success': True,
                'exact_match': True
            }
        ]
        
        summary = {
            'total_cases': 1,
            'embedding_success_count': 1,
            'embedding_success_rate': 1.0,
            'extraction_success_count': 1,
            'extraction_success_rate': 1.0,
            'exact_match_count': 1,
            'exact_match_rate': 1.0,
            'average_mse': 0.5,
            'average_psnr': 51.0,
            'average_utilization': 0.027
        }
        
        output_path = tmp_path / "test_results.xlsx"
        
        exporter = XLSXExporter()
        exporter.export_to_xlsx(test_cases, summary, str(output_path))
        
        # Check file exists
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    def test_convenience_function(self, tmp_path):
        """Test convenience export function."""
        test_cases = [
            {
                'case_id': 'T1P1',
                'image_name': 'test.png',
                'image_format': 'PNG',
                'image_width': 100,
                'image_height': 100,
                'image_channels': 3,
                'usable_capacity_bytes': 3650,
                'payload_name': 'small',
                'payload_type': 'text',
                'payload_size_bytes': 100,
                'capacity_utilization': 0.027,
                'embedding_success': True,
                'mse': 0.5,
                'psnr': 51.0,
                'extraction_success': True,
                'exact_match': True
            }
        ]
        
        summary = {
            'total_cases': 1,
            'embedding_success_count': 1,
            'embedding_success_rate': 1.0,
            'extraction_success_count': 1,
            'extraction_success_rate': 1.0,
            'exact_match_count': 1,
            'exact_match_rate': 1.0,
            'average_mse': 0.5,
            'average_psnr': 51.0,
            'average_utilization': 0.027
        }
        
        output_path = tmp_path / "test_results2.xlsx"
        
        export_matrix_to_xlsx(test_cases, summary, str(output_path))
        
        assert output_path.exists()


class TestOpenpyxlAvailability:
    """Test openpyxl availability check."""
    
    def test_openpyxl_available_flag(self):
        """Test OPENPYXL_AVAILABLE flag."""
        assert isinstance(OPENPYXL_AVAILABLE, bool)
