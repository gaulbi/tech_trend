# ============================================================================
# src/tech_trend_analysis/llm/base.py
# ============================================================================

"""Base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int,
        retry: int
    ):
        """
        Initialize LLM client.

        Args:
            api_key: API key for the provider
            model: Model name to use
            timeout: Request timeout in seconds
            retry: Number of retry attempts
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retry = retry

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: Input prompt

        Returns:
            Generated response text

        Raises:
            LLMError: If generation fails
        """
        pass