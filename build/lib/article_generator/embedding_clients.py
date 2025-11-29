"""
Embedding Client Implementations

Concrete implementations for OpenAI, Voyage, Gemini, and Sentence Transformers.
"""

import logging
import requests
from typing import List, Optional
from src.article_generator.embedding_client_base import EmbeddingClientBase

logger = logging.getLogger(__name__)


class OpenAIEmbeddingClient(EmbeddingClientBase):
    """OpenAI embedding API client."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(model, timeout, max_retries)
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/embeddings"
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": text
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['data'][0]['embedding']


class VoyageEmbeddingClient(EmbeddingClientBase):
    """Voyage AI embedding API client."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(model, timeout, max_retries)
        self.api_key = api_key
        self.base_url = "https://api.voyageai.com/v1/embeddings"
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding using Voyage AI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": text
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['data'][0]['embedding']


class GeminiEmbeddingClient(EmbeddingClientBase):
    """Google Gemini embedding API client."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(model, timeout, max_retries)
        self.api_key = api_key
        self.base_url = f"https://generativelanguage.googleapis.com/v1/models/{model}:embedContent"
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding using Gemini API."""
        params = {"key": self.api_key}
        
        payload = {
            "content": {
                "parts": [{"text": text}]
            }
        }
        
        response = requests.post(
            self.base_url,
            params=params,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['embedding']['values']


class SentenceTransformerClient(EmbeddingClientBase):
    """Sentence Transformers local embedding client."""
    
    def __init__(
        self,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(model, timeout, max_retries)
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model_instance = SentenceTransformer(model)
            logger.info(f"Loaded SentenceTransformer model: {model}")
        except ImportError:
            raise ImportError(
                "sentence-transformers package not installed. "
                "Install with: pip install sentence-transformers"
            )
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding using Sentence Transformers."""
        embedding = self.model_instance.encode(text, convert_to_tensor=False)
        return embedding.tolist()