"""
Content cleaning utilities for wiki_search module.
"""

import re


def clean_wikipedia_content(content: str) -> str:
    """
    Clean Wikipedia page content by removing citations and unwanted sections.
    
    Args:
        content: Raw Wikipedia content
        
    Returns:
        Cleaned content string
    """
    # Remove citation markers like [1], [23], [citation needed]
    content = re.sub(r'\[\d+\]', '', content)
    content = re.sub(r'\[citation needed\]', '', content, flags=re.IGNORECASE)
    
    # Remove common Wikipedia sections and everything after
    content = _remove_wikipedia_sections(content)
    
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()
    
    return content


def _remove_wikipedia_sections(content: str) -> str:
    """
    Remove common Wikipedia sections like References, External links, etc.
    
    Args:
        content: Content to clean
        
    Returns:
        Content with sections removed
    """
    section_patterns = [
        r'==\s*References\s*==.*',
        r'==\s*External links\s*==.*',
        r'==\s*See also\s*==.*',
        r'==\s*Notes\s*==.*',
        r'==\s*Further reading\s*==.*',
        r'==\s*Bibliography\s*==.*',
    ]
    
    for pattern in section_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    return content