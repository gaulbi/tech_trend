# ============================================================================
# src/article_generator/utils/text_utils.py
# ============================================================================
"""Text utility functions."""
import re


def slugify(text: str) -> str:
    """
    Convert text to slug format.
    
    Args:
        text: Input text
        
    Returns:
        Slugified text
        
    Example:
        >>> slugify("Agentic AI Patterns!")
        'agentic-ai-patterns'
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = text.strip('-')
    return text
