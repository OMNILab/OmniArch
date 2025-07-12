"""
PyTest configuration and fixtures for the streamlit application tests
"""

import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the project root and modules to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'modules'))

@pytest.fixture(autouse=True)
def mock_streamlit():
    """Mock streamlit module for all tests"""
    # Create a mock streamlit module
    streamlit_mock = MagicMock()
    streamlit_mock.session_state = {}
    streamlit_mock.success = MagicMock()
    streamlit_mock.error = MagicMock()
    streamlit_mock.stop = MagicMock()
    
    # Replace streamlit in sys.modules if it exists
    sys.modules['streamlit'] = streamlit_mock
    
    yield streamlit_mock
    
    # Clean up
    if 'streamlit' in sys.modules:
        del sys.modules['streamlit']