# ============================================================================
# src/article_generator/clients/base.py
# ============================================================================
"""Base classes for clients."""
from abc import ABC, abstractmethod
from typing import List, Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        pass


class BaseEmbeddingClient(ABC):
    """Abstract base class for embedding clients."""
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass
