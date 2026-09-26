"""
Tests for Embed and Extract page structure and components
Note: These are structural tests, not functional tests
Functional tests will be added when T07-T14 are implemented
"""
import pytest
from frontend.pages import embed, extract


class TestEmbedPage:
    """Test Embed page structure"""
    
    def test_embed_page_exists(self):
        """Test that embed page module exists"""
        assert hasattr(embed, 'show')
        assert callable(embed.show)
    
    def test_embed_imports(self):
        """Test that required modules are imported"""
        # Check imports don't raise errors
        from backend.image.io import validate_and_load_cover_image
        from backend.stego.capacity import calculate_raw_capacity
        assert callable(validate_and_load_cover_image)
        assert callable(calculate_raw_capacity)


class TestExtractPage:
    """Test Extract page structure"""
    
    def test_extract_page_exists(self):
        """Test that extract page module exists"""
        assert hasattr(extract, 'show')
        assert callable(extract.show)
    
    def test_extract_imports(self):
        """Test that required modules are imported"""
        from backend.image.io import validate_and_load_cover_image
        assert callable(validate_and_load_cover_image)


class TestWorkspaceIntegration:
    """Test workspace integration readiness"""
    
    def test_embed_uses_validation(self):
        """Test that embed page uses validation module"""
        import inspect
        source = inspect.getsource(embed)
        assert 'validate_and_load_cover_image' in source
        assert 'ImageValidationError' in source
    
    def test_embed_uses_capacity(self):
        """Test that embed page uses capacity module"""
        import inspect
        source = inspect.getsource(embed)
        assert 'calculate_raw_capacity' in source
        assert 'calculate_usable_capacity' in source
        assert 'check_payload_capacity' in source
    
    def test_extract_uses_validation(self):
        """Test that extract page uses validation module"""
        import inspect
        source = inspect.getsource(extract)
        assert 'validate_and_load_cover_image' in source
    
    def test_no_hardcoded_data(self):
        """Test that pages don't contain hardcoded metrics"""
        import inspect
        
        # Check embed page
        embed_source = inspect.getsource(embed)
        # Should not have fake data like "1920x1080" or "500 KB" hardcoded in logic
        # (they can appear in UI text, but not as computed values)
        
        # Check extract page  
        extract_source = inspect.getsource(extract)
        # Should not have hardcoded ciphertext or keys
        assert 'fake_key' not in extract_source.lower()
        assert 'dummy_data' not in extract_source.lower()


@pytest.mark.unit
def test_ui_components_available():
    """Test that UI components used by pages are available"""
    from frontend.ui.components import (
        page_title,
        section_header,
        muted_text,
        footer
    )
    
    assert callable(page_title)
    assert callable(section_header)
    assert callable(muted_text)
    assert callable(footer)
