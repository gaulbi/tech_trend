# ============================================================================
# src/tech_trend_analysis/llm/ollama_client.py
# ============================================================================

"""Ollama (local) LLM client implementation."""

import time
from typing import Optional

import requests

from ..exceptions import LLMError
from .base import BaseLLMClient


class OllamaClient(BaseLLMClient):
    """Ollama local LLM client."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int,
        retry: int,
        base_url: str = "http://localhost:11434"
    ):
        """Initialize Ollama client."""
        super().__init__(api_key, model, timeout, retry)
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        """
        Generate response using Ollama API.

        Args:
            prompt: Input prompt

        Returns:
            Generated response

        Raises:
            LLMError: If API call fails after retries
        """
        last_error: Optional[Exception] = None

        for attempt in range(self.retry):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                return response.json().get("response", "")

            except requests.RequestException as e:
                last_error = e
                if attempt < self.retry - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                continue

        raise LLMError(
            f"Ollama API failed after {self.retry} attempts: {last_error}"
        )
