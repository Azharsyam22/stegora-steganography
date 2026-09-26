"""
Test UI components and theme
"""
import pytest
from stegora.ui import components, theme


class TestTheme:
    """Test theme module"""
    
    def test_colors_defined(self):
        """Test that color palette is defined"""
        assert theme.COLORS is not None
        assert isinstance(theme.COLORS, dict)
        assert len(theme.COLORS) > 0
    
    def test_get_color(self):
        """Test get_color function"""
        color = theme.get_color("accent")
        assert color == "#718E88"
        
        # Test fallback
        unknown = theme.get_color("nonexistent")
        assert unknown == "#000000"
    
    def test_custom_css_exists(self):
        """Test that custom CSS is defined"""
        assert theme.CUSTOM_CSS_LIGHT is not None
        assert isinstance(theme.CUSTOM_CSS_LIGHT, str)
        assert "<style>" in theme.CUSTOM_CSS_LIGHT
        assert ".stegora-card" in theme.CUSTOM_CSS_LIGHT
        
        assert theme.CUSTOM_CSS_DARK is not None
        assert isinstance(theme.CUSTOM_CSS_DARK, str)
        assert "<style>" in theme.CUSTOM_CSS_DARK
        assert ".stegora-card" in theme.CUSTOM_CSS_DARK


class TestComponents:
    """Test UI components module"""
    
    def test_components_module_imports(self):
        """Test that all component functions exist"""
        assert hasattr(components, "section_header")
        assert hasattr(components, "card")
        assert hasattr(components, "metric_display")
        assert hasattr(components, "status_badge")
        assert hasattr(components, "muted_text")
        assert hasattr(components, "page_title")
        assert hasattr(components, "image_info_card")
        assert hasattr(components, "credentials_input")
        assert hasattr(components, "footer")
        assert hasattr(components, "show_progress")
        assert hasattr(components, "show_progress_bar")
    
    def test_components_are_callable(self):
        """Test that component functions are callable"""
        assert callable(components.section_header)
        assert callable(components.metric_display)
        assert callable(components.status_badge)
        assert callable(components.muted_text)
        assert callable(components.footer)


@pytest.mark.unit
def test_theme_color_count():
    """Test that we have all required colors"""
    required_colors = [
        "background", "surface", "text", "muted",
        "accent", "accent_soft", "border",
        "success", "warning", "error"
    ]
    
    for color_name in required_colors:
        assert color_name in theme.COLORS_LIGHT, f"Missing color in LIGHT: {color_name}"
        assert theme.COLORS_LIGHT[color_name].startswith("#"), f"Invalid color format: {color_name}"
        
        assert color_name in theme.COLORS_DARK, f"Missing color in DARK: {color_name}"
        assert theme.COLORS_DARK[color_name].startswith("#"), f"Invalid color format: {color_name}"


@pytest.mark.unit
def test_theme_functions():
    """Test theme utility functions"""
    assert callable(theme.apply_theme)
    assert callable(theme.toggle_theme)
    assert callable(theme.get_current_theme)
    assert callable(theme.get_color)
