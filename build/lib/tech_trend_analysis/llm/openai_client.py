"""OpenAI LLM client implementation."""

import os
import time
from typing import Optional

from openai import OpenAI, OpenAIError

from ..exceptions import LLMProviderError
from .base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        """
        Initialize OpenAI client.
        
        Args:
            model: OpenAI model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMProviderError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key, timeout=timeout)
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            LLMProviderError: If generation fails after retries
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content or ""
            except OpenAIError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMProviderError(f"OpenAI API error: {e}")
        
        raise LLMProviderError("Max retries exceeded")