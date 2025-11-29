"""Claude (Anthropic) LLM client implementation."""

import time
from typing import Optional
import requests

from .base import BaseLLMClient
from ..exceptions import LLMError, NetworkError


class ClaudeClient(BaseLLMClient):
    """Claude (Anthropic) API client implementation."""

    BASE_URL = "https://api.anthropic.com/v1/messages"

    def generate(self, prompt: str) -> str:
        """Generate response using Claude API.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If generation fails
            NetworkError: If network request fails
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096
        }
        
        return self._make_request_with_retry(headers, payload)

    def _make_request_with_retry(
        self, 
        headers: dict, 
        payload: dict
    ) -> str:
        """Make API request with exponential backoff retry.
        
        Args:
            headers: Request headers
            payload: Request payload
            
        Returns:
            Generated response text
            
        Raises:
            NetworkError: If all retry attempts fail
            LLMError: If API returns an error
        """
        last_error: Optional[Exception] = None
        
        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return self._parse_response(response.json())
                else:
                    raise LLMError(
                        f"API error: {response.status_code} - "
                        f"{response.text}"
                    )
                    
            except requests.Timeout as e:
                last_error = e
                if attempt < self.retry_count - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
            except requests.RequestException as e:
                raise NetworkError(f"Network error: {str(e)}")
        
        raise NetworkError(
            f"Request failed after {self.retry_count} attempts: "
            f"{str(last_error)}"
        )

    def _parse_response(self, response_data: dict) -> str:
        """Parse API response.
        
        Args:
            response_data: Response JSON data
            
        Returns:
            Generated text content
            
        Raises:
            LLMError: If response format is invalid
        """
        try:
            return response_data["content"][0]["text"]
        except (KeyError, IndexError) as e:
            raise LLMError(f"Invalid response format: {str(e)}")