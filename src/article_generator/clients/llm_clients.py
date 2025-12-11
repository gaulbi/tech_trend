"""LLM client implementations with corrected max_tokens handling."""
import time
from typing import Optional
import requests
from openai import OpenAI
from anthropic import Anthropic
from .base import BaseLLMClient
from ..exceptions import LLMError


class OpenAIClient(BaseLLMClient):
    """OpenAI LLM client."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion with retry logic."""
        for attempt in range(self.max_retries):
            try:
                # Build request parameters
                params = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature,
                    "timeout": self.timeout
                }
                
                # Only add max_tokens if it's a valid positive integer
                if max_tokens is not None and max_tokens > 0:
                    params["max_tokens"] = max_tokens
                
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMError(f"OpenAI API failed: {str(e)}")


class DeepSeekClient(BaseLLMClient):
    """DeepSeek LLM client."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize DeepSeek client."""
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion with retry logic."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        # Only add max_tokens if it's a valid positive integer
        if max_tokens is not None and max_tokens > 0:
            payload["max_tokens"] = max_tokens
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMError(f"DeepSeek API failed: {str(e)}")


class ClaudeClient(BaseLLMClient):
    """Claude (Anthropic) LLM client."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize Claude client."""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion with retry logic."""
        for attempt in range(self.max_retries):
            try:
                # Claude requires max_tokens, use default if not provided
                tokens = max_tokens if max_tokens and max_tokens > 0 else 4096
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=temperature,
                    timeout=self.timeout
                )
                return response.content[0].text
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMError(f"Claude API failed: {str(e)}")


class OllamaClient(BaseLLMClient):
    """Ollama LLM client."""
    
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize Ollama client."""
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion with retry logic."""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {"temperature": temperature}
        }
        
        # Only add num_predict if max_tokens is valid
        if max_tokens is not None and max_tokens > 0:
            payload["options"]["num_predict"] = max_tokens
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise LLMError(f"Ollama API failed: {str(e)}")