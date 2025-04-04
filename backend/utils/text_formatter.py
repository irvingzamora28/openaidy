"""
Text formatting utilities for LLM responses.
"""
import re


def format_llm_response(text: str) -> str:
    """
    Format LLM response text to improve readability.

    Args:
        text: The raw text from the LLM

    Returns:
        Formatted text with proper Markdown formatting
    """
    # The LLM responses are already in Markdown format
    # We'll just ensure the Markdown is clean and consistent

    # Clean up any extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Ensure proper spacing for bullet lists
    # Fix cases like "*Item" to "* Item"
    text = re.sub(r'(^|\n)\*(\S)', r'\1* \2', text)
    # Fix cases like "-Item" to "- Item"
    text = re.sub(r'(^|\n)\-(\S)', r'\1- \2', text)

    # Ensure proper spacing for numbered lists
    # Fix cases like "1.Item" to "1. Item"
    text = re.sub(r'(^|\n)(\d+)\.(\S)', r'\1\2. \3', text)
    # Fix cases like "1)Item" to "1) Item"
    text = re.sub(r'(^|\n)(\d+)\)(\S)', r'\1\2) \3', text)

    return text


# These functions are no longer used but kept for reference
# The LLM responses are already in Markdown format, so we just need to clean them up
