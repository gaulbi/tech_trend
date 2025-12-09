# ============================================================================
# src/tech_trend_analysis/llm/openai_client.py
# ============================================================================

"""OpenAI LLM client implementation."""

import time
from typing import Optional

from openai import OpenAI, OpenAIError

from ..exceptions import LLMError
from .base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int,
        retry: int
    ):
        """Initialize OpenAI client."""
        super().__init__(api_key, model, timeout, retry)
        self.client = OpenAI(api_key=api_key, timeout=timeout)

    def generate(self, prompt: str) -> str:
        """
        Generate response using OpenAI API.

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
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content or ""

            except OpenAIError as e:
                last_error = e
                if attempt < self.retry - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                continue

        raise LLMError(
            f"OpenAI API failed after {self.retry} attempts: {last_error}"
        )