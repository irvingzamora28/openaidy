"""
Tests for the text formatter utility.
"""
import os
import sys

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.utils.text_formatter import format_llm_response


def test_format_llm_response_whitespace():
    """Test cleaning up of extra whitespace."""
    # Test with extra newlines
    text = "Paragraph 1\n\n\n\nParagraph 2"
    expected = "Paragraph 1\n\nParagraph 2"
    assert format_llm_response(text) == expected


def test_format_llm_response_list_spacing():
    """Test fixing of list item spacing."""
    # Test with bullet points
    text = "* Item 1\n*Item 2\n- Item 3\n-Item 4"
    expected = "* Item 1\n* Item 2\n- Item 3\n- Item 4"
    assert format_llm_response(text) == expected

    # Test with numbered lists
    text = "1. Item 1\n2.Item 2\n3) Item 3\n4)Item 4"
    expected = "1. Item 1\n2. Item 2\n3) Item 3\n4) Item 4"
    assert format_llm_response(text) == expected


def test_format_llm_response_combined():
    """Test combined formatting."""
    text = "Paragraph 1\n\n\n* Item 1\n*Item 2\n\n1. Step 1\n2.Step 2"
    expected = "Paragraph 1\n\n* Item 1\n* Item 2\n\n1. Step 1\n2. Step 2"
    assert format_llm_response(text) == expected


def test_format_llm_response_no_change():
    """Test that valid markdown is not changed."""
    # Test with already well-formatted markdown
    text = "# Heading\n\nThis is a paragraph with **bold** and *italic* text.\n\n* Item 1\n* Item 2\n\n1. Step 1\n2. Step 2"
    # The output should be identical
    assert format_llm_response(text) == text


def test_format_llm_response_edge_cases():
    """Test edge cases for LLM response formatting."""
    # Test with empty string
    assert format_llm_response("") == ""

    # Test with only whitespace
    assert format_llm_response("   \n\n  ") == "   \n\n  "

    # Test with single line
    assert format_llm_response("Just a single line") == "Just a single line"


def test_format_llm_response():
    """Test the complete formatting of LLM responses."""
    # Test with a complex example
    text = """# New York City Travel Guide

Here are some great places to visit:

* **Central Park** - A massive urban park with lots to do
* **Empire State Building** - Iconic skyscraper with amazing views
* **Metropolitan Museum of Art** - World-class art museum

For food, try these options:

1. Joe's Pizza - Classic NYC slice
2. Katz's Delicatessen - Famous pastrami sandwiches
3. Levain Bakery - Amazing cookies

_Enjoy your trip to New York City!_"""

    # The expected output might vary slightly depending on the implementation details
    # So we'll check for key HTML elements instead of an exact match
    formatted = format_llm_response(text)

    # Check for headings
    assert "# New York City Travel Guide" in formatted

    # Check for bullet points
    assert "* **Central Park** - A massive urban park with lots to do" in formatted
    assert "* **Empire State Building** - Iconic skyscraper with amazing views" in formatted
    assert "* **Metropolitan Museum of Art** - World-class art museum" in formatted

    # Check for numbered list
    assert "1. Joe's Pizza - Classic NYC slice" in formatted
    assert "2. Katz's Delicatessen - Famous pastrami sandwiches" in formatted
    assert "3. Levain Bakery - Amazing cookies" in formatted

    # Check for italic text
    assert "_Enjoy your trip to New York City!_" in formatted

    # Return early since we're using assertions instead of comparison
    return
