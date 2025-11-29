"""
LLM Client Implementations

Concrete implementations for OpenAI, DeepSeek, Claude, and Ollama.
"""

import logging
import requests
from typing import Optional
from src.article_generator.llm_client_base import LLMClientBase

logger = logging.getLogger(__name__)


class OpenAIClient(LLMClientBase):
    """OpenAI API client."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(model, timeout, max_retries)
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def generate(self, prompt: str) -> str:
        """Generate text using OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']


class DeepSeekClient(LLMClientBase):
    """DeepSeek API client."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(model, timeout, max_retries)
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate(self, prompt: str) -> str:
        """Generate text using DeepSeek API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']


class ClaudeClient(LLMClientBase):
    """Claude (Anthropic) API client."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        super().__init__(model, timeout, max_retries)
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def generate(self, prompt: str) -> str:
        """Generate text using Claude API."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['content'][0]['text']


class OllamaClient(LLMClientBase):
    """Ollama local API client."""
    
    def __init__(
        self,
        model: str,
        timeout: int = 60,
        max_retries: int = 3,
        base_url: str = "http://localhost:11434"
    ):
        super().__init__(model, timeout, max_retries)
        self.base_url = f"{base_url}/api/generate"
    
    def generate(self, prompt: str) -> str:
        """Generate text using Ollama API."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            self.base_url,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['response']