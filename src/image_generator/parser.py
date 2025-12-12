"""
Markdown file parser for extracting article summaries.
"""
import re
from pathlib import Path
from typing import Optional

from .exceptions import ValidationError


class MarkdownParser:
    """Parser for extracting article summaries from markdown files."""
    
    SUMMARY_PATTERN = re.compile(
        r'##\s+Summary\s*\n(.*?)\n##\s+Full Article',
        re.DOTALL | re.IGNORECASE
    )
    
    @classmethod
    def extract_summary(cls, md_content: str) -> str:
        """
        Extract summary section from markdown content.
        
        Args:
            md_content: Markdown file content
            
        Returns:
            Extracted summary text
            
        Raises:
            ValidationError: If summary section not found
        """
        match = cls.SUMMARY_PATTERN.search(md_content)
        
        if not match:
            raise ValidationError(
                "Could not find Summary section in markdown file. "
                "Expected format: '## Summary' followed by '## Full Article'"
            )
        
        summary = match.group(1).strip()
        
        if not summary or not summary.strip():
            raise ValidationError("Summary section is empty or whitespace")
        
        return summary
    
    @classmethod
    def parse_file(cls, file_path: Path) -> str:
        """
        Parse markdown file and extract summary.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Extracted summary text
            
        Raises:
            ValidationError: If file cannot be parsed
        """
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() != '.md':
            raise ValidationError(
                f"Invalid file type: {file_path.suffix}. Expected .md"
            )
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            raise ValidationError(f"Failed to read file {file_path}: {e}")
        
        return cls.extract_summary(content)
