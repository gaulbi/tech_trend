"""
DeepSeek image generation provider.
"""
import time
import requests
from pathlib import Path
from typing import Optional

from .base import BaseLLMProvider
from ..exceptions import LLMProviderError, NetworkError, ConfigurationError


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek image generation provider."""
    
    API_URL = "https://api.deepseek.com/v1/images/generations"
    
    def validate_config(self) -> bool:
        """Validate DeepSeek configuration."""
        if not self.api_key:
            raise ConfigurationError("DeepSeek API key is missing")
        return True
    
    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        size: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        output_format: str = "jpg"
    ) -> Path:
        """Generate image using DeepSeek."""
        self.validate_config()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "response_format": "url"
        }
        
        # Add size if supported and provided
        if size:
            payload["size"] = f"{size}x{size}"
        
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
