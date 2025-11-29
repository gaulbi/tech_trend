"""Ollama LLM client implementation."""

import time

import requests

from ..exceptions import LLMProviderError
from .base import BaseLLMClient


class OllamaClient(BaseLLMClient):
    """Ollama local LLM client."""
    
    API_BASE_URL = "http://localhost:11434/api/generate"
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        """
        Initialize Ollama client.
        
        Args:
            model: Ollama model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        super().__init__(model, timeout, max_retries)
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using Ollama API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            LLMProviderError: If generation fails after retries
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.API_BASE_URL,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except (requests.RequestException, KeyError) as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMProviderError(f"Ollama API error: {e}")
        
        raise LLMProviderError("Max retries exceeded")