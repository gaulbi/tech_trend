"""
Text chunking functionality.
"""

from typing import List


class TextChunker:
    """Handles text chunking with overlap."""
    
    def __init__(self, chunk_size: int, chunk_overlap: int):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be less than chunk_size"
            )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        # Handle empty or whitespace-only text
        if not text or not text.strip():
            return []
        
        # Strip and normalize whitespace
        text = text.strip()
        
        # If text fits in one chunk, return it
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Get the chunk
            chunk = text[start:end]
            
            # Try to break at sentence boundary if not at the end
            if end < text_length:
                # Look for sentence ending punctuation
                last_period = chunk.rfind('. ')
                last_newline = chunk.rfind('\n')
                last_question = chunk.rfind('? ')
                last_exclamation = chunk.rfind('! ')
                
                break_point = max(
                    last_period,
                    last_newline,
                    last_question,
                    last_exclamation
                )
                
                # If we found a good break point, use it
                # Only break if it's past the halfway point to avoid tiny chunks
                if break_point > self.chunk_size // 2:
                    chunk = chunk[:break_point + 1].strip()
                    end = start + break_point + 1
            
            # Add non-empty chunk
            chunk_stripped = chunk.strip()
            if chunk_stripped:
                chunks.append(chunk_stripped)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Prevent infinite loop: ensure we always move forward
            if start <= len(''.join(chunks)):
                start = end
        
        return chunks