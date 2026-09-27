"""
Streamlit session state management
Centralized state handling for stable demo flow
"""
import streamlit as st
from typing import Optional, Any, Dict
from PIL import Image


def init_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        # Embed page state
        'cover_image': None,
        'cover_metadata': None,
        'cover_capacity': None,
        'stego_image': None,
        'embed_metadata': None,
        'embed_success': False,
        
        # Extract page state
        'stego_input_image': None,
        'stego_input_metadata': None,
        'extracted_data': None,
        'extract_success': False,
        'extract_error': None,
        
        # Analyze page state
        'analyze_cover': None,
        'analyze_stego': None,
        'analysis_results': None,
        
        # Demo credentials (for quick testing)
        'demo_mode': False,
        'last_password': '',
        'last_stego_key': '',
        
        # Session flow tracking
        'last_embed_time': None,
        'last_extract_time': None,
        'demo_step': 0,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def clear_embed_state():
    """Clear embed-related session state"""
    st.session_state.cover_image = None
    st.session_state.cover_metadata = None
    st.session_state.cover_capacity = None
    st.session_state.stego_image = None
    st.session_state.embed_metadata = None
    st.session_state.embed_success = False


def clear_extract_state():
    """Clear extract-related session state"""
    st.session_state.stego_input_image = None
    st.session_state.stego_input_metadata = None
    st.session_state.extracted_data = None
    st.session_state.extract_success = False
    st.session_state.extract_error = None


def clear_all_state():
    """Clear all session state (fresh start)"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def save_embed_result(stego_image: Image.Image, metadata: Dict[str, Any]):
    """Save embed result to session state"""
    st.session_state.stego_image = stego_image
    st.session_state.embed_metadata = metadata
    st.session_state.embed_success = True
    import datetime
    st.session_state.last_embed_time = datetime.datetime.now()


def save_extract_result(plaintext: bytes, metadata: Dict[str, Any]):
    """Save extract result to session state"""
    st.session_state.extracted_data = {
        'plaintext': plaintext,
        **metadata
    }
    st.session_state.extract_success = True
    st.session_state.extract_error = None
    import datetime
    st.session_state.last_extract_time = datetime.datetime.now()


def save_extract_error(error_message: str):
    """Save extract error to session state"""
    st.session_state.extracted_data = None
    st.session_state.extract_success = False
    st.session_state.extract_error = error_message


def get_demo_credentials() -> tuple:
    """Get demo credentials for quick testing"""
    return ('demopassword123', 'demostegokey456')


def enable_demo_mode():
    """Enable demo mode with pre-filled credentials"""
    st.session_state.demo_mode = True


def disable_demo_mode():
    """Disable demo mode"""
    st.session_state.demo_mode = False


def is_demo_mode() -> bool:
    """Check if demo mode is enabled"""
    return st.session_state.get('demo_mode', False)


def store_credentials(password: str, stego_key: str):
    """Store last used credentials (for convenience, not for security)"""
    st.session_state.last_password = password
    st.session_state.last_stego_key = stego_key


def get_stored_credentials() -> tuple:
    """Get last used credentials"""
    return (
        st.session_state.get('last_password', ''),
        st.session_state.get('last_stego_key', '')
    )


def has_embed_result() -> bool:
    """Check if there's a successful embed result"""
    return (
        st.session_state.get('embed_success', False) and
        st.session_state.get('stego_image') is not None
    )


def has_extract_result() -> bool:
    """Check if there's a successful extract result"""
    return (
        st.session_state.get('extract_success', False) and
        st.session_state.get('extracted_data') is not None
    )


def get_embed_result() -> Optional[tuple]:
    """Get embed result (stego_image, metadata) if available"""
    if has_embed_result():
        return (
            st.session_state.stego_image,
            st.session_state.embed_metadata
        )
    return None


def get_extract_result() -> Optional[Dict[str, Any]]:
    """Get extract result if available"""
    if has_extract_result():
        return st.session_state.extracted_data
    return None


def get_extract_error() -> Optional[str]:
    """Get extract error message if any"""
    return st.session_state.get('extract_error')
