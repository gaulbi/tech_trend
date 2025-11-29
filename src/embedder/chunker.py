"""Text chunking with overlap for RAG applications."""

from typing import List


class TextChunker:
    """Chunks text into overlapping segments."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        """
        Initialize text chunker.

        Args:
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Number of overlapping characters.

        Raises:
            ValueError: If parameters are invalid.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text to chunk.

        Returns:
            List of text chunks.
        """
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary if possible
            if end < len(text):
                chunk = self._break_at_sentence(chunk, text[end:])

            chunks.append(chunk.strip())

            # Move start position with overlap
            start = end - self.chunk_overlap

            # Prevent infinite loop if chunk_overlap equals chunk_size
            if start <= chunks[-1].find(chunks[-1][:50]):
                start = end

        return [c for c in chunks if c]

    def _break_at_sentence(self, chunk: str, next_text: str) -> str:
        """
        Attempt to break chunk at sentence boundary.

        Args:
            chunk: Current chunk text.
            next_text: Text following the chunk.

        Returns:
            Adjusted chunk text.
        """
        sentence_endings = [".", "!", "?", "\n"]

        # Look for sentence ending in last 100 characters
        for i in range(len(chunk) - 1, max(0, len(chunk) - 100), -1):
            if chunk[i] in sentence_endings:
                # Check if next character is space or end
                if i == len(chunk) - 1 or chunk[i + 1].isspace():
                    return chunk[: i + 1]

        return chunk