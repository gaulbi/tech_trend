"""
LLM Client Module

Provides abstraction layer for multiple LLM providers with retry logic and timeout handling.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    All LLM provider implementations must inherit from this class.
    """
    
    def __init__(self, api_key: str, model: str, timeout: int = 60):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API authentication key
            model: Model identifier
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = 3
        self.retry_delays = [1, 3, 5]  # Exponential backoff delays
    
    @abstractmethod
    def _make_request(self, prompt: str) -> str:
        """
        Make a request to the LLM API.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response as a string
            
        Raises:
            RequestException: If the request fails
        """
        pass
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM with retry logic.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response as a string
            
        Raises:
            RequestException: If all retry attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} to call LLM")
                response = self._make_request(prompt)
                logger.info("LLM request successful")
                return response
                
            except Timeout as e:
                logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
                    
            except RequestException as e:
                logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise


class OpenAIClient(LLMClient):
    """OpenAI API client implementation."""
    
    def __init__(self, api_key: str, model: str, timeout: int = 60):
        super().__init__(api_key, model, timeout)
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def _make_request(self, prompt: str) -> str:
        """Make a request to OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']


class DeepSeekClient(LLMClient):
    """DeepSeek API client implementation."""
    
    def __init__(self, api_key: str, model: str, timeout: int = 60):
        super().__init__(api_key, model, timeout)
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def _make_request(self, prompt: str) -> str:
        """Make a request to DeepSeek API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']


class ClaudeClient(LLMClient):
    """Anthropic Claude API client implementation."""
    
    def __init__(self, api_key: str, model: str, timeout: int = 60):
        super().__init__(api_key, model, timeout)
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def _make_request(self, prompt: str) -> str:
        """Make a request to Claude API."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['content'][0]['text']


class OllamaClient(LLMClient):
    """Ollama local LLM client implementation."""
    
    def __init__(self, api_key: str, model: str, timeout: int = 60):
        super().__init__(api_key, model, timeout)
        self.api_url = "http://localhost:11434/api/generate"
    
    def _make_request(self, prompt: str) -> str:
        """Make a request to Ollama API."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            self.api_url,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        return result['response']


class LLMClientFactory:
    """
    Factory class for creating LLM client instances.
    
    Uses the Factory Pattern to instantiate the appropriate LLM client
    based on the provider name.
    """
    
    @staticmethod
    def create_client(
        provider: str,
        api_key: str,
        model: str,
        timeout: int = 60
    ) -> LLMClient:
        """
        Create an LLM client instance.
        
        Args:
            provider: Provider name (openai, deepseek, claude, ollama)
            api_key: API authentication key
            model: Model identifier
            timeout: Request timeout in seconds
            
        Returns:
            An instance of the appropriate LLMClient subclass
            
        Raises:
            ValueError: If provider is not supported
        """
        providers = {
            'openai': OpenAIClient,
            'deepseek': DeepSeekClient,
            'claude': ClaudeClient,
            'ollama': OllamaClient
        }
        
        provider_lower = provider.lower()
        
        if provider_lower not in providers:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: {list(providers.keys())}"
            )
        
        client_class = providers[provider_lower]
        logger.info(f"Creating {provider} client with model: {model}")
        
        return client_class(api_key, model, timeout)