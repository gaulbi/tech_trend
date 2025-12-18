"""
Google Gemini embedding provider implementation.
"""
import os
from typing import List

import google.generativeai as genai

from .base import EmbeddingProvider
from ..exceptions import EmbeddingError


class GeminiProvider(EmbeddingProvider):
    """Google Gemini embedding provider."""
    
    def __init__(
        self,
        model: str,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize Gemini provider.
        
        Args:
            model: Model name
            timeout: API timeout in seconds
            max_retries: Maximum retry attempts
            
        Raises:
            EmbeddingError: If API key is not found
        """
        super().__init__(model, timeout, max_retries)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EmbeddingError(
                "GEMINI_API_KEY not found in environment"
            )
        
        genai.configure(api_key=api_key)
        self.timeout = timeout
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Gemini API.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]
