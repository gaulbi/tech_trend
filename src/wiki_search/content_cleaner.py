"""
Content cleaning utilities for Wikipedia text.
"""

import re


class ContentCleaner:
    """Cleans Wikipedia content by removing citations and references."""

    # Patterns for content cleaning
    CITATION_PATTERN = re.compile(r'\[\d+\]|\[citation needed\]')
    
    # More flexible reference section patterns
    REFERENCE_SECTION_PATTERN = re.compile(
        r'==\s*References?\s*==.*',
        re.IGNORECASE | re.DOTALL
    )
    
    # Additional section patterns with flexible spacing
    SECTION_PATTERNS = [
        re.compile(r'==\s*See also\s*==.*', re.IGNORECASE | re.DOTALL),
        re.compile(r'==\s*External links?\s*==.*', re.IGNORECASE | re.DOTALL),
        re.compile(r'==\s*Further reading\s*==.*', re.IGNORECASE | re.DOTALL),
        re.compile(r'==\s*Notes?\s*==.*', re.IGNORECASE | re.DOTALL),
        re.compile(r'==\s*Bibliography\s*==.*', re.IGNORECASE | re.DOTALL),
        re.compile(r'==\s*Sources?\s*==.*', re.IGNORECASE | re.DOTALL),
    ]

    @classmethod
    def clean(cls, content: str) -> str:
        """
        Clean Wikipedia content.

        Removes:
        - Citation markers ([1], [23], [citation needed])
        - Reference sections and everything after
        - Other metadata sections (See also, External links, etc.)
        - Excessive whitespace while preserving paragraph breaks

        Args:
            content: Raw Wikipedia content

        Returns:
            Cleaned content string
        """
        if not content:
            return ""

        # Remove citation markers
        cleaned = cls.CITATION_PATTERN.sub('', content)

        # Remove reference section and everything after
        cleaned = cls.REFERENCE_SECTION_PATTERN.sub('', cleaned)

        # Remove other metadata sections
        for pattern in cls.SECTION_PATTERNS:
            cleaned = pattern.sub('', cleaned)

        # Normalize excessive whitespace while preserving paragraphs
        # Replace 3+ newlines with 2 newlines (paragraph break)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Replace multiple spaces with single space
        cleaned = re.sub(r' {2,}', ' ', cleaned)
        
        # Clean up spacing around newlines
        cleaned = re.sub(r' *\n *', '\n', cleaned)

        # Clean up spacing around punctuation
        cleaned = cleaned.strip()

        return cleaned