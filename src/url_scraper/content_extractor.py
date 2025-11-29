"""Content extraction and cleaning utilities."""

import re
from typing import Optional
from bs4 import BeautifulSoup, Comment
from readability import Document


class ContentExtractor:
    """Extract and clean readable content from HTML."""
    
    @staticmethod
    def extract_clean_content(html: str) -> str:
        """
        Extract and clean readable content from HTML.
        
        Args:
            html: Raw HTML content
            
        Returns:
            str: Cleaned, readable text content
        """
        # Use readability to extract main content
        doc = Document(html)
        readable_html = doc.summary()
        
        # Parse with BeautifulSoup for cleaning
        soup = BeautifulSoup(readable_html, 'html.parser')
        
        # Remove unwanted elements
        ContentExtractor._remove_unwanted_elements(soup)
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Normalize whitespace
        text = ContentExtractor._normalize_whitespace(text)
        
        return text
    
    @staticmethod
    def _remove_unwanted_elements(soup: BeautifulSoup) -> None:
        """
        Remove script, style, and other unwanted elements.
        
        Args:
            soup: BeautifulSoup object to clean (modified in place)
        """
        # Elements to remove
        unwanted_tags = [
            'script', 'style', 'meta', 'noscript', 
            'iframe', 'embed', 'object'
        ]
        
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove comments
        for comment in soup.find_all(
            string=lambda text: isinstance(text, Comment)
        ):
            comment.extract()
        
        # Remove hidden elements
        for element in soup.find_all(style=re.compile(r'display:\s*none')):
            element.decompose()
    
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Normalized text
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()