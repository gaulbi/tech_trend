"""Base LLM client interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    All LLM providers must inherit from this class and implement
    the generate method.
    """
    
    def __init__(self, model: str, timeout: int, max_retries: int):
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
        Generate response from LLM.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            LLMProviderError: If generation fails
        """
        pass