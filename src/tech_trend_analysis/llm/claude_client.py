# ============================================================================
# src/tech_trend_analysis/llm/claude_client.py
# ============================================================================

"""Claude (Anthropic) LLM client implementation."""

import time
from typing import Optional

from anthropic import Anthropic, AnthropicError

from ..exceptions import LLMError
from .base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """Claude (Anthropic) API client."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int,
        retry: int
    ):
        """Initialize Claude client."""
        super().__init__(api_key, model, timeout, retry)
        self.client = Anthropic(api_key=api_key, timeout=timeout)

    def generate(self, prompt: str) -> str:
        """
        Generate response using Claude API.

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
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                )
                return response.content[0].text

            except AnthropicError as e:
                last_error = e
                if attempt < self.retry - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                continue

        raise LLMError(
            f"Claude API failed after {self.retry} attempts: {last_error}"
        )
