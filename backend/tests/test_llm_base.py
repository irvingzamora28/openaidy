"""
Tests for the LLM base class.
"""
import os
import sys
import pytest
from abc import ABC

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.llm.base import LLMProvider


def test_llm_provider_is_abstract():
    """Test that LLMProvider is an abstract base class."""
    assert issubclass(LLMProvider, ABC)
    
    # Verify that we can't instantiate it directly
    with pytest.raises(TypeError):
        LLMProvider()
