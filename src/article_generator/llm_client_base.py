"""
LLM Client Base Module

Abstract base class and factory for LLM clients.
"""

from abc import ABC, abstractmethod
from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)


class LLMClientBase(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, model: str, timeout: int = 60, max_retries: int = 3):
        """
        Initialize LLM client.
        
        Args:
            model: Model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
            
        Raises:
            Exception: If generation fails after retries
        """
        pass
    
    def generate_with_retry(self, prompt: str) -> str:
        """
        Generate text with exponential backoff retry logic.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
            
        Raises:
            Exception: If all retries fail
        """
        delays = [1, 3, 5]  # Exponential backoff delays
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Generating text (attempt {attempt + 1}/{self.max_retries})")
                return self.generate(prompt)
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    delay = delays[attempt]
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
                    raise


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ) -> LLMClientBase:
        """
        Create LLM client based on provider.
        
        Args:
            provider: LLM provider name
            model: Model identifier
            api_key: API key (not needed for Ollama)
            timeout: Request timeout
            max_retries: Maximum retry attempts
            
        Returns:
            LLM client instance
            
        Raises:
            ValueError: If provider is unknown
        """
        from src.article_generator.llm_clients import (
            OpenAIClient,
            DeepSeekClient,
            ClaudeClient,
            OllamaClient
        )
        
        provider = provider.lower()
        
        if provider == 'openai':
            return OpenAIClient(model, api_key, timeout, max_retries)
        elif provider == 'deepseek':
            return DeepSeekClient(model, api_key, timeout, max_retries)
        elif provider == 'claude':
            return ClaudeClient(model, api_key, timeout, max_retries)
        elif provider == 'ollama':
            return OllamaClient(model, timeout, max_retries)
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                f"Supported: openai, deepseek, claude, ollama"
            )