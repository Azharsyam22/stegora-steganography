# Stegora UI Components Guide

## Overview
Stegora uses a modern, muted, technical aesthetic inspired by security utilities. The UI is built with Streamlit and enhanced with custom components for consistency.

## Color Palette

```python
COLORS = {
    "background": "#F7F8F6",    # Soft warm gray
    "surface": "#FFFFFF",        # Pure white
    "text": "#26343B",          # Dark blue-gray
    "muted": "#6C777C",         # Medium gray
    "accent": "#718E88",        # Muted teal
    "accent_soft": "#E5EEEC",   # Light teal
    "border": "#D9E0DE",        # Light gray
    "success": "#4A9B7F",       # Muted green
    "warning": "#D4A574",       # Muted orange
    "error": "#C7726B",         # Muted red
}
```

## Available Components

### Layout Components

#### `page_title(icon, title, description)`
Standard page header with icon, title, and description.

```python
page_title("📥", "Embed Message", "Hide text or file inside a cover image")
```

#### `section_header(text)`
Uppercase section divider.

```python
section_header("1. Upload Cover Image")
```

#### `footer()`
Consistent page footer.

```python
footer()  # Shows "🔒 Stegora — LSB Steganography with AES-256-GCM"
```

### Data Display

#### `metric_display(label, value, unit="")`
Display metric in card format.

```python
metric_display("Format", "PNG")
metric_display("Capacity", "1024", "bytes")
```

#### `image_info_card(filename, format_type, dimensions, channels, capacity=None)`
Display comprehensive image information.

```python
image_info_card(
    filename="cover.png",
    format_type="PNG",
    dimensions=(800, 600),
    channels=3,
    capacity=180000
)
```

#### `status_badge(text, status="success")`
Colored status badge.

```python
status_badge("Ready", "success")
status_badge("Warning", "warning")
status_badge("Error", "error")
```

### Input Components

#### `credentials_input(key_prefix="")`
Standard password and stego-key input.

```python
password, stego_key = credentials_input("embed")
```

Returns tuple of (password, stego_key).

### Text Components

#### `muted_text(text)`
Display helper text in muted color.

```python
muted_text("This is a helpful hint")
```

## Custom CSS Classes

All custom styling uses `.stegora-*` class prefix to avoid conflicts.

### Card Container
```css
.stegora-card {
    background: #FFFFFF;
    border: 1px solid #D9E0DE;
    border-radius: 8px;
    padding: 1.5rem;
}
```

### Metric Display
```css
.stegora-metric {
    background: #F7F8F6;
    border: 1px solid #D9E0DE;
    border-radius: 6px;
    padding: 1rem;
    text-align: center;
}
```

### Badges
```css
.stegora-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.75rem;
}
```

## Usage Guidelines

### DO ✅
- Use `section_header()` for step divisions
- Use `muted_text()` for hints and helper text
- Use `status_badge()` for status indicators
- Use consistent spacing with `st.markdown("---")`
- Use `page_title()` at the start of every page
- Use `footer()` at the end of every page

### DON'T ❌
- Don't use neon colors or high contrast
- Don't use excessive emojis
- Don't create custom components without `.stegora-` prefix
- Don't use inline styles (use CSS classes)
- Don't hardcode colors (use `theme.get_color()`)
- Don't create overly rounded corners (max 8px)

## Theme Application

Apply theme in `app.py`:

```python
from stegora.ui.theme import apply_theme
apply_theme()
```

## Examples

### Complete Page Structure

```python
from stegora.ui.components import (
    page_title, section_header, 
    credentials_input, footer
)

def show():
    page_title("📥", "Embed", "Description here")
    
    section_header("1. Step One")
    # ... content ...
    
    section_header("2. Step Two")
    # ... content ...
    
    password, stego_key = credentials_input("page")
    
    footer()
```

### Metric Row

```python
col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_display("Format", "PNG")
with col2:
    metric_display("Size", "800×600", "px")
with col3:
    metric_display("Channels", "3")
with col4:
    metric_display("Capacity", "180", "KB")
```

## Testing

UI components have tests in `tests/test_ui_components.py`:
- Theme color palette validation
- Component function existence
- CSS class presence
- Callable verification

Run tests:
```bash
pytest tests/test_ui_components.py -v
```
