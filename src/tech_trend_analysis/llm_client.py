# ============================================================================
# FILE: src/tech_trend_analysis/llm_client.py
# ============================================================================
"""LLM client implementations with factory pattern."""

import os
import sys
import time
from abc import ABC, abstractmethod
from typing import Optional
import json

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv package is not installed.", file=sys.stderr)
    print("Please install it with: pip install python-dotenv", file=sys.stderr)
    sys.exit(1)

from .exceptions import LLMError

# Load environment variables
load_dotenv()


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(
        self,
        model: str,
        timeout: int,
        retry: int
    ):
        """
        Initialize LLM client.
        
        Args:
            model: Model identifier
            timeout: Request timeout in seconds
            retry: Number of retry attempts
        """
        self.model = model
        self.timeout = timeout
        self.retry = retry
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If generation fails
        """
        pass
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(self.retry):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.retry - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        raise LLMError(
            f"Failed after {self.retry} attempts: {last_exception}"
        )


class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""
    
    def __init__(self, model: str, timeout: int, retry: int):
        super().__init__(model, timeout, retry)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise LLMError(
                "OPENAI_API_KEY not found in environment. "
                "Please add it to your .env file."
            )
    
    def generate(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        try:
            from openai import OpenAI
        except ImportError:
            raise LLMError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )
        
        def _call_api():
            client = OpenAI(api_key=self.api_key, timeout=self.timeout)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        return self._retry_with_backoff(_call_api)


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API client."""
    
    def __init__(self, model: str, timeout: int, retry: int):
        super().__init__(model, timeout, retry)
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise LLMError(
                "DEEPSEEK_API_KEY not found in environment. "
                "Please add it to your .env file."
            )
    
    def generate(self, prompt: str) -> str:
        """Generate response using DeepSeek API."""
        try:
            from openai import OpenAI
        except ImportError:
            raise LLMError(
                "OpenAI package not installed (required for DeepSeek). "
                "Install with: pip install openai"
            )
        
        def _call_api():
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
                timeout=self.timeout
            )
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        return self._retry_with_backoff(_call_api)


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, model: str, timeout: int, retry: int):
        super().__init__(model, timeout, retry)
        self.api_key = os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise LLMError(
                "CLAUDE_API_KEY not found in environment. "
                "Please add it to your .env file."
            )
    
    def generate(self, prompt: str) -> str:
        """Generate response using Claude API."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise LLMError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )
        
        def _call_api():
            client = Anthropic(
                api_key=self.api_key,
                timeout=self.timeout
            )
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        return self._retry_with_backoff(_call_api)


class OllamaClient(BaseLLMClient):
    """Ollama local API client."""
    
    def __init__(self, model: str, timeout: int, retry: int):
        super().__init__(model, timeout, retry)
    
    def generate(self, prompt: str) -> str:
        """Generate response using Ollama API."""
        try:
            import requests
        except ImportError:
            raise LLMError(
                "Requests package not installed. "
                "Install with: pip install requests"
            )
        
        def _call_api():
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['response']
        
        return self._retry_with_backoff(_call_api)


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    _clients = {
        'openai': OpenAIClient,
        'deepseek': DeepSeekClient,
        'claude': ClaudeClient,
        'ollama': OllamaClient
    }
    
    @classmethod
    def create(
        cls,
        server: str,
        model: str,
        timeout: int,
        retry: int
    ) -> BaseLLMClient:
        """
        Create LLM client based on server type.
        
        Args:
            server: Server type (openai, deepseek, claude, ollama)
            model: Model identifier
            timeout: Request timeout
            retry: Retry attempts
            
        Returns:
            Configured LLM client
            
        Raises:
            LLMError: If server type is unsupported
        """
        client_class = cls._clients.get(server.lower())
        if not client_class:
            raise LLMError(
                f"Unsupported LLM server: {server}. "
                f"Supported: {', '.join(cls._clients.keys())}"
            )
        
        return client_class(model, timeout, retry)