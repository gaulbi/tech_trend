"""DeepSeek LLM client implementation."""

import os
import time

import requests

from ..exceptions import LLMProviderError
from .base import BaseLLMClient


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API client."""
    
    API_BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        """
        Initialize DeepSeek client.
        
        Args:
            model: DeepSeek model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        super().__init__(model, timeout, max_retries)
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise LLMProviderError("DEEPSEEK_API_KEY not found in environment")
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using DeepSeek API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            LLMProviderError: If generation fails after retries
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.API_BASE_URL,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except (requests.RequestException, KeyError) as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMProviderError(f"DeepSeek API error: {e}")
        
        raise LLMProviderError("Max retries exceeded")