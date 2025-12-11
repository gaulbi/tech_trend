# ============================================================================
# src/article_generator/clients/embedding_clients.py
# ============================================================================
"""Embedding client implementations."""
import time
from typing import List
import requests
from openai import OpenAI
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from .base import BaseEmbeddingClient
from ..exceptions import EmbeddingError


class OpenAIEmbedding(BaseEmbeddingClient):
    """OpenAI embedding client."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize OpenAI embedding client."""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                    timeout=self.timeout
                )
                return [item.embedding for item in response.data]
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise EmbeddingError(f"OpenAI embedding failed: {str(e)}")
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.embed([text])[0]


class VoyageAIEmbedding(BaseEmbeddingClient):
    """VoyageAI embedding client."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize VoyageAI embedding client."""
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://api.voyageai.com/v1/embeddings"
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return [item["embedding"] for item in response.json()["data"]]
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise EmbeddingError(f"VoyageAI embedding failed: {str(e)}")
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.embed([text])[0]


class GeminiEmbedding(BaseEmbeddingClient):
    """Gemini embedding client."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize Gemini embedding client."""
        genai.configure(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        for attempt in range(self.max_retries):
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=texts,
                    task_type="retrieval_document"
                )
                return result['embedding']
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise EmbeddingError(f"Gemini embedding failed: {str(e)}")
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.embed([text])[0]


class SentenceTransformersEmbedding(BaseEmbeddingClient):
    """SentenceTransformers local embedding client."""
    
    def __init__(self, model: str, **kwargs):
        """Initialize SentenceTransformers client."""
        self.model = SentenceTransformer(model)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingError(f"SentenceTransformers failed: {str(e)}")
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.embed([text])[0]
