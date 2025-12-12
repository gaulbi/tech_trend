"""
OpenAI image generation provider.
"""
import time
import requests
from pathlib import Path
from typing import Optional

from .base import BaseLLMProvider
from ..exceptions import LLMProviderError, NetworkError, ConfigurationError


class OpenAIProvider(BaseLLMProvider):
    """OpenAI DALL-E image generation provider."""
    
    API_URL = "https://api.openai.com/v1/images/generations"
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise ConfigurationError("OpenAI API key is missing")
        if not self.model.startswith("dall-e"):
            raise ConfigurationError(
                f"Invalid OpenAI model: {self.model}"
            )
        return True
    
    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        size: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        output_format: str = "jpg"
    ) -> Path:
        """Generate image using OpenAI DALL-E."""
        self.validate_config()
        
        # Map aspect ratio to OpenAI size format
        size_map = {
            "1:1": "1024x1024",
            "square": "1024x1024",
            "wide": "1792x1024",
            "tall": "1024x1792"
        }
        
        dall_e_size = size_map.get(aspect_ratio, "1024x1024")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": dall_e_size,
            "response_format": "url"
        }
        
        last_error = None
        for attempt in range(self.retry):
            try:
                response = requests.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                image_url = data['data'][0]['url']
                
                # Download image
                img_response = requests.get(
                    image_url,
                    timeout=self.timeout
                )
                img_response.raise_for_status()
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(img_response.content)
                
                return output_path
                
            except requests.Timeout as e:
                last_error = NetworkError(f"Request timeout: {e}")
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.RequestException as e:
                last_error = NetworkError(f"Request failed: {e}")
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                last_error = LLMProviderError(f"Unexpected error: {e}")
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)
        
        raise last_error
