"""Claude (Anthropic) LLM client implementation."""

import os
import time

import anthropic

from ..exceptions import LLMProviderError
from .base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """Claude (Anthropic) API client."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        """
        Initialize Claude client.
        
        Args:
            model: Claude model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise LLMProviderError("CLAUDE_API_KEY not found in environment")
        self.client = anthropic.Anthropic(api_key=api_key, 
                                          timeout=timeout)
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using Claude API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            LLMProviderError: If generation fails after retries
        """
        for attempt in range(self.max_retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            except anthropic.AnthropicError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMProviderError(f"Claude API error: {e}")
        
        raise LLMProviderError("Max retries exceeded")